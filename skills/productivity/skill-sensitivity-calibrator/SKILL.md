---
name: skill-sensitivity-calibrator
description: "Use when routing skills. Calibrates sensitivity thresholds."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [skills, routing, intent, sensitivity, threshold, optimization]
---

# Skill Sensitivity Calibrator & Intent Router

Sistem pengatur sensitivitas pemanggilan skill untuk 241+ pustaka kemampuan Hermes. Mencegah kegagalan pengenalan skill (*under-triggering*) dan pemborosan jendela konteks (*over-triggering*) akibat pemanggilan skill yang tidak relevan.

## 3 Ambang Batas Sensitivitas (Sensitivity Tiers)

1. **STRICT (ambang 0.65)**:
   - Gunakan untuk kueri pendek, sederhana, atau perintah deterministik.
   - Hanya memicu skill jika terdapat kecocokan nama eksplisit atau pemicu klausa `Use when` yang sangat spesifik.
   - Menghemat token secara maksimal.

2. **BALANCED (ambang 0.40)**:
   - Pengaturan bawaan (*default production*).
   - Menyeimbangkan presisi dan recall dengan menyerap sinonim dwibahasa (Indonesia <-> English).
   - Cocok untuk instruksi pengembangan sistem harian.

3. **SENSITIVE (ambang 0.25)**:
   - Gunakan saat merencanakan arsitektur besar, penugasan ambigu, atau tugas riset lintas ranah.
   - Mengaktifkan penelusuran konsep semantik sekunder di dalam badan dokumen panduan.

## Aturan Penalti Negatif (Anti-Conflict Filter)

1. **Konteks Headless/Terminal/Daemon**:
   - Jika perintah menyangkut terminal, CLI, PM2, daemon, atau SSH, berikan penalti -0.40 pada skill grafis/3D/kanvas (p5js, threejs, manim, genjutsu).
   - Alasan: Lingkungan server murni tidak boleh dibebani dependensi visual.

2. **Konteks Backend/Database**:
   - Jika perintah menyangkut API, database, skema, atau query, berikan penalti -0.50 pada skill audio/musik (binaural soundscape, music generation).

## Cara Penggunaan Cepat

Jalankan router di terminal atau panggil via Python:
```bash
skill-route "tata letak dasbor modern bento grid"
skill-route -t strict "fix crash nodejs"
skill-route -t sensitive "desain ekosistem otonom multi-agent"
```
