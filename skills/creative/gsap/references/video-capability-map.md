# Peta kemampuan GSAP 3.15 untuk video render (HyperFrames)

Pelengkap `../SKILL.md`. Label status: **[diuji Node]** = lulus di `cache/scratch/gsapmap/test.cjs` (objek polos, tanpa DOM); **[perlu DOM, belum diuji]**; **[tidak cocok untuk render]**.

## 1. Prinsip render deterministik

Renderer membuat `gsap.timeline({paused:true})` lalu me-seek ke waktu frame (30fps). Frame N harus identik, apa pun urutan seek-nya (maju, mundur, lompat). Terbukti di uji 5: `seek(1)` lalu `seek(0.2)` sama dengan langsung `seek(0.2)` (selisih ~1e-6, pembulatan internal GSAP).

Dilarang:
- `repeat:-1`, `yoyo` tanpa batas: durasi timeline jadi tak hingga. Pakai `repeat: n` terhitung.
- `Math.random()`, `gsap.utils.random()` saat render: dokumentasi resmi `random()` tidak punya parameter seed. Pakai PRNG seeded dan hitung nilai sekali saat membangun timeline:
  ```js
  const rng = (s => () => (s = (s * 1664525 + 1013904223) >>> 0) / 2**32)(42); // LCG seeded
  ```
- `Date`, `performance.now()`, `setTimeout`, `requestAnimationFrame` milik sendiri, CSS `transition`/`animation` (tidak ikut seek).
- Callback (`onComplete`, `call()`, `onUpdate`) yang mengubah DOM secara akumulatif (`count++`, `appendChild`). Callback harus menulis nilai dari state tween saat itu.
- **Callback dipanggil ulang di setiap seek saat render.** Di GSAP murni, `tl.seek(t)` menekan callback (`suppressEvents` default `true`, uji 6). Renderer HyperFrames 0.9.33 justru me-seek dengan `suppressEvents=false` (pesan lint vendor dan runtime `totalTime(t, suppressEvents===true)`), dengan urutan seek tidak linear per worker. Akibatnya callback harus idempoten (menulis nilai dari state tween saat itu) dan tidak boleh mengukur DOM (`getBoundingClientRect`, `getTotalLength`, `getComputedStyle`), karena hasil ukurnya bergantung urutan seek. Pilihan paling aman: animasikan properti langsung (resep d).

## 2. Bisa dibuat apa

