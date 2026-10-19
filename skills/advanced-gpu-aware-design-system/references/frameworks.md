# Framework adapters

## React / Next.js
Respect server/client boundaries. Prefer server components for static content in App Router; add client boundaries only for interaction. Keep tokens in CSS variables and component APIs typed. Use semantic HTML; preserve hydration determinism. Lazy-load expensive visual effects; clean up effects and listeners. Test with project's existing toolchain (ESLint, TypeScript, Vitest/Jest, Playwright where present).

## Tailwind
Read installed major version and configuration before writing utilities. Use existing design tokens/theme variables and avoid arbitrary values repeated across components. Use `@apply` sparingly and avoid duplicated utility abstractions. Keep class variants predictable and documented. Do not assume Tailwind v3 config semantics in v4 projects.

## Laravel Blade
Prefer Blade components for reusable UI, named slots/props, and semantic HTML. Keep business authorization/validation on server. Use Vite assets when project uses Vite. Maintain CSRF protections and escaping; avoid raw output of untrusted text.

## Livewire
Read installed Livewire version; preserve component state and `wire:model` behavior. For JS-enhanced UI coordinate DOM ownership with Livewire lifecycle; use `wire:ignore` only when justified. Preserve validation errors, loading states, navigation, and server round-trips. Test actions with Livewire's test utilities where installed.

## Cross-stack rules
Preserve backend routes, schema, migrations, API contracts, and environment configuration. Use CSS custom properties as cross-framework design-token bridge. Avoid adding a second styling framework without explicit tradeoff analysis. When source code is unavailable, provide scaffold and state assumptions clearly.
