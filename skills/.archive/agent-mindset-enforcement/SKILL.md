---
name: agent-mindset-enforcement
description: "Use when enforcing agent mindset through executable rules."
---

# Agent Mindset Enforcement

## User expectations
- Bagas wants learned work principles implemented as executable controls, not only prompt instructions.
- User strictly prefers concise, direct, to-the-point responses (padat, tanpa basa-basi). Never use conversational filler, meta-announcements of tool usage, or repetitive restatements of what the user asked.
- Explain proposed changes and obtain scope confirmation before implementation. Ask one focused question at a time.
- Preserve role-specific identity and memory when transferring reusable skills; skill copies do not guarantee identical reasoning or performance.

## Workflow
- Begin with an isolated prototype; prototype approval is not permission to deploy to live bots or other profiles.
- Model understand → evidence → scope/risk → plan → execute → verify → done/evaluate.
- Gate completion on independent checks of actual results, never model-supplied success, HTTP 200 alone, or exit zero alone.
- Bound retries; distinguish per-call budgets from persistent and wall-clock limits.
- For adaptive exploration of unfamiliar tasks: keep evaluation criteria strictly held out from model prompts; verify adaptation through recorded probe-mismatch-revision cycles rather than scripted sequences or first-try guesses.
- When an upstream model endpoint fails (e.g., HTTP 503), log the transport failure honestly and fall back to available alternatives; never fabricate completion traces.
- Test actual I/O failure, forged evidence, corrupt output, scope escape, overwrite/race cases, and retry exhaustion as well as success.
- Inspect current official Hermes plugin docs and installed source before selecting hooks. Verify exception and timeout behavior rather than assuming fail-closed enforcement.
- Exercise integration in an isolated Hermes runtime before claiming agent control. A standalone controller is not deployed enforcement. When validating plugin hooks in an isolated runtime, point `HERMES_HOME` to a temporary directory or an isolated profile, and declare the plugin under `plugins.enabled` in `config.yaml` (non-bundled plugins require explicit opt-in). Note that `PluginManager._system_prompt_sections` is a `dict` keyed by section ID (iterate `.values()`, not the dict directly).
- For plugin manifests (`plugin.yaml`), `hermes plugins validate` strictly validates `provides_tools`, `provides_hooks`, and `provides_middleware`. Using `tools:` or `hooks:` triggers undeclared capability failures during validation.
- Declare plugin tool handlers to accept `*args, **kwargs` (or `**kwargs`). Hermes passes runtime metadata such as `task_id` alongside user payloads; narrow signatures like `def handler(payload: dict)` raise runtime `TypeError`.
- For isolated sandbox verification without touching live Telegram/WhatsApp gateways, use `hermes profile create --clone --no-alias <name>`. By design, `--clone` excludes messaging tokens and adapter channels. Install the plugin under `~/.hermes/profiles/<name>/plugins/<plugin_dir>`, enable it via `hermes -p <name> plugins enable <plugin>`, and test single-turn queries via `hermes -p <name> chat -q "..." --oneshot -Q`.
- Exempt read-only inspection tools (`read_file`, `search_files`, `web_search`) from mutation idempotency gates to prevent false-positive blocks during repeated reference reads.
- Treat profile/workspace separation as organizational, not an OS security sandbox.
- Preserve prompt caching; avoid modifying shared core for profile-specific experiments.
- Sanitize audit events; never copy credentials or sensitive payloads into lessons.
- Attribute user mindset principles to Bagas Cihuy and Hermes framework to Nous Research. Do not claim controls eliminate hallucinations or transfer an entire mind.

## Reporting
Distinguish artifact built, tests executed, runtime integration verified, and live deployment status. Never conflate these milestones.
