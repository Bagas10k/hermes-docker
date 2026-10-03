#!/usr/bin/env python3
"""
VPS Benchmark v3 Hardened — Eksekusi Penyelesaian 4 Kekurangan v2
1. Real Multi-Process Contention IPC (Proses Produser + Konsumen terpisah via POSIX Shared Memory + Sinyal EventFd).
2. Random Sparse DAG (Graf acak tak beraturan dengan 20.000 simpul & ribuan percabangan acak non-linier).
3. Concurrent Multi-Connection TCP Socket Pool (50 koneksi simultan, bukan ping-pong sekuensial tunggal).
4. Full OS Physical Memory Tracking via /proc/self/status & getrusage (VmRSS, VmHWM, Minor Page Faults).
"""

import os
import sys
import time
import socket
import select
import random
import resource
import threading
import multiprocessing as mp
from multiprocessing import shared_memory
import numpy as np

# --- 1. Real Multi-Process IPC Contention ---
def _ipc_producer(shm_name, count, sem_p2c, sem_c2p):
    shm = shared_memory.SharedMemory(name=shm_name)
    buf = shm.buf
    for i in range(count):
        sem_c2p.acquire() # Tunggu slot kosong
        buf[0:4] = (i & 0xFFFFFFFF).to_bytes(4, byteorder='little')
        sem_p2c.release() # Sinyalkan data siap
    shm.close()

def _ipc_consumer(shm_name, count, sem_p2c, sem_c2p, result_pipe):
    shm = shared_memory.SharedMemory(name=shm_name)
    buf = shm.buf
    checksum = 0
    t0 = time.perf_counter()
    for _ in range(count):
        sem_p2c.acquire() # Tunggu data
        val = int.from_bytes(buf[0:4], byteorder='little')
        checksum += val
        sem_c2p.release() # Sinyalkan slot bebas
    dur = time.perf_counter() - t0
    shm.close()
    result_pipe.send((dur, checksum))

def benchmark_real_contention_ipc(count=50000):
    shm = shared_memory.SharedMemory(create=True, size=64)
    sem_p2c = mp.Semaphore(0)
    sem_c2p = mp.Semaphore(1)
    pipe_recv, pipe_send = mp.Pipe(duplex=False)

    p_cons = mp.Process(target=_ipc_consumer, args=(shm.name, count, sem_p2c, sem_c2p, pipe_send))
    p_prod = mp.Process(target=_ipc_producer, args=(shm.name, count, sem_p2c, sem_c2p))

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
        "duration_sec": round(dur, 4),
        "real_contention_ops_sec": round(ops_sec, 1),
        "verified_checksum": checksum
    }

# --- 2. Random Sparse DAG (20.000 Simpul Acak Non-Linier) ---
def benchmark_random_sparse_dag(nodes=20000, avg_out_degree=3):
    random.seed(42)
    in_degrees = [0] * nodes
    adj = [[] for _ in range(nodes)]

    # Bentuk graf acak terarah asiklik (i < j menjamin bebas siklus)
    for u in range(nodes - 1):
        # Pilih target acak di depan u
        k = random.randint(1, min(avg_out_degree * 2, nodes - 1 - u))
        targets = set()
        for _ in range(k):
            v = random.randint(u + 1, min(u + 200, nodes - 1))
            targets.add(v)
        for v in targets:
            adj[u].append(v)
            in_degrees[v] += 1

    t0 = time.perf_counter()
    # Kahn's Algorithm
    zero_in = [i for i, deg in enumerate(in_degrees) if deg == 0]
    visited = 0
    while zero_in:
        curr = zero_in.pop()
        visited += 1
        for nxt in adj[curr]:
            in_degrees[nxt] -= 1
            if in_degrees[nxt] == 0:
                zero_in.append(nxt)
    dur = time.perf_counter() - t0

    return {
        "nodes": nodes,
        "is_acyclic_verified": (visited == nodes),
        "sort_duration_sec": round(dur, 4),
        "throughput_nodes_sec": round(nodes / dur, 1)
    }

