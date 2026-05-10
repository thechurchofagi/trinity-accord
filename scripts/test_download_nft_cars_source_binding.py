#!/usr/bin/env python3
"""TA-REDTEAM-2026-007: recovery source binding."""
from pathlib import Path
import sys

SRC = Path(__file__).resolve().parents[1] / 'scripts' / 'download-nft-cars.mjs'
text = SRC.read_text(encoding='utf-8')

required = [
    'EXPECTED_RECOVERY_PACKAGE_SHA256',
    'verifyRecoveryPackageSource',
    'readExpectedRecoveryPackageSha256',
    'RECOVERY_PACKAGE_SHA256_FILE',
    'Recovery package sha256 mismatch',
    'refusing to use unauthenticated recovery package',
    'source_recovery_package',
    'stableStringify',
]

for token in required:
    if token not in text:
        print(f'FAIL: missing: {token}')
        sys.exit(1)

print('DOWNLOAD_NFT_CARS_SOURCE_BINDING_OK')
