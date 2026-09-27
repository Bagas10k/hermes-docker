---
name: agent-sub50ms-visual-feedback
description: Use when measuring frame-delta visual feedback.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vision, frame-delta, latency, aci]
    related_skills: [vision-agent-computer-interface]
---

# Frame-Delta Visual Feedback

Detect changed regions without treating pixel movement as task success. Sub-50ms is a measurement target, not a guarantee or an LLM inference claim.

## When to Use
- Measure perception cost and reject stale observations in a vision-action loop.
- Gate expensive visual inference using spatial changes in decoded frames.
- Do not use pixel deltas alone to authorize clicks or confirm transactions.

## Prerequisites
- Python 3.10+ and NumPy for the offline reference detector.
- For browser integration: authorized video capture, feature detection for requestVideoFrameCallback, bounded worker ownership, and calibrated timestamps.
- Read [measurement and architecture](references/architecture.md) before interpreting latency.

## Quick Reference
Through `terminal`, run `python3 <skill-dir>/scripts/test_delta.py`.
Detector: `Detector().observe(rgb_uint8, sequence, capture_ms, now_ms)`; timestamps must share a monotonic clock domain. Output state is baseline, stale, unchanged, or changed, never task_success.

## Procedure
1. Declare scope: decoded-frame CPU processing versus capture-to-feedback versus action-to-verified-result. Completion: timestamp origins and clock uncertainty recorded.
2. Record a prediction: unchanged images produce no regions, a tiny local mutation must survive, stale/out-of-order frames must not replace the baseline. Completion: negative controls specified before testing.
3. Ingest frames with one worker and at most one pending latest frame. Close replaced and processed VideoFrames in finally blocks. Completion: outstanding resources remain bounded under a deliberately slow consumer.
4. Compare RGB channels in signed arithmetic, threshold per-pixel maximum channel difference, aggregate changed pixels into tiles. Reset baseline on dimensions changing. Completion: edge tiles and single-pixel changes pass tests.
5. Use deltas to invalidate affected grounding candidates, not to reuse stale coordinates. Reground before action after resize, scroll, navigation, focus change, or overlays. Completion: action binds to fresh sequence and geometry revision.
6. Collect processing p50/p95/p99 and frame-age distributions separately. Report dropped, stale, missed-callback and full-refresh counts. Completion: no capture or network claim based on a CPU-only benchmark.
7. For actual success read the authoritative DOM/application state after the action, with an independent visual check where relevant. Timeout means unknown; reconcile before any non-idempotent retry. Completion: postcondition is explicit and verified.

## Pitfalls
- requestVideoFrameCallback follows composition; it is not a capture interrupt or real-time scheduler.
- Downsampling can erase small text, cursor or button changes. Preserve native-resolution target ROIs, periodically refresh the full semantic state, and invalidate all geometry on viewport changes.
- Compression noise, blinking cursors, and animations cause false positives. Thresholds require labeled UI calibration; temporal debounce must not hide short-lived errors.
- Uint8 subtraction wraps. Convert before subtraction. RGB-only matching ignores alpha: composite to a fixed background first.
- Same pixels can hide changed application state. Pixel silence never proves success.
- Latest-only queues suit observations, not commands, receipts, or audit events.
- Remote captureTime is estimated; missing metadata means unmeasured, not zero latency.
- The helper is offline CPU reference code, not a browser transport, semantic detector, or proven production memory bound.

## Verification
Run the supplied test twice. It exercises synthetic frames with explicitly known ground truth and prints measured CPU quantiles. Browser/WebRTC, live screen capture, network jitter, GPU readback, human-visible response, and semantic success remain unverified until separately instrumented. Never promote this result into a sub-50ms end-to-end claim.
