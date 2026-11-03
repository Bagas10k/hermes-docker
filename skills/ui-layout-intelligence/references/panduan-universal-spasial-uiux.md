================================================================================
DOKUMEN PANDUAN UNIVERSAL SPASIAL UI/UX: SISTEM PADDING, MARGIN, DAN GAP
Standar Rekayasa Antarmuka & Desain Berkelas Industri (Versi 1.0.0)
Penyusun: Bagas Cihuy & Tim Sistem Otonom
================================================================================

[DAFTAR ISI]
1. LANDASAN MENTAL & DEFINISI PERAN SPASIAL (PADDING VS GAP VS MARGIN)
2. HIERARKI HUBUNGAN 4-TINGKAT (THE SPATIAL LADDER & LAW OF PROXIMITY)
3. SISTEM SKALA SPASIAL BASE 4/8-POINT (PRIMITIF & SEMANTIK)
4. MEKANIKA BROWSER & REKAYASA TEKNIS CSS
   4.1 Eliminasi Jebakan Margin Collapsing
   4.2 Box Sizing & Pengendalian Overflow
   4.3 Standar Modern CSS Logical Properties
   4.4 Formula Fluid Spacing & Responsive Page Shell
5. POLA SPASIAL SPESIFIK KOMPONEN
   5.1 Tombol (Button) & Area Sentuh WCAG (Hit Target)
   5.2 Form & Input Field (Hierarki Asosiasi Kontrol)
   5.3 Kartu (Card Architecture: The 4-Distance Rule)
   5.4 Permukaan Data Padat (Dense Tabular Data & Dashboard)
6. PENYESUAIAN OPTIK (OPTICAL SPACING CORRECTIONS)
7. KATALOG ANTI-PATTERN (DOSA SPASIAL UMUM)
8. BLUEPRINT KODE IMPLEMENTASI (CSS NATIVE & TAILWIND CSS)

================================================================================
1. LANDASAN MENTAL & DEFINISI PERAN SPASIAL
================================================================================
Ruang kosong (whitespace) dalam desain antarmuka bukan sekadar "jarak kosong tanpa
fungsi", melainkan KONTRAK STRUKTURAL yang mendefinisikan hubungan antar-elemen.
Kekacauan tata letak hampir selalu bermula dari pencampuradukan 3 peran spasial:

A. PADDING (Ruang Nafas Internal Container)
   - Definisi: Jarak dari batas pembungkus (border/container) menuju konten di dalamnya.
   - Kepemilikan: Mutlak milik elemen kontainer.
   - Penggunaan Wajib:
     * Jarak antara tepi kartu ke grup teks di dalamnya.
     * Jarak antara batas tombol ke teks label atau ikon.
     * Jarak antara border input field ke teks ketikan pengguna.
     * Jarak bantalan cell pada tabel (td/th).

B. GAP (Hubungan Antar-Elemen Bersaudara / Siblings)
   - Definisi: Jarak antar-elemen anak yang diatur secara sentral oleh kontainer induk
     melalui Flexbox atau CSS Grid.
   - Kepemilikan: Dimiliki oleh kontainer tata letak induk (parent layout).
   - Keunggulan: Prediktif, modular, bebas dari efek samping komponen terisolasi,
     dan mencegah child element menyisipkan margin liar ke luar batasnya.
   - Penggunaan Wajib:
     * Jarak antar-kartu di dalam Grid.
     * Jarak antara label, input, dan pesan error di dalam form stack.
     * Jarak antara ikon dan teks di dalam tombol.

C. MARGIN (Pemisah Aliran Eksternal / Flow Offset)
   - Definisi: Gaya dorong elemen terhadap elemen tetangga di dunia luar.
   - Kepemilikan: Dimiliki oleh elemen yang memerlukan offset eksternal independen.
   - Peringatan: Gunakan margin HANYA jika dorongan tersebut memang murni karakter
     aliran dokumen besar (misalnya jeda antar-seksi halaman atau `margin-inline: auto`
     untuk perataan tengah kontainer). JANGAN menyematkan margin pada komponen anak
     yang berada di dalam Flexbox atau Grid.

================================================================================
2. HIERARKI HUBUNGAN 4-TINGKAT (THE SPATIAL LADDER & LAW OF PROXIMITY)
================================================================================
Berdasarkan prinsip Gestalt (Law of Proximity), elemen yang berdekatan secara visual
akan otomatis dipersepsikan oleh otak manusia sebagai satu kelompok makna.

HUKUM BAKU KONTRAK JARAK:
Jarak Spasial Level 1 < Level 2 < Level 3 < Level 4

