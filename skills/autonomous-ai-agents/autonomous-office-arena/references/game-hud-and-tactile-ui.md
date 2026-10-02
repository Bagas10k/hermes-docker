# Game HUD & Tactile 2.5D Interface Architecture

Panduan arsitektur frontend untuk membangun antarmuka kantor virtual dan simulator manajemen multi-agent dengan standar visual game RTS/SimCity (100dvh edge-to-edge canvas, minimap radar, sliding management dock, dan zero-asset Web Audio synthesis).

---

## 1. Fullscreen Viewport & Canvas Layout Math

Untuk menghindari perilaku scroll dokumen standar yang merusak ilusi diorama game, terapkan kontainer viewport kaku:

```css
html, body {
  margin: 0; padding: 0;
  width: 100vw; height: 100vh; height: 100dvh;
  overflow: hidden !important;
  user-select: none;
}

.game-viewport {
  position: fixed; inset: 0;
  width: 100vw; height: 100vh; height: 100dvh;
  overflow: hidden;
  display: flex; flex-direction: column;
}

.game-world {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  z-index: 1;
}

#arena-canvas {
  width: 100%; height: 100%;
  display: block;
}
```

### Dynamic Hi-DPI Canvas Resizing
```javascript
resize() {
  if (!this.canvas || !this.canvas.parentElement) return;
  const rect = this.canvas.parentElement.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  this.canvas.width = rect.width * dpr;
  this.canvas.height = rect.height * dpr;
  this.canvas.style.width = `${rect.width}px`;
  this.canvas.style.height = `${rect.height}px`;
  this.ctx.scale(dpr, dpr);
  this.width = rect.width;
  this.height = rect.height;
}
```

---

## 2. Tactical Radar Minimap Projection

Minimap merender representasi 2D ortografis mini dari grid 2.5D isometrik dengan skala proporsional:

```javascript
renderMinimap(minimapCanvas) {
  if (!minimapCanvas) return;
  const mCtx = minimapCanvas.getContext('2d');
  if (!mCtx) return;
  const mW = minimapCanvas.width;
  const mH = minimapCanvas.height;

  mCtx.clearRect(0, 0, mW, mH);
  mCtx.fillStyle = '#080c14';
  mCtx.fillRect(0, 0, mW, mH);

  const { columns, rows } = this.layout.grid;
  const pad = 6;
  const scaleX = (mW - pad * 2) / columns;
  const scaleY = (mH - pad * 2) / rows;

  // 1. Render seluruh zona ruangan dengan kode taktis 3-huruf
  const roomCodeMap = {
    meeting_room: 'MTG',
    strategy_room: 'STR',
    research_lab: 'RES',
    tool_factory: 'TOL',
    observation_center: 'OBS',
    engineering_floor: 'ENG',
    archive_office: 'ARC',
    lounge_waiting: 'LNG',
    qa_lab: 'QAL',
    knowledge_vault: 'VAU',
    backup_room: 'BKP'
  };

  for (const room of this.layout.rooms) {
    const rx = pad + room.zone.x * scaleX;
    const ry = pad + room.zone.y * scaleY;
    const rw = room.zone.width * scaleX;
    const rh = room.zone.height * scaleY;

    const isSelected = this.selectedRoom?.id === room.id;
    mCtx.fillStyle = isSelected ? 'rgba(56, 189, 248, 0.35)' : 'rgba(255, 255, 255, 0.06)';
    mCtx.fillRect(rx, ry, rw, rh);
    mCtx.strokeStyle = isSelected ? '#38bdf8' : (room.color || 'rgba(255, 255, 255, 0.25)');
    mCtx.lineWidth = isSelected ? 1.5 : 0.8;
    mCtx.strokeRect(rx, ry, rw, rh);

    // Label 3-huruf resmi
    mCtx.fillStyle = isSelected ? '#38bdf8' : 'rgba(255, 255, 255, 0.75)';
    mCtx.font = 'bold 8px "JetBrains Mono", monospace';
    mCtx.textAlign = 'center';
    mCtx.textBaseline = 'middle';
    const label = roomCodeMap[room.id] || room.name.slice(0, 3).toUpperCase();
    mCtx.fillText(label, rx + rw / 2, ry + rh / 2);
  }

  // 2. Render blip agen aktif
  if (this.agents && this.agents.length) {
    for (const agent of this.agents) {
      const ax = pad + agent.gridX * scaleX;
      const ay = pad + agent.gridY * scaleY;
      mCtx.beginPath();
      mCtx.arc(ax, ay, 2, 0, Math.PI * 2);
      mCtx.fillStyle = agent.color || '#f59e0b';
      mCtx.fill();
    }
  }
}
```

### Minimap 1-Click Camera Navigation
Saat pengguna mengeklik kanvas minimap, koordinat diinversikan kembali ke petak grid untuk mencari ruangan yang dituju:
```javascript
minimapCanvas.addEventListener('click', (e) => {
  const rect = minimapCanvas.getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  const clickY = e.clientY - rect.top;
  const { columns, rows } = arenaEngine.layout.grid;
  const pad = 6;
  const scaleX = (minimapCanvas.width - pad * 2) / columns;
  const scaleY = (minimapCanvas.height - pad * 2) / rows;
  const gridX = (clickX - pad) / scaleX;
  const gridY = (clickY - pad) / scaleY;

  const room = arenaEngine.layout.rooms.find(r =>
    gridX >= r.zone.x && gridX <= r.zone.x + r.zone.width &&
    gridY >= r.zone.y && gridY <= r.zone.y + r.zone.height
  );
  if (room) {
    arenaEngine.focusRoom(room.id);
    showRoomInspector(room);
  }
});
```

---

## 3. Zero-Asset Web Audio API Synthesis

Menghasilkan umpan balik audio taktil instan tanpa aset suara eksternal:

```javascript
const SoundFX = {
  ctx: null,
  enabled: true,
  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
  },
  playClick() {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;
      if (this.ctx.state === 'suspended') this.ctx.resume();
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(800, now);
      osc.frequency.exponentialRampToValueAtTime(300, now + 0.04);
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.05);
    } catch (_) {}
  },
  playChime() {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;
      if (this.ctx.state === 'suspended') this.ctx.resume();
      const now = this.ctx.currentTime;
      [523.25, 659.25, 783.99].forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, now + idx * 0.03);
        gain.gain.setValueAtTime(0.08, now + idx * 0.03);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.03 + 0.15);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now + idx * 0.03);
        osc.stop(now + idx * 0.03 + 0.16);
      });
    } catch (_) {}
  },
  playStep() {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;
      if (this.ctx.state === 'suspended') this.ctx.resume();
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(1200, now);
      gain.gain.setValueAtTime(0.06, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.02);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.025);
    } catch (_) {}
  }
};
```

