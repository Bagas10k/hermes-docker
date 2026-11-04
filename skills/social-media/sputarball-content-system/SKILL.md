---
name: sputarball-content-system
description: Use when producing or auditing SputarBall content.
version: 1.1.0
author: Bagas & Hermes Agent
---

# SputarBall Content System

## Core Growth Directive & Audience Metrics Gate
- Pipeline Execution Is Not Success: Generating hundreds of automated posts without follower growth is rated 0. Metrics that matter are non-follower reach, profile visits, saves, shares, and follower conversion.
- Reels-First Discovery (Top-of-Funnel Engine): Static carousels and single images are primarily retention formats distributed to existing followers. For accounts with <10k followers, carousel non-follower reach is near zero. Vertical video Reels (9:16) must drive >=75% of content output to achieve organic discovery in Instagram Explore and TikTok FYP.

## Motion Video Reels Doctrine (Strict Prohibition on Static Slideshows)
- **STRICT BAN ON STATIC PHOTO SLIDESHOW AS REEL:** Never stitch static graphic cards or still photographs into an MP4 and present it as a Reel or video. A series of still images crossfaded with a monotone drone is a slideshow masquerading as video, completely rejected by audiences and algorithms alike.
- **The 4 Essential Pillars of a Real Video Reel:**
  1. **Real Motion Footage (Cuplikan Gerak Nyata):** Must feature authentic match action clips—goal celebrations, crunching tackles, fingertip saves, manager touchline tantrums, or explosive skill runs—sourced from verified local footage archives (`data/footage/`) or `yt-dlp`.
  2. **Neural Voiceover Mandate (Strict Ban on Robotic Google TTS):** Robotic TTS (like Google Translate TTS) is rated 2/10 and strictly banned. Must use Microsoft Neural Voice (`edge-tts` with `id-ID-ArdiNeural` at `rate=+16%`) for lively, energetic Indonesian suporter commentary cadence.
  3. **Zero-Obstructed Match Footage & Separated Subtitle Card:** Subtitles MUST NEVER cover or obstruct the match action video (rated 1/10 when covering players/pitch). The 1080x1920 layout strictly partitions:
     * Header Bar: y = 0 to 200 (Branding & Hot Take topic, black 95%).
     * Clean Match Video: y = 280 to 1000 (100% clean video, zero text covering the action).
     * Dedicated Subtitle Card: y = 1180 to 1450 (High-contrast yellow `#FFE600` & white text on dark card with 4px yellow top accent rule).
     * Mobile UI Safe Zone: y = 1450 to 1920 (Free for Instagram & TikTok native UI overlays).
  4. **Multi-Track Audio (Soundtrack & SFX):** Multi-track audio mix combining the voiceover (prominent at volume 1.4) with high-energy drill background music (`data/audio/bgm_drill.mp3` ducked at volume 0.13) and clean cut transitions.
- **Local Footage Vault Principle:** Maintain pre-cut 20-30s clean match action clips in `data/footage/` (`match_action_clean.mp4`, `paes_clip_clean.mp4`, `marselino_raw.mp4`) so scheduled background workers render instantly without runtime live download latency or IP blocking.
- **Public Ingress & Meta CDN Routing:** Meta Graph API requires public, unauthenticated access to `video_url`. The gateway/reverse proxy (e.g. `penelitian-pola-pikir-ai/server.js` or ingress router) MUST route `/sputarball` directly to port 3085 without session auth redirects (`/login`), or container creation will fail with download errors.

## Topic Selection & Quota Doctrine (Mandat Mas Bagas)
- **Deterministic 80/20 Quota Rule (80% Timnas & Abroad, 20% Big Match Eropa):**
  * Gatekeeper evaluates the last 5 publications from SQLite. If 1 or more non-Timnas posts exist in the last 4 posts, the candidate selection is LOCKED 100% to `TIMNAS_INDONESIA` / Pemain Diaspora.
  * Base score for `TIMNAS_INDONESIA` is boosted to **+90 Poin** to prevent foreign league saturation.
  * General foreign league results (Al Nassr, Como, Bologna, etc.) are de-prioritized to prevent feed pollution.
