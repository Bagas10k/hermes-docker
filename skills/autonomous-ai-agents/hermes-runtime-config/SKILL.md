---
name: hermes-runtime-config
description: "Use when changing Hermes config.yaml or activating skills."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [config, skills, activation, token-cost, verification]
---

# Hermes Runtime Config

Cara aman mengubah `~/.hermes/config.yaml` dan membuktikan efeknya. Skill ini tidak membahas isi tiap skill — hanya mekanisme aktivasi, biaya token, dan verifikasi.

## When to Use

- Pengguna minta sebuah skill "dibuat aktif terus" / "jalan di setiap respons".
- Perlu mengubah nilai config (model delegasi, limit konkurensi, auto_load, plugin).
- Perlu memastikan sebuah perubahan config benar-benar berlaku, bukan cuma tertulis.

## Aturan Keras

1. **Jangan menulis `config.yaml` dengan `patch` atau `write_file`.** Tool menolak dengan *"Refusing to write to Hermes config file"*. Selalu `hermes config set <key> '<json>'` dan baca balik dengan `hermes config get <key>`.
2. **Bedakan kapan key dibaca runtime.** Perubahan yang menyusun system prompt/toolset baru berlaku pada sesi berikutnya karena prompt di-cache; jangan menyuntik ulang di tengah percakapan. Pengaturan gateway yang di-resolve per turn dapat berlaku pada pesan berikutnya tanpa restart. Baca jalur pemakai key sebelum menjanjikan waktu aktivasi.
3. **Buktikan, jangan klaim.** Jalankan `scripts/verify_auto_load.py` (atau probe `resolve_*` yang setara) sebelum melapor. Nilai yang ada di file config bukan bukti bahwa nilainya terbaca runtime.
4. **Sertakan harga.** Setiap skill yang di-auto-load dibayar di setiap request. Sebutkan angka karakter/token-nya, bukan hanya "sudah aktif".

## Prosedur: Mengaktifkan Skill Permanen (`skills.auto_load`)

1. **Pastikan nama skill persis** — pakai `skills_list` dulu; nama salah ketik dilaporkan `missing` dan tidak menggagalkan start, jadi salah ketik mudah lolos tanpa terlihat.
2. **Set:**
   ```bash
   hermes config set skills.auto_load '["nama-skill"]'
   ```
   Hasil di `config.yaml`:
   ```yaml
   skills:
     auto_load:
       - nama-skill
   ```
3. **Verifikasi dua lapis:**
   ```bash
   hermes config get skills.auto_load
   cd ~/.hermes/hermes-agent && python3 -c "
   from agent.skill_commands import resolve_auto_load_skills, build_auto_load_prompt
   print(resolve_auto_load_skills())
   text, loaded, missing = build_auto_load_prompt()
   print(loaded, missing, len(text))
   "
   ```
   `resolve_auto_load_skills()` = config terbaca. `build_auto_load_prompt()` = skill benar-benar bisa dirender penuh. `missing` harus kosong.
4. **Cek tidak ada key yang hilang.** `hermes config set` menulis ulang file; bandingkan dump YAML baru vs backup terbaru dan cetak selisih key-nya. Key yang lenyap tanpa penjelasan adalah regresi senyap — laporkan sebagai perubahan lama bila bukan akibat edit ini.
5. **Lapor** nama skill, jumlah karakter/token, dan kapan efeknya mulai.

Probe siap pakai: `scripts/verify_auto_load.py`.

## Prosedur: Merapikan Progres Agent di Telegram (`display.platforms.<platform>.*`)

Progres yang berantakan (belasan bubble per turn) hampir selalu soal tiga knob, bukan kode.

1. **Baca dulu nilai efektifnya, jangan tebak dari file.** Urutan resolusi (first non-None wins):
   `display.platforms.<platform>.<key>` → `display.<key>` → tier default platform → default global.
   Override per-platform SELALU menang, jadi mengubah `display.tool_progress` saja tidak berpengaruh
   bila `display.platforms.telegram.tool_progress` sudah diset.
   ```bash
   hermes config set display.platforms.telegram.tool_progress new
   hermes config set display.platforms.telegram.tool_progress_grouping accumulate
   hermes config set display.platforms.telegram.cleanup_progress true
   hermes config set display.platforms.telegram.tool_preview_length 80
   ```
2. **Arti tiap knob** — `tool_progress`: `all` (tiap panggilan tool jadi baris) / `new` (hanya saat jenis tool berganti) / `off` / `log` / `verbose`. `tool_progress_grouping`: `accumulate` = SATU bubble yang diedit di tempat, `separate` = satu pesan per tool. `cleanup_progress`: hapus bubble progres setelah jawaban final sukses (butuh `delete_message` nyata di adapter — Telegram punya). `tool_preview_length`: batas karakter preview perintah.
3. **Buktikan lewat resolver, bukan lewat isi YAML:**
   ```bash
   cd ~/.hermes/hermes-agent && venv/bin/python -c "
   import sys; sys.path.insert(0,'.')
   from gateway.run import _load_gateway_config
   from gateway.display_config import resolve_tool_progress, resolve_display_setting
   cfg=_load_gateway_config()
   print(resolve_tool_progress(cfg,'telegram'))
   print(resolve_display_setting(cfg,'telegram','tool_progress_grouping'))
   "
   ```
   Gateway memakai `load_user_config_effective()` (tanpa merge `DEFAULT_CONFIG`), berbeda dari CLI — kalau CLI melihat key tapi gateway tidak, berarti salah loader.
