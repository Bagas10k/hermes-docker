---
name: multi-agent-deliberation
description: "Use for multi-agent debates and decision gating."
version: 1.3.0
author: Hermes Agent + Bagas Cihuy
license: MIT
platforms: [linux, macos, windows]
related_skills:
  - subagent-lifecycle-management
  - comprehensive-agent-governance
  - autonomous-orchestrator
  - autonomous-learning-pipeline
metadata:
  hermes:
    tags: [multi-agent, deliberation, adversarial-review, quality-gate, decision-making, checks-and-balances, system-1-system-2]
---

# Multi-Agent Deliberation & Decision Gating (SOP Kabinet Tiga Serangkai)

## When to Use
- Perubahan arsitektur sistem baru, migrasi database, skema auth, atau subpath routing.
- Debat pra-eksekusi antara agen perancang (Si Pintar) dan agen eksekutor (Si Eksekutor).
- Laporan koreksi independen oleh Si Pengawas: bukti, kekurangan, dampak, dan saran tanpa veto QC.
- Menghindari perdebatan teks tanpa akhir (*infinite debate loop*) lewat aturan circuit breaker 3 putaran.

## 1. Arsitektur Trias Politica Multi-Agent
Sistem multi-agent pantang menyatukan perancang, pelaksana, dan penguji dalam satu agen (mencegah *self-confirmation bias*). Ekosistem membagi wewenang ke dalam tiga pilar:
1. **Si Pintar (Architect / Researcher):**
   - Merancang blueprint teknis, menyelidiki pustaka resmi, dan merumuskan kriteria penerimaan.
   - Mengajukan proposal perubahan dengan trade-off yang terukur.
2. **Si Eksekutor (Field Implementer):**
   - Menulis dan menguji kode di lingkungan terisolasi (Docker / SQLite lokal).
   - Menjalankan siklus TDD (RED -> GREEN -> REFACTOR).
3. **Si Pengawas (Pengoreksi Independen):**
   - Menambahkan laporan kekurangan berbasis bukti tanpa putusan PASS/REJECT/VETO atau kewajiban mengulang instruksi.
   - Bertindak dari sudut Pengguna (friksi), Pembaca (kejelasan), dan Penasehat (risiko serta saran terukur). Izin dan kontrol keselamatan publikasi/deploy terpisah dari QC.

## 2. Protokol Debat Adversarial (Batas 3 Putaran) & Doktrin Keputusan Tunggal Pragmatis
Debat backend antar-agen bukan sekadar percakapan sopan, melainkan pengujian argumen terstruktur:
1. **Putaran 1 — Proposal & Challenge:**
   - Agen perancang mengajukan spesifikasi.
   - Agen auditor menguji celah (edge cases, cookie scope, subpath routing, memory overhead, privacy leaks).
2. **Putaran 2 — Bukti Kode & Konter-Argumen:**
   - Agen perancang/eksekutor merespons bukan dengan janji kata-kata, melainkan dengan bukti skrip uji coba dan perbaikan terarah.
3. **Putaran 3 — Ringkasan Perbedaan (Circuit Breaker):**
   - Hentikan debat internal setelah tiga putaran; dokumentasikan bukti dan perbedaan yang tersisa. Lanjutkan bagian kerja yang aman. Ajukan satu klarifikasi hanya bila keputusan pengguna memang diperlukan; jangan mengulang instruksi karena QC belum sepakat.
4. **Doktrin Keputusan Tunggal Pragmatis (Mandat Mas Bagas):**
   - DILARANG KERAS terjebak dalam *analysis paralysis* (muter-muter tanpa aksi).
   - Jika suatu solusi secara teknis terbukti merupakan **satu-satunya jalan keluar logis untuk rilis (Single Viable Path)** dan polanya sudah terbukti sukses di sistem saudara (seperti arsitektur subpath PBJ), seluruh agen **WAJIB MENGIZINKAN OTOMATIS (AUTO-APPROVE)** tanpa perlu debat berulang kali atau menunggu persetujuan berbelit-belit.

