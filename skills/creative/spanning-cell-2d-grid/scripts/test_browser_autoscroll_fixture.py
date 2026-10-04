import unittest
from browser_autoscroll_fixture import render_fixture

class FixtureTests(unittest.TestCase):
    def test_default(self):
        html=render_fixture()
        self.assertIn('width:300px;height:200px',html)
        self.assertIn('requestAnimationFrame(frame)',html)
    def test_dimensions(self):
        self.assertIn('width:390px;height:500px',render_fixture(390,500))
    def test_bad_dimensions(self):
        for bad in (True,99,2001,float('nan'),'300',300.5):
            with self.subTest(bad=bad),self.assertRaises(ValueError):render_fixture(bad,200)
    def test_lifecycle_contract_present(self):
        html=render_fixture()
        for token in ('pointercancel','lostpointercapture','visibilitychange','releasePointerCapture','cancelAnimationFrame','dispose()'):
            self.assertIn(token,html)
    def test_isolated(self):
        self.assertNotIn('src="http',render_fixture())

if __name__=='__main__':unittest.main()
