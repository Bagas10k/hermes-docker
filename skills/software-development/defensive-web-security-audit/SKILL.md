---
name: defensive-web-security-audit
description: Use when safely auditing website security posture.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, web-audit, passive-audit, hardening, wordpress]
---

# Defensive Web Security Audit

Use this skill when the user asks to check, scan, or build tools for website security posture. This skill is for defensive, authorized, and passive assessment only.

## Procedure

1. **Set the boundary first**
   - If the target is not clearly owned or authorized by the user, perform only passive checks.
   - Refuse stealth, evasion, brute force, bypass login, exploit payloads, active injection, fuzzing, or form submission against a public third-party site.
   - Offer an admin-facing hardening report instead of exploit instructions.
   - Clarify the distinction between hardening debt and a breach immediately: missing defense-in-depth controls (HSTS, CSP, X-Frame-Options) do not mean an intruder has gained access or that data has leaked.

2. **Run a safe passive browser audit**
   - Use a headless browser to load the public URL once and collect:
     - HTTP status and final URL.
     - Response security headers: HSTS, CSP, X-Content-Type-Options, X-Frame-Options or CSP frame-ancestors, Referrer-Policy, Permissions-Policy.
     - Cookie flags: Secure, HttpOnly, SameSite.
     - Public forms and whether any sensitive-looking fields submit via GET or non-HTTPS.
     - Public scripts, third-party hosts, mixed content, and missing SRI for static third-party scripts.
   - Store a JSON report with score, evidence, and remediation recommendations.

3. **Add deeper passive CMS checks when the site looks like WordPress**
   - Fetch only a small allowlist of public endpoints: `/robots.txt`, `/sitemap.xml`, `/wp-json/`, `/wp-json/wp/v2/types`, `/wp-json/wp/v2/users`, `/wp-login.php`, `/xmlrpc.php`, `/readme.html`, and `/license.txt`.
   - Treat `/wp-json/wp/v2/users` returning 401/403 as a positive control, not a vulnerability.
   - Treat `/xmlrpc.php` returning "POST requests only" as an exposed attack surface, not a confirmed exploit.
   - Extract public plugin/theme names and asset version hints from HTML without probing plugin files beyond what the homepage already references.

4. **Report with defensive language**
   - Separate proof from risk: missing CSP/HSTS, public WordPress metadata, or exposed login pages are hardening debt, not evidence of compromise.
   - Address data-leak questions directly: explain that passive header/endpoint scanning cannot prove or disprove internal data exfiltration, but confirm whether public user-listing endpoints (/wp-json/wp/v2/users) were blocked.
   - When asked to prove a vulnerability is dangerous, provide defensive proofs only (e.g. curl header inspection, safe local HTML mocks for clickjacking or CSP bypass) rather than active exploitation against the target.
   - Give concrete admin-side fixes: add headers, restrict XML-RPC if unused, hide readme/license, update plugins/themes, add WAF/rate limits, and review logs.
   - Do not provide payloads, stealth advice, or instructions to avoid detection.

## Safe Passive Auditor Template

When building a small tool, implement it as a passive auditor:

- Browser loads only the target page and collects headers/cookies/DOM inventory.
- Optional allowlist probes are limited to public metadata endpoints.
- No login attempts, no brute force, no mutation, no POST except explicit admin-owned staging tests.
- Output JSON plus a concise summary.

## Pitfalls

- Do not call missing headers a breach; the mechanism is impact amplification and weaker browser-side containment, not system entry by itself.
- Do not test script injection on third-party sites; active payload injection crosses from posture assessment into exploitation unless explicit written authorization and a staging target exist.
- Do not advise "stay undetected" techniques; that changes a defensive request into evasion-oriented activity.
- Do not infer exact WordPress core or plugin versions from query-string hints alone; label them as asset version hints unless verified by admin-side evidence.

## Verification

A completed safe audit must include:

- Target URL, final URL, HTTP status, and timestamp.
- Findings grouped by severity with evidence and remediation.
- Explicit statement that the scan was passive and non-exploitative.
- A clear conclusion distinguishing confirmed findings from possible risks.
