---
name: design-qa-gatekeeper
description: Use when auditing UI craft before delivery.
version: 0.1.1
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ui-ux, qa, accessibility, responsive, craft]
    related_skills: [e2e-browser-testing, color-intelligence, ui-layout-intelligence, typography-ux-copy]
---
# Design QA Gatekeeper

Audit UI work before delivery so unfinished visuals, fake affordances, cramped spacing, simulator framing, emoji leakage, or accessibility failures do not reach the user. This skill is a hard gate for web/app/dashboard design work.

## When to Use
- Before reporting a UI project as done.
- After refactoring a design in response to user criticism.
- Before adding a project to the portfolio catalog.
- Use with `visual-reference-decompiler` when the work is reference-driven.

## Prerequisites
- A running or buildable project.
- Screenshots at 390px, 768px, and 1440px for web interfaces.
- Real test output from the project test command or Playwright/Axe checks.
- If the task is visual, at least one screenshot must be inspected with `vision_analyze` before final delivery.

## Procedure
1. Run static design checks. Completion: `scripts/design_qa_scan.py PROJECT_DIR --json` exits successfully and findings are triaged.
2. Run build and automated tests. Completion: the real command output exits 0, or blockers are reported plainly.
3. Capture responsive screenshots. Completion: mobile, tablet, and desktop artifacts exist, with expected count, actual PNG pixel dimensions, and nonzero byte sizes verified programmatically. Re-read viewport dimensions and the real scroll container immediately before capture; navigation, focus, or `scrollIntoView()` can invalidate the earlier viewport/scroll setup. On long operational pages, capture both the top-level hierarchy and a second viewport scrolled to the primary data object; compensate fixed headers so one complete row/card shows its identity, outer border, every label/value/status, and every action.
4. Check overflow and accessibility. Completion: mobile `scrollWidth <= clientWidth`, keyboard/focus behavior works for modals/drawers, and Axe has no violations unless explicitly waived. For dense reports, also measure every touch target at ≥44px, keep wide-table overflow inside its ledger container, prove the far-right action column is reachable at maximum `scrollLeft`, label breadcrumb/table regions, set header `scope`, and emulate print to confirm controls disappear, `thead` repeats, and rows/cards use `break-inside: avoid`. For mobile record cards, action groups must also look actionable: keep sibling actions on a stable grid, equalize heights, prevent label wrapping, and distinguish informational/locked controls from destructive or primary actions without relying on color alone.
5. Inspect final visual output and spatial alignment: run spatial alignment audit (`canvas_audit_layout` or `/home/ubuntu/.hermes/scripts/canvas_layout_inspector.py audit`) to verify outer margin symmetry (L vs R diff <= 10px), grid gaps, and center alignment. For animated SVG/canvas elements, audit geometric anchors (`canvas_audit_svg`) to guarantee every scaled or rotated element has an explicit `transform-origin`. Ask neutral questions for visible mismatches, unreadable text, repetitive structure, task visibility, and state continuity—not confirmation that the redesign is fun or successful. Treat a vision model's praise or numeric score as an opinion, not acceptance evidence; it cannot override the user's rejection. Completion: observed issues are tied to the final screenshot/DOM, and owner approval remains distinct from technical verification.
6. Verify catalog/live deployment when applicable. Completion: public route returns HTTP success and screenshot matches the new build.

## Hard Blockers
- Ornamental kicker badges & tech-bragging tag clutter (e.g. `VOL. 02 // PORTFOLIO`, `100% Zero AI-Slop`, `WCAG AAA (≥ 7:1)`, `60 FPS In-Place Morphing`). Quality must be proven through typography, ample space, and real interaction—never proclaimed via decorative floating pills.
- Fallback view (2D/no-GPU/no-JS) looking like an unfinished wireframe while primary view is styled. Fallback must be visually intentional from pass 1.
- Public static deploy lacking cache-busting version strings on CSS/JS when verifying changes on mobile.
- Unicode emoji or Extended Pictographic symbols in UI code.
- Phone/device/mockup framing when the user asked for direct web/app UI.
- Generic template imagery where authentic references/photos are required.
- Fake form submission or backend claims without real persistence.
- Dashboard built like a marketing landing page when the request is a true app shell.
- Horizontal overflow at 390px mobile viewport.
- Missing focus states or inaccessible interactive elements.

