---
name: realtime-voice-agent-architecture
description: Use when building real-time voice agents or voice calls.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  hermes:
    category: autonomous-ai-agents
    tags:
      - voice-agent
      - websocket
      - vad
      - barge-in
      - tts-streaming
      - speech-recognition
---

# Real-Time Voice Agent Architecture

Gunakan skill ini ketika merancang, membangun, dan mengoptimalkan sistem agen suara interaktif dua arah (*voice call* / percakapan telepon real-time). Mengatur arsitektur WebSocket full-duplex, deteksi aktivitas suara (VAD), pencegahan umpan balik akustik (*acoustic echo suppression*), pemotongan pembicaraan (*barge-in / interruption*), serta pemipaan sintesis audio bertahap (*clause-level streaming TTS*).

## When to Use

- Membangun antarmuka telepon web atau VoIP dua arah antara pengguna dan AI.
- Menangani keluhan suara bertumpuk, memantul-mantul, atau agen menjawab suaranya sendiri (*acoustic feedback loop*).
- Mengukur dan mengurangi latensi dari akhir ujaran pengguna sampai audio pertama benar-benar terdengar; catat p50/p95, jangan menjanjikan <500ms sebelum uji jaringan dan perangkat nyata.
- Mengimplementasikan fitur interupsi alami: pengguna dapat memotong ucapan AI kapan saja dan AI langsung berhenti berbicara.

## Gerbang Kualitas Suara Sebelum Membangun

Jika pengguna meminta suara natural seperti percakapan GPT, jangan menganggap Neural TTS generik sebagai hasil setara hanya karena MP3 berhasil dibuat. Mulai dari naskah uji Bahasa Indonesia yang sama (nama, angka, emosi, jeda, pertanyaan), sintesis sampel beberapa penyedia, dan minta pengguna memilih secara buta sebelum mengikat arsitektur. Pisahkan kualitas TTS satu arah dari naturalitas percakapan live (turn-taking, barge-in, latency). Laporan harus menyebut model/provider aktual, biaya pemakaian, persetujuan pengiriman teks, dan keterbatasan yang belum diuji.

Periksa katalog model router dan kapabilitas output audio/endpoint speech secara langsung sebelum menyimpulkan akses: login/model teks atau audio input tidak otomatis memberi TTS/audio output. Jika output audio tidak terdaftar, bedakan 'tidak tersedia dalam katalog yang diperiksa' dari kepastian bahwa seluruh endpoint router tidak mendukungnya; gunakan API audio penyedia tersendiri bila dibutuhkan dan hitung biaya jalur itu secara terpisah.

## Architecture Overview

Bedakan tiga jalur resmi sebelum memilih stack: GPT-Live (percakapan full-duplex dengan backend terpisah, termasuk client delegation ke agen sendiri), Realtime speech-to-speech (audio, reasoning, tools dalam satu sesi), dan pipeline STT–LLM–TTS (kendali tiap tahap, tetapi interupsi/audio scheduling perlu dioperasikan). TTS saja bukan live voice. Rujukan: https://developers.openai.com/api/docs/guides/voice-agents dan https://developers.openai.com/api/docs/guides/live-delegation. Ukur bahasa Indonesia dan biaya per tugas berhasil sebelum memilih.

Arsitektur suara real-time modern menghindari siklus HTTP request-response statis dan menggunakan saluran streaming dua arah:

1. **Voice Gateway (Full-Duplex WebSocket):** Kanal persisten untuk pertukaran sinyal kendali, teks transkrip lisan, dan paket audio base64/PCM.
2. **Client VAD & Mic Energy Analyzer:** Web Audio API `AudioContext` + `AnalyserNode` memantau level RMS/volume mikrofon real-time.
3. **Barge-in / Interruption Handler:** Sinyal seketika yang memutus buffer audio klien dan membatalkan proses inferensi LLM serta proses pekerja TTS di server.
4. **Clause-Level Streaming TTS:** LLM di-stream dan dipecah berdasarkan tanda baca klausa (`,`, `.`, `?`, `!`), sehingga audio klausa pertama diputar saat klausa kedua sedang disintesis.

Lihat rincian 8 pilar arsitektur di [references/gpt_live_voice_architecture.md](references/gpt_live_voice_architecture.md).

## Implementation Procedure

