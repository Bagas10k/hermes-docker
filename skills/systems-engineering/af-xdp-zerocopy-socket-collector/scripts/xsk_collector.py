"""
AF_XDP (XSK) Zero-Copy Ingress Ring-Buffer Model for User-Space Telemetry Collectors.

Mekanisme Kernel vs Userspace:
- UMEM (User Memory): Virtual memory chunk terdaftar di kernel (pinned pages).
- RX Ring: Kernel meletakkan deskriptor frame masuk (addr, len).
- FILL Ring: Userspace mengisi slot UMEM kosong yang siap diisi paket oleh driver NIC.
- TX & COMPLETION Ring: Jalur transmisi nol-salin balik.
- Zero-copy (XDP_ZEROCOPY): DMA langsung dari NIC ke UMEM tanpa alokasi sk_buff dan tanpa copy_to_user().

File ini menyediakan model deterministik arsitektur UMEM & ring buffers (Fill, Rx)
beserta dekoder frame telemetri Ethernet/IP/UDP deterministik berkinerja tinggi.
"""

import struct
import math
from typing import List, Dict, Tuple, Optional

# Konstanta framing Ethernet & IP
ETH_HLEN = 14
IP_HLEN = 20
UDP_HLEN = 8
ETH_P_IP = 0x0800
IPPROTO_UDP = 17

class UMEMChunkPool:
    """
    Simulasi alokasi blok UMEM berukuran tetap (fixed 2048 atau 4096 bytes per frame).
    Bebas alokasi dinamis (Zero-GC / Zero-Alloc saat runtime loop).
    """
    def __init__(self, num_chunks: int = 1024, chunk_size: int = 2048):
        self.chunk_size = chunk_size
        self.num_chunks = num_chunks
        self.buffer = bytearray(num_chunks * chunk_size)
        self.free_stack = list(range(num_chunks))
        
    def get_chunk(self) -> Optional[int]:
        if not self.free_stack:
            return None
        return self.free_stack.pop()

    def release_chunk(self, chunk_idx: int) -> None:
        self.free_stack.append(chunk_idx)

    def write_payload(self, chunk_idx: int, data: bytes, offset: int = 0) -> int:
        start = (chunk_idx * self.chunk_size) + offset
        end = start + len(data)
        if end > ((chunk_idx + 1) * self.chunk_size):
            raise ValueError("Buffer overflow pada chunk UMEM")
        self.buffer[start:end] = data
        return len(data)

    def read_payload(self, chunk_idx: int, offset: int, length: int) -> memoryview:
        start = (chunk_idx * self.chunk_size) + offset
        return memoryview(self.buffer)[start:start + length]


class XSKRingBuffer:
    """
    Simulasi Lock-free Single-Producer Single-Consumer (SPSC) Ring Buffer
    menggunakan indeks Producer & Consumer termask secara bitwise (power of 2).
    """
    def __init__(self, size: int = 512):
        if (size & (size - 1)) != 0:
            raise ValueError("Ukuran ring buffer wajib kelipatan 2 (power of two)")
        self.size = size
        self.mask = size - 1
        self.entries = [None] * size
        self.producer = 0
        self.consumer = 0

    def available_to_produce(self) -> int:
        return self.size - (self.producer - self.consumer)

    def available_to_consume(self) -> int:
        return self.producer - self.consumer

    def produce_batch(self, items: List[any]) -> int:
        n = min(len(items), self.available_to_produce())
        for i in range(n):
            idx = (self.producer + i) & self.mask
            self.entries[idx] = items[i]
        self.producer += n
        return n

    def consume_batch(self, max_items: int) -> List[any]:
        n = min(max_items, self.available_to_consume())
        res = []
        for i in range(n):
            idx = (self.consumer + i) & self.mask
            res.append(self.entries[idx])
            self.entries[idx] = None
        self.consumer += n
        return res


