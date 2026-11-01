---
name: tma-redesign-lessons
description: Use when redesigning or evaluating TMA for Bagas.
version: 1.0.0
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
