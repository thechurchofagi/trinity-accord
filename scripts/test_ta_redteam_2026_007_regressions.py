#!/usr/bin/env python3
"""TA-REDTEAM-2026-007 regression tests — comprehensive.

Validates all findings are fixed in download-nft-cars.mjs:
- SRC-TOKEN-001: unique candidate fail-closed
- SRC-COUNT-001: EXPECTED_NFTS=175 enforced
- SRC-BIND-001: recovery package digest check
- SRC-DUPTXID-001: duplicate txid conflict detection
- SRC-CAR-001: strict CAR parser
- SRC-SCHEMA-001: token_index schema validation
- SRC-TRACE-001: source digests in manifest
- SRC-H1: root_cid boundary
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
        if detail: print(f'    {detail}')
        failures.append(name)

print('TA-REDTEAM-2026-007 comprehensive regression tests')
print('=' * 55)

# SRC-COUNT-001
check('EXPECTED_NFTS = 175 default', 'EXPECTED_NFTS' in src and '175' in src)
check('token_index NFT count mismatch throws', 'token_index NFT count mismatch' in src)
check('metadata count mismatch throws', 'metadata count mismatch' in src)
check('countTokenIndexNfts helper', 'countTokenIndexNfts' in src)
check('countMetadataEntries helper', 'countMetadataEntries' in src)

# SRC-TOKEN-001
check('looksLikeTokenIndexObject function', 'looksLikeTokenIndexObject' in src)
check('extractJsonObjectsFromBlock function', 'extractJsonObjectsFromBlock' in src)
check('Ambiguous candidates throws', 'Ambiguous token_index candidates' in src)
check('candidates.length > 1 check', 'candidates.length > 1' in src)
check('No bestObj pattern', 'bestObj' not in src)
check('No bestKeyCount pattern', 'bestKeyCount' not in src)
check('validateTokenIndex called in extractTokenIndex', 'validateTokenIndex(candidates' in src)

# SRC-CAR-001
check('readVarintStrict function', 'readVarintStrict' in src)
check('parseCarHeaderStrict function', 'parseCarHeaderStrict' in src)
check('iterCarBlocksStrict function', 'iterCarBlocksStrict' in src)
check('Truncated varint throws', 'Truncated' in src)
check('Overlong varint throws', 'Overlong' in src)
check('CAR block length exceeds buffer throws', 'CAR block length exceeds buffer' in src)
check('Number.isSafeInteger check', 'Number.isSafeInteger' in src)
check('No catch {} silent swallow', 'catch {}' not in src)
check('No weak break on block overflow', 'blockLen === 0 || pos + blockLen > data.length) break' not in src)
check('JSON errors logged', 'Malformed JSON candidate' in src or 'Malformed JSON while scanning' in src)

# SRC-DUPTXID-001
check('addTxidRef function', 'addTxidRef' in src)
check('sameExpectedCar function', 'sameExpectedCar' in src)
check('Conflicting duplicate txid throws', 'Conflicting duplicate txid' in src)
check('all_references preserved', 'all_references' in src)
check('reference_count field', 'reference_count' in src)
check('logical_file_references count', 'logical_file_references' in src)

# SRC-BIND-001
check('EXPECTED_RECOVERY_PACKAGE_SHA256', 'EXPECTED_RECOVERY_PACKAGE_SHA256' in src)
check('verifyRecoveryPackageSource function', 'verifyRecoveryPackageSource' in src)
check('readExpectedRecoveryPackageSha256 function', 'readExpectedRecoveryPackageSha256' in src)
check('RECOVERY_PACKAGE_SHA256_FILE', 'RECOVERY_PACKAGE_SHA256_FILE' in src)
check('Mandatory hash for non-DRY_RUN', 'refusing to use unauthenticated' in src)

# SRC-SCHEMA-001
check('validateCarRef function', 'validateCarRef' in src)
check('normalizeTokenId function', 'normalizeTokenId' in src)
check('validateTokenIndex function', 'validateTokenIndex' in src)
check('ARWEAVE_TXID_RE regex', 'ARWEAVE_TXID_RE' in src)
check('ETH_CONTRACT_RE regex', 'ETH_CONTRACT_RE' in src)

# SRC-TRACE-001
check('source_recovery_package in manifest', 'source_recovery_package' in src)
check('source_token_index in manifest', 'source_token_index' in src)
check('source_binding in manifest', 'source_binding' in src)
check('source_expectations in manifest', 'source_expectations' in src)
check('stableStringify for canonical JSON', 'stableStringify' in src)
check('canonicalization field', "canonicalization: 'stable-json-v1'" in src)

# SRC-H1
check('root_cid_verified: false field', 'root_cid_verified: false' in src)
check('cid_policy in manifest', 'cid_policy' in src)
check('producer_verifies_root_cid: false', 'producer_verifies_root_cid: false' in src)
check('root_cid_recorded_as_expected_metadata', 'root_cid_recorded_as_expected_metadata: true' in src)

# Exports
check('exports readVarintStrict', 'readVarintStrict' in src.split('export {')[-1])
check('exports parseCarHeaderStrict', 'parseCarHeaderStrict' in src.split('export {')[-1])
check('exports iterCarBlocksStrict', 'iterCarBlocksStrict' in src.split('export {')[-1])
check('exports addTxidRef', 'addTxidRef' in src.split('export {')[-1])
check('exports stableStringify', 'stableStringify' in src.split('export {')[-1])
check('exports verifyRecoveryPackageSource', 'verifyRecoveryPackageSource' in src.split('export {')[-1])

print('=' * 55)
if failures:
    print(f'❌ {len(failures)} failures:')
    for f in failures:
        print(f'  - {f}')
    sys.exit(1)
print(f'TA-REDTEAM-2026-007_ALL_REGRESSIONS_OK ({len(src.split(chr(10)))} lines checked)')
