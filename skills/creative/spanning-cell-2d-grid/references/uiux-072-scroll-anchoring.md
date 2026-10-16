# UIUX-072 — Default anchoring, native feedback reset dan geometri fokus

Penulis: Bagas Cihuy & Hermes Agent. Status: TESTED, terbatas fixture Chromium lokal. Skill lama diperluas; tidak ada deployment produksi.

## Kontrak dan bukti utama
Target: hentikan pergeseran scroll saat status clipboard berubah/reset dengan kebijakan browser `overflow-anchor:auto`, tetap hormati perpindahan fokus pengguna, dan audit tetangga yang baru menerima fokus.

- Implementasi Python: `scripts/clipboard_scroll_anchor.py` (validator fail-closed memakai geometri bersama).
- Unit deterministik: `scripts/test_clipboard_scroll_anchor.py`.
- Runner browser: `scripts/test_scroll_anchor_chromium.cjs`.
- UI lokal: `history_browser.py`, `history_browser.js`, `branch_dag_topology.py`.
- Bukti utama: `uiux-072-browser.json`, `uiux-072-parent-verification.json` (perintah, exit code, waktu, hash sumber sebelum/sesudah, hash bukti browser).
- Prediksi sebelum eksperimen: `uiux-072-plan.md`; koreksi acceptance gate parent: `uiux-072-parent-red.md`. Rencana dan audit independen adalah catatan hipotesis historis, bukan laporan hasil final. Rencana timer virtual ditolak; bukti akhir memakai timer native tanpa percepatan.

## Observasi dan sebab
Baseline UIUX-071 mengubah tinggi status pada viewport 390px/font2x/failure/forward, lalu default anchoring mengompensasi scroll 38px. Itu bukan pencurian fokus. Angka baseline tidak dipindahkan ke hasil baru: line-height sekarang berbeda.

Parent menemukan acceptance gate pekerja menerima mutasi target di luar viewport dan payload tanpa perbandingan opt-out. Menjalankan callback timer secara langsung juga tidak membuktikan deadline 1500ms. Gate diperketat, mutasi dijadikan uji negatif, kemudian runner nyata diulang. Audit geometri baru mengungkap outline tetangga terpotong dan tooltip menutup bagian target; sumber masalah diperbaiki, bukan menurunkan syarat kelulusan.

## Tiga mindset
**Mekanistik.** Model terbatas: `posisi_visual = posisi_dokumen - scroll_offset`; perubahan tinggi status mengubah posisi dokumen elemen sesudahnya. Auto anchoring dapat mengubah scroll untuk mengimbangi reflow; none menghilangkan kompensasi, bukan reflow. Reservasi grid menjaga tinggi maksimum pesan yang diketahui. Tidak ada klaim speedup: pekerjaan ini menguji kebenaran, bukan benchmark latensi. Waktu timer native tidak dapat dihilangkan sambil tetap mengklaim uji deadline native.

**Bayesian/eksperimental.** Prediksi: reservasi menghentikan perubahan tinggi, auto tanpa reservasi menggeser offset, none tanpa reservasi mempertahankan offset tetapi memindahkan target. Tiga kondisi memakai koordinat sama dan hanya membedakan reservasi/kebijakan anchoring. Hasil mendukung mekanisme dalam fixture; keyakinan tidak diperluas ke bahasa, panjang ID, browser atau OS yang belum diuji. Kontrol negatif menguji apakah gate bisa menolak kegagalan, bukan hanya menerima snapshot bagus.

**Desain sistem.** Pilih perubahan struktur CSS, bukan fixed pixel height atau menyembunyikan overflow. Syarat keras: identitas fokus, deadline timer, tidak ada fokus/scroll tak diminta selama settlement/reset, dan geometri outline aman. Trade-off: ruang setinggi pesan tertinggi tetap terpakai; daftar pesan harus mengikuti perubahan copy. Audit persegi pembatas konservatif, bukan renderer piksel/stacking-context umum.

## Perubahan yang diuji
1. Status live dan tiga template pesan tersembunyi berbagi `grid-area:status`; `visibility:hidden`, `aria-hidden:true`, margin/line-height yang sama. Tidak ada duplikasi status live.
2. SVG memakai outline `:focus-visible`, bukan penghapusan outline menyeluruh. Breadcrumb/SVG mendapat `scroll-margin:8px` dan nearest/instant scroll saat menerima fokus; baseline pengukuran diambil sesudah perpindahan keyboard selesai, bukan melarang scroll yang dibutuhkan navigasi.
3. Tooltip diposisikan setelah batas kanan keseluruhan target, bukan hanya pusat simpul SVG. Hit test SVG memakai lingkaran yang benar-benar dilukis, bukan ruang kosong pusat AABB grup.
4. Gate mengikat urutan event/checkpoint, exact target, rectangle/outline/clip/overlay, status height dan posisi tetangga. Known overlay dengan pointer-events:none tetap diaudit.
5. Timer native dibungkus untuk observasi registration/firing; callback asli berjalan melalui browser setelah delay asli. Promise clipboard pada matriks ini sengaja dikontrol. Tidak ada manipulasi label langsung untuk meniru reset.

