---
name: self-hosted-vpn-and-tunneling
description: Use when setting up VPNs, WireGuard, or Tailscale.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [vpn, wireguard, tailscale, cloudflare-tunnel, networking, adblock, exit-node]
    related_skills: [cloudflare-tunnel-sentinel, client-vps-selfhealing-deployment]
---

# Self-Hosted VPN and Tunneling Ops

Prosedur instalasi, konfigurasi, dan troubleshooting VPN mandiri (WireGuard, Tailscale) serta tunneling ingress aman di lingkungan Linux/VPS, khususnya saat server berada di balik NAT/router tanpa port forwarding publik.

## Decision Matrix: WireGuard vs Tailscale

| Skenario Jaringan | Solusi Rekomendasi | Alasan & Mekanisme |
|---|---|---|
| VPS Cloud dengan IP Publik Dedicated | **WireGuard (`wg-easy`)** | Koneksi langsung via UDP kernel, latency paling rendah, independen tanpa dependensi akun pihak ketiga. |
| Server Rumah/LAN di balik NAT / CGNAT tanpa Port Forward | **Tailscale Exit Node** | Menggunakan DERP/STUN hole-punching; tembus NAT otomatis tanpa perlu membuka port router. |
| Web UI manajemen VPN di balik firewall | **Cloudflare Tunnel (`--edge-ip-version 4`)** | Ekspos HTTPS aman tanpa port publik terbuka di firewall. |

## Procedure

### 1. Deteksi Topologi Host & NAT
Sebelum menjalankan WireGuard, verifikasi apakah host memiliki IP publik langsung atau berada di balik NAT:
```bash
ip -br addr
curl -4 -s ifconfig.me
```
- Jika IP antarmuka jaringan utama (misal `ens34`) adalah privat (`192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`, atau CGNAT `100.64.0.0/10`), periksa apakah router mendukung UPnP: `upnpc -s`.
- Jika UPnP gagal dan akses router tertutup: **Gunakan Tailscale Exit Node**, bukan WireGuard langsung.

### 2. Tailscale Exit Node Setup (NAT-Bypass VPN)
1. **Instalasi:**
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   ```
2. **Aktifkan IP Forwarding di Kernel:**
   ```bash
   echo "net.ipv4.ip_forward = 1
   net.ipv6.conf.all.forwarding = 1" | sudo tee /etc/sysctl.d/99-tailscale.conf
   sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
   ```
3. **Mulai Layanan sebagai Exit Node:**
   ```bash
   sudo tailscale up --advertise-exit-node
   ```
4. **Approve di Admin Console:**
   - Kunjungi `login.tailscale.com/admin/machines`.
   - Pada mesin server, klik **Edit route settings** -> aktifkan **Use as exit node**.
5. **Koneksi Klien (HP / Laptop):**
   - Install Tailscale di perangkat klien, login ke akun yang sama, dan pilih server ini pada menu **Exit Node**.
6. **Verifikasi Jalur & Latensi P2P (Diagnostic):**
   ```bash
   sudo tailscale status
   sudo tailscale ping <PEER_TAILSCALE_IP>
   ```
   - Status `active; direct <ip>:<port>` menandakan NAT hole-punching berhasil (jalur P2P langsung sub-60ms).
   - Status `relay <node>` menandakan koneksi melewati relay DERP (sedikit lebih lambat, biasanya karena firewall symmetric).
7. **Ad-Blocking & Anti-Sensorship di Tailscale (MagicDNS):**
   - Di `login.tailscale.com/admin/dns`, tambahkan **Nameserver Custom**: `94.140.14.14` dan `94.140.14.15` (AdGuard Public DNS).
   - Aktifkan toggle **Override local DNS**. Seluruh perangkat yang terhubung otomatis terbebas dari iklan dan sensor ISP tanpa konfigurasi manual di tiap HP.
8. **Private HTTPS & Tailscale Serve (Gembok Hijau Tanpa Port Publik):**
   - Di `login.tailscale.com/admin/dns`, aktifkan toggle **HTTPS Certificates** pada MagicDNS (mengizinkan provisioning sertifikat Let's Encrypt resmi untuk `*.ts.net`).
   - Ekpos web server lokal/cockpit privat langsung dengan sertifikat TLS valid otomatis:
     ```bash
     tailscale serve --bg <LOCAL_PORT>
     ```
   - Layanan langsung dapat diakses via `https://<node-name>.<tailnet-domain>.ts.net` di peramban klien tanpa *untrusted SSL warning*, 100% terlindung di dalam enkripsi mesh.

