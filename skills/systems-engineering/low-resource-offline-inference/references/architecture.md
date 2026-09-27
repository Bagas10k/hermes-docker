# Architecture and empirical evidence

## Sources
- Official server options: https://github.com/ggml-org/llama.cpp/blob/b11135/tools/server/README.md
- Official model: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
- Release: https://github.com/ggml-org/llama.cpp/releases/tag/b11135
- Retrieved official main README and model card during research; runtime help checked independently.

## Mechanistic model
Resident memory = resident model pages + repacked weights + KV cache + compute workspace + runtime overhead. Disk size is neither a reliable upper bound nor measured RSS. Conventional KV estimate is 2 * layers * context * KV_heads * head_dim * bytes_per_element, excluding padding and allocator overhead; use model metadata rather than guessing head dimension.

Latency = queue + load(if cold) + prefill + decode + transport. Streaming changes observability of progress, not the fundamental compute budget. Amdahl: S = 1 / ((1-p) + p/s); without measured fraction p, no speedup promise is justified.

## Bayesian experiment
Hypothesis: default CPU repacking increases resident buffers. Intervention: only append --no-repack; keep model, context 1024, slots 1, threads 2, batch 128, microbatch 64, GPU layers 0 fixed. Prediction recorded before second run: lower RAM with possible throughput cost.

llama.cpp 0.4.1-dev build 11135, commit bcbc936a8, Linux x86_64.
Model bytes: 1117320736.
Model SHA256: 6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e.

| Observation | Default repack | No repack |
|---|---:|---:|
| Sampled peak RSS KiB | 1808896 | 1197528 |
| Sampled peak RSS GiB | 1.7251 | 1.1421 |
| TTFT request 1 seconds | 2.0780 | 2.6061 |
| TTFT request 2 seconds | 0.8739 | 1.0905 |
| TTFT request 3 seconds | 0.6515 | 0.7348 |
| Total request 1 seconds | 25.7419 | 26.7428 |
| Total request 2 seconds | 24.0842 | 23.3652 |
| Total request 3 seconds | 24.3095 | 25.4693 |

RSS reduction observed: 33.80%. This is one sequential A/B, vulnerable to host load/cache differences; replicated target-hardware tests required. Known: six HTTP SSE requests delivered nonempty text and DONE. Known: low-memory run was under both 1.5 decimal GB and 1.5 GiB sampled process RSS. Uncertain: hard maximum, sustained p95, throughput on constrained CPUs, code quality across tasks.

## Negative evidence matters
The clamp answer exhausted 96 output tokens and ended inside its function. The stream transport succeeded while code completeness failed. Do not automatically execute generated code or claim this run delivered usable code snippets. Budget enough completion tokens; reserve prompt + output space; validate syntax and behavior. A small model can also ignore 'code only'.

## Design trade-offs
Choose no-repack as a measured candidate for low-RAM use, not a universal faster setting. Keep one slot to avoid concurrency memory amplification. Lower context sacrifices retained conversation; summarize deliberately and preserve current code/contracts. Increasing output budget may require trimming input, not enlarging context blindly. Enforce security and code correctness as hard constraints, optimize latency only within them.

Use Linux cgroup memory accounting and a deliberate MemoryMax/MemoryHigh policy for a real hard limit, configured only with approval. Do not mistake RLIMIT_AS for RSS control of mmap-heavy inference. Disable external fallback to preserve offline intent; verify network isolation separately before asserting fully offline deployment.

## Reproduction
Use scripts/probe.py from the parent directory. Raw JSON/logs are retained with the research note's evidence directory in the local vault. The helper does not download models, modify production services, or change providers. No fabricated responses or mocked inference are used.
