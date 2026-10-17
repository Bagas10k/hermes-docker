Obsidian vault berlokasi di /home/ubuntu/otak-koding. Rujukan utama: SYSTEM/KNOWLEDGE_ENGINE.md dan KNOWLEDGE/INDEX.md.
§
1. Verifikasi via curl. 2. Proxy existing UIs. 3. Haram localhost di HTML publik. Bot 2 tugas bising. Debugging: baca langsung log error sistem (~/.hermes/logs/errors.log, pm2 logs), jangan tebak acak.
§
Format Telegram: spasi lega, poin 1 baris. PANTANGAN: Dilarang emoji di UI/UX. Standar TUI: gaya Zen (⚡ Skill, # Command, → Read/Edit, diff side-by-side maks 20 baris, [✓]/[ ] checklist).
§
jajandigital (:3000), hermes-gateway (:8080), hermes-pekerja (@Bekbekk_bot), buku (/buku), system-telemetry (:8090), penelitian-ai (:3050), 9router (:20128).
§
Modular RDP tools via Node.js proxy: 1) Hermes (/hermes :9119), 2) 9Router (:20128), 3) PM2, 4) SputarAI (:3050).
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