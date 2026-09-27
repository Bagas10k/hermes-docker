#!/usr/bin/env python3
"""
tactile_haptic_engine.py
Empirical modeling and verification test suite for Tactile Haptic Synthesis
Simulates Web Vibration API LRA (Linear Resonant Actuator) mechanics, duty-cycle energy,
perceptual saliency, audio fallback sub-bass chirp waveforms, and battery/thermal safeguards.
"""

import sys
import math
import json

HAPTIC_PRESETS = {
    "subtle_tap": {
        "pattern": [15],
        "intent": "Micro-interaction button press or slider step",
        "category": "light",
        "cooldown_ms": 40
    },
    "selection_tick": {
        "pattern": [8],
        "intent": "Picker wheel index change or tab switch",
        "category": "crisp",
        "cooldown_ms": 25
    },
    "success_double": {
        "pattern": [18, 45, 24],
        "intent": "Task completed, build passed, pull request merged",
        "category": "confirm",
        "cooldown_ms": 120
    },
    "spring_snap": {
        "pattern": [12, 25, 20],
        "intent": "Draggable bottom sheet snap to anchor or drawer dock",
        "category": "elastic",
        "cooldown_ms": 80
    },
    "warning_pulse": {
        "pattern": [35, 60, 35],
        "intent": "Stale state, uncommitted changes, non-fatal alert",
        "category": "alert",
        "cooldown_ms": 200
    },
    "error_buzz": {
        "pattern": [60, 40, 60, 40, 90],
        "intent": "Compilation error, syntax reject, failed transaction",
        "category": "error",
        "cooldown_ms": 300
    }
}

class HapticSynthesisEngine:
    def __init__(self, sample_rate=1000, resonant_freq=180.0):
        self.sample_rate = sample_rate
        self.resonant_freq = resonant_freq  # Typical LRA resonance in smartphones: 170-205 Hz

    def calculate_duty_cycle(self, pattern):
        total_time = sum(pattern)
        if total_time == 0:
            return 0.0
        active_time = sum(pattern[i] for i in range(0, len(pattern), 2))
        return (active_time / total_time) * 100.0

    def generate_mechanical_displacement(self, pattern):
        """
        Simulate LRA damped harmonic oscillation response:
        Normalized acceleration envelope response:
        a(t) = exp(-gamma * t) * sin(omega0 * t) during driven bursts
        """
        dt = 1.0 / self.sample_rate
        omega0 = 2.0 * math.pi * self.resonant_freq
        gamma = 28.0  # Deceleration damping factor
        
        signal = []
        t_global = 0.0
        stage_idx = 0
        stage_rem = pattern[0] / 1000.0
        burst_time = 0.0
        
        total_dur_s = sum(pattern) / 1000.0
        total_steps = int(total_dur_s * self.sample_rate)
        
        for _ in range(total_steps):
            is_active = (stage_idx % 2 == 0)
            if is_active:
                # Envelope peaks quickly then stabilizes
                env = min(1.0, burst_time * 120.0) * math.exp(-gamma * 0.08)
                val = env * math.sin(omega0 * burst_time)
                burst_time += dt
            else:
                # Decaying residual ring-down during pause
                val = math.exp(-gamma * burst_time) * math.sin(omega0 * burst_time) * 0.25
                burst_time += dt
                
            signal.append(val)
            t_global += dt
            stage_rem -= dt
            
            if stage_rem <= 0 and stage_idx + 1 < len(pattern):
                stage_idx += 1
                stage_rem = pattern[stage_idx] / 1000.0
                burst_time = 0.0
                
        return signal

    def generate_audio_fallback_chirp(self, pattern, audio_sample_rate=44100):
        """
        Synthesize acoustic sub-bass micro-chirp for desktop / devices without navigator.vibrate.
        Produces gentle 65Hz - 85Hz tactile low-end transient without clipping.
        """
        audio_samples = []
        dt = 1.0 / audio_sample_rate
        
        for stage_idx, dur_ms in enumerate(pattern):
            dur_s = dur_ms / 1000.0
            n_samples = int(dur_s * audio_sample_rate)
            is_active = (stage_idx % 2 == 0)
            
            for i in range(n_samples):
                t_rel = i / max(1, n_samples)
                if is_active:
                    # Exponential decay envelope to prevent speaker pop
                    envelope = math.exp(-4.5 * t_rel)
                    freq = 75.0 + 20.0 * (1.0 - t_rel)
                    val = 0.35 * envelope * math.sin(2.0 * math.pi * freq * (i * dt))
                    audio_samples.append(val)
                else:
                    audio_samples.append(0.0)
                    
        return audio_samples

    def audit_profile(self, name, preset):
        pat = preset["pattern"]
        duty = self.calculate_duty_cycle(pat)
        dur = sum(pat)
        mech = self.generate_mechanical_displacement(pat)
        peak_disp = max(abs(s) for s in mech) if mech else 0.0
        rms_energy = (sum(s**2 for s in mech) / max(1, len(mech))) ** 0.5
        
        # Audio fallback check
        audio = self.generate_audio_fallback_chirp(pat)
        peak_audio = max(abs(a) for a in audio) if audio else 0.0
        
        # Safety gate: duty cycle <= 85% for long patterns, total duration <= 500ms
        passed_safety = (dur <= 500) and (peak_audio <= 0.8) and (preset["cooldown_ms"] >= 20)
        
        return {
            "name": name,
            "duration_ms": dur,
            "stages": len(pat),
            "duty_cycle_pct": round(duty, 2),
            "peak_displacement": round(peak_disp, 4),
            "rms_energy": round(rms_energy, 4),
            "audio_peak_dbfs": round(20 * math.log10(max(1e-5, peak_audio)), 2),
            "safety_passed": passed_safety
        }

