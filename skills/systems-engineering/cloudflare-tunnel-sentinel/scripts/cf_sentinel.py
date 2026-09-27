#!/usr/bin/env python3
"""
cf_sentinel.py - Real-time Cloudflare Tunnel Health & Sentinel Inspector.
Inspects local cloudflared metrics endpoints, connection readiness, and PM2/process supervision.
"""
import sys
import json
import urllib.request
import urllib.error
import subprocess
import argparse

def inspect_ready(endpoint: str):
    url = f"http://{endpoint}/ready"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CF-Tunnel-Sentinel/1.0"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = resp.read().decode('utf-8')
            return json.loads(data)
    except Exception as e:
        return {"status": 503, "error": str(e), "readyConnections": 0}

def inspect_metrics(endpoint: str):
    url = f"http://{endpoint}/metrics"
    metrics = {
        "ha_connections": 0,
        "quic_closed": 0,
        "active_streams": 0
    }
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CF-Tunnel-Sentinel/1.0"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            for line in resp.read().decode('utf-8').splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    k, v = parts[0], parts[1]
                    if k.startswith("cloudflared_tunnel_ha_connections"):
                        metrics["ha_connections"] = int(float(v))
                    elif k.startswith("quic_client_closed_connections"):
                        metrics["quic_closed"] = int(float(v))
    except Exception as e:
        metrics["error"] = str(e)
    return metrics

def inspect_pm2():
    try:
        out = subprocess.check_output(["pm2", "jlist"], stderr=subprocess.DEVNULL)
        processes = json.loads(out)
        tunnel_procs = []
        for p in processes:
            name = p.get("name", "")
            if "cf-tunnel" in name or "cloudflared" in name:
                tunnel_procs.append({
                    "name": name,
                    "pm_id": p.get("pm_id"),
                    "status": p.get("pm2_env", {}).get("status"),
                    "restarts": p.get("pm2_env", {}).get("restart_time", 0),
                    "uptime": p.get("pm2_env", {}).get("pm_uptime"),
                    "memory_mb": round((p.get("monit", {}).get("memory", 0)) / (1024 * 1024), 2),
                    "cpu_pct": p.get("monit", {}).get("cpu", 0)
                })
        return tunnel_procs
    except Exception as e:
        return [{"error": str(e)}]

def main():
    parser = argparse.ArgumentParser(description="Cloudflare Tunnel Sentinel Inspector")
    parser.add_argument("--endpoint", default="127.0.0.1:20241", help="Metrics host:port (default: 127.0.0.1:20241)")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    ready_data = inspect_ready(args.endpoint)
    metrics_data = inspect_metrics(args.endpoint)
    pm2_data = inspect_pm2()

    report = {
        "endpoint": args.endpoint,
        "ready": ready_data,
        "metrics": metrics_data,
        "supervision": pm2_data,
        "is_healthy": (ready_data.get("status") == 200 and ready_data.get("readyConnections", 0) > 0)
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status_str = "HEALTHY" if report["is_healthy"] else "UNHEALTHY"
        print(f"Cloudflare Tunnel Sentinel [{status_str}]")
        print(f"  Endpoint: {args.endpoint}")
        print(f"  Connector ID: {ready_data.get('connectorId', 'N/A')}")
        print(f"  HA Connections: {ready_data.get('readyConnections', 0)} (Metrics HA: {metrics_data.get('ha_connections', 0)})")
        print(f"  Supervised Processes in PM2: {len(pm2_data)}")
        for p in pm2_data:
            print(f"    - {p.get('name')}: {p.get('status')} | Mem: {p.get('memory_mb')} MB | Restarts: {p.get('restarts')}")

if __name__ == "__main__":
    main()
