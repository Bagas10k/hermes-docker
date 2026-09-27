# Bento Grid Mathematical Proportion & Spatial Layout Guide

## 1. Rasio Modular & Spatial Geometry
Dalam arsitektur bento grid kontemporer (mengacu pada standar Apple, Linear, dan Stripe), ritme visual dicapai melalui modular unit $U$:
- Lebar unit standar: $W = (W_{\text{container}} - (N - 1) \times \text{gap}) / N$
- Tinggi baris standar: $H_{\text{row}} = 240\text{px}$ (atau rasio emas $1.618 \times \text{lebar kolom}$ untuk kartu hero)

## 2. Tabel Matriks Komposisi Bento 4-Kolom

| Tipe Modul | Grid Span | Dimensi Relatif | Konten Optimal |
|---|---|---|---|
| Standard Tile | 1x1 | $1U \times 1H$ | Single KPI, micro gauge, tactile switch, avatar stack |
| Broad Feature | 2x1 | $2U \times 1H$ | Sparkline chart, trend line, horizontal timeline |
| High Tower | 1x2 | $1U \times 2H$ | Activity log, vertical checklist, device mockup frame |
| Grand Canvas | 2x2 | $2U \times 2H$ | WebGL / 3D interactive, primary hero graphic, map visual |
| Panoramic Ribbon | 4x1 | $4U \times 1H$ | Global search omnibar, continuous marquee ticker, summary HUD |

## 3. Dark Mode & Warm Paper Token Alignment
- **Warm Obsidian (Dark):** Surface `#1C1915`, Border `#2D2822`, Background `#14120E`, Accent Glow `#F59E0B`.
- **Warm Paper (Light):** Surface `#FFFFFF`, Border `#E2E8F0`, Background `#FAF6EF`, Subtle Shadow `0 10px 25px rgba(15,23,42,0.04)`.
