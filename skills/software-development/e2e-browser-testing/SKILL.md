---
name: e2e-browser-testing
description: E2E headless browser testing via Chrome DevTools Protocol.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, browser, cdp, headless, e2e, verification, accessibility]
    related_skills: [live-sandbox-hot-preview, tactile-microinteraction-studio, pwa-mobile-ergonomics]
---

# E2E Headless Browser Testing & Visual Verification Skill

Skill ini menyediakan pengujian otomatis end-to-end (E2E) dan verifikasi visual web berbasis Chrome DevTools Protocol (CDP) langsung ke Chromium engine. Memastikan aplikasi bebas dari horizontal layout overflow, mematuhi Zero-Emoji Policy, memeriksa semantik Accessibility Tree, dan menangkap tangkapan layar framebuffer deterministik.

## When to Use

- Memverifikasi halaman web atau artefak HTML lokal sebelum rilis ke publik.
- Menguji responsivitas layout mobile (390x844) dan mendeteksi horizontal scroll overflow.
- Mengaudit kepatuhan Zero-Emoji Policy dan semantik elemen aksessibel (AXTree).
- Menangkap bukti tangkapan layar (screenshot) aktual dari engine browser headless.
- Don't use for: Pengujian unit logic backend murni tanpa antarmuka DOM/web.

## Prerequisites

- Python 3.8+ dengan paket `websockets`.
- Biner Chromium atau Google Chrome headless terpasang di sistem (`chromium-browser`, `google-chrome`, atau Chromium cache Playwright/Puppeteer).
- Hak eksekusi pada skrip pembantu di `scripts/cdp_runner.py`.

## How to Run

Jalankan pengujian E2E deterministik melalui Hermes `terminal` tool:

```bash
python3 ~/.hermes/skills/software-development/e2e-browser-testing/scripts/cdp_runner.py --url <URL> --viewport mobile --screenshot /tmp/output.png
```

## Quick Reference

- **Audit Mobile Viewport & Screenshot**:
  `python3 ~/.hermes/skills/software-development/e2e-browser-testing/scripts/cdp_runner.py --url http://127.0.0.1:3050/buku --viewport mobile --screenshot /tmp/buku_mobile.png`
- **Audit Desktop Viewport**:
  `python3 ~/.hermes/skills/software-development/e2e-browser-testing/scripts/cdp_runner.py --url http://127.0.0.1:3000 --viewport desktop`
- **Evaluasi JavaScript Kustom di Browser**:
  `python3 ~/.hermes/skills/software-development/e2e-browser-testing/scripts/cdp_runner.py --url http://127.0.0.1:3050/desain --eval "document.querySelectorAll('img').length"`

## Procedure

1. **Siapkan Target Pengujian**:
   - Pastikan URL halaman yang tepat—bukan sekadar port/listener—melayani HTTP 200 sebelum setiap batch DOM/screenshot. Ulangi probe setelah proses capture panjang; socket `LISTEN` masih dapat memberi empty reply ketika server preview macet.
   - Jika preview disposable macet, hentikan hanya proses preview, jalankan ulang server pada direktori artefak yang sama, lalu buktikan setiap URL target kembali HTTP 200 sebelum melanjutkan.
   - Kriteria selesai: setiap target yang akan diuji merespons HTTP 200 OK.

2. **Eksekusi Pengujian CDP Viewport**:
   - Jalankan `cdp_runner.py` dengan parameter viewport (`mobile` atau `desktop`).
   - Kriteria selesai: Runner mengembalikan luaran JSON berstatus `"success": true` dan `hasHorizontalOverflow: false`.

3. **Verifikasi Aksesibilitas & Zero-Emoji**:
   - Periksa blok `accessibility` dan `zero_emoji` pada luaran JSON.
   - Kriteria selesai: `zero_emoji.passed` bernilai `true` (`emoji_count: 0`) dan elemen tombol/link terdeteksi pada AXTree.

