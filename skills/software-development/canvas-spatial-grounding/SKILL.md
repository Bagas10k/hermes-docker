---
name: canvas-spatial-grounding
description: Use when auditing or designing canvas, SVG, or responsive mobile web layouts without spatial blindness.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [UI, SpatialLayout, ResponsiveDesign, MobileErgonomics, ComputerVision, ASCIIWireframe, MCP]
    related_skills: [tma-redesign-lessons-v3, upnormal-ui-architecture, animated-vector-icons]
---

# Canvas Spatial Grounding & Responsive Sensory Engine

Standard operating procedure for eliminating AI "spatial blindness" when creating, auditing, or refactoring canvas, SVG illustrations, and responsive mobile web interfaces.

## The Problem: AI Spatial Blindness

Vision-Language Models (VLMs) ingest images as downscaled token patches rather than measured metric grids. Consequently, AI agents frequently suffer from spatial errors:
1. **Coordinate Hallucination:** Eyeballing pixel coordinates $(x, y, w, h)$ instead of calculating exact bounds.
2. **Unanchored Floating Transforms:** Applying CSS `scale()` or `rotate()` to SVG sub-elements without explicit `transform-origin`, throwing elements away from their physical pivots.
3. **Mobile Layout Drift:** Failing to detect hidden horizontal scrollbars (`scrollWidth > clientWidth`), asymmetric card margins, or off-center elements.
4. **Touch Target Violations:** Designing mobile buttons smaller than 44x44px.

## Visionless Sensory Perception (Perceive Without Vision Calls)

Do not rely on token-heavy, subjective vision model calls to inspect layout structure. Layout on the DOM is pure geometry. Use headless DOM telemetry to "feel and see" the screen in pure text.

### 1. Viewport Breakpoints & Invariants

Always audit across three standard physical viewports:
- **Mobile Smartphone:** `390x844` (iPhone standard viewport)
- **Tablet:** `768x1024`
- **Desktop:** `1280x800`

### 2. Four Hard Invariants for Responsive Mobile

1. **Zero Horizontal Overflow:**
   $$\text{document.documentElement.scrollWidth} \le \text{window.innerWidth}$$
   Any element where $\text{rect.right} > \text{viewport.width} + 1$ (and not clipped by an `overflow: hidden` parent or SVG viewport) is a critical layout bug that causes accidental horizontal pan.
2. **Touch Target Ergonomics (WCAG 2.5.5 Level AAA):**
   Every interactive button, link, tab, or input on mobile ($\le 800\text{px}$) must have $\ge 44 \times 44\text{px}$ bounding box. On desktop, minimum interactive target is $28\text{px}$.
3. **Above-The-Fold Law (Mobile 844px Budget):**
   Primary headline, core task form, and interactive controls must have $y + \text{height} \le 844\text{px}$. Avoid giant decorative banners that push interactive content below the fold.
4. **Grid & Column Symmetry:**
   In two-column mobile option splits (e.g. category pill and time picker), verify:
   $$|w_{\text{col1}} - w_{\text{col2}}| \le 4\text{px} \quad (50\text{--}50\text{ balanced split})$$

### 3. Native Integration in Browser Harness

In any `browser_exec` turn, call `sense_layout('mobile')` or `sense_layout('desktop')` directly from `agent_helpers.py`. The runtime switches the device viewport metrics override, evaluates the probe, and prints:
- Layout Health Status & Score (0-100)
- Horizontal Scrollbar Bug indicator
- ASCII Viewport Wireframe
- Above-The-Fold Landmark Inventory


---

## ASCII Layout Wireframe Rendering

To perceive layout structure instantly without vision, render an ASCII bounding box matrix:

```text
┌──────────────────────────────────────┐ [Y=0]
│+------------------------------------+│
│|.topbar                             |│ Navbar (h: 64px)
│+------------------------------------+│
│+------------------------------------+│
│|.hero-date-card                     |│ Date Header (h: 215px)
│+------------------------------------+│
│+------------------------------------+│
│|.growth-card                        |│ Botanical Bloom (h: 142px)
│+------------------------------------+│
│+------------------------------------+│
│|#form-new-task                      |│ Task Form (h: 95px)
│+------------------------------------+│
└──────────────────────────────────────┘ [Y=844: ABOVE THE FOLD]
```

## Available Tooling

### CLI & Script
- `/home/ubuntu/.hermes/scripts/canvas_layout_inspector.py`
  * `grid <img.png> -o <grid.png>`: Overlay calibrated pixel rulers & center crosshairs.
  * `detect <img.png> -w`: Detect component bounding boxes and produce annotated wireframe.
  * `audit <img.png>`: Audit margin symmetry, row gaps, and centering deviations.
  * `svg <file.svg>`: Audit SVG for unanchored transforms and viewBox overflows.
- `/home/ubuntu/.hermes/scripts/dom_responsive_sensor.py`
  * Audits DOM telemetry across breakpoints, checks horizontal overflow, and outputs ASCII wireframe.

### Model Context Protocol (MCP)
Server: `canvas-inspector` (`https://github.com/Bagas10k/canvas-layout-inspector`)
- `canvas_get_mobile_probe_script()`: Returns JavaScript snippet to execute via CDP/browser.
- `canvas_sensor_dom_audit(probe_json)`: Visionless DOM layout audit & ASCII wireframe.
- `canvas_overlay_grid(image_path)`: Visual ruler grid for screenshot verification.
- `canvas_audit_svg(svg_path_or_string)`: Geometric SVG validator.