### 1. Bangun Server WebSocket Voice Gateway
Hubungkan WebSocket server langsung ke server HTTP utama pada rute khusus (misal `/ws/telepon`):

```javascript
const { WebSocketServer } = require('ws');
const wss = new WebSocketServer({ noServer: true });

server.on('upgrade', (req, socket, head) => {
  if (req.url && req.url.startsWith('/ws/telepon')) {
    wss.handleUpgrade(req, socket, head, (ws) => {
      wss.emit('connection', ws, req);
    });
  }
});
```

### 2. Implementasikan Pembatalan Inferensi & TTS (*Abort Controller*)
Setiap sesi panggilan harus memiliki `AbortController` yang aktif dan referensi proses anak TTS:

```javascript
class VoiceSession {
  handleInterrupt() {
    if (this.currentAbortController) {
      this.currentAbortController.abort();
      this.currentAbortController = null;
    }
    // Hentikan proses sintesis TTS yang sedang berjalan di OS
    if (this.activeTtsProcess) {
      try { this.activeTtsProcess.kill('SIGTERM'); } catch(e){}
      this.activeTtsProcess = null;
    }
    this.ws.send(JSON.stringify({ type: 'interrupted', reason: 'user_barge_in' }));
  }
}
```

### 3. Pemipaan Audio Bertahap (*Pipelined Clause Chunking*)
Gunakan regex delimiter untuk menangkap klausa kalimat pertama secepat mungkin:

```javascript
const CLAUSE_DELIMITERS = /([.?!,;\n]+)/;
let clauseBuffer = '';

for await (const chunk of llmStream) {
  const token = chunk.choices[0]?.delta?.content || '';
  clauseBuffer += token;

  const parts = clauseBuffer.split(CLAUSE_DELIMITERS);
  if (parts.length > 2) {
    const readyClause = (parts[0] + parts[1]).trim();
    clauseBuffer = parts.slice(2).join('');
    // Kirim langsung ke worker TTS tanpa menunggu LLM selesai
    synthesizeAndPushChunk(readyClause);
  }
}
```

### 4. Client-Side Audio Gating, Cooldown & Barge-In
Di browser, kelola siklus bicara dengan antrean audio (`audioQueue`), pemutusan mikrofon otomatis saat AI bersuara (*smart-gating*), serta jeda pendinginan gema (*cooldown*):

```javascript
function playNextChunk() {
  if (audioQueue.length === 0) {
    currentAudioEl = null;
    // Jeda pendinginan 650ms agar sisa gema di ruangan reda sebelum mic dibuka
    clearTimeout(cooldownTimer);
    cooldownTimer = setTimeout(() => {
      isAgentSpeaking = false;
      if (inCall && !isMuted) startRecognitionSafe();
    }, 650);
    return;
  }

  isAgentSpeaking = true;
  // Mode Speaker HP: putus mic saat audio AI berbunyi agar tidak merekam diri sendiri
  if (mode === 'speaker') stopRecognitionSafe();

  const chunk = audioQueue.shift();
  currentAudioEl = new Audio(chunk.audio);
  currentAudioEl.onended = () => playNextChunk();
  currentAudioEl.play();
}

// Interupsi Instan (Tactile Barge-In)
function triggerBargeIn(reason) {
  if (currentAudioEl) { currentAudioEl.pause(); currentAudioEl = null; }
  audioQueue = [];
  isAgentSpeaking = false;
  ws.send(JSON.stringify({ type: 'interrupt', reason }));
  startRecognitionSafe();
}
```

## Pitfalls & Defensive Rules

