#!/usr/bin/env python3
"""
Procedural Vector Graphics Engine.
Generates resolution-independent SVG vector illustrations directly from mathematical logic,
Catmull-Rom splines, and geometric primitives. Optionally renders to PNG via resvg-py.
"""

import sys
import os
import math
import argparse
import json

class Shapes:
    def __init__(self):
        self.items = []
        self.minx = self.miny = 1e9
        self.maxx = self.maxy = -1e9

    def _box(self, pts):
        for x, y in pts:
            self.minx = min(self.minx, x)
            self.miny = min(self.miny, y)
            self.maxx = max(self.maxx, x)
            self.maxy = max(self.maxy, y)

    def rc(self, x, y, w, h, fill="none", stroke="none", stroke_width=1, r=0, rot=0):
        a = math.radians(rot)
        ca, sa = math.cos(a), math.sin(a)
        self._box([(x + dx * ca - dy * sa, y + dx * sa + dy * ca)
                   for dx in (-w/2, w/2) for dy in (-h/2, h/2)])
        style = f'fill="{fill}"'
        if stroke != "none":
            style += f' stroke="{stroke}" stroke-width="{stroke_width}"'
        self.items.append(
            f'<rect x="{-w/2:.1f}" y="{-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:.1f}" '
            f'{style} transform="translate({x:.1f} {y:.1f}) rotate({rot})"/>'
        )
        return self

    def el(self, x, y, w, h, fill="none", stroke="none", stroke_width=1):
        self._box([(x - w/2, y - h/2), (x + w/2, y + h/2)])
        style = f'fill="{fill}"'
        if stroke != "none":
            style += f' stroke="{stroke}" stroke-width="{stroke_width}"'
        self.items.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w/2:.1f}" ry="{h/2:.1f}" {style}/>')
        return self

    def circle(self, x, y, r, fill="none", stroke="none", stroke_width=1):
        return self.el(x, y, r*2, r*2, fill, stroke, stroke_width)

    def pth(self, pts, fill="none", stroke="none", stroke_width=1, smooth=0.4, closed=True):
        if not pts:
            return self
        n = len(pts)
        if n < 3 or smooth == 0:
            d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
            for p in pts[1:]:
                d += f' L{p[0]:.1f} {p[1]:.1f}'
            if closed:
                d += ' Z'
            self._box(pts)
        else:
            t_vec = []
            for k in range(n):
                prev_p, next_p = pts[(k - 1) % n], pts[(k + 1) % n]
                t_vec.append(((next_p[0] - prev_p[0]) * smooth / 2, (next_p[1] - prev_p[1]) * smooth / 2))
            d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
            for k in range(n):
                p0, p1 = pts[k], pts[(k + 1) % n]
                c1 = (p0[0] + t_vec[k][0], p0[1] + t_vec[k][1])
                c2 = (p1[0] - t_vec[(k + 1) % n][0], p1[1] - t_vec[(k + 1) % n][1])
                d += f' C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p1[0]:.1f} {p1[1]:.1f}'
                self._box([c1, c2, p1])
            if closed:
                d += ' Z'

        style = f'fill="{fill}"'
        if stroke != "none":
            style += f' stroke="{stroke}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"'
        self.items.append(f'<path d="{d}" {style}/>')
        return self

    def text(self, x, y, content, font_size=16, fill="#EDEDED", font_family="Inter Tight, sans-serif", font_weight=600, letter_spacing=0, text_anchor="middle"):
        self._box([(x - 100, y - font_size), (x + 100, y + font_size)])
        self.items.append(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{font_size}" font-family="{font_family}" '
            f'font-weight="{font_weight}" letter-spacing="{letter_spacing}" text-anchor="{text_anchor}">{content}</text>'
        )
        return self

    def to_svg(self, padding=16, bg="#0D0E12"):
        x0 = math.floor(self.minx - padding)
        y0 = math.floor(self.miny - padding)
        w = math.ceil(self.maxx + padding) - x0
        h = math.ceil(self.maxy + padding) - y0
        bg_rect = f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w}" height="{h}">{bg_rect}{"".join(self.items)}</svg>'

