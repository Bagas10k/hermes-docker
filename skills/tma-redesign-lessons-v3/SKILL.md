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
