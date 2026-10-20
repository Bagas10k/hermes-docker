---
name: moli-cdp-server
description: "Run Moli CDP server for Playwright and Puppeteer."
version: 1.1.18
author: "lexmount & Bagas Cihuy"
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cdp, playwright, puppeteer, headless-browser, moli, rust]
---

# Run Moli CDP Server

Jalankan server otomasi Moli untuk endpoint Chrome DevTools Protocol (CDP), WebDriver Classic, dan WebDriver BiDi. Memungkinkan Playwright dan Puppeteer terhubung langsung ke browser headless ultra-ringan (~50-80 MB RAM).

## Kapan Menggunakan
- Menjalankan testing browser E2E atau skrip Playwright/Puppeteer di server dengan resource terbatas tanpa memicu OOM killer.
- Menggantikan proses Chromium bawaan yang boros memori (>600 MB RAM per instance).

## Cara Menjalankan

1. Jalankan server Moli CDP di port lokal:

```bash
moli serve --port 9222 --layout
```

Gunakan opsi `--layout` saat otomasi membutuhkan kalkulasi koordinat, bounding box, atau screenshot.

2. Hubungkan Playwright via CDP (`connectOverCDP`):

```javascript
import { chromium } from "playwright";

const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
const page = context.pages()[0] || await context.newPage();

await page.goto("https://example.com");
console.log(await page.locator("body").innerText());

await browser.close();
```

3. Hubungkan Puppeteer via CDP (`connect`):

```javascript
import puppeteer from "puppeteer-core";

const browser = await puppeteer.connect({
    browserURL: "http://127.0.0.1:9222"
});
const page = await browser.newPage();
await page.goto("https://example.com");
await browser.close();
```

## Aturan Keamanan & Isolasi
- Selalu ikat server ke `127.0.0.1` (loopback lokal). Dilarang mengekspos port CDP langsung ke internet publik tanpa tunneling terenkripsi.
- Pastikan proses `moli serve` dimatikan bersih setelah skrip otomasi selesai.
