---
name: gsap
description: Use when animating with GSAP for UI morph or video.
---
# GSAP (GreenSock Animation Platform) — Arsitektur Standar Morphing UI/UX

Skill ini adalah **panduan baku penerapan animasi morphing 60 FPS** menggunakan ekosistem GSAP 3.15 (Flip, MorphSVG, Timeline) sesuai mandat resmi Mas Bagas.

---

## 1. Mandat Khusus Mas Bagas (Hukum Morphing UI/UX)
- **Zero Abrupt Modal:** Dilarang menggunakan pop-up modal kaku yang mendadak muncul menutup layar.
- **Wajib Animasi Morphing:** Komponen kecil (kartu list, avatar, icon, tombol) **wajib bermetamorfosis secara kontinu (*shared-element expansion*)** menjadi kartu fokus / modal kerja di tempatnya.
- **Fisika Pegas Alami:** Kurva gerak wajib menggunakan natural physics `cubic-bezier(0.16, 1, 0.3, 1)` atau GSAP CustomEase / power3.out, menjamin pergerakan berbobot dan zero jank pada 60-120 FPS.

---

## 2. Pola 1: Morphing Layout & Ekspansi Kartu (GSAP Flip Plugin)

Teknik **FLIP** (*First, Last, Invert, Play*) adalah metode tercepat di browser untuk melakukan morphing kartu tanpa penurunan frame-rate.

```javascript
import gsap from "gsap";
import { Flip } from "gsap/Flip";

gsap.registerPlugin(Flip);

function expandCardToPanel(cardElement, targetContainer) {
  // 1. Rekam koordinat awal (FIRST)
  const state = Flip.getState(cardElement, {
    props: "backgroundColor,borderRadius,boxShadow"
  });

  // 2. Ubah state DOM menjadi tampilan besar (LAST)
  cardElement.classList.toggle("is-expanded");
  if (targetContainer) {
    targetContainer.appendChild(cardElement);
  }

  // 3. Eksekusi morphing fluida 60 FPS (INVERT & PLAY)
  Flip.from(state, {
    duration: 0.65,
    ease: "power3.out", // Pegas inersia alami
    scale: true,        // Menggunakan GPU hardware transform scale
    absolute: true,     // Mencegah layout shift elemen sekitar
    nested: true,       // Menjaga teks & tombol anak tidak terdistorsi
    onComplete: () => {
      console.log("Morphing kartu tuntas 60 FPS");
    }
  });
}
```

---

## 3. Pola 2: Morphing Ikon & Bentuk Vektor (GSAP MorphSVG)

Digunakan untuk transisi halus antar-bentuk SVG (contoh: Ikon Play bermorfing menjadi Pause, atau Ikon Grid menjadi Detail).

```javascript
import gsap from "gsap";
import { MorphSVGPlugin } from "gsap/MorphSVGPlugin";

gsap.registerPlugin(MorphSVGPlugin);

function morphIconShape(pathSelector, targetPathData) {
  gsap.to(pathSelector, {
    morphSVG: targetPathData,
    duration: 0.45,
    ease: "power2.inOut"
  });
}
```

---

## 4. Pola 3: Shared Element Text & Header Migration (SplitText + Timeline)

Saat kartu bermorfing membesar, teks judul bermigrasi secara serempak:

```javascript
import gsap from "gsap";
import { Flip } from "gsap/Flip";

export function handleComponentMorph(triggerEl, expandedEl) {
  const state = Flip.getState([triggerEl, expandedEl]);
  
  // Toggle visibility
  triggerEl.style.display = "none";
  expandedEl.style.display = "flex";

  Flip.from(state, {
    duration: 0.6,
    ease: "power3.out",
    fade: true
  });
}
```

---

## 5. Standar Wajib Interaksi & Motion (SOP Mas Bagas v2.0)
Semua implementasi GSAP wajib memenuhi kriteria:
1. **FLIP In-Place Morphing:** Kartu membesar in-place tanpa modal dialog kaku.
2. **Motion Lifecycle:** Enter (280ms stagger fade-in), Loop (denyut halus), Exit (akselerasi sigap).
3. **Anti-Berkedip Putih (SPA Seamless Swap):** Seluruh transisi filter dan tab di web dipadukan dengan GSAP crossfade tanpa me-reload browser.
4. **Mobile Optimization:** Gunakan `will-change: transform` dan hindari animasi `top/left/width/height` mentah yang memicu CPU reflow.

---

## 6. Timeline video & keyframes (render deterministik, misal HyperFrames)

Video dirender frame demi frame dari `gsap.timeline({paused:true})`, jadi semua yang tampak harus fungsi waktu timeline: tanpa `repeat:-1`, `Math.random()` tanpa seed, `Date`, timer, atau CSS transition. Craft gerak dan QC video ada di skill `product-motion-presentation` (berkas referensi keyframe-craft di skill itu). Daftar plugin yang aman/tidak aman untuk render, beserta resep kamera, kartu, kursor, angka, dan stagger yang sudah diuji, ada di `references/video-capability-map.md`.

**Tiga bentuk keyframes (GSAP ≥ 3.9) dan ease bawaannya:**

| Bentuk | Contoh | Ease per segmen bawaan |
| --- | --- | --- |
| Persen | `keyframes:{'0%':{x:0}, '60%':{x:120, ease:'expo.out'}, '100%':{x:140}, easeEach:'power2.inOut'}` + `duration` di tween | `power1.inOut` |
| Array nilai | `keyframes:{x:[0,120,140], y:[0,-20,0], easeEach:'sine.inOut'}` (nilai dibagi rata, panjang array boleh beda) | `power1.inOut` |
| Array objek | `keyframes:[{x:120, duration:0.4, ease:'expo.out'}, {x:140, duration:0.8}]` (tiap keyframe punya durasi/`delay` sendiri) | linear |

- `easeEach` ditulis di dalam objek `keyframes`; `ease` per keyframe menimpa `easeEach` untuk segmen itu.
- `ease` di level tween membengkokkan seluruh blok. Tulis `ease:'none'` secara eksplisit bila ingin hanya ease segmen yang membentuk kurva.
- Gerak multi-tahap satu elemen = satu tween keyframes, bukan rangkaian `tl.to` terpisah, agar kecepatan tidak patah di sambungan.
- Di sambungan dua gerak, cerminkan ease (`power3.in` → `power3.out`) supaya kecepatan sama di kedua sisi.

**CustomEase (kurva cubic-bezier bernama):**

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/CustomEase.min.js"></script>
<script>
  gsap.registerPlugin(CustomEase);
  CustomEase.create('ui', '0.16,1,0.3,1');   // juga menerima path SVG
</script>
```

- Versi plugin harus sama dengan `gsap.min.js`. Paket hyperframes membawa salinan lokal (`dist/vendor/npm/gsap@<ver>/dist/CustomEase.min.js`, `MotionPathPlugin.min.js`); cari dengan `find ~/.npm/_npx -name CustomEase.min.js`.
- Di HyperFrames setiap komposisi punya skrip sendiri: register di helper bersama generator agar semua adegan memuatnya, lalu buktikan dengan lint + snapshot satu adegan sebelum dipakai massal.
