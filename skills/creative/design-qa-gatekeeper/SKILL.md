---
name: design-qa-gatekeeper
description: Use when auditing UI craft before delivery.
version: 0.1.0
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
3. Capture responsive screenshots. Completion: mobile, tablet, and desktop artifacts exist.
4. Check overflow and accessibility. Completion: mobile `scrollWidth <= clientWidth`, keyboard/focus behavior works for modals/drawers, and Axe has no violations unless explicitly waived.
5. Inspect final visual output. Completion: `vision_analyze` confirms the screen matches the user's latest instruction, not stale assumptions.
6. Verify catalog/live deployment when applicable. Completion: public route returns HTTP success and screenshot matches the new build.

## Hard Blockers
- Unicode emoji or Extended Pictographic symbols in UI code.
- Phone/device/mockup framing when the user asked for direct web/app UI.
- Generic template imagery where authentic references/photos are required.
- Fake form submission or backend claims without real persistence.
- Dashboard built like a marketing landing page when the request is a true app shell.
- Horizontal overflow at 390px mobile viewport.
- Missing focus states or inaccessible interactive elements.

## Static Scan Coverage
The helper script checks common blockers:
- Emoji / Extended Pictographic leakage.
- Device simulator terms like `phone mockup`, `bezel`, `dynamic island`, or `viewport switcher`.
- Generic AI-slop labels such as `premium`, `modern`, or `beautiful` overused in code comments/copy.
- CSS risks: `overflow-x: scroll`, disabled outlines, and layout-animation properties.

Static checks are not enough. A clean static scan does not replace Playwright, Axe, screenshots, or visual inspection.

## Pitfalls
- Do not treat empty grep output as a completed audit; use the helper or explicit file reads.
- Do not claim deployed success from a build alone; verify the public route or copied static directory.
- Do not average responsive quality; the smallest viewport is a hard constraint.
- Do not patch cosmetics after a score below 5; use a total reference-driven rebuild.

## Verification
- Static scan completed.
- Build and tests completed.
- Screenshots captured at required breakpoints.
- Visual inspection completed.
- Final response includes only verified facts: live URL, tests, commits, and remaining limits.
