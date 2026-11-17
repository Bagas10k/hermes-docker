---
name: advanced-gpu-aware-design-system
description: "Use when creating interfaces. GPU-aware design system & UI."
---

# Hermes Advanced GPU-Aware Design System Engineer

Default art direction & workflow GPU-aware saat membuat antarmuka. Versi lengkap: `references/full-guide.md`.

## Precedence
- Brief eksplisit, brand guideline, kebutuhan fungsional/keamanan, dan WCAG mengalahkan default ini. Referensi visual pengguna mengalahkan template lama; jangan paksa semua jadi dark navy diorama atau menjiplak aset/maskot brand luar.
- Ikuti `ui-ux-execution-standard` (scope, perilaku, aksesibilitas, verifikasi runtime); terapkan `ui-layout-intelligence`, `typography-ux-copy`, `color-intelligence`, `ui-ux-design-vault`, `design-qa-gatekeeper` sebelum efek spasial/GPU.
- Motion adalah dimensi UX inti: rancang keyframe sejak awal; uji komposisi statis, motion, dan interaksi terpisah; sesuaikan untuk reduced motion/performa tanpa menghilangkan kendali pengguna; hindari partikel tak perlu atau motion abadi. Muat `motion-principles`, `motion-visual-systems`, `creative-motion-lab` saat relevan.
- 3D tidak pernah wajib di alur transaksional (checkout, billing, form, grid data padat): tetap 2D bersih dan cepat.
- `skills.auto_load` tidak diwarisi child: sertakan kontrak visual ini di context delegasi.

## Grammar dimensional
- **Mode A Tactile 2.5D** (story/product): hero asimetris, kartu miring -1.5° s/d 2°, hard offset shadow, occlusion berlapis, konektor SVG; murni HTML+CSS+SVG tanpa canvas/WebGL (`references/dimensional-composition.md`). **Mode B Spatial Isometric** (topologi/dashboard): proyeksi paralel (`perspective: none`), diorama 3D bertumpuk, label billboard tegak.
- Larangan: emoji sebagai ikon/badge/dekorasi (pakai SVG/glyph aksesibel); gradien teks pelangi/neon; kicker badge ornamental tanpa makna. Aksen semantik terbatas (status beacon, border halus, route trace) dengan kontras WCAG terverifikasi.
- Data dummy hanya sintetis netral ("Cluster Node-04", "Warehouse Zone B", "Latency: 18ms").

## Fakta teknis
"GPU Style Sheets" hanya istilah informal, bukan standar W3C. `transform`/`opacity` ramah compositor tetapi backing GPU tidak dijamin (cek trace DevTools). Konteks canvas terkunci ke satu API (`webgl2`/`webgpu`/`2d`) — pilih satu tier + fallback DOM/SVG. Batas DPR (`Math.min(devicePixelRatio, 2)`) dan 8–16 layer compositor adalah titik awal yang bisa disetel, bukan standar.

