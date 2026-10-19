# Design system engineering

## Visual hierarchy
Set clear page intent and information density before styling. Define a typography scale (body, label, heading, display), line-height, spacing rhythm, container widths, alignment grid, surface elevation, radii, and deliberate contrast. Use a distinctive brand voice grounded in content rather than arbitrary decoration. For dense ERP tables favor scanability, sticky headers when useful, right-aligned numeric data, clear filters, and readable empty/error states.

## Token layers
- Primitives: raw palette, spacing, radii, typography, shadow values.
- Semantics: background, surface, foreground, muted, border, primary, danger, success, focus.
- Components: button padding, field height, table row density, card border radius.
Map component -> semantic -> primitive. Keep light/dark values semantic; avoid hardcoded colors in components. Document token ownership, naming, versioning, and deprecation.

## Components and states
Minimum: Button, Input, Select, Checkbox, Dialog, Toast, Tabs, Card, Table, Sidebar, Header, Tooltip. For each specify variants, size, disabled/loading/error/empty, keyboard, focus, touch targets, responsive behavior, and accessible name. Prefer native controls. Treat modals with focus trap and focus return; avoid implementing complex ARIA patterns from scratch when vetted libraries exist.

## Layout and motion
Design for 320px+ mobile where feasible, tablet, desktop, high zoom (200% and 400% checks), and content expansion. Use grid/flex/container queries where appropriate. Define motion tokens: duration short 120-180ms, standard 180-300ms, long 300-500ms as starting points, not universal rules. Use ease-out for entrances, ease-in for exits; avoid moving critical controls. Reduced motion should remove nonessential movement, not information.

## Token example
See `../assets/tokens.example.json`. Use platform-specific transforms or CSS variables; do not assume the JSON format is native to every framework.
