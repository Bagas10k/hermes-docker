# Backup, Clone, and Migrate a Hermes Install

Three tiers; start at the cheapest and only hand-build a tarball when a lower tier cannot deliver what the user asked for.

**Rung 0 — check the built-in first.** `hermes --help` ships `backup` and `import`: `hermes backup --help` zips the Hermes home, `hermes import <zip>` restores it. Read those `--help` texts before writing a tar command from scratch; a hand-built tarball is justified only when you need a specific exclusion set or a size target the built-ins do not give you.

| Ask | Tool | Gets | Does not get |
|---|---|---|---|
| "pindahkan konfigurasi/skill/memori saya" | `hermes profile export <name> -o <file>.tar.gz` → `hermes profile import <file>` on the new host | One profile's config, skills, memory, sessions | Other profiles, modified core source, host services |
| "kloning seluruh sistem" | hand-built tarball of `~/.hermes` + restore steps | Everything the user built, including patched core | Nothing outside `~/.hermes` (pm2 units, crontab, browser profiles) |

## 1. Measure before promising a size

```bash
du -h -d 1 ~/.hermes | sort -hr | head -n 25
du -sh ~/.hermes/hermes-agent/{.git,venv,node_modules} ~/.hermes/{cache,releases,installs,tools,profiles,skills}
```

Typical bulk in a long-lived install: `venv` (~1 GB), `node_modules` (~400 MB), `.git` (~500 MB), `cache`/`releases`/`installs` (~2 GB), `profiles/*/skills` (each profile re-copies the skill tree), `skills/.curator_backups`. None of it is needed to reproduce the system — it is rebuilt or re-cloned.

State the real number to the user instead of picking a transport first. A grown install is multi-GB; no chat platform accepts that as one file.

## 2. Capture the custom core changes as a patch, not as source

A git-installed Hermes is a checkout: local edits are usually a handful of files, so shipping `.git` (or the whole tree) is waste.

```bash
cd ~/.hermes/hermes-agent
git status --porcelain        # ' M' = tracked edit, '??' = new file
git rev-parse HEAD            # record the base commit
git diff > ~/backup/core.patch
```

Local work is edits **plus** new files; a patch alone loses the new ones. Capture both:

```bash
git ls-files --others --exclude-standard > /tmp/untracked.txt
tar -czf ~/backup/core-untracked.tar.gz -T /tmp/untracked.txt    # run from the repo root
```

On the new host: `git clone` + `git checkout <base-commit>` + `git apply core.patch` + `tar -xzf core-untracked.tar.gz -C <repo>`.

## 3. Build the essentials tarball

```bash
mkdir -p ~/hermes-backup && cd ~/.hermes
tar --ignore-failed-read -czf ~/hermes-backup/hermes-clone-essentials.tar.gz \
  --exclude='.hermes/skills/.curator_backups' \
  --exclude='*/node_modules' --exclude='*/.venv' --exclude='*/venv' \
  --exclude='*/__pycache__' --exclude='*.pyc' \
  --exclude='.hermes/profiles/*/sessions' \
  --exclude='.hermes/profiles/*/skills' \
  --exclude='.hermes/profiles/*/hermes-agent' \
  -C /home/ubuntu \
  .hermes/config.yaml .hermes/profile.yaml .hermes/context_length_cache.yaml .hermes/.env \
  .hermes/memories .hermes/hooks .hermes/plugins .hermes/cron .hermes/scripts .hermes/skills \
  .hermes/profiles
```

Why these exclusions: sessions/profile-skill copies/curator backups/junk add gigabytes and are not needed to stand the system back up. `--ignore-failed-read` keeps a single unreadable file from aborting a long tar. Skip `.hermes/cache`, `releases`, `installs`, `hermes-agent/venv` and `hermes-agent/node_modules` outright — they regenerate.

Also write a plain `CARA-PASANG.txt` next to the archive with the rejoin/extract/venv/symlink steps; the recipient may be future-you on a fresh box.

