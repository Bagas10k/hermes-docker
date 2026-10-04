"""Bounded cross-document review candidates; never a fraud verdict.

Input uses explicit seller_id, currency, document_id and normalized decimal
strings. This API does not infer seller identity or parse OCR documents.
"""
import hashlib
import json
import re
import unicodedata
from decimal import Decimal
from datetime import date
from difflib import SequenceMatcher


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError('expected nonempty string of at most 256 characters')
    return value


def number(value, positive=False):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{1,12}(?:\.[0-9]{1,4})?', value):
        raise ValueError('expected bounded nonnegative decimal string')
    d = Decimal(value)
    if positive and d == 0:
        raise ValueError('quantity must be positive')
    return format(d.normalize(), 'f')


def normalize_description(value):
    return ' '.join(unicodedata.normalize('NFKC', text(value)).casefold().split())


def prepare(row):
    if not isinstance(row, dict):
        raise ValueError('line must be an object')
    try:
        scope = tuple(text(row[k]) for k in ('seller_id', 'currency'))
        if scope[1] not in ('USD', 'IDR'):
            raise ValueError('unsupported currency')
        numeric = tuple(number(row[k], k == 'quantity') for k in ('quantity', 'unit_price', 'amount'))
        return (scope + numeric, normalize_description(row['description']),
                text(row['document_id']), text(row['line_id']))
    except KeyError as exc:
        raise ValueError('missing field: ' + str(exc)) from exc


def service_period(value):
    """Closed calendar-day interval; None means unknown, not invalid."""
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {'start', 'end'}:
        raise ValueError('service_period requires exactly start and end')
    for part in value.values():
        if not isinstance(part, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', part):
            raise ValueError('service period requires YYYY-MM-DD')
    start, end = (date.fromisoformat(value[k]) for k in ('start', 'end'))
    if start > end:
        raise ValueError('reversed service period')
    return start, end


def fingerprint(row):
    key, description, _, _ = prepare(row)
    payload = json.dumps([*key, description], ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def versioned_fingerprint(row, *, version='v2'):
    """Review-only identity envelope; never an automatic deletion key.

    v1 preserves the exact legacy digest and deliberately ignores periods.
    v2 uses domain-separated canonical data with an explicit unknown marker.
    Equal unknown hashes do not establish equal service periods.
    """
    if not isinstance(version, str) or version not in ('v1', 'v2'):
        raise ValueError('unsupported fingerprint version')
    key, description, _, _ = prepare(row)
    if version == 'v1':
        return {'version': 'v1', 'algorithm': 'sha256', 'digest': fingerprint(row),
                'period_state': 'ignored', 'period_identity_complete': False,
                'needs_review': True}
    period = service_period(row.get('service_period'))
    identity = (['known', period[0].isoformat(), period[1].isoformat()]
                if period is not None else ['unknown'])
    payload = json.dumps(['invoice-line-fingerprint', 'v2', list(key), description, identity],
                         ensure_ascii=False, separators=(',', ':'))
    return {'version': 'v2', 'algorithm': 'sha256',
            'digest': hashlib.sha256(payload.encode('utf-8')).hexdigest(),
            'period_state': identity[0], 'period_identity_complete': period is not None,
            'needs_review': True}


def reconcile(rows, threshold=0.9, max_lines=500, *, service_periods=False):
    """Return stable cross-document pairs, bounded to 500 input lines.

    Similarity is a heuristic, not probability. Equal numeric fields and exact
    seller/currency scope are mandatory. Recurring legitimate charges can match.
    """
    if type(threshold) not in (int, float) or not 0.8 <= threshold <= 1:
        raise ValueError('threshold must be between 0.8 and 1')
    if type(max_lines) is not int or not 1 <= max_lines <= 500:
        raise ValueError('max_lines must be 1..500')
    if not isinstance(rows, list) or len(rows) > max_lines:
        raise ValueError('line budget exceeded or invalid container')
    if type(service_periods) is not bool:
        raise ValueError('service_periods must be boolean')
    periods = {}
    prepared = []
    seen = set()
    for row in rows:
        p = prepare(row)
        ref = p[2:]
        if ref in seen:
            raise ValueError('duplicate document/line reference')
        if service_periods:
            periods[ref] = service_period(row.get('service_period'))
        seen.add(ref)
        prepared.append(p)
    prepared.sort(key=lambda p: p[2:])
    groups = {}
    candidates = []
    for key, desc, doc, line in prepared:
        for other_desc, other_doc, other_line in groups.get(key, []):
            if doc == other_doc:
                continue
            exact = desc == other_desc
            # SequenceMatcher can be asymmetric: require both directions.
            score = 1.0 if exact else min(
                SequenceMatcher(None, desc, other_desc, autojunk=False).ratio(),
                SequenceMatcher(None, other_desc, desc, autojunk=False).ratio())
            if score >= threshold:
                candidates.append({'left': [other_doc, other_line], 'right': [doc, line],
                                   'kind': 'exact' if exact else 'fuzzy',
                                   'similarity': score, 'needs_review': True})
        groups.setdefault(key, []).append((desc, doc, line))
    if service_periods:
        retained = []
        for candidate in candidates:
            left, right = (periods[tuple(candidate[k])] for k in ('left', 'right'))
            relation, days = 'unknown', None
            if left is not None and right is not None:
                days = (min(left[1], right[1]) - max(left[0], right[0])).days + 1
                if days <= 0:
                    continue
                relation = 'equal' if left == right else 'overlap'
            candidate.update(period_relation=relation, overlap_days=days)
            retained.append(candidate)
        candidates = retained
    return {'status': 'needs_review' if candidates else 'no_candidates',
            'fraud_verified': False, 'candidates': candidates,
            'limitations': [('Explicit closed-day service periods only; no proration or credit notes'
                             if service_periods else 'No date/service-period reconciliation'),
                            'No authenticity, payment or OCR verification']}
