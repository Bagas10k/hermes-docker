---
name: edge-slm-tool-calling
description: Edge SLM function calling, GBNF grammar, and schema bounds.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [edge-slm, tool-calling, gbnf-grammar, structured-output, json-schema, llama-cpp]
    related_skills: [mcp-dynamic-federation, low-resource-offline-inference, agent-test-time-compute]
---

# Edge SLM Tool-Calling Skill

Small Language Models (SLMs) with 1.5B–3B parameters running on edge CPUs (e.g. Qwen2.5-Coder-1.5B/3B, Llama-3.2-3B) face tight context windows and higher hallucination rates during tool calling. This skill governs constrained decoding via GBNF grammars, JSON schema validation barriers, and context compression to guarantee deterministic function execution with sub-second latency on edge hardware.

## When to Use

- Dispatching tool invocations to local edge models (1B–3B parameters) via llama-server, Ollama, or vLLM.
- Constraining raw LLM generation to strict JSON schemas using GBNF grammar masks.
- Validating and sanitizing edge tool payloads before allowing execution sinks.
- Handling tool-call schema divergence, repair loops, and fail-closed bounds on CPU runtimes.

Don't use for:
- Cloud-hosted frontier models with built-in native schema guarantees (GPT-4o, Claude 3.5 Sonnet).
- Pure text chat without tool execution.

## Prerequisites

- Python 3.10+ with `pydantic` or stdlib `json`/`jsonschema`.
- Local inference server supporting BNF/GBNF grammar masking (e.g., `llama-server` or Ollama endpoint).
- Edge CPU budget: 2-4 cores, RAM budget <= 2.0GB.

## Quick Reference

Validate JSON schema strictly before tool execution:
```bash
python3 -m hermes_skills.edge_slm_tool_calling.validator --schema schema.json --input output.json
```

Generate GBNF grammar from JSON Schema:
```bash
python3 ~/.hermes/skills/autonomous-ai-agents/edge-slm-tool-calling/scripts/slm_tool_engine.py --schema-to-gbnf schema.json
```

Run test suite:
```bash
python3 ~/.hermes/skills/autonomous-ai-agents/edge-slm-tool-calling/scripts/slm_tool_engine.py --test
```

## Procedure

1. **Schema Formulation & Minimal GBNF Generation**:
   Define strict JSON schema. Convert schema to deterministic GBNF rules. Disallow arbitrary wildcard keys to bound the search space:
   $$V_{\text{valid}} \subset \Sigma^*, \quad P(\text{invalid token} \mid GBNF) = 0$$

2. **Inference with Grammar-Constrained Logit Masking**:
   Supply the GBNF grammar directly to the edge inference runtime (`/completion` with `grammar` payload). The sampler masks invalid tokens at each decoding step.

3. **Deterministic Verification Barrier (Fail-Closed Gate)**:
   Pass the generated string through `slm_tool_engine.py`. Check:
   - Well-formed JSON parse.
   - Exact argument type conformance.
   - Whitelist of permitted tool names.
   Reject immediately if validation fails; do not attempt blind execution.

4. **Single-Turn Error Feedback Repair (Max 1 Retry)**:
   If a model outputs an unrecoverable structural syntax error or semantic constraint violation, inject the specific schema error back to the model with temperature $T=0.1$. If the retry fails, trigger fail-closed fallback.

## Pitfalls

- **Complex Regex in GBNF on CPU**: Overly recursive GBNF rules cause CPU pre-compilation latency spikes (>500ms). Keep grammars non-recursive and shallow.
- **Context Bleed in Edge Prompts**: Injecting 20 tool definitions consumes >1,500 tokens, degrading 1.5B attention accuracy. Keep the active tool schema set $\le 3$ relevant tools via dynamic routing.
- **Escape Character Traps**: Edge models frequently choke on escaped quotes within string fields. Use primitive typing (ints, enums, booleans) wherever possible.

## Verification

Run the self-contained verification engine:
```bash
python3 ~/.hermes/skills/autonomous-ai-agents/edge-slm-tool-calling/scripts/slm_tool_engine.py --test
```
Checklist:
- [ ] GBNF grammar accurately constrains JSON schema keys and primitive types.
- [ ] Schema validator rejects malformed inputs and unauthorized tool names fail-closed.
- [ ] Bounded repair loop corrects repairable deviations within 1 turn without infinite loops.
