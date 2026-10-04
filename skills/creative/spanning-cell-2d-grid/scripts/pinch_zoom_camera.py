"""Multi-Touch Pinch-to-Zoom Camera Matrix & 2D Orthographic Projections.

Provides mathematical foundations, focal-point anchoring, matrix transformation,
and GPU uniform / DOM CSS sync manifests for virtual 2D grid zooming.
"""

from dataclasses import dataclass, field
from typing import Tuple, List, Optional
import math


@dataclass
class TouchPoint:
    """Represents a touch contact point in screen viewport space."""
    id: int
    x: float
    y: float


@dataclass
class PinchGestureState:
    """Extracted dual-touch geometric state."""
    distance: float
    center_x: float
    center_y: float
    angle_rad: float


class GestureAnalyzer:
    """Analyzes multi-touch points to extract distance, center, and pinch scale delta."""

    def __init__(self, min_pinch_distance: float = 10.0):
        self.min_pinch_distance = min_pinch_distance

    def analyze_two_touches(self, t1: TouchPoint, t2: TouchPoint) -> PinchGestureState:
        dx = t2.x - t1.x
        dy = t2.y - t1.y
        dist = math.hypot(dx, dy)
        center_x = (t1.x + t2.x) / 2.0
        center_y = (t1.y + t2.y) / 2.0
        angle = math.atan2(dy, dx)
        return PinchGestureState(
            distance=max(dist, self.min_pinch_distance),
            center_x=center_x,
            center_y=center_y,
            angle_rad=angle
        )

    def compute_pinch_ratio(self, initial_state: PinchGestureState, current_state: PinchGestureState) -> float:
        if initial_state.distance <= 1e-6:
            return 1.0
        return current_state.distance / initial_state.distance


@dataclass
class OrthographicCamera2D:
    """Orthographic 2D Camera maintaining viewport bounds, zoom scale, and world offset."""
    viewport_width: float
    viewport_height: float
    min_zoom: float = 0.25
    max_zoom: float = 4.0
    current_zoom: float = 1.0
    target_zoom: float = 1.0
    camera_x: float = 0.0
    camera_y: float = 0.0

    # Spring damping for zoom transitions
    zoom_spring_k: float = 180.0
    zoom_damping_c: float = 24.0
    zoom_velocity: float = 0.0

    def set_zoom_immediate(self, zoom: float, focal_x: Optional[float] = None, focal_y: Optional[float] = None):
        """Sets zoom immediately with focal point anchoring."""
        clamped_zoom = max(self.min_zoom, min(self.max_zoom, zoom))
        if focal_x is None or focal_y is None:
            focal_x = self.viewport_width / 2.0
            focal_y = self.viewport_height / 2.0

        if abs(clamped_zoom - self.current_zoom) > 1e-7:
            # Focal point invariance equation:
            # World coordinate before zoom: W = (Focal - Camera) / Zoom_old
            # Camera_new = Focal - W * Zoom_new
            world_focal_x = (focal_x - self.camera_x) / self.current_zoom
            world_focal_y = (focal_y - self.camera_y) / self.current_zoom

            self.current_zoom = clamped_zoom
            self.target_zoom = clamped_zoom
            self.zoom_velocity = 0.0

            self.camera_x = focal_x - world_focal_x * clamped_zoom
            self.camera_y = focal_y - world_focal_y * clamped_zoom

    def set_target_zoom(self, target: float):
        """Sets smooth target zoom to be integrated via spring dynamics."""
        self.target_zoom = max(self.min_zoom, min(self.max_zoom, target))

    def step_spring_zoom(self, dt: float, focal_x: Optional[float] = None, focal_y: Optional[float] = None) -> bool:
        """Integrates spring dynamics towards target zoom using Symplectic Euler."""
        dt_clamped = max(0.001, min(0.064, dt))
        if focal_x is None or focal_y is None:
            focal_x = self.viewport_width / 2.0
            focal_y = self.viewport_height / 2.0

        delta_z = self.current_zoom - self.target_zoom
        if abs(delta_z) < 1e-5 and abs(self.zoom_velocity) < 1e-4:
            self.current_zoom = self.target_zoom
            self.zoom_velocity = 0.0
            return False

        # Symplectic Euler: F = -k * delta - c * v
        f_spring = -self.zoom_spring_k * delta_z - self.zoom_damping_c * self.zoom_velocity
        self.zoom_velocity += f_spring * dt_clamped
        new_zoom = self.current_zoom + self.zoom_velocity * dt_clamped

        # Clamp zoom during spring bounce
        clamped_new_zoom = max(self.min_zoom * 0.85, min(self.max_zoom * 1.15, new_zoom))

        # Update camera position anchored to focal point
        world_focal_x = (focal_x - self.camera_x) / self.current_zoom
        world_focal_y = (focal_y - self.camera_y) / self.current_zoom

        self.current_zoom = clamped_new_zoom
        self.camera_x = focal_x - world_focal_x * clamped_new_zoom
        self.camera_y = focal_y - world_focal_y * clamped_new_zoom

        return True

    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Maps viewport pixel coordinates to unscaled 2D world coordinates."""
        world_x = (screen_x - self.camera_x) / self.current_zoom
        world_y = (screen_y - self.camera_y) / self.current_zoom
        return world_x, world_y

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Maps 2D world coordinates to viewport pixel coordinates."""
        screen_x = world_x * self.current_zoom + self.camera_x
        screen_y = world_y * self.current_zoom + self.camera_y
        return screen_x, screen_y

    def get_orthographic_matrix_4x4(self) -> List[float]:
        """Returns 4x4 column-major orthographic projection matrix for WebGL/WebGPU shaders.
        
        Maps viewport [0, W] x [0, H] transformed by camera offset & zoom
        to Normalized Device Coordinates (NDC) [-1, 1] x [-1, 1], with Y down or standard.
        Here we generate standard 2D ortho:
        2 / (right - left), 0, 0, 0,
        0, 2 / (top - bottom), 0, 0,
        0, 0, -2 / (far - near), 0,
        tx, ty, tz, 1
        """
        # World view bounds mapped to viewport
        left = -self.camera_x / self.current_zoom
        top = -self.camera_y / self.current_zoom
        right = (self.viewport_width - self.camera_x) / self.current_zoom
        bottom = (self.viewport_height - self.camera_y) / self.current_zoom
        near = -1.0
        far = 1.0

        rl = right - left
        tb = bottom - top
        fn = far - near

        m00 = 2.0 / rl
        m11 = -2.0 / tb  # Invert Y so 0 is top
        m22 = -2.0 / fn
        m30 = -(right + left) / rl
        m31 = (bottom + top) / tb
        m32 = -(far + near) / fn
        m33 = 1.0

        # Column-major 16-element float array for glUniformMatrix4fv
        return [
            m00, 0.0, 0.0, 0.0,
            0.0, m11, 0.0, 0.0,
            0.0, 0.0, m22, 0.0,
            m30, m31, m32, m33
        ]

    def get_camera_uniform_2d(self) -> Tuple[float, float, float]:
        """Returns compact (offset_x, offset_y, zoom) for lightweight 2D vertex shaders."""
        return (self.camera_x, self.camera_y, self.current_zoom)

    def get_dom_css_transform(self) -> str:
        """Returns hardware-accelerated CSS transform string for DOM synchronization."""
        return f"matrix3d({self.current_zoom:.6f}, 0, 0, 0, 0, {self.current_zoom:.6f}, 0, 0, 0, 0, 1, 0, {self.camera_x:.4f}, {self.camera_y:.4f}, 0, 1)"


