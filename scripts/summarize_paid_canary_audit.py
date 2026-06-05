#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CURRENT_OWNER = "r1EdzCQ9E7CaAOEywI5netR6EcSopNOa08oi2Coz68s"

def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def mask_address(address: str | None) -> str | None:
    if not address:
        return None
    if len(address) <= 12:
        return "***"
    return f"{address[:6]}...{address[-6:]}"

def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-dir", required=True)
    parser.add_argument("--record-type", default="echo")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    audit_dir = Path(args.audit_dir)
    record_type = args.record_type

    cost_file = audit_dir / f"10-arweave-cost-estimate.{record_type}.json"
    upload_file = audit_dir / f"11-arweave-upload-result.{record_type}.json"
    readback_file = audit_dir / f"11b-arweave-readback-verify.{record_type}.json"
    balance_file = audit_dir / f"11c-arweave-delayed-balance-recheck.{record_type}.json"

    failures: list[str] = []

    cost = load_json(cost_file)
    upload = load_json(upload_file)
    readback = load_json(readback_file)
    delayed_balance = load_json(balance_file) if balance_file.exists() else None

    require(cost.get("decision") == "ALLOW", "cost gate decision is not ALLOW", failures)
    require(float(cost.get("estimated_upload_cost_usd_with_buffer", 999)) <= 0.10, "cost exceeds cap", failures)
    require(cost.get("wallet_address") == CURRENT_OWNER, "cost wallet owner mismatch", failures)
    require(upload.get("wallet_address") == CURRENT_OWNER, "upload wallet owner mismatch", failures)
    require(upload.get("result") == "uploaded", "upload result is not uploaded", failures)
    require(bool(upload.get("tx_id")), "tx_id missing", failures)
    require(bool(upload.get("gateway_url")), "gateway_url missing", failures)
    require(readback.get("result") == "pass", "readback result is not pass", failures)
    require(readback.get("hash_match") is True, "readback hash_match is not true", failures)
    require(readback.get("byte_for_byte_match") is True, "readback byte_for_byte_match is not true", failures)
    require(upload.get("payload_sha256") == readback.get("downloaded_sha256"), "payload sha != downloaded sha", failures)

    summary = {
        "summary_schema": "trinity_paid_echo_canary_summary.v1",
        "run_id": cost.get("run_id") or upload.get("run_id") or readback.get("run_id"),
        "record_type": record_type,
        "result": "pass" if not failures else "fail",
        "failures": failures,
        "wallet_address_masked": mask_address(upload.get("wallet_address")),
        "wallet_owner_verified": upload.get("wallet_address") == CURRENT_OWNER,
        "tx_id": upload.get("tx_id"),
        "gateway_url": upload.get("gateway_url"),
        "payload_bytes": upload.get("payload_bytes"),
        "payload_sha256": upload.get("payload_sha256"),
        "estimated_upload_cost_usd": cost.get("estimated_upload_cost_usd"),
        "estimated_upload_cost_usd_with_buffer": cost.get("estimated_upload_cost_usd_with_buffer"),
        "cost_cap_usd": cost.get("effective_max_upload_usd"),
        "balance_before_ar": upload.get("balance_before_ar"),
        "balance_after_ar": upload.get("balance_after_ar"),
        "actual_delta_ar": upload.get("actual_delta_ar"),
        "delayed_balance_recheck_present": delayed_balance is not None,
        "readback": {
            "result": readback.get("result"),
            "gateway_url": readback.get("gateway_url"),
            "expected_bytes": readback.get("expected_bytes"),
            "downloaded_bytes": readback.get("downloaded_bytes"),
            "expected_sha256": readback.get("expected_sha256"),
            "downloaded_sha256": readback.get("downloaded_sha256"),
            "hash_match": readback.get("hash_match"),
            "byte_for_byte_match": readback.get("byte_for_byte_match"),
            "attempts": readback.get("attempts"),
            "duration_ms": readback.get("duration_ms"),
        },
        "arweave_reset_possible": False,
        "note": "Arweave tx is permanent. Local/index canary cleanup is separate from Arweave permanence.",
    }

    out = Path(args.out) if args.out else audit_dir / "16-paid-echo-canary-summary.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if failures:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