---

## 4. Sliding Game Management Dock & Mobile Safe-Area

Dock samping menampung seluruh kontrol pengelolaan tanpa menghalangi pandangan kanvas:

- **Desktop (width $\ge 769\text{px}$):**
  - Posisi tetap di kanan: `top: 52px; bottom: 0; right: 0; width: 380px;` (menutup penuh ke dasar layar untuk mengeliminasi celah hitam kosong di sudut kanan bawah).
  - Transisi slide keluar-masuk via `transform: translateX(100%)`.
- **Mobile (width $\le 768\text{px}$):**
  - Pasang `.side` khusus pada tab navigation strip (`height: 44px !important; position: static !important;`) untuk menjamin lulus assertion uji kekompakan seluler (`navHeight < 180`).
  - Dock body terbuka sebagai bottom-sheet layar penuh (`top: 48px; bottom: 0; width: 100vw;`) saat dibuka pengguna.

---

## 5. Interactive Live A* Agent Dispatching

Mengizinkan pengguna mengendalikan agen layaknya unit dalam game strategi RTS secara real-time:

```javascript
sendAgentToRoom(agentId, targetRoomId) {
  const agent = this.agents.find(a => a.id === agentId);
  const room = this.layout.rooms.find(r => r.id === targetRoomId);
  if (!agent || !room) return false;

  const targetX = room.zone.x + room.zone.width / 2;
  const targetY = room.zone.y + room.zone.height / 2;

  agent.domainState = 'WORKING';
  agent.bubble = `Menuju ${room.name}`;
  agent.room = room.id;
  agent.setDestination(targetX, targetY, this.pathfinder);
  return true;
}
```

- **Sinkronisasi Balon & Blip Radar:** Saat agen melangkah mengikuti rute A*, koordinat grid `agent.gridX` dan `agent.gridY` diperbarui setiap frame berbasis delta time $\Delta t$. Kanvas diorama dan radar minimap langsung merefleksikan posisi pergerakan kaki dan blip secara otomatis.
- **Roster 10 Agen:** Tempatkan pemilih ruang tujuan `<select class="agent-move-select">` dan tombol fokus pada setiap kartu agen di panel `Ruang & Agen`.

---

## 6. Generative Binaural Ambient Soundscape (Zero-Asset Drone)

Menciptakan latar suara sci-fi drone analog yang hangat dan menenangkan menggunakan osilator Web Audio API bawaan peramban:

```javascript
startAmbient() {
  if (this.ambientPlaying || !this.ctx) return;
  try {
    if (this.ctx.state === 'suspended') this.ctx.resume();
    const now = this.ctx.currentTime;

    // Master gain lembut (volume rendah, fade in 2 detik)
    this.ambientGain = this.ctx.createGain();
    this.ambientGain.gain.setValueAtTime(0.001, now);
    this.ambientGain.gain.exponentialRampToValueAtTime(0.035, now + 2);

    // Filter analog lowpass hangat
    this.ambientFilter = this.ctx.createBiquadFilter();
    this.ambientFilter.type = 'lowpass';
    this.ambientFilter.frequency.setValueAtTime(280, now);
    this.ambientFilter.Q.setValueAtTime(3.0, now);

    // Osilator drone 55Hz (A1) & binaural harmonic 110.5Hz (+0.5Hz organic beat)
    this.ambientOsc1 = this.ctx.createOscillator();
    this.ambientOsc1.type = 'triangle';
    this.ambientOsc1.frequency.setValueAtTime(55, now);

    this.ambientOsc2 = this.ctx.createOscillator();
    this.ambientOsc2.type = 'sine';
    this.ambientOsc2.frequency.setValueAtTime(110.5, now);

    this.ambientOsc1.connect(this.ambientFilter);
    this.ambientOsc2.connect(this.ambientFilter);
    this.ambientFilter.connect(this.ambientGain);
    this.ambientGain.connect(this.ctx.destination);

    this.ambientOsc1.start(now);
    this.ambientOsc2.start(now);
    this.ambientPlaying = true;
  } catch (_) {}
}
```

---

## 7. Dynamic Atmosphere Lighting Presets

Menyediakan pemilih tema pencahayaan kanvas di bilah atas HUD untuk variasi suasana diorama visual:

- **Studio Cyber:** Default deep void navy (`radial-gradient(circle at 50% 40%, #151f32 0%, #0d1422 45%, #070a0f 100%)`).
- **Sunset Warm:** Nuansa sore hari golden hour (`radial-gradient(circle at 50% 35%, #2a151b 0%, #1a0f18 45%, #0b070e 100%)`).
- **Midnight Neon:** Malam pekat dengan aksen pendar neon listrik cyan/magenta (`radial-gradient(circle at 50% 40%, #0c1a2e 0%, #060d19 45%, #03060a 100%)`).
- **Clean Studio:** Pencahayaan claymorphic lembut netral studio (`radial-gradient(circle at 50% 45%, #1e293b 0%, #0f172a 50%, #080d17 100%)`).

---

## 8. Keyboard Hotkeys Engine & Cheatsheet Modal

Pintasan keyboard ergonomis ala game PC tanpa mengganggu pengetikan form:

```javascript
window.addEventListener('keydown', (e) => {
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) return;

  switch (e.code) {
    case 'Space': e.preventDefault(); $('#replay-play')?.click(); break;
    case 'ArrowRight': case 'KeyD': e.preventDefault(); $('#replay-step')?.click(); break;
    case 'ArrowLeft': case 'KeyA': e.preventDefault(); $('#replay-reset')?.click(); break;
    case 'Digit1': $('#speed-1x')?.click(); break;
    case 'Digit2': $('#speed-2x')?.click(); break;
    case 'Digit5': $('#speed-5x')?.click(); break;
    case 'KeyM': $('#btn-toggle-minimap')?.click(); break;
    case 'KeyE': $('#btn-toggle-dock')?.click(); break;
    case 'KeyF': $('#btn-fullscreen')?.click(); break;
    case 'KeyS': $('#btn-audio-toggle')?.click(); break;
    case 'Escape':
      $('#quick-inspector')?.classList.add('hidden');
      $('#artifact-modal')?.classList.add('hidden');
      $('#keybindings-modal')?.classList.add('hidden');
      break;
  }
});
```

