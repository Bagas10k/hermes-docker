---
name: mindset-ai-engine
description: Use when building text-to-visual animations with Mindset AI.
---

# Mindset AI Engine Specification & Procedural Guide

Gunakan skill ini saat menerima naskah, ide, atau teks materi untuk diubah menjadi video animasi visual-first berbasis Remotion dan Procedural SVG.

## Doktrin Utama
1. **Visual-First (Meaning over Keywords)**:
   - Dilarang membuat diagram kotak geometris abu-abu atau tulisan abstrak seperti "ENTITAS A".
   - Wajib memetakan setiap ide ke objek fisis konkret yang langsung dikenali mata manusia dalam 1 detik (kapal, ombak, vektor gaya, chip komputasi, terminal konsol, lengan robot, roket).
2. **Zero-Emoji Doctrine**:
   - Dilarang keras memunculkan emoji piktorial di narasi, judul, metadata, teks visual, maupun respons sistem.
   - Gunakan simbol tipografi murni: `[SCENE N]`, `[✓]`, `[!]`, `→`, `•`, `≥`, `≤`, `·`, `ρ`.
3. **Kontrak Data Terstruktur (Scene Graph JSON)**:
   - Setiap adegan dimodelkan deklaratif dalam `ProjectSpec`:
     - `objects`: daftar komponen dari 22 katalog primitif dengan posisi `{ x, y }`, orientasi, dan properti spesifik.
     - `actions`: daftar mutasi gerak fisis (`move`, `pulse`, `fade`, `scale`, `rotate`, `draw`, `bob`).
4. **Desain Neobrutalisme Elegan (Warm Paper & Obsidian)**:
   - Background: Kertas grid milimeter krem (`#F4F1EA`).
   - Garis tepi: `4px solid #1A1A1A`.
   - Bayangan: `6px 6px 0px #1A1A1A`.
   - Rasio Kanvas: Vertikal 9:16 (1080 x 1920 piksel, 30 FPS).

## Katalog 22 Primitif Prosedural Resmi
1. `ship` (Kapal kargo fisis dengan draft/waterline dan tumpukan kontainer)
2. `sea_waves` (Gelombang laut dinamis berlapis)
3. `water_volume` (Kubikasi fluida terdesak dengan meteran desakan)
4. `force_arrow` (Vektor gaya kinetik berarah lengkap notasi ilmiah Fa, W)
5. `air_cavity` (Penampang melintang lambung kapal berongga udara 90%)
6. `scale_balance` (Neraca timbangan fisis dua lengan)
7. `pipe_flow` (Pipa aliran partikel venturi / bottleneck sistemik)
8. `particle_cloud` (Awan partikel kinetik difusi vs kisi teratur)
9. `microchip` (CPU silikon berjalur sirkuit nalar terpadu)
10. `camera_scanner` (Lensa pemindai sensorik dengan kerucut laser radar)
11. `robotic_arm` (Lengan mekanis artikulasi pengeksekusi perkakas)
12. `terminal_window` (Jendela shell bash/CLI realistis)
13. `speech_bubble` (Balon dialog komparasi verbal)
14. `text_badge` (Lencana status neobrutalisme kontras tinggi)
15. `equation_card` (Plakat rumus matematika notasi unicode baku)
16. `container_beaker` (Gelas ukur laboratorium berskala cairan)
17. `gear_spindle` (Roda gigi mekanik intermeshing berputar)
18. `prism_beam` (Prisma kaca pembias cahaya putih menjadi spektrum)
19. `magnet_field` (Dipol kutub magnetik U-S dan garis fluks medan gaya)
20. `rocket` (Fuselage wahana antariksa)
21. `flame_exhaust` (Semburan api propulsi kinetik ke bawah)
22. `checklist_card` (Kartu ringkasan takeaways ilmiah bertanda `[✓]`)

## Verifikasi Sebelum Render
Jalankan validasi skema via `agent/scene_schema.js`:
```bash
npm test tests/scene_schema.test.js
```
Render cuplikan frame untuk audit visual dengan `vision_analyze` sebelum memproduksi MP4 penuh.
