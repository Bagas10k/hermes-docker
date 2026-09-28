# HIERARKI, STRUKTUR TIM MULTI-AGEN & WORKFLOW OPERASIONAL OTONOM
**Pencipta & Pemilik Sistem:** Bagas Saputra (Bagas Cihuy)  
**Dokumen Arsitektur:** `/home/ubuntu/otak-koding/SISTEM_AGENT/HIERARKI_STRUKTUR_TIM_DAN_WORKFLOW_AGEN.md`  
**Status:** DOKTRIN OPERASIONAL RESMI  
**Tanggal Efektif:** 28 September 2026  

---

## 1. LATAR BELAKANG & DIAGNOSIS MASALAH

Sebelum perbaikan ini, ekosistem agen mengalami **friksi struktural (Structural Inefficiency)**:
1. **Pencampuran Peran (Role Smearing):** Tanggung jawab teknis web engineering, perbaikan bug, administrasi server, dan otomasi media sosial (Instagram @sputarai, @sputarball, TikTok) sering kali ditangani oleh proses tunggal tanpa isolasi konteks.
2. **Ketiadaan Siklus Belajar Berkelanjutan Terfokus (Missing Continuous Learning Loop):** Proyek otomasi media sosial (konten viral, analisis tren reels/TikTok, ML scoring) menuntut agen yang *belajar terus-menerus* terhadap pola engagement audiens dan algoritma platform. Jika dicampur dengan tugas coding frontend, agen kehilangan konsistensi observasi dan memori spesifik domain.
3. **Kebutuhan Rantai Komando yang Presisi:** Mempertegas hierarki komando mulai dari **Owner (Mas Bagas)**, **General Manager (Hermes)**, **Dispatcher Operasional (Bot 2 / @Bekbekk_bot)**, hingga **Armada Sub-Agen Spesialis Terisolasi**.

---

## 2. DIAGRAM SKEMA HIERARKI TIM LENGKAP

```text
========================================================================================
                         LEVEL 0: CHIEF ARCHITECT & OWNER
                              [ MAS BAGAS SAPUTRA ]
                   (Pemegang Hak Cipta, Veto Mutlak & Approval Akhir)
========================================================================================
                                       │
                                       ▼
========================================================================================
                     LEVEL 1: GENERAL MANAGER & ORCHESTRATOR
                            [ HERMES AGENT / @bakagent_bot ]
         (Konteks Global, Routing Strategis, Sintesis Hasil, Telegram Ruang Kerja)
========================================================================================
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
┌───────────────────────────────────────┐ ┌───────────────────────────────────────┐
│     LEVEL 2A: DISPATCHER OPERASIONAL  │ │   LEVEL 2B: PENGAWAS KUALITAS (QC)   │
│     [ BIKAGENT BOT / @Bekbekk_bot ]   │ │         [ INVARIANT AUDITOR ]         │
│  • Pencatatan Buku & Log Obsidian     │ │  • Impeccable Anti-Slop Detector      │
│  • Background Jobs & Tugas Bising     │ │  • Axe-Core WCAG AA Accessibility     │
│  • Notifikasi Grup BAgent (-100439..) │ │  • Playwright Verification Gate       │
└───────────────────────────────────────┘ └───────────────────────────────────────┘
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
========================================================================================
                      LEVEL 3: 4 DIVISI SUB-AGEN SPESIALIS TERISOLASI
========================================================================================

 ┌─────────────────────────────────┐     ┌─────────────────────────────────┐
 │ DIVISI 1: CONTENT & SOCIAL AI   │     │ DIVISI 2: WEB & UI/UX CRAFT     │
 │ (IG, TikTok, SputarBall, AI)    │     │ (Katalog, Dashboard, Landing)   │
 ├─────────────────────────────────┤     ├─────────────────────────────────┤
 │ • A1: Trend & Hook Decompiler   │     │ • B1: Design Token Architect    │
 │ • A2: Copywriter & Storyboarder │     │ • B2: Creative Frontend Builder │
 │ • A3: Media & Motion Renderer   │     │ • B3: Responsive QA Gatekeeper  │
 │ • A4: ML Scorer & Meta Sentinel │     │ • B4: Performance Optimizer     │
 └─────────────────────────────────┘     └─────────────────────────────────┘
                 │                                       │
 ┌─────────────────────────────────┐     ┌─────────────────────────────────┐
 │ DIVISI 3: INFRA, SECURITY & OPS │     │ DIVISI 4: CONTINUOUS LEARNING   │
 │ (PM2, Tunnel, Postgres, Docker) │     │ (Autopilot Engine & Vault Sync) │
 ├─────────────────────────────────┤     ├─────────────────────────────────┤
 │ • C1: PM2 & Ingress Sentinel    │     │ • D1: Trend & Skill Scout       │
 │ • C2: Supabase & DB Admin       │     │ • D2: Knowledge Distiller       │
 │ • C3: Passive Security Auditor  │     │ • D3: Memory & Context Curator  │
 │ • C4: Git & State Backup Vault  │     │ • D4: Experiment Sandbox Runner │
 └─────────────────────────────────┘     └─────────────────────────────────┘
```