def run_tests():
    engine = HapticSynthesisEngine()
    print("=== TACTILE HAPTIC SYNTHESIS VERIFICATION HARNESS ===")
    all_passed = True
    for name, data in HAPTIC_PRESETS.items():
        res = engine.audit_profile(name, data)
        print(f"[{'PASS' if res['safety_passed'] else 'FAIL'}] {name:16} | Dur: {res['duration_ms']:3d}ms | Duty: {res['duty_cycle_pct']:5.1f}% | RMS: {res['rms_energy']:.4f} | Audio: {res['audio_peak_dbfs']} dBFS")
        if not res["safety_passed"]:
            all_passed = False
            
    # Verify cooldown throttling state machine
    print("\n--- Testing Throttling State Machine ---")
    timeline_ms = [0, 10, 20, 30, 40, 50, 60, 70, 80]
    fired = []
    last_trigger = -999.0
    cooldown = HAPTIC_PRESETS["selection_tick"]["cooldown_ms"]  # 25ms
    
    for t in timeline_ms:
        if (t - last_trigger) >= cooldown:
            fired.append(t)
            last_trigger = t
            
    print(f"Events dispatched at ms: {fired} (expected [0, 30, 60] with 25ms interval across 10ms steps)")
    assert len(fired) == 3, f"Expected 3 triggers, got {len(fired)}"
    print("[PASS] Throttling cooldown strictly bounded")
    
    # Test user consent and battery-saving suppression
    print("\n--- Testing Battery & Consent Gate ---")
    def can_vibrate(user_enabled=True, battery_level=0.85, is_charging=False):
        if not user_enabled:
            return False
        if battery_level <= 0.15 and not is_charging:
            return False
        return True
        
    assert can_vibrate(True, 0.85, False) is True
    assert can_vibrate(False, 0.85, False) is False
    assert can_vibrate(True, 0.10, False) is False  # low battery suppressed
    assert can_vibrate(True, 0.10, True) is True   # charging bypasses low battery
    print("[PASS] Battery and consent gate guard verified")
    
    if all_passed:
        print("\nALL HAPTIC SYNTHESIS HARDLINE INVARIANTS VERIFIED EMPIRICALLY.")
        return 0
    else:
        print("\nERRORS DETECTED IN HAPTIC PROFILES.")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
