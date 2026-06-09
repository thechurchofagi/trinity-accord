#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from record_chain_hashing import build_native_record_chain_head_commitment  # noqa: E402


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"OK: {message}")


def test_native_commitment_binds_current_head() -> None:
    commitment = build_native_record_chain_head_commitment(ROOT)
    tip = json.loads((ROOT / "record-chain" / "chain-tip.json").read_text())
    text = json.dumps(commitment, sort_keys=True)

    if commitment.get("schema") != "trinityaccord.native-record-chain-head-commitment.v1":
        fail("native commitment schema mismatch")
    if commitment.get("latest_record_id") != tip.get("latest_record_id"):
        fail("native commitment latest_record_id must match chain-tip")
    if commitment.get("latest_record_sha256") != tip.get("latest_record_sha256"):
        fail("native commitment latest_record_sha256 must match chain-tip")
    if commitment.get("native_record_count") != tip.get("native_record_count"):
        fail("native commitment native_record_count must match chain-tip")

    expected_id = tip.get("latest_record_id")
    expected_count = tip.get("native_record_count")
    if commitment.get("latest_record_id") != expected_id:
        fail(f"M9 native commitment must include {expected_id}")
    if commitment.get("native_record_count") != expected_count:
        fail(f"M9 native commitment must include native_record_count={expected_count}")
    if "main.chain.jsonl" in text:
        fail("native commitment must not reference legacy main.chain.jsonl")

    coverage = commitment.get("record_coverage", {})
    if coverage.get("source") != "record-chain/indexes/record-index.json":
        fail("native commitment record_coverage must use record-index")
    if coverage.get("record_count") != expected_count:
        fail(f"native commitment record_coverage must include {expected_count} records")
    if coverage.get("last_record_id") != expected_id:
        fail(f"native commitment record_coverage must end at {expected_id}")
    if len(coverage.get("records", [])) != expected_count:
        fail(f"native commitment records list must include {expected_count} records")

    source_files = commitment.get("source_files", {})
    for key in ["chain_tip", "record_index", "latest_record", "guardian_state", "statistics", "batch_index"]:
        ref = source_files.get(key)
        if not isinstance(ref, dict) or not ref.get("path") or not ref.get("sha256"):
            fail(f"native commitment missing source file ref: {key}")

    ok("native commitment binds current native head")


def test_native_ots_script_dry_run() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        out_dir = tmp / "native-anchors"
        api_out = tmp / "record-chain-native-ots-latest.json"
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "ots_anchor_native_record_chain_head.py"),
            "--mode", "dry-run",
            "--out-dir", str(out_dir),
            "--api-out", str(api_out),
            "--overwrite",
        ]
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            fail("native OTS dry-run failed")

        latest = json.loads(api_out.read_text())
        tip = json.loads((ROOT / "record-chain" / "chain-tip.json").read_text())
        if latest.get("schema") != "trinityaccord.native-record-chain-ots-latest.v1":
            fail("native latest schema mismatch")
        if latest.get("latest_record_id") != tip.get("latest_record_id"):
            fail(f"native latest must reference {tip.get('latest_record_id')}")
        if latest.get("native_record_count") != tip.get("native_record_count"):
            fail(f"native latest must reference native_record_count={tip.get('native_record_count')}")
        if latest.get("legacy_main_chain_jsonl_is_not_source") is not True:
            fail("native latest must declare legacy main.chain.jsonl is not source")

        anchored = Path(latest["latest_anchored_file"])
        if not anchored.exists():
            fail("native anchored commitment file missing")
        anchored_text = anchored.read_text()
        if "main.chain.jsonl" in anchored_text:
            fail("native anchored commitment must not mention main.chain.jsonl")

    ok("native OTS dry-run writes native latest")


def test_legacy_ots_refuses_stale_jsonl() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "ots_anchor_record_chain_head.py"),
            "--mode", "dry-run",
            "--out-dir", str(tmp / "legacy-anchors"),
            "--api-out", str(tmp / "legacy-ots-latest.json"),
        ]
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        if result.returncode == 0:
            fail("legacy OTS script must refuse stale main.chain.jsonl when native chain-tip is ahead")
        combined = result.stdout + result.stderr
        if "Refusing to anchor stale legacy main.chain.jsonl" not in combined:
            fail("legacy OTS refusal message missing")

    ok("legacy OTS refuses stale JSONL by default")


def test_arweave_builder_source_markers() -> None:
    text = (ROOT / "scripts" / "build_record_chain_arweave_archive.py").read_text()

    required = [
        "load_native_chain_sources",
        "record-chain/indexes/record-index.json",
        "source_type",
        "native-record-chain",
        "legacy_main_chain_jsonl_is_not_source",
        "batch_manifests_are_auxiliary",
        "native_record_count",
        "latest_record_id",
        "archive-native-",
    ]
    for marker in required:
        if marker not in text:
            fail(f"arweave builder missing native marker: {marker}")

    forbidden_pattern = 'for rid in mf.get("record_ids", [])'
    if forbidden_pattern in text:
        fail("arweave builder must not derive authoritative included_records from batch manifest record_ids")

    ok("arweave builder uses native record-index markers")


def test_arweave_verifier_source_markers() -> None:
    text = (ROOT / "scripts" / "verify_record_chain_arweave_archive.py").read_text()

    required = [
        "source_type",
        "native-record-chain",
        "included_records does not cover native_record_count",
        "latest native record missing",
        "legacy JSONL is not source",
    ]
    for marker in required:
        if marker not in text:
            fail(f"arweave verifier missing native marker: {marker}")

    ok("arweave verifier has native coverage checks")


def main() -> None:
    test_native_commitment_binds_current_head()
    test_native_ots_script_dry_run()
    test_legacy_ots_refuses_stale_jsonl()
    test_arweave_builder_source_markers()
    test_arweave_verifier_source_markers()
    print("PASS: native record-chain archive tooling tests")


if __name__ == "__main__":
    main()
