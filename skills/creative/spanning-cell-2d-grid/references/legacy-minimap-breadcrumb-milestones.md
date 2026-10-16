# Historical minimap and breadcrumb milestones

These are historical verification claims, not current parent rerun results.

## Interactive SVG Mini-Map Radar & Drag Viewport Pan (v0.44.0 / UIUX-056)
`render_dag_minimap_svg`, corner `#dag-minimap-wrap`, draggable `#minimap-viewport-frame`, and bi-directional viewport pan synchronization (scripts/branch_dag_topology.py, scripts/history_browser.js, scripts/history_browser.py):
- Proportional Miniature SVG Radar Minimap (`render_dag_minimap_svg`):
  * Generates a lightweight proportional miniature SVG canvas ($180 \times 90\text{px}$) docked at the bottom-right of the DAG container (`#dag-minimap-wrap`).
  * Emits scaled branch edges (`.minimap-edge`), node dots (`.minimap-node` with active cursor highlighted in cyan `#38BDF8`), and background radar plate (`.minimap-bg`).
  * Encodes world topology bounds (`data-world-width`, `data-world-height`) and scaling factors (`data-scale-x`, `data-scale-y`) directly into SVG XML attributes.
- Interactive Draggable Viewport Bounding Frame (`#minimap-viewport-frame`):
  * SVG rectangle with semi-transparent cyan fill (`rgba(56, 189, 248, 0.15)`) and grab/grabbing cursor states.
  * Dynamically matches visible viewport proportion: $\text{width} = \min(W_{\text{map}}, W_{\text{container}} \times \text{scale}_X)$ and $\text{x} = \text{scrollLeft} \times \text{scale}_X$.
  * Direct mouse drag on the minimap radar updates container `scrollLeft` instantaneously and auto-clamps within bounds.
  * Scrolling `#dag-view` automatically updates the minimap frame position via event listener.
- Dynamic Zoom & Viewport Percentage Indicator (`#dag-minimap-status`):
  * Header label computes visible coverage ratio $\min(100, \text{round}(W_{\text{container}} / W_{\text{world}} \times 100\%))$.
  * Client API exposes: `window.historyPreview.minimapFrameBounds()` and `window.historyPreview.minimapPan(scrollLeft)`.

Verification v0.44.0 (UIUX-056): 309 Python unittest methods pass in 1.751s (covering minimap SVG generation, proportional scale attributes, viewport frame rect structure, active node dot styling, and manifest export integration). Node VM browser unit checks pass 100% (covering initial minimap frame bounds, drag pan synchronization, scrollLeft tracking, and viewport coverage percentage). Exit code 0.

## Minimap Collapsible Toggle & Keyboard Quick-Jump Navigation (v0.45.0 / UIUX-057)
`#dag-minimap-toggle`, collapsible `.dag-minimap-container.collapsed`, Alt+Number numeric keyboard shortcuts, and `breadcrumbJump` (scripts/history_browser.js, scripts/history_browser.py):
- Minimap Collapsible Toggle (`#dag-minimap-toggle`):
  * Header button toggle allowing users to minimize/expand the radar canvas on small viewports without losing spatial position.
  * Toggles `.collapsed` class on `#dag-minimap-wrap`, hiding the SVG radar canvas (`display:none`) while preserving the header status bar and toggle trigger.
  * Updates accessible attributes: `aria-expanded="false"` / `"true"` and text label ("Buka" / "Tutup").
  * Exposes programmatic APIs: `window.historyPreview.toggleMinimap(force)` and `window.historyPreview.isMinimapCollapsed()`.
- Keyboard Quick-Jump Ancestor Shortcuts (`Alt + Digit1..Digit9`):
  * Global keydown event listener binds `Alt + Digit1` through `Alt + Digit9` to directly checkout the $N$-th ancestor in the current lineage path.
  * `Alt+1` jumps instantly to `root` (index 0), `Alt+2` to the first child along the current branch lineage, and so forth.
  * Exposes programmatic API `window.historyPreview.breadcrumbJump(indexOrDigit)`.
  * Safe validation prevents out-of-bounds jumps, preserving current focus without error.

Verification v0.45.0 (UIUX-057): 310 Python unittest methods pass in 1.846s (covering minimap toggle button presence, collapsed class styles, aria-expanded attributes, and template rendering). Node VM browser unit checks pass 100% (covering toggle button click, programmatic collapse/expand, aria state sync, breadcrumb jump to ancestors, out-of-bounds guard, and Alt+Digit keyboard shortcuts). Exit code 0.

## Breadcrumb Visual Shortcut Badges & Minimap LocalStorage Persistence (v0.46.0 / UIUX-058)
`dag-breadcrumb-badge`, `localStorage` key `'dag_minimap_collapsed'`, and instant pre-load state hydration (scripts/history_browser.js, scripts/history_browser.py):
- Visual Numeric Shortcut Badges (`.dag-breadcrumb-badge`):
  * Injects compact monospace badges (`[1]`, `[2]`, ..., `[9]`) into ancestor breadcrumb buttons for the first 9 lineage nodes.
  * Provides immediate discoverability for `Alt+1` .. `Alt+9` quick-jump keyboard shortcuts without requiring hidden menu discovery.
  * Badges dynamically adapt styling on active nodes (`.dag-breadcrumb-item.active .dag-breadcrumb-badge`), maintaining WCAG contrast and unified visual hierarchy.
  * Public API exposes: `window.historyPreview.breadcrumbBadges()` for automated testing and status auditing.
