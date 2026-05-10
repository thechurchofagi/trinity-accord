#!/usr/bin/env python3
"""TA-REDTEAM-2026-007: token_index unique candidate gate."""
from pathlib import Path
import sys

SRC = Path(__file__).resolve().parents[1] / 'scripts' / 'download-nft-cars.mjs'
text = SRC.read_text(encoding='utf-8')

required = [
    'looksLikeTokenIndexObject',
    'extractJsonObjectsFromBlock',
    'Ambiguous token_index candidates',
    'candidates.length > 1',
    'validateTokenIndex(candidates[0]',
    'candidates = []',
]

forbidden = [
    'bestObj',
    'bestKeyCount',
    'bestObj = obj',
    'keys.length > bestKeyCount',
]

for token in required:
    if token not in text:
        print(f'FAIL: missing marker: {token}')
        sys.exit(1)

for bad in forbidden:
    if bad in text:
        print(f'FAIL: old anti-pattern remains: {bad}')
        sys.exit(1)

print('DOWNLOAD_NFT_CARS_TOKEN_INDEX_UNIQUE_CANDIDATE_OK')
