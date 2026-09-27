# Reference-Based Layout Analysis

Use this process when given a screenshot, mockup, competitor UI, or design inspiration.

## Step 1: Find major frames

Identify:

- viewport edge;
- page container;
- top bar/sidebar;
- major panes;
- primary content columns;
- cards and nested groups.

## Step 2: Estimate repeated distances

Collect recurring distances such as:

- 7-9 px -> likely 8-unit micro gap;
- 14-18 px -> likely 16-unit component spacing;
- 22-26 px -> likely 24-unit padding;
- 30-34 px -> likely 32-unit group spacing.

Do not treat screenshot rasterization as exact source values.

## Step 3: Infer the base rhythm

Look for clusters and common divisors. A design with values near 8, 16, 24, 32 probably uses an 8-unit rhythm. A system with many 4, 12, 20, 28 values may be using a 4-unit scale or mixed 4/8 rhythm.

Use `scripts/spacing_audit.py` when numeric measurements are available.

## Step 4: Infer hierarchy

Map each interval to a role:

- micro relationship;
- internal component;
- group;
- section;
- page.

The role is more important than the exact pixel value.

## Step 5: Rebuild for the target

Adapt the system to:

- target viewport;
- content amount;
- target platform;
- touch/pointer input;
- typography;
- localization;
- desired density.

Do not blindly copy dimensions from a different device or product.

## Step 6: Compare perceptually

Ask:

- Does the same information feel grouped?
- Does the same hierarchy survive?
- Are the same alignment anchors preserved?
- Is the target UI too cramped or too loose compared with the reference?
- Did component spacing accidentally become page spacing?

## Useful output format

```text
Detected rhythm: 4px micro / 8px primary
Page margin: ~24px mobile, expands on desktop
Card padding: ~24px
Micro gap: 8px
Control gap: 12-16px
Group gap: 24-32px
Section gap: 48-64px
Density: standard/compact
Adaptation notes: ...
```
