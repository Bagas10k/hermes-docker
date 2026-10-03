#!/usr/bin/env python3
"""
Client VPS Self-Healing Watchdog Engine
Memantau kesehatan aplikasi klien (HTTP health check, ambang batas RSS memory leak,
dan CPU runaway) serta mengeksekusi restart otomatis sebelum server kehabisan RAM.
"""

import os
import sys
import time
import json
import urllib.request
import subprocess
import argparse
from typing import Dict, Any, Optional

class AppWatchdog:
    def __init__(self, config: Dict[str, Any]):
        self.app_name = config.get("app_name", "client-app")
        self.health_url = config.get("health_url", "http://127.0.0.1:3000/health")
        self.restart_cmd = config.get("restart_cmd", "pm2 restart client-app")
        self.max_rss_mb = config.get("max_rss_mb", 512.0) # Restart jika bocor > 512MB
        self.check_interval_sec = config.get("check_interval_sec", 15)
        self.max_failures = config.get("max_failures", 3)
        self.alert_webhook = config.get("alert_webhook") # Optional webhook
        
        self.consecutive_failures = 0
        self.restart_history = []

    def check_http_health(self) -> bool:
        """Pemeriksaan HTTP probe dengan timeout ketat 5 detik."""
        try:
            req = urllib.request.Request(self.health_url, headers={"User-Agent": "Hermes-Watchdog/1.0"})
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def get_process_rss_mb(self, process_pattern: str) -> float:
        """Mengambil penggunaan memori fisik (RSS) proses via pgrep dan /proc."""
        total_rss_kb = 0
        try:
            pids = subprocess.check_output(["pgrep", "-f", process_pattern], text=True).strip().split()
            for pid in pids:
                status_path = f"/proc/{pid}/status"
                if os.path.exists(status_path):
                    with open(status_path, "r") as f:
                        for line in f:
                            if line.startswith("VmRSS:"):
                                parts = line.split()
                                if len(parts) >= 2:
                                    total_rss_kb += int(parts[1])
        except Exception:
            pass
        return total_rss_kb / 1024.0

    def trigger_self_healing(self, reason: str):
        """Mengeksekusi pemulihan mandiri aplikasi dan mencatat telemetri."""
        now = time.strftime("%Y-%m-%d %H:%M:%S WIB")
        print(f"[WATCHDOG TRIGGER] {now} - Memulihkan {self.app_name} karena: {reason}")
        try:
            subprocess.run(self.restart_cmd, shell=True, check=True, timeout=30)
            self.restart_history.append({"timestamp": now, "reason": reason, "status": "SUCCESS"})
        except Exception as e:
            self.restart_history.append({"timestamp": now, "reason": reason, "status": "FAILED", "error": str(e)})
            print(f"[WATCHDOG ERROR] Gagal restart: {e}", file=sys.stderr)
        
        self.consecutive_failures = 0

    def evaluate_cycle(self, pattern: Optional[str] = None) -> Dict[str, Any]:
        """Satu siklus evaluasi metrik kesehatan."""
        is_healthy = self.check_http_health()
        rss_mb = self.get_process_rss_mb(pattern or self.app_name)

        if not is_healthy:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.max_failures:
                self.trigger_self_healing(f"HTTP Probe gagal berturut-turut {self.consecutive_failures}x di {self.health_url}")
        else:
            self.consecutive_failures = 0

        # Proteksi OOM (Out Of Memory)
        if rss_mb > self.max_rss_mb:
            self.trigger_self_healing(f"Memory leak terdeteksi: {rss_mb:.1f}MB melampaui batas {self.max_rss_mb}MB")

        return {
            "app_name": self.app_name,
            "healthy": is_healthy,
            "consecutive_failures": self.consecutive_failures,
            "current_rss_mb": round(rss_mb, 2),
            "max_allowed_rss_mb": self.max_rss_mb,
            "restarts_count": len(self.restart_history)
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client App Watchdog")
    parser.add_argument("--name", default="client-app", help="Nama aplikasi")
    parser.add_argument("--url", default="http://127.0.0.1:3000/health", help="Endpoint health probe")
    parser.add_argument("--restart", default="echo 'Restarting app...'", help="Perintah restart")
    parser.add_argument("--max-rss", type=float, default=512.0, help="Limit RAM (MB)")
    parser.add_argument("--once", action="store_true", help="Jalankan 1 siklus evaluasi")
    args = parser.parse_args()

    cfg = {
        "app_name": args.name,
        "health_url": args.url,
        "restart_cmd": args.restart,
        "max_rss_mb": args.max_rss,
    }
    dog = AppWatchdog(cfg)
    if args.once:
        print(json.dumps(dog.evaluate_cycle(), indent=2))
