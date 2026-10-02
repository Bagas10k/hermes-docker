# Autonomous Cockpit UI Architecture & Visual Hygiene

This reference outlines the technical and aesthetic blueprint for building public-facing autonomous agent observability cockpits (such as Hermes Studio) that adhere to the **"Cute, Elegan, Simple, Keren, Berwarna"** archetype while enforcing strict zero-emoji rules.

## 1. Aesthetic Foundations (Candy Cyber Obsidian)

1. **Canvas & Ambient Backdrops**:
   - Primary dark-mode backdrop: `#0e0f17` or `#13141f` (velvety obsidian slate).
   - Multi-radial ambient aurora: Injected via CSS `radial-gradient` fixed backgrounds using semi-transparent pastel tints (lavender `#818cf818`, mint `#34d39912`, sky-blue `#38bdf814`) to prevent eye fatigue while preserving contrast.
   - Cards & Containers: Glassmorphism chassis (`background: rgba(22, 25, 35, 0.7)`, `backdrop-filter: blur(14px)`, `border: 1px solid rgba(255, 255, 255, 0.08)`, `border-radius: 16px` to `20px`).

2. **Zero-Emoji Mascot & Avatar Architecture**:
   - **Hard Invariant**: Never use Unicode emojis (`🤖`, `⚙️`, `📝`, `🔥`) or ambiguous decorative symbols (`⚡`, `✨`, `⚠️`) which render as jarring OS-specific graphic emojis on mobile devices.
   - **Vector SVG Alternative**: Deploy bespoke, inline geometric SVG icons placed inside rounded squircle badges (`width: 42px`, `height: 42px`, `border-radius: 14px`) with dual-color pastel gradients:
     - Strawberry Pink: `linear-gradient(135deg, #f472b6, #ec4899)`
     - Royal Purple: `linear-gradient(135deg, #a855f7, #6366f1)`
     - Rose Coral: `linear-gradient(135deg, #fb7185, #f43f5e)`
     - Sky Blue: `linear-gradient(135deg, #38bdf8, #0ea5e9)`
     - Mint Emerald: `linear-gradient(135deg, #34d399, #10b981)`
     - Warm Peach: `linear-gradient(135deg, #fbbf24, #f59e0b)`
     - Golden Amber: `linear-gradient(135deg, #f59e0b, #d97706)`
     - Cyan Teal: `linear-gradient(135deg, #2dd4bf, #06b6d4)`

3. **Status Chips & QA Verification Badges**:
   - Verified tasks must render an explicit status chip: `✓ QA PASS` with a mint green tint (`background: rgba(16, 185, 129, 0.15)`, `border: 1px solid rgba(16, 185, 129, 0.35)`, `color: #6ee7b7`, `font-size: 10px`, `font-weight: 700`).
   - Priority pills: High (`#f43f5e`), Normal (`#f59e0b`), Low (`#6366f1`).

## 2. Terminal Log Sanitization (Anti-ANSI Artifacts)

When streaming live worker daemon outputs (e.g., from PM2 or log files) directly to a web console, raw terminal control codes will bleed into the DOM as ugly artifacts like `\x1b[32m` or `^[[0m`.
Always strip ANSI escape sequences before inserting log lines:

```javascript
function stripAnsi(str) {
  if (!str) return '';
  return str.replace(/[\u001b\u009b][[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nqry=><]/g, '');
}
```

## 3. Tactile Floating Dispatch Console

To allow instant intervention without breaking user flow, implement a single-line or compact capsule dispatch bar:
- Sticky/Floating squircle container with smooth pill selects and inputs.
- Tactile bouncy button feedback:
  ```css
  .btn-dispatch {
    transition: transform 0.15s ease, filter 0.15s ease;
  }
  .btn-dispatch:hover {
    transform: translateY(-2px);
    filter: brightness(1.1);
  }
  .btn-dispatch:active {
    transform: scale(0.96);
  }
  ```

## 4. Modal Deliverable Inspection Pattern

Deliverables must be inspectable in-place with zero navigation disruption:
- Full-screen or slide-up modal overlay with `backdrop-filter: blur(10px)` and dark tint.
- Formatted markdown parser (handling code blocks, tables, bold text, and lists cleanly).
- Metadata header displaying task ID, assignee agent, completion time, and QA validation timestamp.
