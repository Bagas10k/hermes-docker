---
name: pm2-systemd-watchdog
description: Monitor and harden Linux PM2 and systemd user services.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [pm2, systemd, watchdog, process-management, systems-engineering, linux]
    related_skills: [sqlite-production-hardening, cloudflare-tunnel-sentinel]
---

# PM2 & Systemd Process Sentinel

Operational watchdog and hardening discipline for persistent Linux daemons, microservices, and user-space service supervisors.

## When to Use

- Inspecting production daemons across PM2 and systemd user services.
- Mitigating fast restart loops, runaway memory consumption, or zombie/orphan workers.
- Tuning ecosystem configurations (`max_memory_restart`, `exp_backoff_restart_delay`).
- Ensuring systemd user linger permanence and zero-downtime microservice reloads.

## Prerequisites

- Linux host running PM2 and systemd user instance.
- User lingering enabled (`loginctl show-user $USER | grep Linger=yes`).
- Python 3.8+ for automated health probes.

## Quick Reference

```bash
# Run unified sentinel audit
python3 ~/.hermes/skills/systems-engineering/pm2-systemd-watchdog/scripts/sentinel_audit.py

# Check user lingering
loginctl show-user ubuntu | grep Linger

# Inspect systemd user units
systemctl --user status

# Inspect PM2 process table and memory
pm2 jlist | jq '.[] | {name: .name, status: .pm2_env.status, mem_mb: (.monit.memory/1048576 | round), restarts: .pm2_env.restart_time}'
```

## Procedure

1. **Audit Live State**:
   Run `sentinel_audit.py` to evaluate both PM2 and Systemd units in a single sub-second pass. Check for processes with errored states, excessive restarts, or memory usage approaching server thresholds.

2. **Diagnose Process Instability**:
   If restarts exceed 50 with low uptime (< 1h), inspect logs immediately:
   ```bash
   pm2 logs <app-name> --lines 50 --nostream
   ```
   Identify root cause (unhandled rejection, port conflict, missing environment variable).

3. **Enforce Memory Caps**:
   For memory-heavy workers (ML inference, Puppeteer headless browsers), declare explicit limits in `ecosystem.config.js`:
   - `max_memory_restart`: "700M"
   - `exp_backoff_restart_delay`: 2000
   - `kill_timeout`: 5000

4. **Verify Systemd User Linger**:
   Verify lingering is active:
   ```bash
   loginctl show-user ubuntu | grep Linger
   ```
   If missing, enable lingering to guarantee daemons survive SSH disconnects.

5. **Commit Configuration**:
   After adjusting processes, persist PM2 dump:
   ```bash
   pm2 save
   ```

## Pitfalls

- **Mass Restart Starvation**: Never run `pm2 restart all` blindly on production servers. Restart services individually to prevent memory spikes and connection dropouts.
- **Log Disk Exhaustion**: Without `pm2-logrotate`, unhandled exceptions can generate gigabytes of log files in `~/.pm2/logs/`.
- **Systemd Linger Inactive**: If linger is disabled, systemd user services terminate as soon as the user logs out.

## Verification

- Audit script returns exit code `0` and `"healthy": true`.
- Zero services in `errored` status.
- Memory consumption within allocated boundaries (<650MB per microservice).