- Minimap LocalStorage Persistence:
  * Automatically writes collapsed/expanded boolean state to browser `localStorage` under key `'dag_minimap_collapsed'` on user toggle.
  * Hydrates saved state upon initial page load (`setupMinimapToggle()`), restoring collapsed styling and ARIA attributes seamlessly prior to initial user interaction.
  * Resilient fallback gracefully degrades when `window.localStorage` is unavailable or restricted.

Verification v0.46.0 (UIUX-058): 311 Python unittest methods pass in 1.814s (covering breadcrumb badge CSS rules, minimap toggle markup, and manifest rendering). Node VM browser unit checks pass 100% (covering visual shortcut badge rendering `['[1]', '[2]', '[3]']`, breadcrumb items structure, localStorage sync on toggle, and pre-load storage hydration). Exit code 0.

## Minimap Scale Preset Multipliers & Breadcrumb Lineage Clipboard Export (v0.47.0 / UIUX-059)
`#dag-minimap-scale-controls`, `dag-breadcrumb-copy-btn`, multiplier presets (1x, 1.5x, 2x), and clipboard lineage serialization (scripts/history_browser.js, scripts/history_browser.py):
- Minimap Zoom Ratio Scale Presets (`#dag-minimap-scale-controls`):
  * Segmented button group (`1x`, `1.5x`, `2x`) allowing users to scale the minimap canvas ($180 \times 90\text{px}$, $270 \times 135\text{px}$, $360 \times 180\text{px}$) for high-density, sprawling DAG topologies with hundreds of nodes.
  * Dynamically resizes the miniature SVG canvas while maintaining exact world coordinate proportions, boundary clamping, and drag-pan synchronization.
  * Persists selected multiplier in `localStorage` under key `'dag_minimap_scale'` with seamless rehydration across page reloads.
  * Programmatic APIs: `window.historyPreview.minimapScale()` and `window.historyPreview.setMinimapScale(multiplier)`.
- One-Click Breadcrumb Lineage Clipboard Export (`.dag-breadcrumb-copy-btn`):
  * Dedicated "Salin Rute" button embedded in the breadcrumbs bar (`#dag-breadcrumbs`) that formats the active branch ancestry path into human-readable lineage syntax (e.g., `root > alpha > alpha_child`).
  * Interacts with `navigator.clipboard.writeText` with fallback to `document.execCommand('copy')`.
  * Provides transient tactile visual feedback (`Tersalin!` green badge) with automated reset after 1.5s.
  * Programmatic API: `window.historyPreview.copyLineage()`.

Verification v0.47.0 (UIUX-059): 312 Python unittest methods pass in 1.685s (covering minimap scale controls markup, copy button presence, CSS rules, and manifest rendering). Node VM browser unit checks pass 100% (covering lineage clipboard export formatting, visual feedback, 1x/1.5x/2x scale multiplier switching, SVG dimensions recalculation, drag pan tracking, and localStorage scale persistence). Exit code 0.

## Interactive Node Search & Filter Omnibar on Visual DAG Viewer (v0.48.0 / UIUX-060)
`#dag-search-bar`, `#dag-search-input`, `.node-item.search-match`, `.node-item.search-dim`, match counter, and camera auto-focus (scripts/history_browser.js, scripts/history_browser.py):
- Interactive Search & Filter Omnibar (`#dag-search-bar`):
  * Dedicated search input bar mounted directly above the SVG DAG container with live match badge (`#dag-search-count`) and clear button (`#dag-search-clear`).
  * Instant sub-millisecond filtering across node IDs and granular diff JSON metadata (`diff.summary`, `diff.added`, `diff.modified`, `diff.deleted`).
  * Dynamic visual state discrimination: matches receive prominent amber glow halos (`.search-match` with stroke `#f59e0b` and drop-shadow) while non-matching nodes are dimmed smoothly (`.search-dim` with opacity `0.25`).
  * Camera auto-centering smoothly pans the SVG viewport to the first matched node upon query change.
  * Keyboard accessibility: pressing `Escape` clears active search and restores full graph visibility immediately.
  * Public APIs: `window.historyPreview.search(query)` and `window.historyPreview.searchQuery()`.

Verification v0.48.0 (UIUX-060): 313 Python unittest methods pass in 1.424s (covering search omnibar controls markup, input presence, count badge, clear button, CSS highlight/dim rules, and manifest rendering). Node VM browser unit checks pass 100% (covering search query initialization, ID filtering, diff metadata mutation matching, DOM class list updates, clear trigger, Escape key dismissal, and public API search state). Exit code 0.

