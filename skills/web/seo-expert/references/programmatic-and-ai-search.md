# Programmatic SEO & Generative Engine Optimization (AEO / GEO)

Scaling pages across programmatic database architectures while positioning content to be cited by LLM answer engines (Perplexity, ChatGPT Search, Claude, Google AI Overviews).

## 1. Programmatic SEO (pSEO) Architectural Rules

Programmatic SEO automatically generates thousands of high-intent landing pages from a structured database (e.g., `/{city}/toko-material/` or `/{part-a}-vs-{part-b}/`).

### Anti-Thin Content Safeguards
Google aggressively penalizes repetitive programmatic templates that merely swap city names or product titles without real value.
- **Minimum 40% Unique Data:** Each page must pull dynamic, factual attributes from the database:
  - Local addresses, maps, phone numbers, delivery zones.
  - Spec comparison tables, verified benchmark scores, pros/cons.
  - Real customer reviews or unique situational commentary.
- **Indexation Thresholds:**
  - If a generated page has zero data (e.g. 0 items found in city X), do NOT index it (`meta robots: noindex, follow`).
  - Keep internal links active so bots discover future populated pages.
- **Dynamic Meta Titles & Descriptions:**
  - Standardize formulas that sound human and varied:
  ```typescript
  const title = `${category} di ${cityName}: Daftar Toko & Harga Terbaru 2026`;
  const desc = `Temukan ${supplierCount} distributor ${category} terdekat di ${cityName}. Cek alamat, nomor WA, dan perbandingan harga sak/curah di sini.`;
  ```

---

## 2. Generative Engine Optimization (GEO / AEO)

AI engines (Perplexity, Google AI Overviews, SearchGPT) synthesize answers using Retrieval-Augmented Generation (RAG). To become the cited authority:

### A. The Direct Answer Formula (First 60 Words)
Under every question heading (`<h2>Bagaimana cara X?</h2>`), provide a concise, direct definition or answer within the first 40-60 words before expanding into nuances:
> *"Untuk memasang RD Shimano Acera pada sepeda minion, gunakan anting RD adaptor gotlink untuk menjembatani dropout standar. Pastikan baut kencang pada torsi 8-10 Nm dan setel baut limit H dan L sebelum memasang rantai."*

### B. High-Information Density Formatting
AI crawlers prioritize dense, scannable structures:
1. **Markdown Tables:** LLM tokenizers parse markdown tables with high semantic precision.
2. **Numbered Procedures:** Strict sequential steps (1, 2, 3) are frequently pulled verbatim into AI step-by-step answers.
3. **Bulleted Pros/Cons & Takeaways:** Direct bullet points with bold leading hooks.

### C. Primary Source Authority & Verifiable Grounding
- Embed original statistics, internal telemetry, or direct test results (*"Berdasarkan pengujian 200 km pada medan tanjakan..."*).
- Include explicit author credentials and publication dates.
- Link out to authoritative primary standards (ISO, manufacturer technical specs, official patents).

---

## 3. Crawl Rate & Bot Admission

Allow modern AI search bots in `robots.txt` unless competitive intelligence must remain shielded:
```text
# Enable AI generative search bots for citations
User-agent: PerplexityBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: Google-Extended
Allow: /
```

---

## 4. Utility Micro-Tools & Instant Calculators (Traffic-to-Cash pSEO)

Interactive utility micro-tools (e.g., material estimation calculators, loan/tax simulators, unit converters) capture high-intent transactional and informational search queries with zero bounce rate and high monetization value.

### A. Architectural Principles
1. **Static HTML Prerendering + Zero-Latency Client JS:**
   - Prerender the complete DOM structure with sensible default inputs and pre-calculated baseline figures.
   - Do not render an empty container waiting for client JS. Search bots must index full formulas, calculation methodology, and default results immediately in the raw HTML response.
   - Run live recalculations purely in browser memory (vanilla JS) on input change events for instant 60 FPS user feedback with zero backend server load.
2. **Schema.org Structured Data Dual-Stack:**
   - Pair `SoftwareApplication` (`applicationCategory: "BusinessApplication"` or `"UtilityApplication"`, `operatingSystem: "All"`, `offers: {"@type": "Offer", "price": "0"}`) with `FAQPage` covering common measurement rules and calculation examples.
3. **Monetization & CLS-Safe Ad Slotting:**
   - Reserve fixed-height min-height containers (`min-height: 90px` or `250px`) for responsive Google AdSense or display ads above and below the calculator to maintain Cumulative Layout Shift (CLS <= 0.1).
4. **Automated Assertion-Driven Compilation:**
   - When generating pages via Python or Node build scripts, embed assertion self-checks verifying:
     - Mathematical accuracy against official standards (e.g., SNI or standard financial formulas).
     - XML sitemap freshness and exact canonical URL alignment across all generated utility slugs.
