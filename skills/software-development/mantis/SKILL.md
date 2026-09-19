---
name: mantis
description: "Google Mantis: Autonomous security review, vulnerability reproduction, threat modeling, and patching suite."
version: 1.0.0
author: Google & Hermes
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mantis, security, vulnerability, audit, patch, threat-model, google]
---

# Google Mantis: Autonomous Security Review Suite

Mantis adalah rangkaian toolkit audit dan review keamanan otonom resmi dari Google yang dirancang khusus untuk AI Coding Agent.

## Modul Kemampuan Utama

1. **Analisis & Threat Modeling**:
   - `/mantis-threat-model`: Membangun model ancaman dan permukaan serangan arsitektur.
   - `/mantis-architecture`: Memetakan dependensi komponen kritis.
   - `/mantis-structural-index`: Mengindeks aliran kontrol dan jalur data sensitif.

2. **Deteksi & Review**:
   - `/mantis-review`: Memvalidasi temuan celah keamanan terhadap kode sumber nyata dan menyaring false positives.
   - `/mantis-critic`: Mengevaluasi ketajaman temuan secara kritis.
   - `/mantis-dedupe`: Mengelompokkan dan menduplikasi temuan yang setara.

3. **Reproduksi & Patching**:
   - `/mantis-reproduce`: Menghasilkan script reproduksi / proof-of-concept (PoC) otomatis di lingkungan sandbox.
   - `/mantis-patch`: Merancang dan menerapkan patch perbaikan kode terkecil yang tuntas.
   - `/mantis-report`: Menyusun laporan audit keamanan berstandar industri.
