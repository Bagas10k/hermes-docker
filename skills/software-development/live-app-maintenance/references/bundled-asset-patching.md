# Patching a Compiled/Standalone App Behind a CDN

Use when a live app ships only built output (Next.js `.next*`/standalone bundle, global npm package) and the change is a string, label, or small markup fix in a generated chunk rather than source you own.

## 0. Decide before touching anything

- Own the source? Rebuild. Bundle patching is the fallback for published-only artifacts.
- Is the target text a *string literal* in the chunk? If removing it needs structural JSX surgery, do not attempt paren/brace surgery on minified code; blank the literals instead. An empty `<p>`/`<code>` is invisible and safe.
- Take backups of every file you will edit before the first write: `cp file file.bak-<tool>`.

## 1. Locate the served build (not just the repo)

```bash
PID=$(ss -ltnp | grep ':20128' | grep -o 'pid=[0-9]*' | cut -d= -f2)
readlink /proc/$PID/cwd            # e.g. /home/ubuntu/.local/lib/node_modules/9router/app
tr '\0' ' ' < /proc/$PID/cmdline  # next-server (vX.Y.Z)
curl -s http://127.0.0.1:20128/dashboard | grep -oE '/_next/static/[^"]+' | sort -u
```

The HTML's `/_next/static/...` paths tell you which build dir is actually served (e.g. `.next-cli-build/static/...`). Editing any other build dir changes nothing.

## 2. Read the minified chunk safely

```bash
grep -c 'Default password is' static/chunks/app/login/page-<hash>.js
grep -o '.\{80\}Default password is .\{120\}' static/chunks/app/login/page-<hash>.js
```

Never `grep` without `-o` on a minified file — matches print the whole single-line bundle.

## 3. Patch literals, validate syntax

```python
pairs = [('children:["Default password is ",', 'children:["",'),
         ('children:"123456"', 'children:""')]
src = open(p + '.bak', encoding='utf-8').read()
for old, new in pairs:
    assert src.count(old) == 1, (p, old, src.count(old))
    src = src.replace(old, new)
open(p, 'w', encoding='utf-8').write(src)
```

```bash
node --check <patched>.js   # must pass before restart
```

Patch both the client chunk and the server-side copy of the same page module (`server/app/<page>/page.js`) when both contain the literal.

## 4. Bust the cache — the URL must change

With no CDN API token, renaming the asset is the reliable move:

```bash
OLD=page-<oldhash>.js; NEW=page-<newhash>.js
mv static/chunks/app/login/$OLD static/chunks/app/login/$NEW
python3 - "$OLD" "$NEW" <<'EOF'
import sys, subprocess
old, new = sys.argv[1], sys.argv[2]
for f in subprocess.run(['grep','-rl',old,'.'],capture_output=True,text=True).stdout.split():
    s = open(f, encoding='utf-8', errors='surrogateescape').read()
    open(f, 'w', encoding='utf-8', errors='surrogateescape').write(s.replace(old, new))
EOF
```

Typical reference set for one page chunk: `server/app/<page>.html`, `server/app/<page>/` (client-reference manifest), `server/app/<page>.rsc`, `server/app/<page>.segments/**`. Restart the service through its supervisor, then prove it:

```bash
curl -s https://<public>/login | grep -oE 'chunks/app/login/page-[a-f0-9]+\.js' | sort -u
curl -s https://<public>/_next/static/chunks/app/login/<newhash>.js | grep -c 'Default password'
```

Expect the HTML to reference the new name and the public chunk to grep clean. `cf-cache-status: HIT` with `age: 0` after a rename is fine — content is what matters.

## 5. Verify the rendered result, not just the file

Load the public page in a real browser and read `document.body.innerText`: assert the removed text AND the underlying value are both absent, the form/inputs/buttons still exist, and no console error appeared. This is the step that catches a half-patch that left a bare `123456` chip rendering.

## 6. Report the ceiling

Bundle patches live in a global npm package and disappear on the next `npm update`. State that explicitly, list the `*.bak` paths as the rollback, and do not claim a permanent fix.

## 9Router dashboard-password flow (same class, repeated task)

Service: `systemctl --user status 9router` (unit `9router.service`, port 20128, `custom-server.js`).

1. Auth state: `curl -s http://127.0.0.1:20128/api/auth/status` → `hasPassword`, `authMode`, `requireLogin`.
2. Login is password-only until changed: from localhost `POST /api/auth/login {"password":"123456"}` succeeds; from the public domain the same request returns `403 "Default password must be changed before remote access"`. So a published dashboard can be reachable yet unusable remotely — check this before calling a publish "done".
3. Get a local session: `curl -c jar -X POST http://127.0.0.1:20128/api/auth/login -H 'Content-Type: application/json' -d '{"password":"123456"}'` (localhost is trusted; cookie `auth_token`, 24h).
4. Change it through the app's own endpoint, never by editing the DB:
   `curl -b jar -X PATCH http://127.0.0.1:20128/api/settings -H 'Content-Type: application/json' -d '{"currentPassword":"...","newPassword":"..."}'` → expect 200 and `auth/status` `hasPassword:true`.
5. Secret handling: generate with `openssl rand -base64 24 | tr -d '/+=\n' | cut -c1-24`, write to `~/.9router/dashboard-password.txt` with `chmod 600`, and report only the path — never the value, in chat or tool output.
6. Verify in this order: old password from the public domain → 401; new password from the public domain → 200 `{"success":true}`; then `curl -b jar2 https://<public>/api/keys` and `/api/providers` → 200. Failed public logins decrement a lockout counter (5 fails → timed lock), so probe deliberately, not repeatedly.
7. Functional regression: inference must still work after the restart — `POST /v1/chat/completions` with the API key → 200 plus a real assistant message.

Health triage when only "is it fine?" is asked: `/api/health` may be open while `/api/status`, `/api/keys`, `/api/providers` require the session; `/v1/models` returns 401 for anonymous remote callers but 200 to a key. Provider truth lives in `/api/providers` → count `testStatus: active` vs `unavailable` per connection, and corroborate with `journalctl --user -u 9router --since '24 hours ago' | grep -oE "\[[0-9]{3}\]" | sort | uniq -c`.
