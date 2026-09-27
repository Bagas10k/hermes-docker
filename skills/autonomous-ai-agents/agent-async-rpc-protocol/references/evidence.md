# RPC architecture and evidence

Research scope: FRONTIER-002. Sources retrieved 2026-09-24 WIB. No production deployment or Hermes runtime modification.

## Primary sources
1. https://grpc.io/docs/guides/cancellation/ — cancellation signals loss of interest; application owns spawned work cleanup. Language behavior differs.
2. https://grpc.io/docs/guides/deadlines/ — no default deadline; remaining timeout propagation avoids remote clock skew.
3. https://grpc.github.io/grpc/python/grpc_asyncio.html — stable AsyncIO API backed by C-Core; objects are thread-affine and blocking handlers starve RPCs. Retrieved page labels itself 1.74.0; installed test runtime reported 1.84.0, so documentation/runtime versions are not identical.
4. https://capnproto.org/rpc.html — promise pipelining over capabilities; byte-stream RPC requires a separate secure transport layer. Inspect the linked rpc.capnp and calculator-client.c++ for actual production implementation, not marketing alone.
5. https://capnproto.org/encoding.html — aligned segments and relative pointers; encoding and RPC are distinct layers.
6. https://flatbuffers.dev/white_paper/ — offset-based in-place access, tables/vtables for schema evolution; structs trade away evolution flexibility.
7. https://flatbuffers.dev/benchmarks/ — benchmark fixture is Windows 7 C++, game-like object. Historical vendor ratios are NOT current agent throughput evidence; its comparisons contain dated platform claims.
8. https://docs.python.org/3/library/asyncio-task.html — structured cancellation and TaskGroup; use APIs available in target Python, not newer examples blindly.
9. https://flatbuffers.dev/languages/cpp/ — generated typed accessors over owned backing buffers. Production readers must verify untrusted buffers using the supported verifier; Python fixture below only reads self-built trusted data.

## Mechanism and mathematical bounds
T = T_queue + T_encode + T_transport + T_work + T_decode.
S = 1 / ((1-p) + p/s). Illustrative p=0.1 and serialization acceleration s=10 gives 1.098901x, computed by probe; NOT a measured application speedup.
Payload memory for bounded queue capacity Q and max payload B is at most Q*B, excluding object/runtime overhead, producers, transport windows and in-flight work. Add C*B for C owned active payloads; bound producer admission as well.
Little's law L=lambda*W describes stationary average occupancy, not a hard bound or a p99 guarantee.
Eligible k-stage promise pipelines remove round-trip waits, not causally required compute. Client inspection/branching on a returned value still needs that value.

## Architecture decision map
- gRPC + Protobuf: default candidate for interoperable typed streaming and deadlines; pays encoding/runtime overhead, earns mature tooling. Actual production requires generated schemas, mTLS/authorization and durable mutation ledger.
- Cap'n Proto RPC: candidate when remote capability dependency chains and network RTT dominate; verify binding support and transport security. Not benchmarked here.
- FlatBuffers + existing transport: candidate when bulk read-mostly payload decoding dominates; schema evolution, verifier support and lifetime ownership are mandatory.
- Shared memory: same-host trusted high-volume peers only after profiling. Lease/generation prevents stale reuse but does not stop malicious concurrent mutation. Synchronize publication and ACK/reclaim; crash cleanup and read-only mapping need dedicated integration tests. No lock-free/shared-memory implementation claimed here.
- Keep control and data budgets separate so a full data queue cannot starve cancellation. Retain idempotency/outcome reconciliation independent of transport selection.

## Bayesian experimental record
Prior qualitative hypothesis: explicit ownership cancels nested work; a client exception alone is insufficient evidence. Predictions before execution: direct cancellation and deadline set server cleanup events; parent cancellation sets child cleanup event; bounded producer blocks; oversized request is rejected; memoryview observes backing mutation.
Observation: all eight named assertions passed twice with grpcio 1.84.0 and flatbuffers 25.12.19 on Python 3.11. Tests use real loopback gRPC calls and a real FlatBuffers builder. No model/API responses were simulated as research output.
Checks: unary roundtrip; ordered server stream; direct cancellation cleanup; deadline cleanup; nested RPC cancellation cleanup; oversize rejection; bounded queue blocking; byte-vector view alias and mutability.
100 sequential 128-byte unary samples/run, nearest-rank quantiles in ms:
- Run 1: p50 1.58143, p95 2.20879, p99 2.42402.
- Run 2: p50 1.66139, p95 2.51441, p99 3.12749.
No baseline comparator, load sweep, RSS trace, WAN, TLS, or throughput experiment; do not infer speedup or capacity. Shutdown emitted a gRPC GOAWAY cancellation diagnostic; both process exits were zero and all cleanup assertions passed.
Known: tested local cancellation/queue/view behavior. Likely: explicit lifecycle ownership reduces orphan compute when integrated correctly. Uncertain: production p99, serialization payoff, shared-memory concurrency and deployment security. No numerical posterior without a measured likelihood model.
Stop rule: this bounded experiment resolves lifecycle mechanism, not stack migration; further platform selection requires real project profiles and approval.
