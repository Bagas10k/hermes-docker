---
name: ambient-binaural-soundscape
description: Synthesize zero-asset Web Audio ambient binaural soundscapes.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web-audio, soundscape, binaural-beats, procedural-audio, ambient, vibe-coding]
    related_skills: [ambient-sonification-flow, audio-reactive-visual-flow, flow-state-telemetry]
---

# Ambient Binaural Soundscape Skill

Engine sintesis audio prosedural murni Web Audio API untuk menghasilkan soundscape latar adaptif, binaural beats penunjang fokus (Gamma 40Hz / Alpha 10Hz), pink noise tersaring lembut, dan ambient harmonic drone tanpa ketergantungan file audio eksternal (.mp3/.wav), hemat bandwidth, serta bebas jeda jaringan.

## When to Use

- Membutuhkan latar audio fokus (flow state / deep work) yang berjalan langsung di browser tanpa memuat aset audio eksternal.
- Mengintegrasikan modul binaural beat ilmiah (40Hz Gamma untuk konsentrasi pemecahan masalah kompleks, 10Hz Alpha untuk arsitektur kreatif).
- Menghadirkan generator noise prosedural (Brownian / Pink / Warm Rain) dengan filter Biquad low-pass interaktif.
- Mencegah lonjakan volume dan speaker click menggunakan envelope linear/exponential ramp terkalibrasi.
- Menghemat konsumsi daya browser dengan auto-suspend AudioContext saat tab tidak aktif (Page Visibility API).

### Don't use for:
- Notifikasi audio diskrit pendek (build pass/fail cues) -> gunakan `ambient-sonification-flow`.
- Visualisasi spektrum FFT audio -> gunakan `audio-reactive-visual-flow`.
- Pemutaran musik rekaman komersial atau audio streaming berbasis file.

## Prerequisites

- Browser modern dengan dukungan standar HTML5 Web Audio API (`window.AudioContext` atau `window.webkitAudioContext`).
- Interaksi pengguna awal (gesture: click / keydown) untuk mengaktifkan AudioContext sesuai kebijakan browser autoplay policy.
- Zero external package dependencies (100% vanilla Web Audio API & JavaScript).

## How to Run

1. Jalankan unit test verifikasi matematika synthesizer via Node.js:
   `terminal(command="node ~/.hermes/skills/creative/ambient-binaural-soundscape/scripts/soundscape_math_test.js")`
2. Sajikan template demonstrasi HTML/JS instan untuk pengujian browser:
   `read_file(path="~/.hermes/skills/creative/ambient-binaural-soundscape/references/soundscape_engine.html")`

## Quick Reference

```javascript
// Inisialisasi Soundscape Engine
const engine = new BinauralSoundscapeEngine();
await engine.init();

// Memulai mode Gamma 40Hz (Deep Coding Flow)
engine.start({
  mode: 'gamma_focus',      // 'gamma_focus' (40Hz) | 'alpha_creative' (10Hz) | 'deep_ambient'
  carrierFreq: 216,          // Frekuensi dasar (Hz)
  pinkNoiseGain: 0.15,       // Latar desis pink noise lembut
  droneGain: 0.12,           // Harmonic sine drone
  masterGain: 0.40           // Master volume (0.0 - 1.0)
});

// Menyesuaikan filter cutoff real-time (efek kedalaman ruang)
engine.setFilterCutoff(480); // Hz

// Meredupkan halus (fade out) dan auto-suspend
await engine.stop(1.5); // durasi ramp-down 1.5 detik
```

## Procedure

1. **Inisialisasi AudioContext Terproteksi (Autoplay Unlock)**:
   - Tangkap interaksi pertama pengguna (`pointerdown` atau `keydown`).
   - Bangkitkan `AudioContext` dengan `sampleRate: 44100` atau `48000`.
   - Pastikan state bukan `suspended`; jika suspended, panggil `ctx.resume()`.

