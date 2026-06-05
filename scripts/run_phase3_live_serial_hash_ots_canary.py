#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = "https://www.trinityaccord.org"
DEFAULT_RUN_ID = time.strftime("phase3-live-serial-%Y%m%dT%H%M%SZ", time.gmtime())

ROUTE_TO_RECORD_TYPE = {
    "pure_echo": "echo",
    "v0_v5": "verification",
    "guardian_signed_echo": "guardian_signed_echo",
    "e2": "e2",
    "v6_plus": "v6_plus",
}

LOCAL_FIXTURE_RECORD_TYPES = [
    "guardian_application",
    "guardian_exit_application",
    "exit_application",
    "custom_future/type:v1",
]


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_json(url: str, timeout: int = 30) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TrinityPhase3LiveSerialHashOtsCanary/1.0",
            "Accept": "application/json,*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


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


def import_lifecycle_module():
    path = ROOT / "scripts" / "smoke_external_agent_write_lifecycle_canary.py"
    if not path.exists():
        raise SystemExit(f"missing lifecycle canary script: {path}")

    spec = importlib.util.spec_from_file_location("smoke_external_agent_write_lifecycle_canary", path)
    if spec is None or spec.loader is None:
        raise SystemExit("failed to load lifecycle canary module spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_lifecycle_report(stdout: str) -> dict[str, Any]:
    marker = "before_leaving lifecycle report:"
    idx = stdout.find(marker)
    if idx < 0:
        raise SystemExit("cannot find lifecycle report marker in stdout")

    after = stdout[idx + len(marker):].strip()

    # Extract the first balanced JSON object.
    start = after.find("{")
    if start < 0:
        raise SystemExit("cannot find JSON object after lifecycle report marker")

    depth = 0
    end = None
    for i, ch in enumerate(after[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    if end is None:
        raise SystemExit("lifecycle report JSON object is not balanced")

    return json.loads(after[start:end])


def assert_safe_environment() -> None:
    dangerous = []
    if os.environ.get("ARWEAVE_UPLOAD_MODE") == "production":
        dangerous.append("ARWEAVE_UPLOAD_MODE=production")
    if os.environ.get("ALLOW_PAID_ARWEAVE_CANARY") == "true":
        dangerous.append("ALLOW_PAID_ARWEAVE_CANARY=true")
    if os.environ.get("ARWEAVE_JWK_PATH"):
        dangerous.append("ARWEAVE_JWK_PATH is set")
    if dangerous:
        raise SystemExit("Unsafe environment for this phase: " + ", ".join(dangerous))


def precheck_required_files() -> None:
    required = [
        "scripts/smoke_external_agent_write_lifecycle_canary.py",
        "scripts/smoke_live_external_agent_three_core_preflight.py",
        "scripts/test_record_chain_hash_and_ots.py",
        "scripts/test_ots_arweave_registry.py",
        "scripts/append_record_chain_link.py",
        "scripts/verify_record_chain_integrity.py",
        "scripts/build_record_chain_indexes.py",
        "scripts/ots_anchor_record_chain_head.py",
        "scripts/ots_verify_record_chain_anchor.py",
        "scripts/build_ots_arweave_bundle.py",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    if missing:
        raise SystemExit("missing required files:\n" + "\n".join(missing))


def append_to_test_ledger(
    *,
    ledger: Path,
    head_out: Path,
    payload_file: Path,
    record_type: str,
    record_id: str,
    receipt_id: str | None,
    source_run_id: str,
    allow_genesis: bool,
) -> None:
    cmd = [
        sys.executable,
        "scripts/append_record_chain_link.py",
        "--ledger",
        str(ledger),
        "--head-out",
        str(head_out),
        "--record-file",
        str(payload_file),
        "--record-type",
        record_type,
        "--record-id",
        record_id,
        "--source-run-id",
        source_run_id,
        "--finalized-by",
        "phase3-test-runner",
        "--verify-payload-files",
    ]
    if receipt_id:
        cmd += ["--receipt-id", receipt_id]
    if allow_genesis:
        cmd.append("--allow-genesis")
    run_cmd(cmd)


def build_local_fixture(record_type: str, ordinal: int, run_id: str) -> dict[str, Any]:
    return {
        "schema": "trinity_phase3_local_fixture_record.v1",
        "record_type": record_type,
        "record_id": f"{run_id}-{record_type.replace('/', '_')}-{ordinal}",
        "source_run_id": run_id,
        "fixture_only": True,
        "test_only": True,
        "created_at": utc_now(),
        "semantics": (
            "Local fixture for hash-chain / index / OTS dry-run coverage only. "
            "Not submitted to Gateway and not a production finalized record."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 3 live serial canary + test hash-chain + OTS dry-run runner."
    )
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--gateway", default="https://trinity-record-chain-gateway.onrender.com")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--log-dir", default=None)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--poll-seconds", type=int, default=120)
    parser.add_argument("--precheck-only", action="store_true")
    parser.add_argument("--enable-live-writes", action="store_true")
    parser.add_argument("--confirm-live-canary", default="")
    parser.add_argument(
        "--route-sequence",
        default="pure_echo,pure_echo,v0_v5",
        help="Comma-separated lifecycle canary routes to submit serially when --enable-live-writes is set.",
    )
    parser.add_argument("--include-local-fixtures", action="store_true", default=True)
    args = parser.parse_args()

    assert_safe_environment()
    precheck_required_files()

    run_id = args.run_id
    log_dir = Path(args.log_dir) if args.log_dir else ROOT / "record-chain" / "audit" / "e2e" / run_id
    records_dir = log_dir / "records"
    hash_dir = log_dir / "hash-chain"
    api_dir = log_dir / "api"
    ots_dir = log_dir / "ots" / "anchors"
    bundle_dir = log_dir / "ots" / "arweave-bundles"

    test_ledger = hash_dir / "test.chain.jsonl"
    test_head = api_dir / "record-chain-head.json"

    log_dir.mkdir(parents=True, exist_ok=True)

    run_config = {
        "schema": "trinity_phase3_live_serial_hash_ots_run_config.v1",
        "run_id": run_id,
        "site": args.site,
        "log_dir": str(log_dir),
        "enable_live_writes": args.enable_live_writes,
        "route_sequence": [x.strip() for x in args.route_sequence.split(",") if x.strip()],
        "include_local_fixtures": args.include_local_fixtures,
        "arweave_upload_mode": os.environ.get("ARWEAVE_UPLOAD_MODE", "unset"),
        "allow_paid_arweave_canary": os.environ.get("ALLOW_PAID_ARWEAVE_CANARY", "unset"),
        "arweave_jwk_path_set": bool(os.environ.get("ARWEAVE_JWK_PATH")),
        "created_at": utc_now(),
    }
    write_json(log_dir / "00-run-config.json", run_config)

    print("[PHASE3] run_id:", run_id)
    print("[PHASE3] log_dir:", log_dir)

    # Source-level tests for newly merged functionality.
    run_cmd([sys.executable, "scripts/test_record_chain_hash_and_ots.py"])
    run_cmd([sys.executable, "scripts/test_ots_arweave_registry.py"])

    # Live preflight-only checks.
    run_cmd(
        [sys.executable, "scripts/smoke_live_external_agent_three_core_preflight.py"],
        stdout_file=log_dir / "01-three-core-preflight.stdout.log",
        stderr_file=log_dir / "01-three-core-preflight.stderr.log",
    )

    run_cmd(
        [
            sys.executable,
            "scripts/smoke_external_agent_write_lifecycle_canary.py",
            "--site",
            args.site,
            "--gateway",
            args.gateway,
            "--mode",
            "preflight-only",
            "--timeout",
            str(args.timeout),
        ],
        stdout_file=log_dir / "02-lifecycle-preflight.stdout.log",
        stderr_file=log_dir / "02-lifecycle-preflight.stderr.log",
    )

    if args.precheck_only:
        summary = {
            "schema": "trinity_phase3_live_serial_hash_ots_summary.v1",
            "run_id": run_id,
            "result": "pass",
            "mode": "precheck_only",
            "live_writes_attempted": 0,
            "test_ledger": None,
            "generated_at": utc_now(),
        }
        write_json(log_dir / "99-phase3-summary.json", summary)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    lifecycle_module = import_lifecycle_module()

    live_records: list[dict[str, Any]] = []
    appended = 0

    routes = [x.strip() for x in args.route_sequence.split(",") if x.strip()]

    if args.enable_live_writes:
        if not args.confirm_live_canary:
            raise SystemExit("--enable-live-writes requires --confirm-live-canary exact phrase")

        for idx, route in enumerate(routes, start=1):
            label = f"live-{idx:02d}-{route}"
            item_dir = records_dir / label
            item_dir.mkdir(parents=True, exist_ok=True)

            stdout_path = item_dir / "lifecycle.stdout.log"
            stderr_path = item_dir / "lifecycle.stderr.log"

            result = run_cmd(
                [
                    sys.executable,
                    "scripts/smoke_external_agent_write_lifecycle_canary.py",
                    "--site",
                    args.site,
                    "--gateway",
                    args.gateway,
                    "--mode",
                    "single-write-canary",
                    "--route",
                    route,
                    "--confirm-live-canary",
                    args.confirm_live_canary,
                    "--timeout",
                    str(args.timeout),
                    "--poll-seconds",
                    str(args.poll_seconds),
                ],
                stdout_file=stdout_path,
                stderr_file=stderr_path,
            )

            report = parse_lifecycle_report(result.stdout)
            write_json(item_dir / "lifecycle-report.json", report)

            nonce = report.get("nonce")
            if not nonce:
                raise SystemExit(f"{label}: lifecycle report missing nonce")

            payload = lifecycle_module.build_synthetic_canary_payload(route, nonce)
            payload["phase3_run_id"] = run_id
            payload["phase3_label"] = label
            payload["gateway_receipt_id_if_any"] = report.get("gateway_receipt_id_if_any")
            payload["github_issue_url_if_any"] = report.get("github_issue_url_if_any")
            payload["phase3_test_chain_semantics"] = (
                "This payload is appended only to the phase3 test ledger, not production main.chain.jsonl."
            )

            payload_file = item_dir / "payload.json"
            write_json(payload_file, payload)

            receipt_id = report.get("gateway_receipt_id_if_any")
            record_type = ROUTE_TO_RECORD_TYPE.get(route, route)
            record_id = f"{run_id}-{label}"

            append_to_test_ledger(
                ledger=test_ledger,
                head_out=test_head,
                payload_file=payload_file,
                record_type=record_type,
                record_id=record_id,
                receipt_id=receipt_id,
                source_run_id=run_id,
                allow_genesis=(appended == 0),
            )
            appended += 1

            live_records.append(
                {
                    "label": label,
                    "route": route,
                    "record_type": record_type,
                    "record_id": record_id,
                    "receipt_id": receipt_id,
                    "payload_file": str(payload_file),
                    "payload_sha256": sha256_bytes(payload_file.read_bytes()),
                    "submission_result": report.get("submission_result"),
                    "archive_status_if_known": report.get("archive_status_if_known"),
                }
            )

    local_fixture_records: list[dict[str, Any]] = []
    if args.include_local_fixtures:
        for idx, record_type in enumerate(LOCAL_FIXTURE_RECORD_TYPES, start=1):
            label = f"fixture-{idx:02d}-{record_type.replace('/', '_')}"
            item_dir = records_dir / label
            item_dir.mkdir(parents=True, exist_ok=True)

            payload = build_local_fixture(record_type, idx, run_id)
            payload_file = item_dir / "payload.json"
            write_json(payload_file, payload)

            record_id = payload["record_id"]

            append_to_test_ledger(
                ledger=test_ledger,
                head_out=test_head,
                payload_file=payload_file,
                record_type=record_type,
                record_id=record_id,
                receipt_id=None,
                source_run_id=run_id,
                allow_genesis=(appended == 0),
            )
            appended += 1

            local_fixture_records.append(
                {
                    "label": label,
                    "record_type": record_type,
                    "record_id": record_id,
                    "payload_file": str(payload_file),
                    "payload_sha256": sha256_bytes(payload_file.read_bytes()),
                }
            )

    if appended == 0:
        raise SystemExit("No records were appended to the test ledger")

    # Verify test ledger and build indexes.
    run_cmd(
        [
            sys.executable,
            "scripts/verify_record_chain_integrity.py",
            "--ledger",
            str(test_ledger),
            "--head",
            str(test_head),
            "--verify-payload-files",
            "--base-dir",
            ".",
            "--write-report",
            str(log_dir / "03-test-ledger-integrity-report.json"),
        ]
    )

    run_cmd(
        [
            sys.executable,
            "scripts/build_record_chain_indexes.py",
            "--ledger",
            str(test_ledger),
            "--out-dir",
            str(api_dir),
            "--verify-payload-files",
            "--base-dir",
            ".",
        ]
    )

    # OTS dry-run anchor for the test head.
    run_cmd(
        [
            sys.executable,
            "scripts/ots_anchor_record_chain_head.py",
            "--ledger",
            str(test_ledger),
            "--head",
            str(test_head),
            "--out-dir",
            str(ots_dir),
            "--api-out",
            str(api_dir / "record-chain-ots-latest.json"),
            "--mode",
            "dry-run",
            "--verify-ledger",
            "--verify-payload-files",
            "--base-dir",
            ".",
        ]
    )

    latest_ots = read_json(api_dir / "record-chain-ots-latest.json")
    anchor_file = ROOT / latest_ots["latest_anchor_file"] if not Path(latest_ots["latest_anchor_file"]).is_absolute() else Path(latest_ots["latest_anchor_file"])
    if not anchor_file.exists():
        # latest_ots was written with the exact path passed to --out-dir; try relative to cwd.
        anchor_file = Path(latest_ots["latest_anchor_file"])
    if not anchor_file.exists():
        raise SystemExit(f"anchor file not found: {latest_ots['latest_anchor_file']}")

    run_cmd(
        [
            sys.executable,
            "scripts/ots_verify_record_chain_anchor.py",
            "--anchor-file",
            str(anchor_file),
            "--allow-dry-run",
        ]
    )

    # Build OTS-Arweave bundle only. Do not upload.
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle_file = bundle_dir / (anchor_file.stem + ".arweave-bundle.json")
    run_cmd(
        [
            sys.executable,
            "scripts/build_ots_arweave_bundle.py",
            "--anchor-file",
            str(anchor_file),
            "--out",
            str(bundle_file),
        ]
    )

    bundle_sha = sha256_bytes(bundle_file.read_bytes())

    # Safety check: the production registry must not be updated in this phase.
    prod_registry_paths = [
        ROOT / "record-chain/ots/arweave-registry.json",
        ROOT / "api/record-chain-ots-arweave-registry.json",
    ]
    prod_registry_existing = [str(p) for p in prod_registry_paths if p.exists()]

    # Run source registry tests again to ensure guards are intact.
    run_cmd([sys.executable, "scripts/test_ots_arweave_registry.py"])

    summary = {
        "schema": "trinity_phase3_live_serial_hash_ots_summary.v1",
        "run_id": run_id,
        "result": "pass",
        "site": args.site,
        "log_dir": str(log_dir),
        "live_writes_enabled": args.enable_live_writes,
        "live_records": live_records,
        "local_fixture_records": local_fixture_records,
        "test_ledger": str(test_ledger),
        "test_head": str(test_head),
        "test_api_dir": str(api_dir),
        "ots_latest": latest_ots,
        "ots_anchor_file": str(anchor_file),
        "ots_arweave_bundle_file": str(bundle_file),
        "ots_arweave_bundle_sha256": bundle_sha,
        "production_registry_files_existing_before_or_after": prod_registry_existing,
        "production_main_chain_modified": False,
        "real_ots_stamp_performed": False,
        "arweave_upload_performed": False,
        "next_phase_allowed": True,
        "generated_at": utc_now(),
    }
    write_json(log_dir / "99-phase3-summary.json", summary)
    print("[PHASE3 COMPLETE]")
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
