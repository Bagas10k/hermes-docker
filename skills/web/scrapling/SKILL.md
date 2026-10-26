---
name: scrapling
description: "High-performance web scraping and data extraction with stealth Cloudflare bypass."
version: 0.5.0
author: D4Vinci & Hermes Agent
license: BSD-3-Clause
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web-scraping, stealth, bypass, crawler, selector, html-parsing, research]
    related_skills: [agent-reach, blocked-page-recovery, moli-webfetch]
---

# Scrapling — Next-Gen Web Scraping & Stealth Engine

Kerangka kerja web scraping Python berkinerja tinggi yang dirancang untuk mengatasi halaman web dengan proteksi bot, Cloudflare, dan struktur DOM dinamis.

## Kapan Digunakan
- Mengambil (*scrape*) konten web yang memblokir `curl`, `requests`, atau `urllib` standar (HTTP 403 / Bot Detection).
- Mengekstrak data riset, artikel berita, tabel data, atau intelijen kompetitor tanpa menyalakan browser berat yang rakus RAM.
- Ekstraksi teks dan atribut DOM cepat menggunakan selector CSS/XPath berkecepatan tinggi berbasis C (`lxml` + `orjson`).

## Cara Penggunaan di Python / Subagent

### 1. Pengambilan Cepat Standar (Fast Fetcher)
```python
from scrapling import Fetcher

fetcher = Fetcher()
page = fetcher.get("https://example.com")
print("Status:", page.status)

# Ekstraksi menggunakan CSS Selector cerdas
headings = page.css("h1::text").getall()
links = page.css("a::attr(href)").getall()
```

### 2. Pengambilan Anti-Blokir / Stealth (StealthyFetcher)
Gunakan saat menghadapi situs yang diproteksi WAF / Cloudflare Turnstile:
```python
from scrapling import StealthyFetcher

stealth = StealthyFetcher()
page = stealth.fetch("https://target-with-protection.com")
print("Content length:", len(page.text))
```

### 3. CLI Command
Scrapling juga dapat dijalankan langsung dari terminal:
```bash
scrapling extract "https://example.com" --css "h1"
```

## Keunggulan & Batasan
- **Hemat RAM:** Jauh lebih ringan dibanding Chromium headless penuh (~10MB vs ~400MB).
- **Format Bersih:** Terintegrasi langsung dengan pipeline riset teks dan Content Intelligence Hermes.