4. **Simpan Bukti Tangkapan Layar**:
   - Simpan setiap viewport/page ke path unik dan eksplisit; jangan mengandalkan path temporer default karena sesi paralel dapat melaporkan nama yang sama.
   - Setelah batch, hitung artefak secara programatik, cocokkan dengan jumlah yang diminta, pastikan setiap PNG berukuran >0 byte, lalu simpan checksum bila verdict harus terikat ke versi tertentu.
   - Jika CDP screenshot timeout tetapi DOM probe lulus, gunakan Chromium headless per URL/viewport sebagai fallback terisolasi; jangan mengubah hasil kosong menjadi klaim screenshot berhasil.
   - Untuk halaman panjang ketika capture viewport setelah scroll tetap tidak andal, buat artefak HTML **focus-record** dari fixture yang sudah dirender: sembunyikan hanya header/ringkasan/filter pendahulu pada salinan disposable, jangan ubah markup record atau shared CSS, lalu sajikan lewat HTTP lokal dan capture viewport. Sebelum memakai bukti ini, ukur pada halaman asli bahwa record dapat dijangkau, tidak overflow, dan target aksi memenuhi dimensi; labeli gambarnya sebagai focus-record fixture, bukan komposisi top-of-page asli.
   - Kriteria selesai: jumlah, nama, ukuran, dan—bila diperlukan—checksum artefak cocok dengan matriks pengujian.

## Pitfalls

- **Browser binary vs package cache**: Resolve an installed Chromium executable before launching Puppeteer. The package's default pinned Chrome may be absent while `/usr/local/bin/chromium` is usable; verify the binary and pass `executablePath` rather than installing another browser.
- **WebGPU shader output vs canvas presentation**: Test an actual `getCurrentTexture()` render and inspect the captured pixels; successful texture readback alone does not prove browser composition. On software-only Linux hosts, isolate backend initialization from application code before rewriting the renderer. One verified Chromium configuration is `--enable-unsafe-webgpu --use-vulkan=swiftshader --use-webgpu-adapter=swiftshader --enable-features=Vulkan,WebGPU --use-gl=angle --use-angle=swiftshader`. These are bounded test-runner flags, not universal requirements or production browser recommendations. Record the real adapter: SwiftShader proves software WebGPU execution, not physical acceleration. Treat device-loss or blank screenshots as failures even when API discovery or WGSL compilation succeeds.
- **Exact delivery surface**: Record the actual response status and final browser URL. A local HTTP 200 does not establish public availability; keep an outer login wall intact and disclose it. Never silently fall back from the requested URL to `file://` and report the URL as tested.
- **Fixture-render authenticated pages**: when the target page sits behind auth you must not log into, render its real controller/view to disposable HTML against the project's approved disposable test database (`:memory:` only when that project genuinely supports it), serve it on an isolated local endpoint, then point the browser runner at it. A rendered private layout may still launch session-expiry UI: neutralize that behavior only inside the disposable preview DOM, never in application source, and assert the final URL, exact requested modal labels, active state, absence of auth overlays, and HTTP 200 before capture. Replace visible business/customer values only in the preview DOM with neutral synthetic values, preserve honest empty-master states, delete the temporary served HTML afterward, and label the screenshot as synthetic-fixture evidence rather than live acceptance.
- **Responsive timeline density gates**: Exercise both a short trace and the maximum retained lane count, with long durations and truncation notices visible. Assert pairwise control non-overlap and final-row reachability, not only document scrollWidth; fixed/absolute headers can clip content without page overflow. Transform SVG endpoints via getScreenCTM() and compare them with actual track coordinates. Test deep-linked sessions outside the recent-list cap and preserve authenticated endpoint validation rather than silently selecting another session.
- **Semantic task counts**: Empty-state list items are not records. Count rows containing the actual record marker/control, and verify the visible total against that count; do not weaken a failing assertion to accommodate genuine data errors.
- **Native-dialog screenshot evidence**: Capture top-layer dialogs with a viewport screenshot (`fullPage:false`). A stitched full-page mobile screenshot may show only the backdrop while omitting the white dialog despite valid DOM assertions; visually inspect the actual image before cropping it into a report.
- **Async result isolation**: Hold a real result response for task A, switch to task B, then release A and assert B remains unchanged. Checking that a result button or modal exists does not prove output isolation. Bind rendering to the requested task identity, not merely to the existence of an active task.
- **Auth expiry with open dialogs**: Expire the disposable session while a private native dialog is open; assert the top-layer dialog closes, its contents clear, and no pending confirmation callback survives. Hiding the main page alone does not hide native dialog content.
- **Synthetic identities and truthful evidence**: Use neutral synthetic names and IDs throughout injected SDKs, fixtures, and screenshots. Label fixture browser evidence separately from genuine Telegram/WebView acceptance; do not use real personal identity as dummy data.
- **Source-bound verdicts**: Re-run independent QC after every functional edit and bind PASS to current implementation and test hashes. A late PASS for an earlier candidate does not authorize publishing a newer candidate.
- **Assert the result, not the affordance**: Read textarea output with `inputValue()`/`.value`, assert it contains fresh input, and verify downloaded bytes against that value. A visible copy/download button or local-only disclaimer is not evidence that generation, copying, or downloading works. Assert menu state both before and after real keyboard activation; `aria-expanded=false` alone does not prove a menu opened.
- **Separate app traffic from edge injection**: Inspect requests on the exact public URL. Cloudflare or another host may inject analytics even when source files contain no network calls. Disclose infrastructure analytics instead of claiming zero external requests; test that synthetic form markers do not appear in request URLs or bodies. Do not weaken a strict network test silently.
- **Keyboard focus and CDP Enter**: Confirm `document.hasFocus()` and the actual focused element, enabling focus emulation for a headless session if necessary. Chromium Enter activation may require the CDP keyDown event to carry its carriage-return text; capture real event order when diagnosing. DOM `dispatchEvent(new KeyboardEvent(...))` is not a substitute for native keyboard acceptance.

