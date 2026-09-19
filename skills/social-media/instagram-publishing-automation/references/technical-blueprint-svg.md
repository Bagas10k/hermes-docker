# Spesifikasi Teknis Skema Arsitektur Blueprint SVG (Slide 2 Supporting Visual)

Gunakan pedoman ini untuk merakit diagram skema arsitektur vektor SVG murni sebagai elemen visual pendukung pada Slide 2 (Konteks Peristiwa) carousel editorial berita *Seputar AI* (1080×1350).

---

## 1. Filosofi & Batasan Mutlak
- **Anti-Diagram Murahan:** Dilarang menggunakan 3 kotak abu-abu teks polos dengan panah biasa. Visual wajib memiliki kedalaman arsitektural layaknya cetak biru teknis (*engineering blueprint*).
- **Nol Emoji & Nol Gradasi Neon:** Ikonografi 100% vektor garis SVG murni (stroke 1.5–2px, solid `#111214` dan `#C5221F`).
- **Dimensi Kanvas:** `width="952" height="236" viewBox="0 0 952 236"`.
- **Bahasa 100% Baku:** Label tahapan konsisten dalam Bahasa Indonesia: `01 // MASUKAN` -> `02 // PROSES` -> `03 // KELUARAN` (dilarang bocor kata asing seperti `OUTPUT`).

---

## 2. Struktur Modul SVG

```
+-----------------------------------------------------------------------------------+
| [•] SKEMA ARSITEKTUR // NAMA SISTEM              [ METRIK: NILAI TOLOK UKUR ]     | (Top Strip)
+-----------------------------------------------------------------------------------+
|  +--------------------+        +---------------------+        +-----------------+ |
|  | 01 // MASUKAN      |  ===>  | 02 // PROSES (INTI) |  ===>  | 03 // KELUARAN  | | (Node Stack)
|  | [Icon] Data Input  | (Red)  | [Icon] Model / AI   | (Red)  | [Icon] Hasil    | |
|  | - Detail spesifikasi|        | [Progress Meter]    |        | - Verifikasi    | |
|  +--------------------+        +---------------------+        +-----------------+ |
+-----------------------------------------------------------------------------------+
| STATUS: TERVALIDASI   | ARSITEKTUR: NAMA MODEL       | DAMPAK: EFISIENSI NYATA    | (Footer Strip)
+-----------------------------------------------------------------------------------+
```

### Rincian Komponen:
1. **Latar Belakang & Grid:** Latar putih solid (`#FFFFFF`) dengan lapisan pola grid garis halus 24px (`rgba(17, 18, 20, 0.05)`).
2. **Top Header Strip (34px):** Latar `#F4F3EE`, lingkaran aksen merah (`#C5221F`, r=4), judul skema teknis monospace (`12px`, tracking 0.14em), dan lencana status hitam pekat di sudut kanan atas.
3. **Konektor Data Highway:** Garis stroke merah tebal 2px dengan marker panah runcing (`marker-end="url(#arrowHeadRed)"`) menghubungkan Node 1 -> Node 2 -> Node 3.
4. **Node 1 (Masukan / Dataset):** 
   - Label: `01 // MASUKAN` (teks merah monospace).
   - Ikon vektor: Terminal prompt / kurung siku kode (`[_<]`).
   - Judul tebal 15px + subteks 12px + tag status bawah (`STRUKTUR MASUKAN`).
5. **Node 2 (Proses / Model Inti - Focal Point):**
   - Bingkai aksen: Garis tepi merah tebal 5px di sisi kiri, garis luar 2px hitam.
   - Header kotak: Hitam solid (`#111214`) dengan teks putih `02 // PROSES`.
   - Ikon vektor: Chip semikonduktor dengan pinout & titik inti merah.
   - Indikator telemetri: Bar meter horizontal dua warna (putih/merah) dengan badge teks `OPTIMAL`.
6. **Node 3 (Keluaran / Capaian Nyata):**
   - Label: `03 // KELUARAN` (teks merah monospace).
   - Ikon vektor: Kotak centang verifikasi ganda tebal (`✓`).
   - Judul tebal 15px + subteks 12px + tag status bawah (`HASIL TERVERIFIKASI`).
7. **Bottom Telemetry Strip (44px):** Tiga kolom data tabular monospace 11px berjarak 300px (`STATUS`, `ARSITEKTUR`, `DAMPAK`).

---

## 3. Integrasi Prompt AI Generator
AI redaksi wajib mengembalikan spesifikasi JSON `slide2_visual_spec` berisi:
- `title`: Nama arsitektur/sistem warta.
- `metric_label` & `metric_value`: Angka konkret terukur (misal: `AKURASI: 100% VALID`, `EFISIENSI: 80X`, `LATENSI: 0.2MS`).
- `node1`, `node2`, `node3`: Judul dan deskripsi spesifik (maksimal 2–3 kata per baris agar tidak meluap dari kotak).
- `specs`: 3 pasangan label-nilai untuk strip bawah.
