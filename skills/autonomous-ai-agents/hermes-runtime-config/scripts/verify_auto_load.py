#!/usr/bin/env python3
"""Verify skills.auto_load: config readable, skills renderable, cost reported.

Run from the hermes-agent tree so `agent.skill_commands` imports resolve:
    cd ~/.hermes/hermes-agent && python3 <skill_dir>/scripts/verify_auto_load.py

Exit 0 = every configured name loaded (or auto_load intentionally empty).
Exit 1 = missing names or import failure.
"""
import sys


def main() -> int:
    try:
        from agent.skill_commands import (
            build_auto_load_prompt,
            resolve_auto_load_skills,
        )
    except Exception as exc:  # wrong cwd or broken install
        print(f"FAIL import: {exc}")
        return 1

    names = resolve_auto_load_skills()
    print(f"configured: {names}")
    if not names:
        print("OK (auto_load empty - nothing is always-on)")
        return 0

    text, loaded, missing = build_auto_load_prompt()
    print(f"loaded: {loaded}")
    print(f"missing: {missing}")
    print(f"chars: {len(text)} (~{len(text) // 4} tokens per request)")

    if missing:
        print(f"FAIL missing skills: {missing}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
