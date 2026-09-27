---
name: tactile-haptic-synthesis
description: Synthesize calibrated Web Vibration and haptic cues.
version: 1.0.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [haptics, vibration, tactile, vibe-coding, mobile-ux, web-audio, flow-state]
    related_skills: [tactile-microinteraction-studio, pwa-mobile-ergonomics, ambient-sonification-flow, live-sandbox-hot-preview]
---

# Tactile Haptic Synthesis Skill

Synthesize physical micro-interaction haptic feedback using calibrated Web Vibration API patterns, acoustic sub-bass fallbacks for desktop, cooldown throttling, and battery safeguards.

## When to Use
- Adding tactile sensory feedback to mobile web apps, PWAs, or touch interfaces.
- Crafting physical confirmation for actions: button taps, tab switches, bottom-sheet docks, build success, and errors.
- Implementing graceful acoustic fallbacks (65Hz-85Hz sub-bass micro-chirps) on desktop browsers lacking vibration actuators.
- Protecting mobile hardware from battery drain and actuator fatigue through duty-cycle throttling.

Don't use for:
- Loud or high-frequency game audio effects (use `ambient-sonification-flow`).
- Desktop-only enterprise data grids with no touch interactions.
- Arbitrary continuous vibration that disrupts user focus.

## Prerequisites
- Web platform supporting `navigator.vibrate` (Chrome, Firefox, Edge on Android/touch devices).
- Modern browser with Web Audio API (`AudioContext`) for desktop acoustic fallbacks.
- Python 3.10+ for running the local test harness (`tactile_haptic_engine.py`).

## Quick Reference
- Test haptic profiles & mechanical displacement:
  ```bash
  python3 ~/.hermes/skills/creative/tactile-haptic-synthesis/scripts/tactile_haptic_engine.py
  ```
- Standard Presets:
  - `subtle_tap`: `[15]` ms (cooldown: 40ms)
  - `selection_tick`: `[8]` ms (cooldown: 25ms)
  - `spring_snap`: `[12, 25, 20]` ms (cooldown: 80ms)
  - `success_double`: `[18, 45, 24]` ms (cooldown: 120ms)
  - `warning_pulse`: `[35, 60, 35]` ms (cooldown: 200ms)
  - `error_buzz`: `[60, 40, 60, 40, 90]` ms (cooldown: 300ms)

## Procedure

1. **Select Semantically Grounded Pattern**:
   Choose one of the 6 standardized presets matching interaction gravity. Never invent arbitrary patterns $> 500\text{ms}$.

2. **Integrate Controller with Throttle Barrier**:
   Import `TactileHapticController` and bind triggers to pointerdown, swipe, or completion hooks:
   ```javascript
   const haptic = new TactileHapticController({ audioFallback: true });
   button.addEventListener('pointerdown', () => haptic.trigger('subtle_tap'));
   ```

3. **Validate Fallback & Permission Constraints**:
   Verify that non-touch environments cleanly fall back to acoustic sub-bass synthesis without thrown exceptions or UI stalls.

4. **Audit Battery & Thermal Guard**:
   Ensure vibration is automatically suppressed when battery drops below 15% without charging.

## Pitfalls
- **iOS Safari Restriction**: Safari on iOS restricts or ignores `navigator.vibrate`. The controller automatically falls back to sub-bass acoustic chirps.
- **Vibration Flooding**: Rapid slider movement or gestures can queue excessive vibrations. The built-in cooldown throttling drops events arriving within the cooldown window.
- **AudioContext Autoplay Policy**: Desktop acoustic fallback requires at least one user gesture before `AudioContext` resumes. Call `haptic.trigger()` inside touch/click handlers.

## Verification
- Run `python3 ~/.hermes/skills/creative/tactile-haptic-synthesis/scripts/tactile_haptic_engine.py` and ensure all 6 profiles output `[PASS]`.
- Verify cooldown state machine and battery guard test assertions pass with zero errors.
