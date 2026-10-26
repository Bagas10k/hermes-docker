---
name: structured-project-execution
description: Execute structured project workflows and task DAG phases.
version: 0.1.0
author: Hermes Agent
license: MIT
related_skills:
  - long-horizon-app-building
  - upnormal-ui-architecture
  - subagent-lifecycle-management
  - fullstack-systems
metadata:
  hermes:
    tags:
      - ProjectExecution
      - StructuredWorkflow
      - TaskDAG
      - TwoPhaseBuild
      - AntiCowboyCoding
      - AntiABS
---

# Structured Project Execution & Workflow Engineering

Orchestrate complex software and system development through structured Directed Acyclic Graph (DAG) phases and strict milestones. Eliminates reactive cowboy coding, silent execution, cognitive overload, and unverified success claims through a mandatory Two-Phase build workflow and the 5-Stage Flight Plan.

## When to Use
- Building new applications, dashboards, or multi-tier services from scratch.
- Executing multi-step engineering tasks requiring sequential or parallel sub-phases.
- Preventing cognitive overload during web construction by separating structure from aesthetic styling.
- Major refactoring, database migrations, or public reverse proxy cutovers.

## Prerequisites
- Target runtime environment (Node.js, Python, PHP, or Go) accessible via `terminal`.
- Execution state tracking file at `build_tracker.json` in the current working directory.
- Standard Python 3 runtime for the tracker script (`scripts/flight_plan_tracker.py`).

## How to Run
Initialize and track the project flight plan using the `terminal` tool:
```bash
# Initialize a new project flight plan
python3 scripts/flight_plan_tracker.py --init "Project Name"

# Update active stage status
python3 scripts/flight_plan_tracker.py --set-stage 1 --state completed --proof "HTTP 200"

# Confirm aesthetic vibe with user
python3 scripts/flight_plan_tracker.py --vibe "Swiss Editorial Modern"

# View current DAG progress
python3 scripts/flight_plan_tracker.py --status
```

## Quick Reference
- **The Two-Phase Engineering Law:**
  - *Phase 1:* Structure & Function First (Grid layout, DB schema, API CRUD, state management, barebones wireframe).
  - *Checkpoint:* Vibe & Theme Confirmation (Ask user: Elegant, Fun, Industrial, Swiss, etc.).
  - *Phase 2:* Aesthetic Craftsmanship (Live internet reference query + 5 Hermes Taste Lenses).
- **The 5-Stage Flight Plan:**
  - Stage 1: Discovery & System Audit (Port & DB inspection).
  - Stage 2: Public Task DAG Checklist (Numbered roadmap in opening turn).
  - Stage 3: Contract Lockdown (Deterministic finish line: exit code 0 / HTTP 200).
  - Stage 4: Bounded Sprint & Micro-Milestone Pulse (30-minute job ceiling, at most 3 attempts per same error, max 60-second silence). When a limit is reached, stop the loop and explain results, evidence, unresolved work and risks. End incomplete work with explicit **Continue** (remaining tasks, added estimate, risks, next verification) versus **Pause/Stop** (safe state), recommend one, and wait for user approval before a new contract.
  - Stage 5: Fixed Evaluation Gate & Atomic Promotion (Independent QC audit).
- **Anti-ABS Rule:** Never claim completion without direct runtime evidence (`KNOWN`, `LIKELY`, `UNCERTAIN`, `UNKNOWN`).

## Procedure

1. **Conduct Discovery & System Audit (Stage 1):**
   Inspect the existing runtime environment using `terminal` commands (`ss -tulpn`, `pm2 list`). Identify existing database tables and port allocations. Define explicit boundary paths and assert zero duplication.

2. **Publish the Public Task DAG (Stage 2):**
   Initialize the DAG tracker with `scripts/flight_plan_tracker.py --init "<Project Name>"` via `terminal`. Present the numbered checklist to the user in the opening turn:
   ```text
   📋 RENCANA EKSEKUSI PROYEK:
   • ⏳ 1. [Fondasi] Setup skema database & model
   • ⏳ 2. [Backend] Routing API CRUD & wireframe grid
   • ⏳ 3. [Checkpoint] Konfirmasi vibe & tema visual dengan user
   • ⏳ 4. [Frontend] Pematangan style Upnormal (Live Search + 5 Lensa)
   • ⏳ 5. [Verifikasi] Uji E2E login/transaksi & rilis produksi
   ```

