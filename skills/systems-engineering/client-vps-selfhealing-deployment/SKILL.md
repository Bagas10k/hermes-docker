---
name: client-vps-selfhealing-deployment
description: Deploy client VPS apps with self-healing watchdog.
version: 1.0.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [vps, deployment, self-healing, watchdog, docker, nginx]
    related_skills: [cloudflare-tunnel-sentinel, sqlite-production-hardening]
---

# Client VPS Self-Healing Deployment

Automated 1-click provisioning and autonomous watchdog self-healing engine for deploying client applications on cost-effective Linux VPS instances.

## When to Use
- When deploying production stacks (Node.js, Python, Go, Docker) on client VPS instances.
- When configuring Nginx reverse proxy, Cloudflare Tunnels, and automated SSL.
- When setting up background health probes with automatic restarts and circuit breakers.
- When configuring online SQLite WAL backups and zero-downtime maintenance hooks.

## Prerequisites
- Linux OS (Ubuntu 20.04/22.04/24.04 LTS or Debian).
- Python 3.8+ with standard library.
- System tools: `systemd`, `curl`, `nginx` (optional), `docker` (optional).

## Architecture & Mindset

### 1. Mechanistic & Bounds
- System Health Model:
  $$H(t) = P_{\text{proc}}(t) \wedge P_{\text{http}}(t)$$
- Exponential Backoff & Circuit Breaker:
  Max consecutive restarts capped at $N = 3$ within a 300-second sliding window to avoid fork-bombing or thrashing CPU.

### 2. Bayesian & Experimental
- Periodic health probes update service belief state $P(\text{Healthy} \mid \text{HTTP 200})$.
- Negative health probes trigger self-healing before escalating to alert channels.

### 3. System Design & Hard Constraints
- Hard constraint: Online database backups must never lock SQLite WAL readers or corrupt transactions.
- Zero external dependencies: Built using pure Python standard library for maximum portability.

## Provisioning Workflow
1. **Stack Provisioning**:
   ```bash
   python3 scripts/vps_stack_provisioner.py
   ```
   Generates `docker-compose.yml`, `nginx.conf`, Cloudflare Tunnel YAML, and systemd service descriptors.

2. **Self-Healing Watchdog**:
   ```bash
   python3 scripts/client_vps_watchdog.py
   ```
   Runs continuous probes, initiates process restarts on degradation, and trips the circuit breaker if failures persist.

3. **Safe Online Backup**:
   Executes non-blocking online SQLite WAL backup via `sqlite3.backup()` API.

## Verification
Run deterministic test suite:
```bash
python3 tests/test_watchdog.py
```
