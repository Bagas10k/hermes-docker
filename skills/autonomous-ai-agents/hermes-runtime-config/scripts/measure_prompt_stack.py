#!/usr/bin/env python3
"""Ukur beban instruksi nyata sebuah profil Hermes.

Menjawab keluhan "prompt banyak yang stack" dengan angka dari berkas nyata:
  1. biaya skills.auto_load (SKILL.md yang dibayar di setiap request)
  2. injeksi plugin pre_llm_call (batas atas dari literal di __init__.py)
  3. payload request asli dari request_dump (instructions + messages/input)
  4. okurensi marker injeksi: beban tetap sekali-per-sesi vs pertumbuhan per turn

Pakai: python3 measure_prompt_stack.py [nama-profil]
       python3 measure_prompt_stack.py --self-check
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from pathlib import Path

HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
MARKERS = ("AUTONOMOUS ORCHESTRATOR ACTIVE", "PONYTAIL MODE ACTIVE")


def config_path(profile: str) -> Path:
    if profile == "default":
        return HOME / "config.yaml"
    return HOME / "profiles" / profile / "config.yaml"


def _parse_auto_load(lines: list[str]) -> list[str]:
    """Ambil item di bawah blok `auto_load:` pada kedalaman lebih dalam."""
    names: list[str] = []
    for i, line in enumerate(lines):
        if line.strip() != "auto_load:":
            continue
        indent = len(line) - len(line.lstrip())
        for nxt in lines[i + 1 :]:
            if not nxt.strip():
                continue
            cur = len(nxt) - len(nxt.lstrip())
            item = re.match(r"^\s*-\s+(\S+)", nxt)
            if item and cur > indent:
                names.append(item.group(1))
            elif cur <= indent:
                break
        break
    return names


def auto_load_names(profile: str) -> list[str]:
    cfg = config_path(profile)
    if not cfg.exists():
        return []
    return _parse_auto_load(cfg.read_text(encoding="utf-8", errors="replace").splitlines())


def skill_size(name: str) -> tuple[int | None, str | None]:
    for base in (HOME / "skills", HOME / "plugins"):
        if not base.exists():
            continue
        for p in base.rglob("SKILL.md"):
            if p.parent.name == name:
                return p.stat().st_size, str(p)
    return None, None


def plugin_literals() -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    base = HOME / "plugins"
    if not base.exists():
        return out
    for f in sorted(base.glob("*/__init__.py")):
        text = f.read_text(encoding="utf-8", errors="replace")
        lits = re.findall(r'"""(.*?)"""', text, re.S) + re.findall(
            r'"((?:[^"\\]|\\.){120,})"', text
        )
        total = sum(len(x) for x in lits)
        if total:
            out.append((f.parent.name, total))
    return out


def load_body(path: str) -> dict:
    try:
        data = json.load(open(path, encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    req = data.get("request") or {}
    body = req.get("body") or data.get("body") or {}
    return body if isinstance(body, dict) else {}


def msg_text(m: object) -> str:
    if not isinstance(m, dict):
        return ""
    c = m.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "".join(x.get("text", "") for x in c if isinstance(x, dict))
    return ""


def messages_of(body: dict) -> list[dict]:
    """Dukung payload bentuk chat (`messages`) maupun Responses (`input`)."""
    for key in ("messages", "input"):
        v = body.get(key)
        if isinstance(v, list):
            return [m for m in v if isinstance(m, dict)]
    return []


def dump_paths() -> list[str]:
    return sorted(
        glob.glob(str(HOME / "sessions" / "request_dump_*.json")), key=os.path.getmtime
    )


def main() -> int:
    if "--self-check" in sys.argv:
        assert _parse_auto_load(
            ["skills:", "  auto_load:", "    - a", "    - b", "  creation_nudge_interval: 15"]
        ) == ["a", "b"]
        assert _parse_auto_load(["skills:", "  auto_load: [x]"]) == []
        assert messages_of({"input": [{"role": "user", "content": [{"text": "hi"}]}]})[
            0
        ]["role"] == "user"
        assert messages_of({"messages": [{"role": "user", "content": "hi"}]})[0]["content"] == "hi"
        assert messages_of({}) == []
        print("self-check OK")
        return 0

    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    profile = args[0] if args else "default"
    print(f"profil: {profile}  (config: {config_path(profile)})")

    names = auto_load_names(profile)
    print("\n[1] skills.auto_load — dibayar di setiap request")
    total = 0
    for n in names:
        size, path = skill_size(n)
        if size is None:
            print(f"    {n}: TIDAK DITEMUKAN (nama salah / skill belum ada)")
            continue
        total += size
        print(f"    {size:>7} char  {n}  ({path})")
    print(f"    total {total} char ≈ {total // 4} token")

    print("\n[2] injeksi plugin (jumlah literal panjang = batas atas teks tersuntik)")
    for name, size in plugin_literals():
        print(f"    {size:>7} char  {name}")

    dumps = dump_paths()
    if not dumps:
        print("\n[3] request_dump: tidak ada berkas di sessions/ — payload nyata belum terukur")
        return 0

    latest = dumps[-1]
    body = load_body(latest)
    msgs = messages_of(body)
    ins = body.get("instructions") or ""
    print(f"\n[3] payload terbaru: {os.path.basename(latest)}")
    print(f"    system instructions: {len(ins)} char")
    print(f"    pesan: {len(msgs)}")
    tot = len(ins)
    for m in msgs:
        t = msg_text(m)
        tot += len(t)
        tags = "".join(f"[{k.split()[0]}]" for k in MARKERS if k in t)
        print(f"      {str(m.get('role')):10s} {len(t):>7} char {tags}")
    print(f"    total {tot} char ≈ {tot // 4} token")

    scan = dumps[-40:]
    biggest = max(scan, key=lambda p: len(messages_of(load_body(p))))
    big_msgs = messages_of(load_body(biggest))
    print(f"\n[4] sesi terpanjang yang dipindai: {os.path.basename(biggest)} ({len(big_msgs)} pesan)")
    for k in MARKERS:
        n = sum(1 for m in big_msgs if k in msg_text(m))
        verdict = (
            "sekali per sesi → beban tetap, bukan per-turn"
            if n <= 1
            else f"{n}x → periksa logika skip plugin"
        )
        print(f"    '{k}': muncul di {n} pesan → {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
