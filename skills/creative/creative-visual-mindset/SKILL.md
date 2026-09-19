---
name: creative-visual-mindset
description: Use when designing visuals, images, or typography.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [visual-design, image-generation, typography]
    related_skills: []
---
# Creative Visual Mindset

## When to use
Apply to visual direction, graphic design, UI, image-generation briefs, isolated object assets, and font selection for this user. This is a taste and quality guide, not an image generator or installed font collection. Current user instructions take precedence.

## Evidence boundaries
- User rated numbered references 11, 12, and 15 as ordinary, not bad; other examples were very good, especially 10, 13, 16, and 19.
- The numbered references are stored in `C:/Users/bagas/Desktop/land/moodboard-pinterest.html`, with source/image mapping in `C:/Users/bagas/Desktop/land/pinterest-sources.json`. Use those files before asking the user to resend references.
- User feedback: 11, 12, and 15 are ordinary rather than bad; 10, 13, 16, and 19 are especially strong favorites. Treat this as taste calibration, not a claim that all remaining references are equally preferred.
- Inspect the actual images before describing their visual properties. Do not infer colors or composition from titles or numbers alone.
- User wants breadth in image styles, attention to no-background object assets, and a broad font repertoire.

## Procedure
1. Establish medium, audience, intended feeling, and technical constraints. Avoid unnecessary questions when a reasonable reversible choice suffices.
2. If references are available, inspect them. Separate observed features from inferred preferences: palette, lighting, material, texture, framing, perspective, spacing, typography, and mood. Record each numbered reference accurately.
3. Select a coherent visual direction rather than adding fashionable effects indiscriminately. When alternatives are requested, vary composition, image treatment, and typography meaningfully.
4. Specify images by subject, medium/style, material, palette, lighting, camera, composition, detail, aspect ratio, and exclusions. Consider photographic, sculptural 3D, clay, paper-cut, collage, line art, painterly, grainy print, and vector approaches as options.
5. Distinguish a full scene from an isolated object. For no-BG assets specify silhouette, full-object framing, edge detail, material, camera, and whether a separate/contact shadow is wanted. Require actual alpha transparency in PNG or WebP, not a white background or baked checkerboard. Inspect alpha and preview on light and dark surfaces before claiming transparency is verified.
6. Choose fonts by letterforms, proportions, weight range, language support, role, and brand fit. Start with one or two complementary families. Test actual copy at desktop and small sizes.
7. Review hierarchy, readability, spacing, asset integration, and distinctiveness. Keep copy direct and brief; remove effects that compete with content.
8. Incorporate feedback as contextual rules with evidence; do not generalize a single preference into an absolute ban.

## Font repertoire: candidates, not installed inventory
- Modern sans: General Sans, Satoshi, Switzer, Plus Jakarta Sans, Instrument Sans, PP Neue Montreal, PP Mori.
- Expressive/geometric display: Clash Display, Space Grotesk, Syne, Cabinet Grotesk.
- Editorial serif: Instrument Serif, Cormorant Garamond, Playfair Display, Boska, PP Editorial New, Canela, Ogg.
- Condensed/wide statement: Archivo, Bebas Neue, Anton, Thunder, Druk, Monument Extended, Integral CF.
- Warm/retro serif: Fraunces, Cooper Black, Recoleta.
- Monospace: JetBrains Mono, Space Mono, Fira Code, Geist Mono. PP Mori is sans-serif, not monospace.
Use these as a starting bank, not a closed list. Do not habitually default to Inter/Roboto/Arial, but allow neutral fonts where they serve the work. Verify licensing, availability, web embedding rights, weights, and glyph coverage before production; never imply premium fonts are free or already installed. Supply a suitable fallback.

## Pitfalls
- Do not equate good design with maximalism, novelty, or heavy display type.
- Do not claim to have learned visual properties from reference numbers alone.
- Do not claim a prompt guarantees transparent output; verify the generated file.
- Do not confuse a font shortlist with downloaded, licensed font assets.

## Verification
Before delivery confirm the direction fits the brief, actual text is readable, font loading/fallback works when implemented, and image edges/shadows fit the layout. For no-BG output verify alpha and edge quality. Report only checks actually performed and state missing reference images or unverified assets plainly.
