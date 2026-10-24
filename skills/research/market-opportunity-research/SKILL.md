---
name: market-opportunity-research
description: Use when researching markets or local solution opportunities.
version: 1.1.0
author: Hermes Agent + Bagas Cihuy
license: MIT
metadata:
  hermes:
    tags: [market-research, customer-discovery, competitors, indonesia, go-to-market]
---

# Market Opportunity Research

Use for market entry, company strategy, or converting geographically scattered public data into local need-to-solution opportunities—not merely a competitor news digest. For Bagas, write in concise Indonesian; distinguish an executable service business from an unvalidated universal platform. Record attribution to Bagas when documenting his architecture, without treating outside market claims as his invention.

## When to Use

Use when deciding which market, locality, customer problem, service model, or go-to-market bet deserves testing. Also use when the user wants to turn BPS, Satu Data, maps, search trends, prices, complaints, or other public internet signals into ranked local solution opportunities. Do not use this skill merely to summarize business news without a decision target.

## Procedure

1. **Frame the decision before searching.** State buyer, geography, workflow or need to solve, outcome metric, and what decision the research must change. For local opportunity discovery, lock the unit of analysis as `wilayah × waktu × kelompok × kebutuhan × solusi`; never let province-level evidence silently become a village-level conclusion. If the user has not named a locality, research national/regional signals and label the local conclusion **belum teruji**; ask for the first kabupaten/kota as the next decision, one question at a time.
2. **Map evidence lanes and provenance before interpreting.** Fetch dated primary statistics (BPS, BI, ministries), population/geospatial estimates, lawful facility or business listings, search-interest signals, prices, official competitor capability/pricing pages, existing local alternatives, and readable public user reports. For every dataset record source URL, observation period, update date, geographic resolution, unit, license/terms, collection method, and known coverage bias. Load `agent-reach` for internet and platform routing, run its doctor for multi-backend social channels, and follow its topical references. Use `grounded-citations` for a source ledger while retrieving, inline citations in the report, and mechanical citation verification. A search result is discovery, not a read page; a page being public does not by itself grant unrestricted scraping or commercial reuse.
3. **Separate voices.** Quote or paraphrase user complaints only from a readable first-person post, review, issue, interview, or observed workflow; vendor posts about customers being overwhelmed are *vendor positioning*, not customer testimony. If authenticated social channels, comments, or scraping are inaccessible, use other readable channels and report the coverage gap; never call snippets a representative social sample.
4. **Model need and supply separately before scoring opportunity.** Infer the chain `group → problem → barrier → current alternatives → service gap → candidate solutions`. Distinguish stated demand, observed behavior, service-provider data, and modeled estimates; triangulate them instead of pooling them as interchangeable rows. Measure effective supply as `count × capacity × quality × operating-hours × affordability × accessibility`, not raw competitor count. Then bound the market: separate all enterprises, reachable prospects, buyers able to pay, and the actual payer when beneficiaries cannot pay directly. Do not convert a national UMKM count, QRIS merchants, search interest, or a manager survey into TAM or conversion rate. Distinguish IMK (manufacturing subset) from all UMKM. Quote sample/population and publication date with every statistic.
5. **Compare alternatives at job level & evaluate OaaS.** Capture actual public prices with billing period, seats, included messages, setup fees, third-party channel/model charges, and date; mark missing terms unknown. In an era where AI commoditizes code, do not default to building traditional multi-page SaaS dashboards with high UI adoption friction. Evaluate Outcome-as-a-Service (OaaS) where the product is delivered headlessly as completed operational outcomes (via WhatsApp/email) under a monthly SLA retainer. Compare the customer's current manual process, deterministic forms/workflows, agency service, and incumbent software before recommending custom AI. For villages, inspect existing official systems and sensitive-data/approval obligations before proposing a new record system.
6. **Score transparently, then forecast as scenarios.** Keep the opportunity score deterministic and inspectable: combine need, effective supply gap, ability or mechanism to fund, access, feasibility, and durability; multiply by an evidence-confidence term derived from source quality, recency, geographic fit, coverage, and cross-source agreement; subtract explicit risk penalties. Treat initial weights and thresholds as hypotheses, preserve the feature values and source lineage behind every score, and run sensitivity checks so small weight changes do not masquerade as certainty. Give baseline/upside/downside mechanisms, observable triggers, disconfirming evidence, and a reversible first bet. Do not claim replacing an entire office role when only bounded tasks have been tested; retain a named human owner for payments, official documents, external communications, and sensitive data.
7. **Design the validation gate without pretending desk data proves purchase.** Internet data may discover and rank opportunities without a new survey, but require a small behavioral test before capital-intensive rollout: a transparent landing page, opt-in waiting list, refundable deposit, bounded WhatsApp order flow, partner-store pilot, or geographic ad test. Where interviews add positive value, ask about the last actual failed transaction rather than opinions. Predeclare the prediction, control or comparator, success threshold, and kill/pivot criterion; measure paid conversion, repeat use, contribution margin, exception rate, support cost, and median/p95 completion time. Label all thresholds, prices, and demand estimates as hypotheses until measured.
8. **Deliver a decision brief.** Lead with recommendation and confidence, then evidence, effective supply gap, target group, payer, candidate solution set, unit-economics assumptions, short pilot sequence, risks, and one next decision. Include both supporting and disconfirming evidence and expose the largest missing variable. Put the detailed source-backed research in an artifact when scope is broad; never state field validation, purchase intent, or social scraping occurred if only desk research did.

For the reusable local-data pipeline, source roles, scoring skeleton, and output contract, read `references/local-needs-opportunity-intelligence.md`.

## Pitfalls

- Verify competitor marketing claims as claims *by that vendor*, not measured performance; otherwise you turn sales copy into evidence.
- Do not conflate a closed bug report with a current widespread product failure; its value is a failure mode and a question to test.
- Preserve geographic uncertainty: national digital-readiness statistics cannot rank a specific village's purchasing power or connectivity.
- Never equate online visibility with population need: digitally quiet, elderly, poor-connectivity, and offline groups are systematically under-observed.
- Never treat Google Trends-style normalized interest as absolute demand, transaction volume, or willingness to pay; relative search signals can rank hypotheses only when triangulated.
- Do not count map points as sufficient supply; capacity, opening hours, affordability, quality, and travel friction determine whether a service is actually available.
- Keep aggregate-area analysis separate from individual profiling and obey dataset/platform licenses plus data-protection duties; joining harmless datasets can create sensitive re-identification risk.
- Count buyer-paid outcomes, not dashboard screens, chat messages, or unverified hours saved; setup/support can erase apparent automation savings.
- Keep quotations and statistics tied to retrieved URLs via the citation ledger; a manually assembled source list is easy to misnumber.
- Do not rush to code prototypes before fully stress-testing risk scenarios and operational workflows; premature prototyping wastes time compared to rigorous conceptual and risk validation.
- Do not propose multi-page web dashboards when the customer workflow can be completely served headlessly via WhatsApp, email, or shared drives; UI friction kills adoption faster than missing features.
