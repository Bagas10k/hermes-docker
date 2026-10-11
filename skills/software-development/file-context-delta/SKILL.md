---
name: file-context-delta
description: Use when rereading files during coding tasks.
version: 1.0.0
author: Bagas Cihuy (Bagas Saputra)
license: MIT
---

# File Context Delta

Untuk berkas yang sudah dipahami pada tugas sebelumnya, pakai `python3 ~/.hermes/scripts/file_context.py --match 'regex' path...` guna menampilkan baris relevan hanya ketika isi berubah. Keluaran `UNCHANGED` berarti hash isi sama, **bukan** bahwa file tidak relevan. Kueri pertama hanya menampilkan petikan, bukan seluruh alur.

Sebelum mengedit, tetap telusuri caller dan alur nyata dengan `search_files` serta `read_file` pada bagian terkait. Gunakan `--force` saat perlu konteks lagi; jika instruksi baru mengubah cakupan analisis, baca penuh bagian yang diperlukan walau hash `UNCHANGED`. Cache lokal menyimpan SHA-256 dan path saja, bukan isi atau rahasia; berkas >2 MB/biner dilewati, tidak ada traversing otomatis. Jangan memakai ringkasan lama sebagai bukti state runtime terkini.

Cek minimum: `python3 ~/.hermes/scripts/file_context.py --help`. Penghematan token bergantung pada seberapa sering file yang sama relevan; jangan klaim angka tanpa mengukur.
