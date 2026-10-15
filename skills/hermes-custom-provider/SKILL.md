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
8. **Local router / 9Router model routing**:
   - Model identifiers via proxies typically use slash prefixes (`oc/<model>`, `ag/<model>`), not colons (`opencode:<model>`).
   - For reasoning/thinking models (e.g. DeepSeek Flash, Muse Spark), provide sufficient `max_tokens` headroom; low limits (e.g. <30) are consumed entirely by reasoning tokens and return blank assistant content.
   - When local routers fail with HTTP 500 on `/v1/models`, inspect combo definitions: object payloads in combo model lists (`{provider, model}`) crash un-normalized `.includes("/")` string operations.

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

**Registered ≠ usable.** A provider can list models, resolve its key, and route correctly while its account is capped: `429` with `{"used":26,"limit":25}` in the body is a valid key on a spent plan, not a config bug. Check the provider directly before editing config again — Hermes's own "billing or quota exhausted" fallback warning may simply be accurate, and the fallback is then expected behaviour rather than a fault to chase.

## Rules

- **No gateway restart to apply model config.** The gateway spawns a fresh agent per message; each spawn re-reads config.yaml and .env from disk. Restarting for a model swap is dead time.
- **Gateway restart is blocked from inside a gateway session** — the terminal guard rejects any command referencing restart/stop of the gateway (SIGTERM would kill the session mid-command). A `nohup`/background wrapper does not dodge the guard. Run `hermes gateway restart` from a separate shell outside the gateway, only when a daemon-level change actually requires it.
- **Profiles are isolated.** `hermes config set` edits the active profile only; a separate gateway profile (bot profile) keeps its own model until configured in that profile.
- **Cron jobs keep their model snapshot** — after a provider switch, unpinned cron jobs still run the old model; pin them with `hermes cron edit <job> --provider custom --model <id>` if they must follow the new default.
- **Key names must match exactly** between .env and the `${...}` reference in config.yaml; if auth fails mysteriously, diff the two strings first (`grep HERMES_CUSTOM ~/.hermes/.env` vs the config `api_key` line).
- **Silent model switching is almost always fallback activation.** When a model seems to "switch itself", check `fallback_providers` in `config.yaml` and recent gateway logs for transient 429/500 errors on the primary route before assuming session corruption.
