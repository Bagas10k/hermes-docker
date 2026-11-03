### 7. Authentic Volumetric Mascot Canvas Engine (Beyond Flat Approximation Trap)
- **Superellipse Curve Formula ($n = 2.7$)**:
  - Never use rigid 2D `ctx.roundRect` or circular `ctx.arc` for organic squircle mascots (Mochi).
  - Trace the perimeter using the superellipse formula over 72 parametric steps to achieve a squishy, dough-like silhouette:
    ```javascript
    for (let i = 0; i <= 72; i++) {
      const a = (i / 72) * Math.PI * 2;
      const ca = Math.cos(a), sa = Math.sin(a);
      const px = rx * Math.sign(ca) * Math.pow(Math.abs(ca), 2 / 2.7);
      const py = ry * Math.sign(sa) * Math.pow(Math.abs(sa), 2 / 2.7);
      i === 0 ? path.moveTo(px, py) : path.lineTo(px, py);
    }
    path.closePath();
    ```
- **4-Layer Volumetric Gradient Lighting**:
  - Layer 1 (Base Tone): Linear gradient from top-right to bottom-left (`createLinearGradient(rx * 0.7, -ry * 0.85, -rx * 0.8, ry * 0.9)`).
  - Layer 2 (Ambient Bottom Tint): Upward fading gradient reflecting agent energy color (`createLinearGradient(0, ry, 0, -ry * 0.25)`).
  - Layer 3 (Radial Inner Shadow): Soft occlusion shadow along bottom perimeter (`createRadialGradient(rx * 0.25, -ry * 0.32, R * 0.15, 0, 0, R * 1.25)`).
  - Layer 4 (Specular Highlight Gloss): Crisp curved gloss reflection at the upper surface (`createRadialGradient(rx * 0.34, -ry * 0.46, 0, rx * 0.34, -ry * 0.46, R * 0.42)`), producing an unmistakable 3D silicone sheen.
- **3D Spherical Gaze Projection & Perspective Foreshortening**:
  - Calculate gaze angles with biological saturation roll-off:
    $$\text{look.x} = \tanh\left(\frac{\Delta x}{260}\right), \quad \text{look.y} = -\tanh\left(\frac{\Delta y}{200}\right)$$
  - Project eyes across a 3D spherical surface:
    $$\text{px} = \sin(\text{yaw}) \cdot \cos(\text{pitch}) \cdot r_x, \quad \text{py} = -\sin(\text{pitch}) \cdot r_y$$
  - Calculate perspective foreshortening scales:
    $$f_x = \operatorname{lerp}(\max(0.18, \cos(\text{yaw})), 1, 0), \quad f_y = \operatorname{lerp}(\max(0.18, \cos(\text{pitch})), 1, 0)$$
  - Clip eye rendering to the body path (`ctx.clip(path)`). When the mascot turns sideways, the far eye realistically foreshortens and wraps around the 3D horizon instead of drifting off into empty air.
- **Kinematic Springs, Organic Breathing & Dynamic Particles**:
  - Use keyframed tweening arrays (`anim(property, [[target, duration, easingFunc], ...], onComplete)`).
  - Continuous differential breathing:
    $$\text{scale}_y = 1 + \sin(t \times 1.8) \times 0.035, \quad \text{scale}_x = 1 - \sin(t \times 1.8) \times 0.02$$
  - Random double-blinks: when a blink triggers, add a 22% chance of firing an immediate second micro-blink 230ms later.
  - Procedural particle emitters (`emit(type, count)`) with velocity, gravity decay, and alpha fading for emotional states: hearts on `love`, stars on `proud`, sparkles on `finish`, sweat droplets on `ratelimit`, and Zzz letters on `sleep`.
  - Waving little hands on greeting (`greet()` sets `s.hands = 1` and oscillates $y$ coordinate by $\sin(t \times 13) \cdot R \times 0.16$).

### 8. Pure CSS/SVG Volumetric Mascot Craft & UI Morphing Kinematics (The Mumu Doctrine)
- **Volumetric 3D Tactile Rendering without Heavy 3D Engines**:
  - Achieve a high-craft tactile robot mascot (like Mumu) using lightweight CSS and SVG rather than heavy WebGL/Three.js bundles:
    * **Ceramic Shell & Subsurface Scattering**: Radial gradient with off-center light source (`radial-gradient(circle at 35% 20%, #ffffff 0%, #fdfcf9 35%, #efe9dd 75%, #ded7ca 100%)`), coupled with multi-tinted inner glow shadows (`inset 0 3px 6px #fff, inset 0 -8px 16px rgba(193, 95, 62, 0.09)`).
    * **Iridescent Rim Aura**: Tri-color gradient blur halo (`#00e5ff`, `#7c3aed`, `#c15f3e`) with soft radial falloff and breathing scale pulse.
    * **Recessed Glass Visor with Inner Bezel & Parallax Depth**: Deep obsidian pill container (`#080c14` with `box-shadow: inset 0 3px 8px #000`), subtle cyan stroke border, and a curved semi-transparent top highlight (`linear-gradient(180deg, rgba(255, 255, 255, 0.28) 0%, transparent 100%)`). Displace the visor within the outer shell with `translateZ(8px)` and directional offsets to generate realistic stereoscopic parallax when the head turns.
    * **Luminous OLED Eyes & Blushing Cheeks**: Cyan-white rounded pills with layered glow (`box-shadow: 0 0 8px #00e5ff, 0 0 16px rgba(0, 229, 255, 0.85)`). Pair with subtle pink/amber blushing cheeks (`.mumu-blush`) that softly illuminate on touch or happy reactions.
