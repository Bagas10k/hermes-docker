# Audit Independen QC & Kritik Desain: UIUX-073

**Target:** UIUX-073 (*Stabilitas Tata Letak Status Dinamis & Plafon Reservasi Teks Panjang pada Alur Clipboard & Reset*)  
**Root Target:** `/home/ubuntu/.hermes/skills/creative/spanning-cell-2d-grid/`  
**Auditor:** Hermes Subagent (Independent Read-Only QC & Design Critique)  
**Status:** Read-Only Audit & Isolated Empirical Probe (Nol mutasi file aplikasi/test baseline)  
**Baseline Test:** 418 metode unit test Python lulus (100%)  

---

## 1. Ringkasan Eksekutif

Audit independen ini mengevaluasi mekanisme reservasi tata letak status clipboard pada baseline UIUX-072, mengidentifikasi celah batas penerimaan (*acceptance gaps*), dan merumuskan arsitektur minimal untuk UIUX-073.

Pada UIUX-072, stabilisasi tinggi elemen status dicapai melalui CSS Grid (`grid-template-areas: "status"`) dengan 3 elemen `<span class="dag-status-reserve">` tersembunyi (`visibility: hidden`, `pointer-events: none`). Namun, ketiga elemen tersebut hanya memuat template teks statis:
1. `"Silsilah rute berhasil disalin ke clipboard"` (42 karakter)
2. `"Gagal menyalin silsilah rute ke clipboard"` (41 karakter)
3. `"Menyalin silsilah rute ke clipboard…"` (36 karakter)

**Temuan Utama QC:**
Stabilitas visual pada UIUX-072 hanya merupakan **kebetulan semu (*accidental stability*)**, karena fixture pengujian hanya menggunakan ID cabang pendek (`anak-雪`, total 32 karakter). Begitu sistem menerima ID revisi panjang, token unbroken (seperti Git commit hash SHA-256), atau teks status terlokalisasi multi-cabang, plafon reservasi statis tersebut jebol:
- Tinggi status anjlok drastis saat proses penyalinan berlangsung ($\Delta h > 113\text{px}$), memicu reflow dan pergeseran scroll/target.
- Token tanpa spasi menyebabkan *blowout* lebar kontainer hingga lebih dari 1000px pada viewport 390px akibat default CSS Grid `min-width: auto`.
- Pengujian UIUX-072 memiliki *acceptance gap* kritis: matriks 36 sekuens tidak pernah memvariasikan panjang ID revisi, dan validator unit melakukan hardcode `statusHeight = 100`.

---

## 2. Bukti Empiris & Counterexample Terbatasi (Chromium Headless Probe)

Pengujian empiris terisolasi dijalankan menggunakan fixture headless Chromium (`scripts/uiux073_qc_probe.cjs`) pada viewport 390px, font scaling 2x, mengukur transisi fase: `initial` $\to$ `pending` $\to$ `settled` $\to$ `reset`.

### 2.1 Hasil Pengukuran Kuantitatif

| Skenario Pengujian | Initial Height | Pending Height | Settled Height | Reset Height | $\Delta h$ (Maks - Min) | Pergeseran Target | Lebar Status (ScrollWidth) | Evaluasi Gate UIUX-072 |
|---|---|---|---|---|---|---|---|---|
| **Baseline 1: Short ID (`anak-雪`)** | 113.39px | 113.39px | 113.39px | 113.39px | **0.00px** | 0.00px | 368px (Normal) | LULUS (Semu) |
| **Baseline 2: Long Branch ID** | 226.78px | 113.39px | 113.39px | 226.78px | **113.39px** | **113.39px** | 368px (Normal) | **GAGAL** (`status-height`, $\Delta h > 0.01$) |
| **Baseline 3: Unbroken SHA-256 Hash** | 113.39px | 113.39px | 113.39px | 113.39px | 0.00px | 0.00px | **1096px (Blowout!)** | **GAGAL** (Horizontal Overflow) |
| **Proposed 1: Short ID + Shadow** | 113.39px | 113.39px | 113.39px | 113.39px | **0.00px** | 0.00px | 368px | LULUS |
| **Proposed 2: Long ID + Shadow** | 226.78px | 226.78px | 226.78px | 226.78px | **0.00px** | 0.00px | 368px | LULUS |
| **Proposed 3: Unbroken Hash + Shadow** | 188.98px | 188.98px | 188.98px | 188.98px | **0.00px** | 0.00px | 368px (Wrapped) | LULUS |

### 2.2 Analisis Mekanisme Kegagalan

