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
