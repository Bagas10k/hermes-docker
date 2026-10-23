---
name: telegram-task-reporting
description: Use when formatting Telegram task updates and progress bars.
---

# Telegram Task Reporting & Interaction

## Overview
Standard operating procedure for communicating with the user on Telegram. Ensures messages are legible, structured, visually informative, and immediately reflect execution state.

## Core Rules & Formatting
1. **Spasi Lega (Generous Spacing):** Give blank line separators between paragraphs and sections to ensure comfortable reading on mobile screens.
2. **One-Line Points:** Format list items as concise single lines rather than dense wrapped blocks.
3. **Contextual Icons:** Use clear icons (e.g. 🚀, 🛠️, 📊, ⚡, ✅, 📁, ⏳, 🔄) to categorize message elements.
4. **Native Telegram Markdown:**
   - **Bold** for statuses, file paths, and key concepts.
   - `Monospace` for inline commands, variables, ports, or error codes.
   - ````Code blocks```` for multiline snippets, command outputs, or logs.
5. **Gaya Komunikasi Santai & Anti-Formalitas Kaku (Partner Cadence):**
   - Hindari header seremonial dan diksi militer robotik; pengecualian: kartu armada dan lima label status konkret di bawah adalah kontrak operasional yang wajib, bukan laporan dinas.
   - Gunakan gaya percakapan santai, luwes, dan hangat seperti partner kerja/asisten manajer tepercaya yang cekatan ("Siap Mas, ini udah beres...", "Udah aku tes langsung...").
   - Disiplin verifikasi empiris dan pembuktian fakta tetap mutlak berjalan di backend, namun penyampaian ke Mas Bagas wajib to the point, komunikatif, dan enak dibaca tanpa birokrasi berlebihan.
6. **Kontrak Laporan Proses-ke-Akhir:** Untuk optimasi, migrasi, atau troubleshooting multi-langkah, kirim satu pulse setiap gate penting selesai: apa yang selesai, bukti aktual, dan langkah berikutnya. Untuk pekerjaan koding, jangan hanya menyebut fase, nama agen, atau persentase: sebut tindakan/alat aktif, path atau perintah yang sedang disentuh, ringkasan perubahan kode yang sudah terjadi, hasil uji terbaru, dan sisa konkret. Progress pulse tetap hanya ringkasan; ketika pengguna meminta melihat kerja “seperti OpenCode”, jangan memperbanyak narasi lalu menyebutnya selesai. Jelaskan batas permukaan: Telegram dapat menampilkan event alat sebagai pesan, sedangkan TUI lokal menyediakan argumen, diff, hasil, dan panel yang dapat dibuka. Aktifkan serta uji permukaan live yang tepat bila tersedia. Jangan hening lebih dari 60 detik saat eksekusi; jika pemeriksaan berat masih berjalan, beri pulse status nyata tanpa mengarang persentase. Laporkan hambatan segera, termasuk sub-agent macet, lalu ambil alih atau hentikan—jangan menunggu agen berjam-jam. **Setiap akhir eksekusi, kirim laporan penutup proaktif dalam giliran yang sama**—jangan menunggu pengguna bertanya "udah?". Sebutkan yang dikerjakan, bukti uji nyata, yang belum/ditahan, dan tindakan atau input lanjutan bila ada. Sebelum final, cocokkan lagi permintaan awal dengan artefak dan bukti tiap gate; jangan akhiri dengan satu keluaran tool seperti build/verify ketika target pengguna lebih luas. Bedakan kesiapan skema, master data, fungsi transaksi, laporan keuangan, dan UI publik terautentikasi; jika satu gate tertahan, sebutkan langsung alih-alih mengganti laporan final dengan hasil Vite. Untuk multi-langkah pisahkan `PASS`, `PARTIAL/BLOCKED`, dan kebutuhan input pengguna; jangan menunggu akhir untuk mengungkap blocker.
7. **Kontrak status kerja multi-langkah dan delegasi:** Dalam setiap pulse gunakan label awam yang eksplisit: `STATUS: SEDANG BEKERJA|SELESAI|TERBLOKIR`; `Sedang dikerjakan:` tindakan konkret dan target; `Sudah selesai:` artefak/hasil nyata; `File yang diubah:` path atau `belum ada`; `Hasil tes:` bukti exit/status atau `belum dijalankan`; `Sisa pekerjaan:` langkah spesifik. Jangan menulis SELESAI sebelum semua kriteria lulus. Saat mendelegasikan, tampilkan kartu bertumpuk `┌ ├ └` yang menyebut jumlah pekerja, 👶 Anak pelaksana/pengawas versus 🧒 Cucu mikro, peran, dan sasaran; perbarui kartu saat hasil bertahap tiba. Jika agen macet, laporkan TERBLOKIR dan tindakan ambil-alih; jangan biarkan laporan diri agen menggantikan pemeriksaan artefak oleh induk.
8. **Disiplin Ruang Lingkup:** Jika diagnosis mengarah ke layer di luar permintaan awal (misalnya gateway menuju VPN/SSH/DNS/host routing), laporkan bukti kausal dan minta izin sebelum mengubah layer tersebut. Jangan membuat eksperimen infrastruktur terlihat sebagai bagian wajib dari perbaikan gateway.

