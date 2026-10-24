---
name: claim-proof-ledger
description: Use when auditing claims against real test evidence.
---
# Claim-proof ledger

## Procedure

1. Before the final report, enumerate every user-visible claim and define a binary `done_when` check for it.
2. Separate evidence classes: unit/integration tests, target-engine rehearsal, build, HTTP health, authenticated browser behavior, visual inspection, external-system readback, and independent QC are not interchangeable.
3. Record one concrete observation per check: command or probe, exit/status, decisive output, and artifact path when relevant. Keep secrets and personal data out of the record.
4. After the last source or tracker write, rerun the verifier whose freshness matters; a previously green result cannot support a changed artifact.
5. For external writes, migrations, or publications, read back the exact target. For database enforcement, test the forbidden operation against a disposable instance of the production engine; `migrate:status` proves installation state, not behavior.
6. Mark intentionally undeployed work as **held/pending** with the missing approval or gate. Never let a local rehearsal imply production deployment.
7. Accept delegated review only when delivery is completed with a substantive verdict; queued, claimed, running, timed-out, or interrupted workers are supporting context, not an independent approval.
8. Create a non-sensitive task record and run `terminal(command="python3 /home/ubuntu/agent-quality/quality_gate.py <record.json>")`. Qualify or remove every claim without a passing check.

## Evidence boundaries

- A Vite/build/readiness pass does not prove Laravel/domain behavior.
- Public HTTP 200 does not prove an authenticated workflow.
- A balanced aggregate does not prove every journal entry is balanced.
- A returned iframe URL is not proof of actual playback; a preview is not a rendered export.
- A screenshot plus DOM geometry proves presentation only, not persistence or authorization.

Report verified work, held work, and limitations separately and plainly.
