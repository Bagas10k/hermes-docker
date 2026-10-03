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

