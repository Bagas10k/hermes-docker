---
name: pbj-unit-alignment
description: "Use when aligning PBJ product units from SO to sales."
version: 1.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pbj, units, so, invoices, inventory, laravel, bigdecimal]
---

# PBJ product-unit revisions

## When to Use

Use for changes to commercial units across product masters, SO, invoices, quota, stock, shipments and their displays. Apply `pbj-project-workflow` for repository and release boundaries and `test-suite-integrity` for disposable testing. This skill specifies the unit contract, not a claim that the current implementation already satisfies it.

## 1. Lock the outcome and preservation boundary

- Once Bagas approves implementation, carry the approved route/unit acceptance list through implementation, integration tests and final review without requesting the same 'lanjut' after each audit. Treat an audit or a partial worker delivery as an intermediate result, not a reason to return the task to him. When he asks to keep working, resume the first unclosed acceptance item from the current files and evidence instead of starting another discovery plan. Stop only for completion, a concrete owner decision, an explicit user stop, or an enforced runtime/time boundary; report an enforced interruption honestly without implying the task is delivered.
- Interpret 'tanpa mengubah yang lain' as preserving unrelated behavior: payment policy, role access, freight tariffs, payroll/ritase rules, other material modules and existing local changes. Quantity plumbing in a related consumer can be necessary; unrelated redesign is not.
- Enumerate acceptance by unit AND route before editing. Direct Plant single-drop, warehouse sales/restock, double-drop, edit, approval/rejection and printing are separate routes; enabling one is not completing all of them. Report an unconverted requested route as unfinished, not as a completed feature with an invisible scope reduction.
- Track permission separately for source edits, isolated tests, sandbox migration/publication and Git publication. When Bagas explicitly asks to see the revision on the sandbox without pushing Git, carry the necessary reviewed schema change and code publication through the sandbox release gates; 'no push' does not mean 'leave the web unchanged'. An instruction to inspect code only limits that inspection to read-only source work; it is not proof that an earlier deployment happened or was undone. Reconcile status from the latest recorded source/schema/runtime evidence rather than reusing an older 'local only' report.

## 2. Trace every reader and writer once

Read the current diffs and schema, then follow actual routes through master/plant eligibility → SO snapshot → invoice request → quota → stock/load/unload → shipment → journal → display/print. Search all references to `jumlah_zak`, `jumlah_unit`, `qty_pengambilan`, `stok_tersedia` and fixed `0.05` factors; classify each occurrence instead of globally replacing it.

- Include alternate invoice creators and warehouse request-to-finance paths; guarding only the AR form leaves sibling writers unchanged.
- Inspect list/index synchronizers before treating them as reads: a page that recalculates and persists quota can overwrite the new contract merely by being opened.
- Distinguish invoice reservation, approved dispatch and physical loading/receipt. Preserve the established side-effect owner rather than adding a second stock decrement to invoice creation.
- Resolve agent-reported methods and bypasses against actual routes. An independent transport module accepting tonnes is not proof of a bypass into SO stock or sales.

For the lifecycle review matrix, migration decisions and a bounded disposable-test sequence, read `references/quantity-lifecycle.md`.

## 3. Specify the canonical value and unit together

- Use `Zak` and `Bag` as integer commercial quantities; normalize Curah to `Ton`, allowing up to three fractional digits. Validate precision and range on the original decimal string before casts, arithmetic or writes; do not truncate with `parseInt`, `(int)` or `ceil`.
- Resolve units from authoritative product/SO records, never hidden client claims. Snapshot each document's unit; do not reinterpret history using today's master.
- Default documents with NO explicit historical unit to Zak. If the unit IS explicitly Bag/Ton but `jumlah_unit` is missing, do not relabel it Zak, borrow `jumlah_zak`, or fabricate zero. Permit a legacy fallback only where that field's unit is documented, such as an explicitly Ton SO's `jumlah_ton`; otherwise reject clearly.
- Keep quota and commercial price in the product's own unit; reject SO/invoice mismatches and never sum Zak, Bag and Ton as one raw quantity.
- Compute gross server-side from validated quantity × authorized price with `BigDecimal` strings. Preserve strings through persistence and inspect called journal/service signatures: conversion back to float before a typed service boundary invalidates an end-to-end exactness claim. Verify the installed Brick Math API; versions using PascalCase rounding enums require `RoundingMode::HalfUp`, not the legacy uppercase spelling.
- Separate physical tonnage from commercial units. Ton is already tonnage; Bag needs a verified positive kg-per-Bag value and a usable master input/validation path. Snapshot the factor on dispatch so later master edits do not rewrite historical loads. Do not apply the legacy Zak weight to Bag.

