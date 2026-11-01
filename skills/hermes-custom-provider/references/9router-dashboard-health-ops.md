# 9Router Dashboard, Auth & Health Operations

Operating the router itself (not just a model behind it): publishing the dashboard, setting its password, verifying provider/combo health, and patching the built UI. Service: `systemctl --user` unit `9router.service`, port `20128`, data in `~/.9router/db/data.sqlite`, build in `~/.local/lib/node_modules/9router/app/.next-cli-build/`.

## Endpoint / auth map

| Surface | Auth | Notes |
|---|---|---|
| `GET /api/health` | public | `{"ok":true}` — cheapest liveness probe |
| `GET /v1/models`, `POST /v1/chat/completions` | `Authorization: Bearer <api key>` | remote callers get `401 API key required for remote API access` without it; local calls pass |
| `POST /api/auth/login` `{password}` | public | sets `auth_token` cookie (httpOnly, 24h) |
| `GET /api/keys`, `/api/providers`, `/api/settings`, `/api/combos` | session cookie | `401` without it |
| `PUT /api/combos/{id}` `{name, models:[...]}` | session cookie | combos: `GET/POST` on `/api/combos`, `GET/PUT/DELETE` on `/api/combos/{id}` |

- **Reuse the issuing host for authenticated calls.** The `auth_token` cookie is host-scoped: a cookie minted at the public domain returns `401 Unauthorized` against `127.0.0.1:20128`, and vice versa. Log in again against the same host you intend to call.
- **Don't guess HTTP verbs.** `PATCH /api/providers/{id}` answers `405`; the method set is discoverable without brute force by grepping the route bundle for `PUT:()=>` / `DELETE:()=>`:
  ```bash
  grep -oE 'POST:\(\)=>|PUT:\(\)=>|PATCH:\(\)=>|DELETE:\(\)=>|GET:\(\)=>' \
    <app>/.next-cli-build/server/app/api/combos/route.js
  ```

## Dashboard password lifecycle

- Fresh install has **no password**; login compares against `INITIAL_PASSWORD` or the literal `123456`. Remote login with the default is refused: `403 Default password must be changed before remote access` — the dashboard is effectively localhost-only until a password exists.
- Set it over the app's own API from localhost (the same call the dashboard makes):
  ```bash
  curl -c jar.txt -X POST http://127.0.0.1:20128/api/auth/login \
    -H 'Content-Type: application/json' -d '{"password":"123456"}'
  # generate, never hand-type, the replacement secret
  PW=$(openssl rand -base64 24 | tr -d '/+=\n' | cut -c1-24)
  printf '%s\n' "$PW" > ~/.9router/dashboard-password.txt && chmod 600 ~/.9router/dashboard-password.txt
  curl -b jar.txt -X PATCH http://127.0.0.1:20128/api/settings \
    -H 'Content-Type: application/json' \
    -d "{\"currentPassword\":\"123456\",\"newPassword\":\"$PW\"}"
  ```
  Comes back with the whole settings object — check `headroomEnabled` etc. while you are there. Verify with `GET /api/auth/status` → `hasPassword:true`, old password → `401`, new password → `200` plus `GET /api/keys` 200 on a fresh cookie jar.
- Never echo the new password into the transcript or a chat message. Print only length/mode and the file path; the user reads the file.
- The public login page prints `Default password is 123456` from a hardcoded string in the built client bundle, and keeps printing it after a password is set (only the `Security risk` line is conditional). Fixing it means patching the bundle — see below — and the patch is lost on `npm update`.

## Health verification that actually means something