## 3. Aturan Sakral Penentu Pemenang Debat
1. **Kebenaran Empiris Menang Mutlak atas Klaim Teks:**
   - Klaim "sudah aman" atau "sudah saya perbaiki" bernilai nol tanpa output eksekusi riil: exit code 0, status HTTP, response header, atau asersi suite tes otomatis (PHPUnit/Pytest/Jest).
2. **Koreksi Wajib Konstruktif:**
   - Tambahkan bukti faktual (file, baris, log), dampak nyata, dan alternatif solusi. Jangan jadikan temuan QC sebagai penolakan seluruh alur.
3. **Isolasi Domain Publik (Zero-Touch Public on Unverified Code):**
   - Uji perubahan di lingkungan terisolasi. Publikasi/deploy mengikuti izin dan kontrol keselamatan tersendiri, bukan putusan PASS dari Si Pengawas.
4. **Anti-Over-Caution & Anti-Looping Birokrasi (Penyelarasan Dual-State):**
   - Dilarang membuat aturan audit kontradiktif yang mengunci sistem dalam lingkaran setan analisa (misal: mewajibkan `.env` production HTTPS sebelum rilis, padahal perubahan itu langsung merusak dev preview lokal HTTP).
   - Gunakan pendekatan **Dual-State Alignment** ala modul teruji (seperti PBJ):
     - Kunci subpath di `AppServiceProvider` hanya jika `config('app.env') === 'production'` (`URL::forceRootUrl`).
     - Delegasikan subpath handling pada layer reverse proxy (`X-Forwarded-Prefix`, `X-Forwarded-Proto`) sehingga berkas `.env` lokal tetap bersih dan pengujian lokal tidak lumpuh.
   - Jika agen terdeteksi bolak-balik menghasilkan dokumen asesmen tanpa tindakan konkret dalam 2 putaran, mandor/operator wajib melakukan intervensi langsung memotong kompas.
5. **Prinsip Jalur Akses Terbuka Sederhana (Anti-Overengineering Akses Demo):**
   - Jangan memaksakan jaringan privat seperti VPN/Tailscale untuk demo prototipe cepat yang diminta pengguna dari ponsel/browser biasa jika pengguna menghendaki akses web langsung.
   - Gunakan subpath publik terisolasi atau token URL sederhana di reverse proxy ketimbang mewajibkan konfigurasi VPN berlapis pada perangkat uji pengguna.

## 4. Dua Mode Pengambilan Keputusan: System 1 (Fast Classifier) vs System 2 (Deliberation Engine)
Pahami perbedaan peran antara model klasifikasi keputusan cepat (seperti model Jev / classifier 70–500ms) dengan sistem deliberasi kausal multi-agent:
- **System 1 (Fast Decision Gate / Classifier):**
   - Cocok untuk routing instan, deteksi urgensi, sensor kepatuhan privasi (zero personal data), dan klasifikasi tiket.
   - Sifat: Cepat, deterministik probabilistik, tanpa jejak penalaran (*black-box choice/score*).
- **System 2 (Deep Deliberation / Trias Politica):**
   - Wajib digunakan untuk perubahan arsitektur, refactoring, auth security, dan rilis subpath produksi.
   - Sifat: penalaran bertahap, pengujian empiris, dan laporan koreksi independen tanpa veto QC. Jangan mengganti verifikasi nyata dengan skor probabilitas.

## 5. Pitfall & Optimasi Goal Loop (/goal & Standing Goals)
Sistem Ralph Loop / standing goal (`/goal`) menggunakan judge otomatis (Goal Judge) yang mengevaluasi status per giliran. Hindari jebakan loop memutar-mutar:
1. **Pitfall Ping-Pong WAIT vs CONTINUE:**
   - Ketika subagent di-spawn di background, judge memutus `WAIT` (bisa memarkir proses hingga 600–900 detik).
   - Jika sasaran (`/goal`) dirumuskan sebagai narasi proses umum (*"lanjutkan"*, *"buat seperti video X"*), judge tidak tahu batas tuntas pekerjaan, sehingga terus memutus `CONTINUE` ➔ agen membalas dengan simulasi/rehearsal tambahan ➔ judge memutus `WAIT` lagi.
   - **Solusi (Completion Contract Biner):**
     Rumuskan goal dengan garis finis biner terukur (Outcome + Verification check):
     `Outcome: Laravel Kasir aktif di /kasir-bangunan | Verification: curl -s -I http://127.0.0.1:port/login merespon 200 OK | Stop_when: Verification tercapai`.
     Begitu output verifikasi muncul, judge langsung memutus `DONE` tanpa putaran berlebih.
