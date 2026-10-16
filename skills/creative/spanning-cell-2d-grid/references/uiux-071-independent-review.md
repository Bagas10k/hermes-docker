# Independent Review: UIUX-071 Research Design & Transient-Focus/Scroll Falsification

**Target:** UIUX-071 (*Native focusin/focusout event continuity, transient blur/refocus elimination, and deliberate keyboard departure under nested reflow and timer reset*)  
**Component:** `spanning-cell-2d-grid` (`scripts/history_browser.js`, `scripts/test_nested_reflow_chromium.cjs`, `scripts/clipboard_nested_reflow.py`)  
**Status:** Independent Architectural & Falsification Review (No application code edits)  
**Date:** Oktober 2026  
**Auditor:** Hermes Agent (Subagent Independent Audit)

---

## Ringkasan Eksekutif (Indonesian Summary)

Penelitian UIUX-071 memperluas verifikasi UIUX-070 dengan fokus utama pada **integritas transient-focus dan pencegahan unsolicited scroll** selama siklus hidup interaksi penyalinan clipboard lineage pada komponen `spanning-cell-2d-grid`. 

Pada arsitektur UIUX-070 sebelumnya, verifikasi hanya memotret status akhir (discrete snapshot) dari `document.activeElement` dan scroll container offset (`scrollTop` dan `scrollLeft`). Pendekatan snapshot diskret ini memiliki kelemahan mendasar (blind spot):
1. **Transient Blur/Refocus:** Komponen atau peramban dapat mengalami pelepasan fokus sesaat (`blur`/`focusout`) dan pemulihan fokus kembali (`focus`/`focusin`) selama reflow/resize kontainer tanpa terdeteksi oleh snapshot status akhir.
2. **Programmatic Focus Masking:** Pemanggilan `element.focus()` via skrip menghasilkan objek event dengan atribut `event.isTrusted === true` berdasarkan standar WHATWG/W3C (karena di-dispatch oleh User Agent). Ini berisiko memalsukan bukti interaksi pengguna asli jika harness atau komponen melakukan "focus repair" secara diam-diam.
3. **Unsolicited Scroll & Transient Restoration:** Perubahan tata letak atau pemulihan fokus (seperti default `preventScroll: false`) dapat memicu scroll yang tidak diinginkan (unsolicited scroll) pada kontainer dalam/luar, atau scroll sesaat yang kemudian dikembalikan sebelum snapshot diambil.
4. **Deliberate Departure Disruption:** Setelah janji (`writeText` Promise) diselesaikan (`success` / `failure`), penekanan `Tab` (maju) atau `Shift+Tab` (mundur) oleh pengguna sengaja memindahkan fokus ke elemen tetangga. Ketika timer reset (1500 ms) berakhir dan merestorasi label tombol menjadi "Salin Rute", fokus dan scroll tidak boleh dicuri kembali ke tombol salin.

Review independen ini menetapkan matriks 36 sekuens (3 viewport × 2 skala font × 2 hasil janji × 3 mode keberangkatan: `stay`, `forward`, `backward`), 8 fase observasi per sekuens (total 288 checkpoint fase), 8 kontrol negatif pemalsuan (falsification negative controls), pelacakan trace event berbasis sekuens monotonik, dan pembatasan klaim yang ketat tanpa klaim screen-reader atau WCAG universal.

---

## 1. Official Standards Grounding & Specifications

Investigasi spesifikasi resmi standar peramban (W3C dan WHATWG) menghasilkan landasan normatif berikut:

