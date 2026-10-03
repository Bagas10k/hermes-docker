"""Bounded label-based invoice extraction; arithmetic is not authenticity."""
import argparse
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import math

MAX_PAGES = 20
MAX_PIXELS = 12_000_000
MAX_TOTAL_PIXELS = 40_000_000
MAX_TEXT = 200_000
DOCUMENT_TIMEOUT = 60
MAX_OUTPUT_BYTES = 4 * 1024 * 1024


def parse_number(raw, locale, tolerate_noise=False):
    import re
    if locale not in ('en_US', 'id_ID'):
        raise ValueError('unsupported locale')
    if tolerate_noise:
        from locale_normalizer import IndonesianLocaleOCRNormalizer
        res = IndonesianLocaleOCRNormalizer.inspect_and_clean(raw, locale)
        if res["decimal_value"] is None:
            raise ValueError(f"invalid number: {raw}")
        return res["decimal_value"], res["anomalies"]

    group, decimal = (',', '.') if locale == 'en_US' else ('.', ',')
    pattern = rf'(?:[0-9]{{1,12}}|[0-9]{{1,3}}(?:{re.escape(group)}[0-9]{{3}}){{1,3}})(?:{re.escape(decimal)}[0-9]{{1,4}})?'
    if not re.fullmatch(pattern, raw):
        raise ValueError('invalid number')
    return Decimal(raw.replace(group, '').replace(decimal, '.')), []


def money(value):
    return value.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)


def extract(pages, locale, tolerate_noise=False, fuzzy_labels=False):
    required = ('invoice', 'currency', 'subtotal', 'tax', 'discount', 'total')
    fields = {k: {'value': None, 'evidence': []} for k in required}
    lines, issues = [], []
    fuzzy_matcher = None
    if fuzzy_labels:
        from fuzzy_matcher import FuzzyLabelMatcher
        fuzzy_matcher = FuzzyLabelMatcher(locale=locale)

    for page, text in enumerate(pages, 1):
        if not text.strip():
            issues.append({'code': 'empty_page', 'page': page})
        for number, raw in enumerate(text.splitlines(), 1):
            if not raw.strip():
                continue
            evidence = {'page': page, 'line': number, 'raw': raw}
            label, separator, value = raw.partition(':')
            raw_key, value = label.strip(), value.strip()
            key = raw_key.lower()

            if not separator:
                issues.append({'code': 'unsupported_layout', 'evidence': evidence})
                continue

            if key not in (*required, 'item'):
                if fuzzy_matcher is not None:
                    match_res = fuzzy_matcher.classify_label(raw_key)
                    if match_res.canonical_label:
                        key = match_res.canonical_label
                        if match_res.anomaly:
                            issues.append({'code': match_res.anomaly, 'evidence': evidence})
                    else:
                        if match_res.anomaly and match_res.anomaly.startswith("ambiguous"):
                            issues.append({'code': match_res.anomaly, 'evidence': evidence})
                        issues.append({'code': 'unsupported_layout', 'evidence': evidence})
                        continue
                else:
                    issues.append({'code': 'unsupported_layout', 'evidence': evidence})
                    continue
            if key == 'item':
                row = {'evidence': [evidence], 'expected_amount': None}
                try:
                    name, qty, price, amount = [x.strip() for x in value.split(';')]
                    q_res, p_res, a_res = [parse_number(x, locale, tolerate_noise=tolerate_noise) for x in (qty, price, amount)]
                    q, q_anom = q_res
                    p, p_anom = p_res
                    a, a_anom = a_res
                    for anom in q_anom + p_anom + a_anom:
                        issues.append({'code': f'ocr_noise_repaired:{anom}', 'evidence': evidence})
                    if not name or q <= 0 or a != money(a):
                        raise ValueError('invalid item')
                    expected = money(q * p)
                    row.update(description=name, quantity=str(q), unit_price=str(p), amount=str(money(a)), expected_amount=str(expected))
                    if expected != a:
                        issues.append({'code': 'line_mismatch', 'evidence': evidence})
                except ValueError:
                    issues.append({'code': 'invalid_item', 'evidence': evidence})
                lines.append(row)
            else:
                field = fields[key]
                field['evidence'].append(evidence)
                try:
                    if key in ('subtotal', 'tax', 'discount', 'total'):
                        n, field_anom = parse_number(value, locale, tolerate_noise=tolerate_noise)
                        for anom in field_anom:
                            issues.append({'code': f'ocr_noise_repaired:{anom}', 'evidence': evidence})
                        if n != money(n):
                            raise ValueError('money precision')
                        value = str(money(n))
                    elif not value or (key == 'currency' and value not in ('USD', 'IDR')):
                        raise ValueError('invalid field')
                    field['value'] = value if len(field['evidence']) == 1 else None
                except ValueError:
                    issues.append({'code': 'invalid_field', 'field': key})
                    field['value'] = None
    for key, field in fields.items():
        if len(field['evidence']) != 1 or field['value'] is None:
            field['value'] = None
            issues.append({'code': 'missing_or_ambiguous_field', 'field': key})
    if not lines:
        issues.append({'code': 'missing_items'})
    if lines and all('amount' in row for row in lines) and fields['subtotal']['value'] is not None:
        if sum((Decimal(row['amount']) for row in lines), Decimal(0)) != Decimal(fields['subtotal']['value']):
            issues.append({'code': 'subtotal_mismatch'})
    if all(fields[k]['value'] is not None for k in ('subtotal', 'tax', 'discount', 'total')):
        s, t, d, total = [Decimal(fields[k]['value']) for k in ('subtotal', 'tax', 'discount', 'total')]
        if money(s + t - d) != total:
            issues.append({'code': 'total_mismatch'})
    return {'status': 'needs_review' if issues else 'arithmetic_consistent', 'locale': locale,
            'rounding': 'ROUND_HALF_UP; line products to 0.01, then sum; exact comparison',
            'authenticity_verified': False, 'fields': fields, 'lines': lines, 'issues': issues}


