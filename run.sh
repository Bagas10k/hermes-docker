#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

case "$1" in
  init)
    mkdir -p data workspace
    touch workspace/.gitkeep
    if [ ! -f .env ]; then
      cp .env.example .env
      echo "File .env berhasil dibuat dari template. Silakan sesuaikan token/kunci Anda."
    else
      echo "File .env sudah ada."
    fi
    ;;
  build)
    docker compose build
    ;;
  start)
    mkdir -p data workspace
    docker compose up -d
    echo "Hermes Agent Docker berhasil dijalankan!"
    echo "Dashboard Web: http://localhost:9119"
    echo "API Server: http://localhost:8642"
    ;;
  stop)
    docker compose down
    echo "Hermes Agent Docker berhasil dihentikan."
    ;;
  restart)
    docker compose restart
    echo "Hermes Agent Docker direstart."
    ;;
  logs)
    docker compose logs -f
    ;;
  cli)
    docker compose exec -it hermes hermes
    ;;
  export)
    echo "Mengekspor image hermes-cihuy ke hermes-bundle.tar..."
    docker save -o hermes-bundle.tar hermes-cihuy:latest
    echo "Selesai! Berkas tersimpan di hermes-bundle.tar"
    ;;
  *)
    echo "Penggunaan: ./run.sh {init|build|start|stop|restart|logs|cli|export}"
    exit 1
    ;;
esac
