#!/usr/bin/env bash
# ERPNext sandbox on/off + link. Usage: manage.sh {start|stop|status|url|creds}
set -euo pipefail
DIR="$HOME/erpnext-sandbox"
cd "$DIR"

case "${1:-status}" in
  start)
    docker compose up -d db redis-cache redis-queue
    until docker compose ps db --format '{{.Status}}' | grep -q healthy; do sleep 2; done
    docker compose run --rm configurator
    docker compose run --rm create-site
    docker compose up -d backend websocket frontend
    # compose sering berhenti di status "Created"; paksa start.
    for c in $(docker compose ps -a --format '{{.Name}}' | grep -E 'frontend|backend|websocket'); do
      [ "$(docker inspect -f '{{.State.Running}}' "$c")" = "true" ] || docker start "$c"
    done
    pm2 restart erpnext-tunnel 2>/dev/null || \
      pm2 start "$HOME/.local/bin/run-erpnext-quicktunnel.sh" --name erpnext-tunnel --interpreter bash
    sleep 12; "$0" url
    ;;
  stop)
    docker compose down
    pm2 stop erpnext-tunnel 2>/dev/null || true
    echo "ERPNext OFF. RAM freed."
    ;;
  status)
    docker compose ps
    printf "local 8088 /login : %s\n" "$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8088/login)"
    ;;
  url)
    sleep 3
    pm2 logs erpnext-tunnel --lines 80 --nostream 2>/dev/null \
      | grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" | tail -1
    ;;
  creds)
    echo "erp user : Administrator"
    echo "erp pass : admin   (default, sandbox demo - jangan taruh data nyata)"
    ;;
  *) echo "usage: $0 {start|stop|status|url|creds}"; exit 1;;
esac
