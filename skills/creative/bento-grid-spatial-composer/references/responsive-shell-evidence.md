# Responsive shell: measured geometry and accessible order

## Procedure and acceptance
1. For pair width W, gap g and desired ratio k, secondary width=(W-g)/(k+1), primary=k times secondary. Equal outer heights are required for the same area ratio. A three-track span contains two gaps; span count alone does not prove 3:1.
2. Use minmax(0,3fr) minmax(0,1fr), min-width:0 and wrapping for long strings. Tablet 2:1 and mobile one column preserve readability; no fixed area ratio on mobile.
3. Preserve DOM order. Do not use dense packing to rearrange logical tasks. Native CSS Grid is sufficient; do not add unverified masonry dependencies.
4. Desktop shell: height:100dvh, rows auto minmax(0,1fr), min-height:0 and independently scrollable main. Mobile returns to natural document flow. Root overflow masking is not acceptance.
5. Use table semantics and tabular numbers; only thead th is sticky, not all row headers. Test keyboard range/reset, filtering, empty recovery, long strings and a large synthetic ledger.
6. Run Playwright at 320,390,640,768,1000,1024,1440px; compare DOM rectangles and actual scrollWidth. Run Axe AA tags and examine incomplete checks, not just violations.
7. If contrast is incomplete because a node is scroll-clipped, bring that exact node into view and rerun Axe contrast without excluding it or modifying styles. Keep original and follow-up results.
8. Obtain independent visual review, zero applicable Impeccable findings, and actual-token documentation. Neither automation nor screenshots establish universal WCAG conformity.

## Reproducible local evidence
Artifact: /home/ubuntu/autopilot-sandbox/trend-004/index.html.
Use terminal with workdir /home/ubuntu/autopilot-sandbox/trend-004: node test.cjs; node contrast.cjs; node close-gates.cjs.
Scripts reuse dependencies from trend-003 and record local Chromium path; install/select local dependencies when porting.
Seven widths: no horizontal overflow, interaction checks passed, zero Axe 4.13.0 AA-tagged violations. Four larger widths had contrast incompletes for clipped lower content. All 28 exact-target followups passed after scrolling into view. A 103-row synthetic stress ledger passed reachability and overflow at those four widths.
Desktop ratio 3.0, tablet approximately 2.0; mobile deliberately natural height. Impeccable final output [] after correcting heading hierarchy and changing this sandbox's cream background to neutral paper. This is not production brand approval.

## Reasoning and limits
Mechanistic: track minima and gap geometry determine area; attention does not follow automatically. Bayesian: scrolling the same node isolates occlusion from inadequate color contrast. Optimization: prioritize correct readable order over decorative packing; startup and Axe runtime bound any layout speedup, so no performance claim is made.
Known: tested Chromium behavior. Likely: native Grid is simpler than masonry for exact ratios. Uncertain: 2026 trend prevalence, screen-reader and cross-browser quality.

## Sources
MDN Grid layout and accessibility, read via Jina: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Grid_layout_and_accessibility . It explains visual reordering does not change speech or keyboard order.
Local REF-072 Vue Notus image inspected: use workspace/sidebar separation and aligned ledger; reject promotional framing and icon-metric tiles. Other reference-board entries were not inspected. UI Layouts masonary-grid source failed to fetch; no external component code claimed.

Vault backlink: [[SKILL-bento-grid-spatial-composer]].
