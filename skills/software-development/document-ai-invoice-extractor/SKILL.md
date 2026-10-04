---
name: document-ai-invoice-extractor
description: "Use when checking bounded invoice arithmetic."
version: 1.6.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [invoices, decimal, pdf, ocr, provenance, boundaries]
    related_skills: [pdf, test-driven-development]
---

# Bounded Invoice Extraction

Extract a strict label-based invoice from UTF-8 text, native/mixed/scanned PDFs, or PNG/JPEG OCR into evidence-bearing JSON. This is a local rule-based parser, not a universal document understanding system. Arithmetic consistency does not establish authenticity, payment, correct OCR, or tax compliance.

## When to Use

- Check arithmetic in documents using the exact supported grammar below.
- Preserve raw extraction evidence while routing uncertainty to human review.
- Do not use for bank statements, arbitrary merchant layouts, multi-invoice bundles, credit notes, handwritten documents, or automated payment approval.

## Prerequisites

Use `terminal` with the skill directory as `workdir`. Python 3.11, Tesseract with English language data, and DejaVu Sans are required for the Linux-tested fixtures. A local `.venv` is supplied on this installation. To recreate it:

`terminal(command="python3 -m venv --system-site-packages .venv && .venv/bin/python -m pip install -r requirements.txt", workdir=skill_dir)`

No cloud service, credentials, or language model is involved. Never send invoice data outside the machine. Evidence output can contain personal or financial information; store it with appropriate access controls.

## How to Run

`terminal(command=".venv/bin/python scripts/extract_invoice.py invoice.pdf --locale en_US", workdir=skill_dir)`

Use `--locale id_ID` explicitly for Indonesian number formatting. Pass `--tolerate-noise` to enable deterministic Indonesian currency/OCR speckle normalization (`locale_normalizer.py`). Pass `--fuzzy-labels` to enable Bayesian & Levenshtein-tolerant heading classification (`fuzzy_matcher.py`) under OCR character corruptions (e.g. 'lnvoice', 'Totql'). Never infer locale from separators or currency. JSON is printed to stdout; operational errors go to stderr.

| Exit | Meaning |
|---|---|
| 0 | All required evidence and arithmetic checks pass; not authenticity verification |
| 2 | `needs_review`: missing, ambiguous, unsupported, or inconsistent evidence |
| 1 | Operational failure, invalid CLI usage, corrupt input, dependency failure, or size limit |

## Supported Grammar

One invoice across one or more PDF pages (OCR pages always require review). Every nonblank line must match one of these English labels (case-insensitive); no headers, footers, addresses, or arbitrary table layouts are ignored:

```text
Invoice: INV-001
Currency: USD
Item: Widget; 2; 10.00; 20.00
Subtotal: 20.00
Tax: 2.00
Discount: 1.00
Total: 21.00
```

Every scalar label is mandatory exactly once. Zero tax/discount must be written explicitly. At least one Item is required; Item fields are description, quantity, unit price, and printed amount. Description cannot contain semicolons. Only USD and IDR are supported; both use a declared 0.01 arithmetic quantum here. Invoice identifiers are opaque, nonempty source strings, not validated business identities.

Numbers are nonnegative ASCII decimal strings: up to 12 integer digits and 4 fractional digits. Grouping must use groups of three. `en_US`: `1,234.56`; `id_ID`: `1.234,56`. No currency symbols, exponent notation, signs, spaces inside numbers, percentages, or nonfinite values. Quantity must be positive. Printed monetary totals/amounts must be exactly representable at 0.01; unit prices and quantities may have up to four decimal places.

## Procedure

1. Confirm supported source and explicit locale; do not rewrite source to make it pass.
2. Run the CLI and retain JSON plus exit status. Every field and item has page/line/raw evidence; all extracted page text is retained under `source.pages`.
3. Reconcile `quantity * unit_price` per line with Decimal `ROUND_HALF_UP` to 0.01. Sum printed line amounts to subtotal, then check subtotal + tax - discount against printed total, with exact comparison and no tolerance.
4. Route exit 2 to a human with issues and evidence. Duplicate scalar labels, even equal duplicate totals, produce a null selected value; never choose first, last, or largest.
5. Report exit 0 only as arithmetic-consistent extracted evidence. Inspect originals before financial action, especially after OCR.

## Pitfalls

