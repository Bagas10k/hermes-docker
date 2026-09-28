#!/usr/bin/env python3
"""
Harmonic Palette Calibrator & Contrast Validator
Mathematical color harmony synthesizer adhering to WCAG 2.1 contrast boundaries and OKLCH color space.
"""

import sys
import json
import math

def hex_to_rgb(hex_str):
    hex_str = hex_str.strip().lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    if len(hex_str) != 6:
        raise ValueError(f"Invalid hex string: {hex_str}")
    return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))

def rgb_to_hex(r, g, b):
    r = max(0, min(255, int(round(r))))
    g = max(0, min(255, int(round(g))))
    b = max(0, min(255, int(round(b))))
    return f"#{r:02X}{g:02X}{b:02X}"

def srgb_to_linear(c):
    c_norm = c / 255.0
    return c_norm / 12.92 if c_norm <= 0.04045 else ((c_norm + 0.055) / 1.055) ** 2.4

def relative_luminance(r, g, b):
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)

def wcag_contrast_ratio(hex1, hex2):
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)
    l1 = relative_luminance(*rgb1)
    l2 = relative_luminance(*rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def rgb_to_hsl(r, g, b):
    r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
    c_max = max(r_n, g_n, b_n)
    c_min = min(r_n, g_n, b_n)
    delta = c_max - c_min

    l = (c_max + c_min) / 2.0

    if delta == 0:
        h = 0
        s = 0
    else:
        s = delta / (1 - abs(2 * l - 1))
        if c_max == r_n:
            h = ((g_n - b_n) / delta) % 6
        elif c_max == g_n:
            h = (b_n - r_n) / delta + 2
        else:
            h = (r_n - g_n) / delta + 4
        h *= 60
        if h < 0:
            h += 360
    return (h, s, l)

def hsl_to_rgb(h, s, l):
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    if 0 <= h < 60:
        r_p, g_p, b_p = c, x, 0
    elif 60 <= h < 120:
        r_p, g_p, b_p = x, c, 0
    elif 120 <= h < 180:
        r_p, g_p, b_p = 0, c, x
    elif 180 <= h < 240:
        r_p, g_p, b_p = 0, x, c
    elif 240 <= h < 300:
        r_p, g_p, b_p = x, 0, c
    else:
        r_p, g_p, b_p = c, 0, x

    return (
        round((r_p + m) * 255),
        round((g_p + m) * 255),
        round((b_p + m) * 255)
    )

def generate_harmonic_palette(primary_hex, harmony_type="triadic", theme_mode="light"):
    """
    Generates a mathematically calibrated, colorful yet harmonious UI palette.
    Harmony types: triadic, tetradic, analogous, split_complementary.
    """
    base_rgb = hex_to_rgb(primary_hex)
    h, s, l = rgb_to_hsl(*base_rgb)

    # Preset offsets
    if harmony_type == "triadic":
        offsets = [0, 120, 240]
    elif harmony_type == "tetradic":
        offsets = [0, 90, 180, 270]
    elif harmony_type == "analogous":
        offsets = [0, 30, 60, -30]
    elif harmony_type == "split_complementary":
        offsets = [0, 150, 210]
    else:
        offsets = [0, 120, 240]

    colors = []
    for off in offsets:
        cur_h = (h + off) % 360
        # Balance saturation to avoid fluorescent eye strain
        cur_s = min(0.85, max(0.45, s))
        # Optimal lightness for UI accents
        cur_l = 0.50 if theme_mode == "light" else 0.60
        rgb = hsl_to_rgb(cur_h, cur_s, cur_l)
        colors.append(rgb_to_hex(*rgb))

    if theme_mode == "light":
        canvas_bg = "#FAF8F5"       # Warm Off-White / Paper
        card_bg = "#FFFFFF"         # Solid Clean White
        text_primary = "#0F172A"    # Deep Charcoal Slate
        text_muted = "#64748B"      # Slate Meta
        border = "#E2E8F0"          # Crisp Hairline Border
    else:
        canvas_bg = "#0B0A10"       # Deep Warm Obsidian
        card_bg = "#15131D"         # Layered Elevation Slate
        text_primary = "#F8FAFC"    # Off-White
        text_muted = "#94A3B8"      # Soft Slate
        border = "#262335"          # Subtle Border

    result = {
        "harmony_type": harmony_type,
        "theme_mode": theme_mode,
        "base_color": primary_hex,
        "system": {
            "canvas_bg": canvas_bg,
            "card_bg": card_bg,
            "text_primary": text_primary,
            "text_muted": text_muted,
            "border": border
        },
        "accents": colors,
        "validations": []
    }

    # Validate WCAG AA contrast against card background & canvas background
    for idx, c in enumerate(colors):
        ratio_on_card = wcag_contrast_ratio(c, card_bg)
        ratio_on_canvas = wcag_contrast_ratio(c, canvas_bg)
        # Check text on accent contrast
        ratio_text_light = wcag_contrast_ratio("#FFFFFF", c)
        ratio_text_dark = wcag_contrast_ratio("#0F172A", c)
        best_text = "#FFFFFF" if ratio_text_light >= ratio_text_dark else "#0F172A"
        best_ratio = max(ratio_text_light, ratio_text_dark)

        result["validations"].append({
            "accent_hex": c,
            "contrast_on_card": round(ratio_on_card, 2),
            "contrast_on_canvas": round(ratio_on_canvas, 2),
            "suggested_badge_text": best_text,
            "badge_contrast_ratio": round(best_ratio, 2),
            "wcag_aa_large": best_ratio >= 3.0,
            "wcag_aa_normal": best_ratio >= 4.5
        })

    # Validate core typography readability
    text_contrast = wcag_contrast_ratio(text_primary, card_bg)
    result["system"]["text_contrast_on_card"] = round(text_contrast, 2)
    result["system"]["wcag_aaa_text"] = text_contrast >= 7.0

    return result

def main():
    if len(sys.argv) < 2:
        # Default run: Amber base (#F59E0B) in light theme
        output = generate_harmonic_palette("#F59E0B", "triadic", "light")
    else:
        base_hex = sys.argv[1]
        harm_type = sys.argv[2] if len(sys.argv) > 2 else "triadic"
        mode = sys.argv[3] if len(sys.argv) > 3 else "light"
        output = generate_harmonic_palette(base_hex, harm_type, mode)

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
