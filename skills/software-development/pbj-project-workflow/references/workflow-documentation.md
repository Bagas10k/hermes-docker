# Evidence-based role guides and visual PDF delivery

Use for explaining an application's actual workflows to its owner or staff. This is documentation, not permission to repair authorization, migrate data, push, or deploy.

## 1. Settle the brief and freeze the source

1. If an interview is requested, ask one decision at a time: actual code, ideal SOP, or their comparison; then depth and external participants. Retrieve role names and existing behavior yourself. Accept a preference for visual, simple points as a presentation decision, not a reason to omit corrections or prohibitions.
2. Record `git branch --show-current`, `git rev-parse HEAD`, and relevant working diffs in the verified repository. Identify whether the guide describes committed code, uncommitted work, or verified runtime. Never label a code-only guide as a walkthrough of the public application.
3. Enumerate application roles from the registry/seeder and reconcile with migrations, account-creation validation, authentication, the UI matrix and access enforcement. Keep four separate facts: a job-title reference exists; an account may be assigned that title; a usable menu/portal exists; a workflow is authorized. Absence from the seeder or menu matrix proves neither that accounts cannot be created nor that login is impossible. Draw drivers, customers, suppliers and similar participants as external actors when no application workflow is evidenced, without claiming a technical login prohibition.
4. For work reports, freeze a reporting cutoff and a small source/hash manifest. Label results arriving later as candidate receipts until execution and review verify them; do not silently upgrade the frozen report's status.

## 2. Discover behavior in bounded parallel scopes

Assign finance, dispatch, warehouse/vehicle, and administration/reporting scopes as appropriate, with a separate boundary reviewer. Give each worker the same source commit, explicit read-only constraints, exact output paths, and a compact data schema. Do not create a separate permanent skill/reference for each role or session.

For every flow, collect:
- Role key, purpose and short flow title.
- Source input/document and prerequisites.
- Real user action, resulting status/document/financial effect, and recipient.
- Rejection reason, owner correction/cancellation path, and forbidden actions.
- Evidence: route, controller method, middleware and relevant view condition.
- Confidence boundary: inspected code versus exercised HTTP/browser behavior.

Trace route → global middleware → route role parameters → controller action guard → state transition → rendered controls. Check all layers before writing “can approve,” “can pay,” or “read-only.” A visible menu, hidden button, controller allowance and globally reachable route are different claims. Verify that the actual page/component consumes a read-only helper before describing its buttons as disabled. Scope permission to the exact endpoint, not just a document label: two controllers printing the same document can enforce different roles. Phrase an absent guard as a code finding, not proof that a direct request succeeds; that requires an isolated authenticated HTTP test. Record contradictions as gaps, not endorsed procedures.

Read the persisted fields and downstream service before simplifying status effects. Do not equate a completed delivery with paid ritase, a completed repair with a ready vehicle, or a general period-order guard with compulsory month-by-month processing. Distinguish rejecting an unpaid draft from reversing a posted expense: only the latter can restore funds. Describe a payment path that executes directly separately from a draft-and-approval path, even when both belong to AP.

Name a handoff automatic only if code implements it. Otherwise label it an operational handoff or a reported issue requiring the appropriate owner. Do not invent an approval role from its managerial title.

## 3. Synthesize the visual guide

1. Lead with a small cross-role map and legend; follow with one role per page where practical.
2. Use 3–4 principal flows per role. Format each as four vector boxes: **Dari → Kerjakan → Hasil → Ke siapa**. Keep each node roughly eight words or fewer; split overflow into a note instead of shrinking fonts. Draw alternative destinations as a visible fork, not successive boxes: a note saying “these are alternatives” does not undo the false sequence implied by arrows. Split independent actions when their results differ; posting a journal and closing a year must not share a single implied outcome.
3. Add two short blocks: **Jika ada kesalahan** and **Tidak boleh**. Include input, output, handoff and correction without turning the page into an essay.
4. Separate inactive/candidate features from current procedures. A static review PASS on a partial does not make the companion controller/script workflow available.
5. Use a warm paper background, dark ink, PBJ blue actions, restrained semantic warnings and no emoji. Label external actors and pending features with text and line style as well as color. Keep arrows behind boxes, with legible arrowheads and gaps.
6. Preserve enough technical references for auditability in a small source line or appendix; keep full hashes and long paths out of diagram nodes.

## 4. Prepare screenshots without leaking static data

- Verify provenance from the test fixture and source artifacts, not from “Sintetis” appearing somewhere on the screen. Synthetic transactions can still use a real company header, bank account or contact details.
- Redact a duplicate raster asset before embedding it; leave application evidence and original files unchanged. Never rely on a translucent HTML/PDF overlay to remove searchable sensitive material.
- Use full screenshots for context and crops from the original resolution for important evidence such as an identity field or an unsupported-reconciliation warning. Enlarging a contact-sheet thumbnail cannot recover detail.
- Caption each image with environment and scope. A screenshot of a button or voucher does not establish submit persistence, successful navigation, or document authenticity; cite the actual execution separately.

## 5. Generate and verify the artifact

1. Reuse installed Playwright/Chromium and local fonts. Write HTML/CSS with inline SVG; avoid introducing a diagram library for static box-and-arrow flows.
2. Prototype the densest role page before duplicating the layout. Check a page with the maximum intended flow count, long role names and warning/correction blocks; an empty template cannot reveal overflow.
3. Wait for `document.fonts.ready`, use print media and generate with `page.pdf({ path, preferCSSPageSize: true, printBackground: true })`. For a fixed-page HTML layout, declare `@page { size: A4; margin: 0 }` and keep the readable margins inside each page element.
4. Before printing, inspect every page in DOM: `scrollHeight <= clientHeight + 1`, `scrollWidth <= clientWidth + 1`, all images `complete && naturalWidth > 0`, and the last content boundary above the footer with a visible safety gap. Account for margins/padding rather than checking only the page container height. Fail the render on clipping or missing assets; do not hide a failure with `overflow: hidden` alone.
5. Read the generated PDF with `pypdf.PdfReader`: compare page count to the authored pages, verify A4 sizes and nonempty text, and search for required role/status terms and accidental secret material. Scope a count to unique modes/checks; later refinements replace rather than add to an earlier browser count.
6. Rasterize the PDF itself using PyMuPDF (`pymupdf.open`, `page.get_pixmap`) and inspect a contact sheet, then full pages containing dense tables, diagrams or screenshots. HTML screenshots and a contact sheet alone do not establish printed text legibility. Check arrows and essential labels at A4 size and, where needed, in grayscale.
7. Batch legibility fixes, rerender and reconfirm the affected pages. Prefer larger detail crops and less prose over smaller fonts. Do not claim the full guide complete from a successful one-page prototype.
8. Verify the final destination file's hash and size, then send its absolute path through `MEDIA:`. Keep the response short: what the PDF covers and any material verification limit.

## 6. Keep claims and task boundaries intact

An independent report is input, not automatic truth. Correct unsupported claims such as universal race safety, physical-document verification, leak success from a failing query, or complete privacy from synthetic labels before incorporating them.

When the user switches from implementation to reporting, do not resume application work merely because an old worker finishes. Record the artifact as candidate/unverified, finish the current documentation task, and keep code/data changes outside its scope.