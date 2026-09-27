#!/usr/bin/env python3
"""
E2E Headless Browser Testing & Visual Verification Runner (CDP-based)
Author: Bagas Cihuy & Hermes Agent
License: MIT
"""

import sys
import os
import json
import time
import urllib.request
import urllib.parse
import asyncio
import argparse
import subprocess
import tempfile
import base64

try:
    import websockets
except ImportError:
    print(json.dumps({"error": "websockets package missing. Run: pip install websockets"}))
    sys.exit(1)

VIEWPORT_PRESETS = {
    "desktop": {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False},
    "mobile": {"width": 390, "height": 844, "deviceScaleFactor": 2, "mobile": True},
    "tablet": {"width": 768, "height": 1024, "deviceScaleFactor": 2, "mobile": True}
}

def find_chrome_binary():
    candidates = [
        "/home/ubuntu/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome",
        "/home/ubuntu/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome",
        "/home/ubuntu/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium"
    ]
    for c in candidates:
        if os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return None

class CDPSession:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.msg_id = 0

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=25 * 1024 * 1024)

    async def close(self):
        if self.ws:
            await self.ws.close()

    async def send(self, method, params=None):
        self.msg_id += 1
        m_id = self.msg_id
        payload = {"id": m_id, "method": method}
        if params:
            payload["params"] = params
        await self.ws.send(json.dumps(payload))
        while True:
            raw = await self.ws.recv()
            resp = json.loads(raw)
            if resp.get("id") == m_id:
                if "error" in resp:
                    raise RuntimeError(f"CDP Error ({method}): {resp['error']}")
                return resp.get("result", {})

