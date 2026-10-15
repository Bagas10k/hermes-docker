import json
import re
import unittest
from pathlib import Path
from native_clipboard_fixture import fixture


class NativeClipboardFixtureTests(unittest.TestCase):
    def test_exact_independent_routes(self):
        data = fixture()
        manifest = json.loads(re.search(r'id="history-data">(.*?)</script>', data['html']).group(1))
        self.assertEqual(manifest['cursor'], data['initial']['id'])
        for case in ('initial', 'recovery'):
            node, route = data[case]['id'], []
            while node is not None:
                route.append(node)
                node = manifest['nodes'][node]['parent']
            self.assertEqual(' > '.join(reversed(route)), data[case]['text'])
        self.assertNotEqual(data['initial']['text'], data['recovery']['text'])

    def test_unmodified_native_adapter_and_escaped_data(self):
        html = fixture()['html']
        script = Path(__file__).with_name('history_browser.js').read_text()
        self.assertIn('<script>' + script + '</script>', html)
        self.assertIn('beta &amp; &lt;baru&gt;', html)
        self.assertIn('\\u003cbaru>', html)
        self.assertNotIn("Object.defineProperty(navigator", html)

    def test_deterministic_json_roundtrip(self):
        self.assertEqual(fixture(), fixture())
        self.assertEqual(json.loads(json.dumps(fixture())), fixture())

    def test_keyboard_metadata_and_accessible_markup(self):
        data = fixture()
        kb = data['keyboard']
        self.assertEqual(kb['activation_keys'], ['Enter', 'Space'])
        self.assertEqual(kb['copy_button_selector'], '.dag-breadcrumb-copy-btn')
        self.assertEqual(kb['status_selector'], '#status')
        html = data['html']
        self.assertIn('id="status" role="status" aria-live="polite"', html)
        self.assertIn('.dag-breadcrumb-copy-btn:focus-visible', html)
        self.assertIn('outline:2px solid #2563eb', html)

    def test_native_button_no_redundant_keyboard_listeners(self):
        script = Path(__file__).with_name('history_browser.js').read_text()
        self.assertNotIn("copyBtn.addEventListener('keydown'", script)
        self.assertNotIn("copyBtn.addEventListener('keyup'", script)
        self.assertNotIn("data-key-activated", script)


if __name__ == '__main__':
    unittest.main()
