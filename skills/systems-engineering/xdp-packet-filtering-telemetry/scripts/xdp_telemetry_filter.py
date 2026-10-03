"""
Kernel-Bypass XDP/eBPF Packet Filtering for High-Volume Telemetry Ingress.
Simulates XDP hook execution (L2 driver level) before Linux network stack allocation (sk_buff bypass).
"""

import struct
import time
from typing import Dict, Tuple, Optional, NamedTuple

# XDP Action Codes (standard Linux xdp_action enum)
XDP_ABORTED = 0
XDP_DROP = 1
XDP_PASS = 2
XDP_TX = 3
XDP_REDIRECT = 4

class Packet(NamedTuple):
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    magic_header: bytes
    tenant_id: int
    metric_type: int
    payload_len: int
    raw_bytes: bytes

class BpfMapHash:
    """BPF_MAP_TYPE_HASH simulation with atomic lookup/update and expiry."""
    def __init__(self, max_entries: int = 10240):
        self.max_entries = max_entries
        self.data: Dict[int, Dict[str, float]] = {}

    def lookup(self, key: int) -> Optional[Dict[str, float]]:
        return self.data.get(key)

    def update(self, key: int, value: Dict[str, float]) -> bool:
        if len(self.data) >= self.max_entries and key not in self.data:
            return False
        self.data[key] = value
        return True

class BpfMapPerCpuArray:
    """BPF_MAP_TYPE_PERCPU_ARRAY simulation for lockless telemetry counters."""
    def __init__(self, num_cpus: int = 4):
        self.num_cpus = num_cpus
        # Action -> [counter per cpu]
        self.counters: Dict[int, list] = {
            XDP_ABORTED: [0] * num_cpus,
            XDP_DROP: [0] * num_cpus,
            XDP_PASS: [0] * num_cpus,
            XDP_TX: [0] * num_cpus,
            XDP_REDIRECT: [0] * num_cpus,
        }

    def increment(self, action: int, cpu_id: int = 0, count: int = 1):
        if action in self.counters:
            self.counters[action][cpu_id % self.num_cpus] += count

    def get_total(self, action: int) -> int:
        return sum(self.counters.get(action, [0]))

class BpfMapRingBuffer:
    """BPF_MAP_TYPE_RINGBUF zero-copy multi-producer ring buffer emulation."""
    def __init__(self, capacity: int = 65536):
        self.capacity = capacity
        self.buffer = []

    def submit(self, data: bytes) -> bool:
        if len(self.buffer) >= self.capacity:
            return False
        self.buffer.append(data)
        return True

    def drain(self, batch_size: int = 128) -> list:
        batch = self.buffer[:batch_size]
        self.buffer = self.buffer[batch_size:]
        return batch

