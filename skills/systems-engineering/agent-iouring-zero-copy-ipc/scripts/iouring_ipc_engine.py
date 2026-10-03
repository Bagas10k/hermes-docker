#!/usr/bin/env python3
"""
Linux io_uring Zero-Copy IPC & SQ/CQ Ring Buffer Engine for Agent RPC
Mengimplementasikan arsitektur asynchronous Submission Queue (SQ) dan Completion Queue (CQ)
dengan zero-copy buffer slicing dan batching untuk komunikasi antar-agen berlatensi ultra-rendah.
"""

import os
import socket
import struct
import errno
from typing import List, Optional, Tuple, Dict, Any

# Opcode I/O URING Primitives
IORING_OP_NOP = 0
IORING_OP_READV = 1
IORING_OP_WRITEV = 2
IORING_OP_SOCKET_SEND = 3
IORING_OP_SOCKET_RECV = 4

class SQE:
    """Submission Queue Entry (64 bytes aligned representation)."""
    __slots__ = ("opcode", "fd", "buffer", "length", "user_data")
    
    def __init__(self, opcode: int, fd: int, buffer: Optional[memoryview], length: int, user_data: int):
        self.opcode = opcode
        self.fd = fd
        self.buffer = buffer
        self.length = length
        self.user_data = user_data

class CQE:
    """Completion Queue Entry (16 bytes aligned representation)."""
    __slots__ = ("user_data", "res", "flags")
    
    def __init__(self, user_data: int, res: int, flags: int = 0):
        self.user_data = user_data
        self.res = res  # Return code: bytes transferred atau -errno
        self.flags = flags

