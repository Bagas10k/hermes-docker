# Type Hierarchy and Responsive Systems

## Contents
1. Semantic roles
2. Hierarchy contrast
3. Responsive type
4. Dense products and dashboards
5. Tables and numbers
6. Forms
7. Marketing surfaces

## 1. Semantic roles

Design tokens should describe purpose, not component name.

Prefer:
- text.display
- text.heading.1
- text.heading.2
- text.body
- text.label
- text.helper
- text.caption
- text.numeric

Avoid creating `dashboard-card-title-17px` unless the role is genuinely unique.

## 2. Hierarchy contrast

A hierarchy can be created by combining:
- size
- weight
- position
- whitespace
- color contrast
- line length
- case

Use at least one clear distinction between adjacent levels. Avoid stacking every form of emphasis on the same element.

Information priority should survive if color is removed.

## 3. Responsive type

Responsive typography is not simply smaller desktop text.

On smaller screens:
- reduce display scale more aggressively than body text
- preserve readable body text
- allow headings to wrap naturally
- avoid forced one-line marketing headlines
- prioritize content over decorative typography

Use CSS `clamp()` when continuous scaling is helpful. Example:

```css
font-size: clamp(2rem, 1.2rem + 3vw, 4rem);
```

Do not use fluid scaling for every small UI label. Stable values are often more predictable for controls.

## 4. Dense products and dashboards

Dense products need information efficiency without visual compression.

Use:
- restrained type scale
- strong alignment
- clear label/value differentiation
- tabular numerals where data comparison matters
- consistent row heights
- deliberate secondary text contrast

Do not shrink body text to compensate for poor information architecture.

For operational or HMI-like interfaces, prioritize fast recognition and status clarity over brand expression.

## 5. Tables and numbers

For data-heavy UI:
- consider tabular numerals for columns
- align decimals or numeric units consistently
- separate value from unit when it improves scanning
- use monospace only when equal character width has a functional purpose
- prevent tiny superscripts or footnotes from carrying critical meaning

Large KPI numbers should still have clear labels, timeframe/context, and units.

## 6. Forms

Form hierarchy should make this sequence obvious:
1. question/label
2. required context or hint
3. input/control
4. error if present

Keep labels persistent. A placeholder can provide an example but should not be the only identifier for the field.

If a page asks one important question, the question can often serve as the main heading when implemented accessibly.

## 7. Marketing surfaces

Marketing typography may be more expressive, but preserve:
- clear value proposition
- readable subhead
- obvious CTA
- scannable proof/features
- mobile wrapping

Do not increase display size until the message itself is clear.
