import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/extract_invoice.py'
TEXT = 'Invoice: INV-001\nCurrency: USD\nItem: Widget; 2; 10.00; 20.00\nSubtotal: 20.00\nTax: 2.00\nDiscount: 1.00\nTotal: 21.00\n'

class InvoiceTests(unittest.TestCase):
    def run_text(self, text=TEXT, locale='en_US'):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'invoice.txt'
            p.write_text(text)
            return subprocess.run([sys.executable, str(SCRIPT), str(p), '--locale', locale], capture_output=True, text=True)

    def test_unverifiable_documents_need_review(self):
        cases = [TEXT.replace('Total: 21.00', 'Total: 22.00'),
                 TEXT.replace('2; 10.00; 20.00', '3; 10.00; 20.00'),
                 TEXT.replace('Subtotal: 20.00', 'Subtotal: 19.00'),
                 TEXT.replace('Tax: 2.00\n', ''),
                 TEXT + 'Total: 21.00\n', TEXT + 'Total: 22.00\n',
                 TEXT.replace('Invoice: INV-001', 'Bank Statement: INV-001'),
                 TEXT + 'Service fee: 50.00\n', '',
                 TEXT.replace('20.00', 'NaN'), TEXT.replace('USD', 'EUR'),
                 TEXT.replace('2; 10.00', '-2; -10.00')]
        for text in cases:
            with self.subTest(text=text):
                p = self.run_text(text)
                self.assertEqual(p.returncode, 2, p.stderr)
                data = json.loads(p.stdout)
                self.assertEqual(data['status'], 'needs_review')
                self.assertTrue(data['issues'])
        data = json.loads(self.run_text(TEXT + 'Total: 21.00\n').stdout)
        self.assertIsNone(data['fields']['total']['value'])
        self.assertEqual(len(data['fields']['total']['evidence']), 2)

    def test_locale_and_rounding(self):
        for locale, price, amount in [('en_US', '1,234.565', '2,469.13'), ('id_ID', '1.234,565', '2.469,13')]:
            with self.subTest(locale=locale):
                text = f'Invoice: R1\nCurrency: IDR\nItem: Part; 2; {price}; {amount}\nSubtotal: {amount}\nTax: 0\nDiscount: 0\nTotal: {amount}\n'
                p = self.run_text(text, locale)
                self.assertEqual(p.returncode, 0, p.stderr)
                data = json.loads(p.stdout)
                self.assertEqual(data['lines'][0]['expected_amount'], '2469.13')
        for token in ('1,23.00', '1.234,56', '1e2', 'Infinity', '1 000', '+10', '1000000000000'):
            self.assertEqual(self.run_text(TEXT.replace('10.00', token)).returncode, 2)

    def test_pdf_real_extraction(self):
        from reportlab.pdfgen.canvas import Canvas
        folder = ROOT / 'artifacts/fixtures'
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / 'invoice.pdf'
        canvas = Canvas(str(path), invariant=1)
        for index, chunk in enumerate((TEXT.splitlines()[:3], TEXT.splitlines()[3:])):
            for n, line in enumerate(chunk):
                canvas.drawString(40, 780 - n * 25, line)
            canvas.showPage()
        canvas.save()
        p = subprocess.run([sys.executable, str(SCRIPT), str(path), '--locale', 'en_US'], capture_output=True, text=True)
        (folder.parent / 'pdf-result.json').write_text(p.stdout)
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data['fields']['total']['value'], '21.00')
        self.assertEqual(data['fields']['total']['evidence'][0]['page'], 2)
        self.assertEqual(data['source']['method'], 'pdfplumber')
        self.assertEqual(len(data['source']['pages']), 2)

    def test_image_real_ocr(self):
        from PIL import Image, ImageDraw, ImageFont
        folder = ROOT / 'artifacts/fixtures'
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / 'invoice.png'
        image = Image.new('RGB', (1800, 850), 'white')
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 38)
        for n, line in enumerate(TEXT.splitlines()):
            draw.text((55, 45 + n * 100), line, fill='black', font=font)
        image.save(path)
        p = subprocess.run([sys.executable, str(SCRIPT), str(path), '--locale', 'en_US'], capture_output=True, text=True)
        (folder.parent / 'ocr-result.json').write_text(p.stdout)
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data['source']['method'], 'pytesseract')
        self.assertEqual(data['fields']['total']['value'], '21.00')
        self.assertEqual(data['fields']['invoice']['value'], 'INV-001')
        self.assertEqual(data['lines'][0]['amount'], '20.00')
        self.assertIn('Total: 21.00', data['source']['pages'][0]['raw'])

    def test_operational_errors(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            for name, content in [('bad.pdf', b'bad'), ('bad.png', b'bad'), ('wrong.csv', TEXT.encode()), ('big.txt', b'x' * (2 * 1024 * 1024 + 1))]:
                path = folder / name
                path.write_bytes(content)
                p = subprocess.run([sys.executable, str(SCRIPT), str(path), '--locale', 'en_US'], capture_output=True, text=True)
                self.assertEqual(p.returncode, 1)
                self.assertEqual(p.stdout, '')
                self.assertIn('error:', p.stderr)
                self.assertNotIn('Traceback', p.stderr)
            p = subprocess.run([sys.executable, str(SCRIPT), str(folder / 'missing.txt')], capture_output=True, text=True)
            self.assertEqual(p.returncode, 1)

    def test_blank_pdf_page_requires_review(self):
        from reportlab.pdfgen.canvas import Canvas
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'blank.pdf'
            canvas = Canvas(str(path), invariant=1)
            for n, line in enumerate(TEXT.splitlines()):
                canvas.drawString(40, 780 - n * 25, line)
            canvas.showPage()
            canvas.showPage()
            canvas.save()
            p = subprocess.run([sys.executable, str(SCRIPT), str(path), '--locale', 'en_US'], capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertIn('empty_page', p.stdout)

    def test_text_invoice_provenance(self):
        p = self.run_text()
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data['status'], 'arithmetic_consistent')
        self.assertEqual(data['fields']['total']['value'], '21.00')
        self.assertEqual(data['fields']['total']['evidence'], [{'page': 1, 'line': 7, 'raw': 'Total: 21.00'}])
        self.assertEqual(data['lines'][0]['expected_amount'], '20.00')

if __name__ == '__main__':
    unittest.main()
