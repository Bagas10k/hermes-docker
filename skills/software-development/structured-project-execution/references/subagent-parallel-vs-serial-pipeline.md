# Sub-Agent Concurrency: Parallel Execution vs Serial Estafet Pipelines

Optimizing sub-agent orchestration based on task dependencies, runtime concurrency bounds, and file contention rules.

## 1. Runtime Concurrency Reality
When sub-agents are spawned via `delegate_task(tasks=[...])`:
- The underlying runtime executes all items in the array **simultaneously in parallel**.
- Each sub-agent runs in an isolated process, dedicated terminal session, and clean context window.
- Sub-agents do not block each other at the CPU or token level.

---

## 2. Choosing Between Parallel (Scatter-Gather) vs Serial (Estafet)

| Architecture | Execution Mode | Trigger Condition | Example Workflow |
|---|---|---|---|
| **Serial Estafet (Pipeline DAG)** | Sequential / Turn-based handoff | Task B strictly requires Task A's output as an immutable input. | Cabinet Tri-Role: 1. Si Pintar drafts Spec ➔ 2. Si Eksekutor writes code ➔ 3. Si Pengawas audits QC. |
| **Parallel Scatter-Gather** | Simultaneous concurrent execution | Tasks are independent with zero shared resource contention. | Worker Triad: 1. Worker Frontend (`index.html`) + 2. Worker Backend (`server.js`) + 3. Worker DB (`schema.sql`). |
| **Hybrid Fan-Out / Fan-In** | Serial phase gate containing parallel sub-tasks | High-level milestones depend on prior phase, but work within phase is divisible. | Phase 1 (Serial DB Setup) ➔ Phase 2 (Parallel API + UI construction) ➔ Phase 3 (Serial E2E verification). |

---

## 3. Sparse File Allocation (Contention Lock)
To safely run sub-agents in parallel without merge conflicts or lost work:
1. **Strict File Isolation:** Assign explicit, non-overlapping target files to each worker.
2. **Directory Write Ban:** Never give two concurrent workers open write permissions to the same directory.
3. **Parent Assembly Barrier:** The parent agent coordinates file integration only after both children finish and report their verified diffs.