## Workflow wajib
1. **Discover** framework (React, Next, Vue, Blade, HTML), token, brand, batasan aksesibilitas.
2. **Specify** arah visual, taksonomi token, breakpoint, inventaris komponen, kontrak fallback 2D; interaksi stateful punya kontrak motion 4 keyframe (`initial`, `intermediate`, `review`, `final`) dengan identitas objek terjaga.
3. **Pilih tier:** HTML+CSS → SVG → CSS 3D → Canvas/WebGL/WebGPU hanya bila perlu atau diminta (permintaan eksplisit = deliverable wajib; jangan diam-diam diganti CSS), selalu dengan fallback (`references/usage-recipes.md`, `references/motion-keyframe-webgpu.md`).
4. **Arsitektur:** token; efek 3D/canvas terpisah dari logika transaksi; modal di luar container 3D; DOM semantik untuk interaksi/teks; canvas dekoratif `aria-hidden="true"` + pointer-events none.
5. **Implementasi** mengikuti konvensi framework tanpa migrasi tak perlu; vertical slice dengan ilustrasi statis sebelum hidrasi (`.motion-ready`). Progressive enhancement kontrol form: kontrol native tetap sumber kebenaran (`name`, `id`, `type`, validasi, nilai submit); inisialisasi juga kontrol yang disisipkan dinamis.
6. **Verifikasi** lint/unit/integrasi/aksesibilitas lalu uji target asli di browser nyata, termasuk jalur aksi→hasil, keyboard/fokus, constraint, propagasi event, fallback. Fixture sintetis = preview, bukan verifikasi integrasi; yang tidak teruji dilaporkan unverified. Revisi visual: satu render dasar, tanpa loop screenshot multi-lebar kecuali diminta; screenshot diambil dari halaman target asli.
7. **Ukur** dengan trace DevTools; metrik hardware yang tidak dijalankan ditandai NOT RUN; jangan mengarang FPS atau klaim speedup universal.
8. **Serahkan** perubahan source, token, bukti tes, batasan, catatan rollback.

## Guardrails
- `prefers-reduced-motion` (WCAG 2.2 SC 2.3.3 AAA): hentikan motion nonesensial (auto-rotate, transisi) tanpa harus menghapus scene 3D statis; sediakan layout 2D alternatif.
- Jangan beri background opak pada container (auth, loading, error, app shell) di atas canvas/mesh ambient; pakai transparan + `backdrop-filter: blur(...)` agar gerak tetap terlihat.
- Floating pill/dynamic island: lepas dari tepi (`margin: auto; width: calc(100% - X); border-radius: 9999px`) + shadow elevasi, bukan bar full-width.
- Landing/auth zero-scroll: clamp ke `100dvh` dengan centering flex/grid, logo tidak diduplikasi di viewport yang sama, ganti raster berat dengan badge vektor/DOM ringan + spring/parallax halus.
- Swiss brutalist: grid badge modular tanpa item yatim (`grid-cols-3 sm:grid-cols-6` untuk 6 item); aset 3D clay/pastel dibingkai chip HUD monospace (`NODE: ...`, `FEED: LIVE`), border gelap 1.5–2px, `contrast-[1.05]`; tekan/hover via transform CSS (`active:translate-x-0.5 active:translate-y-0.5 active:shadow-none`, `hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[5px_5px_0px_#111]`) di atas hard shadow `4px 4px 0px #111`, 60 FPS tanpa beban CPU.
- Motion finite dengan sebab/aksi/hasil jelas; berhenti di review gate, jangan auto-approve state transaksional. Hentikan rAF saat `document.hidden`/offscreen/disposed; WebGPU tangani `device.lost` → fallback SVG/CSS 2D.
- Canvas `aria-hidden="true" tabindex="-1"`; kontrol = `<button>` semantik dengan `aria-pressed="true|false"` (bukan `aria-selected`) + `focus-visible`.
- Render on-demand dengan dirty flag (`requestRenderIfNotRequested`), tanpa loop idle 60fps. Dispose geometry/material/texture milik sendiri saat unmount (`material.dispose()` tidak membuang texture; `renderer.info.memory` tidak harus 0).
- Delegasi: bagi per berkas independen, ownership & kontrak tes jelas, merge setelah verifikasi.

## Reference router
`references/`: `usage-recipes.md` (resep; §7 mini-demo live dengan seeded data dan gate verifikasi), `dimensional-composition.md`, `verified-sources.md`, `motion-keyframe-webgpu.md`, `gpu-rendering.md`, `design-system.md`, `frameworks.md`, `workflows.md`, `quality-gates.md`, `spatial-3d-direction.md`, `agent-contract.md`, `full-guide.md`. Aset `assets/tokens.example.json`; contoh `examples/spatial-interface.html`; skrip `python3 <skill-dir>/scripts/self_check.py`, `token_audit.py`, `css_motion_audit.py`.
