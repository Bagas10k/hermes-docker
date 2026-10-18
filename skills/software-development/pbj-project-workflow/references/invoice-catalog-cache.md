# Invoice form data: cached catalogs, rekening and payloads

Use when a master record exists but is missing, mislabeled or rejected in Buat Faktur. Treat catalog presence, SO eligibility, bank selection and successful invoice posting as separate acceptance criteria.

## 1. Locate the first broken boundary

1. Compare actual runtime source with the intended checkout before diagnosing the database. Read the invoice controller, host Blade, included modal, shared dropdown and its layout JavaScript; a control absent from the host can live in a partial.
2. Inspect actual schema before querying. `data_semen` stores product fields; SO `sisa_kuota_zak` is an accessor over `jumlah_zak` and `qty_pengambilan`, not a stored column. Existing tables/columns and master records argue against an incomplete-migration diagnosis; verify rather than prescribing `migrate`.
3. Record master IDs and cache contents **before** calling a remember()/refresh helper. Use `Cache::get` for `master_barang_semen_pbj`, `master_rekening_pbj` and `master_opsi_dropdown_rekening`. An empty array is a cached result, not a cache miss, and can hide subsequently created records for the configured TTL. Do not mutate cache while collecting the original evidence.
4. Trace cached records → controller view data → embedded option arrays → visible dropdown options → selected hidden IDs → `new FormData(form)`. Inspect label lookup separately: a raw numeric label can mean the selected ID is absent from the option list rather than broken Alpine mounting.
5. Keep diagnostic output to schema, counts, IDs and necessary product labels. Do not print bank numbers, owner names, credentials or complete sessions.

The invoice product list must not hide registered semen merely because it has no eligible SO. Selecting a product without SO and blocking Direct Plant issuance are compatible behaviors; do not remove the SO/quota rule to make the dropdown appear functional.

## 2. Invalidate at the actual shared write boundary

- Inventory every writer before editing. For master semen CRUD handled in one controller, reuse `CacheMasterHelper::bersihkanCacheMaster('barang')` after successful create/update/delete and after the bulk-delete commit. Clearing stale cache once repairs the current symptom but does not prevent recurrence.
- For rekening written through both master CRUD and COA controllers, use the common Eloquent `Rekening` saved/deleted boundary and the existing helper's `rekening` category. Clear both cached records and cached dropdown options; clearing only one permits a mismatched ID/label list.
- Schedule transactional invalidation on the model connection's `afterCommit`. Inspect installed framework semantics and test immediate execution outside a transaction, deferral until the outer commit, and discarded callbacks after rollback. Pre-commit invalidation can let readers refill the cache from old committed rows.
- Do not add redundant controller and model hooks for the same write. Eloquent events do not cover direct SQL or query-builder bulk writes; identify those paths explicitly instead of claiming universal coverage. Catalog freshness is not proof of live bank-balance freshness or concurrency safety.
- Preserve financial balances, posting, COA mappings and access policy. A missing option is not authorization to create replacement master records, reset tables or repair historical accounting.

## 3. Keep empty and inactive form states truthful

- Initialize bank selections from an existing rekening ID or an empty string, never `?? 1` or literal `'1'`. Inspect modal state, reset handlers and per-row confirmation payloads, not only the first initializer. A valid ID need not start at one.
- Reuse the shared dropdown's `kondisiNonaktif` prop: enable `id_rekening` only for toko/CBD/transfer and `id_rekening_dp` only for toko/DP/transfer. `x-show` hides UI but does not remove hidden controls from submission.
- Verify actual FormData: CBD omits the DP bank, DP omits the CBD bank, and TOP/internal restock omit both. Distinct `id_rekening` and `id_rekening_dp` names are not a duplicate-name collision.
- Use a placeholder for no available bank and retain backend relationship validation. Do not fabricate an ID or silently substitute a different bank to make the form submit.

## 4. Prove old-code failure and corrected behavior

1. In a guarded disposable database, warm the real helper cache, call the real master create action, verify persistence, then require that record in actual invoice-controller options. Run the desired assertion on old code and require its specific omission failure before applying the fix.
2. Extend that same check to edit/rename/price updates, deletion and semen bulk deletion. For rekening, exercise the separate COA create/update/delete path plus open-transaction, rollback and commit behavior.
3. Use exact schema enum values for synthetic fixtures; inspect them rather than guessing. A fixture enum failure or a CLI render missing middleware-provided `$errors` is a harness defect, not a reproduced application failure.
4. Require explicit failure exit codes and suite-final markers. Laravel console exception rendering can otherwise leave an apparently successful exit while later assertions never ran.
5. Use a restored isolated copy of the active engine for real HTTP/browser checks. Provision synthetic authentication only there, open the actual invoice modal, click product/SO and CBD/DP bank options, assert hidden IDs, inspect FormData for inactive methods and check mobile visibility. Never create synthetic bank records or submit a financial invoice in active data for proof.
6. Rerun the final compatible bundle after view changes; model-only QC does not certify later Blade corrections. A hand-authored fixture supplied with stale/fresh arrays checks UI handling only, not backend invalidation. A private `file://` render does not prove authenticated public navigation.
7. When swapping sources in an isolated HTTP server, inspect OPcache settings. If timestamp validation is disabled, reload that isolated server after the swap before interpreting a still-failing GREEN run. Refresh compiled Blade too; matching source hashes alone do not prove the running process loaded it.

Backend regression command from a complete checkout:

```sh
PBJ_TEST_INVOICE_CATALOG=1 PBJ_TEST_REKENING_CATALOG=1 flock -w 180 /tmp/pbj-disposable-tests.lock python3 scripts/test-mysql-isolated.py
```

The runner exercises `scripts/test-invoice-catalog-cache.php` and `scripts/test-invoice-rekening-cache.php`. Keep their testing/database/host guards intact, require both final markers and exit status, and verify copied source hashes before execution. Do not run fixtures directly against `pbj_app`.

## 5. Publish and explain the environment difference

1. Follow the approved sandbox publication gates in `branch-integration.md`. Preserve actual runtime rollback source, publish the frozen model/controller/view set, refresh compiled views when changed and reload FPM through the inspected path without accidentally running an entrypoint migration.
2. Invalidate only the relevant cache categories and repopulate from existing master records. Read back both cache layers and compare their IDs to master IDs. Compare relevant master/financial fingerprints before/after; do not mistake a prepared image for a container-image cutover.
3. Separate source correctness, active cache, browser state and Git publication. Git pull changes tracked files, not database cache, already-open tabs or image-built containers. Local behavior can differ with cache state and operation order; state that as a hypothesis unless the local environment was inspected.
4. If a hot-published correction has not reached Git, say so plainly: pulling the old branch cannot receive it. After an authorized push, report the actual commit and remote readback instead of another build-only status.
5. Ask for one refresh/reopen after publication because an open form retains its earlier HTML/Alpine snapshot. Disclose any missing authenticated-public coverage; login HTTP 200 proves availability, not invoice selection or financial posting.