# --- 3. Concurrent Multi-Connection TCP Socket Pool (50 Koneksi Paralel) ---
def benchmark_concurrent_tcp_pool(num_clients=50, requests_per_client=100):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("127.0.0.1", 0))
    server_sock.listen(128)
    server_sock.setblocking(False)
    port = server_sock.getsockname()[1]

    stop_server = threading.Event()
    
    def server_loop():
        epoll = select.epoll()
        epoll.register(server_sock.fileno(), select.EPOLLIN)
        connections = {}
        while not stop_server.is_set():
            events = epoll.poll(0.01)
            for fd, event in events:
                if fd == server_sock.fileno():
                    try:
                        conn, _ = server_sock.accept()
                        conn.setblocking(False)
                        epoll.register(conn.fileno(), select.EPOLLIN)
                        connections[conn.fileno()] = conn
                    except BlockingIOError:
                        pass
                elif event & select.EPOLLIN:
                    conn = connections.get(fd)
                    if conn:
                        try:
                            data = conn.recv(64)
                            if data:
                                conn.sendall(data)
                            else:
                                epoll.unregister(fd)
                                conn.close()
                                del connections[fd]
                        except Exception:
                            epoll.unregister(fd)
                            conn.close()
                            del connections[fd]
        epoll.close()
        server_sock.close()

    srv_thread = threading.Thread(target=server_loop, daemon=True)
    srv_thread.start()

    latencies = []
    lat_lock = threading.Lock()

    def client_worker():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.connect(("127.0.0.1", port))
        local_lats = []
        payload = b"PING_CONCURRENT"
        for _ in range(requests_per_client):
            t1 = time.perf_counter()
            s.sendall(payload)
            resp = s.recv(64)
            t2 = time.perf_counter()
            local_lats.append((t2 - t1) * 1_000_000)
        s.close()
        with lat_lock:
            latencies.extend(local_lats)

    threads = [threading.Thread(target=client_worker) for _ in range(num_clients)]
    t0 = time.perf_counter()
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    total_dur = time.perf_counter() - t0
    stop_server.set()
    srv_thread.join()

    latencies.sort()
    n_samples = len(latencies)
    return {
        "concurrent_clients": num_clients,
        "total_requests": n_samples,
        "total_duration_sec": round(total_dur, 4),
        "requests_per_sec": round(n_samples / total_dur, 1),
        "p50_us": round(latencies[int(n_samples * 0.50)], 2),
        "p95_us": round(latencies[int(n_samples * 0.95)], 2),
        "p99_us": round(latencies[int(n_samples * 0.99)], 2),
        "max_us": round(latencies[-1], 2)
    }

# --- 4. Full OS Physical Memory & Kernel Stats ---
def get_os_memory_and_stats():
    rusage = resource.getrusage(resource.RUSAGE_SELF)
    max_rss_kb = rusage.ru_maxrss # Di Linux ini dalam KB
    minor_page_faults = rusage.ru_minflt
    major_page_faults = rusage.ru_majflt

    proc_status = {}
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith(("VmRSS:", "VmHWM:", "VmSize:", "Threads:")):
                    parts = line.split(":")
                    proc_status[parts[0].strip()] = parts[1].strip()
    except Exception:
        pass

    return {
        "os_max_rss_kb": max_rss_kb,
        "os_max_rss_mb": round(max_rss_kb / 1024, 2),
        "minor_page_faults": minor_page_faults,
        "major_page_faults_io": major_page_faults,
        "proc_status": proc_status
    }

def run_v3():
    print("=== Menjalankan VPS Benchmark v3 Hardened ===")
    t_start = time.perf_counter()

    res_ipc = benchmark_real_contention_ipc(50000)
    res_dag = benchmark_random_sparse_dag(20000)
    res_tcp = benchmark_concurrent_tcp_pool(50, 100)
    res_mem = get_os_memory_and_stats()

    total_dur = round(time.perf_counter() - t_start, 3)

    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S WIB"),
        "total_duration_sec": total_dur,
        "real_ipc_contention": res_ipc,
        "random_sparse_dag_20k": res_dag,
        "concurrent_tcp_50_clients": res_tcp,
        "real_os_memory_telemetry": res_mem
    }
    import json
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    run_v3()
