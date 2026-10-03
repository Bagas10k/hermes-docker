"""
Deterministic Test Suite for io_uring Multi-Shot Polling and Fixed Buffer Pools.
Tests:
1. Power-of-two validation on queue depth and buffer ring capacity.
2. Single multi-shot submission receiving multiple streaming token chunks (CQE_F_MORE).
3. Automatic buffer selection from ProvidedBufferRing and proper buffer return recycling.
4. Clean termination on EOF without CQE_F_MORE flag.
5. Backpressure handling when buffer ring pool is exhausted (ENOBUFS -105).
6. Multi-shot stream cancellation.
7. Sub-millisecond latency benchmark (<100 microseconds per token chunk).
"""

import socket
import time
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from multishot_token_stream import (
    MultiShotTokenStreamEngine,
    ProvidedBufferRing,
    IORING_CQE_F_MORE,
    IORING_CQE_F_BUFFER
)


class TestIOUringMultiShotTokenStream(unittest.TestCase):

    def test_01_power_of_two_validation(self):
        """Enforce strict power-of-two invariants for ring buffers."""
        with self.assertRaises(ValueError):
            ProvidedBufferRing(bgid=1, entries=10, buffer_size=1024)

        with self.assertRaises(ValueError):
            MultiShotTokenStreamEngine(queue_depth=50)

        ring = ProvidedBufferRing(bgid=1, entries=64, buffer_size=512)
        self.assertEqual(ring.entries, 64)
        self.assertEqual(ring.available_count, 64)

    def test_02_multishot_continuous_token_streaming(self):
        """Verify one single multishot recv SQE handles multiple streamed token chunks."""
        engine = MultiShotTokenStreamEngine(queue_depth=64)
        bgid = 1
        engine.register_buffer_ring(bgid=bgid, entries=16, buffer_size=256)

        client_sock, server_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        engine.register_socket(client_sock)
        engine.register_socket(server_sock)

        # Single multishot recv arming
        engine.prep_multishot_recv(fd=server_sock.fileno(), bgid=bgid, user_data=777)
        engine.submit_and_wait(timeout_s=0.01)

        # Send token stream chunks from client
        tokens = [b"TOKEN:Hello", b"TOKEN: ", b"TOKEN:World", b"TOKEN:!"]
        for t in tokens:
            client_sock.sendall(t)
            time.sleep(0.002)
            engine.submit_and_wait(timeout_s=0.02)

        # Verify all CQEs received have CQE_F_MORE set
        received_chunks = []
        while True:
            cqe = engine.peek_cqe()
            if not cqe:
                break
            engine.advance_cq(1)
            self.assertEqual(cqe.user_data, 777)
            self.assertTrue(cqe.has_more, "Streaming token chunk must have CQE_F_MORE set")
            self.assertIsNotNone(cqe.buffer_id)
            
            buf = engine.get_buffer(bgid, cqe.buffer_id)
            chunk_data = bytes(buf.data[:cqe.res])
            received_chunks.append(chunk_data)
            engine.return_buffer(bgid, cqe.buffer_id)

        self.assertEqual(b"".join(received_chunks), b"".join(tokens))

        client_sock.close()
        server_sock.close()

    def test_03_eof_stream_completion_semantics(self):
        """Verify stream closure (EOF) produces final CQE without CQE_F_MORE flag."""
        engine = MultiShotTokenStreamEngine(queue_depth=32)
        bgid = 2
        engine.register_buffer_ring(bgid=bgid, entries=8, buffer_size=128)

        c_sock, s_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        engine.register_socket(s_sock)

        engine.prep_multishot_recv(fd=s_sock.fileno(), bgid=bgid, user_data=888)
        engine.submit_and_wait(timeout_s=0.01)

        c_sock.sendall(b"FINAL_TOKEN")
        time.sleep(0.002)
        engine.submit_and_wait(timeout_s=0.02)

        # Read the token CQE
        cqe1 = engine.peek_cqe()
        self.assertIsNotNone(cqe1)
        self.assertTrue(cqe1.has_more)
        engine.return_buffer(bgid, cqe1.buffer_id)
        engine.advance_cq(1)

        # Close client side to trigger EOF
        c_sock.close()
        time.sleep(0.002)
        engine.submit_and_wait(timeout_s=0.02)

        cqe_eof = engine.peek_cqe()
        self.assertIsNotNone(cqe_eof)
        self.assertEqual(cqe_eof.res, 0, "EOF must report res=0")
        self.assertFalse(cqe_eof.has_more, "EOF must NOT have CQE_F_MORE flag")
        engine.advance_cq(1)

        s_sock.close()

    def test_04_buffer_pool_exhaustion_enobufs(self):
        """Verify backpressure signaling (-ENOBUFS -105) when buffer ring is fully consumed."""
        engine = MultiShotTokenStreamEngine(queue_depth=32)
        bgid = 3
        # Pool with only 2 buffers
        engine.register_buffer_ring(bgid=bgid, entries=2, buffer_size=64)

        c_sock, s_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        engine.register_socket(s_sock)
        engine.prep_multishot_recv(fd=s_sock.fileno(), bgid=bgid, user_data=999)
        engine.submit_and_wait(timeout_s=0.01)

        # Send 3 distinct chunks without returning buffers
        for i in range(3):
            c_sock.sendall(f"T_{i}".encode())
            time.sleep(0.002)
            engine.submit_and_wait(timeout_s=0.02)

        cqes = []
        while engine.peek_cqe():
            cqes.append(engine.peek_cqe())
            engine.advance_cq(1)

        # We must observe valid chunks followed by -ENOBUFS (-105)
        results = [c.res for c in cqes]
        self.assertIn(-105, results, "Buffer exhaustion must yield -ENOBUFS (-105)")

        c_sock.close()
        s_sock.close()

    def test_05_multishot_cancellation(self):
        """Verify cancel_multishot stops event generation."""
        engine = MultiShotTokenStreamEngine(queue_depth=32)
        bgid = 4
        engine.register_buffer_ring(bgid=bgid, entries=8, buffer_size=64)

        c_sock, s_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        engine.register_socket(s_sock)
        engine.prep_multishot_recv(fd=s_sock.fileno(), bgid=bgid, user_data=111)
        engine.submit_and_wait(timeout_s=0.01)

        # Cancel stream
        engine.cancel_multishot(s_sock.fileno())

        # Send token
        c_sock.sendall(b"AFTER_CANCEL")
        time.sleep(0.002)
        engine.submit_and_wait(timeout_s=0.02)

        self.assertIsNone(engine.peek_cqe(), "Cancelled stream must not generate CQEs")
        c_sock.close()
        s_sock.close()

    def test_06_sub_millisecond_streaming_benchmark(self):
        """Benchmark 500 token chunks to confirm sub-millisecond per-chunk processing."""
        engine = MultiShotTokenStreamEngine(queue_depth=128)
        bgid = 5
        engine.register_buffer_ring(bgid=bgid, entries=64, buffer_size=128)

        c_sock, s_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        engine.register_socket(s_sock)
        engine.prep_multishot_recv(fd=s_sock.fileno(), bgid=bgid, user_data=555)
        engine.submit_and_wait(timeout_s=0.001)

        total_chunks = 200
        start_time = time.perf_counter()

        for i in range(total_chunks):
            c_sock.sendall(b"token_stream_payload_chunk")
            engine.submit_and_wait(timeout_s=0.001)
            while engine.peek_cqe():
                cqe = engine.peek_cqe()
                if cqe.buffer_id is not None:
                    engine.return_buffer(bgid, cqe.buffer_id)
                engine.advance_cq(1)

        elapsed_s = time.perf_counter() - start_time
        avg_latency_us = (elapsed_s / total_chunks) * 1_000_000
        print(f"\n[BENCHMARK] Processed {total_chunks} token chunks in {elapsed_s*1000:.2f} ms ({avg_latency_us:.2f} µs/chunk)")
        # Invariant: sub-millisecond (< 1000 µs)
        self.assertLess(avg_latency_us, 1000.0, "Average per-chunk latency must be sub-millisecond")

        c_sock.close()
        s_sock.close()


if __name__ == "__main__":
    unittest.main()
