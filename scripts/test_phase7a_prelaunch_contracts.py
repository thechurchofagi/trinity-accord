#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    agent = read_json("api/agent-start.v2.json")
    gateway = read_json("api/record-chain-intake-gateway.v1.json")
    oath = read_json("api/record-chain-oath-policy.v1.json")
    schema = read_json("api/record-chain-submission-schema.v1.json")
    readiness = read_json("api/founding-guardian-application-readiness.v1.json")
    rate = read_json("api/gateway-rate-limit-policy.v1.json")
    head = read_json("api/record-chain-head.json")

    public_phase = agent.get("public_phase", {})
    require(public_phase.get("status") == "public_test_stabilization", "agent-start must remain public_test_stabilization during prelaunch")
    require(public_phase.get("not_final_public_launch") is True, "not_final_public_launch must be true during prelaunch")
    require(public_phase.get("receipt_is_intake_only") is True, "receipt_is_intake_only must be true")

    gateway_phase = gateway.get("public_phase", {})
    require(gateway_phase.get("gateway_operational") is True, "gateway must be operational")
    require(gateway_phase.get("receipt_is_not_final_inclusion") is True, "receipt must not be final inclusion")
    require(gateway_phase.get("receipt_is_not_active_guardian_status") is True, "receipt must not be active guardian status")

    rules = gateway.get("public_submission_rule", {})
    for key in [
        "external_agents_do_not_need_github",
        "external_agents_must_not_clone_repository",
        "external_agents_must_not_directly_append_record_chain",
        "external_agents_must_not_write_record_chain_pending",
        "external_agents_must_not_request_github_pat",
    ]:
        require(rules.get(key) is True, f"gateway public_submission_rule.{key} must be true")

    require(oath.get("status") == "active", "oath policy must be active")
    oath_types = set(oath.get("formal_record_types_requiring_oath", []))
    require("guardian_application" in oath_types, "guardian_application must require oath")

    no_shortcut = oath.get("no_shortcut_policy", {})
    forbidden = set(no_shortcut.get("forbidden", []))
    for marker in [
        "piping oath from file",
        "generating oath by script",
        "loading oath from cache",
        "summarizing or paraphrasing the oath",
        "using external automation to produce readback",
        "auto-filling readback in builder",
    ]:
        require(marker in forbidden, f"oath no-shortcut forbidden marker missing: {marker}")

    schema_text = json.dumps(schema, sort_keys=True)
    for marker in [
        "client_oath_readback",
        "submission_oath_verification",
        "guardian_application",
        "submitting_participant_identity",
        "authorization_context",
        "non_authority_boundary_acknowledgement",
    ]:
        require(marker in schema_text, f"submission schema missing marker: {marker}")

    require(readiness.get("schema") == "trinityaccord.founding-guardian-application-readiness.v1", "readiness schema mismatch")
    require(readiness.get("status") == "prelaunch_blocked", "readiness status must be prelaunch_blocked")
    require(readiness.get("formal_window_open") is False, "formal_window_open must be false")
    require(readiness.get("founding_guardian_application_formal_window_open") is False, "founding guardian formal window must be false")
    require(readiness.get("formal_applicant_name_reserved") == "刘烘炬", "formal applicant must be 刘烘炬")
    require(readiness.get("must_not_submit_formal_application_yet") is True, "must_not_submit_formal_application_yet must be true")

    external_rules = readiness.get("external_applicant_rules", {})
    for key in [
        "must_use_public_gateway",
        "must_not_use_github_token",
        "must_not_use_arweave_jwk",
        "must_not_clone_repository",
        "must_not_append_record_chain",
        "receipt_is_intake_only",
        "receipt_is_not_final_inclusion",
    ]:
        require(external_rules.get(key) is True, f"readiness external_applicant_rules.{key} must be true")

    test_rules = readiness.get("test_canary_rules", {})
    require(test_rules.get("test_identity_label") == "Test Founding Guardian Applicant", "test identity label mismatch")
    require(test_rules.get("must_not_use_formal_applicant_name") is True, "test canary must not use formal applicant name")

    require(rate.get("schema") == "trinityaccord.gateway-rate-limit-policy.v1", "rate policy schema mismatch")
    policy = rate.get("policy", {})
    require(policy.get("global_submit_limit_per_hour") == 100, "global_submit_limit_per_hour must be 100")
    require(policy.get("participant_submit_limit_per_hour") == 10, "participant_submit_limit_per_hour must be 10")
    rate_types = set(policy.get("applies_to_record_types", []))
    for rt in ["echo", "verification", "guardian_application"]:
        require(rt in rate_types, f"rate limit must apply to {rt}")

    limited = rate.get("response_when_limited", {})
    require(limited.get("http_status") == 429, "rate limit http_status must be 429")
    require(limited.get("diagnostic_code") == "RATE_LIMIT_EXCEEDED", "rate limit diagnostic code mismatch")

    impl = rate.get("implementation_status", {})
    require(impl.get("server_side_enforcement_required_before_formal_window") is True, "rate enforcement must be required before formal window")
    require(impl.get("server_side_enforcement_verified") is False, "prelaunch contract should keep enforcement_verified=false until actually tested")

    require(head.get("entry_count") == 1, "prelaunch expects production chain still genesis-only")
    require(head.get("height") == 0, "prelaunch expects production height 0")

    print("PASS: Phase 7A prelaunch contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
