# Composition, Gestalt Psychology & Spatial Dynamics

Composition is the arrangement of visual elements to create a unified whole. Gestalt psychology describes how human visual perception naturally organizes disparate visual stimuli into coherent groups and patterns.

## 1. The 5 Core Gestalt Laws in Design

Human vision does not process elements individually; it instantly synthesizes relationships based on five immutable perceptual laws:

```text
┌──────────────────────────────────────────────────────────────┐
│                    THE GESTALT LAWS                          │
├────────────────────┬─────────────────────────────────────────┤
│ 1. PROXIMITY       │ Objects close together form one unit.   │
│ 2. SIMILARITY      │ Objects sharing color/shape are linked. │
│ 3. CONTINUITY      │ Eye follows uninterrupted curves/lines. │
│ 4. CLOSURE         │ Mind fills in missing visual boundaries.│
│ 5. FIGURE-GROUND   │ Sharp focus separates from background.  │
└────────────────────┴─────────────────────────────────────────┘
```

### 1. Law of Proximity (Hukum Kedekatan)
Elements placed near each other are perceived as belonging to the same functional group.
- *Application:* Keep a form label directly above its input field ($4\text{px} - 8\text{px}$ gap). The gap between distinct field groups must be at least $3\times$ larger ($24\text{px} - 32\text{px}$) to avoid visual conflation.

### 2. Law of Similarity (Hukum Kesamaan)
Elements that share identical visual attributes (color, typography, border radius) are perceived as having the same functional purpose.
- *Application:* All interactive primary buttons must share the exact same background and padding. Non-interactive status badges must never mimic button styling.

### 3. Law of Continuity (Hukum Kontinuitas)
The human eye naturally tracks smooth paths, lines, and curves rather than sudden abrupt turns.
- *Application:* Aligning left edges of text blocks, cards, and buttons creates an invisible vertical vector guiding the eye down the page.

### 4. Law of Closure (Hukum Penutupan)
The brain automatically completes incomplete shapes or boundaries if enough cues are present.
- *Application:* Cards with 1px semi-transparent hairline borders (`rgba(255, 255, 255, 0.08)`) do not need heavy opaque fills; the user's mind effortlessly perceives the container boundary.

### 5. Figure-Ground Relationship (Hukum Sosok-Latar)
The visual system separates elements into either the focal object ("figure") or the passive background ("ground").
- *The Two-Layer Silhouette Pattern:* The canvas background remains on Layer 0 (`z-index: 0`), while crisp text, buttons, and data cards float on Layer 10 (`z-index: 10`) separated by blur glass or tonal value steps.

---

## 2. Asymmetric vs Symmetric Balance

| Balance Model | Structural Layout | Psychological Effect | Best Suited For |
|---|---|---|---|
| **Symmetrical Balance** | Mirror image across vertical/horizontal axis. | Formal, calm, institutional, stable. | Certifications, formal seals, classical hero logos. |
| **Asymmetrical Balance** | Different elements with equal visual weight balancing across the canvas (e.g. monolithic headline left balanced by complex data table right). | Dynamic, energetic, contemporary, editorial. | Upnormal web dashboards, modern SaaS landing pages, news editorial carousels. |

---

## 3. Eye-Tracking Vectors: F-Pattern & Z-Pattern

Eye tracking studies show predictable ocular reading trajectories across screens:

1. **The F-Pattern (Text-Dense Layouts):**
   - Users scan horizontally across the top headline.
   - Drop down and scan a shorter horizontal span across sub-headings.
   - Scan vertically down the left edge for bullet points, keywords, or icons.
   - *Design Mandate:* Front-load the most critical words, metrics, and actions along the left vertical boundary.

2. **The Z-Pattern (Visual & Landing Page Layouts):**
   - Eye starts at Top-Left (Brand Name / Direct Text).
   - Travels to Top-Right (Navigation / Primary Action).
   - Slants diagonally through the Center Hero Visual or Value Statement.
   - Lands at Bottom-Right (Primary Conversion Trigger / CTA).
