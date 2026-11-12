# The 5-Stage Flight Plan Protocol

A standardized flight plan for complex engineering tasks, eliminating "cowboy coding" and unverified assumptions through strict staged progression.

```text
[STAGE 1: DISCOVERY] ➔ [STAGE 2: PUBLIC TASK DAG] ➔ [STAGE 3: CONTRACT] ➔ [STAGE 4: BOUNDED SPRINT] ➔ [STAGE 5: FIXED GATE]
(Inspect Ports & DB)    (Numbered Checklist)       (Lock Finish Line)     (30m cap, 60s pulse)    (QC correction report)
```

---

## Stage 1: Discovery & System Audit (Inspect Before Acting)
- Inspect existing environment state:
  - Active ports and listening sockets (`ss -tulpn`).
  - Active PM2 services (`pm2 list`).
  - Container allocations (`docker ps`).
  - Existing database tables and schema definitions.
- Inspect architectural precedents: reuse proven subpath patterns, session isolates, and database connectors.
- Explicitly declare boundary paths: what is in-scope vs what is strictly forbidden to touch.

### Repo-native plan onboarding (repo ships AGENTS.md + PROTOCOL + task file)
Use when a repo is planning-first (PRD/TECH/CONTRACTS + task DAG, little or no code). Read-only; batch independent reads.
1. **Read in the repo's declared order** (usually README → AGENTS → PROTOCOL → DECISIONS → CONTRACTS → task file). For large PRD/TECH, list headings first (`grep -n '^#' PRD.md`) and read only the sections the next task references.
2. **Run the repo's own consistency checker** if present (e.g. `python3 tools/check_docs.py`) and quote its exit code/summary line.
3. **Count the plan, don't eyeball it:** load the task file and tally status/kind/size plus tasks containing `manual:` acceptance steps:
   ```bash
   python3 -c "import yaml,collections;t=yaml.safe_load(open('plan/tasks.yaml'))['tasks'];print(len(t),collections.Counter(x['status'] for x in t),collections.Counter(x.get('kind') for x in t),sum(any(str(a).startswith('manual') for a in x.get('acceptance',[])) for x in t))"
   ```
4. **Cross-check names across docs:** grep component/crate/module names used in task deliverables and contracts against the structure list in AGENTS.md. A scaffold task that says "create all X per AGENTS.md" will silently miss anything absent from that list; flag it and propose fixing it inside that scaffold task.
5. **Note superseded sections:** when PRD and TECH disagree, check whether one explicitly defers to the other before calling it a conflict.
6. **Environment fit:** compare documented toolchain versions/target OS with the host (`cargo --version`, `node --version`, `pnpm --version`, free RAM/disk). Split tasks into "runnable here" vs "needs the user's machine" (OS-only APIs, desktop apps, manual acceptance).
7. **Visibility check:** unauthenticated `curl -s -o /dev/null -w '%{http_code}' https://api.github.com/repos/OWNER/NAME` → 404 while the authenticated clone works means the repo is private; mention it and never copy its content to public surfaces.
8. **Design artifacts:** view one key screen with `vision_analyze` and summarise the layout/tokens from the repo's design doc.
9. **Report** (no edits): product in a few lines, state with counts, how to drive the next task per the repo protocol (exact prompt the user can send), numbered inconsistencies/risks, one recommended next step.

---

## Stage 2: Public Task DAG & Checklist (Anti-Silent Planning)
Never conceal execution roadmaps inside internal thinking tags. Present an open, numbered checklist in the opening message to the user:
```text
📋 RENCANA EKSEKUSI PROYEK:
• ⏳ 1. [Fondasi] Setup skema database & container
• ⏳ 2. [Backend] Routing subpath & isolasi session
• ⏳ 3. [Frontend] UI/UX responsif & verifikasi asset
• ⏳ 4. [Integrasi] Penyambungan reverse proxy publik
• ⏳ 5. [Verifikasi] Uji login, transaksi, dan audit QC biner
```

---

## Stage 3: Contract Lockdown (Deterministic Finish Line)
Before modifying a single line of code, establish the exact binary verification criterion:
- Specific curl command: `curl -s -o /dev/null -w "%{http_code}" https://domain/app/login` returning HTTP 200/302.
- Specific unit test runner: `npm test` or `pytest` returning exit code 0.
- State clear circuit breakers: maximum 30 minutes from task receipt across discovery, delegation, tools and verification; at most 3 meaningfully distinct attempts for the same error (stop identical retries earlier). At the limit, stop the loop but deliver a detailed evidence-based status, remaining risks, and recommended next options with estimates; do not silently extend or claim DONE.

---

## Stage 4: Bounded Sprint & Micro-Milestone Progress Pulse
- Execute one task item at a time in isolation.
- Send a short progress pulse to the chat whenever a key milestone completes (`✅ Step 1 Selesai ➔ 🔄 Lanjut Step 2`).
- Enforce the 60-second silence ceiling: if a compilation, build, or test run exceeds 60 seconds, announce it before firing the background process. Give notice before the 30-minute task ceiling; stop new work at the ceiling, preserve progress, and explain results, errors, known versus hypothesized causes, risk, next options and the decision needed. End incomplete work with an explicit Continue option (remaining tasks, added time estimate, risk, next verification) and Pause/Stop (safe state); recommend one, and await user approval for a new contract rather than resetting the timer unilaterally.
- Persist milestone state to disk (`build_tracker.json`) so execution survives turn compactions.

---

## Stage 5: Fixed Evaluation Gate & Atomic Promotion
- The implementing agent must NEVER grade its own work.
- Hand over output to an independent reviewer (Si Pengawas) or automated test runner with immutable assertions. Si Pengawas adds an evidence-based correction report, not a PASS/REJECT veto; safety and permission requirements for production remain separate.
- Validate zero regressions on sibling services before cutover.
- Promote changes atomically and record lessons into knowledge storage.
