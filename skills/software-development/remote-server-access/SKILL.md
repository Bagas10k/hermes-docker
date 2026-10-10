---
name: remote-server-access
description: "Use when connecting to a VPS via RDP or SSH."
---

# Remote Server Access

## First response

1. Establish whether the user wants a Windows graphical desktop (RDP) or a shell (SSH). Ask one short question if unclear; a screenshot of attempted SSH commands does not prove SSH is the intended protocol.
2. Confirm the provider-issued address, port, and username. Do not infer protocol from a custom port or silently replace the username with Administrator/root.
3. Give the shortest actionable connection instructions in the user's language. For a basic how-to, avoid filesystem searches and lengthy diagnostics before establishing the intended access method.
4. Troubleshoot only if the correct client still fails, using the exact new error. Do not ask the user to disclose passwords.

## Windows Remote Desktop

On a Windows client, press Win+R, enter `mstsc`, and put `HOST:PORT` in Computer. Equivalently, run `mstsc /v:HOST:PORT`. Enter the supplied username and password in the client.

Use the port from the provider's RDP details. Treat 3389 as the default, not evidence that the server uses it; do not recommend arbitrary port changes when a custom mapping was supplied.

Verify unfamiliar certificate details with the provider rather than unconditionally accepting warnings. Report success only after user confirmation or observable connection evidence.

## SSH

### Temporary access for the current agent instance

1. Distinguish the agent's actual execution host from the user's laptop or another Hermes Desktop instance. An SSH key on the laptop is not available to this chat's agent; installing another Hermes instance does not transfer this conversation's calibration. Ask which instance must operate before proposing a connection path.
2. If the current agent needs temporary VPS access, generate a dedicated Ed25519 keypair on its execution host with a unique filename and restrictive private-key permissions. Give the user only the public key to append to `~/.ssh/authorized_keys` on a least-privilege VPS account. Do not reuse or request their existing private key.
3. Obtain username, reachable host/IP, and port separately; test with `ssh -i KEY -p PORT -o BatchMode=yes -o ConnectTimeout=10 USER@HOST 'whoami; hostname'`. Confirm the host fingerprint through a trusted channel when security matters; `accept-new` alone trusts first contact and does not prove identity.
4. Start with read-only inspection and distinguish observed health from container status. For a deployed Docker web app, check repo status, `docker ps`, a local HTTP request, web/app logs, and restart counts; report contradictory signals such as HTTP 200 alongside recent 500s. Avoid dumping `.env`, Compose-resolved configuration, or full exception traces into the model: they may contain secrets. Do not change production data during a request to inspect setup.
5. After work, have the user remove the dedicated public-key line from `authorized_keys` and delete the agent-side private key. A temporary key remains valid until the server-side authorization is removed, not until the conversation ends.
6. For Bagas's production PT web apps, start read-only; get approval and verify a recoverable backup before database changes. Application code flows laptop → GitHub → VPS pull/build; keep VPS-only configuration and secrets out of Git and preserve them across deployments. Back up database and uploads encrypted off-VPS; test restore. Avoid sharing customer data or secrets in group chat.
7. When Bagas is learning to operate the VPS himself, explain the purpose and risk of each maintenance step before executing it; leave a short, reproducible operator command or manual rather than making him depend on the agent. If asked only to `git pull`, fetch and list incoming paths first, preserve local/skip-worktree config and ignored secrets, then fast-forward; do not rebuild containers or migrate the production database without a separate request. Verify HEAD, local config, and public HTTP afterward. `git pull` updates files on disk, not the running image. For an authorized deploy, inspect the incoming diff for migrations and mutating tests first; skip database backup/migration when no data path changes, and never run tests on production if setup flushes a shared cache or modifies production state. After recreating a PHP-FPM container behind Nginx, probe both local origin and public login: Nginx may retain the old container IP for a static `fastcgi_pass app:9000` and return 502 despite app being Up. Validate and reload Nginx, then wait/probe again before escalating; synchronize host-mounted frontend assets from the new app image and compare manifest hashes. Report any transient outage rather than claiming a clean deploy.
8. When diagnosing Laravel 500s after deploy, correlate URL and timestamp across web and application logs, then compare actual schema (`Schema::hasTable`/`hasColumn`) against the migrations table. `Ran` is historical metadata, not proof of present tables. For missing production schema, prefer a new tested reconciliation migration in the laptop/GitHub source; never reset migrations or replay old seed-bearing migrations blindly. A backup must include database AND uploads; check both restore and encryption-at-rest, because gzip and SSH transport are not encrypted storage.
9. When asked to maintain a confidential company VPS without seeing business data, enforce the boundary in OS capabilities rather than a conversational promise. First revoke the old broad SSH key; provision a distinct non-root account without `sudo`, Docker group/socket, database credentials, mounted customer data, raw logs, or read access to deployment secrets. Permit only root-owned, parameterless or strictly allowlisted fixed commands for sanitized health/status and tightly scoped deploy; avoid arbitrary shell arguments, shell-evaluable filenames, writable scripts, and generic `docker`/`sudo` wrappers, which defeat the boundary. Test both permitted operations and denied reads against database, uploads, and `.env` from that account before claiming separation. Production migration/restore stays with an authorized human. Explain that output sent to an external model can still contain sensitive data, and report remaining trust limits honestly.

### Zero-Password Security Protocol (Wajib)
1. **Dilarang Meminta/Menerima Password di Chat**: Password mentah yang diketik di percakapan akan tercatat di riwayat chat, log sesi lokal, dan konteks inferensi model. Selalu gunakan otentikasi kunci kriptografi (*SSH Keypair*).
2. **Alur Public Key Exchange**:
   - Periksa atau buat pasangan kunci Ed25519 lokal: `ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519` jika belum ada.
   - Pastikan izin privat terkunci ketat: `chmod 600 ~/.ssh/id_ed25519`.
   - Berikan baris isi `~/.ssh/id_ed25519.pub` ke pengguna untuk ditempelkan ke `~/.ssh/authorized_keys` di VPS remote.
3. **Eksekusi Perintah Non-Interaktif Agen**:
   - Selalu sertakan flag `-o BatchMode=yes -o ConnectTimeout=10` untuk mencegah agen *hang* tanpa batas saat remote meminta password atau prompt konfirmasi kunci:
     ```bash
     ssh -p PORT -o BatchMode=yes -o ConnectTimeout=10 USER@HOST "command"
     ```

For shell access, use `ssh -p PORT USER@HOST`, with an ASCII hyphen. Do not use `USER@HOST:PORT`: that syntax treats the port as part of the hostname.

Interpret failures at the correct stage:

- Hostname resolution failure with `HOST:PORT`: correct the command syntax.
- Connection refused: the connection was actively rejected; verify endpoint/service/firewall rather than changing credentials.
- Connection reset during key exchange: the connection ended before authentication; this is not evidence of a wrong password, and the cause is not yet established.
- Authentication failure: verify the assigned username and credential method without requesting secrets in chat.

Do not continue varying SSH flags after the user identifies RDP as the intended service; switch clients because the protocols are different.

## Migration and System Backup

When backing up or migrating a Windows RDP server, Hermes Agent installation, and project workspaces to a new device or VPS, use a single-execution automated bundle with a zero-friction installer. See [references/rdp-migration-backup.md](references/rdp-migration-backup.md) for the exact directory map, one-click restore script pattern, and Windows file-system pitfalls (reserved device names like `NUL`, ACL buffer sanitation, and archive exclusions).

