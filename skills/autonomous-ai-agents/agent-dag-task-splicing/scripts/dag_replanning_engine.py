#!/usr/bin/env python3
"""
DAG Task Splicing & Dynamic Topological Replanning Engine for Autonomous AI Agents.
Menganalisis dependensi tugas sebagai Directed Acyclic Graph (DAG),
menjalankan topological sorting, dynamic node insertion/splicing saat runtime,
pelacakan causal cone dependensi, serta perhitungan Amdahl concurrency speedup.
"""

import sys
import json
import argparse
from typing import Dict, List, Set, Any, Tuple
from collections import deque, defaultdict


class DAGReplanningEngine:
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[str, Set[str]] = defaultdict(set) # u -> v (u precedes v, v depends on u)
        self.reverse_edges: Dict[str, Set[str]] = defaultdict(set) # v -> u (v depends on u)

    def add_node(self, node_id: str, label: str, duration_ms: float = 100.0, status: str = "pending") -> None:
        self.nodes[node_id] = {
            "id": node_id,
            "label": label,
            "duration_ms": duration_ms,
            "status": status,
            "output": None
        }

    def add_edge(self, from_id: str, to_id: str) -> bool:
        if from_id not in self.nodes or to_id not in self.nodes:
            return False
        # Cek apakah penambahan edge memicu cycle
        if self._would_create_cycle(from_id, to_id):
            return False
        self.edges[from_id].add(to_id)
        self.reverse_edges[to_id].add(from_id)
        return True

    def _would_create_cycle(self, from_id: str, to_id: str) -> bool:
        if from_id == to_id:
            return True
        # BFS dari to_id mencari from_id
        visited = set()
        queue = deque([to_id])
        while queue:
            curr = queue.popleft()
            if curr == from_id:
                return True
            visited.add(curr)
            for neighbor in self.edges.get(curr, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        return False

    def topological_sort(self) -> List[str]:
        in_degree = {nid: len(self.reverse_edges[nid]) for nid in self.nodes}
        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        sorted_nodes = []

        while queue:
            curr = queue.popleft()
            sorted_nodes.append(curr)
            for neighbor in self.edges.get(curr, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_nodes) != len(self.nodes):
            raise ValueError("Deadlock terdeteksi: DAG memiliki siklus!")
        return sorted_nodes

    def get_execution_layers(self) -> List[List[str]]:
        """Membagi node ke dalam layer eksekusi paralel (Sugiyama / K-layered graph)."""
        in_degree = {nid: len(self.reverse_edges[nid]) for nid in self.nodes}
        current_layer = [nid for nid, deg in in_degree.items() if deg == 0]
        layers = []
        visited_count = 0

        while current_layer:
            layers.append(current_layer)
            visited_count += len(current_layer)
            next_layer = []
            for curr in current_layer:
                for neighbor in self.edges.get(curr, []):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_layer.append(neighbor)
            current_layer = next_layer

        if visited_count != len(self.nodes):
            raise ValueError("Deadlock terdeteksi dalam perancangan layer eksekusi!")
        return layers

    def get_causal_cone(self, node_id: str) -> Set[str]:
        """Mencari seluruh downstream dependent nodes (Causal Forward Cone)."""
        cone = set()
        queue = deque([node_id])
        while queue:
            curr = queue.popleft()
            for child in self.edges.get(curr, []):
                if child not in cone:
                    cone.add(child)
                    queue.append(child)
        return cone

    def splice_node(self, target_node_id: str, new_node_id: str, new_label: str, duration_ms: float = 100.0) -> bool:
        """
        Melakukan Dynamic Task Splicing: menyisipkan node baru tepat sebelum target_node_id,
        mengalihkan seluruh upstream dependencies target ke node baru, lalu menghubungkan node baru ke target.
        """
        if target_node_id not in self.nodes or new_node_id in self.nodes:
            return False

        self.add_node(new_node_id, new_label, duration_ms, "pending")
        
        # Ambil dependensi hulu target_node_id
        upstream_nodes = list(self.reverse_edges[target_node_id])
        
        # Hubungkan upstream -> new_node
        for up in upstream_nodes:
            self.edges[up].remove(target_node_id)
            self.reverse_edges[target_node_id].remove(up)
            self.add_edge(up, new_node_id)

        # Hubungkan new_node -> target_node
        self.add_edge(new_node_id, target_node_id)
        return True

    def prune_failed_branch(self, failed_node_id: str) -> Tuple[Set[str], List[str]]:
        """
        Mengisolasi dan memangkas cabang kegagalan (Causal Cone Pruning).
        Menandai failed_node_id sebagai failed, dan seluruh dependent downstream sebagai skipped.
        """
        if failed_node_id not in self.nodes:
            return set(), []

        self.nodes[failed_node_id]["status"] = "failed"
        downstream = self.get_causal_cone(failed_node_id)
        for nid in downstream:
            self.nodes[nid]["status"] = "skipped"

        # Kembalikan daftar node yang masih runnable
        remaining_runnable = [
            nid for nid, data in self.nodes.items()
            if data["status"] in ["pending", "running"]
        ]
        return downstream, remaining_runnable

    def compute_amdahl_metrics(self) -> Dict[str, float]:
        """Menghitung metrik concurrency, critical path, dan theoretical speedup."""
        if not self.nodes:
            return {"serial_duration_ms": 0.0, "critical_path_ms": 0.0, "speedup": 1.0}

        serial_total = sum(data["duration_ms"] for data in self.nodes.values())
        
        # Critical path calculation via DP on DAG
        topo = self.topological_sort()
        earliest_finish = {nid: 0.0 for nid in self.nodes}

        for nid in topo:
            dur = self.nodes[nid]["duration_ms"]
            max_pred = 0.0
            for pred in self.reverse_edges.get(nid, []):
                if earliest_finish[pred] > max_pred:
                    max_pred = earliest_finish[pred]
            earliest_finish[nid] = max_pred + dur

        critical_path = max(earliest_finish.values()) if earliest_finish else 0.0
        theoretical_speedup = serial_total / critical_path if critical_path > 0 else 1.0

        return {
            "serial_duration_ms": round(serial_total, 2),
            "critical_path_ms": round(critical_path, 2),
            "max_theoretical_speedup": round(theoretical_speedup, 2),
            "parallel_concurrency_factor": round((serial_total - critical_path) / serial_total, 3) if serial_total > 0 else 0.0
        }


def build_sample_workflow() -> DAGReplanningEngine:
    engine = DAGReplanningEngine()
    engine.add_node("trigger", "User Intent Ingestion", duration_ms=50.0)
    engine.add_node("planner", "Task Decomposition", duration_ms=120.0)
    
    # 3 Parallel Worker Nodes
    engine.add_node("worker_code", "Codebase Search & Patch", duration_ms=300.0)
    engine.add_node("worker_test", "Unit Test Simulation", duration_ms=250.0)
    engine.add_node("worker_docs", "API Docs Verification", duration_ms=180.0)
    
    engine.add_node("evaluator", "Multi-Agent Consensus QC", duration_ms=150.0)
    engine.add_node("delivery", "Response Dispatch", duration_ms=40.0)

    # Wire DAG
    engine.add_edge("trigger", "planner")
    engine.add_edge("planner", "worker_code")
    engine.add_edge("planner", "worker_test")
    engine.add_edge("planner", "worker_docs")
    
    engine.add_edge("worker_code", "evaluator")
    engine.add_edge("worker_test", "evaluator")
    engine.add_edge("worker_docs", "evaluator")
    
    engine.add_edge("evaluator", "delivery")
    return engine


def main():
    parser = argparse.ArgumentParser(description="DAG Agent Task Splicing & Topological Replanning Engine")
    parser.add_argument("--demo", action="store_true", help="Jalankan simulasi demonstrasi lengkap")
    parser.add_argument("--metrics", action="store_true", help="Tampilkan metrik Amdahl speedup")
    parser.add_argument("--layers", action="store_true", help="Tampilkan Sugiyama parallel execution layers")
    parser.add_argument("--splice", action="store_true", help="Simulasikan dynamic task splicing")
    parser.add_argument("--prune-failed", type=str, help="Simulasikan causal cone pruning saat node gagal")

    args = parser.parse_args()
    engine = build_sample_workflow()

    if args.demo or (not any(vars(args).values())):
        print("=== DAG REPLANNING ENGINE: DEMO RUN ===")
        print("1. Topological Order:")
        topo = engine.topological_sort()
        print(" -> ".join(topo))
        
        print("\n2. Parallel Execution Layers:")
        layers = engine.get_execution_layers()
        for idx, layer in enumerate(layers):
            print(f"  Layer {idx}: {layer}")

        print("\n3. Amdahl Concurrency Metrics:")
        metrics = engine.compute_amdahl_metrics()
        print(json.dumps(metrics, indent=2))

        print("\n4. Simulating Dynamic Splicing (Pre-flight Sanitizer before worker_code):")
        success = engine.splice_node("worker_code", "pre_flight_check", "Static AST Pre-flight Guard", duration_ms=40.0)
        print(f"  Splicing status: {success}")
        print("  New Topological Order:")
        print(" -> ".join(engine.topological_sort()))

        print("\n5. Simulating Causal Cone Pruning on Failure (worker_test fails):")
        pruned, runnable = engine.prune_failed_branch("worker_test")
        print(f"  Pruned downstream cone: {list(pruned)}")
        print(f"  Remaining runnable nodes: {runnable}")
        print("========================================")
        return

    if args.metrics:
        print(json.dumps(engine.compute_amdahl_metrics(), indent=2))

    if args.layers:
        print(json.dumps(engine.get_execution_layers(), indent=2))

    if args.splice:
        engine.splice_node("worker_code", "pre_flight_check", "Static AST Pre-flight Guard", duration_ms=40.0)
        print("Topological order post-splice:")
        print(" -> ".join(engine.topological_sort()))

    if args.prune_failed:
        pruned, runnable = engine.prune_failed_branch(args.prune_failed)
        print(json.dumps({"pruned": list(pruned), "runnable": runnable}, indent=2))


if __name__ == "__main__":
    main()
