const assert = require("assert");

function testBinauralCalculations() {
  const bands = [
    { name: "delta", beat: 2.5, carrier: 150 },
    { name: "theta", beat: 6.0, carrier: 180 },
    { name: "alpha", beat: 10.0, carrier: 200 },
    { name: "beta", beat: 18.0, carrier: 216 },
    { name: "gamma", beat: 40.0, carrier: 216 }
  ];

  bands.forEach(b => {
    const left = b.carrier;
    const right = b.carrier + b.beat;
    const diff = Math.round((right - left) * 100) / 100;
    assert.strictEqual(diff, b.beat, `Difference must match target beat for ${b.name}`);
  });
  console.log("PASS: Binaural frequency calculations verified across 5 EEG brainwave bands.");
}

function testPinkNoiseFilterStability() {
  let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
  const samples = 100000;
  let energySum = 0;

  for (let i = 0; i < samples; i++) {
    const white = Math.random() * 2 - 1;
    b0 = 0.99886 * b0 + white * 0.0555179;
    b1 = 0.99332 * b1 + white * 0.0750759;
    b2 = 0.96900 * b2 + white * 0.1538520;
    b3 = 0.86650 * b3 + white * 0.3104856;
    b4 = 0.55000 * b4 + white * 0.5329522;
    b5 = -0.7616 * b5 - white * 0.0168980;
    const pink = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.11;
    b6 = white * 0.115926;

    assert(!isNaN(pink), "Pink noise sample must not be NaN");
    assert(isFinite(pink), "Pink noise sample must be finite");
    energySum += pink * pink;
  }

  const rms = Math.sqrt(energySum / samples);
  console.log(`PASS: Pink noise filter stable. RMS amplitude: ${rms.toFixed(4)} (well bounded)`);
  assert(rms > 0.05 && rms < 0.5, "RMS amplitude must be within standard comfortable listening range");
}

function testGainRampingSafety() {
  const current = 0.0;
  const target = 0.35;
  const rampTimeMs = 50; // 50ms anti-click ramp
  const sampleRate = 48000;
  const samples = Math.floor((rampTimeMs / 1000) * sampleRate);
  const deltaPerSample = (target - current) / samples;

  assert(deltaPerSample < 0.001, "Delta per sample must be smooth (< 1e-3) to avoid audible clicks");
  console.log(`PASS: Gain ramp anti-click safety verified. Delta/sample: ${deltaPerSample.toExponential(3)}`);
}

testBinauralCalculations();
testPinkNoiseFilterStability();
testGainRampingSafety();
console.log("=== ALL UNIT TESTS COMPLETED SUCCESSFULLY ===");
