---
name: agent-work-observability
description: Use when building dashboards for live agent work.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Live Agent Work Observability

Build operator dashboards that distinguish **observed execution**, **task alignment**, **verified correctness**, and **measured efficiency**. Never collapse these into an invented health score.

## Procedure
1. Trace the actual production page, API routes, and runtime event producer before redesigning. Identify which fields are live, static defaults, inferred, or delayed; preserve a working access path to old controls during an in-place replacement. Inventory the measurement sources that already exist before writing any new instrumentation: behavioral metrics usually live somewhere already (a capability/evidence table in a monitoring service, tool-call traces in the session store, a mutation ledger on disk). Query each with bounded reads and reuse it — a second collector for data that is already recorded creates two sources of truth that will disagree.
2. Inspect real payloads with bounded queries. Correlate event, tool, verification, and task records by trace/session ID. Treat `ACTIVE` database state or a recent message as insufficient evidence of a running agent when no recent runtime event exists.
3. Design the first viewport around four questions: what task is observed, what action just occurred and when, what evidence proves the result, and what remains unknown. Show source and freshness on each relevant status. On fetch failure or stale event, downgrade to `unknown`, not `online`.
4. Render untrusted summaries using `textContent`, not interpolated `innerHTML`; cap line length and sample sizes. Do not expose raw tool arguments, payload JSON, secrets, or private messages on a public dashboard. A page showing behavioral metrics (correction rate, typo rate, working habits) is private data even when it looks like a neutral dashboard: bind the service to `127.0.0.1`, not `0.0.0.0`, and proxy it through the existing authenticated path. "Put it on my domain" is not authorization to publish it — verify with an unauthenticated request that returns 401/303, not 200.
5. Label measurements precisely: tool success is not code correctness; tool p95 is not code efficiency; RAM usage is not token spend; recorded verification for another trace is not proof for the current task. If alignment with the user's request is not assessed against explicit criteria, say `belum dapat dinilai`. A capability with no supporting evidence is rendered `INSUFFICIENT DATA`, never a score: one fabricated number discredits every other number on the page. A high count of unmeasured capabilities is itself a useful finding about how deeply the system has been exercised.
6. Verify the public URL in a browser at desktop and mobile widths after the asynchronous data load completes; inspect populated fields, connection state, and horizontal overflow. A 200 response or syntax check alone does not prove the dashboard works. Exercise stale/disconnected rendering and preserve a path to underlying evidence.
7. Render charts server-side as inline SVG. It needs no chart library, survives a dead CDN, and works with JavaScript disabled — for an internal dashboard this outlasts pulling in a rendering library. Assert in the chart tests that every generated coordinate falls inside the `viewBox`, and cover the cases that break a naive renderer: a flat series (division by zero), an out-of-range value (clamp to the axis bound), and fewer points than the chart needs (emit a message, not a malformed path). When such a test fails, check the assertion before the renderer — a bar at maximum value legitimately equals the canvas width, and editing the code to satisfy a wrong assertion introduces a real bug.
8. **Hierarchical Subagent Tree Monitoring (Transparansi Nyata):**
   - Sediakan panel/window visual di samping area obrolan (`SubagentTreeMonitor`) untuk memantau kapasitas konkuren yang tersedia, jumlah Anak (Level 1), jumlah Cucu (Level 2+), status live (Bekerja, Selesai, Gagal), dan perkakas aktif. Pengguna harus dapat menyaksikan status dan progres agen secara transparan melalui panel monitor, bukan sekadar dipaksa percaya pada klaim teks laporan akhir.
9. **Zero-Scroll TUI & Zen Response Architecture (Claude Code / OpenCode Style):**
   - **Active Skill Shelf (`⚡ Skill`)**: Deklarasikan seluruh skill yang aktif pada turn tersebut di bagian teratas respon (`⚡ Skill <nama> — <peran>`) agar pengguna mengetahui panduan/doktrin yang sedang memandu agen.
   - **Shell Command Card**: Tampilkan eksekusi perintah terminal dengan format `# <deskripsi tugas>` diikuti perintah tebal dan stdout bersih tanpa wrapper berlebihan.
   - **Tool Activity Indicator**: Tampilkan penanda aksi akses file ringkas satu baris (`→ Read <path>`, `→ Edit <path>`).
   - **Batas Keras Diff 20 Baris (Side-by-Side Hunk Box)**: Perubahan kode wajib disajikan per-hunk/metode (bukan satu file utuh panjang) dengan format side-by-side (kiri: baris lama merah `-`, kanan: baris baru toska `+`) dan nomor baris ganda presisi. Batasi tampilan maksimal 20 baris per-hunk; jika melebihi, potong baris ke-19 dan tampilkan keterangan ringkas `... [+ N baris disembunyikan, total M baris]`.
   - **Dynamic Task Checklist**: Tampilkan alur rencana kerja multi-langkah dengan status tegas: `[✓]` selesai (abu-abu), `[ ]` langkah aktif (hijau/toska tebal), dan `[ ]` antrean (abu-abu).
   - **Penalaran Internal Ringkas (CoT)**: Penalaran internal wajib tampil sebagai animasi loading satu baris saat live, dan diringkas satu baris (`◈ Nalar (1.4s · 312 tok)`) saat settled. Dilarang menggelontorkan ratusan baris nalar mentah yang membanjiri ruang obrolan.
   - **Zero Conversational Slop**: Langsung sajikan aksi teknis nyata dan artefak kerja; hilangkan kalimat pembuka/penutup basa-basi AI. Rujukan implementasi lengkap ada di `references/zen-tui-spec.md` dan `scripts/zen_tui_engine.py`.
10. **Pusat Log Galat Tunggal (Centralized Error Log Detection):**
    - Saat menguji atau membuat kode baru, dilarang menebak atau mencari galat secara acak di sembarang berkas. Pemeriksaan wajib langsung merujuk pada pusat log error sistem (`~/.hermes/logs/errors.log`, log servis PM2 `~/.pm2/logs/`, atau keluaran compiler/test runner) untuk menemukan akar masalah (*root cause*) secara cepat dan presisi.

Prefer existing runtime endpoints and a bounded refresh mechanism over a new polling service. Measure before claiming lower token use, latency, or improved developer visibility. Summarize what is verified and what the instrumentation still cannot see in a few weighted points, not a feature tour.