[Level 1: Micro Spacing (2px - 8px)]
- Digunakan untuk:
  * Jarak ikon ke teks label (biasanya 6px - 8px).
  * Padding vertikal badge, tag, atau chip (2px - 6px).
  * Micro offset untuk kompensasi optik font.
- Pesan Psikologis: "Kita adalah satu partikel elemen tunggal tak terpisahkan."

[Level 2: Component Spacing (12px - 16px)]
- Digunakan untuk:
  * Padding internal tombol standar (10px 16px).
  * Gap antar-input field dalam satu kelompok formulir (12px - 16px).
  * Gap antar-item baris pada navigasi atau daftar kompak.
- Pesan Psikologis: "Kita adalah kontrol-kontrol yang bekerja sama dalam satu tugas."

[Level 3: Group & Card Spacing (20px - 32px)]
- Digunakan untuk:
  * Padding internal kartu/panel (16px pada mobile 360px, 24px pada desktop).
  * Gap antar-kartu dalam satu grid (16px - 24px).
  * Jarak pemisah antar-fieldset/kelompok informasi yang berbeda.
- Pesan Psikologis: "Kita adalah satu modul fungsional yang utuh."

[Level 4: Section & Page Spacing (40px - 80px+)]
- Digunakan untuk:
  * Margin tepi viewport layar (Gutter: 16px pada mobile, 32px - 48px pada desktop).
  * Jarak pemisah antar-seksi besar halaman web (48px - 80px+).
- Pesan Psikologis: "Ini adalah babak/konteks baru dalam halaman."

================================================================================
3. SISTEM SKALA SPASIAL BASE 4/8-POINT (PRIMITIF & SEMANTIK)
================================================================================
Dilarang keras memakai "angka ajaib" (magic numbers) seperti 7px, 13px, 19px, 27px.
Gunakan sistem modular berbasis kelipatan 4px (micro) dan 8px (komponen & layout).

A. TOKEN SPASIAL PRIMITIF (SKALA MENTAH):
   --space-0  : 0px
   --space-1  : 4px   (0.25rem) -> Micro fine-tuning
   --space-2  : 8px   (0.50rem) -> Ikon + teks, badge padding
   --space-3  : 12px  (0.75rem) -> Komponen kompak, dense form gap
   --space-4  : 16px  (1.00rem) -> Interval standar UI, padding card mobile
   --space-5  : 20px  (1.25rem) -> Jeda sedang
   --space-6  : 24px  (1.50rem) -> Padding card desktop, grid gap
   --space-8  : 32px  (2.00rem) -> Jarak antar-grup kartu, page gutter desktop
   --space-10 : 40px  (2.50rem) -> Jarak seksi kompak
   --space-12 : 48px  (3.00rem) -> Pemisah seksi standar
   --space-16 : 64px  (4.00rem) -> Pemisah seksi lega / hero layout
   --space-20 : 80px  (5.00rem) -> Landing page editorial rhythm

B. TOKEN SPASIAL SEMANTIK (PEMETAAN PERAN):
   Selalu rujuk token semantik dalam kode antarmuka agar perubahan tema/densitas
   tidak perlu merombak ribuan baris CSS:
   --layout-page-gutter      : var(--space-4); /* Mobile: 16px, Desktop: 32px */
   --layout-section-gap      : var(--space-12);
   --component-card-padding  : var(--space-6);
   --component-form-gap      : var(--space-4);
   --component-control-gap   : var(--space-3);
   --micro-icon-label-gap    : var(--space-2);

================================================================================
4. MEKANIKA BROWSER & REKAYASA TEKNIS CSS
================================================================================

4.1 ELIMINASI JEBAKAN MARGIN COLLAPSING
Masalah Klasik:
Pada aliran blok dokumen standar (Normal Flow), margin vertikal antar-elemen bersaudara
atau antara induk dan anak pertama/terakhir akan "runtuh" (collapse) menjadi satu nilai
terbesar, bukan dijumlahkan. Ini memicu ketidakpastian tata letak yang sulit dilacak.

Solusi Rekayasa Modern:
- Gunakan display `grid` atau `flex` dengan properti `gap`. Properti `gap` kebal
  terhadap margin collapsing secara spesifikasi peramban W3C.
- Jika terpaksa memakai blok flow, gunakan hanya satu arah margin (misal: hanya
  margin-block-end) dan hindari menggabungkan margin-top dan margin-bottom pada saudara.

4.2 BOX SIZING & PENGENDALIAN OVERFLOW
Baku Mutlak:
Setiap antarmuka wajib menerapkan reset box model:
```css
*, *::before, *::after {
  box-sizing: border-box;
}
```
Tanpa `border-box`, elemen dengan `width: 100%` yang diberi `padding: 16px` akan
memiliki total lebar `100% + 32px`, memicu horizontal scrollbar yang merusak UI mobile.

