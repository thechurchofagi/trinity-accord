#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path, expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if expect_ok and result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise AssertionError(f"command failed: {' '.join(cmd)}")
    if not expect_ok and result.returncode == 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise AssertionError(f"command unexpectedly passed: {' '.join(cmd)}")
    return result


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_ledger(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_ledger(path: Path, entries: list[dict]) -> None:
    path.write_text(
        "".join(
            json.dumps(e, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
            for e in entries
        ),
        encoding="utf-8",
    )


def copy_scripts(work: Path) -> None:
    scripts = work / "scripts"
    scripts.mkdir()
    for name in [
        "record_chain_hashing.py",
        "append_record_chain_link.py",
        "verify_record_chain_integrity.py",
        "build_record_chain_indexes.py",
        "ots_anchor_record_chain_head.py",
        "ots_verify_record_chain_anchor.py",
    ]:
        shutil.copy(REPO_ROOT / "scripts" / name, scripts / name)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="trinity-chain-ots-test-") as tmp:
        work = Path(tmp)
        copy_scripts(work)

        ledger = work / "record-chain/hash-chain/main.chain.jsonl"
        head = work / "api/record-chain-head.json"
        payloads = work / "payloads"
        payloads.mkdir(parents=True)

        test_record_types = [
            "echo",
            "verification",
            "guardian_application",
            "guardian_exit_application",
            "exit_application",
            "custom_future/type:v1",
        ]

        records = []
        for i, record_type in enumerate(test_record_types, start=1):
            record_file = payloads / f"record-{i}.json"
            write_json(
                record_file,
                {
                    "record_type": record_type,
                    "record_id": f"test-record-{i}",
                    "body": f"test payload {i}",
                    "test_run": True,
                },
            )
            records.append((record_type, record_file))

        for i, (record_type, record_file) in enumerate(records, start=1):
            cmd = [
                sys.executable,
                "scripts/append_record_chain_link.py",
                "--ledger",
                str(ledger),
                "--head-out",
                str(head),
                "--record-file",
                str(record_file),
                "--record-type",
                record_type,
                "--record-id",
                f"test-record-{i}",
                "--receipt-id",
                f"rcg-test-{i}",
                "--source-run-id",
                "unit-test",
                "--verify-payload-files",
            ]
            if i == 1:
                cmd.append("--allow-genesis")
            run(cmd, cwd=work)

        run(
            [
                sys.executable,
                "scripts/verify_record_chain_integrity.py",
                "--ledger",
                str(ledger),
                "--head",
                str(head),
                "--verify-payload-files",
                "--base-dir",
                str(work),
            ],
            cwd=work,
        )

        run(
            [
                sys.executable,
                "scripts/build_record_chain_indexes.py",
                "--ledger",
                str(ledger),
                "--out-dir",
                str(work / "api"),
                "--verify-payload-files",
                "--base-dir",
                str(work),
            ],
            cwd=work,
        )

        entries = read_ledger(ledger)
        assert len(entries) == 6
        assert entries[0]["height"] == 0
        assert entries[0]["previous_entry_hash"] is None
        for i in range(1, len(entries)):
            assert entries[i]["previous_entry_hash"] == entries[i - 1]["entry_hash"]

        head_json = read_json(head)
        assert head_json["entry_count"] == 6
        assert head_json["height"] == 5
        assert head_json["head_entry_hash"] == entries[-1]["entry_hash"]

        echo_index = read_json(work / "api/record-chain-index.echo.json")
        verification_index = read_json(work / "api/record-chain-index.verification.json")
        guardian_index = read_json(work / "api/record-chain-index.guardian_application.json")
        guardian_exit_index = read_json(work / "api/record-chain-index.guardian_exit_application.json")
        exit_index = read_json(work / "api/record-chain-index.exit_application.json")
        custom_index = read_json(work / "api/record-chain-index.custom_future_type_v1.json")
        all_index = read_json(work / "api/record-chain-index.all.json")
        manifest = read_json(work / "api/record-chain-index.manifest.json")

        assert echo_index["entry_count"] == 1
        assert verification_index["entry_count"] == 1
        assert guardian_index["entry_count"] == 1
        assert guardian_exit_index["entry_count"] == 1
        assert exit_index["entry_count"] == 1
        assert custom_index["entry_count"] == 1
        assert all_index["entry_count"] == 6
        assert echo_index["entries"][0]["global_height"] == 0
        assert verification_index["entries"][0]["global_height"] == 1
        assert guardian_index["entries"][0]["global_height"] == 2
        assert guardian_exit_index["entries"][0]["global_height"] == 3
        assert exit_index["entries"][0]["global_height"] == 4
        assert custom_index["entries"][0]["global_height"] == 5
        assert any(x["record_type"] == "custom_future/type:v1" for x in manifest["record_types"])

        # OTS dry-run anchor of the stable head commitment snapshot.
        run(
            [
                sys.executable,
                "scripts/ots_anchor_record_chain_head.py",
                "--ledger",
                str(ledger),
                "--head",
                str(head),
                "--out-dir",
                str(work / "record-chain/ots/anchors"),
                "--api-out",
                str(work / "api/record-chain-ots-latest.json"),
                "--mode",
                "dry-run",
                "--verify-ledger",
                "--verify-payload-files",
                "--base-dir",
                str(work),
            ],
            cwd=work,
        )

        latest_ots = read_json(work / "api/record-chain-ots-latest.json")
        assert latest_ots["ots_status"] == "dry_run"
        assert latest_ots["head_entry_hash"] == head_json["head_entry_hash"]
        assert latest_ots["height"] == 5
        first_anchor_sha = latest_ots["anchored_file_sha256"]
        anchor_file = work / latest_ots["latest_anchor_file"]
        assert anchor_file.exists()

        run(
            [
                sys.executable,
                "scripts/ots_verify_record_chain_anchor.py",
                "--anchor-file",
                str(anchor_file),
                "--allow-dry-run",
            ],
            cwd=work,
        )

        # Rebuild indexes one second later. Head generated_at changes, but stable OTS commitment must not.
        time.sleep(1)
        run(
            [
                sys.executable,
                "scripts/build_record_chain_indexes.py",
                "--ledger",
                str(ledger),
                "--out-dir",
                str(work / "api"),
                "--verify-payload-files",
                "--base-dir",
                str(work),
            ],
            cwd=work,
        )
        run(
            [
                sys.executable,
                "scripts/ots_anchor_record_chain_head.py",
                "--ledger",
                str(ledger),
                "--head",
                str(head),
                "--out-dir",
                str(work / "record-chain/ots/anchors"),
                "--api-out",
                str(work / "api/record-chain-ots-latest.json"),
                "--mode",
                "dry-run",
                "--verify-ledger",
                "--verify-payload-files",
                "--base-dir",
                str(work),
                "--overwrite",
            ],
            cwd=work,
        )
        latest_ots_second = read_json(work / "api/record-chain-ots-latest.json")
        assert latest_ots_second["anchored_file_sha256"] == first_anchor_sha

        # Tamper anchored commitment snapshot: OTS dry-run verification must fail on sha mismatch.
        anchor_file = work / latest_ots_second["latest_anchor_file"]
        anchor = read_json(anchor_file)
        anchored_file = work / anchor["anchored_file"]
        original_snapshot_bytes = anchored_file.read_bytes()
        snapshot = read_json(anchored_file)
        snapshot["height"] = 999
        write_json(anchored_file, snapshot)

        run(
            [
                sys.executable,
                "scripts/ots_verify_record_chain_anchor.py",
                "--anchor-file",
                str(anchor_file),
                "--allow-dry-run",
            ],
            cwd=work,
            expect_ok=False,
        )

        anchored_file.write_bytes(original_snapshot_bytes)

        # Tampering with payload must fail when payload verification is enabled.
        tampered_payload = payloads / "record-2.json"
        data = json.loads(tampered_payload.read_text(encoding="utf-8"))
        data["body"] = "tampered"
        write_json(tampered_payload, data)

        run(
            [
                sys.executable,
                "scripts/verify_record_chain_integrity.py",
                "--ledger",
                str(ledger),
                "--head",
                str(head),
                "--verify-payload-files",
                "--base-dir",
                str(work),
            ],
            cwd=work,
            expect_ok=False,
        )

        # Restore payload.
        data["body"] = "test payload 2"
        write_json(tampered_payload, data)

        run(
            [
                sys.executable,
                "scripts/verify_record_chain_integrity.py",
                "--ledger",
                str(ledger),
                "--head",
                str(head),
                "--verify-payload-files",
                "--base-dir",
                str(work),
            ],
            cwd=work,
        )

        original_entries = read_ledger(ledger)

        # Tampering with previous hash must fail.
        tampered_entries = json.loads(json.dumps(original_entries))
        tampered_entries[2]["previous_entry_hash"] = "0" * 64
        write_ledger(ledger, tampered_entries)

        run(
            [
                sys.executable,
                "scripts/verify_record_chain_integrity.py",
                "--ledger",
                str(ledger),
                "--head",
                str(head),
            ],
            cwd=work,
            expect_ok=False,
        )

        write_ledger(ledger, original_entries)

        # Deleting a middle entry must fail because height / previous hash / head break.
        deleted_middle = [original_entries[0], original_entries[2]]
        write_ledger(ledger, deleted_middle)

        run(
            [
                sys.executable,
                "scripts/verify_record_chain_integrity.py",
                "--ledger",
                str(ledger),
                "--head",
                str(head),
            ],
            cwd=work,
            expect_ok=False,
        )

        write_ledger(ledger, original_entries)

        # Reordering entries must fail.
        reordered = [original_entries[1], original_entries[0], original_entries[2]]
        write_ledger(ledger, reordered)

        run(
            [
                sys.executable,
                "scripts/verify_record_chain_integrity.py",
                "--ledger",
                str(ledger),
                "--head",
                str(head),
            ],
            cwd=work,
            expect_ok=False,
        )

    print("PASS: record-chain global hash linking and OTS dry-run anchoring")


if __name__ == "__main__":
    main()
