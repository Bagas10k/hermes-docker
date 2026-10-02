# Multi-Agent Canvas Spatial HUD & Speech Bubble De-Stacking

## 1. Problem: Bounding Box Occlusion in Dense Workspaces
When multiple autonomous agents operate in proximity (e.g. conference room meetings, pair-programming, or visiting adjacent workstations), rendering floating status bubbles or speech cards at a fixed offset (e.g. `bodyY - 32px`) results in severe visual stacking:
- Horizontally wide bubbles (~250-320px) due to timestamps and long status strings overlap adjacent agents completely.
- Isometric diorama props (conference tables, desks, monitors) drawn in depth passes occlude speech bubbles of rear agents.
- Bubbles directly obscure the agents' heads and the desks behind them.
- Idle agents displaying default placeholders (e.g. "Belum ada event") flood the canvas with useless visual noise.

## 2. Architecture: Two-Pass Overlay & 2D Relaxation Solver

### A. Separation of Concerns (Global Top-Layer Overlay)
1. **Pass 1 (World & Character Geometry):**
   - Render floor, rooms, walls, and furniture.
   - Render agents sorted by depth (`gridX + gridY`).
   - In the agent loop, DO NOT draw speech bubbles directly. Instead, enqueue active bubbles into `pendingBubbles = []`.
   - Filter out uninitialized / idle placeholder bubbles (`!bubble || bubble === 'Belum ada event'`).
2. **Pass 2 (Global Overhead HUD):**
   - After all diorama props, particles, and motes are drawn, call `renderResolvedBubbles(ctx, pendingBubbles)`.
   - Drawing at the very top guarantees zero occlusion by world geometry (tables/walls).

### B. Compact Pill Formatting & Clearance
- **Strip Timestamps:** Remove noisy `[HH:MM:SS]` prefixes from canvas overhead bubbles. Timestamps belong in the timeline / side inspector, not on the floating world HUD.
- **Strict Character Cap:** Truncate status strings to 18-20 characters with an ellipsis (`…`). Reduces bubble width from ~300px to ~110-140px, cutting collision surface area by >55%.
- **Elevated Headroom:** Anchor base bubble at `headY = bodyY - 56px` (instead of 32px). This places the bubble cleanly above isometric monitors, chairs, and avatar ears.

### C. 4-Pass 2D Relaxation Collision Solver
Iterate through all pairs of active bubbles using Gauss-Seidel relaxation:
```javascript
const iterations = 4;
for (let iter = 0; iter < iterations; iter++) {
  for (let i = 0; i < items.length; i++) {
    for (let j = i + 1; j < items.length; j++) {
      const b1 = items[i];
      const b2 = items[j];

      const dx = Math.abs(b1.bx - b2.bx);
      const dy = Math.abs(b1.by - b2.by);
      const minDistX = (b1.bw + b2.bw) / 2 + 12;
      const minDistY = (b1.bh + b2.bh) / 2 + 10;

      // When horizontal and vertical bounds overlap:
      if (dx < minDistX && dy < (minDistY + 14)) {
        // Vertical altitude staggering (push one higher, one lower)
        const overlapY = (minDistY + 14 - dy) + 6;
        if (b1.by <= b2.by) {
          b1.by -= overlapY * 0.6;
          b2.by += overlapY * 0.6;
        } else {
          b1.by += overlapY * 0.6;
          b2.by -= overlapY * 0.6;
        }

        // Horizontal lateral separation
        if (dx < minDistX) {
          const overlapX = (minDistX - dx) * 0.4 + 6;
          if (b1.bx <= b2.bx) {
            b1.bx -= overlapX;
            b2.bx += overlapX;
          } else {
            b1.bx += overlapX;
            b2.bx += overlapX;
          }
        }
      }
    }
  }
}
```

### D. Elastic Pointer Connector Stems
- When a bubble is displaced by the solver, draw a tapered connector stem from the bottom edge of the displaced bubble (`tipX, tipY`) directly to the agent's head coordinate (`anchorX, anchorY`).
- This guarantees unambiguous attribution so the user instantly sees which agent owns which floating bubble.
