#!/usr/bin/env python3
"""Arweave live-readiness and retired-path contract.

The current native continuity route remains live-capable, incremental,
crash-safe, exact-pinned, and limited to one weekly automated paid window.
Legacy canaries and standalone heartbeat/OTS upload paths remain read-only or
no-cost and cannot access wallet secrets.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ok(message: str) -> None:
    print(f"PASS: {message}")


def main() -> int:
    errors: list[str] = []

    uploader = ROOT / "scripts/arweave_upload_payload.mjs"
    if not uploader.exists():
        errors.append("scripts/arweave_upload_payload.mjs missing")
    else:
        text = uploader.read_text(encoding="utf-8")
        for marker, label in [
            ("process.env.ARKEY", "references ARKEY"),
            ("arweave.transactions.sign", "signs transactions"),
            ("arweave.transactions.post", "posts transactions"),
            ("ARWEAVE_RESUME_READBACK", "supports readback-only resume"),
        ]:
            if marker not in text:
                errors.append(f"current uploader does not {label}")
            else:
                ok(f"current uploader {label}")

    builder = ROOT / "scripts/build_record_chain_arweave_archive.py"
    if not builder.exists():
        errors.append("current native archive builder missing")
    else:
        text = builder.read_text(encoding="utf-8")
        if "ARKEY" not in text:
            errors.append("current native archive builder does not reference ARKEY")
        else:
            ok("current native archive builder references ARKEY")
        if "ARWEAVE_WALLET_JWK_B64" in text:
            errors.append("current native archive builder requires obsolete wallet secret")
        else:
            ok("current native archive builder rejects obsolete wallet-secret dependency")
        if "load_native_chain_sources" not in text or "trinity-accord-public-reception-ledger" not in text:
            errors.append("current archive builder is not bound to the native Record-Chain")
        else:
            ok("current archive builder is bound to the native Record-Chain")

    runner = ROOT / "scripts/run_record_chain_arweave_archive.py"
    if not runner.exists():
        errors.append("crash-safe native archive runner missing")
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
            ok("current crash-safe runner preserves signing, checkpointing, and readback resume")

    incremental = ROOT / "scripts/run_record_chain_arweave_incremental.py"
    if not incremental.exists():
        errors.append("incremental archive wrapper missing")
    else:
        text = incremental.read_text(encoding="utf-8")
        for marker in [
            "import run_record_chain_arweave_archive as runner",
            "build_incremental_payload_json",
            "runner.builder.build_payload_json = build_incremental_payload_json",
            "runner.main()",
            "evaluate_daily_spend",
        ]:
            if marker not in text:
                errors.append(f"incremental live wrapper missing: {marker}")
        if not any(error.startswith("incremental live wrapper missing") for error in errors):
            ok("incremental wrapper delegates one guarded post to the crash-safe runner")

    continuity_builder = ROOT / "scripts/record_chain_arweave_incremental.py"
    if not continuity_builder.exists():
        errors.append("weekly continuity payload builder missing")
    else:
        text = continuity_builder.read_text(encoding="utf-8")
        for marker in [
            "incremental_delta",
            "previous_archive_txid",
            "does not match the current chain prefix",
            "trinityaccord.weekly-continuity-bundle.v1",
            "trinityaccord.weekly-heartbeat-summary.v1",
            "trinityaccord.weekly-native-ots-evidence.v1",
            "proof_files_embedded_in_this_payload",
        ]:
            if marker not in text:
                errors.append(f"weekly continuity payload builder missing: {marker}")

    current_workflow = ROOT / ".github/workflows/record-chain-arweave-archive.yml"
    if not current_workflow.exists():
        errors.append("current native archive workflow missing")
    else:
        text = current_workflow.read_text(encoding="utf-8")
        if "secrets.ARKEY" not in text:
            errors.append("current native archive workflow does not use secrets.ARKEY")
        else:
            ok("current native archive workflow uses ARKEY")
        if "contents: write" not in text or "group: main-write-lock" not in text or "queue: max" not in text:
            errors.append("current native archive workflow lacks serialized write boundary")
        else:
            ok("current native archive workflow is serialized with main-write-lock")
        if "run_record_chain_arweave_workflow_once.py" not in text:
            errors.append("current native archive workflow does not invoke bounded orchestrator")
        elif "run_record_chain_arweave_archive.py --mode" in text:
            errors.append("current native archive workflow bypasses the incremental route")
        else:
            ok("current native archive workflow invokes the bounded incremental route")
        if (
            'cron: "17 7 * * 3"' not in text
            or 'cron: "17 7 * * *"' in text
            or "Automated upstream event is dry-run only" not in text
        ):
            errors.append("current native archive workflow lacks weekly-live/upstream-dry-run cost boundary")
        else:
            ok("current native archive workflow limits automated paid publication to one weekly schedule")
        if 'if [ "$EVENT_ACTOR" = "github-actions[bot]" ]; then' not in text:
            errors.append("bot workflow dispatch is not prevented from authorizing paid mode")

    heartbeat = ROOT / ".github/workflows/waiting-heartbeat-capsule.yml"
    if not heartbeat.exists():
        errors.append("retired heartbeat capsule workflow missing")
    else:
        text = heartbeat.read_text(encoding="utf-8")
        for forbidden in ["schedule:", "workflow_run:", "secrets.ARKEY", "arweave_upload_waiting_heartbeat_capsule"]:
            if forbidden in text:
                errors.append(f"retired heartbeat capsule retains paid capability: {forbidden}")
        if "contents: read" not in text or "Retired" not in text:
            errors.append("retired heartbeat capsule does not declare read-only retirement")
        else:
            ok("standalone heartbeat capsule upload is retired and read-only")

    daily_ots = ROOT / ".github/workflows/native-ots-upgrade-watch.yml"
    if not daily_ots.exists():
        errors.append("daily Native OTS workflow missing")
    else:
        text = daily_ots.read_text(encoding="utf-8")
        if 'cron: "42 6 * * *"' not in text or "upgrade_only" not in text:
            errors.append("daily Native OTS upgrade/verify lifecycle is not scheduled")
        for forbidden in ["ARKEY", "ARWEAVE_JWK", "--enable-paid-upload", "arweave_runtime_spend_guard.mjs"]:
            if forbidden in text:
                errors.append(f"daily Native OTS retains paid capability: {forbidden}")
        if not any(error.startswith("daily Native OTS") for error in errors):
            ok("daily Native OTS remains automatic but no-cost")

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
        for forbidden in ["contents: write", "secrets.ARKEY", "git push"]:
            if forbidden in text:
                errors.append(f"{label} retains forbidden capability: {forbidden}")
        if "Retired" not in text and "retired" not in text:
            errors.append(f"{label} does not declare retirement")
        else:
            ok(f"{label} is explicitly retired and read-only")

    legacy_builder = ROOT / "scripts/build_record_chain_data_arweave_bundle.py"
    legacy_updater = ROOT / "scripts/update_record_chain_data_arweave_registry.py"
    for path in [legacy_builder, legacy_updater, ROOT / "scripts/verify_record_chain_data_arweave_bundle.py"]:
        if not path.exists():
            errors.append(f"missing historical archive boundary tool: {path.relative_to(ROOT)}")
    if legacy_builder.exists():
        text = legacy_builder.read_text(encoding="utf-8")
        for marker in ["historical recovery/audit tooling only", "bundle_identity_sha256", "not_current_native_record_chain"]:
            if marker not in text:
                errors.append(f"legacy builder missing boundary/determinism marker: {marker}")
    if legacy_updater.exists():
        text = legacy_updater.read_text(encoding="utf-8")
        if "legacy record-chain data Arweave uploads are retired" not in text or "would_write_registry" not in text:
            errors.append("legacy registry updater is not fail-closed/read-only")

    behavior = ROOT / "scripts/test_legacy_arweave_retirement_behavior.py"
    if not behavior.exists():
        errors.append("legacy Arweave retirement behavioral regression missing")
    else:
        result = subprocess.run([sys.executable, str(behavior)], cwd=ROOT, capture_output=True, text=True)
        if result.returncode != 0:
            errors.append("legacy Arweave retirement regression failed: " + (result.stderr or result.stdout)[-4000:])
        else:
            ok("legacy Arweave retirement behavioral regression passes")

    package = ROOT / "package.json"
    if not package.exists():
        errors.append("package.json missing")
    else:
        dependencies = json.loads(package.read_text(encoding="utf-8")).get("dependencies", {})
        arweave_version = dependencies.get("arweave")
        if not arweave_version:
            errors.append("package.json missing arweave dependency")
        elif any(marker in str(arweave_version) for marker in ["^", "~"]) or str(arweave_version) == "latest":
            errors.append(f"package.json arweave not exact-pinned: {arweave_version}")
        else:
            ok(f"package.json arweave exact-pinned: {arweave_version}")
        for name, version in dependencies.items():
            if any(marker in str(version) for marker in ["^", "~"]) or str(version) == "latest":
                errors.append(f"package.json dependency {name} uses range: {version}")

    if errors:
        print("FAIL: Arweave live/retired boundary errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nPASS: weekly incremental Arweave continuity path is live-ready; daily paid paths are retired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
