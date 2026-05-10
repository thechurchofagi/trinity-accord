#!/usr/bin/env python3
"""TA-REDTEAM-2026-007: recovery source binding."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "download-nft-cars.mjs"
SHA_FILE = ROOT / "archive" / "evidence" / "nft-recovery-package" / "recovery-package.sha256"

text = SRC.read_text(encoding="utf-8")

required = [
    "EXPECTED_RECOVERY_PACKAGE_SHA256",
    "verifyRecoveryPackageSource",
    "readExpectedRecoveryPackageSha256",
    "RECOVERY_PACKAGE_SHA256_FILE",
    "Recovery package sha256 mismatch",
    "refusing to use unauthenticated recovery package",
    "source_recovery_package",
    "source_token_index",
    "source_binding",
    "stableStringify",
]

for token in required:
    if token not in text:
        print(f"FAIL: missing: {token}")
        sys.exit(1)

if not SHA_FILE.exists():
    print(f"FAIL: missing expected recovery package sha256 file: {SHA_FILE}")
    sys.exit(1)

sha_text = SHA_FILE.read_text(encoding="utf-8").strip()
if not re.match(r"^[a-f0-9]{64}\s+recovery-package\.bin$", sha_text):
    print("FAIL: recovery-package.sha256 must be '<64hex> recovery-package.bin'")
    sys.exit(1)

print("DOWNLOAD_NFT_CARS_SOURCE_BINDING_OK")
