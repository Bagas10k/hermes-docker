---
name: canvas-spatial-grounding
description: Use when measuring responsive DOM, SVG or canvas layout.
version: 1.1.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [UI, SpatialLayout, ResponsiveDesign, MobileErgonomics, ASCIIWireframe, MCP]
    related_skills: [ui-ux-execution-standard, animated-vector-icons, bang-motion]
---

# Canvas Spatial Grounding & Responsive Layout (Mata & Rabaan Agen)

Gunakan pengukuran browser dan visi komputer sebagai "indera struktur" bagi agen:
1. **Mata (Visual Vision):** Kalibrasi koordinat absolut piksel, grid penggaris, deteksi kontur visual, dan Set-of-Marks tanpa halusinasi spasial.
2. **Rabaan (Tactile Sensing):** Pemeriksaan fisik tumpang-tindih (collision/overlap), hit-testing titik `elementFromPoint(x, y)`, batas scroll/overflow, dan occlusion z-index secara deterministik. Telemetri tidak menggantikan penilaian makna, seni, atau piksel gambar yang tidak mempunyai scene metadata.

## Urutan kerja

1. **Tentukan ruang koordinat dan maksud layout.** Catat viewport CSS px, ukuran bitmap/screenshot, devicePixelRatio, scroll, zoom, dan canvas/viewBox. Bedakan fixed video composition yang di-scale dari web responsif yang reflow. Jangan mengukur margin screenshot retina seolah itu CSS px.
2. **Gunakan browser nyata tanpa screenshot dulu.** Atur viewport, tunggu font dan layout stabil, lalu ambil `getBoundingClientRect()`, computed style, `scrollWidth/clientWidth`, `scrollHeight/clientHeight`, struktur induk-anak, dan landmark yang relevan. Catat state, waktu animasi, dan viewport bersama data. Variasi portrait/landscape perlu diuji sebagai komposisi, bukan sekadar angka profil.
3. **Uji breakpoint yang relevan, termasuk layar sempit.** Preset awal boleh 360/390px, tablet768px, desktop1280px; itu viewport emulasi CSS, bukan bukti perangkat fisik. Gunakan pointer/coarse dan hover media query untuk input mode; lebar layar tidak membuktikan perangkat sentuh.
4. **Keluarkan inventaris dan wireframe yang setia.** Sertakan ID, parent, bounds mentah, bounds terlihat setelah clipping, status offscreen/partial/full, dan jumlah data sebenarnya. ASCII hanya pratinjau beresolusi rendah; jangan menjepit objek di luar layar ke tepi lalu menggambarnya seolah berada di viewport. Bedakan ancestor container dan child agar label tidak saling menghapus.
5. **Pisahkan kegagalan, peringatan, dan batas inspeksi.** Gunakan invariant yang dapat diperiksa dan alasan konkret, bukan skor kerapian tanpa kalibrasi. Jangan menyebut seluruh layout lulus ketika hanya overflow dan target sentuh yang diperiksa, atau ketika inventaris terpotong.
6. **Periksa satu perubahan terhadap gejala sebenarnya.** Setelah koreksi lokal, jalankan probe esensial pada state yang sama, lalu serahkan bukti dan keterbatasan. Gunakan screenshot/contact sheet bila perlu menilai hasil visual; vision bukan alat ukur piksel absolut dan gambar diam bukan bukti animasi mulus atau suara.

## Invariant yang benar

### Rabaan Taktil & Deteksi Tabrakan (Tactile Collision & Text Safety)

- **Anti-Text Overlap:** Teks judul dan deskripsi tidak boleh tertimpa atau menimpa visual gerak. Verifikasi via `RectA.bottom < RectB.top` (atau sebaliknya). Jangan hanya mengandalkan `opacity` atau mode blend CSS.
- **Hit-Testing Nyata (`elementFromPoint`):** Untuk memastikan elemen interaktif dapat diraba pengguna, lakukan probe `document.elementFromPoint(x_center, y_center)`. Jika elemen yang kembali adalah backdrop transparan atau overlay tak kasatmata, laporkan `OCCLUDED` (terhalang).
- **Subpixel & Margin Tolerance:** Toleransi subpixel maks 1px; bedakan offset yang disengaja (misal hard brutalist shadow `box-shadow: 4px 4px 0px`) dari pergeseran layout liar (*layout shift*).

### Overflow dan clipping

