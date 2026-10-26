# Inventory Valuation, Bank Reconciliation, and Cash Controls

## 1. Inventory Valuation (FIFO vs Moving Average)

### Moving Average (Rata-Rata Bergerak):
Recalculates unit cost dynamically upon every purchase receipt ($GRN$):
$$\text{Cost Baru} = \frac{(\text{Qty Lama} \times \text{Cost Lama}) + (\text{Qty Masuk} \times \text{Harga Beli})}{\text{Qty Lama} + \text{Qty Masuk}}$$
COGS on dispatch uses the current average cost.

### FIFO (First-In, First-Out):
Maintains discrete cost layers in queue:
```sql
CREATE TABLE persediaan_lapisan (
    id          BIGSERIAL PRIMARY KEY,
    id_barang   BIGINT NOT NULL,
    qty_sisa    NUMERIC(15,4) NOT NULL,
    harga_beli  NUMERIC(19,2) NOT NULL,
    masuk_pada  TIMESTAMPTZ NOT NULL
);
```
Dispatches consume oldest layers first. Remaining balance on Balance Sheet reflects most recent acquisition costs.

### Inventory Ledger (Kartu Stok) Invariant:
For every SKU and location:
$$\text{Beginning Qty} + \sum \text{Qty In} - \sum \text{Qty Out} = \text{Ending Qty}$$
Stock cards track both physical quantity and financial value in parallel.

## 2. Bank Reconciliation (Rekonsiliasi Bank)
Reconciles General Ledger Bank balance with external Bank Statement:
```text
GL Bank Balance
  + Uncredited Deposits (Setoran dalam perjalanan)
  - Unpresented Checks / Outstanding Payments
  + Direct Bank Credits (Bunga jasa giro)
  - Direct Bank Debits (Biaya administrasi bank)
  = Cleared Bank Statement Balance
```
- Auto-matching engine matches by amount, date window ($\pm 3$ days), and reference/cheque number.
- Unmatched items generate discrepancy tickets or adjustment journals.

## 3. Petty Cash Imprest System (Kas Kecil)
1. **Fixed Float / Pagu Tetap:** Petty cash account maintains a constant general ledger balance ($Pagu$).
2. **Voucher Issuance:** Physical cash handed out against stamped receipts/vouchers; general ledger is untouched.
3. **Atomic Replenishment (Pengisian Kembali):**
   - Vouchers audited and summarized.
   - Bank checks issued to reimburse exact total of spent vouchers.
   - Expenses debited directly upon replenishment:
     ```text
     Debit:  52100 - Beban ATK & Perlengkapan
     Debit:  52200 - Beban Jamuan & Konsumsi
     Credit: 11020 - Kas Besar / Bank
     ```
   - Account `11010 - Kas Kecil` remains constant unless permanent float is adjusted.