class XdpTelemetryFilter:
    """
    Simulates eBPF program attached to driver network interface (xdp_drv).
    Direct packet inspection without Linux sk_buff memory allocation overhead.
    """
    MAGIC = b"TELE" # 4 bytes protocol identifier

    def __init__(self, default_port: int = 9876):
        self.default_port = default_port
        self.auth_map = BpfMapHash(max_entries=10000)
        self.metrics_map = BpfMapPerCpuArray(num_cpus=4)
        self.ringbuf = BpfMapRingBuffer(capacity=32768)
        self.rate_limit_map = BpfMapHash(max_entries=10000)

    def register_tenant(self, tenant_id: int, token: int, rate_limit_pps: float):
        """Populates BPF maps from user space."""
        self.auth_map.update(tenant_id, {"token": token, "rate_limit": rate_limit_pps})
        self.rate_limit_map.update(tenant_id, {"tokens": rate_limit_pps, "last_ts": time.monotonic()})

    def check_rate_limit(self, tenant_id: int, rate_limit_pps: float, now: float) -> bool:
        """Token bucket algorithm executed at wire speed."""
        state = self.rate_limit_map.lookup(tenant_id)
        if not state:
            return False
        elapsed = now - state["last_ts"]
        # Refill tokens
        tokens = min(rate_limit_pps, state["tokens"] + elapsed * rate_limit_pps)
        if tokens >= 1.0:
            self.rate_limit_map.update(tenant_id, {"tokens": tokens - 1.0, "last_ts": now})
            return True
        else:
            self.rate_limit_map.update(tenant_id, {"tokens": tokens, "last_ts": now})
            return False

    def process_packet(self, raw_bytes: bytes, cpu_id: int = 0) -> Tuple[int, Optional[str]]:
        """
        Kernel-level XDP hook function.
        Returns: (xdp_action, reason)
        """
        # Minimum packet size: L2 (14B) + L3 (20B) + L4 (8B) + Header (12B) = 54 bytes
        if len(raw_bytes) < 54:
            self.metrics_map.increment(XDP_DROP, cpu_id)
            return XDP_DROP, "PACKET_TOO_SHORT"

        # L2 Ethernet Header parsing
        eth_type = struct.unpack("!H", raw_bytes[12:14])[0]
        if eth_type != 0x0800: # IPv4 only
            self.metrics_map.increment(XDP_PASS, cpu_id)
            return XDP_PASS, "NON_IPV4"

        # L3 IPv4 Header parsing
        ip_header = raw_bytes[14:34]
        proto = ip_header[9]
        if proto != 17: # UDP only
            self.metrics_map.increment(XDP_PASS, cpu_id)
            return XDP_PASS, "NON_UDP"

        # L4 UDP Header parsing
        udp_header = raw_bytes[34:42]
        src_port, dst_port, udp_len = struct.unpack("!HHH", udp_header[:6])
        if dst_port != self.default_port:
            self.metrics_map.increment(XDP_PASS, cpu_id)
            return XDP_PASS, "NOT_TELEMETRY_PORT"

        # Telemetry Protocol Header (Direct Memory Access)
        # Offset 42: Magic (4B), Tenant ID (4B), Metric Type (2B), Token (2B)
        tele_header = raw_bytes[42:54]
        magic = tele_header[0:4]
        if magic != self.MAGIC:
            self.metrics_map.increment(XDP_DROP, cpu_id)
            return XDP_DROP, "INVALID_MAGIC"

        tenant_id, metric_type, token = struct.unpack("!IHH", tele_header[4:12])

        # BPF Map Authentication Lookup
        auth = self.auth_map.lookup(tenant_id)
        if not auth or auth.get("token") != token:
            self.metrics_map.increment(XDP_DROP, cpu_id)
            return XDP_DROP, "UNAUTHORIZED_TENANT"

        # Rate Limiting
        now = time.monotonic()
        if not self.check_rate_limit(tenant_id, auth["rate_limit"], now):
            self.metrics_map.increment(XDP_DROP, cpu_id)
            return XDP_DROP, "RATE_LIMIT_EXCEEDED"

        # Fast Redirect into Ring Buffer (User space ingest)
        payload = raw_bytes[54:]
        if not self.ringbuf.submit(payload):
            self.metrics_map.increment(XDP_DROP, cpu_id)
            return XDP_DROP, "RINGBUF_FULL"

        self.metrics_map.increment(XDP_REDIRECT, cpu_id)
        return XDP_REDIRECT, "INGEST_SUCCESS"

    def get_stats(self) -> Dict[str, int]:
        return {
            "drop": self.metrics_map.get_total(XDP_DROP),
            "pass": self.metrics_map.get_total(XDP_PASS),
            "redirect": self.metrics_map.get_total(XDP_REDIRECT),
            "queued_in_ringbuf": len(self.ringbuf.buffer)
        }

def build_telemetry_packet(tenant_id: int, token: int, metric_type: int, payload: bytes, dst_port: int = 9876, magic: bytes = b"TELE") -> bytes:
    """Helper to assemble raw synthetic network packet for testing."""
    # L2 Ethernet Header (14 bytes)
    eth = b"\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\x08\x00"
    # L3 IPv4 Header (20 bytes: 0x45, UDP proto=17)
    ip = b"\x45\x00\x00\x00\x00\x00\x00\x00\x40\x11\x00\x00\x0a\x00\x00\x01\x0a\x00\x00\x02"
    # L4 UDP Header (8 bytes)
    udp = struct.pack("!HHHH", 54321, dst_port, 8 + 12 + len(payload), 0)
    # Telemetry Header (12 bytes)
    tele = magic + struct.pack("!IHH", tenant_id, metric_type, token)
    return eth + ip + udp + tele + payload
