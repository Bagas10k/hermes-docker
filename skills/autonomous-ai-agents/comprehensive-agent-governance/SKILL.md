---
name: comprehensive-agent-governance
description: Govern autonomous agent workflows, architecture, and scale.
version: 0.1.0
author: Hermes Agent
license: MIT
related_skills:
  - subagent-lifecycle-management
  - autonomous-orchestrator
  - multi-agent-deliberation
  - autonomous-learning-pipeline
metadata:
  hermes:
    tags:
      - MasterOrchestrator
      - AgentGovernance
      - FlightPlan
      - AutonomousLearning
      - UpnormalUI
      - BusinessScaling
---

# Comprehensive Agent Governance & Scaling Master Skill

Unify and orchestrate the four core pillars of autonomous engineering: 5-Stage Flight Plan execution, 3-mode autonomous learning engine, radical Upnormal UI architecture, and high-leverage business scaling frameworks.

## When to Use
- User commands `/learn all`, `!learn-all`, or "jalankan semua pembelajaran dan tata kelola".
- Onboarding new autonomous tasks requiring synchronized planning, visual excellence, and business viability.
- Auditing the complete end-to-end health of agent engineering pipelines.

## Prerequisites
- Hermes multi-agent runtime with access to `hermes-learn` CLI.
- Knowledge Vault at `/home/ubuntu/otak-koding/` and Buku Catatan Digital at `BUKU_CATATAN/`.
- Working directory: `/home/ubuntu`.

## How to Run
Invoke master orchestrations through the `terminal` tool or inspect status with `skill_view`:
- Run master dual learning audit: `terminal(command="hermes-learn --all")`
- Load specific subsystem skills via `skill_view`:
  - `skill_view(name="structured-project-execution")`
  - `skill_view(name="autonomous-learning-pipeline")`
  - `skill_view(name="upnormal-ui-architecture")`
  - `skill_view(name="business-opportunity-scaling")`

## Quick Reference
- **Pillar 1 (Execution):** 5-Stage Flight Plan (Discovery -> Public Task DAG -> Contract -> Bounded Sprint -> Honest Correction Report) + 60s silence ceiling. Si Pengawas only appends evidenced shortcomings; no QC veto or forced repetition. Safety/permission checks for external release remain separate.
- **Pillar 2 (Truthfulness):** Radical Truthfulness (Anti-ABS) + 4-tier epistemic classification (`KNOWN`, `LIKELY`, `UNCERTAIN`, `UNKNOWN`).
- **Pillar 3 (Learning):** 3-Mode Engine (Error-Driven `state.db`, Knowledge-Gap Vault, Frontier New Topic via live web).
- **Pillar 4 (Interface):** Upnormal UI (Live internet reference discovery, 6 world archetypes, 127px type, 60 FPS morphing, Two-Layer Silhouette).
- **Pillar 5 (Accounting):** Double-Entry Invariants ($\sum \text{Debit} == \sum \text{Credit}$, immutable journals, COA 5 classes, 3-way matching).
- **Pillar 6 (Economics):** 4 Leverage Stack (Labor, Capital, Media, Code/AI) + Payback < 6 months.

## Procedure

### Repurpose an underused Hermes profile for a specialist role
1. Inventory profiles and status with `hermes profile list`, then inspect candidate `hermes profile show <name>`, `profile.yaml`, `SOUL.md`, model configuration, and active task assignments. Prefer a stopped, non-core test profile; do not repurpose a running operational identity merely because its name sounds expendable. Confirm the exact candidate with the user before renaming because identity and routing can change.
2. Rename through `hermes profile rename <old> <new>` rather than moving directories manually; set a routing description with `hermes profile describe <new> --text '<scope and exclusions>'`. Update **the renamed profile's** SOUL and relevant topical references while preserving unrelated profiles. Treat advisor, executor, and independent reviewer as separate duties; prohibit production mutations without explicit authorization.
3. Validate the profile's own model/provider and credential **key presence without printing values**; cloned test profiles may carry a stale provider alias even after a successful rename. Fix only that profile's config, then verify `hermes profile show`, the new assignee in `hermes kanban assignees --json`, and a harmless one-shot response (`hermes -p <new> -z '<identity and boundaries check>'`). A profile that exists on disk but times out during inference is configured, not yet operationally verified.
4. For research-enabled specialists, seed a short, cited index of primary sources with applicability and effective-period caveats; research standards and public guidance, never leak private business records to search. Keep specialist domain skills in the specialist's isolated profile rather than assuming another profile's skills are inherited. When the user assigns expertise to that profile, the coordinator delegates the domain task and compiles its response; it does not load or perform the specialist skill itself. Distinguish skill-file validation from a successful profile invocation before claiming the collaboration works.
5. Copy the exact skill name from `skills_list` or the `available_skills` error list into `skill_view(name="...")`; never append probes, suffixes, or comments inside the `name` value. On “not found,” correct that value **once** before retrying; changing `file_path` cannot fix name resolution. If the corrected lookup or specialist invocation still fails, switch to a valid alternative and report the unverified boundary—do not loop or ask the user to recover your tool error.
6. When asked whether a specialist is *working now*, check separate signals: `hermes -p <profile> gateway status` for gateway ownership, `hermes -p <profile> cron list` for scheduled work, `hermes kanban list --assignee <profile> --json` for assignments, and a narrowly filtered process list plus recent sessions/logs for active turns. A shared gateway marked running is not evidence that the specialist is continuously reasoning; sessions indicate history, not current execution. Report each signal and its limits before concluding activity. Do not terminate a shared gateway to stop an individual profile.
7. To attach a dedicated Telegram bot to a profile under a multiplexed gateway:
   - Validate the bot token via `curl -sS https://api.telegram.org/bot<token>/getMe` without printing or logging token values; confirm bot identity (`is_bot: true`, username).
   - Write `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`, and `TELEGRAM_HOME_CHANNEL` into the profile's `.env`. Update `profile.yaml` description and `previous_names`.
   - Never issue gateway restart/kill commands from within a gateway session. The gateway multiplexer hot-reconciles profile adapters automatically every 30 seconds upon detecting signature changes on `.env` or `config.yaml` (`✓ telegram connected (profile: <name>)`).
   - Audit configured default and fallback models in the profile's `config.yaml` to ensure every model returns HTTP 200 / pong before releasing to users.