def render_sample_cyber_seal():
    """Generates an Upnormal Cybernetic System Seal / Vector Insignia."""
    s = Shapes()
    # Outer geometric rings
    s.circle(0, 0, 180, fill="none", stroke="#222630", stroke_width=2)
    s.circle(0, 0, 160, fill="rgba(255,255,255,0.02)", stroke="#FA5D29", stroke_width=1.5)
    
    # Radiating ticks
    for i in range(36):
        ang = math.radians(i * 10)
        r1 = 168 if i % 3 == 0 else 164
        r2 = 175
        x1, y1 = r1 * math.cos(ang), r1 * math.sin(ang)
        x2, y2 = r2 * math.cos(ang), r2 * math.sin(ang)
        s.pth([(x1, y1), (x2, y2)], stroke="#4A5263" if i % 3 != 0 else "#FA5D29", stroke_width=1.5, smooth=0, closed=False)

    # Core frosted diamond
    s.rc(0, 0, 140, 140, fill="rgba(25, 28, 36, 0.8)", stroke="#49B3FC", stroke_width=1.5, r=16, rot=45)
    s.rc(0, 0, 100, 100, fill="rgba(250, 93, 41, 0.08)", stroke="rgba(255,255,255,0.15)", stroke_width=1, r=8, rot=45)

    # Dynamic spline wave
    wave_pts = []
    for step in range(9):
        wx = -90 + step * 22.5
        wy = math.sin(step * 0.8) * 25
        wave_pts.append((wx, wy))
    s.pth(wave_pts, stroke="#49B3FC", stroke_width=3, smooth=0.4, closed=False)

    # Core node
    s.circle(0, 0, 18, fill="#FA5D29", stroke="#FFFFFF", stroke_width=2)
    s.circle(0, 0, 6, fill="#FFFFFF")

    # Typography anchors
    s.text(0, -60, "AUTONOMOUS SYSTEM", font_size=11, fill="#8E9AA8", letter_spacing=2)
    s.text(0, 75, "VERIFIED PROTOCOL", font_size=10, fill="#FA5D29", letter_spacing=2.5)

    return s

def render_sample_duck():
    """Generates the iconic Bekbek procedural mascot duck."""
    s = Shapes()
    # Subtle background halo ring
    s.circle(0, 0, 190, fill="rgba(255,255,255,0.02)", stroke="rgba(255,255,255,0.06)", stroke_width=1.5)

    # Water ripples
    s.pth([(-130, 95), (-60, 90), (0, 98), (70, 92), (140, 95)], stroke="#49B3FC", stroke_width=3, smooth=0.4, closed=False)
    s.pth([(-90, 115), (-20, 112), (40, 118), (100, 114)], stroke="rgba(73, 179, 252, 0.4)", stroke_width=2, smooth=0.4, closed=False)

    # Body spline
    body_pts = [
        (-90, 40), (-115, 20), (-80, 50), (-40, 85),
        (20, 88), (75, 70), (90, 40), (85, 10),
        (40, -10), (-10, 10), (-60, 25)
    ]
    s.pth(body_pts, fill="#FFD166", stroke="#111111", stroke_width=3, smooth=0.35)

    # Head circle
    s.circle(42, -35, 48, fill="#FFD166", stroke="#111111", stroke_width=3)

    # Beak spline
    beak_pts = [(75, -28), (125, -22), (115, -10), (72, -12)]
    s.pth(beak_pts, fill="#FA5D29", stroke="#111111", stroke_width=3, smooth=0.3)
    s.circle(88, -22, 2.5, fill="#8E2800")

    # Eye with specular catchlights
    s.circle(52, -45, 11, fill="#111111")
    s.circle(55, -48, 4, fill="#FFFFFF")
    s.circle(49, -42, 1.8, fill="#FFFFFF")

    # Blush
    s.el(36, -26, 16, 10, fill="rgba(250, 93, 41, 0.25)")

    # Wing spline
    wing_pts = [(-50, 45), (-10, 32), (30, 45), (15, 68), (-25, 70)]
    s.pth(wing_pts, fill="#FFC043", stroke="#111111", stroke_width=2.5, smooth=0.4)

    # Bubbles
    s.circle(-105, 75, 4, fill="#49B3FC")
    s.circle(115, 80, 5, fill="#49B3FC")

    # Captions
    s.text(0, 155, "BEKBEK — PROCEDURAL DUCK", font_size=12, fill="#EDEDED", letter_spacing=2.5)
    s.text(0, 172, "100% SVG CODE · ZERO PIXELS", font_size=9, fill="#FA5D29", letter_spacing=1.8)

    return s

