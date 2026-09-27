---
name: spring-physics-motion-lab
description: Design spring physics and interactive motion curves.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [spring-physics, motion, animation, micro-interactions, vibe-coding, rk4, ui-physics]
    related_skills: [tactile-microinteraction-studio, vibe-coding-accelerator, interactive-canvas-sketchbook]
---

# Spring Physics & Motion Lab

Spring physics and physical kinematics create natural, responsive UI feedback that outclasses static CSS cubic-bezier curves. Instead of fixed durations, spring motion responds dynamically to user gesture velocity, momentum, and target distance.

## When to Use

- Prototyping tactile interactive controls: bouncy buttons, gesture-driven cards, pull-to-refresh, draggable bottom sheets, or snap sliders.
- Tuning realistic physics parameters: mass ($m$), stiffness/tension ($k$), damping ($c$), and initial velocity ($v_0$).
- Preventing unnatural animation interrupts: seamless interruption and retargeting without visual jerk or jarring jumps.
- Exporting calibrated spring configurations to CSS keyframes, Web Animations API (WAAPI), Linear/Framer Motion syntax, or raw JS rAF loops.
- Don't use for: simple opacity fades with fixed duration, low-power e-ink displays, or headless background batch jobs.

## Theoretical Foundations & Governing Equations

### 1. Second-Order Damped Harmonic Oscillator
The continuous equation of motion for a damped spring is:
$$m \frac{d^2x}{dt^2} + c \frac{dx}{dt} + k(x - x_{\text{target}}) = 0$$

Where:
- $m$: Mass (inertia, default $1.0$).
- $k$: Stiffness / Tension (restoring force, typical range $100 - 600$).
- $c$: Damping coefficient (resistance, typical range $10 - 45$).
- Undamped angular frequency: $\omega_0 = \sqrt{\frac{k}{m}}$
- Damping ratio: $\zeta = \frac{c}{2\sqrt{km}}$

### 2. Damping Regimes
- **Underdamped ($\zeta < 1.0$)**: Oscillates around the target before resting. Bouncy, tactile, high energy.
- **Critically Damped ($\zeta = 1.0$)**: Returns to target in minimum time without overshoot. Snappy, professional, enterprise.
- **Overdamped ($\zeta > 1.0$)**: Sluggish approach to equilibrium without oscillation. Heavy, viscous feel.

### 3. Numerical Integration (Semi-Implicit Euler vs RK4)
For real-time UI animation at 60–120 FPS, Semi-Implicit (Symplectic) Euler is computationally optimal ($O(1)$, zero heap allocations) and energy-conserving:
$$\begin{aligned}
a(t) &= \frac{-k(x(t) - x_{\text{target}}) - c \cdot v(t)}{m} \\
v(t + \Delta t) &= v(t) + a(t) \cdot \Delta t \\
x(t + \Delta t) &= x(t) + v(t + \Delta t) \cdot \Delta t
\end{aligned}$$

## Quick Reference Presets

| Preset | Mass ($m$) | Stiffness ($k$) | Damping ($c$) | $\zeta$ | Feel / Best Use Case |
|---|---|---|---|---|---|
| **Snappy / Crisp** | 1.0 | 400 | 38 | 0.95 | Tab switching, toggles, menu popups |
| **Bouncy / Tactile** | 1.0 | 250 | 18 | 0.57 | Like buttons, celebratory badges, dialog enter |
| **Gentle / Floating** | 1.0 | 120 | 16 | 0.73 | Tooltips, toast notifications, dropdowns |
| **Stiff / Strict** | 1.0 | 600 | 48 | 0.98 | Drag handles, slider thumbs, scroll snap |
| **Magnetic Snap** | 1.0 | 320 | 26 | 0.73 | Bottom sheet snap points, card dismiss |

## Implementation Recipes

### 1. Minimal Zero-Dependency Spring Runner (JavaScript)
```javascript
export class SpringRunner {
  constructor({ mass = 1, stiffness = 300, damping = 28, precision = 0.001 } = {}) {
    this.m = mass;
    this.k = stiffness;
    this.c = damping;
    this.precision = precision;
    this.x = 0;
    this.v = 0;
    this.target = 0;
    this.rafId = null;
    this.lastTime = 0;
  }

  setTarget(newTarget, initialVelocity = null) {
    this.target = newTarget;
    if (initialVelocity !== null) this.v = initialVelocity;
    if (!this.rafId) {
      this.lastTime = performance.now();
      this.rafId = requestAnimationFrame(this.loop.bind(this));
    }
  }

  loop(now) {
    const dt = Math.min((now - this.lastTime) / 1000, 0.033); // clamp to prevent tunnel
    this.lastTime = now;

    // Semi-implicit Euler
    const force = -this.k * (this.x - this.target) - this.c * this.v;
    const a = force / this.m;
    this.v += a * dt;
    this.x += this.v * dt;

    if (this.onUpdate) this.onUpdate(this.x, this.v);

    // Settling condition
    if (Math.abs(this.v) < this.precision && Math.abs(this.x - this.target) < this.precision) {
      this.x = this.target;
      this.v = 0;
      if (this.onUpdate) this.onUpdate(this.x, 0);
      if (this.onRest) this.onRest(this.x);
      this.rafId = null;
      return;
    }

    this.rafId = requestAnimationFrame(this.loop.bind(this));
  }

  cancel() {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }
}
```

### 2. Spring-To-CSS Keyframes Precompiler
When runtime JS animation overhead must be avoided (e.g. static hero banners or CSS-only widgets), precompute keyframes at build or initialization:
```javascript
export function generateSpringKeyframes({ mass = 1, stiffness = 300, damping = 25, duration = 0.8, samples = 60 }) {
  let x = 0, v = 0, target = 1;
  const dt = duration / samples;
  const frames = [];

  for (let i = 0; i <= samples; i++) {
    const pct = ((i / samples) * 100).toFixed(1);
    frames.push(`${pct}% { transform: scale(${x.toFixed(4)}); }`);
    const a = (-stiffness * (x - target) - damping * v) / mass;
    v += a * dt;
    x += v * dt;
  }
  return `@keyframes springPop {\n  ${frames.join('\n  ')}\n}`;
}
```

## Pitfalls

1. **Delta Time Explosion (Large $\Delta t$)**: If the browser tab loses focus, `dt` can jump from $0.016s$ to $>1.0s$, causing numeric divergence or NaN coordinates. Always clamp `dt = Math.min(dt, 0.033)`.
2. **Missing Rest / Settle Threshold**: Continuing `requestAnimationFrame` when the spring is imperceptibly vibrating ($<0.001\text{px}$) drains CPU/battery. Always enforce an explicit velocity + distance cutoff.
3. **Interrupt Stutter (Zeroing Velocity on Retargeting)**: When a user clicks a button mid-flight or drags a card during an active spring, never reset velocity to $0$. Preserve existing $v$ to achieve natural, momentum-preserving retargeting.
4. **Emoji Clutter**: Use geometric vector indicators (`[•]`, `[+]`, SVG icons) for physics handles and test widgets; never use emoji.

## Verification Checklist

- [ ] Spring settles cleanly at target without persistent CPU spinning.
- [ ] Interrupting an in-flight motion preserves momentum smoothly.
- [ ] No numerical instability (coordinates remain finite numbers).
- [ ] Zero emoji in markup, CSS, and documentation.
