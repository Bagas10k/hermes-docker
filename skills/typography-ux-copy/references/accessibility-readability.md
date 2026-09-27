# Accessibility and Readability

## Contents
1. Text scaling
2. Text spacing
3. Contrast and weight
4. Reflow and truncation
5. Labels and assistive technology
6. Cognitive accessibility
7. Large text and responsive behavior

## 1. Text scaling

Interfaces must remain usable when users enlarge text. On platforms with Dynamic Type or similar features, adopt platform mechanisms when possible.

Apple's current HIG emphasizes supporting Dynamic Type and testing layouts across larger accessibility text sizes. The web should also tolerate browser zoom and text resizing without clipping or overlap.

Do not solve overflow by disabling zoom or truncating essential information.

## 2. Text spacing

WCAG 2.2 Success Criterion 1.4.12 requires that content and functionality are not lost when users override text spacing to at least:
- line height: 1.5 times font size
- paragraph spacing: 2 times font size
- letter spacing: 0.12 times font size
- word spacing: 0.16 times font size

Important: WCAG does not require authors to use those exact values by default. The interface must tolerate the override.

Therefore:
- avoid fixed-height text containers
- allow wrapping
- prevent overlap with adjacent controls
- test nav bars and chips where expansion pressure is high

## 3. Contrast and weight

Small, thin text is harder to perceive even when numerical contrast appears acceptable. Use adequate weight and size.

Use the color/accessibility system appropriate to the product, but remember typography and contrast interact.

Do not encode disabled text by making it nearly invisible. Disabled states should remain understandable while visually secondary.

## 4. Reflow and truncation

Truncation is acceptable for secondary or recoverable content when the full value can be accessed. Avoid truncating:
- primary actions
- critical warnings
- legal/commercial commitments
- error recovery instructions
- essential labels

If dynamic content can be long, design expansion behavior before implementation.

## 5. Labels and assistive technology

Visible labels are generally preferable for form controls. Ensure programmatic names and descriptions match or support visible text.

Do not rely on placeholder text as the only label. Placeholder text disappears during entry and may create memory burden.

Error text should be programmatically associated with the relevant input when implementing accessible forms.

## 6. Cognitive accessibility

Reduce cognitive load by:
- using familiar words
- keeping terminology consistent
- splitting complex tasks
- placing instructions near the relevant action
- explaining uncommon constraints before failure when possible
- avoiding unnecessary time pressure

## 7. Large text and responsive behavior

When type grows:
- allow cards and rows to become taller
- allow controls to stack
- preserve reading order
- avoid overlapping badges/icons
- prioritize meaningful content

A design is not responsive if only the viewport changes while the content model remains rigid.
