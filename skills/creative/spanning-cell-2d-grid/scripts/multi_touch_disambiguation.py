"""Multi-Touch Dual-Finger Pan and Rotation Disambiguation Engine (UIUX-028).

Solves the conflict between two-finger translation panning and rotational gesture intent
on virtual 2D grid/table viewports through angular threshold deadbands, dual-vector
decomposition, and state machine gesture arbitration.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, List, Optional, Dict, Any
import math


class DualTouchGestureMode(Enum):
    """Active gesture arbitration classification."""
    UNDETERMINED = "UNDETERMINED"
    PAN = "PAN"
    PINCH_ZOOM = "PINCH_ZOOM"
    ROTATE = "ROTATE"
    FREE_TRANSFORM = "FREE_TRANSFORM"


@dataclass
class DualTouchPoint:
    """Represents a discrete contact point in viewport pixel space."""
    id: int
    x: float
    y: float


@dataclass
class DualTouchVectorState:
    """Geometric decomposition of a two-point touch formation."""
    center_x: float
    center_y: float
    span_distance: float
    angle_rad: float
    delta_pan_x: float = 0.0
    delta_pan_y: float = 0.0
    delta_scale: float = 1.0
    delta_rotation_rad: float = 0.0


@dataclass
class DisambiguationConfig:
    """Thresholds and deadband configuration for gesture discrimination."""
    pan_deadband_px: float = 8.0               # Minimum center movement to trigger Pan
    pinch_scale_threshold: float = 0.08        # |scale - 1.0| threshold for Pinch Zoom
    rotation_deadband_deg: float = 5.0         # Minimum angular change to trigger Rotation
    angular_lock_ratio: float = 2.5            # Ratio of angular motion vs radial/pan to enforce rotation lock
    allow_rotation: bool = False               # False = Grid view strictly locks rotation to 0 (Spreadsheet mode)
    rotation_snap_threshold_deg: float = 4.0   # Snap angle back to 0 if within snap band
    hysteresis_confidence_decay: float = 0.92   # Decay rate for gesture classification confidence


class MultiTouchDisambiguationEngine:
    """Arbitrates and disambiguates multi-touch interactions between Pan, Zoom, and Rotation."""

    def __init__(self, config: Optional[DisambiguationConfig] = None):
        self.config = config or DisambiguationConfig()
        self.active_mode = DualTouchGestureMode.UNDETERMINED
        
        # Initial touch tracking
        self.initial_vector: Optional[DualTouchVectorState] = None
        self.previous_vector: Optional[DualTouchVectorState] = None
        
        # Accumulated metrics from start of gesture
        self.accumulated_pan_distance: float = 0.0
        self.accumulated_scale_delta: float = 0.0
        self.accumulated_rotation_deg: float = 0.0
        
        # Current transformed outputs
        self.viewport_offset_x: float = 0.0
        self.viewport_offset_y: float = 0.0
        self.viewport_zoom: float = 1.0
        self.viewport_rotation_deg: float = 0.0
        self.gesture_confidence: float = 0.0

    def start_gesture(self, t1: DualTouchPoint, t2: DualTouchPoint) -> DualTouchVectorState:
        """Initializes a new two-finger interaction session."""
        dx = t2.x - t1.x
        dy = t2.y - t1.y
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        center_x = (t1.x + t2.x) / 2.0
        center_y = (t1.y + t2.y) / 2.0

        state = DualTouchVectorState(
            center_x=center_x,
            center_y=center_y,
            span_distance=max(dist, 1.0),
            angle_rad=angle,
            delta_pan_x=0.0,
            delta_pan_y=0.0,
            delta_scale=1.0,
            delta_rotation_rad=0.0
        )
        self.initial_vector = state
        self.previous_vector = state
        self.active_mode = DualTouchGestureMode.UNDETERMINED
        self.accumulated_pan_distance = 0.0
        self.accumulated_scale_delta = 0.0
        self.accumulated_rotation_deg = 0.0
        self.gesture_confidence = 0.0
        return state

    def normalize_angle_diff_rad(self, current_rad: float, previous_rad: float) -> float:
        """Calculates smallest angular difference wrapped in [-pi, pi]."""
        diff = current_rad - previous_rad
        while diff > math.pi:
            diff -= 2.0 * math.pi
        while diff < -math.pi:
            diff += 2.0 * math.pi
        return diff

    def update_touches(self, t1: DualTouchPoint, t2: DualTouchPoint) -> Tuple[DualTouchGestureMode, DualTouchVectorState]:
        """Processes continuous touch movement, updates disambiguation state machine, and applies transforms."""
        if not self.initial_vector or not self.previous_vector:
            init = self.start_gesture(t1, t2)
            return self.active_mode, init

        # Calculate current geometric properties
        dx = t2.x - t1.x
        dy = t2.y - t1.y
        current_dist = max(math.hypot(dx, dy), 1.0)
        current_angle = math.atan2(dy, dx)
        current_center_x = (t1.x + t2.x) / 2.0
        current_center_y = (t1.y + t2.y) / 2.0

        # Incremental deltas relative to previous frame
        step_pan_x = current_center_x - self.previous_vector.center_x
        step_pan_y = current_center_y - self.previous_vector.center_y
        step_rotation_rad = self.normalize_angle_diff_rad(current_angle, self.previous_vector.angle_rad)
        step_rotation_deg = math.degrees(step_rotation_rad)
        step_scale = current_dist / self.previous_vector.span_distance

        # Cumulative deltas relative to gesture start
        total_pan_x = current_center_x - self.initial_vector.center_x
        total_pan_y = current_center_y - self.initial_vector.center_y
        total_pan_dist = math.hypot(total_pan_x, total_pan_y)
        total_scale = current_dist / self.initial_vector.span_distance
        total_scale_diff = abs(total_scale - 1.0)
        total_rot_rad = self.normalize_angle_diff_rad(current_angle, self.initial_vector.angle_rad)
        total_rot_deg = abs(math.degrees(total_rot_rad))

        self.accumulated_pan_distance = total_pan_dist
        self.accumulated_scale_delta = total_scale_diff
        self.accumulated_rotation_deg = total_rot_deg

        # Gesture Arbitration State Machine
        if self.active_mode == DualTouchGestureMode.UNDETERMINED:
            # Check thresholds to lock into dominant mode
            is_pan_candidate = total_pan_dist >= self.config.pan_deadband_px
            is_pinch_candidate = total_scale_diff >= self.config.pinch_scale_threshold
            is_rot_candidate = (
                self.config.allow_rotation and 
                total_rot_deg >= self.config.rotation_deadband_deg
            )

            if is_rot_candidate and (total_rot_deg / max(1e-4, total_scale_diff * 100.0) >= self.config.angular_lock_ratio):
                self.active_mode = DualTouchGestureMode.ROTATE
                self.gesture_confidence = 1.0
            elif is_pinch_candidate and not is_pan_candidate:
                self.active_mode = DualTouchGestureMode.PINCH_ZOOM
                self.gesture_confidence = 1.0
            elif is_pan_candidate and not is_pinch_candidate:
                self.active_mode = DualTouchGestureMode.PAN
                self.gesture_confidence = 1.0
            elif is_pan_candidate and is_pinch_candidate:
                # Concurrent pan and zoom without rotation
                self.active_mode = DualTouchGestureMode.FREE_TRANSFORM if self.config.allow_rotation else DualTouchGestureMode.PAN
                self.gesture_confidence = 0.85

        # Apply transformations according to arbitrated mode
        vector_state = DualTouchVectorState(
            center_x=current_center_x,
            center_y=current_center_y,
            span_distance=current_dist,
            angle_rad=current_angle,
            delta_pan_x=step_pan_x,
            delta_pan_y=step_pan_y,
            delta_scale=step_scale,
            delta_rotation_rad=step_rotation_rad
        )

        if self.active_mode == DualTouchGestureMode.PAN:
            # Panning absorbs center translation, zeroes out rotation and suppresses zoom
            self.viewport_offset_x += step_pan_x
            self.viewport_offset_y += step_pan_y
            vector_state.delta_scale = 1.0
            vector_state.delta_rotation_rad = 0.0

        elif self.active_mode == DualTouchGestureMode.PINCH_ZOOM:
            # Pinch zoom scales around focal center, zero rotation
            self.viewport_zoom *= step_scale
            vector_state.delta_rotation_rad = 0.0

        elif self.active_mode == DualTouchGestureMode.ROTATE:
            # Rotation mode if allowed
            if self.config.allow_rotation:
                self.viewport_rotation_deg += step_rotation_deg
                # Apply angle snapping if near zero or cardinal axes
                if abs(self.viewport_rotation_deg) < self.config.rotation_snap_threshold_deg:
                    self.viewport_rotation_deg = 0.0
            else:
                self.viewport_rotation_deg = 0.0
                vector_state.delta_rotation_rad = 0.0

        elif self.active_mode == DualTouchGestureMode.FREE_TRANSFORM:
            # Free simultaneous Pan + Zoom (and optional Rotation)
            self.viewport_offset_x += step_pan_x
            self.viewport_offset_y += step_pan_y
            self.viewport_zoom *= step_scale
            if self.config.allow_rotation:
                self.viewport_rotation_deg += step_rotation_deg
            else:
                vector_state.delta_rotation_rad = 0.0

        self.previous_vector = vector_state
        return self.active_mode, vector_state

    def end_gesture(self) -> Dict[str, Any]:
        """Finalizes gesture interaction, applies snap constraints, and resets state."""
        summary = {
            "final_mode": self.active_mode.value,
            "accumulated_pan_px": self.accumulated_pan_distance,
            "accumulated_scale_delta": self.accumulated_scale_delta,
            "accumulated_rotation_deg": self.accumulated_rotation_deg,
            "viewport_offset": (self.viewport_offset_x, self.viewport_offset_y),
            "viewport_zoom": self.viewport_zoom,
            "viewport_rotation_deg": self.viewport_rotation_deg
        }
        self.active_mode = DualTouchGestureMode.UNDETERMINED
        self.initial_vector = None
        self.previous_vector = None
        self.gesture_confidence = 0.0
        return summary
