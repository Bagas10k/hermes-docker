# Figma Export & Styling Tokens for Procedural SVG

Structuring procedural SVG vectors for seamless drag-and-drop into Figma canvases, ensuring high-res rasterization and clean tokenization.

## 1. Clean SVG Hierarchy for Figma Compatibility

When an SVG is pasted or imported into Figma, Figma's parser translates SVG XML elements directly into native Figma vector layers:
1. **Semantic Grouping (`<g id="...">`):** Wrap related sub-components into labeled group tags. Figma names layers according to the group `id`:
   ```xml
   <g id="water-ripples">
     <path d="..." stroke="#49B3FC" stroke-width="3" />
   </g>
   <g id="duck-body">
     <path d="..." fill="#FFD166" stroke="#111111" stroke-width="3" />
   </g>
   <g id="duck-head">
     <circle cx="42" cy="-35" r="48" fill="#FFD166" />
     <g id="eye">
       <circle cx="52" cy="-45" r="11" fill="#111111" />
       <circle cx="55" cy="-48" r="4" fill="#FFFFFF" />
     </g>
   </g>
   ```
2. **Explicit Fill and Stroke Attributes:** Avoid inline CSS `style="..."` blocks when possible; standard XML attributes (`fill="..."`, `stroke="..."`, `stroke-width="..."`) parse more reliably across design tools.
3. **Integer & 1-Decimal Coordinates:** Formats coordinates to at most 1 decimal place (`.1f`). Overly verbose floating points (`42.98172948123`) introduce precision jitter in Figma's vector pen engine.

---

## 2. Palette Tokenization & Contrast

Map colors semantically to establish unified visual branding:

| Semantic Token | Hex Code | Typical SVG Role |
|---|---|---|
| `--stage-bg` | `#0E1015` / `#0A0B0E` | Background canvas / Card container fill |
| `--vector-ink` | `#111111` / `#000000` | Bold vector outlines (2.5px–3px), pupils |
| `--accent-primary` | `#FA5D29` (Ember) | Beaks, focal badges, verified status marks |
| `--accent-secondary` | `#49B3FC` (Cyan) | Fluid waves, telemetry paths, technology rings |
| `--fill-warm` | `#FFD166` (Amber Gold) | Primary mascot body fill |
| `--fill-highlight` | `#FFFFFF` | Specular eye catchlights, core center node |

---

## 3. High-Performance Headless Rasterization (resvg-py)

While SVG provides infinite vector fidelity, delivery platforms (like Telegram image previews or documentation thumbnails) require PNG rasterization.

The `resvg-py` library is Rust-backed and renders compliant SVGs in milliseconds:
```python
import resvg_py

def render_svg_to_png(svg_string: str, output_path: str):
    png_bytes = resvg_py.svg_to_bytes(svg_string)
    with open(output_path, "wb") as f:
        f.write(png_bytes)
```
- Fully supports Catmull-Rom Bezier curves, clipping paths, rounded rectangles, and embedded typography.
- Native Telegram delivery: output files can be forwarded immediately via `MEDIA:/path/to/file.png`.
