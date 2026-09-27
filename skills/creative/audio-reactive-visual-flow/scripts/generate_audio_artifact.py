#!/usr/bin/env python3
"""
Generator Artifact Standalone Audio-Reactive Visual Flow
Bagas Cihuy & Hermes Agent
"""

import sys, os, argparse

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Audio-Reactive Visual Flow</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body, html { width: 100%; height: 100%; overflow: hidden; background: #0b0c10; font-family: monospace; color: #c5c6c7; }
    #canvas-container { position: relative; width: 100vw; height: 100vh; }
    canvas { display: block; width: 100%; height: 100%; }
    .hud-overlay {
      position: absolute; top: 20px; left: 20px; z-index: 10;
      background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(12px);
      padding: 14px 18px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);
      font-size: 13px; line-height: 1.5; pointer-events: none;
    }
    .hud-title { font-weight: bold; color: #66fcf1; text-transform: uppercase; margin-bottom: 4px; }
    .hud-stat { display: flex; justify-content: space-between; gap: 16px; }
    .btn-toggle {
      position: absolute; bottom: 24px; left: 24px; z-index: 10;
      background: #45a29e; color: #0b0c10; border: none; padding: 10px 18px;
      font-size: 12px; font-weight: bold; border-radius: 6px; cursor: pointer;
      text-transform: uppercase; letter-spacing: 0.5px; transition: background 0.2s;
    }
    .btn-toggle:hover { background: #66fcf1; }
  </style>
</head>
<body>
  <div id="canvas-container">
    <canvas id="visualizer-canvas"></canvas>
    <div class="hud-overlay">
      <div class="hud-title">Audio Reactive Vibe Flow</div>
      <div class="hud-stat"><span>ENERGY BASS:</span><span id="stat-bass">0.00</span></div>
      <div class="hud-stat"><span>ENERGY MID:</span><span id="stat-mid">0.00</span></div>
      <div class="hud-stat"><span>ENERGY HIGH:</span><span id="stat-high">0.00</span></div>
      <div class="hud-stat"><span>STATUS:</span><span id="stat-status" style="color:#66fcf1;">ACTIVE</span></div>
    </div>
    <button class="btn-toggle" id="btn-audio">AKTIFKAN MIKROFON / SYNTH</button>
  </div>

  <script>
    (function() {
      const canvas = document.getElementById('visualizer-canvas');
      const ctx = canvas.getContext('2d');
      const statBass = document.getElementById('stat-bass');
      const statMid = document.getElementById('stat-mid');
      const statHigh = document.getElementById('stat-high');
      const statStatus = document.getElementById('stat-status');
      const btnAudio = document.getElementById('btn-audio');

      let audioCtx = null;
      let analyser = null;
      let dataArray = null;
      let isSimulated = true;
      let animId = null;
      let bassEnv = 0, midEnv = 0, highEnv = 0;
      let idleFrames = 0;

      function resize() {
        canvas.width = window.innerWidth * window.devicePixelRatio;
        canvas.height = window.innerHeight * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      }
      window.addEventListener('resize', resize);
      resize();

      function initSyntheticAudio() {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioCtx = new AudioContext();
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        dataArray = new Uint8Array(analyser.frequencyBinCount);

        // Brown noise / periodic synth for demo
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(65, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
        osc.connect(gain);
        gain.connect(analyser);
        gain.connect(audioCtx.destination);
        osc.start();
        isSimulated = false;
        btnAudio.textContent = 'MODE SINTESIS AKTIF';
      }

      btnAudio.addEventListener('click', () => {
        if (!audioCtx) {
          initSyntheticAudio();
        } else if (audioCtx.state === 'suspended') {
          audioCtx.resume();
        }
      });

      function render(time) {
        animId = requestAnimationFrame(render);
        const w = window.innerWidth;
        const h = window.innerHeight;
        const cx = w / 2;
        const cy = h / 2;

        let bVal = 0, mVal = 0, hVal = 0;
        if (analyser) {
          analyser.getByteFrequencyData(dataArray);
          bVal = (dataArray[1] + dataArray[2] + dataArray[3]) / 3 / 255;
          mVal = (dataArray[8] + dataArray[12] + dataArray[16]) / 3 / 255;
          hVal = (dataArray[24] + dataArray[32] + dataArray[40]) / 3 / 255;
        } else {
          // Synthetic procedural flow
          const t = time * 0.002;
          bVal = 0.35 + 0.35 * Math.sin(t * 2.0);
          mVal = 0.25 + 0.25 * Math.cos(t * 3.5);
          hVal = 0.15 + 0.15 * Math.sin(t * 5.0);
        }

        // Asymmetric ballistics
        bassEnv += (bVal > bassEnv ? 0.65 : 0.08) * (bVal - bassEnv);
        midEnv += (mVal > midEnv ? 0.65 : 0.08) * (mVal - midEnv);
        highEnv += (hVal > highEnv ? 0.65 : 0.08) * (hVal - highEnv);

        statBass.textContent = bassEnv.toFixed(2);
        statMid.textContent = midEnv.toFixed(2);
        statHigh.textContent = highEnv.toFixed(2);

        // Background trailing fade
        ctx.fillStyle = 'rgba(11, 12, 16, 0.2)';
        ctx.fillRect(0, 0, w, h);

        // Circular geometric audio reactive rings
        const baseRadius = Math.min(w, h) * 0.18 + (bassEnv * 40);
        const segments = 64;

        ctx.save();
        ctx.translate(cx, cy);
        ctx.beginPath();
        for (let i = 0; i <= segments; i++) {
          const theta = (i / segments) * Math.PI * 2;
          const deform = Math.sin(theta * 6 + time * 0.003) * (midEnv * 28) + Math.cos(theta * 12) * (highEnv * 15);
          const r = baseRadius + deform;
          const x = Math.cos(theta) * r;
          const y = Math.sin(theta) * r;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.strokeStyle = '#66fcf1';
        ctx.lineWidth = 2.5 + (bassEnv * 3);
        ctx.shadowColor = '#45a29e';
        ctx.shadowBlur = 15 + (bassEnv * 20);
        ctx.stroke();

        // Inner glowing core
        ctx.beginPath();
        ctx.arc(0, 0, Math.max(1, baseRadius * 0.35 * (1 + bassEnv * 0.5)), 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(102, 252, 241, ' + (0.15 + bassEnv * 0.3) + ')';
        ctx.fill();
        ctx.restore();
      }

      render(0);
    })();
  </script>
</body>
</html>
"""

def main():
    parser = argparse.ArgumentParser(description="Generate Audio-Reactive Visual Flow Artifact")
    parser.add_argument("--output", default="audio_reactive_preview.html", help="Output path")
    args = parser.parse_args()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)
    print(f"Artifact generated successfully: {args.output}")

if __name__ == "__main__":
    main()
