# Finance correctness audit and safe release

Use this recipe when a change touches journals, cash/bank guards, COA classification, inventory valuation, P&L, or the balance sheet.

## 1. Lock the evidence model

Treat these as separate evidence classes:

1. **Targeted regression** — proves each reproduced defect is fixed.
2. **Full isolated Laravel suite** — catches application regressions.
3. **Disposable MariaDB rehearsal** — proves target-engine DECIMAL, migrations, SQL aggregation, and triggers.
4. **Real-browser review** — proves comprehension and responsive layout, not accounting correctness.
5. **Public read-only health** — proves the served login/subpath is reachable, not an authenticated transaction.
6. **Independent review** — supports the verdict but never replaces parent-run tests and readback.

Do not let one class stand in for another.

## 2. Trace money end to end

Follow every changed amount through:

`request string → validation → controller → service → BigDecimal → DECIMAL column → service result/JSON → Blade/JavaScript`

Keep money as decimal strings across boundaries. Use explicit scales: money 2 decimals; quantity/HPP 4 decimals. Add a regression beyond IEEE-754-safe cents. After the last patch, scan every touched path for `(float)`, `floatval()`, and `Number()`; inspect each match because numeric IDs are acceptable while monetary conversion is not.

For owner comprehension, render neutral synthetic data and verify these four surfaces at mobile and desktop widths:

- Pengeluaran: source account, available balance, consequence of posting, and `Terkunci` state.
- Jurnal Umum: opening balances, chronological entries, debit/credit totals, and `Seimbang` per entry.
- Laba Rugi: period, revenue, COGS, operating expense, and net profit.
- Neraca: as-of date, assets, liabilities, recorded equity, current earnings, and explicit balanced status.

A page-level no-overflow check is necessary but not sufficient; retain screenshots and inspect visible labels, totals, clipping, and action sizes.

## 3. Prove database behavior on a disposable target engine

Apply the exact pending migrations to ephemeral MariaDB, execute a neutral opening balance and representative receipt/sale/expense/ritase flow, then assert:

- every journal entry is balanced;
- P&L values match independently calculated expectations;
- assets equal liabilities plus equity;
- direct journal-line `UPDATE` is rejected;
- direct journal-header `DELETE` is rejected.

Trigger presence or migration status alone is not behavioral proof.

## 4. Production migration gate

Do not migrate until the user has authorized execution and every preceding gate is green.

1. Read the effective database name and baseline counts.
2. Create a private `mariadb-dump --single-transaction --routines --triggers`, compress it, run `gzip -t`, count dumped tables, and record SHA-256. A valid dump is not a restore drill; report that separately.
3. Produce a deterministic pre-migration snapshot containing important table counts and a hash of ordered journal headers plus lines.
4. Run only the named migration:

```bash
docker exec <app> php artisan migrate --force \
  --path=database/migrations/<single-migration>.php --no-ansi
```

5. Produce the same snapshot after migration and require exact equality.
6. Read back `migrate:status` and `information_schema.TRIGGERS`.
7. Run a rollback-safe behavioral probe: start a transaction, attempt an update that preserves the current line value and a header delete, require the trigger error, and roll back if either unexpectedly succeeds.
8. Recheck the public root/login and the application logs.

### Reliable container snapshot pattern

Avoid dense inline `php -r` for namespaced Laravel probes because shell escaping can fail before migration and obscure where execution stopped. Put the snapshot logic in a small checked PHP file, then feed it over stdin without writing into the container:

```bash
docker exec -i <app> php -l < snapshot.php
docker exec -i <app> php < snapshot.php > before.json
```

If any command fails, immediately read migration status and trigger inventory. Report **no schema change** only when both confirm the migration is still pending and triggers are absent; otherwise stop and reconcile actual state before retrying.

## 5. Final evidence freshness

After the last code, tracker, or report write:

- rerun targeted tests affected by that write;
- rerun the full isolated suite when a money-path file changed;
- rerun the disposable MariaDB rehearsal when service or migration behavior changed;
- run `git diff --check` and the detected workspace verifier;
- update the claim-proof ledger so production migration status and limitations are current.

Final reporting must distinguish: code corrected, disposable DB verified, production migration applied or held, authenticated browser flow tested or untested, and prototype limitations such as period close.