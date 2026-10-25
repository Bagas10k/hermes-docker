---
name: frontend-agent-craft
description: Use when building web UI. Autonomous frontend agent craft.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [frontend, ui, ux, design-system, web, html, css, reactive, anti-slop, ponytail]
    related_skills: [ui-ux-design-vault, ui-layout-intelligence, color-intelligence, typography-ux-copy, popular-web-designs, ponytail, autonomous-engineering-craft]
---

# Frontend Agent Craft: Protokol Eksekusi UI/UX Otonom

Skill ini menetapkan standar operasional baku bagi agen AI saat merancang, membangun, memperbaiki, atau merefaktor antarmuka web (Frontend). Menggabungkan kecerdasan tata letak, warna, tipografi, bank komponen APEX, serta doktrin efisiensi *Ponytail*.

---

## 1. Aturan Besi Mas Bagas (Hard Constraints)
Setiap agen frontend wajib mematuhi batasan lingkungan nyata berikut tanpa kompromi:
1. **Haram Localhost / 127.0.0.1 di HTML Publik**: Jangan pernah menulis `http://localhost:...` atau `http://127.0.0.1:...` pada tautan, tag `<a>`, `fetch`, atau aset publik. Gunakan path relatif (`/api/...`) atau nama host produksi.
2. **Pemanfaatan 100 Aset Desain Terverifikasi**: Rujukan aset lokal berstandar tinggi berada di `/home/ubuntu/referensi-desain/` (dapat diakses via web browser di path `/desain/`). Gunakan sebagai aset referensi nyata daripada placeholder kosong.
3. **Halaman Baru Wajib Standalone**: Permintaan halaman baru (seperti halaman login, register, detail produk) wajib dibuat sebagai rute/berkas mandiri terpisah (misal `login.html`), bukan sekadar tab di sidebar dashboard.
4. **Pendaftaran Otomatis ke Katalog Portofolio**: Setiap proyek web baru atau landing page yang dibuat wajib langsung didaftarkan ke katalog portofolio Bagas (`/portofolio/` di `katalog-portofolio-web`).
5. **Standar UI Mobile Companion (Zen)**: Jika merancang tampilan pendamping mobile:
   - 100dvh (1-page non-scrollable).
   - Kanvas zen 'kosongan' minim teks dengan maskot utama besar di tengah.
   - Menu pengaturan lengkap disimpan rapi di dalam slide-up drawer G2 squircle.

---

## 2. Sintesis 5 Pilar UI/UX Intelligence

Sebelum menulis kode visual, sintesiskan 5 pilar desain berikut:
1. **Spatial Layout (`ui-layout-intelligence`)**:
   - Terapkan 4 tingkat spasial: *Page* (margin viewport/container) $\rightarrow$ *Section* (gap antar blok) $\rightarrow$ *Component* (card padding) $\rightarrow$ *Micro* (icon-label gap).
   - Gunakan ritme dasar 8px (4, 8, 12, 16, 24, 32, 48, 64px) dan CSS Gap, bukan margin acak.
2. **Color Intelligence (`color-intelligence`)**:
   - Palet fungsional, bukan dekorasi liar. Dominasi neutral slate/warm paper untuk struktur, aksen saturasi tinggi hanya untuk titik fokus interaksi.
   - Gunakan standar Warm Paper & Obsidian: kanvas porselen (`#f8fafc`), panel baca hangat (`#fdfbf7`), tipografi Obsidian pekat (`#0f172a`), dan aksen permata terukur.
3. **Typography & UX Copy (`typography-ux-copy`)**:
   - Hirarki informasi mendahului ukuran font. Gunakan `text-wrap: balance` agar tidak ada kata yatim (*orphans*).
   - Bahasa lugas, berwibawa, dan bebas basa-basi AI.
