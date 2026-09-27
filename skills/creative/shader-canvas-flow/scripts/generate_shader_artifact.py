import sys, os

output_path = sys.argv[1] if len(sys.argv) > 1 else "shader_canvas_preview.html"

html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Shader Canvas Flow - Vibe Coding Backdrop</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #0b0a10;
      color: #faf6ef;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      position: relative;
    }
    #gl-canvas {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 0;
      pointer-events: none;
    }
    .content-overlay {
      position: relative;
      z-index: 10;
      max-width: 900px;
      margin: 80px auto;
      padding: 32px;
      background: rgba(18, 16, 26, 0.75);
      backdrop-filter: blur(24px) saturate(180%);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
    }
    h1 { font-size: 2.2rem; margin-bottom: 12px; color: #ffffff; letter-spacing: -0.02em; }
    p { color: #a1a1aa; line-height: 1.6; margin-bottom: 24px; font-size: 1.05rem; }
    .hud-chips { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 24px; }
    .chip {
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-family: monospace;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .chip-active { border-color: #10b981; color: #10b981; }
    textarea {
      width: 100%;
      height: 140px;
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 8px;
      color: #f4f4f5;
      font-family: monospace;
      padding: 14px;
      font-size: 0.95rem;
      outline: none;
      resize: vertical;
    }
    textarea:focus { border-color: #8b5cf6; }
  </style>
</head>
<body>
  <canvas id="gl-canvas"></canvas>
  <div class="content-overlay">
    <div class="hud-chips">
      <span class="chip chip-active" id="status-chip">STATUS: RUNNING (60 FPS)</span>
      <span class="chip" id="energy-chip">ENERGY: 0.00</span>
      <span class="chip" id="dpr-chip">DPR: 1.00</span>
    </div>
    <h1>Shader Canvas Flow & Ambient Vibe</h1>
    <p>Latar belakang GLSL domain warping procedural WebGL interaktif. Coba gerakkan mouse, klik, atau ketik kode di kotak bawah untuk memicu lonjakan energi kanvas.</p>
    <textarea id="code-input" placeholder="// Ketik kode di sini untuk melihat reaksi visual ambient..."></textarea>
  </div>

  <script>
    const canvas = document.getElementById('gl-canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) {
      document.body.style.background = '#14120e';
      console.warn('WebGL not supported');
    }

    const vsSource = `
      attribute vec2 a_pos;
      varying vec2 v_uv;
      void main() {
        v_uv = (a_pos + 1.0) * 0.5;
        gl_Position = vec4(a_pos, 0.0, 1.0);
      }
    `;

    const fsSource = `
      precision highp float;
      uniform vec2 u_resolution;
      uniform float u_time;
      uniform vec4 u_mouse;
      uniform float u_energy;
      varying vec2 v_uv;

      float hash(vec2 p) {
        p = fract(p * vec2(123.34, 456.21));
        p += dot(p, p + 45.32);
        return fract(p.x * p.y);
      }

      float noise(vec2 p) {
        vec2 i = floor(p);
        vec2 f = fract(p);
        f = f * f * (3.0 - 2.0 * f);
        return mix(
          mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
          mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x),
          f.y
        );
      }

      float fbm(vec2 p) {
        float v = 0.0;
        float a = 0.5;
        mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
        for (int i = 0; i < 4; ++i) {
          v += a * noise(p);
          p = rot * p * 2.0 + vec2(10.0);
          a *= 0.5;
        }
        return v;
      }

      vec3 palette(float t) {
        vec3 a = vec3(0.12, 0.15, 0.22);
        vec3 b = vec3(0.25, 0.35, 0.45);
        vec3 c = vec3(1.0, 1.0, 1.0);
        vec3 d = vec3(0.0, 0.33, 0.67);
        return a + b * cos(6.28318 * (c * t + d));
      }

      void main() {
        vec2 st = (gl_FragCoord.xy * 2.0 - u_resolution) / min(u_resolution.x, u_resolution.y);
        vec2 mouse = (u_mouse.xy * 2.0 - u_resolution) / min(u_resolution.x, u_resolution.y);

        float dMouse = length(st - mouse);
        float mouseAttract = smoothstep(0.8, 0.0, dMouse) * 0.4;

        vec2 q = vec2(fbm(st + 0.08 * u_time), fbm(st + vec2(5.2, 1.3) + 0.06 * u_time));
        vec2 r = vec2(fbm(st + 3.0 * q + vec2(1.7, 9.2) + 0.12 * u_time + mouseAttract),
                      fbm(st + 3.0 * q + vec2(8.3, 2.8) + 0.10 * u_time));

        float f = fbm(st + 4.0 * r);
        float boost = f + u_energy * 0.6;
        vec3 color = palette(boost + 0.1 * u_time);
        color += vec3(0.1, 0.3, 0.5) * mouseAttract;

        gl_FragColor = vec4(color, 1.0);
      }
    `;

    function createShader(gl, type, source) {
      const shader = gl.createShader(type);
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      return shader;
    }

    const program = gl.createProgram();
    gl.attachShader(program, createShader(gl, gl.VERTEX_SHADER, vsSource));
    gl.attachShader(program, createShader(gl, gl.FRAGMENT_SHADER, fsSource));
    gl.linkProgram(program);
    gl.useProgram(program);

    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
      -1, -1,  1, -1, -1,  1,
      -1,  1,  1, -1,  1,  1
    ]), gl.STATIC_DRAW);

    const aPos = gl.getAttribLocation(program, 'a_pos');
    gl.enableVertexAttribArray(aPos);
    gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

    const uRes = gl.getUniformLocation(program, 'u_resolution');
    const uTime = gl.getUniformLocation(program, 'u_time');
    const uMouse = gl.getUniformLocation(program, 'u_mouse');
    const uEnergy = gl.getUniformLocation(program, 'u_energy');

    let energy = 0.0;
    let targetEnergy = 0.0;
    let mouse = [window.innerWidth / 2, window.innerHeight / 2, 0, 0];
    let idleTimer = 0;
    let isSleeping = false;

    function resize() {
      const dpr = Math.min(1.5, window.devicePixelRatio || 1);
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      gl.viewport(0, 0, canvas.width, canvas.height);
      document.getElementById('dpr-chip').innerText = 'DPR: ' + dpr.toFixed(2);
    }
    window.addEventListener('resize', resize);
    resize();

    window.addEventListener('mousemove', e => {
      mouse[0] = e.clientX * (canvas.width / window.innerWidth);
      mouse[1] = (window.innerHeight - e.clientY) * (canvas.height / window.innerHeight);
      wake();
    });

    const codeInput = document.getElementById('code-input');
    codeInput.addEventListener('keydown', () => {
      targetEnergy = Math.min(1.0, targetEnergy + 0.15);
      wake();
    });

    function wake() {
      idleTimer = 0;
      if (isSleeping) {
        isSleeping = false;
        document.getElementById('status-chip').innerText = 'STATUS: RUNNING (60 FPS)';
        document.getElementById('status-chip').className = 'chip chip-active';
        loop();
      }
    }

    let startTime = performance.now();
    function loop() {
      if (isSleeping) return;
      const now = performance.now();
      const elapsed = (now - startTime) * 0.001;

      energy += (targetEnergy - energy) * 0.1;
      targetEnergy *= 0.95;
      idleTimer += 1 / 60;

      document.getElementById('energy-chip').innerText = 'ENERGY: ' + energy.toFixed(2);

      gl.uniform2f(uRes, canvas.width, canvas.height);
      gl.uniform1f(uTime, elapsed);
      gl.uniform4f(uMouse, mouse[0], mouse[1], mouse[2], mouse[3]);
      gl.uniform1f(uEnergy, energy);

      gl.drawArrays(gl.TRIANGLES, 0, 6);

      if (idleTimer > 6.0 && energy < 0.01) {
        isSleeping = true;
        document.getElementById('status-chip').innerText = 'STATUS: SLEEPING (0% GPU)';
        document.getElementById('status-chip').className = 'chip';
        return;
      }

      requestAnimationFrame(loop);
    }

    loop();
  </script>
</body>
</html>
'''

with open(output_path, "w") as f:
    f.write(html)
print(f"Generated artifact at {output_path} ({len(html)} bytes)")
