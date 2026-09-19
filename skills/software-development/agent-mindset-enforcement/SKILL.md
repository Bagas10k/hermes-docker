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
- Distinguish artifact built, tests executed, runtime integration verified, and live deployment status. Never conflate these milestones.
- Four-Pillar Progress Report: When the user asks for status, progress, or updates, immediately provide a structured report covering: (1) What has been completed (concrete deliverables), (2) Current operational stage/milestone, (3) Obstacles and blockers (explicitly confirm "NIHIL / AMAN" if clear), and (4) Empirical verification (active URL with HTTP 200, memory metric, or visual screenshot). Never reply with vague meta-announcements or ask for new tasks before reporting the status of in-flight work.
- Anti-Monologue Multi-Agent Execution: Never simulate or roleplay cabinet meetings as conversational text monologues. In multi-agent workflows, coordinate via real tools (`delegate_task`, isolated profile executions, or documented backlog entries via the assistant manager bot). Verify group allowlists (`allowed_chats` / `TELEGRAM_GROUP_ALLOWED_CHATS`) so all participating bots receive and process group events.
- Multi-Agent Orchestration & Data Handoff SOP: (1) General Manager controls the Three Pillars (Si Pintar, Si Eksekutor, Si Pengawas). (2) In planning, GM collaborates with Si Pintar via up to 5 refinement loops; Si Pintar acts as Chief Task Dispatcher broadcasting tasks concurrently (True Parallel Concurrency) to reduce latency by 60-70% via Amdahl's Law. (3) The Three Pillars deposit all data and logs to Bikagent; Bikagent does not audit technical execution (held by Si Pengawas), but logs data and directs reports to GM. (4) Upon task completion, Bikagent automatically harvests lessons learned into Obsidian. (5) Monitoring UI must maintain single source of truth between hierarchy and workflow views, auto-poll at 1000ms (no manual refresh), and provide interactive popups explaining the causal reason and payload of each data handoff.
- Background Automation vs. Interactive Standby Audit: When the user queries ongoing work or expresses frustration regarding token consumption ("sekarang lagi ngerjain apa / nyedot token terus"), never claim the system is "100% idle/standby" based solely on the interactive chat state. Always audit autonomous background schedulers (`~/.hermes/cron/jobs.json`, `~/.hermes/cron/executions.db`, and daemon logs). Background pipelines (e.g., automated crawlers, ML trend scoring, and scheduled publishers) consume tokens independently of active conversation. Report running jobs with absolute honesty and pause them (`cronjob_manage action='pause'`) when the user requests zero background token burn.
- Verification Latency & Token Optimization: Avoid chaining heavy Puppeteer headless browser renders and remote multimodal vision inspections (`vision_analyze`) on every incremental step. Vision API roundtrips introduce 15-20s latency and significant token overhead. Prioritize fast deterministic text/DOM assertions, HTTP status codes, and exit-code validation during iterative development, reserving full vision analysis for final milestone verification or explicit user request.
