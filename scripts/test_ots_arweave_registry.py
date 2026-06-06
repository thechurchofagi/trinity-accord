#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_scripts(work: Path) -> None:
    scripts = work / "scripts"
    scripts.mkdir()
    for name in [
        "record_chain_hashing.py",
        "append_record_chain_link.py",
        "verify_record_chain_integrity.py",
        "build_record_chain_indexes.py",
        "ots_anchor_record_chain_head.py",
        "build_ots_arweave_bundle.py",
        "update_ots_arweave_registry.py",
        "verify_ots_arweave_registry.py",
    ]:
        shutil.copy(REPO_ROOT / "scripts" / name, scripts / name)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="trinity-ots-arweave-registry-test-") as tmp:
        work = Path(tmp)
        copy_scripts(work)

        payload = work / "payloads/record.json"
        write_json(payload, {"record_type": "echo", "record_id": "r1", "body": "hello"})

        ledger = work / "record-chain/hash-chain/main.chain.jsonl"
        head = work / "api/record-chain-head.json"

        run([
            sys.executable,
            "scripts/append_record_chain_link.py",
            "--ledger", str(ledger),
            "--head-out", str(head),
            "--record-file", str(payload),
            "--record-type", "echo",
            "--record-id", "r1",
            "--allow-genesis",
            "--verify-payload-files",
        ], cwd=work)

        run([
            sys.executable,
            "scripts/ots_anchor_record_chain_head.py",
            "--ledger", str(ledger),
            "--head", str(head),
            "--out-dir", str(work / "record-chain/ots/anchors"),
            "--api-out", str(work / "api/record-chain-ots-latest.json"),
            "--mode", "dry-run",
            "--verify-ledger",
            "--verify-payload-files",
            "--base-dir", str(work),
        ], cwd=work)

        latest = read_json(work / "api/record-chain-ots-latest.json")
        anchor_file = work / latest["latest_anchor_file"]
        bundle_file = work / "record-chain/ots/arweave-bundles/test.arweave-bundle.json"

        run([
            sys.executable,
            "scripts/build_ots_arweave_bundle.py",
            "--anchor-file", str(anchor_file),
            "--out", str(bundle_file),
        ], cwd=work)

        bundle_sha = sha256_file(bundle_file)
        upload = work / "audit/upload.json"
        readback = work / "audit/readback.json"
        write_json(upload, {
            "result": "uploaded",
            "tx_id": "abcDEFG1234567890_abcdefghijklmnop",
            "gateway_url": "https://arweave.net/abcDEFG1234567890_abcdefghijklmnop",
            "payload_sha256": bundle_sha,
        })
        write_json(readback, {
            "result": "pass",
            "hash_match": True,
            "downloaded_sha256": bundle_sha,
        })

        # Production/default behavior must reject dry_run OTS anchors.
        run([
            sys.executable,
            "scripts/update_ots_arweave_registry.py",
            "--anchor-file", str(anchor_file),
            "--bundle-file", str(bundle_file),
            "--upload-result", str(upload),
            "--readback-result", str(readback),
            "--registry", str(work / "record-chain/ots/arweave-registry.json"),
            "--api-out", str(work / "api/record-chain-ots-arweave-registry.json"),
        ], cwd=work, expect_ok=False)

        # Test-only override should allow exercising the registry code path.
        run([
            sys.executable,
            "scripts/update_ots_arweave_registry.py",
            "--anchor-file", str(anchor_file),
            "--bundle-file", str(bundle_file),
            "--upload-result", str(upload),
            "--readback-result", str(readback),
            "--registry", str(work / "record-chain/ots/arweave-registry.json"),
            "--api-out", str(work / "api/record-chain-ots-arweave-registry.json"),
            "--allow-dry-run-anchor",
        ], cwd=work)

        run([
            sys.executable,
            "scripts/verify_ots_arweave_registry.py",
            "--registry", str(work / "record-chain/ots/arweave-registry.json"),
            "--verify-local-bundles",
        ], cwd=work)

        registry = read_json(work / "record-chain/ots/arweave-registry.json")
        assert registry["entry_count"] == 1
        assert registry["entries"][0]["bundle_sha256"] == bundle_sha
        assert registry["entries"][0]["arweave_hash_match"] is True

        # Mismatched readback must fail.
        bad_readback = work / "audit/bad-readback.json"
        write_json(bad_readback, {
            "result": "pass",
            "hash_match": True,
            "downloaded_sha256": "0" * 64,
        })
        run([
            sys.executable,
            "scripts/update_ots_arweave_registry.py",
            "--anchor-file", str(anchor_file),
            "--bundle-file", str(bundle_file),
            "--upload-result", str(upload),
            "--readback-result", str(bad_readback),
            "--registry", str(work / "record-chain/ots/bad-registry.json"),
            "--api-out", str(work / "api/bad-registry.json"),
            "--allow-dry-run-anchor",
        ], cwd=work, expect_ok=False)

    print("PASS: OTS-Arweave bundle and registry safety")

    # --- Backward compatibility: registry without latest_upgraded_tx_id ---
    _test_registry_backward_compat()

    # --- Upgraded entry: latest_upgraded_tx_id set, latest_verified_tx_id null ---
    _test_upgraded_entry()


