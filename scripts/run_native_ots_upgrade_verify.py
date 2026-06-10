#!/usr/bin/env python3
"""Native OTS upgraded/verified proof bundle lifecycle.

Adapts Phase6 semantics to native Record-Chain OTS paths:
  api/record-chain-native-ots-latest.json
  record-chain/ots/native-anchors/
  record-chain/ots/native-arweave-bundles/
  record-chain/ots/native-arweave-registry.json
  api/record-chain-native-ots-arweave-registry.json

Lifecycle:
  pending  -> initial OTS stamp (handled by record-chain-head-ots-anchor workflow)
  upgraded -> BitcoinBlockHeaderAttestation embedded, bitcoin_verified=false
  verified -> strict Bitcoin verification succeeded, bitcoin_verified=true
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

NATIVE_LATEST_OTS = ROOT / "api/record-chain-native-ots-latest.json"
NATIVE_ANCHORS_DIR = ROOT / "record-chain/ots/native-anchors"
NATIVE_BUNDLES_DIR = ROOT / "record-chain/ots/native-arweave-bundles"
NATIVE_REGISTRY = ROOT / "record-chain/ots/native-arweave-registry.json"
NATIVE_API_REGISTRY = ROOT / "api/record-chain-native-ots-arweave-registry.json"
NATIVE_OTS_BACKLOG = ROOT / "record-chain/ots/native-ots-backlog.json"
NATIVE_OTS_API_BACKLOG = ROOT / "api/record-chain-native-ots-backlog.json"

CHAIN_TIP = ROOT / "record-chain/chain-tip.json"
RECORD_INDEX = ROOT / "record-chain/indexes/record-index.json"

CONFIRM_PAID_UPLOAD = "I_UNDERSTAND_THIS_UPLOADS_THE_VERIFIED_OTS_PROOF_BUNDLE_TO_ARWEAVE"
EXPECTED_OWNER = "r1EdzCQ9E7CaAOEywI5netR6EcSopNOa08oi2Coz68s"
MAX_UPLOAD_USD = "0.10"
SAFETY_MULTIPLIER = "1.20"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=False, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def refresh_native_ots_backlog() -> None:
    detector = ROOT / "scripts" / "detect_archive_backlog.py"
    if detector.exists():
        subprocess.run([sys.executable, str(detector), "--write"], cwd=ROOT, check=False)


def mark_native_ots_backlog_status(anchor_rel: str | None, status: str, error: str | None = None, tx_id: str | None = None) -> None:
    refresh_native_ots_backlog()
    data = read_json(NATIVE_OTS_BACKLOG) if NATIVE_OTS_BACKLOG.exists() else {"items": []}
    changed = False
    for item in data.get("items", []):
        if anchor_rel and item.get("anchor_file") != anchor_rel:
            continue
        item["archive_status"] = status
        item["retry_count"] = int(item.get("retry_count") or 0) + 1
        item["last_attempt_at"] = utc_now()
        item["last_error"] = error
        if tx_id:
            item["tx_id"] = tx_id
        item["next_action"] = {
            "waiting_for_key": "provide_arweave_key",
            "upload_failed": "retry_upload",
            "readback_failed": "retry_readback_or_upload",
            "archived": "no_op",
        }.get(status, "review")
        changed = True
        break
    if changed:
        # Keep the existing detector-generated envelope and let the detector recompute on the next pass.
        write_json(NATIVE_OTS_BACKLOG, data)
        write_json(NATIVE_OTS_API_BACKLOG, data)


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
    check: bool = True,
    stdout_file: Path | None = None,
    stderr_file: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    merged_env = {**os.environ, **(env or {})}
    result = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
        env=merged_env,
    )
    if stdout_file and result.stdout:
        stdout_file.parent.mkdir(parents=True, exist_ok=True)
        stdout_file.write_text(result.stdout, encoding="utf-8")
    if stderr_file and result.stderr:
        stderr_file.parent.mkdir(parents=True, exist_ok=True)
        stderr_file.write_text(result.stderr, encoding="utf-8")
    if check and result.returncode != 0:
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(cmd)}\n{result.stderr}")
    return result


def precheck_files() -> None:
    for path in [
        "api/record-chain-native-ots-latest.json",
        "record-chain/chain-tip.json",
        "record-chain/indexes/record-index.json",
        "scripts/ots_verify_record_chain_anchor.py",
        "scripts/build_ots_arweave_bundle.py",
    ]:
        if not (ROOT / path).exists():
            raise SystemExit(f"missing required file: {path}")


def snapshot_core_files() -> dict[str, str | None]:
    return {
        "chain_tip_sha256": sha256_file(CHAIN_TIP),
        "record_index_sha256": sha256_file(RECORD_INDEX),
    }


def assert_core_files_unchanged(before: dict[str, str | None]) -> None:
    after = snapshot_core_files()
    for key, before_sha in before.items():
        after_sha = after[key]
        if before_sha != after_sha:
            raise SystemExit(f"core file changed during run: {key}")


def validate_native_latest_ots() -> dict[str, Any]:
    latest = read_json(NATIVE_LATEST_OTS)
    if latest.get("schema") != "trinityaccord.native-record-chain-ots-latest.v1":
        raise SystemExit("native OTS latest schema mismatch")
    if latest.get("ots_status") not in {"pending", "upgraded", "verified"}:
        raise SystemExit(f"unexpected native OTS status: {latest.get('ots_status')}")
    if latest.get("bitcoin_verified") is True and latest.get("ots_status") != "verified":
        raise SystemExit("invalid state: bitcoin_verified=true but ots_status is not verified")
    return latest


def validate_native_anchor(anchor_rel: str) -> dict[str, Any]:
    anchor_path = repo_path(anchor_rel)
    if not anchor_path.exists():
        raise SystemExit(f"native anchor missing: {anchor_rel}")
    anchor = read_json(anchor_path)
    if anchor.get("schema") != "trinityaccord.native-record-chain-ots-anchor.v1":
        raise SystemExit(f"native anchor schema mismatch: {anchor.get('schema')}")
    if anchor.get("ots_status") not in {"pending", "upgraded", "verified"}:
        raise SystemExit(f"unexpected native anchor ots_status: {anchor.get('ots_status')}")
    if anchor.get("bitcoin_verified") is True and anchor.get("ots_status") != "verified":
        raise SystemExit("native anchor: bitcoin_verified=true but ots_status is not verified")
    return anchor


def sync_native_latest_from_anchor(anchor_rel: str) -> dict[str, Any]:
    """Sync api/record-chain-native-ots-latest.json from anchor state."""
    anchor = validate_native_anchor(anchor_rel)
    latest = read_json(NATIVE_LATEST_OTS)

    latest["ots_status"] = anchor.get("ots_status", latest.get("ots_status", "pending"))
    latest["bitcoin_pending"] = anchor.get("bitcoin_pending", latest.get("bitcoin_pending", False))
    latest["bitcoin_verified"] = anchor.get("bitcoin_verified", latest.get("bitcoin_verified", False))
    latest["bitcoin_attestation_embedded"] = anchor.get(
        "bitcoin_attestation_embedded", latest.get("bitcoin_attestation_embedded", False)
    )
    latest["strict_bitcoin_verified"] = anchor.get(
        "strict_bitcoin_verified", latest.get("strict_bitcoin_verified", False)
    )
    latest["updated_at"] = utc_now()
    if anchor.get("verified_at"):
        latest["verified_at"] = anchor["verified_at"]

    write_json(NATIVE_LATEST_OTS, latest)
    return latest


def validate_native_registry() -> dict[str, Any]:
    if not NATIVE_REGISTRY.exists():
        # Initialize empty registry
        registry = {
            "schema": "trinityaccord.native-ots-arweave-registry.v1",
            "entries": [],
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        write_json(NATIVE_REGISTRY, registry)
        write_json(NATIVE_API_REGISTRY, registry)
        return registry

    registry = read_json(NATIVE_REGISTRY)
    for index, entry in enumerate(registry.get("entries", [])):
        tx_id = entry.get("tx_id")
        archive_status = entry.get("archive_status")
        if tx_id and archive_status != "arweave_archived":
            raise SystemExit(f"native registry entry[{index}] has tx_id but is not arweave_archived")
        if not tx_id and archive_status == "arweave_archived":
            raise SystemExit(f"native registry entry[{index}] claims arweave_archived without tx_id")

    if NATIVE_API_REGISTRY.exists():
        api_registry = read_json(NATIVE_API_REGISTRY)
        if registry != api_registry:
            raise SystemExit("native registry and api registry differ")
    return registry


def registry_entry_for_bundle_sha(registry: dict[str, Any], bundle_sha: str) -> dict[str, Any] | None:
    for entry in registry.get("entries", []):
        if entry.get("bundle_sha256") == bundle_sha:
            return entry
    return None


def registry_has_bundle_sha(registry: dict[str, Any], bundle_sha: str) -> bool:
    return registry_entry_for_bundle_sha(registry, bundle_sha) is not None


def registry_entry_is_arweave_archived(entry: dict[str, Any] | None) -> bool:
    return bool(entry and entry.get("tx_id") and entry.get("archive_status") == "arweave_archived")


def has_upgraded_archive(registry: dict[str, Any], anchored_sha: str) -> bool:
    for entry in registry.get("entries", []):
        if (
            entry.get("anchored_file_sha256") == anchored_sha
            and entry.get("ots_status") == "upgraded"
            and entry.get("tx_id")
            and entry.get("archive_status") == "arweave_archived"
        ):
            return True
    return False


def has_verified_archive(registry: dict[str, Any], anchored_sha: str) -> bool:
    for entry in registry.get("entries", []):
        if (
            entry.get("anchored_file_sha256") == anchored_sha
            and entry.get("ots_status") == "verified"
            and entry.get("tx_id")
            and entry.get("archive_status") == "arweave_archived"
        ):
            return True
    return False


def ots_upgrade_and_verify(
    *,
    anchor_rel: str,
    log_dir: Path,
    ots_bin: str,
    bitcoin_node_url: str | None,
    strict: bool,
    skip_upgrade: bool = False,
) -> tuple[dict[str, Any], bool]:
    """Run OTS upgrade+verify on a native anchor.

    Returns (anchor_dict, success_bool).
    """
    if not shutil.which(ots_bin):
        raise SystemExit("OTS CLI missing. Install: python3 -m pip install -r requirements-ots.txt")

    cmd = [
        sys.executable,
        "scripts/ots_verify_record_chain_anchor.py",
        "--anchor-file", anchor_rel,
        "--ots-bin", ots_bin,
        "--write-updated-anchor",
    ]
    if not skip_upgrade:
        cmd.append("--upgrade")
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

    anchor = validate_native_anchor(anchor_rel)

    if result.returncode == 0:
        if strict:
            if anchor.get("ots_status") == "verified" and anchor.get("bitcoin_verified") is True:
                return anchor, True
            raise SystemExit("strict verify returned success but anchor is not marked verified")
        is_verified = anchor.get("ots_status") == "verified" and anchor.get("bitcoin_verified") is True
        is_upgraded = anchor.get("ots_status") == "upgraded" or anchor.get("bitcoin_attestation_embedded") is True
        return anchor, bool(is_verified or is_upgraded)

    is_upgraded = anchor.get("ots_status") == "upgraded" or anchor.get("bitcoin_attestation_embedded") is True
    if is_upgraded:
        return anchor, True

    if anchor.get("bitcoin_pending") is True or anchor.get("ots_status") == "pending":
        return anchor, False

    raise SystemExit(f"OTS verify failed for non-pending reason; strict={strict}")


def build_native_upgraded_bundle(anchor_rel: str) -> Path:
    """Build upgraded bundle for native anchor."""
    anchor = validate_native_anchor(anchor_rel)
    if anchor.get("ots_status") != "upgraded":
        raise SystemExit("cannot build upgraded bundle: anchor ots_status is not upgraded")
    if anchor.get("bitcoin_attestation_embedded") is not True:
        raise SystemExit("cannot build upgraded bundle: bitcoin_attestation_embedded is not true")

    safe_stem = Path(anchor_rel).stem
    out = NATIVE_BUNDLES_DIR / f"{safe_stem}.upgraded.arweave-bundle.json"

    run_cmd([
        sys.executable,
        "scripts/build_ots_arweave_bundle.py",
        "--anchor-file", anchor_rel,
        "--out", rel(out),
    ])

    bundle = read_json(out)
    if bundle.get("ots_status") != "upgraded":
        raise SystemExit(f"built bundle ots_status is {bundle.get('ots_status')}, expected upgraded")
    if bundle.get("bitcoin_attestation_embedded") is not True:
        raise SystemExit("built bundle missing bitcoin_attestation_embedded")
    if bundle.get("bitcoin_verified") is not False:
        raise SystemExit("built bundle bitcoin_verified must be false for upgraded bundles")
    return out


def build_native_verified_bundle(anchor_rel: str) -> Path:
    """Build verified bundle for native anchor."""
    anchor = validate_native_anchor(anchor_rel)
    if anchor.get("ots_status") != "verified" or anchor.get("bitcoin_verified") is not True:
        raise SystemExit("cannot build verified bundle before strict Bitcoin verification")

    safe_stem = Path(anchor_rel).stem
    out = NATIVE_BUNDLES_DIR / f"{safe_stem}.verified.arweave-bundle.json"

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


def update_native_registry(
    anchor_rel: str,
    bundle: Path,
    log_dir: Path,
    *,
    tx_id: str | None = None,
    wallet_address: str | None = None,
    gateway_url: str | None = None,
) -> dict[str, Any]:
    """Update native OTS Arweave registry with a new bundle entry."""
    anchor = validate_native_anchor(anchor_rel)
    bundle_data = read_json(bundle)
    bundle_sha = sha256_bytes(bundle.read_bytes())

    registry = validate_native_registry()

    entry = {
        "anchored_file": anchor.get("anchored_file"),
        "anchored_file_sha256": anchor.get("anchored_file_sha256"),
        "anchor_file": anchor_rel,
        "ots_file": anchor.get("ots_file"),
        "ots_file_sha256": anchor.get("ots_file_sha256"),
        "bundle_file": rel(bundle),
        "bundle_sha256": bundle_sha,
        "ots_status": anchor.get("ots_status"),
        "bitcoin_attestation_embedded": anchor.get("bitcoin_attestation_embedded", False),
        "bitcoin_verified": anchor.get("bitcoin_verified", False),
        "strict_bitcoin_verified": anchor.get("strict_bitcoin_verified", False),
        "tx_id": tx_id,
        "gateway_url": gateway_url,
        "wallet_address": wallet_address,
        "archive_status": (
            "arweave_archived" if tx_id else "registered_without_arweave_tx"
        ),
        "uploaded_at": utc_now() if tx_id else None,
        "registered_at": utc_now(),
        "boundary": {
            "ots_proof_bundle_arweave_archive_is_mirror_only": True,
            "ots_proof_bundle_arweave_archive_is_not_authority": True,
            "ots_proof_bundle_arweave_archive_is_not_attestation": True,
            "ots_proof_bundle_arweave_archive_is_not_amendment": True,
            "ots_proof_bundle_arweave_archive_is_not_successor_reception": True,
        },
    }

    entries = registry.setdefault("entries", [])
    existing = registry_entry_for_bundle_sha(registry, bundle_sha)
    if existing:
        if tx_id and not existing.get("tx_id"):
            existing.update(entry)
        elif tx_id and existing.get("tx_id") != tx_id:
            raise SystemExit("bundle already registered with different tx_id")
        else:
            entry = existing
    else:
        entries.append(entry)
    registry["updated_at"] = utc_now()

    write_json(NATIVE_REGISTRY, registry)
    write_json(NATIVE_API_REGISTRY, registry)
    return registry


def upload_native_ots_bundle_to_arweave(
    *,
    bundle: Path,
    log_dir: Path,
    run_id: str,
    jwk_path: str,
    gateway_url: str,
    readback_gateways: str,
    readback_timeout_seconds: str,
    readback_retry_seconds: str,
) -> dict[str, Any]:
    """Upload a native OTS proof bundle to Arweave through the paid cost gate."""
    paid_dir = log_dir / "paid-upload"
    paid_dir.mkdir(parents=True, exist_ok=True)

    extra_tags = [
        {"name": "Trinity-Artifact-Type", "value": "Native-OTS-Proof-Bundle"},
        {"name": "Trinity-Boundary", "value": "mirror-only-not-authority-not-attestation-not-amendment"},
    ]
    env = {
        "ALLOW_PAID_ARWEAVE_CANARY": "true",
        "ARWEAVE_READBACK_GATEWAYS": readback_gateways,
        "ARWEAVE_READBACK_TIMEOUT_SECONDS": str(readback_timeout_seconds),
        "ARWEAVE_READBACK_RETRY_SECONDS": str(readback_retry_seconds),
    }
    run_cmd([
        "node",
        "scripts/arweave_cost_gate.mjs",
        "--payload-file", rel(bundle),
        "--record-type", "native_ots_proof_bundle",
        "--run-id", run_id,
        "--log-dir", rel(paid_dir),
        "--mode", "production",
        "--expected-owner", EXPECTED_OWNER,
        "--gateway-url", gateway_url,
        "--max-upload-usd", MAX_UPLOAD_USD,
        "--safety-multiplier", SAFETY_MULTIPLIER,
        "--jwk-path", jwk_path,
        "--content-type", "application/json",
        "--app-name", "Trinity-Accord-Native-OTS-Proof-Bundle",
        "--extra-tags-json", json.dumps(extra_tags, separators=(",", ":")),
    ], env=env)

    upload = read_json(paid_dir / "11-arweave-upload-result.native_ots_proof_bundle.json")
    readback = read_json(paid_dir / "11b-arweave-readback-verify.native_ots_proof_bundle.json")
    bundle_sha = sha256_bytes(bundle.read_bytes())

    if upload.get("result") != "uploaded":
        raise SystemExit(f"native OTS proof bundle upload did not complete: {upload.get('result')}")
    if not upload.get("tx_id"):
        raise SystemExit("native OTS proof bundle upload result missing tx_id")
    if upload.get("payload_sha256") != bundle_sha:
        raise SystemExit("native OTS proof bundle upload payload sha mismatch")
    if readback.get("result") != "pass" or readback.get("hash_match") is not True:
        raise SystemExit("native OTS proof bundle readback verification failed")
    if readback.get("downloaded_sha256") != bundle_sha:
        raise SystemExit("native OTS proof bundle readback sha mismatch")

    return {
        "tx_id": upload["tx_id"],
        "wallet_address": upload.get("wallet_address"),
        "gateway_url": upload.get("gateway_url"),
        "upload_result": rel(paid_dir / "11-arweave-upload-result.native_ots_proof_bundle.json"),
        "readback_result": rel(paid_dir / "11b-arweave-readback-verify.native_ots_proof_bundle.json"),
    }


def write_summary(log_dir: Path, summary: dict[str, Any]) -> None:
    summary.setdefault("generated_at", utc_now())
    write_json(log_dir / "99-native-ots-summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="Native OTS upgraded/verified proof bundle lifecycle.")
    parser.add_argument("--run-id", default=f"native-ots-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}")
    parser.add_argument("--log-dir", default=None)
    parser.add_argument("--ots-bin", default="ots")
    parser.add_argument("--bitcoin-node-url", default=os.environ.get("OTS_BITCOIN_NODE_URL"))
    parser.add_argument("--skip-upgrade", action="store_true",
                        default=bool(os.environ.get("OTS_SKIP_UPGRADE")),
                        help="Skip ots upgrade step")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--enable-paid-upload", action="store_true")
    parser.add_argument("--anchor-file", default=None)
    parser.add_argument("--all-backlog", action="store_true")
    parser.add_argument("--max-items", type=int, default=1)
    parser.add_argument("--confirm-paid-upload", default="")
    parser.add_argument("--jwk-path", default=os.environ.get("ARWEAVE_JWK_PATH"))
    parser.add_argument("--gateway-url", default=os.environ.get("ARWEAVE_GATEWAY_URL", "https://arweave.net"))
    parser.add_argument("--readback-gateways", default=os.environ.get("ARWEAVE_READBACK_GATEWAYS", "https://arweave.net"))
    parser.add_argument("--readback-timeout-seconds", default=os.environ.get("ARWEAVE_READBACK_TIMEOUT_SECONDS", "900"))
    parser.add_argument("--readback-retry-seconds", default=os.environ.get("ARWEAVE_READBACK_RETRY_SECONDS", "15"))
    args = parser.parse_args()

    precheck_files()

    log_dir = (
        Path(args.log_dir) if args.log_dir
        else ROOT / "record-chain/audit/native-ots" / args.run_id
    )
    if not log_dir.is_absolute():
        log_dir = ROOT / log_dir
    log_dir = under_repo(log_dir, "--log-dir")
    log_dir.mkdir(parents=True, exist_ok=True)

    core_before = snapshot_core_files()

    latest = validate_native_latest_ots()
    if args.all_backlog:
        refresh_native_ots_backlog()
        backlog = read_json(NATIVE_OTS_BACKLOG) if NATIVE_OTS_BACKLOG.exists() else {"items": []}
        candidates = [item for item in backlog.get("items", []) if item.get("archive_status") in {"pending_upload", "upload_failed", "readback_failed", "waiting_for_key"}]
        if not candidates:
            write_summary(log_dir, {"schema": "trinity_native_ots_summary.v1", "run_id": args.run_id, "result": "backlog_empty", "paid_upload_performed": False, "registry_updated": False, "next_action": "no_op"})
            return 0
        if args.max_items < 1:
            raise SystemExit("--max-items must be >= 1")
        args.anchor_file = candidates[0].get("anchor_file") or args.anchor_file
    anchor_rel = args.anchor_file or latest["latest_anchor_file"]
    if not is_repo_relative(anchor_rel):
        raise SystemExit(f"--anchor-file must be repo-relative: {anchor_rel}")
    anchor = validate_native_anchor(anchor_rel)
    registry = validate_native_registry()
    anchored_sha = anchor.get("anchored_file_sha256")

    # Check if already verified and archived
    if has_verified_archive(registry, anchored_sha):
        assert_core_files_unchanged(core_before)
        write_summary(log_dir, {
            "schema": "trinity_native_ots_summary.v1",
            "run_id": args.run_id,
            "result": "already_verified_archived",
            "paid_upload_performed": False,
            "registry_updated": False,
            "next_action": "no_op",
        })
        return 0

    # Step 1: Non-strict upgrade+verify
    anchor, non_strict_ok = ots_upgrade_and_verify(
        anchor_rel=anchor_rel,
        log_dir=log_dir,
        ots_bin=args.ots_bin,
        bitcoin_node_url=args.bitcoin_node_url,
        strict=False,
        skip_upgrade=args.skip_upgrade,
    )

    is_upgraded = anchor.get("ots_status") == "upgraded" or anchor.get("bitcoin_attestation_embedded") is True

    # Step 2: Strict Bitcoin verify if node available
    verified = False
    if args.bitcoin_node_url and non_strict_ok:
        anchor, verified = ots_upgrade_and_verify(
            anchor_rel=anchor_rel,
            log_dir=log_dir,
            ots_bin=args.ots_bin,
            bitcoin_node_url=args.bitcoin_node_url,
            strict=True,
        )

    # Sync latest from anchor
    sync_native_latest_from_anchor(anchor_rel)
    assert_core_files_unchanged(core_before)

    # Build bundle based on state
    bundle: Path | None = None
    result: str = "pending"

    if verified and anchor.get("ots_status") == "verified" and anchor.get("bitcoin_verified") is True:
        bundle = build_native_verified_bundle(anchor_rel)
        result = "verified"
    elif is_upgraded:
        if not has_upgraded_archive(registry, anchored_sha):
            bundle = build_native_upgraded_bundle(anchor_rel)
            result = "upgraded"
        else:
            result = "upgraded_archived"

    paid_upload_performed = False
    upload_info: dict[str, Any] | None = None
    registry_updated = False

    if bundle and not args.verify_only:
        bundle_sha = sha256_bytes(bundle.read_bytes())
        existing_entry = registry_entry_for_bundle_sha(registry, bundle_sha)
        if registry_entry_is_arweave_archived(existing_entry):
            result = f"{result}_archived" if "archived" not in result else result
        elif args.enable_paid_upload:
            if args.confirm_paid_upload != CONFIRM_PAID_UPLOAD:
                raise SystemExit(f"paid upload requires --confirm-paid-upload {CONFIRM_PAID_UPLOAD!r}")
            if not args.jwk_path:
                mark_native_ots_backlog_status(anchor_rel, "waiting_for_key", "paid upload requires --jwk-path or ARWEAVE_JWK_PATH")
                raise SystemExit("paid upload requires --jwk-path or ARWEAVE_JWK_PATH")
            try:
                upload_info = upload_native_ots_bundle_to_arweave(
                bundle=bundle,
                log_dir=log_dir,
                run_id=args.run_id,
                jwk_path=args.jwk_path,
                gateway_url=args.gateway_url,
                readback_gateways=args.readback_gateways,
                readback_timeout_seconds=args.readback_timeout_seconds,
                readback_retry_seconds=args.readback_retry_seconds,
                )
            except SystemExit as exc:
                message = str(exc)
                mark_native_ots_backlog_status(anchor_rel, "readback_failed" if "readback" in message.lower() else "upload_failed", message)
                raise
            registry = update_native_registry(
                anchor_rel,
                bundle,
                log_dir,
                tx_id=upload_info["tx_id"],
                wallet_address=upload_info.get("wallet_address"),
                gateway_url=upload_info.get("gateway_url"),
            )
            paid_upload_performed = True
            registry_updated = True
            mark_native_ots_backlog_status(anchor_rel, "archived", None, upload_info.get("tx_id"))
            result = f"{result}_archived" if "archived" not in result else result
        else:
            registry = update_native_registry(anchor_rel, bundle, log_dir)
            registry_updated = existing_entry is None
            result = f"{result}_registered"

    write_summary(log_dir, {
        "schema": "trinity_native_ots_summary.v1",
        "run_id": args.run_id,
        "result": result,
        "anchor_ots_status": anchor.get("ots_status"),
        "anchor_bitcoin_verified": anchor.get("bitcoin_verified"),
        "anchor_bitcoin_attestation_embedded": anchor.get("bitcoin_attestation_embedded", False),
        "paid_upload_performed": paid_upload_performed,
        "registry_updated": registry_updated,
        "native_ots_proof_bundle_archive": upload_info,
        "core_files_unchanged": True,
    })

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
