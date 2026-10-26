# Pedoman Ringkas Backend & Debugging Berbasis Bukti (Otak Koding)

1. Kontrak Sebelum Sintaks: Petakan input -> syarat -> keputusan -> mutasi -> hasil.
2. Validasi Server-Side: Jangan percaya payload client untuk otorisasi atau role.
3. Perubahan Terfokus: Perbaikan terkecil pada akar masalah; jangan acak dependensi atau arsitektur.
4. Backward Tracing: Lacak mundur dari output abnormal ke proses ke input hulu. Dilarang tambal-gejala.
5. Penanganan Error Jujur: Jangan telan error atau return success palsu.
6. PM2 & Python TUI di Windows: Jangan jalankan CLI interaktif Python yang membutuhkan TUI (seperti `prompt_toolkit`) di latar belakang menggunakan PM2 pada Windows — program akan crash dengan `NoConsoleScreenBufferError` karena tidak ada buffer layar terminal yang terikat. Jalankan proses tersebut di jendela Command Prompt yang terlihat secara persisten.
7. Pencadangan Portabel Multi-Profil: Kemas identitas SOUL, config, dan memories ke dalam data/profiles/<nama> dan filter ketat .env, state.db, serta profil privat terisolasi (koagent). Sistem tujuan langsung mengenali seluruh profil via unpack-state tanpa onboarding ulang.
