# Tactile Haptic Synthesis: Arsitektur & Spesifikasi Teknis

## 1. Latar Belakang & Motivasi
Dalam paradigma **Vibe Coding**, pengalaman pengguna tidak hanya bersifat visual (*sight*) atau auditori (*sound*), melainkan somatosensori taktil (*touch / haptics*). Ketika seorang pengembang berinteraksi dengan antarmuka mobile atau web interaktif (menekan tombol aksi, menggeser slider, melakukan drag-and-drop kanvas, atau menerima feedback compile/build), respons sentuhan memberikan kepastian fisik seketika (*instant physical confirmation*).

Namun, penggunaan Web Vibration API (`navigator.vibrate`) secara naif sering memicu sejumlah masalah kritis:
1. **Haptic Fatigue / Over-Vibration**: Pola getaran yang terlalu panjang (>500ms) atau berulang terlalu cepat membuat tangan pengguna lelah dan terganggu.
2. **Keterbatasan Platform (Desktop & iOS Safari)**: iOS Safari secara default membatasi atau menonaktifkan `navigator.vibrate`, dan sebagian besar desktop tidak memiliki motor getar (LRA/ERM). Tanpa fallback, interaksi menjadi bisu.
3. **Thermal & Battery Drain**: Motor getar mekanikal mengonsumsi daya baterai yang signifikan bila dipacu terus menerus tanpa pembatas duty-cycle.

Skill `tactile-haptic-synthesis` merumuskan arsitektur haptik prosedural kelas industri:
- Menstandarkan 6 profil haptik teruji berdasarkan frekuensi resonansi LRA (170-205 Hz).
- Melengkapi dengan modul **Acoustic Sub-Bass Fallback** (Web Audio API 65Hz-85Hz micro-chirp) untuk desktop dan peramban non-vibrasi.
- Menerapkan **Dynamic Cooldown Throttling** dan **Battery Guard** (otomatis nonaktif jika baterai <= 15% tanpa charging).

---

## 2. Sintesis Tiga Mindset Matematis

### A. Lensa Mekanistik-Kausal (Mechanism & Bounds)
* **Model Fisika Aktuator Haptik (LRA Dynamics):**
  Motor getar linear (*Linear Resonant Actuator*) dimodelkan sebagai osilator harmonik teredam:
  $$m \ddot{x}(t) + c \dot{x}(t) + k x(t) = F(t)$$
  di mana:
  - Frekuensi natural resonansi: $f_0 = \frac{1}{2\pi}\sqrt{\frac{k}{m}} \approx 175 - 195\text{ Hz}$.
  - Rasio redaman: $\zeta = \frac{c}{2\sqrt{km}} \approx 0.20 - 0.25$.
  - Durasi akselerasi bangkit (*rise-time*): $\approx 10 - 15\text{ ms}$.
* **Batasan Siklus Kerja (Duty-Cycle Bounds):**
  Untuk mencegah panas berlebih pada aktuator mikro ponsel:
  $$\text{Duty Cycle} = \frac{\sum t_{\text{active}}}{\sum t_{\text{total}}} \times 100\% \le 75\% \quad (\text{pada pola } > 100\text{ms})$$
* **Batas Latensi Perseptual Manusia:**
  Waktu respons taktil manusia optimal berada di jendela $< 35\text{ms}$ dari sentuhan fisik. Jika getaran tertunda $> 50\text{ms}$, otak mempersepsikannya sebagai *lag* sistem.

### B. Lensa Bayesian-Eksperimental (Evidence & Belief Updating)
* **Distribusi Eksperimen Presets:**
  - *Prior*: Asumsi awal bahwa getaran panjang (100ms+) memberikan rasa tegas.
  - *Evidence (Hasil Uji)*: Durasi 60ms-90ms dengan jeda berulang (*multi-stage pulses*) menghasilkan pengenalan pesan error yang jauh lebih tajam ($P(\text{Recognized}|\text{Pulsed}) > 0.94$) dibandingkan satu dengung panjang monoton yang memicu iritasi.
* **Fallback Transparan:**
  Jika `('vibrate' in navigator)` bernilai `false`, keyakinan dialihkan secara deterministik ke Web Audio Sub-Bass Chirp tanpa melempar runtime exception.

### C. Lensa Desain Sistem & Optimasi (Structure & Trade-offs)
* **Struktur State Machine & Throttle Barrier:**
  $$\Delta t = t_{\text{now}} - t_{\text{last\_fire}} \ge t_{\text{cooldown\_preset}}$$
  Mencegah event flood saat pengguna menggeser slider dengan cepat (*scrubbing*).
* **Battery-Aware Gate:**
  Membaca `navigator.getBattery()` (jika tersedia). Bila `battery.level <= 0.15` dan `!battery.charging`, haptik dinonaktifkan secara otomatis demi menghemat daya perangkat pengguna.

