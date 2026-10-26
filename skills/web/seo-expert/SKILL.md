---
name: seo-expert
description: Audit, optimize, and rank web pages for search engines.
version: 0.1.0
author: Hermes
license: MIT
related_skills:
  - upnormal-ui-architecture
  - content-intelligence
  - news-editorial-copywriting
  - fullstack-systems
metadata:
  hermes:
    tags:
      - SEO
      - SearchEngineOptimization
      - TechnicalSEO
      - CoreWebVitals
      - SchemaMarkup
---

# SEO Expert

Audit, optimize, and rank modern web applications across traditional search engines (Google, Bing) and AI generative search engines (Perplexity, ChatGPT Search, Google AI Overviews). Covers technical foundations, semantic on-page architecture, JSON-LD structured data, and programmatic scale while banishing spam and thin-content penalties.

## When to Use
- "audit SEO website ini" / "analisis SEO halaman ini"
- "optimalkan ranking Google" / "bagaimana cara ranking 1 untuk keyword X"
- "pasang schema markup JSON-LD" / "setup rich snippets"
- "perbaiki Core Web Vitals (LCP, INP, CLS)"
- "optimasi untuk AI Search / Perplexity / Google SGE"
- "buat robots.txt, sitemap.xml, dan metadata OpenGraph"

## Prerequisites
- Standard Python 3 runtime with `urllib` and `json` (stdlib only for baseline auditing).
- Beautiful Soup 4 optional for deeper DOM extraction (`pip install beautifulsoup4`).
- CLI/Dev environment access via `terminal`.

## How to Run
Invoke the built-in SEO audit engine via the `terminal` tool:
```bash
# Audit live URL with SERP preview and health score
python3 scripts/seo_audit.py --url "https://example.com"

# Audit local build file
python3 scripts/seo_audit.py --file "public/index.html"

# Crawl and batch audit XML sitemap
python3 scripts/seo_audit.py --sitemap "https://example.com/sitemap.xml" --limit 20 --output audit.json
```

## Quick Reference
- Title tag: 50-60 characters, primary keyword front-loaded, brand at tail.
- Meta Description: 120-155 characters, clear value proposition with active call to action.
- Heading hierarchy: Exactly one `<h1>` per page matching the page primary thesis, logically nested `<h2>` and `<h3>`.
- Canonical tag: `<link rel="canonical" href="https://example.com/canonical-url">` on every page to prevent duplicate dilution.
- OpenGraph & Twitter: `og:title`, `og:description`, `og:image` (1200x630px, 1.91:1 ratio), `twitter:card`.
- Structured Data: Self-contained `<script type="application/ld+json">` in `<head>`.
- Core Web Vitals targets: LCP <= 2.5s, INP <= 200ms, CLS <= 0.1.

## Procedure

1. **Conduct Automated Technical Audit:**
   Execute `scripts/seo_audit.py` via `terminal` against target URL or local HTML file. Review title length, meta description, missing image alt attributes, canonical tag presence, viewport tag, and robots directives.

2. **Validate Semantic Heading & Content Structure:**
   Inspect DOM using `read_file` or `web_extract`. Verify:
   - Only 1 semantic `<h1>`.
   - Sections broken into clear `<h2>` topic clusters with SILO internal links.
   - Images contain descriptive, contextual `alt` attributes (no keyword stuffing).

3. **Deploy Schema.org JSON-LD Structured Data:**
   Inject context-appropriate schemas into page `<head>`. Load `references/schema-structured-data.md` for verbatim templates (`Article`, `Product`, `FAQPage`, `BreadcrumbList`, `LocalBusiness`).

4. **Audit Robots.txt & XML Sitemap:**
   Inspect `/robots.txt` and `/sitemap.xml`:
   - Ensure crawlers are not inadvertently disallowed from critical CSS/JS or content paths.
   - Sitemap must only include canonical, HTTP 200 URLs (no redirects or 404s).

5. **Optimize for AI Engines (AEO / GEO):**
   Structure content with direct answer definitions within the first 60 words under questions, citation-friendly statistics, and bulleted takeaways to capture Google AI Overviews and Perplexity citations.

## References
Load detailed operational references on demand using `skill_view` (`name="seo-expert"`, `file_path="references/<file>"`):
- `references/technical-seo-core-web-vitals.md`: Indexing rules, canonicalization, Core Web Vitals (LCP, INP, CLS), SSR/SSG vs CSR, and crawl budget management.
- `references/on-page-content-architecture.md`: Heading hierarchies, search intent mapping (informational, transactional), E-E-A-T signals, and internal linking SILO.
- `references/schema-structured-data.md`: Validated JSON-LD schemas for Rich Snippets, Organizations, Products, FAQs, and Breadcrumbs.
- `references/programmatic-and-ai-search.md`: Programmatic SEO (pSEO) database-driven page architecture and Generative Engine Optimization (GEO).
- `references/international-and-multilingual-seo.md`: Multilingual URL routing, bidirectional hreflang tags, and Indonesian market search nuances.
- `references/seo-incident-recovery-and-migrations.md`: Google Core/HCU update recovery, zero-downtime 301 migration DAG, and soft-404 elimination.

## Pitfalls
- **Client-Side Rendering (CSR) Trap:** Relying purely on client-side JS without Server-Side Rendering (SSR) or Static Site Generation (SSG). Search bots may index blank HTML if rendering budget expires.
- **Cannibalization:** Targeting the exact same primary keyword across multiple URLs on the same domain, causing ranking volatility.
- **Soft 404s:** Returning HTTP 200 for empty or "not found" pages instead of HTTP 404 or 410.
- **Blocked Rendering Assets:** Disallowing Googlebot from accessing CSS and JS in `robots.txt`, preventing proper mobile-friendly evaluation.

## Verification
Run audit script on target page:
```bash
python3 scripts/seo_audit.py --url "https://example.com"
```
Verify zero critical errors in title, meta tags, canonical link, and structured data validation.
