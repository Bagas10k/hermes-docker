# Quantity lifecycle and scope-preserving review

Use this matrix when unit support crosses more than one transaction route. These are design and verification requirements, not a verified implementation recipe or an inventory of the currently running application.

## A. Discovery matrix

For each row, record actual route/handler, source identity, unit/quantity columns, status predicate, lock/transaction boundary, mutation owner and test evidence.

| Boundary | Question to settle | Failure to exclude |
| --- | --- | --- |
| Master and plant | Does backend eligibility match frontend filtering, including empty/legacy supply representations? | A visible product fails server validation, or an unavailable product is accepted. |
| SO creation | Are unit, quantity and commercial price snapshotted? | New non-Zak orders masquerade as zero Zak quota. |
| AR invoice and alternate creators | Which authorized path creates sales, restock or loco documents? | A sibling writer bypasses the shared unit rules. |
| Quota reservation | What consumes quota before physical dispatch? | Two invoice requests consume the same remaining quantity. |
| Dispatch and approval | Does a shipment fulfill an existing reservation or create a new one? | Invoice and linked shipment are counted twice, or assigning a shipment briefly releases the invoice reservation. |
| List and monitoring pages | Do accessors/index methods persist recalculated totals? | A read request restores old Zak-only values or destroys fractional usage. |
| Loading and receipt | Which action decrements/increments physical stock? Are there multiple receipt endpoints? | Invoice creation and loading both decrement, or two endpoints both add a receipt. |
| Edit, rejection and deletion | What remains reserved, what is released, and what physical movement already occurred? | Rejecting a dispatch releases an invoice still awaiting re-assignment; repeating a rejection restores stock twice. |
| Freight and ritase | Is each rate per trip, commercial unit or physical tonne? | A per-Zak tariff is multiplied by Bag/Ton without authorization. |
| Summaries and documents | Which numbers are commercial counts versus physical tonnage? | A formatted Ton value loses fractions or a cross-unit KPI adds incomparable quantities. |

Search all writers of the quota counter, not only the controller named in the task. Match linked invoice and shipment identities before excluding one; consider legacy document-number links as well as foreign keys. Decide cancelled/rejected status semantics explicitly and test them; the mere absence of a cancellation method is not evidence that an operational cancellation currently loses real quota.

## B. Preserve history without inventing attribution

- Distinguish a warehouse row carrying an optional product key from a stock ledger actually partitioned by warehouse AND product. A nullable key beside one aggregate balance does not establish multi-product stock accounting.
- Do not backfill one aggregate historical Zak balance into multiple products or new units. Preserve it until approved product attribution is available; expose unresolved attribution as a concrete decision rather than guessing from the latest master.
- Add nullable unit-aware fields or a product-stock structure only after tracing all affected writers/readers. Changing an integer to decimal alone does not solve missing product/unit identity.
- Keep legacy columns semantically legacy. Zeroing `jumlah_zak` for a new non-Zak document is safe only after every route consuming that document uses its canonical fields or rejects it before any side effect.
- Check downstream precision too: storing Ton at three decimals while copying physical load to two-decimal ritase/bongkar fields can round values. Decide an explicit rounding boundary and test the financial effect before claiming exact end-to-end behavior.
- Preflight the complete required column set, not just one feature column; partially applied schema can pass a single-column check and fail after financial mutations.
- Rehearse expansion, legacy backfill and rerun against the native baseline and an upgrade fixture. A no-op `down()` deliberately retaining data is not reversible migration proof; document code rollback compatibility or forward-fix recovery separately.

## C. Narrow behavior changes, not just narrow filenames

A related controller may contain payment, permission, tariff and status behavior outside the requested revision. Change only quantity/unit plumbing needed by the accepted flow. Do not add a blanket edit prohibition, force manual freight charging, redefine cancellation, or block a previously supported route just to simplify the implementation without disclosing the behavioral change and resolving the required business decision.

When the complete change does not fit the sprint, freeze one coherent tested slice and report unsupported requested routes as unfinished. Do not open a non-Zak entry point while its actual stock/shipment/document path remains unit-blind. Keep planned helper signatures and untested candidate architecture explicitly separate from empirically verified behavior.

## D. Bounded disposable integration sequence

1. Create the acceptance script before widening the next route. Require an explicit disposable database name and owned host/container identity before Laravel boot; use an internal test network, an inert app entrypoint and no active data volumes. Synchronize the current controllers, helpers, models, routes and views together, then compare source hashes and clear only the disposable caches. Apply the reviewed unit migration explicitly rather than allowing unrelated pending migrations to run.
2. Separate environment readiness from application assertions. Mark the fixture ready only after database connectivity, baseline import and the required schema succeed—not when an environment file is written. On failed initialization, inspect the owned container's exit/OOM state and bounded logs; repair only that test resource and reinitialize its incomplete state. Keep allocation limits measured rather than turning one successful memory setting into a universal requirement.
3. Provision neutral reference fixtures needed by the real controller, including its journal accounts and relevant opening balances. A financial controller reaching a missing COA account is a fixture failure, not evidence that the product unit is wrong. Correct the fixture without bypassing posting, changing production policy or accepting arbitrary exceptions as expected business rejection.
4. Make retries deterministic: use a fresh owned schema or unique scenario identities, and bind assertions to that scenario's documents. A failed controller may roll back while fixture rows remain; reusing them can alter later quota or stock results. Verify transaction level and before/after source, stock and journal state.
5. Start with the real invoice controller for Zak, integer Bag and fractional Ton below one. Check persisted unit, quantity, gross, HPP and quota; submit a forged client total and require the server-derived amount. Add specific invalid-precision, wrong-unit and over-quota negatives with no partial writes.
6. Exercise dispatch, warehouse receipt/load and double-drop through their actual controllers before claiming those routes pass. A manually inserted linked shipment proves only quota de-duplication, and `StokSemen::mutasi()` proves the stock service—not SPP approval, SPMB/SPBG payloads, browser submission or idempotent receipt. Keep these evidence boundaries in the report.
7. Test migration expansion/backfill, rerun and history preservation as distinct assertions. Calling `up()` twice proves rerun behavior only; it does not prove native fresh loading, production-version upgrade compatibility or rollback. Freeze final source and test hashes, rerun affected scenarios after fixes, then hand the evidence to independent QC.
