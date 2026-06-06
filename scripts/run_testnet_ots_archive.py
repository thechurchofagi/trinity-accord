#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TESTNET_CHAIN_ID = "trinity-record-chain-testnet"

TESTNET_LEDGER = ROOT / "record-chain/testnet/hash-chain/testnet.chain.jsonl"
TESTNET_API_DIR = ROOT / "api/record-chain-testnet"
TESTNET_HEAD = TESTNET_API_DIR / "record-chain-head.json"
TESTNET_OTS_DIR = ROOT / "record-chain/testnet/ots"
TESTNET_ANCHORS = TESTNET_OTS_DIR / "anchors"
TESTNET_BUNDLES = TESTNET_OTS_DIR / "arweave-bundles"
TESTNET_REGISTRY = TESTNET_OTS_DIR / "arweave-registry.json"
TESTNET_OTS_LATEST = TESTNET_API_DIR / "ots-latest.json"
TESTNET_REGISTRY_API = TESTNET_API_DIR / "ots-arweave-registry.json"

MAINNET_FILES = [
    ROOT / "record-chain/hash-chain/main.chain.jsonl",
    ROOT / "api/record-chain-head.json",
    ROOT / "api/record-chain-ots-latest.json",
    ROOT / "api/record-chain-ots-arweave-registry.json",
    ROOT / "record-chain/ots/arweave-registry.json",
]

EXPECTED_OWNER = "r1EdzCQ9E7CaAOEywI5netR6EcSopNOa08oi2Coz68s"
CONFIRM_STAMP = "I_UNDERSTAND_THIS_STAMPS_TESTNET_OTS_NOT_MAINNET"
CONFIRM_ARWEAVE = "I_UNDERSTAND_THIS_UPLOADS_TESTNET_OTS_TO_ARWEAVE"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_mainnet() -> dict[str, str | None]:
    return {str(path.relative_to(ROOT)): sha256_file(path) for path in MAINNET_FILES}


