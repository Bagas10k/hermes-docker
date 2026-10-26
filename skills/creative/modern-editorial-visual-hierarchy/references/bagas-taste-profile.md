# Keputusan & Preferensi Desain Mas Bagas (Calibration Table 90–100%)

Dokumen referensi baku hasil kalibrasi langsung dengan Mas Bagas (Bagas Cihuy). Digunakan untuk mencegah regresi selera pada tugas pembuatan konten media sosial, UI antarmuka, dan infografis.

---

## 1. Matriks Biner Selera

| Dimensi | ❌ Nilai 0 (Diharamkan / AI-Slop) | ✅ Nilai 100 (ACC Mas Bagas) |
| :--- | :--- | :--- |
| **Cover Photo** | Foto kecil terjepit di dalam kotak sempit bergaris. | **Full-Bleed 100% Kanvas (1080×1350)**, dramatis, tatapan langsung ke lensa. |
| **Wadah Teks Cover** | Background gelap kotor dengan gradasi tebal di atas foto. | **Floating White Card** (putih bersih `#FFFFFF`, mengambang di sepertiga bawah, shadow tegas). |
| **Tipografi Judul** | Font serif kaku atau sans-serif generik dengan gradasi warna. | **Plus Jakarta Sans 900**, ukuran 46–64px, leading 1.15, display tracking negatif `-0.03em`. |
| **Aksen Warna** | Gradasi pelangi, neon menyala di banyak elemen. | **Strict Restraint (90/10 Rule)**: 90% netral, aksen kuning cerah (`#FFE600`) atau merah tegas hanya pada 1 titik fokus (tag kategori). |
| **CTA Slide Akhir** | Basa-basi klise: "Jangan lupa like & follow". | **Urgensi Logis**: "Simpan Warta Ini Sebelum Tertimbun Linimasa 📌" + **Dual Action Cards** (Simpan & Bagikan). |
| **Data Dummy** | Memakai data pribadi (nama/kontak) atau entitas bisnis riil (PBJ). | **100% Data Sintetis Netral**: `CLUSTER_INSTANCE_ALPHA`, `LEDGER_CURRENCY_INPUT`. |

---

## 2. Pipa Verifikasi Sebelum Menyerahkan Hasil (Pre-Flight Check)
1. Jalankan `The Squint Test`: Saat layar diburamkan, apakah urutan baca tertangkap jelas (Headline → Kategori Kuning → Ringkasan)?
2. Pastikan tidak ada `animate-ping`, teks gradien, atau border dekoratif tanpa tujuan.
3. Pastikan foto cover tampil penuh tanpa terpotong bingkai sempit.
