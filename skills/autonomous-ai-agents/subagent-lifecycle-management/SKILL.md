---
name: subagent-lifecycle-management
description: Manage hierarchical sub-agents with strict verification.
version: 0.1.0
author: Hermes Agent
license: MIT
related_skills:
  - autonomous-orchestrator
  - comprehensive-agent-governance
  - structured-project-execution
  - long-horizon-app-building
metadata:
  hermes:
    tags:
      - SubAgentManagement
      - Orchestration
      - MultiAgent
      - SparseFileAllocation
      - AntiABS
---

# Sub-Agent Lifecycle Management & Hierarchical Delegation

Architect, dispatch, monitor, and verify autonomous sub-agents across the 3-generation hierarchy (Level 1 Induk, Level 2 Anak / Tiga Serangkai, Level 3 Cucu / Ephemeral Specialists). Enforces sparse file isolation, contention locks, live telemetry status cards, and strict post-landing verification (Anti-ABS) where the parent agent independently inspects on-disk artifacts before claiming completion.

## When to Use
- User asks: "gimana kabar sub agent", "delegasikan ke tim", "buat sub agent untuk kerjakan ini", or "jalankan formasi multi-agent".
- Complex, long-running, or noisy technical tasks (deep code refactoring, parallel scraping, heavy test suites).
- Preventing parent context pollution by offloading voluminous log audits or multi-file research to isolated children.

## Prerequisites
- Hermes runtime with `delegate_task` tool enabled.
- Telemetry script at `/home/ubuntu/.hermes/scripts/subagent_telemetry.py`.
- Working directory: `/home/ubuntu`.

## How to Run
Invoke sub-agent management and dispatch through Hermes tools:
- Dispatch children using `delegate_task`.
- Track active sub-agents via `delegate_task(action='list')` and corroborate with parent agent logs containing `subagent_id`; the registry-backed `subagent_telemetry.py` may be empty even while a child is running. Never treat an IDLE card as conclusive.
- Verify returned artifacts using `read_file`, `search_files`, and `terminal`.
- For a specific child session, run `python3 /home/ubuntu/.hermes/profiles/bikagent/scripts/evaluate_subagent.py <exact_session_id>`; it scans only matching log lines and reports end status, duration, stream drops, API failures, and tool errors. `NO_END_IN_LOG` is unknown, not stuck; content quality still needs independent artifact review.

## Quick Reference
- **The 3-Generation Hierarchy:**
  - *Level 1 (Induk / General Manager):* Deconstructs user intent, designs task DAG, and coordinates delivery.
  - *Level 2 (Anak / Kabinet Tiga Serangkai):* Si Pintar (Architecture/Specs), Si Eksekutor (Implementation/Spawning), Si Pengawas (QC/Veto).
  - *Level 3 (Cucu / Ephemeral Workers):* `subagent-frontend`, `subagent-backend`, `subagent-database`, `subagent-qc-tester`.
- **Sparse File Allocation Rule:** Each sub-agent is assigned strictly isolated target files. Never grant open folder write permissions.
- **No File Contention:** Two sub-agents must NEVER edit the same file concurrently.
- **Honest correction, not QC veto:** Si Pengawas appends evidenced shortcomings, impact, and a suggested fix. Do not reject/repeat a user instruction or block the whole workflow because a QC report is incomplete. The parent still verifies actual artifacts before claiming done; unsafe publication/deploy actions remain subject to independent permission and safety checks.
- **Air-Gapped Confidential Profile Isolation:** When an agent profile (e.g. Koagent) is designated for sensitive operations (credentials, production VPS, real databases), strictly isolate it: 1) Strict DM-Only Telegram channel (never add to shared multi-agent groups); 2) Zero Cross-Agent Inquiry (other agents strictly forbidden from searching, inspecting, or delegating tasks to its private profile directory `~/.hermes/profiles/<name>/`); 3) Filesystem Quarantine (mode 0700 on internal workspace); 4) Zero Public Logging (exempt from automated public vault indexing and status feeds).

