# Independent Audit: UIUX-072 Design, Failure Mechanism & Minimal Acceptance Gate

**Target:** UIUX-072 (*Stable status geometry under default overflow-anchor:auto, full 36-sequence matrix, actual 1500ms feedback reset continuity, and new neighbor geometry verification*)  
**Skill Path:** `/home/ubuntu/.hermes/skills/creative/spanning-cell-2d-grid/`  
**Auditor:** Hermes Subagent (Independent Reviewer)  
**Date:** Oktober 2026  
**Status:** Architectural Audit & Adversarial Test Design (Strictly zero implementation edits)

---

## 1. Ringkasan Eksekutif (Executive Summary)

Audit independen ini menganalisis mekanisme kegagalan riil pada transisi UIUX-071 ke UIUX-072, merumuskan spesifikasi *minimal acceptance gate*, serta menyusun kasus uji mutasi adversarial untuk memverifikasi kontinuitas fokus dan stabilitas scroll browser bawaan (`overflow-anchor: auto`).

Pada siklus UIUX-071 sebelumnya:
1. **Penyembunyian Kegagalan Scroll Anchoring:** Suite pengujian positif UIUX-071 secara eksplisit memaksa `overflow-anchor: none` pada wrapper scroll (`#dag-scroll-outer` dan `#dag-scroll-inner`) untuk meloloskan pengujian dari pergeseran scroll 38px. Kondisi default browser (`overflow-anchor: auto`) hanya diperlakukan sebagai kontrol negatif tunggal pada satu titik koordinat (`viewport: 390, scale: 2, outcome: failure, departure: forward`).
2. **Timer Reset Dibekukan:** Timer pemulihan feedback (1500 ms) di-*freeze* (`window.setTimeout = (cb,ms)=>ms===1500?777777:realTimer(...)`), sehingga kontinuitas event, pencegahan pencurian fokus, dan kestabilan tata letak saat status kembali ke teks awal tidak pernah diuji secara riil.
3. **Geometri Target Tetangga Belum Diaudit:** Ketika fokus pengguna sengaja berpindah (`forward` via `Tab` ke simpul SVG `alpha`, atau `backward` via `Shift+Tab` ke breadcrumb `anak-雪`), verifier hanya memeriksa identitas string tag/atribut, tanpa memeriksa apakah elemen tetangga baru tersebut terpotong (clipped), tertutup overlay (occluded), atau berada dalam viewport yang sah.

Target UIUX-072 menuntut:
- Matriks penuh 36 sekuens berjalan stabil di bawah **`overflow-anchor: auto`** (bawaan browser).
- Siklus hidup 8 fase yang mencakup eksekusi nyata feedback reset 1500 ms (dengan controlled clock berlabel jujur).
- Validasi geometri lengkap elemen tetangga baru.
- Perbandingan objektif antara tata letak stabil ($\Delta h = 0$) versus opt-out anchoring (`none`), tanpa klaim palsu bahwa opt-out adalah solusi universal produksi.

---

## 2. Audit Mekanisme Kegagalan Riil (Root Cause Analysis)

### 2.1 Lokasi Kode & Mekanisme Pergeseran 38px
Pemeriksaan baris demi baris pada kode sumber aktif mengungkap rantai kausal kegagalan:

1. **`history_browser.py` (Baris 55–58, 105):**
   - Baris 105: Elemen status dirender sebagai elemen blok standar tanpa aturan CSS khusus:
     ```html
     <p id="status" role="status" aria-live="polite" aria-atomic="true"></p>
     ```
   - Baris 55–58: Tidak ada batasan `height`, `min-height`, `line-height`, atau `contain` pada `#status`. Elemen ini berada di dalam aliran normal (*in-flow block*) tepat di atas `#dag-breadcrumbs` dan `#dag-view`.

2. **`history_browser.js` (Baris 146, 173, 200, 208–211):**
   - Pada inisialisasi / perpindahan versi:
     `status.textContent = 'Versi anak-雪. 0 cabang lanjutan.'` (34 karakter).
   - Pada saat menyalin:
     `setStatus('Menyalin silsilah rute ke clipboard…')` (36 karakter).
   - Pada penyelesaian gagal (`outcome === 'failure'`):
     `setStatus('Gagal menyalin silsilah rute ke clipboard')` (41 karakter).
   - Pada saat feedback timer 1500 ms berakhir:
     `setStatus('Versi anak-雪. 0 cabang lanjutan.')`.

