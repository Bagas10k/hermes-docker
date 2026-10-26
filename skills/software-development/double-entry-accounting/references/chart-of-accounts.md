# Chart of Accounts (COA) & Normal Balance Types

## 1. Five Fundamental Account Classes
The General Ledger is partitioned into five canonical classes:

| Class Code | Account Class | Indonesian | Normal Balance | Statement |
|---|---|---|---|---|
| `1xxxx` | Assets | Aset / Aktiva | **Debit** | Balance Sheet (Neraca) |
| `2xxxx` | Liabilities | Kewajiban / Hutang | **Credit** | Balance Sheet (Neraca) |
| `3xxxx` | Equity | Ekuitas / Modal | **Credit** | Balance Sheet (Neraca) |
| `4xxxx` | Revenue | Pendapatan / Penjualan | **Credit** | Income Statement (Laba Rugi) |
| `5xxxx` | Expenses / COGS | Beban / HPP | **Debit** | Income Statement (Laba Rugi) |

## 2. Normal Balance Arithmetic
An account balance is calculated based on its natural side:
- **Debit-Normal Accounts (Assets, Expenses):**
  $$\text{Ending Balance} = \text{Beginning Balance} + \sum \text{Debit} - \sum \text{Credit}$$
- **Credit-Normal Accounts (Liabilities, Equity, Revenue):**
  $$\text{Ending Balance} = \text{Beginning Balance} + \sum \text{Credit} - \sum \text{Debit}$$

Contra accounts invert normal behavior (e.g. Akumulasi Penyusutan is Asset class with Credit normal balance; Retur Penjualan is Revenue class with Debit normal balance).

## 3. Hierarchical Account Tree Structure
Accounts must form a strict tree hierarchy (Adjacency List or Nested Set):
```sql
CREATE TABLE akun (
    id            BIGSERIAL PRIMARY KEY,
    id_tenant     UUID NOT NULL,
    id_induk      BIGINT REFERENCES akun(id),
    kode_akun     VARCHAR(32) NOT NULL,
    nama_akun     VARCHAR(128) NOT NULL,
    klasifikasi   VARCHAR(16) NOT NULL CHECK (klasifikasi IN ('ASET', 'KEWAJIBAN', 'EKUITAS', 'PENDAPATAN', 'BEBAN')),
    saldo_normal  VARCHAR(8) NOT NULL CHECK (saldo_normal IN ('DEBIT', 'KREDIT')),
    is_postable   BOOLEAN NOT NULL DEFAULT true,
    is_aktif      BOOLEAN NOT NULL DEFAULT true,
    CONSTRAINT uq_kode_akun UNIQUE (id_tenant, kode_akun)
);
```

### Hierarchical Rules:
- **Header Accounts (`is_postable = false`):** Summarize sub-accounts (e.g., `11000 - Kas & Bank`). Never allowed as `id_akun` in `jurnal_baris`.
- **Detail Accounts (`is_postable = true`):** Leaf nodes that accept journal line postings (e.g., `11010 - Kas Kecil`, `11020 - Bank BCA`).
- **Cycle Prevention:** Triggers or CTE queries must assert that an account's parent pointer never forms a circular reference.
