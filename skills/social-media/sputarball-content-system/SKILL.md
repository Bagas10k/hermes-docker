---
name: sputarball-content-system
description: Use when producing or auditing SputarBall content.
version: 1.0.0
author: Bagas & Hermes Agent
---

# SputarBall Content System

## Cross-channel parity
- Keep Instagram and TikTok identical in visual assets, slide order/count, topic, headline, and publication window.
- Keep captions platform-adapted: Instagram may be detailed; TikTok must remain the shorter version of the same headline/topic.
- Block unpaired TikTok publication or changed assets rather than allowing channel drift.
- Include both channels in dispatch notifications immediately upon submission: when TikTok returns 'SUBMITTED' before a video permalink is generated, link the profile (e.g. https://www.tiktok.com/@sputarball) with a status note rather than omitting the channel, which misleads operators into thinking only Instagram was posted.
- Reconcile exact permalinks and timing skew in the parity ledger (`cross_channel_publications`) asynchronously when telemetry sweeps identify the live post ID.

## Visual selection
- Prefer recognizable iconic footballers and Indonesian national-team figures so broad audiences understand the hook immediately.
- Match the depicted player/team to the actual story; if the correct subject cannot be verified, use a neutral stadium image rather than the wrong player.
- Prioritize sharp Full HD/4K match-action, celebration, or emotionally legible images; reject blur, watermarks, bad crops, and hidden faces.
- Preserve headroom, facial visibility, text safe zones, and consistent crops across channels.
- Display a prominent official competition badge pill on Slide 1 top-bar (e.g. Premier League, LaLiga EA Sports, Serie A, UEFA Champions League, UEFA Europa League, Timnas Indonesia) with sharp SVG logos and competition accent colors so casual viewers immediately identify the league. Strictly avoid HTML/CSS flag boxes or Unicode characters that can be misinterpreted as emojis; use vector SVG emblems or clean dot indicators (`badge-dot`).
- When the story covers an apparel or kit release, the jersey itself MUST be the primary visual hero: place the kit prominently in the upper 65–75% of the frame without cards obscuring the collar, crest, or fabric pattern. Never use photos of players wearing an unrelated kit or generic stadium fillers. Isolate the garment cleanly: crop out all promotional banner text, retail labels, and watermarks so only the authentic jersey fabric, crest, and collar occupy the photographic plate.
- Design Reference Gate & Anti-Slop (Bagas Cihuy Swiss Editorial Standard): Never assemble visual posts from ad-hoc guesswork or generic AI-slop (strictly ban floating rounded card boxes, neon/cyan glowing outlines, and decorative clutter). Ground all graphic layouts in verified high-end design systems:
  1. Consult the 100 curated design vault (`/home/ubuntu/referensi-desain/`) and load `swiss-editorial-carousel`.
  2. Implement architectural Swiss grid discipline: 4-corner pinning, strict 1px hairlines (`rgba(255,255,255,0.12)`), extreme typographic scale (massive condensed display title with tight kerning + micro monospace metadata with wide tracking), and confident negative space.
  3. Present tabular specifications using hairline-divided archival ledgers rather than heavy card containers.

## Formats and archetypes
- `MATCH_POINT_POSTER` (1 Slide): Clean, high-impact full-time result poster inspired by 433 and Bleacher Report Football (1080x1350, 4:5 ratio). The dramatic hero celebration photo dominates 75–80% of the frame without obstruction from heavy text cards. Below, a symmetrical 3-column broadcast scoreboard (`1fr 200px 1fr`) balances Home Crest/Name/Scorers (left), giant bold score `5 - 0` with `FULL TIME` pill badge (center), and Away Crest/Name/Scorers (right) so asymmetric team name lengths do not create visual imbalance. Completely omit secondary match-point, points gained, or league standing strips at the bottom to maintain generous negative space and an open visual breathing room identical to official 433 graphics. Strictly ban multi-paragraph text blocks or nested card clutter on match result graphics.
- `MATCH_POSTER_SINGLE` (1 Slide): Instant visual impact poster for massive matches with prominent score, hero action, and league badge.
- `MATCH_RECAP_2SLIDE` (2 Slides): Slide 1 match result + Slide 2 netizen debate/Man of the Match polling.
- `BREAKING_KIT_2SLIDE` (Strictly 2 Slides): Dedicated format for single kit, merchandise, or national-team uniform releases. Cut all extraneous storytelling filler and get straight to the point:
  - Full-Bleed Main Visual (Edge-to-Edge): The actual kit/garment MUST be the direct, full-bleed main visual spanning 100% of canvas width (edge-to-edge) without enclosing it in small photographic plate frames or card boxes. The physical jersey dominates >60% of the upper canvas, sharp and unobstructed, seamlessly transitioning into the dark bottom area via a smooth gradient fade. Never obscure the collar, crest, or fabric pattern with cards.
  - Slide 1 (Product Reveal & Core Facts): Top bar with official badge pill and counter `01 / 02`. Below the jersey, standard SputarBall hierarchy: uppercase kicker tag, massive bold headline (e.g. `RESMI: JERSEY TIMNAS WARNA BIRU MUDA!`), followed by exactly 3 compact, 1-line feature rows (`APPAREL`, `KOMPETISI/FILOSOFI`, `HARGA RESMI`) with bold keywords for instant comprehension.
  - Slide 2 (Dual Macro Detail & 3 Principles): Dual edge-to-edge macro panels in the upper half (`FIG. 01` 3D embossed metallic crest, `FIG. 02` collar & inner neck motto). Below, standard hierarchy: kicker (`FILOSOFI & MAKNA DESAIN`), bold headline, and exactly 3 numbered 1-line breakdown points (Samudra/Identity, Motif/Growth, Retro history/Debate) anchored by solid number boxes (`[ 01 ]`, `[ 02 ]`, `[ 03 ]`). Footer features a clear discussion prompt (`SIMPAN & BAGIKAN ARSIP INI`).
- `CAROUSEL_4SLIDE` (4 Slides): Deep daily editorial, Timnas abroad, transfer alert, or player myths. Slide 2 must contain a supporting match-action photograph.
- `KIT_LOOKBOOK_4SLIDE` (4 Slides): Curated multi-club kit showcase (comparing 3–5 European third kits, retro collections, bloke core streetwear) structured to maximize Save and Share rates. Use only for broad multi-kit features; single kit releases must use `BREAKING_KIT_2SLIDE`.

## Topic and writing
- Default to Timnas Indonesia when a topic is broad or unconstrained: When requested for a general topic without an explicit club or league (e.g. 'jersey ketiga yang baru', 'kabar pemain cedera', 'update transfer'), evaluate active Timnas Indonesia and Garuda squad developments first before European leagues, as national-team events drive the highest local interest and save velocity.
- Make topics immediately understandable to casual audiences; avoid unexplained tactical jargon.
- Favor concrete, emotionally legible events: scorelines, comebacks, late goals, red cards, blunders, records, transfers, iconic players, major clubs, and Timnas Indonesia.
- Use concise headline structure: emotion/event + recognizable player/team + concrete consequence.
- Enforce topical entity cooldown (12 hours) across drafts and publications: penalize recurring signals for recently covered clubs, players, or match pairings (-50 to -90 points) to prevent duplicate posts for the same match and rotate coverage across leagues.

## Audio and TikTok presentation
- Never reuse the same TikTok background music or always select the first track; vary audio dynamically to keep the feed fresh.
- Classify content mood (High Energy/Hype, Timnas Garuda Pride, Superstar Aura, Drama/Controversy, Tactical/Transfer) and select from curated keyword pools.
- Avoid the last 5 used sound queries and randomize track selection among the top 3 search results, recording selections in `tiktok_sound_history`.

## Continuous learning
- Evaluate visual, topic, writing hook, and publication time as separate dimensions.
- Record predictions before publication and measure results at staged intervals rather than judging only final views.
- Control for timing, freshness, topic, player popularity, and platform before attributing causality.
- Promote a pattern into a rule only after repeated comparable samples; retain confidence levels and revoke rules when performance decays.
- Persist dynamic rules in SQLite table `agent_self_learned_rules` and inject them into Gatekeeper (`evaluateSelfLearnedGatekeeperBonus`) and Writer at runtime rather than relying on static code constants.
- Preserve an experimentation allocation and change one variable at a time.
- Learn from operational failures and QC defects—not only engagement metrics—synthesizing proactive `QC_DEFECT_GUARD` rules (preventing prediction-as-result, face clipping, missing slide facts) before drafts reach QC inspection.

## QC behavior
- Treat wrong subject, watermark, blur, face obstruction, and Instagram/TikTok visual mismatch as hard vetoes.
- Report actual evidence, residual risks, and confidence; do not inflate conclusions from small samples.
