#!/usr/bin/env python3
"""
Production-Grade SEO Audit & Crawler Engine (Stdlib First).
Audits technical health, on-page semantics, Core Web Vitals readiness,
Schema.org structured data, and SERP visual rendering. Supports single URL, local file, or bulk XML sitemaps.
"""

import sys
import os
import argparse
import urllib.request
import urllib.parse
import re
import json
import time
from html.parser import HTMLParser

class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.metas = []
        self.canonical = None
        self.h1_tags = []
        self.in_h1 = False
        self.current_h1 = ""
        self.h2_tags = []
        self.in_h2 = False
        self.current_h2 = ""
        self.h3_count = 0
        self.images = [] # dict with src, alt, width, height
        self.links = [] # href, text, rel
        self.current_link = {}
        self.in_a = False
        self.json_ld = []
        self.in_script = False
        self.script_type = ""
        self.current_script = ""

    def handle_starttag(self, tag, attrs):
        attr_dict = {k.lower(): v for k, v in attrs}
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            self.metas.append(attr_dict)
        elif tag == "link":
            if attr_dict.get("rel") == "canonical":
                self.canonical = attr_dict.get("href")
        elif tag == "h1":
            self.in_h1 = True
            self.current_h1 = ""
        elif tag == "h2":
            self.in_h2 = True
            self.current_h2 = ""
        elif tag == "h3":
            self.h3_count += 1
        elif tag == "a":
            self.in_a = True
            self.current_link = {
                "href": attr_dict.get("href", ""),
                "rel": attr_dict.get("rel", ""),
                "target": attr_dict.get("target", ""),
                "text": ""
            }
        elif tag == "img":
            self.images.append({
                "src": attr_dict.get("src", ""),
                "alt": attr_dict.get("alt"),
                "width": attr_dict.get("width"),
                "height": attr_dict.get("height"),
                "loading": attr_dict.get("loading")
            })
        elif tag == "script":
            stype = attr_dict.get("type", "").lower()
            if stype == "application/ld+json":
                self.in_script = True
                self.script_type = stype
                self.current_script = ""

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
            if self.current_h1.strip():
                self.h1_tags.append(self.current_h1.strip())
        elif tag == "h2":
            self.in_h2 = False
            if self.current_h2.strip():
                self.h2_tags.append(self.current_h2.strip())
        elif tag == "a":
            self.in_a = False
            if self.current_link.get("href"):
                self.current_link["text"] = self.current_link["text"].strip()
                self.links.append(self.current_link)
        elif tag == "script" and self.in_script:
            self.in_script = False
            if self.current_script.strip():
                try:
                    parsed = json.loads(self.current_script)
                    self.json_ld.append(parsed)
                except Exception as e:
                    self.json_ld.append({"_parse_error": str(e), "raw": self.current_script[:120]})

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_h1:
            self.current_h1 += data
        elif self.in_h2:
            self.current_h2 += data
        elif self.in_a:
            self.current_link["text"] += data
        elif self.in_script:
            self.current_script += data

