#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OTS_LATEST = ROOT / "api/record-chain-native-ots-latest.json"
OTS_BACKLOG = ROOT / "record-chain/ots/native-ots-backlog.json"
OTS_API_BACKLOG = ROOT / "api/record-chain-native-ots-backlog.json"
NATIVE_ANCHORS = ROOT / "record-chain/ots/native-anchors"
NATIVE_BUNDLES = ROOT / "record-chain/ots/native-arweave-bundles"
NATIVE_REGISTRY = ROOT / "record-chain/ots/native-arweave-registry.json"
NATIVE_API_REGISTRY = ROOT / "api/record-chain-native-ots-arweave-registry.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def backup(path: Path, tmp: Path) -> None:
    if path.exists():
        shutil.copy2(path, tmp / path.name)


def restore(path: Path, tmp: Path) -> None:
    b = tmp / path.name
    if b.exists():
        shutil.copy2(b, path)


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        for p in [OTS_LATEST, OTS_BACKLOG, OTS_API_BACKLOG, NATIVE_REGISTRY, NATIVE_API_REGISTRY]:
            backup(p, tmp)

        latest_pending_anchor = NATIVE_ANCHORS / "zz-contract-native-record-004.anchor.json"
        historical_pending_anchor = NATIVE_ANCHORS / "zz-contract-native-record-001.anchor.json"
        historical_upgraded_anchor = NATIVE_ANCHORS / "zz-contract-native-record-002.anchor.json"
        historical_verified_anchor = NATIVE_ANCHORS / "zz-contract-native-record-003.anchor.json"
        upgraded_bundle = NATIVE_BUNDLES / "zz-contract-native-record-002.upgraded.arweave-bundle.json"

        created = [
            latest_pending_anchor,
            historical_pending_anchor,
            historical_upgraded_anchor,
            historical_verified_anchor,
            upgraded_bundle,
        ]

        try:
            pending_sha = "1" * 64
            upgraded_sha = "2" * 64
            verified_sha = "3" * 64
            latest_sha = "4" * 64

            write_json(OTS_LATEST, {
                "schema": "trinityaccord.native-record-chain-ots-latest.v1",
                "anchored_file_sha256": latest_sha,
                "bitcoin_pending": True,
                "bitcoin_verified": False,
                "chain_id": "trinity-accord-public-reception-ledger",
                "created_at": "2026-06-10T00:00:00Z",
                "latest_anchor_file": str(latest_pending_anchor.relative_to(ROOT)),
                "latest_anchored_file": "contract/latest-native-head.json",
                "latest_ots_file": "contract/latest-native-head.json.ots",
                "latest_record_id": "R-000000004",
                "latest_record_index": 4,
                "latest_record_sha256": "a" * 64,
                "legacy_main_chain_jsonl_is_not_source": True,
                "native_record_count": 4,
                "ots_status": "pending",
                "record_coverage": {
                    "first_record_id": "R-000000001",
                    "last_record_id": "R-000000004",
                    "record_count": 4,
                    "source": "record-chain/indexes/record-index.json",
                },
                "semantics": "contract fixture",
                "source_semantics": "native_chain_tip_records_indexes_batches.v1",
                "updated_at": "2026-06-10T00:00:00Z",
            })

            def anchor(path: Path, idx: int, sha: str, status: str) -> None:
                write_json(path, {
                    "schema": "trinityaccord.native-record-chain-ots-anchor.v1",
                    "latest_record_index": idx,
                    "native_record_count": idx,
                    "anchored_file": f"contract/native-head-{idx}.json",
                    "anchored_file_sha256": sha,
                    "ots_file": f"contract/native-head-{idx}.json.ots",
                    "ots_file_sha256": str(idx) * 64,
                    "ots_status": status,
                    "bitcoin_pending": status == "pending",
                    "bitcoin_verified": status == "verified",
                    "bitcoin_attestation_embedded": status in {"upgraded", "verified"},
                    "strict_bitcoin_verified": status == "verified",
                    "updated_at": "2026-06-09T00:00:00Z",
                })

            anchor(historical_pending_anchor, 1, pending_sha, "pending")
            anchor(historical_upgraded_anchor, 2, upgraded_sha, "upgraded")
            anchor(historical_verified_anchor, 3, verified_sha, "verified")
            anchor(latest_pending_anchor, 4, latest_sha, "pending")

            write_json(upgraded_bundle, {
                "schema": "trinityaccord.native-ots-arweave-bundle.v1",
                "anchored_file_sha256": upgraded_sha,
                "ots_status": "upgraded",
                "bundle_sha256": "b" * 64,
            })

            write_json(NATIVE_REGISTRY, {
                "schema": "trinityaccord.native-ots-arweave-registry.v1",
                "entries": [],
                "created_at": "2026-06-10T00:00:00Z",
                "updated_at": "2026-06-10T00:00:00Z",
            })
            write_json(NATIVE_API_REGISTRY, read_json(NATIVE_REGISTRY))

            run(["python3", "scripts/detect_archive_backlog.py", "--write"])
            backlog = read_json(OTS_BACKLOG)
            items = backlog.get("items", [])
            by_sha = {i.get("anchored_file_sha256"): i for i in items}

            assert by_sha[pending_sha]["archive_status"] == "upgrade_due"
            assert by_sha[pending_sha]["next_action"] == "upgrade_native_ots_anchor"

            assert by_sha[upgraded_sha]["archive_status"] == "pending_upload"
            assert by_sha[upgraded_sha]["next_action"] == "upload_native_ots_bundle"
            assert by_sha[upgraded_sha]["bundle_file"] == str(upgraded_bundle.relative_to(ROOT))

            assert by_sha[verified_sha]["archive_status"] == "pending_upload"
            assert by_sha[verified_sha]["next_action"] == "build_and_upload_native_ots_bundle"

            assert by_sha[latest_sha]["archive_status"] == "waiting_for_upgrade"
            assert by_sha[latest_sha]["next_action"] == "wait_for_ots_upgrade"

            summary = backlog["summary"]
            assert summary["scan_scope"] == "all_native_anchors"
            assert summary["native_anchor_count"] >= 4
            assert summary["upgrade_due_count"] >= 1
            assert summary["pending_upload_count"] >= 2
            assert summary["waiting_for_upgrade_count"] >= 1
            assert "upgrade_completed_prefix_record_index" in summary
            assert "arweave_archive_completed_prefix_record_index" in summary
            assert "first_open_record_index" in summary

            write_json(NATIVE_REGISTRY, {
                "schema": "trinityaccord.native-ots-arweave-registry.v1",
                "entries": [
                    {
                        "anchored_file_sha256": upgraded_sha,
                        "ots_status": "upgraded",
                        "archive_status": "arweave_archived",
                        "tx_id": "CONTRACT_UPGRADED_TX",
                    },
                    {
                        "anchored_file_sha256": verified_sha,
                        "ots_status": "verified",
                        "archive_status": "arweave_archived",
                        "tx_id": "CONTRACT_VERIFIED_TX",
                    },
                ],
                "created_at": "2026-06-10T00:00:00Z",
                "updated_at": "2026-06-10T00:00:00Z",
            })
            write_json(NATIVE_API_REGISTRY, read_json(NATIVE_REGISTRY))

            run(["python3", "scripts/detect_archive_backlog.py", "--write"])
            backlog = read_json(OTS_BACKLOG)
            items = backlog.get("items", [])
            by_sha = {i.get("anchored_file_sha256"): i for i in items}

            if upgraded_sha in by_sha:
                raise SystemExit("archived upgraded anchor should be removed from backlog")
            if verified_sha in by_sha:
                raise SystemExit("archived verified anchor should be removed from backlog")
            if pending_sha not in by_sha:
                raise SystemExit("historical pending anchor should remain upgrade_due")
            if latest_sha not in by_sha:
                raise SystemExit("latest pending anchor should remain waiting_for_upgrade")

            print("PASS: native OTS repair backlog state machine")
        finally:
            for p in [OTS_LATEST, OTS_BACKLOG, OTS_API_BACKLOG, NATIVE_REGISTRY, NATIVE_API_REGISTRY]:
                restore(p, tmp)
            for p in created:
                if p.exists():
                    p.unlink()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
