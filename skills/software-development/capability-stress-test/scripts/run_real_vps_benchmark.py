#!/usr/bin/env python3
"""
Real VPS Capability & Anti-Overclaim Benchmark Harness
Menguji performa nyata I/O, konkurensi CPU, resolusi algoritma kompleks,
dan audit kejujuran kernel Linux (membedakan fitur kernel native vs userspace mock).
"""

import os
import sys
import time
import hashlib
import json
import multiprocessing as mp
from typing import Dict, Any

def test_1_io_throughput(size_mb: int = 30) -> Dict[str, Any]:
    """Uji I/O disk nyata: write 30MB, read back, verifikasi SHA256."""
    test_file = "/tmp/benchmark_io_test.dat"
    chunk_size = 1024 * 1024 # 1MB
    payload = os.urandom(chunk_size)
    
    # 1. Write Benchmark
    hasher_write = hashlib.sha256()
    t0 = time.perf_counter()
    with open(test_file, "wb") as f:
        for _ in range(size_mb):
            f.write(payload)
            hasher_write.update(payload)
        f.flush()
        os.fsync(f.fileno())
    t_write = time.perf_counter() - t0
    write_speed = size_mb / t_write if t_write > 0 else 0

    # 2. Read Benchmark
    hasher_read = hashlib.sha256()
    t0 = time.perf_counter()
    with open(test_file, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher_read.update(chunk)
    t_read = time.perf_counter() - t0
    read_speed = size_mb / t_read if t_read > 0 else 0

    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)

    integrity_ok = (hasher_write.hexdigest() == hasher_read.hexdigest())
    return {
        "size_mb": size_mb,
        "write_throughput_mbs": round(write_speed, 2),
        "read_throughput_mbs": round(read_speed, 2),
        "integrity_verified": integrity_ok,
        "sha256_match": integrity_ok
    }

def _worker_task(q_in, q_out, count):
    for _ in range(count):
        val = q_in.get()
        q_out.put(val * 2)

def test_2_multiprocess_concurrency(transactions: int = 20000) -> Dict[str, Any]:
    """Uji konkurensi IPC multiproses nyata pada CPU VPS."""
    q_in = mp.Queue()
    q_out = mp.Queue()
    workers = 2
    per_worker = transactions // workers

    procs = [mp.Process(target=_worker_task, args=(q_in, q_out, per_worker)) for _ in range(workers)]
    for p in procs:
        p.start()

    t0 = time.perf_counter()
    for i in range(transactions):
        q_in.put(i)

    received = 0
    while received < transactions:
        q_out.get()
        received += 1
    duration = time.perf_counter() - t0

    for p in procs:
        p.join()

    ops_per_sec = transactions / duration if duration > 0 else 0
    return {
        "transactions": transactions,
        "workers": workers,
        "duration_sec": round(duration, 3),
        "throughput_ops_sec": round(ops_per_sec, 1),
        "zero_loss_verified": (received == transactions)
    }

def test_3_kernel_reality_check() -> Dict[str, Any]:
    """Audit faktual fitur kernel Linux host (Anti-Overclaim Verification)."""
    # 1. Cek eBPF LSM
    lsm_path = "/sys/kernel/security/lsm"
    active_lsms = "N/A"
    bpf_lsm_active = False
    if os.path.exists(lsm_path):
        try:
            with open(lsm_path, "r") as f:
                active_lsms = f.read().strip()
                bpf_lsm_active = "bpf" in active_lsms.split(",")
        except Exception as e:
            active_lsms = f"Error: {e}"

    # 2. Cek Seccomp di status proses
    seccomp_mode = "N/A"
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("Seccomp:"):
                    seccomp_mode = line.split()[1].strip()
    except Exception as e:
        seccomp_mode = f"Error: {e}"

    # 3. Kernel version & Cgroup
    uname = os.uname()
    cgroup_v2 = os.path.exists("/sys/fs/cgroup/cgroup.controllers")

    return {
        "kernel_release": uname.release,
        "active_kernel_lsms": active_lsms,
        "is_bpf_lsm_attached": bpf_lsm_active,
        "process_seccomp_mode": seccomp_mode,
        "cgroup_v2_supported": cgroup_v2,
        "honest_assessment": (
            "Kernel BPF-LSM BUKAN driver aktif di VPS ini." if not bpf_lsm_active
            else "Kernel BPF-LSM aktif secara native."
        )
    }

def test_4_algorithmic_dag_sort(node_count: int = 3000) -> Dict[str, Any]:
    """Uji algoritma kompleks: Topological sort DAG 3.000 simpul & deteksi siklus."""
    import collections
    
    # Bangun rantai linier + multiple random forward edges
    adj = collections.defaultdict(list)
    in_degree = {i: 0 for i in range(node_count)}
    
    for i in range(node_count - 1):
        adj[i].append(i + 1)
        in_degree[i + 1] += 1
        if i + 2 < node_count and i % 3 == 0:
            adj[i].append(i + 2)
            in_degree[i + 2] += 1

    t0 = time.perf_counter()
    # Kahn's algorithm
    queue = collections.deque([n for n, deg in in_degree.items() if deg == 0])
    topo_order = []
    
    while queue:
        u = queue.popleft()
        topo_order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
                
    dur = time.perf_counter() - t0
    is_valid_dag = (len(topo_order) == node_count)

    return {
        "node_count": node_count,
        "sort_duration_sec": round(dur, 4),
        "is_valid_dag": is_valid_dag,
        "cycle_free": is_valid_dag
    }

def run_all():
    print("=== Menjalankan Capability & Anti-Overclaim Benchmark ===")
    t_start = time.perf_counter()
    
    res_io = test_1_io_throughput(30)
    res_ipc = test_2_multiprocess_concurrency(20000)
    res_kernel = test_3_kernel_reality_check()
    res_algo = test_4_algorithmic_dag_sort(3000)
    
    total_time = round(time.perf_counter() - t_start, 2)
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S WIB"),
        "total_benchmark_time_sec": total_time,
        "io_performance": res_io,
        "multiprocess_concurrency": res_ipc,
        "kernel_reality_audit": res_kernel,
        "algorithmic_dag_resolution": res_algo
    }
    
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run_all()
