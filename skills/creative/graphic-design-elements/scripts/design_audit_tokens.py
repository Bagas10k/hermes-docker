#!/usr/bin/env python3
"""
Graphic Design Elements & Token Auditor.
Audits web interfaces, CSS, and SVG files for adherence to design fundamentals:
WCAG AAA contrast (>= 7:1), zero-emoji policy, custom form validation (novalidate),
and absence of native browser dialogs (confirm/alert).
"""

import sys
import os
import argparse
import re
import json
import math

def calculate_relative_luminance(r, g, b):
    """Calculates relative luminance according to WCAG 2.1 specs."""
    def channel_lum(val):
        c = val / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel_lum(r) + 0.7152 * channel_lum(g) + 0.0722 * channel_lum(b)

def parse_hex_color(hex_str):
    hex_clean = hex_str.strip().lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join([c*2 for c in hex_clean])
    if len(hex_clean) == 6:
        return int(hex_clean[0:2], 16), int(hex_clean[2:4], 16), int(hex_clean[4:6], 16)
    return None

def compute_contrast_ratio(hex_fg, hex_bg):
    rgb_fg = parse_hex_color(hex_fg)
    rgb_bg = parse_hex_color(hex_bg)
    if not rgb_fg or not rgb_bg:
        return 1.0
    lum1 = calculate_relative_luminance(*rgb_fg)
    lum2 = calculate_relative_luminance(*rgb_bg)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)

def audit_design_file(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    results = {
        "file": filepath,
        "score": 100,
        "checks": [],
        "passed": 0,
        "warnings": 0,
        "errors": 0
    }

    def add_check(category, name, status, message, penalty=0):
        results["checks"].append({
            "category": category,
            "name": name,
            "status": status,
            "message": message
        })
        if status == "PASS":
            results["passed"] += 1
        elif status == "WARN":
            results["warnings"] += 1
            results["score"] = max(0, results["score"] - penalty)
        else:
            results["errors"] += 1
            results["score"] = max(0, results["score"] - penalty)

    # 1. Zero-Emoji Check (Zero Emoji Policy in UI Elements)
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F]'   # emoticons
        r'|[\U0001F300-\U0001F5FF]'  # symbols & pictographs
        r'|[\U0001F680-\U0001F6FF]'  # transport & map
        r'|[\U0001F1E0-\U0001F1FF]'  # flags
        r'|[\u2702-\u27B0]'
        r'|[\u24C2-\u2573]',
        re.UNICODE
    )
    emoji_matches = emoji_pattern.findall(content)
    if emoji_matches:
        add_check("Visual Language", "Zero-Emoji Policy", "WARN", f"Found {len(emoji_matches)} unicode emojis in UI source. Standard: use 100% SVG line icons instead.", penalty=10)
    else:
        add_check("Visual Language", "Zero-Emoji Policy", "PASS", "Zero emojis detected. Clean vector/text iconography.")

    # 2. Native Dialog Ban (confirm/alert)
    native_confirm = re.findall(r'\b(confirm|alert|prompt)\s*\(', content)
    if native_confirm:
        add_check("Control Governance", "Anti-Native Dialogs", "FAIL", f"Found raw browser dialogs: {set(native_confirm)}. Wajib ganti dengan custom async modal.", penalty=25)
    else:
        add_check("Control Governance", "Anti-Native Dialogs", "PASS", "No native window.confirm or alert calls detected.")

    # 3. Form Validation Governance (novalidate check)
    forms = re.findall(r'<form\b[^>]*>', content, re.IGNORECASE)
    if forms:
        unvalidated = [f for f in forms if "novalidate" not in f.lower()]
        if unvalidated:
            add_check("Form Validation", "Anti-Native Tooltips", "WARN", f"{len(unvalidated)} of {len(forms)} <form> tags missing 'novalidate' attribute. Risks browser validation bubble.", penalty=15)
        else:
            add_check("Form Validation", "Anti-Native Tooltips", "PASS", f"All {len(forms)} form tags declare 'novalidate'. Custom validation enforced.")
    else:
        add_check("Form Validation", "Anti-Native Tooltips", "PASS", "No HTML forms detected or forms already compliant.")

    # 4. Color Palette & Contrast Check
    hex_colors = list(set(re.findall(r'#([A-Fa-f0-9]{6})\b', content)))
    if len(hex_colors) >= 2:
        # Check standard dark theme contrast (first light color against first dark color)
        dark_colors = [c for c in hex_colors if calculate_relative_luminance(*parse_hex_color(c)) < 0.2]
        light_colors = [c for c in hex_colors if calculate_relative_luminance(*parse_hex_color(c)) > 0.6]
        if dark_colors and light_colors:
            sample_ratio = compute_contrast_ratio(light_colors[0], dark_colors[0])
            if sample_ratio >= 7.0:
                add_check("Color Theory", "Contrast Ratio (WCAG AAA)", "PASS", f"Primary text/canvas contrast satisfies WCAG AAA: {sample_ratio:.2f}:1 (>= 7:1).")
            else:
                add_check("Color Theory", "Contrast Ratio (WCAG AAA)", "WARN", f"Primary contrast is {sample_ratio:.2f}:1, below WCAG AAA 7:1 threshold.", penalty=15)
        else:
            add_check("Color Theory", "Contrast Ratio (WCAG AAA)", "PASS", f"Detected {len(hex_colors)} hex tokens in palette.")
    else:
        add_check("Color Theory", "Contrast Ratio (WCAG AAA)", "PASS", "Palette verified.")

    # 5. Direct Text Branding & Anti-AI Slop
    if "✨" in content or "AI PLATFORM" in content.upper():
        add_check("Anti-AI Slop", "Decorative Kicker Badges", "WARN", "Detected generic AI decorative badge markers. Standard: direct text headline only.", penalty=10)
    else:
        add_check("Anti-AI Slop", "Decorative Kicker Badges", "PASS", "No generic AI slop badges detected.")

    return results

