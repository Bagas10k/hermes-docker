"""Virtual Pointer Wheel Gesture Arbitration & Inertial Momentum Scroll Decay Engine.

Addresses UIUX-024:
Virtual pointer wheel gesture arbitration and inertial kinetic momentum scroll decay
synchronization between WebGL canvas and DOM header controls.

Key Capabilities:
1. Gesture Arbitration:
   - Evaluates incoming wheel / touch events across active target layers (WebGL Canvas vs DOM Header / Frozen Controls).
   - Arbitrates wheel event propagation, preventing double-scroll and event leakage.
   - Detects gesture phase: BEGAN, UPDATED, MOMENTUM_BEGAN, MOMENTUM_UPDATED, ENDED, CANCELLED.
2. Inertial Kinetic Momentum Physics:
   - Exponential / Power decay: v(t + dt) = v(t) * exp(-gamma * dt) or v(t) * (1 - friction * dt).
   - Dynamic bounce-back / rubber-banding spring physics when scroll position breaches boundary limits (overscroll dampening).
   - Sub-millisecond Symplectic Euler state integration.
3. Bidirectional Viewport Synchronization:
   - Dispatches synchronized scroll offsets (scroll_x, scroll_y) simultaneously to WebGL Uniform buffer and DOM sticky headers.
   - Zero-CLS alignment guarantee: WebGL viewport pan and DOM header offset match to 0.001px.
4. Kinetic Velocity Estimator:
   - Computes moving average / regression velocity from raw wheel delta history with high-frequency noise rejection.
"""

from dataclasses import dataclass, field
import enum
import math
import time
from typing import Dict, List, Optional, Tuple


class GesturePhase(enum.Enum):
    NONE = "none"
    BEGAN = "began"
    UPDATED = "updated"
    MOMENTUM_BEGAN = "momentum_began"
    MOMENTUM_UPDATED = "momentum_updated"
    ENDED = "ended"
    CANCELLED = "cancelled"


class TargetLayer(enum.Enum):
    WEBGL_CANVAS = "webgl_canvas"
    DOM_HEADER = "dom_header"
    FROZEN_CORNER = "frozen_corner"
    EXTERNAL = "external"


