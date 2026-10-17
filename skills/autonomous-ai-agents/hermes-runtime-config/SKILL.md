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
2. **Perubahan berlaku pada sesi BERIKUTNYA, bukan sesi berjalan.** System prompt di-cache per percakapan; menyuntik skill di tengah sesi membatalkan cache itu. Jangan pernah bilang "sudah aktif sekarang" — katakan "aktif mulai sesi berikutnya".
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

## Pitfalls

- **`delegation.orchestrator_enabled` bukan aktivasi skill.** Key itu hanya mengizinkan anak punya anak (`max_spawn_depth`). Memuat skill orkestrator di setiap turn adalah urusan `skills.auto_load`. Dua hal berbeda; menyamakan keduanya membuat laporan "sudah aktif" yang salah.
- **`skills.auto_load` kosong bukan berarti error** — artinya tidak ada skill yang always-on. Probe harus melaporkan itu sebagai OK, bukan FAIL.
- **Jangan menyimpulkan mekanisme runtime dari nama key.** Baca implementasinya (`grep -rn "def resolve_" agent/`) sebelum menjelaskan ke pengguna; nama key yang mirip sering berbeda fungsi.
- **Skill tebal itu mahal.** Skill 14.000 karakter ≈ 3.500 token per request. Untuk obrolan ringan itu murni ongkos; tawarkan cabut dengan `hermes config set skills.auto_load '[]'`.
- **Plugin `skill-retriever` ≠ auto_load.** Retriever menyuntik saat relevan (bisa terlewat); auto_load menyuntik selalu (deterministik, tapi dibayar). Pilih sesuai kebutuhan, jangan campur klaimnya.
- **Backup dulu sebelum menyentuh config:** `cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak-$(date +%s)`.

## Verification

`python3 scripts/verify_auto_load.py` → `OK`, `missing` kosong, dan angka token tercetak. Tanpa itu, perubahan belum boleh dilaporkan berhasil.
