#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WORKFLOWS = [
    "pure_echo",
    "v0_v5_agent_declared_archive",
    "v6_plus_strict_evidence",
    "e2_verification_echo",
    "guardian_application_stage_1",
    "guardian_listing_stage_2",
    "guardian_signed_echo",
]

EXPECTED_ANCHORS = {
    "pure_echo": "/gateway-workflows/#workflow-pure-echo",
    "v0_v5_agent_declared_archive": "/gateway-workflows/#workflow-v0-v5-agent-declared-archive",
    "v6_plus_strict_evidence": "/gateway-workflows/#workflow-v6-plus-strict-evidence",
    "e2_verification_echo": "/gateway-workflows/#workflow-e2-verification-echo",
    "guardian_application_stage_1": "/gateway-workflows/#workflow-guardian-stage-1-application",
    "guardian_listing_stage_2": "/gateway-workflows/#workflow-guardian-stage-2-listing",
    "guardian_signed_echo": "/gateway-workflows/#workflow-guardian-signed-echo",
}

def main() -> None:
    workflows = json.loads((ROOT / "api" / "gateway-workflows.v1.json").read_text(encoding="utf-8"))
    assert workflows["schema"] == "trinityaccord.gateway-workflows.v1"
    assert workflows["canonical_human_url"] == "/gateway-workflows/"

    assert workflows["artifact_custody_url"] == "/api/gateway-artifact-custody.v1.json"

    for wid in WORKFLOWS:
        assert wid in workflows["workflows"], wid
        assert workflows["workflows"][wid]["human_anchor"] == EXPECTED_ANCHORS[wid], wid
        assert "save_artifacts" in workflows["workflows"][wid], wid

    assert workflows["workflows"]["pure_echo"]["builder"] == "scripts/build_agent_declared_echo_payload.py"
    assert workflows["workflows"]["guardian_signed_echo"]["builder"] == "scripts/build_guardian_echo_payload.py"

    v0_inputs = {item["name"] for item in workflows["workflows"]["v0_v5_agent_declared_archive"]["inputs"]}
    for required in ["--reception-initiation-class", "--first-entry-url", "--what-checked", "--limitation", "--readback", "--idempotency-key"]:
        assert required in v0_inputs, required

    custody = json.loads((ROOT / "api" / "gateway-artifact-custody.v1.json").read_text(encoding="utf-8"))
    assert custody["schema"] == "trinityaccord.gateway-artifact-custody.v1"
    assert "private_key_file" in custody["never_save_publicly"]
    assert "payload_json" in custody["must_not_modify_after_signing"]
    assert "universal_save_artifacts" in custody

    agent_start = json.loads((ROOT / "api" / "agent-start.v1.json").read_text(encoding="utf-8"))
    assert agent_start["workflow_manual_url"] == "/gateway-workflows/"
    assert agent_start["workflow_manual_machine_url"] == "/api/gateway-workflows.v1.json"
    assert agent_start["artifact_custody_url"] == "/api/gateway-artifact-custody.v1.json"

    for wid, anchor in EXPECTED_ANCHORS.items():
        if wid in agent_start["routes"]:
            assert agent_start["routes"][wid]["workflow_anchor"] == anchor

    print("PASS: test_gateway_workflow_api")

if __name__ == "__main__":
    main()
