#!/usr/bin/env python3
"""Audit UI spacing values against a configurable base unit.

Examples:
  python spacing_audit.py scale --base 4 --max 96
  python spacing_audit.py audit 8 16 23 32 47 --base 4
  python spacing_audit.py suggest 19 --base 4
"""

import argparse
import math


def nearest_multiple(value: float, base: float) -> float:
    return round(value / base) * base


def clean_number(value: float):
    if abs(value - round(value)) < 1e-9:
        return int(round(value))
    return round(value, 2)


def cmd_scale(args):
    value = 0.0
    vals = []
    while value <= args.max + 1e-9:
        vals.append(clean_number(value))
        value += args.base
    print("Base scale:", ", ".join(map(str, vals)))


def cmd_suggest(args):
    nearest = nearest_multiple(args.value, args.base)
    delta = args.value - nearest
    print(f"Input: {clean_number(args.value)}px")
    print(f"Nearest {clean_number(args.base)}px-grid token: {clean_number(nearest)}px")
    print(f"Delta: {clean_number(delta)}px")


def cmd_audit(args):
    print(f"Audit against base unit {clean_number(args.base)}px")
    print("value\tnearest\tdelta\tstatus")
    exceptions = 0
    for value in args.values:
        nearest = nearest_multiple(value, args.base)
        delta = value - nearest
        ok = math.isclose(delta, 0.0, abs_tol=args.tolerance)
        status = "on-scale" if ok else "review"
        if not ok:
            exceptions += 1
        print(
            f"{clean_number(value)}\t{clean_number(nearest)}\t"
            f"{clean_number(delta)}\t{status}"
        )
    print(f"\nValues reviewed: {len(args.values)}")
    print(f"Off-scale values: {exceptions}")
    if exceptions:
        print("Off-scale values are not automatically wrong. Confirm whether each is an intentional optical/platform exception.")


def build_parser():
    parser = argparse.ArgumentParser(description="UI spacing scale helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_scale = sub.add_parser("scale", help="Generate a spacing scale")
    p_scale.add_argument("--base", type=float, default=4.0)
    p_scale.add_argument("--max", type=float, default=96.0)
    p_scale.set_defaults(func=cmd_scale)

    p_suggest = sub.add_parser("suggest", help="Suggest nearest spacing token")
    p_suggest.add_argument("value", type=float)
    p_suggest.add_argument("--base", type=float, default=4.0)
    p_suggest.set_defaults(func=cmd_suggest)

    p_audit = sub.add_parser("audit", help="Audit multiple spacing values")
    p_audit.add_argument("values", nargs="+", type=float)
    p_audit.add_argument("--base", type=float, default=4.0)
    p_audit.add_argument("--tolerance", type=float, default=0.01)
    p_audit.set_defaults(func=cmd_audit)

    return parser


def main():
    args = build_parser().parse_args()
    if args.base <= 0:
        raise SystemExit("--base must be greater than zero")
    args.func(args)


if __name__ == "__main__":
    main()
