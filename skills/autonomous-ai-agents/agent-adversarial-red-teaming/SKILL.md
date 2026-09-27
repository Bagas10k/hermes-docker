---
name: agent-adversarial-red-teaming
description: Autonomous agent red-teaming and jailbreak defense gates.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [autonomous-agents, red-teaming, prompt-injection, canary-tokens, security-boundary, sandboxing]
    related_skills: [agent-quarantine-gateway, agent-ephemeral-sandboxing, byzantine-multiagent-debate]
---

# Agent Adversarial Red-Teaming Skill

Evaluates and hardens autonomous agent systems against direct jailbreaks, indirect prompt injections, and canary token exfiltration across long-horizon trajectories.

## When to Use
- Auditing multi-step agent workflows for indirect prompt injection vulnerabilities in web scraping or tool outputs.
- Testing agent resilience against multi-turn jailbreaks and developer mode override bypasses.
- Enforcing canary token integrity checks to prevent system prompt and credential leakage.
- Sanitizing untrusted inputs before injecting into agent context memory.

## Prerequisites
- Python 3.10+ standard library.
- Access to raw trajectory traces or incoming tool observation streams.

## Quick Reference
```bash
python3 ~/.hermes/skills/autonomous-ai-agents/agent-adversarial-red-teaming/scripts/adversarial_red_teaming_engine.py
```

## Procedure
1. **Input Audit Gate**: Pass candidate text through heuristic pattern matching and context tagging (`audit_input`).
2. **Untrusted Tool Sanitization**: Strip nested directive tags from external scraped documents (`sanitize_untrusted_content`).
3. **Canary Token Verification**: Inspect generated responses against active canary tokens to detect leakage (`verify_canary_integrity`).
4. **Veto & Circuit Breaker**: If risk score $\ge 0.70$ or canary leak is detected, veto the execution turn and quarantine the offending context.
5. **Log & Record**: Persist red-team findings to Obsidian vault for continual defense refinement.

## Pitfalls
- **Over-sanitization False Positives**: Blocking benign technical queries that discuss security mechanisms (e.g. debugging "sudo", "override"). Solution: adjust threshold based on `context_type`.
- **Unicode Obfuscation**: Attackers using zero-width spaces or homoglyphs to split keywords. Solution: normalize unicode before regex pattern matching.
- **Canary Replay via Reflection**: Agent echoing canary when debugging prompt templates. Solution: strictly forbid canary references in model output parsing layers.

## Verification
Run the verification suite:
```bash
python3 ~/.hermes/skills/autonomous-ai-agents/agent-adversarial-red-teaming/scripts/adversarial_red_teaming_engine.py
```
Expected output:
```
=== RUNNING ADVERSARIAL RED-TEAMING DEFENSE ENGINE TESTS ===
[PASS] Test 1: Benign User Query classified as SAFE.
[PASS] Test 2: Direct Jailbreak Attempt successfully blocked.
[PASS] Test 3: Indirect Prompt Injection from untrusted tool output blocked.
[PASS] Test 4: Canary Token Integrity & Exfiltration Detection 100% verified.
[PASS] Test 5: Content Sanitizer neutralizes hostile directives.
ALL 5 TESTS PASSED SUCCESSFULLY (100% PASS RATE).
```
