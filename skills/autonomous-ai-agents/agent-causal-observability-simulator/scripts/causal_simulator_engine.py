"""
Causal Observability & Latency/Resource Intervention Simulator Engine
Algoritma deterministik untuk memodelkan trace eksekusi agen otonom sebagai Structural Causal Model (SCM),
melakukan intervensi Pearl do(X=x) pada latensi/alokasi sumber daya,
mengidentifikasi jalur kritis (Amdahl Bottleneck), dan menguji batas invarian.
"""

from typing import Dict, List, Set, Any, Optional
import copy
import math


class CausalNode:
    def __init__(self, name: str, base_latency_ms: float, base_ram_mb: float, base_cost_usd: float = 0.0):
        self.name = name
        self.base_latency_ms = float(base_latency_ms)
        self.base_ram_mb = float(base_ram_mb)
        self.base_cost_usd = float(base_cost_usd)
        
        # Intervened values (None jika mengikuti factual/base)
        self.intervened_latency_ms: Optional[float] = None
        self.intervened_ram_mb: Optional[float] = None
        self.intervened_cost_usd: Optional[float] = None

    @property
    def latency(self) -> float:
        return self.intervened_latency_ms if self.intervened_latency_ms is not None else self.base_latency_ms

    @property
    def ram(self) -> float:
        return self.intervened_ram_mb if self.intervened_ram_mb is not None else self.base_ram_mb

    @property
    def cost(self) -> float:
        return self.intervened_cost_usd if self.intervened_cost_usd is not None else self.base_cost_usd


