---
name: agent-webrtc-lowlatency-aci
description: Use when building low-latency WebRTC Agent-Computer Interface.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms:
  - linux
  - darwin
  - windows
metadata:
  hermes:
    category: autonomous-ai-agents
    tags:
      - vision-action
      - webrtc
      - low-latency
      - computer-use
      - screen-grounding
---

# Agent WebRTC Low-Latency ACI (Agent-Computer Interface)

Gunakan skill ini ketika membangun atau mengoperasikan saluran transmisi visual dan kendali aksi sub-50ms antara antarmuka komputer/browser dengan model kecerdasan buatan multimodal.

## When to Use

- Membutuhkan streaming layar atau DOM berkecepatan tinggi (30-60 FPS) tanpa penundaan snapshot lambat.
- Menjalankan inspeksi visual real-time dan deteksi *bounding box* koordinat piksel $(X, Y)$ di atas tampilan antarmuka.
- Mengirimkan aksi otonom sintetis (klik, ketik, scroll, seret) melalui protokol *data channel* dua arah dengan latensi sangat rendah.

## Prerequisites

- Browser modern dengan dukungan `navigator.mediaDevices.getDisplayMedia` dan WebRTC API.
- Node.js runtime untuk proxy/relay sinyal ACI atau browser harness CDP.
- Alokasi memori terkendali dengan batasan $\le 9.0$ GB RAM server.

## Quick Reference

```javascript
// Inisialisasi Screen Capture dengan Frame Rate Adaptif
const stream = await navigator.mediaDevices.getDisplayMedia({
  video: {
    frameRate: { ideal: 60, max: 60 },
    width: { ideal: 1920 },
    height: { ideal: 1080 }
  },
  audio: false
});

// Ekstraksi Frame Canvas untuk Grounding
const track = stream.getVideoTracks()[0];
const imageCapture = new ImageCapture(track);
const bitmap = await imageCapture.grabFrame();
ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
```

## Procedure

1. **Setup Media Stream Pipeline:**
   - Gunakan resolusi 720p/1080p dengan batas kompresi dinamis agar beban bandwidth $\le 2.5$ Mbps.
   - Sambungkan stream video ke `<canvas>` offscreen untuk pemrosesan citra tingkat piksel.

2. **Ekstraksi Koordinat & Grounding $(X, Y)$:**
   - Petakan sistem koordinat tampilan dari $[0, W] \times [0, H]$ ke ruang normalisasi $[0.0, 1.0]$.
   - Lakukan inferensi visual untuk menemukan posisi tombol atau form input.

3. **Injeksi Tindakan Agen (Action Dispatch):**
   - Kirim instruksi klik atau ketik melalui saluran data biner atau simulasi event DOM sintetik.
   - Verifikasi bahwa respons visual terjadi pada frame berikutnya ($t + \Delta t$, dengan $\Delta t < 50$ ms).

4. **Validasi Loop Tertutup:**
   - Lakukan *differential frame diffing* untuk memastikan klik menghasilkan transisi status UI yang valid.

## Pitfalls

- **Memory Leak pada MediaStreamTrack:** Selalu hentikan seluruh track video (`track.stop()`) ketika sesi selesai untuk mencegah kebocoran RAM.
- **Latency Spikes:** Hindari resolusi 4K tanpa downscaling; gunakan resolusi kanonik 1280x720 untuk inferensi vision guna mempertahankan latensi sub-50ms.
- **Toleransi Koordinat Skala:** Selalu hitung rasio `scaleX = canvas.width / rect.width` saat menerima event kursor pengguna pada elemen canvas yang di-resize.

## Verification

Buka prototipe live di `/kanvas/lab/vision-001-webrtc-aci.html`, aktifkan tombol `[BOUNDING BOX: AKTIF]`, gerakkan kursor di atas canvas, dan pastikan HUD koordinat menampilkan posisi $(X, Y)$ serta target elemen terdeteksi secara real-time.
