#!/usr/bin/env python3
"""TA-REDTEAM-2026-007: expected count gate."""
from pathlib import Path
import sys

SRC = Path(__file__).resolve().parents[1] / 'scripts' / 'download-nft-cars.mjs'
text = SRC.read_text(encoding='utf-8')

required = [
    'EXPECTED_NFTS',
    'token_index NFT count mismatch',
    'metadata count mismatch',
    'countTokenIndexNfts',
    'countMetadataEntries',
    'source_expectations',
]

for token in required:
    if token not in text:
        print(f'FAIL: missing: {token}')
        sys.exit(1)

print('DOWNLOAD_NFT_CARS_EXPECTED_COUNT_GATE_OK')
