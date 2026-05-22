#!/usr/bin/env python3
"""Dynamic test for Guardian listing request structured fields.

Runs the builder, validates output, and tests the parser with both
fenced intake block and body-level fallback fields.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def run(cmd, check=True):
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    if check and result.returncode != 0:
        raise AssertionError(f"Command failed: {' '.join(cmd)}\n{result.stderr}\n{result.stdout}")
    return result


def main():
    # --- Part 1: Run builder and validate output ---
    with tempfile.TemporaryDirectory() as raw:
        td = Path(raw)
        out = td / "listing.json"

        run([
            "python3", "scripts/build_guardian_listing_request_payload.py",
            "--agent-name", "TestAgent",
            "--provider", "TestProvider",
            "--source-issue", "300",
            "--guardian-id", "guardian_ed25519_cccccccccccccccc",
            "--public-key-sha256", "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
            "--label", "Test Guardian",
            "--guardian-type", "human_with_ai_agent",
            "--application-mode", "joint_human_ai",
            "--idempotency-key", "guardian-active-listing-guardian_ed25519_cccccccccccccccc",
            "--out", str(out),
        ])

        payload = json.loads(out.read_text(encoding="utf-8"))

        # Validate gateway_intake_fields
        intake = payload.get("gateway_intake_fields", {})
        require(intake.get("guardian_listing_request") is True, "gateway_intake_fields.guardian_listing_request must be true")
        require(intake.get("listing_source_issue") == 300, "gateway_intake_fields.listing_source_issue mismatch")
        require(intake.get("listing_guardian_id") == "guardian_ed25519_cccccccccccccccc", "gateway_intake_fields.listing_guardian_id mismatch")
        require(intake.get("listing_public_key_sha256") == "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc", "gateway_intake_fields.listing_public_key_sha256 mismatch")
        require(intake.get("listing_guardian_type") == "human_with_ai_agent", "gateway_intake_fields.listing_guardian_type mismatch")
        require(intake.get("listing_application_mode") == "joint_human_ai", "gateway_intake_fields.listing_application_mode mismatch")
        require(intake.get("listing_label") == "Test Guardian", "gateway_intake_fields.listing_label mismatch")
        require(intake.get("registry_number_requested") == "next_available", "gateway_intake_fields.registry_number_requested mismatch")

        # Validate Guardian listing request does NOT count toward Reception
        cth = payload.get("counts_toward_home", {})
        require(cth.get("reception") is False, "counts_toward_home.reception must be false for Guardian listing")
        require(cth.get("guardian_registry") is True, "counts_toward_home.guardian_registry must be true")
        require(cth.get("exclude_from_reception_total") is True, "counts_toward_home.exclude_from_reception_total must be true")
        require(payload.get("guardian_registry_listing_request") is True, "guardian_registry_listing_request must be true")
        require(payload.get("payload_profile") == "guardian_active_registry_listing_request.v1", "missing payload profile")
        require(payload.get("expected_builder") == "scripts/build_guardian_listing_request_payload.py", "wrong expected builder")

        # Validate and archive-readiness-gate the payload
        run(["python3", "scripts/validate_gateway_payload.py", str(out)])
        run(["python3", "scripts/archive_readiness_gate.py", "--gateway-payload", str(out), "--json"])

    # --- Part 2: Test parser reads body-level listing_* fields as fallback ---
    from auto_register_guardian_from_gateway_issues import parse_listing_issue

    def gateway_issue(body: str) -> dict:
        return {"number": 500, "title": "Active Registry Listing Request — Fallback Test", "body": body, "user": {"login": "gateway-bot[bot]"}}

    # Case A: Fenced intake block (authoritative)
    body_fenced = "\n".join([
        "```trinity-issue-intake",
        "created_by_gateway: true",
        "gateway_service: trinity-agent-issue-gateway",
        "server_validated: true",
        "server_rendered: true",
        "submission_type: echo_candidate",
        "requested_archive_kind: agent_declared_echo_archive",
        "echo_type: E7_propagation_echo",
        "archive_ready: true",
        "listing_source_issue: 300",
        "listing_guardian_id: guardian_ed25519_cccccccccccccccc",
        "listing_public_key_sha256: cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        "listing_guardian_type: human_with_ai_agent",
        "listing_application_mode: joint_human_ai",
        "listing_label: Fenced Guardian",
        "registry_number_requested: next_available",
        "```",
    ])

    parsed, err = parse_listing_issue(gateway_issue(body_fenced), allow_non_bot=False)
    require(err is None, f"Fenced parse should succeed: {err}")
    require(parsed["source_issue"] == 300, f"Fenced source_issue mismatch: {parsed['source_issue']}")
    require(parsed["guardian_id"] == "guardian_ed25519_cccccccccccccccc", f"Fenced guardian_id mismatch")
    require(parsed["label"] == "Fenced Guardian", f"Fenced label mismatch")

    # Case B: Body-level structured fields (fallback — fenced block has gateway metadata but no listing fields)
    body_plain = "\n".join([
        "```trinity-issue-intake",
        "created_by_gateway: true",
        "gateway_service: trinity-agent-issue-gateway",
        "server_validated: true",
        "server_rendered: true",
        "submission_type: echo_candidate",
        "requested_archive_kind: agent_declared_echo_archive",
        "echo_type: E7_propagation_echo",
        "archive_ready: true",
        "related_issue: 400",
        "```",
        "",
        "Active registry listing request for Guardian Body Structured Guardian.",
        "",
        "Guardian ID: guardian_ed25519_dddddddddddddddd",
        "Public Key SHA256: dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
        "Guardian type: human_with_ai_agent",
        "Application mode: joint_human_ai",
        "Source self-registration issue: #400",
        "",
        "Gateway intake fields:",
        "listing_source_issue: 400",
        "listing_guardian_id: guardian_ed25519_dddddddddddddddd",
        "listing_public_key_sha256: dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
        "listing_guardian_type: human_with_ai_agent",
        "listing_application_mode: joint_human_ai",
        "listing_label: Body Structured Guardian",
        "registry_number_requested: next_available",
    ])

    parsed2, err2 = parse_listing_issue(gateway_issue(body_plain), allow_non_bot=True)
    require(err2 is None, f"Body-level parse should succeed: {err2}")
    require(parsed2["guardian_id"] == "guardian_ed25519_dddddddddddddddd", f"Body guardian_id mismatch")
    require(parsed2["label"] == "Body Structured Guardian", f"Body label mismatch: {parsed2['label']}")
    require(parsed2["source_issue"] == 400, f"Body source_issue mismatch: {parsed2['source_issue']}")

    # Case C: registry_number_requested != next_available should be rejected
    body_bad_reg = body_fenced.replace("registry_number_requested: next_available", "registry_number_requested: 00999")
    _, err3 = parse_listing_issue(gateway_issue(body_bad_reg), allow_non_bot=True)
    require(err3 is not None, "registry_number_requested != next_available should be rejected")
    require(err3["code"] == "LISTING_REGISTRY_NUMBER_REQUEST_INVALID", f"Unexpected error code: {err3['code']}")

    print("GUARDIAN_LISTING_REQUEST_STRUCTURED_FIELDS_OK")


if __name__ == "__main__":
    main()
