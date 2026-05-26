#!/usr/bin/env python3
"""TA-REDTEAM-2026-007: recovery CAR parser strictness."""
from pathlib import Path
import sys

SRC = Path(__file__).resolve().parents[1] / 'scripts' / 'download-nft-cars.mjs'
text = SRC.read_text(encoding='utf-8')

required = [
    'readVarintStrict',
    'parseCarHeaderStrict',
    'iterCarBlocksStrict',
    'Truncated',
    'Overlong',
    'CAR block length exceeds buffer',
    'CAR header length exceeds buffer',
    'Number.isSafeInteger',
]

forbidden = [
    'catch {}',
    'blockLen === 0 || pos + blockLen > data.length) break',
]

for token in required:
    if token not in text:
        print(f'FAIL: missing: {token}')
        sys.exit(1)

for bad in forbidden:
    if bad in text:
        print(f'FAIL: old weak pattern remains: {bad}')
        sys.exit(1)

# Verify parseCarHeader delegates to strict version
if 'function parseCarHeader(data)' in text:
    # Should be a wrapper
    idx = text.index('function parseCarHeader(data)')
    body = text[idx:idx+200]
    if 'parseCarHeaderStrict' not in body:
        print('FAIL: parseCarHeader does not delegate to parseCarHeaderStrict')
        sys.exit(1)

print('DOWNLOAD_NFT_CARS_RECOVERY_CAR_PARSER_STRICT_OK')
