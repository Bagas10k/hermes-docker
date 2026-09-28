---
name: audio-driven-motion-graphics
description: "Use when building audio-driven motion graphics with code."
version: 1.0.0
author: Bagas & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [remotion, motion-graphics, video, audio-reactive, react, animation]
    related_skills: [manim-video, spring-physics-motion-lab, motion-principles]
---

# Audio-Driven Motion Graphics Engine

Pipeline for generating programmatic, frame-accurate motion graphics and vertical video reels (9:16) driven by audio narration using Remotion (React/TypeScript).

## System Architecture

```
[Audio Input (.mp3/.wav) OR Text Script (edge-tts)]
       ↓
[faster-whisper STT (CPU int8)] -> Millisecond word timestamps [{word, start, end}]
       ↓
[Causal Theory Planner (LLM)] -> Deconstructs script into 5 Theory Visual Archetypes
       ↓
[Parametric Remotion Engine] -> Dynamic React props injection (<TheoryMotionComposition />)
       ↓
[Verification & Export] -> Remotion Studio (:3300) / API (:3350) / Headless Render (.mp4)
```

## Standard Video Specifications

- **Format:** Vertical 9:16 (`1080 x 1920`).
- **Framerate:** 30 FPS (`1 second = 30 frames`).
- **Duration Formula:** `totalFrames = Math.ceil(audioDurationSeconds * fps)`.
- **Audio Alignment:** Never guess audio duration; inspect metadata with `ffprobe` before declaring composition duration.

## Step-by-Step Workflow

### Step 1: Ingest Audio & Derive Precise Duration
Extract metadata from the target narration audio:
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input_audio.mp3
```
Calculate frame budget:
```typescript
const FPS = 30;
const DURATION_SECONDS = 30.5; // from ffprobe
const TOTAL_FRAMES = Math.ceil(DURATION_SECONDS * FPS); // 915 frames
```
*Pitfall:* Never set composition duration shorter than audio duration; Remotion truncates audio tracks that exceed composition frame bounds.

### Step 2: Storyboard Planning & Scene Timing
Divide the script into sequential scene intervals. Each scene is wrapped in a `<Sequence>` component with explicit `from` and `durationInFrames`:
```tsx
<Sequence from={0} durationInFrames={120}>
  <SceneHook />
</Sequence>
<Sequence from={120} durationInFrames={240}>
  <ScenePointOne />
