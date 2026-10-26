---
name: mock-data-governance
description: Use when building UI mocks. Enforce clean synthetic data.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [privacy, mock-data, gatekeeper, security, sanitization, anti-slop, compliance]
    related_skills: [capability-stress-test, ui-ux-design-vault, requesting-code-review]
---

# Mock Data Governance & Release Sanitization

Standar operasional baku untuk memastikan seluruh data dummy, mock-up antarmuka, fixture pengujian, dan halaman showcase publik steril dari kebocoran identitas pribadi serta entitas bisnis nyata pengguna.

## 1. Doktrin Pokok Mas Bagas: Hukum Pola vs Masalah
> *"Yang diterapkan jangan masalahnya, tapi yang diterapkan polanya."*

- **Bukan Tambal Sulam Kasuistik:** Dilarang merespons insiden kebocoran data dengan sekadar menempelkan larangan kata per kata ke semua berkas konfigurasi agen.
- **Pola Gerbang Terpusat (Gatekeeper Pattern):** Pasang dan tegakkan satu mesin pemindai biner di pintu rilis (*Single Point of Enforcement*). Keandalan sistem bersandar pada ketegasan gerbang inspeksi hilir, bukan hafalan buruh di hulu.

---

## 2. Pagar Pengaman Privasi & Pemisahan Domain Mutlak

### A. Larangan Entitas Nyata (Zero Real Business & Personal Data)
- **Data Pribadi Terlarang:** Nama lengkap pengguna, nomor telepon/WhatsApp, alamat rumah/kantor, email pribadi, dan kredensial/token rahasia.
- **Data Bisnis Nyata Terlarang:** Nama perusahaan riil (misal: PT PBJ, logistik semen SIG), nama rekanan/toko riil, nomor Surat Jalan faktur riil, dan akun perbankan/CBD operasional nyata.

### B. Kewajiban Menggunakan Data Sintetis Netral (Pure Synthetic Mocks)
Gunakan pabrik data rekayasa standar industri:
- *Infrastruktur & Cloud:* `CLUSTER_INSTANCE_ALPHA`, `NODE_01`, `ap-southeast-3`, `TELEMETRY_STREAM`.
- *Fintech & Perdagangan:* `Acme Corp`, `Global Logistics Ltd`, akun dummy `1-10001 (Kas Utama)`.
- *Pengguna Sintetis:* `Alex Doe`, `User Alpha`, `0812-0000-0000`.

---

## 3. Prosedur Verifikasi Gerbang Rilis (Release Gatekeeper Protocol)

Sebelum menyerahkan halaman antarmuka demo, komponen baru di Bank Komponen, atau fixture pengujian kepada pengguna:

1. **Jalankan Pemindai Otomatis:**
   ```bash
   python3 /home/ubuntu/.hermes/scripts/privacy_gatekeeper.py <path_file_atau_direktori>
   ```
2. **Evaluasi Exit Code Biner:**
   - `Exit 0 (PASS):` Target terbukti 100% steril dan aman diserahkan ke pengguna atau dipublikasikan.
   - `Exit 1 (VETO / FAIL):` Terdapat pelanggaran terdeteksi. Dilarang melapor selesai! Segera bersihkan baris pelanggaran dan jalankan ulang pemindai sampai menghasilkan Exit 0.

---

## 4. Penegakan Anti-AI-Slop pada Halaman Demo / Bank Komponen
- **Bukan Hero Promosi Marketing:** Jangan membungkus instrumen teknis atau bank komponen dengan hero section promosi SaaS generik, teks basa-basi pembuka, atau kalimat marketing hampa.
- **Zero Kicker Badges & Pings:** Dilarang menggunakan pil pemanis mengambang di atas judul utama dan titik animasi berkedip (`animate-ping`) yang tidak memiliki fungsi sistem.
- **Console-First / Workbench Architecture:** Tampilkan langsung kanvas instrumen kerja, data sheet spesifikasi, kartu sasis fisik nyata, dan drawer inspeksi kode.

## 5. Alur Integrasi Penyerapan Komponen ke Bank Komponen Web
Setiap kali komponen baru diserap dari internet (misal via `autonomous-trend-scout` atau riset manual):
1. **Simpan Berkas Kode Fisik:** Tulis komponen ke `/home/ubuntu/otak-koding/BANK_KOMPONEN/<kategori>/` dalam format modular (JSX dan HTML).
2. **Scan Gatekeeper:** Pastikan lulus uji `python3 /home/ubuntu/.hermes/scripts/privacy_gatekeeper.py <file>` (Exit 0).
3. **Deploy ke Web Showcase:** Perbarui `public/komponen/index.html` (rute publik `/komponen/` di `jajandigital.web.id`) dengan kartu preview interaktif, drawer kode, dan update counter total preset.
4. **Verifikasi Visual Browser:** Jalankan render headless Chromium untuk memastikan tampilan mobile rapi tanpa layout shift sebelum diserahkan ke pengguna.

---

## 6. Integrasi Standar Desain Berita Cerah (Bright Editorial Standards)
Saat merancang template visual berita atau komponen feed konten:
- **Kanvas Terang (*Light Canvas*):** Utamakan latar putih/krem cerah (`#FFFFFF` atau `#F8F9FA`) untuk meningkatkan daya baca cepat (*fast-scrolling readability*).
- **Aksen Terang Kontras Tinggi (*High-Contrast Pop*):** Gunakan kuning cerah (`#FFE600`) untuk kategori/tag dan biru kobalt (`#0052FF`) untuk tombol/swipe indicator.
- **Tipografi Bersih Berbobot:** Gunakan sans-serif modern tebal (*Plus Jakarta Sans* / *Inter* 800-900) pada judul dan *JetBrains Mono* pada metadata, menjaga struktur tetap simpel dan bebas ornamen gelap/slop.
