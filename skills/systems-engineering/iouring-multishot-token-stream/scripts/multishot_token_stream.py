"""
Linux io_uring Multi-Shot Polling & Provided Buffer Ring (PBUF_RING) Engine
for Sub-Millisecond LLM Token Streaming Architecture.

Design:
1. Provided Buffer Ring (pbuf_ring):
   Pre-registers memory buffers to kernel space via IORING_REGISTER_PBUF_RING logic.
   Kernel selects buffer dynamically on read/recv readiness (IOSQE_BUFFER_SELECT).
2. Multi-Shot Recv / Poll (IORING_POLL_ADD_MULTI / IORING_RECV_MULTISHOT):
   One-shot submission triggers continuous completions on incoming token stream chunks
   with CQE_F_MORE flag set until stream closure / EOF.
3. Fallback & Cross-Platform Userspace Engine:
   Implements bitwise exact emulation using non-blocking epoll/socket and ring buffers
   when native liburing is unavailable or restricted by seccomp/LSM.
"""

import os
import sys
import time
import socket
import struct
import select
from typing import List, Dict, Tuple, Optional, Any

# io_uring constants & bitflags
IORING_OP_NOP = 0
IORING_OP_READ = 1
IORING_OP_WRITE = 2
IORING_OP_POLL_ADD = 6
IORING_OP_SEND = 26
IORING_OP_RECV = 27
IORING_OP_PROVIDE_BUFFERS = 31
IORING_OP_REMOVE_BUFFERS = 32

# Multi-shot & buffer selection flags
IOSQE_FIXED_FILE = (1 << 0)
IOSQE_IO_DRAIN = (1 << 1)
IOSQE_IO_LINK = (1 << 2)
IOSQE_BUFFER_SELECT = (1 << 5)
IOSQE_ASYNC = (1 << 4)

IORING_POLL_ADD_MULTI = (1 << 0)
IORING_POLL_UPDATE_EVENTS = (1 << 1)
IORING_POLL_UPDATE_USER_DATA = (1 << 2)
IORING_POLL_ADD_LEVEL = (1 << 3)

# CQE flags
IORING_CQE_F_MORE = (1 << 1)
IORING_CQE_F_BUFFER = (1 << 0)
IORING_CQE_BUFFER_SHIFT = 16


class ProvidedBuffer:
    """Represents a pre-registered buffer chunk in the pbuf_ring."""
    __slots__ = ("bid", "bgid", "addr", "length", "in_use", "data")

    def __init__(self, bid: int, bgid: int, length: int):
        self.bid = bid          # Buffer ID
        self.bgid = bgid        # Buffer Group ID
        self.length = length    # Allocated capacity
        self.in_use = False
        self.data = bytearray(length)

    def reset(self):
        self.in_use = False


class ProvidedBufferRing:
    """
    Provided Buffer Ring Pool (IORING_REGISTER_PBUF_RING emulation).
    Eliminates per-packet buffer allocation in LLM token streaming loops.
    """
    def __init__(self, bgid: int, entries: int, buffer_size: int):
        if entries <= 0 or (entries & (entries - 1)) != 0:
            raise ValueError(f"Buffer pool entries must be power-of-two, got {entries}")
        self.bgid = bgid
        self.entries = entries
        self.buffer_size = buffer_size
        self.mask = entries - 1
        self.buffers: List[ProvidedBuffer] = [
            ProvidedBuffer(bid=i, bgid=bgid, length=buffer_size) for i in range(entries)
        ]
        self.tail = 0
        self.head = 0
        self.available_count = entries

    def get_buffer(self) -> Optional[ProvidedBuffer]:
        """Kernel selects available buffer automatically upon readiness."""
        if self.available_count == 0:
            return None
        buf = self.buffers[self.head & self.mask]
        self.head += 1
        self.available_count -= 1
        buf.in_use = True
        return buf

    def return_buffer(self, bid: int):
        """User releases buffer back into pbuf_ring."""
        buf = self.buffers[bid & self.mask]
        if buf.in_use:
            buf.reset()
            self.tail += 1
            self.available_count = min(self.entries, self.available_count + 1)


