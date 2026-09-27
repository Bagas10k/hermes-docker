---
name: visual-reference-decompiler
description: Use when decompiling UI references before coding.
version: 0.1.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ui-ux, reference-analysis, visual-research, design-contract]
    related_skills: [color-intelligence, ui-layout-intelligence, typography-ux-copy]
---
# Visual Reference Decompiler

Turn real visual references into a strict design contract before implementation. This skill prevents freestyle UI guessing by forcing evidence-first extraction of color, layout, typography, component DNA, and interaction patterns.

## When to Use
- User provides an Instagram, Pinterest, Dribbble, Behance, Mobbin, website, screenshot, or image reference.
- User asks for a UI/web/app/dashboard redesign and expects a high-craft visual direction.
- User rates a design below 5 and the next attempt must pivot from fresh evidence.
- Do not use for purely backend tasks, data processing, or content writing with no visual surface.

## Prerequisites
- Use `agent-reach` or browser tools for web references when direct extraction fails.
- Use `vision_analyze` on downloaded images before coding.
- Load `color-intelligence`, `ui-layout-intelligence`, and `typography-ux-copy` for the actual implementation phase.
- If no reference is supplied, query `mcp__uiux_reference__uiux_search` or `mcp__ui_layouts__search_components` before creating the design direction.

## Procedure
1. Acquire the reference assets. Completion: every source URL/image used is saved or directly accessible, and at least one visual artifact is inspected with `vision_analyze`.
2. Extract the design DNA, not a vague mood. Completion: fill `templates/design-contract.md` with color fingerprint, layout grid, typography ladder, component signatures, texture/material rules, and interaction model.
3. Identify negative constraints. Completion: explicitly list what must not be copied, what would look fake, and which old mistake this prevents.
4. Convert the reference into a product-specific adaptation. Completion: the contract names the target product, core screens/widgets, and contextual data model.
5. Only then implement. Completion: code changes map back to the contract sections, not to unaudited intuition.
6. Before final response, run a QA pass with `design-qa-gatekeeper` or equivalent tests. Completion: screenshots and real test output exist.

## Design Contract Required Fields
- Reference sources and local file paths.
- Color fingerprint: canvas, surfaces, text, muted text, accents, semantic colors, contrast risk.
- Spatial grammar: viewport behavior, grid columns, card rhythm, gap scale, density.
- Typography ladder: display, headings, body, captions, numeric treatment.
- Component signatures: buttons, nav, cards, charts, media, icons, decorative systems.
- Motion/tactility: hover, press, drag, transitions, reduced-motion fallback.
- Anti-copy adaptation: what changes to fit the product and avoid plagiarism.
- Hard blockers: no emoji, no fake forms, no generic templates, no device mockup unless explicitly requested.

## Pitfalls
- Do not describe a reference as "modern/minimal/premium" without measurable traits.
- Do not infer mobile/web split from a screenshot unless the user requested a simulator.
- Do not use generated placeholder imagery when the task requires authentic reference/photo evidence.
- A live URL is not evidence by itself; inspect the visual output.

## Verification
- At least one `vision_analyze` result informed the implementation.
- The delivered UI has screenshots at mobile/tablet/desktop when web-based.
- The final summary names the live route, test status, and any remaining uncertainty.