| Fitur | Kegunaan di video | Snippet | Status |
|---|---|---|---|
| Core `to/from/fromTo/set` | semua gerak dasar | `tl.fromTo(el,{autoAlpha:0,y:24},{autoAlpha:1,y:0,duration:.6,ease:"ui"})` | to diuji Node; from/fromTo/set [perlu DOM, belum diuji] |
| Timeline + position | menyusun adegan tanpa hitung detik manual | `tl.add("hook",2).to(a,{x:100},"hook").to(b,{y:0},"<0.1").to(c,{x:0},">-0.2")` | `"<0.2"` [diuji Node] |
| Stagger | list/huruf/grid masuk berurutan | `stagger:{each:.06,from:"center",ease:"power1.in"}`, `stagger:{amount:.5,grid:[4,6],from:"edges"}` | each/from [diuji Node]; grid [perlu DOM, belum diuji] |
| Keyframes persen + `easeEach` | satu track untuk masuk-hold-keluar / kamera | `keyframes:{"0%":{x:0},"50%":{x:100},"100%":{x:40},easeEach:"power2.inOut"}, ease:"none"` | [diuji Node] |
| Keyframes array nilai | gerak bolak-balik ringkas | `keyframes:{x:[0,50,20]}` | [diuji Node] |
| Keyframes array objek | tahap dengan durasi berbeda | `keyframes:[{y:30,duration:.5},{y:0,duration:.5}]` | [diuji Node] |
| utils | memetakan progres ke nilai, warna, indeks | `interpolate(0,100,.25)`, `mapRange(0,1,100,200,.5)`, `snap(10,23)`, `wrap(arr,4)`, `pipe(clamp(0,1),mapRange(0,1,0,10))` | [diuji Node] |
| Eases bawaan | none, power1-4, sine, expo, circ, back, elastic, bounce, steps | pilih 2-3 peran saja, bukan 14 jenis | `power2/3`, `none` [diuji Node] |
| CustomEase | kurva merek konsisten | `CustomEase.create("ui","0.16,1,0.3,1")` (nilai di 0.5 = 0.9717) | [diuji Node] |
| CustomBounce | jatuh memantul + squash | `CustomBounce.create("hop",{strength:.6,squash:2})` | [diuji Node] |
| CustomWiggle | getar notifikasi/error, kembali ke 0 | `CustomWiggle.create("shake",{wiggles:6,type:"easeOut"}); tl.to(el,{x:8,ease:"shake"})` | [diuji Node] |
| MotionPathPlugin | lintasan kursor, pesawat kertas, partikel | `motionPath:{path:[{x:0,y:0},{x:100,y:50},{x:200,y:0}],curviness:1.2}`; SVG: `{path:"#p",align:"#p",autoRotate:true}` | array titik [diuji Node]; SVG/autoRotate [perlu DOM, belum diuji] |
| DrawSVGPlugin | garis/grafik/tanda tangan tergambar | `tl.from("#line",{drawSVG:0,duration:1})` | [perlu DOM, belum diuji] |
| MorphSVGPlugin | ikon play jadi pause, logo berubah | `tl.to("#play",{morphSVG:"#pause"})` | [perlu DOM, belum diuji] |
| SplitText | headline per huruf/kata/baris | `const s=SplitText.create(".h",{type:"words,chars"}); tl.from(s.chars,{y:"100%",stagger:.02})` | [perlu DOM, belum diuji] |
| ScrambleText / TextPlugin | teks teracak lalu terbaca, efek mengetik | `{scrambleText:{text:"Rilis!",chars:"01"}}`, `{text:"Halo dunia"}` | [perlu DOM, belum diuji]; scramble memakai acak internal, cek frame identik saat render ulang [belum terverifikasi] |
| Physics2D / PhysicsProps | lemparan, confetti jatuh | `{physics2D:{velocity:300,angle:-60,gravity:400}}` | Physics2D [diuji Node] (seek bolak-balik konsisten); PhysicsProps [perlu DOM, belum diuji] |
| Flip | kartu pindah dari grid ke detail | `const st=Flip.getState(els); /*ubah layout*/ tl.add(Flip.from(st,{duration:.6}))` | [perlu DOM, belum diuji]; ubah layout harus terjadi saat membangun timeline, bukan di callback |

Catatan pemuatan Node: plugin UMD mencari `window.gsap`; di Node set `globalThis.window={gsap}` sebelum `require` plugin. Tanpa itu CustomBounce dan `motionPath` gagal ("Missing plugin?") walau sudah `registerPlugin`.

## 3. Tidak cocok untuk video render

| Plugin | Alasan |
|---|---|
| ScrollTrigger, ScrollSmoother | dipicu posisi scroll pengguna; video tidak punya scroll. Pakai posisi waktu di timeline. |
| Draggable, Observer | menunggu input pointer/wheel/touch. |
| InertiaPlugin | menghitung dari kecepatan input nyata; tanpa input tidak ada nilai. Untuk efek luncur pakai `power3.out`/`expo.out`. |
| GSDevTools | panel UI untuk scrubbing manual; boleh saat menyusun di browser, keluarkan dari komposisi render. |

## 4. Resep video promo

Konvensi: satu timeline `tl` paused per komposisi; ease bernama dari helper (resep f).

**(f) Ease bernama, didaftarkan sekali** [diuji Node]
```js
// ease.js, dimuat sekali sebelum adegan
gsap.registerPlugin(CustomEase);
CustomEase.create("ui",    "0.16,1,0.3,1");   // masuk UI: cepat lalu mengendap
CustomEase.create("exit",  "0.7,0,0.84,0");   // keluar: pelan lalu cepat
CustomEase.create("cam",   "0.45,0,0.55,1");  // kamera: simetris, tanpa overshoot
// aturan: UI tanpa back.out besar; maksimal back.out(1.4) untuk aksen tunggal
```

