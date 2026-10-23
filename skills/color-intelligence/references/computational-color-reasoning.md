# Computational Color Reasoning

Use this procedure when a seed HEX must become a reusable UI color system rather than a fixed harmony template.

## Scope and limits

The included engine targets sRGB web/dashboard interfaces. It converts the seed to OKLab/OKLCH, searches role-based candidates, reduces chroma into gamut, validates final quantized HEX pairs, and ranks valid candidates using a non-normative heuristic.

Numeric output verifies geometry and contrast, not beauty, luxury, emotion, uniqueness, or brand fit. Transparent compositing, gradients, HDR, CMYK, video, and browser-specific rendering need separate checks.

## Hard and soft objectives

Treat accessibility, readable role pairs, semantic consistency, and device context as hard constraints. Treat hue tension, chroma energy, accent scarcity, depth, and novelty as soft objectives. Never relax a hard constraint to improve a creative score.

Use OKLCH `(L, C, H)` as the manipulation space:

- `L` is perceptual lightness, not WCAG relative luminance.
- `C` is chroma; available sRGB chroma depends on lightness and hue.
- `H` is circular hue and becomes meaningless near zero chroma.

Use DeltaEOK only to detect near-duplicate variants. A large perceptual distance does not prove readable luminance contrast or visual quality.

## Procedure

1. Establish the brief: UI type, brand, audience, density, light/dark mode, and accessibility target.
2. Run the engine for at least two parameter combinations. Use three for exploratory visual work.
3. If the seed is neutral, ask for or state an explicit hue assumption; `--hue` overrides deterministic inference.
4. Inspect generated role pairs and contrast evidence. Do not treat decorative glow as information.
5. Implement one candidate on real components and states.
6. Inspect desktop/mobile screenshots, including normal, hover, focus, selected, and disabled states.
7. Identify the three largest visual problems, patch them, and rerun numeric and visual checks.
8. Record user feedback as a change to soft parameters; do not lower contrast constraints.

## Engine

Run through `terminal` from the skill directory:

```bash
python3 scripts/color_reasoning_engine.py \
  --seed '#6B4FFF' --mode dark \
  --expression 0.93 --tension 0.84 \
  --variants 3 --explore 320 \
  --json-out /path/to/palette.json \
  --css-out /path/to/palette.css
```

Parameters:

- `--seed`: `#RGB` or `#RRGGBB`.
- `--mode`: `dark` or `light`.
- `--expression`: `0..1`, controls chroma/visual intensity and suggested accent scarcity.
- `--tension`: `0..1`, changes target hue separation.
- `--variants`: `1..20` requested outputs.
- `--explore`: `30..2000` candidates; cost grows approximately linearly.
- `--hue`: optional hue anchor for neutral seeds.

The engine uses fixed-lightness/fixed-hue binary chroma reduction. This is an educational approximation, not the full CSS Color 4 local-MINDE gamut mapping algorithm.

## Output interpretation

For every variant inspect:

- `palette`: semantic UI roles;
- `contrast`: final WCAG 2.x ratios after HEX quantization;
- `hue_separation_degrees`: circular hue relation;
- `deltaEOK_primary_secondary`: deduplication evidence, not quality;
- `accent_area_fraction_suggestion`: heuristic, not an accessibility rule;
- `score_heuristic`: a ranking aid that still requires visual review.

Do not claim whole-product WCAG compliance from these role checks. Test actual backgrounds after opacity, blur, overlays, and gradients.

## Experiment protocol

For a serious UI task:

1. Generate two modes or two tension settings.
2. Keep 2–3 candidates that pass all required role pairs.
3. Build a real page with interaction states.
4. Capture at approximately 390px and 1440px widths.
5. Rate hierarchy, coherence, distinctiveness, legibility, brand fit, and production quality separately on `0..5` scales.
6. Compare before/after screenshots and write three reusable lessons.

A high generator score alone is not a passing result.

## Engine maintenance gate

Apply this gate whenever the generator, optimizer, parser, cache, or public API changes:

1. **Boundary contract:** test `derive` directly, not only the CLI. Reject invalid types and out-of-range `variants`/`explore` values before loops or allocations begin.
2. **Finite arithmetic:** reject `NaN` and infinities at every public numeric boundary (`derive`, gamut mapping, conversion helpers, and selection helpers); non-finite values can silently compare false and produce plausible-looking colors.
3. **Strict seed parsing:** accept exactly one optional `#` and exactly three or six hexadecimal digits. Do not use repeated-prefix stripping because malformed seeds such as multiple `#` characters become valid accidentally.
4. **Final-value evidence:** recompute contrast from emitted HEX role pairs in tests and compare it with metadata. Never assert only against the engine's own reported ratio.
5. **Optimization oracle:** compare branch-and-bound or cached results against an exhaustive implementation over representative hue, chroma, target-lightness, light/dark, and tie cases. Require zero mismatches.
6. **Work bound:** instrument expensive selectors to prove invariant primary work happens once per derivation, not once per explored candidate. Profile before optimizing so structural repetition is removed before numeric tuning.
7. **Cache contract:** normalize/clamp finite inputs before forming cache keys; assert bounded `maxsize`, equivalent-input hits, and eviction after capacity. This prevents semantically identical inputs from consuming separate entries.
8. **Compatibility:** compare valid-domain output against the pre-change baseline for representative seeds and modes. Separate deliberate metadata wording changes from palette/contrast regressions.
9. **Release gate:** run deterministic unit tests, valid-domain fuzzing, a real JSON/CSS CLI probe, static security inspection, and independent QC. A self-report or a passing happy-path suite alone is not release evidence.

## Verification

Run:

```bash
python3 scripts/test_color_reasoning_engine.py -v
```

A valid integration has all tests passing and a sample command that writes parseable JSON plus CSS. For random or project-specific inputs, additionally verify every required ratio from the final rendered colors. If a test suite times out, profile the hot path and fix repeated structure before increasing the timeout; a timeout is a failed release gate, not a pass with slower hardware.

## Primary references

- W3C CSS Color Module Level 4: https://www.w3.org/TR/css-color-4/
- W3C WCAG contrast minimum: https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
- W3C relative luminance: https://www.w3.org/WAI/WCAG21/Understanding/relative-luminance.html
- W3C non-text contrast: https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html
- Björn Ottosson, OKLab: https://bottosson.github.io/posts/oklab/
