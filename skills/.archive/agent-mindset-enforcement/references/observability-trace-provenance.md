# Observability Trace Provenance & Integrity Architecture

## 1. Hierarki Trace & Identifiers
Setiap alur kerja observabilitas wajib mematuhi pemisahan hirarkis tanpa pencemaran silang (*zero cross-trace contamination*):
```text
PROJECT (e.g. design-library)
└── SESSION (e.g. sess_hermes_20260920_01)
    └── TRACE (e.g. trace_hermes_21498) [Task-Scoped]
        ├── SPAN (e.g. span_meta_001, span_builder_001)
        │   ├── EVENT (sequence_number, payload_json)
        │   ├── TOOL CALL (duration_ms, exit_code, args_json)
        │   └── VERIFICATION (claim_statement, method, evidence_json)
        └── CHILD SPAN (parent_span_id linkage)
```

## 2. Aturan Kueri Terisolasi (Isolated Query Contract)
Dilarang keras menggunakan kueri global yang tidak terikat trace:
- **SALAH (Mencemari Sesi)**: `SELECT * FROM verifications ORDER BY created_at DESC LIMIT 10`
- **BENAR (Trace-Scoped)**: `SELECT * FROM verifications WHERE trace_id = ? ORDER BY created_at ASC`
- **BENAR (Memory Provenance)**: `SELECT * FROM memory_mutations WHERE source_trace_id = ?`

## 3. Doktrin Anti-Fixture (Pure Runtime Ingestion)
1. **Zero Mock Traces**: Dilarang membuat skrip seed buatan atau data fixture palsu agar dasbor terlihat penuh.
2. **Zero Manual Inserts**: Seluruh event (`task.started`, `tool.completed`, `verification.completed`, `task.completed`) wajib diekstrak secara otomatis oleh engine sinkronisasi langsung dari database eksekusi fisik runtime (`~/.hermes/state.db`).
3. **Exact Count Assertion**:
   $$\text{COUNT(database events WHERE trace\_id = current\_trace)} \equiv \text{COUNT(events rendered in dashboard)}$$
   Jika ada selisih angka sekecil apa pun, audit dinyatakan **FAIL**.

## 4. Kontrak Provenance Metrik (Metric Provenance Contract)
Setiap metrik kustom (VCR, PCR, TII, AQS) dilarang ditampilkan dengan nilai angka acak/halusinasi. Wajib mendeklarasikan metadata lengkap:
- `name`: Nama metrik terstandarisasi.
- `formula`: Rumus matematis eksplisit (misal `verified_claims / total_claims * 100%`).
- `inputs_count`: Jumlah sampel nyata yang dihitung.
- `scope`: `TRACE` (lingkup tugas) atau `GLOBAL` (lingkup sistem).
- `threshold`: Nilai batas ambang peringatan (misal $TII < 0.15$).

## 5. Seleksi & Mutasi Memori Bersyarat (Conditional Memory Ingestion)
Mutasi memori (`memory_mutations`) hanya boleh dicatat ke trace jika task tersebut benar-benar menghasilkan aturan atau prinsip baru yang teruji.
- Jika task hanya berupa verifikasi rutin atau validasi bug tanpa temuan arsitektural baru: **Jumlah memory event wajib 0**.
- Dilarang memaksakan pencatatan memori sampah (*junk memory*) hanya demi mengisi kolom antarmuka.

## 6. Native Event-Driven Realtime Pipeline
Mekanisme pengamatan waktu nyata wajib mematuhi aliran native berbasis event:
```text
HERMES RUNTIME
      ↓ (Native Hooks)
pre_llm_call (model.started)
pre_tool_call (T0: tool.started / RUNNING)
post_tool_call (T1: tool.completed / DONE atau FAILED)
on_session_finalize (task.completed)
      ↓ (HTTP POST Loopback, Latency < 5ms)
AOMS NATIVE DISPATCHER
      ├──────────────────────────┐
      ↓                          ↓
SQLITE WAL PERSISTENCE    SOCKET.IO TRACE ROOM (trace:<id>)
(source = 'runtime')             ↓
      │                   BROWSER CLIENT
      │                   (DOM Update Instan)
      ↓
STATE.DB RECONCILIATION
(Hanya fallback jika hook terputus, source = 'reconciliation')
```

## 7. Trace-Scoped Socket Isolation & Reconnect Catch-Up
1. **Pemisahan Room**: Dasbor wajib bergabung ke room spesifik `trace:<trace_id>`. Server dilarang memancarkan event telemetri ke ruang publik global tanpa filter room.
2. **Protokol Catch-Up**: Saat koneksi WebSocket terputus dan tersambung kembali, klien mengirimkan `{ trace_id, since_sequence }`. Server merespons dengan `catch_up_batch` untuk memulihkan event yang terlewat secara sekuensial tanpa duplikasi.

## 8. State Machine & Klasifikasi Hasil (Outcome Classification)
- **Status Formal Tugas**: Wajib melalui `CREATED -> RUNNING -> VERIFYING -> COMPLETED / FAILED`. Dilarang meninggalkan status menggantung (*zombie active states*).
- **Klasifikasi Hasil**:
  - `SUCCESS_VERIFIED`: Tugas selesai dan seluruh klaim kritis teruji dengan bukti empiris.
  - `SUCCESS_UNVERIFIED`: Tugas selesai fungsional namun tanpa bukti assertion eksplisit.
  - `PREMATURE_TERMINATION`: Tugas dinyatakan selesai saat verifikasi kritis berstatus gagal/terlewat.
  - `FAILED_BLOCKED`: Terhenti karena kegagalan infrastruktur atau tool yang tak terpulihkan.

## 9. Pengawasan Perilaku Lintas Tugas ("Otak Pengawas")
Sistem observabilitas wajib mengaudit riwayat puluhan tugas untuk menghasilkan diagnosis perilaku:
- **Verification Compliance Rate**: Persentase tugas modifikasi kode yang diverifikasi secara empiris (target $\ge 85\%$).
- **Tool Friction Sentinel**: Pelacak perulangan perintah gagal (*repeated failed tool calls*) untuk mendeteksi kemacetan agen.
- **Memory Hygiene Guard**: Penjaga agar aturan global tidak dipromosikan dari observasi tunggal tanpa pengujian terulang.
- **Actionable Recommendations**: Rekomendasi otomatis berprioritas P1/P2 untuk benchmark peningkatan agen berikutnya.

