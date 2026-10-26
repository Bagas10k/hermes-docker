# Financial Statements Derivation from General Ledger

## 1. The Core Accounting Identity
Financial statements are mathematical transformations of journal line balances:

$$\text{Assets} = \text{Liabilities} + \text{Equity} + (\text{Revenue} - \text{Expenses})$$
$$\text{Assets} = \text{Liabilities} + \text{Ending Equity}$$

## 2. Trial Balance (Neraca Saldo)
The verification gate before financial reporting. Computes ending balance per leaf account across an accounting period:

```sql
SELECT 
    a.kode_akun,
    a.nama_akun,
    a.klasifikasi,
    a.saldo_normal,
    SUM(jb.debit) AS total_debit,
    SUM(jb.kredit) AS total_kredit,
    CASE 
        WHEN a.saldo_normal = 'DEBIT' THEN SUM(jb.debit) - SUM(jb.kredit)
        ELSE 0 
    END AS saldo_debit,
    CASE 
        WHEN a.saldo_normal = 'KREDIT' THEN SUM(jb.kredit) - SUM(jb.debit)
        ELSE 0 
    END AS saldo_kredit
FROM akun a
JOIN jurnal_baris jb ON a.id = jb.id_akun
JOIN jurnal j ON j.id = jb.id_jurnal
WHERE j.status = 'POSTED' AND j.tanggal BETWEEN :start_date AND :end_date
GROUP BY a.id, a.kode_akun, a.nama_akun, a.klasifikasi, a.saldo_normal;
```
**Assertion:** `SUM(saldo_debit) == SUM(saldo_kredit)`.

## 3. Income Statement (Laba Rugi)
Measures operational performance over period $[t_0, t_1]$:
- **Revenue (Pendapatan):** Class 4 accounts (`SUM(kredit) - SUM(debit)`).
- **Cost of Goods Sold (HPP):** Sub-class 51 accounts (`SUM(debit) - SUM(kredit)`).
- **Gross Profit (Laba Kotor):** $\text{Revenue} - \text{COGS}$.
- **Operating Expenses (Beban Operasional):** Sub-class 52+ accounts (`SUM(debit) - SUM(kredit)`).
- **Operating Profit (Laba Operasional):** $\text{Gross Profit} - \text{Operating Expenses}$.
- **Net Income (Laba Bersih):** $\text{Operating Profit} + \text{Other Income} - \text{Tax}$.

## 4. Balance Sheet (Neraca)
Point-in-time financial position at date $t$:
- **Assets (Aktiva):** Class 1 accounts (`SUM(debit) - SUM(kredit)`).
- **Liabilities (Kewajiban):** Class 2 accounts (`SUM(kredit) - SUM(debit)`).
- **Beginning Equity (Modal Awal):** Class 3 accounts (`SUM(kredit) - SUM(debit)`).
- **Current Net Income (Laba Berjalan):** Transferred from Income Statement for the current fiscal year.
- **Ending Equity:** $\text{Beginning Equity} + \text{Current Net Income}$.

**Golden Equation Assertion:**
$$\text{Total Assets} - (\text{Total Liabilities} + \text{Ending Equity}) == 0.00$$

## 5. Period Closing & Locking (Tutup Buku)
At fiscal year-end:
1. Lock all journals in closed period (`status = 'LOCKED'`). Reject any back-dating.
2. Temporary accounts (Revenue & Expense) are zeroed out via a Closing Journal into `Ikhtisar Laba Rugi`.
3. Balance of `Ikhtisar Laba Rugi` transferred to `32000 - Laba Ditahan (Retained Earnings)`.
4. Balance sheet accounts carry their ending balances as beginning balances of the new fiscal period.
