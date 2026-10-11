---
name: agen-pertimbangan
description: Use when menimbang keputusan berdampak besar ala Jev.
version: 1.0.0
author: Bagas Cihuy (Bagas Saputra)
license: MIT
---

# Agen Pertimbangan

Agen khusus menimbang pilihan; tidak mengeksekusi perubahan. Panggil sebagai `delegate_task` satu anak hanya jika pilihan berdampak besar, sukar dibatalkan, atau bukti saling bertentangan. Keputusan sederhana tetap pada agen utama. Jangan hidupkan model/daemon lokal terus-menerus.

## Kontrak delegasi
Berikan tujuan, konteks, opsi, kendala keras, dan bukti yang diketahui. Tugas anak:
1. Gugurkan opsi yang melanggar kendala keras; jangan menukar keamanan/kebenaran dengan kecepatan.
2. Pilah fakta terverifikasi, asumsi, dan data yang hilang. Cari satu bukti yang menentang opsi favorit.
3. Nilai dampak, biaya, risiko, reversibilitas; gunakan angka/probabilitas **hanya** bila ada data kalibrasi, bukan angka karangan.
4. Keluarkan JSON ringkas dengan `choice` (opsi atau `tunda`), `confidence` (`rendah|sedang|tinggi`), `evidence` (maksimal 3 fakta), `tradeoff` (satu kalimat), `risk` (satu kalimat), `next_check` (uji pembeda termurah atau `tidak_perlu`). Jika bukti kritis kurang, pilih `tunda` dan usulkan uji kecil.
5. Agen utama memverifikasi bukti penting dan memutuskan/mengeksekusi; output anak adalah saran, bukan otorisasi. Tindakan eksternal berisiko tetap memerlukan persetujuan yang relevan.

## Batas Jev-style
Tiru antarmuka keputusan terstruktur (pilihan/skor bila terukur), **bukan** klaim memakai model Jev, probabilitas terkalibrasi, atau latensi inferensi khusus. Model decision-head sungguhan hanya ditambahkan bila ada kebutuhan volume tinggi, RAM terukur cukup, dan pengujian akurasi pada data lokal.
