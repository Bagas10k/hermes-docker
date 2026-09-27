#!/usr/bin/env python3
"""Small deterministic color utilities for the color-intelligence skill.

Currently supports WCAG sRGB relative luminance and contrast ratio checks.
"""

import argparse
import re
import sys

HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")


def hex_to_rgb(value: str):
    m = HEX_RE.match(value.strip())
    if not m:
        raise ValueError(f"Expected 6-digit HEX such as #2563eb, got: {value!r}")
    h = m.group(1)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _linearize(channel_8bit: int) -> float:
    c = channel_8bit / 255.0
    # WCAG / sRGB transfer function threshold.
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    r, g, b = hex_to_rgb(hex_color)
    r_lin, g_lin, b_lin = map(_linearize, (r, g, b))
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(a: str, b: str) -> float:
    l1 = relative_luminance(a)
    l2 = relative_luminance(b)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def contrast_labels(ratio: float):
    return {
        "AA_normal": ratio >= 4.5,
        "AA_large": ratio >= 3.0,
        "AAA_normal": ratio >= 7.0,
        "AAA_large": ratio >= 4.5,
    }


def cmd_contrast(args):
    ratio = contrast_ratio(args.foreground, args.background)
    labels = contrast_labels(ratio)
    print(f"contrast_ratio={ratio:.2f}:1")
    for key, ok in labels.items():
        print(f"{key}={'PASS' if ok else 'FAIL'}")


def cmd_luminance(args):
    value = relative_luminance(args.color)
    print(f"relative_luminance={value:.6f}")


def build_parser():
    p = argparse.ArgumentParser(description="Color utilities for Hermes Color Intelligence")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("contrast", help="Calculate WCAG contrast ratio for two HEX colors")
    c.add_argument("foreground")
    c.add_argument("background")
    c.set_defaults(func=cmd_contrast)

    l = sub.add_parser("luminance", help="Calculate WCAG relative luminance for one HEX color")
    l.add_argument("color")
    l.set_defaults(func=cmd_luminance)
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