4. **Anti-Template & Anti-Slop Gate (`ui-ux-design-vault`)**:
   - **Zero Text Gradient**: Judul wajib monokrom solid tajam (putih di dark mode, hitam di light mode).
   - **Zero Decorative Badge**: Dilarang kapsul pil pemanis melayang di atas headline.
   - **0% Emoji di UI Modern**: Gunakan ikon SVG (Lucide/Heroicons) monokrom.
   - **Zero CLS**: Kunci `min-height` pada wadah teks/konten dinamis.
5. **Lazy Senior Dev Mode (`ponytail`)**:
   - Utamakan HTML/CSS native: Flexbox, Grid, CSS Variables, native `<dialog>`, `<input type="date">`.
   - Hindari dependensi JS berat jika cukup dengan 20 baris vanilla JS.

---

## 3. Pipeline Eksekusi Frontend Agent

1. **Riset & Refleks 100 Aset Desain Lokal (MCP `uiux-reference`)**:
   - Sebelum merancang antarmuka dari nol, panggil `tool_call` dengan `mcp__uiux_reference__uiux_search(query=..., category=...)` untuk mengekstrak sasis nyata dari 100 aset desain lokal di `/home/ubuntu/referensi-desain/`.
   - Gunakan `mcp__uiux_reference__uiux_get_component_recipe` untuk komponen cepat (hero-header, interactive-card, 404, empty-state).
   - Analisis relasi layout dan palet warna referensi sebelum koding.
2. **Analisis Konteks & Arketipe Permukaan**:
   - Tentukan apakah antarmuka bertipe *Console/Operate*, *Catalog/Explore*, *Monitor/Dashboard*, atau *Editorial/Learn*.
3. **Struktur Bersih**: Tulis markup semantik dengan aksesibilitas bawaan (ARIA, semantic tags).
   - Untuk perubahan UI multi-file, tetapkan kepemilikan berkas secara eksplisit: satu pelaksana per berkas/komponen, QC read-only terpisah. Mandor menggabungkan kontrol markup, CSS, dan logika hanya setelah kontrak ID/class/atribut antarlapisan jelas; jangan izinkan beberapa agen menyentuh file yang sama.
   - Definisikan kontrak interaksi sebelum patch: nilai default, daftar pilihan valid, state aksesibel (`aria-pressed`/`aria-selected` sesuai kontrol), sumber data render ulang, dan perilaku refresh. Elemen kontrol yang baru ditambahkan belum dianggap selesai sebelum dihubungkan ke logika.
   - Untuk grafik/timeline yang perlu digeser, jadikan viewport sebagai pemilik `overflow-x: auto`, berikan konten internal lebar eksplisit berdasarkan rentang dan skala yang dipilih, serta pertahankan label identitas dengan sticky positioning. Jangan hanya mengaktifkan overflow tanpa membuat isi lebih lebar dari viewport.
   - Saat refresh berkala membangun ulang grafik, pertahankan pilihan rentang dan posisi pengguna; bila pengguna mengikuti ujung terbaru, tetap ikuti data baru, tetapi jangan tarik paksa pengguna yang sedang meninjau bagian sebelumnya. Jaga scroll vertikal, fokus keyboard, dan seleksi secara independen.
   - Jangan menyatakan UI interaktif selesai hanya dari keberhasilan menulis HTML/CSS. Jika pengujian diminta untuk dilewati, nyatakan dengan jelas bahwa interaksi dan hasil render belum diuji; jangan klaim end-to-end atau deployment.
   - Untuk UI yang ditujukan ke URL publik/TMA, identifikasi terlebih dahulu rute yang benar-benar dipakai pengguna dan pemilik route (Express/router/reverse proxy); bandingkan DOM/aset URL publik dengan URL/berkas lokal sebelum menyimpulkan perubahan aktif. Halaman file `index.html` bisa bukan halaman default `/`, dan source lokal bukan bukti deploy.
   - Sebelum mengganti atau mengalihkan rute halaman utama yang sudah dipakai, pertahankan kontrak rute itu dan tawarkan URL khusus untuk fitur baru; verifikasi HTTP/browser pada URL baru serta ulangi pemeriksaan URL lama agar tidak ada regresi. Bila aktivasi perlu reload layanan bersama, identifikasi proses PM2 dari script path dan minta izin eksplisit sebelum reload.
