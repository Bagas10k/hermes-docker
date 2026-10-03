#!/usr/bin/env python3
"""
Enterprise Webhook & Event-Driven Automation Hub
Modul otomasi penanganan webhook bisnis dengan zero-drop queue, validasi HMAC,
idempotency guard, dan retry exponential backoff + dead-letter queue (DLQ).

Arsitektur:
1. Webhook Signature Verifier: Generic HMAC-SHA256, Meta/WhatsApp, Stripe, Midtrans.
2. Idempotency Manager: Atomic SQLite WAL deduplication.
3. Transactional Outbox/Inbox: Persist first, acknowledge fast (HTTP 200), process asynchronously.
4. Worker & Exponential Retry: Auto-retry transient failures with backoff and DLQ routing.
"""

import os
import sys
import time
import json
import hmac
import hashlib
import sqlite3
import random
import threading
from typing import Dict, Any, Optional, Tuple, Callable

DEFAULT_DB_PATH = os.path.expanduser("~/.hermes/data/webhook_hub.sqlite3")

def init_db(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Inisialisasi schema database SQLite dengan mode WAL untuk konkurensi tinggi."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS webhook_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                event_type TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                payload_raw TEXT NOT NULL,
                headers_raw TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'DEAD_LETTER')),
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 5,
                next_retry_at REAL DEFAULT 0.0,
                last_error TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                UNIQUE(provider, idempotency_key)
            );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_webhook_status_retry ON webhook_events(status, next_retry_at);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_webhook_provider_key ON webhook_events(provider, idempotency_key);")
    return conn

# -------------------------------------------------------------
# 1. Signature Verification Engines (Multi-Provider)
# -------------------------------------------------------------
class SignatureVerifier:
    @staticmethod
    def verify_hmac_sha256(payload: bytes, secret: str, signature: str) -> bool:
        """Validasi HMAC-SHA256 generik (GitHub, Shopify, standard webhooks)."""
        if not signature or not secret:
            return False
        expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        clean_sig = signature.replace("sha256=", "").strip()
        return hmac.compare_digest(expected, clean_sig)

    @staticmethod
    def verify_midtrans(order_id: str, status_code: str, gross_amount: str, server_key: str, signature: str) -> bool:
        """Validasi signature Midtrans Payment Gateway: SHA512(order_id + status_code + gross_amount + server_key)."""
        if not signature or not server_key:
            return False
        raw = f"{order_id}{status_code}{gross_amount}{server_key}"
        expected = hashlib.sha512(raw.encode("utf-8")).hexdigest()
        return hmac.compare_digest(expected, signature.strip())

    @staticmethod
    def verify_stripe(payload: bytes, secret: str, stripe_header: str, tolerance_sec: int = 300) -> bool:
        """Validasi signature Stripe Webhook: t=timestamp,v1=signature."""
        if not stripe_header or not secret:
            return False
        parts = {}
        for item in stripe_header.split(","):
            if "=" in item:
                k, v = item.split("=", 1)
                parts[k.strip()] = v.strip()
        
        timestamp = parts.get("t")
        sig_v1 = parts.get("v1")
        if not timestamp or not sig_v1:
            return False
        
        # Cek timestamp tolerance (anti-replay attack)
        try:
            ts = float(timestamp)
            if abs(time.time() - ts) > tolerance_sec:
                return False
        except ValueError:
            return False
        
        signed_payload = f"{timestamp}.".encode("utf-8") + payload
        expected = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, sig_v1)