def assert_mainnet_unchanged(before: dict[str, str | None]) -> None:
    after = snapshot_mainnet()
    changed = [path for path, old in before.items() if after.get(path) != old]
    if changed:
        raise SystemExit("STOP: mainnet files changed during testnet OTS/Arweave: " + ", ".join(changed))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def run(cmd: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    clean_cmd = [x for x in cmd if x != ""]
    print("[RUN]", " ".join(clean_cmd))
    result = subprocess.run(
        clean_cmd,
        cwd=str(ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(clean_cmd)}")
    return result


def verify_testnet() -> None:
    run([
        sys.executable,
        "scripts/verify_record_chain_integrity.py",
        "--ledger", rel(TESTNET_LEDGER),
        "--head", rel(TESTNET_HEAD),
        "--chain-id", TESTNET_CHAIN_ID,
        "--verify-payload-files",
        "--base-dir", ".",
    ])


def build_bundle(anchor_file: str) -> Path:
    anchor_path = ROOT / anchor_file
    if not anchor_path.exists():
        raise SystemExit(f"anchor file missing: {anchor_path}")

    out = TESTNET_BUNDLES / (Path(anchor_file).stem + ".testnet.arweave-bundle.json")

    run([
        sys.executable,
        "scripts/build_ots_arweave_bundle.py",
        "--anchor-file", anchor_file,
        "--out", rel(out),
    ])

    bundle = read_json(out)
    if bundle.get("chain_id") != TESTNET_CHAIN_ID:
        raise SystemExit("testnet bundle chain_id mismatch")

    bundle["environment"] = "testnet"
    bundle["test_only"] = True
    bundle["not_mainnet"] = True
    bundle["mainnet_chain_not_modified"] = True
    bundle["semantics"] = (
        "Real paid Arweave bundle for a TESTNET OTS proof of a stable testnet Record-Chain head commitment. "
        "This archive is not a mainnet archive and does not modify mainnet chain entries."
    )
    write_json(out, bundle)
    return out


def latest_anchor_for_current_head() -> str | None:
    if not TESTNET_OTS_LATEST.exists():
        return None
    latest = read_json(TESTNET_OTS_LATEST)
    if latest.get("chain_id") != TESTNET_CHAIN_ID:
        return None
    head = read_json(TESTNET_HEAD)
    if latest.get("head_entry_hash") != head.get("head_entry_hash"):
        return None
    anchor = latest.get("latest_anchor_file")
    return anchor if isinstance(anchor, str) else None


def extra_arweave_tags_json() -> str:
    return json.dumps([
        {"name": "Chain-Id", "value": TESTNET_CHAIN_ID},
        {"name": "Environment", "value": "testnet"},
        {"name": "Test-Only", "value": "true"},
        {"name": "Not-Mainnet", "value": "true"},
        {"name": "Archive-Scope", "value": "record-chain-testnet"},
    ], separators=(",", ":"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run REAL testnet OTS stamp and REAL testnet Arweave paid archive.")
    parser.add_argument("--run-id", default=time.strftime("phase7b-real-testnet-ots-%Y%m%dT%H%M%SZ", time.gmtime()))
    parser.add_argument("--mode", choices=["stamp"], default="stamp")
    parser.add_argument("--confirm-stamp", required=True)
    parser.add_argument("--arweave-mode", choices=["production"], default="production")
    parser.add_argument("--confirm-arweave-upload", required=True)
    parser.add_argument("--jwk-path", default=os.environ.get("ARWEAVE_JWK_PATH"))
    parser.add_argument("--gateway-url", default=os.environ.get("ARWEAVE_GATEWAY_URL", "https://arweave.net"))
    parser.add_argument("--max-upload-usd", default=os.environ.get("ARWEAVE_MAX_UPLOAD_USD", "0.10"))
    parser.add_argument("--safety-multiplier", default=os.environ.get("ARWEAVE_SAFETY_MULTIPLIER", "1.20"))
    parser.add_argument(
        "--reuse-existing-anchor-for-current-head",
        action="store_true",
        help="Use only if the current testnet head already has a stamped anchor. Never overwrites anchors.",
    )
    args = parser.parse_args()

    if args.confirm_stamp != CONFIRM_STAMP:
        raise SystemExit(f"--confirm-stamp must be exactly {CONFIRM_STAMP!r}")
    if args.confirm_arweave_upload != CONFIRM_ARWEAVE:
        raise SystemExit(f"--confirm-arweave-upload must be exactly {CONFIRM_ARWEAVE!r}")
    if not args.jwk_path:
        raise SystemExit("production testnet Arweave upload requires --jwk-path or ARWEAVE_JWK_PATH")

    before_mainnet = snapshot_mainnet()

    if not TESTNET_LEDGER.exists():
        raise SystemExit("testnet ledger missing; run scripts/init_record_chain_testnet.py first")
    if not TESTNET_HEAD.exists():
        raise SystemExit("testnet head missing; run scripts/init_record_chain_testnet.py first")

    verify_testnet()

    anchor_file = None
    if args.reuse_existing_anchor_for_current_head:
        anchor_file = latest_anchor_for_current_head()
        if anchor_file:
            print(f"[INFO] Reusing existing testnet anchor for current head: {anchor_file}")

    if not anchor_file:
        run([
            sys.executable,
            "scripts/ots_anchor_record_chain_head.py",
            "--ledger", rel(TESTNET_LEDGER),
            "--head", rel(TESTNET_HEAD),
            "--chain-id", TESTNET_CHAIN_ID,
            "--out-dir", rel(TESTNET_ANCHORS),
            "--api-out", rel(TESTNET_OTS_LATEST),
            "--mode", "stamp",
            "--verify-ledger",
            "--verify-payload-files",
            "--base-dir", ".",
        ])
        latest = read_json(TESTNET_OTS_LATEST)
        if latest.get("chain_id") != TESTNET_CHAIN_ID:
            raise SystemExit("testnet ots latest chain_id mismatch")
        anchor_file = latest.get("latest_anchor_file")
        if not isinstance(anchor_file, str):
            raise SystemExit("testnet ots latest missing latest_anchor_file")

    bundle_file = build_bundle(anchor_file)

    log_dir = ROOT / "record-chain/testnet/audit" / args.run_id
    log_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["E2E_RUN_ID"] = args.run_id
    env["E2E_LOG_DIR"] = str(log_dir)
    env["ARWEAVE_UPLOAD_MODE"] = "production"
    env["ALLOW_PAID_ARWEAVE_CANARY"] = "true"
    env["EXPECTED_ARWEAVE_OWNER"] = EXPECTED_OWNER
    env["ARWEAVE_MAX_UPLOAD_USD"] = args.max_upload_usd
    env["ARWEAVE_SAFETY_MULTIPLIER"] = args.safety_multiplier
    env["ARWEAVE_GATEWAY_URL"] = args.gateway_url
    env["ARWEAVE_JWK_PATH"] = args.jwk_path
    env["ARWEAVE_APP_NAME"] = "Trinity-Accord-Record-Chain-Testnet"
    env["ARWEAVE_EXTRA_TAGS_JSON"] = extra_arweave_tags_json()

    record_type = "ots_anchor_archive_testnet"
    run([
        "node",
        "scripts/arweave_cost_gate.mjs",
        "--payload-file", rel(bundle_file),
        "--record-type", record_type,
        "--run-id", args.run_id,
        "--log-dir", str(log_dir),
        "--mode", "production",
        "--expected-owner", EXPECTED_OWNER,
        "--gateway-url", args.gateway_url,
        "--max-upload-usd", args.max_upload_usd,
        "--safety-multiplier", args.safety_multiplier,
        "--app-name", "Trinity-Accord-Record-Chain-Testnet",
        "--extra-tags-json", extra_arweave_tags_json(),
    ], env=env)

    upload_result = log_dir / f"11-arweave-upload-result.{record_type}.json"
    readback_result = log_dir / f"11b-arweave-readback-verify.{record_type}.json"

    upload = read_json(upload_result)
    if upload.get("result") != "uploaded":
        raise SystemExit("production upload did not produce uploaded result")

    if upload.get("extra_tags") is None:
        raise SystemExit("upload result missing extra_tags")
    expected_tags = {tag["name"]: tag["value"] for tag in json.loads(extra_arweave_tags_json())}
    got_tags = {tag["name"]: tag["value"] for tag in upload.get("extra_tags", [])}
    for key, expected in expected_tags.items():
        if got_tags.get(key) != expected:
            raise SystemExit(f"upload result missing expected Arweave tag {key}={expected}")

    if not readback_result.exists():
        raise SystemExit("readback result missing after production upload")

    readback = read_json(readback_result)
    if readback.get("result") != "pass" or readback.get("hash_match") is not True:
        raise SystemExit("Arweave readback did not pass")

    run([
        sys.executable,
        "scripts/update_ots_arweave_registry.py",
        "--registry", rel(TESTNET_REGISTRY),
        "--api-out", rel(TESTNET_REGISTRY_API),
        "--anchor-file", anchor_file,
        "--bundle-file", rel(bundle_file),
        "--upload-result", rel(upload_result),
        "--readback-result", rel(readback_result),
    ])

    registry = read_json(TESTNET_REGISTRY)
    if registry.get("chain_id") != TESTNET_CHAIN_ID:
        raise SystemExit("testnet Arweave registry chain_id mismatch")

    assert_mainnet_unchanged(before_mainnet)

    summary = {
        "result": "pass",
        "chain_id": TESTNET_CHAIN_ID,
        "environment": "testnet",
        "mode": "stamp",
        "arweave_mode": "production",
        "latest_anchor_file": anchor_file,
        "bundle_file": rel(bundle_file),
        "arweave_tx_id": upload.get("tx_id"),
        "arweave_gateway_url": upload.get("gateway_url"),
        "arweave_extra_tags": upload.get("extra_tags"),
        "readback_hash_match": readback.get("hash_match"),
        "mainnet_unchanged": True,
        "generated_at": utc_now(),
    }
    write_json(log_dir / "99-real-testnet-ots-arweave-summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
