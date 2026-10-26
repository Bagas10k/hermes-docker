# 3-Mode Autonomous Learning Engine & Sandbox Supervision

## 1. The Three Modalities of Self-Directed Growth
The learning engine operates along three purposeful axes:
1. **Mode 1 (Error-Driven):** Diagnoses real failure clusters in `state.db`, designs targeted remediation curricula, and trains in sandbox.
2. **Mode 2 (Knowledge-Gap-Driven):** Scans the Obsidian Knowledge Vault (`KNOWLEDGE/INDEX.md` and `BUKU_CATATAN/`) via `knowledge_gap_scanner.py` to identify untested doctrines and explicit gap annotations, solving them proactively before runtime failure.
3. **Mode 3 (Frontier Exploration):** Investigates completely new technologies and frameworks via live web research, runs isolated sandbox prototypes, passes independent evaluation, and crystallizes permanent new skills.

## 2. The Sandbox Isolation & Fixed Supervisor Gate
- Candidate logic is exercised in an isolated temporary sandbox (`/tmp` or `sandbox/exp_<id>/`).
- Production runtime files are untouched during exploration.
- An independent supervisor script (`evaluators/eval_batch*.py`) applies rigid, immutable assertions.
- Only upon receiving `PROVEN_SUCCESS (Exit Code 0)` and proving zero regression across the existing 140+ skill base is the enhancement promoted to production.

## 3. Rapid Shortcuts
- Terminal: `hermes-learn -e` (Error), `hermes-learn -g` (Gap), `hermes-learn -n <topic>` (New), `hermes-learn -a` (All).
- Telegram Chat: `/learn error`, `/learn gap`, `/learn new <topic>`, `/learn all`.