4. **Berlaku per turn, bukan per restart.** Gateway me-resolve display config di setiap turn, jadi perubahan `display.*` langsung terpakai; jangan suruh pengguna restart kecuali yang diubah adalah key yang dibaca saat startup.
5. **Regresi terdekat:** `scripts/run_tests.sh tests/gateway/test_display_config.py`.

## Prosedur: Timestamp pesan gateway

1. Periksa nilai yang ada dan jalur pembacanya sebelum mengubahnya: `hermes config get gateway.message_timestamps`; di `gateway/run.py`, `_message_timestamps_enabled()` menerima `gateway.message_timestamps.enabled: true` maupun shorthand boolean. Pilih bentuk bertingkat yang sesuai dengan konfigurasi yang sudah ada.
2. Cadangkan konfigurasi, lalu jalankan `hermes config set gateway.message_timestamps.enabled true` dan baca kembali dengan `hermes config get gateway.message_timestamps`. Jangan edit YAML langsung.
3. Buktikan nilai efektif dari loader gateway: `cd ~/.hermes/hermes-agent && venv/bin/python -c 'from gateway.run import _load_gateway_config, _message_timestamps_enabled; print(_message_timestamps_enabled(_load_gateway_config()))'`. Jalankan tes terdekat `venv/bin/python -m pytest -q tests/gateway/test_message_timestamps.py tests/gateway/test_timestamp_sidecar_replay.py` bila tersedia.
4. Jelaskan cakupan dengan tepat: timestamp pesan masuk dirender ke konteks model pada turn gateway berikutnya; konten tersimpan tetap bersih. Ini membantu membandingkan waktu kirim antar-pesan, tetapi **bukan guardrail keamanan**. Untuk pengaman anti-stale, pasang pemeriksaan di ingress adapter sebelum penanganan sesi aktif: `/approve`, `/stop`, jawaban klarifikasi, dan antrian pesan dapat diproses tanpa melewati handler pesan biasa. Periksa setiap potongan teks sebelum penggabungan batch: potongan lama yang bergabung dengan event segar dapat mewarisi timestamp segar. Bedakan waktu klik tombol dari waktu kirim prompt bot; timestamp prompt bukan bukti usia klik. Jalankan tes merah untuk pesan lama, tes hijau untuk pesan baru/internal/metadata hilang, lalu tes integrasi melalui jalur pesan aktif. Fitur timestamp **tidak otomatis mengukur latensi balasan ujung-ke-ujung** tanpa waktu pesan balasan terkirim/diterima; profil Hermes lain tetap terisolasi.
5. **Sebelum restart gateway untuk perubahan kode**, inventarisasi `git status --porcelain=v1 -uall` dan `git diff --check`, cadangkan berkas kotor tanpa menghapusnya, lalu audit semua perubahan yang akan ikut dimuat—terutama adapter dan handler gateway. Tes pada worktree terpisah membuktikan patch saja, bukan keseluruhan checkout produksi. Verifikasi ulang bahwa berkas tes/patch masih ada dan jalankan tes di checkout yang akan dijalankan, karena artefak sementara bisa hilang di antara QC dan promosi. Jika ada perubahan lain yang belum diaudit, tahan restart dan laporkan kode di disk terpisah dari kode yang sedang berjalan; jangan klaim fitur sudah aktif dari tes atau salinan berkas saja.

## Pitfalls

- **`delegation.orchestrator_enabled` bukan aktivasi skill.** Key itu hanya mengizinkan anak punya anak (`max_spawn_depth`). Memuat skill orkestrator di setiap turn adalah urusan `skills.auto_load`. Dua hal berbeda; menyamakan keduanya membuat laporan "sudah aktif" yang salah.
- **`skills.auto_load` kosong bukan berarti error** — artinya tidak ada skill yang always-on. Probe harus melaporkan itu sebagai OK, bukan FAIL.
- **Jangan menyimpulkan mekanisme runtime dari nama key.** Baca implementasinya (`grep -rn "def resolve_" agent/`) sebelum menjelaskan ke pengguna; nama key yang mirip sering berbeda fungsi.
- **Skill tebal itu mahal.** Skill 14.000 karakter ≈ 3.500 token per request. Untuk obrolan ringan itu murni ongkos; tawarkan cabut dengan `hermes config set skills.auto_load '[]'`.
- **Plugin `skill-retriever` ≠ auto_load.** Retriever menyuntik saat relevan (bisa terlewat); auto_load menyuntik selalu (deterministik, tapi dibayar). Pilih sesuai kebutuhan, jangan campur klaimnya.
- **Backup dulu sebelum menyentuh config:** `cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak-$(date +%s)`.
- **Entri `platform_toolsets` untuk platform yang tidak ada membanjiri `errors.log`.** Nilai seperti `hermes-google_chat` / `hermes-teams` tidak terdaftar di `toolsets.py`, jadi setiap sesi menulis WARNING "platform has no valid toolsets configured". Validasi nama sebelum set: `venv/bin/python -c "import sys;sys.path.insert(0,'.');from toolsets import validate_toolset;print(validate_toolset('hermes-telegram'))"`, lalu `hermes config unset platform_toolsets.<platform>` untuk yang `False`.

## Verification

`python3 scripts/verify_auto_load.py` → `OK`, `missing` kosong, dan angka token tercetak. Tanpa itu, perubahan belum boleh dilaporkan berhasil.
