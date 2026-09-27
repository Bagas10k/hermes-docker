---
name: ui-layout-intelligence
description: Teach an AI agent to reason about UI/UX spatial layout and spacing systems, including margin, padding, gap, grids, containers, alignment, whitespace, density, responsive behavior, touch targets, visual rhythm, and reference-based spacing adaptation. Use when creating, reviewing, redesigning, or implementing interfaces from prompts, screenshots, mockups, design references, CSS, Tailwind, design tokens, dashboards, mobile apps, websites, HMI panels, or component systems where layout quality and spacing consistency matter.
---

# UI Layout Intelligence

Build spatial systems instead of choosing isolated pixel values. Treat spacing as a relationship between elements, hierarchy, interaction, content, and form factor.

## Core mental model

Always reason at four spatial levels:

1. **Page level** — viewport, safe areas, page margins, max-width, columns, panes.
2. **Section level** — separation between major content groups and hierarchy zones.
3. **Component level** — card padding, field spacing, button padding, list gaps.
4. **Micro level** — icon-label gaps, badge padding, inline controls, optical corrections.

Never apply one spacing value to all four levels.

Distinguish the three primary spacing roles:

- **Padding** = space inside a container between its boundary and content.
- **Gap** = space between sibling elements controlled by their parent layout.
- **Margin** = external separation between an element and surrounding layout.

Prefer parent-controlled `gap` for sibling relationships. Use padding for container breathing room. Use margin when the relationship genuinely belongs to the child/external flow or when required by the implementation context.

## Workflow

### 1. Establish context

Infer or identify:

- platform: web, mobile, desktop, tablet, HMI, kiosk, TV, spatial UI;
- input: touch, pointer, keyboard, eyes/remote, industrial controls;
- content density: compact, standard, comfortable, immersive;
- user task: scan, monitor, read, compare, configure, transact, create;
- visual character: editorial, enterprise, playful, technical, premium, utilitarian;
- responsive range and localization needs.

Do not choose spacing before understanding the task.

### 2. Analyze reference material when present

When a screenshot or design reference exists, inspect relationships rather than copying coordinates blindly.

Extract:

- outer page margin;
- container width;
- column count and gutters;
- repeated horizontal and vertical intervals;
- card padding;
- icon-label distance;
- section-to-section distance;
- component density;
- alignment anchors;
- edge behavior and safe areas;
- repeated ratios such as micro < component < section < page.

Then reconstruct a coherent spacing system. See `references/reference-analysis.md`.

### 3. Choose a spacing scale

Use a small token system instead of arbitrary values.

Default web/product starting point:

- micro base: 4px
- primary rhythm: 8px
- common tokens: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96

Do not treat this as a law. Adapt to platform, typography, target size, density, and reference style.

Use 4-unit increments for micro adjustments and 8-unit rhythm for most component/layout decisions. Permit documented optical exceptions where geometry and perceived spacing differ.

See `references/spacing-foundations.md`.

### 4. Assign semantic spacing tokens

Prefer role-based tokens over raw numbers when building reusable systems.

Example:

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;

