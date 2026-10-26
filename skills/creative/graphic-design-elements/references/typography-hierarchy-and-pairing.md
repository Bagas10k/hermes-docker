# Typography Hierarchy, Font Pairing & Punctuation

Typography is the structural skeleton of graphic design. Type establishes voice, communicates brand dignity, and guides user comprehension.

## 1. Typeface Classification & Architectural Roles

| Category | Anatomical Traits | Psychological Vibe | Recommended Families |
|---|---|---|---|
| **Geometric / Grotesk Sans** | Uniform stroke weight, circular bowls, clean geometry. | Modern, objective, authoritative, Swiss. | *Inter Tight*, *Cabinet Grotesk*, *Syne*, *Plus Jakarta Sans*. |
| **Monospace (Tabular)** | Every character occupies identical width. | Technical, telemetry, code-native, data-first. | *JetBrains Mono*, *Geist Mono*, *Fira Code*, *Space Mono*. |
| **High-Contrast Editorial Serif**| Sharp transitional serifs, extreme contrast between thick/thin strokes. | Intellectual, literary, luxury, high-culture. | *Playfair Display*, *Instrument Serif*, *Cormorant Garamond*, *Cinzel*. |
| **Condensed / Display** | Compressed horizontal width, tall x-height, monumental impact. | Urgent, athletic, industrial headline punch. | *Archivo Condensed*, *Bebas Neue*, *Anton*. |

---

## 2. The Rule of Two (Font Pairing Matrix)

Never mix more than two distinct font families on the same interface or poster. A third family induces visual chaos.

### The Proven Pairing Formulas:
1. **The Modern Tech / Terminal Formula:**
   - *Display Headline:* `Inter Tight` or `Cabinet Grotesk` (Weight: 700 / Bold, Letter-spacing: `-0.02em`).
   - *Data & Micro-label:* `JetBrains Mono` (Weight: 500 / Medium, Letter-spacing: `+0.05em`).
2. **The Swiss Editorial Formula:**
   - *Display Headline:* `Syne` or `PP Neue Montreal` (Weight: 800 / ExtraBold, Tight Line-Height: `0.93`).
   - *Body Copy:* `Plus Jakarta Sans` or `Inter` (Weight: 400 / Regular, Line-Height: `1.55`).
3. **The Contemporary Luxury Formula:**
   - *Display Headline:* `Instrument Serif` (Italic or Regular, monumental scale 96px).
   - *Sub-labels:* `Inter Tight` (Uppercase, Tracking: `+0.12em`).

---

## 3. Typographic Proportion & Modular Scaling

Derive type sizes through a mathematical modular multiplier rather than arbitrary pixel values:

$$\text{Size}_n = \text{Base} \times (\text{Ratio})^n$$
Using Base = $16\text{px}$ and Major Third ($1.250$):

| Level | Size (px) | Line Height | Tracking | Role |
|---|---|---|---|---|
| **Display Hero** | `76px` – `112px` | `0.92` – `0.98` | `-0.03em` | Monolithic anchor keyword |
| **H1 Headline** | `38px` – `48px` | `1.05` – `1.15` | `-0.02em` | Primary page/section thesis |
| **H2 Section** | `24px` – `30px` | `1.25` | `-0.01em` | Topic cluster grouping |
| **H3 Subsection** | `18px` – `20px` | `1.35` | `0` | Card header or feature lead |
| **Body Copy** | `14px` – `16px` | `1.50` – `1.60` | `0` | Sustained reading paragraphs |
| **Micro Caption** | `10px` – `12px` | `1.40` | `+0.08em` | Telemetry tags, timestamps, badges |

---

## 4. Typographic Punctuation & Emphasis Techniques

Banish monotone text walls by infusing deliberate visual punctuation:

### A. The Editorial Underline
- Avoid browser-default `text-decoration: underline` that collides with descenders (*p, q, y, g, j*).
- Specify generous offsets and lightweight strokes:
  ```css
  .editorial-link {
    text-decoration: underline;
    text-underline-offset: 5px;
    text-decoration-thickness: 1.5px;
    text-decoration-color: var(--accent-punch);
  }
  ```

### B. Singular Keyword Accent
- In headline sentences, isolate the core strategic term and inject the 5% singular accent:
  ```html
  <h1>Rekayasa Sistem Kasir dengan <span style="color:#FA5D29">Presisi Mutlak</span>.</h1>
  ```
- The contrast between the neutral phrase and the vivid keyword instantly anchors the reader's gaze.

### C. Direct Text Branding Mandate
- Never flank headlines with fake app-icon boxes or squircle AI badges. Let the raw typographic weight speak for itself.
