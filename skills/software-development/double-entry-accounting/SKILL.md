---
name: double-entry-accounting
description: Manage double-entry bookkeeping and financial accounting.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags:
      - Accounting
      - DoubleEntry
      - GeneralLedger
      - FinancialInvariants
      - ERP
---

# Double-Entry Accounting & Financial Invariants

Architect, enforce, and audit mission-critical double-entry accounting engines, General Ledger (GL) posting, and financial statement generation. Guarantees mathematical conservation laws (Debits equal Credits), immutable transaction journals with reversal corrections, and strict segregation of duties across ERP lifecycles.

## When to Use
- User asks to "bangun modul akuntansi", "sistem pembukuan double-entry", "buat laporan keuangan", or "audit neraca / laba rugi".
- Implementing General Ledger, Chart of Accounts (COA), or Journal posting mechanisms.
- Designing Order-to-Cash (O2C) or Procure-to-Pay (P2P) financial integrations.
- Enforcing database constraints against unbalanced transactions, floating-point rounding errors, or unauthorized retro-edits.
- Advising on business bookkeeping, proposed journal entries, reconciliation, and financial-statement interpretation without production posting.
- User asks to find accounting research or journal articles and integrate the evidence into an ERP-building SOP.

## Advisory workflow for business accounting
1. Determine entity type, reporting period, users of the statements, available source documents, and which reporting framework applies; do not infer SAK EMKM merely from the word “small business.” Separate commercial books from fiscal adjustments.
2. For each proposed entry, present the evidence, date, debit/credit account, amount, rationale, reporting effect, assumptions, and approval status. Reconcile bank, receivables, payables, inventory, and cash to source records before interpreting profit.
3. When researching Indonesian accounting or tax rules, prioritize current IAI standards and DJP/JDIH regulation, identify effective period and applicability, and cite the exact source. Distinguish a regulator-hosted personal article from binding rules; do not crawl or reproduce copyrighted standards wholesale.
4. Keep advice distinct from execution and independent audit. Never post or authorize real transactions, file tax returns, or certify statements without a separate explicit mandate and qualified review. Use only neutral synthetic entities in demos; keep private business records out of public search queries.
5. State verified facts, analysis and assumptions, proposed actions, and outstanding checks separately. If the source documents are missing, request only the facts needed to change the accounting conclusion.

## Research-to-ERP-SOP workflow
1. Inspect the existing ERP SOP and accounting skill references before researching; identify its owner file and acceptance gates. Do not treat a skill update as an edit to the requested SOP.
2. Find primary standards/regulations and, when asked for *jurnal* as literature, peer-reviewed articles on the specific accounting/ERP design question. Verify title, author, DOI or publisher URL, publication year, and what the source actually supports; distinguish scholarly journals from accounting journal entries.
3. Map each supported finding to an implementable SOP gate: requirement -> source/applicability -> design control -> synthetic test -> responsible reviewer. Record unsupported recommendations separately as proposals, not sourced rules.
4. Patch the actual SOP with the smallest change, preserve existing approved behavior, and verify the edited target plus relevant tests. Report separately what was researched, integrated, and runtime-verified. When a skill/tool name fails lookup, copy the exact identifier from the available-skills result, retry it once, then switch to a working discovery path; never vary only irrelevant arguments while preserving the bad name, and never hand the unfinished task back to the user as a request for “continue.” If a research backend is unavailable, use a permitted alternative and verify the retrieved source content before claiming research complete.

## Prerequisites
- Database engine with ACID transaction support (PostgreSQL, MariaDB, or SQLite).
- Strict numeric type discipline: `NUMERIC(19, 2)` or integer cents for monetary values. `FLOAT` or `DOUBLE PRECISION` is strictly forbidden.
- Clean separation between tenant accounting periods, fiscal calendars, and document series.

## How to Run
Invoke database migrations, ledger balance queries, or automated financial reconciliations through Hermes tools:
- Run accounting test harnesses or audits with the `terminal` tool.
- Inspect and patch ledger models using `read_file` and `patch`.
- Verify financial statement balance invariants via `execute_code`.

## Quick Reference
- Fundamental Accounting Equation: `Assets = Liabilities + Equity + (Revenue - Expenses)`.
- Transaction Balance Invariant: `SUM(debit) == SUM(kredit)` for every journal entry transaction.
- Normal Balance Mapping:
  - Assets & Expenses: Increased by Debit (+), Decreased by Credit (-).
  - Liabilities, Equity, Revenue: Increased by Credit (+), Decreased by Debit (-).