- BIZ-003: PDF text pages use pdfplumber. Every image-bearing page, even with a valid native text layer, and every empty-text page is rendered by pypdfium2 at scale 2 (144 DPI), then OCRed with Tesseract English `--psm 6`. Full-page OCR replaces—not concatenates—the native text for parsing; `native_raw` remains in provenance. This avoids double counting but does not resolve conflicting layers. Every such PDF page adds `pdf_coverage_unverified` and forces exit 2, even when arithmetic passes. Blank pages also require review.
- `source.pages` retains page number, raw parsed text, extraction method and coverage state; PDF OCR records also retain native text, image count and fallback reason. Evidence references these page/line numbers. `coverage_complete` is true only for a fully read text file; it is always false for PDF/image input. `text_layer_only` describes native extraction, not visual completeness. Vector outlines, annotations, clipping and hidden layers are not comprehensively reconciled. Native-only PDF arithmetic may still return exit 0; never interpret that as visual coverage.
- Direct PNG/JPEG retains the prior exit-0 arithmetic contract but is explicitly `ocr_unverified`; multi-frame images are rejected. OCR has a 30-second per-call limit. No spelling repair, inferred digits or accuracy guarantee; even arithmetic-consistent OCR needs original-document review. Missing/failed/timed-out OCR is operational exit 1 with no partial JSON.
- Fixed document budgets: 2 MiB input; 20 PDF pages; 12 million pixels per raster or embedded image; 40 million cumulative pixels including rendered pages and each embedded image occurrence; 200,000 cumulative retained text characters (including native and OCR copies). Raster dimensions are checked before rendering; image dimensions before OCR. Text budgets are checked after the library returns text, before parsing/retention. Exceeded budgets return exit 1 without partial JSON.
- The Linux CLI supervises the entire worker (imports, extraction, OCR, parsing and serialization) with a 60-second wall-clock timeout. Worker and normal OCR descendants share a fresh process group, killed with SIGKILL on timeout and cleaned up on completion. Calling `read_source` directly does not provide the supervisor deadline. The supervisor bounds stdout and stderr capture to 4 MiB each (`MAX_OUTPUT_BYTES`) via non-blocking selectors; excessive worker output immediately triggers process group termination and operational error exit 1. Additionally, at exit 0 and 2, the supervisor strictly validates that stdout parses into a valid JSON object matching the full invoice schema (status, locale, rounding, authenticity_verified=False, fields, lines, issues, source) and asserts exit-code parity (exit 0 requires arithmetic_consistent with 0 issues; exit 2 requires needs_review with >=1 issues). Any schema violation, unparseable JSON, or exit status mismatch is transformed into operational exit 1 with an informative diagnostic on stderr and stdout withheld. The CLI launches through `scripts/worker_limits.py` before extraction imports: Linux RLIMIT_AS 1 GiB, RLIMIT_CPU 45 seconds, RLIMIT_FSIZE 32 MiB, RLIMIT_NOFILE 128, RLIMIT_CORE 0, and Linux `PR_SET_PDEATHSIG` (SIGKILL) parent-death signal configuration. Inherited stricter limits are never raised. These are per-process resource ceilings and lifecycle lifecycle anchors, NOT an aggregate RSS/CPU quota or hostile-PDF security sandbox. Descendants inherit ceilings but CPU consumption is not aggregated; while detached processes could escape naive PGID kills, workers configured with `PR_SET_PDEATHSIG` are automatically terminated by the kernel if the supervisor exits. Direct Python API calls bypass the wrapper. Use an external container/cgroup sandbox for hostile documents.
- Unsupported layouts and unknown lines fail closed to review. This intentionally rejects most unnormalized commercial invoices and receipts.
- No seller identity extraction, invoice date, tax-rate validation, bank account extraction or authenticity checks. Cross-document review is available only through the separate normalized-input API below; it is not integrated into the extraction CLI.

## Cross-document re-billing review (BIZ-013)

Use `scripts/rebilling.py` with `reconcile(rows, threshold=0.9)` and `fingerprint(row)`. Each row must supply explicit opaque `seller_id`, `document_id`, `line_id`, currency (USD/IDR), description, and canonical nonnegative decimal strings for quantity, unit_price and amount. Quantity must be positive. Preserve original evidence separately; never infer seller identity from description or the invoice number.

The SHA-256 fingerprint includes exact seller/currency scope, canonical decimals and NFKC/casefold/whitespace-normalized description. Reconciliation compares only cross-document rows within equal scope and numeric fields. Fuzzy matching uses the minimum of both directional SequenceMatcher ratios; scores are heuristics, not probabilities. Return pairs rather than transitive clusters, never delete source rows, and route all candidates to review. An exact match is not proof of fraud: legitimate recurring charges can match.

