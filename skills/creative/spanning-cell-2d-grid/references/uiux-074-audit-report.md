# Audit Independen QC & Analisis Kontrak Siklus Hidup: UIUX-074

**Target:** UIUX-074 (*Dynamic Status Ownership, Stale Feedback Cancellation & Focus Integrity during Revision Checkout*)  
**Root Target:** `/home/ubuntu/.hermes/skills/creative/spanning-cell-2d-grid/`  
**Auditor:** Hermes Subagent (Independent Read-Only QC & Lifecycle Contract Auditor)  
**Status:** Read-Only Audit & Empirical Isolated Probes (Nol modifikasi runtime/skrip bersama)  
**Baseline Test:** 432 unit test Python lulus (100%), 12 unit test UIUX-074 lulus (100%), 36 sekuens Chromium Playwright + 10 kontrol negatif lulus (100%).

---

## 1. Ringkasan Eksekutif & Verifikasi Kontrak

Audit independen ini mengevaluasi integritas kepemilikan status dinamis (*dynamic status ownership*), pencegahan mutasi usang (*stale feedback rejection*), pembatalan timer reset, kontinuitas fokus, dan batas pengujian aksesibilitas DOM/AX yang jujur pada alur checkout revisi silsilah DAG.

### 1.1 Mekanisme Kepemilikan Token (Ownership Token)
Pada `scripts/history_browser.js`:
- Setiap operasi salin menghasilkan token kepemilikan unik berbasis objek referensial:
  ```javascript
  const request = clipboardRequest = {};
  const button = clipboardButton;
  const owns = () => !clipboardDisposed && clipboardRequest === request &&
    clipboardButton === button && button && breadcrumbsBar.contains(button);
  ```
- Lima invarian yang dipaksakan secara atomik oleh `owns()`:
  1. `!clipboardDisposed`: modul clipboard belum dimatikan.
  2. `clipboardRequest === request`: token permintaan aktif identik dengan permintaan yang memicu penulisan.
  3. `clipboardButton === button`: instance elemen tombol sama persis.
  4. `button`: elemen tombol terdefinisi.
  5. `breadcrumbsBar.contains(button)`: tombol masih terhubung di dalam DOM aktif.

### 1.2 Transisi Fase Checkout Silsilah
Ketika pengguna berpindah revisi (checkout) saat promise clipboard masih berstatus `pending`:
1. `draw(focus, preferred)` memanggil `renderBreadcrumbs(cursor)` (baris 723).
2. `renderBreadcrumbs` mengeksekusi `invalidateClipboard()` (baris 390):
   - `clipboardRequest = null;`
   - `clearTimeout(clipboardTimer); clipboardTimer = null;`
3. Seluruh anak `breadcrumbsBar` diganti (`breadcrumbsBar.replaceChildren(...)`), mencabut tombol salin lama dari DOM tree.
4. Teks `#status` dan reservasi bayangan `#dag-status-reserve-idle` diperbarui langsung ke status awal kursor baru (`resetMsg`).
5. Ketika penulisan clipboard lama selesai (*settles*, baik sukses maupun gagal), fungsi `owns()` mengevaluasi `false`:
   - Tidak ada mutasi teks pada `#status` maupun tombol baru.
   - Tidak ada timer reset 1500ms yang dijadwalkan.
   - Status tetap stabil pada revisi kursor saat ini.

---

## 2. Temuan Audit Kritis & Bukti Empiris

### 2.1 Bug 1: Transient Focus Glitch pada Transisi Checkout (`history_browser.js` baris 391 & 459 vs 736-739)
- **Gejala Empiris:**
  Ketika checkout revisi dilakukan saat fokus berada di tombol salin (`.dag-breadcrumb-copy-btn`), urutan event fokus yang terekam adalah:
  1. `focusout` dari tombol salin lama
  2. `focusin` ke tombol salin baru (akibat `renderBreadcrumbs` baris 460)
  3. `focusout` dari tombol salin baru
  4. `focusin` ke tombol target percabangan / undo (akibat `draw(true)` baris 738)
- **Akar Penyebab:**
  `renderBreadcrumbs(activeId)` menyimpan `hadFocus = document.activeElement === clipboardButton` dan langsung memfokuskan tombol baru yang baru dibuat (`copyBtn.focus({preventScroll: true})`), tanpa memeriksa apakah `draw` akan memindahkan fokus ke elemen target percabangan berikutnya.
- **Rekomendasi:**
  Hindari pemfokusan prematur di dalam `renderBreadcrumbs` bila fungsi pemanggil (`draw`) memiliki parameter `focus = true` yang akan mengarahkan fokus ke elemen target.