3. **`test_focus_events_chromium.cjs` (Baris 41–48, 87, 107–119):**
   - Baris 42–44: Runner membungkus `<section aria-label="Navigasi riwayat">` ke dalam `#dag-scroll-outer`. Karena `<section>` memuat `<p id="status">`, maka `#status` berada di dalam kontainer scroll luar.
   - Pada fase `departed` dengan `departure === 'forward'`: Tombol `Tab` ditekan, memindahkan fokus ke simpul SVG `alpha` di dalam `#dag-view`. Untuk membawa simpul ke layar, browser menggulir `#dag-scroll-outer` ke `scrollTop = 340px`.
   - Pada `scrollTop = 340px`, posisi elemen `#status` ($y \approx 50\text{--}100\text{px}$) berada **sepenuhnya di atas viewport scroll yang terlihat** (*fully clipped above the scroll port*).

4. **Fluktuasi Tinggi Elemen Status Terukur:**
   Eksperimen fixture headless Chromium menunjukkan tinggi fisik `#status` berdasarkan skala font dan teks:
   - `viewport: 390, scale: 2` (font size dasar 16px × 2 = 32px):
     - `pending` ("Menyalin..."): 76px (2 baris).
     - `success` ("Silsilah rute berhasil..."): 76px (2 baris).
     - `failure` ("Gagal menyalin silsilah rute ke clipboard", 41 char): **114px** (3 baris).
     - Selisih tinggi: $\Delta h = 114\text{px} - 76\text{px} = \mathbf{38\text{px}}$.

5. **Intervensi Scroll Anchoring Bawaan Browser:**
   - Berdasarkan spesifikasi W3C CSS Scroll Anchoring Module Level 1 § 2.1, browser memilih sebuah simpul terlihat di dalam viewport sebagai *anchor node* (dalam kasus ini simpul SVG `alpha` atau `#dag-view`).
   - Ketika fase `settled` memicu `setStatus('Gagal...')`, `#status` bertambah tinggi sebesar 38px. Karena `#status` berada di atas *anchor node*, seluruh konten di bawahnya terdorong ke bawah sebesar 38px.
   - Di bawah `overflow-anchor: auto` (default Chromium), User Agent mengompensasi pergeseran ini secara otomatis dengan menambahkan 38px pada `scrollTop`:
     $$\text{scrollTop}_{\text{settled}} = \text{scrollTop}_{\text{departed}} + 38 = 340 + 38 = 378\text{px}$$
   - Penyesuaian internal browser ini memancarkan event `scroll` native (`seq: 34, type: 'scroll', target: 'dag-scroll-outer'`).

6. **Penolakan pada Invarian Gate UIUX-071:**
   - `clipboard_focus_events.py` (Baris 134):
     ```python
     'settlement-scroll': settled['scroll'] == departed['scroll'] and not any(e['type'] == 'scroll' for e in events['settled'])
     ```
   - Invarian ini gagal ganda: offset `dag-scroll-outerY` berubah (340 $\ne$ 378) dan terdapat event `scroll` tak diinginkan pada fase `settled`.

---

## 3. Verifikasi Sumber Resmi Standar Web (Normative Specifications)

Untuk memastikan pengujian didasarkan pada standar teknis resmi, dokumen-dokumen otoritatif berikut diverifikasi:

### 3.1 W3C CSS Scroll Anchoring Module Level 1
- **URL Resmi:** https://www.w3.org/TR/css-scroll-anchoring-1/
- **Editor Draft:** https://drafts.csswg.org/css-scroll-anchoring/
- **Poin Normatif:**
  - **§ 2 Description & Anchor Node:** Scroll anchoring bertujuan menjaga konten yang sedang dilihat pengguna tetap stabil secara visual saat terjadi perubahan tata letak di atas area pandang.
  - **§ 2.1 Candidate Examination Algorithm:** Elemen yang berada di luar area optimal (*fully clipped above*) tidak dapat menjadi *anchor node*. Elemen di dalam area pandang dipilih menjadi *anchor node*. Perubahan ukuran elemen pendahulu (*preceding siblings/ancestors*) memicu pergeseran kompensasi pada koordinat scroll kontainer.
  - **§ 2.2 Suppression Triggers:** Perubahan computed property tertentu (`top`, `margin`, `padding`, `width`, `height`, `transform`) pada anchor node atau leluhurnya menonaktifkan anchoring sementara, namun perubahan konten teks pada elemen di atas anchor node **tidak** menekan anchoring.
  - **§ 3 Exclusion API (`overflow-anchor`):** Nilai `auto` adalah inisial/default. Nilai `none` menonaktifkan pemilihan anchor node pada scrolling box terkait.