2. **Perakitan Jalur Stereo Panning Binaural**:
   - Bentuk dua kanal independen menggunakan `StereoPannerNode` atau `ChannelMergerNode`.
   - Saluran Kiri: OscillatorNode frekuensi carrier $f_0$ (misal 216 Hz), di-pan penuh ke kiri (`pan = -1.0`).
   - Saluran Kanan: OscillatorNode frekuensi $f_0 + \Delta f$ (misal 216 + 40 = 256 Hz), di-pan penuh ke kanan (`pan = 1.0`).
   - Otak memproses selisih fase kedua telinga menjadi persepsi ritmik $\Delta f$ (Binaural Beat).

3. **Sintesis Pink Noise Prosedural (Metode Kellet Filter)**:
   - Gunakan `AudioWorkletNode` atau buffer generator 3 detik melingkar (`AudioBufferSourceNode` ber-loop).
   - Terapkan filter poles Paul Kellet untuk mendekati kurva desis pink noise (penurunan -3 dB/oktaf):
     $$S(f) \propto \frac{1}{f}$$
   - Hubungkan ke `BiquadFilterNode` tipe `lowpass` (Q = 0.707) dengan cutoff 400–600 Hz untuk menghilangkan desis tinggi yang menusuk telinga.

4. **Transisi Gain Bebas Pop/Click (Slew-Rate Limiting)**:
   - Dilarang keras memutasi `gain.value` secara seketika (`gain.value = 0.5`).
   - Wajib gunakan:
     `gainNode.gain.cancelScheduledValues(ctx.currentTime)`
     `gainNode.gain.linearRampToValueAtTime(target, ctx.currentTime + rampDuration)`
   - Tetapkan durasi minimum ramp 30–50 ms untuk mencegah lonjakan tegangan DC.

5. **Efisiensi Sumber Daya & Auto-Sleep Tab**:
   - Dengarkan event `document.visibilityState`:
     - Saat tab masuk ke latar belakang (`hidden`), turunkan gain secara bertahap atau tangguhkan konteks jika pengguna memilih mode hemat daya.
     - Saat kembali aktif (`visible`), pulihkan status audio.

## Pitfalls

1. **Autoplay Policy Block**:
   - Browser modern memblokir pemutaran audio jika AudioContext dijalankan sebelum gesture pengguna.
   - Solusi: Bungkus eksekusi di dalam listener tombol interaktif dan selalu panggil `if (ctx.state === 'suspended') await ctx.resume();`.

2. **Mono Summing Cancellation**:
   - Jika sinyal binaural beat didengar lewat speaker laptop biasa (mono/speaker terintegrasi), kedua gelombang saling berinterferensi secara akustik di udara atau tercampur di OS, merusak efek binaural.
   - Solusi: Sediakan peringatan visual "Gunakan Headphone Stereo untuk Efek Binaural Maksimal". Tambahkan tombol sakelar mode "Speaker Ambient" yang beralih ke modulated chorus/drone daripada frekuensi terpisah.

3. **DC Offset & Clipping**:
   - Menggabungkan beberapa osilator dan noise tanpa pembagian gain dapat melampaui rentang $[-1.0, 1.0]$, memicu distorsi digital kasar.
   - Solusi: Selalu letakkan `DynamicsCompressorNode` lunak tepat sebelum `ctx.destination` sebagai limiter darurat, dan batasi jumlah bobot masing-masing layer.

## Verification

Jalankan pengujian logika matematika dan integritas audio:
1. `node ~/.hermes/skills/creative/ambient-binaural-soundscape/scripts/soundscape_math_test.js`
2. Verifikasi perhitungan frekuensi:
   - Gamma: $f_{\text{right}} - f_{\text{left}} = 40.0\text{ Hz} \pm 0.01$
   - Alpha: $f_{\text{right}} - f_{\text{left}} = 10.0\text{ Hz} \pm 0.01$
3. Periksa visual dan fungsionalitas UI via headless browser atau server lokal.
