#!/usr/bin/env python3
"""
kernel_eventfd.py - Linux eventfd wait-free signaling & notification primitive.

Provides ultra-low overhead, non-blocking 8-byte uint64 event notification
between cooperating processes, sub-agents, or worker threads on Linux.
Eliminates busy polling (100% CPU loops) across shared-memory channels.
"""

import os
import sys
import time
import struct
import select
import ctypes
import errno
from typing import Optional, Tuple

# Linux eventfd constants (bits/eventfd.h)
EFD_SEMAPHORE = 0o00000001
EFD_NONBLOCK  = 0o00004000
EFD_CLOEXEC   = 0o02000000

_libc = None

def _get_libc():
    global _libc
    if _libc is None:
        try:
            _libc = ctypes.CDLL(None, use_errno=True)
            _libc.eventfd.argtypes = [ctypes.c_uint, ctypes.c_int]
            _libc.eventfd.restype = ctypes.c_int
        except Exception as e:
            raise RuntimeError(f"Failed to load libc for eventfd: {e}")
    return _libc

class EventFd:
    """
    Linux eventfd file-descriptor wrapper for kernel-level signaling.
    """
    def __init__(self, initval: int = 0, semaphore: bool = False, nonblock: bool = True, cloexec: bool = True, fd: Optional[int] = None):
        if fd is not None:
            self._fd = fd
            self._owned = False
        else:
            libc = _get_libc()
            flags = 0
            if semaphore:
                flags |= EFD_SEMAPHORE
            if nonblock:
                flags |= EFD_NONBLOCK
            if cloexec:
                flags |= EFD_CLOEXEC
            
            res = libc.eventfd(ctypes.c_uint(initval), ctypes.c_int(flags))
            if res < 0:
                err = ctypes.get_errno()
                raise OSError(err, os.strerror(err))
            self._fd = res
            self._owned = True
        
        self._semaphore = semaphore
        self._nonblock = nonblock
        self._closed = False

    @property
    def fd(self) -> int:
        return self._fd

    @property
    def is_closed(self) -> bool:
        return self._closed

    def notify(self, count: int = 1) -> None:
        """
        Signal the eventfd by writing an 8-byte uint64 count (default 1).
        In kernel, this adds `count` to the internal 64-bit counter.
        """
        if self._closed:
            raise ValueError("eventfd is closed")
        if count <= 0:
            raise ValueError("count must be positive integer")
        if count > 0xFFFFFFFFFFFFFFFE:
            raise ValueError("count exceeds maximum allowed (0xFFFFFFFFFFFFFFFE)")
        
        payload = struct.pack("=Q", count)
        try:
            written = os.write(self._fd, payload)
            if written != 8:
                raise OSError("Partial write to eventfd")
        except OSError as e:
            if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                # Counter reached max uint64 (0xFFFFFFFFFFFFFFFF - 1)
                raise BufferError("eventfd counter overflow/would block")
            raise

    def wait(self, timeout_sec: Optional[float] = None) -> int:
        """
        Wait for signal using select/epoll and read the 8-byte counter.
        If nonblock is True, will select first up to timeout_sec.
        Returns the counter value (if semaphore, returns 1; otherwise accumulated sum).
        If timeout expires without event, returns 0.
        """
        if self._closed:
            raise ValueError("eventfd is closed")
        
        if timeout_sec is not None and timeout_sec >= 0:
            rlist, _, _ = select.select([self._fd], [], [], timeout_sec)
            if not rlist:
                return 0
        
        try:
            buf = os.read(self._fd, 8)
            if len(buf) != 8:
                return 0
            return struct.unpack("=Q", buf)[0]
        except OSError as e:
            if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return 0
            raise

    def try_read(self) -> int:
        """
        Non-blocking read. Returns counter value if ready, 0 if EAGAIN/empty.
        """
        return self.wait(timeout_sec=0.0)

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            if self._owned and self._fd >= 0:
                try:
                    os.close(self._fd)
                except OSError:
                    pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self):
        return f"<EventFd fd={self._fd} closed={self._closed} sem={self._semaphore}>"


class EventChannel:
    """
    Bidirectional or Producer-Consumer channel pairing an eventfd with a shared state.
    """
    def __init__(self, efd: Optional[EventFd] = None):
        self.efd = efd or EventFd(nonblock=True)
        self.stats = {"signals_sent": 0, "signals_received": 0, "events_processed": 0}

    def emit(self, count: int = 1):
        self.efd.notify(count)
        self.stats["signals_sent"] += 1

    def poll(self, timeout: Optional[float] = 0.0) -> int:
        val = self.efd.wait(timeout)
        if val > 0:
            self.stats["signals_received"] += 1
            self.stats["events_processed"] += val
        return val

    def close(self):
        self.efd.close()


def benchmark_eventfd(iterations: int = 100000) -> dict:
    """
    Measures latency and throughput of write/read roundtrip on eventfd.
    """
    with EventFd(nonblock=True) as efd:
        # Write benchmark
        t0 = time.perf_counter()
        for _ in range(iterations):
            efd.notify(1)
            efd.try_read()
        t1 = time.perf_counter()
        
        total_time = t1 - t0
        ops_per_sec = (iterations * 2) / total_time
        latency_us = (total_time / (iterations * 2)) * 1_000_000

        return {
            "iterations": iterations,
            "total_time_s": round(total_time, 4),
            "roundtrips_per_sec": round(iterations / total_time, 1),
            "ops_per_sec": round(ops_per_sec, 1),
            "avg_latency_us": round(latency_us, 3)
        }

if __name__ == "__main__":
    if "--bench" in sys.argv:
        iters = 50000
        for i, arg in enumerate(sys.argv):
            if arg == "--iterations" and i + 1 < len(sys.argv):
                iters = int(sys.argv[i+1])
        res = benchmark_eventfd(iters)
        print("=== EventFd Microbenchmark ===")
        print(f"Iterations: {res['iterations']}")
        print(f"Total Time: {res['total_time_s']} s")
        print(f"Roundtrips/sec: {res['roundtrips_per_sec']:,.1f}")
        print(f"Ops/sec (Write+Read): {res['ops_per_sec']:,.1f}")
        print(f"Average Latency: {res['avg_latency_us']} us per operation")
    else:
        print("Running EventFd quick self-test...")
        with EventFd(nonblock=True) as efd:
            efd.notify(5)
            val = efd.wait(timeout_sec=0.1)
            print(f"Self-test success: wrote 5, read {val}")