4. **Styling Modular**: Gunakan variabel CSS terstruktur atau utility class Tailwind yang konsisten dengan token desain.
   - **Aturan token-first pada codebase yang sudah punya token**: bila project telah mendefinisikan custom-property token (`--primary`, `--primary-hover`, `--surface-hover`, `--mint-surface`, `--border-*`, `--danger-*`, `--radius-*`), pakai 100% token itu untuk warna/radius baru. Jangan tambah hex hardcoded di luar token (mis. `#f9fafb`, `#b6c2ba`, `#7f1d1d`) atau gradien `linear-gradient`/`radial-gradient` yang tidak ada di token — warna di luar token membuat halaman tampak kotor/tidak konsisten dan user menilai kerapian+warna sangat rendah. Untuk status sukses/gagal cukup warna SOLID dari token (`--primary-hover` / `--danger`), tanpa gradien.
   - Pada permukaan operasional (kasir, inventori, tabel), letakkan pencarian/aksi utama di viewport pertama; buang hero dekoratif, badge status semu, dan kotak pencarian ganda yang mendorong pekerjaan inti ke bawah.
   - Kelompokkan indikator yang harus dipantau bersamaan dalam satu *monitoring strip* di atas area kerja terkait—misalnya jumlah transaksi, produk unggulan, dan kesehatan stok. Jangan mengubur salah satunya jauh di bawah fold. Bagi lebar berdasarkan kepadatan informasi, bukan sama rata; samakan tinggi kartu, lalu gunakan scroll internal hanya pada daftar yang melebihi tinggi terikat. Pada mobile, pertahankan task utama lebih dahulu dan tumpuk monitoring setelahnya.
   - Jika pengguna menolak **susunan keseluruhan**, hentikan penyesuaian rasio kecil. Tanyakan satu pilihan makro-layout, tulis ulang struktur DOM/grid sesuai pilihan itu, lalu ukur ulang geometri; memoles struktur yang ditolak hanya mempertahankan akar masalah.
   - Untuk dropdown bertema, biarkan `<select>` asli memegang `name`, nilai, validasi, dan pengiriman form. Pemicu visual harus punya fokus keyboard, ArrowUp/Down, Enter, Escape, serta fallback tanpa JS; sinkronkan event `change` ke listener yang sudah ada.
   - Saat menyusun hasil pencarian atau baris keranjang lewat `innerHTML`, escape seluruh teks katalog (nama, SKU, satuan); jangan samakan escaping Blade di tabel statis dengan keamanan interpolasi JavaScript.
   - Pada CSS grid responsif, beri `min-width: 0` pada anak grid dan bungkus hanya tabel yang lebar dengan `overflow-x: auto`. Ukur lebar halaman dan keterbacaan angka pada layar kecil **serta** desktop; `scrollWidth` halaman yang benar tidak membuktikan subtotal di dalam tabel terlihat, dan kolom angka harus utuh di desktop tanpa digeser.
   - Saat memakai `@view-transition { navigation: auto }` untuk transisi halaman, JANGAN memberi `animation:` masuk pada kontainer konten sekaligus — morph ganda terasa patah. Kecualikan chrome tetap (sidebar/topbar) lewat `view-transition-name: none`, beri `view-transition-name` hanya pada area konten, lalu pertahankan fallback `@supports not (view-transition-name: ...)` dan guard `prefers-reduced-motion`.
   - Tabel data yang dipaginasi: tampilkan `firstItem()–lastItem() dari total()` + kontrol halaman lewat satu partial bersama; total uang yang difilter (satu halaman) wajib dilabeli "Total nilai halaman ini", jangan mengklaim agregat global.
   - Untuk ringkasan dashboard yang memasangkan nominal dan grafik dari ukuran bisnis yang sama, satukan keduanya dalam satu kartu semantik agar tidak menduplikasi ruang. Jadikan periode terpilih sebagai satu-satunya sumber bagi label, nominal agregat, jumlah transaksi, dan bucket grafik; ambil semuanya dari satu respons API, jangan menghitung total kedua kalinya di klien.
   - Muat agregasi dashboard berat melalui endpoint JSON terautentikasi dengan periode whitelist. Pertahankan tinggi wadah lewat skeleton, sediakan state kosong/gagal, dan batalkan request lama dengan `AbortController` agar respons lambat dari periode sebelumnya tidak menimpa pilihan terbaru.
   - **Halaman laporan keuangan/data**: angka kunci (Total Pendapatan, Laba Bersih, status SEIMBANG) wajib tampil DI ATAS sebagai kartu ringkasan KPI sebelum filter dan tabel — jangan terkubur di bawah. Tabel laporan wajib beri baris header kolom eksplisit (Kode | Nama Akun | Jumlah) + subtotal per section + baris total bergaris tegas. Rentang tanggal pakai `<input type="date">` native + tombol preset cepat (Bulan Ini/Lalu, Tahun Ini); pisahkan aksi filter (Tampilkan/Reset) ke kiri dari aksi ekspor (Unduh CSV/Cetak PDF) ke kanan (split layout). Tanda `Rp` cukup di header kolom (jangan diulang tiap baris); angka nominal pakai `font-variant-numeric: tabular-nums`. Ekspor CSV sisi-server via `fputcsv` + BOM UTF-8 + `Content-Disposition: attachment` tanpa dependensi baru; PDF cukup `window.print()`.
   - **Input mata uang Indonesia adalah kontrak display/raw**: semua field nominal harus menampilkan pengelompokan ribuan saat diketik (`150000` → `150.000`) tetapi mengirim angka mentah ke server (`150000` atau `150000.50`). Audit seluruh form lebih dulu dan klasifikasikan field uang vs kuantitas/stok; jangan pernah menerapkan formatter uang pada qty, berat, stok fisik, atau field yang sudah punya formatter sendiri. Karena native `type="number"` menolak titik ribuan, gunakan `type="text" inputmode="decimal"` pada field uang, satu helper global berbasis atribut untuk skala desimal, normalisasi saat `submit` capture-phase, dan helper setter untuk modal edit agar nilai lama langsung terformat. Pertahankan skala domain (mis. 2 desimal untuk nominal kas, 4 untuk HPP bila kontrak DB memang 4). Ikuti resep dan matriks uji di `references/indonesian-currency-inputs.md`.
