import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from prune import plan


def row(i='a', **kw):
    r = dict(id=i, scope='p:v1', key='retry', value='bounded', source='trace:1',
             protected=False, stale=False, verified=True)
    r.update(kw)
    return r

class Tests(unittest.TestCase):
    def test_deterministic_and_no_mutation(self):
        rows = [row('b'), row('a')]
        before = copy.deepcopy(rows)
        self.assertEqual(plan(rows,'p:v1',4096), plan(rows[::-1],'p:v1',4096))
        self.assertEqual(rows, before)
    def test_duplicate(self):
        r = plan([row('b'),row('a')],'p:v1',4096)
        self.assertEqual(r['selected'], ['a'])
        self.assertEqual(r['decisions']['b'], 'duplicate:a')
    def test_conflict(self):
        r = plan([row('a'),row('b',value='unbounded')],'p:v1',4096)
        self.assertEqual(set(r['decisions'].values()), {'conflict'})
    def test_protected_conflict(self):
        with self.assertRaises(ValueError):
            plan([row(protected=True),row('b',value='unbounded')],'p:v1',4096)
    def test_filters(self):
        r = plan([row('a',stale=True),row('b',verified=False),row('c',scope='other')],'p:v1',4096)
        self.assertEqual(r['decisions'],dict(a='stale',b='unverified',c='out_of_scope'))
    def test_protected_budget(self):
        with self.assertRaises(ValueError): plan([row(protected=True)],'p:v1',0)
    def test_budget(self):
        r = plan([row(value='aman-é')],'p:v1',4096)
        n = r['bytes']
        self.assertEqual(n,len(r['context'].encode('utf-8')))
        self.assertEqual(plan([row(value='aman-é')],'p:v1',n)['selected'],['a'])
        self.assertEqual(plan([row(value='aman-é')],'p:v1',n-1)['selected'],[])
    def test_bad_schema(self):
        for rows in ([row(),row()], [row(verified='yes')], [row(source='')], [row(extra=1)], [row(protected=True,stale=True)], {}):
            with self.subTest(rows=rows), self.assertRaises(ValueError): plan(rows,'p:v1',4096)
    def test_all_ids_accounted(self):
        rows = [row(str(i),key=str(i)) for i in range(100)]
        r = plan(rows,'p:v1',512)
        self.assertEqual(len(r['decisions']),len(rows))
        self.assertLessEqual(r['bytes'],512)
    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'episodes.json'
            p.write_text(json.dumps([row()]))
            before=hashlib.sha256(p.read_bytes()).hexdigest()
            cmd=[sys.executable,str(Path(__file__).with_name('prune.py')),str(p),'--scope','p:v1','--budget','4096']
            ok=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(ok.returncode,0,ok.stderr)
            self.assertEqual(json.loads(ok.stdout)['selected'],['a'])
            self.assertEqual(before,hashlib.sha256(p.read_bytes()).hexdigest())
            p.write_text('{bad')
            bad=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(bad.returncode,2)
            self.assertEqual(bad.stdout,'')
            self.assertTrue(bad.stderr)

if __name__ == '__main__': unittest.main(verbosity=2)
