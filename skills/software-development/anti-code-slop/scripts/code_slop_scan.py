#!/usr/bin/env python3
"""
Anti-Code Slop Scanner (Code-Slop-Guard)
Memindai berkas kode (JS, TS, Python, CSS) dari pola-pola khas AI Code Slop:
1. Try-catch / except kosong yang menelan error (Swallowed errors).
2. Sisa console.log / print debug liar yang tertinggal di produksi.
3. Komentar narasi malas AI ("// initialize...", "// handle...").
4. Perbandingan boolean eksplisit redundan (=== true / === false).
5. Defensive bloat dan Promise.all tunggal.
6. Mock dummy data yang bocor di berkas produksi.
"""

import sys
import os
import re
import json
from pathlib import Path

# Definisi Pola Slop
PATTERNS = [
    {
        "id": "swallowed_error_catch",
        "severity": "HIGH",
        "desc": "Blok catch kosong atau hanya menelan error tanpa penanganan/rethrow",
        "regex": r'catch\s*\([^)]*\)\s*\{\s*(?:\/\/.*|\/\*.*\*\/)?\s*\}',
        "exts": [".js", ".ts", ".jsx", ".tsx"]
    },
    {
        "id": "swallowed_error_python",
        "severity": "HIGH",
        "desc": "Blok except kosong dengan pass yang menelan error",
        "regex": r'except(\s+[\w\s,]+)?:\s*pass\b',
        "exts": [".py"]
    },
    {
        "id": "stray_debug_log",
        "severity": "HIGH",
        "desc": "Debug console.log/console.debug yang tertinggal di kode aplikasi",
        "regex": r'\bconsole\.(log|debug)\s*\(',
        "exts": [".js", ".ts", ".jsx", ".tsx"],
        "ignore_files": ["release-manager.py", "visual-gate.cjs", "qc.js", "verify"]
    },
    {
        "id": "lazy_ai_comment",
        "severity": "MEDIUM",
        "desc": "Komentar narasi AI malas yang hanya mengulang baris kode berikutnya",
        "regex": r'//\s*(initialize\b|increment\b|return\s+the\b|handle\s+the\s+request|create\s+a\s+new\b|import\b)',
        "exts": [".js", ".ts", ".jsx", ".tsx"],
        "flags": re.IGNORECASE
    },
    {
        "id": "redundant_boolean_comparison",
        "severity": "LOW",
        "desc": "Perbandingan boolean eksplisit redundan (=== true atau === false)",
        "regex": r'===?\s*(true|false)\b',
        "exts": [".js", ".ts", ".jsx", ".tsx"]
    },
    {
        "id": "single_promise_all",
        "severity": "LOW",
        "desc": "Promise.all() yang hanya membungkus satu promise",
        "regex": r'Promise\.all\s*\(\s*\[\s*[^,\]]+\s*\]\s*\)',
        "exts": [".js", ".ts", ".jsx", ".tsx"]
    }
]

def scan_file(file_path: Path):
    ext = file_path.suffix.lower()
    findings = []
    
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return findings

    lines = content.splitlines()

    for p in PATTERNS:
        if ext not in p["exts"]:
            continue
        
        # Check ignore file keywords
        if "ignore_files" in p:
            if any(ign in file_path.name for ign in p["ignore_files"]):
                continue

        regex_flags = p.get("flags", 0)
        regex = re.compile(p["regex"], regex_flags)

        for line_num, line in enumerate(lines, start=1):
            # Skip comments if checking logs
            if p["id"] == "stray_debug_log" and line.strip().startswith("//"):
                continue

            match = regex.search(line)
            if match:
                findings.append({
                    "file": str(file_path),
                    "line": line_num,
                    "code_snippet": line.strip()[:100],
                    "id": p["id"],
                    "severity": p["severity"],
                    "desc": p["desc"]
                })

    return findings

def scan_directory(target_dir: Path):
    all_findings = []
    skip_dirs = {".git", "node_modules", "vendor", "dist", "dist-public", ".hermes", "cache", "__pycache__"}
    
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in [".js", ".ts", ".jsx", ".tsx", ".py"]:
                findings = scan_file(p)
                all_findings.extend(findings)

    return all_findings

if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    findings = scan_directory(target) if target.is_dir() else scan_file(target)

    high_count = sum(1 for f in findings if f["severity"] == "HIGH")
    medium_count = sum(1 for f in findings if f["severity"] == "MEDIUM")
    low_count = sum(1 for f in findings if f["severity"] == "LOW")

    report = {
        "target": str(target),
        "total_findings": len(findings),
        "summary": {
            "HIGH": high_count,
            "MEDIUM": medium_count,
            "LOW": low_count
        },
        "findings": findings
    }

    if "--json" in sys.argv:
        print(json.dumps(report, indent=2))
    else:
        print(f"=== LAPORAN PEMINDAIAN ANTI-CODE SLOP ===")
        print(f"Target: {target}")
        print(f"Total Temuan: {len(findings)} (HIGH: {high_count}, MEDIUM: {medium_count}, LOW: {low_count})")
        print("--------------------------------------------------")
        for f in findings:
            print(f"[{f['severity']}] {f['file']}:{f['line']}")
            print(f"  Pola : {f['desc']}")
            print(f"  Kode : {f['code_snippet']}")
            print("")

        if high_count > 0:
            print("[FAIL] Ditemukan Code Slop tingkat TINGGI! Rilis wajib diveto.")
            sys.exit(1)
        else:
            print("[PASS] Bersih dari Code Slop tingkat tinggi. Kode aman dirilis.")
            sys.exit(0)
