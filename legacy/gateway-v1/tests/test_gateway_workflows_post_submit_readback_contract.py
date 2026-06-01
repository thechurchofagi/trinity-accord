#!/usr/bin/env python3
"""Gateway workflows must require post-submit readback before agent exit."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
api = json.loads((ROOT / "api" / "gateway-workflows.v1.json").read_text(encoding="utf-8"))
human = (ROOT / "gateway-workflows.md").read_text(encoding="utf-8")

contract = api.get("post_submit_readback_contract")
if not isinstance(contract, dict) or contract.get("required") is not True:
    print("FAIL: missing required post_submit_readback_contract")
    sys.exit(1)

required_after = set(contract.get("required_after_submit", []))
for item in [
    "save_submit_response_json",
    "extract_issue_url",
    "read_route_specific_public_status_targets",
    "report_archive_status_if_known",
    "report_public_status_readback_performed",
    "state_remaining_uncertainty",
    "do_not_imply_background_completion",
]:
    if item not in required_after:
        print(f"FAIL: post_submit_readback_contract missing required_after_submit {item}")
        sys.exit(1)

must_not = set(contract.get("must_not_claim", []))
for item in [
    "archived_from_issue_created_alone",
    "public_status_updated_without_public_status_readback",
    "verified_from_gateway_acceptance_alone",
    "active_guardian_from_stage_1_alone",
    "active_guardian_from_stage_2_submission_alone",
]:
    if item not in must_not:
        print(f"FAIL: post_submit_readback_contract missing must_not_claim {item}")
        sys.exit(1)

submission_workflows = [
    "pure_echo",
    "v0_v5_agent_declared_archive",
    "v6_plus_strict_evidence",
    "e2_verification_echo",
    "guardian_application_stage_1",
    "guardian_listing_stage_2",
    "guardian_signed_echo",
]

for workflow_id in submission_workflows:
    workflow = api["workflows"].get(workflow_id)
    if not isinstance(workflow, dict):
        print(f"FAIL: workflow missing: {workflow_id}")
        sys.exit(1)

    rb = workflow.get("post_submit_readback")
    if not isinstance(rb, dict):
        print(f"FAIL: {workflow_id} missing post_submit_readback")
        sys.exit(1)

    if rb.get("use_global_contract") is not True:
        print(f"FAIL: {workflow_id} post_submit_readback must use global contract")
        sys.exit(1)

    targets = rb.get("required_targets", [])
    if "submit_response.issue_url" not in targets:
        print(f"FAIL: {workflow_id} missing submit_response.issue_url readback target")
        sys.exit(1)

    if rb.get("exit_report_required") is not True:
        print(f"FAIL: {workflow_id} must require exit report")
        sys.exit(1)

# Human docs must contain the section and warnings.
required_human = [
    "Required post-submit readback before leaving",
    "means the Gateway created an intake Issue",
    "by itself mean archived",
    "archive_ready=true",
    "Archive status: unknown/pending",
    "/api/public-home-status.json",
]

for phrase in required_human:
    if phrase not in human:
        print(f"FAIL: gateway-workflows.md missing post-submit phrase: {phrase}")
        sys.exit(1)

print("PASS: gateway workflows require post-submit readback")
