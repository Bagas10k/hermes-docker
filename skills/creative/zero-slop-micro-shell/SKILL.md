---
name: zero-slop-micro-shell
description: Use when building bounded tactile micro-app shells.
version: 0.1.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [micro-app, canvas, accessibility, geometry]
---

# Zero-Slop Micro Shell

Build a bounded single-task instrument with semantic DOM controls, decorative canvas feedback, and truthful local telemetry. This is shell correctness, not a mascot, agent roster, chat architecture, or companion identity system.

## When to Use
- A tally, timer control or similarly bounded task must remain usable in one viewport.
- Canvas feedback must not intercept controls or cause telemetry-driven layout churn.
- Squircle terminology needs mathematical and browser-support qualification.

Don't use for content-heavy dashboards, chat companions, or interfaces that inherently need long document scrolling.

## Prerequisites
Use Impeccable context/new-work/craft-floor, real reference inspection, a Chromium browser, Playwright and axe-core for testing. The artifact needs no runtime package. Test dependencies are separate liabilities, not app dependencies. Read the vault knowledge protocol before promoting findings.

## Procedure
1. Bound the job and state space. Record persistence truth, action limit, undo semantics and destructive reset. Never label in-memory state saved.
2. Partition DOM semantics, canvas pixels, and diagnostic state. Put feedback canvas inside a sized isolated stage with `aria-hidden=true`, no tabindex, and `pointer-events:none`. A native button owns activation for mouse, touch and keyboard.
3. Fit header, flexible stage and footer through `minmax(0,1fr)` and dynamic viewport units. Test the height boundary. Below the supported minimum height, allow scrolling instead of clipping essential controls. Do not globally disable zoom or selection.
4. Use native `dialog.showModal()` for protected reset; set safe initial focus, preserve Escape, restore opener and internally scroll long content. Do not introduce a modal merely for decoration.
5. Bound feedback to one pending RAF and a short elapsed-time duration. Cancel on reduced-motion change, visibility loss, pagehide and modal open. Limit DPR; keep count updates synchronous and independent of optional canvas context availability.
6. Collect real draw count and CPU draw duration in memory. Render only a snapshot when requested. Name units and scope: CPU draw work is not FPS, input latency, server CPU or energy consumption. MutationObserver should show zero idle DOM writes.
7. Treat CSS `corner-shape:squircle` as progressive enhancement with ordinary border-radius fallback. Do not claim pixel-perfect G2 from a keyword. Read references/geometry.md and run scripts/check_geometry.py through `terminal` for the mathematical distinction.
8. Test main and expanded dialog using WCAG A/AA tags, actual Impeccable detector and inspected desktop/mobile screenshots. Keep raw incompletes, calculate actual foreground/background contrast, inspect overlap and test scroll reachability. Never replace the detector with a home-grown checklist.

## Pitfalls
- Circular arcs meet straight edges with matching tangent but a curvature jump (0 to 1/r): ordinary rounded rectangles are generally G1, not G2.
- Polygonal superellipse sampling has line joins; smooth-looking does not prove G2. CSS numeric K is not the Lamé exponent n: n=2**K.
- Canvas behind text makes axe contrast indeterminate. Give text an opaque backing matching the button and inspect remaining numeral-only findings; do not globally suppress contrast.
- A full-page screenshot of a short viewport is not a viewport capture. It may show backdrop bounds and offscreen dialog content misleadingly. Capture top and bottom after real scroll and test both.
- Programmatic focus after a mouse click does not necessarily match `:focus-visible`; use keyboard modality to test keyboard rings.
- Zero detected anti-patterns means zero mechanical detector findings, not objective aesthetic perfection or complete WCAG certification.

## Verification
Run `terminal(command="python3 <skill-dir>/scripts/check_geometry.py")`; it must assert circular curvature discontinuity and n=4 endpoint curvature tending to zero. For a new app, use the evidence matrix in references/evidence.md, adapting selectors rather than weakening assertions. Preserve raw reports and browser versions. Test reduced motion dynamically, bounded values, dialog focus/Escape/return, idle DOM quietness, short viewport, and fallback rendering. Report untested physical touch, screen readers and other browser engines explicitly.