4.3 STANDAR MODERN CSS LOGICAL PROPERTIES
Tinggalkan properti fisik (`left`, `right`, `top`, `bottom`) dan gunakan properti logis:
- Gunakan `padding-inline` (menggantikan padding-left + padding-right).
- Gunakan `padding-block` (menggantikan padding-top + padding-bottom).
- Gunakan `margin-inline: auto` (menggantikan margin: 0 auto).
- Gunakan `margin-block-start` / `margin-block-end` untuk aliran blok.
Keuntungan: Otomatis mendukung multi-bahasa (LTR dan RTL) serta tata letak vertikal
tanpa perlu menulis override CSS tambahan.

4.4 FORMULA FLUID SPACING & RESPONSIVE PAGE SHELL
A. Fluid Section Spacing (Penskalaan Otomatis Tanpa Breakpoint Kasar):
   Gunakan fungsi matematika `clamp()`:
   ```css
   .section-container {
     padding-block: clamp(2rem, 5vw, 5rem); /* Minimum 32px, dinamis 5vw, maksimum 80px */
   }
   ```
B. Responsive Page Shell (Kontainer Pusat Terisolasi):
   ```css
   .page-shell {
     width: min(100% - 2 * var(--page-gutter), 1200px);
     margin-inline: auto;
   }
   ```
   * Pada Mobile (< 768px) : `--page-gutter: 16px;` (lebar efektif = 100% - 32px).
   * Pada Desktop (>= 768px): `--page-gutter: 32px;` (lebar efektif = 100% - 64px, maks 1200px).

================================================================================
5. POLA SPASIAL SPESIFIK KOMPONEN
================================================================================

5.1 TOMBOL (BUTTON) & AREA SENTUH WCAG (HIT TARGET)
- Rasio Padding Asimetris:
  Padding horizontal tombol selalu 1.5x hingga 2x lebih besar dibanding padding vertikal
  untuk menjaga proporsi kapsul/tombol tetap elegan.
  Contoh: `padding: 10px 20px;` (bukan 15px 15px).
- Pemisahan Ukuran Visual vs Ukuran Klik (Touch Target Isolation):
  Pada UI mobile atau kontrol mikro (seperti tombol silang close atau icon-only button),
  visual tombol mungkin hanya berukuran 24x24px. Namun, panduan aksesibilitas WCAG 2.5.5
  dan standar Apple/Android mewajibkan area interaksi minimal 44x44px atau 48x48px.
  Teknik Implementasi Pseudo-Element:
  ```css
  .icon-button-small {
    position: relative;
    width: 24px;
    height: 24px;
  }
  .icon-button-small::after {
    content: '';
    position: absolute;
    inset: -10px; /* Memperluas area tap menjadi 44x44px tanpa merusak tata letak visual */
  }
  ```

5.2 FORM & INPUT FIELD (HIERARKI ASOSIASI KONTROL)
Prinsip kedekatan formulir wajib mematuhi aturan berikut:
  `Jarak Label -> Input` < `Jarak Input -> Help/Error Text` < `Jarak Antar-Field`

Contoh Baku:
- Label ke Input: `gap: 6px` atau `8px` (Label terikat erat ke kotaknya).
- Input ke Error Text: `margin-block-start: 4px` (Error melekat pada input penyebabnya).
- Antar-Fieldset / Field Lain: `gap: 16px` atau `20px` (Pemisah jelas antar-tugas isian).

5.3 KARTU (CARD ARCHITECTURE: THE 4-DISTANCE RULE)
Sebuah kartu memiliki 4 tingkat jarak yang TIDAK BOLEH bernilai sama:
1. Card Internal Padding (misal 24px).
2. Internal Group Gap (misal 12px antar judul dan ringkasan).
3. Card-to-Card Gap di dalam Grid (misal 20px).
4. Section-to-Card Grid Spacing (misal 48px).
Jika keempat jarak di atas dibuat sama (misal semuanya 20px), antarmuka akan menjadi
monoton, datar, dan membingungkan pengguna saat memindai isi halaman.

5.4 PERMUKAAN DATA PADAT (DENSE TABULAR DATA & DASHBOARD)
- Jangan terapkan ruang lega (luxury spacing) pada tabel keuangan atau data operasional.
- Padding sel tabel standar: `padding: 8px 12px;` (Kompak: `6px 8px;`).
- Batas Area Header/KPI Dashboard:
  Kartu KPI atau ringkasan metrik di atas tabel utama harus dirancang hemat vertikal
  (maksimal 20-25% dari tinggi layar, target <= 180px pada desktop) dengan layout
  horizontal split, agar tabel data primer dan filter tetap tampak langsung di atas fold
  tanpa perlu scroll.