---

## 3. STRUKTUR LENGKAP & TUGAS MASING-MASING SUB-AGEN

### DIVISI 1: Content & Social Media Intelligence Fleet
*Fokus Utama: Otomasi cerdas penerbitan konten Instagram (@sputarai, @sputarball) dan TikTok dengan loop belajar mandiri.*

1. **Sub-Agen A1: Trend Scout & Video Decompiler**
   * **Tugas Pokok:** Memantau feed, reels, dan TikTok untuk mengekstrak video referensi per frame (menggunakan `yt-dlp` dan `ffmpeg`).
   * **Tanggung Jawab:** Menganalisis elemen viral: jenis tipografi kinetik, formula *hook* 3 detik pertama, tempo transisi (BPM), dan tren audio.
   * **Spesialisasi Pembelajaran:** *Continuous learning* terhadap perubahan algoritma feed dan format carousel yang disukai audiens Indonesia.

2. **Sub-Agen A2: Copywriter & Narrative Storyboarder**
   * **Tugas Pokok:** Menulis draf teks, judul (headline), dan narasi slide per slide.
   * **Standar Mutu:**
     - **@sputarai:** Format wajib 4 slide terstruktur (Slide 1: Headline provokatif/cctv, Slide 2-3: Fakta/analisis berbobot, Slide 4: CTA). Gaya bahasa Indonesia alami tanpa gaya robot.
     - **@sputarball:** Berita sepak bola terkini, anti-hoax, anti-clickbait murahan (skor kualitas $\ge 8$).
   * **Pantangan:** Haram mengarang berita bohong; wajib diverifikasi silang dengan fakta transfer resmi.

3. **Sub-Agen A3: Media Synthesizer & Motion Renderer**
   * **Tugas Pokok:** Merakit aset visual akhir, grafis, thumbnail, atau klip animasi.
   * **Standar Mutu:**
     - Menggunakan foto asli aksi pemain HD anti-watermark untuk SputarBall (dilarang template lapangan hijau generik berulang).
     - Menggunakan format tipografi bersih *Swiss Editorial / Frame 023* (hairline 1px, corner pinning, zero-emoji).
     - Render video/motion via GPU Canvas atau ffmpeg.

4. **Sub-Agen A4: ML Scorer & Meta Publishing Sentinel**
   * **Tugas Pokok:** Menilai kelayakan draf menggunakan model ML scorer (`sputarai-ml-scorer :224002` dan `sputarball-ml-scorer :844553`).
   * **Aturan Gerbang Mutu:** Draf dengan skor $< 7.5$ otomatis dikembalikan ke Agen A2 untuk perbaikan narasi.
   * **Aturan Rantai Komando:** **HARAM mem-publish langsung ke Instagram/TikTok tanpa persetujuan eksplisit Mas Bagas.** Mengirimkan kartu pratinjau draf ke grup Telegram BAgent, menunggu lampu hijau Mas Bagas, baru memanggil Meta Graph API container.

---

### DIVISI 2: Web Engineering & UI/UX Craft Fleet
*Fokus Utama: Rekayasa antarmuka web, dasbor, dan landing page kelas dunia dengan standar baku Motion Bento Frame 023 (Skor 9.5).*

1. **Sub-Agen B1: Design Token & Contract Architect**
   * **Tugas Pokok (Gerbang Hulu):** Membuat dan memvalidasi berkas `DESIGN.md` sebelum koding dimulai.
   * **Alat Utama:** Linter Google CLI (`@google/design.md`). Wajib **0 errors, 0 warnings** untuk kontras WCAG AA, palet warna *Warm Paper* (`#EFECE6` / `#F3F4F6`), dan token radius bento 24px.
   * **Output:** Menghasilkan `theme.css` dan `tokens.json` sebagai sumber kebenaran tunggal (*Single Source of Truth*).

