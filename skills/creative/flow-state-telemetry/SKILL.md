---
name: flow-state-telemetry
description: "Flow state telemetry engine and vibe coding HUD metrics."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [flow-state, telemetry, vibe-coding, wpm, metrics, hud, auto-sleep]
    related_skills: [retro-terminal-hud, ambient-sonification-flow, dynamic-canvas-backdrop]
---

# Flow State Telemetry: Engine Metrik & HUD Kognitif Vibe Coding

Skill ini menyediakan engine telemetri deterministik untuk memantau, mengukur, dan memvisualisasikan kondisi *flow-state* pengembang selama sesi vibe coding. Mengukur densitas ketikan (WPM bergerak), frekuensi eksekusi aksi, streak fokus aktif, serta mengendalikan adaptasi visual dan transisi auto-sleep 0% CPU saat idle.

## When to Use
- Mengukur ritme dan produktivitas koding secara non-intrusif tanpa membebani memori/CPU.
- Mengintegrasikan indikator status kognitif (IDLE, CRUISE, FLOW, HYPERFLOW) ke dalam HUD editor/web preview.
- Memicu perubahan tema dinamis atau intensitas ambient sonification berdasarkan tingkat konsentrasi pengembang.
- Mencegah kebocoran resource dengan auto-sleep instan setelah 45 detik inaktivitas.

## Prerequisites
- Browser modern berkemampuan Web Audio / Canvas API (opsional untuk visualizer).
- Node.js atau Python 3.10+ untuk daemon telemetri lokal.

## Quick Reference
- Jalankan simulator HUD lokal: `python3 ~/.hermes/skills/creative/flow-state-telemetry/scripts/flow_engine.py`
- Ekspor template HUD HTML taktil: salin modul dari `references/flow-hud-template.html`.

## Procedure

1. **Inisialisasi Ring Buffer Aktivitas**:
   - Catat stempel waktu ketikan dan aksi tools dalam sliding window 60 detik.
   - Hitung WPM deterministik: `wpm = count(keystrokes_60s) / 5.0`.
   - Hitung densitas aktivitas kognitif: `activity_density = wpm + (actions_60s * 4.0)`.

2. **Evaluasi Jenjang Kognitif (Tier State Machine)**:
   - `IDLE`: `activity_density < 8.0` atau idle > 45 detik (auto-sleep aktif, 0% CPU).
   - `CRUISE`: `8.0 <= activity_density < 25.0` (ritme stabil penulisan kode awal).
   - `FLOW`: `25.0 <= activity_density < 50.0` (kondisi konsentrasi tinggi terpadu).
   - `HYPERFLOW`: `activity_density >= 50.0` (refactoring cepat dan eksekusi serentak).

3. **Smoothing & Integrasi Taktil**:
   - Terapkan interpolasi linier (LERP) pada transisi parameter intensitas: `val += (target - val) * 0.2`.
   - Tampilkan chip metrik monokrom berpresisi tinggi (WPM, Streak Time, State Badge).
   - Patuhi kebijakan Nol Emoji: gunakan lencana teks mono dan dot indikator SVG.

## Pitfalls
- **High-Frequency Polling Trap**: Dilarang memicu re-render canvas/DOM pada setiap event `keydown`. Gunakan debounce atau throttling berbasis `requestAnimationFrame` (16.6ms).
- **CPU Waste on Idle**: Jika tidak ada aktivitas ketikan selama 45 detik, loop animasi WAJIB dihentikan (`cancelAnimationFrame`) untuk mencapai 0% konsumsi CPU.
- **Inaccurate WPM Spikes**: Jangan menghitung WPM dari delta 2 tombol berturut-turut karena memicu pembagian nol dan lonjakan nilai fiktif; gunakan sliding window rata-rata terbobot.

## Verification
- Validasi logika state machine, sliding window, dan batas auto-sleep via skrip unit test `flow_engine.py`.
