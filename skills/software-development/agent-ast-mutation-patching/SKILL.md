---
name: agent-ast-mutation-patching
description: Runtime AST mutation and structural code patching.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ast, code-mutation, structural-patching, self-healing, program-synthesis]
    related_skills: [agent-crash-repro-synthesis, test-driven-development, systematic-debugging]
---

# Agent AST Mutation & Structural Patching

Sistem manipulasi pohon sintaksis abstrak (Abstract Syntax Tree / AST) deterministik untuk perbaikan kode otonom tanpa kerapuhan regex dan tanpa resintesis seluruh berkas sumber.

## When to Use
- Perbaikan bug fungsional terisolasi pada fungsi, method, atau ekspresi panggilan tertentu.
- Injeksi defensive pre-condition checks (guard clauses) di awal fungsi untuk menangani exception.
- Penggantian argumen fungsi pada call-site secara presisi tanpa salah sasaran ke variabel bertranskrip serupa.
- Verifikasi kompilasi sintaksis pra-commit untuk menjamin zero-broken-syntax.

Don't use for:
- Perubahan format teks sederhana/komentar murni (gunakan `patch`).
- Penambahan file baru atau scaffold awal (gunakan `write_file`).

## Prerequisites
- Python 3.9+ dengan modul bawaan `ast`, `compile`, dan `difflib`.
- Tidak memerlukan pustaka pihak ketiga eksternal.

## How to Run
Jalankan modul CLI AST Mutation Engine:
```bash
python3 ~/.hermes/skills/software-development/agent-ast-mutation-patching/scripts/ast_mutation_engine.py --test
```

## Quick Reference
```python
from ast_mutation_engine import (
    inject_guard_statement,
    mutate_call_argument,
    mutate_function,
    validate_ast_invariants
)

# 1. Injeksi guard clause
res = inject_guard_statement(code, "calculate", "if val is None: return 0")

# 2. Mutasi argumen pemanggilan fungsi
res = mutate_call_argument(code, "connect", arg_idx=1, new_arg_val="timeout=30")

# 3. Ganti seluruh implementasi fungsi
res = mutate_function(code, "target_func", new_func_code_str)

# 4. Validasi invarian statis
valid, err = validate_ast_invariants(mutated_code)
```

## Procedure
1. **Target Identification**: Identifikasi node fungsi atau call-site target dari stack trace kegagalan.
2. **Structural Mutation**: Panggil transformer AST yang sesuai (`inject_guard_statement`, `mutate_call_argument`, atau `mutate_function`).
3. **Static Invariant Gate**: Uji hasil unparse dengan `validate_ast_invariants` untuk memastikan pohon valid dan terkompilasi.
4. **Diff Verification**: Evaluasi diff terpadu untuk memastikan blast radius terbatas murni pada target.
5. **Execution Verification**: Jalankan reproducer test untuk memverifikasi bug terselesaikan tanpa efek samping.

## Pitfalls
- **Docstring Relocation**: Injeksi statement pada head fungsi wajib diletakkan setelah modul/function docstring agar tidak merusak metadata dokumentasi.
- **Location Fixup**: Node baru hasil sintesis wajib dilewatkan melalui `ast.fix_missing_locations` dan `ast.copy_location` sebelum unparse untuk mencegah kompilasi tanpa line number.
- **Async Function Scope**: Pastikan transformer mengenali `AsyncFunctionDef` setara dengan `FunctionDef` standar.

## Verification
- Invarian statis lolos kompilasi tanpa `SyntaxError`.
- Diff terpadu menunjukkan mutasi presisi hanya pada node target.
- Script engine self-test menghasilkan status exit code 0.
