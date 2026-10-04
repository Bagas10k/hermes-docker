"""Pure local migration adapter. Never writes a database or approves payment."""
from copy import deepcopy
from rebilling import versioned_fingerprint


def migrate_records(records):
    """Validate an entire <=500-record batch before returning detached copies.

    Each record contains exactly row and fingerprints. History is one envelope
    per known version, bound to the supplied immutable row. No repair on mismatch.
    """
    if type(records) is not list or len(records) > 500:
        raise ValueError('expected list of at most 500 records')
    required = {'seller_id', 'document_id', 'line_id', 'currency', 'description',
                'quantity', 'unit_price', 'amount'}
    planned = []
    seen = set()
    for record in records:
        if type(record) is not dict or set(record) != {'row', 'fingerprints'}:
            raise ValueError('record requires exactly row and fingerprints')
        row = record['row']
        if (type(row) is not dict or not required <= set(row)
                or set(row) - required - {'service_period'}):
            raise ValueError('unsupported row schema; retain raw evidence separately')
        expected = {v: versioned_fingerprint(row, version=v) for v in ('v1', 'v2')}
        ref = (row['seller_id'], row['document_id'], row['line_id'])
        if ref in seen:
            raise ValueError('duplicate record reference')
        seen.add(ref)
        history = record['fingerprints']
        if type(history) is not list or not 1 <= len(history) <= 2:
            raise ValueError('expected one or two version envelopes')
        versions = set()
        for envelope in history:
            if type(envelope) is not dict:
                raise ValueError('invalid envelope')
            version = envelope.get('version')
            if type(version) is not str or version not in expected or version in versions:
                raise ValueError('unknown or duplicate version')
            canonical = expected[version]
            if set(envelope) != set(canonical) or any(
                    type(envelope[k]) is not type(v) or envelope[k] != v
                    for k, v in canonical.items()):
                raise ValueError('envelope does not match row or schema')
            versions.add(version)
        planned.append((record, expected['v2'], 'v2' not in versions))
    result = []
    for record, v2, append in planned:
        output = deepcopy(record)
        if append:
            output['fingerprints'].append(v2)
        result.append(output)
    return result
