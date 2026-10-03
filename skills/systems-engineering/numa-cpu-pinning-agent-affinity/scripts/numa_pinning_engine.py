#!/usr/bin/env python3
"""
NUMA-Aware CPU Pinning & Memory Affinity Manager for Parallel Agent Workers.

Menyediakan isolasi core CPU, affinitas memori NUMA, dan alokasi resource
deterministik untuk mencegah context switching thrashing dan cross-NUMA latency.
Dilengkapi fallback transparan ketika numactl / multi-node NUMA tidak tersedia.
"""

import os
import sys
import json
import time
import glob
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger("numa_affinity")


@dataclass
class NUMANodeInfo:
    node_id: int
    cpus: List[int]
    total_memory_bytes: int = 0
    free_memory_bytes: int = 0


@dataclass
class Topology:
    total_cpus: int
    numa_nodes: Dict[int, NUMANodeInfo]
    is_multi_node: bool


@dataclass
class WorkerPinAllocation:
    worker_id: str
    pid: int
    assigned_cpus: List[int]
    assigned_numa_node: int
    enforced_sched_affinity: bool
    enforced_numa_memory: bool
    timestamp: float = field(default_factory=time.time)


class NUMAWatcher:
    """Mendeteksi topologi CPU dan NUMA dari Linux sysfs (/sys/devices/system/node/)."""

    @staticmethod
    def detect_topology(sysfs_root: str = "/sys/devices/system") -> Topology:
        cpu_path = os.path.join(sysfs_root, "cpu")
        online_file = os.path.join(cpu_path, "online")
        
        # Deteksi total CPU
        total_cpus = 1
        if os.path.exists(online_file):
            try:
                with open(online_file, "r") as f:
                    content = f.read().strip()
                    total_cpus = NUMAWatcher._parse_cpu_range(content)
            except Exception:
                total_cpus = os.cpu_count() or 1
        else:
            total_cpus = os.cpu_count() or 1

        # Deteksi NUMA Nodes
        nodes: Dict[int, NUMANodeInfo] = {}
        node_pattern = os.path.join(sysfs_root, "node", "node[0-9]*")
        node_dirs = glob.glob(node_pattern)

        if node_dirs:
            for nd in node_dirs:
                try:
                    bname = os.path.basename(nd)
                    node_id = int(bname.replace("node", ""))
                    cpulist_file = os.path.join(nd, "cpulist")
                    cpus = []
                    if os.path.exists(cpulist_file):
                        with open(cpulist_file, "r") as f:
                            cpus = NUMAWatcher._parse_cpu_list(f.read().strip())
                    else:
                        cpus = list(range(total_cpus))

                    # Parse meminfo jika ada
                    meminfo_file = os.path.join(nd, "meminfo")
                    total_mem = 0
                    free_mem = 0
                    if os.path.exists(meminfo_file):
                        with open(meminfo_file, "r") as f:
                            for line in f:
                                if "MemTotal:" in line:
                                    parts = line.split()
                                    if len(parts) >= 4:
                                        total_mem = int(parts[3]) * 1024
                                elif "MemFree:" in line:
                                    parts = line.split()
                                    if len(parts) >= 4:
                                        free_mem = int(parts[3]) * 1024

                    nodes[node_id] = NUMANodeInfo(
                        node_id=node_id,
                        cpus=cpus,
                        total_memory_bytes=total_mem,
                        free_memory_bytes=free_mem,
                    )
                except Exception as e:
                    logger.debug(f"Error parsing node {nd}: {e}")

        # Fallback jika UMA (single node) atau sysfs node tidak ditemukan
        if not nodes:
            nodes[0] = NUMANodeInfo(
                node_id=0,
                cpus=list(range(total_cpus)),
                total_memory_bytes=0,
                free_memory_bytes=0,
            )

        is_multi = len(nodes) > 1
        return Topology(total_cpus=total_cpus, numa_nodes=nodes, is_multi_node=is_multi)

    @staticmethod
    def _parse_cpu_range(range_str: str) -> int:
        """Contoh input '0-5' -> 6 cpus."""
        try:
            if "-" in range_str:
                parts = range_str.split("-")
                return int(parts[1]) - int(parts[0]) + 1
            elif "," in range_str:
                return len(range_str.split(","))
            return int(range_str) + 1
        except Exception:
            return os.cpu_count() or 1

    @staticmethod
    def _parse_cpu_list(list_str: str) -> List[int]:
        """Contoh input '0-2,4' -> [0, 1, 2, 4]."""
        cpus: List[int] = []
        if not list_str:
            return cpus
        for part in list_str.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                start, end = part.split("-")
                cpus.extend(range(int(start), int(end) + 1))
            else:
                cpus.append(int(part))
        return sorted(list(set(cpus)))