---

## 9. Lightweight UI Engineering & 60 FPS Canvas Performance (Anti-Lag Architecture)

Untuk menjamin antarmuka game 2.5D tetap ringan, responsif, dan berjalan mulus 60 FPS pada laptop standar maupun ponsel cerdas:

### A. Reduksi Beban GPU Compositing & Backdrop-Filter
- **Masalah:** Menumpuk efek `backdrop-filter: blur(16px/20px)` pada 5 panel HUD yang melayang di atas kanvas animasi 60 FPS memaksa GPU melakukan pembacaan frame buffer, downsampling, dan konvolusi Gaussian berulang-ulang setiap frame, memicu lonjakan penggunaan daya GPU dan lag pada perangkat seluler.
- **Solusi:**
  1. Turunkan radius blur desktop ke level ringan `blur(6px)` atau `blur(8px)` dengan warna latar kaca pekat berkualitas tinggi (`rgba(9, 13, 22, 0.94)`).
  2. Khusus media query seluler (`@media (max-width: 768px)`), matikan filter blur sepenuhnya (`backdrop-filter: none !important; -webkit-backdrop-filter: none !important; background: rgba(8, 12, 19, 0.98) !important;`).
  3. Terapkan isolasi render `contain: paint layout;` dan dorong layer ke GPU via `transform: translateZ(0); will-change: transform;` pada panel-panel melayang untuk mengeliminasi reflow/relayout seluruh halaman saat panel digeser.

### B. Throttling Sub-Renderer Kanvas (Minimap 15 FPS Cap)
- Kanvas sekunder (seperti radar minimap atau HUD meter) tidak perlu digambar ulang 60 kali per detik jika hanya menyajikan orientasi posisi spasial.
- Batasi render minimap pada interval setiap 4 frame animasi (~15 FPS) menggunakan counter siklus (`this.minimapTick = (this.minimapTick + 1) % 4; if (this.minimapTick === 0) this.renderMinimap(...);`). Ini memangkas 75% beban pemrosesan CPU kanvas tanpa mengorbankan kelancaran interaksi taktis.

### C. Eliminasi Alokasi Memori (Zero GC Garbage) dalam Animasi RAF
- **Masalah:** Menyusun string warna dinamis di setiap partikel pada setiap frame (`ctx.fillStyle = m.color + alpha + ')'`) menghasilkan ribuan alokasi string per detik, memicu jeda *Garbage Collector* periodik (*micro-stutter / dropped frames*).
- **Solusi:** Simpan warna basis tetap (`baseColor: '#38bdf8'`) dan atur transparansi partikel melalui `ctx.globalAlpha = alpha` dalam blok `ctx.save() ... ctx.restore()`. Ini menghasilkan 0 alokasi heap baru per frame.

### D. Epsilon Snapping pada Interpolasi Kamera
- Pergerakan kamera dan zoom kanvas yang menggunakan interpolasi eksponensial (`this.scale += (target - scale) * 0.15`) akan menghasilkan pergeseran floating-point sub-pixel yang tidak pernah benar-benar berhenti.
- Pasang batas *epsilon snapping*: jika `Math.abs(target - current) < epsilon` (misal 0.0005 untuk skala, 0.05px untuk koordinat origin), langsung tetapkan `current = target`. Ini menghentikan siklus render sub-pixel dan memungkinkan peramban mengistirahatkan kalkulasi rasterisasi saat kamera diam.

---

## 10. Neatness & Anti-Fragility Principles (Zero-Clutter Game HUD)

Saat pengguna menilai antarmuka terasa "rapuh" (*brittle, cramped, chaotic*), akar masalahnya hampir selalu berada pada kalkulasi ruang flexbox yang meluap (*overflow*), tipografi bertingkat yang tidak terduga, dan fragmentasi teks mekanis:

### A. Tiga Zona Top Bar & Batas Maksimal Lebar 1040px
- **Mekanisme Kegagalan:** Menumpuk lebih dari 8 kontrol terpisah di bilah atas tetap (`height: 52px`) memerlukan ruang lebar $> 1600\text{px}$. Pada monitor laptop 1366x768 atau 1440x900, elemen flexbox meluap atau terbungkus (*wrap*) ke bawah, menimpa kanvas dan memblokir interaksi klik pengguna.
- **Aturan Solusi:**
  1. *Zona Kiri ($\le 300\text{px}$):* Brand mark, identitas HQ, dan pemilih ruang cepat.
  2. *Zona Tengah ($\le 280\text{px}$):* Kapsul pulau status terpadu (`.hud-status-island`) yang menggabungkan CPU, RAM, status stream, event ticker, dan jam WIB ke dalam satu pill tunggal bergaris pembatas `·` dan `|` tanpa elipsis.
  3. *Zona Kanan ($\le 450\text{px}$):* Tombol kontrol dipadatkan dalam pill terkelompok (misal grup tombol audio `SFX | AMB`), tema dropdown ringkas, tombol pintasan, fullscreen, dan menu utama.
  4. Total lebar bar terjamin $\le 1040\text{px}$, bebas wrapping pada seluruh resolusi desktop standar.

### B. Pulau Komando Bawah Melayang (Floating Command Island)
- **Mekanisme:** Bilah bawah kaku yang membentang dari ujung ke ujung (*edge-to-edge full width*) memotong lantai diorama 2.5D dan meninggalkan sudut-sudut mati yang terhimpit.
- **Aturan Solusi:**
  Gunakan pulau melayang terpusat (`left: 50%; transform: translateX(-50%); max-width: 820px; border-radius: 14px; bottom: 16px;`). Ini memberikan ruang bernapas luas di sudut kiri bawah untuk radar minimap dan sudut kanan bawah untuk batas kanvas, menciptakan ilusi game RTS modern.

