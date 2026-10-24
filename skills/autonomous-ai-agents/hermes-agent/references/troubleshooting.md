# Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes auth` — re-authenticate OAuth providers (or `hermes auth add <provider>`)
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### "Hermes feels slow" — verify the model route before blaming the host
Perceived lag is usually a dead model ID in the chain, not the machine. The
session keeps answering because Hermes walks the fallback chain on every
turn — so the symptom is latency, not an error.

1. Rule out the host in one call — `uptime; free -m; vmstat 1 3`. Rising
   swap with `si`/`so` near 0 is idle swap, not thrashing; only sustained
   `si`/`so` means memory pressure is the cause.
2. Probe each candidate model directly and read the BODY, not just the time:
```bash
curl -s --max-time 25 -o /tmp/r.json -w '%{time_total}s\n' \
  -X POST "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
  -d '{"model":"<id>","messages":[{"role":"user","content":"ok"}],"max_tokens":5}'
head -c 200 /tmp/r.json
```
   Always set `--max-time` per request: one hanging upstream otherwise
   stalls the whole batch and pushes the loop into the background.
3. Classify by body, because the failure modes look identical in latency:
   - `0.01–0.03s` + `"No active credentials for provider: X"` → the router
     lists the model but has no credential upstream.
   - `1–5s` + upstream `400/404` text → the model ID exists but the account
     behind it cannot serve that name; re-read the nested provider message.
   - `>20s` with no body → upstream hang; treat as down.
   - Real answer with `"content"` in `choices[0].message` → this ID is the
     one to pin. A fast `time_total` alone proves nothing.
4. List what the router advertises (`GET /v1/models`) but pin only IDs you
   actually got an answer from. Advertised ≠ credentialed.
5. Set it with the CLI setter, then re-run the same probe:
```bash
hermes config set model.default <verified-id>
```
   File-editing tools refuse `~/.hermes/config.yaml` by design — `hermes
   config set` is the sanctioned path, not a workaround.
6. The running session keeps its old model. `/model <id>` or a new session
   is required before the change is felt — say so instead of reporting the
   fix as already live.
7. Profiles pin their own `model.default`. `hermes profile list` prints each
   profile's model; if the dead family is pinned per-profile, switching
   profile brings the lag straight back.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### web_extract shows a stale page (result caching)
`web_search`/`web_extract` cache results for 20 minutes (PR #94618) — a
repeat fetch of the same URL within the TTL is served from cache, which
can look like "my website changes aren't showing up."

Automatic carveouts (always fetched live, never cached):
- localhost / 127.0.0.1 / `*.local` / `*.localhost` / single-label LAN
  hostnames / private + link-local IP ranges (dev servers, hot-reload
  builds, chat-GUI artifact previews)
- URLs matched by `security.website_blocklist`
- failed responses and keyless-rescue-served responses

Developing a site tested over the PUBLIC internet (Vercel/Netlify
preview, ngrok/cloudflared tunnel, staging domain)? Public DNS isn't
auto-carved-out — list the host in config.yaml:

```yaml
web:
  cache_exempt_hosts:      # always fetched live; effective immediately
    - mysite.vercel.app
    - "*.ngrok-free.app"
    - mysite.dev           # suffix match: also covers preview.mysite.dev
```

Blunt instruments: `web.cache_ttl_minutes: 1` (min) or
`web.cache_enabled: false` disables both caches entirely.

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `hermes -s name` (or the skill's own `/<name>` slash command)

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows-specific issues** (`Alt+Enter` newline, WinError 10106, UTF-8 BOM config, line endings): see `references/windows-quirks.md`.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

### "Reset permissions" / auto-approving everything
See `references/security-privacy.md` — wipe the "Always allow" stores, don't touch yolo mode.

