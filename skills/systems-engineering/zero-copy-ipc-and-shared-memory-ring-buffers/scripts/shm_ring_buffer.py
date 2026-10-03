"""Zero-Copy Ring-Buffer IPC & Shared-Memory Context Transfer for Parallel Agents.

Mechanistic model:
  Header layout (64-byte aligned, 128 bytes total):
    magic: u32 (0x5A434950 'ZCIP')
    version: u32 (1)
    capacity: u32 (power of 2)
    slot_size: u32 (power of 2, >= 64)
    write_seq: atomic_u64 (64-byte cache-line aligned)
    read_seq: atomic_u64 (64-byte cache-line aligned)

  Slot layout (slot_size bytes):
    commit_seq: atomic_u64 (equal to seq + 1 when committed)
    payload_len: u32
    metric_type: u32
    timestamp_ns: u64
    payload: bytes [slot_size - 24]

Memory Safety & Invariants:
  1. Ring buffer capacity MUST be power of 2: mask = capacity - 1.
  2. Single Producer / Multi Consumer or Multi-Reader.
  3. Producer writes data, then memory barrier / release store to commit_seq.
  4. Consumer loads commit_seq with acquire semantics. If commit_seq != seq + 1, slot is being written (torn read prevention).
  5. If write_seq - read_seq >= capacity, buffer is full (overflow backpressure or drop oldest policy).
"""

import os
import sys
import time
import mmap
import struct
import argparse
from typing import Optional, Tuple, Dict, Any

HEADER_MAGIC = 0x5A434950  # 'ZCIP' in ASCII
HEADER_VERSION = 1
HEADER_SIZE = 128
SLOT_HEADER_SIZE = 24  # commit_seq(8), payload_len(4), metric_type(4), timestamp_ns(8)

# Format: magic(I), version(I), capacity(I), slot_size(I) -> 16 bytes
# Followed by padding, write_seq at offset 64, read_seq at offset 96
HEADER_STATIC_FMT = "=IIII"
HEADER_STATIC_SIZE = struct.calcsize(HEADER_STATIC_FMT)

SLOT_HEADER_FMT = "=QIIQ"


def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