5. **Verifikasi Browser Nyata**:
   - Jalankan pemeriksaan curl HTTP 200.
   - Untuk memeriksa tampilan Blade view yang butuh autentikasi/data (laporan, dashboard) tanpa login nyata, render lewat script PHP yang me-boot Laravel (`chdir('/app'); require 'vendor/autoload.php'; bootstrap/app.php; view()->share('errors', error bag); $html = view('...', $mock)->render()`), tulis HTML ke `/tmp`, tarik keluar via `docker exec <container> cat /tmp/x.html > fixture.html`, sajikan lewat server HTTP statis, lalu inspeksi dengan `browser_exec` (DOM `getComputedStyle`, jumlah elemen, teks, warna computed) — jangan menebak dari tangkapan layar yang tidak bisa dilihat model aktif.
   - Periksa responsivitas viewport mobile & desktop via `browser_exec`.
   - Untuk kontrol timeline dashboard, uji setiap periode secara eksplisit: tombol aktif (`aria-pressed`), label rentang, skala/titik data yang tampak berubah, tidak ada mutasi timestamp sumber, posisi ujung terbaru vs riwayat, serta scroll horizontal internal (konten lebih lebar dari viewport) pada 390/768/1440 px; verifikasi juga polling berkala tidak mengembalikan pilihan ke default. Jangan memakai `scrollWidth <= clientWidth` sebagai asersi bagi timeline yang memang harus dapat digeser; asersi itu cocok untuk mencegah overflow halaman, sementara timeline memerlukan `scrollWidth > clientWidth` pada rentang panjang.
   - Buktikan fitur di URL publik yang benar-benar dimaksud, bukan hanya localhost: periksa identitas halaman/title, kontrol, versi/aset cache-buster, dan respons layanan. Jika domain publik memerlukan autentikasi Telegram, gunakan sesi sah untuk menguji interaksi/data privat; anonymous preview hanya membuktikan shell dan kontrol yang tetap aktif sebelum login.
   - Untuk proses panjang, reproduksi saat pengguna berada di tombol aksi (bukan di puncak halaman). Status, tahap, kemajuan nyata, dan kesalahan harus tetap terlihat pada viewport; pulihkan status dari endpoint pekerjaan setelah refresh/koneksi putus. Jangan mengarang ETA atau persentase.
