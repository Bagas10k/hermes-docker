import json
import unittest
from unittest.mock import patch
from byte_budget_history import ByteBudgetHistory
from history_persistence import dump_history, load_history, restore_history


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.h = ByteBudgetHistory({'A': 'é'})
        self.h.commit('z', 'root', {'B': ''})
        self.h.commit('a', 'z', {'A': None})
        self.h.commit('sibling', 'root', {'C': '中文'}, activate=False)
        self.raw = dump_history(self.h)

    def reject(self, raw, **kwargs):
        before, identity = dump_history(self.h), self.h.__dict__
        with self.assertRaises((ValueError, OverflowError)):
            restore_history(self.h, raw, **kwargs)
        self.assertIs(self.h.__dict__, identity)
        self.assertEqual(dump_history(self.h), before)

    def test_roundtrip_all_branches_accounting(self):
        new = load_history(self.raw)
        self.assertEqual(new.cursor, self.h.cursor)
        self.assertEqual(new.retained_bytes, self.h.retained_bytes)
        for key in self.h._nodes:
            self.assertEqual(new.checkout(key), self.h.checkout(key))
            self.assertEqual(new.children(key), self.h.children(key))
        self.assertEqual(dump_history(new), dump_history(self.h))

    def test_wire_cap_before_parser(self):
        with patch('history_persistence.json.loads', side_effect=AssertionError('parsed')):
            self.reject(self.raw, max_wire_bytes=len(self.raw)-1)
        self.assertEqual(dump_history(load_history(self.raw, max_wire_bytes=len(self.raw))), self.raw)

    def test_export_exact_cap(self):
        self.assertEqual(dump_history(self.h, max_wire_bytes=len(self.raw)), self.raw)
        with self.assertRaises(OverflowError):
            dump_history(self.h, max_wire_bytes=len(self.raw)-1)

    def test_bad_encoding_and_syntax(self):
        for raw in (b'\xff', b'{', b'[]', b'null', b'{"version":1,"version":1}', b'['*1500):
            with self.subTest(raw=raw[:30]):
                self.reject(raw)

    def test_duplicate_nested_keys(self):
        raw = b'{"version":1,"initial":{"A":"1","A":"2"},"cursor":"root","nodes":[]}'
        self.reject(raw)

    def test_schema_corruption(self):
        base = json.loads(self.raw)
        for field, value in [('version', True), ('version', 2), ('nodes', {}),
                             ('cursor', 'absent'), ('initial', {'A': None})]:
            obj = dict(base, **{field: value})
            self.reject(json.dumps(obj).encode())
        self.reject(json.dumps(dict(base, retained_bytes=0)).encode())
        self.reject(self.raw.replace(b'"version":1', b'"version":NaN'))
        self.reject(self.raw.replace(b'"version":1', b'"version":Infinity'))

    def test_graph_corruption(self):
        for nodes in ([{'id':'x','parent':'absent','changes':{}}],
                      [{'id':'x','parent':'x','changes':{}}],
                      [{'id':'x','parent':'y','changes':{}}, {'id':'y','parent':'x','changes':{}}],
                      [{'id':'root','parent':'root','changes':{}}],
                      [{'id':'x','parent':'root','changes':{}}]*2):
            obj = json.loads(self.raw)
            obj['nodes'] = nodes
            self.reject(json.dumps(obj).encode())

    def test_late_failure_preserves_target(self):
        obj = json.loads(self.raw)
        obj['nodes'].append({'id':'late','parent':'a','changes':{'A': 42}})
        self.reject(json.dumps(obj).encode())
        obj['nodes'][-1]['changes'] = {'A': '\ud800'}
        self.reject(json.dumps(obj).encode())

    def test_receiver_caps_not_payload_caps(self):
        for options in ({'max_nodes':2}, {'max_cells':1}, {'max_payload_bytes':8},
                        {'max_retained_bytes':8}):
            target = ByteBudgetHistory(**options)
            before = target.__dict__
            with self.assertRaises(OverflowError):
                restore_history(target, self.raw)
            self.assertIs(target.__dict__, before)

    def test_success_replacement_and_navigation(self):
        target = ByteBudgetHistory({'OLD':'removed'})
        self.assertIs(restore_history(target, self.raw), target)
        self.assertEqual(target.snapshot(), {'B':''})
        target.undo()
        self.assertEqual(target.cursor, 'z')
        target.redo('a')
        self.assertEqual(target.retained_bytes, self.h.retained_bytes)
        self.assertFalse(target.commit('a','z',{'A':None}))

    def test_invalid_arguments(self):
        for cap in (True, 0, -1, 1.1):
            self.reject(self.raw, max_wire_bytes=cap)
        for raw in ('{}', bytearray(b'{}'), None):
            self.reject(raw)

    def test_deep_unordered_history(self):
        h = ByteBudgetHistory(max_nodes=1300)
        parent = 'root'
        for i in range(1200):
            key = str(i)
            h.commit(key, parent, {'A': key})
            parent = key
        raw = dump_history(h)
        new = load_history(raw, max_nodes=1300)
        self.assertEqual(new.snapshot(), h.snapshot())
        self.assertEqual(new.retained_bytes, h.retained_bytes)


if __name__ == '__main__':
    unittest.main()