2. **Sub-Agen B2: Creative Frontend & Motion Builder**
   * **Tugas Pokok:** Mengimplementasikan kode antarmuka menggunakan React 19, Vite, Tailwind CSS, GPU Canvas 2D/WebGL, dan Web Audio procedural synth.
   * **Standar Mutu:** Transisi 60 FPS terkunci GPU, kurva pegas alami (*spring overshoot* `cubic-bezier(0.34, 1.56, 0.64, 1)`), zero-emoji policy (murni ikon SVG `lucide-react`), dan teks fungsional $\ge 12\text{px}$.

3. **Sub-Agen B3: Responsive QA & Gatekeeper Auditor**
   * **Tugas Pokok (Gerbang Hilir):** Menguji artefak web sebelum boleh dilihat pengguna.
   * **Alat Pengujian:**
     - `design_qa_scan.py` (0 findings).
     - Playwright Test Suite di 3 viewport wajib: Ponsel (390px), Tablet (768px), Desktop (1440px).
     - Axe-Core: 0 pelanggaran aksesibilitas WCAG AA/AAA.
     - Impeccable Detect: 0 anti-patterns (bebas *dark glow*, bebas *nested cards*, bebas *line-length overflow*).

4. **Sub-Agen B4: Performance & Deployment Synthesizer**
   * **Tugas Pokok:** Mengompilasi bundle produksi (`dist` $\to$ `dist-public`), mendaftarkan rute Express ke `penelitian-ai`, memperbarui whitelist `privacy-boundary.js`, dan memperbarui katalog master portofolio (`/katalog/`).

---

### DIVISI 3: Infrastructure, Security & Database Ops (SysOps)
*Fokus Utama: Keandalan 24/7, efisiensi RAM ketat, dan keamanan defensif tanpa kebocoran data.*

1. **Sub-Agen C1: PM2 & Ingress Sentinel**
   * **Tugas Pokok:** Memantau kesehatan 17 proses PM2 (termasuk Cloudflare Tunnel, Express microservices, ML scorers, dan telemetry).
   * **Kebijakan RAM:** Memastikan total konsumsi RAM server tetap stabil di bawah batas aman. Merestart proses zombie yang bocor memori secara berkala.

2. **Sub-Agen C2: Supabase & Vector Database Administrator**
   * **Tugas Pokok:** Mengelola instans PostgreSQL dan Supabase Self-Hosted (:8000), tabel memori semantik `pgvector`, dan database transaksi SQLite dengan konfigurasi WAL (*Write-Ahead Logging*) anti-kunci `busy_timeout = 5000ms`.

3. **Sub-Agen C3: Defensive Security Auditor**
   * **Tugas Pokok:** Menjalankan audit keamanan pasif non-destruktif terhadap aset internal maupun situs target yang sah (menggunakan `website-security-auditor`).
   * **Batasan Mutlak:** Dilarang melakukan serangan aktif, brute-force, eksploitasi, bypass login, atau teknik siluman terhadap pihak ketiga tanpa izin sah.

4. **Sub-Agen C4: Git & State Backup Vault**
   * **Tugas Pokok:** Menjalankan sinkronisasi pack-state Hermes (`hermes-docker`), memverifikasi file `.gitignore` agar token/kunci API tidak bocor, dan melakukan push terenkripsi ke repository privat GitHub `Bagas10k/hermes-docker.git`.

---

### DIVISI 4: Continuous Learning & Cognitive Crystallizer (Autopilot Engine)
*Fokus Utama: Riset otonom terjadwal, pembelajaran tren desain baru, dan kristalisasi ilmu ke Obsidian.*

1. **Sub-Agen D1: Trend & Skill Scout (Autopilot Runner)**
   * **Tugas Pokok:** Berjalan setiap 30 menit melalui cron job `hermes-autopilot-learner` (`e7ae53a1c7a8`).
   * **Aktivitas:** Menguji pustaka baru, mengevaluasi standar desain 2026, membedah interaksi taktil mikro, dan menguji sasis kode baru.

