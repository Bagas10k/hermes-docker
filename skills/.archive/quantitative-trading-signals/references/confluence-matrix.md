# Matriks Konfluensi & Aturan Eksekusi Sinyal Trading

Tabel konfluensi teknikal terverifikasi untuk deteksi peluang trading otomatis pada XAU/USD (Gold) dan BTC/USDT (Bitcoin).

## 1. Matriks Sinyal BUY (Long)

| Kondisi Teknikal | Indikator Utama | Nilai Ambang Batas | Bobot Konfluensi |
|---|---|---|---|
| **Oversold Reversal** | RSI (14) | ≤ 32.0 (Ekstrem) & melengkung naik | 35% |
| **EMA Ribbon** | EMA 20 vs EMA 50 | EMA 20 memotong atau di atas EMA 50 | 25% |
| **Volume Confirmation** | Volume Ratio | ≥ 1.8x dari MA 20 Volume | 20% |
| **Key Level Interaction** | Support Zone (S1/S2) | Jarak harga ≤ 0.5% dari level support | 20% |
| **SMC Market Structure** | BOS / CHoCH | Terbentuk Higher High (HH) & Higher Low (HL) | Konfirmasi Tambahan |

> **Trigger Eksekusi:** Akumulasi bobot konfluensi ≥ 70% dengan Rasio R:R ≥ 1:1.7.

---

## 2. Matriks Sinyal SELL (Short)

| Kondisi Teknikal | Indikator Utama | Nilai Ambang Batas | Bobot Konfluensi |
|---|---|---|---|
| **Overbought Rejection** | RSI (14) | ≥ 68.0 (Ekstrem) & melengkung turun | 35% |
| **EMA Ribbon** | EMA 20 vs EMA 50 | EMA 20 memotong atau di bawah EMA 50 | 25% |
| **Volume Confirmation** | Volume Ratio | ≥ 1.8x dari MA 20 Volume (Sell Volume) | 20% |
| **Key Level Interaction** | Resistance Zone (R1/R2) | Jarak harga ≤ 0.5% dari level resistance | 20% |
| **SMC Market Structure** | BOS / CHoCH | Terbentuk Lower High (LH) & Lower Low (LL) | Konfirmasi Tambahan |

> **Trigger Eksekusi:** Akumulasi bobot konfluensi ≥ 70% dengan Rasio R:R ≥ 1:1.7.

---

## 3. Parameter Kalkulasi Stop Loss & Take Profit (ATR Dynamic)

| Gaya Trading | Stop Loss (SL) | Take Profit 1 (TP1) | Take Profit 2 (TP2) | R:R Target |
|---|---|---|---|---|
| **⚡ Scalp (5m-15m)** | Entry ± (0.9 x ATR) | Entry ∓ (1.5 x ATR) | Entry ∓ (2.2 x ATR) | 1 : 1.7 s/d 1 : 2.0 |
| **🌊 Swing (1h-4h)** | Entry ± (1.4 x ATR) | Entry ∓ (2.6 x ATR) | Entry ∓ (4.0 x ATR) | 1 : 2.5 s/d 1 : 3.5 |

---

## 4. Logika Bypass Cooldown

- **Cooldown Normal:**
  - Scalp: 15 menit.
  - Swing: 60 menit.
- **Bypass Instan (Kirim Segera):**
  - Terjadi pembalikan arah instan (misal status sebelumnya `BUY` dan candle baru mengonfirmasi setup `STRONG SELL`).
  - Terjadi deviasi harga ekstrem pasca-news (> 1.5% dalam 1 candle).

---

## 5. Alur Siklus Hidup Eksekusi Demo Auto-Trader (Silent Execution)

1. **Penerimaan Sinyal:** Evaluasi konfluensi selesai → menghasilkan payload `symbol`, `action`, `entryPrice`, `stopLoss`, `takeProfit1`.
2. **Pencegahan Over-leverage:** Cek `getActiveTrades()`. Jika instrumen sudah memiliki posisi `OPEN`, lewati pembukaan ganda.
3. **Eksekusi Akun Demo di Balik Layar:** Buka posisi via `tradingEngine.openTrade()` dengan alokasi risiko virtual tetap (misal $1,000 margin) dan lekatkan parameter SL serta TP1 secara senyap (silent).
4. **Transmisi Sinyal Murni:** Kirimkan HANYA pesan sinyal teknikal murni ke grup Telegram terdedikasi tanpa teks demo/tiket order.
5. **Pemantauan Tick Real-Time:** Mesin mengevaluasi setiap tick candle untuk mengawasi level SL/TP secara otomatis.
6. **Pencatatan Hasil & Pembelajaran Mandiri:** Saat posisi ditutup (Take Profit / Stop Loss / Trailing Stop), sistem mencatat Realized PnL dan metrik win-rate ke SQLite untuk evaluasi model self-learning, tanpa membanjiri grup publik dengan notifikasi penutupan demo.
