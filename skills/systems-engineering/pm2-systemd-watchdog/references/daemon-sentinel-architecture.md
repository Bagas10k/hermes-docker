# PM2 & Systemd Process Sentinel: Production Architecture & Hardening

Dokumen arsitektur dan rujukan rekayasa sistem untuk manajemen daemon persisten berbasis PM2 dan Systemd User Services pada infrastruktur VPS Linux.

---

## 1. Mekanisme & Karakteristik Lapis Eksekusi (Mechanism & Bounds)

Pada sistem operasi Linux Ubuntu (host 5.15), ada dua tingkatan supervisor proses yang umum digunakan:

1. **Systemd User Units (`systemctl --user`)**:
   - Berjalan langsung di bawah pengawasan kernel Linux cgroups (`/user.slice/user-1000.slice/user@1000.service`).
   - Sangat tangguh untuk supervisor proses primer (`hermes-gateway`, `dbus`, dsb).
   - Membutuhkan `loginctl enable-linger <user>` agar servis tetap berjalan saat sesi SSH/TTY logout.
   - Kebijakan restart: `Restart=always`, `RestartSec=5s`, batasan frekuensi `StartLimitBurst=5`, `StartLimitIntervalSec=60s`.

2. **PM2 Process Manager**:
   - Lapisan supervisor application-level yang fleksibel untuk Node.js, Python, dan shell wrappers.
   - Fitur monitoring CPU/RAM real-time, `max_memory_restart`, dan `exp_backoff_restart_delay`.
   - Mengelola logging standar (`~/.pm2/logs/`) yang perlu dipasangkan dengan `pm2-logrotate` agar tidak memakan disk space.

---

## 2. Invarian Operasional & Hardening

### A. Memory Leak Circuit Breaker (`max_memory_restart`)
Proses yang memproses tugas machine learning atau browser headless (misalnya `vision-qc-engine` atau PyTorch scorer) dapat mengalami fragmentasi memori. 
- Aturan konfigurasi `ecosystem.config.js`:
  ```javascript
  module.exports = {
    apps: [{
      name: "vision-qc-engine",
      script: "server.py",
      interpreter: "python3",
      max_memory_restart: "750M",
      exp_backoff_restart_delay: 2000,
      min_uptime: "30s",
      max_restarts: 10
    }]
  };
  ```

### B. Anti-Crash Amplification & Exponential Backoff
Proses yang gagal terkoneksi ke upstream API (misalnya Telegram / OpenAI) tidak boleh restart tanpa jeda. Tanpa backoff, restart loop memicu lonjakan CPU 100% dan pencemaran log disk ribuan baris per detik.
- Setel `exp_backoff_restart_delay: 1500` (jeda eksponensial 1.5s -> 3s -> 6s -> 12s ...).

### C. Orphan Process Cleanup
Ketika PM2 melakukan restart pada skrip yang memicu sub-process (seperti Puppeteer Chromium), sinyal `SIGINT` / `SIGTERM` harus diteruskan ke process group atau dibersihkan:
- Gunakan `kill_timeout: 5000` di PM2 untuk memberi waktu graceful shutdown.
- Jalankan pemeriksaan orphan berkala:
  ```bash
  ps -ef | grep -E "chromium|chrome|python" | grep defunct
  ```

### D. Systemd User Lingering Invariant
Pastikan user lingering aktif:
```bash
loginctl show-user ubuntu | grep Linger
# Wajib: Linger=yes
```
Jika `no`, aktifkan dengan:
```bash
loginctl enable-linger ubuntu
```

---

## 3. Protokol Pemulihan & Audit Cepat

1. **Audit Terpadu**:
   Gunakan script `sentinel_audit.py` untuk mendapatkan potret kondisi PM2 dan Systemd secara bersamaan tanpa roundtrip manual.
2. **Restart Terisolasi**:
   Dilarang melakukan `pm2 restart all` secara massal karena dapat memicu starvation I/O dan lonjakan CPU. Lakukan restart spesifik: `pm2 restart <id|name>`.
3. **Penyimpanan State Permanen**:
   Setelah menambah atau memodifikasi proses PM2:
   ```bash
   pm2 save
   ```
