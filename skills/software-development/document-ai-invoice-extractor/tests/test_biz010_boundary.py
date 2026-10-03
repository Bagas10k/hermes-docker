"""Unit tests for deterministic multi-invoice document boundary detection and page slicing (BIZ-010)."""
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from boundary_detector import MultiInvoiceBoundaryDetector


class TestMultiInvoiceBoundaryDetector(unittest.TestCase):
    def setUp(self):
        self.detector = MultiInvoiceBoundaryDetector(max_pages_per_invoice=5)

    def test_single_page_single_invoice(self):
        pages = [
            {'page': 1, 'raw': 'Invoice: INV-100\nCurrency: USD\nItem: Item A; 1; 10.00; 10.00\nSubtotal: 10.00\nTax: 0.00\nDiscount: 0.00\nTotal: 10.00\n'}
        ]
        result = self.detector.slice_document(pages)
        self.assertEqual(result['status'], 'single_invoice')
        self.assertEqual(len(result['segments']), 1)
        self.assertEqual(result['segments'][0]['invoice_id'], 'INV-100')
        self.assertEqual(result['segments'][0]['start_page'], 1)
        self.assertEqual(result['segments'][0]['end_page'], 1)
        self.assertFalse(result['issues'])

    def test_multi_invoice_sequential_slicing(self):
        pages = [
            {'page': 1, 'raw': 'Invoice: INV-001\nCurrency: USD\nItem: Item 1; 1; 5.00; 5.00\nSubtotal: 5.00\nTax: 0.00\nDiscount: 0.00\nTotal: 5.00\n'},
            {'page': 2, 'raw': 'Invoice: INV-002\nCurrency: USD\nItem: Item 2; 2; 10.00; 20.00\nSubtotal: 20.00\nTax: 2.00\nDiscount: 0.00\nTotal: 22.00\n'},
            {'page': 3, 'raw': 'Invoice: INV-003\nCurrency: USD\nItem: Item 3; 1; 15.00; 15.00\nSubtotal: 15.00\nTax: 1.00\nDiscount: 0.00\nTotal: 16.00\n'}
        ]
        result = self.detector.slice_document(pages)
        self.assertEqual(result['status'], 'multi_invoice_sliced')
        self.assertEqual(len(result['segments']), 3)
        self.assertEqual([s['invoice_id'] for s in result['segments']], ['INV-001', 'INV-002', 'INV-003'])
        self.assertEqual([s['start_page'] for s in result['segments']], [1, 2, 3])
        self.assertEqual([s['end_page'] for s in result['segments']], [1, 2, 3])
        self.assertFalse(result['issues'])

    def test_multi_page_invoices_continuous_span(self):
        pages = [
            # Invoice 1 spans page 1 and page 2
            {'page': 1, 'raw': 'Invoice: INV-SPAN-1\nCurrency: USD\nItem: Item 1; 1; 10.00; 10.00\nItem: Item 2; 1; 10.00; 10.00\n'},
            {'page': 2, 'raw': 'Item: Item 3; 1; 10.00; 10.00\nSubtotal: 30.00\nTax: 3.00\nDiscount: 0.00\nTotal: 33.00\n'},
            # Invoice 2 spans page 3
            {'page': 3, 'raw': 'Invoice: INV-SPAN-2\nCurrency: USD\nItem: Item A; 1; 5.00; 5.00\nSubtotal: 5.00\nTax: 0.00\nDiscount: 0.00\nTotal: 5.00\n'}
        ]
        result = self.detector.slice_document(pages)
        self.assertEqual(result['status'], 'multi_invoice_sliced')
        self.assertEqual(len(result['segments']), 2)
        seg1 = result['segments'][0]
        self.assertEqual(seg1['invoice_id'], 'INV-SPAN-1')
        self.assertEqual(seg1['start_page'], 1)
        self.assertEqual(seg1['end_page'], 2)
        self.assertEqual(seg1['page_count'], 2)

        seg2 = result['segments'][1]
        self.assertEqual(seg2['invoice_id'], 'INV-SPAN-2')
        self.assertEqual(seg2['start_page'], 3)
        self.assertEqual(seg2['end_page'], 3)
        self.assertFalse(result['issues'])

    def test_orphaned_preamble_pages_detected(self):
        pages = [
            {'page': 1, 'raw': 'Cover Letter / Preamble text\nNo invoice here\n'},
            {'page': 2, 'raw': 'Invoice: INV-COVER\nCurrency: USD\nItem: A; 1; 10.00; 10.00\nSubtotal: 10.00\nTax: 0.00\nDiscount: 0.00\nTotal: 10.00\n'}
        ]
        result = self.detector.slice_document(pages)
        self.assertEqual(result['status'], 'needs_review')
        codes = [iss['code'] for iss in result['issues']]
        self.assertIn('orphaned_preamble_pages', codes)
        self.assertEqual(result['segments'][0]['invoice_id'], 'INV-COVER')

    def test_multiple_headers_on_same_page_flagged(self):
        pages = [
            {'page': 1, 'raw': 'Invoice: INV-A\nInvoice: INV-B\nCurrency: USD\nTotal: 10.00\n'}
        ]
        result = self.detector.slice_document(pages)
        self.assertEqual(result['status'], 'needs_review')
        codes = [iss['code'] for iss in result['issues']]
        self.assertIn('multiple_headers_on_single_page', codes)

    def test_duplicate_invoice_identifiers_flagged(self):
        pages = [
            {'page': 1, 'raw': 'Invoice: INV-DUP\nCurrency: USD\nItem: A; 1; 10.00; 10.00\nSubtotal: 10.00\nTax: 0.00\nDiscount: 0.00\nTotal: 10.00\n'},
            {'page': 2, 'raw': 'Invoice: INV-DUP\nCurrency: USD\nItem: B; 1; 20.00; 20.00\nSubtotal: 20.00\nTax: 0.00\nDiscount: 0.00\nTotal: 20.00\n'}
        ]
        result = self.detector.slice_document(pages)
        self.assertEqual(result['status'], 'needs_review')
        codes = [iss['code'] for iss in result['issues']]
        self.assertIn('duplicate_invoice_identifier_in_bundle', codes)

    def test_missing_total_in_segment_flagged(self):
        pages = [
            {'page': 1, 'raw': 'Invoice: INV-NOTOTAL\nCurrency: USD\nItem: A; 1; 10.00; 10.00\nSubtotal: 10.00\n'}
        ]
        result = self.detector.slice_document(pages)
        self.assertEqual(result['status'], 'needs_review')
        codes = [iss['code'] for iss in result['issues']]
        self.assertIn('missing_total_in_segment', codes)

    def test_invoice_exceeds_max_page_limit_flagged(self):
        # Detector initialized with max_pages_per_invoice=5
        pages = [{'page': 1, 'raw': 'Invoice: INV-LONG\nCurrency: USD\n'}]
        for i in range(2, 8):  # 7 pages total
            pages.append({'page': i, 'raw': f'Item: Item {i}; 1; 1.00; 1.00\n'})
        pages[-1]['raw'] += 'Subtotal: 6.00\nTax: 0.00\nDiscount: 0.00\nTotal: 6.00\n'

        result = self.detector.slice_document(pages)
        self.assertEqual(result['status'], 'needs_review')
        codes = [iss['code'] for iss in result['issues']]
        self.assertIn('invoice_page_limit_exceeded', codes)

    def test_cli_detect_boundaries_flag_single_invoice(self):
        import subprocess
        import tempfile
        script = ROOT / 'scripts/extract_invoice.py'
        with tempfile.TemporaryDirectory() as d:
            doc = Path(d) / 'single.txt'
            doc.write_text('Invoice: INV-CLI-1\nCurrency: USD\nItem: A; 1; 10.00; 10.00\nSubtotal: 10.00\nTax: 0.00\nDiscount: 0.00\nTotal: 10.00\n')
            p = subprocess.run([sys.executable, str(script), str(doc), '--locale', 'en_US', '--detect-boundaries'],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(data['status'], 'single_invoice')
            self.assertEqual(len(data['segments']), 1)
            self.assertEqual(data['segments'][0]['invoice_id'], 'INV-CLI-1')

    def test_cli_detect_boundaries_flag_multi_invoice_review_on_anomaly(self):
        import subprocess
        import tempfile
        script = ROOT / 'scripts/extract_invoice.py'
        with tempfile.TemporaryDirectory() as d:
            doc = Path(d) / 'multi.txt'
            # Two invoices on single text file -> single page with multiple headers -> review
            doc.write_text('Invoice: INV-A\nTotal: 10.00\nInvoice: INV-B\nTotal: 20.00\n')
            p = subprocess.run([sys.executable, str(script), str(doc), '--locale', 'en_US', '--detect-boundaries'],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 2, p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(data['status'], 'needs_review')
            self.assertIn('multiple_headers_on_single_page', [iss['code'] for iss in data['issues']])


if __name__ == '__main__':
    unittest.main()
