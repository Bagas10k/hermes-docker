"""Deterministic branch navigation contracts; no network simulation claims."""
import unittest
from branch_history import BranchHistory

class BranchTests(unittest.TestCase):
    def test_branch_preserved(self):
        h = BranchHistory(); h.commit('a', 'root', {'A1': '1'}); h.commit('b', 'a', {'A1': '2'})
        h.undo(); h.commit('c', 'a', {'B1': '3'})
        self.assertEqual(h.children('a'), ('b', 'c'))
        self.assertEqual(h.checkout('b'), {'A1': '2'})
        self.assertEqual(h.checkout('c'), {'A1': '1', 'B1': '3'})
    def test_explicit_redo(self):
        h = BranchHistory(); h.commit('a','root',{}); h.commit('b','a',{}); h.undo(); h.commit('c','a',{}); h.undo()
        with self.assertRaises(ValueError): h.redo()
        self.assertEqual(h.cursor,'a'); h.redo('b'); self.assertEqual(h.cursor,'b')
    def test_remote_does_not_move_cursor(self):
        h = BranchHistory(); h.commit('a','root',{'A1':'local'})
        h.commit('r','root',{'A1':'remote'}, activate=False)
        self.assertEqual(h.cursor,'a'); self.assertEqual(h.snapshot(),{'A1':'local'})
    def test_idempotent_and_collision(self):
        h = BranchHistory(); h.commit('a','root',{'A1':'1'}); h.checkout('root')
        self.assertFalse(h.commit('a','root',{'A1':'1'}))
        self.assertEqual(h.cursor,'root')
        with self.assertRaises(ValueError): h.commit('a','root',{'A1':'2'})
    def test_missing_parent_and_self_cycle(self):
        h = BranchHistory()
        for parent in ['missing','a']:
            with self.assertRaises(ValueError): h.commit('a',parent,{})
        self.assertEqual(h.children('root'),())
    def test_copies_and_deletion(self):
        initial={'A1':''}; h=BranchHistory(initial); initial['A1']='bad'
        delta={'A1':None,'B1':'=A1'}; h.commit('a','root',delta); delta['B1']='bad'
        state=h.snapshot(); state['B1']='bad'
        self.assertEqual(h.snapshot(),{'B1':'=A1'}); self.assertEqual(h.undo(),{'A1':''})
    def test_path(self):
        h=BranchHistory(); h.commit('a','root',{}); h.commit('b','a',{}); h.commit('c','root',{}); h.commit('d','c',{})
        self.assertEqual(h.route('b','d'),{'lca':'root','undo':('b','a'),'redo':('c','d')})
        self.assertEqual(h.route('a','a'),{'lca':'a','undo':(),'redo':()})
    def test_bounds_atomic(self):
        h=BranchHistory(max_nodes=2,max_cells=1); h.commit('a','root',{'A1':'1'})
        with self.assertRaises(OverflowError): h.commit('b','a',{})
        self.assertEqual(h.children('a'),()); self.assertEqual(h.cursor,'a')
        h=BranchHistory(max_cells=1)
        with self.assertRaises(OverflowError): h.commit('a','root',{'A1':'1','B1':'2'})
        self.assertEqual(h.children('root'),())
    def test_invalid_input(self):
        for n in [True,0,-1,1.5]:
            with self.assertRaises(ValueError): BranchHistory(max_nodes=n)
        h=BranchHistory()
        for delta in [{'A1':5},{'': 'x'}, {'A1':float('nan')}]:
            with self.assertRaises(ValueError): h.commit('a','root',delta)
        with self.assertRaises(ValueError): h.commit('a','root',{},activate=1)
        with self.assertRaises(ValueError): h.checkout('missing')
        self.assertEqual(h.cursor,'root')
    def test_navigation_boundaries(self):
        h=BranchHistory(); self.assertEqual(h.undo(),{}); self.assertEqual(h.redo(),{})
        h.commit('a','root',{}); h.commit('b','root',{})
        with self.assertRaises(ValueError): h.redo('a')
        self.assertEqual(h.cursor,'b')
    def test_delivery_orders(self):
        import itertools
        for order in itertools.permutations(['b','c','d']):
            h=BranchHistory(); h.commit('a','root',{'A1':'base'})
            for name in order: h.commit(name,'a',{'A1':name},activate=False)
            self.assertEqual(h.children('a'),('b','c','d'))
            for name in order: self.assertEqual(h.checkout(name),{'A1':name})
    def test_deep_iterative(self):
        h=BranchHistory(max_nodes=1501,max_cells=1)
        parent='root'
        for i in range(1500):
            name=str(i); h.commit(name,parent,{'A1':name}); parent=name
        self.assertEqual(len(h.route(parent,'root')['undo']),1500)
        self.assertEqual(h.checkout('root'),{})

if __name__=='__main__': unittest.main()