## Hasil eksekusi parent
Timestamp awal rerun: 2026-10-15T23:29:20.480070+00:00. Chromium 156.0.8078.4.

| Bukti | Hasil |
|---|---|
| Unit Python keseluruhan | 418 metode lulus, 18 tambahan dari baseline 400 |
| Matriks utama | 36 urutan: viewport 320/390/768 × font1x/2x × success/failure × stay/forward/backward |
| Checkpoint | 288 pengukuran: 8 per urutan |
| Kontrol negatif | 9 kegagalan sengaja terdeteksi |
| Perbandingan opt-out | 1 kondisi; offset stabil tetapi target bergerak, bukan sukses visual |
| Timer asli | 1500.2–1504.9ms teramati; bukan estimasi p95/populasi |
| Perintah final | 16/16 exit code 0; hash sumber sebelum/sesudah identik |

Sembilan kontrol: oldUnstableAuto, transientBlurRefocus, completionFocusTheft, completionStealReturn, resetFocusTheft, transientResetScroll, wrongDepartureIdentity, targetClipped, targetCovered. Output gate juga menampilkan `optOutComparison` di objek bernama negative_controls; itu perbandingan kesepuluh, bukan kontrol negatif kesepuluh.

Perbandingan 390px/font2x/failure/forward, urutan departed → settled → reset:

| Kondisi | Scroll luar (px) | Tinggi status (px) | Target top (px) |
|---|---|---|---|
| Reserved + auto | 314 → 314 → 314 | 129.5625 tetap | 853.3687744140625 tetap |
| Unreserved + auto | 271 → 314 → 271 | 86.375 → 129.5625 → 86.375 | 853.1812744140625 → 853.3687744140625 → 853.1812744140625 |
| Unreserved + none | 314 tetap | 86.375 → 129.5625 → 86.375 | 823.1812744140625 → 866.3687744140625 → 823.1812744140625 |

Dengan none, posisi target berubah 43.1875px meskipun offset scroll identik. Dengan auto tanpa reservasi, offset berubah 43px dan posisi target hampir dipertahankan (pembulatan subpiksel). Reservasi menjaga keduanya dalam matriks.

Regresi terpisah juga exit 0: event 36 urutan/252 fase, nested 12 urutan/84 fase, reflow 48 record, kontras 72 record, aksesibilitas DOM/AX 12 record, clipboard focus 27 record, native clipboard mouse 9 record dan keyboard 24 record; minimap serta tiga runner Node juga dijalankan. Angka ini bukan unit test tambahan dan tidak dijumlahkan sebagai satu skor aksesibilitas.

## Reproduksi
Melalui `terminal`, cwd direktori skill:

```text
python3 -B -m unittest discover -s scripts -q
NODE_PATH=/home/ubuntu/website-security-auditor/node_modules node scripts/test_scroll_anchor_chromium.cjs
python3 -B scripts/clipboard_scroll_anchor.py references/uiux-072-browser.json
```

Gunakan path Playwright terpasang yang sesuai jika berpindah mesin; tidak ada instalasi dependency baru. Semua argv regresi tersimpan di parent-verification JSON. Jalankan native clipboard serial agar tidak saling mengubah isi clipboard.

## Sumber yang dibaca
- https://developer.mozilla.org/en-US/docs/Web/CSS/overflow-anchor — nilai awal auto; none merupakan opt-out.
- https://developer.mozilla.org/en-US/docs/Web/CSS/visibility — hidden mempertahankan layout, tidak menjadi target fokus.
- https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollIntoView — nearest/instant dan scroll-margin untuk clearance.

Ketiganya diambil melalui Jina Reader dengan curl exit 0; dokumentasi memberi semantik, hasil aplikasi dibuktikan runner di atas.

## Kesimpulan dan Gap List
Pada pesan clipboard yang diketahui, reservasi intrinsik grid menghilangkan reflow yang memicu kompensasi anchoring; verifikasi offset dan posisi target bersamaan agar none tidak dianggap otomatis stabil. Pertahankan event trace sampai timer benar-benar reset.

Belum terbukti: reset status berisi ID revisi sangat panjang/lokalisasi berbeda; reservasi tiga pesan bukan jaminan seluruh teks dinamis. Target lanjutan UIUX-073: audit lalu perbaiki reservation contract untuk teks dinamis panjang dan token tidak terputus, dengan matriks terbatasi dan counterexample nyata. Antrekan pada siklus berikutnya, jangan perluas run ini.

Batas lain: browser headless tunggal, font CSS eksplisit bukan native zoom, known opaque rectangles bukan seluruh paint, timer satu aktivasi bukan race antar-aktivasi. DOM/AX tidak membuktikan pembacaan screen-reader; tidak ada klaim clipboard OS lintas aplikasi, WCAG penuh, CLS, performa, atau produksi.
