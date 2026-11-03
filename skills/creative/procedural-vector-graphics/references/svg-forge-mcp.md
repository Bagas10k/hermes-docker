# Unified SVG Forge MCP — static assets and motion

Use registered server `svg-forge` for original SVG UI icons/elements and moving variants. Use Iconify instead for named third-party icon libraries with their licenses. Do not replace a meaningful UI symbol with an emoji.

## Working sequence

1. Call `svg_catalog` for actual available names. Current local implementation has 34 icon subjects, nine support elements, rounded/precise/bold stroke styles and six motion patterns. Do not invent catalog names.
2. Call `svg_generate_icon`, `svg_generate_element` or `svg_generate_family`. Keep one stroke family in one interface; use `currentColor` unless approved theme tokens require explicit hex. Set `decorative=false` plus a label when the graphic conveys meaning without adjacent text.
3. For a custom shape not in the catalog, use `svg_compose` with JSON geometry: `{tag: path|rect|circle|ellipse|line|polyline|polygon|g, attrs: {...}, children?: [...]}`. Use an intentional silhouette and bounded viewBox, not random ornament to fill whitespace.
4. Call `svg_animate` with the STATIC SVG returned above. Presets: draw, reveal, spring-pop, float, breathe, orbit. Finite is default; loop only for an actual ambient/status purpose. Supply `include_preview=true` for a standalone HTML with pause and hidden-tab handling.
5. To save, call `svg_export` with the original static SVG, simple .svg basename and optional motion parameters. It applies animation itself; do not pass animated output back to a static validator. `html_preview=true` also exports the review HTML.
6. Render actual assets in the target browser; verify clipped stroke, baseline alignment, touch target on surrounding control, contextual contrast, reduced motion and pause. Never claim 60 FPS/GPU or zero CLS from source inspection.

## Boundaries

- No scripts, SMIL, arbitrary CSS, external images/links, foreignObject, XML declarations or entities are accepted as input. Only internally generated motion CSS is added.
- Input limit 64 KiB,128 shapes,depth8; families1..32; exports refuse overwrite and path traversal.
- Default export root is `/home/ubuntu/mcp-svg-forge/output/`; trusted operator can configure `SVG_FORGE_OUTPUT_DIR`. This is not an OS sandbox.
- HTML preview pauses on hidden document/reduced motion; raw inline SVG integration must supply its own lifecycle (`data-paused=true`). An SVG in img cannot be controlled through its internal DOM by the host.
- Bang Motion integration means deterministic timing and preserved object identity in the SAME MCP, not its complete cinematic/VO/MP4/After Effects workflow. Credit Bang Tutorial's Bang Motion when documenting that provenance.
- Local source: `/home/ubuntu/mcp-svg-forge/`; README has verified startup/test and registration commands. BekVector tangent reuse is read-only and its optional fallback provenance is returned by catalog.
- To expose new registration in an older session, use `/reload-mcp` if supported or start a new session; installed configuration is not proof of live tool refresh.
