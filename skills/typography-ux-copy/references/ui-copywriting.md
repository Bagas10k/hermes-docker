# UX Writing and Interface Copy

## Contents
1. Content design mindset
2. Clarity hierarchy
3. Scan behavior
4. Information scent
5. Sentence construction
6. Questions and forms
7. Navigation and labels
8. AI-generated copy guardrails

## 1. Content design mindset

Treat words as interface elements with constraints, states, and behavior.

Write from the user's task, not the organization's internal structure.

Before adding copy, ask whether the UI can be made self-explanatory through better structure, labels, defaults, or interaction design.

## 2. Clarity hierarchy

Prioritize:
1. Meaning
2. Action
3. Consequence
4. Supporting explanation
5. Brand expression

The interface should still work if users skim only headings, labels, and buttons.

## 3. Scan behavior

Users often scan transactional interfaces instead of reading every sentence.

Support scanning by:
- putting important words early
- using short headings
- splitting unrelated ideas
- using bullets for comparable items
- avoiding paragraph walls
- reducing repeated words already visible in the UI

## 4. Information scent

A label should predict what happens next.

Good labels reduce uncertainty:
- Billing details
- Download CSV
- Invite teammate
- Review order
- Change password

Weak labels hide intent:
- More
- Learn
- Proceed
- Go

Generic labels can still work when surrounding context makes the destination unmistakable, but do not use them by default.

## 5. Sentence construction

Prefer:
- active voice
- concrete verbs
- familiar words
- one main idea per sentence
- user terminology
- consistent nouns for the same object

Avoid:
- internal system jargon
- unnecessary nominalizations
- repeated politeness filler
- unexplained acronyms
- vague time claims
- passive constructions that hide responsibility

## 6. Questions and forms

Ask only for information needed at that moment.

Question design:
- ask in language users understand
- give context before sensitive or unusual requests
- explain why information is needed when trust could be affected
- provide examples as hint text when format is non-obvious
- do not put critical instructions only in placeholders

## 7. Navigation and labels

Navigation labels should be:
- distinct
- predictable
- parallel in grammar when possible
- based on user mental models

Avoid using several terms for one object across a product. If the product calls something a "workspace", do not randomly switch to "team space", "project area", and "hub" without a real distinction.

## 8. AI-generated copy guardrails

AI often over-writes. Correct these patterns:

### Pattern: explaining the obvious
UI: "Search"
Bad helper: "Use this search box to search for items."
Action: remove the helper unless a special search scope needs explanation.

### Pattern: generic enthusiasm
Bad: "Awesome! You successfully completed the process!"
Better: "Profile updated."

### Pattern: filler adjectives
Bad: "Powerful, seamless, innovative analytics."
Better: name the concrete capability and outcome.

### Pattern: fabricated proof
Never invent customer counts, ratings, benchmarks, testimonials, certifications, performance improvements, or time savings.

### Pattern: explaining every feature
Use progressive disclosure. Keep the primary screen focused and reveal detail only when needed.