def audit_html(html_content, source_name="Target", response_time_ms=None):
    parser = SEOParser()
    parser.feed(html_content)

    results = {
        "source": source_name,
        "response_time_ms": response_time_ms,
        "score": 100,
        "checks": [],
        "passed": 0,
        "warnings": 0,
        "errors": 0,
        "serp_preview": {}
    }

    def add_check(category, name, status, message, details=None, penalty=0):
        results["checks"].append({
            "category": category,
            "name": name,
            "status": status,
            "message": message,
            "details": details
        })
        if status == "PASS":
            results["passed"] += 1
        elif status == "WARN":
            results["warnings"] += 1
            results["score"] = max(0, results["score"] - (penalty or 5))
        else:
            results["errors"] += 1
            results["score"] = max(0, results["score"] - (penalty or 15))

    # Response Time / TTFB check
    if response_time_ms is not None:
        if response_time_ms < 600:
            add_check("Performance", "TTFB / Server Latency", "PASS", f"Fast server response: {response_time_ms}ms")
        elif response_time_ms < 1500:
            add_check("Performance", "TTFB / Server Latency", "WARN", f"Moderate latency: {response_time_ms}ms. Optimize database/caching.", penalty=5)
        else:
            add_check("Performance", "TTFB / Server Latency", "FAIL", f"Slow TTFB: {response_time_ms}ms. Risks search crawler timeout.", penalty=15)

    # 1. Title Tag
    title = parser.title.strip()
    results["serp_preview"]["title"] = title or "(No Title)"
    if not title:
        add_check("Technical", "Title Tag", "FAIL", "Missing <title> tag in <head>.", penalty=20)
    else:
        tlen = len(title)
        if 40 <= tlen <= 62:
            add_check("Technical", "Title Tag", "PASS", f"Title length optimal ({tlen} chars): '{title}'")
        elif tlen < 40:
            add_check("Technical", "Title Tag", "WARN", f"Title short ({tlen} chars): '{title}'. Recommended: 50-60 chars.", penalty=5)
        else:
            add_check("Technical", "Title Tag", "WARN", f"Title exceeds 62 chars ({tlen} chars, will truncate): '{title[:60]}...'", penalty=5)

    # 2. Meta Description
    desc = None
    for m in parser.metas:
        if m.get("name", "").lower() == "description":
            desc = m.get("content", "").strip()
            break
    
    results["serp_preview"]["description"] = desc or "(No Description provided)"
    if not desc:
        add_check("Technical", "Meta Description", "FAIL", "Missing <meta name='description'> tag.", penalty=15)
    else:
        dlen = len(desc)
        if 115 <= dlen <= 160:
            add_check("Technical", "Meta Description", "PASS", f"Meta description length optimal ({dlen} chars).")
        elif dlen < 115:
            add_check("Technical", "Meta Description", "WARN", f"Meta description short ({dlen} chars): '{desc}'. Recommended: 120-155 chars.", penalty=5)
        else:
            add_check("Technical", "Meta Description", "WARN", f"Meta description exceeds 160 chars ({dlen} chars, will truncate).", penalty=5)

    # 3. Viewport (Mobile Friendly)
    viewport = any(m.get("name", "").lower() == "viewport" for m in parser.metas)
    if viewport:
        add_check("Technical", "Mobile Viewport", "PASS", "Mobile viewport tag present.")
    else:
        add_check("Technical", "Mobile Viewport", "FAIL", "Missing <meta name='viewport'> tag. Critical mobile failure.", penalty=20)

    # 4. Canonical Tag
    if parser.canonical:
        if parser.canonical.startswith("http://") or parser.canonical.startswith("https://"):
            add_check("Technical", "Canonical URL", "PASS", f"Absolute canonical present: {parser.canonical}")
        else:
            add_check("Technical", "Canonical URL", "WARN", f"Canonical URL is relative: {parser.canonical}. Absolute URL strongly required.", penalty=10)
    else:
        add_check("Technical", "Canonical URL", "WARN", "Missing <link rel='canonical'> tag. Duplicate dilution risk.", penalty=10)

    # 5. Robots Meta Directives
    robots_meta = [m.get("content", "") for m in parser.metas if m.get("name", "").lower() == "robots"]
    if robots_meta:
        content = " ".join(robots_meta).lower()
        if "noindex" in content:
            add_check("Indexation", "Robots Meta", "WARN", f"Page explicitly set to 'noindex': {content}. Not visible in Google.")
        else:
            add_check("Indexation", "Robots Meta", "PASS", f"Robots directives: {content}")
    else:
        add_check("Indexation", "Robots Meta", "PASS", "Default index, follow behavior active (no restrictive robots meta).")

    # 6. Heading 1 Hierarchy
    h1_count = len(parser.h1_tags)
    if h1_count == 1:
        add_check("Structure", "H1 Heading", "PASS", f"Exactly one <h1> tag present: '{parser.h1_tags[0]}'")
    elif h1_count == 0:
        add_check("Structure", "H1 Heading", "FAIL", "No <h1> heading found on page.", penalty=15)
    else:
        add_check("Structure", "H1 Heading", "WARN", f"Multiple <h1> headings found ({h1_count}). Recommended: 1 unique H1 per document.", parser.h1_tags, penalty=5)

    # 7. Secondary Headings
    h2_count = len(parser.h2_tags)
    if h2_count > 0:
        add_check("Structure", "H2/H3 Hierarchy", "PASS", f"Structured headings found: {h2_count} H2s, {parser.h3_count} H3s.")
    else:
        add_check("Structure", "H2/H3 Hierarchy", "WARN", "No <h2> headings found. Content lacks topical chunking for AI RAG parsers.", penalty=5)

    # 8. Image Alt & Sizing (Core Web Vitals CLS)
    if parser.images:
        missing_alts = [img["src"] for img in parser.images if img["alt"] is None or not img["alt"].strip()]
        missing_dims = [img["src"] for img in parser.images if not img["width"] or not img["height"]]
        total_imgs = len(parser.images)
        
        if not missing_alts:
            add_check("Accessibility & Content", "Image Alt Attributes", "PASS", f"All {total_imgs} images contain alt attributes.")
        else:
            add_check("Accessibility & Content", "Image Alt Attributes", "WARN", f"{len(missing_alts)} of {total_imgs} images missing alt text.", missing_alts[:5], penalty=5)

        if not missing_dims:
            add_check("Core Web Vitals", "Image Dimensions (CLS Prevention)", "PASS", "All images specify explicit width & height attributes.")
        else:
            add_check("Core Web Vitals", "Image Dimensions (CLS Prevention)", "WARN", f"{len(missing_dims)} of {total_imgs} images lack width/height attributes (Layout Shift risk).", penalty=5)
    else:
        add_check("Accessibility & Content", "Image Alt Attributes", "PASS", "No images detected on page.")

    # 9. Link Integrity (Internal & External Links)
    if parser.links:
        vague_anchors = [l for l in parser.links if l["text"].lower() in ["klik disini", "click here", "here", "link", "more", "baca selengkapnya"]]
        if vague_anchors:
            add_check("Content Architecture", "Anchor Text Quality", "WARN", f"Found {len(vague_anchors)} low-value generic anchor links (e.g., 'klik disini'). Use descriptive keywords.", penalty=5)
        else:
            add_check("Content Architecture", "Anchor Text Quality", "PASS", f"Evaluated {len(parser.links)} links; anchor texts are descriptive.")

    # 10. OpenGraph & Social Cards
    og_title = any(m.get("property", "").lower() == "og:title" for m in parser.metas)
    og_image = any(m.get("property", "").lower() == "og:image" for m in parser.metas)
    twitter_card = any(m.get("name", "").lower() == "twitter:card" for m in parser.metas)

    if og_title and og_image and twitter_card:
        add_check("Social & Distribution", "OpenGraph / Twitter", "PASS", "Complete OpenGraph (og:title, og:image) and Twitter Card tags present.")
    elif og_title or og_image or twitter_card:
        add_check("Social & Distribution", "OpenGraph / Twitter", "WARN", "Partial social tags detected. Ensure og:title, og:image, and twitter:card are all configured.", penalty=5)
    else:
        add_check("Social & Distribution", "OpenGraph / Twitter", "WARN", "Missing OpenGraph and Twitter card metadata.", penalty=5)

    # 11. Schema.org JSON-LD Structured Data
    if parser.json_ld:
        errors_in_schema = [s for s in parser.json_ld if "_parse_error" in s]
        if not errors_in_schema:
            schema_types = []
            for s in parser.json_ld:
                if isinstance(s, dict):
                    t = s.get("@type")
                    if t:
                        schema_types.append(t)
                    elif "@graph" in s and isinstance(s["@graph"], list):
                        schema_types.extend([item.get("@type", "Unknown") for item in s["@graph"]])
            add_check("Structured Data", "Schema.org JSON-LD", "PASS", f"Valid JSON-LD schema found ({len(parser.json_ld)} blocks): {', '.join(schema_types)}")
        else:
            add_check("Structured Data", "Schema.org JSON-LD", "FAIL", "JSON-LD script contained syntax errors.", errors_in_schema, penalty=15)
    else:
        add_check("Structured Data", "Schema.org JSON-LD", "WARN", "No Schema.org JSON-LD structured data detected (Rich Snippet loss).", penalty=10)

    return results