- **Regex Word Boundary Matching for Keywords:** Short keywords (<=4 characters, e.g. `aff`, `sty`, `pssi`) MUST be matched using regex word boundaries `\bkeyword\b` to prevent catastrophic substring false positives (e.g. `aff` accidentally matching `Old Trafford`).
- **Generation Model Mandate (Mas Bagas Standard):** Exclusively use Gemini (`ag/gemini-3.8-flash-high` with fast fallback `ag/gemini-3.8-flash-medium` via router `127.0.0.1:20128/v1/chat/completions`). Do not route debate naskah to models lacking colloquial Indonesian suporter tone.

## Content cleanup scope and inventory
- Before destructive cleanup, resolve the account and whether the request means local assets, live platform posts, or both; do not infer SputarBall from a generic carousel request when multiple brands exist.
- Inventory candidates read-only before deleting: join drafts to each platform's publication records by draft ID, include format, slide count, publication status, exact post ID, and permalink. Filter carousel candidates separately from single-image posters and reels; a published status alone does not identify a carousel.
- Save the candidate inventory to a working JSON/CSV file and print only grouped counts plus a small sample; full publication dumps overwhelm context and conceal scope errors.
- Treat SUBMITTED records and profile-only permalinks as unresolved, not verified live posts. Reconcile them to exact posts on the confirmed account before any deletion; a profile URL cannot identify a deletion target.
- When both remote posts and local data are in scope, retain the local ID/permalink mapping until remote removal is verified. Authentication blockers are not a reason to erase the remaining reconciliation evidence or claim completion.