### 3.2 MDN Web Docs: Overview of Scroll Anchoring & overflow-anchor
- **URL Resmi:** https://developer.mozilla.org/en-US/docs/Web/CSS/overflow-anchor
- **URL Panduan:** https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll_anchoring/Scroll_anchoring
- **Catatan Implementasi:**
  - `overflow-anchor: none` adalah mekanisme opt-out.
  - Opt-out menonaktifkan penyesuaian scroll otomatis peramban, tetapi **tidak** mencegah pergeseran visual. Jika elemen di atas membesar, konten yang sedang dibaca pengguna akan melompat ke bawah (*Cumulative Layout Shift* / CLS).

### 3.3 WHATWG HTML Specification § 6.5 Focus Processing Model & § 8.5 Timers
- **URL Focus:** https://html.spec.whatwg.org/multipage/interaction.html#focus-processing-model
- **URL Timers:** https://html.spec.whatwg.org/multipage/timers-and-user-prompts.html#timers
- **Poin Normatif:**
  - Pemanggilan `element.focus()` secara default menyertakan `{preventScroll: false}`, yang memerintahkan browser menggulir elemen ke area pandang (*scroll into view*). Pemanggilan tanpa `{preventScroll: true}` berpotensi memicu unsolicited scroll.
  - Timer callback (`setTimeout`) dieksekusi secara asinkron dari task queue. Perubahan status DOM di dalam timer callback yang memperbarui layout dapat memicu reflow sekunder dan scroll anchoring kedua saat feedback berakhir.

### 3.4 WHATWG DOM Specification § 2.7 Event.isTrusted & W3C UI Events § 3.3
- **URL DOM:** https://dom.spec.whatwg.org/#dom-event-istrusted
- **URL UI Events:** https://w3c.github.io/uievents/#events-focusevent-event-order
- **Poin Normatif:**
  - Event yang di-dispatch oleh User Agent saat eksekusi `element.focus()` memiliki atribut `event.isTrusted === true`. Pengujian integritas tidak boleh hanya mengandalkan flag `isTrusted` untuk membuktikan tindakan fisik keyboard pengguna, melainkan wajib mengikat transisi fokus ke event `keydown` asli (`Tab` / `Shift+Tab`).

---

## 4. Analisis Komparatif: Stable Layout vs Opt-Out (`overflow-anchor: none`)

Siklus UIUX-072 memerlukan perbandingan objektif antara pendekatan tata letak stabil dan opt-out kebijakan peramban:

| Parameter Evaluasi | Opt-Out Anchoring (`overflow-anchor: none`) | Tata Letak Status Stabil ($\Delta h = 0$) |
|---|---|---|
| **Nilai Properti CSS** | `overflow-anchor: none;` pada kontainer scroll | `overflow-anchor: auto;` (standar peramban) |
| **Koordinat Scroll (`scrollTop`)** | Tetap konstan (misal: 340px) | Tetap konstan (misal: 340px) |
| **Perilaku Event `scroll`** | Tidak ada event `scroll` yang dipancarkan | Tidak ada event `scroll` yang dipancarkan |
| **Stabilitas Visual Konten (CLS)** | **BURUK (Layout Shift):** Konten terlihat bergeser tiba-tiba ke bawah sebesar 38px saat failure, lalu melonjak ke atas saat reset. | **SEMPURNA (Zero Shift):** Konten terlihat tetap diam di tempat karena tinggi wadah status dicadangkan secara tetap. |
| **Kesesuaian Standar Browser** | Mengabaikan mekanisme perlindungan bawaan web platform. | Memanfaatkan standar web platform secara harmonis tanpa mematikan fitur mesin rendering. |
| **Kelaikan Produksi** | **Bukan rekomendasi universal:** Hanya menutupi kegagalan metrik scroll di test harness, mengorbankan pengalaman visual pengguna nyata. | **Rekomendasi Utama:** Menyelesaikan akar penyebab struktural (*root cause*) di level CSS box model. |

