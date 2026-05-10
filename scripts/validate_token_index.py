#!/usr/bin/env python3
"""Validate token_index.json against Trinity Accord schema.

Usage:
  python3 scripts/validate_token_index.py path/to/token_index.json
  python3 scripts/validate_token_index.py --self-test
"""

import json, re, sys, os

ETH_CONTRACT_RE = re.compile(r'^0x[a-fA-F0-9]{40}$')
ARWEAVE_TXID_RE = re.compile(r'^[A-Za-z0-9_-]{43}$')
SHA256_RE = re.compile(r'^[a-fA-F0-9]{64}$')


def validate_car_ref(ref, path_label):
    errors = []
    if not isinstance(ref, dict):
        errors.append(f'{path_label}: must be object')
        return errors
    if not ARWEAVE_TXID_RE.match(ref.get('txid', '')):
        errors.append(f'{path_label}.txid invalid: {ref.get("txid")}')
    rc = ref.get('root_cid', '')
    if not isinstance(rc, str) or len(rc) < 10:
        errors.append(f'{path_label}.root_cid missing or invalid')
    if not SHA256_RE.match(ref.get('car_sha256', '')):
        errors.append(f'{path_label}.car_sha256 invalid')
    sz = ref.get('car_size')
    if isinstance(sz, int):
        if sz <= 0: errors.append(f'{path_label}.car_size must be > 0')
    elif isinstance(sz, str):
        if not re.match(r'^[1-9][0-9]*$', sz): errors.append(f'{path_label}.car_size string invalid')
    else:
        errors.append(f'{path_label}.car_size must be int or numeric string')
    return errors


def validate_token_index(index):
    errors = []
    if not isinstance(index, dict) or len(index) == 0:
        errors.append('token_index must be non-empty object')
        return errors

    total_nfts = 0
    for contract, tokens in index.items():
        if not ETH_CONTRACT_RE.match(contract):
            errors.append(f'Invalid contract: {contract}')
            continue
        if not isinstance(tokens, dict):
            errors.append(f'{contract}: must be object')
            continue
        for token_id, entry in tokens.items():
            if not re.match(r'^[0-9]+$', str(token_id)):
                errors.append(f'{contract}/{token_id}: invalid token_id')
            if not isinstance(entry, dict):
                errors.append(f'{contract}/{token_id}: entry must be object')
                continue
            if 'metadata' not in entry:
                errors.append(f'{contract}/{token_id}: metadata missing')
            else:
                errors.extend(validate_car_ref(entry['metadata'], f'{contract}/{token_id}.metadata'))
            media = entry.get('media', [])
            if not isinstance(media, list):
                errors.append(f'{contract}/{token_id}.media must be array')
            else:
                for i, m in enumerate(media):
                    errors.extend(validate_car_ref(m, f'{contract}/{token_id}.media[{i}]'))
            total_nfts += 1

    return errors


def self_test():
    tests_passed = 0
    tests_failed = 0

    def ok(name):
        nonlocal tests_passed
        tests_passed += 1
        print(f'  ✓ {name}')

    def fail(name, detail=''):
        nonlocal tests_failed
        tests_failed += 1
        print(f'  ✗ {name}: {detail}')

    def expect_valid(name, index):
        errs = validate_token_index(index)
        if not errs: ok(name)
        else: fail(name, f'expected valid but got: {errs}')

    def expect_invalid(name, index, pattern=''):
        errs = validate_token_index(index)
        if errs:
            if pattern and not any(pattern in e for e in errs):
                fail(name, f'expected pattern "{pattern}" in errors: {errs}')
            else:
                ok(name)
        else:
            fail(name, 'expected errors but got none')

    valid_entry = {
        'metadata': {
            'txid': 'a' * 43,
            'root_cid': 'bafybeig' + 'a' * 50,
            'car_sha256': 'ab' * 32,
            'car_size': 12345
        },
        'media': [{
            'txid': 'b' * 43,
            'root_cid': 'bafybeig' + 'b' * 50,
            'car_sha256': 'cd' * 32,
            'car_size': 67890
        }]
    }

    print('token_index schema validator self-test')
    print('=' * 45)

    expect_valid('valid minimal', {'0x' + 'ab' * 20: {'1': valid_entry}})
    expect_invalid('bad contract', {'0xBAD': {'1': valid_entry}}, 'Invalid contract')
    expect_invalid('bad token_id', {'0x' + 'ab' * 20: {'notnum': valid_entry}}, 'invalid token_id')
    expect_invalid('missing metadata', {'0x' + 'ab' * 20: {'1': {'media': []}}}, 'metadata missing')
    bad_meta = dict(valid_entry); bad_meta['metadata'] = dict(valid_entry['metadata'], txid='short')
    expect_invalid('bad txid', {'0x' + 'ab' * 20: {'1': bad_meta}}, 'txid invalid')
    bad_sha = dict(valid_entry); bad_sha['metadata'] = dict(valid_entry['metadata'], car_sha256='zzzz')
    expect_invalid('bad sha256', {'0x' + 'ab' * 20: {'1': bad_sha}}, 'car_sha256 invalid')
    bad_sz = dict(valid_entry); bad_sz['metadata'] = dict(valid_entry['metadata'], car_size=-1)
    expect_invalid('bad size', {'0x' + 'ab' * 20: {'1': bad_sz}}, 'car_size')
    bad_media = dict(valid_entry, media='notarray')
    expect_invalid('media not array', {'0x' + 'ab' * 20: {'1': bad_media}}, 'media must be array')
    expect_invalid('empty index', {}, 'non-empty object')

    print('=' * 45)
    if tests_failed:
        print(f'❌ {tests_failed} failures')
        sys.exit(1)
    print(f'TOKEN_INDEX_SCHEMA_VALIDATION_SELF_TEST_OK ({tests_passed} passed)')


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        self_test()
    elif len(sys.argv) < 2:
        print('Usage: python3 validate_token_index.py <path> | --self-test', file=sys.stderr)
        sys.exit(1)
    else:
        path = sys.argv[1]
        with open(path) as f:
            index = json.load(f)
        errs = validate_token_index(index)
        if errs:
            for e in errs: print(f'ERROR: {e}', file=sys.stderr)
            sys.exit(1)
        print(f'✅ {path} valid')
