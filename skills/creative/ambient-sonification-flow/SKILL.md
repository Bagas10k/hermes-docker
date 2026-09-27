---
name: ambient-sonification-flow
description: Use when adding opt-in audio cues to coding workflows.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web-audio, sonification, flow-state, build-feedback]
    related_skills: [vibe-coding-accelerator, live-sandbox-hot-preview]
---

# Ambient Sonification Flow

Add opt-in procedural build feedback to a browser coding workspace. Ships a bounded audio controller, a working integration page, and reproducible browser verification. Audio supplements visible status; it never replaces it. This is a user-local Hermes skill, not an upstream release.

## When to Use
- Build/test status should be noticeable without leaving the editor.
- A sandbox needs optional, low-distraction success/failure cues.
- Don't use for medical treatment, guaranteed concentration, or physical haptic output.

## Prerequisites
- Modern browser with AudioContext; no credentials, audio downloads, or microphone access.
- Use `terminal` with Python 3 to serve the templates locally, or copy assets into an existing isolated preview.
- For verification use `browser_exec`; offline rendering proves signal properties, not speaker output or human comfort.

## Quick Reference
- Resolve this skill directory from `skill_view`; paths below are relative to it.
- `terminal(command="python3 -m http.server 8769 --bind 127.0.0.1 --directory <skill-directory>", background=true)` for private preview only. Check HTTP readiness before opening it. Never expose the entire skills directory publicly.
- Open `/templates/studio.html` in a browser reachable from that server.
- Load `scripts/flow-audio.js`, instantiate `new FlowAudio()`, call `enable()` directly inside a user click handler.
- Feed real terminal build results through `audio.cue('success', runId)` or `audio.cue('failure', runId)`; no shell contents or credentials enter the audio layer.
- `audio.mute()` clears active nodes and suspends context; `audio.close()` releases resources on unmount.
- See [technical evidence](references/audio-contract.md) and run [browser checks](scripts/browser-checks.js) in the page via `browser_exec`.

## Procedure
1. **Define intent.** Use visible build status as source of truth; choose success/failure and owner opt-in. Pass: UI is fully usable while silent.
2. **Choose scope.** Native Web Audio suits two short cues; use Tone.js for musical transport, Howler for streamed assets. Pass: no framework added solely to play two tones.
3. **Integrate controller.** Copy the shipped controller and connect run IDs from the actual build stream. A test button must be labeled preview, not a real successful build. Pass: repeated run ID cannot create duplicate sound within the bounded recent-ID window.
4. **Unlock deliberately.** Create/resume only inside a click; wait for resume success and handle unsupported/interrupted contexts honestly. Pass: no context before opt-in and no autoplay bypass flags.
5. **Bound work.** Permit one cue at a time, globally rate-limit starts, drop stale or hidden events, and clear nodes before suspension. Pass: burst does not become a playback backlog.
6. **Expose control.** Keep an explicit mute and low default volume; clamp volume. Hidden tab and pagehide mute without auto-resuming. Pass: coming back requires another click and no old cue replays.
7. **Verify actual browser.** Run shipped checks and click Enable, Preview success, Preview failure, Mute in the page. Record browser/version and limitations. Pass: signal rendered, nodes cleaned up, and mute gate preserved.
8. **Report precisely.** Distinguish browser-tested behavior from perceived focus or comfort. Pass: no claim of binaural therapeutic benefits or measured physical latency without evidence.

## Pitfalls
- Headless tabs may start hidden: inspect `document.hidden` and bring the test page to front through CDP before testing a trusted click. Never disable autoplay policy to make the test pass.
- AudioContext resumption is asynchronous: use a generation token so mute during unlock cannot re-enable sound later.
- Suspend alone freezes scheduled audio; remove active oscillators first or old cues can return on resume.
- Linear gain ramps can reach zero; exponential ramps cannot. Keep attack/release envelopes and start/end at zero.
- Browser clock scheduling is not speaker latency. Do not equate a 10 ms scheduling lead with 10 ms end-to-end response.
- `document.hidden` suppresses cues; hidden failures still require persistent visible status when returning.
- Binaural beats need separate ear channels and headphones to preserve intended difference; this does not establish improved concentration. Continuous ambience is intentionally not bundled by default.
- Digital peak limits do not guarantee safe acoustic sound pressure. Keep user control; avoid prolonged or unpleasant playback.
- Recent-ID deduplication is bounded, not permanent delivery semantics; the build transport owns durable deduplication.

## Verification
- Run `scripts/browser-checks.js` after the controller has loaded; require every returned check to pass.
- Verify silent default, unsupported API failure, trusted click activation, success and failure signal, duplicate suppression, burst limit, gain bound, mute, close, and node cleanup.
- Test hidden-tab behavior on target browsers and mobile device interruption separately; record anything not exercised.
- Archive JSON results with browser/version in the research note. Do not claim human auditory QA from headless tests.
