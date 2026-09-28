---
name: color-intelligence
description: Advanced color reasoning and customization for visual design. Use when Hermes must analyze, choose, adapt, repair, or implement colors for UI/UX, websites, apps, dashboards, posters, HMI/SCADA, branding, data visualization, illustrations, screenshots, reference images, light/dark themes, design systems, CSS, Tailwind, or design tokens. Trigger on requests about palette, theme, vibe, recoloring, contrast, accessibility, color hierarchy, semantic states, gradients, neutral scales, brand color, reference matching, or making an existing design feel more premium, calm, playful, technical, elegant, industrial, modern, or readable.
---

# Color Intelligence

Treat color as a functional system, not decoration. Derive color decisions from context, hierarchy, perception, semantics, accessibility, and implementation constraints.

## Core operating model

For every color task, reason in this order:

1. **Context** — identify medium, audience, environment, brand personality, emotional target, density, and usage conditions.
2. **Reference intent** — if a screenshot/image/reference exists, identify its color relationships and role structure before copying any literal values.
3. **Functional roles** — assign background, surface, text, border, primary, secondary, accent, focus, success, warning, danger, info, disabled, chart, and overlay roles as applicable.
4. **Hierarchy** — make importance visible through lightness, chroma, area, contrast, and frequency. Do not use hue alone to create hierarchy.
5. **Accessibility** — verify readable text and distinguishable interactive/state colors. Never rely on color as the only signal for critical meaning.
6. **Consistency** — build a scale/token system instead of isolated hex values whenever the output will be reused.
7. **Implementation** — map the palette to the user's target format: HEX/RGB/HSL/OKLCH, CSS variables, Tailwind theme, JSON tokens, or prose specification.
8. **Validation** — look for muddy neutrals, excessive saturation, accidental competition, weak contrast, state ambiguity, dark-mode glare, and reference mismatch.

## Decision rules

- Prefer **relationships over literal copying**. Preserve the reference's lightness structure, temperature, saturation rhythm, and accent proportion before matching exact hues.
- Prefer **perceptual lightness control** for systematic palettes. Use OKLCH when the target stack supports it; otherwise provide practical sRGB/HEX fallbacks.
- Use saturation/chroma sparingly. Large surfaces usually need lower chroma than small accents.
- Use neutrals to carry most layout structure. Reserve stronger color for identity, action, selection, status, and emphasis.
- Do not make every semantic state equally vivid. Danger and blocking states may need more visual urgency than informational states.
- Do not assume “premium = black and gold”, “feminine = pink”, “technology = blue”, or similar clichés. Infer tone from context and references.
- In industrial/HMI contexts, prioritize normal-state calmness and reserve strong color for abnormal/attention states.
- In data visualization, prioritize distinguishability and ordered meaning over decorative harmony.
- In dark mode, redesign surfaces and luminance relationships; do not merely invert the light theme.
- If the user gives only adjectives such as “premium”, “soft”, “futuristic”, or “cute”, translate them into measurable color behavior using `references/mood-brand-context.md`.

## Workflow by task

### A. Create a palette from scratch
1. Read `references/foundations.md` for harmony/perception principles when needed.
2. Read `references/mood-brand-context.md` to convert desired vibe into hue, temperature, lightness, chroma, and contrast behavior.
3. Define neutral, brand, accent, and semantic families.
4. Build usable steps (for example 50–950 or role-based tokens), not a handful of unrelated colors.
5. Read `references/accessibility-quality.md` and validate critical foreground/background pairs.
6. Read `references/implementation.md` if code/tokens are requested.

### B. Recolor or improve an existing design
1. Audit what is wrong before changing colors: hierarchy, temperature, excess saturation, weak contrast, inconsistent states, or brand mismatch.
2. Preserve colors that already perform a clear role unless a change solves a defined problem.
3. Repair relationships first: background↔surface, surface↔border, text↔surface, action↔surroundings, status↔normal state.
4. Change the fewest high-leverage tokens needed to shift the overall feel.
5. Validate both isolated components and the whole composition.

### C. Adapt colors from a screenshot/reference
Read `references/reference-adaptation.md`.

