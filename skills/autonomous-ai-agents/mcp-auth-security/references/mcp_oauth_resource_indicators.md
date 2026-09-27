# Spesifikasi Arsitektur MCP OAuth Resource Indicators & Confused-Deputy Defense

## 1. Landasan Masalah: Serangan Confused Deputy pada MCP
Ketika LLM agen otonom mengorkestrasi banyak MCP Server (misalnya MCP Filesystem, MCP Database, MCP Web Fetcher), risiko keamanan paling kritis timbul saat token otorisasi yang diberikan oleh pengguna bersifat *ambient* (global) tanpa pembatasan audiens.

Skenario eksploitasi Confused-Deputy:
1. Agen memperoleh token OAuth umum dengan scope luas (`read`, `write`, `execute`).
2. Agen mengirimkan token ini ke MCP Web Fetcher untuk mengambil data dari internet.
3. MCP Web Fetcher (yang mungkin jahat atau dikompromikan) mengambil token inbound tersebut, lalu memanggil MCP Database atau MCP Filesystem dengan menyamar sebagai Agen/Pengguna.
4. MCP Database menerima token tersebut karena tanda tangan kriptografisnya valid, mengeksekusi operasi berbahaya tanpa izin.

## 2. Solusi Standar: RFC 8707 Resource Indicators & RFC 9728
Solusi arsitektural resmi:
1. **RFC 8707 (Resource Indicators for OAuth 2.0):**
   - Klien (Agen) saat meminta token ke Authorization Server wajib menyertakan parameter `resource=<canonical_mcp_server_uri>`.
   - Token akses yang diterbitkan mengikat claim audiens (`aud`) secara ketat ke URI kanonikal server target:
     $$\text{aud} = \text{canonical\_resource\_uri}$$
   - MCP Server penerima wajib memvalidasi:
     $$\text{claims}[\text{"aud"}] \equiv \text{self.canonical\_resource\_uri}$$
     Jika tidak cocok, permintaan ditolak mentah-mentah (HTTP 403 Forbidden).

2. **RFC 9728 (OAuth 2.0 Protected Resource Metadata):**
   - Setiap MCP Server mempublikasikan metadata otentikasi di `/.well-known/oauth-protected-resource`, mendeklarasikan `resource` identifier kanonikal, scope yang didukung, dan Authorization Server yang dipercaya.

3. **Invarian Mutlak: Anti-Token Passthrough:**
   - MCP Server DILARANG KERAS meneruskan token akses inbound ke API hilir (*downstream APIs*).
   - Layanan hilir harus diakses menggunakan kredensial independen atau token baru hasil pertukaran (Token Exchange RFC 8693) dengan audiens hilir yang tepat.

## 3. Matriks Keputusan Evaluasi Bukti (Bayesian Update)
- **Prior Belief:** Penggunaan token Bearer statis atau API key global cukup aman untuk lingkungan internal.
- **Evidence:** Dalam topologi multi-agent di mana tools dapat dikembangkan oleh pihak ketiga atau berjalan di kontainer terpisah, kebocoran token global memicu kompromi lateral 100% pada seluruh resource pengguna.
- **Posterior:** Mandatory per-resource audience token binding (RFC 8707) menurunkan probabilitas serangan lateral confused-deputy menjadi 0.