- **Anti-Elongation Squircle Proportions ("Anti-Lonjong Invariant")**:
  - Never design mascot dimensions taller than they are wide (e.g. 118px width by 142px height with egg-shaped radii), and never bias harmonic breathing vertically ($scale_y$ expanding while $scale_x$ contracts). An elongated egg silhouette feels stiff, alien, and "lonjong".
  - Enforce chubby, plump squircle geometry (width >= height, e.g. 136px by 124px, with 46%–50% curvature radii) and lateral breathing bias ($scale_x = 1.0 + \sin(t \times 2.0) \times 0.018, scale_y = 1.0 + \sin(t \times 2.0) \times 0.012$) so the mascot looks cuddly, rounded, and living.
- **3D Perspective Rig & Continuous Kinematics (Anti-Stiffness Invariant)**:
  - Never animate the mascot with isolated 2D translation keyframes alone (which makes the character feel rigid, flat, and robotic).
  - Wrap the character in a 3D perspective rig (`perspective: 800px; transform-style: preserve-3d;`).
  - Calculate dynamic 3D head orientation (yaw, pitch, roll) driven continuously by pointer/touch offsets normalized to window dimensions:
    ```javascript
    targetYaw = Math.max(-25, Math.min(25, (deltaX / winW) * 45));
    targetPitch = Math.max(-18, Math.min(18, -(deltaY / winH) * 35));
    targetRoll = Math.max(-12, Math.min(12, (deltaX / winW) * 20));
    currentYaw += (targetYaw - currentYaw) * 0.12;
    currentPitch += (targetPitch - currentPitch) * 0.12;
    currentRoll += (targetRoll - currentRoll) * 0.12;
    ```
  - Apply the dynamic rotation matrix together with harmonic breathing and hovering float:
    `rig.style.transform = translateY(${floatY}px) scale(${scaleX}, ${scaleY}) rotateY(${currentYaw}deg) rotateX(${currentPitch}deg) rotateZ(${currentRoll}deg);`
  - Drive interactive tap/click feedback via Euler-Hooke numerical spring integration ($F = -kx - cv$, impulse $v_0 = -0.38$) rather than canned keyframes to produce an authentic squishy silicone rebound. Enforce coupled volume preservation ($\text{scale}_x = 1.0 + (1.0 - \text{scale}_y) \times 0.6$) so vertical compression forces realistic lateral bulging.
  - Implement biological double-blinking: schedule random intervals (2.4s–5.4s) with a 35% probability of a secondary 110ms micro-blink 120ms after the first, eliminating the uncanny metronome cadence of single-interval CSS animations.
- **Two-Tier Hero-to-Header Morphing Architecture**:
  - **Idle Hero Stage**: Mascot floats centrally in the welcome viewport with synchronized floor contact shadow breathing (`@keyframes mumuShadowPulse`).
  - **Fluid State Migration to Sticky Companion**: When conversation starts or messages populate, morph the hero container out via FLIP or smooth spring contraction (`transform: translateY(-40px) scale(0.65); opacity: 0; max-height: 0;`) using `cubic-bezier(0.16, 1, 0.3, 1)` and `cubic-bezier(0.34, 1.56, 0.64, 1)`.
  - Concurrently, activate the mini companion in the top navigation header (`.mumu-mini-wrapper.active-companion`) with an overshoot spring pop (`animation: miniMumuPop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)`).
  - Synchronize companion state to AI inference: eyes pulse in `thinking` mode during model generation and celebrate with a squash & stretch `happy` bounce (`^ ^`) upon completion.
  - Resetting chat clears the active thread and smoothly expands the hero mascot back into the center stage with elastic spring overshoot.
- **Physics Pointer Tracking with Spring Easing**:
  - Track pointer/touch coordinates across the window and calculate normalized offsets relative to mascot center.
  - Apply semi-implicit Euler or lerp spring interpolation ($k \approx 0.16$) on `requestAnimationFrame`:
    ```javascript
    eyeCurrentX += (eyeTargetX - eyeCurrentX) * 0.16;
    eyeCurrentY += (eyeTargetY - eyeCurrentY) * 0.16;
    const transform = `translate(${eyeCurrentX.toFixed(2)}px, ${eyeCurrentY.toFixed(2)}px)`;
    ```
  - Apply identical proportional vectors to the header mini companion ($0.35\times$ scale) so all mascot avatars across the UI track the user in unison.
- **Mobile Hero Claustrophobia Defense (Horizontal Suggestion Carousel)**:
  - Stacking multiple prompt or suggestion cards vertically on mobile viewports (`max-width: 640px`) consumes >240px of vertical space, crowding the mascot and causing vertical claustrophobia.
  - Convert prompt cards on mobile into a single-line horizontal swipeable carousel (`display: flex; overflow-x: auto; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch; scrollbar-width: none;`). Each card spans ~200px with a 2-line clamped summary, reducing vertical consumption to ~68px (freeing >170px of negative space) and keeping the mascot, greeting, and input cleanly above the fold.
- **Mobile Bottom Dock Safe Area Clearance**:
  - Always enforce `padding-bottom: calc(20px + env(safe-area-inset-bottom, 12px))` on fixed or floating bottom docks on mobile. Standard zero-margin docks directly collide with or graze the iOS Home Indicator and Android gesture bar, triggering accidental navigation instead of prompt submissions.