### Akar Perbaikan Tata Letak Stabil:
Sesuai prinsip *Ponytail* (Rung 4: Native platform feature & Rung 6: Shortest diff), solusi stabilitas geometri status dicapai melalui CSS, bukan manipulasi JS:
- Mencadangkan tinggi vertikal minimum atau konstan pada `#status` yang menampung jumlah baris maksimum pada skala font 2x (misal: `min-height: 3.8em` atau area layout terisolasi), atau
- Mengisolasi dimensi `#status` agar perubahan teks tidak mengubah tinggi kotak luar elemen (`contain: layout size` atau struktur grid yang terdefinisi).
Dengan $\Delta h = 0$ antara status `initial`, `pending`, `success`, `failure`, dan `reset`, *anchor node* tidak bergeser sama sekali, sehingga di bawah `overflow-anchor: auto`, browser tidak melakukan kompensasi scroll apa pun.

---

## 5. Rancangan Siklus Hidup 8 Fase & Matriks 36 Sekuens

### 5.1 Definisi 8 Fase Observasi UIUX-072
Siklus UIUX-072 memperluas 7 fase UIUX-071 dengan menambahkan fase ke-8: **`reset`**.

```
[initial] -> [pending] -> [scrolled] -> [shrunk] -> [regrown] -> [departed] -> [settled] -> [reset]
  idle        Enter        scroll Y+30   width-     width=       Tab/Shift+    settle copy   timer 1500ms
              promise      scroll X±25                           Enter target  outcomes      clears label
```

1. **`initial`:** Tombol Salin dicapai melalui navigasi keyboard native `Tab` dari `#outside`.
2. **`pending`:** Aktivasi keyboard native via `Enter`. Janji `writeText` clipboard tertunda (*pending*). Status bertuliskan `Menyalin…`.
3. **`scrolled`:** Intervensi scroll luar vertikal ($+30\text{px}$) dan dalam horizontal ($\pm 25\text{px}$).
4. **`shrunk`:** Intervensi ukuran kontainer (penyempitan lebar `dag-scroll-outer`).
5. **`regrown`:** Pemulihan lebar kontainer ke ukuran normal.
6. **`departed`:** Keberangkatan fokus pengguna via `Tab` (`forward` ke SVG `alpha`), `Shift+Tab` (`backward` ke breadcrumb `anak-雪`), atau `stay` (tetap pada tombol salin).
7. **`settled`:** Janji clipboard diselesaikan (`resolve` untuk `success`, `reject` untuk `failure`). Status menampilkan pesan keberhasilan/kegagalan.
8. **`reset` (BARU di UIUX-072):** Timer feedback 1500 ms dieksekusi (via controlled clock berlabel jujur). Label tombol kembali menjadi `Salin Rute`, kelas `.copied` dilepas, status kembali ke `Versi <cursor>...`.

### 5.2 Komposisi Matriks Penuh 36 Sekuens
- **Viewport:** 3 varian (320px, 390px, 768px).
- **Skala Font:** 2 varian (1x = 16px, 2x = 32px eksplisit).
- **Hasil Janji:** 2 varian (`success`, `failure`).
- **Mode Keberangkatan:** 3 varian (`stay`, `forward`, `backward`).
- **Total Sekuens Positif:** $3 \times 2 \times 2 \times 3 = \mathbf{36\text{ sekuens}}$.
- **Total Pengukuran Fase:** $36 \times 8 = \mathbf{288\text{ fase terukur}}$.
- **Kebijakan Anchoring Wajib:** Seluruh 36 sekuens positif **harus** dijalankan di bawah `overflow-anchor: auto`.

---

## 6. Spesifikasi Minimal Acceptance Gate UIUX-072

Audit ini menetapkan batas penerimaan minimal (*acceptance gate*) yang ketat untuk validator Python (`clipboard_focus_events.py`) dan runner Chromium (`test_focus_events_chromium.cjs`):

### 6.1 Invarian Kontinuitas Trace & Waktu Monotonik
1. **Rantai Event Berurutan:** Array `eventTrace` harus memiliki `seq` yang inkremental rapat ($1, 2, \dots, N$) tanpa jeda (*gap*) atau duplikasi.
2. **Waktu Monotonik:** `observedTime` pada setiap event harus bersifat *non-decreasing* ($t_i \ge t_{i-1}$) dan berasal dari `performance.now()`.
3. **Ketiadaan Glitch Transient:**
   - Pada fase stabil non-input (`pending`, `scrolled`, `shrunk`, `regrown`, `settled`, `reset`), kemunculan event `focusin` atau `focusout` apa pun dianggap pelanggaran fatal (`no-transient-glitch` atau `no-focus-theft`).
   - Pada mode `stay`, jumlah event fokus keluar/masuk selama seluruh siklus hidup interaksi adalah **persis 0**.

