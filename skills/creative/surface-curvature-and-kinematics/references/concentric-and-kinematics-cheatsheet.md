# Concentric Radius & LERP Kinematics Reference Cheatsheet

## 1. Concentric Radius Pairings Table

| Parent Radius ($R_o$) | Container Padding ($P$) | Required Child Radius ($R_i = R_o - P$) | Use Case |
|---|---|---|---|
| `32px` | `20px` | `12px` | Large outer Bento container with inner widgets |
| `28px` | `16px` | `12px` | Standard modal / elevated card with embedded modules |
| `24px` | `16px` | `8px` | Compact interactive card with embedded tags |
| `20px` | `12px` | `8px` | Inner submodule with nested buttons |
| `16px` | `10px` | `6px` | List items and sub-cards |
| `Any` | `P >= R_o` | `0px` or `4px` | Deeply padded content (prevents inverted curve glitch) |

## 2. LERP Kinematics RAF Template (Zero-Lag Pointer Inertia)

```javascript
class DampedSurfacePhysics {
  constructor(element, damping = 0.08) {
    this.el = element;
    this.damping = damping;
    this.current = { x: 0, y: 0, rx: 0, ry: 0 };
    this.target = { x: 0, y: 0, rx: 0, ry: 0 };
    this.rafId = null;
    this.isTicking = false;
    this.bind();
  }

  bind() {
    this.el.addEventListener('pointermove', (e) => {
      const rect = this.el.getBoundingClientRect();
      const nx = (e.clientX - rect.left) / rect.width - 0.5; // [-0.5, 0.5]
      const ny = (e.clientY - rect.top) / rect.height - 0.5;

      this.target.rx = -ny * 12; // Max 12deg tilt
      this.target.ry = nx * 12;
      this.target.x = nx * 16;
      this.target.y = ny * 16;

      if (!this.isTicking) {
        this.isTicking = true;
        this.loop();
      }
    });

    this.el.addEventListener('pointerleave', () => {
      this.target.rx = 0;
      this.target.ry = 0;
      this.target.x = 0;
      this.target.y = 0;
    });
  }

  loop() {
    this.current.rx += (this.target.rx - this.current.rx) * this.damping;
    this.current.ry += (this.target.ry - this.current.ry) * this.damping;
    this.current.x += (this.target.x - this.current.x) * this.damping;
    this.current.y += (this.target.y - this.current.y) * this.damping;

    this.el.style.transform = `perspective(1000px) rotateX(${this.current.rx.toFixed(3)}deg) rotateY(${this.current.ry.toFixed(3)}deg) translate3d(${this.current.x.toFixed(2)}px, ${this.current.y.toFixed(2)}px, 0)`;

    const delta = Math.abs(this.target.rx - this.current.rx) + Math.abs(this.target.ry - this.current.ry);
    if (delta > 0.01) {
      this.rafId = requestAnimationFrame(() => this.loop());
    } else {
      this.isTicking = false;
      cancelAnimationFrame(this.rafId);
    }
  }
}
```

## 3. Specular Rim Palette by Surface Luminance

### Dark Obsidian (#0E0F10)
```css
box-shadow:
  inset 0 1px 1px 0 rgba(255, 255, 255, 0.28),
  inset 0 0 0 1px rgba(255, 255, 255, 0.04),
  0 24px 60px -15px rgba(0, 0, 0, 0.70);
```

### Light Porcelain (#F8FAFC)
```css
box-shadow:
  inset 0 1px 1px 0 rgba(255, 255, 255, 0.90),
  inset 0 0 0 1px rgba(0, 0, 0, 0.05),
  0 12px 32px -8px rgba(0, 0, 0, 0.06);
```

## 4. Modular Soft Tile Grids & Calendar Scheduling Curvature

When building modern calendar/timetable interfaces (Linear, Arounda standard) instead of rigid table grids:

| Element | Target Curvature / Geometry | Border Treatment & Specular Depth |
|---|---|---|
| Outer Timetable Viewport | `border-radius: 24px - 28px` | `1px solid rgba(0,0,0,0.05)` + diffused float |
| Individual Time Slots (Grid Cells) | `border-radius: 16px - 18px; margin: 3px` | `1.5px dashed rgba(0,0,0,0.08 - 0.10); bg: rgba(255,255,255,0.7)` |
| Full-Hour / Multi-Hour Event Cards | `border-radius: 20px - 22px; padding: 12px 14px` | Soft multi-stop pastel gradient + `inset 0 1px 1px rgba(255,255,255,0.7)` |
| Inner Time-Capsule Badges | `border-radius: 9999px; padding: 4px 10px` | `backdrop-filter: blur(8px); bg: rgba(255,255,255,0.4)` |
| Milestone / Quick Task Pills | `border-radius: 9999px; height: 34px - 36px` | Tactile drop shadow `0 4px 12px rgba(0,0,0,0.1)` |
| Mobile Bottom Sheet Modal | `border-radius: 28px 28px 0 0` | `box-shadow: 0 -16px 48px rgba(0,0,0,0.6)` + top handle (`38px x 4px`) |

