#!/usr/bin/env python3
"""TA-REDTEAM-2026-007 regression tests.

Validates that download-nft-cars.mjs has the required security hardening:
- SRC-TOKEN-001: extractTokenIndex fails on multiple candidates
- SRC-COUNT-001: EXPECTED_NFTS = 175 enforced
- SRC-BIND-001: recovery package digest check
- SRC-DUPTXID-001: duplicate txid conflict detection
- SRC-CAR-001: strict parseCarHeader with bounds checks
- SRC-SCHEMA-001: token_index schema validation
- SRC-TRACE-001: source digests in RELEASE-MANIFEST.json
- SRC-H1: root_cid_verified field in manifest
"""

import re, sys, os

SCRIPT = os.path.join(os.path.dirname(__file__), 'download-nft-cars.mjs')
with open(SCRIPT, 'r') as f:
    src = f.read()

failures = []

def check(name, condition, detail=''):
    if condition:
        print(f'  ✓ {name}')
    else:
        print(f'  ✗ {name}')
        if detail:
            print(f'    {detail}')
        failures.append(name)

print('TA-REDTEAM-2026-007 regression tests')
print('=' * 50)

# SRC-COUNT-001: EXPECTED_NFTS constant
check(
    'EXPECTED_NFTS = 175 defined',
    'const EXPECTED_NFTS = 175' in src,
    'Expected: const EXPECTED_NFTS = 175'
)
check(
    'EXPECTED_NFTS enforced after token_index extraction',
    'totalTokens !== EXPECTED_NFTS' in src,
    'Expected: throw if totalTokens !== EXPECTED_NFTS'
)

# SRC-TOKEN-001: multiple candidates fail-closed
check(
    'extractTokenIndex collects candidates (not largest-wins)',
    'candidates' in src and 'candidates.push' in src,
    'Expected: candidates array, not bestObj'
)
check(
    'Multiple candidates throw error',
    'candidates.length > 1' in src and 'Multiple token_index-like JSON' in src,
    'Expected: throw on candidates.length > 1'
)
check(
    'No more bestObj / bestKeyCount pattern',
    'bestObj' not in src and 'bestKeyCount' not in src,
    'Expected: removed largest-wins heuristic'
)

# SRC-CAR-001: strict parseCarHeader
check(
    'parseCarHeader has bounds check (pos >= data.length)',
    'pos >= data.length' in src and 'Truncated CAR header varint' in src,
    'Expected: bounds check before accessing data[pos]'
)
check(
    'parseCarHeader has safe integer check',
    'Number.isSafeInteger(headerLen)' in src,
    'Expected: Number.isSafeInteger check'
)
check(
    'parseCarHeader has max iterations (10)',
    'for (let i = 0; i < 10' in src,
    'Expected: bounded loop'
)
check(
    'JSON parse errors logged (not silent catch {})',
    'JSON parse error in CAR block' in src or 'console.warn' in src,
    'Expected: console.warn instead of catch {}'
)

# SRC-DUPTXID-001: duplicate txid conflict detection
check(
    'collectTxids checks for duplicate txids',
    'existing = txids.get' in src or 'const existing = txids.get' in src,
    'Expected: check for existing entry before set'
)
check(
    'Conflicting sha256 throws',
    'conflicting expected sha256' in src,
    'Expected: throw on conflicting sha256'
)
check(
    'Conflicting size throws',
    'conflicting expected size' in src,
    'Expected: throw on conflicting size'
)
check(
    'all_references preserved for duplicates',
    'all_references' in src,
    'Expected: all_references array'
)

# SRC-BIND-001: recovery package digest check
check(
    'Recovery package SHA-256 computed',
    'recoveryPackageSha256' in src,
    'Expected: sha256hex of recovery package'
)
check(
    'Hash manifest check',
    'hash-manifest.json' in src and 'Recovery package digest mismatch' in src,
    'Expected: check against hash-manifest.json'
)

# SRC-SCHEMA-001: token_index schema validation
check(
    'validateTokenIndexEntry function exists',
    'function validateTokenIndexEntry' in src,
    'Expected: schema validation function'
)
check(
    'Contract format validated (0x + 40 hex)',
    '0x[0-9a-fA-F]{40}' in src,
    'Expected: contract regex check'
)
check(
    'car_sha256 format validated',
    'SHA256_RE.test(meta.car_sha256' in src or "SHA256_RE.test(m.car_sha256" in src,
    'Expected: sha256 format check'
)
check(
    'Schema errors abort',
    'schemaErrors' in src and 'aborting' in src,
    'Expected: throw on schema errors'
)

# SRC-TRACE-001: source digests in release manifest
check(
    'recovery_package_sha256 in release manifest',
    'recovery_package_sha256: recoveryPackageSha256' in src,
    'Expected: source digest in manifest'
)
check(
    'token_index_sha256 in release manifest',
    'token_index_sha256: tokenIndexSha256' in src,
    'Expected: token index digest in manifest'
)
check(
    'expected_nfts in release manifest',
    'expected_nfts: EXPECTED_NFTS' in src,
    'Expected: expected_nfts field'
)

# SRC-H1: root_cid_verified field
check(
    'root_cid_verified: false field in manifest',
    'root_cid_verified: false' in src,
    'Expected: explicit root_cid_verified boundary'
)
check(
    'does_not_prove updated for root_cid',
    'root_cid is metadata from token_index' in src or 'NOT verified by this producer' in src,
    'Expected: clearer does_not_prove wording'
)

print('=' * 50)
if failures:
    print(f'❌ {len(failures)} failures:')
    for f in failures:
        print(f'  - {f}')
    sys.exit(1)
else:
    print('TA-REDTEAM-2026-007_ALL_REGRESSIONS_OK')
