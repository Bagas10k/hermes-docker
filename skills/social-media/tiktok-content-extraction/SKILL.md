---
name: tiktok-content-extraction
description: "Use when extracting TikTok videos, photo slides, or audio."
version: 1.0.0
category: social-media
related_skills:
  - seo-expert
  - content-intelligence
  - instagram-publishing-automation
  - news-editorial-copywriting
---

# TikTok Content Extraction

When extracting TikTok posts — videos, photo mode slideshows, audio, captions, or product hauls — direct curl and browser navigation frequently trigger puzzle slider captchas or unhydrated JSON state. Use the lightweight API fallback pipeline below to bypass interstitials reliably.

## The Procedure

### 1. Shortlink Resolution (vt.tiktok.com / vm.tiktok.com)
Always resolve shortlinks before querying APIs or parsing IDs:

```python
import urllib.request
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    canonical_url = resp.geturl()
```

### 2. Fetch Metadata via Zero-Config Gateway (Bypass Captcha)
Do not use `browser_exec` or direct scrape for raw content; TikTok renders a slider puzzle captcha ("Drag the slider to fit the puzzle") and strips `itemStruct` from `__UNIVERSAL_DATA_FOR_REHYDRATION__`.

Use the TikWM endpoint:

```bash
curl -s -X POST "https://www.tikwm.com/api/" -d "url=https://vt.tiktok.com/EXAMPLE/" -o /tmp/tiktok_meta.json
```

Or via Python:

```python
import urllib.request, urllib.parse, json

api_url = "https://www.tikwm.com/api/"
data = urllib.parse.urlencode({"url": tiktok_url}).encode()
req = urllib.request.Request(api_url, data=data, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    meta = res.get("data", {})
```

### 3. Media Type Routing

- **Photo Mode (Slideshow / Multi-image Haul):**
  Check `meta.get("images")`. It returns a list of high-resolution CDN JPEG URLs.
  Download all slides locally to `/tmp/tiktok_slides/slide_XX.jpg` for processing.
- **Video Mode:**
  Check `meta.get("play")` for the watermark-free MP4 stream, or `meta.get("wmplay")` for watermarked stream.
- **Audio:**
  Check `meta.get("music")` for the direct MP3 soundtrack URL.

### 4. Text & Receipt Extraction Pipeline (Haul / Spill Part Posts)

When analyzing shopping hauls, bicycle builds, tech setups, or multi-item breakdown slides:

1. **Batch Download:** Save all images to `/tmp/tiktok_slides/slide_{i:02d}.jpg`.
2. **Fast OCR Discovery:** Run `tesseract` across the batch (`tesseract slide.jpg stdout -l eng+ind`) to identify which slides contain invoices, product names, or store tags.
3. **Multimodal Deep Extraction:** Call `vision_analyze` on slides with invoices or receipts to verify:
   - Store name (`Toko`)
   - Complete product title and variant (e.g. color, size, tooth count)
   - Unit price vs. final checkout total (`Total pesanan` after discounts/promos)
   - Missing/joke items (e.g. `rem kok gaada (rp 0)`)
4. **Programmatic Calculation:** Compute totals using Python stdlib. Differentiate between:
   - Net total paid (actual checkout out-of-pocket).
   - Retail/catalog total (sum of unit prices before vouchers).

### 5. E-Commerce Link Tracking (Shopee / Marketplace)
When users request links for items in the haul:
- Extract standard search query keywords: `[Brand] [Product Type] [Model/Spec]`.
- Construct URL: `https://shopee.co.id/search?keyword={urllib.parse.quote(query)}`.
- Retain the store name from the screenshot to help the user identify the exact seller.

## Pitfalls & Rules

- **Never rely on browser screenshots to solve TikTok captchas:** The slider puzzle requires interactive drag physics that fail in headless automation. Always pivot to the API endpoint immediately upon encountering a captcha.
- **Differentiate unit price from checkout total:** E-commerce screenshots (Shopee/TikTok Shop) show slashed prices, quantity multipliers, shipping subsidies, and coin cashbacks. Clearly report the net amount actually paid per item.
- **Check slide 1 and final slide roles:** Slide 1 is almost always a teaser cover photo; the final slide is often an aesthetic summary or outro. Do not confuse them with receipt slides.