async def audit_url(url, viewport="desktop", screenshot_path=None, check_zero_emoji=True, eval_script=None):
    chrome_bin = find_chrome_binary()
    if not chrome_bin:
        return {"success": False, "error": "No usable Chromium/Chrome binary located on host."}

    user_data = tempfile.mkdtemp(prefix="cdp_runner_")
    port = 9445
    proc = subprocess.Popen([
        chrome_bin,
        "--headless=new",
        f"--remote-debugging-port={port}",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        f"--user-data-dir={user_data}"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    session = None
    try:
        # Wait for debugging endpoint
        connected = False
        target = None
        for _ in range(25):
            time.sleep(0.2)
            try:
                req = urllib.request.Request(f"http://127.0.0.1:{port}/json/new", method="PUT")
                with urllib.request.urlopen(req, timeout=2) as r:
                    target = json.loads(r.read().decode())
                connected = True
                break
            except Exception:
                continue

        if not connected or not target:
            return {"success": False, "error": f"Failed to connect to Chromium CDP port {port}"}

        ws_url = target.get("webSocketDebuggerUrl")
        session = CDPSession(ws_url)
        await session.connect()

        # Enable domains
        await session.send("Page.enable")
        await session.send("Runtime.enable")
        await session.send("DOM.enable")
        await session.send("Accessibility.enable")

        # Set device metrics
        vp_config = VIEWPORT_PRESETS.get(viewport, VIEWPORT_PRESETS["desktop"])
        await session.send("Emulation.setDeviceMetricsOverride", vp_config)

        # Navigate
        t0 = time.time()
        await session.send("Page.navigate", {"url": url})
        await asyncio.sleep(1.8) # Wait settle
        load_time_ms = int((time.time() - t0) * 1000)

        # Basic page info
        title_res = await session.send("Runtime.evaluate", {"expression": "document.title"})
        page_title = title_res.get("result", {}).get("value", "")

        # Layout metrics & horizontal overflow check
        layout_res = await session.send("Runtime.evaluate", {
            "expression": """
            (() => {
                const docEl = document.documentElement;
                const body = document.body;
                const scrollW = Math.max(docEl.scrollWidth, body ? body.scrollWidth : 0);
                const clientW = docEl.clientWidth || window.innerWidth;
                const hasOverflow = scrollW > (clientW + 1);
                return {
                    scrollWidth: scrollW,
                    clientWidth: clientW,
                    hasHorizontalOverflow: hasOverflow
                };
            })()
            """,
            "returnByValue": True
        })
        layout_metrics = layout_res.get("result", {}).get("value", {})

        # Accessibility tree inspect
        ax_tree = await session.send("Accessibility.getFullAXTree")
        nodes = ax_tree.get("nodes", [])
        button_count = sum(1 for n in nodes if n.get("role", {}).get("value") == "button")
        link_count = sum(1 for n in nodes if n.get("role", {}).get("value") == "link")
        heading_count = sum(1 for n in nodes if n.get("role", {}).get("value") == "heading")

        # Zero-emoji check
        emoji_count = 0
        if check_zero_emoji:
            emoji_res = await session.send("Runtime.evaluate", {
                "expression": """
                (() => {
                    const text = document.body ? document.body.innerText : '';
                    const emojiRegex = /[\\u{1F600}-\\u{1F64F}\\u{1F300}-\\u{1F5FF}\\u{1F680}-\\u{1F6FF}\\u{1F1E0}-\\u{1F1FF}\\u{2600}-\\u{26FF}\\u{2700}-\\u{27BF}\\u{FE00}-\\u{FE0F}\\u{1F900}-\\u{1F9FF}\\u{1FA70}-\\u{1FAFF}]/gu;
                    const matches = text.match(emojiRegex) || [];
                    return matches.length;
                })()
                """,
                "returnByValue": True
            })
            emoji_count = emoji_res.get("result", {}).get("value", 0)

        # Custom eval script
        custom_eval_result = None
        if eval_script:
            ev = await session.send("Runtime.evaluate", {
                "expression": eval_script,
                "returnByValue": True
            })
            custom_eval_result = ev.get("result", {}).get("value")

        # Screenshot capture
        screenshot_size = 0
        if screenshot_path:
            shot = await session.send("Page.captureScreenshot", {"format": "png"})
            b64_data = shot.get("data", "")
            if b64_data:
                raw_bytes = base64.b64decode(b64_data)
                screenshot_size = len(raw_bytes)
                os.makedirs(os.path.dirname(os.path.abspath(screenshot_path)), exist_ok=True)
                with open(screenshot_path, "wb") as f:
                    f.write(raw_bytes)

        return {
            "success": True,
            "url": url,
            "viewport": viewport,
            "page_title": page_title,
            "load_time_ms": load_time_ms,
            "layout": layout_metrics,
            "accessibility": {
                "total_ax_nodes": len(nodes),
                "buttons": button_count,
                "links": link_count,
                "headings": heading_count
            },
            "zero_emoji": {
                "passed": (emoji_count == 0),
                "emoji_count": emoji_count
            },
            "custom_eval": custom_eval_result,
            "screenshot_saved": screenshot_path if screenshot_size > 0 else None,
            "screenshot_bytes": screenshot_size
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if session:
            await session.close()
        proc.terminate()
        proc.wait()
        subprocess.getoutput(f"rm -rf {user_data}")

def main():
    parser = argparse.ArgumentParser(description="E2E CDP Headless Browser Runner")
    parser.add_argument("--url", required=True, help="URL or file:// path to verify")
    parser.add_argument("--viewport", choices=["desktop", "mobile", "tablet"], default="desktop", help="Viewport preset")
    parser.add_argument("--screenshot", help="Output file path for captured PNG screenshot")
    parser.add_argument("--eval", help="JavaScript expression to evaluate inside page")
    parser.add_argument("--no-emoji-check", action="store_true", help="Skip zero-emoji policy audit")

    args = parser.parse_args()
    res = asyncio.run(audit_url(
        url=args.url,
        viewport=args.viewport,
        screenshot_path=args.screenshot,
        check_zero_emoji=(not args.no_emoji_check),
        eval_script=args.eval
    ))
    print(json.dumps(res, indent=2))
    if not res.get("success"):
        sys.exit(1)

if __name__ == "__main__":
    main()