--layout-page-inline: var(--space-6);
--layout-section-gap: var(--space-12);
--component-card-padding: var(--space-6);
--component-control-gap: var(--space-3);
--component-icon-label-gap: var(--space-2);
```

Semantic aliases may change by breakpoint or density mode while the primitive scale stays stable.

### 5. Build hierarchy through distance

Use spatial distance as a grouping signal:

- elements with strong semantic connection should generally be closer;
- unrelated groups should have visibly larger separation;
- section spacing should normally exceed internal component spacing;
- card-to-card gap should not accidentally look like card internal padding;
- labels should visually belong to their controls;
- headings should usually feel more connected to their following content than to the preceding section.

Apply proximity before adding borders, boxes, or background colors just to create grouping.

### 6. Apply alignment and grid logic

Avoid "almost aligned" layouts.

Prefer shared anchors for:

- headings;
- body text;
- cards;
- field labels;
- primary controls;
- table columns;
- repeated icon positions.

Use grids as constraints, not decoration. Choose columns, gutters, and page margins based on usable content width and breakpoint. See `references/grid-rhythm.md`.

### 7. Handle density intentionally

Support three conceptual modes when appropriate:

- **Compact** — data-heavy desktop tools, monitoring, expert workflows.
- **Standard** — default productivity and general-purpose UI.
- **Comfortable** — touch-heavy, consumer, learning, or relaxed interfaces.

Do not shrink interactive hit regions merely to achieve compact visuals. Visual size and hit area may differ.

See `references/responsive-density.md`.

### 8. Verify interaction spacing and accessibility

For web pointer targets, account for WCAG target-size requirements. Do not rely only on visible icon dimensions.

Check:

- hit area;
- distance to adjacent targets;
- keyboard focus visibility and clipping;
- zoom/reflow behavior;
- touch comfort;
- safe areas;
- RTL logical spacing;
- text growth/localization.

See `references/accessibility-quality.md`.

### 9. Implement using system primitives

For CSS, prefer:

- `gap` in flex/grid for sibling separation;
- logical properties such as `padding-inline`, `margin-block`;
- `min()`, `max()`, `clamp()` when fluid spacing is justified;
- reusable custom properties/tokens;
- container/grid rules over manual positional offsets.

For Tailwind, map the design's spacing tokens deliberately instead of sprinkling unrelated arbitrary values throughout the UI.

See `references/implementation.md`.

## Spacing decision rules

Use these rules before inventing a number:

1. Ask which relationship owns the space.
2. Reuse an existing token when the relationship is equivalent.
3. Increase distance when hierarchy or grouping needs stronger separation.
4. Reduce distance when two elements must be perceived as one unit.
5. Preserve tap/click comfort even in compact layouts.
6. Prefer consistent repeated relationships over perfect local symmetry.
7. Use optical correction only after structural spacing is correct.
8. Document exceptions instead of silently creating magic numbers.

## Optical spacing

Mathematical equality does not always look equal.

Account for:

- icons with uneven internal whitespace;
- round shapes beside rectangular shapes;
- uppercase vs lowercase visual mass;
- large display type;
- chevrons/arrows with directional visual weight;
- badges and pills;
- asymmetric illustrations.

Use the token scale as the baseline, then make the smallest justified optical correction. Do not use optical adjustment to hide a broken layout hierarchy.

## Anti-patterns

Avoid:

- random values such as 13px, 17px, 27px without a reason;
- adding margin independently to every child;
- stacking parent gap + child margins accidentally;
- equal spacing between elements that belong to different hierarchy levels;
- using whitespace only decoratively while ignoring grouping;
- centering everything by default;
- forcing desktop density onto touch interfaces;
- shrinking hit targets because the icon looks small;
- copying screenshot coordinates without reconstructing the underlying system;
- using excessive cards/borders because spacing hierarchy is weak;
- fixed widths that break localization or responsive reflow.

## Reference reconstruction principle

Do not conclude:

> "The reference uses 24px, therefore use 24px."

Conclude instead:

> "The reference appears to use a 4/8-unit rhythm, 24px component padding, 8px micro gaps, 32px group separation, and about 64px section separation; preserve those relationships while adapting them to the target viewport and content density."

## Expected output

When asked to design or correct layout, provide as relevant:

1. detected or proposed spacing system;
2. page/container/grid rules;
3. component spacing rules;
4. semantic spacing tokens;
5. density/responsive adaptations;
6. accessibility concerns;
7. implementation in CSS, Tailwind, design tokens, or framework requested;
8. explanation of any deliberate exceptions.

Prefer concise actionable output over a generic lecture.

## Resources

Load only what is needed:

- `references/spacing-foundations.md` — spacing scales, margin/padding/gap, proximity, whitespace.
- `references/grid-rhythm.md` — grids, alignment, containers, vertical rhythm and hierarchy.
- `references/component-spacing.md` — cards, forms, buttons, navigation, lists, tables, dialogs.
- `references/responsive-density.md` — breakpoints, density modes, touch vs desktop, fluid spacing.
- `references/reference-analysis.md` — extracting a spacing system from screenshots and references.
- `references/accessibility-quality.md` — target size, RTL, zoom, localization, QA checklist.
- `references/implementation.md` — CSS, Tailwind, tokens, React-oriented implementation patterns.
- `references/sources.md` — authoritative reference links and notes.
- `scripts/spacing_audit.py` — inspect values against a base spacing system and suggest nearest tokens.
