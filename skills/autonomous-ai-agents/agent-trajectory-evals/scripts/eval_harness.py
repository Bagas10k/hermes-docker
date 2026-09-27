#!/usr/bin/env python3
import json
import argparse
import sys

def audit_trajectory(data):
    steps = data.get("steps", [])
    total_steps = len(steps)
    failed_steps = []
    
    for idx, step in enumerate(steps):
        tool = step.get("tool")
        status = step.get("status", "unknown")
        duration_ms = step.get("duration_ms", 0)
        
        if status in ("failed", "error") or step.get("exit_code", 0) != 0:
            failed_steps.append({
                "step_index": idx,
                "tool": tool,
                "error": step.get("error", "Non-zero exit code or failed status")
            })
            
    is_success = len(failed_steps) == 0 and data.get("outcome_verified", False)
    return {
        "trajectory_id": data.get("id", "unknown"),
        "total_steps": total_steps,
        "failed_steps_count": len(failed_steps),
        "first_failure": failed_steps[0] if failed_steps else None,
        "outcome_verified": data.get("outcome_verified", False),
        "success": is_success
    }

def main():
    parser = argparse.ArgumentParser(description="Harness Audit Trajektori Agen")
    parser.add_argument("--trajectory", type=str, required=True, help="Path ke file trajectory JSON")
    args = parser.parse_args()
    
    try:
        with open(args.trajectory, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Gagal membaca berkas: {e}", file=sys.stderr)
        sys.exit(1)
        
    result = audit_trajectory(data)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
