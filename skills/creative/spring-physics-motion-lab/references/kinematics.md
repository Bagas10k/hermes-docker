# Spring Physics Kinematics & Numerical Methods

Dokumentasi matematis dan implementasi referensi untuk simulasi pegas UI real-time.

## 1. Analisis Regim Redaman (Damping Regime)

Sistem getaran selaras teredam satu derajat kebebasan:
$$m \ddot{x} + c \dot{x} + k x = 0$$

Persamaan karakteristik:
$$m r^2 + c r + k = 0 \implies r = \frac{-c \pm \sqrt{c^2 - 4km}}{2m}$$

Didefinisikan:
- Frekuensi natural tak teredam: $\omega_0 = \sqrt{\frac{k}{m}}$
- Rasio redaman: $\zeta = \frac{c}{2\sqrt{km}}$

### Tiga Kondisi Fisik:
1. **Underdamped ($\zeta < 1$)**:
   Akar konjugat kompleks: $r = -\alpha \pm i \omega_d$, dengan $\omega_d = \omega_0 \sqrt{1 - \zeta^2}$.
   Respon posisi analitik:
   $$x(t) = x_{\text{target}} + e^{-\zeta \omega_0 t} \left( A \cos(\omega_d t) + B \sin(\omega_d t) \right)$$
   Cocok untuk animasi UI ceria, tombol bounch, dan mikroskopis efek magnet.

2. **Critically Damped ($\zeta = 1$)**:
   Akar kembar riil: $r = -\omega_0$.
   Respon analitik:
   $$x(t) = x_{\text{target}} + (A + B t) e^{-\omega_0 t}$$
   Menuju target paling cepat tanpa pernah melampaui (overshoot). Standar industri untuk transisi enterprise/Apple iOS navigation.

3. **Overdamped ($\zeta > 1$)**:
   Dua akar riil berbeda negatif. Respon lambat tanpa osilasi.

---

## 2. Pemilihan Integrator Numerik: Mengapa Semi-Implicit Euler?

Dalam animasi real-time web/mobile:
- **Explicit Forward Euler**: Tidak stabil secara energi; untuk $k$ tinggi dan $\Delta t$ biasa, amplitudo membesar tak terbatas (blow-up).
- **Runge-Kutta 4 (RK4)**: Sangat presisi, namun membutuhkan 4 kali evaluasi fungsi gaya per frame. Membebani garbage collector jika mengalokasikan objek baru per frame.
- **Semi-Implicit Euler (Symplectic Euler)**:
  $$v_{n+1} = v_n + a_n \Delta t$$
  $$x_{n+1} = x_n + v_{n+1} \Delta t$$
  Integrator simplektik ini mempertahankan invarian energi fase (area-preserving in phase space), stabil tanpa kebocoran energi, dan memiliki kompleksitas komputasi terendah.

---

## 3. Penanganan Interupsi Alami (Gesture Interruption & Momentum Preserving)

Pada UI sentuh/kursor, interupsi sering terjadi (misal: saat kartu sedang meluncur, pengguna menyentuh dan melempar ke arah berlawanan).

Jika rumus CSS transition dipakai:
- CSS menghentikan animasi di posisi saat ini, lalu memulai durasi baru dari nol. Ini menciptakan sensasi "lag" atau patah arah.

Pada Dynamic Spring Physics:
- State fisik hanya memuat $(x, v)$.
- Ketika target berubah ke $x_{\text{new}}$, kita **TIDAK PERNAH** me-reset $v$ ke 0.
- Vektor kecepatan $v$ eksisting dialirkan sebagai initial condition ke langkah integrasi berikutnya.
- Hasil: Perubahan arah berlangsung mulus sesuai hukum inersia Newton.
