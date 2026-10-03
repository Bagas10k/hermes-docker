import unittest
import time
from xdp_telemetry_filter import (
    XdpTelemetryFilter,
    build_telemetry_packet,
    XDP_DROP,
    XDP_PASS,
    XDP_REDIRECT
)

class TestXdpTelemetryFilter(unittest.TestCase):
    def setUp(self):
        self.filter = XdpTelemetryFilter(default_port=9876)
        # Register Tenant 100 with token 0xABCD and 500 pps limit
        self.filter.register_tenant(tenant_id=100, token=0xABCD, rate_limit_pps=500.0)
        # Register Tenant 200 with token 0x1234 and 2 pps limit (strict for rate testing)
        self.filter.register_tenant(tenant_id=200, token=0x1234, rate_limit_pps=2.0)

    def test_valid_telemetry_packet(self):
        pkt = build_telemetry_packet(tenant_id=100, token=0xABCD, metric_type=1, payload=b"cpu_pct=42.5")
        action, reason = self.filter.process_packet(pkt, cpu_id=0)
        self.assertEqual(action, XDP_REDIRECT)
        self.assertEqual(reason, "INGEST_SUCCESS")
        self.assertEqual(self.filter.ringbuf.drain(), [b"cpu_pct=42.5"])

    def test_short_packet_dropped(self):
        action, reason = self.filter.process_packet(b"too_short", cpu_id=1)
        self.assertEqual(action, XDP_DROP)
        self.assertEqual(reason, "PACKET_TOO_SHORT")

    def test_invalid_magic_dropped(self):
        pkt = build_telemetry_packet(tenant_id=100, token=0xABCD, metric_type=1, payload=b"data", magic=b"FAIL")
        action, reason = self.filter.process_packet(pkt, cpu_id=2)
        self.assertEqual(action, XDP_DROP)
        self.assertEqual(reason, "INVALID_MAGIC")

    def test_unauthorized_tenant_dropped(self):
        pkt = build_telemetry_packet(tenant_id=999, token=0x0000, metric_type=1, payload=b"data")
        action, reason = self.filter.process_packet(pkt, cpu_id=3)
        self.assertEqual(action, XDP_DROP)
        self.assertEqual(reason, "UNAUTHORIZED_TENANT")

    def test_wrong_port_passed_to_kernel_stack(self):
        # Non-telemetry traffic should bypass XDP filter and pass to normal kernel TCP/IP stack
        pkt = build_telemetry_packet(tenant_id=100, token=0xABCD, metric_type=1, payload=b"data", dst_port=80)
        action, reason = self.filter.process_packet(pkt, cpu_id=0)
        self.assertEqual(action, XDP_PASS)
        self.assertEqual(reason, "NOT_TELEMETRY_PORT")

    def test_token_bucket_rate_limiting(self):
        pkt = build_telemetry_packet(tenant_id=200, token=0x1234, metric_type=2, payload=b"mem_rss=1024")
        # Packet 1 & 2 within burst limit (rate=2.0)
        a1, _ = self.filter.process_packet(pkt, cpu_id=0)
        a2, _ = self.filter.process_packet(pkt, cpu_id=1)
        self.assertEqual(a1, XDP_REDIRECT)
        self.assertEqual(a2, XDP_REDIRECT)

        # Immediate 3rd packet must exceed rate limit
        a3, r3 = self.filter.process_packet(pkt, cpu_id=2)
        self.assertEqual(a3, XDP_DROP)
        self.assertEqual(r3, "RATE_LIMIT_EXCEEDED")

    def test_multicore_percpu_stats_aggregation(self):
        for cpu in range(4):
            pkt = build_telemetry_packet(tenant_id=100, token=0xABCD, metric_type=1, payload=b"metric")
            self.filter.process_packet(pkt, cpu_id=cpu)
        stats = self.filter.get_stats()
        self.assertEqual(stats["redirect"], 4)
        self.assertEqual(stats["drop"], 0)

if __name__ == "__main__":
    unittest.main()
