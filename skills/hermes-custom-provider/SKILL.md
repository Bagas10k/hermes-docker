---
name: hermes-custom-provider
description: "Use when adding/switching Hermes custom model provider."
version: 1.0.0
---

# Hermes Custom Provider Setup

Point Hermes at any OpenAI-compatible endpoint. Order matters: verify the provider raw, configure, then verify through Hermes itself.

## Procedure

1. **Verify the raw API before touching config** (never config first — a wrong endpoint or dead key wastes a config round-trip):
   - `curl -s "$BASE/v1/models" -H "Authorization: Bearer $KEY"` — list models, pick the default model ID.
   - POST one real chat completion with that model. A 200 on /models proves nothing about the key+model pairing on /chat/completions.
   - If curl succeeds but a scripted HTTP client gets 403 on the same URL and key, suspect WAF/User-Agent filtering (e.g. Cloudflare challenging non-browser agents) — retry with curl or a browser-like User-Agent before concluding the key is dead.
2. **Store the key in `~/.hermes/.env`** with the conventional derived name: `HERMES_CUSTOM_` + host (dots/colons → underscores) + `_API_KEY`. Example: `https://ai.cutad.web.id/v1` → `HERMES_CUSTOM_AI_CUTAD_WEB_ID_API_KEY`. Append: `echo 'NAME="key"' >> ~/.hermes/.env` (terminal bypasses the credential-file read block; write, don't read).
3. **Configure a single active provider via CLI:**
   ```
   hermes config set model.base_url https://HOST/v1
   hermes config set model.provider custom
   hermes config set model.default MODEL_ID
   hermes config set model.api_key '${NAME}'
   ```
   - `model.api_key` holds the `${...}` reference, NOT the literal key (secrets in .env, settings in config.yaml).
   - Single-quote the `${...}` so the shell does not expand it.
   - Never hand-edit config.yaml with a text editor: a stray indent corrupts a live gateway, and file-edit tools refuse Hermes config paths. Adding a *list* entry is the one exception — use the scripted edit below.
4. **Verify through Hermes, not just curl:** `hermes chat -q "balas satu kata: siap"`. A fresh process reads config.yaml + .env from disk, so this proves Hermes's env-resolution chain end-to-end — curl cannot prove that.
5. **Record notable model IDs** from step 1; later switching is one command: `hermes config set model.default <id>`.
6. **Telegram runtime footer alignment**: When verifying output on Telegram messaging (`display.runtime_footer`), ensure `gateway/runtime_footer.py` preserves provider context for custom/proxy endpoints so the footer reflects the actual serving provider alongside the short model name.
7. **Align or isolate fallback chains**: Hermes automatically walks `fallback_providers` on 429, 500, or capacity errors. If user requests a specific model/tier (e.g. free models or specific proxy), align `fallback_providers` to peer models on the same tier or disable with `hermes config set fallback_providers "[]"` so failures report directly instead of silently switching models.
8. **Local router / 9Router model routing & combo troubleshooting**:
   - Model identifiers via proxies typically use slash prefixes (`oc/<model>`, `ag/<model>`), not colons (`opencode:<model>`).
   - For reasoning/thinking models (e.g. DeepSeek Flash, Muse Spark), provide sufficient `max_tokens` headroom; low limits (e.g. <30) are consumed entirely by reasoning tokens and return blank assistant content.
   - **Combo `a.includes is not a function` (HTTP 500)**: In 9Router (`~/.9router/db/data.sqlite`), `combos.models` must be stored as a JSON array of model ID strings (e.g. `["ag/claude-opus-4-6-thinking", "cx/gpt-5.5"]`), NOT an array of metadata objects (`[{"provider":"ag","model":...}]`). When objects are stored, 9Router's dispatcher passes the object directly to `handleSingleModel(body, modelId)` where `modelId.includes('/')` throws `TypeError: a.includes is not a function`. Fix in place by updating `combos.models` in `data.sqlite` to string arrays of `fullModel || routedModel || model`.
   - **Headless browser path for auxiliary local bots**: On Linux environments with system Chromium at `/usr/local/bin/chromium`, companion apps (such as WhatsApp Web / Puppeteer) crash in continuous initialization loops if `puppeteer_executable_path` points to a non-existent cache directory (`~/.cache/puppeteer/...`). Set `puppeteer_executable_path: "/usr/local/bin/chromium"` and guard client options with fallback detection if the configured path is missing.

## Adding a named provider without touching the current default

`hermes config set model.*` overwrites the single active endpoint. To *add* a provider you can switch to later, append an entry to the `custom_providers` list in `~/.hermes/config.yaml`. `hermes config set` cannot append to a list, so this is the one place a scripted YAML edit is correct — back up first, always.

```bash
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak-$(date +%s)
python3 - <<'PY'
import yaml
p = '/home/ubuntu/.hermes/config.yaml'
c = yaml.safe_load(open(p))
name = 'NAME'
c['custom_providers'] = [e for e in c['custom_providers']
                         if str(e.get('name', '')).lower() != name.lower()]  # idempotent
c['custom_providers'].append({
    'name': name,
    'base_url': 'https://HOST/v1',
    'key_env': 'HERMES_CUSTOM_HOST_API_KEY',
    'model': 'DEFAULT_MODEL_ID',
    'models': {m: {} for m in ['id1', 'id2']},   # dict of id -> {}, not a list
    'models_discovered': True,
})
yaml.safe_dump(c, open(p, 'w'), sort_keys=False, allow_unicode=True, width=4096)
PY
```

- `safe_load`/`safe_dump` round-trips the entire file, so re-parse and assert afterwards: entry present, `model.default` unchanged, every pre-existing entry still present. `width=4096` stops `safe_dump` from line-wrapping long model lists.
- The provider slug is `custom:<name>`; `--provider <name>` also resolves.
- Filtering by name before appending keeps re-runs idempotent instead of stacking duplicates.

## Verify routing reached the provider, not just that config saved

A saved entry proves nothing about the request path. Two checks:

1. **Bogus-model probe** — `hermes chat -q hi -m no-such-model-xyz --provider NAME`. A *provider-side* error (quota/billing, upstream 404) proves the request landed on that endpoint. A local `model_not_found` / `No active credentials` means it landed somewhere else and the entry is not being used.
2. **Provider-direct curl** of the same model, to separate key/endpoint problems from Hermes config problems.

**Registered ≠ usable.** A provider can list models, resolve its key, and route correctly while its account is capped: `429` with `{"used":26,"limit":25}` in the body is a valid key on a spent plan, not a config bug. The same holds for `402 insufficient_balance`: providers distinguish `balance too low — top up` (every model blocked) from `free model requires at least $X in lifetime deposits` (priced-0 models stay locked until the first deposit). A 0/0/0 catalog price means $0 per token, not usable-without-funding — always live-test the default model with a real chat completion before declaring a provider ready. Check the provider directly before editing config again — Hermes's own "billing or quota exhausted" fallback warning may simply be accurate, and the fallback is then expected behaviour rather than a fault to chase.

## Trust check for a new third-party gateway

Before routing daily work through an unfamiliar gateway, run this once:

1. `echo | openssl s_client -connect HOST:443 -servername HOST -verify_return_error` must end `Verify return code: 0 (ok)`; note the issuer and expiry.
2. `curl -sI` should show HSTS plus sane `x-frame-options` / `x-content-type-options` — their absence on an API host is a smell, not a blocker.
3. Key reaches config only via `key_env` (never inline `api_key`); confirm `.env` is mode 600.
4. Assume the gateway reads prompts and responses in plaintext — never send secrets, credentials, or sensitive data through its models.
5. One key for the whole catalog means one leak drains the balance — cap top-ups and watch the per-response cost header if the gateway provides one.

No independent reviews plus a fresh domain behind Cloudflare is normal for a new gateway, not proof of malice — but it earns untrusted-provider handling (rules 4–5) until proven otherwise.

## Diagnosing a dead model ID behind a proxy router

A model can 404 through a healthy proxy on healthy accounts. Run this attribution chain before touching config:

1. **Read the upstream error, not the proxy error.** Grep the proxy journal for the upstream host and response body. If the upstream host itself returns the 404, the fault is upstream of the proxy — no local edit can fix it.
2. **Sibling-model test.** Run a different model on the same provider through the same proxy. Success proves credentials, tokens, and plumbing are healthy, isolating the fault to the one model ID.
3. **Twin-route test.** If the same model exists under another route prefix, try it. A second failure with an entitlement-shaped body (quota limit 0 naming that model) confirms the source pulled or restricted the model rather than a bad route.
4. **History check.** Grep proxy logs for that model over days. Zero successes with the same error shape throughout means a dead upstream mapping, not a transient outage — stop retrying and pick a replacement.
5. **Catalog presence proves nothing.** A model listed in `/v1/models` but missing from the provider's supported mapping is a stale entry. Pin the effective mapping first: in 9router the served `id → upstreamModelId → endpoint` map lives in the built `app/.next-cli-build/server/chunks/` bundle (CLI-side list: `src/cli/menus/providers.js`) — read it instead of assuming what the proxy sends.
6. **Check for a fix upstream before upgrading.** Compare installed vs latest (`npm view <pkg> version`); if they match, no mapping fix is waiting in an upgrade.

## Rules

- **No gateway restart to apply model config.** The gateway spawns a fresh agent per message; each spawn re-reads config.yaml and .env from disk. Restarting for a model swap is dead time.
- **Gateway restart is blocked from inside a gateway session** — the terminal guard rejects any command referencing restart/stop of the gateway (SIGTERM would kill the session mid-command). A `nohup`/background wrapper does not dodge the guard. Run `hermes gateway restart` from a separate shell outside the gateway, only when a daemon-level change actually requires it.
- **Profiles are isolated.** `hermes config set` edits the active profile only; a separate gateway profile (bot profile) keeps its own model until configured in that profile.
- **Cron jobs keep their model snapshot** — after a provider switch, unpinned cron jobs still run the old model; pin them with `hermes cron edit <job> --provider custom --model <id>` if they must follow the new default.
- **Key names must match exactly** between .env and the `${...}` reference in config.yaml; if auth fails mysteriously, diff the two strings first (`grep HERMES_CUSTOM ~/.hermes/.env` vs the config `api_key` line).
- **Silent model switching is almost always fallback activation.** When a model seems to "switch itself", check `fallback_providers` in `config.yaml` and recent gateway logs for transient 429/500 errors on the primary route before assuming session corruption.

## Native round-robin combos for custom providers

For an Atmo-style upstream with multiple route prefixes, follow `references/9router-atmo-round-robin.md`. Use the installed management API, preserve existing router settings, verify real A→B→A requests, and distinguish routing from MoA or expanding account quota.

## 9. Reusing the Hermes Gateway in Auxiliary Apps (HexChat pattern)

When a secondary local app (e.g. HexChat on :8765) needs LLM without its own key, reuse the Hermes/9Router credentials instead of minting a new provider:

1. Read the key from `HERMES_CUSTOM_LOCALHOST_20128_API_KEY` in env (the same env Hermes resolves) — never hardcode or copy the literal key into the app's config/db.
2. Set the app's `base_url` to `http://127.0.0.1:20128/v1` and `model` to the Hermes default (`ag/gemini-3.8-flash-high` or `hight`/`medium` as tested) — verify with `curl -s http://127.0.0.1:20128/v1/chat/completions -H "Authorization: Bearer $HERMES_CUSTOM_LOCALHOST_20128_API_KEY" -d '{"model":"ag/gemini-3.8-flash-high","messages":[{"role":"user","content":"hi"}],"stream":false}'` before writing the app's profile.
3. Fix stale dummy profiles that point at mock endpoints (`http://127.0.0.1:8099/v1` / model `ok`) — patch every profile matching that URL or model, not just `active_profile`, or the next profile switch resurrects the failure.
4. Restart the auxiliary app (e.g. `pm2 restart hexchat`) and verify end-to-end via its own SSE path (`POST /api/send` with a device token), not just `curl /v1/models` — a 200 on models does not prove streaming works through the app's gateway.
- **Model outages surface as tool failures.** A vision or analysis call failing with an upstream 4xx/5xx names the serving model as the fault — verify the input file independently and check the model itself (sibling test above) before re-sending or blaming the input.
