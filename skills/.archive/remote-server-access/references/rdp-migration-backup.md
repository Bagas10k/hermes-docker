# Windows RDP / VPS One-Click Migration & Backup

Use when migrating an active Hermes Agent, background daemons, secrets, and project workspaces between Windows RDP/VPS servers or preparing a full system backup.

## Core Migration Architecture

A complete migration bundle consists of 5 modular components:
1. **Hermes Agent Identity (`%LOCALAPPDATA%\hermes`)**:
   - Files: `config.yaml`, `.env`, `auth.json`, `channel_directory.json`, `SOUL.md`, `context_length_cache.yaml`, `gateway-pm2.config.js`.
   - Directories: `memories/`, `skills/`, `cron/`, `profiles/`, `sessions/`.
   - Exclude: `runtime/`, `node/`, `git/`, `cache/`, `audio_cache/` (these are heavy binaries easily recreated on the target).
2. **System Secrets (`C:\ProgramData\chronicle-secrets`)**:
   - API tokens, Meta Graph API tokens, 9router credentials, and admin pin hashes.
3. **Knowledge Vaults (`C:\Users\bagas\otak koding`)**:
   - Markdown vaults and knowledge graphs.
4. **Active Projects (`%USERPROFILE%\Desktop\...`)**:
   - Application source code (excluding `node_modules`, `.git`, temporary upload caches, and rendered image caches).
5. **Daemon Snapshot (`%USERPROFILE%\.pm2\dump.pm2`)**:
   - Generated via `pm2 save` prior to packaging.

## One-Click Restore Pattern (`PASANG_DI_DEVICE_BARU.bat`)

Always generate a self-contained batch installer inside the root of the backup bundle:
- Uses `%LOCALAPPDATA%`, `%USERPROFILE%`, and `%~dp0` dynamic path resolution so it works regardless of username or drive letter differences.
- Automatically creates target directories if missing.
- Silently xcopies files into their exact original system locations:
  - `%LOCALAPPDATA%\hermes\`
  - `C:\ProgramData\chronicle-secrets\`
  - `C:\Users\bagas\otak koding\`
  - `%USERPROFILE%\Desktop\<projects>\`
  - `%USERPROFILE%\.pm2\dump.pm2`
- Instructs the user to run `pm2 resurrect` to immediately restore all daemon processes.

## Multi-OS Universal Installer Pattern (`restore.js` & `pasang_di_device_baru.sh`)

When the migration destination may be a Linux VPS (Ubuntu/Debian) or macOS rather than Windows:
- Provide `pasang_di_device_baru.sh` and a universal Node.js script `restore.js`.
- Use `process.platform` to dynamically map paths:
  - Windows: `%LOCALAPPDATA%\hermes` and `C:\ProgramData\chronicle-secrets`.
  - Linux / macOS: `~/.hermes` and `~/.chronicle-secrets` (or `/etc/chronicle-secrets`).
- Allows seamless one-command setup across Windows, Linux, and macOS without manual folder placement.

## GitHub Private Repo Migration & the 100MB File Limit Pitfall

- **Strict Privacy Requirement**:
  - *Mechanism*: Migration bundles contain live API tokens, bot tokens, and agent memories.
  - *Rule*: Repositories containing migration bundles must ALWAYS be created as `--private` on GitHub (`"private": true`). Never push to a public repository.
- **GitHub 100MB Hard File Limit (`GH001: Large files detected`)**:
  - *Mechanism*: A monolithic archive (`.zip`) containing projects, media caches, or big index files can easily exceed 100 MB. GitHub pre-receive hooks unconditionally reject pushes with any single blob over 100 MB.
  - *Rule*: Do not push monolithic `.zip` archives into Git. Instead, push the extracted directory tree directly (`hermes_core/`, `projects/`, etc.) with a `.gitignore` that excludes binary tools (`cloudflared.exe`, node binaries), `.git/`, and media caches (`ig-cache/`, `video-cache/`).

## Critical Pitfalls & Hard-Won Lessons

- **Windows DOS Reserved Device Names (`NUL`, `CON`, `PRN`, `AUX`)**:
  - *Mechanism*: Shell redirections in bash/MSYS (e.g. `> NUL`) can inadvertently write a physical file named `NUL` to the filesystem. When PowerShell's `Compress-Archive` encounters `NUL`, its .NET `FileStream` throws `CompressArchiveUnauthorizedAccessError` / `NotSupportedException`.
  - *Rule*: Always explicitly filter out `['NUL', 'nul', 'CON', 'PRN', 'AUX']` or delete literal `NUL` files before compression.

- **Strict ACL / File Lock on `C:\ProgramData` Secrets**:
  - *Mechanism*: Node's `fs.copyFileSync` copies file permissions and ACL metadata from protected system folders, triggering `EPERM: operation not permitted` on Windows.
  - *Rule*: Use binary buffer streaming (`fs.writeFileSync(dest, fs.readFileSync(src))`) when backing up credentials to sanitize inherited ACLs.

- **Lightweight Archive Sizing**:
  - *Mechanism*: Bundling `node_modules`, git packfiles, and rendered media cache (`public/ig-cache/*.png`) inflates archives to gigabytes, causing timeouts on upload/download.
  - *Rule*: Exclude `['node_modules', '.git', '.tmp.driveupload', 'session', '.next', 'cache', 'ig-cache/*.png']`. The core identity is ~70-150 MB and packages in seconds.

- **Telegram Bot API Upload Timeout & Large Archive Delivery (>15 MB)**:
  - *Mechanism*: Uploading archives >15 MB directly via Telegram Bot API (`sendDocument`) over RDP uplink frequently times out at the SSL/socket write layer (`TimeoutError: The write operation timed out`).
  - *Rule*: For archives >15 MB, split into ~4MB chunk files (`hermes_backup.zip.part01of05`, etc.), upload each part sequentially with a 1-second delay, and provide a single-line reconstruction command:
    - *Windows (PowerShell)*: `Get-Content hermes_backup.zip.part* -Raw -AsByteStream | Set-Content HERMES_MIGRATION.zip -AsByteStream`
    - *Linux/macOS*: `cat hermes_backup.zip.part* > HERMES_MIGRATION.zip`
    Verify byte-level parity (`reconstructed == original`) before deleting temporary chunk files.

- **Cron Runner Script Directory Omission (`~/.hermes/scripts/`)**:
  - *Mechanism*: Relative runner scripts in Hermes `jobs.json` resolve strictly under `~/.hermes/scripts/`. If the `scripts/` folder is excluded or wiped during OS migration, recurring jobs immediately crash with `Script not found: ...`.
  - *Rule*: Always back up and restore `scripts/` alongside `cron/jobs.json`, or deploy idempotent shell/Python wrappers upon initial bootstrap.

- **Cross-OS Folder Naming Mismatch (Spaces vs Hyphens)**:
  - *Mechanism*: Restoring Windows project folders containing spaces (e.g., `dasbor jajan digital`) as hyphenated folders on Linux (e.g., `dasbor-jajan-digital`) breaks hardcoded relative `require('../dasbor jajan digital/...')` paths in sibling projects.
  - *Rule*: Create backward-compatible directory symlinks (`ln -s /path/dasbor-jajan-digital "/path/dasbor jajan digital"`) on the Linux destination immediately after extraction.
