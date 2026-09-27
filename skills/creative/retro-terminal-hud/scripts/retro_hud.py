#!/usr/bin/env python3
"""
Retro Terminal HUD Generator & TUI Synthesizer
Generates lightweight, zero-dependency, standalone ANSI/HTML cyber cockpit artifacts.
Zero external packages; runs on standard Python 3.
"""

import sys
import os
import time
import json
import re

ANSI_CLEAR = "\033[2J\033[H"
ANSI_HOME = "\033[H"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"

# Palette: Cyan, Amber, Emerald, Violet, Rose
FG_CYAN = "\033[38;2;14;165;233m"
FG_AMBER = "\033[38;2;245;158;11m"
FG_EMERALD = "\033[38;2;16;185;129m"
FG_VIOLET = "\033[38;2;139;92;246m"
FG_ROSE = "\033[38;2;244;63;94m"
FG_MUTED = "\033[38;2;100;116;139m"

ANSI_RE = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')

def strip_ansi(text: str) -> str:
    return ANSI_RE.sub('', text)

def pad_visible(text: str, width: int, align: str = 'left') -> str:
    vis_len = len(strip_ansi(text))
    pad = max(0, width - vis_len)
    if align == 'right':
        return (' ' * pad) + text
    elif align == 'center':
        left = pad // 2
        right = pad - left
        return (' ' * left) + text + (' ' * right)
    return text + (' ' * pad)

def render_gauge(value: float, max_val: float = 100.0, width: int = 20, color: str = FG_CYAN) -> str:
    ratio = max(0.0, min(1.0, value / max_val))
    filled = int(round(ratio * width))
    bar = "█" * filled + "░" * (width - filled)
    return f"{color}{bar}{ANSI_RESET} {value:5.1f}%"

def render_ascii_box(title: str, lines: list, width: int = 68, color: str = FG_CYAN) -> str:
    top = f"{color}┌─ {ANSI_BOLD}{title}{ANSI_RESET}{color} " + "─" * max(0, width - 4 - len(title)) + f"┐{ANSI_RESET}"
    bottom = f"{color}└" + "─" * (width - 2) + f"┘{ANSI_RESET}"
    body = []
    for line in lines:
        padded = pad_visible(line, width - 4)
        body.append(f"{color}│{ANSI_RESET} {padded} {color}│{ANSI_RESET}")
    return "\n".join([top] + body + [bottom])

