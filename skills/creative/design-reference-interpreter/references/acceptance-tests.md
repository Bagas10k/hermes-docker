# Daftar Periksa Pengujian Kualitas Desain (Acceptance Tests & Visual Audit)

Sebelum artefak UI dinyatakan **SELESAI (DONE)**, agen atau modul **Visual Judge** wajib mengaudit hasil render aktual menggunakan checklist 5 gerbang pengujian berikut:

---

## Gerbang 1: Keterbacaan & Kontras (Readability Gate)
- [ ] **Rasio Kontras Teks:** Seluruh teks memiliki rasio kontras minimal 4.5:1 terhadap latar belakang (WCAG AA).
- [ ] **Ukuran Font Terbaca:** Teks body minimal 14px di desktop dan 13px di mobile. Tidak ada teks penting yang di bawah 11px.
- [ ] **Line-Height Nyaman:** Body text memiliki line-height minimal 1.5 - 1.6 agar tidak bertumpuk di layar ponsel.
- [ ] **Uji Keterbacaan Cepat (5-Second Scan):** Pengguna dapat langsung memahami apa judul utama, pesan inti, dan tindakan aksi pertama dalam 5 detik pertama.

---

## Gerbang 2: Kepadatan & Skalabilitas Ruang (Density & Spacing Gate)
- [ ] **Batas Radius Kartu:** Maksimal `rounded-xl` (12px) untuk dashboard/aplikasi data. Tidak ada kartu menggelembung `rounded-3xl` berlebihan.
- [ ] **Padding Terkontrol:** Padding kartu kompak (12px - 20px). Dilarang padding boros (> 32px) yang menyisakan ruang mati (*dead space*) > 50%.
- [ ] **Tabel & DataGrid:** Kolom angka atau finansial wajib rata kanan (`text-right`) dengan format tabular numbers (`tabular-nums`). Header tabel tetap terlihat saat di-scroll (*sticky header*).

---

## Gerbang 3: Responsivitas Mobile Murni (Mobile Responsiveness Gate)
- [ ] **Uji Lebar 390px (Layar Ponsel):** Tidak ada horizontal scrollbar yang tidak sengaja pada body (`overflow-x: hidden`).
- [ ] **Thumb Zone Ergonomics:** Tombol aksi utama, input dock, atau kontrol esensial berada dalam jangkauan satu jempol (di sepertiga bawah layar).
- [ ] **Transformasi Tabel Mobile:** Tabel multi-kolom yang rumit otomatis berubah menjadi kartu vertikal atau memiliki scroll horizontal terkontainer rapi.

---

## Gerbang 4: Kepatuhan Vibe & Brand (Vibe Fidelity Gate)
- [ ] **Bebas Template Klise:** Tidak ada efek glow berlebihan jika vibe bukan futuristic; tidak ada teks emas jika vibe bukan luxury; tidak ada font serif acak jika vibe bukan editorial.
- [ ] **Koleksi Warna Terbatas:** Maksimal 1 warna dominan, 1 warna surface/netral, dan 1 warna aksen fungsional. Tidak menggunakan warna acak.
- [ ] **Ritme Spacing Konsisten:** Jarak antar-elemen menggunakan kelipatan standar sistem (4px, 8px, 12px, 16px, 24px, 32px).

---

## Gerbang 5: Aturan Anti-AI-Slop & Integritas Gambar (Strict Image & UI QC)
- [ ] **Bebas Watermark & Artefak:** Gambar dan aset visual 100% bersih dari watermark (logo stok foto, teks generator acak, cap hak cipta luar, atau cap tanggal).
- [ ] **Focal Point & Komposisi Tepat:** Titik fokus utama gambar (subjek/objek) terposisikan proporsional (di tengah atau framing seimbang), tidak terpotong canggung (*awkward crop*), dan tidak melenceng keluar kanvas.
- [ ] **Proteksi Subjek dari Teks (Anti-Obscured Subject):** Subjek utama gambar dilarang tertutup atau tertabrak oleh teks/heading tebal. Gunakan teknik *scrim gradient overlay* halus atau penataan layout berdampingan agar subjek tetap terlihat jelas dan teks tetap terbaca sempurna.
- [ ] **Nol Emoji di Elemen UI:** Dilarang keras menaruh emoji di tombol, nama menu, tabel, atau ikon sistem (gunakan SVG murni atau tipografi).
- [ ] **Nol Pill Kicker / Badge Melayang:** Dilarang meletakkan badge kecil mengapung di atas heading jika hanya mengulang konteks judul.
- [ ] **Uji Subtraksi (Subtraction Test):** Jika ada elemen dekoratif yang dihapus dan fungsionalitas sistem tidak terganggu, elemen tersebut wajib dihapus.
- [ ] **Penanganan Gambar Rusak:** Semua tag `<img>` dilengkapi fallback onerror (`this.style.display='none'`) agar tidak menyisakan broken icon.