def main():
    parser = argparse.ArgumentParser(description="Procedural Vector Graphics Engine")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--demo", action="store_true", help="Generate sample cybernetic seal vector")
    group.add_argument("--mascot", action="store_true", help="Generate Bekbek mascot duck vector")
    group.add_argument("--animate-sky", action="store_true", help="Render looping animated sky video")
    parser.add_argument("--frames", type=int, default=90, help="Total animation frames (default: 90)")
    parser.add_argument("--fps", type=int, default=30, help="Animation FPS (default: 30)")
    parser.add_argument("--output", default="vector_output.svg", help="Output SVG or MP4 filepath")
    parser.add_argument("--png", help="Optional output PNG filepath (via resvg-py)")

    args = parser.parse_args()

    if args.animate_sky:
        import subprocess
        frame_dir = "/tmp/sky_render_frames"
        os.makedirs(frame_dir, exist_ok=True)
        print(f"Rendering {args.frames} procedural vector frames...")
        
        # Generator for sky frame
        def render_sky(t_norm):
            w_box, h_box = 720, 480
            moon_x = 540 + math.sin(t_norm * 2 * math.pi) * 4
            moon_y = 110 + math.cos(t_norm * 2 * math.pi) * 3
            
            stars = []
            star_coords = [(80,70,2.5,0.0), (160,110,1.8,0.25), (240,60,2.0,0.5), (320,130,1.5,0.75), (410,80,2.8,0.1), (490,50,1.5,0.4), (620,95,2.2,0.6)]
            for sx, sy, sr, ph in star_coords:
                tw = 0.3 + 0.7 * (0.5 + 0.5 * math.sin((t_norm + ph) * 2 * math.pi))
                stars.append(f'<circle cx="{sx}" cy="{sy}" r="{sr*tw:.2f}" fill="#FFF" opacity="{tw:.2f}"/>')
            
            c_drift = (t_norm * 200) % w_box
            c_svg = []
            for shift in [-w_box, 0, w_box]:
                cx = c_drift + shift + 200
                c_svg.append(f'<path d="M {cx-120} 240 Q {cx-80} 200 {cx-40} 215 Q {cx} 175 {cx+50} 210 Q {cx+100} 195 {cx+130} 240 Z" fill="rgba(45, 52, 75, 0.5)"/>')
            
            return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_box} {h_box}" width="{w_box}" height="{h_box}">' \
                   f'<rect width="{w_box}" height="{h_box}" fill="#0A0D15"/>' \
                   f'{"".join(stars)}' \
                   f'<circle cx="{moon_x:.1f}" cy="{moon_y:.1f}" r="38" fill="rgba(255,235,180,0.2)"/>' \
                   f'<circle cx="{moon_x:.1f}" cy="{moon_y:.1f}" r="22" fill="#FFE8A3"/>' \
                   f'<circle cx="{moon_x-8:.1f}" cy="{moon_y-6:.1f}" r="20" fill="#0A0D15"/>' \
                   f'{"".join(c_svg)}' \
                   f'<path d="M -20 480 L 100 380 L 250 420 L 400 360 L 550 410 L 740 370 L 740 480 Z" fill="#06070B"/>' \
                   f'<text x="24" y="450" fill="#8E9AA8" font-family="monospace" font-size="10" letter-spacing="2">PROCEDURAL VECTOR SKY · 60 FPS MORPH</text>' \
                   f'</svg>'

        import resvg_py
        for f_idx in range(args.frames):
            t_norm = f_idx / args.frames
            svg_code = render_sky(t_norm)
            png_b = resvg_py.svg_to_bytes(svg_code)
            with open(f"{frame_dir}/f_{f_idx:03d}.png", "wb") as f_out:
                f_out.write(png_b)

        mp4_out = args.output if args.output.endswith(".mp4") else "sky_animation.mp4"
        cmd = ["ffmpeg", "-y", "-framerate", str(args.fps), "-i", f"{frame_dir}/f_%03d.png", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", mp4_out]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Compiled procedural vector animation video: {mp4_out} ({os.path.getsize(mp4_out)} bytes)")
        return

    if args.mascot:
        shapes = render_sample_duck()
        bg_col = "#0B0D13"
    else:
        shapes = render_sample_cyber_seal()
        bg_col = "#0A0B0E"

    svg_code = shapes.to_svg(padding=24, bg=bg_col)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg_code)
    print(f"Generated procedural vector SVG: {args.output} ({len(svg_code)} bytes)")

    if args.png:
        try:
            import resvg_py
            png_bytes = resvg_py.svg_to_bytes(svg_code)
            with open(args.png, "wb") as f:
                f.write(png_bytes)
            print(f"Rasterized to PNG: {args.png} ({len(png_bytes)} bytes)")
        except Exception as e:
            print(f"PNG rasterization failed: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
