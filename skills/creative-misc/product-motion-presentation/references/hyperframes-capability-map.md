# Peta kemampuan HyperFrames (CLI 0.9.33)

Baca ini sebelum merancang adegan atau efek untuk video promo: ia memetakan jenis keluaran ke cara dan perintah HyperFrames. Aturan utamanya: cari dulu di registry (`catalog`) sebelum membuat efek sendiri; ambil unit terbesar yang cocok, lalu sunting.

Sumber T1: skill hyperframes, hyperframes-cli, hyperframes-registry. Jumlah item diambil dari `npx --yes hyperframes@0.9.33 catalog --json --type block|component` (cache lokal, 15 Nov 2026): 210 block, 238 component.

## 1. Apa yang bisa dibuat

| Jenis keluaran | Cara di HyperFrames | Contoh nama nyata | Sumber |
| --- | --- | --- | --- |
| Promo / launch produk | Alur hook, ketegangan, reveal, bukti, payoff, klaim, end card (20-45 dtk); hanya UI asli, tanpa mockup | `app-showcase`, `product-turntable`, `cta-close`, `cta-lockup`, `logo-outro`, `store-badge-lockup` | hyperframes/references/types/launch.md; catalog |
| Demo UI produk | Component product-demo (20 item) dan cursor (14 item) | `agent-cursor`, `browser-device-stage`, `device-frame-stage`, `before-after-wipe`, `ui-focus-zoom` | hyperframes-registry/SKILL.md; catalog |
| Slideshow / deck langsung | Skill `/slideshow`, disajikan lewat `hyperframes present` | (bukan block) | slideshow/SKILL.md |
| Caption / subtitle | `transcribe` menghasilkan waktu per kata, lalu gaya caption (16 component) | `caption-clip-wipe`, `caption-editorial-emphasis`, `caption-kinetic-slam`, `caption-highlight` | hyperframes/references/captions.md; catalog |
| Kinetic type / title card | Block title-card (13), component typography (36) | `canopy-part-title`, `kinetic-type-swap`, `kinetic-center-build`, `morph-text`, `split-flap-board`, `blur-in` | hyperframes-registry/SKILL.md; catalog |
| Chart / data | Block data (10); grafik digerakkan dari `onUpdate` tween GSAP | `bar-chart-race`, `data-chart`, `animated-bar-chart`, `chart-story`, `flowchart` | hyperframes/references/runtimes.md; catalog |
| Kode di layar | Block `code-*` 1920x1080 digerakkan `window.__TOKENS` | `code-diff`, `code-morph`, `code-typing`, `code-slice-hero` | hyperframes/references/film.md |
| Peta / tempat nyata | Citra satelit yang di-bake jadi MP4 (`scripts/bake-basemap.mjs`), vektor hanya untuk label | `world-map`, `us-map`, `spain-map`, `nyc-paris-flight` | hyperframes/references/film.md; catalog |
| 3D / shader / latar | Three.js, WebGPU, p5, canvas via event `hf-seek`; path tracing ada aturan sendiri | `aurora`, `blob`, `cosmic-orb`, `extruded-logo`, `carousel-orbit-1` | runtimes.md; path-tracing.md; catalog |
| Overlay / lower third | Block overlay (31) dan lower-third (13); kartu di atas talking head | `lt-clean-bar`, `camcorder-hud`, `editorial-flash-overlay`, `yt-lower-third` | overlays.md; hyperframes-registry/SKILL.md |
| Transisi | Block transition (33) + component transition-primitive (19) | `beat-freeze-cut`, `cinematic-zoom`, `whip-pan`, `whip-pan-cut`, `light-leak`, `zoom-through-transition` | hyperframes-registry/SKILL.md; catalog |
| Gerak kamera | Component camera (14) | `camera-shake`, `camera-scan-gate`, `camera-dolly-zoom`, `push-in`, `parallax-zoom`, `cursor-zoom-follow`, `drift-hold`, `rack-focus` | hyperframes-registry/SKILL.md; catalog |
| Tekstur / partikel | Component texture/effect; grade footage lewat `media-treatment`, bukan filter CSS | `grain-overlay`, `ascii-render-pass` | hyperframes/SKILL.md (kontrak 11) |
| Rekonstruksi video dari file | Skill `/reverse-any-video`, dicek frame demi frame dengan aslinya | (alur kerja) | reverse-any-video/SKILL.md |
| Episode bergaya tetap | Skill `/style-sampling` (Collage, Finance, Animated Science, 3D Brand, 3D True Crime Explainer) | (alur kerja) | style-sampling/SKILL.md |
| Port dari alat lain / Figma / situs | `/remotion-to-hyperframes`, `/figma`, `capture <url>` | (alur kerja) | SKILL.md masing-masing; film.md |
| Media: musik, SFX, VO, cutout | `/media-use`: `tts`, `remove-background`, `normalize-audio`, `media-treatment` | (alur kerja) | media-use/SKILL.md; hyperframes-cli/SKILL.md |

