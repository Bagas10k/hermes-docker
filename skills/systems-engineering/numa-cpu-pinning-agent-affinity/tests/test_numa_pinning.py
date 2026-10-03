#!/usr/bin/env python3
"""
Unit tests untuk NUMA-Aware CPU Pinning & Memory Affinity Manager.
"""

import os
import sys
import unittest
import tempfile
import shutil

# Tambahkan direktori scripts ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))
from numa_pinning_engine import NUMAWatcher, NUMAPinningEngine, Topology, NUMANodeInfo


class TestNUMAPinningEngine(unittest.TestCase):
    def setUp(self):
        # Buat temporary sysfs tree untuk simulasi multi-node NUMA
        self.temp_dir = tempfile.mkdtemp()
        self.sysfs_root = os.path.join(self.temp_dir, "sys", "devices", "system")
        os.makedirs(os.path.join(self.sysfs_root, "cpu"), exist_ok=True)
        os.makedirs(os.path.join(self.sysfs_root, "node", "node0"), exist_ok=True)
        os.makedirs(os.path.join(self.sysfs_root, "node", "node1"), exist_ok=True)

        with open(os.path.join(self.sysfs_root, "cpu", "online"), "w") as f:
            f.write("0-7\n")

        with open(os.path.join(self.sysfs_root, "node", "node0", "cpulist"), "w") as f:
            f.write("0-3\n")

        with open(os.path.join(self.sysfs_root, "node", "node1", "cpulist"), "w") as f:
            f.write("4-7\n")

        with open(os.path.join(self.sysfs_root, "node", "node0", "meminfo"), "w") as f:
            f.write("Node 0 MemTotal:        16384000 kB\nNode 0 MemFree:         12000000 kB\n")

        with open(os.path.join(self.sysfs_root, "node", "node1", "meminfo"), "w") as f:
            f.write("Node 1 MemTotal:        16384000 kB\nNode 1 MemFree:         10000000 kB\n")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_01_synthetic_topology_detection(self):
        topo = NUMAWatcher.detect_topology(self.sysfs_root)
        self.assertEqual(topo.total_cpus, 8)
        self.assertTrue(topo.is_multi_node)
        self.assertEqual(len(topo.numa_nodes), 2)
        self.assertEqual(topo.numa_nodes[0].cpus, [0, 1, 2, 3])
        self.assertEqual(topo.numa_nodes[1].cpus, [4, 5, 6, 7])

    def test_02_cpu_list_parsing(self):
        self.assertEqual(NUMAWatcher._parse_cpu_list("0-2,4,6-7"), [0, 1, 2, 4, 6, 7])
        self.assertEqual(NUMAWatcher._parse_cpu_list(""), [])
        self.assertEqual(NUMAWatcher._parse_cpu_list("3"), [3])

    def test_03_worker_allocation_and_load_balance(self):
        engine = NUMAPinningEngine(sysfs_root=self.sysfs_root)
        
        # Worker 1 dialokasikan ke node 0 (2 core)
        alloc1 = engine.allocate_worker("worker_1", pid=0, num_cores=2, preferred_node=0)
        self.assertEqual(alloc1.assigned_numa_node, 0)
        self.assertEqual(alloc1.assigned_cpus, [0, 1])
        self.assertEqual(engine.node_load[0], 2)

        # Worker 2 tanpa preferensi harus masuk ke node 1 karena node 0 lebih berbeban
        alloc2 = engine.allocate_worker("worker_2", pid=0, num_cores=2)
        self.assertEqual(alloc2.assigned_numa_node, 1)
        self.assertEqual(alloc2.assigned_cpus, [4, 5])
        self.assertEqual(engine.node_load[1], 2)

    def test_04_worker_release(self):
        engine = NUMAPinningEngine(sysfs_root=self.sysfs_root)
        engine.allocate_worker("worker_a", pid=0, num_cores=2, preferred_node=0)
        self.assertEqual(engine.node_load[0], 2)
        
        released = engine.release_worker("worker_a")
        self.assertTrue(released)
        self.assertEqual(engine.node_load[0], 0)
        self.assertNotIn("worker_a", engine.allocations)

    def test_05_cross_node_latency_penalty(self):
        engine = NUMAPinningEngine(sysfs_root=self.sysfs_root)
        # Core 0 ada di node 0
        local_penalty = engine.calculate_cross_node_penalty(cpu_id=0, target_node_id=0)
        self.assertEqual(local_penalty, 1.0)

        # Core 0 mengakses memory di node 1
        cross_penalty = engine.calculate_cross_node_penalty(cpu_id=0, target_node_id=1)
        self.assertEqual(cross_penalty, 1.75)

    def test_06_live_os_topology_fallback(self):
        # Jalankan pada sistem host Linux live riil (fallback UMA jika hanya 1 node)
        live_engine = NUMAPinningEngine()
        summary = live_engine.get_summary()
        self.assertGreater(summary["total_cpus"], 0)
        self.assertGreater(summary["numa_node_count"], 0)

        # Alokasikan worker pada PID saat ini
        current_pid = os.getpid()
        alloc = live_engine.allocate_worker("self_test", pid=current_pid, num_cores=1)
        self.assertIn("self_test", live_engine.allocations)
        if hasattr(os, "sched_setaffinity"):
            self.assertTrue(alloc.enforced_sched_affinity)


if __name__ == "__main__":
    unittest.main()
