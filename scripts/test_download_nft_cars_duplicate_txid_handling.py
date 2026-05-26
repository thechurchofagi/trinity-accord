#!/usr/bin/env python3
"""TA-REDTEAM-2026-007: duplicate txid handling."""
from pathlib import Path
import sys

SRC = Path(__file__).resolve().parents[1] / 'scripts' / 'download-nft-cars.mjs'
text = SRC.read_text(encoding='utf-8')

required = [
    'addTxidRef',
    'sameExpectedCar',
    'Conflicting duplicate txid',
    'all_references',
    'reference_count',
    'logical_file_references',
]

for token in required:
    if token not in text:
        print(f'FAIL: missing: {token}')
        sys.exit(1)

# Must not have old pattern
if 'txids.set(meta.txid, {' in text and 'existing' not in text.split('txids.set(meta.txid, {')[0][-200:]:
    print('FAIL: old silent overwrite pattern may remain')
    sys.exit(1)

print('DOWNLOAD_NFT_CARS_DUPLICATE_TXID_HANDLING_OK')