## Static Scan Coverage
The helper script checks source files, including Laravel `*.blade.php`, while skipping dependencies, archived backups, and generated storage so findings stay actionable:
- Emoji / Extended Pictographic leakage.
- Floating ornamental kicker badges or boastful tag strips (`hero-pill`, `Zero AI-Slop`, `WCAG AAA`, etc.).
- Device simulator terms like `phone mockup`, `bezel`, `dynamic island`, or `viewport switcher`.
- Generic AI-slop labels such as `premium`, `modern`, or `beautiful` overused in code comments/copy.
- CSS risks: `overflow-x: scroll`, disabled outlines, and layout-animation properties.

Static checks are not enough. A clean static scan does not replace Playwright, Axe, screenshots, or visual inspection.

## Pitfalls
- Do not treat empty grep output as a completed audit; use the helper or explicit file reads.
- Do not claim deployed success from a build alone; verify the public route or copied static directory. Report candidate-written, integrated-tested, deployed, and owner-approved as distinct states; having separate HTML/CSS/JS files or a worker's passing helper tests proves none of the later states.
- Attach numerical claims to their actual measurements: contrast ratios to the final rendered foreground/background pairs, FPS to a motion trace and device, and persistence compatibility to an old-data mutation/reload fixture. HTTP 200 proves delivery, and a screenshot proves one visible state; neither establishes AAA compliance, 60 FPS, or absence of data-loss risk. State NOT RUN when the measurement was not performed.
- Target task interactions by stable record ID or current semantic state, not array position, because pinning/completion can reorder the list after every click. Re-query after mutations and assert the intended record changed; index-based toggles can undo a different task and misdiagnose correct behavior.
- Do not average responsive quality; the smallest viewport is a hard constraint.
- Never add floating kicker tags or feature-bragging badge strips to fill space; users find decorative meta-pills tacky and repulsive.
- Treat a low user score as evidence that the brief or reference was missed, not approval of a different brief. Use the rejection decision in `ui-ux-execution-standard`: preserve an incumbent for refinement/restoration; when redesign was already explicitly authorized, correct within that scope without asking the user to repeat the authorization. Do not present the next unreviewed aesthetic as an established improvement.
- Treat delegated QC as a versioned snapshot, not a timeless verdict: bind it to the final source hash and exact post-remediation artifact paths. Every CSS/markup edit invalidates prior screenshots and verdicts, even when tests still pass; stop in-flight reviewers of stale artifacts, regenerate the full evidence matrix, then request one final read-only verdict. Reject recommendations for work already visible in the supplied hash.
- Do not call ordinary document continuation “clipping” because the screenshot ends mid-row. Distinguish viewport fold from layout failure with DOM bounds, document scroll reachability, wrapper scroll reachability, and a second screenshot of a complete record; only hidden/unreachable content is a blocker. Before diagnosing a sticky-header overlap, inspect current scroll offsets and the target element's rectangle: focus may have scrolled a valid layout beneath the header.
- When `vision_analyze` fails (non-vision model returns unsupported_modality), do not skip visual inspection — delegate it to a vision-capable leaf subagent via `delegate_task` with the screenshot paths in the `images` field, require a GO/NO-GO with file:line evidence, and re-verify DOM/bounds yourself; a self-report is not proof.

## Verification
- Static scan completed.
- Build and tests completed.
- Screenshots captured at required breakpoints.
- Visual inspection completed.
- Final response includes only verified facts: live URL, tests, commits, and remaining limits.
