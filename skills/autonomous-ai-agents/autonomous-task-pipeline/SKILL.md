---
name: autonomous-task-pipeline
description: "Use when building agent pipelines. Hardens task queues."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [pipeline, kanban, fcntl, concurrency, qa-gates, observability, hitl]
---

# Autonomous Multi-Agent Task Pipeline

Instructions for building, hardening, and operating multi-agent task execution pipelines with atomic locking, bounded concurrency, deterministic QA verification, and public observability cockpits.

## Procedure

1. **Implement Atomic State Locking (Anti-Race Condition)**:
   - For file-backed queues (e.g., `tasks.json`), never perform direct unbounded `json.dump()` writes.
   - Use OS-level advisory file locking (`fcntl` on Linux/macOS):
     - Shared lock (`fcntl.LOCK_SH`) for read operations.
     - Exclusive lock (`fcntl.LOCK_EX`) on a temporary file (`.tmp.<pid>`), followed by `os.fsync()` and an atomic `os.replace()` to swap into the target path.
   - Guard against write contention across concurrent worker processes, CLI tools, and web dispatch endpoints.

2. **Bound Worker Concurrency (Anti-Thrashing)**:
   - Avoid single-threaded head-of-line blocking while preventing VPS resource exhaustion.
   - Run worker threads via `concurrent.futures.ThreadPoolExecutor(max_workers=2)` (or an equivalent bounded pool).
   - Allow independent tasks to execute concurrently while ensuring system RAM and CPU remain within safe limits.

3. **Enforce Deterministic QA Gates (Anti-Heuristic Passing)**:
   - Never consider a task verified simply because the output length exceeds a character threshold (`len(text) > 50`).
   - Extract code blocks and validate deterministically:
     - Python blocks: Parse using `ast.parse()` to catch `SyntaxError` before acceptance.
     - JSON blocks: Validate with `json.loads()`.
     - Structured domain deliverables: Verify required structural contracts (e.g., exactly 4 slides for SputarAI carousels, concrete schema configs for backend tasks).
   - If QA checks fail, route the task to a `review` stage with specific diagnostic failure notes rather than marking it `done`.

4. **Wrap Local Gateway Calls with Exponential Backoff**:
   - Model routers or local LLM gateways may experience temporary latency spikes, rate limits, or transient connection errors.
   - Implement exponential backoff retry loops (3 attempts with delays of 2s -> 4s -> 8s) before failing a task or releasing its claim lock.

5. **Expose Public Observability & Human-in-the-Loop (HITL) Controls**:
   - Do not isolate autonomous agent pipelines inside terminal CLI sessions.
   - Expose a responsive web cockpit (e.g., `/studio/`) with sub-2-second auto-polling or SSE.
   - Provide visibility into the 7-stage kanban pipeline (`planning`, `inbox`, `assigned`, `in_progress`, `testing`, `review`, `done`), specialist fleet status (`ACTIVE` vs `IDLE`), and raw deliverable previews.
   - Include HITL actions (Approve / Request Revision) for tasks in `review` and an interactive dispatch console.

6. **Automate Artifact Retention**:
   - Store generated outputs in structured artifact directories (`.runtime/artifacts/`).
   - Implement an automated retention policy: archive or compress files exceeding capacity limits (e.g., > 50 files) or aging thresholds (> 30 days) into an archive subfolder with an index ledger.

## Pitfalls

- Length-based QA checks (`len(output) > 50`) silently approve invalid syntax and hallucinated code; always enforce deterministic AST or schema parsing before marking tasks complete.
- Unlocked file writes across multiple processes cause silent data loss and corrupted JSON; always pair state persistence with `fcntl.LOCK_EX` and atomic replacement.
- Unbounded asynchronous task dispatching triggers VPS memory thrashing and OOM killer termination; always enforce hard worker pool limits (`max_workers=2`).
- Restricting agent visibility to terminal commands leaves users unaware of background execution status; always expose a lightweight public web cockpit with live status feeds.
- Rendering raw terminal logs in the web cockpit without stripping ANSI escape codes leaves `\x1b[...]` artifacts; always sanitize string streams with an ANSI regex filter before DOM injection.