1. **Runtuhnya Plafon Reservasi (Counterexample 2):**
   - Pada teks ID panjang (`feat/virtualized-2d-grid-with-asymmetric-spans-and-history-undo-redo`), teks idle awal memakan 6 baris (tinggi 226.78px).
   - Saat pengguna menekan *Salin Rute*, teks `#status` berubah menjadi *"Menyalin silsilah rute ke clipboard…"*. Karena ketiga span reservasi statis hanya setinggi 3 baris (113.39px), kontainer grid langsung kolaps ke 113.39px.
   - Penurunan tinggi sebesar 113.39px memicu reflow besar. Konten dan simpul yang terfokus melompat ke atas.
   - Setelah timer native 1500ms selesai, status kembali ke teks awal dan melompat kembali ke 226.78px.
   - Gate `clipboard_scroll_anchor.py` yang mensyaratkan $\max(heights) - \min(heights) \le 0.01\text{px}$ langsung mendeteksi kegagalan `status-height`.

2. **Ledakan Lebar Kontainer / Horizontal Blowout (Counterexample 3):**
   - Pada commit hash tanpa spasi (`c98f820b784913c98b671a5392812d4a7536901234567890abcdef1234567890`), aturan CSS bawaan tidak memiliki `overflow-wrap: anywhere;`.
   - Mengikuti spesifikasi W3C CSS Grid Level 1, item grid memiliki default `min-width: auto` yang menghitung ukuran *min-content*. Karena token tidak memiliki jeda pemenggalan, *min-content* adalah lebar seluruh string unbroken tersebut.
   - Pada viewport 390px dengan font 2x, lebar elemen membengkak menjadi **1096px**, merusak batas tata letak dokumen dan memicu scroll horizontal tak diminta.

---

## 3. Identifikasi Celah Penerimaan (Acceptance Gaps) pada UIUX-072

1. **Ketiadaan Variasi Panjang String pada Matriks Pengujian:**
   - Runner `scripts/test_scroll_anchor_chromium.cjs` mengeksekusi 36 sekuens (viewport $320/390/768 \times$ scale $1/2 \times$ outcome $\times$ departure). Seluruh 36 sekuens tersebut menggunakan fixture tunggal yang sama (`anak-雪`).
   - Tidak ada pengujian positif maupun kontrol negatif untuk teks ID panjang atau token unbroken.
2. **Hardcoded Synthetic Test Assertion:**
   - Pada unit test sintetis `scripts/test_clipboard_scroll_anchor.py`, nilai `statusHeight = 100` di-hardcode secara seragam di seluruh 8 fase (`make()`, baris 87), sehingga relasi kausal antara isi teks dan tinggi grid tidak pernah diverifikasi di tingkat unit test Python.
3. **Ketiadaan Audit Lebar & Overflow Horizontal:**
   - Verifikasi geometri fokus pada `clipboard_scroll_anchor.py` memeriksa pergeseran vertikal target (`target-position`), tetapi tidak mengaudit apakah kontainer status mengalami horizontal overflow (`scrollWidth > clientWidth`).

---

## 4. Rekomendasi Arsitektur Minimal (Minimum Correct Architecture)

Sesuai prinsip *Ponytail* (solusi paling sederhana pada akar penyebab, tanpa boilerplate dan tanpa abstraksi baru):

```
                   ┌───────────────────────────────────────────┐
                   │          .dag-status-region               │
                   │ (display: grid; min-width: 0; wrap:any)   │
                   └─────────────────────┬─────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
┌───────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────────┐
│  3 Static Spans       │   │  1 Shadow Dynamic Span    │   │  Active #status Element   │
│  .dag-status-reserve  │   │  #dag-status-reserve-idle │   │  role="status"            │
│  (Clipboard messages) │   │  (Mirrors active cursor)  │   │  (Live visible feedback)  │
└───────────────────────┘   └───────────────────────────┘   └───────────────────────────┘
```

### 4.1 Komponen 1: Shadow Dynamic Reservation Span
Tambahkan satu elemen span reservasi dinamis di dalam kontainer `.dag-status-region` di `scripts/history_browser.py`:
```html
<div class="dag-status-region" aria-hidden="false">
  <span class="dag-status-reserve" aria-hidden="true">Silsilah rute berhasil disalin ke clipboard</span>
  <span class="dag-status-reserve" aria-hidden="true">Gagal menyalin silsilah rute ke clipboard</span>
  <span class="dag-status-reserve" aria-hidden="true">Menyalin silsilah rute ke clipboard…</span>
  <span class="dag-status-reserve" id="dag-status-reserve-idle" aria-hidden="true"></span>
  <p id="status" role="status" aria-live="polite" aria-atomic="true"></p>
</div>
```
- **Mekanisme:** Elemen `#dag-status-reserve-idle` memegang teks idle cabang aktif. Sepanjang siklus clipboard (saat `#status` berganti ke pesan pendek "Menyalin…" atau "Tersalin!"), span shadow ini tetap menahan teks idle cabang yang lebih tinggi di dalam grid cell yang sama.
- Secara matematis: $\text{tinggi} = \max(h_{\text{success}}, h_{\text{failure}}, h_{\text{pending}}, h_{\text{idle}})$. Tinggi grid otomatis terkunci pada batas maksimum dan **tidak pernah kolaps ($\Delta h = 0$)**.

