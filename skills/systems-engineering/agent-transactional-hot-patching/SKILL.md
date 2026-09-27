---
name: agent-transactional-hot-patching
description: Transactional hot-patching with shadow rollback isolation.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [systems-engineering, self-healing, hot-patching, shadow-workspace, rollback, atomic-commit]
    related_skills: [agent-zero-regression-fuzzing, agent-ast-mutation-patching, 027-autonomous-schema-evolution-zero-downtime]
---

# Agent Transactional Hot-Patching Skill

Transactional hot-patching engine for self-healing and evolving autonomous systems. Prevents partial writes, eliminates broken runtime states, and guarantees instantaneous zero-downtime rollbacks via isolated shadow copy-on-write workspaces and two-phase commit verification.

## When to Use

- When an autonomous agent needs to patch production backend code, API handlers, or configuration files while services are running.
- When applying bug fixes or feature evolutions without risking service crash loops.
- When performing multi-file refactoring where all files must land atomically together or not at all.
- Don't use for: Simple scratchpad prototyping or read-only inspections.

## Prerequisites

- Python 3.8+ with standard library modules (`os`, `shutil`, `tempfile`, `pathlib`, `subprocess`).
- Helper script available at `~/.hermes/skills/systems-engineering/agent-transactional-hot-patching/scripts/transactional_patch_manager.py`.

## Quick Reference

```bash
# Verify and commit hot-patch with shadow isolation
python3 ~/.hermes/skills/systems-engineering/agent-transactional-hot-patching/scripts/transactional_patch_manager.py \
  --target /path/to/project \
  --files app.py config.json \
  --check-cmd "pytest tests/test_health.py"
```

## Procedure

1. **Stage Shadow Workspace**:
   Call `create_shadow_copy([files])` to isolate target files into a dedicated staging directory (`tx_<session_id>`). Original live files remain completely untouched.
2. **Apply Staged Mutations**:
   Perform all AST mutations, regex substitutions, or string replacements exclusively inside the shadow directory.
3. **Phase 1: Shadow Health & Invariant Verification**:
   Execute pre-commit test suites, syntax linters, and invariant assertions inside the shadow workspace. If any assertion fails, trigger `rollback()` to wipe shadow files. Live files suffer zero mutations ($T_{\text{rollback}} = 0$).
4. **Phase 2: Atomic POSIX Swap**:
   Invoke `commit()` which writes to target-local `.atomic_tmp` buffers and executes atomic `os.replace` swaps.
5. **Post-Commit Live Health Probe**:
   If an optional live probe fails, the engine automatically restores target files from the pre-commit snapshot (`bak_<session_id>`) in under 2ms.

## Pitfalls

- **Cross-Filesystem Rename Failure**: Direct `os.replace` across different mount points (e.g. `/tmp` to `/home`) throws `EXDEV` (Invalid cross-device link). *Mitigation*: The engine copies shadow files to `.atomic_tmp` within the target directory before invoking `os.replace`.
- **Dangling Incomplete Transactions**: Process crashes during shadow editing could leave temporary directories behind. *Mitigation*: Session workspaces use prefixed identifiers (`hermes_shadow_patches/tx_*`) with automatic ephemeral lifecycle cleanup.
- **Service Cache Desynchronization**: Python or Node.js runtimes with aggressive module caching may not pick up hot-swapped files immediately. *Mitigation*: Pair with process reload signals (e.g. `pm2 reload` or SIGHUP) within the post-commit verification probe.

## Verification

Run deterministic verification tests:
```bash
python3 ~/.hermes/skills/systems-engineering/agent-transactional-hot-patching/scripts/test_transactional_patch_manager.py
```
Expected result: 3 tests pass with exit code 0 (`OK`).