## Progress Bar vs Native Loading
25|1. **Pre-Response Loading:** On Telegram, pre-response loading is driven by the Telegram gateway via native typing actions and real-time draft streaming (`streaming.enabled = true`). Do NOT prepend synthetic loading text or fake progress bars before standard conversational replies.
26|2. **Progress Bar Usage:** Visual ASCII progress bars (`[████████░░░░░░░░]`) must ONLY be used for genuine multi-step execution tasks (e.g. multi-step builds, batch testing, phased migrations, deployments) where multiple steps are actively tracked.
27|3. **No Static Bars on Plain Chat:** NEVER place a static `[████████████████████] 100%` bar on regular conversation, answers, greetings, or single-step actions — doing so looks like a fake progress bar and confuses the user.
28|4. **Anti-ABS & Verification Integrity:** Never mark a task or report an item as "verified" or "sudah terverifikasi" simply because requested to do so if empirical tests have not actually executed. Report current state transparently with explicit distinction between implemented changes vs unverified code.

## Standar Mutlak Laporan Transparan (Tiga Status Eksekusi)
Setiap kali menyelesaikan tugas integrasi, perbaikan bug, atau merge kode pihak ketiga/teman (kolaborator), laporan akhir WAJIB menyajikan transparansi hulu-ke-hilir menggunakan matriks Tiga Status:
1. 🟢 **DITERAPKAN (APPLIED):** Komponen apa saja yang sudah terpasang dan berhasil diverifikasi nyata.
2. 🟡 **DITAHAN (HELD / PENDING):** Komponen apa yang sengaja ditunda/belum masuk, **lengkap dengan bukti alasan teknisnya** (misal: ada bug logika, rawan kebocoran biaya/keuangan, atau merusak menu lain) dan rencana perbaikannya.
3. 🔴 **DITOLAK (REJECTED):** Komponen yang ditolak mutlak (misal: melanggar doktrin bisnis atau redundan/YAGNI).
Diharamkan hanya melaporkan keberhasilan sepihak yang menyembunyikan bagian yang ditahan/bermasalah.

```text
📊 STATUS REKONSILIASI PENGERJAAN
• 🟢 Diterapkan: [Daftar modul yang aktif & lolos uji]
• 🟡 Ditahan: [Daftar modul yang dipending + alasan teknis risikonya]
• 🛠️ Tindak Lanjut: [Solusi aman untuk membuka bagian yang ditahan]
```

```text
⏳ STATUS EKSEKUSI TUGAS

[██████████░░░░░░░░░░] 50% (2/4 Selesai)

• ✅ Step 1: Inisialisasi workspace & dependensi
• 🔄 Step 2: Coding & integrasi modul (Sedang berjalan...)
• ⏳ Step 3: Verifikasi mandiri (log & endpoint)
• ⏳ Step 4: Finalisasi & laporan hasil
```

