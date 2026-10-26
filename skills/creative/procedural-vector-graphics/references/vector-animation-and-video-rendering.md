# Vector Animation & Parametric Video Rendering

Compiling procedural mathematical SVG vectors into seamless looping 60 FPS animations and high-efficiency MP4 video files.

## 1. The Normalized Time Invariant ($t_{\text{norm}}$)

Seamless periodic animation requires every dynamic element to be parameterized by a single normalized time variable:
$$t_{\text{norm}} = \frac{\text{frame\_index}}{\text{total\_frames}}, \quad t_{\text{norm}} \in [0.0, 1.0)$$

### Golden Rules of Seamless Looping:
1. **Periodic Trigonometric Continuity:**
   Any oscillatory displacement, rotation, or scale must use complete $2\pi$ cycles:
   $$x(t) = x_{\text{base}} + A \cdot \sin(2\pi \cdot t_{\text{norm}})$$
   $$y(t) = y_{\text{base}} + A \cdot \cos(2\pi \cdot t_{\text{norm}})$$
   Because $\sin(0) = \sin(2\pi) = 0$, frame $0$ and frame $N$ connect without visual hitching.
2. **Horizontal Wrapping (Seamless Cloud & Surface Drift):**
   When translating drifting elements (clouds, water waves, passing obstacles):
   $$\text{offset} = (t_{\text{norm}} \cdot \text{speed}) \pmod W$$
   Render duplicates at $\text{offset} - W$, $\text{offset}$, and $\text{offset} + W$ so as one instance exits the right edge, the duplicate enters seamlessly from the left.

---

## 2. Multi-Layer Parallax Speed Hierarchy

Depth perception in 2D vector animation is governed by relative translation velocity:

| Layer Depth | Visual Elements | Velocity Multiplier | Opacity | Blur / Stroke |
|---|---|---|---|---|
| **Deep Background** | Stars, distant moon, nebula | $0.0\times$ (Fixed) | $0.3 - 1.0$ (Pulsing) | Subtle glow halo |
| **Distant Layer** | High cirrus clouds, mountain ridge | $1.0\times$ baseline | $0.40 - 0.50$ | Thin 1px boundary |
| **Midground Layer** | Stratus clouds, floating airships | $1.6\times$ baseline | $0.70 - 0.80$ | 2px contour stroke |
| **Foreground Layer** | Storm cumulus, dark silhouettes | $2.2\times$ baseline | $0.95 - 1.00$ | Crisp 3px stroke |

---

## 3. High-Throughput Headless Pipeline (Python + resvg-py + ffmpeg)

Directly pipeline vector mathematics to MP4 video in under 5 seconds:

```python
import os
import math
import subprocess
import resvg_py

def render_vector_animation(render_svg_fn, total_frames=90, fps=30, output_mp4="animation.mp4"):
    frame_dir = "/tmp/vector_frames"
    os.makedirs(frame_dir, exist_ok=True)

    # 1. Generate & Rasterize Frames
    for idx in range(total_frames):
        t_norm = idx / total_frames
        svg_code = render_svg_fn(t_norm)
        png_bytes = resvg_py.svg_to_bytes(svg_code)
        with open(f"{frame_dir}/frame_{idx:03d}.png", "wb") as f:
            f.write(png_bytes)

    # 2. Assemble MP4 via ffmpeg
    cmd = [
        "ffmpeg", "-y", "-framerate", str(fps),
        "-i", f"{frame_dir}/frame_%03d.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "18", output_mp4
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_mp4
```

### Video Codec Requirements:
- `-pix_fmt yuv420p`: Mandatory for broad browser, mobile, and Telegram native video playback compatibility.
- `-crf 18`: Visually lossless H.264 compression preserving razor-sharp vector line art without macroblocking.
- Payload efficiency: A 90-frame (3-second) vector animation compresses to under $60\text{ KB}$.
