# Replikasi Antarmuka Sci-Fi HUD & Efisiensi Resource 3D WebGL

Doktrin ini mengkodifikasi standar replikasi antarmuka kelas fiksi ilmiah (Sci-Fi HUD / J.A.R.V.I.S. / Z.E.R.O. / BennettOS) dan optimasi eksekusi Three.js/WebGL di sisi peramban klien.

---

## 1. Replikasi Antarmuka Presisi 1:1 Sesuai Referensi Video/Gambar
Saat pengguna memberikan referensi video atau gambar antarmuka ("kalau kek gini bisa ngga?"):
- **Anti-Dashboard Generik**: DILARANG KERAS mereduksi desain fiksi ilmiah menjadi template web admin standar (sidebar vertikal kaku dan kartu tabel kotak abu-abu).
- **Anatomi Visual Sci-Fi HUD Otentik**:
  1. **Kanvas Ruang Gelap & Pendaran**: Latar belakang hitam pekat (`#020308` / `#000000`) dengan ambient radial glow halus dan garis scanline CRT mikro (`opacity: 0.5-0.6`).
  2. **4 Sudut Kartu HUD Melayang (Floating Corner Brackets)**: Kartu telemetri diletakkan di 4 pojok layar (Top-Left, Bottom-Left, Top-Right, Bottom-Right) menggunakan latar kaca blur (`backdrop-filter: blur(14px)`), garis batas hairline, dan aksen kurung siku presisi (`::before` / `::after` border 2px cyan).
  3. **Inti 3D Dinamis di Tengah**: Sumbu visual utama adalah visualisasi 3D organik nyata (Three.js / WebGL neural connectome, particle burst, gyro rings), bukan sekadar teks box. Berikan ruang lapang di tengah tanpa terhalang elemen lain.
  4. **Bilah Input Prompt Bawah**: Bar masukan perintah diletakkan di bagian bawah tengah layar dengan prompt arrow `>` cyan menyala dan kursor terminal berkedip (`_`).
  5. **Status Audio & Jam Presisi**: Jam digital monospaced di pojok kanan atas, serta indikator gelombang audio mini di footer (`LISTENING FOR "HEY ZERO"`).
  6. **Respon Aksi Dramatis**: Saat memicu permintaan rekap (Enter, Spasi, atau klik), munculkan banner angka besar melayang berpendar neon cyan (`text-shadow: 0 0 35px #00f0ff`) disertai pembacaan suara audio otomatis (*Web Speech API synthesis*).

---

## 2. Doktrin Konservasi Resource WebGL 3D (Smart Inactivity Auto-Sleep)
Rendering 3D WebGL berjalan di perangkat pengguna (klien). Membiarkan loop render 60 FPS berjalan di latar belakang menghabiskan daya baterai, GPU, dan memicu throttle.

### Protokol Hibernasi Pintar (0% GPU Idle):
1. **Deteksi Tab Latar Belakang (`visibilitychange`)**:
   ```javascript
   document.addEventListener('visibilitychange', () => {
       if (document.hidden) {
           enterSleep(); // Hentikan render loop seketika
       } else {
           wakeUp(); // Bangunkan loop render
       }
   });
   ```
2. **Timer Inaktivitas (30-45 Detik)**:
   - Pasang timer idle 30-45 detik tanpa interaksi kursor/sentuhan/keyboard.
   - Jika waktu habis, panggil `cancelAnimationFrame` atau `Graph.pauseAnimation()`.
   - Perbarui badge status visual menjadi `CORE 3D: SLEEP (0% GPU)`.
3. **Bangun Seketika (*Wake-on-Interaction*)**:
   - Daftarkan listener pada event: `mousemove`, `mousedown`, `touchstart`, `touchmove`, `keydown`.
   - Panggil `wakeUp()` untuk memulai kembali `requestAnimationFrame` dan mereset timer idle.
4. **Integritas Status di Latar Belakang**:
   - Seluruh data query, cache graf pengetahuan, dan stream telemetri tetap hidup di latar belakang tanpa diputus, sehingga antarmuka selalu siap tanpa perlu reload.

---

## 3. Doktrin Cockpit Observabilitas Real-Time (RADAR & HUD Terminal)

### A. Anti-Blur Teks Monospace (Haram 3D Tilt pada Teks Kode/HUD)
- **Problem**: Penggunaan CSS 3D transforms (`rotateY`, `rotateX`, `perspective` skew) pada jendela floating HUD atau kartu yang memuat teks kode monospace, diff baris merah/hijau, atau log terminal memicu *subpixel rasterization blur* parah pada layar resolusi standar/LCD.
- **Rule**: Pertahankan orientasi datar 2D ortogonal (*pixel-crisp*) untuk seluruh container teks dan jendela kode. Ciptakan kesan kedalaman ruang (*Z-space depth*) murni melalui:
  1. *Layered Box-Shadow*: Bayangan jatuh bertingkat `0 15px 35px rgba(0,0,0,0.9), 0 0 20px rgba(6,182,212,0.35)`.
  2. *Accent Border & Neon Bloom*: Border hairline 1.5px cyan (`#06B6D4`) dengan garis kiri tebal 4px (`#38BDF8`).
  3. *High Z-Index*: Lapisan z-index tinggi di atas kanvas dengan backdrop blur (`backdrop-filter: blur(12px)`).

### B. Doktrin Transparansi Real-Time Radikal (Dual-Mode Deliberasi & Eksekusi)
- **Problem**: Antarmuka observabilitas yang hanya menampilkan aktivitas saat tool dijalankan akan tampak mati/kosong selama fase agen 'berpikir' atau merumuskan rencana.
- **Rule**: Siklus observabilitas wajib transparan 100% tanpa jeda hitam:
  1. *Fase Deliberasi & Planning (`pre_llm_call`)*: Jendela HUD otomatis menampilkan tab `[🧠 PLANNING & KEPUTUSAN]` berisi dekonstruksi intensi, hipotesis kausal ($y = f(x) + \epsilon$), trade-off keputusan, dan urutan topological DAG steps dengan stopwatch penalaran live.
  2. *Fase Mutasi & Tool Execution (`pre_tool_call`)*: Jendela HUD otomatis bertransisi ke tab `[⚡ KODE & EKSEKUSI]` menampilkan baris diff merah/hijau atau perintah shell seketika sebelum eksekusi dimulai (< 50ms).
  3. *Laser Calling Beam*: Tampilkan berkas kurva sinar laser SVG bercahaya (`<path>` dengan filter glow neon cyan dan partikel pulsa `<circle>`) yang menghubungkan simpul pemanggil ke simpul target dan jendela HUD.

### C. Jalur Sirkuit Laser Dinamis antar-Hierarki Step-by-Step
- Gantikan tanda panah teks kaku/mati (↓) pada diagram alir hierarkis dengan bus sirkuit laser SVG aktif (`viewBox="0 0 240 20"`):
  - *Tahap Running*: Garis sirkuit neon cyan berpendar terang (`#00F0FF`) dengan partikel pulsa energi bergerak cepat mengalir ke bawah.
  - *Tahap Selesai*: Garis solid hijau toska (`#10B981`) tenang.
  - *Tahap Standby*: Garis sirkuit redup (`#263554`) tanpa animasi.
