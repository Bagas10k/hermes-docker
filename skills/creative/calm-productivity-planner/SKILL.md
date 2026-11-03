---
name: calm-productivity-planner
description: Use when building daily planners or calm habit trackers.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [planner, habit-tracker, calm-productivity, upnormal-ui, morphing, mobile-first]
    related_skills: [upnormal-ui-architecture, ui-ux-design-vault, motion-ui-lifecycle-and-morphing]
---

# Calm Productivity Planner Architecture (Standar Baku Mas Bagas)

Gunakan skill ini saat merancang, membangun, atau merombak aplikasi perencanaan harian (*daily planner*), pelacak kebiasaan (*habit tracker*), atau workstation produktivitas pribadi. Skill ini mengkodifikasi standar visual, ergonomi mobile, dan rekayasa gerak *in-place morphing* yang telah disetujui Mas Bagas agar hasil kerja langsung tepat sasaran pada percobaan pertama.

---

## 1. Filosofi & Karakter Visual "Ruang Tenang"

- **Palet Warna Bumi (*Warm Studio Editorial*):**
  - Kanvas utama: *Warm Oatmeal Paper* (`#FAF8F5`) dengan pola bintik halus (*dot-grid* 24px `radial-gradient(rgba(40, 35, 28, 0.06) 1.2px, transparent 1.2px)`).
  - Permukaan kartu: Putih bersih (`#FFFFFF`) dengan aksen latar hangat (`#FAF5ED` / `#F4F0E8`).
  - Tinta teks: *Deep Charcoal Ink* (`#1F2421`) untuk teks utama dan abu-abu arang lembut (`#5A6258`) untuk teks pendukung (rasio kontras WCAG AAA > 10:1).
  - Aksen utama: *Earthy Terracotta* (`#D9532F`) untuk pemicu aksi (CTA), *Forest Green* (`#235436`) untuk status hari/sukses, dan *Warm Amber* (`#E5982A`) untuk prioritas.
- **Tipografi Editorial Seimbang:**
  - Kombinasi font *Serif* berkelas (`Fraunces` / Georgia) untuk judul tanggal dan kutipan motivasi, dipadukan font *Sans-serif* bersih (`Plus Jakarta Sans` / `DM Sans`) untuk data fungsional dan kartu tugas.

---

## 2. Enam Hukum Rekayasa Baku (Non-Negotiable Invariants)

### Hukum 1: In-Place Persistent Sliding Indicator Morphing (Anti-Snap / Anti-Blink)
- **Dilarang Keras:** Menghancurkan DOM (`container.textContent = ''` atau me-recreate tombol) setiap kali hari kalender atau tab filter diklik.
- **Wajib:**
  1. Elemen 7 tombol hari (`.week-day`) dan elemen indikator luncur (`.week-indicator`, `.filter-indicator`) **wajib persisten di dalam DOM**.
  2. Saat berpindah hari/filter, perbarui atribut `data-date`, `aria-pressed`, dan kelas aktif langsung pada node yang sudah ada.
  3. Indikator aktif meluncur mulus secara fisik menggunakan CSS `transform: translateX(...)` dan kurva spring easing `cubic-bezier(0.16, 1, 0.3, 1)`:
```css
.week-strip {
  position: relative;
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}
.week-indicator {
  position: absolute;
  top: 0; bottom: 0; left: 0; width: 0;
  background: var(--accent-forest);
  border-radius: 14px;
  box-shadow: 0 4px 14px -2px rgba(35, 84, 54, 0.35);
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), width 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  pointer-events: none;
  z-index: 1;
}
.week-day {
  position: relative;
  z-index: 2;
  background: transparent !important;
  transition: color 0.25s ease;
}
.week-day.is-selected {
  color: #FFFFFF !important;
}
```
  4. Gerakkan posisi indikator seketika pada saat klik (`requestAnimationFrame`) agar tidak ada jeda tunda (*zero-latency*).

### Hukum 2: Gamifikasi Botani Bertahap (*Botanical Habit Bloom*)
Gantikan bar analitik kaku dengan metafora pertumbuhan tanaman pot tanah liat terakota 4 tahap sesuai persentase penyelesaian tugas:
- **Pencegahan Glitch Bunga Melayang (Pinned Transform-Origin Absolut):**
  - Pada fase pertumbuhan (Stage 1 dan 2), elemen bunga dan kelopak **wajib dikunci dengan `transform-origin: 140px 85px`** (titik pucuk batang utama). Tanpa ini, peramban melakukan scale dari titik `(0, 0)` kanvas SVG yang melempar lingkaran kuncup melayang lepas ke kiri atas udara.
  - Daun dan urat daun wajib dibundel dalam satu grup SVG (`<g class="leaf-left-group">` di titik tumpu `139px 155px` dan `<g class="leaf-right-group">` di `140px 135px`) agar urat daun tidak terpisah dari helaiannya saat scaling.
