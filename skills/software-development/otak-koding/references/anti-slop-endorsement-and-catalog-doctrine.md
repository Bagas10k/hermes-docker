# Doktrin Anti-AI-Slop Endorsement, Kanvas Asli, dan Katalog Portofolio

**Arsitektur & Standar**: Bagas Cihuy (Bagas Saputra)  
**Tujuan**: Menghilangkan kebiasaan generik AI template, menjaga estetika berkelas dunia (Swiss Editorial & High-Credibility Institutional Ledger), dan memastikan akumulasi karya web terpusat.

---

## 1. Standar Anti-AI-Slop Social Proof & Endorsements (Anti-Rainbow Pills)
- **Gejala Slop yang Ditolak**:
  - Penggunaan lencana kapsul (*pill badges*) berwarna-warni pastel acak (peach, lilac, mint, sky blue) yang memuat lingkaran inisial nama generik (`SB`, `ER`, `MB`, `BS`).
  - Nama-nama pemodal ventura atau klien hanya ditulis dalam teks kapital polos biasa tanpa lambang resmi.
  - Memberi kesan murahan, kaku, dan seperti template UI kit generik Tailwind/Figma yang tidak memiliki bobot kredibilitas.
- **Standar Solusi (Swiss Editorial Endorsement Cards)**:
  - **Palet Warna Alabaster & Monokrom**: Gunakan kartu berlatar putih bersih atau warm alabaster (`#FFFFFF` / `#FAF8F4`) dengan garis tepi *hairline* 1px tipis (`#EAE3D5` atau `rgba(0,0,0,0.08)`).
  - **Logo Vektor Geometris Orisinal**: Setiap nama institusi atau modal ventura wajib dihadirkan dalam bentuk logo vektor SVG monokromatik terstruktur dengan opasitas netral teredam (`#45423C` opacity ~0.75-0.8), bukan teks sans-serif kapital mentah.
  - **Kutipan Nyata & Berbobot (*Substantive Backing Quotes*)**: Alih-alih hanya mencantumkan nama dan jabatan, sertakan tanda kutip editorial (`“`) dan pernyataan otentik (*Why they backed* / apa peran strategis mereka) yang menjelaskan mengapa platform ini penting.
  - **Hierarki Metadata Terstruktur**: Di bawah kutipan, sertakan nama dalam bobot tebal (*bold/semibold*), afiliasi/posisi terkemuka, dan lencana verifikasi netral.

---

## 2. Larangan "Floating Mock-Up Frame Trap" pada Landing Page Asli
- **Gejala Slop yang Ditolak**:
  - Membungkus seluruh halaman landing page ke dalam kontainer sempit melayang (*floating paper card*) dengan margin luar berwarna tebal (misal: ungu/lavender di sekelilingnya) saat diminta membuat website asli.
  - Halaman terlihat seperti mockup presentasi Dribbble atau screenshot media cetak, bukan website produksi fungsional yang hidup di peramban.
- **Standar Solusi (Natural Full-Width Canvas)**:
  - Seluruh kanvas browser (`body`, `html`) wajib menjadi latar belakang utama halaman secara penuh (*full-width edge-to-edge*).
  - Konten utama dikelompokkan dalam container grid terpusat yang responsif (`max-width: 1240px; margin: 0 auto; padding: 0 32px;`).
  - Header dan footer mengalir natural dari ujung ke ujung tanpa terkurung di dalam kartu mengambang artifisial.

---

## 3. Doktrin Katalog Master Portofolio Terpadu
- **Tujuan**: Memastikan setiap karya desain web dan eksperimen antarmuka yang selesai dibangun langsung ditabungkan ke dalam satu wadah portofolio resmi milik Mas Bagas (`/home/ubuntu/katalog-portofolio-web`).
- **Aturan Integrasi Setiap Karya Baru**:
  1. *Visual Preview Card*: Buat representasi vektor SVG orisinal di `src/Art.jsx` yang mencerminkan anatomi unik proyek (bukan placeholder kosong).
  2. *Metadata Komprehensif*: Cantumkan nama, tahun (2026), status live, ringkasan arsitektur, 4-5 poin keunggulan rekayasa, palet warna *swatches* hex, dan tags teknologi.
  3. *Tampilan Ganda*: Pastikan karya muncul rapi pada mode *Grid View* maupun *Ledger/Table View*.
  4. *Modal Bedah Kasus*: Modal dialog interaktif harus memuat rincian studi kasus, tantangan desain, dan tombol *Buka Live* yang mengarah langsung ke URL aktif (HTTP 200).
  5. *Integritas Uji*: Setiap penambahan proyek wajib melalui uji otomatis Playwright (viewport 390px, 768px, 1440px, 0 overflow horizontal, Zero Emoji, dan 0 pelanggaran Axe Core).
  6. *Vite Subpath Relative Base (`base: './'`)*: Selalu pastikan `vite.config.js` menyertakan `base: './'`. Jika dibiarkan default `/`, aset JS/CSS akan dimuat dari root host (`/assets/...`) alih-alih subpath (`/portofolio/assets/...`), memicu layar putih kosong (*blank screen*) dan galat MIME type stylesheet pada server reverse proxy.
  7. *Metrik Statistik Dinamis*: Indikator kuantitas proyek pada header dan *stats-strip* wajib terikat secara reaktif ke `{PROJECTS.length}`, bukan teks angka statis manual, agar total proyek selalu sinkron seketika saat karya baru didaftarkan.
  8. *Disambiguasi Kueri Pencarian E2E*: Saat menambahkan proyek baru dengan substring judul yang mirip dengan entri lama (misal: "Neraca Akuntansi Frame 023" vs "NERACA OS"), gunakan kueri penelusuran frase spesifik pada Playwright test suite agar ekspektasi jumlah kartu hasil pencarian tidak ambigu.