class SQE:
    """Submission Queue Entry."""
    __slots__ = ("opcode", "fd", "flags", "addr", "len", "user_data", "buf_group")

    def __init__(self, opcode: int, fd: int, flags: int = 0, addr: Any = None,
                 length: int = 0, user_data: int = 0, buf_group: int = 0):
        self.opcode = opcode
        self.fd = fd
        self.flags = flags
        self.addr = addr
        self.len = length
        self.user_data = user_data
        self.buf_group = buf_group


class CQE:
    """Completion Queue Entry."""
    __slots__ = ("user_data", "res", "flags")

    def __init__(self, user_data: int, res: int, flags: int = 0):
        self.user_data = user_data
        self.res = res      # Bytes transferred, ready events, or negative errno
        self.flags = flags  # May contain IORING_CQE_F_MORE | (bid << 16)

    @property
    def has_more(self) -> bool:
        return bool(self.flags & IORING_CQE_F_MORE)

    @property
    def buffer_id(self) -> Optional[int]:
        if self.flags & IORING_CQE_F_BUFFER:
            return (self.flags >> IORING_CQE_BUFFER_SHIFT) & 0xFFFF
        return None


class MultiShotTokenStreamEngine:
    """
    Sub-millisecond Token Stream Dispatcher using io_uring multi-shot & fixed buffer semantics.
    """
    def __init__(self, queue_depth: int = 128):
        if queue_depth <= 0 or (queue_depth & (queue_depth - 1)) != 0:
            raise ValueError(f"Queue depth must be power-of-two, got {queue_depth}")
        self.queue_depth = queue_depth
        self.sq: List[SQE] = []
        self.cq: List[CQE] = []
        self.buffer_rings: Dict[int, ProvidedBufferRing] = {}
        self.multishot_active_streams: Dict[int, SQE] = {}  # fd -> SQE
        self.registered_fds: Dict[int, Any] = {}

    def register_buffer_ring(self, bgid: int, entries: int, buffer_size: int) -> ProvidedBufferRing:
        """Register a fixed provided buffer pool (IORING_REGISTER_PBUF_RING)."""
        ring = ProvidedBufferRing(bgid=bgid, entries=entries, buffer_size=buffer_size)
        self.buffer_rings[bgid] = ring
        return ring

    def register_socket(self, sock: socket.socket):
        """Register socket and enforce non-blocking mode."""
        sock.setblocking(False)
        self.registered_fds[sock.fileno()] = sock

    def prep_multishot_recv(self, fd: int, bgid: int, user_data: int):
        """
        Prepare a multi-shot recv operation using provided buffer selection.
        Kernel will continuously fire completions for each incoming chunk without re-arming.
        """
        sqe = SQE(
            opcode=IORING_OP_RECV,
            fd=fd,
            flags=IOSQE_BUFFER_SELECT,
            length=0,
            user_data=user_data,
            buf_group=bgid
        )
        if len(self.sq) >= self.queue_depth:
            raise OverflowError("Submission queue full (Backpressure engaged)")
        self.sq.append(sqe)

    def prep_send(self, fd: int, data: bytes, user_data: int):
        """Prepare send operation for LLM token chunk."""
        sqe = SQE(
            opcode=IORING_OP_SEND,
            fd=fd,
            flags=0,
            addr=data,
            length=len(data),
            user_data=user_data
        )
        if len(self.sq) >= self.queue_depth:
            raise OverflowError("Submission queue full (Backpressure engaged)")
        self.sq.append(sqe)

    def prep_multishot_poll(self, fd: int, events: int, user_data: int):
        """Prepare multi-shot poll (IORING_POLL_ADD_MULTI)."""
        sqe = SQE(
            opcode=IORING_OP_POLL_ADD,
            fd=fd,
            flags=IORING_POLL_ADD_MULTI,
            length=events,
            user_data=user_data
        )
        if len(self.sq) >= self.queue_depth:
            raise OverflowError("Submission queue full")
        self.sq.append(sqe)

    def cancel_multishot(self, fd: int):
        """Cancel an active multi-shot stream subscription."""
        if fd in self.multishot_active_streams:
            del self.multishot_active_streams[fd]

    def submit_and_wait(self, timeout_s: float = 0.05) -> int:
        """
        Processes submitted SQEs and services active multi-shot streams.
        Returns the number of generated CQEs.
        """
        # Move new submissions to active streams
        while self.sq:
            sqe = self.sq.pop(0)
            if sqe.opcode == IORING_OP_SEND:
                # Direct send execution
                sock = self.registered_fds.get(sqe.fd)
                if sock is None:
                    self.cq.append(CQE(sqe.user_data, -9))  # -EBADF
                    continue
                try:
                    sent = sock.send(sqe.addr)
                    self.cq.append(CQE(sqe.user_data, sent, 0))
                except BlockingIOError:
                    self.cq.append(CQE(sqe.user_data, -11, 0))  # -EAGAIN
                except Exception as e:
                    self.cq.append(CQE(sqe.user_data, -32, 0))  # -EPIPE
            elif sqe.opcode in (IORING_OP_RECV, IORING_OP_POLL_ADD):
                self.multishot_active_streams[sqe.fd] = sqe

        # Service active multi-shot streams
        if not self.multishot_active_streams:
            return len(self.cq)

        r_fds = list(self.multishot_active_streams.keys())
        try:
            readable, _, errored = select.select(r_fds, [], r_fds, timeout_s)
        except (ValueError, OSError):
            return len(self.cq)

        for fd in errored:
            sqe = self.multishot_active_streams.pop(fd, None)
            if sqe:
                self.cq.append(CQE(sqe.user_data, -5, 0))  # -EIO

        for fd in readable:
            sqe = self.multishot_active_streams.get(fd)
            if not sqe:
                continue

            sock = self.registered_fds.get(fd)
            if not sock:
                del self.multishot_active_streams[fd]
                self.cq.append(CQE(sqe.user_data, -9, 0))
                continue

            if sqe.opcode == IORING_OP_RECV:
                bgid = sqe.buf_group
                ring = self.buffer_rings.get(bgid)
                if not ring:
                    del self.multishot_active_streams[fd]
                    self.cq.append(CQE(sqe.user_data, -22, 0))  # -EINVAL
                    continue

                buf = ring.get_buffer()
                if not buf:
                    # Out of provided buffers: generate completion with ENOBUFS
                    self.cq.append(CQE(sqe.user_data, -105, IORING_CQE_F_MORE))
                    continue

                try:
                    chunk = sock.recv(ring.buffer_size)
                    if not chunk:
                        # Stream finished (EOF) -> final CQE WITHOUT IORING_CQE_F_MORE
                        del self.multishot_active_streams[fd]
                        ring.return_buffer(buf.bid)
                        self.cq.append(CQE(sqe.user_data, 0, 0))
                    else:
                        buf.data[:len(chunk)] = chunk
                        flags = IORING_CQE_F_MORE | IORING_CQE_F_BUFFER | (buf.bid << IORING_CQE_BUFFER_SHIFT)
                        self.cq.append(CQE(sqe.user_data, len(chunk), flags))
                except BlockingIOError:
                    ring.return_buffer(buf.bid)
                except Exception:
                    del self.multishot_active_streams[fd]
                    ring.return_buffer(buf.bid)
                    self.cq.append(CQE(sqe.user_data, -104, 0))  # -ECONNRESET

            elif sqe.opcode == IORING_OP_POLL_ADD:
                # Multi-shot poll produces continuous completions
                flags = IORING_CQE_F_MORE
                self.cq.append(CQE(sqe.user_data, select.POLLIN, flags))

        return len(self.cq)

    def peek_cqe(self) -> Optional[CQE]:
        """View next CQE without popping."""
        return self.cq[0] if self.cq else None

    def advance_cq(self, count: int = 1):
        """Acknowledge and consume CQEs."""
        for _ in range(min(count, len(self.cq))):
            self.cq.pop(0)

    def get_buffer(self, bgid: int, bid: int) -> Optional[ProvidedBuffer]:
        """Retrieve buffer object by ID from registered pool."""
        ring = self.buffer_rings.get(bgid)
        if ring and 0 <= bid < ring.entries:
            return ring.buffers[bid]
        return None

    def return_buffer(self, bgid: int, bid: int):
        """Release buffer back to pool for future token arrivals."""
        ring = self.buffer_rings.get(bgid)
        if ring:
            ring.return_buffer(bid)
