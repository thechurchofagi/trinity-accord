#!/usr/bin/env python3
"""Test bootstrap materials consistency (TA-REDTEAM-2026-014).

Checks:
- api/authority.json has exactly 3 Bitcoin Originals
- RECOVERY.md contains all 3 inscription IDs
- api/recovery-index.json contains same IDs
- authority BTC address matches across files
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

INSCRIPTION_IDS = ["97631551", "98369145", "98387475"]
BTC_ADDRESS = "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf"


def main():
    errors = []

    # Check authority.json
    auth_path = ROOT / "api" / "authority.json"
    if auth_path.exists():
        auth = json.loads(auth_path.read_text(encoding="utf-8"))
        originals = auth.get("bitcoin_originals", [])
        if len(originals) != 3:
            errors.append(f"authority.json has {len(originals)} bitcoin_originals, expected 3")
        for oid in INSCRIPTION_IDS:
            if not any(o.get("inscription_id") == oid for o in originals):
                errors.append(f"authority.json missing inscription_id {oid}")
        addr = auth.get("bitcoin_authority_address", "")
        if addr != BTC_ADDRESS:
            errors.append(f"authority.json BTC address mismatch: {addr}")
    else:
        errors.append("api/authority.json missing")

    # Check RECOVERY.md
    recovery_path = ROOT / "RECOVERY.md"
    if recovery_path.exists():
        text = recovery_path.read_text(encoding="utf-8")
        for oid in INSCRIPTION_IDS:
            if oid not in text:
                errors.append(f"RECOVERY.md missing inscription_id {oid}")
        if BTC_ADDRESS not in text:
            errors.append(f"RECOVERY.md missing BTC address")
    else:
        errors.append("RECOVERY.md missing")

    # Check recovery-index.json
    ri_path = ROOT / "api" / "recovery-index.json"
    if ri_path.exists():
        ri = json.loads(ri_path.read_text(encoding="utf-8"))
        root = ri.get("minimal_trusted_bootstrap_root", {})
        originals = root.get("bitcoin_originals", [])
        if len(originals) != 3:
            errors.append(f"recovery-index has {len(originals)} bitcoin_originals, expected 3")
        for oid in INSCRIPTION_IDS:
            if not any(o.get("inscription_id") == oid for o in originals):
                errors.append(f"recovery-index missing inscription_id {oid}")
        addr = root.get("bitcoin_authority_address", "")
        if addr != BTC_ADDRESS:
            errors.append(f"recovery-index BTC address mismatch: {addr}")
    else:
        errors.append("api/recovery-index.json missing")

    if errors:
        print("BOOTSTRAP_MATERIALS_FAIL")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print("BOOTSTRAP_MATERIALS_OK")


if __name__ == "__main__":
    main()