class AFXDPIngressCollector:
    """
    Arsitektur AF_XDP Zero-Copy Ingress Telemetry Collector.
    Menghubungkan UMEM Pool, FILL Ring, dan RX Ring.
    """
    def __init__(self, ring_size: int = 512, chunk_size: int = 2048):
        self.chunk_size = chunk_size
        self.umem = UMEMChunkPool(num_chunks=ring_size * 2, chunk_size=chunk_size)
        self.fill_ring = XSKRingBuffer(size=ring_size)
        self.rx_ring = XSKRingBuffer(size=ring_size)
        
        # Inisialisasi: Isi FILL ring dengan buffer kosong untuk driver NIC
        self.refill_fill_ring()

    def refill_fill_ring(self) -> int:
        """Mengisi FILL ring dari pool UMEM yang belum dipakai."""
        avail = self.fill_ring.available_to_produce()
        items = []
        for _ in range(avail):
            c_idx = self.umem.get_chunk()
            if c_idx is None:
                break
            items.append(c_idx * self.chunk_size)
        return self.fill_ring.produce_batch(items)

    def simulate_nic_dma_ingress(self, raw_frames: List[bytes]) -> int:
        """
        Kernel / NIC driver side:
        1. Ambil alamat dari FILL ring.
        2. DMA raw_frame langsung ke alamat UMEM.
        3. Kirim deskriptor (addr, len) ke RX ring.
        """
        consumed_addrs = self.fill_ring.consume_batch(len(raw_frames))
        rx_desc = []
        
        for i, addr in enumerate(consumed_addrs):
            chunk_idx = addr // self.chunk_size
            data = raw_frames[i]
            length = self.umem.write_payload(chunk_idx, data, offset=0)
            rx_desc.append({"addr": addr, "len": length, "chunk_idx": chunk_idx})
            
        return self.rx_ring.produce_batch(rx_desc)

    def process_rx_batch(self, max_batch: int = 64) -> Tuple[List[Dict], int]:
        """
        Userspace collector side (Zero syscall recvmsg):
        1. Baca deskriptor dari RX ring.
        2. Parse zero-copy payload via memoryview.
        3. Release chunk kembali ke pool / siapkan untuk FILL ring.
        """
        descriptors = self.rx_ring.consume_batch(max_batch)
        parsed_records = []
        
        for desc in descriptors:
            addr = desc["addr"]
            length = desc["len"]
            chunk_idx = desc["chunk_idx"]
            
            # Zero-copy memoryview
            view = self.umem.read_payload(chunk_idx, offset=0, length=length)
            parsed = self.parse_telemetry_frame(view)
            if parsed:
                parsed_records.append(parsed)
                
            # Recycle chunk kembali
            self.umem.release_chunk(chunk_idx)
            
        # Refill kembali FILL ring
        self.refill_fill_ring()
        return parsed_records, len(descriptors)

    @staticmethod
    def parse_telemetry_frame(frame: memoryview) -> Optional[Dict]:
        """
        Parsing header Ethernet + IPv4 + UDP + Telemetry Metric (Binary Protocol)
        tanpa alokasi string intermediate jika parsing gagal.
        Format Header:
        - Eth: dst (6), src (6), proto (2)
        - IP: ver_ihl (1), tos (1), len (2), id (2), frag (2), ttl (1), proto (1), csum (2), src (4), dst (4)
        - UDP: src_port (2), dst_port (2), len (2), csum (2)
        - Telemetry Payload: agent_id (uint32), metric_id (uint16), value (float64)
        """
        if len(frame) < (ETH_HLEN + IP_HLEN + UDP_HLEN + 14):
            return None
        
        eth_type = struct.unpack("!H", frame[12:14])[0]
        if eth_type != ETH_P_IP:
            return None
            
        ip_proto = frame[ETH_HLEN + 9]
        if ip_proto != IPPROTO_UDP:
            return None
            
        udp_offset = ETH_HLEN + IP_HLEN
        dst_port = struct.unpack("!H", frame[udp_offset + 2:udp_offset + 4])[0]
        
        payload_offset = udp_offset + UDP_HLEN
        p_view = frame[payload_offset:payload_offset + 14]
        
        agent_id, metric_id, val = struct.unpack("!IHd", p_view)
        
        return {
            "port": dst_port,
            "agent_id": agent_id,
            "metric_id": metric_id,
            "value": val
        }


def craft_telemetry_packet(agent_id: int, metric_id: int, value: float, dst_port: int = 9999) -> bytes:
    """Helper membuat frame Ethernet/IP/UDP biner untuk pengujian."""
    eth_hdr = b"\x00\x11\x22\x33\x44\x55" + b"\x66\x77\x88\x99\xaa\xbb" + struct.pack("!H", ETH_P_IP)
    ip_hdr = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + 8 + 14, 1234, 0, 64, IPPROTO_UDP, 0, b"\x7f\x00\x00\x01", b"\x7f\x00\x00\x01")
    udp_hdr = struct.pack("!HHHH", 12345, dst_port, 8 + 14, 0)
    payload = struct.pack("!IHd", agent_id, metric_id, value)
    return eth_hdr + ip_hdr + udp_hdr + payload