## 4. Restore recipe (hand this to the user verbatim)

```bash
cat hermes-clone-essentials.tar.gz.part-* > hermes-clone-essentials.tar.gz
tar -xzf hermes-clone-essentials.tar.gz -C ~
cd ~/.hermes/hermes-agent && python3 -m venv venv && ./venv/bin/pip install -e .
mkdir -p ~/.local/bin && ln -sf ~/.hermes/hermes-agent/venv/bin/hermes ~/.local/bin/hermes
hermes --version && hermes profile list
```

The venv must be rebuilt on the target — it hardcodes the source interpreter path. `.env` travels with the archive (keys + bot token), so the restore is one step.

Tar members are relative (`.hermes/...`), but config **values** are absolute. A grown `config.yaml` pins `/home/<olduser>/...` for every MCP server `command` and script path (15 such lines is typical). Same home path on the target = extract and go; a different home needs one rewrite right after extraction:

```bash
sed -i 's|/home/<olduser>|/home/<newuser>|g' ~/.hermes/config.yaml
grep -c '/home/<newuser>' ~/.hermes/config.yaml     # expect the same count you started with
```

Check `.env` separately — it normally carries no absolute paths.

## 5. Shipping a file to a Telegram chat

**Hard cap: the Bot API rejects documents over 50 MB.** Photos 10 MB, video 50 MB. Do not offer to push a multi-GB archive through a bot; say the limit out loud and give the split or a file-host link.

Resolve the target chat id from the token that is already on this host — never guess an id or ask the user to spell one out:

```bash
set -a; . ~/.hermes/.env; set +a
awk -F= '/^TELEGRAM_(HOME_CHANNEL|GROUP_ALLOWED_CHATS|ALERT_CHAT_ID)=/{print}' ~/.hermes/.env
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getChat?chat_id=<id>" \
  | python3 -c "import sys,json;r=json.load(sys.stdin).get('result',{});print(r.get('type'),r.get('title'))"
```

`getChat` returns `supergroup` + title, which is how you confirm the group name actually matches what the user called it before sending.

Split, then send each part (caption carries the rejoin command):

```bash
cd ~/hermes-backup && split -b 45M -d hermes-clone-essentials.tar.gz hermes-clone-essentials.tar.gz.part-
sha256sum hermes-clone-essentials.tar.gz | tee SHA256.txt

for f in hermes-clone-essentials.tar.gz.part-*; do
  curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendDocument" \
    -F chat_id=<id> -F document=@$f \
    -F caption="Backup Hermes ($f) - gabung: cat part-* > hermes-clone-essentials.tar.gz" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print('$f',d.get('ok'),d.get('result',{}).get('message_id'),d.get('description',''))"
done
```

45 MB leaves headroom under the 50 MB ceiling. Verify with the returned `ok: true` + `message_id` per part; a bot cannot fetch group history back, so the API response is the proof of delivery — quote the ids in the report. Send a final `sendMessage` with the SHA256 so the recipient can check the reassembled archive.

## 6. Say the security part once, plainly

The archive carries `.env`: model API keys and the Telegram bot token. Anyone who can read that chat can lift them. Warn in one line, tell the user to delete the uploads after downloading when the group has other members, and note key rotation as the remedy if it has already been shared. Do not silently strip `.env` — a clone without credentials is not a clone.

## Pitfalls

- **Don't offer "I'll send the whole 13 GB system"** — the bot ceiling is 50 MB/file; either split (and say how many parts) or upload to a host and send a link.
- **Don't claim "SELESAI" from the tar exit code alone** — the deliverable is the `sendDocument` `ok:true` per part.
- **Don't ship `.git`/`venv`/`node_modules` to save the user a rebuild step** — they are bigger than everything that matters and the rebuild is two commands.
- **Don't ask the user for the chat id or token** — both already live in `~/.hermes/.env` under the active `HERMES_HOME`.