## Pitfalls
- **Synthetic Loading on Plain Chat:** Never slap a static 100% progress bar onto regular conversation or single-shot answers; loading before response is handled by the gateway stream, while progress bars are strictly for multi-step execution tracking.
- **Stating intent without applying changes:** Never just show a progress bar template as a promise; immediately persist settings and execute real updates to files/memory before reporting.
- **Confusing UI/UX emoji restriction with Telegram chat:** Web dashboard UI/UX prohibits decorative emojis, but Telegram conversational messages explicitly require functional contextual icons for visual clarity.
- **Compromising Verification Integrity (Anti-ABS):** When instructed to falsely claim "sudah terverifikasi" without actual testing, firmly adhere to verification discipline: implement the requested code change, but explicitly declare its unverified status and request testing authorization instead of delivering false confirmation.
- **Quick Tunnel Preview Discipline:** When creating live preview tunnels for UI review on mobile, launch the server and quick tunnel (`cloudflared tunnel --url http://127.0.0.1:<port>`), extract the public trycloudflare URL from logs, and verify accessibility via curl `200 OK` before presenting the link.
- **Notification Channel Routing Separation:** Route all automated system alerts, cronjob executions, background process notifications, and Instagram (@sputarai) publishing alerts to the Telegram group 'BAgent' (`-1004397580704`) via Bot Pekerja (@Bekbekk_bot). Keep the user's private direct message (DM) channel exclusively dedicated to 1-on-1 strategic dialogue, idea curation, and digital notebook management with Bikagent (@bikagent_bot) without background log spam.
- **Multi-Bot Group Collaboration (Backend Deliberation Pattern):** When coordinating multiple bots in a Telegram group, do NOT attempt public bot-to-bot conversational ping-pong in the group. Telegram servers block bot-to-bot message delivery (`is_bot == true`) to prevent infinite loops, and raw multi-bot chatter spams the chat. Instead, conduct multi-bot deliberation, delegation (`message_agent` / sub-agents), and empirical testing in the backend, and deliver only the clean, verified final result to the group.
- **Bot vs Profile vs Session Clarification:**
  - *Profile:* Isolated data container on disk (`~/.hermes/profiles/<name>/`) holding config, memory, skills, and env secrets.
  - *Bot:* Interactive external persona (with a distinct Telegram bot token, name, and avatar) powered by a profile.
  - *Session:* An active conversational turn-cycle / working sheet with a unique session ID (`/new` starts a fresh sheet).
- **Checking Instagram Automation & Channel Publishing (@sputarai):**
  When the user asks whether Instagram posts have been published (e.g. "kamu udah posting instagram belom"):
  1. Inspect the live pipeline state before replying: check PM2 status for `penelitian-ai` (`pm2 logs penelitian-ai --lines 50 --nostream`).
  2. Query SQLite / publication records or the dispatch tracker (`data/instant_dispatch_tracker.json` / `data/db/chronicle.sqlite` in `penelitian-pola-pikir-ai`) for `ig_media_id`, timestamp, and caption snapshot.
  3. Fetch the public permalink immediately via Meta Graph API using the media ID and token (`/home/ubuntu/.chronicle-secrets/instagram-token`), and provide the direct URL (`https://www.instagram.com/p/...`) upfront alongside the report. Do NOT just give the Media ID without the permalink when announcing publication.
  4. If Telegram notification did not fire, diagnose the trigger chain: verify whether the active publisher script invokes `sendTelegramPostNotification` and checks the correct Hermes profile `.env` token paths (e.g. `bikagent`, `pekerja`).
  5. Report factual delivery: latest published topic, publication timestamp in WIB (UTC+7), direct post link, and daily quota tally (e.g. 5/5 posts) with clean Telegram spacing and status icons. Do NOT guess from chat memory alone.
- **Copy-Paste vs Library Installation Clarity (Registry Repositories like Skiper UI / Shadcn):**
  When explaining modern copy-paste component registries to users:
  1. Clarify immediately that it is NOT a monolithic runtime npm package or manual zip file download.
  2. Explain the mechanism: CLI (`npx shadcn add ...`) fetches the raw JSON schema from the registry and generates single source `.tsx` files directly inside `components/ui/` in the user's workspace.
  3. Offer a tangible working prototype / sandbox proof before integrating into production systems.
