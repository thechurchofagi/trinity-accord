#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ID = time.strftime("phase6-ots-watch-%Y%m%dT%H%M%SZ", time.gmtime())

CONFIRM_PAID_UPLOAD = "I_UNDERSTAND_THIS_UPLOADS_THE_VERIFIED_OTS_PROOF_BUNDLE_TO_ARWEAVE"
EXPECTED_OWNER = "r1EdzCQ9E7CaAOEywI5netR6EcSopNOa08oi2Coz68s"
RECORD_TYPE = "ots_anchor_archive"
MAX_UPLOAD_USD = "0.10"
SAFETY_MULTIPLIER = "1.20"

MAIN_CHAIN = ROOT / "record-chain/hash-chain/main.chain.jsonl"
HEAD = ROOT / "api/record-chain-head.json"
LATEST_OTS = ROOT / "api/record-chain-ots-latest.json"
REGISTRY = ROOT / "record-chain/ots/arweave-registry.json"
API_REGISTRY = ROOT / "api/record-chain-ots-arweave-registry.json"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def is_repo_relative(value: str) -> bool:
    p = Path(value)
    return bool(value) and not p.is_absolute() and ".." not in p.parts


def repo_path(value: str) -> Path:
    if not is_repo_relative(value):
        raise SystemExit(f"expected repo-relative path, got: {value}")
    return ROOT / value


def under_repo(path: Path, label: str) -> Path:
    resolved = path.resolve()
    root = ROOT.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        raise SystemExit(f"{label} must be under repo root: {path}")
    return resolved


def rel(path: Path) -> str:
    return str(under_repo(path, "path").relative_to(ROOT))


