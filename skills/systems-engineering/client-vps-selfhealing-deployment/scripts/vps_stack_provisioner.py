#!/usr/bin/env python3
"""
vps_stack_provisioner.py
Automated 1-Click Provisioning for Client VPS.
Generates Docker Compose, Nginx reverse proxy configs, Cloudflare Tunnel ingress configurations,
and systemd watchdog unit definitions.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class VPSStackProvisioner:
    def __init__(self, target_dir: str, app_name: str, domain: str, port: int):
        self.target_dir = Path(target_dir)
        self.app_name = app_name
        self.domain = domain
        self.port = port
        self.target_dir.mkdir(parents=True, exist_ok=True)

    def generate_docker_compose(self, runtime: str = "node") -> str:
        compose_content = f"""version: '3.8'

services:
  {self.app_name}:
    build: .
    container_name: {self.app_name}_app
    restart: unless-stopped
    ports:
      - "127.0.0.1:{self.port}:{self.port}"
    environment:
      - NODE_ENV=production
      - PORT={self.port}
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:{self.port}/health || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    volumes:
      - ./data:/app/data
"""
        compose_file = self.target_dir / "docker-compose.yml"
        compose_file.write_text(compose_content)
        return str(compose_file)

    def generate_nginx_conf(self) -> str:
        nginx_conf = f"""server {{
    listen 80;
    server_name {self.domain};

    client_max_body_size 50M;

    location / {{
        proxy_pass http://127.0.0.1:{self.port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }}

    location /health {{
        proxy_pass http://127.0.0.1:{self.port}/health;
        proxy_intercept_errors on;
    }}
}}
"""
        conf_file = self.target_dir / f"{self.app_name}_nginx.conf"
        conf_file.write_text(nginx_conf)
        return str(conf_file)

    def generate_cloudflare_tunnel_yaml(self, tunnel_id: str = "auto-tunnel-id") -> str:
        tunnel_yaml = f"""tunnel: {tunnel_id}
credentials-file: /etc/cloudflared/{tunnel_id}.json

ingress:
  - hostname: {self.domain}
    service: http://127.0.0.1:{self.port}
  - service: http_status:404
"""
        tunnel_file = self.target_dir / "tunnel.yml"
        tunnel_file.write_text(tunnel_yaml)
        return str(tunnel_file)

    def generate_systemd_watchdog_service(self) -> str:
        service_unit = f"""[Unit]
Description=Self-Healing Watchdog for {self.app_name}
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={self.target_dir.resolve()}
ExecStart=/usr/bin/python3 {self.target_dir.resolve()}/watchdog.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        unit_file = self.target_dir / f"{self.app_name}-watchdog.service"
        unit_file.write_text(service_unit)
        return str(unit_file)

if __name__ == "__main__":
    prov = VPSStackProvisioner("/tmp/vps_test_provision", "demoapp", "demo.example.com", 3000)
    print("Compose:", prov.generate_docker_compose())
    print("Nginx:", prov.generate_nginx_conf())
    print("Tunnel:", prov.generate_cloudflare_tunnel_yaml())
    print("Systemd:", prov.generate_systemd_watchdog_service())