- Immutable Posting Rule: Posted journals are NEVER edited or deleted; errors are corrected exclusively via signed Reversal Journals.
- Hard Closing Rule: Locked fiscal periods reject all insert, update, or back-dating attempts.

## Procedure

1. **Enforce Database Invariants at Schema Level:**
   Always declare constraints on journal line tables (`jurnal_baris`):
   ```sql
   CONSTRAINT cek_bukan_negatif CHECK (debit >= 0 AND kredit >= 0),
   CONSTRAINT cek_sisi_tunggal CHECK ((debit > 0 AND kredit = 0) OR (kredit > 0 AND debit = 0))
   ```
   Enforce zero transaction delta using deferrable constraints or transactional stored procedures.

2. **Structure the Hierarchical Chart of Accounts (COA):**
   - 5 Top-Level Classes: 1 = Aset, 2 = Kewajiban, 3 = Ekuitas, 4 = Pendapatan, 5 = Beban.
   - Header Accounts (Parent): Grouping only, never receive posted journal entries (`is_postable = false`).
   - Detail Accounts (Leaf): Accept transactional line postings (`is_postable = true`).

3. **Execute Atomic Journal Posting:**
   - Verify transaction balance: `SUM(debit) - SUM(kredit) == 0`.
   - Verify active fiscal period: Date falls within an `OPEN` accounting period.
   - Assign monotonic sequence number without gaps.
   - Insert journal header and lines in a single ACID transaction block.

4. **Derive Core Financial Statements:**
   - **Trial Balance (Neraca Saldo):** Sum debits and credits across all leaf accounts; verify delta is 0.
   - **Income Statement (Laba Rugi):** `Revenue - COGS - Operational Expenses = Net Income`.
   - **Balance Sheet (Neraca):** Assets on the left, Liabilities + Equity + Net Income on the right. Both sides must balance identically.
   - **Cash Flow Statement (Arus Kas):** Direct or indirect method classifying operating, investing, and financing activities.

5. **Implement Three-Way Matching (P2P) & Invoicing (O2C):**
   - Purchase Orders match Goods Receipts and Vendor Bills before AP authorization.
   - Sales Invoices credit Revenue and debit Accounts Receivable, accompanied by inventory COGS debit and Asset credit.

## References
Load topic-specific architectural reference files on demand using `skill_view` (`name="double-entry-accounting"`, `file_path="references/<file>"`):
- `references/double-entry-invariants.md`: Mathematical conservation laws, schema constraints, and immutable reversal patterns.
- `references/chart-of-accounts.md`: COA 5-class structure, recursive tree traversal, and normal balance rules.
- `references/financial-statements.md`: Exact SQL derivation of Trial Balance, Income Statement, Balance Sheet, and Retained Earnings.
- `references/order-to-cash-procure-to-pay.md`: State machines, Three-Way Matching, and unbilled GRNI liabilities.
- `references/inventory-and-reconciliation.md`: FIFO vs Moving Average valuation, bank reconciliation, and petty cash replenishment.
- `references/business-accounting-advisory.md`: Indonesian business-accounting advisory, official-source checks, and joint resource planning with Si Pintar.

## Pitfalls
- **Floating-Point Drift:** Using `FLOAT` causes cumulative penny mismatches over millions of rows. Always use `NUMERIC(19, 2)` or integer cents.
- **Direct Database Mutations:** Updating an existing posted journal destroys audit trails and invalidates historical tax filings. Always issue a contra/reversal journal.
- **Negative Debits / Negative Credits:** Entering negative numbers to reverse an entry corrupts debit/credit turnover metrics. Use positive values in the opposite column.
- **Back-Dating into Locked Periods:** Allowing transactions into closed fiscal periods shifts historical retained earnings without management awareness.

## Verification
Execute the double-entry accounting self-test via `terminal`:
`python3 /home/ubuntu/otak-koding/10-Rekayasa-ERP-dan-Akuntansi-Sistem/verifikasi_catatan_erp.py`
Exit code 0 verifies only the vault's documentation checks and embedded assertions that the script actually runs. Inspect its output/implementation before claiming runtime accounting behavior; separately run application tests against synthetic transactions for journal balance, reconciliation, constraints, and concurrent posting.
