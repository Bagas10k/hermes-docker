---
name: xdp-packet-filtering-telemetry
description: Filter telemetry packets at L2 driver level via XDP.
version: 1.0.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [xdp, ebpf, packet-filtering, kernel-bypass, telemetry, wire-speed]
    related_skills: [seccomp-bpf-sandbox-filter, agent-ebpf-lsm-sandboxing]
---

# XDP Packet Filtering for High-Volume Telemetry Ingress

Provides zero-copy L2/L3 packet filtering and wire-speed validation for telemetry data before allocation in the Linux TCP/IP network stack (`sk_buff`).

## When to Use
- Telemetry ingestion throughput exceeds 500,000 packets per second.
- Preventing DDoS or noisy tenant telemetry flooding from exhausting kernel memory.
- Enforcing per-tenant rate limits directly in NIC ring buffer context.

## Core Mechanisms
1. **L2 Driver Hook (`xdp_drv`)**: Inspects raw packets at the driver boundary before `netif_receive_skb()`.
2. **BPF Maps**:
   - `BPF_MAP_TYPE_HASH`: Token verification and per-tenant rate-limit state.
   - `BPF_MAP_TYPE_PERCPU_ARRAY`: Lockless per-core packet drops and pass counters.
   - `BPF_MAP_TYPE_RINGBUF`: Zero-copy ring buffer delivery to user-space agent runtimes.
3. **Decisions**:
   - `XDP_DROP`: Malformed, unauthenticated, or rate-exceeded telemetry packets.
   - `XDP_PASS`: Standard non-telemetry traffic forwarded to Linux network stack.
   - `XDP_REDIRECT`: Valid telemetry dispatched to AF_XDP socket or shared ring buffer.

## Quick Reference
```bash
python3 ~/.hermes/skills/systems-engineering/xdp-packet-filtering-telemetry/scripts/xdp_telemetry_filter.py
python3 ~/.hermes/skills/systems-engineering/xdp-packet-filtering-telemetry/scripts/test_xdp_filter.py
```
