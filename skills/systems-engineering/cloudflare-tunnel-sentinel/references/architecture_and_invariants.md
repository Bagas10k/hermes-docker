# Cloudflare Tunnel Architecture & Operational Invariants

## 1. Arsitektur Ingress & Multi-Edge Anycast
Cloudflare Tunnel (`cloudflared`) membentuk 4 koneksi redundan (HA - High Availability) ke edge data center Cloudflare terdekat menggunakan protokol QUIC (HTTP/3 over UDP).
- **Zero Inbound Ports**: Tidak ada port ingress publik terbuka di firewall/router VPS. Seluruh koneksi bersifat outbound.
- **Anycast BGP Routing**: Trafik dari user di-proxy oleh edge Cloudflare dan diteruskan melalui terowongan terenkripsi ke VPS lokal.
- **Multi-Tunnel Active-Passive / Dual-Connector**:
  - `cf-tunnel-1`: Primary tunnel connector dengan token file tersimpan di `.chronicle-secrets/cf-token-1`.
  - `cf-tunnel-2`: Redundant connector untuk menjamin ketersediaan tinggi tanpa single point of failure.

## 2. Invarian Operasional & Health Check Probes
- **HTTP /ready Endpoint**:
  Endpoint `http://127.0.0.1:<port>/ready` mengembalikan payload JSON status 200 dan jumlah koneksi aktif:
  ```json
  {"status":200,"readyConnections":4,"connectorId":"..."}
  ```
  Jika status != 200 atau `readyConnections == 0`, tunnel dalam kondisi split-brain atau terputus dari edge.
- **Prometheus Metrics Endpoint**:
  Endpoint `http://127.0.0.1:<port>/metrics` mengekspos metrik:
  - `cloudflared_tunnel_ha_connections`: Jumlah koneksi edge aktif (standar: 4).
  - `quic_client_closed_connections`: Akumulator koneksi QUIC tertutup karena network switch atau packet loss.

## 3. Pitfalls & Anti-Patterns
1. **Hardcoding Token di Argumen CLI**:
   Dilarang keras menyematkan token Cloudflare di argumen baris perintah (`--token eyJh...`), karena token akan terekspos di tabel proses Linux (`ps aux`) dan log sistem. Selalu gunakan `--token-file /path/to/secret`.
2. **Missing Metrics Endpoint Flag**:
   Menjalankan `cloudflared tunnel run` tanpa flag `--metrics 127.0.0.1:<port>` mematikan observabilitas status koneksi, sehingga health check eksternal tidak dapat memverifikasi kesiapan tunnel secara deterministik.
3. **UDP Blocking di Firewall Keluar**:
   QUIC beroperasi di atas UDP port 7844. Jika firewall provider memblokir UDP keluar, `cloudflared` akan fallback ke TCP (HTTP/2), yang menaikkan latensi jabat tangan (handshake) dan rentan terhadap head-of-line blocking.
4. **WebSocket Upgrade Failure**:
   Pada antarmuka dashboard agen real-time (SSE/WebSocket), Cloudflare Edge memerlukan aktivasi fitur WebSocket di dashboard Cloudflare (Network -> WebSockets enabled) agar stream duplex tidak ditutup paksa setelah 100 detik.
