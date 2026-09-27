---
name: audio-reactive-visual-flow
description: "Build audio-reactive 60 FPS visuals for vibe coding flow."
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web-audio, audio-reactive, visualizer, vibe-coding, fft-analysis, canvas-60fps]
    related_skills: [ambient-sonification-flow, dynamic-canvas-backdrop, shader-canvas-flow]
---

# Audio Reactive Visual Flow Skill

Engine Web Audio API & HTML5 Canvas interaktif 60 FPS untuk antarmuka vibe coding, visualizer audio reaktif real-time, dan flow-state ambient background. Mengintegrasikan dekomposisi frekuensi FFT (Sub-bass, Bass, Mid, Treble), peluruhan envelope asimetris (asymmetric ballistics filter), onset detection berbasis fluks spektral, serta mode auto-sleep 0% CPU saat hening.

## When to Use

- Membangun kanvas visual latar belakang atau HUD audio-reaktif saat sesi vibe coding.
- Menerjemahkan ketukan musik latar, suara ketikan, atau synth audio menjadi deformasi geometri procedural (orbital rings, particle burst, ripple field).
- Membutuhkan visualizer ringan zero-dependency berbasis Web Audio API `AnalyserNode` tanpa framework visual eksternal yang boros memori.
- Memerlukan mekanisme auto-sleep hemat baterai saat audio hening ($E_{\text{RMS}} < 0.001$) dengan reaktivitas instan saat sinyal kembali aktif.

Don't use for:
- Menghasilkan nada audio atau soundscape frekuensi binaural semata tanpa visualizer (gunakan `ambient-sonification-flow`).
- Latar belakang ambient berbasis kursor murni tanpa sinyal audio (gunakan `dynamic-canvas-backdrop`).
- Shading GLSL WebGL tingkat lanjut tanpa ketergantungan audio stream (gunakan `shader-canvas-flow`).

## Prerequisites

- Browser modern dengan dukungan HTML5 Canvas dan Web Audio API (`window.AudioContext` atau `window.webkitAudioContext`).
- Zero dependencies eksternal: murni single-file vanilla HTML/JS dengan native Canvas 2D API.
- Node.js (v18+) untuk pengujian unit dan validasi filter ballistics asimetris.

## Quick Reference

Jalankan pengujian unit dan generate preview via `terminal`:

```bash
# Validasi filter envelope asimetris dan deteksi fluks spektral
node ~/.hermes/skills/creative/audio-reactive-visual-flow/scripts/test_audio_reactive.js

# Generate standalone HTML preview artifact
python3 ~/.hermes/skills/creative/audio-reactive-visual-flow/scripts/generate_audio_artifact.py --output=preview.html
```

## Architecture & Mathematical Mechanics

### 1. Dekomposisi Frekuensi FFT
Sinyal audio domain waktu diubah ke domain frekuensi via Fast Fourier Transform (FFT) dengan ukuran $N = 256$ atau $512$ (`frequencyBinCount = N / 2`):
- **Sub-Bass & Bass (20 Hz - 250 Hz)**: Menggerakkan radius inti geometris (*radial pulse*) dan ketebalan garis gelombang.
- **Mid-Range (250 Hz - 2.500 Hz)**: Mengendalikan deformasi harmonik sinusoidal sudut ($\sin(6\theta)$).
- **Treble / High (2.500 Hz - 16.000 Hz)**: Mengendalikan riak getaran mikro ($\cos(12\theta)$) dan pendaran bayangan luminous.

### 2. Envelope Following Asimetris
Mencegah getaran kaku (*jitter*) dengan rumus ballistics:
$$E_t = \begin{cases} E_{t-1} + 0.65 \cdot (x_t - E_{t-1}) & \text{jika } x_t > E_{t-1} \\ E_{t-1} + 0.08 \cdot (x_t - E_{t-1}) & \text{jika } x_t \le E_{t-1} \end{cases}$$
Menghasilkan respons instan saat hentakan kick drum dan peluruhan lembut saat transisi hening.

### 3. State Machine Auto-Sleep 0% CPU
Jika rata-rata amplitudo $< 0.001$ selama lebih dari 10 detik:
- Hentikan loop `requestAnimationFrame`.
- Turunkan thread render ke status `SLEEPING` (0% CPU / 0% GPU).
- Bangunkan kembali seketika (`ACTIVE`) saat sinyal audio atau input interaktif terdeteksi.

## Procedure

1. **Inisialisasi Web Audio Analyser**:
   Hubungkan audio source (mikrofon atau synthesizer oscillator internal) ke `AnalyserNode` dengan `fftSize = 256` dan `smoothingTimeConstant = 0.8`.
2. **Setup Kanvas Lapis Dua**:
   Buat kanvas fullscreen dengan `ctx.fillStyle = 'rgba(11, 12, 16, 0.2)'` untuk efek trail visual halus 60 FPS tanpa ghosting berlebih.
3. **Ekstraksi Spektrum Bins**:
   Panggil `analyser.getByteFrequencyData(dataArray)` setiap frame, ekstrak rata-rata energi bass, mid, dan treble yang dinormalisasi ke rentang $[0.0, 1.0]$.
4. **Transformasi Geometri Prosedural**:
   Modulasi keliling lingkaran polar $(r(\theta) = r_0 + \Delta r_{\text{mid}} \sin(6\theta) + \Delta r_{\text{high}} \cos(12\theta))$ dengan warna aksen cyan `#66fcf1` dan pendaran `#45a29e`.
5. **Verifikasi Beban CPU**:
   Pastikan konsumsi daya idle turun ke 0% saat audio dimatikan.

## Pitfalls

- **Autoplay Audio Policy**: Browser memblokir inisialisasi `AudioContext` sebelum ada interaksi klik pengguna (`state: suspended`). Wajib membungkus pemanggilan audio di balik event listener tombol aktifkan mikrofon/synth.
- **FFT Size Terlalu Besar**: Menggunakan `fftSize = 2048` memicu latensi pemrosesan domain frekuensi yang terasa terlambat (*lagging beat sync*). Gunakan `fftSize = 256` atau `512` untuk sinkronisasi instan sub-20ms.
- **Canvas Blur pada Layar Retina**: Mengabaikan `window.devicePixelRatio` menyebabkan garis render pecah/buram di layar resolusi tinggi. Wajib mengalikan ukuran buffer kanvas dengan `devicePixelRatio`.

## Verification

Buktikan fungsi skill menggunakan test harness deterministik:

1. Jalankan `node ~/.hermes/skills/creative/audio-reactive-visual-flow/scripts/test_audio_reactive.js`.
2. Pastikan seluruh 3 rangkaian tes (Envelope Ballistics, Spectral Flux Onset, Auto-Sleep State Machine) lulus 100/100.
3. Buat file pratinjau standalone via generator python dan periksa struktur DOM kanvas bebas dari karakter emoji.
