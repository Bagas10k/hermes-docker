---
name: quantitative-trading-signals
title: Quantitative Trading Signals & Market Surveillance
description: "Use when building real-time trading signal alert engines."
author: Hermes Agent
version: 1.0.0
tags: [trading, crypto, forex, technical-analysis, signals, automated-alerts, market-surveillance]
---

# Quantitative Trading Signals & Market Surveillance

Pedoman rekayasa arsitektur untuk membangun mesin pemantau pasar otonom 24/7 dan generator sinyal trading real-time (khususnya aset volatil seperti XAU/USD dan BTC/USDT) tanpa mencemari sistem aplikasi lainnya.

## 1. Prinsip Isolasi Sistem (Zero Contamination)
- **Haram Bercampur:** Modul trading, pemantau harga, kalkulator teknikal, dan notifikasi sinyal WAJIB hidup di dalam direktori proyek trading tersendiri (misal: `trading-training-platform`).
- **Dilarang keras** menumpangkan logika trading ke dalam modul CMS warta, scraper berita, atau web portal umum.
- **Resource Boundary:** Gunakan daemon terdedikasi (misal PM2 proses mandiri) dengan pemantauan memori ketat dan koneksi SQLite WAL terpisah (`trading.db`).

## 2. Pipa Data Real-Time (Ultra-Low Latency)
- **Crypto (BTC/USDT, ETH, SOL):** Gunakan WebSocket publik Binance (`wss://stream.binance.com:9443`) untuk kline dan bookTicker tanpa limitasi kuota berbayar.
- **Gold / Forex (XAU/USD):** Gunakan feed Binance Futures 100ms (`fapi.binance.com`) atau proxy likuiditas emas (PAXG/XAU) dengan polling aktif 100ms - 1s untuk menjaga sinkronisasi pergerakan harga dunia secara instan.

## 3. Matriks Konfluensi Multi-Indikator
Jangan pernah memicu sinyal hanya berdasarkan satu indikator tunggal. Sinyal valid membutuhkan minimal **3 konfluensi teknikal**:
1. **EMA Ribbon Trend Alignment (20, 50, 200):**
   - BUY: EMA 20 > EMA 50 > EMA 200 (atau harga menembus ke atas EMA ribbon).
   - SELL: EMA 20 < EMA 50 < EMA 200 (atau harga breakdown ke bawah EMA ribbon).
2. **RSI Momentum & Extreme Reversal (14):**
   - Rebound BUY: RSI ≤ 32 (Oversold extreme) yang mulai melengkung naik.
   - Rejection SELL: RSI ≥ 68 (Overbought extreme) yang mulai melengkung turun.
   - Trend Continuation: RSI 45 - 60 dengan akselerasi volume.
3. **Volume Surge Filter:**
   - Wajib konfirmasi lonjakan volume ≥ 1.8x dari rata-rata volume (MA 20) untuk memvalidasi minat institusional / likuiditas nyata.
4. **Smart Money Concepts (SMC) & Struktur S&R:**
   - Konfirmasi penembusan struktur (*Break of Structure* / BOS) atau perubahan karakter tren (*Change of Character* / CHoCH) pada level Support & Resistance kunci.

## 4. Arsitektur Hybrid (Scalping vs. Swing)
Sistem memisahkan strategi berdasarkan horizon waktu trading:
- **⚡ Scalping & Intraday (5M - 15M):**
  - Target: Reaksi cepat, volume spike, micro S&R bounce/breakout.
  - SL: 0.9 - 1.1 x ATR. TP1: 1.4 - 1.6 x ATR. TP2: 2.0 - 2.4 x ATR.
  - R:R minimal 1 : 1.7. Cooldown: 15 menit. Durasi: 15m - 2 jam.
- **🌊 Swing Trading (1H - 4H):**
  - Target: Gelombang tren makro, SMC BOS, major S&R.
  - SL: 1.4 - 1.6 x ATR di balik swing high/low. TP1: 2.5 - 2.8 x ATR. TP2: 4.0 x ATR.
  - R:R minimal 1 : 2.5 s/d 1 : 3.5. Cooldown: 60 menit. Durasi: 1 - 3 hari.

## 5. Protokol Anti-Spam & Deduplikasi Sinyal
- **Cooldown Jeda Waktu:** Terapkan pembatasan waktu antar sinyal untuk instrumen dan gaya trading yang sama (`symbol_type`).
- **Filter Deviasi Harga:** Jika waktu cooldown terlewati namun harga belum bergeser signifikan (< 0.3% untuk scalping, < 0.8% untuk swing), tahan sinyal agar tidak membanjiri notifikasi pengguna.
- **Reversal Bypass:** Jika terjadi pembalikan arah instan (misal dari BUY berbalik tajam menjadi SELL terkonfirmasi), jeda cooldown WAJIB di-bypass secara otomatis.

## 6. Format Pengiriman Notifikasi & Rute Saluran (Zero-Clutter)
- **Rute Saluran Terdedikasi (Sterilisasi Chat Pribadi):** Sinyal trading DILARANG dialirkan ke chat pribadi (DM) jika pengguna telah menyiapkan grup atau channel khusus (konfigurasikan via `TELEGRAM_SIGNAL_CHAT_ID` / default ke supergroup BAgent). Chat pribadi wajib tetap bersih untuk percakapan instruksi.
- **Format Sinyal Murni (Zero Fluff & No Noise):** Pesan sinyal yang dikirimkan ke grup/saluran publik WAJIB MURNI menyajikan data teknikal actionable: Simbol instrumen, gaya trading (⚡ Scalping / 🌊 Swing), aksi tegas (🟢 BUY / 🔴 SELL), harga entry, level Stop Loss (SL), Target TP 1 & TP 2, rasio R:R, poin konfluensi teknikal, dan estimasi durasi posisi.
- **Pemisahan Logika Pesan vs. Eksekusi Mesin:** DILARANG KERAS menyisipkan informasi tiket order demo, modal akun virtual, saldo, atau notifikasi penutupan posisi demo ke dalam pesan grup sinyal agar ruang komunitas/grup tetap berwibawa dan tidak terdistraksi log internal mesin.
- **Audit Basis Data:** Setiap sinyal yang dikirim wajib dicatat ke SQLite `trading_signals` lengkap dengan snapshot harga, waktu, payload konfluensi, dan status pengiriman.

## 7. Integrasi Otomasi Eksekusi Demo (Silent Paper Trading Bridge)
- **Eksekusi Senyap (Silent Execution):** Sinyal yang lolos validasi konfluensi otomatis dieksekusi secara otonom ke akun demo virtual (`tradingEngine.openTrade`) dengan alokasi risiko terukur (misal $1,000 atau 1-2% equity) di latar belakang tanpa spamming chat.
- **Anti-Overleverage:** Cegah pembukaan posisi ganda (*duplicate open positions*) pada instrumen yang sama jika order demo sebelumnya masih berstatus `OPEN`.
- **Manajemen SL/TP Otomatis:** Mesin mengevaluasi setiap tick candle untuk mengawasi level SL/TP secara presisi di basis data lokal `trading.db` dan jurnal performa. Hasil akhir (Win/Loss, Realized PnL) dicatat di database untuk evaluasi self-learning tanpa mencemari saluran sinyal publik.
