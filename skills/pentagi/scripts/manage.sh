#!/usr/bin/env bash
set -euo pipefail

COMPOSE_DIR="$HOME/.hermes/skills/pentagi"
ACTION="${1:-status}"

cd "$COMPOSE_DIR"

case "$ACTION" in
  setup)
    echo "[*] Mengunduh docker-compose.yml resmi PentAGI..."
    curl -sSL "https://raw.githubusercontent.com/vxcontrol/pentagi/main/docker-compose.yml" -o docker-compose.yml
    echo "[+] Setup selesai. File compose tersimpan di $COMPOSE_DIR/docker-compose.yml"
    ;;
  start)
    if [[ ! -f docker-compose.yml ]]; then
      "$0" setup
    fi
    echo "[*] Menjalankan PentAGI container..."
    docker compose up -d pentagi pgvector
    echo "[+] PentAGI aktif di https://127.0.0.1:8443"
    ;;
  stop)
    echo "[*] Menghentikan PentAGI (hemat RAM)..."
    docker compose down
    echo "[+] PentAGI dimatikan."
    ;;
  status)
    if docker compose ps --format json 2>/dev/null | grep -q "pentagi"; then
      docker compose ps
    else
      echo "PentAGI status: OFF (RAM aman)."
    fi
    ;;
  *)
    echo "Usage: $0 {setup|start|stop|status}"
    exit 1
    ;;
esac
