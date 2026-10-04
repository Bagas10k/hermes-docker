---
name: haptic-microinteraction-state-machines
description: "Design deterministic haptic and acoustic interaction FSMs."
version: 1.0.0
author: Bagas Cihuy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [haptic, web-audio, microinteraction, fsm, mobile-ergonomics, state-machine]
    related_skills: [pwa-mobile-ergonomics, tactile-microinteraction-studio]
---

# Haptic & Acoustic Micro-Interaction State Machines

Model and compile deterministic mobile thumb interaction states with coordinated Web Vibration API patterns and Web Audio API psychoacoustic synthesis.

## When to Use
- Designing mobile PWA thumb swipe, sheet pull, slider snap, or button detents.
- Replacing ad-hoc, jittery gesture feedback with mathematically bounded Finite State Machines (FSM).
- Synthesizing zero-asset Web Audio micro-clicks and low-latency haptic ticks.
- Enforcing anti-chattering hysteresis boundaries on gesture activation thresholds.

## Architectural Model & State Flow

The interaction lifecycle follows a deterministic 8-state transition graph:
1. `IDLE` -> `TOUCH_START`: Initial touch registered (8ms micro-pulse, 440->220Hz sine pop).
2. `TOUCH_START` -> `DRAGGING`: Displacement below 75% threshold (silent tracking).
3. `DRAGGING` -> `THRESHOLD_APPROACH`: Displacement >= 75% threshold (12ms warning tick, 520->580Hz triangle cue).
4. `THRESHOLD_APPROACH` -> `THRESHOLD_CROSSED`: Displacement >= 100% threshold (detent notch: [18ms, 20ms, 24ms], 660->880Hz confirmation).
5. `THRESHOLD_CROSSED` -> `ACTION_TRIGGERED`: Pointer released past threshold (action fired: [15ms, 30ms, 25ms], 880->1320Hz chime).
6. Any non-confirmed state -> `RELEASE_CANCELLED`: Touch abort / fallback return (10ms dull rubber-band tick, 300->150Hz drop).

## Hysteresis & Anti-Chattering Bounds
To prevent rapid vibration flapping when a user's thumb hovers near the activation threshold ($x_{\text{act}}$):
- Transition to `THRESHOLD_CROSSED`: requires $\frac{\Delta x}{x_{\text{act}}} \ge 1.0$.
- Fallback transition back to `THRESHOLD_APPROACH`: requires $\frac{\Delta x}{x_{\text{act}}} < 0.90$.
The $10\%$ deadband hysteresis guarantees $0$ state oscillation during thumb jitter.

## Quick Reference
Execute the FSM compiler and test runner:
```bash
python3 ~/.hermes/skills/creative/haptic-microinteraction-state-machines/scripts/fsm_engine.py
python3 ~/.hermes/skills/creative/haptic-microinteraction-state-machines/scripts/test_fsm_engine.py
```

## Verification
- Unit test suite passes with 100% assertions (`test_fsm_engine.py`).
- Exported JSON contracts contain complete Web Audio oscillator parameters and Vibration pulse timings.
