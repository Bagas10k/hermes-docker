"""Deterministic multi-invoice document boundary detection and page slicing.

Given a list of extracted page records (from text files, multi-page PDFs, or page streams),
detect where invoice boundaries occur, validate page continuity, detect overlapping / ambiguous
invoice headers, and partition/slice the document into discrete invoice segments.
"""
from dataclasses import dataclass, field
from decimal import Decimal
import re
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class InvoicePageSpan:
    invoice_id: str
    start_page: int
    end_page: int
    page_indices: List[int]  # 0-indexed page indices
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0
    issues: List[Dict[str, Any]] = field(default_factory=list)


class MultiInvoiceBoundaryDetector:
    """Detects multi-invoice boundaries across ordered document pages."""

    INVOICE_HEADER_PATTERN = re.compile(r'^\s*invoice\s*:\s*(\S.*?)\s*$', re.IGNORECASE)
    TOTAL_PATTERN = re.compile(r'^\s*total\s*:\s*(\S.*?)\s*$', re.IGNORECASE)

    def __init__(self, max_pages_per_invoice: int = 20, fuzzy_labels: bool = False, locale: str = "en_US"):
        self.max_pages_per_invoice = max_pages_per_invoice
        self.fuzzy_labels = fuzzy_labels
        self.locale = locale
        self.fuzzy_matcher = None
        if fuzzy_labels:
            from fuzzy_matcher import FuzzyLabelMatcher
            self.fuzzy_matcher = FuzzyLabelMatcher(locale=locale)

    def find_invoice_headers_on_page(self, page_text: str, page_num: int) -> List[Tuple[str, int, str]]:
        """Return list of (invoice_id, line_number, raw_line) found on page."""
        headers = []
        for line_num, line in enumerate(page_text.splitlines(), 1):
            m = self.INVOICE_HEADER_PATTERN.match(line)
            if m:
                inv_id = m.group(1).strip()
                headers.append((inv_id, line_num, line))
            elif self.fuzzy_matcher is not None and ':' in line:
                lbl, _, val = line.partition(':')
                match_res = self.fuzzy_matcher.classify_label(lbl.strip())
                if match_res.canonical_label == 'invoice' and val.strip():
                    inv_id = val.strip()
                    headers.append((inv_id, line_num, line))
        return headers

    def has_total_on_page(self, page_text: str) -> bool:
        """Return True if page contains a Total: scalar line."""
        for line in page_text.splitlines():
            if self.TOTAL_PATTERN.match(line):
                return True
            elif self.fuzzy_matcher is not None and ':' in line:
                lbl, _, val = line.partition(':')
                match_res = self.fuzzy_matcher.classify_label(lbl.strip())
                if match_res.canonical_label == 'total' and val.strip():
                    return True
        return False

    def slice_document(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Partition page records into discrete invoice segments.

        Parameters:
            pages: List of dicts with 'page' (1-indexed int) and 'raw' (str) text.

        Returns:
            Dict containing:
                - status: 'single_invoice', 'multi_invoice_sliced', or 'needs_review'
                - segments: List of sliced invoice segments with page spans and records
                - issues: List of detected boundary issues/anomalies
        """
        if not pages:
            return {
                'status': 'needs_review',
                'segments': [],
                'issues': [{'code': 'empty_document', 'message': 'No pages provided'}]
            }

        issues = []
        page_headers = {}  # page_idx -> list of headers
        for idx, p in enumerate(pages):
            p_num = p.get('page', idx + 1)
            raw = p.get('raw', '')
            headers = self.find_invoice_headers_on_page(raw, p_num)
            page_headers[idx] = headers

        # Collect pages that start a new invoice
        invoice_start_indices = []
        for idx, headers in page_headers.items():
            if len(headers) > 1:
                issues.append({
                    'code': 'multiple_headers_on_single_page',
                    'page': pages[idx].get('page', idx + 1),
                    'headers': [h[0] for h in headers]
                })
            elif len(headers) == 1:
                invoice_start_indices.append((idx, headers[0][0], headers[0]))

        # Case 1: No valid single invoice start found anywhere
        if not invoice_start_indices:
            if not issues:
                issues.append({'code': 'no_invoice_headers_found', 'message': 'Document contains zero Invoice: headers'})
            return {
                'status': 'needs_review',
                'segments': [],
                'issues': issues
            }

        # Case 2: Pages exist before the first invoice header
        first_start_idx = invoice_start_indices[0][0]
        if first_start_idx > 0:
            issues.append({
                'code': 'orphaned_preamble_pages',
                'pages': [pages[i].get('page', i + 1) for i in range(first_start_idx)]
            })

        # Build segments based on sequential start points
        segments = []
        total_starts = len(invoice_start_indices)

        for i in range(total_starts):
            start_idx, inv_id, header_info = invoice_start_indices[i]
            if i + 1 < total_starts:
                next_start_idx = invoice_start_indices[i + 1][0]
                end_idx = next_start_idx - 1
            else:
                end_idx = len(pages) - 1

            span_indices = list(range(start_idx, end_idx + 1))
            span_page_nums = [pages[x].get('page', x + 1) for x in span_indices]

            segment_issues = []
            if len(span_indices) > self.max_pages_per_invoice:
                segment_issues.append({
                    'code': 'invoice_page_limit_exceeded',
                    'invoice_id': inv_id,
                    'page_count': len(span_indices),
                    'limit': self.max_pages_per_invoice
                })

            # Check if segment has at least one total
            segment_has_total = any(self.has_total_on_page(pages[x].get('raw', '')) for x in span_indices)
            if not segment_has_total:
                segment_issues.append({
                    'code': 'missing_total_in_segment',
                    'invoice_id': inv_id,
                    'start_page': span_page_nums[0],
                    'end_page': span_page_nums[-1]
                })

            seg_records = [pages[x] for x in span_indices]
            segments.append({
                'invoice_id': inv_id,
                'start_page': span_page_nums[0],
                'end_page': span_page_nums[-1],
                'page_count': len(span_indices),
                'pages': seg_records,
                'header_evidence': {
                    'page': header_info[1] if len(header_info) > 3 else pages[start_idx].get('page', start_idx + 1),
                    'line': header_info[1],
                    'raw': header_info[2]
                },
                'issues': segment_issues
            })

        # Check for duplicate invoice IDs across document
        seen_ids = set()
        for seg in segments:
            iid = seg['invoice_id']
            if iid in seen_ids:
                issues.append({
                    'code': 'duplicate_invoice_identifier_in_bundle',
                    'invoice_id': iid
                })
            seen_ids.add(iid)

        # Aggregate issues
        for seg in segments:
            if seg['issues']:
                issues.extend(seg['issues'])

        if issues:
            status = 'needs_review'
        elif len(segments) == 1:
            status = 'single_invoice'
        else:
            status = 'multi_invoice_sliced'

        return {
            'status': status,
            'segments': segments,
            'issues': issues,
            'total_invoices_detected': len(segments)
        }
