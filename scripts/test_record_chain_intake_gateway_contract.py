#!/usr/bin/env python3
"""Test: Record-Chain Intake Gateway contract compliance."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    errors = []

    # Test 1: Gateway contract exists
    gw_path = ROOT / "api" / "record-chain-intake-gateway.v1.json"
    if not gw_path.exists():
        errors.append("api/record-chain-intake-gateway.v1.json: NOT FOUND")
    else:
        gw = json.loads(gw_path.read_text())
        if gw.get("schema") != "trinityaccord.record-chain-intake-gateway.v1":
            errors.append(f"wrong schema: {gw.get('schema')}")
        if gw.get("status") != "active_public_submission_interface":
            errors.append(f"wrong status: {gw.get('status')}")
        endpoints = gw.get("endpoints", {})
        for ep in ["health", "readiness", "preflight", "submit", "receipt"]:
            if ep not in endpoints:
                errors.append(f"missing endpoint: {ep}")
        rules = gw.get("public_submission_rule", {})
        if not rules.get("render_is_only_public_submission_method"):
            errors.append("render_is_only_public_submission_method not true")
        if not rules.get("external_agents_must_not_clone_repository"):
            errors.append("external_agents_must_not_clone_repository not true")

    # Test 2: Submission schema exists
    sub_path = ROOT / "api" / "record-chain-submission-schema.v1.json"
    if not sub_path.exists():
        errors.append("api/record-chain-submission-schema.v1.json: NOT FOUND")
    else:
        sub = json.loads(sub_path.read_text())
        if "trinityaccord" not in sub.get("$id", ""):
            errors.append(f"submission schema $id wrong: {sub.get('$id')}")

    # Test 3: Preflight response schema exists
    pr_path = ROOT / "api" / "record-chain-preflight-response.v1.json"
    if not pr_path.exists():
        errors.append("api/record-chain-preflight-response.v1.json: NOT FOUND")

    # Test 4: Submit response schema exists
    sr_path = ROOT / "api" / "record-chain-submit-response.v1.json"
    if not sr_path.exists():
        errors.append("api/record-chain-submit-response.v1.json: NOT FOUND")

    # Test 5: Builder bundles exist and match
    bb_path = ROOT / "api" / "record-chain-builder-bundles.v1.json"
    if not bb_path.exists():
        errors.append("api/record-chain-builder-bundles.v1.json: NOT FOUND")
    else:
        bb = json.loads(bb_path.read_text())
        if not bb.get("public_submission_rule", {}).get("render_is_only_public_submission_method"):
            errors.append("builder bundles: render_is_only not true")

    # Test 6: record-chain-status.json has public_submission
    status_path = ROOT / "api" / "record-chain-status.json"
    if status_path.exists():
        status = json.loads(status_path.read_text())
        if "public_submission" not in status:
            errors.append("record-chain-status.json: missing public_submission field")

    # Test 7: receipt_id pattern is correct
    if gw_path.exists():
        gw = json.loads(gw_path.read_text())
        receipt_ep = gw.get("endpoints", {}).get("receipt", {})
        receipt_params = receipt_ep.get("path_parameters", {}).get("receipt_id", {})
        pattern = receipt_params.get("pattern", "")
        if pattern != "^rcg-[0-9]{8}-[a-f0-9]{12}$":
            errors.append(f"receipt_id pattern wrong: {pattern}")

    # Test 8: public_phase exists
    if gw_path.exists():
        gw = json.loads(gw_path.read_text())
        pp = gw.get("public_phase", {})
        if pp.get("status") != "public_test_stabilization":
            errors.append("public_phase.status not public_test_stabilization")
        if not pp.get("receipt_is_not_final_inclusion"):
            errors.append("receipt_is_not_final_inclusion not true")

    if errors:
        print("FAIL: Contract test errors:\n")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("PASS: All Record-Chain Intake Gateway contract tests passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
