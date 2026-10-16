---
name: fleet-branch-merge-protocol
description: "Use when parallel agents merge work into a verified core."
version: 0.1.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [multi-agent, parallel, branch-merge, verification-gate, unbounded-depth, consensus]
    related_skills: [autonomous-orchestrator, tiga-serangkai-orchestration, multiagent-worktree-orchestration, multiagent-consensus-circuit-breaker]
---

# Fleet Branch & Merge Protocol

Protokol orkestrasi armada sub-agent paralel untuk ekosistem LangitDev (Bagas Cihuy, VPS 4-core / 16 GB RAM, arsitektur database-per-tenant). Mengatur sistem isolasi cabang kerja, gerbang verifikasi bukti sebelum penggabungan (*evidence-first merge gate*), tata kelola kedalaman tanpa plafon berbasis disiplin anggaran ketat, konsensus artefak tertulis tanpa interupsi manusia, dan penjadwalan antrean paralel bebas hambatan (*zero idle worker*).

## When to Use
- Menggabungkan kode dari banyak sub-agent paralel ke cabang utama tanpa risiko tabrakan modifikasi (*write collisions*) atau regresi pada puluhan tenant ERP.
- Mengelola pendelegasian sub-agent bertingkat (anak melahirkan anak) dengan jaminan keamanan token dan memori agar tidak menguras sumber daya VPS.
- Menyelesaikan pertentangan antarmuka atau kebutuhan konsensus antarsub-agent secara otonom melalui pertukaran artefak tertulis tanpa mengganggu fokus Mas Bagas.
- Menjadwalkan antrean tugas paralel dinamis dengan prinsip pengisian slot instan demi efisiensi prosesor.

Don't use for:
- Tugas tunggal sekuensial berskala kecil yang tuntas dalam satu putaran tanpa pembuatan cabang kerja.
- Tugas inspeksi atau pembacaan berkas murni (*read-only*) tanpa modifikasi basis kode repositori.

## Prerequisites
- Repositori Git lokal aktif dengan konfigurasi `delegation.worktree_isolation: true`. **Periksa dulu bahwa direktori kerja memang repo git**: setelan ini hanya berlaku di git repo dengan backend terminal lokal, dan di luar itu ia turun diam-diam ke ruang kerja bersama (isolasi tidak terjadi meski setelannya menyala).
- Python 3.11+ standard library (`re`, `pathlib`, `dataclasses`, `sys`).
- Pemahaman konfigurasi `delegation.max_spawn_depth` dan batasan tool bawaan Hermes Agent.
- Ketersediaan skill rujukan: `autonomous-orchestrator`, `tiga-serangkai-orchestration`, `multiagent-worktree-orchestration`, `multiagent-consensus-circuit-breaker`.

## Quick Reference
```bash
# 1. Alokasi cabang terisolasi untuk tugas armada
git worktree add -b fleet/<task-id> /tmp/kanvas-worktrees/<task-id> main

# 2. Eksekusi pengujian deterministik pada HEAD sebelum merge
pytest /tmp/kanvas-worktrees/<task-id>/tests --quiet

# 3. Penggabungan aman setelah status gerbang LULUS
git merge --no-ff -m "[FLEET] Gabung terverifikasi fleet/<task-id>" fleet/<task-id>
git worktree remove --force /tmp/kanvas-worktrees/<task-id>
git branch -d fleet/<task-id>
```

## Procedure

1. **Isolasi Cabang Mandiri Berbasis Git Worktree**
   Setiap sub-agent koding wajib dialokasikan ke ruang kerja terisolasi (`git worktree` dan cabang independen `fleet/<task-id>`), bukan bekerja langsung pada direktori inti. Agen induk mendefinisikan batas cakupan berkas yang boleh disentuh (`lingkup_berkas`).
   *Akibat kegagalan:* Menulis langsung pada cabang inti memicu tabrakan penulisan (*file overwrite*), riwayat commit kotor, dan merembesnya perubahan setengah jadi ke basis data tenant aktif.

2. **Gerbang Verifikasi Bukti pada HEAD Sebelum Penggabungan (Evidence-First Merge Gate)**
   Mengadopsi prinsip verifikasi ketat Repoach dan GitHub Agent Gate. Gerbang menginspeksi ulang bukti fisik pada commit HEAD cabang kerja sebelum instruksi `git merge` dieksekusi. Laporan mandiri sub-agent ("pekerjaan selesai", "LGTM") dikarantina sebagai data tidak tepercaya (*untrusted self-report*).
   *Urutan eksekusi:* Jalankan pemeriksa deterministik berbiaya murah (skrip pengujian unit, regex pendeteksi rahasia, audit diff berkas, deteksi tabrakan berkas pekerja lain) LEBIH DULU. Pemeriksaan berbasis LLM hanya dipanggil untuk evaluasi makna semantik yang memerlukan pertimbangan akal. Skrip deterministik menyaring 95% cacat kode dengan biaya token nol.
   *Syarat mutlak:* Verifikasi wajib tuntas SEBELUM penggabungan ke inti, bukan sesudahnya.
   *Akibat kegagalan:* Memverifikasi setelah penggabungan menyebabkan kode cacat meresap ke basis kode utama; proses rollback di sistem multi-tenant memaksa penghentian layanan puluhan basis data klien.

