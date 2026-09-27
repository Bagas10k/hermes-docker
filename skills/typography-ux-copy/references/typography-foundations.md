# Typography Foundations

## Contents
1. Typography as interface architecture
2. Typeface selection
3. Size and scale
4. Weight and emphasis
5. Line-height
6. Tracking and letter spacing
7. Width and measure
8. Variable fonts
9. Common failure modes

## 1. Typography as interface architecture

Typography is not a decoration layer. It organizes information, creates scan paths, establishes priority, and communicates product character.

A useful typography system should answer:
- What should be noticed first?
- Which text is actionable?
- Which text is supporting detail?
- Which text repeats often?
- Which text can become long or dynamic?
- Which text must remain legible under stress or at a distance?

Prefer semantic roles. A visual role should be reusable across components when its meaning is the same.

## 2. Typeface selection

Evaluate a typeface by:
- legibility at small sizes
- distinguishable character forms
- available weights
- language and glyph coverage
- numeral quality
- punctuation and symbols
- UI hinting/rendering quality
- variable font support when useful
- loading cost on web
- licensing and deployment constraints
- brand fit

System fonts are often excellent for application interfaces because they are optimized for platform rendering and accessibility. Custom fonts can add identity, especially for display and headings, but should not compromise body legibility.

Avoid using several families merely to create hierarchy. Size, weight, spacing, and color usually provide enough hierarchy.

## 3. Size and scale

Do not begin with a fashionable scale. Begin with semantic needs.

A practical UI may need only 6-9 roles. A marketing site may need a larger display range.

Scale ratios are starting points:
- 1.125-1.2 for dense application UI
- 1.2-1.25 for balanced product UI
- 1.25-1.333 for more expressive editorial or marketing layouts

Round to implementable values and inspect optically.

Example product scale:
- caption: 12
- helper/label: 13-14
- body: 16
- body-lg/title-sm: 18
- title: 20-24
- section heading: 28-32
- page heading: 36-48 depending on context

These are examples, not mandatory values.

## 4. Weight and emphasis

Weight is a hierarchy tool, not a substitute for structure.

General approach:
- body: Regular or equivalent
- labels and important UI: Regular to Medium
- headings: Medium to Bold depending on family
- data emphasis: Medium/Semibold when needed

Avoid very light weights for small or critical UI text. Apple HIG currently recommends avoiding Ultralight, Thin, and Light system weights for legibility, especially at small sizes.

Do not bold entire paragraphs. The eye needs contrast between normal and emphasized content.

## 5. Line-height

Line-height depends on font, width, role, and number of lines.

Tendencies:
- display text: around 1.0-1.15
- headings: around 1.1-1.3
- UI body: around 1.4-1.6
- long reading text: often 1.5-1.7

Do not copy these values blindly. Fonts with large x-height, unusual ascenders/descenders, or script-specific forms may require different leading.

For three or more lines, avoid cramped leading.

## 6. Tracking and letter spacing

Use tracking carefully:
- Large display type may benefit from slight negative tracking depending on font.
- Small caps or uppercase labels may need added tracking.
- Body copy usually performs best near the font's intended default tracking.
- Do not use aggressive negative tracking on small text.

Variable system fonts may adjust tracking optically at different sizes. Respect native behavior when available.

## 7. Width and measure

Long lines reduce scanning comfort for reading-heavy content. Narrow lines can create excessive wrapping.

Use content purpose to determine measure:
- Documentation/article body: constrain line length.
- Forms: align text with input widths and task flow.
- Dashboards: prioritize quick scanning over editorial rhythm.
- Tables: keep labels compact, but never at the cost of ambiguity.

Do not use a single max-width rule for every text role.

## 8. Variable fonts

Variable fonts can expose axes such as:
- weight (wght)
- width (wdth)
- optical size (opsz)
- slant/italic

Use them when they improve quality or reduce font files. Do not animate typography axes gratuitously in productivity UI.

Optical size can improve type rendering across sizes when supported. Do not fake optical sizing by arbitrary tracking alone.

## 9. Common failure modes

- Too many type sizes with no semantic meaning
- H1 and H2 too similar to scan quickly
- Body text too small to fit more content
- Excessive bold text
- Thin gray text on low-contrast surfaces
- Fixed-height cards that clip longer copy
- Giant marketing headings on mobile
- Decorative fonts used in dense controls
- Using monospaced fonts for ordinary labels because it looks "technical"
- Center-aligning long paragraphs
- Using uppercase for long strings
- Font pairing based only on visual novelty