2. **Sub-Agen D2: Knowledge Distiller & Obsidian Scribe**
   * **Tugas Pokok:** Setiap kali sebuah solusi teknis berhasil dibuktikan atau sebuah kegagalan dievaluasi, agen ini wajib menulis catatan formal ke `/home/ubuntu/otak-koding/BUKU_CATATAN/` dan memperbarui `/home/ubuntu/otak-koding/KNOWLEDGE/INDEX.md` ke status `TESTED`.

3. **Sub-Agen D3: Memory & Context Curator (AGOTIMA Engine)**
   * **Tugas Pokok:** Menjaga kebersihan memori jangka panjang. Menghapus fakta yang sudah basi, mencegah duplikasi informasi, dan memastikan kuota karakter memori sistem tidak melebihi 2.200 karakter.

4. **Sub-Agen D4: Experiment Sandbox Runner**
   * **Tugas Pokok:** Menjalankan eksperimen *throwaway* di folder terisolasi (`/tmp/` atau sandbox lab) untuk memverifikasi hipotesis teknis sebelum diterapkan ke kode produksi.

---

## 4. WORKFLOW SISTEM: BAGAIMANA MENGELOLA & MENJALANKAN ARMADA AGEN

Alur kerja operasional menerapkan **Protokol 5 Tahap Tertutup (Closed-Loop Lifecycle)**:

```text
  [ Instruksi Mas Bagas ]
             │
             ▼
  ┌────────────────────────────────────────────────────────┐
  │ TAHAP 1: INGESTION & INTENT ROUTING (Hermes GM)        │
  │ • Klasifikasi domain: Konten? Web? Infra? Riset?       │
  │ • Penetapan batas token & penentuan Single Purpose     │
  └────────────────────────────────────────────────────────┘
             │
             ▼
  ┌────────────────────────────────────────────────────────┐
  │ TAHAP 2: DEKOMPOSISI DAG & DISPATCH KE DIVISI TERPISAH │
  │ • Divisi Konten: Scout -> Copy -> Render -> ML Scorer   │
  │ • Divisi Web: Design.md -> Builder -> QA Gatekeeper    │
  │ • Isolasi Sandbox Tool & Worktree                      │
  └────────────────────────────────────────────────────────┘
             │
             ▼
  ┌────────────────────────────────────────────────────────┐
  │ TAHAP 3: CONTINUOUS LEARNING LOOP (Khusus Divisi 1 & 4)│
  │ • Evaluasi metrik engagement / skor visual             │
  │ • Identifikasi pola baru & eliminasi kegagalan         │
  │ • Kristalisasi ke Obsidian BUKU_CATATAN                │
  └────────────────────────────────────────────────────────┘
             │
             ▼
  ┌────────────────────────────────────────────────────────┐
  │ TAHAP 4: INVARIANT VERIFICATION GATE (Si Pengawas)     │
  │ • Playwright 3 layar pass?                             │
  │ • Axe WCAG AA 0 pelanggaran?                           │
  │ • Impeccable detect 0 anti-patterns?                   │
  │ • ML Scorer >= 7.5?                                    │
  └────────────────────────────────────────────────────────┘
             │
             ▼
  ┌────────────────────────────────────────────────────────┐
  │ TAHAP 5: MAS BAGAS HUMAN APPROVAL & COMMITTED ACTION   │
  │ • Lolos uji -> Kirim draf/link bersih ke Mas Bagas     │
  │ • Mas Bagas Setuju -> Publish IG / Push Git / Live     │
  │ • Mas Bagas Beri Skor < 5 -> Reset total dari nol      │
  └────────────────────────────────────────────────────────┘
```

---

## 5. DETAIL SIKLUS BELAJAR MANDIRI KONTEN (CONTINUOUS LEARNING SOCIAL MEDIA)

Mengatasi masalah spesifik Mas Bagas di mana agen otomasi IG dan TikTok sebelumnya campur aduk:

1. **Observasi Berkelanjutan (Observe):**
   Agen A1 secara terjadwal mengekstrak 10 konten teratas di ceruk AI dan sepak bola. Data yang diekstrak:
   - Durasi video & titik pergantian slide.
   - Kata pertama headline (Hook analysis).
   - Rasio warna dominan pada thumbnail.

