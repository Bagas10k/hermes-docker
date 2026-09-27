#!/usr/bin/env python3
"""Generate practical typography scale candidates.

This script generates candidate sizes from a base size and ratio, then optionally
prints CSS custom properties. Generated values are starting points, not final
visual decisions.
"""

import argparse


def build_scale(base: float, ratio: float, down: int, up: int):
    values = []
    for step in range(-down, up + 1):
        raw = base * (ratio ** step)
        values.append((step, raw))
    return values


def label_for(step: int) -> str:
    if step == 0:
        return "body"
    if step < 0:
        return f"sm{abs(step)}"
    return f"lg{step}"


def main():
    parser = argparse.ArgumentParser(description="Generate a modular typography scale candidate.")
    parser.add_argument("--base", type=float, default=16.0, help="Base font size in px")
    parser.add_argument("--ratio", type=float, default=1.2, help="Scale ratio")
    parser.add_argument("--down", type=int, default=2, help="Steps below base")
    parser.add_argument("--up", type=int, default=5, help="Steps above base")
    parser.add_argument("--round", type=float, default=1.0, dest="round_to", help="Round to this px increment")
    parser.add_argument("--css", action="store_true", help="Output CSS variables")
    args = parser.parse_args()

    if args.base <= 0 or args.ratio <= 1 or args.round_to <= 0:
        raise SystemExit("base and round must be > 0; ratio must be > 1")

    scale = build_scale(args.base, args.ratio, args.down, args.up)

    def rounded(value: float) -> float:
        return round(value / args.round_to) * args.round_to

    if args.css:
        print(":root {")
        for step, raw in scale:
            value = rounded(raw)
            label = label_for(step)
            number = int(value) if value.is_integer() else value
            print(f"  --text-{label}: {number}px;")
        print("}")
    else:
        print("step\trole\traw_px\trounded_px")
        for step, raw in scale:
            value = rounded(raw)
            print(f"{step}\t{label_for(step)}\t{raw:.3f}\t{value:g}")


if __name__ == "__main__":
    main()
