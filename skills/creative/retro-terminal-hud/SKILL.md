---
name: retro-terminal-hud
description: "Build retro terminal HUDs and cyber cockpits with zero slop."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [retro, terminal, hud, tui, cockpit, vibe-coding, zero-emoji, audio-synth]
    related_skills: [ambient-sonification-flow, live-sandbox-hot-preview, tactile-microinteraction-studio]
---

# Retro Terminal HUD & Cyber Cockpit Skill

Merancang dan menyintesis antarmuka telemetri retro-futuristik, Cyber HUD, dashboard TUI terminal anti-kedip (*zero-flicker*), dan artefak visual CRT monitor untuk meningkatkan vibe koding secara instan.

## When to Use

- Membangun antarmuka telemetri sistem atau dashboard pemantau status agen yang seru (*fun*), taktil, dan berestetika cyber-cockpit.
- Merancang TUI CLI berbasis kotak garis ANSI presisi tanpa pustaka eksternal yang berat.
- Mengonversi data metrik backend menjadi artefak web CRT scanlines dengan synth audio retro terintegrasi.
- **Don't use for:** Dokumen teks sastra biasa, blog korporat kaku, atau halaman formulir input transaksional biasa.

## Prerequisites

- Python 3 standard library (zero external packages required).
- Peramban modern dengan Web Audio API untuk rendering artefak HTML.
- Kepatuhan mutlak: **Zero Emoji Policy** (100% menggunakan karakter garis Unicode box-drawing atau ikon SVG garis).

## Quick Reference

```bash
# Menjalankan synthesizer TUI di terminal
python3 ~/.hermes/skills/creative/retro-terminal-hud/scripts/retro_hud.py tui

# Menghasilkan artefak HTML Cyber HUD mandiri
python3 ~/.hermes/skills/creative/retro-terminal-hud/scripts/retro_hud.py html /tmp/cockpit.html
```

## Procedure

1. **Definisikan Kontrak Data Metrik**:
   - Petakan metrik inti: CPU, RAM, Network Throughput, Pipeline Latency, dan Status Operasional.
2. **Kalkulasi Lebar Visual ANSI (Zero Offset Drift)**:
   - Wajib menyaring sequence ANSI sebelum menghitung padding kolom tabel agar garis tepi kotak (`│`, `┌`, `└`) tidak bergeser secara asimetris.
3. **Penyusunan Efek Visual CRT (Web HUD Artifact)**:
   - Pasang lapisan scanlines 4px linier transparan di CSS body.
   - Tambahkan pendaran cahaya phosphor glow (`text-shadow` dan `box-shadow` dengan aksen Cyan `#0ea5e9` atau Amber `#f59e0b`).
4. **Integrasi Audio Prosedural**:
   - Suntikkan nada beeps/blips singkat (sine wave oscillator 880Hz -> 1760Hz dengan exponential decay) pada interaksi tombol atau perubahan status.

## Pitfalls

- **Flicker Trap**: Menggunakan `\033[2J` berulang-ulang di loop TUI memicu kedipan hebat pada layar. Gunakan `\033[H` (Cursor Home) untuk overdraw atomik.
- **Emoji Leak**: Menyematkan emoji ke dalam antarmuka cyber HUD merusak estetika retro enterprise dan memicu layout drift font monospace.
- **Pointer Blocking**: Lapisan overlay CRT `::before` tanpa `pointer-events: none` akan memblokir interaksi klik mouse pada seluruh elemen antarmuka di bawahnya.

## Verification

- Jalankan skrip pembantu `retro_hud.py tui` di terminal dan pastikan batas garis tepi kotak lurus simetris.
- Periksa berkas HTML yang dihasilkan dengan peramban headless atau browser_exec untuk memverifikasi ketiadaan horizontal scroll dan memastikan elemen scanline render secara presisi.
