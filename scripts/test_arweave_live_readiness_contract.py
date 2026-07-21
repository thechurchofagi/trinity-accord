#!/usr/bin/env python3
"""Arweave live-readiness and retired-path contract.

The current native archive route must remain live-capable and exact-pinned.
Legacy hash-chain/Phase-5 canaries must remain read-only and unable to access
wallet secrets or report repository writes.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def main() -> int:
    errors: list[str] = []

    uploader = ROOT / "scripts" / "arweave_upload_payload.mjs"
    if not uploader.exists():
        errors.append("scripts/arweave_upload_payload.mjs missing")
    else:
        text = uploader.read_text(encoding="utf-8")
        if "process.env.ARKEY" not in text:
            errors.append("arweave_upload_payload.mjs does not reference process.env.ARKEY")
        else:
            ok("current uploader references ARKEY")
        if "arweave.transactions.sign" not in text:
            errors.append("arweave_upload_payload.mjs does not sign transactions")
        else:
            ok("current uploader signs transactions")
        if "arweave.transactions.post" not in text:
            errors.append("arweave_upload_payload.mjs does not post transactions")
        else:
            ok("current uploader posts transactions")

    builder = ROOT / "scripts" / "build_record_chain_arweave_archive.py"
    if not builder.exists():
        errors.append("scripts/build_record_chain_arweave_archive.py missing")
    else:
        text = builder.read_text(encoding="utf-8")
        if "ARKEY" not in text:
            errors.append("current native archive builder does not reference ARKEY")
        else:
            ok("current native archive builder references ARKEY")
        if "ARWEAVE_WALLET_JWK_B64" in text:
            errors.append("current native archive builder still requires ARWEAVE_WALLET_JWK_B64")
        else:
            ok("current native archive builder does not require obsolete wallet secret")
        if "load_native_chain_sources" not in text or "trinity-accord-public-reception-ledger" not in text:
            errors.append("current archive builder is not bound to the native Record-Chain")
        else:
            ok("current archive builder is bound to the native Record-Chain")

    runner = ROOT / "scripts" / "run_record_chain_arweave_archive.py"
    if not runner.exists():
        errors.append("scripts/run_record_chain_arweave_archive.py missing")
    else:
        text = runner.read_text(encoding="utf-8")
        for marker in [
            "import build_record_chain_arweave_archive as builder",
            "builder.build_archive_manifest",
            "builder.upload_to_arweave = guarded_upload",
            "Resuming Arweave readback without a new paid post",
        ]:
            if marker not in text:
                errors.append(f"current native archive runner missing: {marker}")
        if not any(error.startswith("current native archive runner missing") for error in errors):
            ok("current crash-safe runner invokes the authoritative native builder")

    current_workflow = ROOT / ".github" / "workflows" / "record-chain-arweave-archive.yml"
    if not current_workflow.exists():
        errors.append("current native archive workflow missing")
    else:
        text = current_workflow.read_text(encoding="utf-8")
        if "secrets.ARKEY" not in text:
            errors.append("current native archive workflow does not use secrets.ARKEY")
        else:
            ok("current native archive workflow uses ARKEY")
        if "contents: write" not in text or "group: main-write-lock" not in text:
            errors.append("current native archive workflow lacks write serialization")
        else:
            ok("current native archive workflow is serialized with main-write-lock")
        if "run_record_chain_arweave_archive.py" not in text:
            errors.append("current native archive workflow does not invoke the crash-safe native runner")
        else:
            ok("current native archive workflow invokes the crash-safe native runner")

    retired_paths = {
        "legacy data archive": ROOT / ".github/workflows/record-chain-data-arweave-archive.yml",
        "Phase 5 paid OTS": ROOT / ".github/workflows/phase5-ots-arweave-paid-upload.yml",
        "paid echo canary": ROOT / ".github/workflows/paid-echo-arweave-canary.yml",
    }
    for label, path in retired_paths.items():
        if not path.exists():
            errors.append(f"{label} workflow missing")
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in ("contents: write", "secrets.ARKEY", "git push"):
            if forbidden in text:
                errors.append(f"{label} retains forbidden capability: {forbidden}")
        if "Retired" not in text and "retired" not in text:
            errors.append(f"{label} does not declare retirement")
        else:
            ok(f"{label} is explicitly retired and read-only")

    legacy_builder = ROOT / "scripts" / "build_record_chain_data_arweave_bundle.py"
    legacy_updater = ROOT / "scripts" / "update_record_chain_data_arweave_registry.py"
    bundle_verifier = ROOT / "scripts" / "verify_record_chain_data_arweave_bundle.py"
    for path in (legacy_builder, legacy_updater, bundle_verifier):
        if not path.exists():
            errors.append(f"missing historical archive boundary tool: {path.relative_to(ROOT)}")
    if legacy_builder.exists():
        text = legacy_builder.read_text(encoding="utf-8")
        for required in ("historical recovery/audit tooling only", "bundle_identity_sha256", "not_current_native_record_chain"):
            if required not in text:
                errors.append(f"legacy builder missing boundary/determinism marker: {required}")
    if legacy_updater.exists():
        text = legacy_updater.read_text(encoding="utf-8")
        if "legacy record-chain data Arweave uploads are retired" not in text or "would_write_registry" not in text:
            errors.append("legacy registry updater is not fail-closed/read-only")

    behavior = ROOT / "scripts" / "test_legacy_arweave_retirement_behavior.py"
    if not behavior.exists():
        errors.append("legacy Arweave retirement behavioral regression missing")
    else:
        result = subprocess.run(
            [sys.executable, str(behavior)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            errors.append(
                "legacy Arweave retirement behavioral regression failed: "
                + (result.stderr or result.stdout)[-4000:]
            )
        else:
            ok("legacy Arweave retirement behavioral regression passes")

    package = ROOT / "package.json"
    if not package.exists():
        errors.append("package.json missing")
    else:
        data = json.loads(package.read_text(encoding="utf-8"))
        dependencies = data.get("dependencies", {})
        arweave_version = dependencies.get("arweave")
        if not arweave_version:
            errors.append("package.json missing arweave dependency")
        elif any(marker in str(arweave_version) for marker in ("^", "~")) or str(arweave_version) == "latest":
            errors.append(f"package.json arweave not exact-pinned: {arweave_version}")
        else:
            ok(f"package.json arweave exact-pinned: {arweave_version}")
        for name, version in dependencies.items():
            if any(marker in str(version) for marker in ("^", "~")) or str(version) == "latest":
                errors.append(f"package.json dependency {name} uses range: {version}")

    if errors:
        print("FAIL: Arweave live/retired boundary errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nPASS: current native Arweave path is live-ready; legacy paid paths are retired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