### C. Tipografi Single-Line Horisontal pada Status Scrubber
- **Mekanisme:** Memasukkan string status panjang dan disclaimer statis secara bersamaan ke dalam baris flex sempit menyebabkan teks terlipat compang-camping menjadi 3 baris dengan tanda pemisah peluru (*bullets*) yang menggantung canggung.
- **Aturan Solusi:**
  - Terapkan `white-space: nowrap; overflow: hidden;` pada kontainer status.
  - Pisahkan hitungan progres tegas di kiri (`5 / 32 event · 0 ditolak`) dan status event aktif ber-ellipsis di kanan (`5 · TASK_ASSIGNED · SputarAI`).
  - Sembunyikan teks disclaimer statis panjang dari pulau melayang; tempatkan rincian tersebut di dalam panel audit ledger di sidebar.

### D. Kode Taktis 3-Huruf Standar (Anti-String Slicing)
- **Mekanisme:** Memotong nama string secara mekanis dengan `slice(0, 6)` menghasilkan fragmen kata terpotong seperti `Meetin`, `Strate`, `Resear`, `Observ`, `Knowle` yang terkesan kasar dan seperti prototipe mentah.
- **Aturan Solusi:**
  Gunakan tabel pemetaan akronim taktis 3-huruf resmi (`MTG`, `STR`, `RES`, `TOL`, `OBS`, `ENG`, `ARC`, `LNG`, `QAL`, `VAU`, `BKP`) yang proporsional, simetris, dan terpusat di kanvas radar.

### E. Scrollbar Gelap Kustom Terpadu
- Pasang styling scrollbar kustom di seluruh antarmuka (`scrollbar-width: thin; scrollbar-color: rgba(56, 189, 248, 0.25) transparent;` serta `::-webkit-scrollbar` dengan lebar 5px dan sudut membulat) untuk mengeliminasi scrollbar abu-abu terang bawaan browser yang merusak suasana gelap cybernetic.

---

## 11. Seating Slots, Social Proximity Conversations & Tactical Command Deck

Untuk mewujudkan simulasi kantor multi-agent yang realistis dan bebas tabrakan visual:

### A. Titik Kursi & Workstation Mandiri (Anti-Penumpukan 100%)
Jangan pernah mengirim beberapa agen ke titik tengah ruangan yang sama (`room.zone.x + width/2`, `y + height/2`). Definisikan slot kursi fisik untuk seluruh ruangan:

```javascript
createOfficeSeats() {
  return [
    // Meeting Room (10 Kursi Rapat mengelilingi meja konferensi)
    { id: 'mtg_01', roomId: 'meeting_room', label: 'Kursi Utama CEO', gx: 8, gy: 5, facing: 'south', occupant: null },
    { id: 'mtg_02', roomId: 'meeting_room', label: 'Kursi Rapat Utara B', gx: 10, gy: 5, facing: 'south', occupant: null },
    ...
    // Engineering Floor (14 Workstation terbagi dalam Pod Backend, Frontend, Agile Bar, dan Sofa)
    { id: 'eng_01', roomId: 'engineering_floor', label: 'Backend Pod 1A', gx: 24, gy: 20, facing: 'south', occupant: null },
    ...
  ];
}
```

Alokator kursi wajib memeriksa ketersediaan kursi kosong, melepas kursi sebelumnya di ruangan lain, dan menghasilkan offset berdiri jika kapasitas ruangan terlampaui:

```javascript
assignSeatForAgent(roomId, agentId) {
  const roomSeats = this.seats.filter(s => s.roomId === roomId);
  if (!roomSeats.length) return null;

  let seat = roomSeats.find(s => s.occupant === agentId) || roomSeats.find(s => !s.occupant);
  for (const s of this.seats) {
    if (s.occupant === agentId && s !== seat) s.occupant = null;
  }
  if (seat) {
    seat.occupant = agentId;
    return seat;
  }
  // Overflow slot jika seluruh kursi penuh
  const occupiedCount = roomSeats.filter(s => s.occupant).length;
  const room = this.layout.rooms.find(r => r.id === roomId);
  return {
    id: `overflow_${roomId}_${occupiedCount}`,
    roomId,
    label: `Posisi Berdiri ${occupiedCount + 1}`,
    gx: room.zone.x + 3 + (occupiedCount % 3) * 1.5,
    gy: room.zone.y + 3 + Math.floor(occupiedCount / 3) * 1.5,
    facing: 'south'
  };
}
```

### B. Pathfinding Berjarak Sosial (Proximity Social Distance)
Saat agen A diperintahkan berbicara dengan agen B, agen A tidak boleh berjalan ke petak yang sama persis dengan agen B:

```javascript
talkToAgent(agentAId, agentBId) {
  const agentA = this.agents.find(a => a.id === agentAId);
  const agentB = this.agents.find(a => a.id === agentBId);
  if (!agentA || !agentB || agentAId === agentBId) return false;

  // Cari petak tetangga yang valid dan kosong (jarak sopan 1.0 - 1.2 petak grid)
  const offsets = [
    { dx: 1.2, dy: 0 }, { dx: -1.2, dy: 0 },
    { dx: 0, dy: 1.2 }, { dx: 0, dy: -1.2 }
  ];
  let targetCell = null;
  for (const off of offsets) {
    const gx = Math.round((agentB.gridX + off.dx) * 10) / 10;
    const gy = Math.round((agentB.gridY + off.dy) * 10) / 10;
    const isOccupied = this.agents.some(a => a.id !== agentA.id && Math.hypot(a.gridX - gx, a.gridY - gy) < 0.9);
    if (!isOccupied && gx >= 1 && gx < 63 && gy >= 1 && gy < 47) {
      targetCell = { gx, gy };
      break;
    }
  }
  if (!targetCell) targetCell = { gx: agentB.gridX + 1.2, gy: agentB.gridY };

  agentA.bubble = `Menemui ${agentB.name}`;
  agentA.domainState = 'CONVERSING';
  agentA.targetAgent = agentB;
  agentA.setDestination(targetCell.gx, targetCell.gy, this.pathfinder);
  return true;
}
```

Saat agen A tiba, hadapkan kedua agen dan picu dialog dua arah (`triggerConversationExchange`) dengan audio chime dan durasi bicara otomatis.

