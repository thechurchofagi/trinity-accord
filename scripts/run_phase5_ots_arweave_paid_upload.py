#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ID = time.strftime("phase5-ots-arweave-%Y%m%dT%H%M%SZ", time.gmtime())

CONFIRM_PAID_UPLOAD = "I_UNDERSTAND_THIS_UPLOADS_THE_OTS_PROOF_BUNDLE_TO_ARWEAVE"
EXPECTED_OWNER = "r1EdzCQ9E7CaAOEywI5netR6EcSopNOa08oi2Coz68s"
RECORD_TYPE = "ots_anchor_archive"
MAX_UPLOAD_USD = "0.10"
SAFETY_MULTIPLIER = "1.20"

PRODUCTION_MAIN_CHAIN = ROOT / "record-chain/hash-chain/main.chain.jsonl"
PRODUCTION_HEAD = ROOT / "api/record-chain-head.json"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def is_repo_relative_path(value: str) -> bool:
    p = Path(value)
    return bool(value) and not p.is_absolute() and ".." not in p.parts


def resolve_repo_path(value: str) -> Path:
    if not is_repo_relative_path(value):
        raise SystemExit(f"expected repo-relative path, got: {value}")
    return ROOT / value


def require_under_repo(path: Path, label: str) -> Path:
    resolved = path.resolve()
    root = ROOT.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        raise SystemExit(f"{label} must be under repository root: {path}")
    return resolved


def rel_to_root(path: Path) -> str:
    return str(require_under_repo(path, "path").relative_to(ROOT.resolve()))


