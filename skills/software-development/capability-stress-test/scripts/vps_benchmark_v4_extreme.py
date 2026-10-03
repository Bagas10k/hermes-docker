#!/usr/bin/env python3
"""
VPS Benchmark v4 Extreme — Perbaikan 3 Kekurangan v3:
1. Eliminasi Tail Spike Jaringan via Non-blocking Async Event-Loop (Asyncio Client Pool alih-alih OS Thread Pool).
2. Batched Lock-Free Shared Memory IPC (Pemberantasan context switch syscall per item, target >200.000 ops/detik).
3. Multi-Tier Payload Bandwidth Matrix: 128B (RPC), 16KB (JSON API), 1MB (Binary Stream) dengan throughput MB/s.
4. Full OS Physical Memory & Page Faults tracking.
"""

import os
import sys
import time
import socket
import select
import asyncio
import threading
import resource
import multiprocessing as mp
from multiprocessing import shared_memory
import numpy as np

# --- 1. Batched Lock-Free Shared Memory IPC (Eliminasi Context Switch Per-Item) ---
BATCH_SIZE = 256

def _batched_producer(shm_name, count, sem_p2c, sem_c2p):
    shm = shared_memory.SharedMemory(name=shm_name)
    buf = shm.buf
    batches = count // BATCH_SIZE
    for b in range(batches):
        sem_c2p.acquire() # Tunggu batch buffer kosong
        offset = 0
        for i in range(BATCH_SIZE):
            val = (b * BATCH_SIZE + i) & 0xFFFFFFFF
            buf[offset:offset+4] = val.to_bytes(4, byteorder='little')
            offset += 4
        sem_p2c.release() # Sinyalkan seluruh batch siap
    shm.close()

def _batched_consumer(shm_name, count, sem_p2c, sem_c2p, result_pipe):
    shm = shared_memory.SharedMemory(name=shm_name)
    buf = shm.buf
    batches = count // BATCH_SIZE
    checksum = 0
    t0 = time.perf_counter()
    for _ in range(batches):
        sem_p2c.acquire() # Tunggu batch
        offset = 0
        for _ in range(BATCH_SIZE):
            val = int.from_bytes(buf[offset:offset+4], byteorder='little')
            checksum += val
            offset += 4
        sem_c2p.release() # Sinyalkan batch slot bebas
    dur = time.perf_counter() - t0
    shm.close()
    result_pipe.send((dur, checksum))

def benchmark_batched_ipc(count=200000):
    buf_size = BATCH_SIZE * 4 # 1024 byte (1 KB)
    shm = shared_memory.SharedMemory(create=True, size=buf_size)
    sem_p2c = mp.Semaphore(0)
    sem_c2p = mp.Semaphore(1)
    pipe_recv, pipe_send = mp.Pipe(duplex=False)

    p_cons = mp.Process(target=_batched_consumer, args=(shm.name, count, sem_p2c, sem_c2p, pipe_send))
    p_prod = mp.Process(target=_batched_producer, args=(shm.name, count, sem_p2c, sem_c2p))

    p_cons.start()
    p_prod.start()

    dur, checksum = pipe_recv.recv()
    p_prod.join()
    p_cons.join()
    shm.close()
    shm.unlink()

    ops_sec = count / dur if dur > 0 else 0
    return {
        "transactions": count,
        "batch_size": BATCH_SIZE,
        "duration_sec": round(dur, 4),
        "batched_throughput_ops_sec": round(ops_sec, 1),
        "speedup_vs_v3": f"{round(ops_sec / 15588.9, 1)}x lebih kencang"
    }

# --- 2. Async Non-Blocking TCP Pool (Eliminasi Thread Contention & Tail Spikes) ---
async def _async_tcp_server(host, port, ready_event, stop_event):
    async def handle_echo(reader, writer):
        while not stop_event.is_set():
            data = await reader.read(4096)
            if not data:
                break
            writer.write(data)
            await writer.drain()
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(handle_echo, host, port)
    ready_event.set()
    async with server:
        await stop_event.wait()

