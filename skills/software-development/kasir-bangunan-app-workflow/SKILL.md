---
name: kasir-bangunan-app-workflow
description: Use when maintaining Bagas's kasir-bangunan-app prototype.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [laravel, cashier, prototype, subpath]
    related_skills: [systematic-debugging, application-auth-security]
---

# Kasir Bangunan prototype workflow

## When to Use

Load for changes or diagnostics in `/home/ubuntu/kasir-bangunan-app`, especially login, sidebar, and public subpath routing.

## Incumbent navigation and input workflow

- Preserve the approved green-white application shell during UI refinement: primary navigation stays in the left sidebar on desktop and becomes a left drawer on phones. Do not replace it with top tabs or a bottom menu without explicit approval; matching the palette alone does not preserve the interface.
- Master data entities must be presented as separate, directly accessible pages/sub-menus in the sidebar (e.g. Produk, Pelanggan, Supplier, Karyawan, Kendaraan/Armada) rather than bundled into a single screen with an entity-type select dropdown filter. Direct one-click access per master entity matches user workflow; never force users to pick entity types from a dropdown just to view or manage different master datasets. Land the sidebar link, panel mapping, entity dataset, form handlers, and reload/deep-link behavior as one working slice; a renamed sidebar pointing to an empty or still-combined panel is unfinished. After the direction is selected and execution authorized, continue that slice instead of repeating the same audit or asking the same navigation question.
- Present **Akun Login** as a separate Admin-only sidebar page, not part of Master Karyawan. Creating an employee record must not implicitly create a login or grant privileges. Reuse the approved list-first page and add/edit popups for name, email login, Admin/Kasir role, active status, and password changes; keep existing credentials unchanged until an explicit account action. Preserve the agreed cashier permission matrix rather than adding speculative permission toggles or new roles. Use `application-auth-security` for account lifecycle and server-enforced session revocation.
- Keep supporting CRUD/operational pages list-first, with labelled add/edit actions opening input forms in popups. The cashier is an explicit exception: preserve the approved catalogue-left/cart-right workspace, quantity steppers, visible total and checkout; stack catalogue then cart on phones. Only payment and pre-save review are popups. Never turn cashier into a nota list with an Add Sale button or put the whole sale into a long popup. Adding roles or operational modules is not permission to replace working cashier features; compare the incumbent source and flow before editing.
- For a request to match the old cashier, open the actual incumbent route and candidate in the same isolated runtime before editing. Compare the collapsed/expanded sidebar, loaded font, header/content spacing, monitoring panels, populated catalogue/cart, history, and payment/review states; copying green-white colors or only restoring two columns is insufficient. Preserve the incumbent's compact rail behavior and reuse its real components/CSS before creating replacement controls. Keep legacy source untouched when adapting the candidate to V2 data.
- Lock the measured presentation and existing flow as acceptance criteria. Capture equivalent old/new desktop/mobile states and inspect the saved image dimensions and scroll positions; distinguish restored workflow from pixel-identical appearance. For the ordered procedure, load `ui-ux-execution-standard` → `references/incumbent-preservation.md`.
- Use the reusable popup recipe in `ui-ux-execution-standard` → `references/task-workspaces.md` for DOM ancestry, named-control collisions, focus, cancellation, and request-count checks.

## Repository Documentation and Scope Safety

- Before a multi-file project task, inspect `git status --short`, read the current `build_tracker.json` if present, and check whether target documentation files already exist; an existing dirty tree means preserve unrelated work and do not overwrite a tracker owned by another task.
- When asked to establish project-wide agent guidance, read the existing `AGENTS.md`/`CLAUDE.md` first, create focused topic documents, and add a small mandatory-reading pointer to the agent entrypoints rather than duplicating full policy in each file. Verify the exact changed-file list and `git diff --check`.
- Keep durable design principles, agent workflow, reusable project facts, and execution history in their respective documents; treat execution logs as append-only, record only commands/results actually observed, and never convert a prior task's claims into current verification. Before writing an execution-log timestamp, read the system clock in the project's stated timezone (for WIB use `date '+%Y-%m-%d %H:%M:%S %Z (%z)'`); do not infer the current time from conversation timestamps or delegate start times.
- Repository guidance should require agents to inspect applicable instructions and existing code before acting, use synthetic data only, verify runtime claims, and explicitly disclose untested authentication or production gates. Do not put credentials or personal data in documentation.

## Deployment & Dirty Working Tree Operations
*(Full step-by-step procedures in `references/git-dirty-tree-and-deployment.md`)*

1. **Host Bind-Mount Model**: Code on host (`~/kasir-bangunan-app`) is bind-mounted read-only into production container (`kasir-bangunan-prod-app-1`). Host edits immediately reflect inside the container.
2. **Standard Deploy Sequence**:
   - `npm run build` (build Vite assets)
   - `docker exec kasir-bangunan-prod-app-1 php artisan view:clear`
   - `docker exec kasir-bangunan-prod-app-1 php artisan config:clear`
