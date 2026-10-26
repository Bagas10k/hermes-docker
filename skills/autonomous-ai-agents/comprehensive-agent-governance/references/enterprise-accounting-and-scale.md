# Enterprise Accounting Invariants & High-Leverage Business Scaling

## 1. Enterprise Double-Entry Accounting Invariants
- **Conservation Invariant:** $\sum \text{Debit} == \sum \text{Credit}$ enforced at database schema level. Floating point types are strictly banned (`NUMERIC(19, 2)` or integer cents mandatory). Negative debits/credits prohibited.
- **Immutable General Ledger:** Posted journals are write-once, append-only. Corrections are executed exclusively through paired, signed Reversal Journals ($J_{orig} + J_{rev} = 0$).
- **Hierarchical COA 5 Classes:** Assets (1), Liabilities (2), Equity (3), Revenue (4), Expenses (5). Header grouping accounts forbid direct line posting.
- **Statement Triad:** Trial Balance verifies zero delta. Income Statement derives net income. Balance Sheet enforces $\text{Assets} = \text{Liabilities} + \text{Equity} + \text{Net Income}$.
- **P2P & O2C Cycles:** Three-Way Matching (PO, GRN/Surat Jalan, Supplier Invoice) with unbilled GRNI clearing accounts. Petty cash operates under the fixed-float Imprest system.

## 2. High-Leverage Business Opportunity & Scale Mindset
- **The 4 Leverage Stack (Naval Ravikant):**
  1. *Labor:* Other people's time (coordination overhead).
  2. *Capital:* Reinvested cash / external funds.
  3. *Media / Content:* Permissionless distribution (reproduced at zero marginal cost).
  4. *Code / AI:* Software executing repeatedly with zero marginal cost of reproduction.
- **The 3 Engines of Scale (Alex Hormozi):** Leveraged Demand (leads arrive without founder hours), Leveraged Conversion (automated funnel / irresistible offer closes sales), Leveraged Delivery (digital systems and SOP teams fulfill without founder bottleneck).
- **Unit Economics Rule:** Cash payback period $< 6$ months to enable continuous self-funded growth without debt distress. LTV/CAC ratio $\ge 3:1$.