- **HTTP PUT pada `/json/new`**: Endpoint `/json/new` pada Chromium modern mewajibkan HTTP method `PUT`; pemanggilan dengan `GET` melempar HTTP 405 Method Not Allowed.
- **WebSocket Frame Size**: Tangkapan layar base64 resolusi tinggi dapat melebihi batas default WebSocket frame (1 MB). Runner mengonfigurasi batas `max_size=25MB` untuk mencegah koneksi terputus tiba-tiba.
- **Horizontal Overflow False Negatives**: Nilai `scrollWidth` elemen `document.documentElement` wajib dibandingkan terhadap `clientWidth`. Runner menyertakan toleransi 1px untuk mencegah subpixel anti-aliasing jitter. Jangan berhenti pada cek halaman: untuk kartu dengan `overflow: hidden`, ukur setiap kontrol penting memakai `getBoundingClientRect()` dan pastikan batas kiri/kanannya berada di dalam content box kartu; anak dapat terpotong tanpa memperbesar `documentElement.scrollWidth`.
- **Viewport-task reachability**: Untuk antarmuka kerja padat, ukur posisi kontrol wajib terhadap `innerHeight` pada viewport target, lalu inspeksi framebuffer. Contoh kontrak POS desktop: pencarian, input transaksi, total, dan CTA final semuanya memiliki `bottom <= innerHeight`; daftar sekunder boleh memakai scroll internal. Untuk tabel tablet yang sengaja lebih lebar, set `scrollLeft` ke maksimum dan buktikan kolom aksi masuk utuh ke content box wrapper. Untuk bukti record mobile yang di-scroll, kompensasikan topbar tetap dengan `scroll-margin-top` atau offset eksplisit dan pastikan identitas, batas kartu, status, serta semua aksi terlihat. Ulangi setelah patch CSS terakhir karena screenshot atau verdict sebelum edit tidak membuktikan kandidat terbaru.
- **Off-canvas focus trap**: `scrollWidth <= clientWidth` tidak membuktikan drawer tertutup aman. Kirim Tab native dan pastikan fokus pertama berada pada kontrol yang terlihat; drawer off-canvas harus `inert` atau setara (`visibility:hidden`/`pointer-events:none` plus pemulihan saat dibuka) agar kontrol pada koordinat negatif tidak menerima fokus.
- **DOM order across breakpoints**: Audit urutan visual dan DOM pada desktop serta mobile. Reordering dengan flex/grid `order` hilang ketika breakpoint mengubah parent menjadi `display: block`, sehingga konten ringkasan yang lebih dulu di DOM dapat kembali mendahului tugas utama di mobile. Gunakan DOM order sesuai prioritas utama dan batasi reordering hanya sebagai enhancement desktop.
- **Synthetic pointer events and `setPointerCapture`**: Dispatching `pointerdown`/`pointermove` via `dispatchEvent` does not create a real active pointer, so `setPointerCapture(e.pointerId)` throws `NotFoundError: No active pointer with the given id is found`. If that call sits before the handler's state assignment, the exception aborts the rest of the handler and the drag silently never starts — a false FAIL that looks like broken app code. Fix the app, not the test: set state first, then wrap capture in `try/catch` (capture is an optimization, not a requirement). Then read back the error surface, because a swallowed console error is not a passed test.
- **`requestAnimationFrame` batching hides state changes from assertions**: When render is coalesced through `requestAnimationFrame` (the correct pattern for pan/zoom, drag, scroll), reading `element.style.transform` immediately after dispatching events returns the PREVIOUS frame. Assert only after waiting two frames: `await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))`. A same-tick read reports 'no change' on code that works perfectly.
- **Hidden tab freezes rAF entirely**: A CDP/headless session can report `document.hidden === true`, and browsers suspend `requestAnimationFrame` for hidden documents — so a two-frame wait never resolves and the DOM never updates, while the JS state object has already changed correctly. Before concluding the handler is broken, read `document.hidden`/`document.visibilityState` and compare the state object (e.g. `SWARM.x`) against the DOM (`element.style.transform`). State changed + DOM stale + hidden tab = test artifact, not an app bug. If the app must stay correct in a backgrounded tab, add a `setTimeout` fallback beside the rAF (cancel the frame, write once) rather than dropping the coalescing.
- **Zero-size container produces phantom failures**: Before asserting on pointer geometry, log `root.getBoundingClientRect()`. A hidden mode/panel (`display:none`, wrong tab active, or a mode you switched away from in an earlier step) yields `0x0`, so every synthesized pointer lands outside the element and every assertion fails for the wrong reason. Re-activate the target surface and re-measure, and use `document.elementFromPoint(x, y)` to confirm which element actually receives the event. Order matters in long probe scripts: re-select the mode at the START of each geometric assertion block, never assume it is still active.
- **Overlay/HUD occlusion is a layout assertion, not a visual one**: Fixed bottom HUDs, toolbars, and floating panels cover absolutely-positioned canvas/card content without any overflow appearing in `scrollWidth`. Compare each item's `getBoundingClientRect().bottom` against the overlay's `top` and assert the violation set is empty (`overlapAll: []`), then confirm the fix by re-measuring after the CSS change. Screenshot inspection reports occlusion as prose; the rect comparison is what makes it a gate.
- **Do not hard-code element heights in fit-to-content math**: An auto-fit / zoom-to-content routine that assumes a fixed card height under-scales by exactly the overflow it cannot see, leaving the last row flush against a bottom overlay or clipped. Measure real height from the DOM first (`el.offsetHeight / currentScale`, take the max across items) because titles wrap to 2-3 lines and every card differs. Re-assert `bottom <= overlay.top` after the change: equality means still touching, not clear.
- **Row pitch must exceed measured card height plus overlay reserve**: Verify `rowGap > measuredCardHeight` and subtract the HUD band from the usable viewport height in the fit calculation. A 220px pitch against ~158px cards leaves only 62px of air and collides the moment a title wraps.

## Verification

Buktikan pengujian E2E berfungsi menggunakan perintah berikut:

```bash
python3 ~/.hermes/skills/software-development/e2e-browser-testing/scripts/cdp_runner.py --url http://127.0.0.1:3050/buku --viewport mobile
```

Harus mengembalikan luaran JSON dengan `"success": true`, `"hasHorizontalOverflow": false`, dan `"zero_emoji": {"passed": true, "emoji_count": 0}`.