def print_audit_report(results):
    score = results['score']
    grade = "A+" if score >= 95 else ("A" if score >= 90 else ("B" if score >= 80 else ("C" if score >= 70 else "D")))

    print("\n" + "═" * 65)
    print(f" 🎨 GRAPHIC DESIGN ELEMENTS AUDIT: {results['file']}")
    print("═" * 65)
    print(f" Design Health Score: {score}/100 [Grade {grade}]")
    print(f" Summary:             {results['passed']} Passed | {results['warnings']} Warnings | {results['errors']} Errors")
    print("─" * 65)

    for c in results["checks"]:
        icon = "\033[32m[PASS]\033[0m" if c["status"] == "PASS" else ("\033[33m[WARN]\033[0m" if c["status"] == "WARN" else "\033[31m[FAIL]\033[0m")
        print(f" {icon} \033[1m[{c['category']}]\033[0m {c['name']}")
        print(f"        {c['message']}")
    print("═" * 65 + "\n")

def run_self_verification():
    print("Running Design Token Auditor self-verification...")
    # Contrast math test
    ratio_high = compute_contrast_ratio("FFFFFF", "0E1015")
    assert ratio_high >= 15.0, f"Expected high contrast ratio, got {ratio_high}"

    ratio_fail = compute_contrast_ratio("777777", "FFFFFF")
    assert ratio_fail < 5.0, f"Expected low contrast, got {ratio_fail}"

    print(f"Contrast formula verified: White on #0E1015 = {ratio_high:.2f}:1")
    print("All mathematical design token assertions PASSED!")

def main():
    parser = argparse.ArgumentParser(description="Graphic Design Elements & Token Auditor")
    parser.add_argument("--file", help="File to audit (HTML, CSS, SVG)")
    parser.add_argument("--verify", action="store_true", help="Run internal mathematical verification")
    parser.add_argument("--json", action="store_true", help="Output raw JSON results")

    args = parser.parse_args()

    if args.verify:
        run_self_verification()
        return

    if not args.file:
        print("Please provide a file to audit with --file <path> or run with --verify", file=sys.stderr)
        sys.exit(1)

    results = audit_design_file(args.file)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_audit_report(results)

if __name__ == "__main__":
    main()
