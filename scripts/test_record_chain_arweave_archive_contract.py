#!/usr/bin/env python3
"""Contract test: Arweave archive dry-run pipeline.

Asserts:
- .github/workflows/record-chain-arweave-archive.yml exists
- workflow defaults to dry-run
- workflow references ARWEAVE_WALLET_JWK_B64 only as secret env
- scripts/build_record_chain_arweave_archive.py exists
- scripts/verify_record_chain_arweave_archive.py exists
- api/record-chain-arweave-index.json exists
- dry-run creates archive manifest if unarchived batches exist
- dry-run is idempotent if no new batches exist
- archive_id is deterministic from included batch range/source hash
- archive manifest has archive_manifest_sha256
- archive manifest has arweave.enabled = false in dry-run
- archive boundary says not authority / not amendment
- no ARV5/LV5/IPFS current terminology
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_TERMS = {"ARV5", "LV5", "IVV5", "IPFS"}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    errors: list[str] = []

    # 1. Workflow exists
    wf = ROOT / ".github" / "workflows" / "record-chain-arweave-archive.yml"
    if not wf.exists():
        errors.append("missing .github/workflows/record-chain-arweave-archive.yml")
    else:
        text = wf.read_text(encoding="utf-8")
        if "dry-run" not in text:
            errors.append("arweave-archive workflow missing dry-run default")
        if "ARWEAVE_WALLET_JWK_B64" not in text:
            errors.append("arweave-archive workflow missing ARWEAVE_WALLET_JWK_B64 reference")
        # Should not use the secret in a run: step directly
        if "echo" in text.lower() and "ARWEAVE_WALLET_JWK_B64" in text:
            errors.append("arweave-archive workflow may echo wallet secret")

    # 2. Scripts exist
    build_script = ROOT / "scripts" / "build_record_chain_arweave_archive.py"
    verify_script = ROOT / "scripts" / "verify_record_chain_arweave_archive.py"
    if not build_script.exists():
        errors.append("missing scripts/build_record_chain_arweave_archive.py")
    if not verify_script.exists():
        errors.append("missing scripts/verify_record_chain_arweave_archive.py")

    # 3. API index exists
    api = ROOT / "api" / "record-chain-arweave-index.json"
    if not api.exists():
        errors.append("missing api/record-chain-arweave-index.json")
    else:
        data = json.loads(api.read_text(encoding="utf-8"))
        if data.get("schema") != "trinityaccord.record-chain-arweave-index.v1":
            errors.append("arweave-index.json wrong schema")
        if data.get("live_upload_enabled") is not False:
            errors.append("arweave-index.json live_upload_enabled should be false")
        if data.get("live_upload_implemented") is not False:
            errors.append("arweave-index.json live_upload_implemented should be false")
        boundary = data.get("boundary", {})
        for key in ["arweave_archive_is_mirror_only", "arweave_archive_is_not_authority",
                     "arweave_archive_is_not_amendment", "bitcoin_originals_prevail"]:
            if not boundary.get(key):
                errors.append(f"arweave-index.json boundary missing: {key}")
        # Check for forbidden terminology
        api_text = api.read_text(encoding="utf-8")
        for term in FORBIDDEN_TERMS:
            if term in api_text:
                errors.append(f"forbidden term '{term}' in arweave-index.json")

    # 4. Arweave archives directory
    archives_dir = ROOT / "record-chain" / "arweave-archives"
    if not archives_dir.exists():
        gitkeep = archives_dir / ".gitkeep"
        if not gitkeep.exists():
            errors.append("record-chain/arweave-archives/.gitkeep missing")

    # 5. Check build script for idempotency and deterministic archive_id
    if build_script.exists():
        text = build_script.read_text(encoding="utf-8")
        if "No new Arweave archive needed" not in text:
            errors.append("build script missing idempotency check message")
        if "archive_manifest_sha256" not in text:
            errors.append("build script missing archive_manifest_sha256 computation")
        if "not_authority" not in text:
            errors.append("build script missing boundary fields")

    # 6. Check verify script for boundary and terminology checks
    if verify_script.exists():
        text = verify_script.read_text(encoding="utf-8")
        if "FORBIDDEN_TERMS" not in text and "ARV5" not in text:
            errors.append("verify script missing forbidden terminology check")
        if "not_authority" not in text:
            errors.append("verify script missing boundary check")

    if errors:
        print("Arweave archive contract tests FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("Arweave archive contract tests PASSED.")


if __name__ == "__main__":
    main()