def run_cmd(
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    check: bool = True,
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

    if check and result.returncode != 0:
        raise SystemExit(f"command failed exit={result.returncode}: {' '.join(cmd)}")

    return result


def precheck_files() -> None:
    required = [
        "requirements-ots.txt",
        "api/record-chain-ots-latest.json",
        "record-chain/hash-chain/main.chain.jsonl",
        "record-chain/ots/arweave-registry.json",
        "api/record-chain-ots-arweave-registry.json",
        "scripts/ots_verify_record_chain_anchor.py",
        "scripts/build_ots_arweave_bundle.py",
        "scripts/arweave_cost_gate.mjs",
        "scripts/update_ots_arweave_registry.py",
        "scripts/verify_ots_arweave_registry.py",
        "scripts/test_arweave_cost_gate_safety.mjs",
        "scripts/test_arweave_readback_hash_fixture.mjs",
        "scripts/test_ots_arweave_registry.py",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    if missing:
        raise SystemExit("missing required files:\n" + "\n".join(missing))


def snapshot_core_files() -> dict[str, str | None]:
    return {
        "main_chain_sha256": sha256_file(MAIN_CHAIN),
        "head_sha256": sha256_file(HEAD),
    }


def assert_core_files_unchanged(before: dict[str, str | None]) -> None:
    after = snapshot_core_files()
    if after["main_chain_sha256"] != before["main_chain_sha256"]:
        raise SystemExit("main.chain.jsonl changed unexpectedly")
    if after["head_sha256"] != before["head_sha256"]:
        raise SystemExit("api/record-chain-head.json changed unexpectedly")


def validate_latest_ots() -> dict[str, Any]:
    latest = read_json(LATEST_OTS)
    if latest.get("schema") != "trinity_record_chain_ots_latest.v1":
        raise SystemExit("latest OTS schema mismatch")
    if latest.get("chain_id") != "trinity-record-chain-main":
        raise SystemExit("latest chain_id mismatch")
    if latest.get("ots_status") == "dry_run":
        raise SystemExit("refusing dry_run OTS latest")
    if latest.get("ots_status") not in {"pending", "verified"}:
        raise SystemExit(f"unexpected latest ots_status: {latest.get('ots_status')}")
    if not re.fullmatch(r"[a-f0-9]{64}", str(latest.get("head_entry_hash") or "")):
        raise SystemExit("latest head_entry_hash invalid")

    for key in ["latest_anchor_file", "latest_anchored_file", "latest_ots_file"]:
        value = latest.get(key)
        if not isinstance(value, str) or not is_repo_relative(value):
            raise SystemExit(f"{key} must be repo-relative")
        if not repo_path(value).exists():
            raise SystemExit(f"{key} missing: {value}")

    return latest


def validate_anchor(anchor_rel: str) -> dict[str, Any]:
    anchor = read_json(repo_path(anchor_rel))
    if anchor.get("schema") != "trinity_record_chain_ots_anchor.v1":
        raise SystemExit("anchor schema mismatch")
    if anchor.get("chain_id") != "trinity-record-chain-main":
        raise SystemExit("anchor chain_id mismatch")
    if anchor.get("ots_status") == "dry_run":
        raise SystemExit("refusing dry_run anchor")
    if anchor.get("ots_status") not in {"pending", "verified"}:
        raise SystemExit(f"unexpected anchor ots_status: {anchor.get('ots_status')}")

    for key in ["anchored_file", "ots_file"]:
        value = anchor.get(key)
        if not isinstance(value, str) or not is_repo_relative(value):
            raise SystemExit(f"anchor {key} must be repo-relative")
        if not repo_path(value).exists():
            raise SystemExit(f"anchor {key} missing: {value}")

    anchored_sha = sha256_file(repo_path(anchor["anchored_file"]))
    if anchored_sha != anchor.get("anchored_file_sha256"):
        raise SystemExit("anchored_file_sha256 mismatch")

    ots_sha = sha256_file(repo_path(anchor["ots_file"]))
    if anchor.get("ots_file_sha256") and ots_sha != anchor.get("ots_file_sha256"):
        raise SystemExit("ots_file_sha256 mismatch")

    return anchor


def validate_registry() -> dict[str, Any]:
    registry = read_json(REGISTRY)
    api_registry = read_json(API_REGISTRY)
    if registry != api_registry:
        raise SystemExit("registry and api registry differ")
    if registry.get("schema") != "trinity_record_chain_ots_arweave_registry.v1":
        raise SystemExit("registry schema mismatch")
    return registry


def latest_for_head(registry: dict[str, Any], head_hash: str) -> dict[str, Any]:
    item = registry.get("latest_by_head", {}).get(head_hash)
    if not item:
        raise SystemExit(f"registry.latest_by_head missing head {head_hash}")
    return item


def pending_tx_exists(registry: dict[str, Any], head_hash: str) -> bool:
    return bool(latest_for_head(registry, head_hash).get("latest_pending_tx_id"))


def has_verified_archive(registry: dict[str, Any], head_hash: str) -> bool:
    return bool(latest_for_head(registry, head_hash).get("latest_verified_tx_id"))


def registry_has_bundle_sha(registry: dict[str, Any], bundle_sha: str) -> bool:
    return any(entry.get("bundle_sha256") == bundle_sha for entry in registry.get("entries", []))


def ots_upgrade_and_verify(
    *,
    anchor_rel: str,
    log_dir: Path,
    ots_bin: str,
    bitcoin_node_url: str | None,
    strict: bool,
) -> tuple[dict[str, Any], bool]:
    if not shutil.which(ots_bin):
        raise SystemExit("OTS CLI missing. Install: python3 -m pip install -r requirements-ots.txt")

    cmd = [
        sys.executable,
        "scripts/ots_verify_record_chain_anchor.py",
        "--anchor-file", anchor_rel,
        "--ots-bin", ots_bin,
        "--upgrade",
        "--write-updated-anchor",
    ]
    if bitcoin_node_url:
        cmd += ["--bitcoin-node-url", bitcoin_node_url]
    if strict:
        cmd.append("--strict-bitcoin")

    result = run_cmd(
        cmd,
        check=False,
        stdout_file=log_dir / ("ots.strict.stdout.log" if strict else "ots.nonstrict.stdout.log"),
        stderr_file=log_dir / ("ots.strict.stderr.log" if strict else "ots.nonstrict.stderr.log"),
    )

    anchor = validate_anchor(anchor_rel)

    if result.returncode == 0:
        if strict:
            if anchor.get("ots_status") == "verified" and anchor.get("bitcoin_verified") is True:
                return anchor, True
            raise SystemExit("strict verify returned success but anchor is not marked verified")
        return anchor, bool(anchor.get("ots_status") == "verified" and anchor.get("bitcoin_verified") is True)

    if strict and (anchor.get("bitcoin_pending") is True or anchor.get("ots_status") == "pending"):
        return anchor, False

    raise SystemExit(f"OTS verify failed for non-pending reason; strict={strict}")


def forbid_price_overrides(env: dict[str, str]) -> None:
    forbidden = [
        "ARWEAVE_UPLOAD_PRICE_WINSTON_OVERRIDE",
        "AR_USD_PRICE_OVERRIDE",
        "ALLOW_ARWEAVE_PRICE_OVERRIDE_IN_PRODUCTION",
    ]
    present = [name for name in forbidden if env.get(name)]
    if present:
        raise SystemExit("price override forbidden: " + ", ".join(present))


def arweave_env(
    *,
    mode: str,
    log_dir: Path,
    run_id: str,
    jwk_path: str | None,
    gateway: str,
    readback_gateways: str,
    timeout: str,
    retry: str,
) -> dict[str, str]:
    env = os.environ.copy()
    env["E2E_RUN_ID"] = run_id
    env["E2E_LOG_DIR"] = str(log_dir)
    env["ARWEAVE_UPLOAD_MODE"] = mode
    env["EXPECTED_ARWEAVE_OWNER"] = EXPECTED_OWNER
    env["ARWEAVE_MAX_UPLOAD_USD"] = MAX_UPLOAD_USD
    env["ARWEAVE_SAFETY_MULTIPLIER"] = SAFETY_MULTIPLIER
    env["ARWEAVE_GATEWAY_URL"] = gateway
    env["ARWEAVE_READBACK_GATEWAYS"] = readback_gateways
    env["ARWEAVE_READBACK_TIMEOUT_SECONDS"] = timeout
    env["ARWEAVE_READBACK_RETRY_SECONDS"] = retry

    if mode == "production":
        env["ALLOW_PAID_ARWEAVE_CANARY"] = "true"
        if not jwk_path:
            raise SystemExit("production upload requires --jwk-path or ARWEAVE_JWK_PATH")
        env["ARWEAVE_JWK_PATH"] = jwk_path
        forbid_price_overrides(env)
    else:
        env["ALLOW_PAID_ARWEAVE_CANARY"] = "false"
        env.pop("ARWEAVE_JWK_PATH", None)

    return env


def build_verified_bundle(anchor_rel: str) -> Path:
    anchor = validate_anchor(anchor_rel)
    if anchor.get("ots_status") != "verified" or anchor.get("bitcoin_verified") is not True:
        raise SystemExit("cannot build verified bundle before strict Bitcoin verification")

    safe_stem = Path(anchor_rel).stem
    out = ROOT / "record-chain/ots/arweave-bundles" / f"{safe_stem}.verified.arweave-bundle.json"

    run_cmd([
        sys.executable,
        "scripts/build_ots_arweave_bundle.py",
        "--anchor-file", anchor_rel,
        "--out", rel(out),
    ])

    bundle = read_json(out)
    if bundle.get("ots_status") != "verified" or bundle.get("bitcoin_verified") is not True:
        raise SystemExit("built bundle is not verified")
    return out


def run_cost_gate(
    *,
    payload: Path,
    run_id: str,
    log_dir: Path,
    mode: str,
    jwk_path: str | None,
    gateway: str,
    readback_gateways: str,
    timeout: str,
    retry: str,
) -> None:
    payload = under_repo(payload, "payload")
    log_dir.mkdir(parents=True, exist_ok=True)
    env = arweave_env(
        mode=mode,
        log_dir=log_dir,
        run_id=run_id,
        jwk_path=jwk_path,
        gateway=gateway,
        readback_gateways=readback_gateways,
        timeout=timeout,
        retry=retry,
    )

    run_cmd([
        "node",
        "scripts/arweave_cost_gate.mjs",
        "--payload-file", rel(payload),
        "--record-type", RECORD_TYPE,
        "--run-id", run_id,
        "--log-dir", str(log_dir),
        "--mode", mode,
        "--expected-owner", EXPECTED_OWNER,
        "--gateway-url", gateway,
        "--max-upload-usd", MAX_UPLOAD_USD,
        "--safety-multiplier", SAFETY_MULTIPLIER,
    ], env=env)


def validate_dry_cost(log_dir: Path, bundle_sha: str) -> dict[str, Any]:
    cost = read_json(log_dir / f"10-arweave-cost-estimate.{RECORD_TYPE}.json")
    if cost.get("decision") != "DRY_RUN":
        raise SystemExit("dry-run decision must be DRY_RUN")
    if cost.get("payload_sha256") != bundle_sha:
        raise SystemExit("dry-run payload sha mismatch")
    if float(cost.get("effective_max_upload_usd", 0)) > 0.10:
        raise SystemExit("effective max upload USD exceeds 0.10")
    return cost


def validate_paid(log_dir: Path, bundle_sha: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    cost = read_json(log_dir / f"10-arweave-cost-estimate.{RECORD_TYPE}.json")
    upload = read_json(log_dir / f"11-arweave-upload-result.{RECORD_TYPE}.json")
    readback = read_json(log_dir / f"11b-arweave-readback-verify.{RECORD_TYPE}.json")

    if cost.get("decision") != "ALLOW":
        raise SystemExit("paid cost gate must be ALLOW")
    if float(cost.get("estimated_upload_cost_usd_with_buffer", 999)) > 0.10:
        raise SystemExit("estimated cost exceeds 0.10")
    if upload.get("result") != "uploaded":
        raise SystemExit("upload not uploaded")
    if upload.get("wallet_address") != EXPECTED_OWNER:
        raise SystemExit("wallet owner mismatch")
    if upload.get("payload_sha256") != bundle_sha:
        raise SystemExit("upload payload sha mismatch")
    if readback.get("result") != "pass":
        raise SystemExit("readback not pass")
    if readback.get("hash_match") is not True or readback.get("byte_for_byte_match") is not True:
        raise SystemExit("readback hash/byte match failed")
    if readback.get("downloaded_sha256") != bundle_sha:
        raise SystemExit("readback sha mismatch")

    return cost, upload, readback


def update_registry(anchor_rel: str, bundle: Path, log_dir: Path) -> dict[str, Any]:
    run_cmd([
        sys.executable,
        "scripts/update_ots_arweave_registry.py",
        "--anchor-file", anchor_rel,
        "--bundle-file", rel(bundle),
        "--upload-result", rel(log_dir / f"11-arweave-upload-result.{RECORD_TYPE}.json"),
        "--readback-result", rel(log_dir / f"11b-arweave-readback-verify.{RECORD_TYPE}.json"),
        "--registry", "record-chain/ots/arweave-registry.json",
        "--api-out", "api/record-chain-ots-arweave-registry.json",
    ])

    run_cmd([
        sys.executable,
        "scripts/verify_ots_arweave_registry.py",
        "--registry", "record-chain/ots/arweave-registry.json",
        "--verify-local-bundles",
    ])

    registry = read_json(REGISTRY)
    api = read_json(API_REGISTRY)
    if registry != api:
        raise SystemExit("registry and api registry differ after update")
    return registry


def write_summary(log_dir: Path, summary: dict[str, Any]) -> None:
    summary.setdefault("generated_at", utc_now())
    write_json(log_dir / "99-phase6-summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--log-dir", default=None)
    parser.add_argument("--ots-bin", default="ots")
    parser.add_argument("--bitcoin-node-url", default=os.environ.get("OTS_BITCOIN_NODE_URL"))
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--dry-run-cost-only", action="store_true")
    parser.add_argument("--enable-paid-upload", action="store_true")
    parser.add_argument("--confirm-paid-upload", default="")
    parser.add_argument("--jwk-path", default=os.environ.get("ARWEAVE_JWK_PATH"))
    parser.add_argument("--gateway-url", default=os.environ.get("ARWEAVE_GATEWAY_URL", "https://arweave.net"))
    parser.add_argument("--readback-gateways", default=os.environ.get("ARWEAVE_READBACK_GATEWAYS", "https://arweave.net"))
    parser.add_argument("--readback-timeout-seconds", default=os.environ.get("ARWEAVE_READBACK_TIMEOUT_SECONDS", "900"))
    parser.add_argument("--readback-retry-seconds", default=os.environ.get("ARWEAVE_READBACK_RETRY_SECONDS", "15"))
    args = parser.parse_args()

    precheck_files()

    log_dir = Path(args.log_dir) if args.log_dir else ROOT / "record-chain/audit/phase6" / args.run_id
    if not log_dir.is_absolute():
        log_dir = ROOT / log_dir
    log_dir = under_repo(log_dir, "--log-dir")
    log_dir.mkdir(parents=True, exist_ok=True)

    core_before = snapshot_core_files()
    registry_before = sha256_file(REGISTRY)
    api_registry_before = sha256_file(API_REGISTRY)

    run_cmd(["node", "scripts/test_arweave_cost_gate_safety.mjs"])
    run_cmd(["node", "scripts/test_arweave_readback_hash_fixture.mjs"])
    run_cmd([sys.executable, "scripts/test_ots_arweave_registry.py"])

    latest = validate_latest_ots()
    anchor_rel = latest["latest_anchor_file"]
    anchor = validate_anchor(anchor_rel)
    registry = validate_registry()
    head_hash = anchor.get("head_entry_hash")

    if not pending_tx_exists(registry, head_hash):
        raise SystemExit("Phase 5 pending archive missing from registry")

    if has_verified_archive(registry, head_hash):
        item = latest_for_head(registry, head_hash)
        assert_core_files_unchanged(core_before)
        write_summary(log_dir, {
            "schema": "trinity_phase6_summary.v1",
            "run_id": args.run_id,
            "result": "already_verified_archived",
            "latest_verified_tx_id": item.get("latest_verified_tx_id"),
            "paid_upload_performed": False,
            "registry_updated": False,
            "main_chain_before_sha256": core_before["main_chain_sha256"],
            "main_chain_after_sha256": sha256_file(MAIN_CHAIN),
            "head_before_sha256": core_before["head_sha256"],
            "head_after_sha256": sha256_file(HEAD),
            "next_action": "no_op",
        })
        return 0

    anchor, _ = ots_upgrade_and_verify(
        anchor_rel=anchor_rel,
        log_dir=log_dir,
        ots_bin=args.ots_bin,
        bitcoin_node_url=args.bitcoin_node_url,
        strict=False,
    )

    anchor, verified = ots_upgrade_and_verify(
        anchor_rel=anchor_rel,
        log_dir=log_dir,
        ots_bin=args.ots_bin,
        bitcoin_node_url=args.bitcoin_node_url,
        strict=True,
    )

    if not verified:
        assert_core_files_unchanged(core_before)
        write_summary(log_dir, {
            "schema": "trinity_phase6_summary.v1",
            "run_id": args.run_id,
            "result": "pending",
            "next_action": "retry_later",
            "anchor_file": anchor_rel,
            "ots_status": anchor.get("ots_status"),
            "bitcoin_verified": anchor.get("bitcoin_verified"),
            "bitcoin_pending": anchor.get("bitcoin_pending"),
            "paid_upload_performed": False,
            "registry_updated": False,
            "main_chain_before_sha256": core_before["main_chain_sha256"],
            "main_chain_after_sha256": sha256_file(MAIN_CHAIN),
            "head_before_sha256": core_before["head_sha256"],
            "head_after_sha256": sha256_file(HEAD),
            "registry_before_sha256": registry_before,
            "registry_after_sha256": sha256_file(REGISTRY),
            "api_registry_before_sha256": api_registry_before,
            "api_registry_after_sha256": sha256_file(API_REGISTRY),
        })
        return 0

    if args.verify_only:
        assert_core_files_unchanged(core_before)
        write_summary(log_dir, {
            "schema": "trinity_phase6_summary.v1",
            "run_id": args.run_id,
            "result": "verified",
            "anchor_file": anchor_rel,
            "bitcoin_verified": True,
            "paid_upload_performed": False,
            "registry_updated": False,
            "next_phase_allowed": True,
        })
        return 0

    bundle = build_verified_bundle(anchor_rel)
    bundle_sha = sha256_file(bundle)
    if not bundle_sha:
        raise SystemExit("verified bundle missing")

    registry = validate_registry()
    if registry_has_bundle_sha(registry, bundle_sha):
        raise SystemExit("verified bundle sha already exists in registry; refusing duplicate paid upload")

    dry_dir = log_dir / "dry-run-cost"
    run_cost_gate(
        payload=bundle,
        run_id=f"{args.run_id}-dry-run",
        log_dir=dry_dir,
        mode="dry_run",
        jwk_path=None,
        gateway=args.gateway_url,
        readback_gateways=args.readback_gateways,
        timeout=args.readback_timeout_seconds,
        retry=args.readback_retry_seconds,
    )
    dry_cost = validate_dry_cost(dry_dir, bundle_sha)

    if args.dry_run_cost_only:
        assert_core_files_unchanged(core_before)
        write_summary(log_dir, {
            "schema": "trinity_phase6_summary.v1",
            "run_id": args.run_id,
            "result": "verified_cost_dry_run",
            "bundle_file": rel(bundle),
            "bundle_sha256": bundle_sha,
            "dry_run_cost": dry_cost,
            "paid_upload_performed": False,
            "registry_updated": False,
            "next_phase_allowed": True,
        })
        return 0

    if not args.enable_paid_upload:
        raise SystemExit("verified. Use --enable-paid-upload with explicit confirmation to upload verified bundle.")

    if args.confirm_paid_upload != CONFIRM_PAID_UPLOAD:
        raise SystemExit(f"paid upload requires --confirm-paid-upload {CONFIRM_PAID_UPLOAD!r}")

    paid_dir = log_dir / "paid-upload"
    run_cost_gate(
        payload=bundle,
        run_id=args.run_id,
        log_dir=paid_dir,
        mode="production",
        jwk_path=args.jwk_path,
        gateway=args.gateway_url,
        readback_gateways=args.readback_gateways,
        timeout=args.readback_timeout_seconds,
        retry=args.readback_retry_seconds,
    )

    paid_cost, upload, readback = validate_paid(paid_dir, bundle_sha)
    registry = update_registry(anchor_rel, bundle, paid_dir)

    latest_item = latest_for_head(registry, head_hash)
    if latest_item.get("latest_verified_tx_id") != upload.get("tx_id"):
        raise SystemExit("latest_verified_tx_id not updated to verified tx")
    if latest_item.get("latest_any_tx_id") != upload.get("tx_id"):
        raise SystemExit("latest_any_tx_id not updated to verified tx")

    assert_core_files_unchanged(core_before)

    write_summary(log_dir, {
        "schema": "trinity_phase6_summary.v1",
        "run_id": args.run_id,
        "result": "pass",
        "anchor_file": anchor_rel,
        "bundle_file": rel(bundle),
        "bundle_sha256": bundle_sha,
        "ots_status": "verified",
        "bitcoin_verified": True,
        "cost_estimate": {
            "decision": paid_cost.get("decision"),
            "estimated_upload_cost_usd_with_buffer": paid_cost.get("estimated_upload_cost_usd_with_buffer"),
            "balance_before_ar": paid_cost.get("balance_before_ar"),
        },
        "upload_result": {
            "tx_id": upload.get("tx_id"),
            "gateway_url": upload.get("gateway_url"),
            "wallet_address": upload.get("wallet_address"),
            "payload_sha256": upload.get("payload_sha256"),
            "balance_before_ar": upload.get("balance_before_ar"),
            "balance_after_ar": upload.get("balance_after_ar"),
            "actual_delta_ar": upload.get("actual_delta_ar"),
        },
        "readback_result": {
            "result": readback.get("result"),
            "hash_match": readback.get("hash_match"),
            "byte_for_byte_match": readback.get("byte_for_byte_match"),
            "downloaded_sha256": readback.get("downloaded_sha256"),
        },
        "latest_pending_tx_id": latest_item.get("latest_pending_tx_id"),
        "latest_verified_tx_id": latest_item.get("latest_verified_tx_id"),
        "latest_any_tx_id": latest_item.get("latest_any_tx_id"),
        "paid_upload_performed": True,
        "registry_updated": True,
        "main_chain_before_sha256": core_before["main_chain_sha256"],
        "main_chain_after_sha256": sha256_file(MAIN_CHAIN),
        "head_before_sha256": core_before["head_sha256"],
        "head_after_sha256": sha256_file(HEAD),
        "next_action": "done",
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
