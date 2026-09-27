"""Offline tests: candidate strings are data, never Python execution."""
import importlib.util
import json
from pathlib import Path
import unittest

MODULE = Path(__file__).with_name('admission.py')

def spec(program='$x 2 *', inputs=None):
    return json.dumps({'name': 'score', 'inputs': inputs if inputs is not None else ['x'], 'program': program}).encode()

class CompilerTests(unittest.TestCase):
    def test_compiler_exists_and_evaluates(self):
        self.assertTrue(MODULE.exists(), 'bounded compiler not implemented')
        import admission as a
        tool = a.compile_tool(spec())
        self.assertEqual(a.evaluate(tool, b'{"x":21}'), 42)

class RegistryTests(unittest.TestCase):
    def test_lifetime(self):
        import admission as a
        self.assertTrue(hasattr(a, 'Registry'), 'ephemeral registry missing')
        now = [100.0]
        r = a.Registry(clock=lambda: now[0])
        h, digest = r.admit(spec(), owner='alice', ttl=5, calls=2)
        self.assertEqual(r.call(h, owner='alice', arguments=b'{"x":3}'), 6)
        with self.assertRaises(a.Rejected):
            r.call(h, owner='bob', arguments=b'{"x":3}')
        now[0] = 105.0
        with self.assertRaises(a.Rejected):
            r.call(h, owner='alice', arguments=b'{"x":3}')
        self.assertEqual(r.size(), 0)

class NegativeTests(unittest.TestCase):
    def test_hostile_programs_rejected(self):
        import admission as a
        for text in ["__import__('os').system('id')", 'open(/etc/passwd)', '$x.__class__', '$y', '1 2 **', 'while True', '1 +', '1 2', '']:
            with self.subTest(text=text), self.assertRaises(a.Rejected):
                a.compile_tool(spec(text))

    def test_manifest_schema_and_json(self):
        import admission as a
        for raw in [b'[]', b'{"name":"a","name":"b"}', b'{}', b'\xff', b'['*1000, b' '*4097,
                    spec('1', ['x','x']), spec('1', []), spec('1', ['X']),
                    b'{"name":"a","inputs":["x"],"program":"1","permissions":["network"]}']:
            with self.subTest(raw=raw[:80]), self.assertRaises(a.Rejected):
                a.compile_tool(raw)

    def test_program_budgets(self):
        import admission as a
        for text in ['1000000000001', '1 '*17+'+ '*16, '$x '+'1 + '*32]:
            with self.subTest(text=text), self.assertRaises(a.Rejected):
                a.compile_tool(spec(text))

    def test_argument_types_and_keys(self):
        import admission as a
        t = a.compile_tool(spec())
        for raw in [b'{}', b'{"x":1,"y":2}', b'{"x":true}', b'{"x":1.0}', b'{"x":"1"}',
                    b'{"x":NaN}', b'{"x":1,"x":2}', b'{"x":1000000000001}', b'{"x":[]}', b' '*4097]:
            with self.subTest(raw=raw[:80]), self.assertRaises(a.Rejected):
                a.evaluate(t, raw)

    def test_arithmetic_failures(self):
        import admission as a
        for text in ['$x 0 //', '$x 1000000000000 *', '$x 1000000000000 +']:
            with self.subTest(text=text), self.assertRaises(a.Rejected):
                a.evaluate(a.compile_tool(spec(text)), b'{"x":2}')

    def test_all_ops_and_floor_semantics(self):
        import admission as a
        for text, expected in [('$x 3 +', 10), ('$x 3 -',4), ('$x 3 *',21),
                               ('$x 3 //',2), ('$x 3 min',3), ('$x 3 max',7), ('-7 3 //',-3)]:
            self.assertEqual(a.evaluate(a.compile_tool(spec(text)), b'{"x":7}'), expected)

    def test_digest_and_frozen_instructions(self):
        import admission as a
        from dataclasses import FrozenInstanceError
        t = a.compile_tool(spec())
        self.assertEqual(t.digest, a.compile_tool(spec(' $x   2 * ')).digest)
        self.assertNotEqual(t.digest, a.compile_tool(spec('$x 3 *')).digest)
        with self.assertRaises(FrozenInstanceError): t.name = 'changed'

    def test_quota_failed_attempt_and_wrong_owner(self):
        import admission as a
        r = a.Registry()
        h, _ = r.admit(spec(), owner='alice', ttl=5, calls=1)
        with self.assertRaises(a.Rejected): r.call(h, owner='bob', arguments=b'{"x":1}')
        with self.assertRaises(a.Rejected): r.call(h, owner='alice', arguments=b'{"x":true}')
        with self.assertRaises(a.Rejected): r.call(h, owner='alice', arguments=b'{"x":1}')
        self.assertEqual(r.size(), 0)

    def test_revoke_close_and_registry_scope(self):
        import admission as a
        r = a.Registry()
        h, _ = r.admit(spec(), owner='alice', ttl=5, calls=2)
        with self.assertRaises(a.Rejected): a.Registry().call(h, owner='alice', arguments=b'{"x":1}')
        with self.assertRaises(a.Rejected): r.revoke(h, owner='bob')
        r.revoke(h, owner='alice')
        with self.assertRaises(a.Rejected): r.call(h, owner='alice', arguments=b'{"x":1}')
        r.admit(spec(), owner='alice', ttl=5, calls=1)
        r.close()
        self.assertEqual(r.size(), 0)
        with self.assertRaises(a.Rejected): r.admit(spec(), owner='alice', ttl=5, calls=1)

    def test_policy_limits(self):
        import admission as a
        r = a.Registry()
        for ttl in [0, -1, 301, True, float('nan'), float('inf')]:
            with self.subTest(ttl=ttl), self.assertRaises(a.Rejected): r.admit(spec(), owner='alice', ttl=ttl, calls=1)
        for count in [0, 101, True, 1.1]:
            with self.subTest(count=count), self.assertRaises(a.Rejected): r.admit(spec(), owner='alice', ttl=1, calls=count)
        with self.assertRaises(a.Rejected): r.admit(spec(), owner='../alice', ttl=1, calls=1)

    def test_capacity_and_expiry_reclaim(self):
        import admission as a
        now = [0]
        r = a.Registry(clock=lambda: now[0])
        for _ in range(32): r.admit(spec(), owner='alice', ttl=1, calls=1)
        with self.assertRaises(a.Rejected): r.admit(spec(), owner='alice', ttl=1, calls=1)
        now[0] = 1
        r.admit(spec(), owner='alice', ttl=1, calls=1)
        self.assertEqual(r.size(), 1)

    def test_concurrent_quota(self):
        import admission as a
        from concurrent.futures import ThreadPoolExecutor
        r = a.Registry()
        h, _ = r.admit(spec(), owner='alice', ttl=300, calls=7)
        def invoke(_):
            try: return r.call(h, owner='alice', arguments=b'{"x":1}')
            except a.Rejected: return None
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(invoke, range(40)))
        self.assertEqual(results.count(2), 7)
        self.assertEqual(r.size(), 0)

    def test_formula_grid(self):
        import admission as a
        t = a.compile_tool(spec('$price $qty * 100 $discount - * 100 //', ['price','qty','discount']))
        for price in range(0, 101, 10):
            for qty in range(1, 6):
                for discount in [0, 10, 50, 100]:
                    raw = json.dumps(dict(price=price,qty=qty,discount=discount)).encode()
                    self.assertEqual(a.evaluate(t, raw), price*qty*(100-discount)//100)

if __name__ == '__main__':
    unittest.main()