## Procedure

1. **Pre-Dispatch Contention & Boundary Check:**
   Before calling `delegate_task`, register intended child file allocations:
   - Identify explicit target files for Worker A and Worker B.
   - Assert zero overlap between claimed file paths.

2. **Formulate High-Context Dispatch Payload:**
   Set acceptance criteria and a time budget before dispatch. For read-only diagnosis, bound scope to named logs/time range and require citations; avoid launching another costly child merely to assess status. If a task exceeds its budget, inspect `delegate_task(action='list')` and steer/stop deliberately, not a blind retry. Do not claim a shorter runtime until measured in a subsequent comparable run.
   Because sub-agents start with fresh, isolated context, provide complete context:
   - Absolute file paths and exact function names.
   - Project constraints and forbidden paths (e.g. "Do not mutate production configs").
   - Explicit expected output format (`output_schema` or clean summary).

3. **Dispatch via `delegate_task`:**
   Execute parallel sub-agents:
   ```python
   delegate_task(tasks=[
       {
           "goal": "Refactor backend API routing and enforce session path lock",
           "context": "Working directory: /home/ubuntu/app. Target file: server.js. Constraint: Keep port 3050."
       },
       {
           "goal": "Implement responsive table view without horizontal overflow",
           "context": "Working directory: /home/ubuntu/app. Target file: public/index.html. Constraint: Follow upnormal UI."
       }
   ])
   ```

4. **Emit Real-Time Telegram Status Card:**
   Display visual progress to the user:
   ```text
   ┌ 👶 [Anak] Si Eksekutor (ID: subagent-101)
   ├ 🎯 Tugas: Implementasi routing subpath /kasir-bangunan
   ├ 🔒 File Terisolasi: server.js
   └ ⏱️ Durasi: 24s · Status: 🔄 RUNNING
   ```

5. **Post-Landing Evidence & Correction (Anti-ABS):**
   When `delegate_task` returns:
   - Do NOT immediately declare victory.
   - Use `read_file` or `search_files` to verify claimed changes and a relevant runtime check via `terminal`.
   - Si Pengawas contributes an additive correction report: observed evidence, shortcomings, impact, and proposed remedy; no PASS/REJECT/VETO or forced repetition loop.
   - Deliver verified achievements and unresolved limitations together. A report cannot authorize an unsafe external action; permissions and safety gates are separate from QC.

## Pitfalls
- **Blind Courier Anti-Pattern:** Regurgitating a sub-agent's self-report without running real verification commands.
- **Context Starvation:** Sending a one-line goal to a sub-agent without file paths or environment constraints; child will guess or fail.
- **Parallel Race Conditions:** Assigning two sub-agents to edit the same file simultaneously, causing overwritten code.
- **Sub-Agent Sprawl:** Spawning >5 sub-agents for trivial tasks; creates token waste and latency. Keep to `2 <= N <= 5` for complex tasks, or handle directly for micro-tasks.
- **Provider latency vs task quality:** Evaluate elapsed time, stream retries, tool failures, and verified artifact/result separately. An HTTP 200 without finish reason is not a completed answer; profile CLI activity is not `delegate_task` activity.
- **Exact skill names:** Never append suffixes or invented file paths to `skill_view` names; a failed lookup is a tool-use error, not evidence of a missing capability. After one bad-name error, copy the exact name from available skills and retry once.
- **Cross-Agent Confidentiality Bleed:** Allowing shared team agents to inspect, delegate to, or log an air-gapped sensitive agent's workspace or sessions. Sensitive profiles must be explicitly quarantined from multi-agent registries, audit cycles, and public document summarization.

## Verification
Execute the sub-agent telemetry harness check via `terminal`:
`python3 /home/ubuntu/.hermes/scripts/subagent_telemetry.py`
Verify output initializes cleanly. Empty manual registry must say delegate_task status TIDAK DIKETAHUI, not IDLE; cross-check `delegate_task(action='list')`. Test empty, active, and settled states using a temporary synthetic registry rather than mutating production registry.
