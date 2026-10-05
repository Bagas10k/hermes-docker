/* Bagas Cihuy & Hermes Agent — MIT */
export function createFlow(canvas, {count = 360, idleMs = 45000} = {}) {
  if (!Number.isInteger(count) || count < 1 || count > 1200) throw new RangeError('count: 1..1200');
  if (!Number.isFinite(idleMs) || idleMs < 100) throw new RangeError('idleMs >= 100');
  const ctx = canvas.getContext('2d', {alpha: false});
  if (!ctx) throw new Error('Canvas 2D unavailable');
  const positions = new Float32Array(count * 2);
  const costs = new Float32Array(240), intervals = new Float32Array(240);
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const abort = new AbortController();
  let width = 1, height = 1, raf = null, last = null, lastInput = performance.now();
  let disposed = false, enabled = true, intersecting = true, frames = 0, cursor = 0;
  let samples = 0, energy = 0, reason = 'ready';
  function seed() {
    for (let i = 0; i < count; i++) {
      positions[2*i] = ((i * 0.61803398875) % 1) * width;
      positions[2*i+1] = ((i * 0.41421356237) % 1) * height;
    }
  }
  function clear() {ctx.fillStyle = '#faf6ef'; ctx.fillRect(0, 0, width, height);}
  function halt(why) {
    if (raf !== null) cancelAnimationFrame(raf);
    raf = null; last = null; reason = why;
  }
  function allowed() {
    if (disposed) return 'disposed';
    if (!enabled) return 'paused';
    if (document.hidden) return 'hidden';
    if (!intersecting) return 'offscreen';
    if (motion.matches) return 'reduced-motion';
    if (performance.now() - lastInput >= idleMs) return 'idle';
    return null;
  }
  function reconcile() {
    const blocked = allowed();
    if (blocked) {halt(blocked); return;}
    if (raf === null) {reason = 'running'; raf = requestAnimationFrame(frame);}
  }
  function frame(time) {
    raf = null;
    const blocked = allowed();
    if (blocked) {halt(blocked); return;}
    const start = performance.now();
    const raw = last === null ? 0 : time - last;
    const dt = Math.min(raw / 1000, 0.032);
    last = time; energy *= Math.exp(-dt / 0.8);
    ctx.fillStyle = `rgba(250,246,239,${1-Math.exp(-dt/0.14)})`;
    ctx.fillRect(0, 0, width, height);
    const k = 0.008, phase = time * 0.00008, speed = 38 + 50 * energy;
    ctx.lineWidth = 1;
    // Curl of psi = sin(k*x + phase) * sin(k*y - phase) / k.
    // v = (dpsi/dy, -dpsi/dx); analytic, not Perlin noise.
    for (let group = 0; group < 3; group++) {
      ctx.beginPath(); ctx.strokeStyle = ['#0369a1', '#047857', '#7c3aed'][group];
      for (let i = group; i < count; i += 3) {
        const j = i * 2, x = positions[j], y = positions[j+1];
        const vx = Math.sin(k*x+phase)*Math.cos(k*y-phase);
        const vy = -Math.cos(k*x+phase)*Math.sin(k*y-phase);
        const nx = x + vx*speed*dt, ny = y + vy*speed*dt;
        ctx.moveTo(x,y); ctx.lineTo(nx,ny);
        positions[j] = (nx % width + width) % width;
        positions[j+1] = (ny % height + height) % height;
      }
      ctx.stroke();
    }
    frames++;
    if (raw > 0) {
      costs[cursor] = performance.now()-start; intervals[cursor] = raw;
      cursor = (cursor+1)%costs.length; samples = Math.min(samples+1, costs.length);
    }
    reconcile();
  }
  function resize() {
    if (disposed) return;
    const rect = canvas.getBoundingClientRect();
    width = Math.max(1, rect.width); height = Math.max(1, rect.height);
    // Bound pixel area independently of CSS size and DPR.
    const dpr = Math.min(devicePixelRatio || 1, 2, Math.sqrt(2000000/(width*height)));
    canvas.width = Math.max(1, Math.floor(width*dpr));
    canvas.height = Math.max(1, Math.floor(height*dpr));
    ctx.setTransform(canvas.width/width,0,0,canvas.height/height,0,0);
    seed(); clear(); reconcile();
  }
  function activity() {
    if (disposed || document.hidden || !enabled) return;
    lastInput = performance.now(); energy = Math.min(1, energy+0.15); reconcile();
  }
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(canvas);
  const intersectionObserver = new IntersectionObserver(entries => {
    if (disposed) return;
    intersecting = entries[0].isIntersecting; reconcile();
  });
  intersectionObserver.observe(canvas);
  document.addEventListener('visibilitychange', reconcile, {signal: abort.signal});
  motion.addEventListener('change', reconcile, {signal: abort.signal});
  resize();
  function percentile(array, p) {
    if (!samples) return null;
    const sorted = Array.from(array.subarray(0,samples)).sort((a,b)=>a-b);
    return sorted[Math.ceil(p*sorted.length)-1];
  }
  return {
    activity,
    pause() {enabled = false; reconcile();},
    resume() {if (!disposed) {enabled = true; lastInput = performance.now(); reconcile();}},
    stats() {return {frames, count, state: reason, pendingRAF: raf !== null,
      samples, p95RenderMs: percentile(costs,.95), p95FrameMs: percentile(intervals,.95),
      particleBytes: positions.byteLength, bitmapPixels: canvas.width*canvas.height,
      finite: positions.every(Number.isFinite)};},
    dispose() {if (disposed) return; disposed = true; halt('disposed');
      abort.abort(); resizeObserver.disconnect(); intersectionObserver.disconnect();}
  };
}
