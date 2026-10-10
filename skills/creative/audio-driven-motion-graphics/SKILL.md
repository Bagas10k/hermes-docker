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

## Canvas-First Editing Workflow

When asked for a canvas before the complete generator, deliver a standalone usable editor surface first: import local video, preview and scrub a bounded IN/OUT segment, switch output ratio (9:16 / 16:9 / 1:1) and contain/cover, preview named transitions and easing, and export an explicit edit-plan JSON. For a web-based clip-selection test, add a standalone page where the user sets a bounded option count (1–10), previews each range, edits IN/OUT, selects clips, and exports the selection plan; keep the source video local to the browser unless a separately authorized upload workflow exists. Make the initial range generator explicit: evenly spaced ranges are a UI exercise, not content-aware highlights or actual MP4 cutting. Verify an actual short video fixture by setting the file input, waiting for metadata, generating N options, selecting one, and checking horizontal overflow at desktop and mobile widths. Distinguish JSON plans and browser previews from rendered MP4, automatic voice-over synchronization, and remote podcast extraction.

For long remote sources, treat URL entry as a note until a validated server-side segment fetch exists. A browser-only URL field does not prove range retrieval without downloading the whole source; verify authorized access, precise start/end extraction, transferred bytes, and output before claiming it works. Keep this gate separate from local file trimming so the first canvas is honestly usable.

## Curated Source-Video Workflow

For short-form clips from a long-form channel, follow this order: receive the authorized channel and visual reference; list recent videos without downloading footage; read timestamped transcripts; propose at most ten distinct 20–30-second ranges (up to 60 seconds only when the idea needs it); verify every quote and its surrounding context; then present candidates for human selection before fetching or rendering. Show source URL, IN–OUT, duration, exact quote, context, hook/payoff, visual treatment, rights risk, and an editorial score broken into hook 0–25, substance 0–30, retention rationale 0–25, visualizability 0–20. Treat lexical/heuristic scores only as screening, never final editorial scores or a prediction of views. Do not manufacture controversy from a clipped quote. Without an explicit candidate selection, the operator must stop at the shortlist: no footage fetch, render, or publication. A selected candidate first becomes a private draft for review, never an automatically published final.

After selection, verify rights and test segment-only extraction on that source: log transferred bytes and output duration, since a section request does not prove it avoided downloading the full stream. Reframe 16:9 footage shot by shot using a lightweight two-tier pipeline:
1. Detect camera switches via FFmpeg built-in scene filter (`select='gt(scene,0.35)',showinfo`) to create hard shot boundaries.
2. Sample frames and detect face centers with a lightweight detector only to estimate a crop, not to identify who is speaking. On a multi-face shot, fail closed and request manually reviewed keyframes until audiovisual speaker attribution has been validated on representative real interviews: mouth-region pixel motion alone also reacts to smiles, head movement, and camera motion.
3. Within continuous shots, smooth genuine repositioning and suppress small jitter; at camera cuts, jump directly to the newly reviewed center (`cut: true`). Fall back to a safe composition when no face is present. Verify the vertical render on real representative footage, including two-shot and camera switches, before claiming automatic speaker tracking.
4. Word-Level Subtitle Draft & Karaoke Burn-In: Run faster-whisper (tiny or base, int8 CPU) for approximate word timestamps, then review words and timing against the source audio; this is transcription with inferred timings, not guaranteed forced alignment. Generate `.ass` subtitles in short phrases (3–5 words, max 2 lines) with `\k<centiseconds>` karaoke tags and a high-contrast background. Check placement on a phone against the actual speaker and platform overlays; a fixed margin alone does not prove a safe area.
5. SVG Composition & Output QA: Render a validated SVG to an alpha buffer, then overlay and burn reviewed subtitles into a draft MP4. A single static SVG with fade is **not** inter-object morphing; an animation-parameter matrix is **not** a set of visually evaluated renders. Browser-preview SFX are not present in the MP4 unless the audio streams are actually mixed. Probe the finished MP4 for duration, dimensions, video/audio streams, and inspect sampled frames/audio before describing morphing, SFX, or readability as shipped.