3. **Matriks Otorisasi Penggabungan Otomatis vs Izin Manusia**
   - **Penggabungan Otomatis (Zero-Click Gate):** Diizinkan untuk perubahan berlingkup terbatas yang lolos 100% gerbang deterministik (dokumentasi teknis, penambahan file tes baru, perbaikan bug lokal dalam modul tertutup).
   - **Wajib Izin Manusia (1-Click Mas Bagas):** Wajib meminta konfirmasi eksplisit pengguna untuk setiap perubahan yang menyentuh skema database tenant, logika mutasi keuangan/pembayaran, kunci rahasia/lingkungan produksi, dan arsitektur inti sistem (`SYSTEM/`).
   - *Akibat kegagalan:* Menggabungkan perubahan struktural keuangan secara otomatis memicu risiko ketidaksesuaian saldo akuntansi klien dan sanksi audit.

4. **Skrip Pemeriksa Gerbang Deterministik (Python Stdlib)**
   Skrip berikut dijalankan oleh agen induk atau Si Pengawas untuk memvalidasi 5 pilar invarian (uji lulus, anti-bocor kredensial, kepatuhan lingkup, kesesuaian berkas target, dan nol konflik antar-pekerja):

```python
import re
from dataclasses import dataclass

@dataclass
class HasilVerifikasi:
    lulus: bool
    temuan_gerbang: list[str]

POLA_KREDENSIAL = [
    re.compile(r"(?i)(api[_-]?key|secret|password|bearer|token)\s*[:=]\s*['\"][A-Za-z0-9_\\-]{8,}['\"]"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"),
]

def periksa_gerbang_gabung(
    berkas_diubah: list[str],
    lingkup_berkas: set[str],
    berkas_target_wajib: set[str],
    kode_keluar_uji: int,
    konten_berkas_map: dict[str, str],
    berkas_pekerja_lain: set[str],
    ada_konflik_git: bool
) -> HasilVerifikasi:
    temuan: list[str] = []
    if kode_keluar_uji != 0:
        temuan.append(f"Uji unit gagal dengan status kode keluar: {kode_keluar_uji}")
    if ada_konflik_git:
        temuan.append("Konflik git terdeteksi terhadap cabang inti")
    for target in berkas_target_wajib:
        if target not in berkas_diubah:
            temuan.append(f"Berkas target wajib belum diubah: {target}")
    for berkas in berkas_diubah:
        if berkas not in lingkup_berkas:
            temuan.append(f"Pelanggaran lingkup modifikasi: {berkas} di luar kontrak")
        if berkas in berkas_pekerja_lain:
            temuan.append(f"Konflik antar-pekerja: {berkas} sedang dimodifikasi pekerja lain")
        konten = konten_berkas_map.get(berkas, "")
        for pola in POLA_KREDENSIAL:
            if pola.search(konten):
                temuan.append(f"Kebocoran kredensial rahasia terdeteksi di {berkas}")
    return HasilVerifikasi(lulus=len(temuan) == 0, temuan_gerbang=temuan)

# Uji Invarian Gerbang
hasil_valid = periksa_gerbang_gabung(["app.py"], {"app.py"}, {"app.py"}, 0, {"app.py": "x = 1"}, set(), False)
assert hasil_valid.lulus is True, "Gagal meloloskan perubahan yang sah"

hasil_uji_gagal = periksa_gerbang_gabung(["app.py"], {"app.py"}, {"app.py"}, 1, {"app.py": "x = 1"}, set(), False)
assert hasil_uji_gagal.lulus is False and "status kode keluar: 1" in hasil_uji_gagal.temuan_gerbang[0]

hasil_bocor = periksa_gerbang_gabung(["cfg.py"], {"cfg.py"}, {"cfg.py"}, 0, {"cfg.py": "api_key = 'abcdef123456'"}, set(), False)
assert hasil_bocor.lulus is False and "Kebocoran kredensial" in hasil_bocor.temuan_gerbang[0]

hasil_konflik = periksa_gerbang_gabung(["app.py"], {"app.py"}, {"app.py"}, 0, {"app.py": "x = 1"}, {"app.py"}, False)
assert hasil_konflik.lulus is False and "Konflik antar-pekerja" in hasil_konflik.temuan_gerbang[0]
```