async def benchmark_async_tcp_pool(num_clients=50, requests_per_client=100):
    host = "127.0.0.1"
    # Cari port bebas
    s_temp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_temp.bind((host, 0))
    port = s_temp.getsockname()[1]
    s_temp.close()

    ready_event = asyncio.Event()
    stop_event = asyncio.Event()

    server_task = asyncio.create_task(_async_tcp_server(host, port, ready_event, stop_event))
    await ready_event.wait()

    latencies = []

    async def client_worker():
        reader, writer = await asyncio.open_connection(host, port)
        payload = b"PING_ASYNC_FAST"
        for _ in range(requests_per_client):
            t1 = time.perf_counter()
            writer.write(payload)
            await writer.drain()
            _ = await reader.read(len(payload))
            t2 = time.perf_counter()
            latencies.append((t2 - t1) * 1_000_000)
        writer.close()
        await writer.wait_closed()

    t0 = time.perf_counter()
    tasks = [asyncio.create_task(client_worker()) for _ in range(num_clients)]
    await asyncio.gather(*tasks)
    total_dur = time.perf_counter() - t0

    stop_event.set()
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass

    latencies.sort()
    n = len(latencies)
    return {
        "concurrent_clients": num_clients,
        "total_requests": n,
        "total_duration_sec": round(total_dur, 4),
        "throughput_req_sec": round(n / total_dur, 1),
        "p50_us": round(latencies[int(n * 0.50)], 2),
        "p95_us": round(latencies[int(n * 0.95)], 2),
        "p99_us": round(latencies[int(n * 0.99)], 2),
        "max_us": round(latencies[-1], 2),
        "max_ms": round(latencies[-1] / 1000, 2)
    }

# --- 3. Multi-Tier Payload Bandwidth Matrix ---
def benchmark_payload_bandwidth():
    tiers = [
        ("128B_RPC", 128, 5000),
        ("16KB_JSON", 16 * 1024, 1000),
        ("1MB_BINARY", 1024 * 1024, 50)
    ]
    results = {}
    host = "127.0.0.1"

    for label, size, iters in tiers:
        payload = b"X" * size
        total_bytes = size * iters
        
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, 0))
        srv.listen(1)
        port = srv.getsockname()[1]

        def srv_func():
            conn, _ = srv.accept()
            bytes_received = 0
            while bytes_received < total_bytes:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                bytes_received += len(chunk)
            conn.close()
            srv.close()

        th = threading.Thread(target=srv_func, daemon=True)
        th.start()

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        client.connect((host, port))

        t0 = time.perf_counter()
        for _ in range(iters):
            client.sendall(payload)
        client.close()
        th.join()
        dur = time.perf_counter() - t0

        mb_transferred = total_bytes / (1024 * 1024)
        throughput_mbs = mb_transferred / dur if dur > 0 else 0

        results[label] = {
            "payload_size": size,
            "iterations": iters,
            "total_transferred_mb": round(mb_transferred, 2),
            "duration_sec": round(dur, 4),
            "throughput_mbs": round(throughput_mbs, 2)
        }
    return results

def get_os_telemetry():
    rusage = resource.getrusage(resource.RUSAGE_SELF)
    proc_status = {}
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith(("VmRSS:", "VmHWM:")):
                    parts = line.split(":")
                    proc_status[parts[0].strip()] = parts[1].strip()
    except Exception:
        pass
    return {
        "max_rss_mb": round(rusage.ru_maxrss / 1024, 2),
        "minor_page_faults": rusage.ru_minflt,
        "proc_status": proc_status
    }

def run_v4():
    print("=== Menjalankan VPS Benchmark v4 Extreme ===")
    t_start = time.perf_counter()

    res_ipc = benchmark_batched_ipc(200000)
    res_tcp = asyncio.run(benchmark_async_tcp_pool(50, 100))
    res_bandwidth = benchmark_payload_bandwidth()
    res_mem = get_os_telemetry()

    total_dur = round(time.perf_counter() - t_start, 3)

    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S WIB"),
        "total_benchmark_time_sec": total_dur,
        "batched_ipc_contention": res_ipc,
        "async_tcp_pool_50_clients": res_tcp,
        "payload_bandwidth_matrix": res_bandwidth,
        "os_memory_telemetry": res_mem
    }
    import json
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    run_v4()
