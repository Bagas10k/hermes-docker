---
name: vision-agent-computer-interface
description: "Vision-Language ACI hybrid grounding and visual action loop."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [computer-use, aci, vision-language, accessibility-tree, hybrid-grounding, browser-agents]
    related_skills: [computer-use, e2e-browser-testing, autonomous-orchestrator]
---

# Vision-Language Agent-Computer Interface (ACI) & Hybrid Grounding

Skill rekayasa antarmuka aksi komputer agen otonom generasi baru yang menggabungkan pembacaan Accessibility DOM Tree (AXTree) dengan deteksi koordinat visual (*Hybrid Grounding*). Dirancang untuk menembus kelemahan selector DOM dinamis (Tailwind/CSS-in-JS acak, Canvas rendering, Shadow DOM) serta meminimalkan latensi per siklus aksi ke batas sub-detik.

## When to Use

- Mengotomasi tugas GUI desktop atau browser yang memiliki elemen dinamis tanpa ID/class stabil.
- Menjalankan Computer Use berbasis koordinat $(x, y)$ dengan verifikasi ganda agar klik tidak meleset.
- Menangani aplikasi berbasis WebGL/Canvas di mana inspeksi DOM biasa gagal menemukan node teks atau tombol.
- Membutuhkan siklus aksi GUI cepat dengan fallback bertingkat: AXTree -> Visual Coordinate -> Keyboard Shortcut.
- **Don't use for:** Operasi data backend murni tanpa GUI atau scraping API headless standar.

## Prerequisites

- Python 3.10+ (stdlib `json`, `math`, `re`, `pathlib`).
- Akses Chrome DevTools Protocol (CDP) atau antarmuka OS windowing (`xdotool`, `pyautogui`, atau `cua-driver`).
- Model Vision-Language multimodal (seperti Claude 3.5 Sonnet Computer Use, Gemini 2.0/Pro Vision, atau local UI detector).

## How to Run

Uji keselarasan koordinat target menggunakan script hybrid grounding:
```bash
python3 ~/.hermes/skills/autonomous-ai-agents/vision-agent-computer-interface/scripts/hybrid_grounding_engine.py --intent "Submit Order" --viewport 1920x1080
```

## Quick Reference

- **AXTree Extraction:** Ambil subtree elemen interaktif (`role in [button, link, input, combobox]`).
- **Normalized Coordinates:** Konversi koordinat visual ke float $[0.0, 1.0]$ lalu petakan ke resolusi fisik display.
- **Symmetric Jaccard Overlap:** Ukur IoU antara bounding box DOM dan bounding box deteksi visual:
  $$\text{IoU} = \frac{\text{Area}(B_{\text{AX}} \cap B_{\text{Vis}})}{\text{Area}(B_{\text{AX}} \cup B_{\text{Vis}})}$$
- **Confidence Gate:** Eksekusi klik langsung jika $P(\text{Match}) \ge 0.85$; lakukan visual zoom/crop jika $0.50 \le P < 0.85$; batalkan jika $< 0.50$.

## Procedure

1. **Snapshot & State Ingestion:**
   - Tangkap screenshot layar terkini dan ambil dump accessibility tree via CDP `Accessibility.getFullAXTree`.
   - Normalisasi dimensi viewport fisik ($W \times H$).
2. **Deterministic Pre-Filter (AX Tree Prior):**
   - Saring ribuan node generik; pertahankan hanya node dengan status `clickable`, `focusable`, atau teks semantik relevan.
   - Ekstrak box model fisik tiap elemen via `DOM.getBoxModel`.
3. **Multimodal Visual Alignment:**
   - Petakan target intent ke visual bounding box.
   - Hitung jarak Euclidean pusat elemen: $d = \sqrt{(x_{\text{AX}} - x_{\text{Vis}})^2 + (y_{\text{AX}} - y_{\text{Vis}})^2}$.
   - Padukan skor teks semantik ($0.60$) dan kedekatan spasial visual ($0.40$).
4. **Action Execution Barrier:**
   - Jalankan aksi klik pada titik pusat terverifikasi: $x_c = x + w/2, y_c = y + h/2$.
   - Sisipkan post-action visual delta check: verifikasi perubahan piksel layar untuk mendeteksi apakah klik memicu feedback/loading.
5. **Resilient Retry & Dynamic Replanning:**
   - Jika DOM, scroll, zoom, frame atau window berubah sebelum dispatch, batalkan koordinat lama dan ambil ulang bukti. Jangan gunakan last-known coordinates sebagai fallback. Terapkan gerbang generation, identity dan hit-test pada skill `agent-multimodal-hybrid-grounding`.

## Pitfalls

- **Coordinate-space contract:** CDP mouse input memakai main-frame viewport CSS pixels: jangan kalikan DPR. Input OS memakai unit backend dan origin layar yang harus dikalibrasi terpisah (scale serta translation, termasuk chrome browser/DPI). DPR saja tidak menentukan transform CSS-ke-OS; tolak transform yang tidak diketahui.
- **Dynamic Popup & Stale AXTree:** Menu dropdown yang menghilang seketika saat blur event memicu koordinat fiktif. Selalu re-sample bounding box 50ms sebelum eksekusi klik.
- **Click-Drift pada Animasi:** Elemen yang sedang bergeser (CSS transition) dapat memicu klik meleset jika snapshot diambil di tengah frame interpolasi.

## Verification

Jalankan suite uji fungsionalitas hybrid grounding engine:
```bash
python3 -c "
from pathlib import Path
import subprocess
p = Path.home() / '.hermes/skills/autonomous-ai-agents/vision-agent-computer-interface/scripts/hybrid_grounding_engine.py'
res = subprocess.run(['python3', str(p), '--test'], capture_output=True, text=True)
assert res.returncode == 0
assert 'HYBRID GROUNDING VERIFIED' in res.stdout
print('Verification successful!')
"
```