### 6.2 Invarian Fase Reset Feedback 1500 ms
1. **Restorasi Semantik:**
   - Tombol salin: `label === 'Salin Rute'`, `aria-label === 'Salin seluruh jejak silsilah rute ke clipboard'`, dan tidak memiliki kelas `.copied`.
   - Status teks: kembali berawalan `'Versi '` sesuai node aktif.
2. **Pencegahan Pencurian Fokus (*No Focus Theft on Reset*):**
   - Jika `departure === 'forward'`, elemen aktif pada akhir fase `reset` **tetap** `g[data-node=alpha][role=button]`.
   - Jika `departure === 'backward'`, elemen aktif **tetap** `button[data-breadcrumb-node=anak-雪]`.
   - Jika `departure === 'stay'`, elemen aktif **tetap** tombol salin.
   - Tidak boleh ada pemanggilan `.focus()` liar oleh handler timer.
3. **Invarian Koordinat Scroll pada Reset:**
   - Koordinat scroll pada akhir fase `reset` harus identik dengan fase `settled`:
     $$\text{scroll}_{\text{reset}} == \text{scroll}_{\text{settled}} == \text{scroll}_{\text{departed}}$$
   - Jumlah event `scroll` selama fase `reset` harus **persis 0**.

### 6.3 Invarian Geometri Elemen Tetangga Baru (New Neighbor Geometry)
Audit menemukan bahwa UIUX-071 hanya memeriksa keberadaan tombol lama tanpa memvalidasi keterlihatan elemen tetangga yang baru difokuskan. UIUX-072 mewajibkan validasi geometri target baru:

1. **Forward Neighbor (`g[data-node=alpha][role=button]`):**
   - **Konektivitas DOM:** `isConnected === true`.
   - **Dimensi Bounding Box:** Bounding rect SVG harus bernilai positif ($width > 0, height > 0$).
   - **Viewport Clipping:** Bounding box harus berada di dalam batas viewport peramban ($0 \le left < right \le viewportWidth$, $0 \le top < bottom \le viewportHeight$).
   - **Bebas Oklusi Overlay:** Bounding box tidak boleh bertabrakan dengan overlay foreground yang diketahui (`#dag-diff-popover` dan `#dag-minimap-wrap` yang memiliki `z-index: 90`).
   - **PITFALL KRUSIAL:** Uji coba riil membuktikan bahwa Chromium mengevaluasi `outlineStyle: "none"` pada SVG `<g>` meskipun `:focus-visible` bernilai `true` (karena keterbatasan CSS outline standar pada elemen SVG container). Gate **DILARANG** memaksakan `outlineStyle === 'solid'` pada simpul SVG, melainkan wajib memverifikasi kecocokan pseudoclass `:focus-visible` atau atribut rendering SVG yang valid.

2. **Backward Neighbor (`button[data-breadcrumb-node=anak-雪]`):**
   - **Konektivitas & Visibilitas:** `isConnected === true`, berada di dalam area pandang `#dag-scroll-inner` dan viewport.
   - **Focus Indicator HTML:** Sebagai elemen `<button>` native, wajib memiliki `:focus-visible === true`, `outlineStyle === 'solid'`, `outlineWidth >= 2px`, dan `outlineOffset >= 2px`.
   - **Bebas Oklusi:** Tidak tertutup popover atau overlay buram.

---

## 7. Rekomendasi Kasus Uji Mutasi & Kontrol Negatif Adversarial

Untuk menguji sensitivitas dan kekebalan verifier terhadap pemalsuan (*falsification*), suite pengujian unit deterministik (`test_clipboard_focus_events.py`) harus ditambahkan metode uji mutasi berikut:

### 7.1 Daftar Kasus Uji Mutasi Adversarial
1. **`test_status_height_oscillation_under_auto`:**
   - *Skenario:* Mensimulasikan rekaman di mana `#status` membesar 38px pada fase `settled` dan menyusut 32px pada fase `reset`, memicu perubahan `dag-scroll-outerY` dari 340 $\to$ 378 $\to$ 346 disertai event `scroll`.
   - *Ekspektasi Gate:* Ditolak dengan kegagalan `settlement-scroll` dan `reset-scroll`.
2. **`test_feedback_timer_focus_theft_on_reset`:**
   - *Skenario:* Pada mode `forward`, handler timer memanggil `copyButton.focus()` saat reset selesai, mengembalikan fokus dari `alpha` ke tombol salin.
   - *Ekspektasi Gate:* Ditolak dengan kegagalan `active-target` atau `no-reset-theft` pada fase `reset`.