def generate_hud_html(title: str, metrics: dict, output_path: str):
    """
    Renders a standalone zero-dependency HTML Cyber HUD with scanlines, CRT glow,
    circular SVG gauges, reactive status, and optional Web Audio synth clicks.
    """
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    :root {{
      --bg: #090a0f;
      --card-bg: rgba(15, 23, 42, 0.75);
      --border: rgba(14, 165, 233, 0.35);
      --border-glow: rgba(14, 165, 233, 0.6);
      --cyan: #0ea5e9;
      --amber: #f59e0b;
      --emerald: #10b981;
      --rose: #f43f5e;
      --text-main: #f8fafc;
      --text-muted: #64748b;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text-main);
      font-family: 'JetBrains Mono', 'Courier New', monospace;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
      position: relative;
      overflow-x: hidden;
    }}
    /* CRT Scanline overlay */
    body::before {{
      content: " ";
      position: fixed;
      top: 0; left: 0; bottom: 0; right: 0;
      background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
      background-size: 100% 4px;
      z-index: 100;
      pointer-events: none;
      opacity: 0.6;
    }}
    /* CRT subtle flicker */
    .cockpit-container {{
      width: 100%;
      max-width: 900px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      box-shadow: 0 0 35px rgba(14, 165, 233, 0.15), inset 0 0 20px rgba(14, 165, 233, 0.05);
      border-radius: 8px;
      padding: 24px;
      backdrop-filter: blur(12px);
      position: relative;
    }}
    .hud-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
      margin-bottom: 24px;
    }}
    .hud-title {{
      font-size: 1.15rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--cyan);
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .hud-status-badge {{
      display: inline-block;
      width: 8px;
      height: 8px;
      background: var(--emerald);
      border-radius: 50%;
      box-shadow: 0 0 8px var(--emerald);
      animation: pulse-dot 2s infinite ease-in-out;
    }}
    @keyframes pulse-dot {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.4; transform: scale(0.85); }}
    }}
    .hud-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 18px;
      margin-bottom: 24px;
    }}
    .metric-card {{
      background: rgba(11, 15, 25, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.07);
      border-radius: 6px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      transition: border-color 0.2s, box-shadow 0.2s;
    }}
    .metric-card:hover {{
      border-color: var(--border-glow);
      box-shadow: 0 0 15px rgba(14, 165, 233, 0.2);
    }}
    .metric-label {{
      font-size: 0.75rem;
      color: var(--text-muted);
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }}
    .metric-val {{
      font-size: 1.4rem;
      font-weight: bold;
    }}
    .gauge-bar-track {{
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
      overflow: hidden;
    }}
    .gauge-bar-fill {{
      height: 100%;
      border-radius: 3px;
      transition: width 0.4s ease;
    }}
    .hud-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.72rem;
      color: var(--text-muted);
      border-top: 1px solid rgba(255, 255, 255, 0.07);
      padding-top: 16px;
    }}
    .btn-audio {{
      background: transparent;
      border: 1px solid var(--border);
      color: var(--cyan);
      font-family: inherit;
      font-size: 0.75rem;
      padding: 6px 14px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .btn-audio:hover {{
      background: rgba(14, 165, 233, 0.15);
      box-shadow: 0 0 10px rgba(14, 165, 233, 0.3);
    }}
  </style>
</head>
<body>
  <div class="cockpit-container">
    <header class="hud-header">
      <div class="hud-title">
        <span class="hud-status-badge"></span>
        <span>{title}</span>
      </div>
      <div style="font-size: 0.8rem; color: var(--text-muted);" id="clock">LIVE</div>
    </header>

    <div class="hud-grid">
      <div class="metric-card">
        <span class="metric-label">CPU Core Activity</span>
        <span class="metric-val" style="color: var(--amber);">{metrics.get('cpu', 24.5)}%</span>
        <div class="gauge-bar-track">
          <div class="gauge-bar-fill" style="width: {metrics.get('cpu', 24.5)}%; background: var(--amber);"></div>
        </div>
      </div>
      <div class="metric-card">
        <span class="metric-label">RAM Allocated</span>
        <span class="metric-val" style="color: var(--emerald);">{metrics.get('ram', 4.2)} GB</span>
        <div class="gauge-bar-track">
          <div class="gauge-bar-fill" style="width: {(metrics.get('ram', 4.2) / 9.0) * 100}%; background: var(--emerald);"></div>
        </div>
      </div>
      <div class="metric-card">
        <span class="metric-label">Pipeline Frame Rate</span>
        <span class="metric-val" style="color: var(--cyan);">{metrics.get('fps', 60.0)} FPS</span>
        <div class="gauge-bar-track">
          <div class="gauge-bar-fill" style="width: 100%; background: var(--cyan);"></div>
        </div>
      </div>
    </div>

    <footer class="hud-footer">
      <span>NOUS CYBER HUD // ZERO-EMOJI ENFORCED</span>
      <button class="btn-audio" id="btnBeep" onclick="playBeep()">TEST AUDIO PULSE</button>
    </footer>
  </div>

  <script>
    setInterval(() => {{
      const d = new Date();
      document.getElementById('clock').innerText = d.toTimeString().split(' ')[0] + '.' + String(d.getMilliseconds()).padStart(3, '0');
    }}, 100);

    let audioCtx = null;
    function playBeep() {{
      try {{
        if (!audioCtx) {{
          audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }}
        if (audioCtx.state === 'suspended') {{
          audioCtx.resume();
        }}
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1760, audioCtx.currentTime + 0.08);
        gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.08);
      }} catch (e) {{
        console.error("Audio synth error:", e);
      }}
    }}
  </script>
</body>
</html>"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    if len(sys.argv) < 2:
        print("Usage: retro_hud.py [tui|html] [args...]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "tui":
        lines = [
            f"STATUS  : {FG_EMERALD}ONLINE - 100% NOMINAL{ANSI_RESET}",
            f"CPU LOAD: {render_gauge(28.4, 100, 24, FG_AMBER)}",
            f"RAM USED: {render_gauge(4.18, 9.0, 24, FG_EMERALD)} (4.18/9.0 GB)",
            f"NETWORK : {FG_CYAN}420 KB/s RX │ 180 KB/s TX{ANSI_RESET}",
            f"AUDIO   : {FG_VIOLET}WEB AUDIO SYNTH READY [880Hz PULSE]{ANSI_RESET}",
            f"CADENCE : {FG_MUTED}100ms Direct Kernel Sampling Zero-Flicker{ANSI_RESET}"
        ]
        box = render_ascii_box("HERMES CYBER COCKPIT // TELEMETRY HUD", lines, width=64, color=FG_CYAN)
        print(box)
    elif cmd == "html":
        out_file = sys.argv[2] if len(sys.argv) > 2 else "/tmp/cyber_hud.html"
        generate_hud_html("HERMES COCKPIT TELEMETRY", {"cpu": 32.1, "ram": 4.12, "fps": 60.0}, out_file)
        print(f"HTML HUD generated at: {out_file}")

if __name__ == "__main__":
    main()
