# Component Microcopy

## Contents
1. Buttons
2. Links
3. Forms and labels
4. Helper text
5. Validation and errors
6. Empty states
7. Loading and progress
8. Success and confirmation
9. Dialogs and destructive actions
10. Permissions and privacy
11. Notifications
12. Search and zero results

## 1. Buttons

Use verb-led action labels when possible.

Examples:
- Save changes
- Add payment method
- Generate report
- Send invitation
- Cancel subscription

When two buttons sit together, their labels should communicate the decision without requiring the dialog body to disambiguate them.

Destructive actions should name the object when ambiguity exists:
- Delete workspace
- Remove member

## 2. Links

Link text should describe destination or action.

Prefer:
- View billing history
- Read privacy policy
- Change delivery address

Avoid isolated "here" links.

## 3. Forms and labels

Labels identify what information belongs in a control. Keep them visible.

Use hints for:
- format examples
- unusual requirements
- why sensitive data is requested
- constraints not obvious from the label

Do not repeat the label in the hint.

## 4. Helper text

Helper text should prevent uncertainty. If a helper is longer than a few lines, reconsider the flow or progressive disclosure.

Good:
"Use the email linked to your company account."

Weak:
"Please enter your email address in the field above so that we can use it."

## 5. Validation and errors

Good error messages are:
- specific
- local to the problem
- recoverable
- consistent with the label
- non-blaming

Pattern:
`[What needs attention] + [how to fix it]`

Examples:
- "Enter a password with at least 12 characters."
- "Choose a date after 26 September 2026."
- "This file is larger than 10 MB. Choose a smaller file."

Do not use only:
- Invalid
- Error 403
- Something went wrong
- Required field

When the failure is a service problem rather than user input, say so and provide the next meaningful action.

## 6. Empty states

Types:
- first use
- user-cleared
- filtered/no results
- permission-restricted
- system not connected

Write different copy for each cause.

Example first use:
Heading: "No projects yet"
Body: "Create a project to organize tasks, files, and updates in one place."
CTA: "Create project"

Example filtered empty state:
Heading: "No invoices match these filters"
CTA: "Clear filters"

## 7. Loading and progress

Use a simple label for short waits:
- Loading invoices...

For longer processes:
- state what is happening
- preserve work if possible
- offer cancellation when safe
- avoid fake countdowns or percentages

## 8. Success and confirmation

Confirm the outcome and relevant destination.

Examples:
- "Changes saved."
- "Report exported as CSV."
- "Invite sent to alex@example.com."

Avoid redundant "successfully" when the sentence is already clear.

## 9. Dialogs and destructive actions

Dialog title: describe decision or consequence.
Body: include only information needed to decide.
Buttons: name outcomes.

Example:
Title: "Delete this workspace?"
Body: "This removes 24 projects and cannot be undone."
Buttons: "Cancel" / "Delete workspace"

Do not make the dangerous option visually or verbally ambiguous.

## 10. Permissions and privacy

Explain permission requests just before they are needed when possible.

Answer:
- what access is requested
- why it is needed
- what the user gains
- whether there is an alternative

Do not use fear, guilt, or misleading urgency to obtain permission.

## 11. Notifications

A useful notification should have:
- event
- relevant object/person
- next action when required

Avoid notifications that merely restate background system activity with no user value.

## 12. Search and zero results

Differentiate:
- no content exists
- query has no matches
- filters exclude results
- search service failed

Offer an action that corresponds to the cause.