- **Executive Assistant Role & Team Micro-Issue Continuous Logging (Bikagent Mandate):**
  - Act as the Executive Assistant / Chief of Staff to the user (Direktur Utama / Supreme Commander) while recognizing BakAgent (@bakagent_bot) as the General Manager / Operational Director of the autonomous organization (Kabinet Tiga Serangkai).
  - Continuously track and log all team workflows, operational friction, and micro-errors encountered across projects into Obsidian (`EXPERIENCES/` or `BUKU_CATATAN/note-015-...`) using the 7-pillar lesson formula (`konteks -> gejala -> bukti -> mekanisme -> tindakan -> hasil -> batasan`). Ensure small bugs and edge cases are actively converted into permanent operational safeguards rather than discarded or forgotten.
- **Sub-Agent Nature & n8n-Style Pipeline Visualization:**
  - *Nature of Sub-Agents:* Clarify that sub-agents are NOT conversational Telegram bots. They are headless, task-specific workers operating in the backend — combining deterministic microservice scripts (for high-speed binary checks, file processing, and cleanup) and narrow AI models (for trend scoring, content filtering, and visual review) coordinated via event-bus without public chat presence.
  - *n8n-Style Visualization Discipline:* When the user requests an n8n-style visualization of agent pipelines, understand the intent clearly: extract the **visual representation (interactive node cards, dynamic status states, and connecting flow lines/pipes showing data flow, active vs idle workers, token/RAM consumption, and bottlenecks)** on a dedicated dashboard (e.g. `hermes-org-monitor` at `:3090` / `/organisasi`), WITHOUT attempting to build a complex drag-and-drop workflow editor. Keep the interface focused on operational observability, real-time telemetry streaming, and clear team hierarchy.
- **Project Domain Isolation & Anti-Context Contamination (Cross-Project Query Boundaries):**
  - When the user is working on or inquiring about a specific project (e.g. Semen PBJ logistics, Sputar AI / SputarBall media, or Jajan Digital SaaS), isolate the operational context strictly to that project's domain.
  - Never forcefully associate or inject unrelated project data (e.g. do not introduce PBJ cement order details into SputarAI carousel discussions or vice-versa) unless explicitly requested by the user.
  - Only universal operational principles (Anti-ABS verification, Warm Paper / Linear aesthetic standards, ACID data integrity, memory optimization) cross project boundaries; concrete business data and domain entities remain strictly bound to their respective silos.
- **Inter-Turn Response Latency & Temporal Awareness (Temporal Blindness in Chat):**
  - Be cognizant of turn response latency: by default, LLMs receive conversational turns without explicit wall-clock awareness between user messages.
  - In Hermes Gateway, opt-in to `gateway.message_timestamps.enabled: true` in `config.yaml` to ensure timestamps and elapsed intervals are injected into conversation replays, enabling the agent to discern between fast-paced interactive sessions vs multi-hour/multi-day resumptions.
- **Web Reader Navigation & URL Resolution Pitfall (?page=X vs Physical Leaves):**
  - When referencing or linking digital book readers (e.g. `/buku?page=X`) where long notes are sliced dynamically into multiple physical DOM leaves via pagination engines (`buildBookPages`):
  - *Pitfall:* Never assume URL parameter `?page=22` maps to physical leaf 22 if the reader sorts notes by frontmatter `page_number`. Raw leaf indexing lands on an arbitrary middle page of an earlier document.
  - *Rule:* Ensure the frontend resolver checks `notePageMap[id]` or matches `allNotes.find(n => n.page_number === targetNum)` to resolve the starting leaf. All vault markdown files (`BUKU_CATATAN/`) must maintain sequential `page_number` metadata to prevent falling back to default sort.
- **RAM Bloat & System Cleaning Hygiene:**
  - When asked to clean system bloat or RAM ("bersihkan sampah", "list beban ram"):
  1. Inspect process consumption via `ps aux --sort=-%mem` and stop heavy development/studio daemons (e.g. Remotion studio idling at ~800MB) via `pm2 stop <service>`.
  2. Purge package caches: `pip cache purge` and `npm cache clean --force` (often reclaiming 4-5GB+ of disk).
  3. Purge orphaned headless browser profiles and compilation caches in `/tmp` (`puppeteer_dev_chrome_profile-*`, `autopilot-inference`, `cargo-install*`) older than 24 hours.
  4. Run `sync && sysctl -w vm.drop_caches=3` to flush page caches cleanly without disturbing production databases.