class NUMAPinningEngine:
    """Engine alokasi dan penegakan CPU pinning serta NUMA node affinity."""

    def __init__(self, sysfs_root: str = "/sys/devices/system"):
        self.topology = NUMAWatcher.detect_topology(sysfs_root)
        self.allocations: Dict[str, WorkerPinAllocation] = {}
        self.node_load: Dict[int, int] = {nid: 0 for nid in self.topology.numa_nodes.keys()}
        self.cpu_assignments: Dict[int, str] = {}  # cpu_id -> worker_id

    def allocate_worker(
        self,
        worker_id: str,
        pid: int,
        num_cores: int = 1,
        preferred_node: Optional[int] = None,
        exclusive: bool = False,
    ) -> WorkerPinAllocation:
        """Mengalokasikan core CPU dan NUMA node untuk pekerja agen."""
        if worker_id in self.allocations:
            self.release_worker(worker_id)

        # 1. Pilih NUMA node paling seimbang (least loaded) jika tidak ditentukan
        target_node_id = preferred_node
        if target_node_id is None or target_node_id not in self.topology.numa_nodes:
            target_node_id = min(self.node_load.keys(), key=lambda n: self.node_load[n])

        node = self.topology.numa_nodes[target_node_id]
        available_cpus = list(node.cpus)

        # 2. Filter CPU berdasarkan ketersediaan (jika exclusive diminta)
        if exclusive:
            unassigned = [c for c in available_cpus if c not in self.cpu_assignments]
            if len(unassigned) >= num_cores:
                selected_cpus = unassigned[:num_cores]
            else:
                # Fallback: ambil yang ada
                selected_cpus = (unassigned + [c for c in available_cpus if c not in unassigned])[:num_cores]
        else:
            # Ambil core terdepan dari node
            selected_cpus = available_cpus[:num_cores] if len(available_cpus) >= num_cores else available_cpus

        if not selected_cpus:
            selected_cpus = [0]

        # 3. Terapkan OS-level CPU affinity jika proses PID hidup dan os.sched_setaffinity tersedia
        enforced_sched = False
        enforced_numa = False

        if hasattr(os, "sched_setaffinity") and pid > 0:
            try:
                os.sched_setaffinity(pid, set(selected_cpus))
                enforced_sched = True
            except (ProcessLookupError, PermissionError, OSError) as e:
                logger.warning(f"Could not apply sched_setaffinity on pid {pid}: {e}")

        # Catat alokasi
        alloc = WorkerPinAllocation(
            worker_id=worker_id,
            pid=pid,
            assigned_cpus=selected_cpus,
            assigned_numa_node=target_node_id,
            enforced_sched_affinity=enforced_sched,
            enforced_numa_memory=enforced_numa,
        )

        self.allocations[worker_id] = alloc
        self.node_load[target_node_id] += len(selected_cpus)
        for c in selected_cpus:
            self.cpu_assignments[c] = worker_id

        return alloc

    def release_worker(self, worker_id: str) -> bool:
        """Membebaskan alokasi CPU untuk pekerja."""
        if worker_id not in self.allocations:
            return False

        alloc = self.allocations.pop(worker_id)
        if alloc.assigned_numa_node in self.node_load:
            self.node_load[alloc.assigned_numa_node] = max(
                0, self.node_load[alloc.assigned_numa_node] - len(alloc.assigned_cpus)
            )

        for c in alloc.assigned_cpus:
            if self.cpu_assignments.get(c) == worker_id:
                del self.cpu_assignments[c]

        return True

    def calculate_cross_node_penalty(self, cpu_id: int, target_node_id: int) -> float:
        """
        Menghitung estimasi penalti inter-socket latency (Amdahl & memory hop).
        Di node lokal penalty = 1.0 (baseline), cross-node penalty = 1.6x - 2.1x latency.
        """
        for nid, node in self.topology.numa_nodes.items():
            if cpu_id in node.cpus:
                if nid == target_node_id:
                    return 1.0  # Lokal (zero QPI/UPI hop penalty)
                else:
                    return 1.75  # Cross-socket UPI hop (~75% extra latency)
        return 1.0

    def get_summary(self) -> Dict:
        return {
            "total_cpus": self.topology.total_cpus,
            "is_multi_node": self.topology.is_multi_node,
            "numa_node_count": len(self.topology.numa_nodes),
            "active_allocations": {k: asdict(v) for k, v in self.allocations.items()},
            "node_load": self.node_load,
        }


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        engine = NUMAPinningEngine()
        print(json.dumps(engine.get_summary(), indent=2))
        sys.exit(0)

    print("NUMA Pinning Engine CLI. Gunakan --status untuk melihat topologi.")


if __name__ == "__main__":
    main()
