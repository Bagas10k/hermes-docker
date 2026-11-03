---
name: tma-redesign-lessons-v3
description: Use when redesigning or evaluating TMA for Bagas.
version: 1.2.0
author: Hermes Agent
---

# Pelajaran Desain TMA untuk Mas Bagas

1. **Anti-Tebak Kosmetik & Wajib Visual Anchor (Patokan Riil):**
   - Saat mendesain ulang TMA dengan arahan subjektif (seperti "fun & elegan"), dilarang menebak sendiri atau sekadar menambal padding, font, dan floating pill jika belum ada referensi visual acuan konkret dari Mas Bagas.
   - Jika nilai user anjlok (< 4/10), segera berhenti utak-atik kode, tawarkan opsi rollback ke baseline stabil, dan minta 1 referensi nyata (screenshot/link produk rujukan 10/10) sebelum melangkah lebih jauh.

2. **Verifikasi Visual Layar Nyata (Bukan Layar Kunci):**
   - Headless screenshot TMA harus selalu diuji pada status terautentikasi (unlocked) agar yang tertangkap bukan merely auth lock screen / error state.

3. **Routing Statis & CSP TMA:**
   - Endpoint publik Express di TMA membatasi file statis via allowlist (`app.css`, `chat.css`). Jangan memecah ke CSS terpisah tanpa mendaftarkannya ke router atau membundlenya langsung ke stylesheet utama.
   - Penggunaan Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`) wajib disertai whitelist di CSP header Express router.

4. **Pencegahan Kedutan (*Anti-Jitter*) pada Linimasa Realtime:**
   - Dilarang menjalankan re-render DOM/chart penuh pada interval ticker 1 detik; batasi ticker hanya untuk memperbarui teks jam telemetri.
   - Hindari CSS transition pada properti `left` atau `width` elemen yang koordinatnya dimanipulasi dinamis oleh JS; gunakan transisi `opacity` lembut tanpa perubahan skala agar baris tidak berkedut saat sinkronisasi data berlangsung.

5. **Disiplin Tipografi Luxury Editorial:**
   - Gunakan bobot SemiBold yang ramping dengan tracking longgar (`0.18em`–`0.24em`) untuk judul brand kapital daripada bobot Black/Heavy yang memadat, dan gunakan angka tabular JetBrains Mono untuk metrik telemetri agar tidak goyang.

6. **Diskrit Kinerja Agen (*Truth-Grounded Discrete Events*):**
   - Dilarang merekayasa balok pengerjaan yang terus-menerus memanjang tanpa henti (`bar-running` buatan) saat agen aktif.
   - Balok linimasa wajib terputus-putus (*discrete*) sesuai pemanggilan alat/tool nyata (`lane.events`). Saat agen sedang jeda, berpikir, atau menunggu, lintasan wajib kosong/terputus agar mencerminkan kinerja nyata.

7. **In-Place Sliding Indicator Morphing & Ergonomi Mobile (Standar Mas Bagas):**
   - **Anti-Snap/Anti-Blink**: Dilarang merusak DOM (`container.textContent = ''`) saat berpindah tab atau tanggal. Node tombol dan indikator aktif (`.week-indicator`, `.filter-indicator`) wajib persisten, bergerak meluncur mulus via CSS `transform: translateX(...)` dan spring easing `cubic-bezier(0.16, 1, 0.3, 1)`.
   - **Above The Fold Priority Mobile**: Header dan kartu gamifikasi (seperti tanaman tumbuh) wajib kompak horizontal (maks 20-25% tinggi layar HP 390px) agar formulir input dan daftar agenda langsung terlihat utuh tanpa scroll.
   - **Simetri Input 50-50**: Hindari prefix statis panjang pada kapsul pilihan (gunakan `● Kategori ▾` dan `🕒 Jam`), posisikan simetris 50-50, dan pastikan floating toast tidak pernah menutupi area input atau kartu tugas aktif.

8. **Visionless Spatial Sensory Audit (Standar Mandat Mas Bagas):**
   - Dilarang hanya mengandalkan tebakan visual atau vision_analyze semata untuk mengecek kerapian tata letak mobile. Jalankan probe telemetri DOM (`dom_responsive_sensor.py` / `canvas-inspector` MCP) untuk memverifikasi matematis:
     * `scrollWidth <= clientWidth` (wajib zero horizontal overflow / dilarang ada geseran kanan-kiri yang merusak UX).
     * Luas target sentuh tombol/link interaktif $\ge 44 \times 44$px sesuai standar ergonomi sentuh mobile.
     * Peta wireframe ASCII berbasis teks untuk melihat langsung posisi elemen above-the-fold tanpa memanggil Vision API yang boros token.


