# Arsitektur & Spesifikasi Formal MCP Dynamic Tool Federation & Capability Scoping

## 1. Landasan Teori & Batasan Matematis

Dalam ekosistem Multi-MCP Server (misal 15 server dengan total 250+ tools), memuat seluruh schema JSON ke context window sistem menimbulkan dua hambatan fatal:
1. **Context Pollution & Token Bloat**: 250 tools menghabiskan rata-rata 50.000 hingga 120.000 tokens hanya untuk system prompt sebelum instruksi pengguna dibaca.
2. **Distraction & Attentional Degradation**: Akurasi pemilihan tools anjlok seiring bertambahnya kandidat (fenomena *scale degradation* yang dibuktikan pada riset RAG-MCP dan MCPBench).

### Formulasi Model Kausal
$$P(\text{Task Success}) = P(\text{Route Correct}) \times P(\text{Schema Compatibility}) \times P(\text{Exec Success}) \times P(\text{Safety Guard})$$

Menurut Hukum Amdahl untuk latensi agen ($S_{\text{latency}} = \frac{1}{(1-p) + p/s}$), memotong langkah serial round-trip natural language tool calling dengan *programmatic tool calling* dan *deferred schema retrieval* memberikan akselerasi latensi hingga 65% ($p \approx 0.7$).

## 2. Arsitektur Komponen

```
                  [User Request / Goal]
                           │
                           ▼
          ┌──────────────────────────────────┐
          │  Tier-1: Compact Index Catalog   │ (Tool ID + Ringkasan 1 Baris)
          │  ~1.2k Tokens Total (~95% Saved) │
          └──────────────────────────────────┘
                           │
            (Dynamic Tool Search / Regex)
                           │
                           ▼
          ┌──────────────────────────────────┐
          │ Tier-2: Scope & Capability Gate  │ (OAuth 2.1 RFC 8707 / RFC 9728)
          │ (Read / Write / Admin Scopes)    │
          └──────────────────────────────────┘
                           │
           [Authorized? YES] ─── NO ──► [Step-Up Challenge: 403 Insufficient Scope]
                           │
                           ▼
          ┌──────────────────────────────────┐
          │ Tier-3: On-Demand Schema Resolve │ (Draft 2020-12 / Draft-07 JSON Schema)
          │ (Hydrated into Model Context)    │
          └──────────────────────────────────┘
                           │
                           ▼
          ┌──────────────────────────────────┐
          │ Tier-4: Multi-Transport Runner   │
          │ (stdio / Streamable HTTP Modern) │
          └──────────────────────────────────┘
```

## 3. Protokol Stateful Tools & Handles

Pada spesifikasi modern MCP (`2026-07-28`), tidak ada session per-koneksi tersirat. Server yang memerlukan status lintas panggilan (misal koneksi transaksi database, cart belanja, browser session) menggunakan pola **State Handle**:
- Tool pencipta mengembalikan identifier tak-tembus pandang (*opaque handle*, e.g., `mcp_h_<uuid>`).
- Parameter pemanggilan berikutnya menyertakan handle tersebut.
- Server memvalidasi kepemilikan handle, batas waktu (TTL), dan otoritas token.

## 4. Matriks Transpor & Kompatibilitas Era

| Aspek | Modern (`2026-07-28`+) | Legacy (`2025-11-25` dan sebelumnya) |
|---|---|---|
| Negosiasi Versi | Per-request metadata `_meta` + Header HTTP | `initialize` handshake di awal sesi |
| Discovery | `server/discover` RPC | Disimpulkan dari hasil handshake `initialize` |
| HTTP Transport | Streamable HTTP (Single endpoint POST + SSE) | HTTP + SSE terpisah (Deprecated) |
| Caching | Server menyertakan `ttlMs` dan `cacheScope` | Klien menyimpulkan secara heuristik |