class SharedMemoryRingBuffer:
    def __init__(
        self,
        name: str,
        capacity: int = 256,
        slot_size: int = 1024,
        create: bool = False,
        backed_by_file: bool = False,
        filepath: Optional[str] = None
    ):
        if not is_power_of_two(capacity):
            raise ValueError(f"Capacity must be power of 2, got {capacity}")
        if slot_size < SLOT_HEADER_SIZE or not is_power_of_two(slot_size):
            raise ValueError(f"Slot size must be power of 2 and >= {SLOT_HEADER_SIZE}, got {slot_size}")

        self.name = name
        self.capacity = capacity
        self.slot_size = slot_size
        self.mask = capacity - 1
        self.total_size = HEADER_SIZE + (capacity * slot_size)
        self.max_payload_size = slot_size - SLOT_HEADER_SIZE
        self.filepath = filepath or f"/dev/shm/{name}"
        self.fd = None
        self.mm: Optional[mmap.mmap] = None
        self._is_owner = create

        if create:
            self._init_create()
        else:
            self._init_open()

    def _init_create(self):
        # Open / truncate file
        self.fd = os.open(self.filepath, os.O_CREAT | os.O_RDWR | os.O_TRUNC, 0o600)
        os.ftruncate(self.fd, self.total_size)
        self.mm = mmap.mmap(self.fd, self.total_size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
        
        # Write static header
        header_data = struct.pack(HEADER_STATIC_FMT, HEADER_MAGIC, HEADER_VERSION, self.capacity, self.slot_size)
        self.mm[0:HEADER_STATIC_SIZE] = header_data
        
        # Zero write_seq and read_seq
        self._set_write_seq(0)
        self._set_read_seq(0)
        
        # Zero out all slots
        self.mm[HEADER_SIZE:self.total_size] = b"\x00" * (self.capacity * self.slot_size)

    def _init_open(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Shared memory file not found: {self.filepath}")
        self.fd = os.open(self.filepath, os.O_RDWR, 0o600)
        file_size = os.fstat(self.fd).st_size
        if file_size < HEADER_SIZE:
            raise ValueError("Shared memory file is corrupted or too small")
            
        self.mm = mmap.mmap(self.fd, file_size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
        magic, version, capacity, slot_size = struct.unpack_from(HEADER_STATIC_FMT, self.mm, 0)
        
        if magic != HEADER_MAGIC:
            raise ValueError(f"Invalid magic header: {hex(magic)} != {hex(HEADER_MAGIC)}")
        if version != HEADER_VERSION:
            raise ValueError(f"Unsupported version: {version}")
            
        self.capacity = capacity
        self.slot_size = slot_size
        self.mask = capacity - 1
        self.total_size = HEADER_SIZE + (capacity * slot_size)
        self.max_payload_size = slot_size - SLOT_HEADER_SIZE

    def _get_write_seq(self) -> int:
        return struct.unpack_from("=Q", self.mm, 64)[0]

    def _set_write_seq(self, seq: int):
        struct.pack_into("=Q", self.mm, 64, seq)

    def _get_read_seq(self) -> int:
        return struct.unpack_from("=Q", self.mm, 96)[0]

    def _set_read_seq(self, seq: int):
        struct.pack_into("=Q", self.mm, 96, seq)

    def _slot_offset(self, index: int) -> int:
        return HEADER_SIZE + ((index & self.mask) * self.slot_size)

    def push(self, metric_type: int, payload: bytes, timestamp_ns: Optional[int] = None) -> Tuple[bool, int]:
        """Push payload to the ring buffer.
        Returns: (success: bool, sequence_number: int)
        """
        if len(payload) > self.max_payload_size:
            raise ValueError(f"Payload size {len(payload)} exceeds max {self.max_payload_size}")
            
        write_seq = self._get_write_seq()
        read_seq = self._get_read_seq()

        # Check full condition
        if write_seq - read_seq >= self.capacity:
            return False, write_seq

        slot_off = self._slot_offset(write_seq)
        if timestamp_ns is None:
            timestamp_ns = time.time_ns()

        # 1. Invalidate slot commit_seq first (uncommitted marker: 0)
        struct.pack_into("=Q", self.mm, slot_off, 0)

        # 2. Write slot body & metadata
        struct.pack_into(
            "=IIQ",
            self.mm,
            slot_off + 8,
            len(payload),
            metric_type,
            timestamp_ns
        )
        self.mm[slot_off + SLOT_HEADER_SIZE : slot_off + SLOT_HEADER_SIZE + len(payload)] = payload

        # 3. Commit barrier: commit_seq = write_seq + 1
        struct.pack_into("=Q", self.mm, slot_off, write_seq + 1)

        # 4. Advance write_seq
        self._set_write_seq(write_seq + 1)
        return True, write_seq

    def pop(self) -> Optional[Dict[str, Any]]:
        """Pop the oldest entry from the ring buffer.
        Returns: dict with metric_type, timestamp_ns, payload, seq or None if empty.
        """
        read_seq = self._get_read_seq()
        write_seq = self._get_write_seq()

        if read_seq >= write_seq:
            return None

        slot_off = self._slot_offset(read_seq)
        commit_seq, payload_len, metric_type, timestamp_ns = struct.unpack_from(SLOT_HEADER_FMT, self.mm, slot_off)

        # Torn read check: must be committed with exactly read_seq + 1
        if commit_seq != read_seq + 1:
            return None

        payload = bytes(self.mm[slot_off + SLOT_HEADER_SIZE : slot_off + SLOT_HEADER_SIZE + payload_len])

        # Advance read cursor
        self._set_read_seq(read_seq + 1)

        return {
            "seq": read_seq,
            "metric_type": metric_type,
            "timestamp_ns": timestamp_ns,
            "payload": payload,
            "len": payload_len
        }

    def peek_latest(self) -> Optional[Dict[str, Any]]:
        """Read the most recently written committed slot without advancing read pointer."""
        write_seq = self._get_write_seq()
        if write_seq == 0:
            return None

        target_seq = write_seq - 1
        slot_off = self._slot_offset(target_seq)
        commit_seq, payload_len, metric_type, timestamp_ns = struct.unpack_from(SLOT_HEADER_FMT, self.mm, slot_off)

        if commit_seq != target_seq + 1:
            return None

        payload = bytes(self.mm[slot_off + SLOT_HEADER_SIZE : slot_off + SLOT_HEADER_SIZE + payload_len])
        return {
            "seq": target_seq,
            "metric_type": metric_type,
            "timestamp_ns": timestamp_ns,
            "payload": payload,
            "len": payload_len
        }

    def stats(self) -> Dict[str, Any]:
        write_seq = self._get_write_seq()
        read_seq = self._get_read_seq()
        return {
            "capacity": self.capacity,
            "slot_size": self.slot_size,
            "write_seq": write_seq,
            "read_seq": read_seq,
            "unconsumed_count": write_seq - read_seq,
            "total_bytes": self.total_size,
            "max_payload_size": self.max_payload_size
        }

    def close(self):
        if self.mm:
            self.mm.close()
            self.mm = None
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def unlink(self):
        self.close()
        if os.path.exists(self.filepath):
            try:
                os.remove(self.filepath)
            except OSError:
                pass


def run_benchmark(iterations: int = 50000, payload_len: int = 256) -> Dict[str, Any]:
    """Microbenchmark measuring push and pop throughput in nanoseconds."""
    test_shm_name = f"bench_ring_{os.getpid()}"
    ring = SharedMemoryRingBuffer(test_shm_name, capacity=4096, slot_size=512, create=True)
    payload = b"X" * payload_len

    try:
        # Push throughput
        t0 = time.perf_counter_ns()
        for i in range(iterations):
            success, seq = ring.push(metric_type=1, payload=payload)
            if not success:
                ring.pop()
                ring.push(metric_type=1, payload=payload)
        t1 = time.perf_counter_ns()

        total_push_time_ns = t1 - t0
        avg_push_ns = total_push_time_ns / iterations

        # Pop throughput
        t2 = time.perf_counter_ns()
        popped = 0
        while popped < iterations:
            item = ring.pop()
            if item is not None:
                popped += 1
            else:
                break
        t3 = time.perf_counter_ns()

        total_pop_time_ns = t3 - t2
        avg_pop_ns = total_pop_time_ns / max(1, popped)

        return {
            "iterations": iterations,
            "payload_bytes": payload_len,
            "avg_push_ns": avg_push_ns,
            "avg_pop_ns": avg_pop_ns,
            "push_ops_per_sec": int(1e9 / avg_push_ns) if avg_push_ns > 0 else 0,
            "pop_ops_per_sec": int(1e9 / avg_pop_ns) if avg_pop_ns > 0 else 0
        }
    finally:
        ring.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zero-Copy Shared Memory Ring Buffer CLI")
    parser.add_argument("--demo", action="store_true", help="Run a quick demo push and pop")
    parser.add_argument("--bench", action="store_true", help="Run performance benchmark")
    parser.add_argument("--iterations", type=int, default=50000, help="Benchmark iterations")
    args = parser.parse_args()

    if args.bench:
        results = run_benchmark(iterations=args.iterations)
        print(f"Benchmark Results ({results['iterations']} ops, {results['payload_bytes']} bytes payload):")
        print(f"  Push: {results['avg_push_ns']:.1f} ns/op ({results['push_ops_per_sec']:,} ops/s)")
        print(f"  Pop:  {results['avg_pop_ns']:.1f} ns/op ({results['pop_ops_per_sec']:,} ops/s)")
    elif args.demo:
        shm_name = f"demo_ring_{os.getpid()}"
        ring = SharedMemoryRingBuffer(shm_name, capacity=8, slot_size=128, create=True)
        try:
            print("Pushed 3 frames...")
            ring.push(101, b"AGENT_FRAME_001_DATA")
            ring.push(102, b"AGENT_FRAME_002_DATA")
            ring.push(103, b"AGENT_FRAME_003_DATA")
            print("Stats:", ring.stats())
            
            latest = ring.peek_latest()
            print("Peek Latest:", latest["metric_type"], latest["payload"])
            
            print("Popping entries:")
            while True:
                item = ring.pop()
                if item is None:
                    break
                print(f"  Seq {item['seq']} [Type {item['metric_type']}]: {item['payload'].decode('utf-8', errors='ignore')}")
            print("Done demo.")
        finally:
            ring.unlink()
    else:
        parser.print_help()
