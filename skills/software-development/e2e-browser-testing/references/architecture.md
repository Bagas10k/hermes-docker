# E2E Headless Browser Testing & Visual Verification Architecture

## 1. Mekanisme & Bounds (Mechanistic Architecture)
Pengujian antarmuka modern memerlukan verifikasi langsung pada level browser engine nyata tanpa bergantung pada tebakan HTML statis. Chrome DevTools Protocol (CDP) menyediakan antarmuka deterministik berlatensi rendah untuk berinteraksi langsung dengan Chromium compositor dan JavaScript runtime:

- **Target Domain WebSocket (`/json/new`)**: Endpoint HTTP `PUT /json/new` membuat target halaman baru dan mengembalikan `webSocketDebuggerUrl`. Seluruh kontrol berjalan di atas satu koneksi WebSocket dupleks penuh.
- **Emulation Matrix**: Domain `Emulation.setDeviceMetricsOverride` mengunci viewport secara deterministik:
  - Mobile: `width=390, height=844, deviceScaleFactor=2, mobile=true` (iPhone 13/14 class).
  - Desktop: `width=1440, height=900, deviceScaleFactor=1, mobile=false`.
- **Accessibility Tree (`Accessibility.getFullAXTree`)**: Membaca semantik Accessibility Tree yang diurai browser. Memastikan tombol, link, form control memiliki peran aksessibel nyata, bukan sekadar tag `<div>` tak berbobot.
- **Horizontal Overflow Detection**:
  $$\Delta_{\text{overflow}} = \max(\text{scrollWidth}_{\text{doc}}, \text{scrollWidth}_{\text{body}}) - \text{clientWidth}$$
  Bila $\Delta_{\text{overflow}} > 1\text{px}$, sistem otomatis menandai bug responsivitas layout horizontal overflow.

## 2. Bayesian-Experimental Verification Loop
- **Prior Hypothesis**: Setiap rilis UI baru mengasumsikan nol regresi layout pada breakpoint mobile dan kepatuhan 100% terhadap Zero-Emoji Policy.
- **Evidence Gathering**:
  - Snapshot Accessibility Tree membuktikan interaktivitas elemen (jumlah tombol > 0, peran semantik terdeteksi).
  - Runtime evaluation mengeksekusi ekspresi regex Unicode audit di dalam context browser asli.
  - Tangkapan layar PNG memvalidasi representasi visual riil dari framebuffer Chromium.
- **Disqualifying Negative Tests**: Jika ditemukan karakter emoji Unicode atau horizontal overflow pada viewport 390px, build otomatis diblokir (veto) sebelum rilis ke produksi.

## 3. Desain Sistem & Hard Constraints
- **Zero-GC & Transient Sandboxing**: Setiap eksekusi pengujian menggunakan `--user-data-dir` sementara terisolasi di `/tmp` yang dihapus secara atomik setelah pengujian usai, menjaga disk dan memory leaks tetap 0 MB.
- **Sub-2s Execution Bounds**: Menghindari overhead cold-start WebDriver atau Selenium yang memakan waktu 10-20 detik; eksekusi CDP langsung selesai dalam waktu $<1.9$ detik.
- **Fail-Closed Safety Guard**: Jika endpoint CDP gagal merespons dalam 5 detik, pengujian otomatis melempar exit code 1 dan memutus proses secara bersih.