### C. Dek Perintah Taktis Cepat (Quick Inspector Command Deck)
Saat karakter agen diklik langsung di kanvas:
1. Munculkan kartu popover yang berisi dropdown `PINDAH KE KURSI RUANGAN` dan `AJAK BERBINCANG (DEKATI REKAN)`.
2. Sertakan baris chip aksi cepat 1-klik (`Rapat`, `Coding`, `Uji QA`, `Lounge`) untuk routing instan tanpa perlu membuka dock samping.
3. Gambarkan retikel target melayang berdenyut (`renderDestinationMarker`) pada petak kursi tujuan agar pengguna mendapatkan kepastian visual ke mana agen sedang diarahkan.

---

## 12. Direct Canvas RTS Interaction & Master Office Operations

Untuk menghilangkan ketergantungan pada drawer dan memberikan pengalaman taktil kelas game strategi:

### A. Contextual Double-Click / Direct Canvas RTS Dispatch
Terapkan logika pointer di kanvas:
- **Seleksi Agen A $\rightarrow$ Klik Agen B:** Langsung memicu `talkToAgent(agentA.id, agentB.id)`. Agen A mendekat ke petak kosong di dekat Agen B (jarak 1.2 grid) dan dialog dua arah dimulai secara natural.
- **Seleksi Agen A $\rightarrow$ Klik Kursi Kosong:** Langsung memicu `moveAgentToSpecificSeat(agentA.id, seat)`.
- **Hover Feedback Kursi:** Saat kursor melayang di atas kursi kosong saat agen aktif dipilih, sorot kursi dengan aura cyan terang dan tampilkan label `[Duduk di ${seat.label}]`.

### B. Master Office Operations (1-Klik Orkestrasi Global)
Sediakan dua kontrol komando tingkat master:
1. **Rapat Pleno (Semua Agen):** Memanggil seluruh 10 agen secara serentak ke 10 kursi meja konferensi Meeting Room.
2. **Kembali ke Divisi:** Mengirimkan seluruh agen kembali ke meja workstation spesialis mereka masing-masing secara simultan.

### C. Postur Duduk Fisik & Orientasi Hadap 4 Arah
Saat agen berada di status duduk (`!isWalking && a.targetSeat`):
- Turunkan torso tubuh sebesar 4px mendekati permukaan meja (`bodyY = iy - 11`).
- Lipat kaki ke depan dalam posisi rileks (`ctx.roundRect(ix - 5, iy - 4, 10, 4, 2)`).
- Sesuaikan arah hadap wajah (Utara, Selatan, Timur, Barat) berdasarkan arah kursi terhadap meja (misal: kursi di utara meja menghadap ke Selatan ke arah meja rapat).

### D. Audio Feedback Sintesis Mesin Tik (Typewriter Audio Synth)
Gunakan osilator sine acak berfrekuensi tinggi (1200 - 1600 Hz) berdurasi sangat singkat (20ms) dalam interval 40ms untuk mensimulasikan suara ketukan mekanikal saat balon percakapan dialog muncul.

---

## 13. Pathfinder Wall Obstacles & Doorway Traversal

Jangan biarkan `GridPathfinder` menggunakan `obstacles = new Set()` kosong. Ekstrak koordinat perimeter seluruh ruangan:

```javascript
initializeObstacles(layout) {
  const obstacles = new Set();
  const doors = new Set(layout.rooms.map(r => `${r.door.x},${r.door.y}`));

  for (const r of layout.rooms) {
    const z = r.zone;
    // Dinding horizontal utara dan selatan
    for (let x = z.x; x < z.x + z.width; x++) {
      const topKey = `${x},${z.y}`;
      const botKey = `${x},${z.y + z.height}`;
      if (!doors.has(topKey)) obstacles.add(topKey);
      if (!doors.has(botKey)) obstacles.add(botKey);
    }
    // Dinding vertikal barat dan timur
    for (let y = z.y; y < z.y + z.height; y++) {
      const leftKey = `${z.x},${y}`;
      const rightKey = `${z.x + z.width},${y}`;
      if (!doors.has(leftKey)) obstacles.add(leftKey);
      if (!doors.has(rightKey)) obstacles.add(rightKey);
    }
  }
  return obstacles;
}
```

Dengan mengalokasikan dinding sebagai rintangan dan membiarkan pintu terbuka, algoritma A* secara otomatis mengarahkan agen keluar melalui pintu ruangan dan menyusuri koridor alih-alih menembus dinding 2.5D.

---

## 14. Interactive Fixtures & Dynamic World Props

Daftarkan furnitur/perangkat utama kantor sebagai objek interaktif berkemampuan klik (*clickable fixtures*):

```javascript
createInteractiveFixtures() {
  return [
    { id: 'fix_espresso', roomId: 'lounge_waiting', label: 'Mesin Espresso La Marzocco', gx: 5, gy: 43, action: 'makeCoffee' },
    { id: 'fix_whiteboard', roomId: 'strategy_room', label: 'Papan Tulis Arsitektur 6-Track', gx: 20, gy: 4, action: 'viewWorkGraph' },
    { id: 'fix_server_rack', roomId: 'backup_room', label: 'Server Rack & Cold Storage', gx: 52, gy: 34, action: 'viewBackup' },
    { id: 'fix_radar_holo', roomId: 'observation_center', label: 'Konsol Radar & Proyektor Telemetri', gx: 9, gy: 23, action: 'viewTelemetry' },
    { id: 'fix_cnc_machine', roomId: 'tool_factory', label: 'Mesin Sintesis Tool & Sandbox', gx: 54, gy: 6, action: 'viewTools' }
  ];
}
```

- **Hover Reticle:** Saat kursor berada dalam radius 1.8 grid unit dari perabot interaktif, render cincin elips bergaris putus-putus berputar cyan di lantai ubin dan tampilkan badge label nama objek.
- **Contextual Dispatch:** Klik pada mesin espresso langsung menugaskan agen terdekat berjalan ke Lounge untuk rehat kopi; klik pada papan tulis arsitektur langsung mengarahkan kamera dan membuka tab Work Graph DAG.

---

## 15. Mobile Pinch-to-Zoom & Multi-Touch Gestures

Untuk mencegah getaran kanvas (*jitter*) saat pengguna ponsel mencubit layar dengan 2 jari:

