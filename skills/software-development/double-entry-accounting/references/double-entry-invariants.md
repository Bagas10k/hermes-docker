# Double-Entry Invariants & Immutable Ledger Architecture

## 1. Mathematical Conservation Invariant
Double-entry bookkeeping is an error-detection and conservation system. For every transaction $t$ and aggregate period $p$:

$$\sum_{i \in t} \text{debit}_i = \sum_{i \in t} \text{kredit}_i \qquad \forall t$$
$$\sum_{i \in p} \text{debit}_i = \sum_{i \in p} \text{kredit}_i \qquad \forall p$$

Every journal entry must strictly balance to zero delta before commit:
`SUM(debit) - SUM(kredit) == 0`.

## 2. Relational Schema Discipline
```sql
CREATE TABLE jurnal (
    id            BIGSERIAL PRIMARY KEY,
    id_tenant     UUID NOT NULL,
    nomor_bukti   TEXT NOT NULL,
    tanggal       DATE NOT NULL,
    id_periode    BIGINT NOT NULL REFERENCES periode_akuntansi(id),
    keterangan    TEXT NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('DRAFT', 'POSTED', 'REVERSED')),
    dibuat_pada   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_nomor_bukti UNIQUE (id_tenant, nomor_bukti)
);

CREATE TABLE jurnal_baris (
    id            BIGSERIAL PRIMARY KEY,
    id_jurnal     BIGINT NOT NULL REFERENCES jurnal(id) ON DELETE RESTRICT,
    id_akun       BIGINT NOT NULL REFERENCES akun(id),
    debit         NUMERIC(19,2) NOT NULL DEFAULT 0,
    kredit        NUMERIC(19,2) NOT NULL DEFAULT 0,
    memo          TEXT,
    CONSTRAINT cek_bukan_negatif CHECK (debit >= 0 AND kredit >= 0),
    CONSTRAINT cek_sisi_tunggal CHECK (
        (debit > 0 AND kredit = 0) OR (kredit > 0 AND debit = 0)
    )
);
```

### Critical Database Constraints:
- `NUMERIC(19,2)`: Prevents IEEE-754 floating-point rounding errors. Float/Double is strictly prohibited.
- `cek_bukan_negatif`: Prohibits negative debits/credits. Reversals must be positive entries on the opposing side.
- `cek_sisi_tunggal`: Prohibits both debit and credit being non-zero on the same line item.

## 3. Immutable Journal & Reversal Pattern
Posted journals are append-only. `UPDATE` and `DELETE` queries on posted lines are blocked by triggers or database permissions.

### Reversal Mechanism:
When an erroneous journal $J_1$ must be corrected:
1. Mark $J_1$ status as `REVERSED`.
2. Insert reversal journal $J_{rev}$ containing identical amounts swapped:
   - Original debit in $J_1$ becomes credit in $J_{rev}$.
   - Original credit in $J_1$ becomes debit in $J_{rev}$.
3. Net accounting impact of $J_1 + J_{rev} = 0$.
4. Insert corrected journal $J_2$ with valid accounts and amounts.
5. All 3 documents remain visible in audit trails with cross-referenced document IDs.

## 4. Idempotency Key Pattern
To prevent double-posting from retried network requests, enforce unique idempotency keys per transactional intent:
```sql
ALTER TABLE jurnal ADD COLUMN idempotency_key VARCHAR(64) UNIQUE;
```
If an insert with the same key arrives, return the existing journal reference rather than creating a duplicate financial entry.