def print_report(results):
    score = results['score']
    grade = "A+" if score >= 95 else ("A" if score >= 90 else ("B" if score >= 80 else ("C" if score >= 70 else "D")))
    
    print("\n" + "═" * 65)
    print(f" 🔍 SEO AUDIT REPORT: {results['source']}")
    print("═" * 65)
    print(f" Health Score: {score}/100 [Grade {grade}]")
    print(f" Summary:      {results['passed']} Passed | {results['warnings']} Warnings | {results['errors']} Errors")
    if results.get("response_time_ms"):
        print(f" Latency:      {results['response_time_ms']} ms")
    print("─" * 65)

    # SERP Snippet Preview
    sp = results.get("serp_preview", {})
    print(" 📱 GOOGLE SERP PREVIEW (DESKTOP & MOBILE):")
    print(f"   \033[1;34m{sp.get('title', '')}\033[0m")
    print(f"   \033[32m{results['source']}\033[0m")
    print(f"   \033[90m{sp.get('description', '')}\033[0m")
    print("─" * 65)

    for c in results["checks"]:
        icon = "\033[32m[PASS]\033[0m" if c["status"] == "PASS" else ("\033[33m[WARN]\033[0m" if c["status"] == "WARN" else "\033[31m[FAIL]\033[0m")
        print(f" {icon} \033[1m[{c['category']}]\033[0m {c['name']}")
        print(f"        {c['message']}")
        if c.get("details"):
            print(f"        \033[90mDetails: {c['details']}\033[0m")
    print("═" * 65 + "\n")

