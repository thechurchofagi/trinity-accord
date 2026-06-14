#!/usr/bin/env python3
"""Test: Phase 5 OTS-Arweave accepts ots_status=upgraded with boundary checks."""
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase5_ots_arweave_paid_upload.py"

spec = importlib.util.spec_from_file_location("phase5", SCRIPT)
assert spec and spec.loader
phase5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(phase5)


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_upgraded_accepted() -> None:
    """upgraded OTS status is accepted when bitcoin_attestation_embedded=true."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        phase5.ROOT = tmp

        anchored = tmp / "record-chain/ots/anchors/test.record-chain-head-commitment.json"
        ots = tmp / "record-chain/ots/anchors/test.record-chain-head-commitment.json.ots"
        anchor = tmp / "record-chain/ots/anchors/test.anchor.json"
        latest = tmp / "api/record-chain-ots-latest.json"

        anchored.parent.mkdir(parents=True, exist_ok=True)
        anchored.write_text("test anchored commitment\n", encoding="utf-8")
        ots.write_bytes(b"test ots proof")

        anchored_sha = phase5.sha256_file(anchored)
        ots_sha = phase5.sha256_file(ots)

        write_json(anchor, {
            "schema": "trinity_record_chain_ots_anchor.v1",
            "chain_id": "trinity-record-chain-main",
            "ots_status": "upgraded",
            "anchored_file": str(anchored.relative_to(tmp)),
            "anchored_file_sha256": anchored_sha,
            "ots_file": str(ots.relative_to(tmp)),
            "ots_file_sha256": ots_sha,
        })

        write_json(latest, {
            "schema": "trinity_record_chain_ots_latest.v1",
            "chain_id": "trinity-record-chain-main",
            "ots_status": "upgraded",
            "bitcoin_attestation_embedded": True,
            "bitcoin_pending": False,
            "height": 1,
            "entry_count": 1,
            "head_entry_hash": "a" * 64,
            "latest_anchor_file": str(anchor.relative_to(tmp)),
            "latest_anchored_file": str(anchored.relative_to(tmp)),
            "latest_ots_file": str(ots.relative_to(tmp)),
        })

        loaded_latest = phase5.validate_latest_ots(latest)
        assert loaded_latest["ots_status"] == "upgraded"
        loaded_anchor = phase5.validate_anchor(loaded_latest["latest_anchor_file"])
        assert loaded_anchor["ots_status"] == "upgraded"


def test_dry_run_refused() -> None:
    """dry_run OTS status is refused."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        phase5.ROOT = tmp

        latest = tmp / "api/record-chain-ots-latest.json"
        write_json(latest, {
            "schema": "trinity_record_chain_ots_latest.v1",
            "chain_id": "trinity-record-chain-main",
            "ots_status": "dry_run",
            "height": 1,
            "entry_count": 1,
            "head_entry_hash": "a" * 64,
            "latest_anchor_file": "record-chain/ots/anchors/test.anchor.json",
            "latest_anchored_file": "record-chain/ots/anchors/test.json",
            "latest_ots_file": "record-chain/ots/anchors/test.json.ots",
        })

        try:
            phase5.validate_latest_ots(latest)
            assert False, "Should have raised SystemExit for dry_run"
        except SystemExit as e:
            assert "dry_run" in str(e)


def test_upgraded_without_bitcoin_attestation_refused() -> None:
    """upgraded without bitcoin_attestation_embedded=true is refused."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        phase5.ROOT = tmp

        latest = tmp / "api/record-chain-ots-latest.json"
        write_json(latest, {
            "schema": "trinity_record_chain_ots_latest.v1",
            "chain_id": "trinity-record-chain-main",
            "ots_status": "upgraded",
            "bitcoin_attestation_embedded": False,
            "bitcoin_pending": False,
            "height": 1,
            "entry_count": 1,
            "head_entry_hash": "a" * 64,
            "latest_anchor_file": "record-chain/ots/anchors/test.anchor.json",
            "latest_anchored_file": "record-chain/ots/anchors/test.json",
            "latest_ots_file": "record-chain/ots/anchors/test.json.ots",
        })

        try:
            phase5.validate_latest_ots(latest)
            assert False, "Should have raised SystemExit"
        except SystemExit as e:
            assert "bitcoin_attestation_embedded" in str(e)


if __name__ == "__main__":
    test_upgraded_accepted()
    test_dry_run_refused()
    test_upgraded_without_bitcoin_attestation_refused()
    print("PASS: Phase 5 OTS-Arweave upgraded status contract")