3. **`test_transient_scroll_restore_during_reset`:**
   - *Skenario:* Layout status menyusut saat reset, mengubah scroll sesaat, lalu skrip mencoba memulihkan scroll kembali ke 340px sebelum snapshot diambil.
   - *Ekspektasi Gate:* Terdeteksi melalui event listener `scroll` pada fase `reset` dan ditolak dengan `reset-scroll`.
4. **`test_neighbor_clipped_by_container`:**
   - *Skenario:* Navigasi `Shift+Tab` memindahkan fokus ke breadcrumb item yang berada di luar batas scroll kiri (`left < inner.left`).
   - *Ekspektasi Gate:* Ditolak dengan `neighbor-clipping`.
5. **`test_neighbor_occluded_by_minimap_overlay`:**
   - *Skenario:* Simpul SVG `alpha` terletak di bawah panel `#dag-minimap-wrap` (koordinat bertubrukan dengan rect overlay buram).
   - *Ekspektasi Gate:* Ditolak dengan `neighbor-occlusion`.
6. **`test_clock_tampering_or_frozen_timer_label`:**
   - *Skenario:* Runner mengklaim fase `reset` telah selesai, tetapi delta waktu observasi antara `settled` dan `reset` kurang dari 1500 ms tanpa label controlled clock yang sah.
   - *Ekspektasi Gate:* Ditolak dengan `invalid-timer-duration`.
7. **`test_svg_neighbor_focus_indicator_heuristic`:**
   - *Skenario:* Gate mencoba memeriksa `outlineStyle === 'solid'` pada simpul SVG dan memicu *false rejection*.
   - *Ekspektasi Gate:* Suite unit harus memverifikasi bahwa validator secara fleksibel menerima `:focus-visible` pada node SVG tanpa menuntut CSS outline box HTML.

---

## 8. Batas Penerapan & Batasan yang Belum Terverifikasi (Unverified Limits)

Audit ini mencatat batas keabsahan klaim teknis secara jujur:
1. **Skala Font vs Native Zoom:** Pengujian menggunakan pengali CSS `fontSize` eksplisit (skala 1x dan 2x), bukan native pinch-to-zoom atau browser viewport zoom (Ctrl+/Ctrl-).
2. **Controlled Clock vs Real-World Timer:** Pengujian 1500 ms menggunakan controlled clock berbasis intervensi Playwright / virtual time yang diberi label secara jujur, bukan jaminan presisi interval OS pada hardware dengan beban CPU tinggi.
3. **Headless vs OS Physical Clipboard:** Harness menggunakan antarmuka mock `navigator.clipboard.writeText` terkontrol, bukan verifikasi transfer buffer antar-aplikasi di level sistem operasi native.
4. **Aksesibilitas DOM vs Screen-Reader Audio:** Pengujian memverifikasi atribut ARIA (`role="status"`, `aria-live="polite"`, `aria-atomic="true"`, `aria-label`), bukan emisi suara aktual dari screen-reader pihak ketiga (NVDA/JAWS/VoiceOver).
5. **Cakupan Engine:** Pengujian terisolasi pada mesin Chromium (versi 156.0.8078.4); rendering SVG focus-visible dan algoritma kandidat scroll anchoring pada Gecko (Firefox) dan WebKit (Safari) belum diverifikasi.

---

## 9. Rekomendasi Konkret untuk Parent Integration Reviewer

1. **Aplikasi Perbaikan Struktur (Bukan Workaround):**
   - Pastikan worker menerapkan stabilisasi geometri `#status` pada `history_browser.py` menggunakan styling native yang mencadangkan tinggi vertikal, bukan mematikan `overflow-anchor`.
2. **Validasi Default Auto:**
   - Pastikan seluruh 36 sekuens positif dalam `test_focus_events_chromium.cjs` menetapkan `anchorPolicy: 'auto'` dan lulus murni tanpa event `scroll` tak diinginkan.
3. **Sertakan Bukti Perbandingan:**
   - Simpan data komparatif uji coba antara `overflow-anchor: auto` dan `overflow-anchor: none` pada berkas referensi verifikasi untuk mendokumentasikan pencegahan CLS secara empiris.
4. **Verifikasi Geometri Tetangga:**
   - Pastikan validator `clipboard_focus_events.py` memeriksa bounding box, konektivitas, dan ketiadaan oklusi pada elemen target keberangkatan (`alpha` dan `anak-雪`).