Hard bounds: 500 lines, 256 characters per text field, 12 integer/4 fractional digits, threshold 0.8–1. Worst-case comparisons are quadratic in line count and description length; no latency SLA is claimed. Missing metadata or duplicate document/line references fail closed with ValueError. `no_candidates` does not certify legitimacy. Credit notes, partial quantities and split invoices remain unsupported. Service periods require the explicit opt-in API below.

Verification: `terminal(command=".venv/bin/python -m unittest discover -s tests -v", workdir=skill_dir)`. BIZ-013 adds ten deterministic tests (exact/fuzzy, directional stability, seller/currency/numeric negative controls, invalid input and bounds, immutable source rows). Full suite: 81 passing tests; evidence `artifacts/biz013-tests.log`.

## Service-period review (BIZ-014)

Call `reconcile(rows, service_periods=True)` to validate every supplied `service_period` before comparison. A period is exactly `{"start": "2026-01-01", "end": "2026-01-31"}`: real calendar dates in strict YYYY-MM-DD format, start <= end, both endpoints inclusive. Missing/null periods mean unknown; malformed, partial or reversed periods raise ValueError, even for unmatched rows. Never substitute invoice issue dates for service dates.

Disjoint known periods suppress otherwise matching candidates (recurring-charge negative control). Equal/overlapping periods remain review-only candidates, with `period_relation` equal/overlap and inclusive `overlap_days`. Unknown periods retain candidates with relation unknown and null overlap. This does not certify legitimate billing or fraud. Source rows are unchanged. Legacy default behavior and `fingerprint` remain period-agnostic: never use that fingerprint alone to delete recurring charges. Date extraction from OCR, proration, contract entitlements and credit-note reconciliation remain unsupported.

Verification: `tests/test_biz014_periods.py` covers recurring exclusions, malformed dates, inclusive overlap, leap days, missing periods, order invariance and source preservation. Full suite: 85 tests passed; `artifacts/biz014-tests.log`. Inputs are synthetic fixtures, not a real-invoice accuracy study. Maintain the 500-line cap; no performance improvement is claimed because fuzzy comparison still precedes interval filtering.

## Versioned period identity (BIZ-015)

Call `versioned_fingerprint(row, version='v2')` from `scripts/rebilling.py`. Store the complete envelope (version, algorithm, digest, period_state, period_identity_complete, needs_review), not a bare hash. v2 domain-separates canonical content and explicit inclusive service dates. Missing/null periods use an unknown marker; equal unknown hashes do not establish equal service periods. Invalid periods fail closed. All identities remain review-only, including known equal periods: never delete or approve payments automatically.

For compatibility, `version='v1'` returns the unchanged `fingerprint(row)` digest and reports periods as ignored. Compare only like versions; never rewrite historical hashes in place. Retain original evidence and compute side-by-side v1/v2 envelopes when migrating. Overlapping unequal periods have different v2 digests; continue using `reconcile(..., service_periods=True)` to find overlaps, not equality hashing alone. The local adapters below support in-memory migration and single-writer atomic local snapshots; power-loss durability and OCR date extraction remain unimplemented.

Verification: eight deterministic tests in `tests/test_biz015_fingerprints.py` cover legacy serialization, period separation, canonical equivalence, unknowns, invalid dates, version/scope separation, overlap distinction and input preservation. Full local suite: 93 passing tests; evidence `artifacts/biz015-tests.log`. These fixtures do not measure real-invoice accuracy.

## Local fingerprint record migration (BIZ-016)

Call `migrate_records(records)` from `scripts/fingerprint_migration.py`. Input is a list of at most 500 records, each exactly `{'row': normalized_row, 'fingerprints': [envelope]}`. Rows accept only the eight required re-billing fields and optional service_period. Keep raw evidence outside this bounded adapter. History must contain one or two distinct supported version envelopes. Bare hashes, unknown fields/versions, duplicate seller/document/line references, malformed periods, and envelopes inconsistent with the supplied row raise ValueError; nothing is silently repaired.