## 2. Runtime animasi yang didukung

- GSAP (utama): satu timeline paused per komposisi, didaftarkan paling akhir: `window.__timelines["<data-composition-id>"] = tl`. Tween di detik absolut (`tl.to(el, {...}, 2.4)`), state awal lewat `fromTo`.
- CSS `@keyframes`: iterasi terbatas, `animation-fill-mode: both`, `data-start` di elemen.
- WAAPI: `element.animate(..., { fill: "both" })` lalu `pause()`.
- Lottie / dotLottie: `autoplay: false`, `loop` selalu diisi, instance di-push ke `window.__hfLottie`.
- anime.js v4: `autoplay: false`, push ke `window.__hfAnime`, acak lewat `anime.createSeededRandom`.
- Three.js / WebGPU / p5 / canvas: gambar dari `e.detail.time` di listener `hf-seek`; setup berat lewat `window.__hf.buildReady["<key>"]`.

Determinisme (kontrak 4): dilarang `Date.now()`, `Math.random()` tanpa seed (pakai PRNG seperti mulberry32), fetch jaringan, timer, `requestAnimationFrame` sebagai jam, dan `repeat: -1`. Repeat terbatas: `repeat: Math.max(0, Math.floor(duration / cycle) - 1)`. Ukur layout sekali sebelum tween, bukan di `onUpdate`. Sumber: hyperframes/references/runtimes.md, hyperframes/SKILL.md.

## 3. Alur kerja dan perintah CLI per tahap

Semua dipanggil `npx hyperframes <cmd>` (di proyek Bagas: `npx --yes hyperframes@0.9.33 <cmd>`).

1. Mulai: `init <dir> --skip-skills` (opsi `--resolution portrait`, `--video clip.mp4`, `--audio track.mp3`, `--example <name>` hanya bila diminta); dari situs: `capture <url> --json`. Proyek lama: `timeline --json`, `info`, `compositions`.
2. Registry: `catalog --query "<efek, dalam bahasa Inggris>" --json` (filter `--type block|component`, `--tag <tag>`); pasang: `add <name> --json` (cetak snippet mount; `--vars '{"title":"..."}'`). Block dipasang ke `compositions/<name>.html`, component ke `compositions/components/<name>.html`. Tidak ada perintah `hyperframes registry`.
3. Cek: `lint` (atau `lint --json`, `--verbose`) saat menulis; `check --json` sebagai gerbang (lint, runtime, layout, kontras). `validate`, `inspect`, `layout` adalah alias usang dari `check`, jangan dipakai. Niat gerak bisa diasersi lewat `<nama>.motion.json` (`appearsBy`, `before`, `staysInFrame`, `keepsMoving`).
4. Lihat: `snapshot` (5 frame), `snapshot --at <t,...>`, `--range 3,5 --frames 8`, `--composition <id>`, `--zoom '#id'`, `--angle iso`, `--against ref.mp4`, `snapshot --review` (beat sheet, strip sambungan -0.2..+0.2 dtk, lembar ukuran ponsel). Studio: `preview --background --port 4567`, berhenti dengan `preview --stop`.
5. Keyframes: `keyframes --json [--selector '#id'] [--runtime all]` (properti, waktu, nilai, ease); `keyframes --shot motion.png --selector '#id'` (9 sampel, `--samples N`), `--layout strip` untuk gerak di tempat (filmstrip piksel per waktu hanya bila `--selector` menunjuk elemen SVG; selector DOM mendapat satu frame plus penanda posisi, menurut `keyframes --help` 0.9.33), `--from`/`--to` untuk satu rentang, `--angle iso|top|side`, `--ghost` untuk `<canvas>`. Klaim "--layout strip hanya untuk SVG" tidak ada di dokumen: [belum terverifikasi].
6. Beat musik: `beats ./my-video --json` (butuh `<audio data-timeline-role="music">`, menulis `beats/<path>.json`); `beats music.mp3 --json` hanya analisis. Titik hit untuk block = waktu beat dikurangi `data-start` mount. Tambahan: `audio --only sections,onsets,moments --json`.
7. Edit timeline: `timeline move|trim|split|set|duplicate|delete <ref> --plan --json`, lalu tanpa `--plan`; banyak edit: `timeline apply plan.json --json`, batal: `timeline undo receipt.json`.
8. Render: `render --quality draft|looks|delivery -o out.mp4`; `-c compositions/intro.html` untuk satu adegan; `--format webm|mov|gif|png-sequence|hls`; `--docker --strict` untuk hasil identik; `--batch rows.json -o "renders/{name}.mp4"`; `--variables '{...}'`. Setelah render: cek file tidak kosong dan durasi `ffprobe` sama dengan `data-duration` root.
9. Bandingkan: `compare <a> <b> --at <detik> --labels baseline,candidate --out compare.png --cols 2` (maks 16 varian; alat review visual, bukan gerbang kualitas).

