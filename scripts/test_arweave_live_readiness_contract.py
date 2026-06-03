#!/usr/bin/env python3
"""Phase 6C: Arweave live readiness contract.

Verifies that the Arweave live upload implementation is properly configured.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def main() -> int:
    errors: list[str] = []

    # 1. arweave_upload_payload.mjs exists and references ARKEY
    uploader = ROOT / "scripts" / "arweave_upload_payload.mjs"
    if not uploader.exists():
        errors.append("scripts/arweave_upload_payload.mjs missing")
    else:
        text = uploader.read_text(encoding="utf-8")
        if "process.env.ARKEY" not in text:
            errors.append("arweave_upload_payload.mjs does not reference process.env.ARKEY")
        else:
            ok("arweave_upload_payload.mjs references ARKEY")
        if "arweave.transactions.sign" not in text:
            errors.append("arweave_upload_payload.mjs does not sign transactions")
        else:
            ok("arweave_upload_payload.mjs signs transactions")
        if "arweave.transactions.post" not in text:
            errors.append("arweave_upload_payload.mjs does not post transactions")
        else:
            ok("arweave_upload_payload.mjs posts transactions")

    # 2. build_record_chain_arweave_archive.py references ARKEY, not ARWEAVE_WALLET_JWK_B64
    builder = ROOT / "scripts" / "build_record_chain_arweave_archive.py"
    if not builder.exists():
        errors.append("scripts/build_record_chain_arweave_archive.py missing")
    else:
        text = builder.read_text(encoding="utf-8")
        if "ARKEY" not in text:
            errors.append("build_record_chain_arweave_archive.py does not reference ARKEY")
        else:
            ok("build_record_chain_arweave_archive.py references ARKEY")
        if "ARWEAVE_WALLET_JWK_B64" in text:
            errors.append("build_record_chain_arweave_archive.py still requires ARWEAVE_WALLET_JWK_B64")
        else:
            ok("build_record_chain_arweave_archive.py does not require ARWEAVE_WALLET_JWK_B64")
        if "Live Arweave upload is not implemented" in text:
            errors.append("build_record_chain_arweave_archive.py still says live upload is not implemented")
        else:
            ok("build_record_chain_arweave_archive.py does not claim live upload unimplemented")

    # 3. record-chain-arweave-archive.yml uses secrets.ARKEY
    wf = ROOT / ".github" / "workflows" / "record-chain-arweave-archive.yml"
    if not wf.exists():
        errors.append(".github/workflows/record-chain-arweave-archive.yml missing")
    else:
        text = wf.read_text(encoding="utf-8")
        if "secrets.ARKEY" not in text:
            errors.append("record-chain-arweave-archive.yml does not use secrets.ARKEY")
        else:
            ok("record-chain-arweave-archive.yml uses secrets.ARKEY")
        if "secrets.ARWEAVE_WALLET_JWK_B64" in text:
            errors.append("record-chain-arweave-archive.yml must not require ARWEAVE_WALLET_JWK_B64")
        else:
            ok("record-chain-arweave-archive.yml does not require ARWEAVE_WALLET_JWK_B64")

    # 4. package.json has exact-pinned arweave
    pkg = ROOT / "package.json"
    if not pkg.exists():
        errors.append("package.json missing")
    else:
        data = json.loads(pkg.read_text(encoding="utf-8"))
        deps = data.get("dependencies", {})
        arweave_ver = deps.get("arweave")
        if not arweave_ver:
            errors.append("package.json missing arweave dependency")
        elif "^" in str(arweave_ver) or "~" in str(arweave_ver) or str(arweave_ver) == "latest":
            errors.append(f"package.json arweave not exact-pinned: {arweave_ver}")
        else:
            ok(f"package.json arweave exact-pinned: {arweave_ver}")

        # No dependency uses ^, ~, or latest
        for name, ver in deps.items():
            if "^" in str(ver) or "~" in str(ver) or str(ver) == "latest":
                errors.append(f"package.json dependency {name} uses range: {ver}")

    if errors:
        print("FAIL: Arweave live readiness contract errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\nPASS: Arweave live readiness contract verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
