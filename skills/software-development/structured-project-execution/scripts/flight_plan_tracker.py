#!/usr/bin/env python3
"""
Structured Flight Plan & DAG Milestone Tracker.
Persists execution state across long-horizon sessions to prevent context drift and amnesia.
"""

import sys
import os
import argparse
import json
import time

TRACKER_FILE = "build_tracker.json"

def load_tracker(path=TRACKER_FILE):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}", file=sys.stderr)
    return None

def save_tracker(data, path=TRACKER_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def init_tracker(name, stages, path=TRACKER_FILE):
    data = {
        "project": name,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "phase": 1,
        "vibe": None,
        "stages": []
    }
    for idx, s in enumerate(stages):
        data["stages"].append({
            "id": idx + 1,
            "name": s,
            "status": "pending", # pending, in_progress, completed, failed
            "started_at": None,
            "completed_at": None,
            "proof": None
        })
    save_tracker(data, path)
    print(f"Initialized flight plan tracker '{name}' with {len(stages)} stages in {path}")
    render_tracker(data)

def update_stage(stage_id, status, proof=None, path=TRACKER_FILE):
    data = load_tracker(path)
    if not data:
        print(f"No tracker file found at {path}. Run --init first.", file=sys.stderr)
        sys.exit(1)

    found = False
    for s in data["stages"]:
        if s["id"] == stage_id:
            s["status"] = status
            s["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            if status == "in_progress" and not s.get("started_at"):
                s["started_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            elif status == "completed":
                s["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                if proof:
                    s["proof"] = proof
            found = True
            break

    if not found:
        print(f"Stage ID {stage_id} not found.", file=sys.stderr)
        sys.exit(1)

    data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_tracker(data, path)
    print(f"Updated stage {stage_id} to '{status}'")
    render_tracker(data)

def set_vibe(vibe_name, path=TRACKER_FILE):
    data = load_tracker(path)
    if not data:
        print("No tracker file found.", file=sys.stderr)
        sys.exit(1)
    data["vibe"] = vibe_name
    data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_tracker(data, path)
    print(f"Confirmed project visual vibe: '{vibe_name}'")

def render_tracker(data):
    print("\n" + "═" * 60)
    print(f" 🛫 FLIGHT PLAN DAG: {data['project']}")
    if data.get("vibe"):
        print(f" Visual Vibe: {data['vibe']}")
    print("═" * 60)
    for s in data["stages"]:
        icon = "⏳"
        if s["status"] == "in_progress":
            icon = "🔄"
        elif s["status"] == "completed":
            icon = "✅"
        elif s["status"] == "failed":
            icon = "❌"
        proof_text = f" -> Proof: {s['proof']}" if s.get("proof") else ""
        print(f" {icon} Step {s['id']}: {s['name']} [{s['status'].upper()}]{proof_text}")
    print("═" * 60 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Structured Project Execution Tracker")
    parser.add_argument("--init", help="Initialize tracker with project name")
    parser.add_argument("--stages", nargs="+", help="List of stage names for init")
    parser.add_argument("--status", action="store_true", help="Display current flight plan status")
    parser.add_argument("--set-stage", type=int, help="Stage ID to update")
    parser.add_argument("--state", choices=["pending", "in_progress", "completed", "failed"], help="New stage state")
    parser.add_argument("--proof", help="Verification proof (e.g. 'HTTP 200', 'Exit code 0')")
    parser.add_argument("--vibe", help="Set confirmed aesthetic vibe")
    parser.add_argument("--file", default=TRACKER_FILE, help="Path to tracker json (default: build_tracker.json)")

    args = parser.parse_args()

    if args.init:
        stages = args.stages or [
            "Fase 1: Discovery & Audit Port/DB",
            "Fase 1: Setup Skema Database & Model",
            "Fase 1: Implementasi API CRUD & Wireframe Grid",
            "Checkpoint: Konfirmasi Vibe Visual dengan User",
            "Fase 2: Pematangan Style Upnormal (Live Search + 5 Lensa)",
            "Fase 2: Verifikasi E2E & Rilis"
        ]
        init_tracker(args.init, stages, args.file)
    elif args.set_stage:
        if not args.state:
            print("Must specify --state with --set-stage", file=sys.stderr)
            sys.exit(1)
        update_stage(args.set_stage, args.state, args.proof, args.file)
    elif args.vibe:
        set_vibe(args.vibe, args.file)
    elif args.status or len(sys.argv) == 1:
        data = load_tracker(args.file)
        if data:
            render_tracker(data)
        else:
            print(f"No active tracker found at {args.file}. Run with --init <project_name>.")

if __name__ == "__main__":
    main()