3. **Route Invariant**: POS route is mounted at root `/` (`pos.index`), NOT `/pos`.
4. **Dirty Tree Staging**: Never run `git add -A` or `git commit -a`. Stage only files directly touched by the approved task.
5. **Pull & Sync**: Inspect `git status --short` and `git diff` before pulling. Use stash with index preservation if uncommitted local work exists.

## Supporting References
- `references/git-dirty-tree-and-deployment.md`: Full 35KB guide for safe branching, dirty tree commits, and container deployment.
- `references/operational-v2-requirements.md`: POS cashier, thermal printing, barcode scanning, and invoice generation specs.
- `references/finance-audit-and-release.md`: Accounting journal integration, ledger reconciliation, and shift closing reports.
- `references/release-artifact-verification.md`: E2E preview container testing and smoke tests.

## Shared CRUD Forms and Themed Date Pickers

1. Before a cross-page form cleanup, mechanically inventory every Blade `<form>`, CRUD modal, validation-error path, and `input[type=date]`; count actual matches and record per-field `id`, `name`, type, bounds, required/disabled state, default, and JS consumers. A form that is visually inconsistent may still have a page-specific submit or modal contract.
2. Inspect the full cascade in `layouts/app.blade.php` and every loaded partial before adding shared CSS. For modal placement, inspect its DOM ancestors for `transform`, `filter`, or `perspective`, which can change a fixed overlay's containing block; then compare the rendered overlay/dialog bounds with the viewport before deciding that it is miscentered. Treat screenshot diagnosis as a hypothesis, not proof, because existing flex centering may already be correct. Scope styling to explicit form classes or `.form-group` descendants; exclude hidden, checkbox, and radio inputs from text-field rules. Find duplicate selectors and later media rules first, because the last matching `grid-2` rule wins and can silently undo a new shared layout.
3. Preserve each form's action, method, CSRF/method spoofing, names/IDs, validation semantics, and data attributes. Do not add controls that imply unsupported controller behavior; form polish is not permission to change persistence or filters.
4. Keep a native date input as the canonical successful form control (`name`, `id`, ISO `YYYY-MM-DD`, `min`, `max`, `required`, `disabled`) when adding a themed calendar. Synchronize selected dates to `.value` and dispatch native `input`/`change` events so inline handlers and existing JS consumers continue to work. Do not suppress the native picker until the custom control has initialized; retain a native fallback when JavaScript is unavailable or fails.
5. Implement the custom calendar against the WAI-ARIA APG dialog/grid pattern: labelled month/year live region, one roving tab stop in the day grid, arrow-key day/week movement, Home/End week movement, PageUp/PageDown month navigation (Shift for year), Enter/Space selection, Escape close, outside-click close, and focus restoration. Respect `min`/`max`, leap years, required/disabled inputs, and reduced motion. Render month names in Indonesian; construct dates from local year/month/day parts rather than parsing `YYYY-MM-DD` with `new Date(string)`, which can shift a calendar day through UTC timezone conversion.
6. Separate shared form styling from calendar behavior so visual changes cannot alter date serialization. In a real browser, exercise the behavior—not just markup or screenshots—and assert the visible localized label plus canonical ISO value and dispatched `input`/`change` event. Cover selection, min/max edges, month navigation, Escape plus focus restoration, form reset, disabled inputs, and each known JS ID consumer; mark any unexercised case unverified. A CSS preview alone does not prove a working datepicker. An isolated synthetic preview can verify shared-component appearance and behavior, but it does not prove the authenticated app route works.
7. Before editing shared layout or JS, inspect container mounts and whether the host source is served live. A read-only container mount can still expose host edits immediately; make that live impact explicit and obtain the user's authorization before a direct shared-file patch. Prefer isolated QA/render first, then apply the bounded patch to the authorized source.
8. For a request covering many forms, land and verify the complete shared primitive before claiming the rollout complete: consistent labels, spacing, text/select/textarea states, field errors/help, touch/focus behavior, responsive layout, and the themed date interaction. State exactly which forms were covered; never report a CSS foundation as a finished calendar or all-form cleanup.
9. When Bagas asks what an interactive control looks like “while selecting” or corrects a description as referring to another state, open that exact control in a real browser and show the active-state screenshot; do not describe the idle control again. Answer the clarified state directly and keep commentary shorter than the implementation report.

Reference: use the W3C WAI-ARIA APG Date Picker Dialog pattern (`https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/datepicker-dialog/`) for keyboard and focus behavior; adapt visual tokens to the existing Kasir Bangunan theme rather than copying its example styling.

description: Use when maintaining Bagas's kasir-bangunan-app prototype. Includes shared CRUD form and localized date-picker workflows.

## Related Workflow Overlap

`frontend-agent-craft` and `ui-layout-intelligence` also cover reusable UI layout and browser verification. Use this repo skill for Laravel form contracts, live-bind-mount safety, and project-specific acceptance; use those skills for general interface craft and spacing decisions.