Validate all records before copying. Preserve historical v1 envelopes exactly and append v2 only when missing; rerunning produces equal values and independent output objects. Verify exact field types: Python equality alone incorrectly treats True as 1 and False as 0. Unknown periods remain review-only. Hash integrity is not authentication. This pure function does not write files/databases and provides no durable transaction, checkpoint, crash recovery, or cross-process concurrency control. Use immutable input snapshots; concurrent mutation during a call is unsupported.

Verification: `terminal(command=".venv/bin/python -m unittest discover -s tests -v", workdir=skill_dir)`; six BIZ-016 tests cover history preservation, idempotence, envelope tampering/types, schema/bounds, late batch failure without source mutation, known-period drift, and the 500-record boundary. Full suite: 99 tests passed; `artifacts/biz016-tests.log`. Synthetic local fixtures only.

## Atomic local snapshot & directory durability (BIZ-017 / BIZ-018)

Call `save_snapshot(path, records)` from `scripts/fingerprint_snapshot.py` only in a trusted local directory with one writer. It validates and migrates the entire batch before I/O, writes deterministic JSON to a same-directory owner-only temporary file, flushes/fsyncs it, uses `os.replace` to publish, and then opens and fsyncs the parent directory. Reruns preserve historical envelopes and identical serialized bytes. Catch operational exceptions; never report failure as success. Pre-replace exceptions preserve the previous target and clean temporary files when normal cleanup can run.

If parent directory fsync fails after `os.replace`, `SnapshotDurabilityError` is raised. At this state, the snapshot is already published and visible at `path`, but persistence across sudden power loss is not guaranteed by the filesystem. Catch `SnapshotDurabilityError` specifically when handling durability boundaries. Atomic visibility and directory sync do not protect against concurrent writer conflict, hostile-path directory tampering, or power loss during filesystem metadata journaling. Existing file permissions become 0600. Do not use a production database path. The returned object is a detached migrated snapshot, not authentication evidence.

Verification: `tests/test_biz018_durability.py` adds four deterministic tests for directory sync ordering, post-replace directory fsync failure semantics (`SnapshotDurabilityError`), non-directory parents, and input preservation. Full local suite: 111 tests passed; `artifacts/biz018-tests.log`. Synthetic fixtures and temporary directories only; no power-cut testing or performance claim.

## Verification

`terminal(command=".venv/bin/python -m unittest discover -s tests -v", workdir=skill_dir)`

BIZ-012: Confidence scoring for fuzzy label matches and Levenshtein tolerance verification. Nine deterministic unit tests in `tests/test_biz012_fuzzy_label.py` evaluate Bayesian probability scoring and Levenshtein edit distance alignment for OCR-corrupted headings (`scripts/fuzzy_matcher.py` and CLI `--fuzzy-labels`). Tests verify that: (1) exact labels yield distance 0, confidence 1.0, and require no review; (2) OCR visual character confusions ('lnvoice', 'Totql', 'Subtotql', 'D1scount') are mapped to canonical labels with confidence >= 0.65 and gated to `needs_review` with audit anomalies; (3) Indonesian locale synonyms and typos ('faktvr', 'jum1ah') are supported; (4) short labels (<=3 chars like 'tax') strictly enforce 0-tolerance to prevent false collisions; (5) excessive distance (>2 edits) is rejected; (6) ambiguous candidates fail closed; and (7) end-to-end extraction with `--fuzzy-labels` successfully resolves corrupted headers into arithmetic verification while routing fuzzy audit logs to review. The test suite expands to 71 passing tests (`artifacts/biz012-tests.log`).

BIZ-011: Indonesian locale OCR dialect and noise tolerance verification. Ten deterministic unit tests in `tests/test_biz011_locale.py` verify normalization of Rupiah (`id_ID`) numeric tokens against OCR punctuation speckles, Indonesian nil-cents conventions (`,-`), currency prefix intrusions (`Rp`, `IDR`), whitespace kerning splits, and irregular grouping detection. Tests assert that (1) clean `id_ID` tokens pass without anomalies; (2) currency prefixes (`Rp.`, `IDR`, `$`) are stripped and flagged to `needs_review`; (3) nil-cents suffixes (`,-`, `,--`) are normalized to `.00`; (4) double punctuation speckles (`..`, `,,`) are collapsed; (5) scanning jitter / kerning whitespace is normalized; (6) irregular grouping lengths (`1.23.456`, `12.345.6`) are rejected without guessing; and (7) the `--tolerate-noise` CLI flag correctly reconstructs noisy OCR line items while preserving review auditability. The test suite expands to 62 passing tests (`artifacts/biz011-tests.log`).