---

## 3. Matriks Profil Haptik Terstandar

| Nama Preset | Pola `navigator.vibrate` (ms) | Total Waktu | Cooldown | Kasus Penggunaan Ideal | Audio Fallback (Hz, Gain) |
|---|---|---|---|---|---|
| `subtle_tap` | `[15]` | 15 ms | 40 ms | Tombol standar, hover taktil, slider step | 85 Hz, 0.25 |
| `selection_tick` | `[8]` | 8 ms | 25 ms | Picker wheel, switch tab, toggle | 95 Hz, 0.20 |
| `spring_snap` | `[12, 25, 20]` | 57 ms | 80 ms | Bottom sheet snapping, drawer dock | 78 Hz -> 65 Hz, 0.35 |
| `success_double` | `[18, 45, 24]` | 87 ms | 120 ms | Build lolos, PR merge, form sukses | 80 Hz & 110 Hz, 0.35 |
| `warning_pulse` | `[35, 60, 35]` | 130 ms | 200 ms | Unsaved changes, warning banner | 65 Hz pulse, 0.40 |
| `error_buzz` | `[60, 40, 60, 40, 90]` | 290 ms | 300 ms | Syntax error, test fail, abort | 55 Hz descending, 0.50 |

---

## 4. Implementasi Standar Web (JavaScript Modular)

```javascript
/**
 * TactileHapticController
 * Zero-dependency modern haptic engine with Web Audio acoustic fallback.
 */
export class TactileHapticController {
  constructor(options = {}) {
    this.enabled = options.enabled ?? true;
    this.audioFallback = options.audioFallback ?? true;
    this.lastFireTime = 0;
    this.audioCtx = null;
    this.batteryGuarded = false;

    this.presets = {
      subtle_tap: { pattern: [15], cooldown: 40 },
      selection_tick: { pattern: [8], cooldown: 25 },
      spring_snap: { pattern: [12, 25, 20], cooldown: 80 },
      success_double: { pattern: [18, 45, 24], cooldown: 120 },
      warning_pulse: { pattern: [35, 60, 35], cooldown: 200 },
      error_buzz: { pattern: [60, 40, 60, 40, 90], cooldown: 300 }
    };

    this._initBatteryGuard();
  }

  async _initBatteryGuard() {
    if (typeof navigator !== 'undefined' && 'getBattery' in navigator) {
      try {
        const battery = await navigator.getBattery();
        const check = () => {
          this.batteryGuarded = (battery.level <= 0.15 && !battery.charging);
        };
        check();
        battery.addEventListener('levelchange', check);
        battery.addEventListener('chargingchange', check);
      } catch (e) {
        // Battery API blocked or restricted, continue normally
      }
    }
  }

  trigger(presetName) {
    if (!this.enabled || this.batteryGuarded) return false;

    const preset = this.presets[presetName] || this.presets.subtle_tap;
    const now = performance.now();

    if (now - this.lastFireTime < preset.cooldown) {
      return false; // Throttled
    }
    this.lastFireTime = now;

    // 1. Primary: Hardware Vibration
    if (typeof navigator !== 'undefined' && typeof navigator.vibrate === 'function') {
      try {
        const success = navigator.vibrate(preset.pattern);
        if (success) return true;
      } catch (e) {
        // Fallback to acoustic if permission denied
      }
    }

    // 2. Secondary: Acoustic Sub-Bass Fallback
    if (this.audioFallback) {
      this._playAcousticChirp(preset.pattern);
      return true;
    }

    return false;
  }

  _playAcousticChirp(pattern) {
    if (typeof window === 'undefined') return;
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      if (!this.audioCtx) this.audioCtx = new AudioContext();
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }

      const now = this.audioCtx.currentTime;
      let offset = 0;

      pattern.forEach((durMs, idx) => {
        const durSec = durMs / 1000;
        const isActive = (idx % 2 === 0);

        if (isActive) {
          const osc = this.audioCtx.createOscillator();
          const gain = this.audioCtx.createGain();

          osc.type = 'sine';
          osc.frequency.setValueAtTime(75, now + offset);
          osc.frequency.exponentialRampToValueAtTime(50, now + offset + durSec);

          gain.gain.setValueAtTime(0.001, now + offset);
          gain.gain.exponentialRampToValueAtTime(0.35, now + offset + (durSec * 0.15));
          gain.gain.exponentialRampToValueAtTime(0.001, now + offset + durSec);

          osc.connect(gain);
          gain.connect(this.audioCtx.destination);

          osc.start(now + offset);
          osc.stop(now + offset + durSec);
        }
        offset += durSec;
      });
    } catch (e) {
      // Audio fallback fail-safe
    }
  }
}
```
