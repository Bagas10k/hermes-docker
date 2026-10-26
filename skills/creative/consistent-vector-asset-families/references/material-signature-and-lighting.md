# Material Signature and Studio Lighting Specification

This reference defines the mathematical formulas and SVG gradient definitions required to maintain 100% material consistency across diverse vector subjects.

---

## 1. The Rose Gold & Champagne Metal Signature

The visual style popularized by QuiverAI ("Arrow 2 Telos") relies on a combination of warm metallic luster and semi-translucent glassmorphism.

### Palette Tokens
- **Base Metal High:** `#FFD7CE` (Warm Specular Highlight, RGB: 255, 215, 206)
- **Base Metal Mid:** `#E08E79` (Lustrous Rose Gold, RGB: 224, 142, 121)
- **Base Metal Low:** `#B5634F` (Warm Deep Copper, RGB: 181, 99, 79)
- **Creep Shadow:** `#6D3224` (Ambient Occlusion Creep, RGB: 109, 50, 36)

### SVG Linear Gradient Definition
```xml
<linearGradient id="roseGoldMetal" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="#FFD7CE" stop-opacity="1" />
  <stop offset="35%" stop-color="#E08E79" stop-opacity="1" />
  <stop offset="70%" stop-color="#B5634F" stop-opacity="1" />
  <stop offset="100%" stop-color="#6D3224" stop-opacity="1" />
</linearGradient>
```

---

## 2. Master Glass Architecture (Physical Double-Wall & Refraction)

A flat semi-transparent fill looks like cloudy plastic or film. High-end crystal glass requires 4 structural layers:

1. **Double-Wall Contour (Offset 6-8px):** Outer glass perimeter and inner refraction contour create physical mass.
2. **Refractive Dark Edge Stop:** On a light canvas, glass is defined by a thin dark refraction rim (`#4A1A10` at 45% opacity) on the shadow side.
3. **Crescent Specular Ribbon:** Razor-sharp curved highlight arc following the dome curvature rather than wide diffused blur.
4. **Solid Crystal Junction:** Thick pedestals and footings connecting glass bowls to stems.

### Master Glass Gradients
```xml
<!-- Crystal Clear Glass Hull with Refractive Dark Edge -->
<linearGradient id="glassHull" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.80" />
  <stop offset="25%" stop-color="#FFFFFF" stop-opacity="0.08" />
  <stop offset="65%" stop-color="#5E2619" stop-opacity="0.22" />
  <stop offset="90%" stop-color="#FFFFFF" stop-opacity="0.20" />
  <stop offset="100%" stop-color="#4A1A10" stop-opacity="0.45" />
</linearGradient>

<!-- Razor Sharp Specular Ribbon -->
<linearGradient id="sharpRibbon" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95" />
  <stop offset="40%" stop-color="#FFFFFF" stop-opacity="0.60" />
  <stop offset="80%" stop-color="#FFE5DF" stop-opacity="0.10" />
  <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.0" />
</linearGradient>
```

---

## 3. Directional Studio Lighting Vector

To achieve visual cohesion across completely unrelated objects:
- **Key Light (Primary):** Positioned at angle $-45^\circ$ (top-left). All metallic highlights and glass rim lights must align along this vector.
- **Fill Light (Secondary):** Soft ambient bounce from bottom-right, colored in warm copper (`#B5634F` at 20% intensity).
- **Contact Drop Shadow:** Soft horizontal ellipse directly beneath the contact plane with caustic core:
  ```xml
  <radialGradient id="crystalShadow" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#FFD8CE" stop-opacity="0.75" />
    <stop offset="30%" stop-color="#63261A" stop-opacity="0.22" />
    <stop offset="70%" stop-color="#63261A" stop-opacity="0.06" />
    <stop offset="100%" stop-color="#63261A" stop-opacity="0.0" />
  </radialGradient>
  ```