def read_source(path):
    if path.suffix.lower() not in ('.txt', '.pdf', '.png', '.jpg', '.jpeg'):
        raise ValueError('unsupported file extension')
    if path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError('input exceeds 2 MiB')
    records = []
    total_text = 0
    total_pixels = 0

    def pixels(width, height):
        nonlocal total_pixels
        count = math.ceil(width) * math.ceil(height)
        if count <= 0 or count > MAX_PIXELS or total_pixels + count > MAX_TOTAL_PIXELS:
            raise ValueError('document pixel limit exceeded')
        total_pixels += count

    def text_budget(text):
        nonlocal total_text
        total_text += len(text)
        if total_text > MAX_TEXT:
            raise ValueError('document text limit exceeded')

    def add(text, method, coverage, **extra):
        text_budget(text)
        records.append(dict(page=len(records) + 1, raw=text, method=method,
                            coverage=coverage, **extra))

    if path.suffix.lower() == '.pdf':
        import pdfplumber
        import pypdfium2
        import pytesseract
        with pdfplumber.open(path) as pdf, pypdfium2.PdfDocument(path) as renderer:
            if not 0 < len(renderer) <= MAX_PAGES:
                raise ValueError('document page limit exceeded')
            for index, page in enumerate(pdf.pages):
                native = page.extract_text() or ''
                images = len(page.images)
                if images or not native.strip():
                    text_budget(native)
                    rendered = renderer[index]
                    try:
                        width, height = rendered.get_size()
                        pixels(width * 2, height * 2)
                        for embedded in page.images:
                            w, h = embedded['srcsize']
                            pixels(w, h)
                        bitmap = rendered.render(scale=2)
                        try:
                            im = bitmap.to_pil()
                            try:
                                text = pytesseract.image_to_string(im, lang='eng', config='--psm 6', timeout=30)
                            finally:
                                im.close()
                        finally:
                            bitmap.close()
                    finally:
                        rendered.close()
                    add(text, 'pytesseract', 'ocr_unverified', native_raw=native,
                        image_count=images, ocr_reason='image_bearing' if images else 'empty_text_layer')
                else:
                    add(native, 'pdfplumber', 'text_layer_only', image_count=0)
                page.close()
        method = 'pdfplumber+ocr' if any(r['method'] == 'pytesseract' for r in records) else 'pdfplumber'
    elif path.suffix.lower() in ('.png', '.jpg', '.jpeg'):
        from PIL import Image
        import pytesseract
        with Image.open(path) as image:
            if getattr(image, 'n_frames', 1) != 1:
                raise ValueError('multi-frame image unsupported')
            pixels(*image.size)
            text = pytesseract.image_to_string(image, lang='eng', config='--psm 6', timeout=30)
        add(text, 'pytesseract', 'ocr_unverified')
        method = 'pytesseract'
    else:
        add(path.read_text(encoding='utf-8'), 'text', 'text_source')
        method = 'text'
    return records, method


class CLIParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def main():
    parser = CLIParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--locale', required=True, choices=['en_US', 'id_ID'])
    parser.add_argument('--detect-boundaries', action='store_true',
                        help='Detect and report multi-invoice boundaries across pages')
    parser.add_argument('--tolerate-noise', action='store_true',
                        help='Tolerate and normalize OCR punctuation speckles and Indonesian dialect artifacts')
    parser.add_argument('--fuzzy-labels', action='store_true',
                        help='Enable Bayesian & Levenshtein-tolerant label classification for corrupted OCR headings')
    args = parser.parse_args()
    records, method = read_source(args.source)

    if args.detect_boundaries:
        from boundary_detector import MultiInvoiceBoundaryDetector
        detector = MultiInvoiceBoundaryDetector(fuzzy_labels=args.fuzzy_labels, locale=args.locale)
        boundary_result = detector.slice_document(records)
        boundary_result['source'] = {
            'path': str(args.source),
            'method': method,
            'pages_count': len(records),
            'coverage_complete': method == 'text'
        }
        print(json.dumps(boundary_result, indent=2))
        return 2 if boundary_result['status'] == 'needs_review' else 0

    data = extract([r['raw'] for r in records], args.locale, tolerate_noise=args.tolerate_noise, fuzzy_labels=args.fuzzy_labels)
    for record in records:
        if args.source.suffix.lower() == '.pdf' and record['coverage'] == 'ocr_unverified':
            data['issues'].append({'code': 'pdf_coverage_unverified', 'page': record['page']})
            data['status'] = 'needs_review'
    data['source'] = {'path': str(args.source), 'method': method, 'pages': records,
                      'coverage_complete': method == 'text',
                      'coverage_scope': 'text extraction only; visual completeness not established'}
    print(json.dumps(data, indent=2))
    return 2 if data['status'] == 'needs_review' else 0


def validate_invoice_schema(payload, expected_code=None):
    """Strict schema and exit integrity verification for invoice extraction payload."""
    if not isinstance(payload, dict):
        raise ValueError("Root payload must be a JSON object")

    status = payload.get("status")
    if status not in ("arithmetic_consistent", "needs_review"):
        raise ValueError(f"Invalid or missing status: {status!r}")

    if expected_code == 0 and status != "arithmetic_consistent":
        raise ValueError(f"Exit code 0 requires status 'arithmetic_consistent', got {status!r}")
    if expected_code == 2 and status != "needs_review":
        raise ValueError(f"Exit code 2 requires status 'needs_review', got {status!r}")

    locale = payload.get("locale")
    if locale not in ("en_US", "id_ID"):
        raise ValueError(f"Invalid or missing locale: {locale!r}")

    if not isinstance(payload.get("rounding"), str):
        raise ValueError("Missing or invalid rounding field")

    if payload.get("authenticity_verified") is not False:
        raise ValueError("authenticity_verified must be explicitly False")

    fields = payload.get("fields")
    if not isinstance(fields, dict):
        raise ValueError("Missing or invalid fields object")
    required_fields = ("invoice", "currency", "subtotal", "tax", "discount", "total")
    for k in required_fields:
        if k not in fields or not isinstance(fields[k], dict):
            raise ValueError(f"Missing field object: {k}")
        f_val = fields[k].get("value")
        if f_val is not None and not isinstance(f_val, str):
            raise ValueError(f"Field {k} value must be str or None")
        f_ev = fields[k].get("evidence")
        if not isinstance(f_ev, list):
            raise ValueError(f"Field {k} evidence must be a list")

    lines = payload.get("lines")
    if not isinstance(lines, list):
        raise ValueError("Missing or invalid lines list")
    for idx, item in enumerate(lines):
        if not isinstance(item, dict):
            raise ValueError(f"Item {idx} must be a dict")
        if "evidence" not in item or not isinstance(item["evidence"], list):
            raise ValueError(f"Item {idx} missing evidence list")

    issues = payload.get("issues")
    if not isinstance(issues, list):
        raise ValueError("Missing or invalid issues list")
    for idx, issue in enumerate(issues):
        if not isinstance(issue, dict) or "code" not in issue:
            raise ValueError(f"Issue {idx} must be a dict with 'code'")

    source = payload.get("source")
    if not isinstance(source, dict):
        raise ValueError("Missing or invalid source object")
    for key in ("path", "method", "pages", "coverage_complete", "coverage_scope"):
        if key not in source:
            raise ValueError(f"source missing key: {key}")
    if not isinstance(source["pages"], list):
        raise ValueError("source.pages must be a list")
    if not isinstance(source["coverage_complete"], bool):
        raise ValueError("source.coverage_complete must be a bool")

    has_issues = len(issues) > 0
    if status == "arithmetic_consistent" and has_issues:
        raise ValueError("Status cannot be arithmetic_consistent when issues exist")
    if status == "needs_review" and not has_issues:
        raise ValueError("Status cannot be needs_review without recorded issues")
    return True


