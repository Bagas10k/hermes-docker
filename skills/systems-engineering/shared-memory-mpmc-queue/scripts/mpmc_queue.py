#!/usr/bin/env python3
"""
Lock-Free MPMC (Multi-Producer Multi-Consumer) Bounded Ring-Buffer
Mengimplementasikan algoritma antrean bebas-kunci (Vyukov MPMC Bounded Queue)
dengan sequence-based synchronization dan power-of-two bitwise wrapping untuk transmisi data antar-agen.
"""

import ctypes
import multiprocessing as mp
import threading
import time
from typing import Any, Optional, Tuple, List

class MPMCSlot:
    """Satu slot pada cincin antrean dengan nomor sekuens atomik dan muatan data."""
    def __init__(self, initial_seq: int):
        self.sequence = mp.RawValue(ctypes.c_uint64, initial_seq)
        # 256-byte payload buffer per slot untuk zero-allocation messaging
        self.payload = mp.RawArray(ctypes.c_char, 256)
        self.length = mp.RawValue(ctypes.c_uint32, 0)

class LockFreeMPMCQueue:
    """
    Vyukov MPMC Bounded Queue.
    Mendukung N-Producer dan M-Consumer konkuren secara aman tanpa mutex/lock pada jalur data.
    """
    def __init__(self, capacity: int = 64):
        # Kapasitas wajib power-of-two (2^N)
        if capacity < 2 or (capacity & (capacity - 1)) != 0:
            raise ValueError(f"Kapasitas ({capacity}) wajib merupakan power of two (>= 2)")
        
        self.capacity = capacity
        self.mask = capacity - 1
        
        # Alokasikan slot dengan sequence = index
        self.slots = [MPMCSlot(i) for i in range(capacity)]
        
        # Monotonically increasing atomic indices
        self.enqueue_pos = mp.RawValue(ctypes.c_uint64, 0)
        self.dequeue_pos = mp.RawValue(ctypes.c_uint64, 0)
        
        # Lock internal khusus untuk operasi CAS atomik di lingkungan Python
        self._cas_lock = mp.Lock()

    def _atomic_cas_enqueue(self, expected: int, new_val: int) -> bool:
        with self._cas_lock:
            if self.enqueue_pos.value == expected:
                self.enqueue_pos.value = new_val
                return True
            return False

    def _atomic_cas_dequeue(self, expected: int, new_val: int) -> bool:
        with self._cas_lock:
            if self.dequeue_pos.value == expected:
                self.dequeue_pos.value = new_val
                return True
            return False

    def push(self, data: bytes) -> bool:
        """
        Menambahkan item ke antrean (Multi-Producer safe).
        Mengembalikan True jika sukses, False jika kapasitas penuh.
        """
        if len(data) > 256:
            raise ValueError("Data melebihi batas slot maksimum (256 bytes)")
        
        while True:
            pos = self.enqueue_pos.value
            slot = self.slots[pos & self.mask]
            seq = slot.sequence.value
            dif = seq - pos
            
            if dif == 0:
                if self._atomic_cas_enqueue(pos, pos + 1):
                    # Tulis data ke slot
                    slot.payload[:len(data)] = data
                    slot.length.value = len(data)
                    # Publikasikan sekuens baru (menandakan slot siap dibaca)
                    slot.sequence.value = pos + 1
                    return True
            elif dif < 0:
                # Antrean penuh (backpressure)
                return False
            # Jika dif > 0, produser lain telah mengambil slot ini, ulangi loop

    def pop(self) -> Optional[bytes]:
        """
        Mengambil item dari antrean (Multi-Consumer safe).
        Mengembalikan bytes jika ada data, None jika antrean kosong.
        """
        while True:
            pos = self.dequeue_pos.value
            slot = self.slots[pos & self.mask]
            seq = slot.sequence.value
            dif = seq - (pos + 1)
            
            if dif == 0:
                if self._atomic_cas_dequeue(pos, pos + 1):
                    # Baca data dari slot
                    length = slot.length.value
                    data = bytes(slot.payload[:length])
                    # Perbarui sekuens slot untuk putaran berikutnya
                    slot.sequence.value = pos + self.mask + 1
                    return data
            elif dif < 0:
                # Antrean kosong
                return None
            # Jika dif > 0, konsumen lain telah mengambil item ini, ulangi loop

    def is_empty(self) -> bool:
        return self.dequeue_pos.value >= self.enqueue_pos.value

    def approximate_size(self) -> int:
        enq = self.enqueue_pos.value
        deq = self.dequeue_pos.value
        return max(0, enq - deq)

if __name__ == "__main__":
    q = LockFreeMPMCQueue(capacity=16)
    q.push(b"AGENT_MSG_1")
    q.push(b"AGENT_MSG_2")
    print("Pop:", q.pop())
    print("Pop:", q.pop())
    print("Pop empty:", q.pop())