- **Tahapan Pertumbuhan:**
  - **Stage 0 (0%):** Kuncup hening (tunas hijau kecil di pot tanah liat tanpa ada bunga mengambang).
  - **Stage 1 (1–49%):** Mulai bersemi (pucuk kuncup bulat cokelat-emas menempel kokoh di ujung batang).
  - **Stage 2 (50–99%):** Merekah segar (kelopak bunga mulai membuka setengah mekar).
  - **Stage 3 (100%):** Mekar sempurna (bunga matahari mekar penuh berseri-seri, lingkaran cahaya *sun halo*, partikel kilau emas, dan pesan *"Semua tugas telah tuntas diselesaikan"*).
- *Catatan Teknis:* Jangan menghancurkan SVG tanaman; gunakan CSS state selector `[data-stage="0|1|2|3"]` untuk menganimasikan `transform: scale()`, `opacity`, dan rotasi secara mulus.

### Hukum 3: Ergonomi Mobile 390px (*Above The Fold Priority*)
- **Budgeting Vertikal Ringkasan:** Header kalender dan kartu pertumbuhan di layar HP **maksimal memakan 20–25% tinggi layar**.
- **Compact Horizontal Widget:** Di HP, kartu pertumbuhan diubah menjadi **layout grid horizontal kompak** (ilustrasi pot di kiri selebar ~78px, angka persentase & bar progres di kanan), bukan balok vertikal besar yang memakan 80% layar.
- **Keharusan Lipatan Layar:** Kolom input tugas baru dan minimal 2 item agenda teratas **harus langsung terlihat utuh tanpa perlu scroll** saat aplikasi pertama kali dibuka.

### Hukum 4: Kontrol Masukan Simetris 50–50 (*Command Pill Form*)
- **Dilarang Prefix Statis Panjang:** Jangan menulis `Kategori: Kesehatan` atau `Target Jam: 10:00` di dalam tombol HP karena memicu pemotongan teks (*truncation*).
- **Format Bersih Baku:**
  - Dropdown kategori: Titik warna dinamis + nama kategori + panah dropdown (contoh: `● Kesehatan ▾`).
  - Pemilih waktu: Ikon jam + waktu (contoh: `🕒 10:00`).
- **Simetri Grid:** Terapkan `display: grid; grid-template-columns: 1fr 1fr; gap: 8px;` pada kontrol sekunder form agar kedua kapsul terbagi 50–50 simetris di ponsel.
- **Placeholder Ringkas:** Gunakan placeholder padat seperti *"Tambah target hari ini..."* agar muat utuh di samping tombol aksi.

### Hukum 5: Penempatan Notifikasi Melayang (*Floating Toast Safety*)
- Dilarang keras menempatkan floating toast di area yang menutupi kolom input pengetikan atau menutupi kartu tugas yang baru saja dibuat.
- **Posisi Baku:** Letakkan di bagian **bawah tengah** (`bottom: 24px; left: 50%; transform: translateX(-50%)`) atau sudut kanan bawah dengan safe margin yang tidak menabrak kartu tugas.

### Hukum 6: Imunitas Boundary & Bundel Mandiri (*Self-Contained Bundle*)
- Jika middleware reverse proxy luar atau sistem otentikasi membatasi rute berkas statis terpisah (menghasilkan HTTP 401 Unauthorized pada request file `.css` atau `.js` terpisah), bundel seluruh styling CSS (`<style>...</style>`) dan skrip logika JS (`<script>...</script>`) langsung ke dalam **satu berkas mandiri `index.html`**.
- Ini menjamin pemuatan instan 1-request tanpa risiko FOUC (*Flash of Unstyled Content*).

---

## 3. Prosedur Kerja Pembuatan / Redesain

1. **Inisialisasi Skema & Multi-Key Storage:**
   - Selalu dukung pembacaan data dari kunci primer (`plan_harian_workstation_data_v1`) dan kunci warisan (`hari-ini:v1`).
   - Lakukan penggabungan data tanggal secara aman (*safe merge*); jangan pernah menghapus data korup lama tanpa konfirmasi pengguna.
2. **Susun Struktur HTML Semantik:**
   - Topbar ringkas (logo tunas, tombol salin agenda, tombol unduh JSON cadangan).
   - Kartu tanggal terintegrasi strip pekan 7-hari dengan elemen `.week-indicator`.
   - Form input di baris atas agenda dengan dropdown pill 50–50.
   - Filter segmented tabs (*Semua, Belum, Selesai*) dengan `.filter-indicator`.
   - Sidebar kartu pertumbuhan botani 4-tahap dan timer fokus Pomodoro 25 menit.
3. **Terapkan Morphing CSS & Transisi Spring:**
   - Gunakan kurva `cubic-bezier(0.16, 1, 0.3, 1)` untuk pergeseran indikator.
   - Gunakan `cubic-bezier(0.34, 1.56, 0.64, 1)` untuk sakelar toggle kenyal.
4. **Verifikasi Visual Nyata di Browser:**
   - Periksa di desktop (1280px) dan mobile (390px).
   - Pastikan klik hari meluncurkan kapsul secara mulus tanpa lonjakan visual.
   - Pastikan teks placeholder dan nama kategori tidak terpotong satu huruf pun.
