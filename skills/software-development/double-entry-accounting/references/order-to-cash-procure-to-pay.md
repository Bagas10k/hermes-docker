# Order-to-Cash (O2C) & Procure-to-Pay (P2P) Workflows

## 1. Procure-to-Pay (P2P) Flow & Three-Way Matching

```text
[Purchase Order (PO)] ──> [Goods Receipt (GRN)] ──> [Vendor Bill (AP)] ──> [Payment]
```

### Journal Steps in P2P:
1. **Purchase Order Issued:** Non-financial commitment. No journal generated.
2. **Goods Receipt (GRN / Surat Jalan Masuk):**
   - Inventory Asset debited when physical custody transfers.
   - Unbilled AP clearing account credited (Goods Received Not Invoiced / GRNI):
     ```text
     Debit:  14000 - Persediaan Barang Dagang
     Credit: 21100 - Hutang Belum Ditagih (Unbilled GRN)
     ```
3. **Vendor Bill Received (Faktur Pembelian):**
   - Three-Way Match verified against PO price and GRN quantity.
   - Clears GRNI and recognizes final Accounts Payable:
     ```text
     Debit:  21100 - Hutang Belum Ditagih (Unbilled GRN)
     Debit:  11800 - PPN Masukan (VAT In)
     Credit: 21000 - Hutang Usaha (Accounts Payable)
     ```
4. **Disbursement (Pembayaran Hutang):**
     ```text
     Debit:  21000 - Hutang Usaha (Accounts Payable)
     Credit: 11020 - Kas / Bank
     ```

## 2. Order-to-Cash (O2C) Flow

```text
[Sales Order (SO)] ──> [Delivery Order (DO)] ──> [Sales Invoice (AR)] ──> [Receipt]
```

### Journal Steps in O2C:
1. **Sales Order Approved:** Non-financial commitment. Reserves inventory allocation.
2. **Delivery Order Dispatched (Surat Jalan Keluar):**
   - Inventory reduced; Cost of Goods Sold recognized:
     ```text
     Debit:  51000 - Harga Pokok Penjualan (COGS)
     Credit: 14000 - Persediaan Barang Dagang
     ```
3. **Sales Invoice Issued (Faktur Penjualan):**
   - Revenue and tax liability recognized; receivable created:
     ```text
     Debit:  12000 - Piutang Usaha (Accounts Receivable)
     Credit: 41000 - Pendapatan Penjualan (Revenue)
     Credit: 22100 - PPN Keluaran (VAT Out)
     ```
4. **Customer Receipt (Penerimaan Piutang):**
     ```text
     Debit:  11020 - Bank BCA
     Credit: 12000 - Piutang Usaha (Accounts Receivable)
     ```

## 3. Segregation of Duties (SOD) Matrix
Internal controls enforce separation across execution, recording, custody, and authorization:
- `O` (Otorisasi): Approve PO, approve credit limits, approve journal reversals.
- `P` (Pencatatan): Create invoice, draft manual journal entries.
- `A` (Aset/Fisik): Warehouse dispatch, receiving physical goods, petty cash custody.
- **Rule:** A single employee cannot possess both `O` and `P` for the same document cycle.