### 3. WireGuard Setup (`wg-easy`) dengan Ad-Blocking DNS
Jika IP publik langsung tersedia atau port forwarding UDP sudah aktif di router:
1. **Jalankan Container Docker:**
   ```bash
   docker run -d \
     --name=wg-easy \
     -e WG_HOST="<PUBLIC_IP>" \
     -e PASSWORD_HASH='<BCRYPT_HASH>' \
     -e WG_DEFAULT_DNS="94.140.14.14, 94.140.14.15" \
     -v ~/.wg-easy:/etc/wireguard \
     -p 51820:51820/udp \
     -p 51821:51821/tcp \
     --cap-add=NET_ADMIN \
     --cap-add=SYS_MODULE \
     --sysctl="net.ipv4.conf.all.src_valid_mark=1" \
     --sysctl="net.ipv4.ip_forward=1" \
     --restart unless-stopped \
     ghcr.io/wg-easy/wg-easy
   ```
2. **Ad-Blocking & Anti-Sensorship Instan (Ponytail Rule):**
   Jangan memasang container Pi-hole/AdGuard Home yang memakan RAM jika hanya butuh pemblokiran iklan umum. Cukup arahkan DNS WireGuard ke **AdGuard Public DNS** (`94.140.14.14, 94.140.14.15`). Domain iklan dibuang ke `0.0.0.0` dan sensor ISP terlewati.

### 4. Distribusi Konfigurasi ke Pengguna (Anti-Gagal)
Jangan hanya mengandalkan scan QR code atau download web UI:
- **Di Chat Telegram:** Izin media grup sering memblokir upload foto QR.
- **Di Web UI via Tunnel:** Endpoint download web UI sering gagal (500 Error) karena perbedaan origin cookie.
- **Prosedur:**
  1. Cetak isi teks `.conf` langsung di dalam blok kode Markdown agar pengguna bisa copy-paste via opsi "Create from scratch" di aplikasi WireGuard.
  2. Sajikan file `.conf` mentah melalui HTTP server sederhana yang ditunnelkan publik.

## Pitfalls & Lessons

- **WireGuard Blackhole Symptom (Tx Bertambah, Rx 0 B):** Jika status transfer di aplikasi HP menunjukkan data terkirim tetapi Rx tetap 0 B dan seluruh internet HP mati, ini adalah tanda pasti handshake gagal karena port UDP 51820 tertutup di router. `AllowedIPs = 0.0.0.0/0` membelokkan seluruh traffic ke antarmuka mati. Segera beralih ke Tailscale.
- **Mobile Exit Node Confusion (Orange Banner):** Pada aplikasi Tailscale Android/iOS, pengguna sering keliru memencet tombol "Run exit node" di HP-nya sendiri (muncul banner oranye "Exit node running on this device"). Selalu minta pengguna menekan tombol "Stop" pada banner HP tersebut, lalu arahkan mereka memilih server Linux (`ubuntu`) melalui menu titik tiga / Exit Nodes di aplikasi HP.
- **Cloudflare Quick Tunnel IPv6 Unreachable:** Perintah `cloudflared tunnel --url ...` tanpa parameter IP version akan mencoba resolusi IPv6 terlebih dahulu. Jika server tidak memiliki rute IPv6 publik, daemon langsung crash (`network is unreachable`). Selalu gunakan `--edge-ip-version 4`.
- **Private Web Microservice di Tailscale Interface:** Saat menjalankan server Python/Node.js lokal di antarmuka Tailscale (`100.x.x.x`), selalu implementasikan method `do_HEAD` di samping `do_GET` agar healthcheck `curl -I` tidak menghasilkan HTTP 501, dan setel `allow_reuse_address = True` untuk mencegah error bind port `Address already in use` saat restart cepat.
- **Carrier Quota Bypass Invariant:** Tidak ada VPN atau proxy perangkat lunak yang dapat memberikan internet gratis tanpa kuota/sinyal aktif dari operator seluler. Layer 1/2 transport radio BTS mutlak dibutuhkan agar paket data pertama dapat keluar dari perangkat menuju server.