2. **Skor Prediktif (Evaluate):**
   Sebelum draf dibuat, Agen A4 membandingkan storyboard terhadap model historis `sputarai-ml-scorer`:
   - Jika probabilitas jangkauan diprediksi rendah karena teks terlalu panjang di slide 1, draf ditolak secara internal dan diinstruksikan menulis ulang headline yang lebih tajam.

3. **Kristalisasi Pola Sukses (Learn):**
   Jika postingan yang telah terbit mendapatkan rasio likes/komentar tinggi di atas rata-rata:
   - Polanya dicatat ke memori Divisi 1 sebagai formula valid.
   - Jika performanya buruk, parameter tersebut ditandai sebagai *negative constraint* (pantangan baru).

---

## 6. DOKTRIN KONTROL & PANTANGAN MUTLAK HIERARKI

1. **Haram Menjalankan Tugas Konten di Thread Koding Web:**
   Agen yang sedang mengerjakan desain/dashboard dilarang merangkap memproses postingan IG/TikTok dalam satu siklus berpikir agar memori dan token tidak bocor.
2. **Doktrin Keputusan Kritis Mas Bagas:**
   - Penerbitan postingan sosial media resmi (@sputarai, @sputarball).
   - Commit & push repositori git utama.
   - Perubahan struktur basis data produksi.
   *Ketiga hal di atas wajib meminta approval Mas Bagas dan dilarang dieksekusi secara sepihak.*
3. **Penyaluran Notifikasi Otomatis:**
   Seluruh notifikasi bot, laporan telemetri, draf carousel, dan hasil audit otomatis wajib dialirkan ke **Grup Telegram BAgent (`-1004397580704`)**, sedangkan chat pribadi/ruang kerja difokuskan khusus untuk arahan strategis Mas Bagas.

---

## 7. PATCH OPERASIONAL 001 — APPROVAL GATE TERPASANG
**Tanggal:** 28 September 2026  
**Status:** DITERAPKAN & TERVERIFIKASI  

Perbaikan urutan pertama telah dipasang ke sistem produksi agar worker konten tidak lagi langsung menerbitkan postingan tanpa persetujuan manusia.

### File Kendali Baru
1. `/home/ubuntu/otak-koding/SISTEM_AGENT/NEGATIVE_CONSTRAINTS.json`
   - Menjadi sumber aturan pantangan terpusat: human approval wajib, zero emoji UI/content, reset total jika skor < 5, larangan localhost publik, anti generic pitch SputarBall, foto asli HD, anti clickbait/hoax, dan format 4 slide Sputarai.
2. `/home/ubuntu/otak-koding/SISTEM_AGENT/APPROVAL_QUEUE.json`
   - Menjadi antrean draf yang menunggu keputusan Mas Bagas.
   - Worker otomatis hanya boleh `scan -> draft -> render -> QC -> queue -> notify`.
   - Worker otomatis tidak boleh `instagram_media_publish` atau `tiktok_publish` sebelum approval eksplisit.

### Patch Worker
1. `sputarai-instant-news-trigger`
   - File: `/home/ubuntu/penelitian-pola-pikir-ai/scripts/instant-news-dispatcher.js`
   - Perubahan: setelah QC lulus, draf masuk `STAGING_READY` dan antrean approval; auto approve/publish diblokir.
2. `sputarball-subagent-patrol`
   - File: `/home/ubuntu/sputarball/scripts/subagent-controller.js`
   - Perubahan: setelah render + QC, draf masuk antrean `PENDING_APPROVAL`; feedback ML `published` tidak dikirim sebelum benar-benar terbit.
3. Telegram notifier Sputarai
   - File: `/home/ubuntu/penelitian-pola-pikir-ai/scripts/telegram-notifier.js`
   - Perubahan: notifikasi publish bebas emoji dan fungsi baru `sendTelegramDraftApprovalRequest` untuk mengirim kartu approval.

### Verifikasi
- `node --check` lulus untuk ketiga file JavaScript yang dipatch.
- `python3 -m json.tool` lulus untuk `NEGATIVE_CONSTRAINTS.json` dan `APPROVAL_QUEUE.json`.
- Modul notifier diverifikasi mengekspor `sendTelegramDraftApprovalRequest` dan `sendTelegramPostNotification`.

### Konsekuensi Operasional
Mulai patch ini, sistem konten boleh belajar, membuat draf, merender, dan mengirim preview ke grup BAgent. Namun publikasi sosial resmi tetap berada di tangan Mas Bagas sebagai approval akhir.