================================================================================
6. PENYESUAIAN OPTIK (OPTICAL SPACING CORRECTIONS)
================================================================================
Presisi matematis tidak selalu menghasilkan keseimbangan persepsi visual di mata manusia.
Lakukan penyesuaian optik (optical nudge) pada kondisi berikut:

1. Ikon dengan Bentuk Asimetris:
   Ikon segitiga "Play", chevron panah kanan, atau bintang memiliki titik berat massa
   yang tidak berada di titik tengah kotak bounding box.
   -> Lakukan koreksi: Geser 1px - 2px ke arah titik berat visual.
2. Teks Huruf Kapital (All-Caps / Uppercase):
   Teks uppercase tidak memiliki "descender" (kaki huruf g, y, p, q) dan memiliki visual mass
   yang lebih solid di atas.
   -> Naikkan sedikit padding-block-end atau kurangi margin-block-start sebesar 1px - 2px.
3. Tombol Pil / Bulat Sempurna (`border-radius: 9999px`):
   Kurva melengkung ekstrem memotong ruang di sudut-sudut kiri dan kanan.
   -> Tambahkan ekstra padding-inline sebesar 4px - 8px dibandingkan tombol beradius kotak
      agar teks di dalamnya tidak terasa tercekik.

================================================================================
7. KATALOG ANTI-PATTERN (DOSA SPASIAL UMUM)
================================================================================
[x] 1. The Double-Stacking Bug:
    Memberi `margin-bottom: 16px` pada elemen anak di dalam kontainer yang sudah
    memiliki `gap: 16px`. Akibat: Jarak menjadi 32px tanpa disengaja.
[x] 2. The Equidistant Trap:
    Jarak antara akhir paragraf ke Subjudul Baru dibuat sama persis dengan jarak Subjudul
    ke paragraf berikutnya. Akibat: Pembaca bingung apakah subjudul tersebut milik seksi
    atas atau seksi bawah.
    -> Rumus Solusi: Jarak ke atas harus minimal 1.5x hingga 2x lebih besar dibanding jarak ke bawah.
[x] 3. The Magic Number Scattering:
    Menuliskan `padding: 13px; margin-top: 27px; gap: 19px;` secara sembarangan di berbagai berkas.
    -> Wajib ditertibkan ke dalam token modular skala 4/8-point.
[x] 4. Forcing Desktop Density on Touch:
    Mengecilkan padding tombol dan baris tabel di layar ponsel sentuh sehingga area klik
    sulit ditekan jari manusia (fat-finger syndrome).
[x] 5. Compensating Layout with Cards & Borders:
    Membuat border kotak-kotak tebal dan kartu di setiap tempat hanya karena gagal
    mengelompokkan elemen menggunakan ruang spasial (whitespace & proximity).

================================================================================
8. BLUEPRINT KODE IMPLEMENTASI
================================================================================

A. CSS NATIVE DESIGN TOKENS & UTILITIES:
```css
:root {
  /* Skala Primitif Spasial (Base 4/8-Point) */
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Token Semantik Responsif */
  --page-gutter: var(--space-4);
  --section-gap: clamp(var(--space-8), 4vw, var(--space-16));
  --card-padding: var(--space-6);
  --control-gap: var(--space-3);
}

@media (min-width: 768px) {
  :root {
    --page-gutter: var(--space-8);
  }
}

/* Pola Kontainer Utama */
.app-container {
  width: min(100% - 2 * var(--page-gutter), 1200px);
  margin-inline: auto;
}

/* Pola Kartu Bersih */
.surface-card {
  padding-block: var(--card-padding);
  padding-inline: var(--card-padding);
  border-radius: 12px;
}

/* Pola Form Stack Menggunakan Gap Terpusat */
.form-group-stack {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.input-field-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--space-2); /* Label ke input sangat dekat */
}
```

B. PEMETAAN STANDAR TAILWIND CSS:
- Micro spacing       : `gap-1` (4px), `gap-2` (8px), `px-2 py-1` (badge)
- Control spacing     : `px-4 py-2` (button), `gap-3` (12px), `space-y-4` (form)
- Card internal       : `p-4 sm:p-6` (padding 16px mobile -> 24px desktop)
- Grid layout         : `gap-4 sm:gap-6`
- Section separation  : `py-8 sm:py-12 lg:py-16`
- Page Margins        : `px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto`

================================================================================
DOKUMEN INI DIJADIKAN RUJUKAN RESMI SISTEM DESAIN & REKAYASA SPASIAL UNIVERSAL.
================================================================================
