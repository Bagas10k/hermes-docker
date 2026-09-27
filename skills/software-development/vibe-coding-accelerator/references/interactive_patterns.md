# Interactive Vibe Coding Patterns

Panduan pola interaktif untuk meningkatkan kepuasan dan kecepatan saat vibe coding bersama agen AI.

## 1. Zero-Install Stack Recommendation
Saat melakukan prototyping cepat berbasis vibe coding, gunakan pustaka CDN modern tanpa build step:
- **Tailwind CSS v3 Play CDN**: `<script src="https://cdn.tailwindcss.com"></script>`
- **Lucide Icons Web**: `<script src="https://unpkg.com/lucide@latest"></script>` diikuti `lucide.createIcons();`
- **Alpine.js v3**: Reaktivitas deklaratif ringan di atribut HTML (`x-data`, `x-show`, `x-model`).
- **Canvas-Confetti**: Efek perayaan visual instan saat aksi selesai (`<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>`).

## 2. Audio Sonification Engine (Web Audio API)
Menghasilkan suara sintesis dinamis tanpa mengunduh berkas audio eksternal:
- **Soft Click (40ms)**: Menandai sentuhan tombol.
- **Chord Fanfare (200ms)**: Menandai selesainya kompilasi atau aksi sukses.
- **Error Buzz (100ms sawtooth)**: Peringatan kesalahan input atau kegagalan validasi.

## 3. Tactile Neo-Brutalist Micro-Interactions
- Border tegas 1px–2px dengan sudut melengkung sedang (`rounded-xl`).
- Bayangan offset fisik (`box-shadow: 3px 3px 0px rgba(0,0,0,0.9)`).
- Status aktif menekan ke bawah (`transform: translate(2px, 2px); box-shadow: 1px 1px 0px rgba(0,0,0,0.9)`).
- Pill picker geser bawah (*bottom sheet*) untuk perangkat layar sentuh agar jempol tidak perlu menjangkau bagian atas layar.