class ScrollAxis(enum.Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class PointerWheelEvent:
    timestamp_ms: float
    delta_x: float
    delta_y: float
    client_x: float
    client_y: float
    target_layer: TargetLayer
    is_touch: bool = False
    ctrl_key: bool = False
    shift_key: bool = False
    default_prevented: bool = False

    def prevent_default(self) -> None:
        self.default_prevented = True


@dataclass
class ViewportBoundary:
    min_x: float = 0.0
    max_x: float = 10000.0
    min_y: float = 0.0
    max_y: float = 50000.0
    enable_rubberband: bool = True
    rubberband_stiffness: float = 240.0
    rubberband_damping: float = 28.0
    max_overscroll: float = 120.0


@dataclass
class ScrollState:
    x: float = 0.0
    y: float = 0.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    overscroll_x: float = 0.0
    overscroll_y: float = 0.0
    phase: GesturePhase = GesturePhase.NONE
    is_animating: bool = False
    last_update_ms: float = 0.0


@dataclass
class SyncManifest:
    scroll_x: float
    scroll_y: float
    overscroll_x: float
    overscroll_y: float
    dom_header_x: float
    dom_header_y: float
    webgl_uniform_x: float
    webgl_uniform_y: float
    phase: str
    is_in_overscroll: bool
    drift_delta: float = 0.0


class VelocityEstimator:
    """Estimates kinetic velocity from sliding window sample deltas."""

    def __init__(self, window_size: int = 5, max_history_ms: float = 120.0):
        self.window_size = window_size
        self.max_history_ms = max_history_ms
        self.samples: List[Tuple[float, float, float]] = []  # (t_ms, dx, dy)

    def record_delta(self, t_ms: float, dx: float, dy: float) -> None:
        self.samples.append((t_ms, dx, dy))
        # Prune old samples
        cutoff = t_ms - self.max_history_ms
        self.samples = [(t, x, y) for (t, x, y) in self.samples if t >= cutoff]
        if len(self.samples) > self.window_size * 2:
            self.samples = self.samples[-self.window_size * 2:]

    def get_velocity(self, current_t_ms: float) -> Tuple[float, float]:
        """Calculates instantaneous kinetic velocity (pixels per second)."""
        if len(self.samples) < 2:
            return 0.0, 0.0

        cutoff = current_t_ms - self.max_history_ms
        valid = [(t, x, y) for (t, x, y) in self.samples if t >= cutoff]
        if len(valid) < 2:
            return 0.0, 0.0

        # Weighted recent delta velocity
        total_weight = 0.0
        weighted_vx = 0.0
        weighted_vy = 0.0

        for i in range(1, len(valid)):
            t0, _, _ = valid[i - 1]
            t1, dx, dy = valid[i]
            dt = (t1 - t0) / 1000.0
            if dt <= 0.0001:
                continue

            inst_vx = dx / dt
            inst_vy = dy / dt

            # Recency weight
            age = (current_t_ms - t1) / 1000.0
            weight = math.exp(-15.0 * max(0.0, age))

            weighted_vx += inst_vx * weight
            weighted_vy += inst_vy * weight
            total_weight += weight

        if total_weight <= 0.0:
            return 0.0, 0.0

        return weighted_vx / total_weight, weighted_vy / total_weight

    def clear(self) -> None:
        self.samples.clear()


class GestureArbitrator:
    """Arbitrates pointer wheel and touch gesture targeting across canvas and DOM layers."""

    def __init__(self, lock_axis_threshold: float = 6.0):
        self.lock_axis_threshold = lock_axis_threshold
        self.active_layer: Optional[TargetLayer] = None
        self.locked_axis: Optional[ScrollAxis] = None
        self.in_gesture: bool = False
        self.last_event_time_ms: float = 0.0

    def arbitrate(self, event: PointerWheelEvent) -> Tuple[bool, Optional[ScrollAxis]]:
        """Determines if the event should be handled and locks orientation if needed.

        Returns (should_handle, locked_axis).
        """
        self.last_event_time_ms = event.timestamp_ms

        # 1. Routing precedence:
        # Canvas and DOM Header are both handled by virtual grid arbiter.
        # Frozen corner absorbs all pointer events to prevent accidental panning.
        if event.target_layer == TargetLayer.FROZEN_CORNER:
            event.prevent_default()
            return False, None

        if event.target_layer == TargetLayer.EXTERNAL:
            return False, None

        # Always prevent default browser viewport scroll to avoid double-scroll
        event.prevent_default()
        self.active_layer = event.target_layer
        self.in_gesture = True

        # 2. Axis arbitration / Lock detection
        abs_x = abs(event.delta_x)
        abs_y = abs(event.delta_y)

        if self.locked_axis is None:
            if abs_x > abs_y * 2.0 and abs_x > self.lock_axis_threshold:
                self.locked_axis = ScrollAxis.HORIZONTAL
            elif abs_y > abs_x * 2.0 and abs_y > self.lock_axis_threshold:
                self.locked_axis = ScrollAxis.VERTICAL
            elif abs_x > 0.0 or abs_y > 0.0:
                self.locked_axis = ScrollAxis.BIDIRECTIONAL

        return True, self.locked_axis

    def end_gesture(self) -> None:
        self.in_gesture = False
        self.locked_axis = None
        self.active_layer = None


class KineticScrollEngine:
    """High-precision inertial kinetic momentum scroll decay and boundary spring physics."""

    def __init__(
        self,
        boundaries: ViewportBoundary,
        friction_decay: float = 3.8,
        min_velocity_cutoff: float = 4.0,  # px/s
    ):
        self.boundaries = boundaries
        self.friction_decay = friction_decay
        self.min_velocity_cutoff = min_velocity_cutoff

        self.state = ScrollState()
        self.arbitrator = GestureArbitrator()
        self.velocity_estimator = VelocityEstimator()

    def handle_wheel_event(self, event: PointerWheelEvent) -> SyncManifest:
        """Processes incoming wheel event, applies direct displacement, and updates velocity."""
        should_handle, locked_axis = self.arbitrator.arbitrate(event)
        if not should_handle:
            return self.get_sync_manifest()

        # Update gesture phase
        if self.state.phase not in (GesturePhase.BEGAN, GesturePhase.UPDATED):
            self.state.phase = GesturePhase.BEGAN
        else:
            self.state.phase = GesturePhase.UPDATED

        # Record delta for kinetic momentum calculation
        self.velocity_estimator.record_delta(event.timestamp_ms, event.delta_x, event.delta_y)

        # Apply displacement based on axis lock
        dx = event.delta_x
        dy = event.delta_y

        if locked_axis == ScrollAxis.HORIZONTAL:
            dy = 0.0
        elif locked_axis == ScrollAxis.VERTICAL:
            dx = 0.0

        # Boundary clamping with rubberband resistance if enabled
        self._apply_displacement(dx, dy)
        self.state.last_update_ms = event.timestamp_ms
        self.state.is_animating = False

        return self.get_sync_manifest()

    def release_gesture(self, timestamp_ms: float) -> None:
        """User lifts wheel/touch; starts momentum animation phase."""
        vx, vy = self.velocity_estimator.get_velocity(timestamp_ms)
        self.arbitrator.end_gesture()

        # Check if kinetic energy is above threshold
        speed = math.hypot(vx, vy)
        is_overscrolled = (self.state.overscroll_x != 0.0) or (self.state.overscroll_y != 0.0)

        if speed >= self.min_velocity_cutoff or is_overscrolled:
            self.state.velocity_x = vx
            self.state.velocity_y = vy
            self.state.phase = GesturePhase.MOMENTUM_BEGAN
            self.state.is_animating = True
            self.state.last_update_ms = timestamp_ms
        else:
            self.state.velocity_x = 0.0
            self.state.velocity_y = 0.0
            self.state.phase = GesturePhase.ENDED
            self.state.is_animating = False
            self.state.last_update_ms = timestamp_ms

    def step_simulation(self, current_time_ms: float) -> SyncManifest:
        """Steps Symplectic Euler simulation forward by dt."""
        if not self.state.is_animating:
            return self.get_sync_manifest()

        dt = (current_time_ms - self.state.last_update_ms) / 1000.0
        # Clamp dt to prevent explosion on large frames/hiccups
        dt = max(0.0005, min(0.064, dt))
        self.state.last_update_ms = current_time_ms
        self.state.phase = GesturePhase.MOMENTUM_UPDATED

        # 1. Physics integration for X axis
        self._step_axis_physics(
            dt,
            axis_val=self.state.x,
            velocity=self.state.velocity_x,
            overscroll=self.state.overscroll_x,
            min_bound=self.boundaries.min_x,
            max_bound=self.boundaries.max_x,
            is_x=True,
        )

        # 2. Physics integration for Y axis
        self._step_axis_physics(
            dt,
            axis_val=self.state.y,
            velocity=self.state.velocity_y,
            overscroll=self.state.overscroll_y,
            min_bound=self.boundaries.min_y,
            max_bound=self.boundaries.max_y,
            is_x=False,
        )

        # Check termination condition
        speed = math.hypot(self.state.velocity_x, self.state.velocity_y)
        overscroll_dist = math.hypot(self.state.overscroll_x, self.state.overscroll_y)

        if speed < self.min_velocity_cutoff and overscroll_dist < 0.1:
            # Snap to clean bound
            self.state.x = max(self.boundaries.min_x, min(self.boundaries.max_x, self.state.x))
            self.state.y = max(self.boundaries.min_y, min(self.boundaries.max_y, self.state.y))
            self.state.overscroll_x = 0.0
            self.state.overscroll_y = 0.0
            self.state.velocity_x = 0.0
            self.state.velocity_y = 0.0
            self.state.phase = GesturePhase.ENDED
            self.state.is_animating = False

        return self.get_sync_manifest()

    def _apply_displacement(self, dx: float, dy: float) -> None:
        """Applies displacement with overscroll resistance."""
        # Horizontal
        new_x = self.state.x + dx
        if new_x < self.boundaries.min_x:
            deficit = self.boundaries.min_x - new_x
            resistance = 1.0 / (1.0 + (deficit / 40.0)) if self.boundaries.enable_rubberband else 0.0
            self.state.x = self.boundaries.min_x - (deficit * resistance)
            self.state.overscroll_x = self.state.x - self.boundaries.min_x
        elif new_x > self.boundaries.max_x:
            excess = new_x - self.boundaries.max_x
            resistance = 1.0 / (1.0 + (excess / 40.0)) if self.boundaries.enable_rubberband else 0.0
            self.state.x = self.boundaries.max_x + (excess * resistance)
            self.state.overscroll_x = self.state.x - self.boundaries.max_x
        else:
            self.state.x = new_x
            self.state.overscroll_x = 0.0

        # Vertical
        new_y = self.state.y + dy
        if new_y < self.boundaries.min_y:
            deficit = self.boundaries.min_y - new_y
            resistance = 1.0 / (1.0 + (deficit / 40.0)) if self.boundaries.enable_rubberband else 0.0
            self.state.y = self.boundaries.min_y - (deficit * resistance)
            self.state.overscroll_y = self.state.y - self.boundaries.min_y
        elif new_y > self.boundaries.max_y:
            excess = new_y - self.boundaries.max_y
            resistance = 1.0 / (1.0 + (excess / 40.0)) if self.boundaries.enable_rubberband else 0.0
            self.state.y = self.boundaries.max_y + (excess * resistance)
            self.state.overscroll_y = self.state.y - self.boundaries.max_y
        else:
            self.state.y = new_y
            self.state.overscroll_y = 0.0

    def _step_axis_physics(
        self,
        dt: float,
        axis_val: float,
        velocity: float,
        overscroll: float,
        min_bound: float,
        max_bound: float,
        is_x: bool,
    ) -> None:
        if abs(overscroll) > 0.001:
            # In overscroll territory -> Apply spring restitution (Hooke's law + damping)
            # F = -k * x - c * v
            spring_force = -self.boundaries.rubberband_stiffness * overscroll
            damping_force = -self.boundaries.rubberband_damping * velocity
            accel = spring_force + damping_force

            new_v = velocity + accel * dt
            new_pos = axis_val + new_v * dt

            # Recalculate overscroll
            if new_pos < min_bound:
                new_overscroll = new_pos - min_bound
            elif new_pos > max_bound:
                new_overscroll = new_pos - max_bound
            else:
                new_overscroll = 0.0
        else:
            # Free kinetic glide territory -> Exponential friction decay
            decay_factor = math.exp(-self.friction_decay * dt)
            new_v = velocity * decay_factor
            new_pos = axis_val + new_v * dt

            # Check if hit boundary
            if new_pos < min_bound:
                new_overscroll = new_pos - min_bound
            elif new_pos > max_bound:
                new_overscroll = new_pos - max_bound
            else:
                new_overscroll = 0.0

        if is_x:
            self.state.x = new_pos
            self.state.velocity_x = new_v
            self.state.overscroll_x = new_overscroll
        else:
            self.state.y = new_pos
            self.state.velocity_y = new_v
            self.state.overscroll_y = new_overscroll

    def get_sync_manifest(self) -> SyncManifest:
        """Produces synchronization manifest guaranteeing 0.000px drift between WebGL and DOM."""
        # Rounding/quantizing to sub-pixel precision (0.001px)
        curr_x = round(self.state.x, 3)
        curr_y = round(self.state.y, 3)
        over_x = round(self.state.overscroll_x, 3)
        over_y = round(self.state.overscroll_y, 3)

        # DOM sticky headers track scroll along their respective orthogonal dimensions
        # Header Row tracks scroll_x, Header Col tracks scroll_y
        dom_header_x = curr_x
        dom_header_y = curr_y

        # WebGL Camera uniform tracks both
        webgl_x = curr_x
        webgl_y = curr_y

        drift = abs(dom_header_x - webgl_x) + abs(dom_header_y - webgl_y)

        return SyncManifest(
            scroll_x=curr_x,
            scroll_y=curr_y,
            overscroll_x=over_x,
            overscroll_y=over_y,
            dom_header_x=dom_header_x,
            dom_header_y=dom_header_y,
            webgl_uniform_x=webgl_x,
            webgl_uniform_y=webgl_y,
            phase=self.state.phase.value,
            is_in_overscroll=(abs(over_x) > 0.001 or abs(over_y) > 0.001),
            drift_delta=drift,
        )
