#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib

OUT = pathlib.Path(os.getenv('CHRONICLE_OUT', 'artifacts/chronicle-sidechain-scan'))
E = OUT / 'evidence-v2'


def sha(data):
    return hashlib.sha256(data).digest()


def stable(value):
    if isinstance(value, list):
        return '[' + ','.join(stable(x) for x in value) + ']'
    if isinstance(value, dict):
        return '{' + ','.join(json.dumps(k, separators=(',', ':')) + ':' + stable(value[k]) for k in sorted(value)) + '}'
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    if value is None:
        return 'null'
    return json.dumps(value, separators=(',', ':'), ensure_ascii=False)


def projection(r):
    return {
        'asset_id': r['asset_id'],
        'chain_id': r['chain']['chain_id'],
        'standard': r['standard'],
        'contract': r['contract'],
        'token_id': r['token_id'],
        'origin': ({k: r['origin'].get(k) for k in ['kind', 'mint_observed', 'transaction_hash', 'block_hash', 'block_number', 'log_index', 'timestamp', 'timestamp_unix', 'from', 'to', 'quantity']} if r.get('origin') else None),
        'content': {
            'metadata': {
                'root_cid': r['content']['metadata'].get('root_cid'),
                'leaf_path': r['content']['metadata'].get('leaf_path'),
                'payload_sha256': (r['content']['metadata'].get('payload') or {}).get('sha256'),
                'payload_bytes': (r['content']['metadata'].get('payload') or {}).get('bytes'),
                'normalized_sha256': r['content']['metadata'].get('normalized_sha256'),
                'car_sha256': (r['content']['metadata'].get('car') or {}).get('car_sha256'),
                'car_bytes': (r['content']['metadata'].get('car') or {}).get('car_bytes'),
            },
            'media': [{
                'role': m['role'],
                'root_cid': (m.get('ipfs') or {}).get('root_cid'),
                'leaf_path': (m.get('ipfs') or {}).get('leaf_path'),
                'payload_sha256': (m.get('payload') or {}).get('sha256'),
                'payload_bytes': (m.get('payload') or {}).get('bytes'),
                'car_sha256': (m.get('car') or {}).get('car_sha256'),
                'car_bytes': (m.get('car') or {}).get('car_bytes'),
            } for m in r['content']['media']],
        },
    }


def main():
    idx = json.loads((E / 'SIDECHAIN-NFT-IDENTITY-INDEX.json').read_text())
    commitment = json.loads((E / 'SIDECHAIN-NFT-COLLECTION-COMMITMENT.json').read_text())
    projections = sorted((projection(r) for r in idx['records']), key=lambda x: x['asset_id'])
    actual = {p['asset_id']: sha(b'\x00' + stable(p).encode()).hex() for p in projections}
    expected_rows = commitment.get('leaves') or []
    expected = {row.get('asset_id'): row.get('leaf_sha256') for row in expected_rows}
    mismatches = []
    for asset_id in sorted(set(actual) | set(expected)):
        if actual.get(asset_id) != expected.get(asset_id):
            mismatches.append({'asset_id': asset_id, 'expected': expected.get(asset_id), 'actual': actual.get(asset_id)})
    expected_order = [row.get('asset_id') for row in expected_rows]
    actual_order = [p['asset_id'] for p in projections]
    report = {
        'schema': 'trinity-accord/chronicle-sidechain-l1-leaf-diagnostics/v1',
        'records': len(projections),
        'commitment_leaf_count': len(expected_rows),
        'leaf_mismatch_count': len(mismatches),
        'leaf_mismatches': mismatches[:40],
        'leaf_mismatches_omitted': max(0, len(mismatches) - 40),
        'order_matches': expected_order == actual_order,
        'first_order_difference': next(({'index': i, 'expected': e, 'actual': a} for i, (e, a) in enumerate(zip(expected_order, actual_order)) if e != a), None),
    }
    path = E / 'L1-LEAF-DIAGNOSTICS.json'
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(f"[L1 DIAG] records={report['records']} leaves={report['commitment_leaf_count']} mismatches={report['leaf_mismatch_count']} order_matches={report['order_matches']}")
    for row in report['leaf_mismatches'][:10]:
        print(f"[L1 LEAF MISMATCH] {row['asset_id']} expected={row['expected']} actual={row['actual']}")
    if report['first_order_difference']:
        print(f"[L1 ORDER MISMATCH] {report['first_order_difference']}")


if __name__ == '__main__':
    main()
