#!/usr/bin/env python3
"""TA-REDTEAM-2026-007: release manifest source traceability."""
from pathlib import Path
import sys

SRC = Path(__file__).resolve().parents[1] / 'scripts' / 'download-nft-cars.mjs'
text = SRC.read_text(encoding='utf-8')

required = [
    'source_recovery_package',
    'source_token_index',
    'source_binding',
    'source_expectations',
    'recovery_package_sha256_enforced',
    'digest_manifest_crosscheck_performed',
    'authority_manifest_crosscheck_performed',
    'canonicalization',
    'all_references',
    'reference_count',
    'logical_file_references',
]

for token in required:
    if token not in text:
        print(f'FAIL: missing: {token}')
        sys.exit(1)

print('DOWNLOAD_NFT_CARS_MANIFEST_SOURCE_TRACEABILITY_OK')