### 1.1 W3C UI Events § 3.3 Focus Events & Event Order
- **Sumber Resmi:** [W3C UI Events Specification § 3.3.2 Focus Event Order](https://w3c.github.io/uievents/#events-focusevent-event-order)  
- **MDN Reference:** [MDN Web Docs: FocusEvent](https://developer.mozilla.org/en-US/docs/Web/API/FocusEvent) & [MDN: FocusEvent Order of Events](https://developer.mozilla.org/en-US/docs/Web/API/FocusEvent#order_of_events)
- **Urutan Normatif Perpindahan Fokus:** Ketika fokus berpindah dari Elemen $A$ ke Elemen $B$:
  1. `blur`: dikirim ke $A$ (tidak membuih/does not bubble).
  2. `focusout`: dikirim ke $A$ (membuih/bubbles).
  3. `focus`: dikirim ke $B$ (tidak membuih/does not bubble).
  4. `focusin`: dikirim ke $B$ (membuih/bubbles).
- **Implikasi Gate:** Event listener tingkat dokumen/jendela untuk `focus` dan `blur` **harus didaftarkan pada capture phase** (`useCapture: true`), sedangkan `focusin` dan `focusout` dapat ditangkap pada bubbling phase. Setiap transisi fokus yang sah harus mematuhi urutan kanonikal ini.

### 1.2 Event.isTrusted Semantics & The Programmatic Focus Trap
- **Sumber Resmi:** [WHATWG DOM § 2.7 Interface Event (isTrusted)](https://dom.spec.whatwg.org/#dom-event-istrusted)  
- **MDN Reference:** [MDN Web Docs: Event.isTrusted](https://developer.mozilla.org/en-US/docs/Web/API/Event/isTrusted)
- **Karakteristik Kritis:** Berdasarkan spesifikasi DOM, `event.isTrusted` bernilai `true` apabila event di-dispatch oleh User Agent (browser engine), dan bernilai `false` hanya jika di-dispatch via skrip menggunakan `element.dispatchEvent(new Event(...))`.
- **Temuan Eksperimental & Verifikasi:** Ketika JavaScript memanggil metode `element.focus()`, User Agent mengeksekusi *focus update steps* internal dan men-dispatch event `focus` serta `focusin` dengan **`isTrusted === true`**.
- **Konsekuensi Pemalsuan:** Pengecekan sederhana `if (event.isTrusted)` **TIDAK DAPAT** membuktikan bahwa interaksi berasal dari pengguna keyboard asli! Programmatic focus yang dipanggil oleh harness atau komponen akan lolos sebagai "trusted". Gate UIUX-071 harus mengkorelasikan perpindahan fokus dengan event `keydown` asli (`Tab` atau `Shift+Tab`) dan melarang event fokus apa pun pada fase yang tidak melibatkan input pengguna.

### 1.3 WHATWG HTML Focus Processing Model & preventScroll
- **Sumber Resmi:** [WHATWG HTML Specification § 6.5.3 Focus Processing Model](https://html.spec.whatwg.org/multipage/interaction.html#focus-processing-model)  
- **MDN Reference:** [MDN Web Docs: HTMLElement.focus()](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus)
- **Semantik Scroll:** Secara default, pemanggilan `element.focus()` memiliki opsi implisit `{preventScroll: false}`, yang memerintahkan browser untuk menggulir kontainer leluhur hingga elemen berada dalam viewport (*scroll into view*). Opsi `{preventScroll: true}` mencegah scrolling otomatis tersebut.
- **Konteks Kode Aplikasi:** Di dalam `scripts/history_browser.js` (baris 452–454):
  ```javascript
  breadcrumbsBar.replaceChildren(...items);
  if (hadFocus && copyBtn.isConnected && typeof copyBtn.focus === 'function') {
    copyBtn.focus({preventScroll: true});
  }
  ```
  Komponen secara eksplisit menggunakan `preventScroll: true` saat me-render ulang breadcrumbs. Namun, pemanggilan `replaceChildren` menghancurkan elemen DOM lama dan membuat tombol baru. Jika ini terjadi saat scrolling/pending, ini adalah *DOM node identity churn* dan memicu pelepasan fokus sesaat.

### 1.4 Scroll Event Semantics & Asynchronous Dispatch
- **Sumber Resmi:** [W3C CSSOM View Module § 12. Scrolling](https://www.w3.org/TR/cssom-view-1/#scrolling) & [W3C UI Events § 3.6 Scroll Events](https://w3c.github.io/uievents/#event-type-scroll)
- **Karakteristik:** Event `scroll` pada elemen kontainer tidak membuih (does not bubble; `bubbles: false`), hanya event `scroll` pada `document` yang mencapai `window`. Oleh karena itu, pengawasan scroll harus memasang listener langsung pada masing-masing kontainer: `#dag-scroll-outer`, `#dag-scroll-inner`, serta `window`.
- Event `scroll` di-dispatch secara asynchronous sebelum frame rendering berikutnya. Snapshot posisi statis tidak dapat membuktikan ketiadaan transient scroll tanpa pemantauan counter event `scroll`.

---

## 2. Review of Existing Clipboard & Harness Code

Pemeriksaan mendalam terhadap artefak yang ada (`scripts/history_browser.js`, `scripts/test_nested_reflow_chromium.cjs`, `scripts/clipboard_nested_reflow.py`) mengungkap risiko teknis berikut:

### 2.1 Mekanisme Kepemilikan Timer pada `history_browser.js`
Dalam fungsi `copyLineageToClipboard()`:
```javascript
clipboardTimer = setTimeout(() => {
  if (!owns()) return;
  clipboardTimer = null;
  clipboardRequest = null;
  button.textContent = 'Salin Rute';
  button.setAttribute('aria-label', 'Salin seluruh jejak silsilah rute ke clipboard');
  button.classList.remove('copied');
  if (status && history && history.nodes && history.nodes[cursor]) {
    const node = history.nodes[cursor];
    setStatus(`Versi ${cursor}. ${node.children ? node.children.length : 0} cabang lanjutan.`);
  }
}, 1500);
```
- **Kondisi `owns()`:** Mengecek `!clipboardDisposed && clipboardRequest === request && clipboardButton === button && button && breadcrumbsBar.contains(button)`.
- **Risiko:** Fungsi `owns()` bernilai `true` meskipun fokus pengguna telah berpindah ke elemen lain (misalnya SVG DAG atau breadcrumb sebelumnya). Ketika callback timer dieksekusi setelah 1500 ms, callback memperbarui atribut DOM dan textContent.
- **Verifikasi UIUX-071:** Memastikan bahwa eksekusi pemulihan label pada 1500 ms **TIDAK** memanggil `.focus()`, tidak merebut kembali fokus dari tetangga, dan tidak memicu reflow yang mengakibatkan unsolicited scroll.

### 2.2 Blind Spot pada Snapshot Phase UIUX-070
Pada `scripts/test_nested_reflow_chromium.cjs`, fungsi `extractPhase` hanya mengumpulkan status instan:
```javascript
return {
  sameNode: b === window.initialCopyButton,
  isConnected: Boolean(b && b.isConnected),
  activeElementMatchesBtn: Boolean(document.activeElement && document.activeElement.matches('.dag-breadcrumb-copy-btn')),
  trustedClicks: window.trustedClicks || 0,
  writeCalls: window.writeCalls || 0,
  outerScrollTop: outer ? outer.scrollTop : 0,
  innerScrollLeft: inner ? inner.scrollLeft : 0,
  containerWidth: outer ? outer.clientWidth : 0,
  windowWidth: window.innerWidth,
  windowHeight: window.innerHeight
};
```
- **Kelemahan:** Jika terjadi event `blur` dan `focus` kembali dalam mikrodetik yang sama (misalnya selama mutasi style `maxWidth` atau `scrollTop`), `activeElementMatchesBtn` tetap bernilai `true` pada saat snapshot dievaluasi.
- **Kebutuhan:** Buffer trace event `focusTrace` berurutan yang mencatat setiap event `focusin`, `focusout`, `focus`, `blur`, dan `scroll` beserta fase aktif saat event terjadi.

---

## 3. Seven Precise Technical Risks & Falsification Analysis

| # | Resiko Teknis | Mekanisme Terjadinya Bug / False-Proof | Aturan Gate & Pengecekan Falsifikasi |
|---|---------------|---------------------------------------|--------------------------------------|
| **K1** | **Binding Trace Checkpoints to Phases** | Trace event ditampung dalam array global tanpa pemisahan per fase. Gate hanya mengecek total event di akhir pengujian, sehingga event liar pada fase stabil (misal: blur saat resize) terlewat. | Setiap fase harus memiliki checkpoint trace `[phaseStart, phaseEnd]`. Pada fase `pending`, `scrolled`, `shrunk`, `regrown`, `settled`, dan `stay`, jumlah event fokus keluar/masuk harus **persis 0**. |
| **K2** | **Event Listener Coverage Deficit** | Listener hanya dipasang pada tombol salin, atau hanya pada `document` bubbling. Jika tombol di-remount atau fokus jatuh ke `document.body`, listener lokal tidak menangkap event. | Wajib memasang listener komprehensif: (1) `focus`/`blur` dengan `capture: true` pada `window`, (2) `focusin`/`focusout` pada `document`, (3) `scroll` pada `window`, `#dag-scroll-outer`, dan `#dag-scroll-inner`. |
| **K3** | **Event Sequence Monotonicity Violation** | Event teracak urutannya karena asynchronous microtask queue atau race condition penanganan event handler. | Setiap event trace wajib memiliki ID urutan inkremental (`seq++`) dan `timestamp` dari `performance.now()`. Wajib mematuhi urutan W3C saat perpindahan: `blur` $\to$ `focusout` $\to$ `focus` $\to$ `focusin`. |
| **K4** | **Missing or Incomplete Trace Window** | Listener diinisialisasi terlambat (setelah navigasi `#outside`), atau dibersihkan terlalu cepat sebelum callback timer 1500 ms selesai. | Inisialisasi trace buffer di level `page.evaluateOnNewDocument` atau tepat sebelum navigasi pertama. Buffer bersifat append-only selama seluruh siklus hidup test runner. |
| **K5** | **Exact Neighbor Identity Ambiguity** | Gate hanya memverifikasi `activeElement !== copyBtn` saat tombol `Tab` atau `Shift+Tab` ditekan, menerima sembarang elemen acak (misal: `<body>` atau `#dag-search-input`). | Validasi identitas deterministik berbasis struktur DOM riil:<br>• **Forward (`Tab`):** Tag `g`, `role="button"`, `data-node="alpha"`.<br>• **Backward (`Shift+Tab`):** Tag `BUTTON`, kelas `dag-breadcrumb-item active`, `data-breadcrumb-node="anak-雪"`.<br>• **Stay:** Tetap pada `.dag-breadcrumb-copy-btn`. |
| **K6** | **Programmatic Focus Masking (Trusted Trap)** | Programmatic `copyBtn.focus()` menghasilkan `isTrusted: true`, menyamarkan hilangnya fokus asli sebagai interaksi pengguna. | Validasi ketat: perpindahan fokus ke tetangga **hanya sah** jika didahului langsung oleh native `keydown` (`Tab` / `Shift+Tab`). Pada fase non-keyboard, kemunculan event fokus apa pun (meskipun `isTrusted === true`) langsung menggagalkan gate. |
| **K7** | **Scroll Snapshots Hide Restoration** | Terjadi unsolicited scroll akibat layout shift atau focus scroll-into-view, tetapi skrip mengembalikannya sebelum akhir fase, sehingga snapshot offset tampak normal. | Memonitor counter event `scroll` pada kontainer luar dan dalam. Selama fase `shrunk`, `regrown`, `settled`, `departure`, dan `post_timer`, pertambahan event `scroll` yang tidak diminta harus **0**, dan delta offset harus identik dengan nilai perturbed. |

---

## 4. UIUX-071 36-Sequence Matrix Specification

Matriks pengujian UIUX-071 mencakup kombinasi ortogonal lengkap tanpa jalan pintas:

### 4.1 Dimensi Matriks
1. **Viewport Widths (3):** `320px` (mobile sempit), `390px` (mobile standar), `768px` (tablet).
2. **Computed Font Scales (2):** `1x` (baseline 16px), `2x` (enlarged text 32px snapshot).
3. **Promise Outcomes (2):** `'success'` (resolves clipboard write), `'failure'` (rejects clipboard write).
4. **Departure Modes (3):**
   - `'stay'`: Fokus dipertahankan pada tombol salin; menunggu timer reset 1500 ms selesai.
   - `'forward'`: Native keyboard `Tab` menuju simpul SVG DAG pertama (`alpha`).
   - `'backward'`: Native keyboard `Shift+Tab` kembali ke item breadcrumb sebelumnya (`anak-雪`).

$$\text{Total Sekuens} = 3 \times 2 \times 2 \times 3 = 36\text{ sekuens}$$

### 4.2 Delapan Fase per Sekuens (288 Observasi Fase)
Setiap sekuens dari 36 sekuens melalui 8 fase terikat checkpoint:
1. `initial`: Fokus via native `Tab` dari kontrol `#outside` ke `.dag-breadcrumb-copy-btn`.
2. `pending`: Penekanan native `Enter`; pemanggilan `copyLineageToClipboard()`; janji `writeText` ditahan pending; label berubah menjadi "Menyalin…".
3. `scrolled`: `outerScrollTop += 30px` dan `innerScrollLeft += 25px` saat operasi masih pending.
4. `shrunk`: Lebar kontainer luar dipersempit (250px pada 320, 310px pada 390, 660px pada 768) tanpa mengubah dimensi jendela browser.
5. `regrown`: `maxWidth` kontainer luar dikembalikan ke normal.
6. `settled`: Janji diselesaikan (`window.settleCopy.resolve()` atau `reject()`); label diperbarui menjadi "Tersalin!" atau "Gagal menyalin".
7. `departure`: Aksi keyboard departure dieksekusi (`stay`, `Tab` forward, atau `Shift+Tab` backward); identitas target diverifikasi.
8. `post_timer`: Jeda waktu melampaui timeout reset 1500 ms; verifikasi label kembali ke "Salin Rute", tidak ada perebutan fokus, dan tidak ada unsolicited scroll.

---

## 5. Concrete Falsification Tests & Negative Controls Suite

Gate verifikasi UIUX-071 harus menguji sekurang-kurangnya 8 kontrol negatif (fail-closed controls) menggunakan pipeline Python yang sama:

```
+-----------------------------------------------------------------------------------------+
|                               UIUX-071 NEGATIVE CONTROLS                                |
+------------------------------------+----------------------------+-----------------------+
| Negative Control Name              | Injected Fault / Anomaly   | Expected Gate Failure |
+------------------------------------+----------------------------+-----------------------+
| 1. transientBlurRefocus            | button.blur() lalu focus() | phase-focus-disruption|
| 2. unsolicitedFocusTheft           | focus() kembali saat reset | unsolicited-focus-theft|
| 3. unsolicitedScrollOnSettle       | scrollIntoView() di settle | unsolicited-scroll    |
| 4. unsolicitedScrollOnReset        | scrollTop += 10 di reset   | unsolicited-scroll    |
| 5. wrongNeighborForward            | Tab mendarat di #search    | neighbor-identity     |
| 6. wrongNeighborBackward           | Shift+Tab mendarat di body | neighbor-identity     |
| 7. programmaticFocusSpoofing       | focus() tanpa keydown      | untrusted-departure   |
| 8. stickyOcclusionAuto             | sticky overlay pointer-auto| occlusion (hit-fail)  |
| 9. stickyOcclusionPointerEventsNone| sticky overlay pointer-none| occlusion (hit-pass)  |
| 10. outlineOnly                    | overlay 1px pada outline   | occlusion             |
+------------------------------------+----------------------------+-----------------------+
```

### Rincian Kontrol Negatif Utama:
1. **`transientBlurRefocus`:** Pada fase `shrunk`, harness memanggil `b.blur(); b.focus();`. Walaupun snapshot akhir menunjukkan `document.activeElement === b`, log trace mencatat event `blur` dan `focusin` di luar jadwal. **Gate wajib menolak dengan `phase-focus-disruption`.**
2. **`unsolicitedFocusTheft`:** Pada mode departure `forward`, saat timer 1500 ms aktif di fase `post_timer`, diinjeksikan `b.focus()`. **Gate wajib menolak dengan `unsolicited-focus-theft`.**
3. **`unsolicitedScrollOnSettle`:** Pada saat settle, disimulasikan auto-scroll via `outer.scrollTop += 15`. **Gate wajib menolak dengan `unsolicited-scroll`.**
4. **`wrongNeighborForward`:** Pada mode `forward`, fokus dialihkan ke input pencarian `#dag-search-input` alih-alih simpul SVG `alpha`. **Gate wajib menolak dengan `neighbor-identity-mismatch`.**
5. **`wrongNeighborBackward`:** Pada mode `backward`, fokus dialihkan ke tombol `#undo` alih-alih `anak-雪`. **Gate wajib menolak dengan `neighbor-identity-mismatch`.**
6. **`programmaticFocusSpoofing`:** Fokus dipindahkan menggunakan `element.focus()` tanpa event keyboard native dari Playwright. Walaupun `isTrusted === true`, ketiadaan event `keydown` terkait membuat gate menolak dengan `untrusted-departure`.

---

## 6. Mathematical & Acceptance Criteria for Parent Gate

Untuk memastikan integritas matematika dan mencegah regresi pada eksekusi baru oleh worker, gate Python harus memvalidasi kriteria berikut:

1. **Matriks Lengkap Tanpa Duplikasi:**
   - Panjang array `records` tepat 36.
   - Himpunan kunci `(viewport, scale, outcome, departure)` tepat mencocoki produk Kartesius:
     $$\{320, 390, 768\} \times \{1, 2\} \times \{\text{'success'}, \text{'failure'}\} \times \{\text{'stay'}, \text{'forward'}, \text{'backward'}\}$$
2. **Kesesuaian 8 Fase per Record:**
   - Setiap record memiliki kamus `phases` berisi 8 fase kanonikal.
   - Setiap fase terikat pada metadata jendela yang konsisten (`windowWidth == viewport`, `windowHeight == initial.windowHeight`).
3. **Monotonisitas Trace Event:**
   - Nilai `sequenceId` harus berurut naik ($0, 1, 2, \dots$).
   - Nilai `timeStamp` harus monotonik tidak turun ($t_i \le t_{i+1}$).
4. **Identitas Tetangga Deterministi:**
   - Mode `forward`: `neighborTag == 'g'`, `neighborRole == 'button'`, `neighborNode == 'alpha'`.
   - Mode `backward`: `neighborTag == 'button'`, `neighborRole == None`, `neighborNode == 'anak-雪'`.
   - Mode `stay`: `activeElementMatchesBtn == True`, `returnedToCopy == True`.
5. **Pengecualian Unsolicited Scroll:**
   - Selama fase `shrunk`, `regrown`, `settled`, `departure`, dan `post_timer`, jumlah event `scroll` liar harus $0$.
   - Nilai `outerScrollTop` dan `innerScrollLeft` harus tetap konstan sesuai offset perturbed dari fase `scrolled`.
6. **Validasi Geometri Terpadu:**
   - Setiap fase tetap diverifikasi melalui audit geometri konservatif AABB outline clearance, bounding ancestor clipping, dan deteksi overlap opaque overlay yang diwarisi dari UIUX-069 dan UIUX-070.

---

## 7. Explicit Boundary Disclosures & Claim Limitations

Review ini menetapkan batasan klaim yang jujur dan dapat diverifikasi:
1. **Bukan Pengujian OS Clipboard Daemon:** Pengujian menggunakan Promise terkontrol pada `navigator.clipboard.writeText` dalam lingkungan fixture loopback HTTP. Tidak ada klaim integrasi daemon clipboard OS (seperti X11/Wayland clipboard atau clipboard manager pihak ketiga).
2. **Bukan Sertifikasi Screen-Reader / WCAG Penuh:** Pengujian membuktikan kontinuitas activeElement, urutan event fokus DOM, dan ketiadaan unsolicited scroll. Pengujian **TIDAK** memvalidasi sintesis suara screen reader (NVDA, JAWS, VoiceOver, Orca), live region announcement speech, atau kepatuhan WCAG 2.2 secara penuh.
3. **Skalasi Font Komputasi Terkontrol:** Pengujian menggunakan pengali computed font baseline (1x dan 2x), bukan browser native zoom (Ctrl +/-) atau DPI scaling sistem operasi.
4. **Konservatisme AABB Geometri:** Clearance outline dihitung menggunakan axis-aligned bounding box (AABB) dengan padding outline-width dan outline-offset. Pengujian tidak memodelkan anti-aliasing sudut melengkung pada tingkat shader GPU.

---

## 8. Summary of Primary Documentation Sources

1. **W3C UI Events Specification § 3.3.2 Focus Event Order:**  
   `https://w3c.github.io/uievents/#events-focusevent-event-order`
2. **MDN Web Docs — FocusEvent Interface & Order of Events:**  
   `https://developer.mozilla.org/en-US/docs/Web/API/FocusEvent`
3. **MDN Web Docs — Element: focusin event:**  
   `https://developer.mozilla.org/en-US/docs/Web/API/Element/focusin_event`
4. **MDN Web Docs — Element: focusout event:**  
   `https://developer.mozilla.org/en-US/docs/Web/API/Element/focusout_event`
5. **WHATWG HTML Living Standard § 6.5.3 Focus Processing Model:**  
   `https://html.spec.whatwg.org/multipage/interaction.html#focus-processing-model`
6. **MDN Web Docs — HTMLElement.focus() & preventScroll Option:**  
   `https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus`
7. **WHATWG DOM Living Standard § 2.7 Interface Event (isTrusted):**  
   `https://dom.spec.whatwg.org/#dom-event-istrusted`
8. **MDN Web Docs — Event.isTrusted Property:**  
   `https://developer.mozilla.org/en-US/docs/Web/API/Event/isTrusted`
9. **W3C CSS Positioned Layout Module Level 3 § 6.2 Sticky Positioning:**  
   `https://www.w3.org/TR/css-position-3/#sticky-pos`
10. **W3C CSSOM View Module § 10.1 Element From Point & § 12 Scrolling:**  
    `https://www.w3.org/TR/cssom-view-1/#dom-document-elementfrompoint`
