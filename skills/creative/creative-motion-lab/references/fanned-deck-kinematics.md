# Fanned-Out Card Deck Kinematics & Depth Management

## 1. Rumus Geometri Kipas (Fan Arc Geometry)

Untuk $N$ kartu dengan indeks tengah $C = \lfloor N / 2 \rfloor$ dan jarak offset $o_i = i - C$:

1. **Rotasi Spasial:**
   $$\theta_i = o_i \times \Delta\theta$$
   *Nilai terkalibrasi:* $\Delta\theta \in [3.2^\circ, 4.5^\circ]$. Jangan melebihi $5.5^\circ$ agar ujung kartu tidak terpotong tepi layar.

2. **Pergeseran Horizontal (Horizontal Spread Axis):**
   $$X_i = o_i \times \Delta X$$
   *Nilai terkalibrasi:* $\Delta X \approx 0.45 \times W_{\text{card}}$. Jika lebar kartu $250\text{px}$, gunakan $\Delta X = 110\text{px}$. Nilai ini menjamin minimal $40\%$ permukaan setiap kartu terbuka dan dapat diklik tanpa tertutup kartu tetangga.

3. **Pergeseran Vertikal (Curved Parabola Arc):**
   $$Y_i = |o_i| \times \Delta Y$$
   *Nilai terkalibrasi:* $\Delta Y \in [7\text{px}, 12\text{px}]$.

## 2. Invarian Hover Tanpa Jitter

- **Transform Origin:** Selalu gunakan `center 88%` atau `center bottom`.
- **Aturan Elevasi Normal:**
  ```css
  /* SALAH: Memaksa kartu tegak (memicu flicker 40px) */
  .card:hover {
    transform: translateY(-20px) rotate(0deg) !important;
  }

  /* BENAR: Mengangkat kartu di sepanjang sumbu rotasi alaminya */
  .card:hover {
    transform: translateX(var(--spread-x)) translateY(calc(var(--trans-y) - 24px)) rotate(var(--rot)) scale(1.035);
  }
  ```

- **Kedalaman Deterministik (No Layer-Hopping):**
  ```javascript
  // Z-index dihitung murni dari kedalaman visual terhadap pusat
  const zIndex = 20 - Math.abs(offset);
  ```
  *Pantangan:* Dilarang melompatkan `z-index` ke angka 30+ saat `:hover` karena akan merusak hit-test kursor pada kartu yang bertumpuk sebagian.
