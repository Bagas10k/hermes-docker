import json
import subprocess
import sys
import unittest
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/extract_invoice.py'
FOLDER = ROOT / 'artifacts/biz003'
FOLDER.mkdir(parents=True, exist_ok=True)
TEXT = 'Invoice: INV-001\nCurrency: USD\nItem: Widget; 2; 10.00; 20.00\nSubtotal: 20.00\nTax: 2.00\nDiscount: 1.00\nTotal: 21.00\n'


def run(path, *args):
    return subprocess.run([sys.executable, str(SCRIPT), str(path), '--locale', 'en_US', *args], capture_output=True, text=True)


def image(lines, name):
    path = FOLDER / name
    im = Image.new('RGB', (1800, 850), 'white')
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 38)
    for n, line in enumerate(lines):
        draw.text((55, 45 + n * 100), line, fill='black', font=font)
    im.save(path)
    return path


class CoverageTests(unittest.TestCase):
    def test_real_scanned_pdf(self):
        scan = image(TEXT.splitlines(), 'scan.png')
        path = FOLDER / 'scan.pdf'
        c = Canvas(str(path), invariant=1)
        c.drawImage(str(scan), 0, 400, width=600, height=283.333)
        c.showPage()
        c.save()
        p = run(path)
        (FOLDER / 'scan-result.json').write_text(p.stdout)
        self.assertEqual(p.returncode, 2, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data['fields']['total']['value'], '21.00')
        self.assertFalse(data['source']['coverage_complete'])

    def test_text_plus_image_never_silently_passes(self):
        scan = image(['Total: 999.00'], 'conflict.png')
        path = FOLDER / 'conflict.pdf'
        c = Canvas(str(path), invariant=1)
        for n, line in enumerate(TEXT.splitlines()):
            c.drawString(40, 780 - n * 25, line)
        c.drawImage(str(scan), 0, 250, width=600, height=283.333)
        c.showPage()
        c.save()
        p = run(path)
        (FOLDER / 'conflict-result.json').write_text(p.stdout)
        self.assertEqual(p.returncode, 2, p.stderr)
        data = json.loads(p.stdout)
        record = data['source']['pages'][0]
        self.assertIn('Total: 21.00', record['native_raw'])
        self.assertEqual(record['ocr_reason'], 'image_bearing')
        self.assertTrue(any(x['code'] == 'pdf_coverage_unverified' for x in data['issues']))
        self.assertFalse(data['source']['coverage_complete'])

    def test_failed_ocr_is_operational_error(self):
        import os
        path = FOLDER / 'no-ocr.pdf'
        c = Canvas(str(path), invariant=1)
        c.showPage()
        c.save()
        p = subprocess.run([sys.executable, str(SCRIPT), str(path), '--locale', 'en_US'],
                           env={**os.environ, 'PATH': ''}, capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertEqual(p.stdout, '')
        self.assertIn('error:', p.stderr)

    def test_real_mixed_pdf_requires_review_and_preserves_coverage(self):
        scan = image(TEXT.splitlines()[3:], 'totals.png')
        path = FOLDER / 'mixed.pdf'
        c = Canvas(str(path), invariant=1)
        for n, line in enumerate(TEXT.splitlines()[:3]):
            c.drawString(40, 780 - n * 25, line)
        c.showPage()
        c.drawImage(str(scan), 0, 400, width=600, height=283.333)
        c.showPage()
        c.save()
        p = run(path)
        (FOLDER / 'mixed-result.json').write_text(p.stdout)
        self.assertEqual(p.returncode, 2, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data['fields']['total']['value'], '21.00')
        self.assertFalse(data['source']['coverage_complete'])
        self.assertEqual([x['method'] for x in data['source']['pages']], ['pdfplumber', 'pytesseract'])
        self.assertEqual(data['source']['pages'][1]['coverage'], 'ocr_unverified')
        self.assertEqual(data['fields']['total']['evidence'][0]['page'], 2)


class LimitsTests(unittest.TestCase):
    def test_timeout_kills_descendants(self):
        import importlib.util
        import os
        import time
        spec = importlib.util.spec_from_file_location('invoice', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(hasattr(module, 'supervise'), 'whole-document supervisor missing')
        pidfile = FOLDER / 'descendant.pid'
        pidfile.unlink(missing_ok=True)
        child = 'import time; time.sleep(120)'
        program = ('import subprocess,sys,time; from pathlib import Path; '
                   f'p=subprocess.Popen([sys.executable,"-c",{child!r}]); '
                   f'Path({str(pidfile)!r}).write_text(str(p.pid)); time.sleep(120)')
        start = time.monotonic()
        with self.assertRaisesRegex(TimeoutError, 'document timeout'):
            module.supervise([sys.executable, '-c', program], 1)
        self.assertLess(time.monotonic() - start, 5)
        pid = int(pidfile.read_text())
        for _ in range(50):
            status = Path(f'/proc/{pid}/stat')
            try:
                if not status.exists() or status.read_text().split()[2] == 'Z':
                    break
            except (ProcessLookupError, FileNotFoundError):
                break
            time.sleep(.02)
        else:
            os.kill(pid, 9)
            self.fail('descendant remained alive after document timeout')

    def test_cumulative_pixel_and_text_limits(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('invoice_limits', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        path = FOLDER / 'cumulative.pdf'
        c = Canvas(str(path), pagesize=(100, 100), invariant=1)
        for _ in range(2):
            c.showPage()
        c.save()
        module.MAX_TOTAL_PIXELS = 60000
        with self.assertRaisesRegex(ValueError, 'pixel limit'):
            module.read_source(path)
        path = FOLDER / 'cumulative-text.pdf'
        c = Canvas(str(path), invariant=1)
        for _ in range(2):
            c.drawString(40, 780, 'Invoice: X')
            c.showPage()
        c.save()
        module.MAX_TEXT = 15
        with self.assertRaisesRegex(ValueError, 'text limit'):
            module.read_source(path)

    def test_image_pixels_rejected(self):
        path = FOLDER / 'large.png'
        Image.new('1', (4000, 4000)).save(path)
        p = run(path)
        self.assertEqual(p.returncode, 1)
        self.assertIn('pixel limit', p.stderr)

    def test_text_budget_is_document_wide(self):
        path = FOLDER / 'text-limit.txt'
        path.write_text('x' * 200001)
        p = run(path)
        self.assertEqual(p.returncode, 1)
        self.assertIn('text limit', p.stderr)
        self.assertEqual(p.stdout, '')

    def test_page_limit(self):
        path = FOLDER / 'page-limit.pdf'
        c = Canvas(str(path), invariant=1)
        for _ in range(21):
            c.drawString(40, 780, 'Invoice: X')
            c.showPage()
        c.save()
        p = run(path)
        self.assertEqual(p.returncode, 1)
        self.assertIn('page limit', p.stderr)

    def test_pixels_rejected_before_render(self):
        path = FOLDER / 'pixel-limit.pdf'
        c = Canvas(str(path), pagesize=(10000, 10000), invariant=1)
        c.showPage()
        c.save()
        p = run(path)
        self.assertEqual(p.returncode, 1)
        self.assertIn('pixel limit', p.stderr)


if __name__ == '__main__':
    unittest.main()
