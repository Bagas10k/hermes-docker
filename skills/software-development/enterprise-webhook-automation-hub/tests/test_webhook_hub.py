#!/usr/bin/env python3
"""
Test Suite for Enterprise Webhook & Automation Hub
Memverifikasi:
1. Validasi cryptographic signatures (HMAC-SHA256, Midtrans SHA512, Stripe).
2. Idempotency guard (deduplikasi event ganda).
3. Transisi state antrean zero-drop (PENDING -> PROCESSING -> COMPLETED).
4. Exponential backoff retry & Dead-Letter Queue (DLQ).
5. Konkurensi ingestion multithreaded tanpa lost updates di SQLite WAL.
"""

import os
import sys
import time
import hmac
import hashlib
import unittest
import threading
import tempfile
import shutil

# Tambahkan path scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))
from webhook_hub import WebhookHub, SignatureVerifier

class TestWebhookHub(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_webhook.sqlite3")
        self.hub = WebhookHub(db_path=self.db_path)

    def tearDown(self):
        self.hub.conn.close()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ---------------------------------------------------------
    # 1. Test Signature Verification
    # ---------------------------------------------------------
    def test_hmac_sha256_verification(self):
        secret = "client_webhook_secret_key_12345"
        payload = b'{"event":"order.created","amount":150000}'
        sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

        # Valid signature
        self.assertTrue(SignatureVerifier.verify_hmac_sha256(payload, secret, sig))
        self.assertTrue(SignatureVerifier.verify_hmac_sha256(payload, secret, f"sha256={sig}"))

        # Invalid signature / tampered payload
        tampered = b'{"event":"order.created","amount":50000}'
        self.assertFalse(SignatureVerifier.verify_hmac_sha256(tampered, secret, sig))
        self.assertFalse(SignatureVerifier.verify_hmac_sha256(payload, "wrong_secret", sig))

    def test_midtrans_signature_verification(self):
        order_id = "ORDER-2026-001"
        status_code = "200"
        gross_amount = "250000.00"
        server_key = "SB-Mid-server-TESTKEY"
        
        raw = f"{order_id}{status_code}{gross_amount}{server_key}"
        valid_sig = hashlib.sha512(raw.encode("utf-8")).hexdigest()

        self.assertTrue(SignatureVerifier.verify_midtrans(order_id, status_code, gross_amount, server_key, valid_sig))
        self.assertFalse(SignatureVerifier.verify_midtrans(order_id, status_code, gross_amount, server_key, "invalidsig"))

    def test_stripe_signature_verification(self):
        secret = "whsec_test_secret_stripe"
        payload = b'{"id":"evt_123","type":"payment_intent.succeeded"}'
        ts = str(int(time.time()))
        signed = f"{ts}.".encode("utf-8") + payload
        sig_v1 = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
        header = f"t={ts},v1={sig_v1}"

        self.assertTrue(SignatureVerifier.verify_stripe(payload, secret, header))
        
        # Expired timestamp (replay attack simulation)
        old_ts = str(int(time.time()) - 400)
        old_signed = f"{old_ts}.".encode("utf-8") + payload
        old_sig = hmac.new(secret.encode("utf-8"), old_signed, hashlib.sha256).hexdigest()
        self.assertFalse(SignatureVerifier.verify_stripe(payload, secret, f"t={old_ts},v1={old_sig}", tolerance_sec=300))

    # ---------------------------------------------------------
    # 2. Test Ingestion & Idempotency Guard
    # ---------------------------------------------------------
    def test_idempotency_deduplication(self):
        provider = "whatsapp_meta"
        event_type = "message.received"
        key = "msg_wam_id_998877"
        payload = {"from": "6282185504003", "text": "Halo, saya butuh penawaran otomasi"}

        # Ingestion pertama: harus sukses
        ok1, msg1, id1 = self.hub.ingest_webhook(provider, event_type, key, payload)
        self.assertTrue(ok1)
        self.assertEqual(msg1, "EVENT_QUEUED")
        self.assertGreater(id1, 0)

        # Ingestion kedua dengan key yang sama (duplikat): harus diabaikan secara aman
        ok2, msg2, id2 = self.hub.ingest_webhook(provider, event_type, key, payload)
        self.assertFalse(ok2)
        self.assertIn("DUPLICATE_IGNORED", msg2)
        self.assertEqual(id2, id1) # Mengembalikan event ID yang sama

    # ---------------------------------------------------------
    # 3. Test Processing & State Transitions
    # ---------------------------------------------------------
    def test_successful_event_dispatch(self):
        processed_orders = []
        def order_handler(payload):
            processed_orders.append(payload["order_id"])
            return True

        self.hub.register_handler("order.paid", order_handler)

        self.hub.ingest_webhook("midtrans", "order.paid", "inv_001", {"order_id": "ORD-101", "total": 500000})
        self.hub.ingest_webhook("midtrans", "order.paid", "inv_002", {"order_id": "ORD-102", "total": 750000})

        stats = self.hub.process_pending_events(batch_size=10)
        self.assertEqual(stats["processed"], 2)
        self.assertEqual(stats["completed"], 2)
        self.assertEqual(processed_orders, ["ORD-101", "ORD-102"])

        metrics = self.hub.get_metrics()
        self.assertEqual(metrics["completed"], 2)
        self.assertEqual(metrics["pending"], 0)

    # ---------------------------------------------------------
    # 4. Test Exponential Backoff & Dead-Letter Queue (DLQ)
    # ---------------------------------------------------------
    def test_retry_and_dead_letter_queue(self):
        attempt_counter = [0]
        def flaky_handler(payload):
            attempt_counter[0] += 1
            # Selalu gagal
            raise ConnectionError("CRM API down (503 Service Unavailable)")

        self.hub.register_handler("crm.sync", flaky_handler)

        # Ingest event dengan max_attempts = 2
        ok, _, event_id = self.hub.ingest_webhook("hubspot", "crm.sync", "lead_8899", {"lead": "Bagas"}, max_attempts=2)
        self.assertTrue(ok)

        # Attempt 1: harus gagal dan masuk status FAILED (menunggu retry)
        stats1 = self.hub.process_pending_events(batch_size=1)
        self.assertEqual(stats1["processed"], 1)
        self.assertEqual(stats1["retried"], 1)
        
        # Cek database status
        cur = self.hub.conn.cursor()
        cur.execute("SELECT status, attempts FROM webhook_events WHERE id = ?", (event_id,))
        status, attempts = cur.fetchone()
        self.assertEqual(status, "FAILED")
        self.assertEqual(attempts, 1)

        # Simulasikan waktu berlalu melampaui retry_at
        cur.execute("UPDATE webhook_events SET next_retry_at = 0 WHERE id = ?", (event_id,))
        self.hub.conn.commit()

        # Attempt 2: melampaui max_attempts (2) -> harus masuk DEAD_LETTER
        stats2 = self.hub.process_pending_events(batch_size=1)
        self.assertEqual(stats2["processed"], 1)
        self.assertEqual(stats2["dead_lettered"], 1)

        cur.execute("SELECT status, attempts, last_error FROM webhook_events WHERE id = ?", (event_id,))
        status, attempts, err = cur.fetchone()
        self.assertEqual(status, "DEAD_LETTER")
        self.assertEqual(attempts, 2)
        self.assertIn("CRM API down", err)

    # ---------------------------------------------------------
    # 5. Test Concurrent High-Volume Ingestion
    # ---------------------------------------------------------
    def test_concurrent_ingestion_sqlite_wal(self):
        num_threads = 5
        events_per_thread = 20
        total_expected = num_threads * events_per_thread

        def worker(thread_idx):
            # Masing-masing thread menggunakan instance hub sendiri yang berbagi file sqlite
            local_hub = WebhookHub(db_path=self.db_path)
            for i in range(events_per_thread):
                key = f"th_{thread_idx}_evt_{i}"
                local_hub.ingest_webhook("pos_system", "sale.logged", key, {"item": f"coffee_{i}", "price": 25000})
            local_hub.conn.close()

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        metrics = self.hub.get_metrics()
        self.assertEqual(metrics["total_events"], total_expected)
        self.assertEqual(metrics["pending"], total_expected)

if __name__ == "__main__":
    unittest.main()
