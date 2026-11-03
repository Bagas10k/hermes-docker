---
name: code-video-information-engine
description: Use when building code-driven video engines and MCP tools.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [video-automation, remotion, mcp, information-design, edge-tts, ffmpeg, safe-zone, educational-video]
    related_skills: [bang-motion, mcp-engineering-workflow, canvas-spatial-grounding]
---

# Code-Video Information Engine

Standard operating procedures for developing and auditing code-driven video generators (Remotion, React, SVG, FFmpeg, and MCP) designed for viewer comprehension rather than superficial template animation.

## 1. The Core Law: Explanation Over Decoration

1. **Understand Before Animating:** Define the communication goal, source facts, spoken narration, visual semantic representation, and required observable proof for each beat before writing code.
2. **Visualize the Actual Quantity:** If the topic is queue accumulation, show the waiting entities accumulating and shrinking; do not replace it with generic moving particles. Distinguish arrival rate, processing capacity, actual output, and backlog.
3. **Strict Beat Consistency:** Never pair a spoken claim with an opposing visual number. If the voiceover states "capacity increases to 6", the diagram for that timestamp must show 6, not an unadjusted earlier figure.
4. **Sentence-Aligned Timing:** Synchronize subtitles and visual changes to measured voiceover timestamps from audio processing (`silencedetect`), not arbitrary mathematical word division that splits phrases unnaturally.

## 2. Recipe Banks vs Runtime Adapters

- **Data Banks are Not Renderers:** A JSON bank containing dozens of layout, motion, or text recipes is a catalog of possibilities. It does not prove the rendering engine can execute them.
- **Fail Closed on Missing Adapters:** If an editor or LLM requests a visual semantic type or motion preset without a concrete renderer implementation, raise an explicit error. Never silently substitute an unrelated layout.
- **Separate Bounded Semantic Regions from Exact Slots:** Distinguish generic bounded regions (headline, visual stage, caption bar) from bespoke multi-slot layout implementations in architecture documents.
- **Complete Visual Semantic Coverage:** When declaring support for visual types (e.g. `warning`, `comparison`, `process`, `timeline`, `quote`, `location`, `entity`, `definition`, `statistic`, `abstract`), ensure each type has an active SVG/React rendering adapter and strict matching in pipeline validation.

## 3. Audio Pipeline & TTS Reliability

- **Isolate Provider Dependencies:** When using external neural TTS engines (such as `edge-tts`), manage dependencies in an isolated virtual environment (`.venv-bakmotion/`). Upstream protocol changes can cause HTTP 403 errors on older minor versions (e.g. 7.2.7 vs 7.3.1); verify package releases before declaring audio broken.
- **Cache Narration by Hash:** Hash `voice + text + provider_version` into sidecar receipt files (`.json`). Re-render runs should reuse valid cached audio rather than hitting public rate limits.
- **Two-Stage FFmpeg Mixing & Filter Order:**
  1. Materialize voice clips into a single continuous `narration.wav` using `adelay` and `amix`.
  2. Mix the unified narration with procedural sound effects (cues) using `sidechaincompress` and `alimiter`.
  *Pitfalls:*
  - Chaining multiple `amix` nodes, sidechain splits, and filters in a single complex graph causes sample format negotiation failures in FFmpeg.
  - In FFmpeg audio filtergraphs, always place `volume` adjustments *before* the explicit `aformat` filter preceding `sidechaincompress`. Inserting `volume` after `aformat` causes the filter to renegotiate formats and fail.
  - Do not use unsupported options like `latency=1` in `alimiter` without verifying local `ffmpeg -h filter=alimiter`. Use standard `limit=0.89` directly.

## 4. Safe Zones & Spatial Verification

- **Treat Platform Dimensions as Policy:** Vertical safe zones (e.g., top 260px, bottom 420px, left 90px, right 140px on 1080×1920) represent conservative design rules to avoid platform UI overlays, not universal operating system constants. Disclose them as policies.
- **Runtime Text Clipping Protection:** In Remotion/React compositions, use DOM layout effects (`useLayoutEffect`) to compare `scrollHeight` vs `clientHeight` and `scrollWidth` vs `clientWidth`. Throw an explicit render-time error if titles or captions overflow their allocated containers.
- **Independent Layouts per Aspect Ratio:** 16:9 landscape and 9:16 portrait require different spatial arrangements. Never squash vertical layouts horizontally.

## 5. MCP Server & Tool Governance

- **Use Native MCP SDK v2:** For Python MCP servers, use `from mcp.server.mcpserver import MCPServer` and execute via `asyncio.run(server.run_stdio_async())`.
- **Wrap Tool Boundaries:** Catch internal `ValueError` and `RuntimeError` at tool entry points and re-raise as `mcp.server.mcpserver.exceptions.ToolError` so clients receive structured error responses rather than unhandled server crashes.
- **Restrict File Operations:** Bounded video rendering tools must strictly restrict output paths to designated subdirectories under the project workspace (`output/`). Reject attempts to write outside the project root.
- **Disclose Verification Gaps:** Automated passes (safe-zone checks, file hashes, FFprobe metrics) do not prove human comprehension, listening quality, or platform-native rendering. Maintain an explicit `not_run` list in all QA reports.