### 4.2 Komponen 2: CSS Hardening (No Text Clipping)
Perbarui aturan CSS di `scripts/history_browser.py`:
```css
.dag-status-region { display: grid; grid-template-areas: "status"; margin: 1em 0; min-width: 0; overflow-wrap: anywhere; }
.dag-status-reserve { grid-area: status; visibility: hidden; pointer-events: none; line-height: 1.35; margin: 0; min-width: 0; overflow-wrap: anywhere; }
#status { grid-area: status; margin: 0; line-height: 1.35; min-width: 0; overflow-wrap: anywhere; }
```
- **`min-width: 0;`**: Mengizinkan item grid menyusut di bawah ukuran *min-content*, mencegah pembengkakan horizontal.
- **`overflow-wrap: anywhere;`**: Mengizinkan pemenggalan karakter pada string tanpa spasi (unbroken hash) persis di batas kontainer.
- **Larangan Keras:** Jangan gunakan `overflow: hidden`, `text-overflow: ellipsis`, atau `white-space: nowrap` yang memotong teks terbaca atau mengorbankan aksesibilitas.

### 4.3 Komponen 3: Sinkronisasi Siklus Hidup JS (Timing per Cursor Update)
Di `scripts/history_browser.js`:
- Setiap kali `cursor` diperbarui di fungsi `draw()`:
  ```javascript
  const statusReserveIdle = document.getElementById('dag-status-reserve-idle');
  const statusText = `Versi ${cursor}. ${node.children.length} cabang lanjutan.`;
  status.textContent = statusText;
  if (statusReserveIdle) statusReserveIdle.textContent = statusText;
  ```
- Pada callback reset timer 1500ms:
  ```javascript
  if (status && history && history.nodes && history.nodes[cursor]) {
    const node = history.nodes[cursor];
    const text = `Versi ${cursor}. ${node.children ? node.children.length : 0} cabang lanjutan.`;
    setStatus(text);
    if (statusReserveIdle) statusReserveIdle.textContent = text;
  }
  ```

### 4.4 Komponen 4: Text Escaping Ketat
- Di sisi server/Python (`scripts/history_browser.py`): Teks awal yang dimasukkan ke `#dag-status-reserve-idle` wajib melalui `html.escape(..., quote=True)` untuk mencegah kegagalan rendering karakter khusus (misal `<baru>`, `&`, atau kutip).
- Di sisi klien/JS (`scripts/history_browser.js`): Pembaruan DOM wajib menggunakan properti native `.textContent`, bukan `.innerHTML`.

---

## 5. Matriks Pengujian Terbatasi & Kontrol Negatif untuk UIUX-073

Untuk menutup celah penerimaan tanpa membebani runtime, matriks pengujian browser UIUX-073 direkomendasikan mencakup dimensi ID:

1. **Dimensi Variasi ID Revisi:**
   - `short`: `anak-雪` (Unicode pendek, 7 char)
   - `long`: `feat/virtualized-2d-grid-with-asymmetric-spans-and-history-undo-redo` (Slug panjang, 67 char)
   - `unbroken`: `c98f820b784913c98b671a5392812d4a7536901234567890abcdef` (Token hash 56 char tanpa spasi)
2. **Kontrol Negatif Baru:**
   - `unreservedDynamicText`: Menghilangkan `#dag-status-reserve-idle` pada teks ID panjang; wajib gagal dengan `status-height`.
   - `unbrokenTextBlowout`: Menghilangkan `min-width: 0; overflow-wrap: anywhere;` pada teks unbroken; wajib terdeteksi melalui pemeriksaan `scrollWidth > clientWidth`.
3. **Integritas Timer & Geometri:**
   - Pertahankan deadline native 1500ms tanpa akselerasi tiruan.
   - Pertahankan toleransi ketat $\Delta h \le 0.01\text{px}$.

---

## 6. Prosedur Verifikasi Runnable (Read-Only)

Pemeriksaan independen dapat dijalankan kapan saja dengan perintah berikut tanpa memodifikasi file aplikasi maupun mengganggu pekerja implementasi:

```bash
# 1. Jalankan probe kuantitatif terisolasi UIUX-073
NODE_PATH=/home/ubuntu/website-security-auditor/node_modules node scripts/uiux073_qc_probe.cjs

# 2. Verifikasi keutuhan baseline unit test Python (wajib tetap 418 metode lulus)
python3 -B -m unittest discover -s scripts -q
```
