Obsidian vault berlokasi di /home/ubuntu/otak-koding. Rujukan utama: SYSTEM/KNOWLEDGE_ENGINE.md dan KNOWLEDGE/INDEX.md.
§
1. Verifikasi via curl. 2. Proxy existing UIs. 3. Haram localhost di HTML publik. Bot 2 tugas bising. Debugging: baca langsung log error sistem (~/.hermes/logs/errors.log, pm2 logs), jangan tebak acak.
§
Format Telegram: spasi lega, poin 1 baris. PANTANGAN: Dilarang emoji di UI/UX. Standar TUI: gaya Zen (⚡ Skill, # Command, → Read/Edit, diff side-by-side maks 20 baris, [✓]/[ ] checklist).
§
jajandigital (:3000), hermes-gateway (:8080), hermes-pekerja (@Bekbekk_bot), buku (/buku), system-telemetry (:8090), penelitian-ai (:3050), 9router (:20128).
§
100 aset desain terverifikasi tersimpan di /home/ubuntu/referensi-desain/, dikelola via web https://www.jajandigital.web.id/desain/.
§
Fokus PBJ adalah pengelolaan laporan keuangan; sistem/alur bisnis, engine DB, data historis, dan VPS tidak diubah tanpa izin eksplisit.
§
Peran Direktur di PBJ bersifat read-only: hanya melihat laporan, tanpa tulis/posting/batal jurnal.
§
User mengharapkan bukti screenshot untuk setiap perubahan UI selesai, dan ringkasan direktur berupa PDF berisi screenshot plus penjelasan.
§
LangitDev adalah proyek web dev multi-klien ERP milik user. User memilih pemeliharaan VPS didelegasikan langsung ke Hermes via chat daripada memakai dashboard GUI. Tailscale aktif sebagai mesh/exit node privat antar HP dan VPS.
§
Vault Obsidian: ~/otak-koding/ (00-Peta-Pengetahuan ... 10-Rekayasa-ERP-dan-Akuntansi-Sistem). Standar catatan: YAML frontmatter (judul/kategori/tag/tanggal_dibuat/terakhir_diperbarui/tautan_terkait), kebab-case, wikilink [[...]], penutup '*Skipped:*'/'*Add when:*'. Folder 10 berisi 30 catatan doktrin ERP; verifikasi dengan `python3 ~/otak-koding/10-Rekayasa-ERP-dan-Akuntansi-Sistem/verifikasi_catatan_erp.py`. Skill terkait: erp-engineering-doctrine.
§
Skill `otak-koding`: SKILL.md sudah 101k char, di atas batas 100k — tambahan teks ke SKILL.md ditolak sistem; taruh materi baru di `references/` skill itu (tetap terdeteksi via linked_files).
§
Plugin autonomous-orchestrator aktif via pre_llm_call hook (hierarki 3 generasi). Tangga kebenaran: lokal/vault -> empiris mesin -> model -> pencarian semantik Exa. Telegram display: cleanup_progress: false, thinking_progress: true, tool_preview_length: 120, delegation fallback aktif.
§
VPS LangitDev: 187.77.120.168 (user langitdev), pbj.melodygroup.cloud di /srv/apps/website-pbj (Docker: pbj_app, pbj_worker, pbj_web, mysql_pusat, pbj_tunnel). Script cek kesehatan: ~/pbj-check.sh. Database db_pbj memakai skema sandbox (79 tabel, 9 akun login aktif).
§
Rilis statis publik (seperti di jajandigital): wajib sematkan cache-buster (?v=...) pada tautan CSS/JS di HTML agar peramban ponsel klien tidak menyajikan aset usang.
§
Protokol Batas Waktu 30 Menit: Batas kerja mandiri per tugas/sprint adalah maks 30 menit. Tetap jaga mutu maksimal (pantang asal jadi). Jika waktu habis, langsung laporkan: 1) Hasil terverifikasi, 2) Kekurangan/limitasi saat ini, 3) Rencana langkah kelanjutan.
§
Anti-Overclaim & Batas Nalar: Dilarang mengklaim hasil/status tanpa bukti empiris fisik. Asisten tidak dapat membaca riwayat blok nalar (thought) sebelumnya, jadi jangan pernah klaim blok nalar sudah berubah tanpa verifikasi. Tulis reasoning sepenuhnya dalam Bahasa Indonesia. Jika tidak tahu atau belum diverifikasi, akui jujur.
§
Kasir app: ~/kasir-bangunan-app; containers: prod kasir-bangunan-prod-app-1, QA kasir-e2e-preview.