3. **Execute Phase 1 — Structural Grid & Functional Engine:**
   Scaffold CSS Grid/Flexbox containers, database migrations, backend routes, and basic CRUD handling. Keep visuals clean, neutral, and barebones. Update tracker milestone via `terminal`:
   ```bash
   python3 scripts/flight_plan_tracker.py --set-stage 2 --state completed --proof "CRUD Endpoints Verified"
   ```

4. **Execute Checkpoint — Confirm Vibe with User:**
   Pause execution once Phase 1 is verified running. Ask the user directly:
   *"Sistem dasar dan tata letak grid sudah berjalan stabil. Untuk tahap pematangan visual, Mas Bagas ingin tema dan vibe rasanya seperti apa (misal: Elegan, Fun Neo-Brutalist, Industrial HUD, Swiss Modern, dll)?"*
   Record the confirmed theme:
   ```bash
   python3 scripts/flight_plan_tracker.py --vibe "Swiss Modern"
   ```

5. **Execute Phase 2 — Aesthetic Craftsmanship & Upnormal Styling:**
   Active web reconnaissance is mandatory before styling. Search live internet references matching the confirmed vibe (`web_search`), rather than relying on model training weights. Filter candidates through the 5 Hermes Taste Lenses (WCAG AAA >= 7:1, 60 FPS in-place morphing, custom anti-native controls, direct text branding). Polish the interface without breaking Phase 1 functional invariants.

6. **Conduct Independent QC Audit & Atomic Promotion (Stage 5):**
   Execute deterministic curl commands and unit test suites via `terminal`. Assert exit code 0 and zero regressions. Promote changes atomically and record lessons to knowledge storage.

## References
Load deep architectural references on demand using `skill_view` (`name="structured-project-execution"`, `file_path="references/<file>"`):
- `references/two-phase-system-then-vibe.md`: Complete specification for separating structural wireframes from vibe-driven aesthetic styling.
- `references/five-stage-flight-plan.md`: Discovery, Public Task DAG, Contract Lockdown, Bounded Sprint with 60s pulse, and Fixed Evaluation Gate.
- `references/subagent-parallel-vs-serial-pipeline.md`: Runtime parallel concurrency vs serial estafet pipelines, sparse file allocation, and contention locks.
- `references/anti-abs-verification-matrix.md`: Epistemic classification (`KNOWN`, `LIKELY`, `UNCERTAIN`, `UNKNOWN`) and empirical verification checklists.

## Pitfalls
- **Premature Polishing Trap:** Styling colors, gradients, and animations before the database and CRUD endpoints work. Strictly adhere to Phase 1 first.
- **Silent Rabbit Holes:** Spending over 60 seconds debugging without sending a progress pulse to the user.
- **Silent Infinite Tool Loops & Failing to Fail-Fast:** When a backend command, script, or patch encounters repeated errors, the agent must NEVER loop silently (e.g. running 50–100+ turns leaving the user in an endless loading state). Enforce `hard_stop_enabled: true` and a strict turn ceiling (`max_turns: 25`). If a tool fails 3 times with the same error or cannot make progress after 3–4 tries, HALT immediately, emit the concrete error output and root blocker directly to the user, and present clear next options.
- **Defaulting to AI Model Training Hallucinations Instead of Live Design Research:** In Phase 2 or any UI/UX overhaul, models default to generic AI training tropes (purple/cyan gradients, cookie-cutter cards, bad contrast). Agents MUST actively query live internet references via `web_search` (Godly, Mobbin, Siteinspire, curated design systems) before writing CSS/templates, and cite the concrete design patterns adopted.
- **Self-Grading Bias:** An agent declaring its own code bug-free without running independent verification commands.
- **Context Amnesia:** Forgetting earlier architectural constraints during long sessions. Always re-read `build_tracker.json` via `read_file`.

## Verification
Initialize and inspect tracker status via `terminal`:
```bash
python3 scripts/flight_plan_tracker.py --status
```
Verify that the output displays the active project name, stage statuses, and confirmed vibe without exceptions.
