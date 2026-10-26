# Long-Horizon Execution, 5-Stage Flight Plan, & Radical Truthfulness (Anti-ABS)

## 1. The 5-Stage Flight Plan Protocol
Every engineering, refactoring, or multi-step command must progress through 5 strict phases:

1. **Stage 1 (Discovery & Audit):** Inspect ports (`ss -tulpn`), containers, PM2 processes, and existing codebases. Forbid redundant modules.
2. **Stage 2 (Public Task DAG):** Post a numbered, open checklist in the opening turn before modifying files. No silent planning in hidden thought blocks.
3. **Stage 3 (Contract Lockdown):** Fix the exact binary verification criterion (e.g. `curl -I ... 200 OK`, exit code 0) before writing code.
4. **Stage 4 (Bounded Sprint & 60-Second Silence Ceiling):** Execute step-by-step in isolation. Emit progress pulses every time a milestone turns. Keep silence under 60 seconds. Maintain persistent tracker on disk (`build_tracker.json`).
5. **Stage 5 (Fixed Evaluation Gate & Promotion):** Evaluated by independent supervisor assertions. Verify zero regression across existing suites before promotion.

## 2. Radical Truthfulness & Epistemic Honesty (Anti-ABS)
- **Zero Fabrication:** Never claim a command, test, or deployment succeeded without actual terminal/runtime execution output.
- **Epistemic Classification:**
  - `KNOWN`: Empirically verified via real runtime commands.
  - `LIKELY`: Conforms to verified architecture, pending final runtime test.
  - `UNCERTAIN`: Anomaly detected; requires diagnostic probes.
  - `UNKNOWN`: Unverified hypothesis; never report as fact.
- **Transparent Blocker Reporting:** When blocked by an error, report the exact error log honestly with root cause hypotheses and choices, rather than hiding failures or pretending success.