Do not just extract dominant colors. Identify:
- dominant neutral family;
- perceived background/surface ladder;
- primary/accent family;
- warm/cool bias;
- chroma ceiling;
- text contrast behavior;
- border/elevation behavior;
- accent area ratio;
- state colors;
- gradients or translucency;
- which characteristics are essential to the vibe versus incidental to the source.

Then rebuild these relationships for the target content and platform.

### D. Build light/dark themes or a design system
Read `references/ui-color-systems.md` and `references/implementation.md`.

Create semantic tokens first, such as:
- `bg.canvas`
- `bg.surface`
- `bg.elevated`
- `text.primary`
- `text.secondary`
- `border.default`
- `action.primary`
- `action.primary.hover`
- `focus.ring`
- `status.success`
- `status.warning`
- `status.danger`

Keep component code bound to semantic tokens rather than raw palette steps.

### E. Check contrast or numeric color relationships
Use `scripts/color_tools.py` for deterministic WCAG contrast checks when HEX values are available. Do not estimate contrast ratios by eye.

Example:
```bash
python scripts/color_tools.py contrast '#111827' '#ffffff'
```

## Output contract

Adapt detail to the request. For a full color-design answer, default to:

1. **Color direction** — one short paragraph describing the visual logic.
2. **Palette/tokens** — role, value, and purpose.
3. **Usage rules** — where each family should and should not appear.
4. **States** — hover, active, focus, selected, disabled, and semantic feedback if relevant.
5. **Accessibility notes** — critical contrast or non-color cues.
6. **Implementation** — code/tokens only when requested or clearly useful.
7. **Validation notes** — likely failure modes to check in the final composition.

When the user asks for a direct build, spend less prose on theory and provide the actual palette/tokens/code.

## Knowledge map

Load only what the current task needs:

- `references/foundations.md` — color perception, models, harmony, contrast, temperature, saturation, lightness, proportion, and mixing logic.
- `references/mood-brand-context.md` — converting style words, brand personality, medium, and audience into color behavior.
- `references/ui-color-systems.md` — neutrals, semantic roles, interaction states, light/dark mode, dashboards, HMI, charts, and gradients.
- `references/reference-adaptation.md` — how to learn from screenshots/images without blindly copying them.
- `references/accessibility-quality.md` — WCAG contrast, use-of-color rules, color-vision concerns, and quality audit checklist.
- `references/implementation.md` — HEX/RGB/HSL/OKLCH, CSS variables, Tailwind, JSON tokens, naming, and handoff patterns.
- `references/sources.md` — authoritative W3C/MDN references for standards or compatibility checks.

## Anti-patterns

Avoid:
- random palette generators as the primary reasoning method;
- choosing colors only by personal preference;
- using more accent colors to fix weak hierarchy;
- pure black/pure white everywhere by default;
- gray text that becomes unreadable for the sake of subtlety;
- red/green-only distinction for important states;
- identical lightness for multiple categorical chart colors;
- uncontrolled neon colors on large surfaces;
- gradients that reduce text readability;
- creating separate arbitrary HEX values for every component;
- copying a reference palette without adapting it to new content density, platform, or accessibility needs.

## Final self-check

Before finishing, ask internally:
- Does every important color have a role?
- Is attention concentrated in the right place?
- Could the design still be understood in grayscale?
- Are normal and abnormal states distinguishable without hue alone?
- Are text and controls readable?
- Does the palette still match the requested vibe after accessibility corrections?
- Are token relationships reusable and coherent?

---

## Harmonic Palette Calibration & Script Helper

Untuk menghasilkan palet triadik atau komplementer yang terkalibrasi secara matematis dengan WCAG AA/AAA:
```bash
python3 ~/.hermes/skills/color-intelligence/scripts/palette_calibrator.py "#F59E0B" triadic light
```

### Fondasi Teruji Light Mode vs Dark Mode:
- **Light Mode (Warm Paper):** Canvas `#EFECE6` atau `#FAF8F5`, Card `#FFFFFF` (1px `#E2E8F0` border), Heading Text `#0F172A` (WCAG AAA 17.8:1), Body Text `#334155`.
- **Dark Mode (Obsidian Noir):** Canvas `#0B0A10` atau `#0F172A`, Card `#15131D`, Aksen Tajam: Crimson `#EF4444`, Amber `#F59E0B`, Safety Orange `#FF5C00`.
