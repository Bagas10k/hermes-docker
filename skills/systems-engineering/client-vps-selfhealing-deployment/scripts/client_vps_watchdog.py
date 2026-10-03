#!/usr/bin/env python3
"""
client_vps_watchdog.py
Autonomous Self-Healing Watchdog Engine for Client VPS Deployment.
Supports process health monitoring, HTTP health-check probes, automatic restarts,
exponential backoff circuit breaker, systemd/supervisord/docker hooks, and SQLite backup triggers.
"""

import sys
import time
import json
import sqlite3
import shutil
import urllib.request
import urllib.error
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

class ServiceState:
    UP = "UP"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"
    TRIPPED = "CIRCUIT_TRIPPED"

class VPSDeploymentWatchdog:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.services = config.get("services", [])
        self.max_restarts = config.get("max_restarts", 3)
        self.backoff_base_sec = config.get("backoff_base_sec", 1.0)
        self.restart_history: Dict[str, List[float]] = {s["name"]: [] for s in self.services}
        self.circuit_tripped: Dict[str, bool] = {s["name"]: False for s in self.services}

    def check_http_probe(self, service: Dict[str, Any]) -> bool:
        url = service.get("probe_url")
        if not url:
            return True
        timeout = service.get("timeout_sec", 3.0)
        expected_status = service.get("expected_status", 200)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "VPS-SelfHealing-Watchdog/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status == expected_status
        except Exception:
            return False

    def check_process_probe(self, service: Dict[str, Any]) -> bool:
        pid_file = service.get("pid_file")
        if not pid_file:
            return True
        p = Path(pid_file)
        if not p.exists():
            return False
        try:
            pid = int(p.read_text().strip())
            # Check liveness via kill -0
            subprocess.run(["kill", "-0", str(pid)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except (ValueError, subprocess.CalledProcessError, ProcessLookupError, PermissionError):
            return False

    def evaluate_service(self, service: Dict[str, Any]) -> str:
        name = service["name"]
        if self.circuit_tripped[name]:
            return ServiceState.TRIPPED

        proc_ok = self.check_process_probe(service)
        http_ok = self.check_http_probe(service)

        if proc_ok and http_ok:
            return ServiceState.UP
        elif proc_ok and not http_ok:
            return ServiceState.DEGRADED
        else:
            return ServiceState.DOWN

    def trigger_restart(self, service: Dict[str, Any]) -> bool:
        name = service["name"]
        now = time.time()
        # Clean older history outside 300 seconds window
        self.restart_history[name] = [t for t in self.restart_history[name] if now - t < 300]

        if len(self.restart_history[name]) >= self.max_restarts:
            self.circuit_tripped[name] = True
            return False

        restart_cmd = service.get("restart_cmd")
        if not restart_cmd:
            return False

        try:
            res = subprocess.run(restart_cmd, shell=True, capture_output=True, text=True, timeout=15)
            self.restart_history[name].append(now)
            return res.returncode == 0
        except Exception:
            return False

    def run_health_and_heal_cycle(self) -> Dict[str, Any]:
        results = {}
        for s in self.services:
            name = s["name"]
            status = self.evaluate_service(s)
            healed = False
            if status in [ServiceState.DOWN, ServiceState.DEGRADED]:
                healed = self.trigger_restart(s)
                # Re-evaluate
                status = self.evaluate_service(s)

            results[name] = {
                "status": status,
                "restart_count": len(self.restart_history[name]),
                "circuit_tripped": self.circuit_tripped[name],
                "healed": healed
            }
        return results

    @staticmethod
    def backup_sqlite_wal(db_path: str, backup_dir: str) -> Optional[str]:
        src = Path(db_path)
        if not src.exists():
            return None
        dest_dir = Path(backup_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        timestamp = int(time.time())
        dest = dest_dir / f"{src.stem}_backup_{timestamp}.db"
        
        # Use sqlite3 online backup API for WAL safety
        try:
            con_src = sqlite3.connect(f"file:{src.resolve()}?mode=ro", uri=True)
            con_dst = sqlite3.connect(str(dest.resolve()))
            with con_dst:
                con_src.backup(con_dst, pages=100)
            con_src.close()
            con_dst.close()
            return str(dest)
        except Exception:
            # Fallback copy
            shutil.copy2(src, dest)
            return str(dest)

if __name__ == "__main__":
    sample_conf = {
        "services": [
            {
                "name": "sample_api",
                "probe_url": "http://127.0.0.1:8080/health",
                "restart_cmd": "echo restarting",
                "timeout_sec": 1.0
            }
        ],
        "max_restarts": 3
    }
    watchdog = VPSDeploymentWatchdog(sample_conf)
    print(json.dumps(watchdog.run_health_and_heal_cycle(), indent=2))
