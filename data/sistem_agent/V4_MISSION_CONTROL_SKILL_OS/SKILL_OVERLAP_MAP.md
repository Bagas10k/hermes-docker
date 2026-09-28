# SKILL OVERLAP MAP — ANALISIS REDUNDANSI & KLUSTER SKILL
**Tanggal:** 28 September 2026  
**Auditor:** Hermes Agent  
**Dasar Analisis:** Analisis semantik dan fungsional dari 232 skill terpasang.

---

## 1. UNIQUE (Skill Spesialis Tanpa Duplikasi)
- `otak-koding` (835x) — Integrasi Obsidian vault lokal Mas Bagas.
- `hermes-agent` (126x) — Framework operasional Hermes core & tools.
- `sputarball-content-system` (42x) — Standar redaksi, kurasi foto HD, dan skor SputarBall.
- `instagram-publishing-automation` (129x) — Integrasi Meta Graph API Instagram.
- `design-md` — Integrasi Google DESIGN.md spec & linter CLI.
- `impeccable` — Linter deteksi anti-pattern visual dan AI-slop web.
- `himalaya` — CLI IMAP/SMTP email client.
- `cloudflare-tunnel-sentinel` — Edge ingress probe Cloudflare.

---

## 2. PARTIAL_OVERLAP (Fungsi Mirip tapi Berbeda Lapisan / Konteks)

### Kluster A: UI/UX & Web Design
- `bento-grid-spatial-composer` (Matematika spasial CSS bento)
- `ui-layout-intelligence` (Penalaran tata letak spasial AI)
- `ui-ux-design-vault` (Komponen tombol, card, dan layout)
- `popular-web-designs` (54 design system nyata Stripe/Vercel/Linear)
- `enterprise-ui-architecture` (Arsitektur sistem UI enterprise)
*Rekomendasi:* Canonical hulu: `design-md` + `bento-grid-spatial-composer`. Komponen: `ui-ux-design-vault`.

### Kluster B: Security & Auditing
- `mantis` & suite mantis-advise/calibrate/critic/dedupe/meta-agent/patch (Auditing mendalam kode repo)
- `defensive-web-security-audit` (Audit pasif eksternal web)
- `application-auth-security` (Implementasi auth/token aplikasi)
*Rekomendasi:* Gunakan `defensive-web-security-audit` untuk URL publik; gunakan `mantis` hanya untuk repositori lokal privat.

### Kluster C: Reasoning & DAG Systems
- `mathematical-problem-solving` (515x — Tiga mindset pemecahan masalah)
- `agent-causal-graph-reasoning` (Penalaran graf kausal Pearl)
- `agent-dag-task-splicing` (Topological replanning DAG)
- `hermes-cognitive-engine` (Autonomous task deep reasoning)
*Rekomendasi:* Jadikan `mathematical-problem-solving` sebagai doktrin utama; skill DAG dipanggil secara lazy-load hanya saat multi-step scheduling.

---

## 3. HIGH_OVERLAP / ROUTING_AMBIGUOUS (Rentan Membingungkan Agent Router)
1. `creative/genjutsu` vs `creative/ui-ux-design-vault`: Keduanya memuat pustaka animasi/komponen.
2. `hermes-autopilot` vs `hermes-cognitive-engine`: Peran riset otonom vs eksekusi mendalam.
3. `typography-ux-copy` vs `humanizer`: Penataan copywriting teknis vs pembersihan AI-isms. Keduanya sering dipanggil bersamaan; dapat digabungkan dalam satu skill-chain.

---

## 4. ACTION PLAN & DEPRECATION CANDIDATES
- **Haram Menghapus Sembarangan:** Tidak ada skill yang dihapus fisik.
- **Penyederhanaan Routing:** Buat routing table deterministik di Skill OS agar Hermes tidak bingung memilih antara 5 skill UI yang serupa.