```javascript
const activePointers = new Map();

canvas.addEventListener('pointerdown', e => {
  activePointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (activePointers.size === 1) {
    this.isDragging = true;
    this.dragStartX = e.clientX - this.originX;
    this.dragStartY = e.clientY - this.originY;
  }
});

canvas.addEventListener('pointermove', e => {
  if (!activePointers.has(e.pointerId)) return;
  activePointers.set(e.pointerId, { x: e.clientX, y: e.clientY });

  if (activePointers.size === 2) {
    // 2-Finger Pinch Zoom
    const [p1, p2] = Array.from(activePointers.values());
    const currentDist = Math.hypot(p1.x - p2.x, p1.y - p2.y);
    if (this.lastPinchDist) {
      const pinchFactor = currentDist / this.lastPinchDist;
      this.targetScale = Math.max(0.05, Math.min(2.5, this.targetScale * pinchFactor));
    }
    this.lastPinchDist = currentDist;
  } else if (activePointers.size === 1 && this.isDragging) {
    this.originX = e.clientX - this.dragStartX;
    this.originY = e.clientY - this.dragStartY;
    this.targetOriginX = this.originX;
    this.targetOriginY = this.originY;
  }
});

const onPointerUp = e => {
  activePointers.delete(e.pointerId);
  if (activePointers.size < 2) this.lastPinchDist = null;
  if (activePointers.size === 0) this.isDragging = false;
};
canvas.addEventListener('pointerup', onPointerUp);
canvas.addEventListener('pointercancel', onPointerUp);
```

---

## 16. Safe Turn-Taking Dialogue Timers & Memory Leak Prevention

Saat menjalankan alur percakapan atau rapat bertahap multi-babak, selalu kelola ID timer dalam array dan bersihkan sebelum memulai siklus baru:

```javascript
class DialogueSequenceManager {
  constructor() {
    this.timers = [];
  }

  stopAll() {
    this.timers.forEach(t => clearTimeout(t));
    this.timers = [];
  }

  scheduleStep(fn, delayMs) {
    const tid = setTimeout(() => {
      this.timers = this.timers.filter(t => t !== tid);
      fn();
    }, delayMs);
    this.timers.push(tid);
    return tid;
  }
}
```
Panggil `dialogueManager.stopAll()` seketika pengguna memicu perintah kontradiktif (seperti tombol *Kembali ke Divisi* atau seleksi agen lain) untuk mengeliminasi konflik race condition.

---

## 17. Camera Pan Boundary Clamping & Quick Recenter

Mencegah kanvas terlempar hilang ke ruang hampa kosong saat pengguna melakukan *pan/drag* agresif:

```javascript
// Di dalam pointermove handler
const maxPanX = Math.max(1000, this.width * 1.6);
const maxPanY = Math.max(800, this.height * 1.6);
this.originX = Math.max(-maxPanX, Math.min(maxPanX, e.clientX - this.dragStartX));
this.originY = Math.max(-maxPanY, Math.min(maxPanY, e.clientY - this.dragStartY));
this.targetOriginX = this.originX;
this.targetOriginY = this.originY;

// Metode pemulihan kamera (Key 'R')
recenterCamera() {
  this.targetOriginX = 0;
  this.targetOriginY = 80;
  this.targetScale = 0.95;
  this.selectedRoom = null;
}
```

---

## 18. Walking Path Trajectory & Tactical Waypoint Nodes

Menggambar rute spasial A* yang sedang dilalui karakter di atas lantai kanvas:

```javascript
renderAgentPaths(ctx) {
  for (const a of this.agents) {
    if (a.state === 'WALKING' && a.path && a.path.length > 0) {
      ctx.save();
      ctx.beginPath();
      const [startX, startY] = this.gridToIso(a.gridX + (a.dodgeOffsetX || 0), a.gridY + (a.dodgeOffsetY || 0));
      ctx.moveTo(startX, startY);

      for (const pt of a.path) {
        const [px, py] = this.gridToIso(pt.x, pt.y);
        ctx.lineTo(px, py);
      }
      ctx.strokeStyle = `${a.color}66`;
      ctx.lineWidth = 1.8;
      ctx.setLineDash([4, 5]);
      ctx.lineDashOffset = -this.clockTime * 18;
      ctx.stroke();

      // Waypoint nodes bercahaya
      for (const pt of a.path) {
        const [px, py] = this.gridToIso(pt.x, pt.y);
        ctx.beginPath();
        ctx.arc(px, py, 2.2, 0, Math.PI * 2);
        ctx.fillStyle = a.color;
        ctx.fill();
      }
      ctx.restore();
    }
  }
}
```

---

## 19. 1-Click High-Resolution Canvas PNG Export & Global Shortcuts

Menyediakan fungsi ekspor tangkapan layar kanvas bersih dan pintasan taktis:

```javascript
function captureCanvasScreenshot() {
  if (!arenaEngine?.canvas) return;
  const dataURL = arenaEngine.canvas.toDataURL('image/png');
  const a = document.createElement('a');
  a.href = dataURL;
  a.download = `kantor-hermes-diorama-${Date.now()}.png`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

// Pintasan Keyboard Taktis Tambahan:
// '/' -> Buka dock samping dan fokuskan kursor ke pencarian roster
// 'R' -> Memusatkan kembali kamera ke default
// 'P' -> Ekspor tangkapan layar HD PNG instan
```

---

## 20. Drag-to-Scrub Timeline & Interactive Minimap Collapsing

### A. Drag-to-Scrub Timeline Replay (Pointer API with setPointerCapture)
Menghindari kewajiban mengklik berulang kali dengan mengizinkan seretan pointer mulus pada bilah progres:
```javascript
const progressTrack = $('#replay-progress-track');
if (progressTrack) {
  let isScrubbing = false;
  const scrubTo = (clientX) => {
    if (!replayEvents?.length) return;
    const rect = progressTrack.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    const targetIdx = Math.round(ratio * replayEvents.length);
    jumpToReplayEvent(targetIdx);
  };
  progressTrack.addEventListener('pointerdown', (e) => {
    isScrubbing = true;
    try { progressTrack.setPointerCapture?.(e.pointerId); } catch (_) {}
    scrubTo(e.clientX);
  });
  progressTrack.addEventListener('pointermove', (e) => {
    if (isScrubbing) scrubTo(e.clientX);
  });
  const stopScrub = (e) => {
    if (isScrubbing) {
      isScrubbing = false;
      try { progressTrack.releasePointerCapture?.(e.pointerId); } catch (_) {}
    }
  };
  progressTrack.addEventListener('pointerup', stopScrub);
  progressTrack.addEventListener('pointercancel', stopScrub);
}
```

