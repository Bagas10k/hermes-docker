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

- **HTTP PUT pada `/json/new`**: Endpoint `/json/new` pada Chromium modern mewajibkan HTTP method `PUT`; pemanggilan dengan `GET` melempar HTTP 405 Method Not Allowed.
- **WebSocket Frame Size**: Tangkapan layar base64 resolusi tinggi dapat melebihi batas default WebSocket frame (1 MB). Runner mengonfigurasi batas `max_size=25MB` untuk mencegah koneksi terputus tiba-tiba.
- **Horizontal Overflow False Negatives**: Nilai `scrollWidth` elemen `document.documentElement` wajib dibandingkan terhadap `clientWidth`. Runner menyertakan toleransi 1px untuk mencegah subpixel anti-aliasing jitter.

## Verification

Buktikan pengujian E2E berfungsi menggunakan perintah berikut:

```bash
python3 ~/.hermes/skills/software-development/e2e-browser-testing/scripts/cdp_runner.py --url http://127.0.0.1:3050/buku --viewport mobile
```

Harus mengembalikan luaran JSON dengan `"success": true`, `"hasHorizontalOverflow": false`, dan `"zero_emoji": {"passed": true, "emoji_count": 0}`.
