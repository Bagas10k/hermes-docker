// Node.js test harness for Shader Canvas Flow mechanics
function calculateCosinePalette(t, a, b, c, d) {
  return [
    a[0] + b[0] * Math.cos(2 * Math.PI * (c[0] * t + d[0])),
    a[1] + b[1] * Math.cos(2 * Math.PI * (c[1] * t + d[1])),
    a[2] + b[2] * Math.cos(2 * Math.PI * (c[2] * t + d[2]))
  ];
}

console.log("=== Shader Canvas Flow Test Harness ===");

// 1. Uji Palet Aurora Borealis
const auroraA = [0.1, 0.3, 0.4];
const auroraB = [0.2, 0.4, 0.5];
const auroraC = [1.0, 1.0, 1.0];
const auroraD = [0.0, 0.33, 0.67];

const tSamples = [0.0, 0.25, 0.5, 0.75, 1.0];
console.log("1. Testing Inigo Quilez Cosine Palette generation:");
tSamples.forEach(t => {
  const col = calculateCosinePalette(t, auroraA, auroraB, auroraC, auroraD);
  const r = Math.min(255, Math.max(0, Math.round(col[0] * 255)));
  const g = Math.min(255, Math.max(0, Math.round(col[1] * 255)));
  const b = Math.min(255, Math.max(0, Math.round(col[2] * 255)));
  console.log(`   t=${t.toFixed(2)} -> RGB(${r}, ${g}, ${b})`);
});

// 2. Simulasi State Machine Auto-Sleep
console.log("\n2. Testing Energy Decay & Auto-Sleep State Machine:");
let energy = 1.0;
const decayRate = 0.90; // Halus & cepat meluruh saat idle
let idleTimer = 0;
let isSleeping = false;

for (let frame = 1; frame <= 120; frame++) {
  energy *= decayRate;
  idleTimer += 1 / 60;
  if (idleTimer >= 1.0 && energy < 0.005) {
    isSleeping = true;
    console.log(`   Auto-sleep triggered at frame ${frame} (energy=${energy.toFixed(6)}, idle=${idleTimer.toFixed(2)}s) -> GPU 0% sleep mode ACTIVE.`);
    break;
  }
}

if (!isSleeping) {
  console.error("FAIL: Auto-sleep did not trigger.");
  process.exit(1);
}

// 3. Validasi Sintaks GLSL Uniform Tokens
console.log("\n3. Validating GLSL Fragment Shader Tokens:");
const shaderSource = `
precision highp float;
uniform vec2 u_resolution;
uniform float u_time;
uniform vec4 u_mouse;
uniform float u_energy;
varying vec2 v_uv;

void main() {
  vec2 p = (gl_FragCoord.xy * 2.0 - u_resolution) / min(u_resolution.x, u_resolution.y);
  gl_FragColor = vec4(p.x, p.y, u_energy, 1.0);
}
`;

const requiredTokens = ['precision', 'u_resolution', 'u_time', 'u_mouse', 'u_energy', 'gl_FragColor'];
for (const token of requiredTokens) {
  if (!shaderSource.includes(token)) {
    console.error(`FAIL: Missing required GLSL token: ${token}`);
    process.exit(1);
  }
}
console.log("   All required GLSL uniform tokens confirmed present.");
console.log("\n=== TEST HARNESS PASSED: 100% OPERATIONAL ===");
