# Hermes Cognitive Bridge & Dekomposisi Kausal Otomatis

Dokumen ini mendokumentasikan spesifikasi arsitektur dan implementasi teknis Hermes Cognitive Bridge (Fase 4 KANVAS Fleet Orchestrator) untuk memecah instruksi bahasa alami menjadi armada sub-agen terisolasi.

---

## 1. Arsitektur Dekomposisi Kognitif (Si Pintar)

Tujuan Cognitive Bridge adalah mentransformasikan instruksi pengguna tingkat tinggi (*Natural Language Prompt*) menjadi graf kausalitas asiklik (*Acyclic Directed Graph / Causal DAG*) dari 2 hingga 4 sub-agent paralel.

### Alur Kerja:
1. **Analisis Proyek:** Memeriksa repositori target (mendeteksi jenis runtime: Rust `Cargo.toml`, Node.js `package.json`, Python `pyproject.toml`).
2. **Inferensi Model Terpandu:** Mengirim prompt terstruktur ke 9Router (`127.0.0.1:20128`) menggunakan model penalaran seperti `ag/claude-sonnet-4-6` atau `cx/gpt-6-astra`.
3. **Validasi Skema & Asiklik:** Memvalidasi JSON output dan menjalankan algoritma Kahn untuk memastikan graf bebas dari siklus sirkular.
4. **Provisioning Worktree Paralel:** Membuat direktori kerja Git Worktree fisik terisolasi untuk tiap sub-tugas (`fleet/<task-id>`) lengkap dengan simlink cache bersama.
5. **Registrasi & Penjadwalan DAG:** Memasukkan seluruh tugas ke `causal_scheduler.js` dan langsung mengeksekusi sub-tugas akar (*root tasks* tanpa dependensi).

---

## 2. Kontrak Skema JSON Dekomposisi

Model penalaran diwajibkan menghasilkan output JSON murni tanpa markdown pembungkus:

```json
{
  "plan_title": "Rencana Otonom: Token Bucket Rate Limiter",
  "summary": "Implementasi algoritma token bucket, middleware integrasi, dan suite pengujian invarian.",
  "tasks": [
    {
      "id": "task-01-core-bucket",
      "goal": "Implementasikan struct TokenBucket thread-safe di Rust beserta tes unit internal.",
      "dependencies": [],
      "command": "cargo check",
      "testCommand": "cargo",
      "testArgs": ["test", "--quiet", "--test", "token_bucket_tests"]
    },
    {
      "id": "task-02-middleware-layer",
      "goal": "Buat struct RateLimitMiddleware yang mengonsumsi TokenBucket pada handler request.",
      "dependencies": ["task-01-core-bucket"],
      "command": "cargo check",
      "testCommand": "cargo",
      "testArgs": ["test", "--quiet"]
    },
    {
      "id": "task-03-integration-verify",
      "goal": "Audit invarian batas konkurensi dan pastikan tidak ada kebocoran memori pada beban tinggi.",
      "dependencies": ["task-02-middleware-layer"],
      "command": "cargo test --quiet",
      "testCommand": "cargo",
      "testArgs": ["test", "--quiet"]
    }
  ]
}
```

---

## 3. Penanganan Galat & Pelajaran Lapangan

### A. Pitfall Streaming SSE vs JSON Murni
* **Gejala:** Pemanggilan 9Router lokal menghasilkan string pembuka `data: {"id":"chatcmpl-..."}` yang menyebabkan `JSON.parse` melempar galat sintaksis tak terduga.
* **Solusi Mutlak:** Selalu menyertakan `"stream": false` pada payload HTTP POST ke `/v1/chat/completions`.

### B. Fallback Heuristik Tahan Banting (Fault-Tolerant)
Jika koneksi router terputus, token habis, atau inferensi gagal:
* Sistem TIDAK BOLEH mogok (*crash*).
* Sistem otomatis beralih ke dekomposisi heuristik deterministik dua tahap:
  1. `[task-core]`: Implementasi modul inti sesuai instruksi pengguna.
  2. `[task-verify]`: Audit invarian dan pengujian regresi deterministik (bergantung pada `task-core`).

### C. Perlindungan Siklus Sirkular (Kahn Invariant Gate)
Sebelum worktree dibuat, periksa dependensi dengan algoritma Kahn:
```javascript
function validateAcyclic(tasks) {
  const inDegree = {};
  const adj = {};
  for (const t of tasks) {
    inDegree[t.id] = t.dependencies.length;
    adj[t.id] = [];
  }
  for (const t of tasks) {
    for (const dep of t.dependencies) {
      if (adj[dep]) adj[dep].push(t.id);
    }
  }
  const queue = Object.keys(inDegree).filter(id => inDegree[id] === 0);
  let visited = 0;
  while (queue.length > 0) {
    const u = queue.shift();
    visited++;
    for (const v of adj[u] || []) {
      inDegree[v]--;
      if (inDegree[v] === 0) queue.push(v);
    }
  }
  return visited === tasks.length;
}
```
Jika `visited !== tasks.length`, tolak rencana dan minta perbaikan dekomposisi sebelum alokasi sumber daya disk/CPU.
