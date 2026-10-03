#!/usr/bin/env python3
import unittest
import tempfile
import sqlite3
import os
import shutil
import http.server
import threading
import time
from pathlib import Path

import sys
sys.path.append("/home/ubuntu/.hermes/skills/systems-engineering/client-vps-selfhealing-deployment/scripts")

from client_vps_watchdog import VPSDeploymentWatchdog, ServiceState
from vps_stack_provisioner import VPSStackProvisioner

class MockHealthHandler(http.server.BaseHTTPRequestHandler):
    should_fail = False

    def do_GET(self):
        if self.path == "/health":
            if MockHealthHandler.should_fail:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Internal Error")
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Quiet

class TestClientVPSSelfHealing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_port = 18991
        MockHealthHandler.should_fail = False
        cls.httpd = http.server.HTTPServer(("127.0.0.1", cls.server_port), MockHealthHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_vps_stack_provisioning(self):
        prov = VPSStackProvisioner(self.test_dir, "myapp", "myapp.client.com", 4000)
        c_path = prov.generate_docker_compose()
        n_path = prov.generate_nginx_conf()
        t_path = prov.generate_cloudflare_tunnel_yaml()
        s_path = prov.generate_systemd_watchdog_service()

        self.assertTrue(os.path.exists(c_path))
        self.assertTrue(os.path.exists(n_path))
        self.assertTrue(os.path.exists(t_path))
        self.assertTrue(os.path.exists(s_path))

        with open(n_path) as f:
            content = f.read()
            self.assertIn("myapp.client.com", content)
            self.assertIn("proxy_pass http://127.0.0.1:4000;", content)

    def test_sqlite_wal_backup(self):
        db_file = os.path.join(self.test_dir, "app.db")
        con = sqlite3.connect(db_file)
        cur = con.cursor()
        cur.execute("CREATE TABLE users (id INT, name TEXT)")
        cur.execute("INSERT INTO users VALUES (1, 'Bagas')")
        con.commit()
        con.close()

        backup_dir = os.path.join(self.test_dir, "backups")
        backup_file = VPSDeploymentWatchdog.backup_sqlite_wal(db_file, backup_dir)
        self.assertIsNotNone(backup_file)
        self.assertTrue(os.path.exists(backup_file))

        # Verify integrity of backup
        con_b = sqlite3.connect(backup_file)
        cur_b = con_b.cursor()
        cur_b.execute("SELECT name FROM users WHERE id=1")
        row = cur_b.fetchone()
        self.assertEqual(row[0], "Bagas")
        con_b.close()

    def test_watchdog_healthy_probe(self):
        MockHealthHandler.should_fail = False
        config = {
            "services": [
                {
                    "name": "web_api",
                    "probe_url": f"http://127.0.0.1:{self.server_port}/health",
                    "restart_cmd": "echo restarted",
                    "timeout_sec": 1.0
                }
            ],
            "max_restarts": 3
        }
        watchdog = VPSDeploymentWatchdog(config)
        res = watchdog.run_health_and_heal_cycle()
        self.assertEqual(res["web_api"]["status"], ServiceState.UP)
        self.assertEqual(res["web_api"]["restart_count"], 0)
        self.assertFalse(res["web_api"]["circuit_tripped"])

    def test_watchdog_degraded_and_circuit_breaker(self):
        MockHealthHandler.should_fail = True
        config = {
            "services": [
                {
                    "name": "failing_api",
                    "probe_url": f"http://127.0.0.1:{self.server_port}/health",
                    "restart_cmd": "echo failing_restart",
                    "timeout_sec": 1.0
                }
            ],
            "max_restarts": 2
        }
        watchdog = VPSDeploymentWatchdog(config)

        # Iteration 1: Degraded -> triggers restart
        res1 = watchdog.run_health_and_heal_cycle()
        self.assertEqual(res1["failing_api"]["restart_count"], 1)

        # Iteration 2: Degraded -> triggers restart
        res2 = watchdog.run_health_and_heal_cycle()
        self.assertEqual(res2["failing_api"]["restart_count"], 2)

        # Iteration 3: Hit max_restarts -> Circuit breaker tripped
        res3 = watchdog.run_health_and_heal_cycle()
        self.assertTrue(res3["failing_api"]["circuit_tripped"])
        self.assertEqual(res3["failing_api"]["status"], ServiceState.TRIPPED)

if __name__ == "__main__":
    unittest.main()
