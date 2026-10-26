# SEO Incident Recovery & Site Migration DAG

Recovering from traffic drops (Google Core Updates, Helpful Content Updates / HCU) and safely executing site migrations without catastrophic rank loss.

## 1. Google Core Update & HCU Recovery Protocol

When an algorithmic traffic drop occurs (> 25% organic decline following a confirmed Google search update):

```text
[PHASE 1: TRAFFIC AUDIT] ➔ [PHASE 2: PAGE ISOLATION] ➔ [PHASE 3: PURGE OR MERGE] ➔ [PHASE 4: E-E-A-T INJECTION]
(Compare 28-day GSC)       (Identify fallen URLs)      (Prune low-value fluff)    (Direct author proof & data)
```

### Forensic Action Plan:
1. **Query & Page Isolation:**
   - Filter Google Search Console (GSC) by "Date: Compare last 28 days year-over-year".
   - Isolate which specific query clusters lost CTR vs which lost average position.
2. **The "Helpful Content" Audit:**
   - Detect AI Slop: Eliminate boilerplate intros, generic summarize-the-web filler, and clickbait headlines.
   - First-Hand Experience: Embed original photos, telemetry logs, real code snippets, and author bios demonstrating verified real-world practice.
3. **Pruning & Consolidation (Merge DAG):**
   - Identify zombie URLs (< 5 visits in 6 months).
   - If low quality with zero backlinks: Return HTTP 410 (Gone).
   - If valuable topic but thin: Merge into a master pillar page with a permanent 301 redirect.

---

## 2. Zero-Downtime Site Migration Playbook

For domain renaming, restructuring URL paths, or moving to a new CMS:

### Pre-Migration Checklist
- [ ] Crawl full legacy site and save master URL baseline (`urls_legacy.csv`).
- [ ] Construct 1:1 Redirect Map (`old_url` -> `new_url`). Never redirect all pages to the homepage (Google treats homepage redirects as soft 404s).
- [ ] Prepare new XML Sitemap and robots.txt in staging.

### Cutover Day Execution
1. Deploy Nginx / Caddy 301 redirect rules:
```nginx
# Permanent 301 redirection rule
rewrite ^/old-category/(.*)$ /category/$1 permanent;
```
2. Verify redirect status via `curl -I`:
   - Must return HTTP `301 Moved Permanently`.
   - Must point directly to target (single hop, strictly zero redirect chains 301 -> 301 -> 200).
3. Submit "Change of Address" in Google Search Console.
4. Upload both legacy sitemap (with 301s) and new sitemap (with 200s) to expedite crawler verification.

### Post-Migration Monitoring
- Daily GSC crawl stats inspection: look for spike in 404s, 500s, or redirect errors.
- Monitor canonical acceptance: check if Google has selected the new canonical URL.