## Cross-channel parity
- Keep Instagram and TikTok identical in visual assets, slide order/count, topic, headline, and publication window.
- Keep captions platform-adapted: Instagram may be detailed; TikTok must remain the shorter version of the same headline/topic.
- Block unpaired TikTok publication or changed assets rather than allowing channel drift.
- Include both channels in dispatch notifications immediately upon submission: when TikTok returns 'SUBMITTED' before a video permalink is generated, link the profile (e.g. https://www.tiktok.com/@sputarball) with a status note rather than omitting the channel, which misleads operators into thinking only Instagram was posted.
- Reconcile exact permalinks and timing skew in the parity ledger (`cross_channel_publications`) asynchronously when telemetry sweeps identify the live post ID.

## Visual selection
- Prefer recognizable iconic footballers and Indonesian national-team figures so broad audiences understand the hook immediately.
- Iconic Subject Requirement for Match Posters: Reject generic distant / birds-eye / high-angle stadium action photos where players appear as small, anonymous figures. The hero visual for a match point poster MUST prominently feature an instantly recognizable iconic figure from the winning/featured club — either a marquee superstar player (e.g. Julian Alvarez, Antoine Griezmann, Fernando Torres) in a moment of triumph/high intensity, or a legendary manager (e.g. Diego Simeone) in a cinematic touchline stance. Audiences connect with star persona and emotional gravity, not distant tactical formations.
- Direct-From-Camera Press Photography Doctrine: Strictly ban telephoto crowd/stand snapshots, broadcast TV frame grabs, re-compressed thumbnails, or distant digital crops that look like low-quality screenshots ("ss / cacat"). Every hero visual MUST be an authentic, high-resolution press photo captured directly from professional sports camera sensors (DSLR / mirrorless, e.g. Canon EOS, Sony Alpha, Nikon full-frame) with pin-sharp optical clarity, genuine depth-of-field, and crisp micro-texture (hair, skin, jersey stitch, stadium lighting catchlights). If an asset shows soft focus, heavy grain, or pixelation when framed, reject it immediately and source a verified high-resolution camera original.
- Match the depicted player/team to the actual story; if the correct subject cannot be verified, use a neutral stadium image rather than the wrong player.
- Prioritize sharp Full HD/4K match-action, celebration, or emotionally legible images; reject blur, watermarks, bad crops, and hidden faces.
- Preserve headroom, facial visibility, text safe zones, and consistent crops across channels.
- Display a prominent official competition badge pill on Slide 1 top-bar (e.g. Premier League, LaLiga EA Sports, Serie A, UEFA Champions League, UEFA Europa League, Timnas Indonesia) with sharp SVG logos and competition accent colors so casual viewers immediately identify the league. Strictly avoid HTML/CSS flag boxes or Unicode characters that can be misinterpreted as emojis; use vector SVG emblems or clean dot indicators (`badge-dot`).
- When the story covers an apparel or kit release, the jersey itself MUST be the primary visual hero: place the kit prominently in the upper 65–75% of the frame without cards obscuring the collar, crest, or fabric pattern. Never use photos of players wearing an unrelated kit or generic stadium fillers. Isolate the garment cleanly: crop out all promotional banner text, retail labels, and watermarks so only the authentic jersey fabric, crest, and collar occupy the photographic plate.
- Strict Fallback Image Ban (Zero Generic Pitch / 3D Cartoon Asset): Strictly ban generic 3D soccer pitch renders, empty stadium turf illustrations, or cartoon field graphics (e.g. stadium_epic.jpg, football_goal.jpg) as hero or supporting visuals. If an authentic, high-resolution camera photograph cannot be acquired, return null so layout falls back to an elegant typography/ledger card instead of polluting the grid with generic green turf.
- Autonomous QC Release Gate (Zero-Bottleneck Telegram Approval): Draft preview notifications sent to the operator channel (-1004397580704) do NOT require manual approval buttons. Wewenang rilis penuh dipegang oleh Agent QC (Invariant Auditor). Draf dengan skor QC >= 80, foto aksi kamera asli HD terverifikasi, dan zero invariant defect LANGSUNG dipublikasikan secara otonom ke Instagram dan TikTok. Jika skor < 80 atau terdapat cacat visual/foto tidak layak, draf otomatis diveto (HARD_VETO) di tempat. Kanal Telegram murni menerima warta siaran bersih begitu konten sukses terbit.
- Non-Blocking Webhook Execution Rule (Deadlock Prevention): When handling human approval actions inside an HTTP gateway (e.g. Express on `:3050`), NEVER execute downstream publishing scripts with synchronous blocking subprocesses (`execSync`). If the publisher makes loopback or CDN head probes back to that same origin, the blocked single-threaded Node.js event loop creates a circular deadlock that times out the mobile browser. Always execute publishing actions via asynchronous non-blocking child processes (`exec` with Promise) and keep loopback CDN pre-warming timeouts bounded (<= 2000ms).
- Design Reference Gate & Anti-Slop (Bagas Cihuy Swiss Editorial Standard): Never assemble visual posts from ad-hoc guesswork or generic AI-slop (strictly ban floating rounded card boxes, neon/cyan glowing outlines, and decorative clutter). Ground all graphic layouts in verified high-end design systems:
  1. Consult the 100 curated design vault (`/home/ubuntu/referensi-desain/`) and load `swiss-editorial-carousel`.
  2. Implement architectural Swiss grid discipline: 4-corner pinning, strict 1px hairlines (`rgba(255,255,255,0.12)`), extreme typographic scale (massive condensed display title with tight kerning + micro monospace metadata with wide tracking), and confident negative space.
  3. Present tabular specifications using hairline-divided archival ledgers rather than heavy card containers.

## Formats and archetypes
- `DEBATE_REEL_916` (Real Video Reels / TikTok 1080x1920): High-intensity 15-20s real motion video designed to spark heated comments between opposing fan bases.
  - Video Composition: Fast cuts of authentic match action clips (2-3s per beat), dynamic spoken voiceover narration, animated kinetic text overlays, and drill/trap sports soundtrack.
  - Structure:
    * Beat 1 (0.0s - 4.0s): Slap hook question + intense action clip.
    * Beat 2 (4.0s - 12.0s): 2 brutal contrasting arguments + matching footage.
    * Beat 3 (12.0s - 18.0s): Call to debate question forcing fans to pick a side in the comments.
- `MATCH_POINT_POSTER` (1 Slide): Clean, high-impact full-time result poster inspired by 433 and Bleacher Report Football (1080x1350, 4:5 ratio). The dramatic hero celebration/action photo dominates 70–75% of the upper frame without obstruction from heavy text cards.
  - Scoreboard Elevation & Bottom Negative Space: Raise the entire scoreboard block away from the bottom canvas edge (e.g., bottom padding 85–95px, not <50px) to provide generous visual breathing room and prevent crowding against the footer rule.
  - Anti-AI Slop Status Rule (Ban Floating Capsule/Pill Badges): Strictly ban floating rounded neon/green capsule pill badges for `FULL TIME` or match status (rejected as generic AI slop). Present match status with architectural Swiss discipline: a clean micro-tracked monospace label (e.g. `• FULL TIME` or `FULL TIME // RESULT`, letter-spacing 0.25–0.28em) flanked symmetrically by 1px subtle hairline rules (`rgba(255, 255, 255, 0.18)`), or integrated directly into the typographic grid.
  - Symmetrical 3-Column Layout: Below the status hairline, a balanced 3-column broadcast scoreboard (`1fr 200px 1fr`) balances Home Crest/Name/Scorers (left), giant bold score `2 - 1` (center), and Away Crest/Name/Scorers (right) so asymmetric team name lengths do not create visual imbalance. Completely omit secondary match-point, points gained, or league standing strips at the bottom to maintain generous negative space and an open visual breathing room identical to official 433 graphics. Strictly ban multi-paragraph text blocks or nested card clutter on match result graphics.
  - Club Crest & Venue Integrity: Always supply authentic transparent vector/webp club crests via local `file://` URIs (`home_crest`, `away_crest`) into the template payload so Puppeteer renders real team badges rather than geometric fallback bars. Pass the explicit match venue (`venue`, e.g. `RIYADH AIR METROPOLITANO, MADRID`) to prevent hardcoded stadium fallback leaks.
  - Zero Emoji Compliance in Scoreboards: Strictly ban emoji characters (e.g. `⚽`) in match scoreboards and scorer line items; use clean 6px CSS dot indicators (`.goal-dot`, `#00FF87`) or monochrome vector SVGs.
- `MATCH_POSTER_SINGLE` (1 Slide): Instant visual impact poster for massive matches with prominent score, hero action, and league badge.
- `MATCH_RECAP_2SLIDE` (2 Slides): Slide 1 match result + Slide 2 netizen debate/Man of the Match polling.
- `BREAKING_KIT_2SLIDE` (Strictly 2 Slides): Dedicated format for single kit, merchandise, or national-team uniform releases. Cut all extraneous storytelling filler and get straight to the point:
  - Full-Bleed Main Visual (Edge-to-Edge): The actual kit/garment MUST be the direct, full-bleed main visual spanning 100% of canvas width (edge-to-edge) without enclosing it in small photographic plate frames or card boxes. The physical jersey dominates >60% of the upper canvas, sharp and unobstructed, seamlessly transitioning into the dark bottom area via a smooth gradient fade. Never obscure the collar, crest, or fabric pattern with cards.
  - Slide 1 (Product Reveal & Core Facts): Top bar with official badge pill and counter `01 / 02`. Below the jersey, standard SputarBall hierarchy: uppercase kicker tag, massive bold headline (e.g. `RESMI: JERSEY TIMNAS WARNA BIRU MUDA!`), followed by exactly 3 compact, 1-line feature rows (`APPAREL`, `KOMPETISI/FILOSOFI`, `HARGA RESMI`) with bold keywords for instant comprehension.
  - Slide 2 (Dual Macro Detail & 3 Principles): Dual edge-to-edge macro panels in the upper half (`FIG. 01` 3D embossed metallic crest, `FIG. 02` collar & inner neck motto). Below, standard hierarchy: kicker (`FILOSOFI & MAKNA DESAIN`), bold headline, and exactly 3 numbered 1-line breakdown points (Samudra/Identity, Motif/Growth, Retro history/Debate) anchored by solid number boxes (`[ 01 ]`, `[ 02 ]`, `[ 03 ]`). Footer features a clear discussion prompt (`SIMPAN & BAGIKAN ARSIP INI`).
- `CAROUSEL_4SLIDE` (4 Slides): Deep daily editorial, Timnas abroad, transfer alert, or player myths. Slide 2 must contain a supporting match-action photograph.
- `KIT_LOOKBOOK_4SLIDE` (4 Slides): Curated multi-club kit showcase (comparing 3–5 European third kits, retro collections, bloke core streetwear) structured to maximize Save and Share rates. Use only for broad multi-kit features; single kit releases must use `BREAKING_KIT_2SLIDE`.
- `HIGHLIGHT_REEL_916` (Vertical Video Reels / TikTok): 1080x1920 (9:16) format for official match highlights and goal clips.
  - Aspect Ratio & Canvas: 1080x1920 with obsidian dark canvas (`#0A0B0E`) and centered 16:9 match footage scaled to 1080px width (`scale=1080:608`), positioned around `y = 656`.
  - Top Header Safe Zone: Header (`SPUTARBALL // HIGHLIGHTS`, headline hook, and 3-column scoreboard card) must have `padding-top: 120-130px` to clear the camera punch-hole / notch and status bar.
  - Middle Safe-Zone Footer (Crucial for TikTok & IG Reels UI Safe Zone): The bottom 25–30% of the screen (`y > 1550`) is permanently obstructed by mobile native UI elements (username, caption, audio track bar, and vertical action buttons: Like, Comment, Share, Bookmark). Therefore, NEVER place text metadata, descriptions, or credit CTAs in the bottom 25% of the canvas. Position the footer card (match venue, short 1-line recap, broadcast credit, and follow CTA) immediately below the 16:9 video frame (between `y = 1280` and `y = 1500`), leaving the lower 30% as clean dark negative space that naturally absorbs platform UI overlays.
  - Legibility & Contrast: Goal scorers and minute timestamps must use high-contrast light text (`#CBD5E1` or `#FFFFFF` at >=14px bold), not dark muted gray, to remain legible on small smartphone screens.
  - Zero Emoji Compliance: 100% text and CSS indicators only (`•`, monospace tags, glowing dots).

## Topic and writing
- Generation Model Mandate (Mas Bagas Standard): Exclusively use Gemini (`ag/gemini-3.8-flash-high` with fast fallback `ag/gemini-3.8-flash-medium` via router `127.0.0.1:20128/v1/chat/completions`). Do not route debate naskah to models lacking colloquial Indonesian suporter tone.
- Anti-Commodity News Rule (Opinion & Debate Takes over Raw Scoreboards): Raw match results and scoreboards ("Team A menang 3-0") are low-value commodities already broadcast by mainstream outlets hours earlier. Audiences do not follow new accounts for stale scores. Every post must carry an emotional hook, debatable angle, controversial take, or tactical critique ("Bukti taktik X gagal", "Wasit berat sebelah?", "Siapa paling bersalah?").
- Mandatory Shareability Gate: Before passing Gatekeeper, evaluate: "Would an Indonesian football fan share this to their IG Story or WhatsApp football group?" If purely informative without emotional resonance, debate friction, or sharing utility, penalize or veto.
- Empirical Match Data Verification Gate: Strictly prohibit assuming, predicting, or extracting match statistics (scorers, minute timestamps, cards, penalties) from unverified live stream commentary feeds, pirate stream chat, or pre-match templates. An incorrect goalscorer attribution destroys media credibility immediately. Always verify against official match result cards (e.g. Google Sports official match card, official competition site, SofaScore/Flashscore) before rendering match result graphics or writing match captions. 'No Official Score Card = No Publication'.
- Default to Timnas Indonesia when a topic is broad or unconstrained: When requested for a general topic without an explicit club or league (e.g. 'jersey ketiga yang baru', 'kabar pemain cedera', 'update transfer'), evaluate active Timnas Indonesia and Garuda squad developments first before European leagues, as national-team events drive the highest local interest and save velocity.
- Make topics immediately understandable to casual audiences; avoid unexplained tactical jargon.
- Favor concrete, emotionally legible events: scorelines, comebacks, late goals, red cards, blunders, records, transfers, iconic players, major clubs, and Timnas Indonesia.
- Use concise headline structure: emotion/event + recognizable player/team + concrete consequence.
- Ban Sensational Clickbait Spam Openers: Strictly prohibit formulaic clickbait prefixes such as GEMPAR!, GEGER TRANSFER!, PLOT TWIST GILA!, or HEBOH!. Headlining must follow authoritative modern editorial standards (433 / Fabrizio Romano): clear, punchy, fact-grounded, and respectful of the audience's intelligence.
- Filter 100% Bahasa Indonesia Alami & Anti-AI Slop (Mandat Mas Bagas): Naskah wajib menggunakan bahasa santai khas suporter sepak bola dan Gen Z Indonesia. Dilarang keras menyelipkan frasa klise terjemahan mesin/LLM kaku seperti 'memanfaatkan kekuatan', 'merevolusi lanskap', 'menyelam lebih dalam', 'game changer yang sesungguhnya', 'bukan rahasia lagi bahwa', 'tak tertandingi di lapangan', atau 'merupakan bukti nyata bahwa'. Pelanggaran frasa ini memotong 25 poin dan memicu penolakan publikasi otomatis.
- CLI QC Warta Otomatis: Jalankan `/usr/local/bin/qc-warta check-text --domain sputarball --text "..."` untuk memverifikasi kepatuhan naskah secara instan sebelum dipublikasikan.
- Enforce topical entity cooldown (24 hours) across drafts and publications: penalize recurring signals for recently covered clubs, players, or match pairings (-50 to -90 points) to prevent duplicate posts for the same match and rotate coverage across leagues. Date comparison in database queries MUST use normalized SQLite datetime string format (YYYY-MM-DD HH:MM:SS), not JavaScript toISOString(), because space (' ') sorts before 'T' in ASCII, silently breaking lookback filters.

## Audio and TikTok presentation
- Never reuse the same TikTok background music or always select the first track; vary audio dynamically to keep the feed fresh.
- Classify content mood (High Energy/Hype, Timnas Garuda Pride, Superstar Aura, Drama/Controversy, Tactical/Transfer) and select from curated keyword pools.
- Avoid the last 5 used sound queries and randomize track selection among the top 3 search results, recording selections in `tiktok_sound_history`.

## Continuous learning
- Statistical Minimum Support for Topic Penalization: Never prune or penalize high-affinity core niche categories (such as Timnas Indonesia or marquee rivalries) based on underpowered sample sizes (e.g. < 25-30 posts) or skewed metrics from an unseeded infant account. Small sample noise on cold accounts will falsely penalize top-performing categories.
- Evaluate visual, topic, writing hook, and publication time as separate dimensions.
- Record predictions before publication and measure results at staged intervals rather than judging only final views.
- Control for timing, freshness, topic, player popularity, and platform before attributing causality.
- Promote a pattern into a rule only after repeated comparable samples; retain confidence levels and revoke rules when performance decays.
- Persist dynamic rules in SQLite table `agent_self_learned_rules` and inject them into Gatekeeper (`evaluateSelfLearnedGatekeeperBonus`) and Writer at runtime rather than relying on static code constants.
- Preserve an experimentation allocation and change one variable at a time.
- Learn from operational failures and QC defects—not only engagement metrics—synthesizing proactive `QC_DEFECT_GUARD` rules (preventing prediction-as-result, face clipping, missing slide facts) before drafts reach QC inspection.

## QC behavior
- Autonomous Invariant QC Gatekeeper (Full Release Authorization): When a draft passes audit with `score >= 80`, zero visual/factual defects, and authentic camera photography, the background worker is authorized to publish directly to Instagram and TikTok. If a draft fails QC (`score < 80` or defects detected), it is automatically vetoed and quarantined. Telegram notifications serve as clean broadcast receipts with live permalinks.
- Mandatory Programmatic QC Gatekeeper: Never allow any publishing script to bypass `auditDraft()`. `publisher.js` enforces a hard database gate requiring an authentic `PASSED` record with `score >= 80` in `qc_audits`. Manually setting `draft.status = 'QC_APPROVED'` without a genuine QC pass is strictly blocked.
- Match Data Verification Gate (NO EVIDENCE = NO SCORE): If a draft claims match results, scorers, penalties, or minute timestamps, it MUST be validated against verified official empirical evidence (e.g. Google Sports official match card, official competition site). Unverified or hallucinated scorers trigger an automatic defect, score penalty, and hard veto (`REJECTED`).
- Treat wrong subject, watermark, blur, face obstruction, and Instagram/TikTok visual mismatch as hard vetoes.
- Report actual evidence, residual risks, and confidence; do not inflate conclusions from small samples.