5. **Tata Kelola Kedalaman Tanpa Plafon Berbasis Anggaran (Unbounded Depth)**
   - **Arsitektur Tingkat Hermes:** Pengaturan `delegation.max_spawn_depth` menentukan kedalaman delegasi. Nilai bawaan adalah 1 (armada datar tanpa hierarki). Angka 2 berarti agen anak diizinkan melahirkan cucu; angka 3 mengizinkan hierarki 3 tingkat. Secara komputasi Hermes tidak menetapkan batas atas (tanpa plafon).
   - **Distribusi Peran Berbasis Kedalaman:** Peran sub-agent ditentukan secara mutlak oleh KEDALAMAN posisi, bukan oleh instruksi teks atau permintaan tugas. Sub-agent dengan kedalaman `< max_spawn_depth` otomatis berstatus `orchestrator` (mempertahankan hak `delegate_task`). Sub-agent pada tingkat terdalam (`leaf`) murni berstatus kuli eksekusi.
   - **Restriksi Tool Ketat:** Agen peran `leaf` DILARANG memanggil `delegate_task`, `clarify`, `memory`, `send_message`, dan `cronjob`. Agen `orchestrator` mempertahankan `delegate_task` untuk dekomposisi lanjutan, namun tetap DILARANG memanggil `clarify`, `memory`, `send_message`, dan `cronjob`. Kedua peran tetap memiliki akses penuh ke `execute_code`.
   - **Konsekuensi Komunikasi Pengguna:** Sub-agent anak TIDAK BISA bertanya langsung kepada Mas Bagas karena tool interaksi diblokir sistem. Segala bentuk eskalasi wajib merayap naik melalui rantai agen induk.
   - **Pengendali Anggaran Nyata (bukan plafon jumlah):** Jumlah sub-agent **tidak dibatasi** — yang mengendalikan adalah anggaran, bukan angka. Tanpa rem anggaran, biaya token dan thread proses meledak berlipat per tingkat secara eksponensial ($O(B^D)$). Pada VPS 4-core / 16 GB RAM, ledakan sub-agent liar memicu Linux OOM-killer yang merusak proses PM2 dan basis data. Rem yang wajib dipasang:
     - `child_timeout_seconds` (rekomendasi 180-300 detik) — anak yang menggantung memakan slot dan token tanpa hasil.
     - Pemutus sirkuit kegagalan: bila satu cabang gagal 2 kali berturut-turut pada tujuan yang sama, dilarang melahirkan anak baru pada cabang itu; hentikan rantai tersebut seketika.
     - Pemeriksaan ringkas sebelum menaikkan kedalaman: apakah tugas benar-benar butuh anak, atau cukup dikerjakan anak yang sudah berjalan? Menaikkan kedalaman untuk tugas yang tidak butuh anak hanya menambah biaya dan titik kegagalan senyap.
     - Pantau konsumsi RAM VPS; hentikan penambahan pekerja bila mendekati batas, karena OOM-killer membunuh proses acak (termasuk PM2 dan basis data tenant), bukan hanya sub-agent.

6. **Protokol Rembukan Sesama Agen Melalui Pertukaran Artefak Tertulis**
   - **Prinsip Mandiri Tanpa Interupsi:** Dilarang menginterupsi Bagas Cihuy untuk persoalan sintaks bahasa, dokumentasi modul, cara integrasi dependensi, atau penelusuran galat teknis. Jika kurang pengetahuan teknis, sub-agent wajib melakukan riset mandiri (membaca web, dokumentasi resmi, atau basis kode lokal).
   - **Batas Eskalasi ke Pengguna:** Tanya ke Mas Bagas HANYA untuk: (a) kebutuhan logika bisnis tenant riil, (b) kendala perangkat keras atau lingkungan nyata di luar server, (c) pilihan preferensi arsitektur yang hanya diketahui pemilik sistem, atau (d) keputusan berdampak besar yang tidak dapat disimpulkan dari data.
   - **Komunikasi Berbasis Berkas (Artefak Tertulis):** Karena sub-agent tidak memiliki soket komunikasi langsung antar-sesama, rembukan diwujudkan lewat pertukaran dokumen fisik di direktori proyek bersama:
     - `KONTRAK-ANTARMUKA.md`: Diterbitkan oleh agen perancang sebelum koding dimulai; memuat spesifikasi skema JSON, tipe data input/output, dan batasan invariant. Seluruh sub-agent hilir wajib membaca berkas ini sebelum mengetik kode.
     - `TEMUAN.md`: Dokumentasi temuan lapangan, keterbatasan library, atau bug internal yang ditemukan selama eksekusi.
     - `KEPUTUSAN.md`: Keputusan konsensus teknis yang mengikat seluruh armada. Jika terjadi ketidaksepakatan antar-agen, keputusan agen induk bersifat final.
     - Untuk pembobotan konsensus dan pencegahan halusinasi kelompok, rujuk `multiagent-consensus-circuit-breaker` (voting terbobot bukti empiris) dan `byzantine-multiagent-debate` (audit quorum BFT).
   - *Akibat kegagalan:* Bertanya hal sepele ke pengguna menurunkan kecepatan eksekusi dan merusak fokus bisnis; sebaliknya, beroperasi tanpa kontrak tertulis memicu ketidakcocokan antarmuka modul saat digabungkan.

