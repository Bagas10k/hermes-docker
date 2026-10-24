# Local Needs-to-Opportunity Intelligence

Use this reference when the task is to discover which service or business solution fits a target area from existing public internet data, without starting from a new survey.

## 1. Lock the analysis grain

Represent every claim as:

```text
geography × observation period × population group × unmet need × candidate solution
```

Keep the source resolution alongside the value. Aggregate only toward a coarser geography; do not disaggregate province or district statistics into village estimates unless an explicit model supplies uncertainty bounds and validation.

## 2. Build an evidence manifest

For each source capture:

```yaml
source_url:
provider:
retrieved_at:
observation_period:
geography_level:
unit:
collection_method:
license_or_terms:
update_frequency:
coverage_bias:
```

Useful source roles in Indonesia include:

- **BPS Web API and official tables:** demographic, socioeconomic, publication, and regional statistics. API access may require a token; inspect metadata and table definition before joining values.
- **PODES/SILASTIK:** village infrastructure, facilities, transport, economic and social conditions. Check access price, permitted use, microdata disclosure rules, year, and variable dictionary before planning around it.
- **Satu Data Indonesia and ministry/local open-data portals:** cross-sector datasets. Normalize reference codes, metadata, and update periods before integration.
- **Bank Indonesia regional statistics:** provincial/regional economic, financial, banking, price, and payment context; never force a province indicator into a neighborhood claim.
- **OpenStreetMap:** roads, facilities, and points of interest under ODbL. Provide attribution, review database-share-alike implications, and do not assume map completeness equals nonexistence.
- **WorldPop or other gridded population models:** catchment-area population estimates. Preserve model vintage, census/projection dependency, resolution, and uncertainty; modeled grids do not replace a census.
- **Google Trends:** anonymized, sampled, normalized search interest, usually scaled 0–100 for a selected time/place. Use as a relative intent signal only; low-volume terms may show zero or noise.
- **Readable public complaints, reviews, news, prices, vacancies, weather, procurement, and service notices:** use only when terms allow the intended access and reuse; separate first-person reports from vendor or journalist characterization.

A public URL is not automatic permission for bulk scraping, redistribution, or commercial reuse.

## 3. Normalize before inference

1. Map place names to one authoritative area code and boundary vintage.
2. Convert all timestamps to observation periods; keep retrieval time separate.
3. Preserve raw values and units, then create derived normalized features.
4. Deduplicate syndication, reposts, identical complaints, and repeated map records.
5. Record missingness explicitly; absence of an online record is not proof of absence.
6. Aggregate or suppress sparse cells that could identify individuals.

## 4. Construct the causal opportunity chain

```text
population group
→ experienced problem
→ barrier or mechanism
→ current alternatives
→ effective service gap
→ candidate solutions
→ payer and delivery model
```

Do not jump from correlation to intervention. A rise in searches for medicine may reflect illness, news exposure, fear, or price comparison. State competing hypotheses and identify the cheapest evidence that distinguishes them.

## 5. Estimate demand and effective supply

Demand features may include:

```text
population exposed × need prevalence × severity × recurrence × observed intent
```

Effective supply should reflect usability, not point count:

```text
provider count
× usable capacity
× quality/reliability
× relevant operating hours
× affordability
× physical/digital accessibility
```

Keep both as ranges when inputs are estimates. A high need with no viable payer is a social need, not yet a commercial opportunity; test government, employer, cooperative, insurer, donor, or cross-subsidy models rather than inventing household purchasing power.

## 6. Score with evidence confidence

A reusable structure is:

```text
Opportunity = Confidence × WeightedUtility − RiskPenalty
```

Possible utility features:

- need magnitude and severity;
- effective supply gap;
- funding or willingness-to-pay mechanism;
- geographic and operational accessibility;
- solution feasibility;
- durability rather than transient virality.

Compute confidence from source quality, recency, geographic fit, population coverage, and independent cross-source agreement. Normalize weights to 1.0, retain every feature value and source, and run sensitivity analysis. If plausible weight changes reverse the ranking, report a tie and seek higher-value evidence rather than declaring a winner.

Use an LLM to classify text and propose hypotheses, not to silently invent numeric features or final scores. Deterministic code should calculate the score from stored features.

## 7. Produce a falsifiable opportunity card

```yaml
need:
target_area:
target_group:
observed_problem:
causal_hypotheses:
effective_supply_gap:
candidate_solutions:
payer:
rough_unit_economics:
evidence_for:
evidence_against:
confidence:
largest_unknown:
cheapest_behavioral_test:
success_threshold:
kill_or_pivot_threshold:
source_lineage:
```

Return several solution forms when the need permits them; the job is to solve the need, not force a predetermined storefront, app, or AI product.

## 8. Validate behavior without requiring a survey

Choose the smallest ethical intervention that tests a purchase or usage decision:

- transparent landing page plus opt-in;
- refundable deposit or preorder;
- limited WhatsApp ordering window;
- partner-store or mobile-service pilot;
- geographic ad test tied to a real offer;
- comparison between a pilot catchment and a matched control.

Write predictions before launching. Measure paid conversion, repeat use, contribution margin, cancellation/refund rate, unmet exceptions, support hours, and median/p95 completion time. Do not use fake scarcity, deceptive checkout, or collect unnecessary personal data.

## 9. Privacy, fairness, and licensing gate

- Prefer aggregate area-level data and data minimization.
- Do not profile identifiable people or infer sensitive traits without a valid legal basis.
- Inspect licenses and platform terms before collection, storage, enrichment, redistribution, or commercial use.
- Test whether combining datasets makes individuals or vulnerable groups identifiable.
- Report digital-coverage bias and avoid penalizing areas whose needs are underrepresented online.
- Preserve attribution and share-alike duties where applicable.

## 10. Minimum decision statement

Conclude with one of:

- **Supported for behavioral pilot:** multiple independent signals, plausible supply gap, and a testable payer.
- **Promising but under-evidenced:** apparent need or gap, but one load-bearing variable is missing.
- **Not supported:** effective supply is adequate, need is transient/weak, economics fail, or evidence is geographically mismatched.

Never translate desk evidence into “this business will succeed.” The strongest valid conclusion before a behavioral pilot is a ranked, evidence-backed opportunity hypothesis.