import unittest
from byte_budget_history import ByteBudgetHistory, utf8_size, cell_bytes


class ByteBudgetTests(unittest.TestCase):
    def fingerprint(self, h):
        return (h.cursor, h.snapshot(), h.retained_bytes,
                {k: (v.parent, dict(v.delta), dict(v.state), h.children(k))
                 for k, v in h._nodes.items()})

    def test_utf8(self):
        for s in ('', 'ASCII', '\u00e9', '\u4e2d', '\U0001f642', 'a'*4095+'\u4e2d'*5000):
            self.assertEqual(utf8_size(s), len(s.encode('utf8')))

    def test_root_exact(self):
        h = ByteBudgetHistory({'a':'\u00e9'}, max_payload_bytes=7, max_retained_bytes=7)
        self.assertEqual(h.retained_bytes, 7)
        for kw in ({'max_payload_bytes':6}, {'max_retained_bytes':6}):
            with self.assertRaises(OverflowError): ByteBudgetHistory({'a':'\u00e9'}, **kw)

    def test_payload_boundary(self):
        h = ByteBudgetHistory(max_payload_bytes=8)
        h.commit('n','root',{'k':'\u00e9'})
        before = self.fingerprint(h)
        with self.assertRaises(OverflowError): h.commit('m','root',{'k':'\u4e2d'})
        self.assertEqual(before,self.fingerprint(h))

    def test_retained_exact_and_replay(self):
        h = ByteBudgetHistory(max_retained_bytes=15)
        h.commit('n','root',{'k':'\u00e9'})
        self.assertEqual(h.retained_bytes,15)
        h.undo()
        self.assertFalse(h.commit('n','root',{'k':'\u00e9'}))
        self.assertEqual(h.cursor,'root')
        before=self.fingerprint(h)
        with self.assertRaises(OverflowError): h.commit('m','root',{})
        self.assertEqual(before,self.fingerprint(h))

    def test_delete_and_empty(self):
        h=ByteBudgetHistory({'a':'abc'})
        h.commit('n','root',{'a':None,'b':''})
        self.assertEqual(h.snapshot(),{'b':''})
        self.assertEqual(h.retained_bytes,8+5+2+1)

    def test_navigation_keeps_accounting(self):
        h=ByteBudgetHistory()
        h.commit('a','root',{'x':'1'})
        h.commit('b','root',{'x':'2'},activate=False)
        size=h.retained_bytes
        h.undo(); h.redo('b'); h.checkout('a')
        self.assertEqual(h.retained_bytes,size)
        self.assertEqual(h.children('root'),('a','b'))

    def test_invalid_limits(self):
        for name in ('max_payload_bytes','max_retained_bytes'):
            for value in (0,-1,True,1.5,None):
                with self.assertRaises(ValueError): ByteBudgetHistory(**{name:value})

    def test_invalid_unicode_atomic(self):
        h=ByteBudgetHistory()
        before=self.fingerprint(h)
        for changes in ({'a':'\ud800'},{'\udfff':'a'}):
            with self.assertRaises(UnicodeEncodeError): h.commit('a','root',changes)
            self.assertEqual(before,self.fingerprint(h))

    def test_base_rejections_atomic(self):
        h=ByteBudgetHistory(max_nodes=2,max_cells=1)
        h.commit('a','root',{'x':'1'})
        before=self.fingerprint(h)
        for args in [('a','root',{'x':'2'}),('b','missing',{}),('b','root',{})]:
            with self.assertRaises((ValueError,OverflowError)): h.commit(*args)
            self.assertEqual(before,self.fingerprint(h))

    def test_oracle_each_commit(self):
        h=ByteBudgetHistory({'x':'\u4e2d'})
        for i in range(30):
            parent='root' if i%3==0 else str(i-1)
            h.commit(str(i),parent,{'x':None if i%2 else '\u00e9'*i,'y':''},activate=False)
            oracle=sum(len(k.encode()) + (0 if v.parent is None else len(v.parent.encode()))
                       + sum(len(a.encode())+(0 if b is None else len(b.encode())) for a,b in v.delta.items())
                       + sum(len(a.encode())+len(b.encode()) for a,b in v.state.items())
                       for k,v in h._nodes.items())
            self.assertEqual(h.retained_bytes,oracle)


if __name__ == '__main__': unittest.main()