7. **Manajemen Kerja Paralel yang Efisien (Dynamic Slotted Pipeline)**
   - **Dekomposisi Kecil dan Banyak:** Pecah pekerjaan besar menjadi unit-unit tugas kecil berdurasi 1-3 menit daripada beberapa tugas raksasa. Tugas kecil mencegah pekerja cepat menganggur menunggu pekerja yang paling lambat.
   - **Pengisian Ulang Slot Seketika (Slot Refilling):** Jangan menunggu satu gelombang (*batch*) selesai penuh. Begitu satu sub-agent menuntaskan pekerjaannya dan lolos gerbang verifikasi, langsung isi slot konkurensi yang kosong dengan tugas antrean berikutnya.
   - **Larangan Pengambilalihan Tugas Berjalan:** Pekerjaan yang telah didelegasikan kepada satu sub-agent pantang diambil alih oleh sub-agent lain. Mengambil alih tugas memicu penulisan berkas tumpang tindih (*race condition*) dan membatalkan keabsahan audit gerbang.
   - **Penanganan Pekerja Macet:** Jika transkrip satu sub-agent berhenti bergerak melampaui batas toleransi sementara yang lain berjalan maju, segera eksekusi `stop`. Ambil hasil parsial yang valid di disk, lalu delegasikan sisa tugas yang belum selesai sebagai tugas baru.
   - **Mandor Pantang Berdiam Diri:** Selagi sub-agent bekerja di worktree masing-masing, agen induk memanfaatkan waktu tunggu untuk menyiapkan skrip verifikasi, memeriksa log parsial, mengagregasi dokumentasi, atau merapikan indeks repositori.
   - *Akibat kegagalan:* Antrean kaku berbasis gelombang membuang 40-60% siklus CPU VPS; pengambilalihan tugas aktif menyebabkan kerusakan berkas yang tidak dapat dipulihkan.

## Pitfalls
- **Verifikasi Pasca-Gabung (Post-Merge Trap):** Menggabungkan cabang ke inti sebelum pengujian tuntas. Akibatnya: kode rusak mencemari cabang inti dan memicu pemadaman layanan pada tenant ERP.
- **Klaim Mandiri Tanpa Verifikasi Ulang (Self-Report Blindness):** Mempercayai klaim sub-agent bahwa fiturnya telah berjalan sempurna tanpa menguji langsung commit HEAD. Akibatnya: kode stub atau implementasi palsu meresap ke sistem.
- **Ledakan Rekursi Tanpa Anggaran (Spawning Explosion):** Mengaktifkan kedalaman tak terbatas tanpa batas waktu dan tanpa pemantauan RAM. Jumlah pekerja boleh tak terbatas, tetapi tanpa `child_timeout_seconds` dan pemantauan memori, biaya token meledak dan OOM-killer VPS membunuh proses PM2 serta basis data tenant — bukan hanya sub-agent.
- **Eskalasi Trivial ke Pengguna (Human Distraction Fatigue):** Mengajukan pertanyaan teknis yang jawabannya ada di dokumentasi atau web ke Mas Bagas. Akibatnya: memperlambat laju proyek dan membebani pengguna dengan rincian implementasi.
- **Antrean Tunggu Gelombang Kaku (Wave Stall Bottleneck):** Menunggu seluruh tugas dalam satu gelombang selesai sebelum memulai tugas baru. Akibatnya: pemborosan sumber daya komputasi VPS karena agen cepat menganggur lama.

## Verification
- Jalankan modul pemeriksa gerbang `periksa_gerbang_gabung` dan pastikan seluruh kondisi `assert` lulus tanpa galat.
- Periksa status Git worktree: pastikan seluruh cabang kerja `fleet/*` telah dibersihkan secara atomik setelah penggabungan terverifikasi.
- Pastikan berkas `KONTRAK-ANTARMUKA.md` dan `KEPUTUSAN.md` terbit pada direktori kerja sebelum fase koding paralel dimulai.

*Skipped: implementasi soket IPC antar-proses p2p, memilih pertukaran dokumen berbasis disk lokal.*
*Add when: frekuensi sinkronisasi status antar-agen melampaui kemampuan I/O disk pada armada di atas 50 pekerja aktif.*
