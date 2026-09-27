# Build audio contract and evidence

## Sources
- MDN Web Audio best practices: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Best_practices — create/resume in user gesture, explicit user control, native oscillator synthesis; retrieved through Jina reader.
- https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/suspend — suspension lifecycle; initial extractor returned only partial text, do not treat snippets as exhaustive specification.
- https://developer.mozilla.org/en-US/docs/Web/API/AudioParam/linearRampToValueAtTime — scheduled parameter changes; test API availability in target browser.

## Mechanistic lens
Event -> visible status -> recent-ID gate -> opt-in/visibility/context gate -> cooldown -> oscillator -> envelope -> master gain -> device. y[n] = master * envelope[n] * sin(phase[n]). Controller owns at most one oscillator; gain envelope <=0.5 and master <=0.15 bound this source's digital amplitude to 0.075. This is not a sound-pressure guarantee. Proposed defaults are design choices, not scientifically optimal settings.

Schedule against AudioContext.currentTime, not timer callbacks for individual notes. Total perceived delay includes event transport, main thread, audio buffer and physical output. Amdahl: optimizing cue synthesis cannot remove build or transport time; no speedup percentage asserted without measurement. Memory is bounded by one active voice and 128 recent IDs; no continuous rendering loop or polling timer.

## Bayesian lens and pre-test predictions
Known from documentation: gesture policy, AudioParam scheduling, user mute controls. Predictions before browser tests: silent construction has no context; offline signal is nonzero with peak <=0.04001 at default master gain; tail after 300 ms is zero; unsupported context stays disabled. Live predictions: one burst cue accepted, repeated ID rejected, nodes empty after ending, hidden state blocks all cues, mute during pending unlock never restores enabled. Human concentration, pleasantness and physical output latency remain uncertain until user/device testing.

## System design trade-offs
- Native API avoids an extra audio framework for two cues; musical transport warrants Tone.js rather than expanding a hand-rolled scheduler.
- Drop bursts rather than queue them. Cooldown may suppress a later failure; visible build status must always update. Critical alerts require a separate reviewed policy.
- Mute on hidden/pagehide, require explicit unlock on return. This prioritizes low distraction over background alerts.
- No binaural ambience by default. Optional two-ear oscillators are technically feasible, but effectiveness for coding is unverified; do not market frequencies as cognitive enhancement.
- Close on component unmount; mute on visibility transition. Resume promises use generation guard against mute/unlock races.
- Offline rendering tests real DSP, not mock API arithmetic. Integration page accepts actual build result events and visibly labels manual previews.

## Verification limits
Headless rendering is not hearing. Browser checks cannot establish headphone comfort, mobile interruption handling or end-to-end speaker latency. Re-test Safari/Firefox/mobile and trusted gestures where deployed. Store run output in verification.json after actual execution; never embed invented pass counts.
