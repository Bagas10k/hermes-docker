---
name: business-opportunity-scaling
description: Screen business opportunities and apply leverage to scale.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
      - BusinessStrategy
      - OpportunityScreening
      - ScaleLeverage
      - UnitEconomics
      - HormoziNaval
---

# Business Opportunity & Scale Mindset

Evaluate commercial opportunities, calculate unit economics, and architect leverage mechanisms (Labor, Capital, Media, Code/Technology) to scale operations without linear founder time commitment. Based on Naval Ravikant's leverage stack and Alex Hormozi's scale invariance frameworks.

## When to Use
- User asks to "analisis peluang bisnis", "mindset scaling bisnis", or "scale up usaha".
- Evaluating new venture viability, pricing power, and distribution moats.
- Diagnosing bottlenecks where founder hours scale 1:1 with revenue instead of output compounding.

## Prerequisites
- Basic financial metrics: CAC (Customer Acquisition Cost), LTV (Lifetime Value), Gross Margin, and Payback Period.
- Target market understanding and operational delivery model.

## How to Run
Evaluate venture hypotheses or run quantitative projections through Hermes tools:
- Analyze model assumptions with `execute_code`.
- Document business teardowns in `BUKU_CATATAN/` or evaluate unit margins.

## Quick Reference
- **The 4 Forms of Leverage:**
  1. *Labor:* Other people's time (permission-dependent, coordination overhead).
  2. *Capital:* Other people's money / reinvested cash (permission-dependent).
  3. *Media / Content:* Permissionless distribution (recorded once, viewed infinitely).
  4. *Code / Technology:* Zero marginal cost of reproduction (automated software/AI).
- **Golden Unit Metric:** `Payback Period < 6 Months` and `LTV / CAC >= 3:1`.
- **Scale Invariance:** `Contribution Margin = gm * LTV_n - CAC`. Does unit profit hold as volume increases 10x?

## Procedure

1. **Screen the Opportunity (The Naval Screen):**
   - *Scale Economies:* Does widget #10,000 cost less to produce than widget #5?
   - *Zero Marginal Cost:* Is the cost of serving the next customer effectively zero?
   - *Network Effects:* Does user N+1 add intrinsic value to users 1 through N?

2. **Evaluate the Three Leveraged Engines (Hormozi Framework):**
   - *Leveraged Demand:* Can new qualified prospects discover the product without founder hours?
   - *Leveraged Conversion:* Does an automated funnel or standardized sales asset close customers?
   - *Leveraged Delivery:* Can products be fulfilled via code, digital systems, or delegated SOP teams?

3. **Validate Unit Economics & Payback:**
   - Calculate gross margin percentage `(Revenue - COGS) / Revenue`.
   - Ensure cash payback occurs within 6 months to enable capital recycling without debt distress.

4. **Identify and Eliminate Bottlenecks (Theory of Constraints):**
   - Pinpoint the single constraint: Is it Demand, Conversion, or Delivery?
   - Apply the cheapest leverage type (Media or Code first, then Capital or Labor) to unblock the bottleneck.

5. **Institutionalize Systems & Veto Low-Leverage Traps:**
   - Turn manual heroics into repeatable SOPs.
   - Reject high-maintenance, customized service deals that prevent standardized scaling.

## Pitfalls
- **Premature Scaling:** Pouring capital and labor into an unproven product before achieving strong unit economics and organic retention.
- **Selling Time Linearly:** Operating in agency or consulting modes without converting IP into software or productized media.
- **Overestimating Extrapolated LTV:** Relying on distant 3-year churn assumptions instead of actual cash payback in months 1 to 6.

## Verification
Execute quantitative unit economic verification via `execute_code`:
Calculate contribution margin and ensure `Payback <= 6` months with non-linear founder time scaling.
