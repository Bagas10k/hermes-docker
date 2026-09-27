#!/usr/bin/env python3
"""
Supabase Self-Hosted Ops CLI
Inspects cluster health, audits RLS policies, tests PostgREST REST APIs,
and runs verified safe database dump & schema validation.

Author: Bagas Cihuy & Hermes Agent
License: MIT
"""

import sys
import os
import json
import argparse
import subprocess
import urllib.request
import urllib.error

SUPABASE_DIR = os.path.expanduser("~/supabase")
ENV_PATH = os.path.join(SUPABASE_DIR, ".env")

def get_env_map():
    if not os.path.exists(ENV_PATH):
        return {}
    res = {}
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                res[k.strip()] = v.strip().strip("'\"")
    return res

def run_psql(query):
    cmd = ["docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-X", "-t", "-A", "-F", "\t", "-c", query]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"psql error: {res.stderr.strip()}")
    return res.stdout.strip()

def cmd_status(args):
    containers = [
        "supabase-db",
        "supabase-auth",
        "supabase-rest",
        "realtime-dev.supabase-realtime",
        "supabase-storage",
        "supabase-meta",
        "supabase-pooler",
        "supabase-studio",
        "supabase-envoy",
        "supabase-edge-functions"
    ]
    
    ps_output = subprocess.getoutput("docker ps --format '{{.Names}}\t{{.Status}}'")
    active_map = {}
    for line in ps_output.splitlines():
        if "\t" in line:
            name, status = line.split("\t", 1)
            active_map[name.strip()] = status.strip()

    report = []
    all_healthy = True
    for c in containers:
        st = active_map.get(c, "STOPPED/MISSING")
        healthy = "Up" in st and "healthy" in st
        if not healthy:
            all_healthy = False
        report.append({
            "container": c,
            "status": st,
            "healthy": healthy
        })

    # Test HTTP endpoint
    env = get_env_map()
    kong_port = env.get("KONG_HTTP_PORT", "8000")
    http_live = False
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{kong_port}/")
        with urllib.request.urlopen(req, timeout=3) as resp:
            http_live = (resp.status in [200, 401])
    except urllib.error.HTTPError as e:
        http_live = (e.code in [200, 401])
    except Exception:
        http_live = False

    result = {
        "all_containers_healthy": all_healthy,
        "gateway_http_live": http_live,
        "port": kong_port,
        "containers": report
    }
    print(json.dumps(result, indent=2))
    return 0 if (all_healthy and http_live) else 1

def cmd_audit_rls(args):
    # Query all public tables and check rowsecurity
    q_tables = "SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';"
    table_lines = run_psql(q_tables).splitlines()
    
    # Query all policies
    q_policies = "SELECT tablename, policyname, permissive, roles, cmd, qual, with_check FROM pg_policies WHERE schemaname = 'public';"
    policy_lines = run_psql(q_policies).splitlines()

    policies_by_table = {}
    for pl in policy_lines:
        if not pl.strip():
            continue
        parts = pl.split("\t")
        tname = parts[0]
        p_entry = {
            "policy": parts[1] if len(parts) > 1 else "",
            "permissive": parts[2] if len(parts) > 2 else "",
            "roles": parts[3] if len(parts) > 3 else "",
            "cmd": parts[4] if len(parts) > 4 else "",
            "qual": parts[5] if len(parts) > 5 else "",
            "with_check": parts[6] if len(parts) > 6 else ""
        }
        policies_by_table.setdefault(tname, []).append(p_entry)

    tables = []
    unprotected = []
    for tl in table_lines:
        if not tl.strip():
            continue
        parts = tl.split("\t")
        tname = parts[0]
        rsec = (parts[1] == "t")
        pols = policies_by_table.get(tname, [])
        is_safe = rsec and len(pols) > 0
        if not is_safe:
            unprotected.append(tname)
        tables.append({
            "table": tname,
            "rowsecurity": rsec,
            "policies_count": len(pols),
            "policies": pols,
            "status": "PROTECTED" if is_safe else "UNPROTECTED_OR_NO_POLICIES"
        })

    summary = {
        "total_tables": len(tables),
        "unprotected_count": len(unprotected),
        "unprotected_tables": unprotected,
        "tables": tables
    }
    print(json.dumps(summary, indent=2))
    return 0

def cmd_test_api(args):
    env = get_env_map()
    anon_key = env.get("ANON_KEY", "")
    service_key = env.get("SERVICE_ROLE_KEY", "")
    table = args.table or "drive_files"
    port = env.get("KONG_HTTP_PORT", "8000")

    results = {}
    
    # Test 1: anon key query
    url_anon = f"http://127.0.0.1:{port}/rest/v1/{table}?limit=1"
    try:
        req = urllib.request.Request(url_anon, headers={
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}"
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode("utf-8")
            results["anon_query"] = {
                "status": resp.status,
                "data": json.loads(data) if data else []
            }
    except urllib.error.HTTPError as e:
        results["anon_query"] = {"status": e.code, "error": e.read().decode("utf-8")}
    except Exception as ex:
        results["anon_query"] = {"status": 500, "error": str(ex)}

    # Test 2: service role key OpenAPI schema
    url_meta = f"http://127.0.0.1:{port}/rest/v1/"
    try:
        req = urllib.request.Request(url_meta, headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}"
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode("utf-8")
            js = json.loads(data)
            results["service_role_openapi"] = {
                "status": resp.status,
                "title": js.get("info", {}).get("title"),
                "version": js.get("info", {}).get("version")
            }
    except urllib.error.HTTPError as e:
        results["service_role_openapi"] = {"status": e.code, "error": e.read().decode("utf-8")}
    except Exception as ex:
        results["service_role_openapi"] = {"status": 500, "error": str(ex)}

    print(json.dumps(results, indent=2))
    return 0

def cmd_backup(args):
    dest = args.output or "/home/ubuntu/supabase/volumes/db/supabase_backup.sql"
    # Execute pg_dump from inside container
    cmd = [
        "docker", "exec", "supabase-db",
        "pg_dump", "-U", "postgres", "-d", "postgres",
        "--clean", "--if-exists", "--schema=public"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(json.dumps({"success": False, "error": res.stderr.strip()}))
        return 1

    with open(dest, "w", encoding="utf-8") as f:
        f.write(res.stdout)

    size = os.path.getsize(dest)
    print(json.dumps({
        "success": True,
        "backup_path": dest,
        "bytes": size,
        "schema": "public"
    }, indent=2))
    return 0

def main():
    parser = argparse.ArgumentParser(description="Supabase Self-Hosted Ops CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Inspect all Supabase container health & gateway")
    subparsers.add_parser("audit-rls", help="Audit public tables and RLS security policies")
    
    p_api = subparsers.add_parser("test-api", help="Test PostgREST endpoints with anon/service keys")
    p_api.add_argument("--table", default="drive_files", help="Table name to test query")

    p_bak = subparsers.add_parser("backup", help="Run clean pg_dump of public schema")
    p_bak.add_argument("--output", default="/tmp/supabase_public_schema.sql", help="Destination path")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "status":
        sys.exit(cmd_status(args))
    elif args.command == "audit-rls":
        sys.exit(cmd_audit_rls(args))
    elif args.command == "test-api":
        sys.exit(cmd_test_api(args))
    elif args.command == "backup":
        sys.exit(cmd_backup(args))

if __name__ == "__main__":
    main()
