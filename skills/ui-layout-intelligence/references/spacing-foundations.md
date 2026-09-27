# Spacing Foundations

## 1. Space is relational

A spacing value is meaningful only because of what it separates. Classify every distance as one of:

- page edge -> content;
- section -> section;
- group -> group;
- component boundary -> internal content;
- sibling -> sibling;
- icon -> label;
- text line -> text line;
- control -> control.

Do not evaluate spacing as an isolated number.

## 2. Margin, padding, and gap

### Padding
Use padding when the container owns the breathing room around its contents. Typical examples:

- card interior;
- button label to button edge;
- input content inset;
- panel content to panel edge;
- navigation bar content inset.

### Gap
Use gap when a parent owns spacing between siblings. Typical examples:

- rows in a stack;
- icon and label;
- cards in a grid;
- buttons in an action group;
- columns.

Gap is often preferable to independent child margins because the relationship remains explicit and predictable.

### Margin
Use margin when external flow/separation belongs to an element or when implementation constraints call for it. Be alert to margin collapsing and accidental double-spacing.

## 3. Base scale

A useful general-purpose product scale:

| Token | Value | Common role |
|---|---:|---|
| 0 | 0 | no separation |
| 1 | 4px | tiny optical/micro gap |
| 2 | 8px | icon-label, compact micro gap |
| 3 | 12px | compact component gap |
| 4 | 16px | default control/component interval |
| 5 | 20px | intermediate padding |
| 6 | 24px | card/panel padding, page margin mobile |
| 8 | 32px | group separation |
| 10 | 40px | large group separation |
| 12 | 48px | section spacing |
| 16 | 64px | strong section separation |
| 20 | 80px | landing/editorial section separation |
| 24 | 96px | large desktop composition spacing |

Use 4px as a micro increment and 8px as the dominant rhythm, but adapt rather than enforce mechanically.

Material Design 3 uses an 8dp baseline spacing scale and distinguishes padding, gaps, and margins. The skill may borrow the principle without forcing every product to look like Material Design.

## 4. Proximity and grouping

A strong hierarchy often follows:

`micro gap < component internal gap < group gap < section gap < page-scale separation`

Example:

- icon -> text: 8px
- label -> field: 8px
- field -> field: 16px
- form group -> form group: 24-32px
- section -> section: 48-64px

The exact values may vary, but their ordering should remain legible.

## 5. Whitespace

Whitespace is functional. It can:

- separate concepts;
- indicate hierarchy;
- improve scanning;
- reduce accidental interaction;
- create emphasis;
- establish brand character and perceived density.

Avoid equating more whitespace with better design. Data-heavy tools may need tighter spacing than editorial or premium interfaces.

## 6. Density

Think in terms of relationship preservation rather than scaling every number uniformly.

Compact mode may reduce:

- row height;
- panel padding;
- group gaps;

But preserve:

- readable text;
- focus treatment;
- target separation;
- critical section hierarchy.

## 7. Optical correction

Allow small exceptions when perceived geometry requires it. Examples:

- a chevron may need less apparent gap than its bounding box suggests;
- a circular icon can look farther away than a square icon at the same measured distance;
- display headings may need custom vertical spacing due to font metrics.

Start from a token, then adjust minimally and record why.