8. To migrate operational context and memory from an existing session to another profile:
   - Apply a two-tier transfer: (a) Distill critical topology, paths, container isolates, tunnel configs, and safety invariants into the target profile's persistent memory (`memories/MEMORY.md`), keeping within the character budget. (b) For historical searchability, copy the session and message rows from the source `state.db` to the target profile's `state.db`; SQLite FTS triggers index the text automatically so `session_search` queries succeed.
   - Enforce the "Calm & Thoughtful" communication persona in the target profile's `SOUL.md`: warm, natural, structured, concise, and direct to the point without robotic pleasantries.

1. **Phase 1: Discovery & Public Blueprint:**
   Audit existing infrastructure with `read_file` and `search_files`. Post the public 5-stage task checklist before writing code. Enforce the 60-second silence ceiling with Progress Pulses. Maintain `build_tracker.json` on disk.

2. **Phase 2: Live Frontier Exploration & Upnormal Design:**
   Query latest web design references via `web_search` (`site:godly.website`, `site:awwwards.com`). Deploy Two-Layer Silhouette (Layer 0 dynamic WebGPU/SVG backdrop, Layer 10 WCAG AAA 7:1 typography). Ban blurry drop-shadows and generic AI slop.

3. **Phase 3: Mission-Critical Backend & Accounting Invariants:**
   Enforce double-entry bookkeeping rules at schema level (`NUMERIC(19, 2)`). Ensure posted journals are immutable with signed reversal patterns. Validate Three-Way Matching and financial statement balances.

4. **Phase 4: Autonomous Deficit Repair & Learning:**
   Execute `autonomous-learning-pipeline`. Run candidate patches in isolated sandboxes (`/tmp` or `sandbox/`). Enforce immutable supervisor evaluation with biner `Exit Code 0`.

5. **Phase 5: Commercial Viability & Scale Audit:**
   Apply `business-opportunity-scaling`. Validate scale invariance (`Contribution Margin = gm * LTV_n - CAC`) and verify zero-marginal-cost reproduction.

6. **Phase 6: Honest Verification & Vault Crystallization:**
   Execute real runtime checks (exit code 0, curl 200). Never fabricate success. Document findings in `BUKU_CATATAN/` and register links in `KNOWLEDGE/INDEX.md` under `Status: TESTED`.

## References
Load topic-specific architectural reference files on demand using `skill_view` (`name="comprehensive-agent-governance"`, `file_path="references/<file>"`):
- `references/execution-and-anti-abs.md`: 5-Stage Flight Plan, persistent build tracker, epistemic honesty, and anti-ABS rules.
- `references/upnormal-design-and-frontier.md`: Live internet discovery (Awwwards/Godly), 6 world archetypes, 60 FPS morphing, and anti-slop gates.
- `references/autonomous-learning-architecture.md`: 3 learning modes, knowledge gap scanner, sandbox supervisor evaluation, and quick shortcuts.
- `references/enterprise-accounting-and-scale.md`: Double-entry invariants, COA 5 classes, 3-way matching, 4 leverage stack, and unit economics.

## Pitfalls
- **Cowboy Coding Trap:** Never start editing production files without an initial public task checklist.
- **Unbounded Learning Loops:** Keep autonomous learning bounded and event-driven; avoid 24/7 background CPU/token drains.
- **Generic AI Aesthetics:** Never revert to generic purple-blue gradients or unmotivated card badges.
- **Linear Founder Traps:** Reject business models requiring 1:1 founder hours per revenue increment.

## Verification
Execute the master system audit check via `terminal`:
`hermes-learn --all`
Verify that both Error-Driven and Knowledge-Gap pipelines return `Exit Code 0` in <2 seconds.
