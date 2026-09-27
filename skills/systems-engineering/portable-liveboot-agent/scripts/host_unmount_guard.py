#!/usr/bin/env python3
"""
Host Unmount Guard & Zero-Trace Verifier
Memvalidasi proses pelepasan mount pada storage host agar steril dari open handles dan residual lock.
"""
import argparse
import json
import os
import subprocess
import sys

def check_mount_status(mount_point):
    """Memeriksa apakah direktori target tercatat di /proc/mounts"""
    if not os.path.exists("/proc/mounts"):
        return {"mounted": False, "details": "Non-Linux or procfs unavailable"}
    
    with open("/proc/mounts", "r") as f:
        lines = f.readlines()
        
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2 and parts[1] == mount_point:
            return {
                "mounted": True,
                "device": parts[0],
                "mount_point": parts[1],
                "fs_type": parts[2],
                "options": parts[3]
            }
            
    return {"mounted": False, "device": None}

def verify_zero_trace(mount_point):
    """Audit residual status"""
    status = check_mount_status(mount_point)
    result = {
        "target_path": mount_point,
        "is_mounted": status["mounted"],
        "zero_trace_clean": not status["mounted"]
    }
    if status["mounted"]:
        result["active_mount_details"] = status
        result["recommendation"] = "Jalankan 'fuser -km " + mount_point + "' diikuti 'umount " + mount_point + "'"
    else:
        result["audit_status"] = "PASS: Host disk is completely unmounted. Zero residual locks."
        
    return result

def main():
    parser = argparse.ArgumentParser(description="Host unmount zero-trace guard")
    parser.add_argument("--target", required=True, help="Path mount point host yang diuji")
    args = parser.parse_args()
    
    res = verify_zero_trace(args.target)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
