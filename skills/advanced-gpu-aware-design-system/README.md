# Hermes installation and usage

Unzip this archive and copy `advanced-gpu-aware-design-system/` into the skill directory used by your Hermes runtime, e.g. `~/.hermes/skills/advanced-gpu-aware-design-system/` if Hermes loads that location. Confirm your Hermes skill loader supports `SKILL.md` and reload/reindex skills as required by your installation. This package does not automatically modify Hermes or install dependencies.

Example request: "Use advanced-gpu-aware-design-system to redesign this Laravel Livewire ERP dashboard; keep routes and database relations unchanged; deliver tokens, reusable components, reduced-motion support, screenshots and test evidence."

The scripts require Python 3.8+ and use only the standard library. `token_audit.py` verifies references; `css_motion_audit.py` only warns about potential performance risks. Browser benchmarking and real GPU tests must be run separately on the target project.

## Updated visual direction
Choose dimensional composition to match the task: tactile/editorial 2.5D for product or story-led interfaces, spatial/isometric overviews when relationships benefit from depth, or straightforward 2D when that is clearer. User references and existing brand constraints override default templates. Start with `references/usage-recipes.md` and `references/dimensional-composition.md`; the operations command-center palette is optional, not universal.
Note: Strict constraints apply — no emoji in UI, no rainbow/neon text gradients, no ornamental kicker badges, neutral synthetic dummy data only, and 3D is progressive enhancement never mandatory on transactional flows.
