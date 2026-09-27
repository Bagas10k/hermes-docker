---
name: fluid-interactive-surface
description: "Build 60 FPS real-time fluid surfaces for vibe coding."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, fluid-simulation, vibe-coding, canvas-2d, visual-artifacts, physics]
    related_skills: [interactive-canvas-sketchbook, spring-physics-motion-lab, tactile-microinteraction-studio]
---

# Fluid Interactive Surface Skill

Build real-time, interactive 2D Eulerian fluid simulation surfaces (smoke, liquid swirls, cursor wakes) directly on HTML5 Canvas 2D/WebGL for vibe coding flow-state and tactile dashboards.

## When to Use

- Building dynamic background canvases responsive to cursor/touch movement.
- Creating engaging interactive web artifacts for vibe coding demonstrations.
- Simulating organic liquid ripple, smoke trails, and reactive dye dissipation.
- Don't use for: heavy multi-phase 3D CFD modeling, rigid body physics engines, or static flat card layouts.

## Prerequisites

- Modern browser supporting HTML5 `<canvas>` and `requestAnimationFrame`.
- Optional: Python 3 for headless simulation verification (`scripts/fluid_engine.py`).

## Quick Reference

- **Run Verification**: `terminal(command="python3 ~/.hermes/skills/creative/fluid-interactive-surface/scripts/fluid_engine.py")`
- **Simulation Grid**: Keep resolution at 32x32 to 64x64 cells; upscale via bilinear interpolation.
- **Iterations**: 4 Gauss-Seidel relaxation steps balance 60 FPS performance and visual stability.

## Procedure

1. **Configure Simulation Sizing**:
   Initialize internal grid state ($N \in [32, 64]$) independent of canvas pixel width/height to decouple physical computation from display resolution.
2. **Handle Input Interaction**:
   Capture `pointermove` or `touchmove` events to inject velocity impulses $(\Delta x, \Delta y)$ and density bursts into the grid.
3. **Execute Navier-Stokes Step**:
   Sequentially compute velocity diffusion, divergence-free pressure projection, semi-Lagrangian advection, and density dissipation.
4. **Render with Bilinear Upscaling**:
   Draw fluid density buffer to canvas with context image smoothing enabled for natural soft smoke gradients.
5. **Enforce Idle Auto-Sleep**:
   Halt the animation loop when total kinetic energy drops below threshold ($\epsilon = 0.05$) to maintain 0% CPU consumption during idle reading.

## Pitfalls

- **Pixel-for-Cell Traps**: Running Navier-Stokes equations at 1920x1080 resolution will freeze the browser main thread. Always compute on coarse grids ($32 \times 32$ to $64 \times 64$) and upscale.
- **Unbounded Acceleration**: Rapid mouse shakes can introduce velocity spikes exceeding stability limits. Clamp max impulse magnitude per pointer event ($\|\mathbf{v}\| \le 15.0$).
- **Missing Incompressibility**: Omitting the Poisson pressure projection step causes density to collapse into non-physical clusters instead of swirling vortices.

## Verification

Run the deterministic Python verification script to confirm boundary conditions, diffusion, advection, and safe dissipation:
`terminal(command="python3 ~/.hermes/skills/creative/fluid-interactive-surface/scripts/fluid_engine.py")`
All checks must output `VERIFIED`.
