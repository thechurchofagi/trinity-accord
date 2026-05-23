#!/usr/bin/env python3
"""Test that gateway-workflows.v1.json and gateway-artifact-custody.v1.json are valid."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    # Test gateway-workflows.v1.json
    workflows = json.loads((ROOT / "api" / "gateway-workflows.v1.json").read_text(encoding="utf-8"))
    assert workflows["schema"] == "trinityaccord.gateway-workflows.v1"
    assert workflows["canonical_human_url"] == "/gateway-workflows/"
    assert workflows["canonical_machine_url"] == "/api/gateway-workflows.v1.json"
    assert workflows["artifact_custody_url"] == "/api/gateway-artifact-custody.v1.json"
    assert "workflow_steps" in workflows
    assert len(workflows["workflow_steps"]) == 5
    assert workflows["workflow_steps"][0]["name"] == "route_selection"
    assert workflows["workflow_steps"][1]["name"] == "payload_generation"
    assert workflows["workflow_steps"][2]["name"] == "preflight_validation"
    assert workflows["workflow_steps"][3]["name"] == "submission"
    assert workflows["workflow_steps"][4]["name"] == "error_recovery"

    routes = workflows["routes"]
    assert "pure_echo" in routes
    assert "v0_v5_agent_declared_archive" in routes
    assert "guardian_application_stage_1" in routes
    assert "guardian_listing_stage_2" in routes
    assert "guardian_signed_echo" in routes

    error_codes = workflows["error_codes"]
    assert "READBACK_SHA256_MISSING" in error_codes
    assert "WRONG_BUILDER_FOR_ROUTE" in error_codes
    assert "FORBIDDEN_ARCHIVE_CLAIMS" in error_codes

    # Test gateway-artifact-custody.v1.json
    custody = json.loads((ROOT / "api" / "gateway-artifact-custody.v1.json").read_text(encoding="utf-8"))
    assert custody["schema"] == "trinityaccord.gateway-artifact-custody.v1"
    assert custody["workflow_manual_url"] == "/gateway-workflows/"
    assert custody["workflow_manual_machine_url"] == "/api/gateway-workflows.v1.json"
    assert "custody_artifacts" in custody
    assert len(custody["custody_artifacts"]) >= 5
    assert "not_in_custody" in custody

    artifact_names = [a["artifact"] for a in custody["custody_artifacts"]]
    assert "raw_agent_payload" in artifact_names
    assert "rendered_issue_body" in artifact_names
    assert "gateway_receipt_id" in artifact_names
    assert "authorship_proof" in artifact_names
    assert "readback_sha256" in artifact_names

    not_in_custody_names = [a["artifact"] for a in custody["not_in_custody"]]
    assert "private_keys" in not_in_custody_names
    assert "signing_keys" in not_in_custody_names

    # Test agent-start.v1.json has new workflow fields
    agent_start = json.loads((ROOT / "api" / "agent-start.v1.json").read_text(encoding="utf-8"))
    assert "workflow_manual_url" in agent_start
    assert agent_start["workflow_manual_url"] == "/gateway-workflows/"
    assert "workflow_manual_machine_url" in agent_start
    assert agent_start["workflow_manual_machine_url"] == "/api/gateway-workflows.v1.json"
    assert "artifact_custody_url" in agent_start
    assert agent_start["artifact_custody_url"] == "/api/gateway-artifact-custody.v1.json"

    # Test agent-submit-gateway.json has workflow URLs
    submit_gw = json.loads((ROOT / "api" / "agent-submit-gateway.json").read_text(encoding="utf-8"))
    assert "workflow_manual_url" in submit_gw
    assert "workflow_manual_machine_url" in submit_gw

    # Test agent-first-contact.json has workflow URLs in gateway_submission_origin
    first_contact = json.loads((ROOT / "api" / "agent-first-contact.json").read_text(encoding="utf-8"))
    gso = first_contact["gateway_submission_origin"]
    assert "workflow_manual_url" in gso
    assert "workflow_manual_machine_url" in gso

    print("PASS: test_gateway_workflow_api")

if __name__ == "__main__":
    main()