### B. Collapsible Minimap Radar Box
Mencegah kotak kosong melayang saat radar diminimize:
```css
.game-minimap-wrap.collapsed {
  padding: 4px 10px;
  gap: 0;
  border-radius: 8px;
}
.game-minimap-wrap.collapsed #minimap-canvas {
  display: none !important;
}
```

---

## 21. Living Diorama Micro-Effects (Steam, Airflow & Acoustic Resonances)

- **Kepulan Uap Mesin Kopi Lounge:** Animasikan 3-4 partikel uap melayang ke atas dengan offset sinusoidal `Math.sin(clock * 3) * 2` dan fading opacity lembut di atas mesin espresso.
- **Konveksi Pendingin Ruang Server:** Gambarkan garis aliran angin konveksi pendingin beranimasi cyan dengan alpha lembut di antara rak server cluster.
- **Riak Kedatangan di Petak Tujuan:** Saat agen mendarat di kursi tujuan, pancarkan gelombang riak elips lantai isometrik beranimasi (`arrivalRipples`) untuk memberikan umpan balik visual landing yang jelas.
- **Gelombang Resonansi Akustik Percakapan:** Gambar kurva lengkung berdenyut bergaris putus-putus dan riak elips lantai yang menghubungkan dua agen yang sedang berdialog.

---

## 22. Differentiated Audio Presets & Native Fullscreen Sync

- **Profil Audio Akustik Unik:** Bedakan frekuensi dan kurva suara: fanfare 4-nada (Kickoff), chime harmoni (Assign API), dual sawtooth alert sweep (Hotpatch), kristal pip ganda (Uji QA), dan deep resonant sub-bass (Cold Storage Backup).
- **Sinkronisasi Native Fullscreen:** Selalu pasang event listener `document.addEventListener('fullscreenchange', ...)` agar status teks tombol dan visual active selalu sinkron dengan state browser sesungguhnya saat pengguna keluar dari layar penuh via tombol `ESC`.

---

## 23. DPI Minimap Coordinate Normalization, User Preference Persistence & Tactical ETA Indicators

### A. DPI-Normalized Minimap Click-to-Focus
Menjamin klik minimap selalu tepat sasaran pada layar HiDPI / Retina atau saat ukuran canvas di-override CSS:
```javascript
minimapCanvas.addEventListener('click', (e) => {
  if (!arenaEngine || !arenaEngine.layout) return;
  const rect = minimapCanvas.getBoundingClientRect();
  const scaleCoordX = minimapCanvas.width / (rect.width || 1);
  const scaleCoordY = minimapCanvas.height / (rect.height || 1);
  const clickX = (e.clientX - rect.left) * scaleCoordX;
  const clickY = (e.clientY - rect.top) * scaleCoordY;

  const { columns, rows } = arenaEngine.layout.grid;
  const pad = 6;
  const scaleX = (minimapCanvas.width - pad * 2) / columns;
  const scaleY = (minimapCanvas.height - pad * 2) / rows;
  const gridX = (clickX - pad) / scaleX;
  const gridY = (clickY - pad) / scaleY;

  const clickedRoom = arenaEngine.layout.rooms.find(r =>
    gridX >= r.zone.x && gridX <= r.zone.x + r.zone.width &&
    gridY >= r.zone.y && gridY <= r.zone.y + r.zone.height
  );
  if (clickedRoom) {
    SoundFX.playChime();
    arenaEngine.focusRoom(clickedRoom.id);
    showRoomInspector(clickedRoom);
    showToast?.(`Radar: Fokus ke ${clickedRoom.name}`);
  }
});
```

### B. User Preference Persistence in LocalStorage
Menjaga preferensi volume, SFX, dan tema cahaya sirkadian tetap aktif saat halaman di-refresh:
```javascript
const UserPrefs = {
  load() {
    try {
      const vol = localStorage.getItem('kantor_vol');
      if (vol !== null) {
        const v = parseFloat(vol);
        SoundFX.setVolume(v);
        const slider = document.querySelector('#master-volume-slider');
        if (slider) slider.value = String(Math.round(v * 100));
      }
      const sfx = localStorage.getItem('kantor_sfx');
      if (sfx !== null) {
        SoundFX.enabled = sfx === '1';
        const el = document.querySelector('#btn-audio-toggle');
        if (el) el.textContent = SoundFX.enabled ? 'SFX: ON' : 'SFX: OFF';
      }
      const theme = localStorage.getItem('kantor_theme');
      if (theme) {
        const themeSelect = document.querySelector('#theme-select');
        if (themeSelect) {
          themeSelect.value = theme;
          applyCircadianAtmosphere(theme);
        }
      }
    } catch (_) {}
  },
  save(k, v) {
    try { localStorage.setItem(k, String(v)); } catch (_) {}
  }
};
```

### C. Tactical ETA Metric Capsule at Waypoint Terminus
Menampilkan estimasi jarak dan waktu tempuh pada jalur A* agen aktif:
```javascript
if (agent.path.length > 0 && (this.selectedAgent?.id === agent.id || this.hoveredAgent?.id === agent.id)) {
  const lastNode = agent.path[agent.path.length - 1];
  const [lx, ly] = this.gridToIso(lastNode.x, lastNode.y);
  const steps = agent.path.length;
  const eta = (steps / (agent.speed || 6)).toFixed(1);
  const badgeText = `ETA: ${steps} petak · ${eta}s`;

  ctx.save();
  ctx.font = 'bold 8.5px "JetBrains Mono", monospace';
  const tw = ctx.measureText(badgeText).width;
  const bw = tw + 14;
  const bh = 15;
  const bx = lx - bw / 2;
  const by = ly - 28;

  ctx.fillStyle = 'rgba(8, 12, 20, 0.92)';
  ctx.beginPath();
  ctx.roundRect(bx, by, bw, bh, 4);
  ctx.fill();
  ctx.strokeStyle = agent.color || '#38bdf8';
  ctx.lineWidth = 1.2;
  ctx.stroke();

  ctx.fillStyle = '#F8FAFC';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(badgeText, lx, by + bh / 2);
  ctx.restore();
}
```

---

## 24. Tactical Sweep Beams, Directional Shadows, Clipboard Export & Station Tethers

