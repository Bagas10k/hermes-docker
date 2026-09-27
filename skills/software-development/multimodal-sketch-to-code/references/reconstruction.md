# Reconstruction evidence and operational trade-offs

## Official sources checked
- Pillow Image module: https://pillow.readthedocs.io/en/stable/reference/Image.html — lazy decoding, image size warnings and explicit handling of decompression bombs. Use MEDIANCUT only after RGB conversion; keep alpha compositing explicit.
- WCAG Contrast Minimum: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html — normal text 4.5:1, large text 3:1; never round a failing result up. Source CSS foreground/background are more reliable than antialiased edge pixels.
- Hermes skills: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills — local skill directory and progressive disclosure. The guessed /user-guide/skills/ endpoint returned 404; the official llms.txt supplied the correct route.

## Mechanistic model
T_feedback = image inspection + decoding + crop/quantization + role mapping + code + browser verification. Improving palette extraction cannot remove semantic inference or testing. Amdahl S = 1 / ((1-p)+p/s); no p or speedup was measured here. Input bytes and pixel limits bound acceptance, not resident memory: full-image decoding and EXIF copies may precede cropping. Sample-side quantization works on at most 384 x 384 pixels. Work serially on large screenshots.

Relative luminance uses sRGB linearization at 0.04045, weights 0.2126/0.7152/0.0722; contrast = (lighter+0.05)/(darker+0.05). Alpha needs a known backdrop. An ICC-tagged source without conversion makes numerical matching uncertain.

## Bayesian/experimental contract
Prediction before color probe: the flat CTA crop yields a pink accent rather than photograph gray, and black text beats white. Result: #FF70CF, black ratio 8.470666994720654, white ratio 2.479143615619438. Thus black passes normal text and white fails. Vision's earlier approximate #FF68D3 was only an estimate, not a measurement. Actual screenshot dimensions were 2880 x 12461, not 1200 x 1000 (the latter was only a crop). Inspect dimensions before interpreting screenshot coverage.

Known: sampled RGB pixels, crop geometry, functional browser assertions. Likely: selecting flat UI regions avoids photo-dominated palettes. Uncertain: exact original CSS, fonts, interaction, mobile layout, color-management fidelity, human flow-state benefit. Do not attach fabricated confidence percentages.

## Design choices
Use agent vision for hierarchy and semantic role mapping, Pillow for bounded color measurement, and the existing frontend stack for implementation. OCR-only loses grouping and visual hierarchy; automatic full-page palettes confuse media with UI; screenshot-as-background yields no accessible component. A learned screenshot-to-code model might speed large batches but adds model hosting, privacy and validation costs. One component at a time remains the baseline, without new services or production changes.

## Actual verification scope
Reference: local curated 028-protip-marketing-fullscreen-preview.png. SHA256 6e6932ec314be26cd0eadef54b4270b4001611d940696a038248893e2d6d1615.
Crop [110,425,500,440], sample [384,15], palette #FF70CF with fraction 1.0. CLI tests passed contrast endpoints, fraction sum, foreground pass and three invalid crops. Browser execution of the shipped inquiry template passed initial hidden state, opening with heading focus, closing with trigger focus, Escape closing, actual RGB colors, and no horizontal overflow at 390/768/1440 widths. Browser used a data URL, no public service or backend was deployed.

The template is an operational component example with explicitly invented local panel interaction, not a claim that the source website has that interaction. No full-page reconstruction, hand-drawn sketch sample, screenshot-diff score, cross-browser guarantee or human usability benchmark was performed. Full original vision attempt hit a provider usage limit; successful inspection covered top crops only. Repeated identical crop calls provided no new evidence; do not repeat a tool request unless changing the input or testing a distinct hypothesis.
