---
name: edge-decision-models
title: Edge Decision Models & In-Process Probability Gating
description: "Use when running local decision models for fast triage."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [decision-models, edge-ai, classification, probability-gating, fast-inference, kev, typesafe]
---

# Edge Decision Models & In-Process Probability Gating

Decision models (such as Kev-0.8B and Jev-style architectures) differ fundamentally from text-generating LLMs: they operate prefill-only with a pointer readout head, producing calibrated probability distributions in a single forward pass without autoregressive token generation. This enables sub-second classification, routing, and policy gating on modest CPU/edge hardware without token-based cloud API costs.

## When to Use
- Validating and classifying incoming transaction webhooks (e.g. Midtrans, Stripe fraud status, chargeback risk).
- Triage of client support messages, emails, and tickets (urgency, emotional tone, routing department).
- Pre-flight tool and command safety gates (checking destructive risk probability before execution).
- Workloads where calibrated confidence scores ($p \in [0.0, 1.0]$) and deterministic option schemas (`noul`, `choice`, `score`) are required over open-ended text.

Do NOT use for:
- Generative text drafting, conversational chat, or multi-turn reasoning.
- Complex code generation or long-form document synthesis.

## Architecture & Primitives
1. **`noul` (Boolean Decision)**:
   Returns probability of truth $p(\text{true})$. Useful for binary checks (`is_fraud`, `is_billing_issue`, `is_destructive`).
2. **`choice` (Categorical Decision)**:
   Evaluates 2–255 named options, each with an optional description. Outputs argmax choice, confidence score, and normalized probability per option.
3. **`score` (Ordinal Scale Decision)**:
   Evaluates an ordered list of criteria (e.g., `["low", "medium", "high"]`). Outputs expected score index and probability distribution.

## Verified Deployment on VPS
The system maintains a local daemon managed by PM2 on loopback:
- **Service Name**: `kev-decision-engine` (PM2 PID, port `8008`).
- **Endpoint**: `http://127.0.0.1:8008/v1/systemone` (TypeSafe System One compatible).
- **Global CLI**: `/usr/local/bin/kev-decide`.

### Quick Reference Commands
```bash
# Binary Yes/No verification
kev-decide --state "Transaksi Midtrans status settlement sukses" \
           --question "Apakah transaksi ini valid dan aman?" --type noul

# Categorical routing triage
kev-decide --state "Sistem kasir error 500 saat cetak struk antrean ramai" \
           --question "Seberapa genting tiket kendala ini?" \
           --type choice --options "darurat,sedang,santai"

# Ordinal score evaluation
kev-decide --state "Perubahan konfigurasi database firewall" \
           --question "Tingkat risiko operasi sistem" \
           --type score --options "rendah,sedang,kritis"
```

## Procedure
1. **Identify the Decision Surface**:
   Map the incoming text payload (webhook JSON, customer message, or shell command) to the `state` string.
2. **Formulate Unambiguous Questions**:
   Keep questions focused on a single property. Supply concise criteria descriptions for `choice` to resolve ambiguity.
3. **Dispatch via CLI or HTTP**:
   Send a JSON request to `POST http://127.0.0.1:8008/v1/systemone`.
4. **Enforce Calibrated Thresholds**:
   - For automated pass/fail: require $p(\text{true}) \ge 0.85$ for high-stakes actions; route to manual review queue if $0.40 < p < 0.85$.
   - For multi-choice triage: verify `confidence` margin $> 0.20$ before executing automated branching.

## Pitfalls
- **Do Not Run Generation Passes**: Attempting to prompt decision models with "Explain why..." fails; pointer heads do not output text tokens.
- **CPU Memory Sizing**: Float32 models on CPU allocate working buffers during inference (~5GB resident for 0.8B weights). Ensure at least 6GB available host RAM before spinning up concurrent model workers.
- **Context Bounds**: Keep state inputs within validated window ($\le 8,192$ tokens for 0.8B). Extremely long unstructured documents should be pre-chunked or summarized.
