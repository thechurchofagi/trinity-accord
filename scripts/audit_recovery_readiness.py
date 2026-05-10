#!/usr/bin/env python3
"""Audit recovery readiness — read-only check that recovery materials exist (TA-REDTEAM-2026-014).

Usage:
  python3 scripts/audit_recovery_readiness.py
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "RECOVERY.md",
    "DISASTER-RECOVERY-DRILL.md",
    "api/recovery-index.json",
    "api/recovery-index-schema.v1.json",
    "api/corrections-index.json",
    "archive/authority-manifest/authority.jcs.json",
    "archive/btc-signature/btc-signature.json",
    "archive/eth-witness/eth-witness.json",
    "archive/trust-root-policy.json",
    "archive/evidence/digest-manifest.json",
    "archive/evidence/digest-manifest.csv",
    "scripts/verify-release-assets.mjs",
    "scripts/verify-full-evidence-chain.mjs",
    "requirements-ci.txt",
    ".node-version",
]

COMMANDS = [
    ["python3", "scripts/validate_recovery_index.py"],
    ["python3", "scripts/validate_corrections_index.py"],
    ["python3", "scripts/validate_authority_manifest.py", "archive/authority-manifest/authority.jcs.json"],
    ["python3", "scripts/validate_btc_signature_manifest.py", "archive/btc-signature/btc-signature.json"],
    ["python3", "scripts/validate_eth_witness_manifest.py", "archive/eth-witness/eth-witness.json"],
    ["python3", "scripts/validate_public_api_metadata.py"],
]


def main():
    errors = []

    # Check required files exist
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            errors.append(f"missing required recovery file: {rel}")

    # Check public surfaces reference recovery-index
    for rel in ["llms.txt", "ai.txt", "sitemap.xml", "api/links.json"]:
        path = ROOT / rel
        if path.exists() and "recovery-index" not in path.read_text(encoding="utf-8"):
            errors.append(f"{rel} does not reference recovery-index")
        elif not path.exists():
            errors.append(f"{rel} missing")

    # Run validators
    for cmd in COMMANDS:
        r = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        if r.returncode != 0:
            errors.append(f"command failed: {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")

    if errors:
        print("RECOVERY_READINESS_FAIL")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print("RECOVERY_READINESS_OK")


if __name__ == "__main__":
    main()