6. **Zero Abrupt State Change (Motion Continuity)**: Tidak boleh ada perubahan state yang muncul mendadak — nilai, label, warna, posisi/konten, visibilitas, semua wajib bertransisi halus (CSS transition atau animasi masuk 0.15–0.3s, easing ease-out/snappy). Ganti konten teks (`textContent`/`innerHTML`) lewat swap dua fase: nilai lama dianimasikan KELUAR dulu (opacity/translate + `forwards`), baru nilai baru masuk — jangan cuma fade-in nilai baru di atas nilai lama yang hilang seketika (user minta 'ada animasi keluarnya juga'). Untuk daftar/batang yang muncul bertahap, beri `animation-delay` per baris/item (stagger) agar terasa muncul satu per satu. Re-trigger animasi via hapus class → `void el.offsetWidth` (reflow) → tambah class. Audit titik yang kerap lolos transisi: background-color `td`/`tr:hover` dan warna link sort (`th a.th-sort`). Hormati `prefers-reduced-motion`.
   - PITFALL teks tombol aktif kelabu: tombol segmented yang state aktifnya ditandai dengan men-`disable` tombol itu akan dirender kelabu/dim di browser mobile — WebKit menimpa `color` lewat `-webkit-text-fill-color` pada `:disabled`. Saat state aktif = disabled, set JUGА `-webkit-text-fill-color` senilai `color` (mis. teks putih `#fff`) pada state aktif, atau jangan disable tombol aktif.
   - PITFALL lebar segmented-control: bila lebar tiap tombol `auto`, indikator pill yang translate ikut melebar/menyempit saat geser dan terasa 'loncat'. Pakai `grid-template-columns: repeat(n, 1fr)` agar semua slot sama lebar sehingga pill cukup translate tanpa mengubah `width`.
   - PITFALL highlight titik kosong: jangan beri warna sorot/'hari ini' (gelap/berbeda) pada titik data yang nilainya 0 — terbaca sebagai artfak/glitch. Terapkan sorot hanya bila nilai > 0; titik kosong tetap warna dasar + `opacity` redup.
7. **Registrasi Portofolio**: Daftarkan tautan proyek ke `katalog-portofolio-web`.
8. **Notifikasi/Toast**: SELALU riset referensi desain terkini di internet (Sonner, Vercel Geist, NicelyDone, Dribbble) SEBELUM implementasi — jangan pernah pakai pola toast bawaan model (border-left 4px, ikon bulat, uppercase title). Ini hard gate SOP. Setelah riset, sesuaikan dengan token tema proyek. Wajib ada durasi auto-dismiss (progress bar tipis), animasi masuk/keluar halus, pause-on-hover, dan hormati `prefers-reduced-motion`. Posisi dan struktur ikuti hasil riset + tema, bukan default kaku.
