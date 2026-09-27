# Arsitektur WebRTC Low-Latency Agent-Computer Interface (ACI)

## 1. Latar Belakang & Analisis Mekanistik

Metode tradisional inspeksi antarmuka agen berbasis *DOM Tree serialization* atau *single screenshot poll* memiliki keterlambatan waktu (round-trip time) antara 300 ms hingga 1.5 detik per aksi. Batasan ini membuat agen AI lambat dan rentan salah klik ketika antarmuka pengguna sedang menjalankan animasi atau transisi dinamis.

Arsitektur WebRTC ACI memangkas latensi ini ke ranah sub-50ms dengan:
- **Pipa Video Peer-to-Peer:** Mengalirkan frame antarmuka secara berkelanjutan (30-60 FPS) via VP8/H.264 hardware encoder.
- **DataChannel Biner:** Mengirim koordinat klik dan penekanan tombol menggunakan paket UDP/SCTP berukuran < 64 byte.
- **Delta Differencing:** Model hanya memproses region-of-interest (ROI) yang berubah antar frame, bukan menganalisis ulang seluruh kanvas.

## 2. Diagram Aliran Data

```
[Antarmuka Pengguna / Layar OS]
        │
        ▼ (WebRTC MediaStream / getDisplayMedia)
[WebRTC Video Pipeline (Sub-50ms)] ──► [Canvas Frame Extractor]
        ▲                                     │
        │ (SCTP DataChannel Actions)          ▼
[Synthetic Action Dispatcher]       [Visual Grounding Engine (X, Y)]
        ▲                                     │
        └─────────────────────────────────────┘
```

## 3. Rumus Normalisasi Koordinat

Untuk mengatasi variasi DPI dan perbedaan resolusi layar:

$$x_{norm} = \frac{x_{pixel}}{W_{display}}, \quad y_{norm} = \frac{y_{pixel}}{H_{display}}$$

Di mana $x_{norm}, y_{norm} \in [0.0, 1.0]$. Dengan koordinat ternormalisasi, instruksi tindakan agen dapat dieksekusi secara deterministik di berbagai rasio layar tanpa distorsi posisi.
