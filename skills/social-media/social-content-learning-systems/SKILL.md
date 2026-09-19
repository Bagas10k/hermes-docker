---
name: social-content-learning-systems
description: Use when building social content learning systems.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [social-media, analytics, content-learning, recommendations, cross-channel, qc]
---

# Social Content Learning Systems

Build evidence-driven systems that learn from content performance across social platforms without confusing correlation with causation.

## Standing delivery rules

- Explain a complex content-learning pipeline visually when prose becomes hard to follow. Produce a clean diagram or infographic file showing inputs, gates, publication, measurements, feedback, and failure paths; accompany it with a short plain-language summary rather than another long explanation.
- Use wording understandable to non-specialists. Translate technical terms at first use: for example, “content fingerprint” before “SHA-256 manifest,” and “how quickly views arrive” before “view velocity.”
- Keep platform-specific caption treatment separate from shared creative identity: visual, topic, headline, slide order/count, and intended publication window may be shared while captions adapt to platform behavior.

## Procedure

### 1. Define the causal model before collecting metrics

Model outcome as:

`performance = f(visual, subject fame, topic, writing hook, publication time, freshness, platform mechanics, audio) + noise`

Write the expected direction of each factor before examining results. Never attribute a high-performing post to its visual when it also changed topic, timing, and audio.

### 2. Record a pre-publication manifest

For each post, persist:

- canonical content ID and platform IDs;
- visual type, featured subject, topic class, headline/hook class, caption length;
- intended publication window and actual timestamp;
- QC score and predicted outcome;
- hashes of ordered media assets when cross-channel identity matters.

Use a deterministic content hash to detect accidental changes between channels. Allow deliberate platform-only exceptions only through an explicit, auditable override with a reason; never weaken the default gate silently.

### 3. Run pre-publication QC

Score at least these dimensions:

- subject/topic correctness;
- iconic recognition and stopping power;
- resolution, sharpness, and watermark status;
- composition, face safety, and text-safe zones;
- subject clarity;
- cross-channel parity where required.

Treat wrong subject, visible watermark, severe blur, face obstruction, and mismatched channel assets as vetoes even if the aggregate score passes.

### 4. Publish and preserve platform adaptations

- Reuse the exact rendered media package when visual parity is required.
- Keep the canonical topic and headline stable.
- Adapt only the allowed fields, such as shortening TikTok captions while retaining a fuller Instagram caption.
- Track publication skew; distinguish “same workflow window” from impossible exact simultaneity caused by upload/API processing.
- Include all targeted channels in dispatch notifications immediately upon submission. When web automation or delayed platform processing yields a 'SUBMITTED' or pending status before a permanent permalink is minted, surface the channel profile link with an explicit status note; omitting the channel from the alert falsely signals to operators that publication was skipped.
- Asynchronously reconcile permalinks and sync status when background telemetry scrapers detect the live post ID, recalculating cross-channel timing skew against the ledger.

### 5. Collect staged observations

Capture comparable snapshots at 30 minutes, 2 hours, 24 hours, and 72 hours. Store raw counters and normalized rates.

- TikTok: views, view velocity, likes, comments, shares, completion/retention when available.
- Instagram: reach, impressions, likes, comments, shares, saves, profile visits, and followers gained when available.

For Instagram, weight saves and shares more than likes because they better signal durable utility and distribution intent.

### 6. Analyze four dimensions separately

1. **Visual:** match action, celebration, portrait, reaction, iconic player, crop/framing quality.
2. **Topic:** team/player popularity, match result, controversy, record, transfer, national team relevance.
3. **Writing:** emotional exclamation, dramatic scoreline, direct fact, question/challenge, caption length.
4. **Time:** day, WIB slot, initial velocity, and time-to-peak.

Compare like with like. Use normalized rates and minimum sample thresholds; raw views alone reward older posts and larger initial distribution.

### 7. Diagnose gaps instead of merely ranking winners

Use these interpretations as hypotheses to test:

- high reach/views + low engagement: hook attracts attention but substance or CTA is weak;
- low reach/views + high engagement: content resonates with a small audience but distribution, timing, or opening visual is weak;
- strong Instagram + weak TikTok: inspect audio, caption brevity, and TikTok distribution mechanics;
- strong TikTok + weak Instagram: inspect carousel depth, save/share value, and Instagram caption/CTA;
- both weak: re-evaluate subject, topic, visual, and headline together;
- prediction high + result low: reduce model confidence and inspect omitted variables.

### 8. Update cautiously

- Require 5–10 comparable samples before promoting a pattern.
- Change one variable per deliberate experiment.
- Weight recent evidence more heavily, but retain older baselines for drift detection.
- Reserve roughly 20% of slots for exploration so the system does not overfit to the same stars and topics.
- Label findings `EXPERIMENTAL`, `PROMISING`, or `VALIDATED` with sample count and confidence.
- Version every learned rule and revoke it when fresh evidence deteriorates.

### 9. Feed validated rules back into production via dynamic tables

Avoid hardcoding learned rules into static code constants. Maintain an active rules table (`agent_self_learned_rules`):

- Store `rule_id`, `domain` (TOPIC, VISUAL, COPYWRITING, TIMING, PIPELINE, QC_DEFECT_GUARD), `condition_trigger`, `rule_directive`, `action_type` (BOOST, PENALIZE, REQUIRE, FORBID), `weight_delta`, `confidence_score` (Bayesian posterior), `sample_support`, `lift_ratio`, `status` (ACTIVE, EXPERIMENTAL, PRUNED), and `reasoning_audit`.
- Expose a runtime provider function (`getActiveRules(domain)`) called by the gatekeeper, writer, and visual selector on every run.
- Automatically synthesize proactive defect guards from past QC rejection logs (`qc_audits`) so repeated failure modes (e.g. preview disguised as result, text over player face, missing slide facts) are blocked before reaching QC.
- Run autonomous learning cycles in the background (e.g. after telemetry sync) to evaluate rule performance, adjust weights, and prune decayed rules without requiring manual human prompts.

Keep predictions, observations, decisions, and rule changes traceable so a future audit can explain why the system changed.

## Pitfalls

- Do not learn from one viral post; stochastic distribution produces false rules.
- Do not use public “best time to post” articles as ground truth; use them only as priors until account-specific analytics provide evidence.
- Do not let an iconic player override subject correctness; fame cannot compensate for the wrong person or unrelated image.
- Do not judge portrait assets only from the master file; verify thumbnail and final-cover crops because fixed `object-fit: cover` framing can cut off faces.
- Do not equate platform failure with content failure; login expiry, CAPTCHA, DOM changes, and API processing are operational variables and must be labeled separately.
- Do not omit a channel from notifications just because its specific post permalink is still pending; operators will assume the channel was skipped or failed.
- Do not claim continuous learning is active unless collection, staged snapshots, rule updates, and feedback into production are all implemented and exercised.

## Explanation artifact template

When the user asks “how does this work?”, prefer one diagram with this sequence:

`News → understandable hook → correct visual → hard QC → shared cross-channel package → staged metrics → causal comparison → cautious rule update → next content`

The diagram must show the feedback arrow returning learned rules to visual selection, writing, timing, and QC. Verify text contrast, mobile readability, complete connectors, and absence of clipped cards before delivery.