2. **Pitfall Uji Coba Rollback Berulang (Rehearsal Loop):**
   - Lakukan verifikasi rollback cukup 1 kali untuk memvalidasi hash dan byte file cadangan. Dilarang melakukan putaran simulasi berulang-ulang di loopback socket hanya untuk menunda cutover yang jalurnya sudah jelas.

## 6. Protokol Tool Parsing Safety pada Multi-Skill Invocation
- Hindari menggabungkan pemanggilan banyak skill dengan delimiter titik koma (`;`) dalam satu parameter `skill_view("skill1;skill2;...")` karena akan memicu galat filesystem `[Errno 36] File name too long` atau `Skill not found` yang menyebabkan agen terjebak dalam retry loop panjang. Panggil `skill_view` secara atomik satu per satu per giliran atau gunakan batch tool call terpisah.

## 7. Arsitektur TMA Observer Duplex Real-Time & Linimasa Armada (Armada Timeline)
Ketika pengguna menghendaki pemantauan kinerja agen secara duplex real-time pada perangkat seluler:
- Gunakan arsitektur **Telegram Mini App (TMA) Observer Murni**:
  - Transport data streaming real-time menggunakan Server-Sent Events (SSE) atau WebSocket (`/tma/api/events/stream`).
  - Hapus atau sembunyikan kontrol eksekusi/tombol create/spawn manual pada antarmuka jika pengguna menghendaki mode observasi murni.
  - Tampilkan 4 pilar observasi: **Denyut Agen (Active Agent Pulse)**, **Pipa Alur Kerja (Active Pipeline Steps)**, **Jejak Terminal Live (Console Telemetry)**, dan **Kesehatan Server Host (CPU & RAM Vital Signs)**.
  - Hal ini membebaskan chat Telegram dari spam log panjang, sementara pengarahan strategis tetap berjalan alami lewat teks percakapan biasa.
- **Pola Desain Linimasa Armada (Horizontal Shared-Time Axis):**
  - **Sumbu Waktu Tunggal (Shared Horizontal Time Axis):** Seluruh lajur agen (*lanes*) wajib menggunakan sumbu waktu yang sama agar durasi berpikir vs durasi aksi terlihat sinkron secara visual.
  - **Prinsip Anti-Halusinasi Garis (Zero-Evidence Bar Suppression):** DILARANG menggambar batang durasi atau garis progres jika tidak ada rekaman event konkret di database (`state.db`). Jika koneksi terputus atau agen berhenti tanpa kabar, garis waktu wajib terputus secara visual dan diberi label status diskoneksi eksplisit (tidak boleh ditarik terus seolah-olah agen masih aktif).
  - **Pencegahan Celah Lingkup Callback Frontend:** Pastikan modul render linimasa terdaftar pada scope publik atau didaftarkan pada lifecycle initialization event yang tepat di `app.js` agar tidak menimbulkan eror pemanggilan tak terjangkau saat data tiba dari endpoint backend.
  - **Keamanan Kriptografis HMAC:** Seluruh endpoint TMA (termasuk `/tma/api/armada/timeline/:sessionId`) wajib berada di balik verifikasi sesi `auth.requireAuth` Telegram WebApp HMAC SHA-256 untuk memastikan data operasional agen hanya bisa dilihat oleh pemilik resmi sistem.

## 8. Protokol Pembukuan Keputusan (Knowledge Crystallization)
Setiap keputusan arsitektur dan kekurangan yang dilaporkan wajib dicatat oleh Bikagent ke dalam Obsidian Vault (`EXPERIENCES/`) dengan formula:
`Konteks Arsitektur -> Gejala / Celah -> Bentuk Debat & Bukti Uji -> Keputusan Final -> Batas Penerapan`. Hal ini menjamin keputusan masa lalu menjadi memori bersama yang mencegah tim mengulangi perdebatan atau kesalahan yang sama di masa depan.
