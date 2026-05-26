#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CODEOWNERS = ROOT / "CODEOWNERS"
text = CODEOWNERS.read_text(encoding="utf-8")

REQUIRED = [
    "archive/authority-manifest/",
    "archive/btc-signature/",
    "archive/eth-witness/",
    "archive/evidence/digest-manifest.json",
    "archive/evidence/digest-manifest.csv",
    "archive/evidence/verify-report.json",
    "archive/evidence/ots-proofs/",
    "archive/evidence/nft-recovery-package/recovery-package.bin",
    "archive/evidence/nft-recovery-package/recovery-package.sha256",
    "scripts/verify-full-evidence-chain.mjs",
    "scripts/verify-signed-manifest-coverage.mjs",
    "scripts/verify-ots-time-anchor.mjs",
    "scripts/verify-onchain-tokenuri.mjs",
    "scripts/verify-dag-and-signed-cids.mjs",
    "archive/trust-root-policy.json",
    "CODEOWNERS",
]

missing = [p for p in REQUIRED if p not in text]
if missing:
    print("FAIL: CODEOWNERS missing trust-root paths:")
    for p in missing:
        print(f"  - {p}")
    sys.exit(1)

if "@thechurchofagi" not in text:
    print("FAIL: expected owner @thechurchofagi missing")
    sys.exit(1)

print("CODEOWNERS_TRUST_ROOT_PATHS_OK")
