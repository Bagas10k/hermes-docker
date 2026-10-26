# Technical SEO & Core Web Vitals

A rigorous technical baseline ensures crawlers can efficiently discover, render, index, and evaluate web pages without resource waste.

## 1. Crawling & Indexing Rules

### Robots.txt Architecture
The `robots.txt` file must be located at the domain root (`/robots.txt`).
- Never block CSS, JavaScript, or font files: Googlebot renders pages like modern Chrome. Blocking assets causes false layout shifts and mobile-unfriendly flags.
- Syntax standard:
```text
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /auth/
Disallow: /*?*sort=
Disallow: /*?*filter=

Sitemap: https://www.example.com/sitemap.xml
```

### Canonicalization Protocols
Canonical tags eliminate duplicate content issues (e.g., HTTP vs HTTPS, trailing slashes, tracking parameters):
```html
<link rel="canonical" href="https://www.example.com/category/product-slug" />
```
- Must be absolute URLs (never relative).
- Canonical target must return HTTP status `200 OK` (never a 301, 302, or 404).
- Self-referencing canonicals are mandatory on all unique master pages.

### Indexation Meta Directives
Control indexing per page:
```html
<!-- Public indexed page -->
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />

<!-- Staging / Internal / Thank You page -->
<meta name="robots" content="noindex, follow" />
```

---

## 2. Core Web Vitals (CWV) Targets & Engineering Fixes

Google measures user experience via three critical real-world performance metrics:

| Metric | Target (Good) | Measures | Primary Engineering Fixes |
|---|---|---|---|
| **LCP (Largest Contentful Paint)** | <= 2.5s | Perceived loading speed | 1. Preload hero image (`<link rel="preload" as="image" href="..." fetchpriority="high">`).<br>2. Compress images to AVIF/WebP.<br>3. Eliminate render-blocking CSS/JS. |
| **INP (Interaction to Next Paint)** | <= 200ms | UI responsiveness to user clicks/keys | 1. Break long JS tasks (`setTimeout(0)` or `scheduler.yield()`).<br>2. Avoid heavy React/Vue re-renders on inputs.<br>3. Defer non-critical third-party analytics. |
| **CLS (Cumulative Layout Shift)** | <= 0.1 | Visual stability | 1. Always set explicit `width` and `height` attributes on `<img>` and `<video>`.<br>2. Reserve aspect-ratio CSS boxes for dynamic ads/embeds.<br>3. Avoid inserting DOM elements above existing content. |

---

## 3. Rendering Strategies: SSR/SSG vs CSR

| Mode | Search Engine Impact | Best Fit |
|---|---|---|
| **SSG (Static Site Generation)** | Optimal. Instant TTFB, pre-rendered HTML ready for immediate parsing. | Blogs, documentation, marketing landing pages, e-commerce catalog. |
| **SSR (Server-Side Rendering)** | Excellent. Dynamic data baked into HTML on server before response. | Dashboards, live news, real-time inventory pricing. |
| **CSR (Client-Side Rendering)** | High risk. Search bots execute JS in a second wave; if CPU quota lapses, page is indexed blank. | Authenticated admin apps (where SEO does not matter). |

---

## 4. XML Sitemap Best Practices
- Only include indexable, canonical URLs (HTTP 200).
- Keep sitemap under 50,000 URLs or 50MB uncompressed (split into Sitemap Index if larger).
- Update `<lastmod>` only when meaningful content updates occur.
- Submit via Google Search Console and reference in `robots.txt`.
