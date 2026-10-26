# Color Theory, Contrast Mathematics & Palette Tokenization

Color governs emotional impact, information grouping, and visual hierarchy. In digital systems, color must balance aesthetic drama with rigorous mathematical accessibility.

## 1. Contrast Mathematics & WCAG AAA Standard

The World Health Organization and W3C define visual contrast as the relative luminance ratio between text and its background:
$$\text{Ratio} = \frac{L_1 + 0.05}{L_2 + 0.05}$$
Where $L_1$ is the relative luminance of the lighter color and $L_2$ is the relative luminance of the darker color (ranging from $0.0$ for black to $1.0$ for white).

| Standard | Level | Minimum Ratio (Normal Text) | Minimum Ratio (Large Text $\ge 18\text{pt}$) |
|---|---|---|---|
| **WCAG AA** | Minimum compliance | $4.5 : 1$ | $3.0 : 1$ |
| **WCAG AAA** | **The Hermes Standard** | $\ge 7.0 : 1$ | $\ge 4.5 : 1$ |

### Why We Enforce WCAG AAA ($\ge 7:1$):
Subtle light-gray text on white backgrounds looks trendy in mockups but renders illegible on low-brightness mobile screens in direct sunlight. High contrast guarantees instant legibility in all operational conditions.

---

## 2. The 95/5 Achromatic Stage Rule

A common AI slop failure is "color soup"—using 5 competing vibrant colors simultaneously (blue buttons, purple gradients, yellow badges, green borders, pink cards).

### The Formula:
- **95% Canvas Surface (Achromatic Substrate):**
  - Dark Theme: Ink `#0A0B0E`, Surface `#12151D`, Card `#1A1E29`, Border `rgba(255, 255, 255, 0.08)`.
  - Light Theme: Canvas `#F8F9FA`, Surface `#FFFFFF`, Card `#F1F3F5`, Border `#E9ECEF`.
- **5% Singular Focal Accent:**
  - One high-chroma punch color reserved exclusively for the most critical action or status indicator.

### Curated 5% Accent Candidates:
1. **Ember Flame (`#FA5D29`):** Energetic, industrial, urgent, authoritative. Best for checkout CTAs, primary triggers, and warning states.
2. **Electric Cyan (`#49B3FC`):** Cybernetic, telemetric, data-driven, serene. Best for active data streams, telemetry charts, and technology badges.
3. **Acid Lime (`#A6FF00`):** High-speed, cutting-edge, vanguard. Best for live system status, growth metrics, and algorithmic counters.
4. **Warm Ochre / Gold (`#FFD166`):** Friendly, optimistic, mascot warmths, luxury accents.

---

## 3. Harmonic Color Palettes

When secondary semantic categories are required (e.g. multi-tier status charts, traffic indicators), apply mathematical color harmony:

| Harmony Model | Angle Distance on Color Wheel | Characteristic | Best For |
|---|---|---|---|
| **Monochromatic** | $0^\circ$ (varying lightness/saturation) | Sophisticated, quiet, zero visual conflict. | Executive dashboards, luxury portals. |
| **Complementary** | $180^\circ$ (opposite poles) | Maximum chromatic tension and focal energy. | Warm/Cool juxtapositions (Orange + Cyan). |
| **Split-Complementary**| $150^\circ$ and $210^\circ$ | High contrast with softer tension. | Complex data grids with 3 distinct statuses. |
| **Analogous** | $30^\circ$ adjacent span | Harmonious, smooth natural transitions. | Gradient backdrops, progress bars. |

---

## 4. Design Token Architecture (CSS Custom Properties)

```css
:root {
  /* 95% Achromatic Stage */
  --stage-bg: #0b0d13;
  --surface-panel: rgba(18, 21, 29, 0.85);
  --border-hairline: rgba(255, 255, 255, 0.08);
  --text-primary: #f8f9fa;   /* Contrast ~18:1 against stage */
  --text-muted: #8e9aa8;     /* Contrast ~7.2:1 against stage */

  /* 5% Singular Accent */
  --accent-punch: #fa5d29;
  --accent-glow: rgba(250, 93, 41, 0.2);

  /* Semantic Feedback States */
  --state-success: #10b981;
  --state-danger: #ef4444;
  --state-info: #49b3fc;
}
```
