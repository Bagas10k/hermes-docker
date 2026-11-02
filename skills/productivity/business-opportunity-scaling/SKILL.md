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
- Identify which financial metrics are measured and which are unknown: CAC, realized cohort contribution, retention, margin and cash payback. Missing metrics are validation tasks, not permission to invent benchmarks.
- Record the founder's selected first buyer, first paid workflow, delivery model and budget authority separately from recommendations.

## How to Run
Evaluate venture hypotheses or run quantitative projections through Hermes tools:
- Analyze model assumptions with `execute_code`.
- Save the working assumptions, model and evidence in the task workspace; publish to a knowledge vault only when that destination is authorized.
- For a complete company operating manual, use `references/company-operating-manuals.md` for chapter sequencing, cross-checks and a compact delivery contract.

## Quick Reference
- **The 4 Forms of Leverage:**
  1. *Labor:* Other people's time (permission-dependent, coordination overhead).
  2. *Capital:* Other people's money / reinvested cash (permission-dependent).
  3. *Media / Content:* Permissionless distribution (recorded once, viewed infinitely).
  4. *Code / Technology:* Low reproduction effort, but AI inference, storage, payment fees, support and review can remain variable costs.
- **Candidate screening heuristics, not universal benchmarks:** consider cash payback within 6 months and LTV/CAC around 3 or more only when the segment, cohort method and cash constraints justify them. Do not present these as verified industry requirements.
- **Scale test:** `unit contribution = net revenue − directly attributable variable costs`; assess acquisition cost separately. Does contribution and human workload remain viable as volume increases? Do not mix gross margin, contribution and profit.

## Procedure

1. **Screen the Opportunity (The Naval Screen):**
   - *Scale Economies:* Does widget #10,000 cost less to produce than widget #5?
   - *Marginal Cost:* What inference, tools, storage, channel fees, retries and human review are added by the next customer? Owning the product does not imply a 100% margin.
   - *Network Effects:* Does user N+1 add intrinsic value to users 1 through N?

2. **Evaluate the Three Leveraged Engines (Hormozi Framework):**
   - *Leveraged Demand:* Can new qualified prospects discover the product without founder hours?
   - *Leveraged Conversion:* Does an automated funnel or standardized sales asset close customers?
   - *Leveraged Delivery:* Can products be fulfilled via code, digital systems, or delegated SOP teams?

3. **Validate Unit Economics & Payback:**
   - Calculate gross margin percentage `(Revenue - COGS) / Revenue`.
   - Calculate cash payback against actual runway and collection timing; choose and label a segment-appropriate target rather than assuming a universal threshold.

4. **Identify and Eliminate Bottlenecks (Theory of Constraints):**
   - Pinpoint the single constraint: Is it Demand, Conversion, or Delivery?
   - Apply the cheapest leverage type (Media or Code first, then Capital or Labor) to unblock the bottleneck.

5. **Institutionalize Systems & Veto Low-Leverage Traps:**
   - Turn manual heroics into repeatable SOPs.
   - Reject high-maintenance, customized service deals that prevent standardized scaling.

## Founder decisions and operating-manual delivery

- For this user, prioritize evidence of a credible offer, qualified demand, willingness to pay and repeat value before recommending more capital or building speculative features. A flexible budget is not authorization for unlimited spending.
- Preserve the founder's first buyer and first paid role across positioning, product scope, outreach, examples, pricing discussion, forecasts and onboarding. Treat secondary segments as secondary; do not silently substitute an easier niche.
- When an AI builder already exists, focus the company plan on operating and selling it. Inspect its capabilities before promising workflow automation, exports, integrations or production controls; do not rebuild the product merely to produce activity.
- Distinguish automated routine work from authority to approve documents, disclose data, sign contracts or spend money. Describe review gates explicitly instead of selling 'fully automatic' as no setup, no errors or no human accountability.
- Package a company operating manual as one modular master with embedded templates and one concise AI onboarding brief. Honor the selected native format; keep calculations, code, source ledgers and QC files optional rather than multiplying primary documents.

## Capacity and obligation gates

- Reconcile forecasted human support and onboarding hours against the founder's actual capacity before calling a growth scenario operationally feasible. Keep uncapped scenarios as labelled stress tests; do not invent unbudgeted contractors or silently revise the forecast to make it pass.
- Specify refund formulas, included-credit expiry, top-up expiry, cancellation treatment, and unused-credit obligations separately. Treat unused prepaid balances as an accounting/review item rather than automatically free cash.
- Distinguish a prudential tax cash reserve from a statutory tax rate. Do not replace an explicitly hypothetical reserve with a reviewer-suggested rate before entity eligibility and current rules are confirmed.
- Check QC findings against source/model values before applying them. Recompute rounding, first cash-shortfall month versus minimum-cash month, and exact table scope programmatically; reviewer self-reports can be wrong.

## Pitfalls
- **Premature Scaling:** Pouring capital and labor into an unproven product before achieving strong unit economics and organic retention.
- **Selling Time Linearly:** Operating in agency or consulting modes without converting IP into software or productized media.
- **Overestimating Extrapolated LTV:** Relying on distant 3-year churn assumptions instead of actual cash payback in months 1 to 6.

## Verification
Execute quantitative unit economic verification via `execute_code`:
Reconcile monthly customer movements, revenue, direct costs, operating surplus, founder cash draws, reserves and closing cash in code. Report the first cash-shortfall month separately from the minimum balance. Calculate payback and capacity against explicitly labelled targets; correct arithmetic does not validate demand, pricing, churn or founder-time assumptions.