- Bandingkan lebar dokumen dengan layout viewport/clientWidth menggunakan toleransi subpixel yang disebutkan. Catat elemen kiri-negatif dan kanan-melebihi secara terpisah; jangan menulis semua kasus sebagai overflow kanan.
- Hitung perpotongan terhadap viewport dan ancestor clip/scroll **per sumbu**. `overflow:hidden` dapat mencegah scrollbar tetapi memotong tombol/teks penting; laporkan clipping, jangan hilangkan alarm begitu menemukan ancestor hidden.
- Bedakan dekorasi yang sengaja keluar, carousel/scroll region yang disengaja, elemen focus-only, dan konten penting. Jangan mengubah CSS untuk memuaskan sensor yang salah mengartikan desain.
- Periksa isi teks HTML dengan `scrollHeight > clientHeight` atau `scrollWidth > clientWidth`; kotak yang masuk safe area belum membuktikan teks muat. Periksa multiline, font fallback, dan label SVG dengan metode yang sesuai.
- Jelaskan cakupan shadow DOM, iframe lintas origin, transform, opacity, visibility dan occlusion yang tidak diinspeksi. Elemen `display:none`, hidden/inert, atau tidak punya painted/hit region jangan dihitung sebagai target aktif tanpa alasan.

### Target sentuh dan fold

- Bedakan kebijakan ergonomi44×44CSSpx (selaras target enhanced/AAA dengan pengecualian) dari minimum AA WCAG2.2 sebesar24×24CSSpx beserta spacing/pengecualian. Angka28px desktop adalah kebijakan produk jika dipilih, **bukan standar WCAG**. Bounding box kecil saja tidak membuktikan pelanggaran tanpa evaluasi pengecualian dan hit area.
- Tandai full-above-fold hanya bila `top>=0` dan `bottom<=viewportHeight`; tandai partial dan below/above secara berbeda. Primary form/controls di fold adalah tujuan produk bila brief menuntutnya, bukan hukum untuk semua halaman atau seluruh dokumen.
- Uji simetri50–50 hanya pada kelompok yang memang dikontrak sama lebar. Layout editorial asimetris bukan bug. Gunakan computed grid/flex dan hubungan parent/child, bukan nama kelas `.grid` sebagai satu-satunya detektor.

## SVG dan canvas

- Untuk SVG, gabungkan `getBBox()` lokal dengan `getScreenCTM()` dan viewport/clip untuk bounds layar. Jangan mengecualikan semua descendant SVG dari audit: node dekoratif boleh keluar, label atau ikon penting tetap bisa terpotong.
- Bedakan CSS transform-origin dari atribut XML SVG. `rotate(angle cx cy)` sudah menyebut pivot; `translate()` tidak memerlukan origin. Kelompokkan daun/urat atau subbagian yang bergerak bersama dan ukur titik sambung pada fase awal, antara, dan akhir. Pemeriksaan string XML saja tidak membuktikan geometri benar karena CSS, parent transform, radius, dan viewBox origin ikut berpengaruh.
- Untuk Canvas2D/WebGL/WebGPU, DOM hanya mengetahui kotak canvas. Ekspos scene graph/metadata `{id,role,bounds,transform,parent,clip,z,state}` dari pembuatnya agar struktur internal dapat diaudit tanpa vision. Bila metadata tidak ada, nyatakan internals UNKNOWN; jangan mengklaim DOM membaca piksel canvas.
- OpenCV contour boxes adalah kandidat geometris, bukan identitas semantik komponen yang pasti. Grid/penggaris membantu orientasi, tidak menghilangkan halusinasi atau membuktikan kecocokan referensi. IoU harus memakai luas kotak konsisten, dan data kosong berarti tidak terukur, bukan skor100.

## Integrasi tooling

Probe dan formatter harus tersimpan sebagai modul/sumber kanonik proyek. Helper `sense_layout` di `agent_helpers.py` hanya berlaku pada workspace browser tempat ia dipasang; jangan mengklaim tersedia di semua sesi. Muat helper secara eksplisit atau pasang dari sumber kanonik, lalu uji satu pemanggilan di workspace baru sebelum menyebut integrasi persisten.

Tooling lokal yang dapat ditemukan ulang: `canvas_layout_inspector.py` dan `dom_responsive_sensor.py` di `~/.hermes/scripts/`, serta proyek `canvas-layout-inspector` di GitHub. Periksa implementasi aktif sebelum memakai hasilnya sebagai gate; revisi heuristik lama tidak otomatis mengikuti skill yang diperbaiki ini.

### Standar Kompatibilitas MCP Server Python (SDK 2.0.0)
Pada lingkungan Hermes dengan pustaka `mcp >= 2.0.0`, server MCP Python lokal WAJIB mengimpor `from mcp.server.mcpserver import MCPServer` (bukan `from mcp.server.fastmcp import FastMCP` yang usang dan menyebabkan kegagalan startup modul).
