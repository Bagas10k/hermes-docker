---
name: ui-ux-execution-standard
description: "Use when implementing UI/UX. Preserve behavior; verify UI."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ui, ux, execution, accessibility, browser-verification, design-system]
    related_skills: [ui-ux-design-vault, upnormal-ui-architecture, design-qa-gatekeeper, browser-keyboard-accessibility-verification]
---

# UI/UX Execution Standard

## When to Use

Use when implementing, polishing, or verifying web/app UI/UX. Preserve existing behavior and verify the real interaction in a browser.

This standard governs execution and verification; it does not impose one universal visual theme.

## 1. Start from the actual product

- Read applicable repository instructions, current design tokens, shared components, target route/view, and existing behavior before editing.
- Treat explicit user references, brand rules, accessibility, and security requirements as hard constraints. Reuse the product's visual language; do not copy a component palette into unrelated products.
- Prefer one shared, small primitive when the same interaction belongs across pages. Avoid a project-wide redesign when the request is a bounded component change.
- For multi-step work, state concrete scope and binary checks before broad edits. Preserve unrelated dirty work.

## 2. Preserve the behavior contract

- Keep form actions, methods, names, IDs, validation, data attributes, events, and URL/query contracts unless the user explicitly changes them.
- For enhanced inputs, retain a semantic successful form control as source of truth. A visual layer may localize or theme it, but must not change submitted values or bypass listeners.
- Keep a usable fallback when enhancement is unavailable. Do not hide or disable the base control before enhancement initializes successfully.
- Do not add fake interactions, unsupported fields, or persistence claims to make a preview look complete.
- Use neutral synthetic fixtures only; never put personal or real business data in demos/tests.

## 3. Make interaction accessible and bounded

- Use native semantic controls where they satisfy the product contract; add a custom surface only when a real design or platform-consistency need warrants it.
- Verify keyboard access, focus visibility/restoration, accessible name/state, disabled/read-only behavior, validation, and boundary values for the interaction.
- Respect `prefers-reduced-motion`; keep transitions finite and tied to a user action. Do not claim frame rate or hardware acceleration without measurement.
- Test relevant edge cases such as empty/required values, min/max, reset, dynamic insertion, and known JavaScript consumers.

## 4. Keep project build documentation useful

When UI work changes a project's setup, build/test commands, routes, design-system contracts, or reusable component behavior, update the existing canonical documentation in the same change. Read docs first; document verified commands and behavior only; link to focused architecture notes rather than repeating them. For visual-only changes that do not alter how the project is built or maintained, avoid unnecessary doc churn. Follow `project-build-documentation`.

## 5. Verify the running UI, not just source text

- Run the smallest relevant automated check in a verified isolated environment; never point tests at a live business database.
- Open the rendered target route in a browser when access exists. Exercise the control as a user would, then assert visible output and underlying form/API value. A DOM click alone does not prove keyboard operation.
- Capture and inspect screenshots at relevant narrow and wide viewports; check clipping, overlap, and horizontal overflow. Use the real route where possible. Label a synthetic preview as a preview, not live-page verification.
- Re-run checks after the final source change. Report automated results, browser/visual evidence, untested gates, and whether production state or deployment changed as separate facts.
- If authenticated access is unavailable, do not invent a session or claim the live authenticated screen was verified.

## 5. Approved date-picker reference

The green-and-white Kasir Bangunan date picker is the approved visual reference for date selection in that product: a clean white popover, Indonesian month and weekday labels, weekly date grid, restrained deep-green selected state, visible month navigation, and disabled dates outside `min`/`max`. Its native date input remains the source of form values (`YYYY-MM-DD`), with localized display and existing `input`/`change` events preserved.

For another product, reuse the interaction and verification lessons only; adopt that product's colors, typography, density, and motion. Do not impose the Kasir palette or a custom picker where the product does not need one.

## Completion gate

Call UI work complete only when requested scope is implemented and relevant behavior checks pass. Separate verified, not tested, and remaining scope in the handoff. A shared CSS foundation or screenshot alone does not prove every page or interaction complete.

## Related workflows

For Kasir Bangunan form contracts, live bind-mount safety, and date input specifics, also load `kasir-bangunan-app-workflow`. For visual quality gates, load `design-qa-gatekeeper`; for real keyboard verification, load `browser-keyboard-accessibility-verification`.

Skipped: no universal palette or custom-control mandate. Add either only when the product brief or evidence requires it.

## Design Principles

Follow the design system's current project references and required research gate for interaction design; do not treat this execution standard as permission to reuse a default aesthetic.