# Offline API and example

Use Python 3.11+ and import the trusted `scripts/admission.py` library. With `terminal` workdir set to the skill's `scripts` directory, this complete example may be run by a trusted caller:

```python
import json
from admission import Registry, Rejected
manifest = json.dumps({
    'name': 'discounted_total',
    'inputs': ['price', 'qty', 'discount'],
    'program': '$price $qty * 100 $discount - * 100 //',
}).encode()
registry = Registry()
try:
    handle, digest = registry.admit(manifest, owner='alice', ttl=30, calls=2)
    result = registry.call(handle, owner='alice', arguments=b'{"price":1250,"qty":3,"discount":10}')
    assert result == 3375
    registry.revoke(handle, owner='alice')
finally:
    registry.close()
```

`price` is integer minor currency units; `discount` is integer percent. The application must independently enforce domain rules such as nonnegative quantities and discount in [0,100]. Generic numeric bounds are not domain validation.

## Manifest

Exactly three keys, UTF-8 JSON bytes, at most 4096 bytes:
- `name`: lowercase ASCII identifier, 1–32 characters, starts with letter.
- `inputs`: 1–8 distinct identifiers of the same form.
- `program`: whitespace-separated reverse-Polish tokens. `$name` pushes a declared argument, a decimal integer pushes a bounded constant; `+ - * // min max` pop two values and push one result. No comments, calls, attributes, loops, branches, exponentiation or implicit conversions.

Arguments: JSON object bytes with exactly all input names and exact integers. No optional/default values. Only one integer result is returned. `//` floors towards negative infinity, not towards zero. Digest normalizes whitespace by hashing the instruction sequence plus policy/name/inputs; it does not identify source whitespace or certify authorship.

## Registry

- `Registry(clock=time.monotonic)`: trusted injectable monotonic clock for deterministic tests. No clock selected from manifest.
- `admit(raw, owner=..., ttl=..., calls=...) -> (handle, digest)`: fail-closed validation, new capability even for identical manifests. Same-name tools never shadow by name because resolution uses handles.
- `call(handle, owner=..., arguments=...) -> int`: authorized attempts consume quota even on argument/arithmetic failure. Quota reaching zero removes the entry.
- `revoke(handle, owner=...)`: rejects missing/expired/wrong-owner capability; removes live one.
- `size()`: lazily purges expired entries and returns active count.
- `close()`: clears entries, permanently denies admission/calls; idempotent.

All expected invalid inputs raise `Rejected`, a `ValueError` subclass. Host API controls and clock are trusted. `compile_tool(raw) -> Tool` and `evaluate(tool, raw_args)` are available for offline validation/tests; do not accept untrusted Python objects through this lower-level API.

The registry is memory-only and process-local. There is no automatic finalizer or persistent history. Call `close` in `finally`; an exception does not magically trigger application cleanup. No global name registration, Hermes plugin registration, network server, or MCP mutation occurs.
