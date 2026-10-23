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
   - Pastikan server web target aktif melayani HTTP 200 di port lokal atau URL publik.
   - Kriteria selesai: Target merespons permintaan HTTP dengan status kode 200 OK.

2. **Eksekusi Pengujian CDP Viewport**:
   - Jalankan `cdp_runner.py` dengan parameter viewport (`mobile` atau `desktop`).
   - Kriteria selesai: Runner mengembalikan luaran JSON berstatus `"success": true` dan `hasHorizontalOverflow: false`.

3. **Verifikasi Aksesibilitas & Zero-Emoji**:
   - Periksa blok `accessibility` dan `zero_emoji` pada luaran JSON.
   - Kriteria selesai: `zero_emoji.passed` bernilai `true` (`emoji_count: 0`) dan elemen tombol/link terdeteksi pada AXTree.

4. **Simpan Bukti Tangkapan Layar**:
   - Simpan berkas PNG tangkapan layar ke direktori sementara atau direktori aset pengujian.
   - Kriteria selesai: Ukuran berkas screenshot $>0$ bytes dan framebuffer tersimpan di disk.

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
- **Viewport-task reachability**: Untuk antarmuka kerja padat, ukur posisi kontrol wajib terhadap `innerHeight` pada viewport target, lalu inspeksi framebuffer. Contoh kontrak POS desktop: pencarian, input transaksi, total, dan CTA final semuanya memiliki `bottom <= innerHeight`; daftar sekunder boleh memakai scroll internal. Ulangi setelah patch CSS terakhir karena screenshot atau verdict sebelum edit tidak membuktikan kandidat terbaru.
- **DOM order across breakpoints**: Audit urutan visual dan DOM pada desktop serta mobile. Reordering dengan flex/grid `order` hilang ketika breakpoint mengubah parent menjadi `display: block`, sehingga konten ringkasan yang lebih dulu di DOM dapat kembali mendahului tugas utama di mobile. Gunakan DOM order sesuai prioritas utama dan batasi reordering hanya sebagai enhancement desktop.

## Verification

Buktikan pengujian E2E berfungsi menggunakan perintah berikut:

```bash
python3 ~/.hermes/skills/software-development/e2e-browser-testing/scripts/cdp_runner.py --url http://127.0.0.1:3050/buku --viewport mobile
```

Harus mengembalikan luaran JSON dengan `"success": true`, `"hasHorizontalOverflow": false`, dan `"zero_emoji": {"passed": true, "emoji_count": 0}`.
