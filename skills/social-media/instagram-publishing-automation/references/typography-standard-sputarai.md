# Standar Tipografi @sputarai (dikunci 29 Okt 2026)

Keputusan Mas Bagas: varian **B — Inter Tight 900, sentence case** dipilih dari tiga arah tipografi. Font sistem Linux (Liberation/DejaVu) dinilai 3/10 dan dilarang dipakai untuk aset publikasi.

## Font wajib

Disimpan di `~/.local/share/fonts/`, diunduh dari Google Fonts (lisensi OFL, aman komersial):

| Peran | Berkas | Variasi |
|---|---|---|
| Headline | `InterTight.ttf` | weight 900 |
| Kicker / label | `InterTight.ttf` | weight 600, tracking +4…+7 px |
| Body kecil | `InterTight.ttf` | weight 400 |
| Metadata / handle | `JetBrainsMono.ttf` | weight 400–500, tracking +5 px |

Cadangan bila butuh arah lain: `Anton-Regular.ttf` (poster condensed, all-caps) dan `InstrumentSerif-Regular.ttf` (serif editorial) — hanya untuk eksperimen, bukan default.

## Aturan komposisi

- Headline: sentence case, weight 900, tracking **−3.2 … −3.4 px**, line-height 1.02, maksimal dua baris, ukuran 96–112 px.
- Kicker: uppercase, mono atau Inter 600, tracking lebar, di atas garis merah 5 px.
- Handle kiri-bawah `@SPUTARAI`, nomor `01 / 02` kanan-bawah, mono 18 px.
- Warna teks putih `#FFFFFF`; aksen merah `#C8201E` hanya garis, bukan teks.
- Kicker memakai warna teks yang sama, bukan merah.

## Aturan clearance (wajib diukur, bukan dikira)

- Hitung `draw.textbbox()` tiap baris; blok headline **wajib berakhir ≤ 405 px** bila subjek mulai di y≈420.
- Jangan pakai estimasi tinggi blok (`size × 0.82`); itu pernah membuat varian Anton menabrak kepala 82 px.
- Simpan jarak aman minimal 15 px ke bagian teratas subjek (rambut, sensor, topi).

## Larangan

- Jangan kembali ke Liberation Sans Narrow, DejaVu, atau font sistem lain untuk aset publikasi.
- Jangan pakai all-caps untuk headline default; itu membuat berita terasa tabloid.
- Jangan menaruh teks di area yang sama pada dua berita berbeda tanpa mengecek ulang posisi subjek.
