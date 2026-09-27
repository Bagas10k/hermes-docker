---
name: low-resource-offline-inference
description: Use when running offline coding models on small CPUs.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [offline, inference, gguf, cpu, vibe-coding]
    related_skills: [portable-liveboot-agent, live-sandbox-hot-preview]
---

# Low-Resource Offline Inference

Run a small local coding assistant with measured memory and streaming behavior. This is an installed user-local skill, not an upstream Hermes contribution. Small models produce drafts, not trustworthy autonomous tool decisions.

## When to Use
- Offline code explanations, small snippets, and local prototype assistance with a tight RAM budget.
- Compare llama.cpp CPU options before deploying on a low-memory laptop or live USB.
- Do not use for autonomous recovery actions, unrestricted shell execution, or claims of full-model reasoning quality.

## Prerequisites
- Linux, Python 3.11+, an official llama.cpp CPU release matching architecture/libc, and a locally downloaded GGUF model.
- Start with official Qwen/Qwen2.5-1.5B-Instruct-GGUF `qwen2.5-1.5b-instruct-q4_k_m.gguf`; record revision and digest.
- Reserve disk space for download plus extraction and memory headroom for desktop/editor/OS. Do not install a persistent daemon or edit Hermes provider settings during a probe.
- Read [the measured architecture and evidence](references/architecture.md) before selecting defaults.

## Quick Reference
Use `terminal` with the following commands, replacing paths with verified local paths:

```text
python3 scripts/probe.py --server /path/llama-server --model /path/model.gguf --output /path/baseline.json
python3 scripts/probe.py --server /path/llama-server --model /path/model.gguf --output /path/no-repack.json --no-repack
```

Run from this skill directory. Each command starts a loopback-only temporary server, executes real SSE coding requests, records sampled peak RSS/TTFT, and terminates its own process. It does not hard-limit memory; use an approved cgroup for hard deployment limits.

Measured low-memory starting command, through `terminal`:
```text
llama-server -m /path/model.gguf --host 127.0.0.1 --port 18081 -ngl 0 -t 2 -tb 2 -c 1024 -np 1 -b 128 -ub 64 --no-repack
```
Do not publish this port or embed its address in public HTML. Port selection must be checked before persistent use.

## Procedure
1. Define the budget in bytes and reserve OS/editor headroom. Record CPU, build, model digest, context, batch sizes, and thread count. Success: reproducible configuration, not a model filename alone.
2. Read the installed `--help`; flags change. Verify CPU-only `-ngl 0`, bounded context, and one slot. Success: help confirms every selected flag.
3. Predict before testing: weight repacking may add resident buffers; disabling it may trade throughput for RAM. Run the baseline and `--no-repack` probes with every other setting unchanged. Success: both streams contain actual content and `[DONE]`, raw results retained.
4. Compare sampled RSS and TTFT separately from output quality. Use actual prompts with enough output budget to finish code. Success: code is complete and passes compiler/tests; otherwise retain as a failed quality gate, not a working artifact.
5. Tune one of threads, context, or microbatch at a time only when its result could change the decision. Do not infer a p95 from three requests. Success: use representative prompt lengths and repeated runs on target hardware before deployment.
6. Integrate behind the existing local editor/sandbox adapter, with visible cancel and draft status; compile/test before applying suggested changes. Bound output and queue length, reject excess work rather than expanding slots silently. Success: no unreviewed edits, network-dependent fallback, or escaped tool calls.
7. Stop only processes created by the probe and retain evidence. Success: no leftover test server; no production service touched.

## Pitfalls
- Q4_K_M is mixed quantization; parameter count times four bits is not resident memory.
- mmap does not mean zero RSS. Repacked weights, compute buffers, KV cache, allocator and mapped pages all contribute.
- Default context can follow large model metadata. Explicit context/slot counts protect RAM.
- `[DONE]` proves stream termination, not complete source code: max_tokens may truncate a function.
- Streaming improves visible responsiveness but not prefill compute. Cold loading, prefill and decoding require separate measurements.
- A server tested on a larger VPS is not certification on a 4 GB laptop, and three short prompts do not prove maximum-context memory bounds.
- This helper samples `/proc`, hence Linux-only. RSS sampling can miss peaks and excludes other processes/cgroup page-cache accounting.
- A free-port probe has a small bind race; a collision must fail visibly, never kill the port's existing owner.
- GitHub `releases/latest` may point to a metadata release without binaries. Enumerate releases and choose an official matching CPU asset; pin the selected tag.

## Verification
- Run both real probes and inspect nonempty output, terminal stream marker, TTFT and peak RSS.
- Read generated code and run its tests; do not label inference transport as coding-quality verification.
- Validate this frontmatter and run `python3 -m py_compile scripts/probe.py` through `terminal`.
- Evidence scope: Qwen 1.5B Q4_K_M on llama.cpp b11135 passed six real SSE requests; low-memory variant measured below 1.5 GiB. Short-output code was truncated and did not pass a code-completeness gate. No target-laptop, p95, offline network isolation, or production integration claim.