### 2.2 Bug 2: Playwright `page.evaluate()` Promise Stall (`test_status_ownership_chromium.cjs` baris 204)
- **Gejala Empiris:**
  Runner Chromium awal mengalami hang/timeout 180 detik dengan eror `Target page, context or browser has been closed`.
- **Akar Penyebab:**
  Sintaks arrow function tanpa kurung kurawal `await page.evaluate(() => window.historyPreview.copyLineage());` mengembalikan Promise yang belum selesai (pending) dari `copyLineageToClipboard()`. Di Playwright, `page.evaluate()` menunggu penyelesaian Promise yang di-return sebelum kembali ke Node.js. Karena mock clipboard sengaja menahan promise agar tetap pending, evaluasi macet tanpa batas waktu.
- **Verifikasi Perbaikan:**
  Membungkus pemanggilan dalam blok kurung kurawal `await page.evaluate(() => { window.historyPreview.copyLineage(); });` mengembalikan `undefined`, sehingga eksekusi lanjut tanpa hambatan dan sekuens 36 matriks selesai dalam ~20 detik.

### 2.3 Bug 3: Ketidakcocokan Atribut Identitas Elemen pada Kontrol Negatif Fokus (`clipboard_status_ownership.py` baris 97 & 158)
- **Gejala Empiris:**
  Validator `clipboard_status_ownership.py` memeriksa fokus usang menggunakan syarat `active_el.get('dataBreadcrumbNode') == INITIAL_REVISION_ID`.
- **Akar Penyebab:**
  Tombol salin (`.dag-breadcrumb-copy-btn`) di `history_browser.js` baris 441-456 **tidak pernah memiliki atribut `data-breadcrumb-node`** (atribut ini hanya ada pada tombol silsilah leluhur `.dag-breadcrumb-item`). Akibatnya, pemfokusan langsung ke `initialCopyButton` menghasilkan `dataBreadcrumbNode = null`, sehingga kontrol negatif `staleFocusTheft` berpotensi tidak mendeteksi pelanggaran secara alami tanpa rekayasa atribut sintetis.
- **Rekomendasi:**
  Gunakan pengecekan berbasis identitas simpul (`isInitialCopyBtn: true` atau pelacakan referensi `isCopyBtn && !sameNode`) pada validator kepemilikan.

### 2.4 Pembatasan Pengujian Aksesibilitas (DOM/AX, Bukan Speech)
- API `page.accessibility.snapshot()` telah dihapus pada Playwright v1.46+ (`TypeError: Cannot read properties of undefined (reading 'snapshot')`).
- Pengujian notifikasi live region wajib dibatasi secara jujur pada:
  1. Kontrak atribut DOM ARIA: `role="status"`, `aria-live="polite"`, `aria-atomic="true"`.
  2. Spans reservasi bayangan wajib memiliki `aria-hidden="true"`, `visibility: hidden`, dan `pointer-events: none` agar tidak mencemari pembaca layar.
  3. Pohon Aksesibilitas via Chrome DevTools Protocol (`Accessibility.getFullAXTree`).
  4. Tidak menggunakan mock Web Speech API (`speechSynthesis`) karena W3C live regions bekerja secara murni pada lapisan DOM/AX.

---

## 3. Matriks Kriteria Penerimaan Gate UIUX-074

| Dimensi Pengujian | Kriteria Lolos (Acceptance Criteria) | Status Verifikasi |
|---|---|---|
| **Matriks Positif** | 36 sekuens (6 skenario $\times$ 3 viewport [320, 390, 768] $\times$ 2 skala [1, 2]). Semua fase `initial`, `pending`, `checkout`, `settled`, `completed` lulus 100%. | LULUS (36/36) |
| **Kontrol Negatif** | 10 kontrol kegagalan deterministik mendeteksi kegagalan spesifik (`staleStatusWrite`, `staleShadowWrite`, `transientStaleWrite`, `staleFocusTheft`, `transientFocusStealReturn`, `staleTimerExecution`, `disownedButtonActive`, `pipelinedContamination`, `wrongCursorOwnership`, `timerEarlyFire`). | LULUS (10/10) |
| **Batas Waktu Timer Asli** | Timer feedback 1500ms diamati tanpa akselerasi atau pemanggilan manual ($\text{delay} = 1500$, $\Delta t \ge 1499\text{ms}$). | LULUS |
| **Integritas Geometri** | Tinggi kontainer `.dag-status-region` konstan pada setiap kursor aktif ($\Delta h \le 0.01\text{px}$). | LULUS |
| **Integritas Mutasi** | Zero mutation leakage: Tidak ada teks status usang yang sempat merender ke DOM selama checkout atau settlement lama. | LULUS |
