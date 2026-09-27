---
name: live-sandbox-hot-preview
description: Use when building isolated live code previews.
version: 0.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vibe-coding, sandbox, live-preview, postmessage]
    related_skills: [vibe-coding-accelerator]
---

# Live Sandbox Hot Preview

Build an executable HTML/CSS/JavaScript playground with a persistent editor and replaceable preview. This is a local trusted-draft tool, not a hostile-code execution service or framework HMR implementation.

## When to Use
- Rapidly iterate a visual artifact without reloading the editor.
- Capture syntax errors, runtime errors, and rejected promises next to a preview.
- Do not use for unknown third-party code, secrets, server programs, or package-based applications requiring a bundler.

## Prerequisites
- A modern browser and the packaged `templates/playground.html`.
- Resolve this skill directory through `skill_view`; copy the template to a disposable project workspace using file tools before customization.
- No dependency installation, credentials, external fonts, or CDN is required.
- For browser automation, use `browser_exec`; local file paths work only when the browser can access that filesystem. Otherwise use an explicitly local static server, not a production route.

## Quick Reference
- Open: `browser_exec(code="new_tab('file:///absolute/workspace/playground.html'); print(page_info())")`.
- Edit the three text fields; select **Run preview**. Auto-run is opt-in for trusted edits only.
- **Stop** removes the frame and pending debounce timer; a later run starts clean.
- Source architecture and limitations: `references/protocol.md`.
- Recorded browser checks: `references/browser-evidence.json`.

## Procedure
1. Define trust and acceptance before running: trusted HTML/CSS/JS, no credentials, no external networking. Success: choose a concrete interactive behavior and expected error outcome.
2. Open the copied artifact and keep manual Run as the default. Success: editor survives preview replacement and works at desktop and narrow viewport widths.
3. Preserve `sandbox="allow-scripts"` without `allow-same-origin`. Install CSP before any preview content. Success: attempts to read parent DOM throw SecurityError, and fetch is blocked.
4. Preserve the one-shot handshake: child ready, parent sends code, child executes. Validate source window, channel, generation, bounded fields, allowed kinds, and opaque origin on the parent. Success: a message from the parent window itself cannot alter status.
5. Replace the entire iframe on every run; do not eval edits into the old global scope. Success: timers, closures, and old listeners do not accumulate across runs. Preview state resets by design.
6. Capture errors before injecting code. Keep error state sticky even after the executed acknowledgement. Success: both a syntax failure and a rejected promise remain visible as errors.
7. Opt into 300 ms debounce only after verifying trusted inputs. Success: burst typing triggers the latest edit, not a build per keystroke; Stop cancels pending work.
8. Exercise the real artifact: counter clicks, edits, syntax/runtime/promise errors, parent isolation, blocked network, forged messages, and Stop. Success: save structured pass/fail evidence and report limitations rather than claiming universal security or performance.

## Pitfalls
- Opaque frames require wildcard target origin; this exception does not authorize sending secrets. Source validation is essential; origin `null` alone is insufficient.
- Do not add allow-same-origin to fix a convenience issue. For external dependencies use a deliberately separate-origin architecture and reviewed CSP.
- Error events do not necessarily stop script insertion from returning; executed means the insertion returned, not that the program succeeded.
- A sandboxed frame is not a CPU quota. An infinite loop may block the renderer and Stop/watchdog; hostile code needs stronger process isolation.
- CSP here blocks ordinary fetch/resource paths, not every possible exfiltration/navigation channel. Never place secrets in drafts or treat this as an adversarial security boundary.
- Scripts inside HTML inserted with innerHTML do not run normally; executable code belongs in the JavaScript field. Inline event handlers may run under this CSP.
- Error logs use textContent and are bounded; do not turn draft output into parent HTML.
- Acknowledgement latency is not paint latency, p95, or proof of user flow improvement. Measure distributions under realistic workloads before making speed claims.

## Verification
The packaged artifact was browser-tested for interactive counter updates, runtime/syntax/promise errors, blocked parent access, blocked fetch, Stop, forged-source rejection, sticky errors, and 390px overflow. These checks establish bounded functional evidence, not visual aesthetic approval, cross-browser coverage, or hostile-code safety. Re-run them after modifying the protocol. Keep human flow-state benefits labelled as a hypothesis until evaluated with actual use.
