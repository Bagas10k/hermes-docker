# Grid, Alignment, and Rhythm

## 1. Alignment creates invisible structure

Repeated elements should share anchors. Common anchors include:

- leading edge of page content;
- heading and body copy;
- cards in a row;
- labels and inputs;
- icon columns;
- numeric columns in tables;
- primary action edge.

A layout with inconsistent anchors often feels less polished even when each component is attractive.

## 2. Page containers

Choose a container model intentionally:

- **full bleed** for immersive/media surfaces;
- **centered max-width** for reading and conventional product pages;
- **fixed sidebar + fluid content** for tools;
- **multi-pane** for master-detail or monitoring;
- **fluid grid** for dashboards and responsive galleries.

Page margin should adapt to viewport size. Mobile may use a modest fixed inset; larger screens can increase margins or cap content width.

## 3. Columns and gutters

Use columns to align unrelated components into a coherent composition. Gutters are relationships between columns; do not confuse them with card padding.

Prefer fewer, meaningful column behaviors over overly complex grids.

## 4. Vertical rhythm

Vertical rhythm is the repeated pacing of content down the page. Build it from:

- typography line height;
- heading-to-content spacing;
- paragraph spacing;
- group spacing;
- section spacing.

Avoid making every vertical interval identical. Rhythm depends on hierarchy, not repetition alone.

## 5. Heading relationships

A heading normally belongs more strongly to the content that follows than to the preceding block. Therefore the space above a heading can often be greater than the space below it.

## 6. Alignment vs centering

Centering is not a universal default. Left/leading alignment is often easier to scan for text-heavy, forms, dashboards, and enterprise tools. Center alignment is useful for short focal content, empty states, hero sections, and deliberate compositions.

## 7. Dense dashboards

For monitoring and dashboards:

- align repeated metrics to common baselines;
- preserve consistent card padding;
- make inter-card gaps smaller than section separation;
- avoid decorative whitespace that pushes critical information below the fold;
- retain enough separation to distinguish control groups and status clusters.