def supervise(command, timeout=DOCUMENT_TIMEOUT, max_output_bytes=MAX_OUTPUT_BYTES):
    """Bound wall time, capture buffer sizes, and kill the worker's process group.

    Captures stdout and stderr up to max_output_bytes each via non-blocking selectors.
    If the worker floods output beyond max_output_bytes, the worker process group is
    killed immediately and an operational failure is returned.
    Not a security sandbox: deliberately detached processes can escape the group.
    Output is withheld until the whole operation succeeds or returns review (exit 0 or 2).
    """
    import os
    import selectors
    import signal
    import subprocess
    import time
    proc = subprocess.Popen(command, start_new_session=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, bufsize=0)
    sel = selectors.DefaultSelector()
    os.set_blocking(proc.stdout.fileno(), False)
    os.set_blocking(proc.stderr.fileno(), False)
    sel.register(proc.stdout, selectors.EVENT_READ, data='stdout')
    sel.register(proc.stderr, selectors.EVENT_READ, data='stderr')

    stdout_chunks, stderr_chunks = [], []
    stdout_len, stderr_len = 0, 0
    overflow, overflow_stream = False, None
    deadline = time.monotonic() + timeout

    try:
        while sel.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('document timeout exceeded')
            events = sel.select(timeout=max(0.01, min(remaining, 0.2)))
            for key, mask in events:
                stream_name = key.data
                fd = key.fileobj
                try:
                    chunk = fd.read(65536)
                except Exception:
                    chunk = b''
                if not chunk:
                    sel.unregister(fd)
                    continue
                if stream_name == 'stdout':
                    stdout_len += len(chunk)
                    if stdout_len > max_output_bytes:
                        overflow = True
                        overflow_stream = 'stdout'
                        break
                    stdout_chunks.append(chunk)
                else:
                    stderr_len += len(chunk)
                    if stderr_len > max_output_bytes:
                        overflow = True
                        overflow_stream = 'stderr'
                        break
                    stderr_chunks.append(chunk)
            if overflow:
                break
            if proc.poll() is not None:
                for key in list(sel.get_map().values()):
                    fd = key.fileobj
                    stream_name = key.data
                    while True:
                        try:
                            chunk = fd.read(65536)
                        except Exception:
                            chunk = b''
                        if not chunk:
                            break
                        if stream_name == 'stdout':
                            stdout_len += len(chunk)
                            if stdout_len > max_output_bytes:
                                overflow = True
                                overflow_stream = 'stdout'
                                break
                            stdout_chunks.append(chunk)
                        else:
                            stderr_len += len(chunk)
                            if stderr_len > max_output_bytes:
                                overflow = True
                                overflow_stream = 'stderr'
                                break
                            stderr_chunks.append(chunk)
                    sel.unregister(fd)
                break
    finally:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        sel.close()
        for s in (proc.stdout, proc.stderr):
            if s and not s.closed:
                try:
                    s.close()
                except Exception:
                    pass
        proc.wait()

    if overflow:
        diagnostic = f'error: document worker exceeded output buffer limit on {overflow_stream}\n'
        return 1, '', diagnostic

    stdout = b''.join(stdout_chunks).decode('utf-8', errors='replace')
    stderr = b''.join(stderr_chunks).decode('utf-8', errors='replace')

    code = proc.returncode
    if code not in (0, 2):
        reason = f'signal {-code}' if code < 0 else f'exit {code}'
        diagnostic = f'error: document worker failed ({reason})\n'
        return 1, '', stderr + diagnostic

    # BIZ-007: Validate JSON schema and exit-status contract at supervisor boundary
    # BIZ-010: Boundary detector results have their own contract (status in single_invoice, multi_invoice_sliced, needs_review)
    try:
        parsed_payload = json.loads(stdout)
        if '--detect-boundaries' in command:
            b_status = parsed_payload.get('status')
            if b_status not in ('single_invoice', 'multi_invoice_sliced', 'needs_review'):
                raise ValueError(f"Invalid boundary detection status: {b_status!r}")
            if code == 0 and b_status not in ('single_invoice', 'multi_invoice_sliced'):
                raise ValueError(f"Exit code 0 requires clean boundary status, got {b_status!r}")
            if code == 2 and b_status != 'needs_review':
                raise ValueError(f"Exit code 2 requires 'needs_review', got {b_status!r}")
        else:
            validate_invoice_schema(parsed_payload, expected_code=code)
    except Exception as exc:
        diagnostic = f'error: document worker produced invalid schema or corrupted payload ({type(exc).__name__}: {exc})\n'
        return 1, '', stderr + diagnostic

    return code, stdout, stderr


if __name__ in ('__main__', '__invoice_worker__'):
    import sys
    try:
        if __name__ == '__invoice_worker__':
            code = main()
        else:
            command = [sys.executable, str(Path(__file__).with_name('worker_limits.py')),
                       str(Path(__file__).resolve()), *sys.argv[1:]]
            code, stdout, stderr = supervise(command)
            if code not in (0, 1, 2):
                raise RuntimeError('document worker failed')
            if code != 1:
                print(stdout, end='')
            print(stderr, end='', file=sys.stderr)
    except Exception as exc:
        print(f'error: {type(exc).__name__}: {exc}', file=sys.stderr)
        code = 1
    raise SystemExit(code)