## 4. Implement a dependency-complete slice

- Choose and document one quota lifecycle before changing its writers. Define reservation, physical collection, rejection and release; an invoice and its linked shipment must not consume the same quota twice. Require locks and consistent source identity for each mutation.
- Materialize and test the shared contract before delegating callers. Give workers an existing helper path, exact signatures and return types; a promised helper plus speculative `class_exists` fallbacks creates divergent behavior and leaves integration untested.
- Partition workers by non-overlapping, dependency-complete edits, normally no more than three principal files per dispatch. Hand off an already-inspected method, exact helper signatures, payload and one acceptance check; a whole warehouse or shipment subsystem with a short prompt budget is still an oversized task. If a worker returns partial work or exhausts iterations, inspect its actual diff, integrate only verified hunks and take over the remainder. Preserve budget for the parent integration test and a separate final reviewer; worker lint or a self-written 'SELESAI' is not that review.
- Preflight all required columns before financial mutations. Preserve an unmigrated Zak-only path only when demonstrably compatible; reject non-Zak clearly while required schema is absent. Treat migration as a functional dependency, not optional finishing work: code that persists new quantity/unit fields cannot enable the feature on an old schema. Report 'coded, migration pending, feature not active' until the named target's migration record AND actual column types are read back.
- Keep selective fail-closed guards at unsupported boundaries until the corresponding route is complete. A guard is temporary containment, not delivery of Bag/Ton support. Do not invent stock allocations or change freight charging policy merely to make a route pass.
- Finish the real form path too: dropdown filters, Alpine watchers, submit validators, hidden fields, table formatting and printed documents. A decimal input can still fail when a later watcher truncates it or a submit handler rejects values below one. Follow every new field through validation → insert/update payload → model mass assignment/cast → database readback; a weight input that the controller never saves or a unit field absent from `$fillable` silently breaks the contract. Keep frontend containment aligned with the backend: do not remove its unsupported-route warning merely because another worker promises support.
- Reserve tool/time budget for verification before widening edits. Stop starting new partial paths when only enough budget remains for final diff, checks and reporting.

## 5. Prove the final candidate at the right boundary

1. Lint the exact changed source mounted read-only in a disposable PHP container; linting a baked file in the active app does not verify a host edit.
2. Run pure helper/model checks with no network where possible. Use `php -d zend.assertions=1 -d assert.exception=1 <test>`; source-string assertions and copied formulas are structural checks, not transaction evidence. Avoid interpolating PHP variable names in double-quoted source assertions.
3. Drive actual controllers and persistence on a guarded disposable database of the authorized MySQL engine/version, on an isolated network without active data volumes. Synchronize and hash-check all exercised dependencies, run only the reviewed migration set, and refresh route/view caches.
4. Assert legacy Zak, integer Bag, fractional Ton including a value below one, malformed/overprecision/over-quota and cross-unit rejection, exact stored totals, no writes on rejection, invoice-to-shipment quota continuity, and physical stock side effects on the routes claimed supported. Verify fresh/upgrade/rerun migration behavior without changing historical values unexpectedly.
5. Exercise the real modal and inspect its submitted payload plus saved result in a browser; test edit and terminal actions where changed. Treat screenshots and tests from before the last relevant edit as stale.
6. Obtain independent QC of the frozen diff and test artifacts. A verdict contradicted by raw failures, a missing success marker, or lint of another source cannot pass the candidate. After any integration edit, rerun the affected controller/persistence check on the final bytes before advancing its status; never make a last untested warehouse/double-drop edit and reuse the earlier direct-invoice PASS. Track coded/tested/browser-reviewed per route so the next turn closes gaps rather than restarting the task.

## 6. Deliver one consolidated report

Report in plain Indonesian: **what changed**, **what remains unfinished by route/unit**, **tests actually run**, and **challenges or owner decisions**. Separate local source, tested candidate, migration execution, commit/push and served runtime. Do not claim universal precision, zero regression or completed sales from a helper test, lint, an agent summary or migration draft. Keep interim pulses concise; do not end an approved implementation with another request to approve the same audit.
