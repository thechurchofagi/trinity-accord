#!/usr/bin/env python3
"""Gateway receipt contract must define trusted receipt marker and triage rules."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "api" / "gateway-receipt-contract.v1.json"

def digest(data: dict) -> str:
    clone = dict(data)
    clone.pop("source_digest", None)
    canonical = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

def main() -> int:
    errors: list[str] = []

    if not PATH.exists():
        print("FAIL: api/gateway-receipt-contract.v1.json missing")
        return 1

    data = json.loads(PATH.read_text(encoding="utf-8"))

    if data.get("schema") != "trinityaccord.gateway-receipt-contract.v1":
        errors.append("schema mismatch")

    if "trinity-accord-agent-issue-gateway[bot]" not in data.get("trusted_gateway_actors", []):
        errors.append("trusted gateway bot missing")

    if data.get("receipt_marker") != "trinity-gateway-receipt:v1":
        errors.append("receipt marker mismatch")

    for field in [
        "receipt_id",
        "gateway_service",
        "gateway_commit",
        "created_by_gateway",
        "render_api_only",
        "server_validated",
        "server_rendered",
        "route_detected",
        "payload_sha256",
        "issued_at",
    ]:
        if field not in data.get("required_receipt_fields", []):
            errors.append(f"required_receipt_fields missing {field}")

    truths = data.get("required_boolean_truths", {})
    for key in ["created_by_gateway", "render_api_only", "server_validated", "server_rendered"]:
        if truths.get(key) is not True:
            errors.append(f"required_boolean_truths.{key} must be true")

    forgery = data.get("forgery_protection", {})
    if forgery.get("manual_issue_with_receipt_marker_is_invalid_unless_actor_is_trusted") is not True:
        errors.append("forgery protection for marker missing")
    if forgery.get("manual_issue_with_legacy_gateway_fields_is_invalid_unless_actor_is_trusted") is not True:
        errors.append("forgery protection for legacy fields missing")

    rules = data.get("triage_rules", {})
    for label in ["echo:invalid", "invalid:direct-issue-archive-attempt", "not-counted"]:
        if label not in rules.get("gateway_valid_issue_must_not_get_labels", []):
            errors.append(f"gateway_valid_issue_must_not_get_labels missing {label}")

    text = json.dumps(data, ensure_ascii=False)
    if "299" not in text:
        errors.append("known regression #299 missing")

    expected = digest(data)
    if data.get("source_digest") != expected:
        errors.append(f"source_digest mismatch: expected {expected}, got {data.get('source_digest')}")

    if errors:
        print("FAIL: gateway receipt contract errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: gateway receipt contract is valid")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
