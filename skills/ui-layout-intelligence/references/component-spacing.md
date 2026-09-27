# Component Spacing Patterns

## Buttons

Separate visible size from hit region. Button padding depends on typography, hierarchy, platform, and density.

Check:

- label is vertically centered optically, not only mathematically;
- icon-label gap is consistent across button variants;
- adjacent actions are distinguishable;
- destructive and primary actions do not appear accidentally grouped.

## Inputs and forms

Relationships normally follow:

`label -> control < field -> field < group -> group`

Keep validation/help text visually attached to the relevant field. Do not let generic stack spacing separate an error message from its input more than the next field.

## Cards

Distinguish:

- card padding;
- internal group gap;
- card-to-card gap;
- section-to-card gap.

If all four are equal, hierarchy often becomes ambiguous.

## Lists

Use row height and internal padding based on scan density and interaction. Repeated list rows should share stable vertical rhythm and alignment.

## Navigation

Navigation spacing must communicate grouping and target affordance. Avoid tiny icon targets with large decorative empty areas that do not belong to the actual clickable region.

## Tables

Tables favor compact, repeatable spacing. Use:

- consistent cell padding;
- aligned numbers;
- sufficient row differentiation;
- clear separation between headers, grouped rows, and totals.

Do not apply spacious card rules to dense tabular data.

## Dialogs and sheets

Preserve zones:

- header;
- body;
- footer/actions.

Spacing between zones should be stronger than internal text spacing. Ensure action rows remain usable at narrow widths and with longer localized labels.

## Empty states

Empty states can be more spacious than surrounding data views, but should still align to the system's page/container rules.

## HMI and operational interfaces

For HMI/monitoring contexts:

- prioritize rapid scanning and stable placement;
- use spacing to separate process groups and control zones;
- keep critical status/alarm relationships visually unambiguous;
- avoid luxury whitespace that reduces simultaneous process visibility;
- protect touch/control targets from accidental activation.
