#!/usr/bin/env python3
"""
Deterministic Haptic & Acoustic Micro-Interaction State Machine Engine.
Provides mathematical modeling, deterministic state transitions, 
Web Vibration API pattern compilation, and Web Audio synthesiser parameter synthesis.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import json

class InteractionState(Enum):
    IDLE = "IDLE"
    TOUCH_START = "TOUCH_START"
    DRAGGING = "DRAGGING"
    THRESHOLD_APPROACH = "THRESHOLD_APPROACH"
    THRESHOLD_CROSSED = "THRESHOLD_CROSSED"
    ACTION_TRIGGERED = "ACTION_TRIGGERED"
    RELEASE_CANCELLED = "RELEASE_CANCELLED"
    ERROR_LOCKOUT = "ERROR_LOCKOUT"

class GestureType(Enum):
    TAP = "TAP"
    LONG_PRESS = "LONG_PRESS"
    SWIPE_DISMISS = "SWIPE_DISMISS"
    SLIDER_STEP = "SLIDER_STEP"
    PULL_TO_REFRESH = "PULL_TO_REFRESH"

@dataclass
class AudioCueSpec:
    oscillator_type: str  # sine, triangle, square, sawtooth
    freq_start_hz: float
    freq_end_hz: float
    duration_ms: float
    gain_peak: float
    attack_ms: float
    decay_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "oscillator_type": self.oscillator_type,
            "freq_start_hz": round(self.freq_start_hz, 2),
            "freq_end_hz": round(self.freq_end_hz, 2),
            "duration_ms": round(self.duration_ms, 2),
            "gain_peak": round(self.gain_peak, 3),
            "attack_ms": round(self.attack_ms, 2),
            "decay_ms": round(self.decay_ms, 2)
        }

@dataclass
class HapticFeedbackSpec:
    vibration_pattern: List[int]  # [vibrate_ms, pause_ms, vibrate_ms, ...]
    intensity: float  # 0.0 to 1.0 (relative throttle/duty cycle)
    audio_cue: Optional[AudioCueSpec] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vibration_pattern": self.vibration_pattern,
            "intensity": round(self.intensity, 2),
            "audio_cue": self.audio_cue.to_dict() if self.audio_cue else None
        }

class HapticAcousticFSM:
    """
    Deterministic Finite State Machine for Mobile Thumb Gestures
    with Synced Haptic and Audio Cue Generation.
    """
    
    TRANSITIONS: Dict[Tuple[InteractionState, str], InteractionState] = {
        (InteractionState.IDLE, "POINTER_DOWN"): InteractionState.TOUCH_START,
        
        # From TOUCH_START
        (InteractionState.TOUCH_START, "MOVE_SUB_THRESHOLD"): InteractionState.DRAGGING,
        (InteractionState.TOUCH_START, "MOVE_NEAR_THRESHOLD"): InteractionState.THRESHOLD_APPROACH,
        (InteractionState.TOUCH_START, "MOVE_CROSS"): InteractionState.THRESHOLD_CROSSED,
        (InteractionState.TOUCH_START, "POINTER_UP"): InteractionState.ACTION_TRIGGERED,
        (InteractionState.TOUCH_START, "POINTER_CANCEL"): InteractionState.RELEASE_CANCELLED,
        
        # From DRAGGING
        (InteractionState.DRAGGING, "MOVE_SUB_THRESHOLD"): InteractionState.DRAGGING,
        (InteractionState.DRAGGING, "MOVE_NEAR_THRESHOLD"): InteractionState.THRESHOLD_APPROACH,
        (InteractionState.DRAGGING, "MOVE_CROSS"): InteractionState.THRESHOLD_CROSSED,
        (InteractionState.DRAGGING, "POINTER_UP"): InteractionState.RELEASE_CANCELLED,
        (InteractionState.DRAGGING, "POINTER_CANCEL"): InteractionState.RELEASE_CANCELLED,
        
        # From THRESHOLD_APPROACH
        (InteractionState.THRESHOLD_APPROACH, "MOVE_CROSS"): InteractionState.THRESHOLD_CROSSED,
        (InteractionState.THRESHOLD_APPROACH, "MOVE_FALLBACK"): InteractionState.DRAGGING,
        (InteractionState.THRESHOLD_APPROACH, "MOVE_NEAR_THRESHOLD"): InteractionState.THRESHOLD_APPROACH,
        (InteractionState.THRESHOLD_APPROACH, "POINTER_UP"): InteractionState.RELEASE_CANCELLED,
        (InteractionState.THRESHOLD_APPROACH, "POINTER_CANCEL"): InteractionState.RELEASE_CANCELLED,
        
        # From THRESHOLD_CROSSED
        (InteractionState.THRESHOLD_CROSSED, "MOVE_CROSS"): InteractionState.THRESHOLD_CROSSED,
        (InteractionState.THRESHOLD_CROSSED, "POINTER_UP"): InteractionState.ACTION_TRIGGERED,
        (InteractionState.THRESHOLD_CROSSED, "MOVE_FALLBACK"): InteractionState.THRESHOLD_APPROACH,
        (InteractionState.THRESHOLD_CROSSED, "POINTER_CANCEL"): InteractionState.RELEASE_CANCELLED,
        
        # Terminal states
        (InteractionState.ACTION_TRIGGERED, "RESET"): InteractionState.IDLE,
        (InteractionState.RELEASE_CANCELLED, "RESET"): InteractionState.IDLE,
        (InteractionState.ERROR_LOCKOUT, "RESET"): InteractionState.IDLE,
    }

    def __init__(self, gesture_type: GestureType = GestureType.SWIPE_DISMISS, threshold_px: float = 75.0):
        self.gesture_type = gesture_type
        self.threshold_px = threshold_px
        self.current_state = InteractionState.IDLE
        self.current_displacement_px = 0.0
        self.history: List[InteractionState] = [InteractionState.IDLE]

    def transition(self, event: str) -> Tuple[InteractionState, Optional[HapticFeedbackSpec]]:
        key = (self.current_state, event)
        if key not in self.TRANSITIONS:
            if event == "FORCE_ERROR":
                self.current_state = InteractionState.ERROR_LOCKOUT
                feedback = self._synthesize_feedback(InteractionState.ERROR_LOCKOUT)
                return self.current_state, feedback
            return self.current_state, None

        next_state = self.TRANSITIONS[key]
        state_changed = (next_state != self.current_state)
        self.current_state = next_state
        self.history.append(next_state)
        
        # Only synthesize distinct feedback on actual state transition
        feedback = self._synthesize_feedback(next_state) if state_changed else None
        return next_state, feedback

    def update_drag(self, delta_px: float) -> Tuple[InteractionState, Optional[HapticFeedbackSpec]]:
        self.current_displacement_px = delta_px
        ratio = abs(delta_px) / self.threshold_px

        if self.current_state in (InteractionState.TOUCH_START, InteractionState.DRAGGING):
            if ratio >= 1.0:
                return self.transition("MOVE_CROSS")
            elif ratio >= 0.75:
                return self.transition("MOVE_NEAR_THRESHOLD")
            else:
                return self.transition("MOVE_SUB_THRESHOLD")
        elif self.current_state == InteractionState.THRESHOLD_APPROACH:
            if ratio >= 1.0:
                return self.transition("MOVE_CROSS")
            elif ratio < 0.70:
                return self.transition("MOVE_FALLBACK")
            else:
                return self.transition("MOVE_NEAR_THRESHOLD")
        elif self.current_state == InteractionState.THRESHOLD_CROSSED:
            if ratio < 0.90:  # Hysteresis deadband (10%)
                return self.transition("MOVE_FALLBACK")
            return self.transition("MOVE_CROSS")

        return self.current_state, None

    def _synthesize_feedback(self, state: InteractionState) -> Optional[HapticFeedbackSpec]:
        if state == InteractionState.TOUCH_START:
            audio = AudioCueSpec(
                oscillator_type="sine",
                freq_start_hz=440.0,
                freq_end_hz=220.0,
                duration_ms=12.0,
                gain_peak=0.15,
                attack_ms=1.5,
                decay_ms=10.5
            )
            return HapticFeedbackSpec(vibration_pattern=[8], intensity=0.25, audio_cue=audio)

        elif state == InteractionState.THRESHOLD_APPROACH:
            audio = AudioCueSpec(
                oscillator_type="triangle",
                freq_start_hz=520.0,
                freq_end_hz=580.0,
                duration_ms=18.0,
                gain_peak=0.20,
                attack_ms=2.0,
                decay_ms=16.0
            )
            return HapticFeedbackSpec(vibration_pattern=[12], intensity=0.45, audio_cue=audio)

        elif state == InteractionState.THRESHOLD_CROSSED:
            audio = AudioCueSpec(
                oscillator_type="sine",
                freq_start_hz=660.0,
                freq_end_hz=880.0,
                duration_ms=35.0,
                gain_peak=0.35,
                attack_ms=2.0,
                decay_ms=33.0
            )
            return HapticFeedbackSpec(vibration_pattern=[18, 20, 24], intensity=0.85, audio_cue=audio)

        elif state == InteractionState.ACTION_TRIGGERED:
            audio = AudioCueSpec(
                oscillator_type="sine",
                freq_start_hz=880.0,
                freq_end_hz=1320.0,
                duration_ms=50.0,
                gain_peak=0.40,
                attack_ms=3.0,
                decay_ms=47.0
            )
            return HapticFeedbackSpec(vibration_pattern=[15, 30, 25], intensity=0.90, audio_cue=audio)

        elif state == InteractionState.RELEASE_CANCELLED:
            audio = AudioCueSpec(
                oscillator_type="sine",
                freq_start_hz=300.0,
                freq_end_hz=150.0,
                duration_ms=40.0,
                gain_peak=0.18,
                attack_ms=3.0,
                decay_ms=37.0
            )
            return HapticFeedbackSpec(vibration_pattern=[10], intensity=0.20, audio_cue=audio)

        elif state == InteractionState.ERROR_LOCKOUT:
            audio = AudioCueSpec(
                oscillator_type="sawtooth",
                freq_start_hz=180.0,
                freq_end_hz=130.0,
                duration_ms=75.0,
                gain_peak=0.50,
                attack_ms=5.0,
                decay_ms=70.0
            )
            return HapticFeedbackSpec(vibration_pattern=[35, 30, 35], intensity=1.0, audio_cue=audio)

        return None

    def export_web_contract(self) -> Dict[str, Any]:
        states_catalog = {}
        for state in InteractionState:
            feedback = self._synthesize_feedback(state)
            states_catalog[state.value] = feedback.to_dict() if feedback else None

        return {
            "gesture_type": self.gesture_type.value,
            "threshold_px": self.threshold_px,
            "hysteresis_margin_px": self.threshold_px * 0.10,
            "states": states_catalog
        }
