#!/usr/bin/env python3
"""
Live Intervention Splicing & Dynamic Topological Task Rescheduling Engine.
Implements:
1. In-flight DAG task representation with runtime task states.
2. Causal Cone Downstream Invalidation upon intervention / tool mutation.
3. Live Task Splicing with cycle rejection (Acyclic Invariant).
4. Dynamic Kahn's Topological Rescheduling preserving completed work.
5. Invariant State Preservation & Resource Budget Gating.
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import copy
import json
import time


class TaskState(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    INVALIDATED = "INVALIDATED"
    SKIPPED = "SKIPPED"


@dataclass
class TaskNode:
    task_id: str
    name: str
    action: str
    estimated_duration_ms: float = 100.0
    actual_duration_ms: Optional[float] = None
    state: TaskState = TaskState.PENDING
    payload: Dict = field(default_factory=dict)
    output: Optional[Dict] = None
    metadata: Dict = field(default_factory=dict)


class DAGCycleError(ValueError):
    """Raised when an intervention introduces a circular dependency."""
    pass


class SplicingConflictError(RuntimeError):
    """Raised when splicing violates active execution invariants."""
    pass


class InterventionDAGSplicer:
    def __init__(self, dag_id: str = "agent-runtime-dag"):
        self.dag_id = dag_id
        self.nodes: Dict[str, TaskNode] = {}
        # edges: u -> [v] meaning v depends on u (u must complete before v)
        self.edges: Dict[str, Set[str]] = defaultdict(set)
        # reverse edges: v -> [u] meaning dependencies of v
        self.rev_edges: Dict[str, Set[str]] = defaultdict(set)
        self.splicing_history: List[Dict] = []

    def add_task(self, node: TaskNode, dependencies: Optional[List[str]] = None) -> None:
        """Add a new task node with its prerequisites."""
        if node.task_id in self.nodes:
            raise ValueError(f"Task {node.task_id} already exists in DAG.")
        self.nodes[node.task_id] = node
        dependencies = dependencies or []
        for dep in dependencies:
            if dep not in self.nodes:
                raise ValueError(f"Dependency {dep} does not exist in DAG.")
            self.edges[dep].add(node.task_id)
            self.rev_edges[node.task_id].add(dep)

    def detect_cycle(self) -> bool:
        """Kahn's cycle detection algorithm on active DAG."""
        in_degree = {t_id: len(self.rev_edges.get(t_id, set())) for t_id in self.nodes}
        queue = deque([t_id for t_id, deg in in_degree.items() if deg == 0])
        visited_count = 0

        while queue:
            curr = queue.popleft()
            visited_count += 1
            for child in self.edges[curr]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        return visited_count < len(self.nodes)

    def get_causal_downstream_cone(self, source_task_id: str) -> Set[str]:
        """
        Calculates the causal cone: all downstream reachable nodes from source_task_id.
        These nodes must be invalidated if the output/contract of source_task_id is altered.
        """
        if source_task_id not in self.nodes:
            raise ValueError(f"Task {source_task_id} not found in DAG.")

        downstream: Set[str] = set()
        queue = deque(list(self.edges[source_task_id]))

        while queue:
            curr = queue.popleft()
            if curr not in downstream:
                downstream.add(curr)
                for child in self.edges[curr]:
                    if child not in downstream:
                        queue.append(child)

        return downstream

    def invalidate_causal_cone(self, source_task_id: str, reason: str = "Intervention mutation") -> List[str]:
        """
        Invalidates all downstream tasks that depend on the intervened node.
        Completed tasks in the cone are marked INVALIDATED to trigger recalculation.
        Running tasks are flagged for cooperative cancellation.
        """
        affected = self.get_causal_downstream_cone(source_task_id)
        invalidated_tasks = []

        for t_id in affected:
            node = self.nodes[t_id]
            if node.state in (TaskState.COMPLETED, TaskState.PENDING):
                node.state = TaskState.INVALIDATED
                node.metadata["invalidation_reason"] = reason
                node.metadata["invalidated_by"] = source_task_id
                invalidated_tasks.append(t_id)
            elif node.state == TaskState.RUNNING:
                node.state = TaskState.INVALIDATED
                node.metadata["cancellation_requested"] = True
                node.metadata["invalidation_reason"] = reason
                invalidated_tasks.append(t_id)

        return invalidated_tasks

    def splice_intervention_nodes(
        self,
        intervention_nodes: List[TaskNode],
        splice_edges: List[Tuple[str, str]],
        remove_edges: Optional[List[Tuple[str, str]]] = None,
        reason: str = "Live Intervention"
    ) -> Dict:
        """
        Live Task Splicing with Atomic Transactional Rollback:
        1. Backs up current topology.
        2. Applies node injections and edge mutations.
        3. Validates Acyclic Invariant (no cycle introduced).
        4. If cycle detected, rolls back instantly.
        5. Invalidates downstream causal cone.
        """
        # Backup state
        backup_nodes = {k: copy.deepcopy(v) for k, v in self.nodes.items()}
        backup_edges = {k: set(v) for k, v in self.edges.items()}
        backup_rev_edges = {k: set(v) for k, v in self.rev_edges.items()}

        try:
            # 1. Insert new nodes
            for node in intervention_nodes:
                if node.task_id in self.nodes:
                    raise SplicingConflictError(f"Cannot splice existing node {node.task_id}.")
                self.nodes[node.task_id] = node

            # 2. Remove specified obsolete edges
            if remove_edges:
                for u, v in remove_edges:
                    if u in self.edges and v in self.edges[u]:
                        self.edges[u].remove(v)
                    if v in self.rev_edges and u in self.rev_edges[v]:
                        self.rev_edges[v].remove(u)

            # 3. Add new splice edges
            for u, v in splice_edges:
                if u not in self.nodes or v not in self.nodes:
                    raise ValueError(f"Splice edge ({u} -> {v}) references non-existent node.")
                self.edges[u].add(v)
                self.rev_edges[v].add(u)

            # 4. Cycle check (Hard Invariant)
            if self.detect_cycle():
                raise DAGCycleError("Intervention splicing introduces a cyclical dependency!")

            # 5. Invalidate downstream causal cones from injected nodes
            total_invalidated = set()
            for node in intervention_nodes:
                inv = self.invalidate_causal_cone(node.task_id, reason=reason)
                total_invalidated.update(inv)

            splice_record = {
                "timestamp": time.time(),
                "reason": reason,
                "injected_nodes": [n.task_id for n in intervention_nodes],
                "added_edges": splice_edges,
                "removed_edges": remove_edges or [],
                "invalidated_downstream": list(total_invalidated),
                "status": "SUCCESS"
            }
            self.splicing_history.append(splice_record)
            return splice_record

        except Exception as e:
            # Rollback
            self.nodes = backup_nodes
            self.edges = defaultdict(set, {k: set(v) for k, v in backup_edges.items()})
            self.rev_edges = defaultdict(set, {k: set(v) for k, v in backup_rev_edges.items()})
            raise e

    def reschedule_topological_order(self) -> List[str]:
        """
        Dynamic Kahn's Topological Rescheduling.
        Returns executable order for all uncompleted or invalidated tasks.
        Preserves COMPLETED tasks and positions INVALIDATED tasks for re-execution.
        """
        # Calculate in-degrees considering only non-completed dependencies or dependencies needing re-run
        in_degree = defaultdict(int)
        for t_id in self.nodes:
            in_degree[t_id] = 0

        # Build in-degrees for pending/invalidated tasks
        for u in self.nodes:
            # If u is COMPLETED and not invalidated, its downstream dependencies consider u satisfied
            if self.nodes[u].state == TaskState.COMPLETED:
                continue
            for v in self.edges[u]:
                in_degree[v] += 1

        # Tasks ready for execution: in_degree == 0 and not COMPLETED
        queue = deque([
            t_id for t_id in self.nodes
            if in_degree[t_id] == 0 and self.nodes[t_id].state in (TaskState.PENDING, TaskState.INVALIDATED)
        ])

        execution_order = []
        visited = set()

        while queue:
            curr = queue.popleft()
            if curr in visited:
                continue
            visited.add(curr)
            execution_order.append(curr)

            for child in self.edges[curr]:
                in_degree[child] -= 1
                if in_degree[child] == 0 and self.nodes[child].state in (TaskState.PENDING, TaskState.INVALIDATED):
                    queue.append(child)

        return execution_order

    def calculate_amdahl_schedule_speedup(self, parallel_workers: int = 4) -> Dict:
        """
        Calculates theoretical Amdahl speedup for remaining schedule:
        S = 1 / ((1 - p) + p / N)
        Identifies critical sequential bottleneck vs parallelizable branches.
        """
        sched = self.reschedule_topological_order()
        if not sched:
            return {"speedup": 1.0, "parallel_fraction": 0.0, "total_remaining_ms": 0.0}

        total_time = sum(self.nodes[t].estimated_duration_ms for t in sched)
        # Determine concurrency layers via longest path
        in_deg = defaultdict(int)
        for u in sched:
            for v in self.edges[u]:
                if v in sched:
                    in_deg[v] += 1

        layers = defaultdict(list)
        dist = {t: 0 for t in sched}
        q = deque([t for t in sched if in_deg[t] == 0])

        while q:
            curr = q.popleft()
            layers[dist[curr]].append(curr)
            for child in self.edges[curr]:
                if child in sched:
                    in_deg[child] -= 1
                    if dist[child] < dist[curr] + 1:
                        dist[child] = dist[curr] + 1
                    if in_deg[child] == 0:
                        q.append(child)

        critical_path_time = sum(
            max((self.nodes[t].estimated_duration_ms for t in layer), default=0.0)
            for layer in layers.values()
        )

        p = 1.0 - (critical_path_time / total_time) if total_time > 0 else 0.0
        p = max(0.0, min(1.0, p))
        s = 1.0 / ((1.0 - p) + (p / parallel_workers)) if ((1.0 - p) + (p / parallel_workers)) > 0 else 1.0

        return {
            "parallel_fraction": round(p, 4),
            "theoretical_speedup": round(s, 2),
            "critical_path_ms": critical_path_time,
            "total_sequential_ms": total_time,
            "concurrency_layers": len(layers)
        }