def parse_sitemap(sitemap_url):
    req = urllib.request.Request(sitemap_url, headers={"User-Agent": "Mozilla/5.0 (compatible; HermesSEOEngine/1.0)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        xml = resp.read().decode("utf-8", errors="ignore")
    urls = re.findall(r"<loc>(https?://[^<]+)</loc>", xml)
    return urls

def main():
    parser = argparse.ArgumentParser(description="Production-Grade SEO Audit & Crawler Engine")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="Target URL to fetch and audit")
    group.add_argument("--file", help="Local HTML file path to audit")
    group.add_argument("--sitemap", help="XML Sitemap URL to batch audit")
    parser.add_argument("--json", action="store_true", help="Output raw JSON results")
    parser.add_argument("--output", help="Save audit result to JSON file")
    parser.add_argument("--limit", type=int, default=10, help="Max URLs to audit from sitemap (default: 10)")

    args = parser.parse_args()

    if args.sitemap:
        print(f"Fetching sitemap: {args.sitemap}")
        try:
            urls = parse_sitemap(args.sitemap)
            print(f"Discovered {len(urls)} URLs in sitemap. Auditing top {min(len(urls), args.limit)} URLs...\n")
        except Exception as e:
            print(f"Failed to fetch/parse sitemap: {e}", file=sys.stderr)
            sys.exit(1)

        batch_results = []
        for idx, u in enumerate(urls[:args.limit]):
            try:
                start_t = time.time()
                req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (compatible; HermesSEOEngine/1.0)"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    html = resp.read().decode("utf-8", errors="ignore")
                latency_ms = int((time.time() - start_t) * 1000)
                res = audit_html(html, u, response_time_ms=latency_ms)
                batch_results.append(res)
                if not args.json:
                    print_report(res)
            except Exception as err:
                print(f"Error auditing {u}: {err}")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(batch_results, f, indent=2)
            print(f"Saved batch results to {args.output}")
        if args.json:
            print(json.dumps(batch_results, indent=2))
        return

    html = ""
    source = ""
    latency_ms = None
    if args.url:
        source = args.url
        start_t = time.time()
        req = urllib.request.Request(args.url, headers={"User-Agent": "Mozilla/5.0 (compatible; HermesSEOEngine/1.0)"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            latency_ms = int((time.time() - start_t) * 1000)
        except Exception as e:
            print(f"Error fetching URL: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.file:
        source = args.file
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                html = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)

    results = audit_html(html, source, response_time_ms=latency_ms)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Saved report to {args.output}")

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)

if __name__ == "__main__":
    main()
