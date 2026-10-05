---
name: typography-ux-copy
description: Use when crafting UI typography, font scales & UX copy.
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [typography, font, copy, copywriting, ux-copy, hierarchy, text, ui, ux, tipografi]
    category: creative
---

# Typography & UX Copy Intelligence

Treat typography and interface language as one information system. Typography decides what users notice, scan, understand, and act on. Copy decides what those elements mean.

Do not decorate a weak information hierarchy with larger fonts. Do not compensate for an unclear interface with more explanatory text.

## Core operating model

For every task, reason in this order:

1. Identify product context, user, task, risk, platform, viewport, and language.
2. Identify the screen's single primary purpose.
3. Build the information hierarchy before selecting exact type sizes.
4. Define semantic text roles such as display, heading, title, body, label, helper, caption, data, and code.
5. Write or revise the copy for each role.
6. Match copy length to component capacity and responsive behavior.
7. Check readability, accessibility, localization expansion, and error recovery.
8. Implement with semantic tokens instead of isolated font values.
9. Review the whole screen for scanability, consistency, tone, and unnecessary words.

When a screenshot or design reference is provided, infer the system behind it rather than copying visible values blindly. Read `references/reference-analysis.md`.

## Non-negotiable principles

- Optimize for comprehension and action before personality.
- Use hierarchy, not random size changes.
- Keep the number of typefaces small unless the concept truly requires more.
- Prefer semantic type roles over component-specific one-offs.
- Do not use placeholder text as the only field label.
- Do not use typography alone to convey critical state.
- Do not force single-line containers when localization or text scaling can expand content.
- Avoid excessively light weights for important or small text.
- Avoid all-caps body copy. Use uppercase sparingly and intentionally.
- Do not make every text element bold. Emphasis only works when contrast exists.
- Do not write generic CTAs such as "Click here" when the action can be named.
- Do not blame the user in error messages.
- Do not write long helper text to explain a confusing interaction. Improve the interaction first.
- Do not fabricate claims, urgency, scarcity, social proof, metrics, or guarantees in product copy.

## Choose the correct knowledge module

Read only the references required for the current task:

- Type fundamentals, anatomy, scale, weight, width, line-height, tracking: `references/typography-foundations.md`
- Semantic hierarchy, responsive type systems, numbers/data, dense interfaces: `references/type-hierarchy.md`
- UX writing principles, clarity, brevity, information scent, scanability: `references/ui-copywriting.md`
- Buttons, forms, helper text, errors, empty states, loading, success, permissions, dialogs, notifications: `references/component-microcopy.md`
- Hero sections, product descriptions, feature copy, pricing, offers, CTAs, benefit framing: `references/offer-value-proposition.md`
- Brand voice, tone by situation, Bahasa Indonesia, English, localization: `references/voice-tone-localization.md`
- Readability, text scaling, WCAG, inclusive language, truncation: `references/accessibility-readability.md`
- Screenshot/reference reverse engineering: `references/reference-analysis.md`
- CSS, Tailwind, variable fonts, font loading, design tokens: `references/implementation.md`
- Expert review and quality gates: `references/expert-review-checklist.md`
- Source bibliography and update notes: `references/sources.md`

## Typography decision workflow

### 1. Establish semantic roles

Start with roles, not pixel values. A useful default set is:

- display
- h1
- h2
- h3
- title
- body-lg
- body
- body-sm
- label
- helper
- caption
- numeric/data
- code/mono when required

Delete roles the product does not need. Add a role only when it represents a repeated semantic purpose.

### 2. Define hierarchy using multiple variables

Create hierarchy through a controlled combination of:

- size
- weight
- line-height
- color/contrast
- spacing
- width/measure
- font family only when justified

Do not rely on size alone.

### 3. Select a scale

Prefer a restrained scale for application UI and a more expressive scale for editorial or marketing surfaces.

Typical starting ratios, not laws:

- Dense/product UI: approximately 1.125 to 1.2
- General responsive UI: approximately 1.2 to 1.25
- Editorial/marketing: approximately 1.25 to 1.333 when the layout supports it

Use optical judgment. Round values to practical design tokens. Do not preserve mathematically pure values when they create awkward implementation.

### 4. Tune line-height by role

General tendency:

- Large display text: tighter leading
- Headings: moderately tight
- Body copy: more generous leading
- Small labels/captions: enough leading to remain legible
- Multi-line text: never compress merely to save space

Treat line-height as part of the component's vertical rhythm, not a typography-only setting.

### 5. Tune measure

Avoid extremely long body lines. For reading-heavy interfaces, constrain content width. For dashboards and forms, size text blocks according to task rather than forcing editorial measures everywhere.

### 6. Verify scaling

Test:

- narrow mobile
- standard desktop
- large text/accessibility settings
- long translations
- bold text where the platform supports it
- error states and validation text
- dynamic data and long user-generated strings

## UX copy decision workflow

Before writing, answer internally:

- What does the user want to do now?
- What do they need to know before acting?
- What uncertainty or risk might stop them?
- What is the shortest copy that removes that uncertainty?
- Does the component itself already communicate part of the message?

Then write copy using this priority:

1. Clear
2. Specific
3. Useful
4. Concise
5. Consistent
6. On-brand
7. Clever only if the first six remain intact