# -------------------------------------------------------------
# 2. Transactional Ingestion & Zero-Drop Queue
# -------------------------------------------------------------
class WebhookHub:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.conn = init_db(db_path)
        self.handlers: Dict[str, Callable[[Dict[str, Any]], bool]] = {}
        self._lock = threading.Lock()

    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], bool]):
        """Daftarkan callback bisnis untuk tipe event tertentu."""
        self.handlers[event_type] = handler

    def ingest_webhook(self, provider: str, event_type: str, idempotency_key: str,
                       payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None,
                       max_attempts: int = 5) -> Tuple[bool, str, int]:
        """
        Menerima dan menyimpan event secara atomik ke antrean SQLite WAL.
        Returns: (success: bool, message: str, event_id: int)
        """
        now = time.time()
        payload_str = json.dumps(payload, separators=(',', ':'))
        headers_str = json.dumps(headers or {}, separators=(',', ':'))
        
        try:
            with self._lock:
                cur = self.conn.cursor()
                cur.execute("""
                    INSERT INTO webhook_events (
                        provider, event_type, idempotency_key, payload_raw, headers_raw,
                        status, attempts, max_attempts, next_retry_at, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 'PENDING', 0, ?, ?, ?, ?)
                """, (provider, event_type, idempotency_key, payload_str, headers_str,
                      max_attempts, now, now, now))
                self.conn.commit()
                event_id = cur.lastrowid
                return True, "EVENT_QUEUED", event_id
        except sqlite3.IntegrityError:
            # Idempotency collision: event dengan provider & key yang sama sudah ada
            cur = self.conn.cursor()
            cur.execute("SELECT id, status FROM webhook_events WHERE provider = ? AND idempotency_key = ?",
                        (provider, idempotency_key))
            row = cur.fetchone()
            existing_id = row[0] if row else -1
            status = row[1] if row else "UNKNOWN"
            return False, f"DUPLICATE_IGNORED (status: {status})", existing_id

    def process_pending_events(self, batch_size: int = 10) -> Dict[str, int]:
        """
        Mengambil batch event yang siap diproses dan mengeksekusi handler bisnis.
        Mendukung exponential backoff + jitter dan dead-letter queue (DLQ).
        """
        now = time.time()
        stats = {"processed": 0, "completed": 0, "retried": 0, "dead_lettered": 0}

        with self._lock:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT id, event_type, payload_raw, attempts, max_attempts
                FROM webhook_events
                WHERE status IN ('PENDING', 'FAILED') AND next_retry_at <= ?
                ORDER BY id ASC
                LIMIT ?
            """, (now, batch_size))
            rows = cur.fetchall()

            for event_id, event_type, payload_raw, attempts, max_attempts in rows:
                stats["processed"] += 1
                new_attempts = attempts + 1
                
                # Tandai sedang diproses
                cur.execute("UPDATE webhook_events SET status = 'PROCESSING', updated_at = ? WHERE id = ?",
                            (time.time(), event_id))
                self.conn.commit()

                # Eksekusi handler
                success = False
                error_msg = None
                try:
                    payload = json.loads(payload_raw)
                    if event_type in self.handlers:
                        success = bool(self.handlers[event_type](payload))
                    elif "*" in self.handlers:
                        success = bool(self.handlers["*"](payload))
                    else:
                        error_msg = f"No handler registered for event_type: {event_type}"
                        success = False
                except Exception as ex:
                    error_msg = str(ex)
                    success = False

                t_done = time.time()
                if success:
                    cur.execute("""
                        UPDATE webhook_events
                        SET status = 'COMPLETED', attempts = ?, last_error = NULL, updated_at = ?
                        WHERE id = ?
                    """, (new_attempts, t_done, event_id))
                    stats["completed"] += 1
                else:
                    if new_attempts >= max_attempts:
                        # Pindah ke Dead-Letter Queue
                        cur.execute("""
                            UPDATE webhook_events
                            SET status = 'DEAD_LETTER', attempts = ?, last_error = ?, updated_at = ?
                            WHERE id = ?
                        """, (new_attempts, error_msg or "Failed after max retries", t_done, event_id))
                        stats["dead_lettered"] += 1
                    else:
                        # Hitung exponential backoff dengan jitter: 2^attempt + jitter
                        backoff = (2 ** new_attempts) + random.uniform(0.1, 1.0)
                        next_retry = t_done + backoff
                        cur.execute("""
                            UPDATE webhook_events
                            SET status = 'FAILED', attempts = ?, next_retry_at = ?, last_error = ?, updated_at = ?
                            WHERE id = ?
                        """, (new_attempts, next_retry, error_msg or "Execution failed", t_done, event_id))
                        stats["retried"] += 1
                self.conn.commit()

        return stats

    def get_metrics(self) -> Dict[str, Any]:
        """Ambil metrik status antrean webhook terkini."""
        with self._lock:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT status, COUNT(*)
                FROM webhook_events
                GROUP BY status
            """)
            counts = dict(cur.fetchall())
            cur.execute("SELECT COUNT(*) FROM webhook_events")
            total = cur.fetchone()[0]
        
        return {
            "total_events": total,
            "pending": counts.get("PENDING", 0),
            "processing": counts.get("PROCESSING", 0),
            "completed": counts.get("COMPLETED", 0),
            "failed_retry_waiting": counts.get("FAILED", 0),
            "dead_letter_queue": counts.get("DEAD_LETTER", 0)
        }

if __name__ == "__main__":
    hub = WebhookHub()
    print("=== Webhook & Automation Hub Status ===")
    print(json.dumps(hub.get_metrics(), indent=2))
