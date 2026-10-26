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
  pack-state)
    echo "Mencadangkan memori, konfigurasi, dan profil kabinet Hermes..."
    mkdir -p data/memories data/profiles

    # 1. Salin memori root & konfigurasi utama
    if [ -d "$HOME/.hermes/memories" ]; then
      cp -r "$HOME/.hermes/memories"/* data/memories/ 2>/dev/null || true
      rm -f data/memories/*.lock 2>/dev/null || true
    fi
    if [ -f "$HOME/.hermes/config.yaml" ]; then
      cp "$HOME/.hermes/config.yaml" data/config.yaml
    fi
    if [ -f "$HOME/.hermes/SOUL.md" ]; then
      cp "$HOME/.hermes/SOUL.md" data/SOUL.md
    fi

    # 2. Salin profil kabinet (kecuali koagent, ksatest, dan profil tersembunyi)
    EXCLUDED_PROFILES="koagent ksatest .deleted"
    if [ -d "$HOME/.hermes/profiles" ]; then
      for prof_dir in "$HOME/.hermes/profiles"/*; do
        if [ -d "$prof_dir" ]; then
          prof_name="$(basename "$prof_dir")"
          case " $EXCLUDED_PROFILES " in
            *" $prof_name "*|*".*"*)
              echo "  [SKIP] Melewati profil terisolasi/khusus: $prof_name"
              ;;
            *)
              target_dir="data/profiles/$prof_name"
              mkdir -p "$target_dir"
              for item in SOUL.md profile.yaml config.yaml; do
                if [ -f "$prof_dir/$item" ]; then
                  cp "$prof_dir/$item" "$target_dir/$item"
                fi
              done
              if [ -d "$prof_dir/memories" ]; then
                mkdir -p "$target_dir/memories"
                cp -r "$prof_dir/memories"/* "$target_dir/memories/" 2>/dev/null || true
                rm -f "$target_dir/memories/"*.lock 2>/dev/null || true
              fi
              echo "  [OK] Berhasil mencadangkan profil kabinet: $prof_name"
              ;;
          esac
        fi
      done
    fi

    echo "Pencadangan state lokal dan profil kabinet ke ./data/ selesai!"
    ;;
  unpack-state)
    echo "Memulihkan memori, konfigurasi, dan profil kabinet ke sistem lokal (~/.hermes/)..."
    mkdir -p "$HOME/.hermes/memories" "$HOME/.hermes/profiles"

    # 1. Pulihkan memori root & config
    if [ -d data/memories ]; then
      cp -r data/memories/* "$HOME/.hermes/memories/" 2>/dev/null || true
    fi
    if [ -f data/config.yaml ] && [ ! -f "$HOME/.hermes/config.yaml" ]; then
      cp data/config.yaml "$HOME/.hermes/config.yaml"
      echo "  [OK] Konfigurasi utama dipulihkan ke ~/.hermes/config.yaml"
    fi
    if [ -f data/SOUL.md ] && [ ! -f "$HOME/.hermes/SOUL.md" ]; then
      cp data/SOUL.md "$HOME/.hermes/SOUL.md"
      echo "  [OK] SOUL utama dipulihkan ke ~/.hermes/SOUL.md"
    fi

    # 2. Pulihkan profil kabinet
    if [ -d data/profiles ]; then
      for prof_dir in data/profiles/*; do
        if [ -d "$prof_dir" ]; then
          prof_name="$(basename "$prof_dir")"
          target_dir="$HOME/.hermes/profiles/$prof_name"
          mkdir -p "$target_dir"
          for item in SOUL.md profile.yaml config.yaml; do
            if [ -f "$prof_dir/$item" ]; then
              cp "$prof_dir/$item" "$target_dir/$item"
            fi
          done
          if [ -d "$prof_dir/memories" ]; then
            mkdir -p "$target_dir/memories"
            cp -r "$prof_dir/memories"/* "$target_dir/memories/" 2>/dev/null || true
          fi
          echo "  [OK] Profil $prof_name berhasil dipulihkan ke ~/.hermes/profiles/$prof_name"
        fi
      done
    fi

    echo "Selesai! Seluruh profil dan memori telah terpasang di ~/.hermes/."
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
