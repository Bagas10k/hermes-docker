# Headless Rasterization Latency & Memory Benchmarking

Benchmarking headless SVG-to-raster pipelines to ensure sub-millisecond execution without memory leakage on high-concurrency server environments.

## 1. Engine Comparison: resvg-py vs CairoSVG

In server-side rendering pipelines (e.g. generating Telegram preview images, OpenGraph cards, or dynamic PDF reports):

| Attribute | `resvg-py` (Rust resvg binding) | `CairoSVG` (Python Cairo binding) |
|---|---|---|
| **Underlying Engine** | Rust (`tiny-skia` + `resvg`) | C (`cairo` + `cairocffi`) |
| **System Dependencies** | **Zero** (self-contained wheel) | Heavy (`libcairo2`, `pango`, `gobject`) |
| **Render Latency (1080p)**| **$8\text{ms} - 16\text{ms}$** | $65\text{ms} - 140\text{ms}$ |
| **Memory Consumption** | Constant $18\text{ MB}$ RSS | Spikes up to $120\text{ MB}$ RSS |
| **SVG Spec Compliance** | Full SVG 1.1 + SVG 2 paths & filters | Inconsistent clip-path and text rendering |
| **Verdict** | **Mandatory Standard** | Deprecated fallback |

---

## 2. Latency Benchmarking Protocol

A healthy procedural vector engine must satisfy the following performance gates:

```text
┌────────────────────────────────────────────────────────┐
│             PERFORMANCE LATENCY TARGETS                │
├────────────────────────────────┬───────────────────────┤
│ 1. Vector Mathematical Gen     │ < 3 ms per asset      │
│ 2. SVG XML String Compilation  │ < 1 ms per asset      │
│ 3. Headless PNG Render (1x)    │ < 15 ms per frame     │
│ 4. High-Res Retina Render (2x) │ < 35 ms per frame     │
│ 5. Total End-to-End Pipeline   │ < 50 ms per asset     │
└────────────────────────────────┴───────────────────────┘
```

---

## 3. High-Throughput Rasterization Benchmark Script

```python
import time
import resvg_py

def benchmark_resvg(svg_content: str, iterations=50):
    latencies = []
    # Warmup pass
    resvg_py.svg_to_bytes(svg_content)

    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = resvg_py.svg_to_bytes(svg_content)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)

    avg_ms = sum(latencies) / len(latencies)
    min_ms = min(latencies)
    max_ms = max(latencies)
    p95_ms = sorted(latencies)[int(len(latencies) * 0.95)]

    return {
        "iterations": iterations,
        "avg_ms": round(avg_ms, 2),
        "min_ms": round(min_ms, 2),
        "max_ms": round(max_ms, 2),
        "p95_ms": round(p95_ms, 2)
    }
```
If $P_{95} > 50\text{ms}$, profile the input SVG for excessive nested filter elements or unclosed path strings.