## 4. Batas dan jebakan

- Hampir semua block berukuran 1920x1080 (195 dari 210); proyek 1440x1080 harus menyesuaikan tata letak block, dan `--resolution` tidak bisa mengubah rasio aspek.
- Jangan tween `display`, `visibility`, `autoAlpha` pada `.clip`; jangan pasang CSS `transform` pada elemen yang ditransform GSAP; animasikan transform, bukan `left/top/width/height`.
- Timeline yang didaftarkan sebelum build async selesai merender kosong; dua timeline tidak boleh menggerakkan properti yang sama pada satu elemen.
- Jangan `play()`/`pause()`/seek media; `<audio>` wajib punya `id`; aset `assets/...` tanpa `/` di depan.
- Hanya font bawaan yang dikenali lewat nama; keluarga lain wajib `@font-face` ke berkas di `assets/fonts/` (kontrak 9).
- Query catalog wajib bahasa Inggris (indeks berbahasa Inggris); skrip lain memberi `No searchable words in query`, bukan berarti kosong.
- `beats` gagal pada musik tanpa ketukan stabil; pada musik tenang tracker bisa mengarang tempo ganda (cek `bpmConfidence`).
- Lolos `check` bukan alasan render: render setelah preview disetujui.

## 5. Untuk video promo Bagas (masalah r7)

- Gerak patah di sambungan: `snapshot --review` membuat strip -0.2..+0.2 dtk di tiap cut; cocokkan ease di seam (`power3.in` keluar, `power3.out` masuk) sesuai tabel kesalahan umum motion.md.
- Kamera goyang/tidak mulus: pakai component kamera jadi (`push-in`, `parallax-zoom`, `drift-hold`, `camera-dolly-zoom`) alih-alih tween buatan; verifikasi lintasan dengan `keyframes --shot cam.png --selector '#id' --samples 15` dan `keyframes --json` untuk melihat ease tiap properti. Gerak kamera 0.4-0.6 dtk lalu tahan (launch.md).
- Tata letak berantakan: `check --json` (audit layout dan kontras, ada `suggestedColor`), konten di kotak aman 90%, teks di 80%; `snapshot --at 1,2,3,...` per detik dan `--zoom '#id'` untuk detail.
- Sinkron SFX dan musik: `beats --json` untuk hit, gerak mulai 40-190 ms sebelum hit, hit sebagai `tl.set` 0 ms; cek hasil dengan `audio <video> --json`.
- Bandingkan revisi r6 vs r7: `compare <dir-r6> <dir-r7> --at <detik> --labels r6,r7 --out compare.png`; kunci niat gerak dengan `.motion.json` agar `check` menangkap regresi.
