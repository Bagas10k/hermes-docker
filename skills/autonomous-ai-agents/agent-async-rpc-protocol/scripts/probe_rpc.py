"""Sandbox integration evidence only; no external services or mutations."""
import asyncio
import importlib.metadata
import json
import math
import struct
import time

import flatbuffers
import grpc


async def main():
    passed = []
    events = {}

    async def work(request, context):
        key = request.decode('ascii')
        started, stopped = events.setdefault(key, (asyncio.Event(), asyncio.Event()))
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            stopped.set()

    async def echo(request, context):
        return request

    async def stream(request, context):
        for i in range(3):
            yield str(i).encode()
            await asyncio.sleep(0)

    server = grpc.aio.server(options=[('grpc.max_receive_message_length', 1024)])
    channel = None
    child = None
    try:
        # Outgoing RPC lifetime is explicitly owned by its parent handler.
        async def parent(request, context):
            nonlocal child
            remaining = context.time_remaining()
            child = channel.unary_unary('/probe/Work')(b'child', timeout=remaining)
            try:
                return await child
            finally:
                child.cancel()

        server.add_generic_rpc_handlers((grpc.method_handlers_generic_handler('probe', {
            'Echo': grpc.unary_unary_rpc_method_handler(echo),
            'Work': grpc.unary_unary_rpc_method_handler(work),
            'Parent': grpc.unary_unary_rpc_method_handler(parent),
            'Stream': grpc.unary_stream_rpc_method_handler(stream),
        }),))
        port = server.add_insecure_port('127.0.0.1:0')
        assert port
        await server.start()
        channel = grpc.aio.insecure_channel(f'127.0.0.1:{port}')
        await asyncio.wait_for(channel.channel_ready(), 5)
        call = channel.unary_unary('/probe/Echo')
        assert await call(b'hello', timeout=2) == b'hello'
        passed.append('unary_roundtrip')
        assert [v async for v in channel.unary_stream('/probe/Stream')(b'', timeout=2)] == [b'0', b'1', b'2']
        passed.append('ordered_stream')
        events['direct'] = (asyncio.Event(), asyncio.Event())
        pending = channel.unary_unary('/probe/Work')(b'direct', timeout=2)
        await asyncio.wait_for(events['direct'][0].wait(), 2)
        assert pending.cancel()
        try:
            await pending
            raise AssertionError('cancel returned success')
        except asyncio.CancelledError:
            pass
        await asyncio.wait_for(events['direct'][1].wait(), 2)
        passed.append('direct_cancel_cleanup')
        events['deadline'] = (asyncio.Event(), asyncio.Event())
        try:
            await channel.unary_unary('/probe/Work')(b'deadline', timeout=0.1)
            raise AssertionError('deadline returned success')
        except grpc.aio.AioRpcError as exc:
            assert exc.code() == grpc.StatusCode.DEADLINE_EXCEEDED
        await asyncio.wait_for(events['deadline'][1].wait(), 2)
        passed.append('deadline_cleanup')
        events['child'] = (asyncio.Event(), asyncio.Event())
        pending = channel.unary_unary('/probe/Parent')(b'', timeout=3)
        await asyncio.wait_for(events['child'][0].wait(), 2)
        pending.cancel()
        try:
            await pending
        except asyncio.CancelledError:
            pass
        await asyncio.wait_for(events['child'][1].wait(), 2)
        passed.append('nested_rpc_cancel_cleanup')
        try:
            await call(b'x' * 2048, timeout=2)
            raise AssertionError('oversize accepted')
        except grpc.aio.AioRpcError as exc:
            assert exc.code() == grpc.StatusCode.RESOURCE_EXHAUSTED
        passed.append('oversize_rejection')
        q = asyncio.Queue(maxsize=1)
        await q.put(b'a')
        producer = asyncio.create_task(q.put(b'b'))
        await asyncio.sleep(0)
        assert not producer.done() and q.qsize() == 1
        assert await q.get() == b'a'
        await asyncio.wait_for(producer, 1)
        assert await q.get() == b'b'
        passed.append('bounded_queue_backpressure')
        builder = flatbuffers.Builder(64)
        vector = builder.CreateByteVector(b'agent')
        builder.Finish(vector)
        buffer = builder.Output()  # Output construction may copy; claim only view access.
        root = struct.unpack_from('<I', buffer, 0)[0]
        size = struct.unpack_from('<I', buffer, root)[0]
        view = memoryview(buffer)[root + 4:root + 4 + size]
        assert bytes(view) == b'agent' and view.obj is buffer
        buffer[root + 4] = ord('A')
        assert bytes(view) == b'Agent'
        view.release()
        passed.append('flatbuffers_view_alias_and_mutability')
        samples = []
        for _ in range(100):
            begin = time.perf_counter()
            assert await call(b'x' * 128, timeout=2) == b'x' * 128
            samples.append((time.perf_counter() - begin) * 1000)
        samples.sort()
        percentiles = {f'p{p}': samples[math.ceil(p / 100 * len(samples)) - 1] for p in (50, 95, 99)}
        print(json.dumps({'checks': passed, 'count': len(passed), 'grpcio': importlib.metadata.version('grpcio'), 'flatbuffers': importlib.metadata.version('flatbuffers'), 'loopback_unary_128_bytes_ms': percentiles, 'samples': len(samples), 'amdahl_example_serialization_fraction_0.1_speedup_10': 1 / (0.9 + 0.1 / 10)}, indent=2))
    finally:
        if child is not None:
            child.cancel()
        if channel is not None:
            await channel.close()
        await server.stop(0)


if __name__ == '__main__':
    asyncio.run(main())