### A. Concentric Range Rings & Rotating Radar Sweep
Mengubah minimap menjadi radar militer/taktis dengan gelombang sapuan berputar dan pendaran fosfor:
```javascript
// Di dalam renderMinimap:
const cx = mW / 2;
const cy = mH / 2;
const maxR = Math.hypot(mW, mH) / 2;

mCtx.save();
// Lingkaran konsentris
mCtx.strokeStyle = 'rgba(56, 189, 248, 0.12)';
mCtx.lineWidth = 1;
mCtx.beginPath();
mCtx.arc(cx, cy, maxR * 0.35, 0, Math.PI * 2);
mCtx.arc(cx, cy, maxR * 0.7, 0, Math.PI * 2);
mCtx.stroke();

// Gelombang sapuan dengan phosphor trail
const sweepAngle = (this.clockTime * 1.8) % (Math.PI * 2);
mCtx.beginPath();
mCtx.moveTo(cx, cy);
mCtx.arc(cx, cy, maxR, sweepAngle - 0.28, sweepAngle);
mCtx.closePath();
mCtx.fillStyle = 'rgba(56, 189, 248, 0.16)';
mCtx.fill();

// Garis pendar utama
mCtx.beginPath();
mCtx.moveTo(cx, cy);
mCtx.lineTo(cx + Math.cos(sweepAngle) * maxR, cy + Math.sin(sweepAngle) * maxR);
mCtx.strokeStyle = 'rgba(56, 189, 248, 0.85)';
mCtx.lineWidth = 1.5;
mCtx.stroke();
mCtx.restore();
```

### B. Proyeksi Bayangan Berarah Isometrik (Directional Skewed Shadows)
Menyelaraskan bayangan jatuh tanah dengan vektor cahaya barat laut:
```javascript
ctx.beginPath();
ctx.ellipse(ix + 2.5, iy + 3, 14, 6.5, Math.PI / 16, 0, Math.PI * 2);
ctx.fillStyle = 'rgba(0, 0, 0, 0.62)';
ctx.fill();
```

### C. 1-Click Clipboard Export dengan Audio Chime
```javascript
btnCopy.addEventListener('click', () => {
  navigator.clipboard.writeText(draftText).then(() => {
    SoundFX.playChime();
    btnCopy.textContent = 'Tersalin!';
    setTimeout(() => { btnCopy.textContent = 'Salin JSON'; }, 2000);
    showToast('Draf JSON berhasil disalin ke clipboard');
  });
});
```

### D. Station Return Tether Line
Menghubungkan agen terpilih yang sedang berpindah ruangan dengan workstation asalnya:
```javascript
if (agent.targetSeat && Math.hypot(agent.gridX - seat.gx, agent.gridY - seat.gy) > 1.2) {
  const [ax, ay] = this.gridToIso(agent.gridX, agent.gridY);
  const [sx, sy] = this.gridToIso(seat.gx, seat.gy);
  ctx.beginPath();
  ctx.moveTo(ax, ay - 4);
  ctx.lineTo(sx, sy - 6);
  ctx.strokeStyle = 'rgba(245, 158, 11, 0.45)';
  ctx.lineWidth = 1.2;
  ctx.setLineDash([3, 4]);
  ctx.lineDashOffset = this.clockTime * 10;
  ctx.stroke();
}
```

---

## 25. Duplex Realtime Audio Synthesis, Spatial Radio Waves, & Reconnection Buffer

### A. Variable Micro-Click & Dissonant Abort Synthesizer
Mencegah kelelahan auditori dari aliran 20-30 token/detik:
```javascript
playDuplexToken() {
  if (!this.enabled) return;
  try {
    this.init();
    if (!this.ctx || this.ctx.state === 'suspended') return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    const freq = 1100 + Math.random() * 200; // 1100 - 1300 Hz acak halus
    osc.frequency.setValueAtTime(freq, now);
    gain.gain.setValueAtTime(0.015 * this.masterVolume, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.018);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.02);
  } catch (_) {}
},
playDuplexInterrupt() {
  if (!this.enabled) return;
  try {
    this.init();
    if (!this.ctx) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();
    const now = this.ctx.currentTime;
    [220, 233.08].forEach((freq) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(freq, now);
      osc.frequency.exponentialRampToValueAtTime(80, now + 0.25);
      gain.gain.setValueAtTime(0.14 * this.masterVolume, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.26);
    });
  } catch (_) {}
}
```

### B. Spatial Radio Emission Ripples on Active Reasoners
Memancarkan gelombang denyut radio cyan di lantai isometrik agen saat transmisi duplex aktif:
```javascript
if (a.isDuplexStreaming && a.state === 'WORKING') {
  const rippleRadius = 24 + ((this.clockTime * 22) % 18);
  const rippleAlpha = Math.max(0, 0.45 - (rippleRadius - 24) / 18 * 0.45);
  ctx.save();
  ctx.beginPath();
  ctx.ellipse(ix, iy + 2, rippleRadius, rippleRadius * 0.5, 0, 0, Math.PI * 2);
  ctx.strokeStyle = `rgba(56, 189, 248, ${rippleAlpha.toFixed(2)})`;
  ctx.lineWidth = 1.2;
  ctx.setLineDash([3, 4]);
  ctx.lineDashOffset = -this.clockTime * 14;
  ctx.stroke();
  ctx.restore();
}
```

### C. Direct-Mention `@agent` Routing for Rapid In-Flight Steering
```javascript
const mentionMatch = rawText.match(/^@([a-zA-Z0-9_]+)\s*(.*)/s);
if (mentionMatch) {
  const rawMention = mentionMatch[1].toLowerCase();
  const directive = mentionMatch[2].trim() || 'Lanjutkan tugas prioritas';
  const aliasMap = {
    'backend': 'dev_backend',
    'frontend': 'dev_frontend',
    'qa': 'qa_agent',
    'architect': 'architect',
    'hermes': 'hermes'
  };
  const targetAgentId = aliasMap[rawMention] || rawMention;
  const targetAgent = arenaEngine?.agents?.find(a => a.id === targetAgentId);
  if (targetAgent) {
    arenaEngine.selectedAgent = targetAgent;
    showAgentInspector(targetAgent);
  }
  duplexClient.steerTask(targetAgentId, directive);
}
```







