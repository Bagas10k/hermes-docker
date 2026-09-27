---
name: agent-ephemeral-sandboxing
description: Isolate dangerous agent tool execution via ephemeral sandboxes.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sandboxing, microvm, ephemeral-runtime, security, rollback, agent-tools]
    related_skills: [systems-engineering/pm2-systemd-watchdog, autonomous-ai-agents/edge-slm-tool-calling]
---

# Agent Ephemeral Sandboxing Skill

Ephemeral tool isolation and rollback barrier for autonomous AI agent execution.

## When to Use

- Executing untrusted, mutating, or potentially destructive commands from autonomous agents.
- Running package installs (`pip`, `npm`, `cargo`) or arbitrary code execution (`python`, `bash`).
- Preventing cascade filesystem corruption or accidental workspace wipes.
- Enforcing resource ceilings (RAM limit via `RLIMIT_AS`, CPU time, and deadline timeouts).
- Don't use for: simple read-only commands (`cat`, `grep`, `git diff`) where overhead adds no safety gain.

## Prerequisites

- Python 3.9+ with standard library (`subprocess`, `tempfile`, `shutil`, `resource`).
- For Linux containerized hard-fencing: optional `bwrap` (Bubblewrap) or `gVisor` (`runsc`).

## How to Run

Execute the bundled sandbox engine CLI through the `terminal` tool:
```bash
python3 ~/.hermes/skills/systems-engineering/agent-ephemeral-sandboxing/scripts/ephemeral_sandbox_engine.py
```

## Quick Reference

- **Classify Risk**: Evaluate whether command requires Tier 0 (Read), Tier 2 (CoW Sandbox), or Tier 3 (MicroVM).
- **Create Ephemeral Workspace**: Initialize temporary directory with selective file snapshots.
- **Execute with Bound**: Run command with strict timeout (`timeout_sec=10`) and memory ceiling (`max_memory_mb=256`).
- **Rollback on Error**: Instantly purge temporary workspace on failure (`exit_code != 0`), zero host contamination.
- **Atomic Commit**: Promote only verified artifacts back to host workspace on success.

## Procedure

1. **Classify Execution Risk**:
   Pass candidate tool command through `classify_risk(cmd)` to determine the required isolation tier.
   *Completion criterion:* Action assigned to `TIER_0_READONLY`, `TIER_2_USERSPACE_COW`, or `TIER_3_MICROVM`.

2. **Provision Ephemeral Sandbox**:
   Call `create_ephemeral_workspace(session_id, files_to_snapshot)`.
   *Completion criterion:* Temporary isolated workspace active in `/tmp/hermes_sandbox_*`.

3. **Execute Under Hard Constraints**:
   Run `execute_bounded(session_id, command, timeout_sec, max_memory_mb)`.
   *Completion criterion:* Process terminated within deadline, exit code and standard streams captured.

4. **Verify and Resolve Transaction**:
   - If execution fails (`exit_code != 0` or timed out): trigger `rollback(session_id)`.
   - If execution succeeds: trigger `commit(session_id, dest_workspace)`.
   *Completion criterion:* Host workspace remains untouched on failure; changes cleanly committed on success.

## Pitfalls

- **False Sense of Safety in In-Process Limits**: `RLIMIT_AS` limits address space, not disk IOPS. Always mount ephemeral workspaces on temporary filesystems with quotas.
- **Fork Bomb Exhaustion**: Unprivileged user execution should restrict `RLIMIT_NPROC` to prevent subagent fork bombs.
- **Cross-Platform Resource Modules**: The `resource` module is POSIX-only. The script handles non-Linux platforms defensively by falling back to process timeout supervision.

## Verification

Run the built-in invariant test suite:
```bash
python3 ~/.hermes/skills/systems-engineering/agent-ephemeral-sandboxing/scripts/ephemeral_sandbox_engine.py
```
Expected output:
```
ALL EPHEMERAL SANDBOX ENGINE TESTS PASSED (100%).
```
