#!/usr/bin/env python3
"""Operator secret names contract.

The repository intentionally uses existing GitHub secret names:
ARKEY, ETH_RPC, GH_PAT, RENDER.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_NAMES = ["ARKEY", "ETH_RPC", "GH_PAT", "RENDER"]

def main() -> int:
    errors: list[str] = []

    docs = ROOT / "docs" / "operator-secrets.md"
    if not docs.exists():
        errors.append("docs/operator-secrets.md missing")
    else:
        text = docs.read_text(encoding="utf-8")
        for name in REQUIRED_NAMES:
            if name not in text:
                errors.append(f"docs/operator-secrets.md missing {name}")

    script = ROOT / "scripts" / "smoke_check_configured_secrets.py"
    if not script.exists():
        errors.append("scripts/smoke_check_configured_secrets.py missing")
    else:
        text = script.read_text(encoding="utf-8")
        for name in REQUIRED_NAMES:
            if f'"{name}"' not in text and f"'{name}'" not in text:
                errors.append(f"secret smoke script does not reference {name}")

    workflow = ROOT / ".github" / "workflows" / "operator-secret-smoke.yml"
    if not workflow.exists():
        errors.append(".github/workflows/operator-secret-smoke.yml missing")
    else:
        text = workflow.read_text(encoding="utf-8")
        for name in REQUIRED_NAMES:
            if f"secrets.{name}" not in text:
                errors.append(f"operator-secret-smoke.yml does not use secrets.{name}")

    arweave_wf = ROOT / ".github" / "workflows" / "record-chain-arweave-archive.yml"
    if arweave_wf.exists():
        text = arweave_wf.read_text(encoding="utf-8")
        if "secrets.ARKEY" not in text:
            errors.append("record-chain-arweave-archive.yml must use secrets.ARKEY")
        if "secrets.ARWEAVE_WALLET_JWK_B64" in text:
            errors.append("record-chain-arweave-archive.yml must not require ARWEAVE_WALLET_JWK_B64")

    if errors:
        print("FAIL: operator secret names contract errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("PASS: operator secret names contract")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