</Sequence>
```

### Step 3: Implement Visual Motion Components
Use declarative springs and interpolations rather than manual CSS keyframe timers:

```tsx
import { spring, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

// Entrance pop-in with spring physics
const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const scale = spring({
  frame,
  fps,
  config: { damping: 14, stiffness: 140, mass: 0.8 },
});

// Highlighter sweep across key phrase
const highlightWidth = interpolate(frame, [10, 30], [0, 100], {
  extrapolateLeft: 'clamp',
  extrapolateRight: 'clamp',
});
```

*Pitfall:* Always add `{ extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }` to `interpolate()` calls to avoid visual overshoot before the animation begins or after it settles.

### Step 4: Live Verification via Remotion Studio Daemon
Launch Remotion Studio for interactive inspection and scrubbing:
```bash
pm2 start "npx remotion studio --port=3300 --no-open" --name "hermes-motion-studio"
```
*Pitfall:* Never run `npx remotion studio &` via bare bash background subshells; child processes retain stdout/stderr handles and cause automation runners to hang indefinitely. Use PM2 process management.

### Step 5: Headless Video Rendering
Render final MP4 directly on the server:
```bash
npx remotion render src/index.ts <CompositionId> output/final.mp4 \
  --gl=angle \
  --concurrency=4 \
  --quality=85
```
*Pitfall:* On headless Linux servers without discrete GPUs, Chromium crashes during WebGL context creation unless `--gl=angle` or `--gl=swiftshader` is passed. Always use `--gl=angle`.

## Autonomous End-to-End CLI & REST API

### 1. The "Visual-First" Principle
The motion graphics MUST be 100% self-explanatory on mute:
- Each sentence/beat maps directly to an active physical simulation or diagram (cross-section cutaway, fluid displacement, vector forces, molecular chaos, bottleneck flow, balance scale).
- **Haram Kotak/Card Abstrak (Concrete Physical Objects Required):** Never use generic gray wireframe boxes or abstract cards with arrows to depict entities. The viewer cannot tell what the object is without sound and will rate it poorly. Always render recognizable procedural SVG vector illustrations of the actual physical entities (e.g., an expressive robot with antennas and toolbelt holding CLI/wrench, an actual rocket fuselage blasting fiery exhaust downward, an actual boat bobbing on waves, or an actual terminal screen displaying a real fatal error code transitioning to a green resolved state).
- **Layout Balance & Character Isolation:** Never let characters or mascots overlap code or reading text; isolate them in a dedicated status dock at the bottom or side. Distribute elements evenly across the 1080x1920 canvas so the lower half is not left empty—anchor it with data conduits, synergy cards, or formula banners. For loop cycles, provide explicit directional flow arrows (`1 → 2 → 3 → 4 → 1`) with distinct pastel background contrasts.

### 2. Autonomous Pipeline CLI
Generate theory motion graphics directly via command line with automatic audio alignment:
```bash
# Option A: Standalone theory-motion production CLI (Recommended)
node /home/ubuntu/theory-motion/bin/theory-motion.js generate "Theory Name or Prompt" -o output/video.mp4

# Option B: From recorded voice audio or script text
node /home/ubuntu/hermes-motion-engine/bin/hermes-theory-motion.js \
  --audio /path/to/voiceover.mp3 \
  --topic "Theory Name" \
  --output output/video.mp4
```

### 3. REST API Endpoints (PM2 Port 3350)
- `POST /api/theory/generate` or `POST /api/motion/generate`: Triggers async pipeline `{ prompt, voice, outputPath }`, returns `{ jobId, statusUrl }`.
- `GET /api/theory/jobs/:id` or `GET /api/motion/jobs/:id`: Polls job rendering progress (0% to 100%).
- `GET /api/theory/videos` or `GET /api/motion/videos`: Lists all completed video files with streamable URLs.

## Critical Pitfalls & Engineering Gates

*Pitfall (Headless Render Command Timeout):* For long compositions (>1,000 frames or >30 seconds), Remotion headless render takes ~2 to 3 minutes on CPU/ANGLE. Shell commands running the render must specify an explicit generous timeout (e.g. `timeout=600`) to prevent the automation runner from killing the command prematurely with exit code 124.

*Pitfall (Domain Label Hardcoding in Visual Archetypes):* Never hardcode domain-specific labels (e.g. "air", "lambung kapal", "fluida") inside generic archetype views (`ForceVectorsView`, `CrossSectionView`). Always bind labels to dynamic semantic beat props (`leftEntity`, `rightEntity`, `formula`, `visualHeadline`) so that non-fluid theories (mechanics, rocketry, data pipelines) do not display mismatched fluid diagrams.

*Pitfall (LLM JSON Completion SSE Stream Hang):* When requesting JSON objects from OpenAI-compatible router endpoints (e.g. 9Router) via `fetch()`, always pass `stream: false` explicitly alongside `response_format: { type: 'json_object' }`. Without `stream: false`, some router configurations default to server-sent events (`data: {"id"...`), causing `JSON.parse` to crash.

*Pitfall (Pictorial Emoji vs Dingbats Scoping):* Scope Zero-Emoji validator regexes strictly to pictorial emoji ranges (`\u{1F300}-\u{1F5FF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}\u{1F900}-\u{1F9FF}\u{1FA70}-\u{1FAFF}`). Do not use broad ranges like `\u{2700}-\u{27BF}` which inadvertently match standard technical symbols like `[✓]` (`\u2713`), `[•]`, `[→]`, `[+]`, and `[-]`.

*Pitfall (Express Reverse Proxy Stream Hang):* When reverse-proxying `POST` requests to the motion backend, if `express.json()` has already parsed `req.body`, calling `req.pipe(proxyReq)` hangs indefinitely because the body stream is already consumed. Always check if `req.body` exists, serialize with `JSON.stringify(req.body)`, set `content-length: Buffer.byteLength(postData)`, and write via `proxyReq.write(postData)` and `proxyReq.end()`.

## Creative Styles & References

- See `references/motion-genres-and-techniques.md` for taxonomy and decomposition of kinetic typography, SDF raymarching, creative coding shaders, particle simulations, video reel ffmpeg extraction pipelines, 1-style-per-view multi-chapter architecture, and the Frame 023 high-density motion bento pattern.
- See `references/theory-motion-pipeline.md` for the 5 Theory Visual Archetypes (`hook`, `metric`, `mechanism`, `comparison`, `outro`), JSON choreography schema, and dynamic Remotion `--props` workflows.
- See `references/neobrutalism-notebook-style.md` for tactile bento cards, scotch tape textures, graph paper backgrounds, and highlighter animations.
- See `references/rendering-and-headless-ops.md` for production render flags, PM2 studio management, and multi-core scaling.