BIZ-010: Multi-invoice document boundary detection and page slicing verification. Ten deterministic unit tests in `tests/test_biz010_boundary.py` verify partitioning of multi-page bundled documents into discrete invoice segments via `scripts/boundary_detector.py` and CLI `--detect-boundaries` flag. Tests assert that (1) single and multi-page continuous invoice spans are correctly segmented with accurate start/end page boundaries; (2) orphaned preamble pages before the first invoice header are routed to `needs_review`; (3) multiple invoice headers colliding on a single page trigger immediate review routing; (4) duplicate invoice identifiers within a bundle trigger review; (5) segments lacking explicit `Total:` lines are flagged for review; and (6) segments exceeding the page budget ceiling are caught. The test suite expands to 52 passing tests (`artifacts/biz010-tests.log`).

BIZ-009: Detached worker containment and parent-death signal (PR_SET_PDEATHSIG) verification. Four deterministic tests in `tests/test_biz009_pdeathsig.py` evaluate process lifecycle containment when workers or their descendants create separate sessions (`setsid`). Tests verify that (1) Linux `prctl(PR_SET_PDEATHSIG, SIGKILL)` is correctly configured; (2) `apply_limits` activates the signal by default; (3) a detached worker is terminated automatically upon supervisor death; and (4) an unprotected setsid child survives as an orphan, proving causal necessity. Suite reached 42 passing tests (`artifacts/biz009-tests.log`).

BIZ-007: `supervise` enforces strict JSON schema validation and exit status parity at the supervisor boundary for worker completions. When a worker returns exit 0 or 2, stdout is parsed and verified against all required keys (`status`, `locale`, `rounding`, `authenticity_verified=False`, `fields`, `lines`, `issues`, `source`) as well as contractual invariants (exit 0 strictly demands `arithmetic_consistent` with zero issues; exit 2 strictly demands `needs_review` with at least one issue). If the worker emits invalid JSON, misses mandatory schema fields, or violates status parity, the supervisor discards the output and returns operational exit 1 with diagnostic on stderr. Three new tests in `test_worker_failure.py` verify schema enforcement and corruption containment, bringing the suite to 35 tests. `artifacts/biz007-tests.log` records 35 passing tests.

BIZ-006: `supervise` bounds pipe buffer accumulation for both stdout and stderr (up to `MAX_OUTPUT_BYTES = 4 MiB`) using asynchronous non-blocking selector polling. When an output flood occurs, the supervisor immediately aborts accumulation, terminates the worker's process group with SIGKILL, closes descriptors cleanly, and emits an operational failure without leaking partial output. Two new tests in `test_worker_failure.py` verify isolated stdout and stderr flooding prevention, bringing the suite to 32 tests. `artifacts/biz006-tests.log` records 32 passing tests. These are isolated worker tests, not an adversarial security-sandbox claim.

BIZ-005: `supervise` itself discards stdout on every exit except 0/2, maps signals and unexpected exit codes to operational exit 1, and reports the signal number or exit code on stderr. Do not rely solely on the CLI printer to contain partial output. Timeout still raises `TimeoutError` after group cleanup. The supervisor trusts exit 0/2; it does not validate JSON. Six isolated subprocess tests cover SIGTERM, SIGKILL, partial output on exit 1, unknown exit 7, success/review controls, and partial-output timeout. `artifacts/biz005-tests.log` records 30 passing tests.

The prior 24-test suite includes seven isolated Linux resource probes (allocation denial/control, file-size denial, descriptor exhaustion, inherited ceilings, CPU/core configuration, invalid configuration); `artifacts/biz004-tests.log` records the passing run. CPU exhaustion itself and aggregate descendant budgets remain untested. The original 17 tests exercise real CLI processes, Decimal/locale checks, ambiguity, invalid documents, native PDFs, generated mixed/scanned PDFs with real Tesseract OCR, conflicting image/text pages, missing OCR, document/cumulative budgets, and a real sleeping child process killed by the supervisor. `artifacts/biz003-tests.log` records the BIZ-003 run; `artifacts/biz003/` retains generated PDFs, images and JSON. The timeout test uses a shortened supervisor deadline rather than waiting 60 seconds. Generated fixtures and extraction JSON live under `artifacts/`; historical red/green logs document incremental vertical implementation. OCR reproducibility is limited to the installed Tesseract/font versions, not a benchmark across real invoices. Tests are offline after dependency installation.
