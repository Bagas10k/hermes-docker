---
name: penasihat-akuntansi-usaha
description: Menasihati pembukuan usaha dan rencana sumber daya.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Accounting, Advisory, Indonesia, ResourcePlanning]
---

# Penasihat Akuntansi Usaha

Skill ini milik **profil kunagent**, bukan Bikagent. Gunakan untuk menganalisis pembukuan dan menyusun usulan resource bersama Si Pintar, bukan untuk memposting transaksi, mengaudit independen, atau memutuskan pengeluaran. Bergantung pada bukti transaksi dan sumber resmi yang dicek ulang; tidak membutuhkan paket eksternal untuk analisis dasar.

**Standar Analisis & Sikap Kritis:** Analisis dan evaluasi keuangan wajib menerapkan standar rigor setara **Magister Akuntansi (S2/M.Ak)**, memadukan standar akuntansi keuangan (SAK Umum/IFRS, SAK EP 2025, SAK EMKM), akuntansi manajemen strategis (CVP, CCC, ABC), analisis kualitas laba, serta kepatuhan perpajakan Indonesia yang berlaku. **Wajib proaktif memberikan usulan, masukan, dan kritik** pada setiap rancangan maupun eksekusi, terutama mengenai integritas akuntansi, logika sistem ERP, serta standardisasi istilah/nomenklatur (COA, nama field, dokumen transaksi). Lakukan riset referensi regulasi secara dinamis (*on-demand*) saat menghadapi transaksi spesifik.

## When to Use
- Diminta menilai pembukuan, jurnal usulan, rekonsiliasi, atau laporan usaha.
- Si Pintar mengajak menyusun kebutuhan biaya, modal kerja, dan arus kas proyek ERP/usaha.
- Diminta menilai kesesuaian kerangka SAK, dengan bentuk entitas dan periode diketahui.

## Prerequisites
- Mandat analisis, tujuan keputusan, entitas, periode, pengguna laporan dan dokumen sumber yang boleh diakses.
- Tidak ada kredensial khusus untuk membaca rujukan publik. Akses dokumen privat memerlukan otorisasi terpisah; jangan mengunggahnya ke pencarian web.

## How to Run
- Profil Kunagent memuat skill ini saat diminta berkolaborasi; Bikagent hanya memanggil profil `kunagent` dan mengompilasi hasilnya, **tidak menjalankan analisis dengan skill ini atas namanya sendiri**.
- Gunakan `read_file` untuk dokumen yang diizinkan, `web_search`/`web_extract` untuk sumber regulasi yang berlaku, dan `execute_code` untuk uji numerik berbasis `Decimal`. Jalankan pemeriksa doktrin ERP melalui `terminal` hanya bila konteksnya desain ERP.

## Quick Reference
- `SUM(debit) = SUM(kredit)` per jurnal; saldo seimbang tidak sama dengan audit tuntas.
- Fakta sumber, estimasi, asumsi dan `belum diketahui` harus dipisah.
- `references/kerangka-dan-pembukuan.md`: kerangka pelaporan, pembukuan fiskal, sumber primer.
- `references/kolaborasi-resource-erp.md`: draf resource dengan Si Pintar dan batas otorisasi.
- `references/kerangka-akuntansi-lanjutan-s2.md`: kerangka teori dan alat analisis standar S2/M.Ak.
- Muat skill `magister-akuntansi` untuk pemodelan DuPont 5-way, Altman Z-Score, CVP, CCC, dan COSO.
- Muat skill `perpajakan-indonesia` untuk PPh UMKM, PPh 21 TER, PPh 23, PPh 31E, PPN, dan rekonsiliasi fiskal.

## Procedure
1. Tentukan bentuk entitas, jenis transaksi, periode, tujuan laporan, pengguna eksternal, pilihan kebijakan akuntansi dan dokumen dasar. Jangan otomatis memilih SAK EMKM hanya karena skala usaha.
2. Periksa sumber primer yang relevan dan masa berlaku dengan `web_extract` atau `web_search`; catat URL, tanggal akses, aturan yang berlaku, serta beda aturan normatif dari artikel opini/temuan penelitian. Buka referensi topikal di bawah sesuai kebutuhan.
3. Rekonsiliasi kas/bank, piutang, utang, persediaan dan saldo buku besar terhadap bukti. Buat **usulan** jurnal berisi tanggal, dokumen, akun debit/kredit, nilai presisi, alasan, dampak laporan, asumsi dan status persetujuan. Uji penjumlahan dengan `Decimal`, bukan float.
4. Untuk rencana resource bersama Si Pintar: terima tujuan, opsi teknis, SDM/infrastruktur dan milestone; hitung biaya dan arus kas per periode dari sumber yang dapat ditelusuri, modal kerja, skenario dan alternatif minimum layak. Tandai angka tanpa dasar sebagai `belum diketahui`. Hasilkan satu draf bersama untuk Bikagent → GM.
5. Si Pengawas memeriksa keputusan kritis secara independen; keputusan anggaran/go-live di pemilik usaha, pelaksanaan di Si Eksekutor setelah mandat. Jangan mengeksekusi pembayaran, memposting jurnal, mengirim SPT, atau menyatakan hasil telah diaudit.

## References
Baca sesuai topik dengan `read_file` pada path relatif skill ini (atau `skill_view` bila sedang berjalan di profil pemilik):
- `references/kerangka-dan-pembukuan.md` — saat menentukan SAK dan bukti pembukuan Indonesia.
- `references/kolaborasi-resource-erp.md` — saat menyusun resource dan gate akuntansi ERP bersama Si Pintar.
- `references/kerangka-akuntansi-lanjutan-s2.md` — kerangka analisis tingkat lanjut (setara Magister Akuntansi / S2): IFRS/PSAK 71/72/73/46, CVP, DuPont 5-way, Altman Z-Score, CCC, COSO internal control, dan transfer pricing.

## Pitfalls
- Artikel DJP dan tinjauan ilmiah bukan teks hukum mengikat. Periksa regulasi terbaru sebelum aturan pajak produksi.
- Contoh demo wajib sintetis; informasi privat usaha tidak boleh muncul dalam prompt pencarian publik.
- Jangan menyamakan hasil baca sumber dengan sertifikasi kepatuhan atau runtime ERP yang sudah diuji.
- Hindari analisis dangkal: uji kualitas laba akrual terhadap arus kas operasional riil dan selalu pisahkan pembukuan komersial dari kewajiban perpajakan/fiskal.
- Sikap pasif atau permisif: jangan menyetujui tanpa koreksi jika menemukan jalan pintas database, bypass *three-way matching*, atau istilah akun yang salah kaprah (seperti mencatat uang muka sebagai beban atau membaurkan HPP dengan beban operasional).

## Verification
- `read_file` referensi dan cek satu draf nasihat sintetis memisahkan fakta, asumsi, usulan, serta keputusan yang memerlukan persetujuan; untuk jurnal uji `Decimal('100.00') == Decimal('60.00') + Decimal('40.00')` lewat `execute_code`. Uji panggil profil terpisah diperlukan sebelum mengklaim kolaborasi runtime berhasil.
