---
name: agent-zero-regression-fuzzing
description: Zero-regression differential fuzzing and invariant gate.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [differential-testing, fuzzing, zero-regression, invariant-gate, verification]
    related_skills: [agent-ast-mutation-patching, agent-crash-repro-synthesis, test-driven-development]
---

# Agent Zero-Regression Differential Fuzzing & Invariant Verification Gate

Sistem verifikasi diferensial pra-rilis deterministik untuk membandingkan luaran sistem lama $f_{\text{old}}(x)$ dan versi baru $f_{\text{new}}(x)$ di bawah korpus fuzzing terarah. Mencegah regresi perilaku tersembunyi pada pembaruan kode otonom.

## When to Use
- Verifikasi pra-merge atau pra-commit perbaikan bug otomatis untuk memastikan fungsi lain tidak terganggu.
- Deteksi regresi semantik tersembunyi (*unintended side-effects*) pada fungsi yang dimutasi atau direfaktor.
- Evaluasi invarian sistem ketat $g(x) \le 0$ (misalnya jaminan tipe, pembatasan nilai non-null, kepatuhan batas latensi).
- Pemisahan divergensi perilaku yang disengaja (*intentional bugfix*) vs regresi liar (*accidental drift*).

Don't use for:
- Pengujian tampilan antarmuka visual murni (gunakan `e2e-browser-testing`).
- Pengujian unit dasar baris tunggal tanpa mutasi fungsi (gunakan `test-driven-development`).

## Prerequisites
- Python 3.9+ dengan pustaka standar `inspect`, `random`, `math`, `time`.
- Tidak memerlukan dependensi pihak ketiga berat.

## How to Run
Jalankan pengujian mesin verifikasi diferensial:
```bash
python3 ~/.hermes/skills/software-development/agent-zero-regression-fuzzing/scripts/differential_fuzz_engine.py --test
```

## Quick Reference
```python
from differential_fuzz_engine import DifferentialFuzzEngine

engine = DifferentialFuzzEngine(seed=42)
corpus = engine.generate_typed_inputs(sig, count=50)

# Verifikasi fungsi lama vs baru
results = engine.run_differential(
    f_old=original_fn,
    f_new=patched_fn,
    corpus=corpus,
    target_invariant=lambda args, outcome: outcome[1] is None,  # no unhandled exception
    expected_patch_scope=lambda args: args[0] == target_edge_case # intended divergence scope
)

assert results["status"] == "PASS"
```

## Procedure

### 1. Ekstraksi Kontrak & Sintesis Korpus Uji
Tentukan tanda tangan fungsi ($f_{\text{old}}$) dan buat korpus kasus batas (*boundary cases*):
- Angka ekstrem ($0, -1, 1, 2^{31}-1, \text{NaN}, \pm\infty$).
- String pembatas (string kosong, whitespace, newline, null byte, unicode).
- Koleksi kosong vs beranak (`[]`, `[None]`, `{}`), dan tipe data gabungan.

### 2. Formulasi Invarian & Lingkup Patch (3 Mindsets)
- **Mekanistik-Kausal**: Petakan fungsi $y = f(x) + \epsilon$. Tetapkan batas invarian $g(x) \le 0$ yang wajib dipenuhi oleh seluruh $x$.
- **Bayesian**: Tetapkan hipotesis divergensi $P(\text{Diff} \mid \text{Scope})$. Setiap divergensi di luar lingkup perbaikan yang disengaja bernilai regresi ($P(\text{Regression}) = 1.0$).
- **Desain Sistem**: Hitung delta performa (speedup ratio) dan pastikan patch tidak memicu regresi latensi tail $p95$.

### 3. Eksekusi Pengujian Diferensial Paralel
Eksekusi $f_{\text{old}}(x_i)$ dan $f_{\text{new}}(x_i)$ secara deterministik untuk setiap $x_i \in \text{Corpus}$. Catat waktu eksekusi dalam nanodetik dan periksa apakah hasil ekuivalen atau termasuk dalam pengecualian lingkup patch.

### 4. Evaluasi Gerbang Kelulusan (Gate Decision)
- Jika ditemukan $\ge 1$ regresi di luar lingkup yang disengaja: Status **FAIL**. Patch ditolak dan dikembalikan ke siklus perbaikan kode.
- Jika ditemukan $\ge 1$ pelanggaran invarian: Status **FAIL**.
- Jika 100% korpus identik atau divergen sesuai niat perbaikan: Status **PASS**.

## Pitfalls
- **Floating Point NaN Equivalence Trap**: Di Python standar, `float('nan') == float('nan')` menghasilkan `False`. Engine fuzzing wajib menangani `math.isnan()` secara eksplisit agar kasus batas numerik tidak memicu false regression.
- **Flaky Seed Non-Determinism**: Korpus fuzzing tanpa penyemaian seed acak deterministik akan memicu hasil fluktuatif antar-run. Wajib sematkan seed eksplisit.
- **Unbounded Recursion / Deep Structure**: Fuzzing struktur nested tak terbatas dapat memicu `RecursionError` pada generator. Batasi kedalaman nested structures maksimal level 3.

## Verification
- Jalankan suite unit-test mandiri:
  `python3 ~/.hermes/skills/software-development/agent-zero-regression-fuzzing/scripts/differential_fuzz_engine.py --test`
- Pastikan seluruh 4 skenario (Ekuivalensi Identik, Deteksi Regresi, Intentional Bugfix Scope, dan Invariant Gate) berstatus `PASSED` dengan status keseluruhan `all_passed: true`.
