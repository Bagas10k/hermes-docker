---
name: spatial-canvas-ui-physics
description: Use when building 3D spatial canvas and UI card physics.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
---

# Spatial Canvas UI Physics & Studio-Grade Web Craft

Doktrin dan rekayasa antarmuka web tingkat tinggi (Awwwards / Studio Grade) yang melampaui tata letak statis biasa. Menggabungkan fisika spasial 3D, kanvas atmosferik 60 FPS, momentum scrolling, dan umpan balik akustik multi-nada.

---

## 1. Standar Mutu: Membedakan Skor 6/10 vs 9.8/10

Sebuah antarmuka dinilai "hanya bernilai 6/10" apabila sekadar menumpuk blok `<div>` dengan teks dan gambar statis tanpa responsivitas spasial terhadap kehadiran kursor pengguna, atau menggunakan ornamen murah seperti kapsul pill badge mengambang di atas H1.

Untuk mencapai standar **9.8/10 (Studio of the Day)**, terapkan 5 pilar wajib:
1. **Respons Spasial 3D (3D Gyro Tilt & Specular Varnish):** Objek utama berotasi secara halus terhadap posisi pointer mouse dengan lapisan kilau cahaya (*specular glare overlay*) yang bergerak melintasi permukaan material.
2. **Kanvas Atmosferik 60 FPS (Organic Atmospheric Dust):** Latar belakang memiliki partikel mikro mengambang yang hidup di HTML5 Canvas 2D murni (<1% CPU) dan bereaksi lembut terhadap tarikan kursor.
3. **Presisi Editorial Swiss:** Detail kuratorial fisik berupa tanda pin sudut (*corner cross marks* `+`), nomor katalog arsip (`CAT. NO. 04-PR`), dan pita koordinat studio (`LAT 51.5° N // LON 0.1° W`).
4. **Resonansi Akustik Multi-Tone (Web Audio API):** Umpan balik taktil berbasis frekuensi analog:
   - *Mechanical micro-tick* saat beralih antar kartu/item.
   - *Harmonic pentatonic chord* (akord F-A-C-E hangat) saat inspeksi detail dibuka.
5. **Momentum Scrolling (Lenis 60 FPS):** Gulir halaman berbobot dengan *reading progress bar* di bagian atas layar (`useScroll` + `useSpring`).

---

## 2. Aturan Fisika Tumpukan Kartu Kipas (Fanned-Out Deck Physics)

### Pitfall Utama: Hover Jitter & Layer Hopping
Memaksa kartu miring dalam susunan kipas untuk tegak lurus (`rotate(0deg) !important`) saat di-*hover* akan menggeser sudut geometri kartu puluhan piksel menjauhi kursor mouse. Hal ini membuat status `:hover` terlepas seketika, kartu kembali miring, kursor masuk lagi, dan memicu siklus getaran/hentakan (*infinite hunting oscillation / nyentak-nyentak*). Perubahan `z-index` mendadak juga memicu perebutan layer (*z-fighting*).

### Invarian Fisika Wajib:
1. **Preserve Natural Arc Angle:** Pertahankan sudut kemiringan alami kartu (`rotate(var(--card-rot))`). Cukup angkat kartu sepanjang sumbu alaminya:
   ```css
   transform: translateX(var(--card-spread-x)) translateY(calc(var(--card-trans-y) - 24px)) rotate(var(--card-rot)) scale(1.035);
   transition: transform 0.45s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.45s ease;
   ```
2. **Rentang Sebar Horizontal (Proportional Spread):** Berikan jarak sebar sumbu X yang cukup (`spreadX = offset * 110px`) agar setiap kartu memiliki bidang sentuh kursor yang leluasa tanpa tertutup 100% oleh kartu tetangga.
3. **Kedalaman Deterministik Tanpa Lonjakan Z-Index:** Kunci hierarki kedalaman secara matematis dari jarak ke kartu aktif:
   ```javascript
   zIndex: 20 - Math.abs(offset)
   ```
   Jangan menaikkan `z-index` secara liar saat `:hover` agar kursor tidak kehilangan target.
4. **Fokus Meredup Halus (Depth Dimming):** Kartu-kartu di sekitar kartu yang sedang disentuh meredup secara anggun (`opacity: 0.86; filter: saturate(0.92)`).

*Detail formulasi matematis dan kurva kipas: lihat [references/fanned-deck-kinematics.md](references/fanned-deck-kinematics.md).*

---

## 3. Resep Kanvas Debu Atmosferik 60 FPS (Canvas 2D Ringan)

```javascript
// Partikel debu studio melayang dengan pergeseran pointer halus
export function AmbientStudioCanvas() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let rafId;
    let width = (canvas.width = canvas.offsetWidth);
    let height = (canvas.height = canvas.offsetHeight);

    const particles = Array.from({ length: 32 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      r: Math.random() * 1.5 + 0.5,
      vx: (Math.random() - 0.5) * 0.25,
      vy: (Math.random() - 0.5) * 0.25,
      alpha: Math.random() * 0.4 + 0.1
    }));

    function render() {
      ctx.clearRect(0, 0, width, height);
      for (const p of particles) {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${p.alpha})`;
        ctx.fill();
      }
      rafId = requestAnimationFrame(render);
    }
    rafId = requestAnimationFrame(render);

    return () => cancelAnimationFrame(rafId);
  }, []);

  return <canvas ref={canvasRef} className="ambient-studio-canvas" aria-hidden="true" />;
}
```

---

## 4. Uji Aksesibilitas & Zero Emoji

- **Zero Unicode Emoji:** Seluruh visual, status badge, dan ikon wajib menggunakan SVG murni atau `lucide-react`. Larangan mutlak karakter Extended Pictographic.
- **Pointer & Keyboard Trapping:** Modal inspeksi dialog wajib memiliki trap fokus `Tab` / `Shift+Tab` dan dapat ditutup via tombol keyboard `Escape`.
- **Axe-Core Compliance:** 0 pelanggaran aksesibilitas WCAG 2.1 AA di seluruh viewport responsif (390px, 768px, 1440px).
