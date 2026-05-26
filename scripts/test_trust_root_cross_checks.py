#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

checks = [
    ["python3", "scripts/validate_authority_manifest.py", "archive/authority-manifest/authority.jcs.json"],
    ["python3", "scripts/validate_btc_signature_manifest.py", "archive/btc-signature/btc-signature.json"],
    ["python3", "scripts/validate_eth_witness_manifest.py", "archive/eth-witness/eth-witness.json"],
    ["python3", "scripts/validate_trust_root_policy.py", "archive/trust-root-policy.json"],
]

for cmd in checks:
    res = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if res.returncode != 0:
        print("FAIL:", " ".join(cmd))
        print(res.stdout)
        print(res.stderr)
        sys.exit(res.returncode)

# Static markers in full verifier.
vf = (ROOT / "scripts" / "verify-full-evidence-chain.mjs").read_text(encoding="utf-8")
required = [
    "AUTHORITY_JCS_FILE",
    "BTC_SIG_FILE",
    "ETH_WITNESS_FILE",
    "btc_minter_address",
    "eth_address",
    "message_sha256",
    "input_sha256",
]
for token in required:
    if token not in vf:
        print(f"FAIL: verify-full-evidence-chain.mjs missing cross-check marker: {token}")
        sys.exit(1)

print("TRUST_ROOT_CROSS_CHECKS_OK")
