#!/usr/bin/env python3
"""
Live-Boot RAM-Disk Footprint & Capacity Calculator
Memverifikasi batas matematis alokasi memori sistem live boot (budget <= 400 MB).
"""
import argparse
import json
import sys

PROFILES = {
    "minimal": {
        "kernel_mb": 32,
        "squashfs_mb": 95,
        "overlayfs_scratch_mb": 64,
        "agent_runtime_mb": 160,
        "max_ram_budget_mb": 400
    },
    "standard": {
        "kernel_mb": 42,
        "squashfs_mb": 140,
        "overlayfs_scratch_mb": 96,
        "agent_runtime_mb": 220,
        "max_ram_budget_mb": 512
    }
}

def evaluate_footprint(profile_name):
    if profile_name not in PROFILES:
        raise ValueError(f"Profil tidak dikenal: {profile_name}")
    
    cfg = PROFILES[profile_name]
    total_used = (
        cfg["kernel_mb"] +
        cfg["squashfs_mb"] +
        cfg["overlayfs_scratch_mb"] +
        cfg["agent_runtime_mb"]
    )
    
    headroom = cfg["max_ram_budget_mb"] - total_used
    is_compliant = total_used <= cfg["max_ram_budget_mb"]
    
    result = {
        "profile": profile_name,
        "components": {
            "kernel_and_drivers": f"{cfg['kernel_mb']} MB",
            "squashfs_compressed_rootfs": f"{cfg['squashfs_mb']} MB",
            "overlayfs_cow_scratchpad": f"{cfg['overlayfs_scratch_mb']} MB",
            "agent_micro_runtime": f"{cfg['agent_runtime_mb']} MB"
        },
        "total_ram_used_mb": total_used,
        "ram_budget_limit_mb": cfg["max_ram_budget_mb"],
        "headroom_mb": headroom,
        "compliant": is_compliant
    }
    return result

def main():
    parser = argparse.ArgumentParser(description="Live-boot RAM footprint evaluator")
    parser.add_argument("--profile", default="minimal", choices=["minimal", "standard"])
    args = parser.parse_args()
    
    res = evaluate_footprint(args.profile)
    print(json.dumps(res, indent=2))
    if not res["compliant"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
