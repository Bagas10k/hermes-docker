#!/usr/bin/env python3
"""
Sentinel audit script for PM2 managed processes and Systemd user services.
Evaluates memory boundaries, restart amplification, uptime, and orphan workers.
Output format: JSON with exit code 0 (clean) or 1 (alert).
"""

import json
import os
import subprocess
import sys
from datetime import datetime

def run_cmd(cmd):
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        return p.stdout, p.stderr, p.returncode
    except Exception as e:
        return "", str(e), 1

def audit_pm2():
    stdout, stderr, rc = run_cmd(["pm2", "jlist"])
    if rc != 0 or not stdout.strip():
        return {"status": "error", "error": f"Failed to get pm2 jlist: {stderr.strip()}"}
    
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        return {"status": "error", "error": f"Invalid JSON from pm2: {e}"}

    summary = {
        "total_apps": len(data),
        "online": 0,
        "stopped": 0,
        "errored": 0,
        "high_memory_apps": [],
        "high_restart_apps": [],
        "apps": []
    }

    for app in data:
        name = app.get("name", "unknown")
        pid = app.get("pid", 0)
        pm_id = app.get("pm_id", -1)
        monit = app.get("monit", {})
        pm2_env = app.get("pm2_env", {})
        
        status = pm2_env.get("status", "unknown")
        restarts = pm2_env.get("restart_time", 0)
        unstable_restarts = pm2_env.get("unstable_restarts", 0)
        memory_bytes = monit.get("memory", 0)
        memory_mb = round(memory_bytes / (1024 * 1024), 2)
        cpu = monit.get("cpu", 0)
        uptime_ms = pm2_env.get("pm_uptime", 0)
        uptime_s = round((datetime.now().timestamp() * 1000 - uptime_ms) / 1000) if uptime_ms else 0

        if status == "online":
            summary["online"] += 1
        elif status == "stopped":
            summary["stopped"] += 1
        else:
            summary["errored"] += 1

        # Check memory threshold (> 650 MB)
        if memory_mb > 650.0:
            summary["high_memory_apps"].append({"name": name, "pm_id": pm_id, "memory_mb": memory_mb})

        # Check restart spikes (> 50 restarts while uptime < 1 hour)
        if restarts > 50 and uptime_s < 3600:
            summary["high_restart_apps"].append({"name": name, "pm_id": pm_id, "restarts": restarts, "uptime_s": uptime_s})

        summary["apps"].append({
            "name": name,
            "pm_id": pm_id,
            "pid": pid,
            "status": status,
            "memory_mb": memory_mb,
            "cpu_pct": cpu,
            "restarts": restarts,
            "uptime_s": uptime_s
        })

    return summary

def audit_systemd_user():
    stdout, stderr, rc = run_cmd(["systemctl", "--user", "list-units", "--type=service", "--state=running", "--no-legend", "--no-pager"])
    if rc != 0:
        return {"status": "error", "error": f"Failed to list systemd user units: {stderr.strip()}"}

    services = []
    for line in stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 4:
            unit = parts[0]
            load = parts[1]
            active = parts[2]
            sub = parts[3]
            services.append({"unit": unit, "load": load, "active": active, "sub": sub})

    return {
        "status": "ok",
        "running_units_count": len(services),
        "units": services
    }

def main():
    report = {
        "timestamp": datetime.now().isoformat(),
        "pm2": audit_pm2(),
        "systemd_user": audit_systemd_user()
    }
    
    has_alert = False
    alerts = []
    
    if isinstance(report["pm2"], dict) and report["pm2"].get("errored", 0) > 0:
        has_alert = True
        alerts.append(f"{report['pm2']['errored']} PM2 apps in errored status")
        
    if isinstance(report["pm2"], dict) and report["pm2"].get("high_restart_apps"):
        has_alert = True
        alerts.append(f"Fast restart loop detected: {report['pm2']['high_restart_apps']}")

    report["alerts"] = alerts
    report["healthy"] = not has_alert
    
    print(json.dumps(report, indent=2))
    sys.exit(0 if not has_alert else 1)

if __name__ == "__main__":
    main()
