# 60 FPS Fluid Morphing & Motion Engineering

## 1. The Core Motion Mandate
Traditional AI designs produce jarring, static web pages with abrupt modal popups and flickering state switches. Upnormal interfaces demand continuous visual flow:
- **Zero-Blink Rule:** Elements never vanish and reappear instantly. Layout changes morph smoothly between states.
- **Target Frame Rate:** Solid 60 FPS without layout thrashing (triggering `composite` only, avoiding `layout`/`paint` recalculations during animation).

## 2. In-Place Card Expansion via GSAP Flip
Instead of opening a detached modal that obscures context, expand cards in-place:

```javascript
import { gsap } from "gsap";
import { Flip } from "gsap/Flip";

gsap.registerPlugin(Flip);

function expandCardInPlace(cardElement, containerElement) {
  // 1. Record initial geometry
  const state = Flip.getState(cardElement);

  // 2. Mutate DOM class / attributes
  cardElement.classList.toggle("is-expanded");

  // 3. Animate smoothly from initial to new coordinates
  Flip.from(state, {
    duration: 0.55,
    ease: "power3.inOut",
    absolute: true, // Prevents document reflow jitter
    onComplete: () => {
      // Reveal nested details smoothly
      gsap.to(cardElement.querySelectorAll(".detail-reveal"), {
        opacity: 1,
        y: 0,
        stagger: 0.05,
        duration: 0.3
      });
    }
  });
}
```

## 3. Spring Physics & Tactile Press Micro-Interactions
Every interactive button, pill, or card must provide instantaneous tactile feedback:

```css
.tactile-upnormal {
  transition: transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1),
              background-color 0.15s ease,
              border-color 0.15s ease;
  will-change: transform;
}

.tactile-upnormal:hover {
  transform: translateY(-2px);
}

.tactile-upnormal:active {
  transform: scale(0.975) translateY(0);
}
```

## 4. Shared Element Transitions (View Transitions API)
For multi-page or view transitions in modern browsers:
```css
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 0.35s;
  animation-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
}

.hero-media {
  view-transition-name: hero-shared;
}
```
Ensures page-to-page navigation morphs shared images and titles effortlessly.