class IOUringIPCEngine:
    """
    Simulasi arsitektur ring buffer io_uring di Linux dengan zero-copy memoryview.
    Memisahkan jalur Submission (SQ) dan Completion (CQ) dengan operasi batch enter.
    """
    def __init__(self, entries: int = 64):
        # Ukuran ring buffer wajib power-of-two untuk bitwise wrapping
        if entries & (entries - 1) != 0:
            raise ValueError(f"Entries ({entries}) wajib merupakan power of two (2^N)")
        
        self.ring_size = entries
        self.ring_mask = entries - 1
        
        # SQ Ring
        self.sq_entries: List[Optional[SQE]] = [None] * entries
        self.sq_head = 0
        self.sq_tail = 0
        
        # CQ Ring
        self.cq_entries: List[Optional[CQE]] = [None] * (entries * 2)
        self.cq_mask = (entries * 2) - 1
        self.cq_head = 0
        self.cq_tail = 0
        
        # Registry socket objects by fileno untuk zero-syscall socket I/O
        self._sock_registry: Dict[int, socket.socket] = {}

    def register_socket(self, sock: socket.socket):
        sock.setblocking(False)
        self._sock_registry[sock.fileno()] = sock

    def unregister_socket(self, sock: socket.socket):
        self._sock_registry.pop(sock.fileno(), None)

    def prep_nop(self, user_data: int) -> bool:
        """Menyiapkan NOP operation (benchmark ring overhead)."""
        sqe = SQE(IORING_OP_NOP, -1, None, 0, user_data)
        return self._push_sqe(sqe)

    def prep_send(self, fd: int, data: bytes, user_data: int) -> bool:
        """Menyiapkan asynchronous zero-copy socket send."""
        mv = memoryview(data)
        sqe = SQE(IORING_OP_SOCKET_SEND, fd, mv, len(data), user_data)
        return self._push_sqe(sqe)

    def prep_recv(self, fd: int, length: int, user_data: int) -> bool:
        """Menyiapkan asynchronous socket recv."""
        sqe = SQE(IORING_OP_SOCKET_RECV, fd, None, length, user_data)
        return self._push_sqe(sqe)

    def _push_sqe(self, sqe: SQE) -> bool:
        """Memasukkan SQE ke antrean submission (producer side)."""
        if (self.sq_tail - self.sq_head) >= self.ring_size:
            return False  # SQ Full
        
        idx = self.sq_tail & self.ring_mask
        self.sq_entries[idx] = sqe
        self.sq_tail += 1
        return True

    def _push_cqe(self, cqe: CQE) -> bool:
        """Memasukkan CQE ke antrean completion (kernel side)."""
        if (self.cq_tail - self.cq_head) >= len(self.cq_entries):
            return False  # CQ Overflow
        
        idx = self.cq_tail & self.cq_mask
        self.cq_entries[idx] = cqe
        self.cq_tail += 1
        return True

    def submit_and_wait(self, min_complete: int = 0) -> int:
        """
        Meniru io_uring_enter(2):
        Memproses seluruh SQE yang ada di antrean dalam satu batch syscall-less loop,
        lalu menghasilkan CQE yang sesuai.
        """
        submitted = 0
        
        while self.sq_head < self.sq_tail:
            idx = self.sq_head & self.ring_mask
            sqe = self.sq_entries[idx]
            self.sq_entries[idx] = None
            self.sq_head += 1
            submitted += 1
            
            if sqe is None:
                continue
                
            # Proses operasi secara asinkron/non-blocking
            if sqe.opcode == IORING_OP_NOP:
                self._push_cqe(CQE(user_data=sqe.user_data, res=0))
            
            elif sqe.opcode == IORING_OP_SOCKET_SEND:
                sock = self._sock_registry.get(sqe.fd)
                if not sock:
                    self._push_cqe(CQE(user_data=sqe.user_data, res=-errno.EBADF))
                else:
                    try:
                        sent = sock.send(sqe.buffer)
                        self._push_cqe(CQE(user_data=sqe.user_data, res=sent))
                    except BlockingIOError:
                        self._push_cqe(CQE(user_data=sqe.user_data, res=-errno.EAGAIN))
                    except Exception as ex:
                        self._push_cqe(CQE(user_data=sqe.user_data, res=-errno.EIO))
            
            elif sqe.opcode == IORING_OP_SOCKET_RECV:
                sock = self._sock_registry.get(sqe.fd)
                if not sock:
                    self._push_cqe(CQE(user_data=sqe.user_data, res=-errno.EBADF))
                else:
                    try:
                        recv_data = sock.recv(sqe.length)
                        # Simpan data di CQE flags atau struktur hasil
                        self._push_cqe(CQE(user_data=sqe.user_data, res=len(recv_data)))
                    except BlockingIOError:
                        self._push_cqe(CQE(user_data=sqe.user_data, res=-errno.EAGAIN))
                    except Exception as ex:
                        self._push_cqe(CQE(user_data=sqe.user_data, res=-errno.EIO))
            
            else:
                self._push_cqe(CQE(user_data=sqe.user_data, res=-errno.ENOSYS))

        return submitted

    def peek_cqe(self) -> Optional[CQE]:
        """Membaca CQE terdepan tanpa mengeluarkannya."""
        if self.cq_head >= self.cq_tail:
            return None
        idx = self.cq_head & self.cq_mask
        return self.cq_entries[idx]

    def advance_cq(self, count: int = 1):
        """Memajukan head completion queue setelah consumer membaca hasil."""
        self.cq_head = min(self.cq_head + count, self.cq_tail)

    def get_pending_sq(self) -> int:
        return self.sq_tail - self.sq_head

    def get_available_cq(self) -> int:
        return self.cq_tail - self.cq_head

if __name__ == "__main__":
    # Smoke test dasar
    ring = IOUringIPCEngine(entries=32)
    s1, s2 = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
    ring.register_socket(s1)
    ring.register_socket(s2)
    
    ring.prep_send(s1.fileno(), b"PING_AGENT_RPC", user_data=101)
    ring.submit_and_wait()
    
    cqe = ring.peek_cqe()
    print("CQE Result:", cqe.user_data, cqe.res)
    ring.advance_cq(1)
    
    s1.close()
    s2.close()
