# Hermes Agent Docker Blueprint

Paket cetak biru (*blueprint*) Docker mandiri untuk menjalankan Hermes Agent lengkap dengan Web Dashboard, gateway perpesanan, dan penyimpanan proyek terisolasi.

## Struktur Direktori
- `Dockerfile`: Ekstensi dari image resmi `nousresearch/hermes-agent:latest` dengan paket utilitas tambahan.
- `docker-compose.yml`: Orkestrasi kontainer dengan port forwarding dan volume mounting.
- `run.sh`: Skrip utilitas 1-klik untuk inisialisasi, build, start, stop, dan ekspor image.
- `skills/`: Pustaka keahlian kustom bawaan agen.
- `workspace/`: Direktori kerja untuk proyek-proyek Git.

## Cara Menjalankan di Server / Komputer Baru

1. **Clone Repositori:**
   ```bash
   git clone git@github.com:Bagas10k/hermes-docker.git
   cd hermes-docker
   ```

2. **Inisialisasi & Konfigurasi:**
   ```bash
   ./run.sh init
   nano .env  # Masukkan token Telegram dan API Key Anda
   ```

3. **Jalankan Kontainer:**
   ```bash
   ./run.sh start
   ```

4. **Akses Dashboard:**
   Buka peramban di `http://<ip-server>:9119`

5. **Membuka Terminal Hermes Interaktif:**
   ```bash
   ./run.sh cli
   ```