- **Dual-Tier Acoustic Echo & Self-Reply Prevention ("AI Membalas AI"):** Pada peramban seluler (Chrome/Safari), mesin `webkitSpeechRecognition` tidak terhubung dengan *Hardware Acoustic Echo Cancellation* (AEC) elemen HTML5 `<audio>`. Pada mode *loudspeaker* (speaker HP tanpa headset), audio AI akan bocor langsung ke mikrofon, mentranskripsikan suara AI sendiri, memicu *barge-in* palsu, dan mengirimkannya kembali ke LLM hingga terjadi loop tanpa henti. Cegah dengan pertahanan dua lapis:
  1. *Client Smart-Gating & Cooldown:* Putus paksa mikrofon (`recognition.abort()`) seketika saat chunk audio pertama mulai diputar, dan abaikan setiap event transkrip yang masuk saat `isAgentSpeaking === true`. Terapkan jeda pendinginan minimal 650–700ms setelah chunk audio terakhir selesai diputar sebelum membuka kembali mikrofon (`recognition.start()`) agar gema ruangan dan getaran sasis HP reda total. Pada mode speaker HP, nonaktifkan *voice-triggered barge-in* (karena suara speaker akan memicu dirinya sendiri) dan ganti dengan *Tactile Barge-In* (ketuk layar/orb untuk memotong suara); sediakan opsi *voice barge-in* hands-free hanya untuk mode Headset/TWS.
  2. *Server-Side Echo Review:* Simpan identitas output audio/transkrip terakhir untuk diagnostik. Jangan membuang ucapan pengguna hanya berdasarkan kemiripan teks: pengguna bisa mengulang ucapan AI secara sengaja. Utamakan AEC/isolasi akustik, uji speaker vs headset, dan tandai transkrip mencurigakan untuk konfirmasi bila perlu.
- **Android Audio Device Lock Collision (`getUserMedia` vs `webkitSpeechRecognition`):** Pada sistem operasi Android/Chrome Mobile, memanggil `navigator.mediaDevices.getUserMedia()` (misal untuk pembacaan desibel/RMS VAD di Web Audio API) bersamaan dengan `webkitSpeechRecognition` akan memonopoli perangkat keras mikrofon (`AUDIO_SOURCE_MIC`), sehingga memicu galat OS: *"Pengenalan dan Sintesis Ucapan dari Google cannot record now as Chrome is recording"*. Dilarang membuka `getUserMedia` secara bersamaan dengan `SpeechRecognition` di peramban seluler; gunakan event native `rec.onspeechstart` dan `rec.onsoundstart` sebagai pemicu *barge-in* instan tanpa membaca desibel mentah, dan gerakkan animasi visualizer secara prosedural atau berbasis output audio.
- **Race Condition Interim vs Final STT:** Event `onresult` dari `SpeechRecognition` sering kali memancarkan hasil transkrip `interim` tepat sebelum paket `final` tiba. Tanpa penguncian *debounce* (`isProcessing` dan perbandingan `lastSentText`), server akan menerima dan memproses kalimat yang sama dua kali, memicu respon audio ganda. Pasang *debounce timer* (350ms untuk `final`, 850ms untuk `interim`) dan batalkan pengiriman jika teks sama persis dengan yang sedang diproses.
- **Z-Index & Mobile Safari Audio Context Auto-Play:** Browser seluler memblokir `AudioContext` dan objek `Audio` baru yang dipanggil tanpa interaksi sentuhan langsung. Selalu inisialisasi `new AudioContext()` dan panggil `audioContext.resume()` di dalam event handler klik tombol "Mulai Panggilan".
- **Zombie Process pada Fast Barge-In:** Jika pengguna memotong pembicaraan secara beruntun, proses CLI `edge-tts` atau pustaka audio eksternal dapat menumpuk di latar belakang dan menghabiskan CPU. Simpan referensi PID setiap child process dan panggil `.kill('SIGTERM')` secara eksplisit pada event `interrupt`.
- **Markdown Leaks pada Voice Synthesizer:** Mesin TTS akan mengeja simbol tanda baca seperti asterisk ganda `**`, backtick, tag pagar, atau format bullet. Wajib bersihkan teks LLM menggunakan ekspresi reguler pembersih Markdown (`s.replace(/[*#`_~]/g, '')`) sebelum diteruskan ke mesin suara.

## Verification Checklist

1. **Uji Koneksi Duplex:** Buka WebSocket publik `wss://<host>/ws/telepon`, pastikan status `session_ready` diterima dalam < 100ms.
2. **Uji Latensi Awal:** Ukur dari akhir ujaran sampai audio pertama terdengar di speaker; laporkan p50/p95 dan jaringan/perangkat. Penerimaan chunk server saja bukan TTFA pengguna. Tetapkan target setelah baseline.
3. **Uji Barge-In:** Saat AI sedang mengucapkan kalimat panjang, bersuara atau tekan tombol potong. Verifikasi audio browser berhenti seketika dan server mencatat event `interrupted`.
4. **Uji Zero-Echo:** Lakukan panggilan menggunakan loudspeaker ponsel tanpa headphone; pastikan ucapan AI tidak memicu input teks baru ke diri sendiri.