**(a) Kamera push: satu track keyframes pada SATU wrapper** [pola diuji Node pada objek polos]
```js
// #cam membungkus seluruh adegan; jangan ada tween lain pada transform #cam
tl.to("#cam", { duration: 8, ease: "none", keyframes: {
  "0%":   { scale: 1,    x: 0,   y: 0 },
  "40%":  { scale: 1.08, x: -40, y: -10 },
  "100%": { scale: 1.15, x: -60, y: -20 },
  easeEach: "cam" } }, 0);
```
Satu wrapper satu track menghilangkan goyang dari tiga lapis kamera yang saling menimpa.

**(b) Kartu masuk-hold-keluar, satu tween** [pola diuji Node]
```js
tl.to(".card", { duration: 3, ease: "none", keyframes: {
  "0%":   { autoAlpha: 0, y: 40 },
  "15%":  { autoAlpha: 1, y: 0, ease: "ui" },   // masuk 0.45s
  "85%":  { autoAlpha: 1, y: -6 },              // hold dengan drift halus
  "100%": { autoAlpha: 0, y: -30, ease: "exit" } } }, "hook");
```
`ease` per keyframe berlaku untuk segmen menuju keyframe itu; `easeEach` jadi bawaan.

**(c) Kursor lewat MotionPath lalu tekan** [lintasan diuji Node; tekan scale pola keyframes array]
```js
tl.to("#cursor", { duration: 1.2, ease: "power2.inOut",
    motionPath: { path: [{x:0,y:0},{x:220,y:-60},{x:420,y:30}], curviness: 1.1 } })
  .to("#cursor", { keyframes: { scale: [1, 0.92, 1] }, duration: 0.25, ease: "power1.inOut" }, ">")
  .to("#btn",    { keyframes: { scale: [1, 0.96, 1] }, duration: 0.25 }, "<");
```

**(d) Angka menghitung, aman di-seek** [diuji Node]
```js
// Pilihan 1 (disarankan): animasikan properti langsung, tidak bergantung callback
tl.to("#num", { innerText: 1234, snap: { innerText: 1 }, duration: 1.5, ease: "power2.out" });

// Pilihan 2: format ribuan via objek state + onUpdate yang MENULIS dari state (bukan count++)
const s = { v: 0 };
tl.to(s, { v: 1234, snap: { v: 1 }, duration: 1.5, ease: "power2.out",
  onUpdate: () => { num.textContent = s.v.toLocaleString("id-ID"); } });
```
Pilihan 2 bergantung pada callback. Saat render, HyperFrames me-seek dengan `suppressEvents=false` sehingga onUpdate jalan, tetapi saat fase discover dan di GSAP murni (`tl.seek(t)`, uji 6) callback ditekan, jadi preview dan QC bisa menampilkan teks lama. Pakai Pilihan 1 kecuali butuh format ribuan.

**(e) Stagger list masuk dengan ease peran** [stagger diuji Node]
```js
tl.from(".row", { autoAlpha: 0, y: 16, duration: 0.5, ease: "ui",
  stagger: { each: 0.07, from: "start" } }, "list");
```
Satu ease peran (`ui`) untuk semua baris; variasi datang dari waktu (stagger), bukan dari jenis ease.

## 5. Memuat plugin di komposisi HyperFrames

Vendor HyperFrames hanya membawa `gsap.min.js`, `CustomEase.min.js`, `MotionPathPlugin.min.js`. Plugin lain dari CDN dengan **versi persis sama 3.15.0** (beda versi = plugin bisa gagal terdaftar).

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/CustomEase.min.js"></script>
<!-- CustomBounce/CustomWiggle butuh CustomEase dimuat lebih dulu -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/CustomBounce.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/CustomWiggle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/MotionPathPlugin.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/SplitText.min.js"></script>
<script>
  gsap.registerPlugin(CustomEase, CustomBounce, CustomWiggle, MotionPathPlugin, SplitText);
  // lalu ease.js (resep f), lalu bangun tl paused
</script>
```
Urutan: core, CustomEase, turunan CustomEase, plugin lain, `registerPlugin`, helper ease, timeline. Lebih aman salin berkas `.min.js` 3.15.0 ke folder proyek (render offline, tanpa risiko CDN); bila tetap CDN, tambahkan `integrity`+`crossorigin`. SplitText dan Flip mengukur layout: tunggu font termuat (`document.fonts.ready`) sebelum membangun timeline, kalau tidak pecahan baris berbeda antar-render [belum terverifikasi di HyperFrames].
