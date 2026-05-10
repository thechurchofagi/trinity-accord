#!/usr/bin/env python3
"""TA-REDTEAM-2026-007: root CID boundary."""
from pathlib import Path
import sys

SRC = Path(__file__).resolve().parents[1] / 'scripts' / 'download-nft-cars.mjs'
text = SRC.read_text(encoding='utf-8')

required = [
    'expected_root_cid',
    'root_cid_verified',
    'cid_policy',
    'producer_verifies_root_cid: false',
    'root_cid_recorded_as_expected_metadata: true',
    'CID/root/DAG correctness',
    'verify-release-assets.mjs --cid-check',
]

for token in required:
    if token not in text:
        print(f'FAIL: missing: {token}')
        sys.exit(1)

print('DOWNLOAD_NFT_CARS_ROOT_CID_BOUNDARY_OK')
