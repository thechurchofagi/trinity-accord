#!/usr/bin/env python3
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
DEFAULT_RUN_ID = time.strftime("phase4-prod-chain-ots-%Y%m%dT%H%M%SZ", time.gmtime())
REAL_OTS_CONFIRMATION = "I_UNDERSTAND_THIS_CREATES_A_REAL_OTS_TIMESTAMP"
PROD_APPEND_CONFIRMATION = "I_UNDERSTAND_THIS_APPENDS_TO_PRODUCTION_RECORD_CHAIN"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def run_cmd(
    cmd: list[str],
    *,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
    expect_ok: bool = True,
    stdout_file: Path | None = None,
    stderr_file: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    print("[RUN]", " ".join(cmd))
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
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


def assert_no_arweave_write_environment() -> None:
    dangerous = []
    if os.environ.get("ARWEAVE_UPLOAD_MODE") == "production":
        dangerous.append("ARWEAVE_UPLOAD_MODE=production")
    if os.environ.get("ALLOW_PAID_ARWEAVE_CANARY") == "true":
        dangerous.append("ALLOW_PAID_ARWEAVE_CANARY=true")
    if os.environ.get("ARWEAVE_JWK_PATH"):
        dangerous.append("ARWEAVE_JWK_PATH is set")
    if dangerous:
        raise SystemExit("Unsafe environment for Phase 4: " + ", ".join(dangerous))


def precheck_required_files() -> None:
    required = [
        "requirements-ots.txt",
        "scripts/record_chain_hashing.py",
        "scripts/append_record_chain_link.py",
        "scripts/verify_record_chain_integrity.py",
        "scripts/build_record_chain_indexes.py",
        "scripts/ots_anchor_record_chain_head.py",
        "scripts/ots_verify_record_chain_anchor.py",
        "scripts/build_ots_arweave_bundle.py",
        "scripts/update_ots_arweave_registry.py",
        "scripts/verify_ots_arweave_registry.py",
        "scripts/test_record_chain_hash_and_ots.py",
        "scripts/test_ots_arweave_registry.py",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    if missing:
        raise SystemExit("missing required files:\n" + "\n".join(missing))


def count_ledger_entries(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def assert_not_phase3_test_payload(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    forbidden_markers = [
        "phase3_test_chain_semantics",
        "Local fixture for hash-chain / index / OTS dry-run coverage only",
        "trinity_phase3_local_fixture_record.v1",
        '"fixture_only": true',
        '"test_only": true',
    ]
    found = [m for m in forbidden_markers if m in text]
    if found:
        raise SystemExit(
            "refusing to append Phase 3 test/fixture payload to production ledger: "
            + ", ".join(found)
        )


def verify_prod_ledger(
    *,
    ledger: Path,
    head: Path,
    base_dir: Path,
    verify_payload_files: bool,
    report_out: Path,
) -> None:
    cmd = [
        sys.executable,
        "scripts/verify_record_chain_integrity.py",
        "--ledger",
        str(ledger),
        "--head",
        str(head),
        "--base-dir",
        str(base_dir),
        "--write-report",
        str(report_out),
    ]
    if verify_payload_files:
        cmd.append("--verify-payload-files")
    run_cmd(cmd)


def build_prod_indexes(
    *,
    ledger: Path,
    api_dir: Path,
    base_dir: Path,
    verify_payload_files: bool,
) -> None:
    cmd = [
        sys.executable,
        "scripts/build_record_chain_indexes.py",
        "--ledger",
        str(ledger),
        "--out-dir",
        str(api_dir),
        "--base-dir",
        str(base_dir),
    ]
    if verify_payload_files:
        cmd.append("--verify-payload-files")
    run_cmd(cmd)


def append_prod_record(
    *,
    ledger: Path,
    head: Path,
    record_file: Path,
    record_type: str,
    record_id: str,
    receipt_id: str | None,
    source_run_id: str,
    finalized_by: str,
    allow_genesis: bool,
    verify_payload_files: bool,
) -> None:
    assert_not_phase3_test_payload(record_file)

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
        record_id,
        "--source-run-id",
        source_run_id,
        "--finalized-by",
        finalized_by,
    ]
    if receipt_id:
        cmd += ["--receipt-id", receipt_id]
    if allow_genesis:
        cmd.append("--allow-genesis")
    if verify_payload_files:
        cmd.append("--verify-payload-files")

    run_cmd(cmd)


def resolve_anchor_file(latest: dict[str, Any]) -> Path:
    anchor_file = Path(latest["latest_anchor_file"])
    if not anchor_file.is_absolute():
        candidate = ROOT / anchor_file
        if candidate.exists():
            return candidate
    if anchor_file.exists():
        return anchor_file
    raise SystemExit(f"anchor file not found: {latest['latest_anchor_file']}")


def ots_dry_run_anchor(
    *,
    ledger: Path,
    head: Path,
    out_dir: Path,
    api_out: Path,
    base_dir: Path,
    verify_payload_files: bool,
) -> Path:
    cmd = [
        sys.executable,
        "scripts/ots_anchor_record_chain_head.py",
        "--ledger",
        str(ledger),
        "--head",
        str(head),
        "--out-dir",
        str(out_dir),
        "--api-out",
        str(api_out),
        "--mode",
        "dry-run",
        "--verify-ledger",
        "--base-dir",
        str(base_dir),
        "--overwrite",
    ]
    if verify_payload_files:
        cmd.append("--verify-payload-files")
    run_cmd(cmd)

    latest = read_json(api_out)
    anchor_file = resolve_anchor_file(latest)

    run_cmd(
        [
            sys.executable,
            "scripts/ots_verify_record_chain_anchor.py",
            "--anchor-file",
            str(anchor_file),
            "--allow-dry-run",
        ]
    )
    return anchor_file


def ots_real_stamp(
    *,
    ledger: Path,
    head: Path,
    out_dir: Path,
    api_out: Path,
    base_dir: Path,
    verify_payload_files: bool,
    ots_bin: str,
    confirmation: str,
) -> Path:
    if confirmation != REAL_OTS_CONFIRMATION:
        raise SystemExit(
            f"real OTS stamp requires --confirm-real-ots-stamp {REAL_OTS_CONFIRMATION!r}"
        )
    if not shutil.which(ots_bin):
        raise SystemExit(
            f"OTS CLI not found: {ots_bin}. Install with: python3 -m pip install -r requirements-ots.txt"
        )

    cmd = [
        sys.executable,
        "scripts/ots_anchor_record_chain_head.py",
        "--ledger",
        str(ledger),
        "--head",
        str(head),
        "--out-dir",
        str(out_dir),
        "--api-out",
        str(api_out),
        "--mode",
        "stamp",
        "--verify-ledger",
        "--base-dir",
        str(base_dir),
    ]
    if verify_payload_files:
        cmd.append("--verify-payload-files")
    run_cmd(cmd)

    latest = read_json(api_out)
    anchor_file = resolve_anchor_file(latest)
    anchor = read_json(anchor_file)
    ots_file = anchor.get("ots_file")
    if not ots_file or not Path(ots_file).exists():
        raise SystemExit(f"real OTS stamp did not produce .ots file: {ots_file}")

    # Non-strict verification allows pending.
    run_cmd(
        [
            sys.executable,
            "scripts/ots_verify_record_chain_anchor.py",
            "--anchor-file",
            str(anchor_file),
            "--upgrade",
            "--write-updated-anchor",
        ]
    )
    return anchor_file


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 4 production Record-Chain verify/append + OTS stamp runner. No Arweave upload."
    )
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--log-dir", default=None)
    parser.add_argument("--ledger", default="record-chain/hash-chain/main.chain.jsonl")
    parser.add_argument("--api-dir", default="api")
    parser.add_argument("--ots-out-dir", default="record-chain/ots/anchors")
    parser.add_argument("--base-dir", default=".")
    parser.add_argument("--verify-payload-files", action="store_true")
    parser.add_argument("--precheck-only", action="store_true")

    parser.add_argument("--record-file", default=None)
    parser.add_argument("--record-type", default=None)
    parser.add_argument("--record-id", default=None)
    parser.add_argument("--receipt-id", default=None)
    parser.add_argument("--finalized-by", default="record-chain-operator")
    parser.add_argument("--allow-genesis", action="store_true")
    parser.add_argument("--enable-production-append", action="store_true")
    parser.add_argument("--confirm-production-append", default="")

    parser.add_argument("--enable-real-ots-stamp", action="store_true")
    parser.add_argument("--confirm-real-ots-stamp", default="")
    parser.add_argument("--ots-bin", default="ots")

    args = parser.parse_args()

    assert_no_arweave_write_environment()
    precheck_required_files()

    run_id = args.run_id
    log_dir = Path(args.log_dir) if args.log_dir else ROOT / "record-chain" / "audit" / "phase4" / run_id
    log_dir.mkdir(parents=True, exist_ok=True)

    ledger = ROOT / args.ledger if not Path(args.ledger).is_absolute() else Path(args.ledger)
    api_dir = ROOT / args.api_dir if not Path(args.api_dir).is_absolute() else Path(args.api_dir)
    head = api_dir / "record-chain-head.json"
    ots_out_dir = ROOT / args.ots_out_dir if not Path(args.ots_out_dir).is_absolute() else Path(args.ots_out_dir)
    ots_latest = api_dir / "record-chain-ots-latest.json"
    base_dir = ROOT / args.base_dir if not Path(args.base_dir).is_absolute() else Path(args.base_dir)

    run_config = {
        "schema": "trinity_phase4_production_chain_ots_run_config.v1",
        "run_id": run_id,
        "log_dir": str(log_dir),
        "ledger": str(ledger),
        "head": str(head),
        "ots_out_dir": str(ots_out_dir),
        "verify_payload_files": args.verify_payload_files,
        "precheck_only": args.precheck_only,
        "enable_production_append": args.enable_production_append,
        "enable_real_ots_stamp": args.enable_real_ots_stamp,
        "arweave_upload_mode": os.environ.get("ARWEAVE_UPLOAD_MODE", "unset"),
        "allow_paid_arweave_canary": os.environ.get("ALLOW_PAID_ARWEAVE_CANARY", "unset"),
        "arweave_jwk_path_set": bool(os.environ.get("ARWEAVE_JWK_PATH")),
        "created_at": utc_now(),
    }
    write_json(log_dir / "00-run-config.json", run_config)

    print("[PHASE4] run_id:", run_id)
    print("[PHASE4] log_dir:", log_dir)

    # Source tests must still pass.
    run_cmd([sys.executable, "scripts/test_record_chain_hash_and_ots.py"])
    run_cmd([sys.executable, "scripts/test_ots_arweave_registry.py"])

    before_entries = count_ledger_entries(ledger)
    before_head_sha = sha256_bytes(head.read_bytes()) if head.exists() else None

    if args.precheck_only:
        summary = {
            "schema": "trinity_phase4_production_chain_ots_summary.v1",
            "run_id": run_id,
            "result": "pass",
            "mode": "precheck_only",
            "production_entries_before": before_entries,
            "production_append_performed": False,
            "real_ots_stamp_performed": False,
            "arweave_upload_performed": False,
            "generated_at": utc_now(),
        }
        write_json(log_dir / "99-phase4-summary.json", summary)
        print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
        return 0

    append_performed = False

    if args.enable_production_append:
        if args.confirm_production_append != PROD_APPEND_CONFIRMATION:
            raise SystemExit(
                f"production append requires --confirm-production-append {PROD_APPEND_CONFIRMATION!r}"
            )
        if not args.record_file or not args.record_type or not args.record_id:
            raise SystemExit(
                "--enable-production-append requires --record-file, --record-type, and --record-id"
            )

        record_file = Path(args.record_file)
        if not record_file.is_absolute():
            record_file = ROOT / record_file
        if not record_file.exists():
            raise SystemExit(f"record file not found: {record_file}")

        if before_entries == 0 and not args.allow_genesis:
            raise SystemExit("production ledger is empty; genesis append requires --allow-genesis")

        append_prod_record(
            ledger=ledger,
            head=head,
            record_file=record_file,
            record_type=args.record_type,
            record_id=args.record_id,
            receipt_id=args.receipt_id,
            source_run_id=run_id,
            finalized_by=args.finalized_by,
            allow_genesis=args.allow_genesis,
            verify_payload_files=args.verify_payload_files,
        )
        append_performed = True

    after_entries = count_ledger_entries(ledger)
    if after_entries == 0:
        raise SystemExit(
            "production ledger has zero entries. Provide --enable-production-append with an operator-approved record."
        )

    verify_prod_ledger(
        ledger=ledger,
        head=head,
        base_dir=base_dir,
        verify_payload_files=args.verify_payload_files,
        report_out=log_dir / "01-production-ledger-integrity-report.json",
    )

    build_prod_indexes(
        ledger=ledger,
        api_dir=api_dir,
        base_dir=base_dir,
        verify_payload_files=args.verify_payload_files,
    )

    dry_anchor = ots_dry_run_anchor(
        ledger=ledger,
        head=head,
        out_dir=log_dir / "ots-dry-run",
        api_out=log_dir / "record-chain-ots-latest.dry-run.json",
        base_dir=base_dir,
        verify_payload_files=args.verify_payload_files,
    )

    real_anchor = None
    if args.enable_real_ots_stamp:
        real_anchor = ots_real_stamp(
            ledger=ledger,
            head=head,
            out_dir=ots_out_dir,
            api_out=ots_latest,
            base_dir=base_dir,
            verify_payload_files=args.verify_payload_files,
            ots_bin=args.ots_bin,
            confirmation=args.confirm_real_ots_stamp,
        )

    after_head_sha = sha256_bytes(head.read_bytes()) if head.exists() else None

    summary = {
        "schema": "trinity_phase4_production_chain_ots_summary.v1",
        "run_id": run_id,
        "result": "pass",
        "production_entries_before": before_entries,
        "production_entries_after": after_entries,
        "production_append_performed": append_performed,
        "production_head_before_sha256": before_head_sha,
        "production_head_after_sha256": after_head_sha,
        "production_ledger": str(ledger),
        "production_head": str(head),
        "ots_dry_run_anchor": str(dry_anchor),
        "real_ots_stamp_performed": bool(real_anchor),
        "real_ots_anchor": str(real_anchor) if real_anchor else None,
        "arweave_upload_performed": False,
        "ots_arweave_registry_updated": False,
        "next_phase_allowed": bool(real_anchor),
        "generated_at": utc_now(),
    }
    write_json(log_dir / "99-phase4-summary.json", summary)
    print("[PHASE4 COMPLETE]")
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
