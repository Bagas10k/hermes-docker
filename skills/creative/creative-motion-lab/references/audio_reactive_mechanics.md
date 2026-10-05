# Audio Reactive Visual Flow: Mathematical & Architectural Mechanics

## 1. Web Audio API AnalyserNode & FFT Windowing
Web Audio API mengekspos `AnalyserNode` yang memproses sinyal audio domain waktu menjadi domain frekuensi menggunakan Fast Fourier Transform (FFT):
- **Baud / FFT Size**: $N = 128, 256, 512, 1024, 2048$. Default optimal untuk vibe visualizer adalah $N = 256$ atau $512$ (`frequencyBinCount = N / 2 = 128` bins).
- **Frekuensi per Bin**:
  $$\Delta f = \frac{f_s}{N}$$
  Pada sampling rate standar $f_s = 44.100\text{ Hz}$ dan $N = 512$, setiap bin merepresentasikan rentang lebar $\approx 86.13\text{ Hz}$.

## 2. Band Decomposition: Sub-bass, Bass, Mid, High
Spektrum pendengaran manusia bersifat logaritmik (Bark / Mel scale). Pembagian band diskrit:
1. **Sub-Bass (20 Hz - 60 Hz)**: Bin 0 s/d 1 pada $N=512$. Mengendalikan getaran skala kanvas (*screen shake* dan *radial pulse*).
2. **Bass (60 Hz - 250 Hz)**: Bin 1 s/d 3. Mengendalikan ledakan partikel (*particle impulse*) dan perpindahan vertex.
3. **Mid (250 Hz - 2.500 Hz)**: Bin 3 s/d 29. Mengendalikan rotasi, dispersi warna, dan geometri gelombang.
4. **Treble / High (2.500 Hz - 16.000 Hz)**: Bin 29 s/d 186. Mengendalikan kilatan partikel mikro (*sparkles*) dan aksen tepi.

## 3. Envelope Following & Ballistics Filter
Untuk mencegah getaran visual patah-patah (*jitter*), energi audio dihaluskan dengan ballistics asymmetric low-pass filter:
$$E_t = \begin{cases} E_{t-1} + \alpha_{\text{attack}} \cdot (x_t - E_{t-1}) & \text{jika } x_t > E_{t-1} \\ E_{t-1} + \alpha_{\text{release}} \cdot (x_t - E_{t-1}) & \text{jika } x_t \le E_{t-1} \end{cases}$$
Di mana:
- $\alpha_{\text{attack}} \approx 0.65$ (respons instan terhadap ketukan kick drum)
- $\alpha_{\text{release}} \approx 0.08$ (peluruhan lembut dan organik)

## 4. Algoritma Onset Detection (Spectral Flux)
Deteksi ketukan (*beat detection*) dihitung melalui fluks spektral positif diferensial:
$$\text{Flux}_t = \sum_{k=0}^{M-1} H(X_t[k] - X_{t-1}[k])$$
dengan $H(v) = \frac{v + |v|}{2}$ (half-wave rectification).
Ketika $\text{Flux}_t > \gamma \cdot \mu_{\text{flux}} + \lambda \cdot \sigma_{\text{flux}}$, ketukan kick terkonfirmasi secara deterministik.

## 5. Auto-Sleep & Zero Resource Drain Invariant
Jika intensitas audio $E_{\text{RMS}} < 0.001$ selama lebih dari 10 detik dan tidak ada interaksi kursor:
- Hentikan loop `requestAnimationFrame`.
- Turunkan thread CPU ke mode istirahat (0% CPU, 0% GPU).
- Bangunkan seketika via event `audioprocess` atau input keyboard/mouse.