## Component copy rules

### Buttons and CTAs

Name the action or outcome.

Prefer:
- Save changes
- Create project
- Send invoice
- View report
- Start free trial

Avoid vague labels when context does not make them obvious:
- OK
- Submit
- Go
- Click here
- Yes

Use destructive labels that explicitly name the destructive action, such as "Delete project", when confirmation is required.

### Headings

Make the heading tell users where they are, what happened, or what they can do. Do not use decorative headings that require the paragraph below to make sense.

### Helper text

Use helper text only when it prevents a likely mistake, explains a constraint, or provides an example the user actually needs. Keep it adjacent to the relevant control.

### Error messages

State what needs attention and how to recover. Use the same terminology as the associated field or action. Preserve user input where possible.

Bad:
"Invalid input."

Better:
"Enter an email address in the format name@example.com."

Do not use humor for high-stress failures, financial loss, security, health, permissions, or destructive actions.

### Empty states

An empty state should answer, when relevant:

1. What is this area?
2. Why is it empty?
3. What can the user do next?

Do not add a CTA when there is no meaningful next action.

### Success messages

Confirm the result, not the interface action.

Prefer:
"Invoice sent to Maya."

Instead of:
"Success! Your action has been completed successfully."

### Loading and progress

If the wait is meaningful, explain what is happening in user terms. Avoid fake precision. Provide progress or an escape path when the wait can become long.

## Product descriptions, offers, and value propositions

Separate UX copy from persuasive product copy.

For a product/feature offer:

1. Identify audience and job-to-be-done.
2. Name the outcome.
3. Explain the mechanism or relevant capability.
4. Provide evidence only if evidence is supplied or verifiable.
5. Address meaningful friction or risk.
6. Use a CTA that matches the next step.

A strong value proposition usually answers:

- For whom?
- What problem or desire?
- What outcome?
- Why this product or approach?
- What should they do next?

Do not invent numbers, testimonials, "best" claims, scarcity, urgency, or guarantees.

Read `references/offer-value-proposition.md` for landing-page and monetization surfaces.

## Voice and tone

Voice is the stable personality of the product. Tone changes with the situation.

Examples:

- Onboarding: encouraging and low-pressure
- Success: concise and positive
- Validation error: calm and corrective
- Destructive action: precise and serious
- Security warning: direct, specific, non-alarmist
- Empty state: helpful, optionally warm
- Enterprise dashboard: efficient and restrained

For Bahasa Indonesia, write natural product language, not literal translations from English. Prefer familiar terms used by the target audience. Keep terminology consistent across screens.

Read `references/voice-tone-localization.md` when tone, localization, or bilingual copy matters.

## Screenshot/reference analysis

When analyzing an existing interface:

1. Identify the likely font category and whether the exact family matters.
2. Map visible text into semantic roles.
3. Estimate relative size ratios, weight contrast, line-height, tracking, and case.
4. Identify repeated copy patterns and terminology.
5. Identify how hierarchy changes across components.
6. Separate brand expression from functional typography.
7. Infer what is structural versus decorative.
8. Rebuild the system for the target product instead of copying isolated values.

Never claim an exact font, size, or weight from an image unless it is actually known. Mark estimates as estimates.

## Output modes

Choose the smallest useful output for the request.

### Quick recommendation
Provide:
- recommended type roles
- key sizes/weights/line-heights
- revised copy
- short rationale

### Full UI system
Provide:
- type families and fallbacks
- semantic type scale
- responsive behavior
- type tokens
- component copy patterns
- voice and tone rules
- accessibility rules
- examples in the product language
- implementation tokens/CSS/Tailwind if requested

### UI audit
Provide findings grouped by severity:
- Critical: blocks comprehension, action, accessibility, or error recovery
- Major: damages hierarchy, consistency, scanability, or trust
- Minor: polish and consistency issues

For each finding include:
- observed issue
- why it matters
- recommended change
- revised example when copy is involved

Do not assign arbitrary numeric design scores unless the user explicitly needs a rubric-based evaluation.

## Implementation

Prefer semantic tokens such as:

```css
--font-sans: Inter, ui-sans-serif, system-ui, sans-serif;
--text-body-size: 1rem;
--text-body-line: 1.5;
--text-label-size: 0.875rem;
--text-heading-1-size: clamp(2rem, 4vw, 3.5rem);
```

Keep content and presentation separable. Let containers grow where copy may expand. Avoid fixed heights for text-heavy components.

Use `scripts/type_scale.py` when a calculated type scale or token starter is helpful. Treat generated values as candidates that still require visual review.

## Expert review standard

Before finalizing a design or recommendation, verify:

- The primary task is understandable from a quick scan.
- Heading levels reflect information hierarchy.
- Body copy is readable at the intended viewport.
- Font choices support all required characters and languages.
- Important text does not rely on thin weights.
- Copy matches component purpose.
- Buttons name actions clearly.
- Errors tell users how to recover.
- Empty states provide an appropriate next step.
- Labels remain visible after input.
- Dynamic and localized strings have room to expand.
- Text resizing does not clip or overlap content.
- Brand voice does not reduce clarity.
- Marketing copy does not fabricate evidence or manipulate users.
- Terminology is consistent across the flow.

For a deeper review, read `references/expert-review-checklist.md`.