1. `/api/health` first (liveness), then a real completion per model you care about — `GET /v1/models` listing 213 models proves nothing about routing.
2. **`testStatus` / `errorCode` on `/api/providers` is unreliable.** Connections report `unavailable` with `400/401/404/429/502/503` while still serving traffic. Never disable or delete a connection on `testStatus` alone — run a completion against a model it backs first. Conversely, a 400 like `The '<model>' model is not supported when...` is a per-model test failing, not a dead account.
3. **Cross-check every combo member against the live catalog.** A combo entry that is not in `/v1/models` fails 100% of the time (surfaced as `503` wrapping the upstream error), which looks like provider outage but is a stale config:
   ```bash
   python3 - <<'EOF'
   import json, sqlite3, urllib.request
   ids = {m['id'] for m in json.load(urllib.request.urlopen('http://localhost:20128/v1/models'))['data']}
   c = sqlite3.connect('file:/home/ubuntu/.9router/db/data.sqlite?mode=ro', uri=True)
   for name, models in c.execute('select name, models from combos'):
       miss = [m for m in json.loads(models) if m not in ids]
       print(('RUSAK ' if miss else 'OK    ') + name, models, miss or '')
   EOF
   ```
   Replace the dead member through `PUT /api/combos/{id}` with a model already proven by a completion — keep the primary untouched and change only the broken fallback.
4. Reasoning models under a low `max_tokens` return empty `content`; retry with headroom before calling the model broken.
5. A completion without `"stream": false` may come back as SSE `data:` chunks — parse accordingly.

## Headroom (context compression client)

Settings key `headroomEnabled` points the router at `http://localhost:8787/v1/compress`. If nothing listens there, every request pays a failed connect and writes a log line (`[HEADROOM] skipped: request failed: ECONNREFUSED 127.0.0.1:8787`) — thousands per day. Confirm with `ss -ltn | grep 8787`; if empty, disable through the settings API rather than starting a service nobody asked for:
```bash
curl -b jar.txt -X PATCH https://<host>/api/settings -H 'Content-Type: application/json' -d '{"headroomEnabled":false}'
```
Verify by sending one completion and grepping the journal since that moment — zero `HEADROOM` lines is the pass condition.

## Patching the built dashboard UI (Next.js chunk)

`/_next/static/*` is served `cache-control: public, max-age=31536000, immutable` and Cloudflare keeps a copy for a year, so **editing a chunk in place changes nothing for public visitors**. `cf-cache-status: HIT` with a stale body is the proof. Two things are needed:

1. **Patch by literal replacement, never by element surgery.** Removing a JSX element by paren-matching breaks minified code (`null("p",{...})` → `SyntaxError: Unexpected token ','`). Replace the text children instead, then assert syntax:
   ```bash
   python3 - <<'EOF'
   pairs = [('children:["Default password is ",', 'children:["",'), ('children:"123456"', 'children:""')]
   for p in ['<app>/.next-cli-build/static/chunks/app/login/page-<hash>.js',
             '<app>/.next-cli-build/server/app/login/page.js']:
       src = open(p + '.bak-9r', encoding='utf-8').read()   # bak = pristine copy taken first
       for o, n in pairs: src = src.replace(o, n)
       open(p, 'w', encoding='utf-8').write(src)
   EOF
   node --check <app>/.next-cli-build/static/chunks/app/login/page-<hash>.js
   ```
2. **Bust the cache by renaming the asset.** Copy the chunk to a new hash name, then rewrite every reference — for the login page that is five files: `server/app/login.html`, `server/app/login/page_client-reference-manifest.js`, `server/app/login.rsc`, `server/app/login.segments/_full.segment.rsc`, `server/app/login.segments/login/__PAGE__.segment.rsc`. Find them with `grep -rl <oldname> .`, then `systemctl --user restart 9router`. The served HTML now points at the new name and Cloudflare fetches it fresh (`age: 0`). No Cloudflare API token needed; a full purge is the alternative when you have one.
3. Keep `*.bak-9r` copies for rollback and tell the user the patch disappears on the next `npm update`.

## Boot persistence

`systemctl --user is-enabled 9router` must say `enabled` **and** `loginctl show-user <user> -p Linger` must say `Linger=yes`; without lingering a user unit does not start after reboot with nobody logged in. Unit already carries `Restart=always`.

## Reading the installed app without drowning in minified code

Grep on a Next production bundle dumps hundreds of kilobytes into context in one hit. Always bound it: `grep -o '.\{80\}SEARCHTERM.\{120\}' file`, or grep the `src/` tree when present, or the route bundle only (`server/app/api/<route>/route.js`).