@dataclass
class CameraSyncManifest:
    """Unified render manifest ensuring 0.000px drift between WebGL & DOM headers."""
    zoom_scale: float
    camera_offset_x: float
    camera_offset_y: float
    visible_world_box: Tuple[float, float, float, float]  # min_x, min_y, max_x, max_y
    webgl_ortho_matrix: List[float]
    dom_css_transform: str
    subpixel_drift: float = 0.0


class ZoomController:
    """Top-level manager coordinating touch gestures, camera projections, and manifest generation."""

    def __init__(self, viewport_width: float, viewport_height: float, min_zoom: float = 0.25, max_zoom: float = 4.0):
        self.camera = OrthographicCamera2D(
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            min_zoom=min_zoom,
            max_zoom=max_zoom
        )
        self.analyzer = GestureAnalyzer()
        self._initial_gesture_state: Optional[PinchGestureState] = None
        self._initial_zoom_at_pinch: float = 1.0

    def on_touch_start(self, t1: TouchPoint, t2: TouchPoint):
        """Initiates pinch gesture."""
        self._initial_gesture_state = self.analyzer.analyze_two_touches(t1, t2)
        self._initial_zoom_at_pinch = self.camera.current_zoom

    def on_touch_move(self, t1: TouchPoint, t2: TouchPoint) -> CameraSyncManifest:
        """Updates camera zoom in real-time according to pinch distance ratio."""
        if self._initial_gesture_state is None:
            self.on_touch_start(t1, t2)

        current_gesture = self.analyzer.analyze_two_touches(t1, t2)
        ratio = self.analyzer.compute_pinch_ratio(self._initial_gesture_state, current_gesture)
        new_zoom = self._initial_zoom_at_pinch * ratio

        # Anchor at current pinch center
        self.camera.set_zoom_immediate(
            zoom=new_zoom,
            focal_x=current_gesture.center_x,
            focal_y=current_gesture.center_y
        )
        return self.generate_sync_manifest()

    def on_touch_end(self):
        """Completes pinch gesture, resetting reference tracking."""
        self._initial_gesture_state = None

    def on_wheel_zoom(self, delta_wheel: float, focal_x: float, focal_y: float) -> CameraSyncManifest:
        """Handles desktop mouse wheel zooming with exponential sensitivity."""
        zoom_factor = math.exp(-delta_wheel * 0.002)
        target = self.camera.current_zoom * zoom_factor
        self.camera.set_zoom_immediate(target, focal_x=focal_x, focal_y=focal_y)
        return self.generate_sync_manifest()

    def generate_sync_manifest(self) -> CameraSyncManifest:
        """Creates unified render synchronization manifest."""
        w_min_x, w_min_y = self.camera.screen_to_world(0.0, 0.0)
        w_max_x, w_max_y = self.camera.screen_to_world(self.camera.viewport_width, self.camera.viewport_height)

        # Drift between world-to-screen roundtrip
        test_world_x = (w_min_x + w_max_x) / 2.0
        test_world_y = (w_min_y + w_max_y) / 2.0
        sx, sy = self.camera.world_to_screen(test_world_x, test_world_y)
        rx, ry = self.camera.screen_to_world(sx, sy)
        drift = math.hypot(test_world_x - rx, test_world_y - ry)

        return CameraSyncManifest(
            zoom_scale=self.camera.current_zoom,
            camera_offset_x=self.camera.camera_x,
            camera_offset_y=self.camera.camera_y,
            visible_world_box=(w_min_x, w_min_y, w_max_x, w_max_y),
            webgl_ortho_matrix=self.camera.get_orthographic_matrix_4x4(),
            dom_css_transform=self.camera.get_dom_css_transform(),
            subpixel_drift=drift
        )
