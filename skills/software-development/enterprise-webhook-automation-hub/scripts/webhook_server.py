#!/usr/bin/env python3
"""
Enterprise Webhook Server & Ingestion Gateway
HTTP Server mandiri untuk menerima, memvalidasi signature, dan memasukkan webhook
ke antrean SQLite WAL zero-drop.
"""

import os
import sys
import json
import time
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import engine hub
sys.path.insert(0, os.path.dirname(__file__))
from webhook_hub import WebhookHub, SignatureVerifier, DEFAULT_DB_PATH

class WebhookHTTPHandler(BaseHTTPRequestHandler):
    hub: WebhookHub = None
    secrets: dict = {}

    def log_message(self, format, *args):
        # Silence default noisy stderr logging
        pass

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/metrics" or self.path == "/health":
            metrics = self.hub.get_metrics()
            self._send_json(200, {"status": "healthy", "metrics": metrics})
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0 or content_len > 10 * 1024 * 1024: # Limit 10MB
            self._send_json(400, {"error": "Invalid Content-Length"})
            return

        body_bytes = self.rfile.read(content_len)

        # Routing: /webhook/<provider>
        parts = self.path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "webhook":
            provider = parts[1]
            secret = self.secrets.get(provider, "")
            
            # Signature check jika secret dikonfigurasi
            if secret:
                sig_header = self.headers.get("X-Hub-Signature-256") or self.headers.get("X-Signature")
                if sig_header:
                    if not SignatureVerifier.verify_hmac_sha256(body_bytes, secret, sig_header):
                        self._send_json(401, {"error": "Invalid HMAC signature"})
                        return

            try:
                payload = json.loads(body_bytes.decode("utf-8"))
            except Exception as e:
                self._send_json(400, {"error": f"Invalid JSON payload: {e}"})
                return

            event_type = payload.get("event") or payload.get("type") or "generic.event"
            idempotency_key = (
                self.headers.get("X-Idempotency-Key") or
                payload.get("idempotency_key") or
                payload.get("id") or
                f"auto_{int(time.time() * 1000)}"
            )

            headers_dict = {k: v for k, v in self.headers.items()}
            ok, msg, event_id = self.hub.ingest_webhook(
                provider=provider,
                event_type=event_type,
                idempotency_key=str(idempotency_key),
                payload=payload,
                headers=headers_dict
            )

            if ok:
                self._send_json(200, {"ok": True, "message": msg, "event_id": event_id})
            else:
                # Duplikat diabaikan tapi tetap return HTTP 200 agar provider tidak terus me-retry
                self._send_json(200, {"ok": False, "message": msg, "event_id": event_id})
        
        elif self.path == "/retry-dlq":
            # Reset dead-letter items
            cur = self.hub.conn.cursor()
            cur.execute("UPDATE webhook_events SET status = 'PENDING', attempts = 0, next_retry_at = ? WHERE status = 'DEAD_LETTER'", (time.time(),))
            self.hub.conn.commit()
            count = cur.rowcount
            self._send_json(200, {"ok": True, "requeued_count": count})
        else:
            self._send_json(404, {"error": "Not Found"})

def run_server(port: int = 8085, db_path: str = DEFAULT_DB_PATH):
    hub = WebhookHub(db_path=db_path)
    WebhookHTTPHandler.hub = hub
    # Baca secrets jika ada di env
    WebhookHTTPHandler.secrets = {
        "whatsapp": os.environ.get("WHATSAPP_WEBHOOK_SECRET", ""),
        "stripe": os.environ.get("STRIPE_WEBHOOK_SECRET", ""),
        "midtrans": os.environ.get("MIDTRANS_SERVER_KEY", ""),
        "github": os.environ.get("GITHUB_WEBHOOK_SECRET", "")
    }

    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, WebhookHTTPHandler)
    print(f"[Webhook Gateway] Aktif mendengarkan di http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enterprise Webhook Server")
    parser.add_argument("--port", type=int, default=8085, help="Port HTTP (default: 8085)")
    parser.add_argument("--db", type=str, default=DEFAULT_DB_PATH, help="Path SQLite DB")
    args = parser.parse_args()
    run_server(port=args.port, db_path=args.db)