For this user's short-form visual direction, make explanatory illustrations and icons recognizable SVGs, use restrained UI-like motion, and keep subtitles legible on a phone within platform safe areas without obscuring the speaker. Build subtitle cues from verified speech timing: keep phrases short (at most two lines), let ordinary words remain calm, and choose a single context-appropriate emphasis for a meaningful word or contrast—weight/scale, underline, reveal, or placement—rather than repeating one animation on every phrase. When the user asks for emphasis *inside* a mechanism animation, add one short, transient label near the active operation per beat—not a second continuous subtitle track. Position each label against connector paths and card bounds, then inspect stills at branching, convergence, and final delivery; a diagonal connector can cross legible-looking text even when cards do not collide. Review each shot's composition and emphasize only words actually spoken; a style demo is not synchronized or rendered subtitles.

## Private Draft and Publication Gate

Keep source footage, render drafts, candidate manifests, and test fixtures outside any publicly served directory. First produce a shortlist, then render only the chosen candidate into a private draft; review exact quote/context, face framing, subtitles, audio, asset rights, and the actual MP4 before asking the user to approve publication. Publishing requires explicit authorization and an independently verified public URL; marking an item `ready` or copying it into a web directory is a public side effect, not an internal test. If an old public draft must be withdrawn, move it outside the served tree, verify the old URLs return 404, and relabel archived test media as unreviewed rather than deleting it. Test the negative gate (no selection => no render or public write) and the served route as well as the unit suite.

## Standard Video Specifications

- **Default format:** Vertical 9:16 (`1080 x 1920`); let an editing canvas select other ratios explicitly.
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
For a narrated reel, synthesize the final spoken script first, inspect its actual duration, then derive scene boundaries from reviewed audio timestamps before designing transitions. If TTS emits no word boundaries and STT mishears names, use STT only to locate approximate phrase times, correct the words against the actual script/audio, and label cues as reviewed estimates rather than exact word synchronization. Use one boundaries array for headline, shape morph, secondary diagrams, and subtitle timing: separate `frame / fixedSceneLength` calculations drift as soon as voice-paced scenes vary. Keep each caption short enough to read on a phone and check a still from every scene plus transition frames for collisions.

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
The motion graphics MUST be self-explanatory on mute:
- First name the mechanism the viewer must understand; storyboard an actual state change from input through action to output, then bind narration beats to those changes. A collection of attractive standalone icons or slides explains labels, not how the system works.
- Keep one visual system across beats: persist objects, grow or move connections, branch concurrent work, converge results, and visibly test before delivery. Show failures as failures rather than substituting a checkmark for evidence. After the causal diagram reads clearly, give each active beat sustained purposeful motion (data traveling along opened paths, concurrent work visibly progressing, convergence and verification changing state); an entrance animation followed by static cards feels lifeless. Inspect short clips across each beat, not only stills or a nonzero frame-difference count, because incidental headline/progress changes do not prove the mechanism is alive.
- Use concrete recognizable objects for physical processes. For software/UI workflows, connected interface modules are appropriate when their labels, connectors, and transformations show real data or work flowing between them; generic boxes and arrows without visible causality remain insufficient.
- Keep on-screen copy sparse: one short claim per beat, with diagrams doing the explanatory work. Verify comprehension on mute using representative frames and transitions, not just a hero still.
- When given a video reference, inspect the actual clip rather than its title/thumbnail alone. Sample the full sequence, then sample adjacent frames around transitions: a contact sheet reveals composition and palette but not easing or object continuity. Extract the reference's reusable motion grammar (what persists, assembles, fades, or changes scale) and element treatment (typography, depth, color hierarchy), then apply it to the requested subject without copying branding or content. Compare rendered frames at the same kinds of beats; a palette swap alone does not reproduce the reference's pacing or visual storytelling.
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

