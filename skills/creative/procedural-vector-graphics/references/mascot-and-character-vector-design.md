# Mascot & Character Procedural Vector Design

Constructing appealing, memorable mascot and character illustrations directly from procedural code, applying classical character design proportions and flat modern aesthetics.

## 1. The Chibi & Kawaii Proportional Formula

Human perception instinctively registers "cuteness" through biological infant schema triggers (*Kindchenschema*):
1. **Head-to-Body Ratio:** Head diameter represents 45% to 60% of total mascot height (ratio 1:1.5 or 1:2 instead of realistic human 1:7).
2. **Low-Set Facial Features:** Position the horizontal eye axis at or below the vertical midpoint of the head sphere ($y_{\text{eyes}} \approx y_{\text{head\_center}} + 0.1 \cdot r_{\text{head}}$).
3. **Bulbous, Plump Silhouettes:** Use Catmull-Rom splines with `smooth=0.35` to create soft, rounded body contours that mimic plush toys or rubber bath toys.

---

## 2. Anatomical Layering Hierarchy (Z-Order)

In 2D vector code, draw order dictates visual depth. Elements must be rendered back-to-front:

```text
[Z-0: Environmental Ripple / Shadow] ➔ Lower ground shadow or water ripples.
[Z-1: Distal Appendages]            ➔ Rear wing, back leg, or trailing ear.
[Z-2: Main Torso Body Spline]       ➔ Plump organic body contour.
[Z-3: Proximal Appendages]          ➔ Front wing, belly patch, or chest fluff.
[Z-4: Head Spherical Primitive]     ➔ Main head circle or organic head spline.
[Z-5: Beak / Snout Spline]          ➔ Overlaps lower third of head.
[Z-6: Facial Features]              ➔ Large pupil circles, specular highlights, blush.
[Z-7: Accessories & Overlays]       ➔ Crown, headphones, eyeglasses, necktie.
```

---

## 3. The Specular Eye Formula (Bringing Vectors to Life)

A character's emotional warmth is dictated almost entirely by specular eye highlights:
1. **Base Pupil:** Solid black (`#111111`) or deep ink ellipse/circle.
2. **Primary Specular Highlight:** Crisp pure white (`#FFFFFF`) circle placed at the upper-right or upper-left quadrant ($r_{\text{primary}} \approx 0.35 \cdot r_{\text{pupil}}$).
3. **Secondary Catchlight:** Smaller white circle placed diagonally opposite ($r_{\text{secondary}} \approx 0.15 \cdot r_{\text{pupil}}$).
4. **Subtle Blush (*Cheek Tint*):** Soft semi-transparent warm ellipse placed directly beneath the outer eye corner (`fill="rgba(250, 93, 41, 0.25)"`).

---

## 4. Case Study: Bekbek (The Procedural Mascot Duck)

Key coordinate geometry applied in `scripts/vector_engine.py`:
- **Head:** Perfect circle at $(x=42, y=-35, r=48)$ in warm amber yellow (`#FFD166`).
- **Beak:** Closed Catmull-Rom spline with 4 control points pointing horizontally forward, filled with energetic flame orange (`#FA5D29`).
- **Body:** 11-point closed spline starting from an upward-tilted tail tip $(-115, 20)$, sweeping down through a deep rounded belly $(-40, 85) \to (20, 88)$, and rising into the forward chest $(90, 40)$.
- **Water Ripple Bed:** Two horizontal open sine waves with cyan accents (`#49B3FC`) giving fluid floating context.

---

## 5. Ligne Claire Editorial Characters & Companion Mascots

When creating editorial character portraits for stationery, brand identity cards, or team profiles (e.g., European/Turkish studio identity cards like *Şaşı Kedi*):

1. **Scale & Whitespace Restraint (35-40% Rule):**
   - The human figure must occupy only 35% to 45% of the card area, rendered from mid-thigh up ($3/4$ standing body).
   - Never over-zoom to a tight bust (65%+ area); generous breathing whitespace in the upper half creates quiet, high-end editorial elegance.
2. **Subtle Companion Mascot Scaling:**
   - Companion mascots (cats, ducks, small creatures) must remain realistically proportioned (15-20% of torso height).
   - Place them perched on the scapula/shoulder or resting in the crook of an arm. An oversized mascot that covers the entire chest destroys figure-ground balance.
3. **The Derpy / Expressive Asymmetrical Eye Formula:**
   - For whimsical or playful mascots (*şapang/derpy*), shift pupils sharply inward toward the nose bridge with slight vertical asymmetry (one pupil slightly higher) to create an affectionate, comedic personality.
4. **Physical Stationery Form Factor:**
   - Physical print cards (business cards, art prints) require crisp $90^\circ$ sharp paper corners and soft ambient physical shadows, not rounded $32\text{px}$ mobile app widget cards.
5. **Organic Ink Line Weight:**
   - Use fine organic stroke weights ($2.0\text{px} - 2.6\text{px}$) with natural gravity crease lines around waistbands and elbows, avoiding mechanical geometric thickness.