def run_cmd(
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    expect_ok: bool = True,
    stdout_file: Path | None = None,
    stderr_file: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    print("[RUN]", " ".join(cmd))
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if stdout_file:
        stdout_file.parent.mkdir(parents=True, exist_ok=True)
        stdout_file.write_text(result.stdout, encoding="utf-8")
    if stderr_file:
        stderr_file.parent.mkdir(parents=True, exist_ok=True)
        stderr_file.write_text(result.stderr, encoding="utf-8")

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if expect_ok and result.returncode != 0:
        raise SystemExit(f"command failed with exit={result.returncode}: {' '.join(cmd)}")
    if not expect_ok and result.returncode == 0:
        raise SystemExit(f"command unexpectedly passed: {' '.join(cmd)}")
    return result


def precheck_required_files() -> None:
    required = [
        "api/record-chain-head.json",
        "api/record-chain-ots-latest.json",
        "record-chain/hash-chain/main.chain.jsonl",
        "scripts/build_ots_arweave_bundle.py",
        "scripts/arweave_cost_gate.mjs",
        "scripts/verify_arweave_upload_readback.mjs",
        "scripts/update_ots_arweave_registry.py",
        "scripts/verify_ots_arweave_registry.py",
        "scripts/test_ots_arweave_registry.py",
        "scripts/test_arweave_cost_gate_safety.mjs",
        "scripts/test_arweave_readback_hash_fixture.mjs",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    if missing:
        raise SystemExit("missing required files:\n" + "\n".join(missing))


def assert_no_price_override_in_production_env(env: dict[str, str]) -> None:
    forbidden = [
        "ARWEAVE_UPLOAD_PRICE_WINSTON_OVERRIDE",
        "AR_USD_PRICE_OVERRIDE",
        "ALLOW_ARWEAVE_PRICE_OVERRIDE_IN_PRODUCTION",
    ]
    present = [k for k in forbidden if env.get(k)]
    if present:
        raise SystemExit(
            "Price override variables are forbidden for Phase 5 production upload: "
            + ", ".join(present)
        )


def validate_latest_ots(latest_path: Path) -> dict[str, Any]:
    latest = read_json(latest_path)

    if latest.get("schema") != "trinity_record_chain_ots_latest.v1":
        raise SystemExit(f"unexpected latest schema: {latest.get('schema')}")

    ots_status = latest.get("ots_status")
    if ots_status == "dry_run":
        raise SystemExit("Refusing Phase 5: latest OTS anchor is dry_run")
    if ots_status not in {"pending", "verified"}:
        raise SystemExit(f"Refusing Phase 5: unexpected ots_status={ots_status!r}")

    if latest.get("chain_id") != "trinity-record-chain-main":
        raise SystemExit(f"unexpected chain_id: {latest.get('chain_id')}")

    for key in ["latest_anchor_file", "latest_anchored_file", "latest_ots_file"]:
        value = latest.get(key)
        if not isinstance(value, str) or not value:
            raise SystemExit(f"{key} missing")
        if not is_repo_relative_path(value):
            raise SystemExit(f"{key} must be repo-relative, got {value}")
        if not resolve_repo_path(value).exists():
            raise SystemExit(f"{key} path does not exist: {value}")

    if latest.get("height") is None or latest.get("entry_count") is None:
        raise SystemExit("latest height/entry_count missing")

    if not re.fullmatch(r"[a-f0-9]{64}", str(latest.get("head_entry_hash") or "")):
        raise SystemExit("latest head_entry_hash missing/invalid")

    return latest


def validate_anchor(anchor_path_rel: str) -> dict[str, Any]:
    anchor_path = resolve_repo_path(anchor_path_rel)
    anchor = read_json(anchor_path)

    if anchor.get("schema") != "trinity_record_chain_ots_anchor.v1":
        raise SystemExit(f"anchor schema mismatch: {anchor.get('schema')}")

    if anchor.get("ots_status") == "dry_run":
        raise SystemExit("Refusing Phase 5: anchor ots_status is dry_run")

    if anchor.get("ots_status") not in {"pending", "verified"}:
        raise SystemExit(f"unexpected anchor ots_status: {anchor.get('ots_status')}")

    if anchor.get("chain_id") != "trinity-record-chain-main":
        raise SystemExit("anchor chain_id mismatch")

    for key in ["anchored_file", "ots_file"]:
        value = anchor.get(key)
        if not isinstance(value, str) or not value:
            raise SystemExit(f"anchor {key} missing")
        if not is_repo_relative_path(value):
            raise SystemExit(f"anchor {key} must be repo-relative, got {value}")
        if not resolve_repo_path(value).exists():
            raise SystemExit(f"anchor {key} does not exist: {value}")

    anchored_sha = sha256_file(resolve_repo_path(anchor["anchored_file"]))
    if anchored_sha != anchor.get("anchored_file_sha256"):
        raise SystemExit(
            f"anchored_file_sha256 mismatch: expected {anchor.get('anchored_file_sha256')}, got {anchored_sha}"
        )

    ots_sha = sha256_file(resolve_repo_path(anchor["ots_file"]))
    if anchor.get("ots_file_sha256") and anchor.get("ots_file_sha256") != ots_sha:
        raise SystemExit(
            f"ots_file_sha256 mismatch: expected {anchor.get('ots_file_sha256')}, got {ots_sha}"
        )

    return anchor


def build_bundle(anchor_file_rel: str, out_file: Path) -> dict[str, Any]:
    out_file = require_under_repo(out_file, "--bundle-out")
    run_cmd(
        [
            sys.executable,
            "scripts/build_ots_arweave_bundle.py",
            "--anchor-file",
            anchor_file_rel,
            "--out",
            rel_to_root(out_file),
        ]
    )

    bundle = read_json(out_file)
    if bundle.get("schema") != "trinity_record_chain_ots_arweave_bundle.v1":
        raise SystemExit(f"bundle schema mismatch: {bundle.get('schema')}")
    if bundle.get("ots_status") == "dry_run":
        raise SystemExit("bundle is dry_run; refusing Phase 5")
    if bundle.get("source_anchor_file") != anchor_file_rel:
        raise SystemExit(
            f"bundle.source_anchor_file mismatch: {bundle.get('source_anchor_file')} != {anchor_file_rel}"
        )

    roles = {f.get("role") for f in bundle.get("files", []) if isinstance(f, dict)}
    required_roles = {"head_commitment_snapshot", "ots_anchor_metadata", "ots_proof"}
    missing_roles = required_roles - roles
    if missing_roles:
        raise SystemExit(f"bundle missing roles: {sorted(missing_roles)}")

    return bundle


def make_arweave_env(
    *,
    mode: str,
    log_dir: Path,
    run_id: str,
    jwk_path: str | None,
    gateway_url: str,
    readback_gateways: str,
    readback_timeout: str,
    readback_retry: str,
) -> dict[str, str]:
    env = os.environ.copy()
    env["E2E_RUN_ID"] = run_id
    env["E2E_LOG_DIR"] = str(log_dir)
    env["ARWEAVE_UPLOAD_MODE"] = mode
    env["EXPECTED_ARWEAVE_OWNER"] = EXPECTED_OWNER
    env["ARWEAVE_MAX_UPLOAD_USD"] = MAX_UPLOAD_USD
    env["ARWEAVE_SAFETY_MULTIPLIER"] = SAFETY_MULTIPLIER
    env["ARWEAVE_GATEWAY_URL"] = gateway_url
    env["ARWEAVE_READBACK_GATEWAYS"] = readback_gateways
    env["ARWEAVE_READBACK_TIMEOUT_SECONDS"] = readback_timeout
    env["ARWEAVE_READBACK_RETRY_SECONDS"] = readback_retry

    if mode == "production":
        env["ALLOW_PAID_ARWEAVE_CANARY"] = "true"
        if not jwk_path:
            raise SystemExit("production mode requires --jwk-path or ARWEAVE_JWK_PATH")
        env["ARWEAVE_JWK_PATH"] = jwk_path
        assert_no_price_override_in_production_env(env)
    else:
        env["ALLOW_PAID_ARWEAVE_CANARY"] = "false"
        env.pop("ARWEAVE_JWK_PATH", None)

    return env


def run_arweave_cost_gate(
    *,
    payload_file: Path,
    run_id: str,
    log_dir: Path,
    mode: str,
    jwk_path: str | None,
    gateway_url: str,
    readback_gateways: str,
    readback_timeout: str,
    readback_retry: str,
) -> None:
    payload_file = require_under_repo(payload_file, "payload_file")
    log_dir.mkdir(parents=True, exist_ok=True)

    env = make_arweave_env(
        mode=mode,
        log_dir=log_dir,
        run_id=run_id,
        jwk_path=jwk_path,
        gateway_url=gateway_url,
        readback_gateways=readback_gateways,
        readback_timeout=readback_timeout,
        readback_retry=readback_retry,
    )

    cmd = [
        "node",
        "scripts/arweave_cost_gate.mjs",
        "--payload-file",
        rel_to_root(payload_file),
        "--record-type",
        RECORD_TYPE,
        "--run-id",
        run_id,
        "--log-dir",
        str(log_dir),
        "--mode",
        mode,
        "--expected-owner",
        EXPECTED_OWNER,
        "--gateway-url",
        gateway_url,
        "--max-upload-usd",
        MAX_UPLOAD_USD,
        "--safety-multiplier",
        SAFETY_MULTIPLIER,
    ]

    run_cmd(
        cmd,
        env=env,
        stdout_file=log_dir / f"arweave-cost-gate.{mode}.stdout.log",
        stderr_file=log_dir / f"arweave-cost-gate.{mode}.stderr.log",
    )


def validate_cost_dry_run(log_dir: Path, bundle_sha: str) -> dict[str, Any]:
    path = log_dir / f"10-arweave-cost-estimate.{RECORD_TYPE}.json"
    cost = read_json(path)

    if cost.get("record_type") != RECORD_TYPE:
        raise SystemExit("cost record_type mismatch")
    if cost.get("payload_sha256") != bundle_sha:
        raise SystemExit("dry-run cost payload sha != bundle sha")
    if cost.get("mode") != "dry_run":
        raise SystemExit("cost dry-run mode mismatch")
    if cost.get("decision") != "DRY_RUN":
        raise SystemExit(f"expected DRY_RUN, got {cost.get('decision')}")
    if float(cost.get("effective_max_upload_usd", 0)) > 0.10:
        raise SystemExit("effective max upload USD exceeds 0.10")
    return cost


def validate_paid_outputs(
    log_dir: Path,
    bundle_sha: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    cost = read_json(log_dir / f"10-arweave-cost-estimate.{RECORD_TYPE}.json")
    upload = read_json(log_dir / f"11-arweave-upload-result.{RECORD_TYPE}.json")
    readback = read_json(log_dir / f"11b-arweave-readback-verify.{RECORD_TYPE}.json")

    if cost.get("decision") != "ALLOW":
        raise SystemExit(f"paid cost gate was not ALLOW: {cost.get('decision')}")
    if float(cost.get("estimated_upload_cost_usd_with_buffer", 999)) > 0.10:
        raise SystemExit("paid cost estimate with buffer exceeds 0.10")

    if upload.get("result") != "uploaded":
        raise SystemExit(f"upload result not uploaded: {upload.get('result')}")
    if upload.get("record_type") != RECORD_TYPE:
        raise SystemExit("upload record_type mismatch")
    if upload.get("payload_sha256") != bundle_sha:
        raise SystemExit("upload payload_sha256 != bundle_sha")
    if upload.get("wallet_address") != EXPECTED_OWNER:
        raise SystemExit("upload wallet address != expected owner")

    if readback.get("result") != "pass":
        raise SystemExit("readback result != pass")
    if readback.get("hash_match") is not True:
        raise SystemExit("readback hash_match != true")
    if readback.get("byte_for_byte_match") is not True:
        raise SystemExit("readback byte_for_byte_match != true")
    if readback.get("downloaded_sha256") != bundle_sha:
        raise SystemExit("readback downloaded_sha256 != bundle_sha")

    return cost, upload, readback


def update_and_verify_registry(
    *,
    anchor_file_rel: str,
    bundle_file: Path,
    log_dir: Path,
) -> dict[str, Any]:
    bundle_file = require_under_repo(bundle_file, "bundle_file")
    run_cmd(
        [
            sys.executable,
            "scripts/update_ots_arweave_registry.py",
            "--anchor-file",
            anchor_file_rel,
            "--bundle-file",
            rel_to_root(bundle_file),
            "--upload-result",
            rel_to_root(log_dir / f"11-arweave-upload-result.{RECORD_TYPE}.json"),
            "--readback-result",
            rel_to_root(log_dir / f"11b-arweave-readback-verify.{RECORD_TYPE}.json"),
            "--registry",
            "record-chain/ots/arweave-registry.json",
            "--api-out",
            "api/record-chain-ots-arweave-registry.json",
        ]
    )

    run_cmd(
        [
            sys.executable,
            "scripts/verify_ots_arweave_registry.py",
            "--registry",
            "record-chain/ots/arweave-registry.json",
            "--verify-local-bundles",
        ]
    )

    registry = read_json(ROOT / "record-chain/ots/arweave-registry.json")
    api_registry = read_json(ROOT / "api/record-chain-ots-arweave-registry.json")
    if registry != api_registry:
        raise SystemExit("registry and api registry differ")
    return registry


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 5 OTS proof bundle Arweave paid upload + readback + registry update."
    )
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--log-dir", default=None)
    parser.add_argument("--latest-ots", default="api/record-chain-ots-latest.json")
    parser.add_argument("--bundle-out", default=None)
    parser.add_argument("--precheck-only", action="store_true")
    parser.add_argument("--dry-run-cost-only", action="store_true")
    parser.add_argument("--enable-paid-upload", action="store_true")
    parser.add_argument("--confirm-paid-upload", default="")
    parser.add_argument("--jwk-path", default=os.environ.get("ARWEAVE_JWK_PATH"))
    parser.add_argument("--gateway-url", default=os.environ.get("ARWEAVE_GATEWAY_URL", "https://arweave.net"))
    parser.add_argument(
        "--readback-gateways",
        default=os.environ.get("ARWEAVE_READBACK_GATEWAYS", "https://arweave.net"),
    )
    parser.add_argument(
        "--readback-timeout-seconds",
        default=os.environ.get("ARWEAVE_READBACK_TIMEOUT_SECONDS", "900"),
    )
    parser.add_argument(
        "--readback-retry-seconds",
        default=os.environ.get("ARWEAVE_READBACK_RETRY_SECONDS", "15"),
    )
    args = parser.parse_args()

    precheck_required_files()

    run_id = args.run_id
    log_dir = Path(args.log_dir) if args.log_dir else ROOT / "record-chain" / "audit" / "phase5" / run_id
    if not log_dir.is_absolute():
        log_dir = ROOT / log_dir
    log_dir = require_under_repo(log_dir, "--log-dir")
    log_dir.mkdir(parents=True, exist_ok=True)

    main_chain_before_sha = sha256_file(PRODUCTION_MAIN_CHAIN)
    head_before_sha = sha256_file(PRODUCTION_HEAD)

    run_config = {
        "schema": "trinity_phase5_ots_arweave_paid_upload_config.v1",
        "run_id": run_id,
        "log_dir": rel_to_root(log_dir),
        "latest_ots": args.latest_ots,
        "precheck_only": args.precheck_only,
        "dry_run_cost_only": args.dry_run_cost_only,
        "enable_paid_upload": args.enable_paid_upload,
        "expected_owner": EXPECTED_OWNER,
        "max_upload_usd": MAX_UPLOAD_USD,
        "safety_multiplier": SAFETY_MULTIPLIER,
        "gateway_url": args.gateway_url,
        "readback_gateways": args.readback_gateways,
        "main_chain_before_sha256": main_chain_before_sha,
        "head_before_sha256": head_before_sha,
        "created_at": utc_now(),
    }
    write_json(log_dir / "00-run-config.json", run_config)

    print("[PHASE5] run_id:", run_id)
    print("[PHASE5] log_dir:", rel_to_root(log_dir))

    # Baseline tests.
    run_cmd(["node", "scripts/test_arweave_cost_gate_safety.mjs"])
    run_cmd(["node", "scripts/test_arweave_readback_hash_fixture.mjs"])
    run_cmd([sys.executable, "scripts/test_ots_arweave_registry.py"])

    latest_path = resolve_repo_path(args.latest_ots)
    latest = validate_latest_ots(latest_path)
    anchor_file_rel = latest["latest_anchor_file"]
    anchor = validate_anchor(anchor_file_rel)

    # Build bundle.
    if args.bundle_out:
        bundle_out = Path(args.bundle_out)
        if not bundle_out.is_absolute():
            bundle_out = ROOT / bundle_out
        bundle_out = require_under_repo(bundle_out, "--bundle-out")
    else:
        safe_stem = Path(anchor_file_rel).stem.replace("/", "_")
        bundle_out = ROOT / "record-chain" / "ots" / "arweave-bundles" / f"{safe_stem}.arweave-bundle.json"

    bundle = build_bundle(anchor_file_rel, bundle_out)
    bundle_sha = sha256_file(bundle_out)
    if bundle_sha is None:
        raise SystemExit("bundle file missing after build")

    if bundle.get("ots_status") != anchor.get("ots_status"):
        raise SystemExit("bundle ots_status != anchor ots_status")
    if bundle.get("head_entry_hash") != anchor.get("head_entry_hash"):
        raise SystemExit("bundle head_entry_hash != anchor head_entry_hash")

    # Always run cost gate dry-run first.
    dry_run_log_dir = log_dir / "dry-run-cost"
    dry_run_log_dir.mkdir(parents=True, exist_ok=True)
    run_arweave_cost_gate(
        payload_file=bundle_out,
        run_id=f"{run_id}-dry-run",
        log_dir=dry_run_log_dir,
        mode="dry_run",
        jwk_path=None,
        gateway_url=args.gateway_url,
        readback_gateways=args.readback_gateways,
        readback_timeout=args.readback_timeout_seconds,
        readback_retry=args.readback_retry_seconds,
    )
    dry_cost = validate_cost_dry_run(dry_run_log_dir, bundle_sha)

    if args.precheck_only or args.dry_run_cost_only:
        summary = {
            "schema": "trinity_phase5_ots_arweave_paid_upload_summary.v1",
            "run_id": run_id,
            "result": "pass",
            "mode": "precheck_only" if args.precheck_only else "dry_run_cost_only",
            "anchor_file": anchor_file_rel,
            "bundle_file": rel_to_root(bundle_out),
            "bundle_sha256": bundle_sha,
            "ots_status": bundle.get("ots_status"),
            "dry_run_cost": dry_cost,
            "paid_upload_performed": False,
            "registry_updated": False,
            "main_chain_before_sha256": main_chain_before_sha,
            "main_chain_after_sha256": sha256_file(PRODUCTION_MAIN_CHAIN),
            "head_before_sha256": head_before_sha,
            "head_after_sha256": sha256_file(PRODUCTION_HEAD),
            "next_phase_allowed": False,
            "generated_at": utc_now(),
        }
        write_json(log_dir / "99-phase5-summary.json", summary)
        print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
        return 0

    if not args.enable_paid_upload:
        raise SystemExit("Use --enable-paid-upload with explicit confirmation to perform Phase 5 paid upload")

    if args.confirm_paid_upload != CONFIRM_PAID_UPLOAD:
        raise SystemExit(
            f"paid upload requires --confirm-paid-upload {CONFIRM_PAID_UPLOAD!r}"
        )

    if not args.jwk_path:
        raise SystemExit("--enable-paid-upload requires --jwk-path or ARWEAVE_JWK_PATH")

    paid_log_dir = log_dir / "paid-upload"
    paid_log_dir.mkdir(parents=True, exist_ok=True)

    run_arweave_cost_gate(
        payload_file=bundle_out,
        run_id=run_id,
        log_dir=paid_log_dir,
        mode="production",
        jwk_path=args.jwk_path,
        gateway_url=args.gateway_url,
        readback_gateways=args.readback_gateways,
        readback_timeout=args.readback_timeout_seconds,
        readback_retry=args.readback_retry_seconds,
    )

    paid_cost, upload, readback = validate_paid_outputs(paid_log_dir, bundle_sha)

    registry = update_and_verify_registry(
        anchor_file_rel=anchor_file_rel,
        bundle_file=bundle_out,
        log_dir=paid_log_dir,
    )

    latest_for_head = registry.get("latest_by_head", {}).get(bundle.get("head_entry_hash"), {})
    if upload.get("tx_id") not in {
        latest_for_head.get("latest_pending_tx_id"),
        latest_for_head.get("latest_verified_tx_id"),
        latest_for_head.get("latest_any_tx_id"),
    }:
        raise SystemExit("uploaded tx_id not reflected in latest_by_head")

    main_chain_after_sha = sha256_file(PRODUCTION_MAIN_CHAIN)
    head_after_sha = sha256_file(PRODUCTION_HEAD)

    if main_chain_after_sha != main_chain_before_sha:
        raise SystemExit("Phase 5 unexpectedly modified production main.chain.jsonl")
    if head_after_sha != head_before_sha:
        raise SystemExit("Phase 5 unexpectedly modified api/record-chain-head.json")

    summary = {
        "schema": "trinity_phase5_ots_arweave_paid_upload_summary.v1",
        "run_id": run_id,
        "result": "pass",
        "anchor_file": anchor_file_rel,
        "bundle_file": rel_to_root(bundle_out),
        "bundle_sha256": bundle_sha,
        "ots_status": bundle.get("ots_status"),
        "bitcoin_verified": bundle.get("bitcoin_verified"),
        "bitcoin_pending": bundle.get("bitcoin_pending"),
        "cost_estimate": {
            "estimated_upload_cost_winston": paid_cost.get("estimated_upload_cost_winston"),
            "estimated_upload_cost_ar": paid_cost.get("estimated_upload_cost_ar"),
            "estimated_upload_cost_usd": paid_cost.get("estimated_upload_cost_usd"),
            "estimated_upload_cost_usd_with_buffer": paid_cost.get("estimated_upload_cost_usd_with_buffer"),
            "effective_max_upload_usd": paid_cost.get("effective_max_upload_usd"),
            "balance_before_ar": paid_cost.get("balance_before_ar"),
            "decision": paid_cost.get("decision"),
        },
        "upload_result": {
            "tx_id": upload.get("tx_id"),
            "gateway_url": upload.get("gateway_url"),
            "wallet_address": upload.get("wallet_address"),
            "balance_before_ar": upload.get("balance_before_ar"),
            "balance_after_ar": upload.get("balance_after_ar"),
            "actual_delta_ar": upload.get("actual_delta_ar"),
            "estimated_cost_usd": upload.get("estimated_cost_usd"),
            "remaining_balance_estimated_usd": upload.get("remaining_balance_estimated_usd"),
            "payload_sha256": upload.get("payload_sha256"),
        },
        "readback_result": {
            "result": readback.get("result"),
            "hash_match": readback.get("hash_match"),
            "byte_for_byte_match": readback.get("byte_for_byte_match"),
            "downloaded_sha256": readback.get("downloaded_sha256"),
            "gateway_url": readback.get("gateway_url"),
        },
        "arweave_tx_id": upload.get("tx_id"),
        "arweave_gateway_url": upload.get("gateway_url"),
        "registry": "record-chain/ots/arweave-registry.json",
        "api_registry": "api/record-chain-ots-arweave-registry.json",
        "registry_entry_count": registry.get("entry_count"),
        "paid_upload_performed": True,
        "registry_updated": True,
        "main_chain_before_sha256": main_chain_before_sha,
        "main_chain_after_sha256": main_chain_after_sha,
        "head_before_sha256": head_before_sha,
        "head_after_sha256": head_after_sha,
        "main_chain_modified": False,
        "head_modified": False,
        "entry_hash_modified": False,
        "next_phase_allowed": True,
        "generated_at": utc_now(),
    }
    write_json(log_dir / "99-phase5-summary.json", summary)
    print("[PHASE5 COMPLETE]")
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