def _test_registry_backward_compat() -> None:
    """Old registry without latest_upgraded_tx_id should not fail verification."""
    import tempfile
    with tempfile.TemporaryDirectory(prefix="trinity-bc-test-") as tmp:
        work = Path(tmp)
        old_registry = {
            "schema": "trinity_record_chain_ots_arweave_registry.v1",
            "chain_id": "trinity-record-chain-main",
            "entries": [],
            "latest_by_head": {
                "abc123": {
                    "height": 0,
                    "latest_pending_tx_id": "tx_pending_123",
                    "latest_verified_tx_id": None,
                    "latest_any_tx_id": "tx_pending_123",
                    # Note: no latest_upgraded_tx_id — old format
                }
            },
            "generated_at": "2026-01-01T00:00:00Z",
        }
        reg_path = work / "registry.json"
        write_json(reg_path, old_registry)

        # Verify should pass (no latest_upgraded_tx_id required)
        run([
            sys.executable,
            "scripts/verify_ots_arweave_registry.py",
            "--registry", str(reg_path),
        ], cwd=REPO_ROOT)

    print("PASS: registry backward compatibility (no latest_upgraded_tx_id)")


def _test_upgraded_entry() -> None:
    """Upgraded entry must set latest_upgraded_tx_id, not latest_verified_tx_id."""
    import tempfile
    with tempfile.TemporaryDirectory(prefix="trinity-upgraded-test-") as tmp:
        work = Path(tmp)
        copy_scripts(work)

        payload = work / "payloads/record.json"
        write_json(payload, {"record_type": "echo", "record_id": "r1", "body": "hello"})

        ledger = work / "record-chain/hash-chain/main.chain.jsonl"
        head = work / "api/record-chain-head.json"

        run([
            sys.executable,
            "scripts/append_record_chain_link.py",
            "--ledger", str(ledger),
            "--head-out", str(head),
            "--record-file", str(payload),
            "--record-type", "echo",
            "--record-id", "r1",
            "--allow-genesis",
            "--verify-payload-files",
        ], cwd=work)

        run([
            sys.executable,
            "scripts/ots_anchor_record_chain_head.py",
            "--ledger", str(ledger),
            "--head", str(head),
            "--out-dir", str(work / "record-chain/ots/anchors"),
            "--api-out", str(work / "api/record-chain-ots-latest.json"),
            "--mode", "dry-run",
            "--verify-ledger",
            "--verify-payload-files",
            "--base-dir", str(work),
        ], cwd=work)

        latest = read_json(work / "api/record-chain-ots-latest.json")
        anchor_file = work / latest["latest_anchor_file"]

        # Patch anchor to look like an upgraded anchor
        anchor = read_json(anchor_file)
        anchor["ots_status"] = "upgraded"
        anchor["bitcoin_attestation_embedded"] = True
        anchor["bitcoin_verified"] = False
        anchor["bitcoin_pending"] = False
        write_json(anchor_file, anchor)

        bundle_file = work / "record-chain/ots/arweave-bundles/test.upgraded.arweave-bundle.json"
        run([
            sys.executable,
            "scripts/build_ots_arweave_bundle.py",
            "--anchor-file", str(anchor_file),
            "--out", str(bundle_file),
        ], cwd=work)

        # Verify bundle has upgraded status
        bundle = read_json(bundle_file)
        assert bundle["ots_status"] == "upgraded", f"expected upgraded, got {bundle['ots_status']}"
        assert bundle["bitcoin_attestation_embedded"] is True
        assert bundle["bitcoin_verified"] is False

        bundle_sha = sha256_file(bundle_file)
        upload = work / "audit/upload.json"
        readback = work / "audit/readback.json"
        write_json(upload, {
            "result": "uploaded",
            "tx_id": "upgraded_tx_id_1234567890_abc",
            "gateway_url": "https://arweave.net/upgraded_tx_id_1234567890_abc",
            "payload_sha256": bundle_sha,
        })
        write_json(readback, {
            "result": "pass",
            "hash_match": True,
            "downloaded_sha256": bundle_sha,
        })

        run([
            sys.executable,
            "scripts/update_ots_arweave_registry.py",
            "--anchor-file", str(anchor_file),
            "--bundle-file", str(bundle_file),
            "--upload-result", str(upload),
            "--readback-result", str(readback),
            "--registry", str(work / "record-chain/ots/arweave-registry.json"),
            "--api-out", str(work / "api/record-chain-ots-arweave-registry.json"),
            "--allow-dry-run-anchor",
        ], cwd=work)

        registry = read_json(work / "record-chain/ots/arweave-registry.json")
        head_hash = anchor.get("head_entry_hash")
        item = registry["latest_by_head"][head_hash]

        # Upgraded entry: latest_upgraded_tx_id set, latest_verified_tx_id null
        assert item["latest_upgraded_tx_id"] == "upgraded_tx_id_1234567890_abc", \
            f"latest_upgraded_tx_id wrong: {item.get('latest_upgraded_tx_id')}"
        assert item["latest_verified_tx_id"] is None, \
            f"latest_verified_tx_id must be null, got: {item.get('latest_verified_tx_id')}"
        assert item["latest_any_tx_id"] == "upgraded_tx_id_1234567890_abc", \
            f"latest_any_tx_id wrong: {item.get('latest_any_tx_id')}"

        # Verify passes
        run([
            sys.executable,
            "scripts/verify_ots_arweave_registry.py",
            "--registry", str(work / "record-chain/ots/arweave-registry.json"),
            "--verify-local-bundles",
        ], cwd=work)

    print("PASS: upgraded entry: latest_upgraded_tx_id set, latest_verified_tx_id null")


if __name__ == "__main__":
    main()
