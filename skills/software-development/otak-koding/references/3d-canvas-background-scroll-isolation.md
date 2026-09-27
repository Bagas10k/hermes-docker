# 3D Canvas Background Gesture Isolation & Native Scroll Synchronization

Gunakan panduan ini ketika menyematkan kanvas 3D WebGL (Three.js, 3d-force-graph, R3F) sebagai latar belakang (*fixed background*) di balik dokumen atau portofolio web interaktif.

## 1. Gejala Masalah ("Bocor ke Background")
Ketika kanvas 3D diletakkan di latar belakang:
- Pengguna tidak bisa menggulir halaman web saat kursor berada di area kosong (margin kiri/kanan atau jarak antar kartu).
- Roda mouse (*mouse wheel*) malah memperbesar/memperkecil (*zoom*) kanvas 3D alih-alih menggulir halaman web.
- Usapan jari (*touch swipe*) di layar sentuh tertahan dan tidak menggerakkan halaman.

## 2. Akar Penyebab Mekanistik
1. **Three.js OrbitControls / TrackballControls**: Secara default menambahkan event listener `wheel`, `pointerdown`, `pointermove`, dan `pointerup` non-pasif langsung ke elemen `<canvas>`.
2. **Atribut Inline `touch-action: none`**: Three.js menyisipkan gaya inline ini pada kanvas, yang menginstruksikan peramban untuk mematikan penanganan gesture bawaan (*default scrolling*).
3. **Pewarisan CSS Terbatas**: Menyetel `#bg-container { pointer-events: none; }` tidak cukup jika elemen `<canvas>` di dalamnya memiliki gaya inline tersendiri atau jika *stacking context* tidak diisolasi.

## 3. Protokol Penanganan Mutlak (3 Lapis Pertahanan)

### Lapis 1: Isolasi CSS Total
Gunakan selektor universal berprioritas tinggi agar tidak ada elemen anak yang menangkap pointer:
```css
#bg-3d-canvas,
#bg-3d-canvas *,
#bg-3d-canvas canvas,
#bg-3d-canvas .scene-container {
  pointer-events: none !important;
  touch-action: auto !important;
  user-select: none !important;
}

#bg-3d-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0; /* Letakkan di layer dasar */
}
```

### Lapis 2: Pelucutan Kontrol di Sisi JavaScript
Segera setelah inisialisasi kanvas/graf 3D, matikan dan lepas kontrol bawaan:
```javascript
// 1. Nonaktifkan kontrol internal
Graph.enableNavigationControls(false);
const controls = Graph.controls();
if (controls) {
    controls.enabled = false;
    if (typeof controls.dispose === 'function') controls.dispose();
}

// 2. Kunci elemen canvas agar sepenuhnya pasif
const canvasEl = container.querySelector('canvas');
if (canvasEl) {
    canvasEl.style.setProperty('pointer-events', 'none', 'important');
    canvasEl.style.setProperty('touch-action', 'auto', 'important');
}
```

### Lapis 3: Sinkronisasi Kamera Murni Berbasis Scroll Dokumen (LERP 60 FPS)
Alih-alih menangkap event mouse/touch, gerakkan kamera 3D secara proporsional terhadap kemajuan scroll dokumen:
```javascript
let targetProgress = 0;
let currentProgress = 0;
let ambientAngle = 0;

function updateScrollProgress() {
    const scrollY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;
    const scrollHeight = document.documentElement.scrollHeight || document.body.scrollHeight || 1;
    const clientHeight = window.innerHeight || document.documentElement.clientHeight || 1;
    const maxScroll = Math.max(1, scrollHeight - clientHeight);
    targetProgress = Math.min(1, Math.max(0, scrollY / maxScroll));
}

window.addEventListener('scroll', updateScrollProgress, { passive: true });
window.addEventListener('resize', updateScrollProgress, { passive: true });
document.addEventListener('scroll', updateScrollProgress, { passive: true });

function renderLoop() {
    requestAnimationFrame(renderLoop);
    if (!Graph) return;

    // LERP smoothing agar transisi kamera terasa sinematik
    currentProgress += (targetProgress - currentProgress) * 0.085;
    ambientAngle += 0.0008;

    // Hitung posisi kamera spasial (orbit dan elevasi dinamis)
    const angle = (currentProgress * Math.PI * 2.2) + ambientAngle;
    const radius = 430 - Math.sin(currentProgress * Math.PI) * 50;
    const elevation = 65 + Math.sin(currentProgress * Math.PI) * 220 - (currentProgress * 95);

    Graph.cameraPosition(
        { x: radius * Math.sin(angle), y: elevation, z: radius * Math.cos(angle) },
        { x: 0, y: 0, z: 0 },
        0
    );
}
requestAnimationFrame(renderLoop);
```

### Lapis 4: Cache-Busting Wajib
Saat memperbarui berkas CSS atau skrip yang mengubah penanganan event kanvas, selalu perbarui parameter versi di tag HTML (`?v=scroll-fixed-...`) agar peramban klien dan jaringan CDN tidak menjalankan versi *cached* yang masih mencegat gesture.
