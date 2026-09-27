# Deduplikasi Dependensi & Protokol Gerbang Mutu (Gatekeeper)

Dokumen ini menjelaskan implementasi teknis deduplikasi ruang kerja Git Worktree dan arsitektur pengujian otomatis untuk armada sub-agen.

---

## 1. Arsitektur Deduplikasi Disk & Memori (Node.js & Rust)

### Masalah Duplikasi:
Jika sebuah proyek Node.js memiliki ukuran `node_modules` sebesar 350 MB atau proyek Rust memiliki folder `target/` sebesar 1.2 GB, dan kita menjalankan 4 sub-agen paralel, pembuatan worktree konvensional akan memakan:
- Node.js: $4 \times 350\text{ MB} = 1.4\text{ GB disk extra}$
- Rust: $4 \times 1.2\text{ GB} = 4.8\text{ GB disk extra}$ + beban kompilasi ulang CPU berulang kali.

### Solusi Tautan Simbolik & Shared Build Cache:
```bash
# Path kerja repositori utama
REPO_ROOT="/home/ubuntu/hermes-agent-foundry"
WORKTREE_DIR="/home/ubuntu/.kanvas-fleet/worktrees/task-101"

# Buat worktree terisolasi
git -C "$REPO_ROOT" worktree add -b fleet/task-101 "$WORKTREE_DIR" main

# 1. Deduplikasi dependensi Node.js
if [ -d "$REPO_ROOT/node_modules" ]; then
  ln -s "$REPO_ROOT/node_modules" "$WORKTREE_DIR/node_modules"
fi

# 2. Deduplikasi cache kompilasi Rust
if [ -d "$REPO_ROOT/target" ]; then
  ln -s "$REPO_ROOT/target" "$WORKTREE_DIR/target"
fi
```
Dengan pola ini:
- Eksekusi `cargo test` atau `npm test` di dalam worktree langsung memanfaatkan artefak biner yang telah terkompilasi, memangkas durasi pengujian menjadi $< 0.05\text{ detik}$ (sub-50ms).
- Konsumsi disk tambahan murni hanya sebatas file teks kode yang dimodifikasi ($< 1\text{ MB}$ per cabang).

---

## 2. Matriks Gerbang Mutu Invarian (Autonomous Quality Gate)

Setiap sub-agen yang selesai mengeksekusi tugas wajib melalui skrip gatekeeper sebelum cabang kerjanya diizinkan masuk antrean merge:

| Layer Uji | Target Verifikasi | Tolok Ukur Keberhasilan | Waktu Eksekusi Maksimal |
| :--- | :--- | :--- | :--- |
| **L1 (Syntax)** | AST Parsing integritas bahasa | Exit code 0, nol error parser | $< 50\text{ ms}$ |
| **L2 (Unit Test)** | Suite pengujian modular | Seluruh unit test lokal lolos | $< 2.0\text{ s}$ |
| **L3 (Sanitasi)** | Pemindaian rahasia & kredensial | Nol kebocoran pola token/key | $< 100\text{ ms}$ |
| **L4 (Kebijakan)** | Audit Nol Emoji | Nol karakter Unicode emoji | $< 20\text{ ms}$ |

---

## 3. Protokol Semi-Otonom Terverifikasi (Semi-Autonomous Merge)

Sistem membedakan secara tegas antara **verifikasi otomatis** dan **penggabungan kode ke branch utama**:
1. **Verifikasi Penuh Otomatis:** Si Pengawas secara otonom memicu L1-L4 begitu sub-agent menyelesaikan penulisan kode.
2. **Promosi Status:** Jika 100% tes lulus, cabang dipromosikan ke status `READY_TO_MERGE`.
3. **Gerbang Otorisasi Manusia:** Eksekusi penggabungan (`git merge`) tidak dilakukan secara serampangan oleh agen (*blind YOLO merge*), melainkan menunggu klik konfirmasi manual oleh arsitek (Mas Bagas) di dasbor KANVAS Fleet.
4. **Reklaim Otomatis:** Begitu penggabungan terkonfirmasi, sistem otomatis menghapus direktori worktree (`git worktree remove --force`) dan menghapus branch lokal untuk menjaga repositori tetap bersih (*zero-pollution*).

---

## 4. Integrasi Causal DAG untuk Pencegahan Konflik

Jika terdapat 2 sub-agen paralel:
- **Agen A (Backend):** Memodifikasi endpoint rute `/api/fleet/status`.
- **Agen B (Frontend):** Sedang membuat komponen UI pemanggil endpoint tersebut.

Jika Agen A melakukan perubahan skema (*API breaking change*) atau gagal tes:
1. Orkestrator memicu pembatalan kerucut kausal (*causal cone cancellation* via Pearl's Hard-Do Surgery).
2. Status Agen B diubah dari `RUNNING` menjadi `INVALIDATED` dan prosesnya dihentikan.
3. Setelah Agen A meloloskan Gerbang Mutu L1-L4 dan di-merge, Agen B dijadwalkan ulang secara dinamis dengan skema baru sebelum melanjutkan koding.
