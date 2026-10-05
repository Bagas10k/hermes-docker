---
name: content-intelligence
description: "Content Learning Loop: analyze and optimize social content."
version: 1.0.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [content-intelligence, analytics, content-learning-loop, social-media, cross-channel, qc]
    related_skills: [sputarball-content-system, news-editorial-copywriting, otak-koding]
---

# Content Intelligence & Social Learning Systems

Transformasi pembuatan konten sosial dari sekadar posting acak menjadi sistem pembelajaran berkelanjutan berbasis bukti (Content Learning Loop & Causal Modeling) lintas kanal (Instagram, TikTok).
Mengonsolidasikan prinsip analisis DNA, funnel diagnosa, dan arsitektur evaluasi kausalitas. Atribusi sistem: Bagas Cihuy.

## 1. Siklus Kognitif Konten (Content Learning Loop)
```text
IDEA ➔ CONTENT DNA ➔ PRE-PUB QC ➔ PUBLISH ➔ OBSERVE ➔ COMPARE ➔ DIAGNOSE ➔ LEARN ➔ EXPERIMENT ➔ REPEAT
```
1. **OBSERVE**: Rekam snapshot performa bertahap pada 30 menit, 2 jam, 24 jam, dan 72 jam (Reach, Impressions, Retention, Saves, Shares, Profile Visits).
2. **DECOMPOSE**: Bedah struktur DNA: Hook, Topic, Subject, Angle, Visual Type, Tone, CTA, dan Durasi.
3. **COMPARE**: Bandingkan terhadap **median baseline akun sendiri** (30 post terakhir) pada usia yang setara, bukan rata-rata terdistorsi.
4. **DIAGNOSE**: Analisis 4 dimensi terpisah: Visual, Topik, Gaya Penulisan, dan Waktu Rilis.
5. **LEARN**: Simpan pola ke tabel dinamis `agent_self_learned_rules` dengan status `EXPERIMENTAL`, `PROMISING`, atau `VALIDATED` berbasis Bayesian posterior.
6. **EXPERIMENT**: Rancang uji komparasi berikutnya dengan mengubah **hanya satu variabel**.

## 2. Model Kausalitas & Manifest Pra-Publikasi
- **Model Kausalitas Hasil Konten**:
  $$\text{Performa} = f(\text{Visual}, \text{Subject}, \text{Topic}, \text{Hook}, \text{Time Slot}, \text{Freshness}, \text{Audio}) + \text{Noise}$$
  Deklarasikan prediksi arah faktor sebelum metrik terkumpul untuk menghindari atribusi semu.
- **Manifest Pra-Publikasi**:
  Simpan canonical content ID, platform ID, kelas topik/hook, QC score, dan hash aset deterministik untuk memastikan paritas visual lintas kanal.

## 3. Disiplin Metrik & QC Gatekeeper
- **Bobot Metrik Utilitas**: Pada Instagram, prioritaskan Save Rate dan Share Rate (`Saves / Reach`, `Shares / Reach`) daripada Likes karena mencerminkan utilitas riil dan retensi audiens.
- **QC Invariant Veto**: Cacat visual (subjek salah, watermark tampak, blur berat, wajah terpotong, atau ketidakcocokan aset antar-kanal) menghasilkan veto instan (`HARD_VETO`).
- **Human-in-the-Loop & Approval Gate**: Draf yang lolos QC otomatis diproses sesuai kebijakan akun atau diajukan ke antrean persetujuan sebelum eksekusi API publikasi.

## 4. Pelaporan Analisis Konten (Template)
- **DNA & Konteks**: Format, platform, hook type, subjek, visual style.
- **Metrik vs Median Baseline**: Delta Reach, Save Rate, Share Rate, titik retensi (drop-off).
- **Diagnosa Kausal**: Komponen DNA dominan yang berkontribusi, titik gesekan audiens, dan faktor pengganggu (confounding).
- **Pembaruan Aturan**: Rule delta untuk `agent_self_learned_rules` dan 1 variabel kontrol untuk eksperimen berikutnya.