class CausalObservabilitySimulator:
    def __init__(self, ram_limit_mb: float = 9000.0, max_latency_ceiling_ms: float = 30000.0):
        self.ram_limit_mb = float(ram_limit_mb)
        self.max_latency_ceiling_ms = float(max_latency_ceiling_ms)
        self.nodes: Dict[str, CausalNode] = {}
        self.edges: Dict[str, List[str]] = {}  # parent -> children
        self.parents: Dict[str, List[str]] = {} # child -> parents

    def add_node(self, name: str, base_latency_ms: float, base_ram_mb: float, base_cost_usd: float = 0.0) -> None:
        if name in self.nodes:
            raise ValueError(f"Node '{name}' sudah terdaftar dalam graph.")
        self.nodes[name] = CausalNode(name, base_latency_ms, base_ram_mb, base_cost_usd)
        self.edges[name] = []
        self.parents[name] = []

    def add_causal_edge(self, parent: str, child: str) -> None:
        if parent not in self.nodes or child not in self.nodes:
            raise KeyError(f"Node '{parent}' atau '{child}' tidak ditemukan.")
        if child in self.edges[parent]:
            return
        
        # Validasi DAG (anti-cycle check)
        self.edges[parent].append(child)
        self.parents[child].append(parent)
        if self._has_cycle():
            self.edges[parent].remove(child)
            self.parents[child].remove(parent)
            raise ValueError(f"Siklus terdeteksi saat menambahkan relasi kausal {parent} -> {child}.")

    def _has_cycle(self) -> bool:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self.edges.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in self.nodes:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def topological_sort(self) -> List[str]:
        in_degree = {n: len(self.parents[n]) for n in self.nodes}
        queue = [n for n, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for child in self.edges[curr]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if len(order) != len(self.nodes):
            raise RuntimeError("Topological sort gagal: terdapat siklus tersembunyi.")
        return order

    def compute_critical_path(self) -> Dict[str, Any]:
        """
        Menghitung jalur kritis (Critical Path) berbasis ketergantungan DAG:
        Earliest Start (ES) dan Earliest Finish (EF) untuk setiap node.
        """
        order = self.topological_sort()
        es: Dict[str, float] = {n: 0.0 for n in self.nodes}
        ef: Dict[str, float] = {n: 0.0 for n in self.nodes}

        for n in order:
            node = self.nodes[n]
            if self.parents[n]:
                es[n] = max(ef[p] for p in self.parents[n])
            else:
                es[n] = 0.0
            ef[n] = es[n] + node.latency

        total_critical_latency = max(ef.values()) if ef else 0.0

        # Backtrack untuk menemukan jalur kritis (Critical Path Sequence)
        # Cari node akhir dengan ef maksimal
        end_nodes = [n for n in self.nodes if len(self.edges[n]) == 0]
        if not end_nodes:
            end_nodes = list(self.nodes.keys())
        
        last_node = max(end_nodes, key=lambda x: ef[x]) if end_nodes else None
        critical_path = []
        curr = last_node
        while curr:
            critical_path.append(curr)
            if self.parents[curr]:
                # Pilih parent yang ef-nya menyumbang start curr
                curr = max(self.parents[curr], key=lambda p: ef[p])
            else:
                curr = None
        critical_path.reverse()

        # Hitung kontribusi Amdahl untuk setiap node terhadap total critical path latency
        amdahl_contributions = {}
        for n in self.nodes:
            p_fraction = (self.nodes[n].latency / total_critical_latency) if total_critical_latency > 0 else 0.0
            amdahl_contributions[n] = round(p_fraction, 4)

        # Hitung peak RAM (concurrency envelope atau worst-case sum of parallel stages)
        peak_ram_mb = sum(node.ram for node in self.nodes.values())
        total_cost = sum(node.cost for node in self.nodes.values())

        return {
            "critical_path": critical_path,
            "total_latency_ms": round(total_critical_latency, 2),
            "peak_ram_mb": round(peak_ram_mb, 2),
            "total_cost_usd": round(total_cost, 4),
            "earliest_start": es,
            "earliest_finish": ef,
            "amdahl_contributions": amdahl_contributions,
            "bottleneck_node": critical_path[-1] if critical_path else None
        }

    def simulate_do_intervention(self, interventions: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Menerapkan Pearl Do-Calculus do(Node = {latency: x, ram: y, cost: z}).
        Memutus ketergantungan empiris node tersebut dan mengevaluasi sistem counterfactual.
        """
        # Simpan state awal untuk rollback/comparison
        original_states = {}
        for n, vals in interventions.items():
            if n not in self.nodes:
                raise KeyError(f"Node '{n}' tidak valid untuk intervensi.")
            node = self.nodes[n]
            original_states[n] = (node.intervened_latency_ms, node.intervened_ram_mb, node.intervened_cost_usd)
            
            if "latency_ms" in vals:
                node.intervened_latency_ms = float(vals["latency_ms"])
            if "ram_mb" in vals:
                node.intervened_ram_mb = float(vals["ram_mb"])
            if "cost_usd" in vals:
                node.intervened_cost_usd = float(vals["cost_usd"])

        # Evaluasi metrik counterfactual
        counterfactual_metrics = self.compute_critical_path()

        # Reset intervensi agar simulator tetap bersih
        for n, (old_lat, old_ram, old_cost) in original_states.items():
            node = self.nodes[n]
            node.intervened_latency_ms = old_lat
            node.intervened_ram_mb = old_ram
            node.intervened_cost_usd = old_cost

        return counterfactual_metrics

    def evaluate_invariant_bounds(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluasi apakah hasil intervensi memenuhi kendala keras g(x) <= 0:
        1. Peak RAM <= ram_limit_mb (default 9000 MB)
        2. Total Latency <= max_latency_ceiling_ms (default 30000 ms)
        """
        ram_breached = metrics["peak_ram_mb"] > self.ram_limit_mb
        latency_breached = metrics["total_latency_ms"] > self.max_latency_ceiling_ms

        passed = (not ram_breached) and (not latency_breached)
        return {
            "passed": passed,
            "ram_breached": ram_breached,
            "latency_breached": latency_breached,
            "ram_headroom_mb": round(self.ram_limit_mb - metrics["peak_ram_mb"], 2),
            "latency_headroom_ms": round(self.max_latency_ceiling_ms - metrics["total_latency_ms"], 2)
        }

    def compute_amdahl_theoretical_speedup(self, target_node: str, speedup_factor: float) -> float:
        """
        Menghitung theoretical speedup batas Amdahl:
        S = 1 / ((1 - p) + p / s)
        di mana p adalah fraksi kontribusi target_node terhadap critical path.
        """
        base_metrics = self.compute_critical_path()
        p = base_metrics["amdahl_contributions"].get(target_node, 0.0)
        if p == 0.0 or speedup_factor <= 0.0:
            return 1.0
        
        speedup = 1.0 / ((1.0 - p) + (p / speedup_factor))
        return round(speedup, 4)