*Pitfall (YouTube Range Requests vs Actual Transfer):* Use a supported JS runtime and a bounded `yt-dlp --download-sections` range with a suitable stream selection, then measure transferred bytes and verify the output duration for the actual source; a short output file does not prove the network avoided downloading the full source.

*Pitfall (FFmpeg Crop Filtergraph Comma Delimiter Collision):* In FFmpeg `-vf crop=w:h:x:y`, commas inside mathematical functions (like `if(cond, a, b)` or `min(x, y)`) are parsed as filter parameter separators, triggering `[AVFilterGraph] No such filter`. Always escape internal commas with a backslash (`\,`) before building the crop filter argument (e.g. `expr.replace(',', r'\,')`).

*Pitfall (Shot-Cut Discontinuity in Vertical Dynamic Crop):* When reframing horizontal 16:9 video to vertical 9:16, smooth interpolation across camera angle changes creates disorienting pans. Use smooth easing (smoothstep/cubic) strictly within continuous shots; at shot boundaries or camera cuts, execute a hard step jump (`cut: true`) to the new speaker center coordinate.

*Pitfall (Face Detection vs Speaker Attribution):* Use a face detector as a crop-position estimate only. On multi-face footage, require reviewed keyframes or a separately validated audiovisual speaker model; a confident face bounding box and mouth-region motion do not establish who is speaking.

*Pitfall (Premature True-Path Morph on Dissimilar Shapes):* Attempting true path interpolation between silhouettes with low geometric similarity (<0.75) triggers visual fold/twist artifacts; fall back immediately to decomposition or transform morphing (scale/position/radius) rather than forcing bezier node interpolation.

*Pitfall (Literal Sentence-Level Visual Switching):* Cutting to an entirely new graphic for every sentence destroys visual continuity and exhausts viewer attention; maintain a persistent hero object across adjacent beats and transform its parts or state to convey semantic evolution.

*Pitfall (FFmpeg Subtitles Filter Special Character & Path Escaping):* In FFmpeg `-vf subtitles='path.ass'`, colons, spaces, and backslashes in paths break the libass parser; always resolve absolute paths and wrap with single quotes (`subtitles='/abs/path.ass'`) or escape colons (`\:`) when constructing complex filter chains.

*Pitfall (Word-Level Karaoke Chunking & Mobile Screen Congestion):* Grouping more than 4–6 words per dialogue event in `.ass` files crowds vertical phone screens and causes text wrapping that obscures the speaker; chunk word timestamps into 3–5 word phrases with `BorderStyle=3` background boxes and `MarginV=220` (on 1080x1920) within the safe area.

*Pitfall (SVG Alpha Burn-In Pixel Format Mismatch):* Overlaying rendered vector assets without explicit alpha pixel formatting (`format=rgba`) causes black borders around transparent vector graphics; always normalize overlay inputs with `format=rgba` before chaining into the FFmpeg `overlay` filter.

## Creative Styles & References

- See `references/vector-motion-morphing-guide.md` for the complete vector motion and morphing system: semantic-to-shape translation (Makna → Objek → Hubungan → Transformasi → Timing), 5-tier asset sourcing, 512x512 SVG tokens, 4 morphing strategies (True Path, Decomposition, Transform, Mask/Reveal), and mobile safe-area subtitle contracts.

- See `references/motion-genres-and-techniques.md` for taxonomy and decomposition of kinetic typography, SDF raymarching, creative coding shaders, particle simulations, video reel ffmpeg extraction pipelines, 1-style-per-view multi-chapter architecture, and the Frame 023 high-density motion bento pattern.
- See `references/theory-motion-pipeline.md` for the 5 Theory Visual Archetypes (`hook`, `metric`, `mechanism`, `comparison`, `outro`), JSON choreography schema, and dynamic Remotion `--props` workflows.
- See `references/neobrutalism-notebook-style.md` for tactile bento cards, scotch tape textures, graph paper backgrounds, and highlighter animations.
- See `references/rendering-and-headless-ops.md` for production render flags, PM2 studio management, and multi-core scaling.
