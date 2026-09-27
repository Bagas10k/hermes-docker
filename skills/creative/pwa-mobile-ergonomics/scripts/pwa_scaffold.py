#!/usr/bin/env python3
"""
PWA Scaffold & Audit CLI for Tactile Mobile Ergonomics
Validates and scaffolds standalone PWA assets: manifest, sw.js, and tactile bottom sheet templates.
"""

import os
import sys
import json
import argparse
import re

MANIFEST_TEMPLATE = {
    "name": "{app_name}",
    "short_name": "{short_name}",
    "description": "Tactile Mobile Web App powered by Hermes",
    "start_url": "/",
    "scope": "/",
    "display": "standalone",
    "background_color": "#0B0A10",
    "theme_color": "#0B0A10",
    "orientation": "portrait-primary",
    "icons": [
        {
            "src": "/icons/icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable"
        },
        {
            "src": "/icons/icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable"
        }
    ]
}

SW_TEMPLATE = """// Service Worker v1.0.0 - Tactile Mobile PWA
const CACHE_NAME = 'tactile-pwa-v1';
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Network-Only for dynamic APIs, streams, websockets, and telemetry
  if (/\\/api\\/|\\/sse|\\/stream|\\/ws|\\/telemetry/.test(url.pathname)) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Cache-first for static assets with background update
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
          return networkResponse;
        }
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return networkResponse;
      }).catch(() => {
        // Fallback for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/index.html');
        }
      });
    })
  );
});
"""

def audit_pwa(target_dir):
    report = {
        "target": target_dir,
        "manifest_present": False,
        "manifest_valid": False,
        "sw_present": False,
        "sw_api_bypass": False,
        "safe_area_insets": False,
        "zero_emoji_compliant": True,
        "score": 0,
        "findings": []
    }

    manifest_path = os.path.join(target_dir, "manifest.json")
    if os.path.exists(manifest_path):
        report["manifest_present"] = True
        try:
            with open(manifest_path) as f:
                data = json.load(f)
                if data.get("display") == "standalone" and data.get("icons"):
                    report["manifest_valid"] = True
                    report["score"] += 30
                else:
                    report["findings"].append("manifest.json missing 'standalone' display or icons array.")
        except Exception as e:
            report["findings"].append(f"manifest.json parse error: {e}")
    else:
        report["findings"].append("manifest.json not found.")

    sw_path = os.path.join(target_dir, "sw.js")
    if os.path.exists(sw_path):
        report["sw_present"] = True
        with open(sw_path) as f:
            content = f.read()
            if "api" in content and ("fetch" in content or "skipWaiting" in content):
                report["sw_api_bypass"] = True
                report["score"] += 35
            else:
                report["findings"].append("sw.js lacks explicit dynamic API/stream bypass check.")
    else:
        report["findings"].append("sw.js (Service Worker) not found.")

    index_path = os.path.join(target_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path) as f:
            content = f.read()
            if "viewport-fit=cover" in content or "safe-area-inset" in content:
                report["safe_area_insets"] = True
                report["score"] += 20
            else:
                report["findings"].append("index.html missing viewport-fit=cover or safe-area-inset handling.")

            # Emoji check
            emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]')
            if emoji_pattern.search(content):
                report["zero_emoji_compliant"] = False
                report["findings"].append("index.html violates zero-emoji policy.")
            else:
                report["score"] += 15

    return report

def scaffold_pwa(target_dir, app_name):
    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(os.path.join(target_dir, "icons"), exist_ok=True)

    manifest_file = os.path.join(target_dir, "manifest.json")
    if not os.path.exists(manifest_file):
        data = dict(MANIFEST_TEMPLATE)
        data["name"] = app_name
        data["short_name"] = app_name[:12]
        with open(manifest_file, "w") as f:
            json.dump(data, f, indent=2)

    sw_file = os.path.join(target_dir, "sw.js")
    if not os.path.exists(sw_file):
        with open(sw_file, "w") as f:
            f.write(SW_TEMPLATE)

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PWA Scaffold & Audit CLI")
    parser.add_argument("--audit", help="Directory path to audit PWA compliance")
    parser.add_argument("--scaffold", help="Directory path to scaffold PWA assets")
    parser.add_argument("--app-name", default="Tactile Mobile App", help="Application name for manifest")

    args = parser.parse_args()
    if args.audit:
        res = audit_pwa(args.audit)
        print(json.dumps(res, indent=2))
    elif args.scaffold:
        scaffold_pwa(args.scaffold, args.app_name)
        print(f"PWA assets successfully scaffolded in: {args.scaffold}")
    else:
        parser.print_help()
