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
    phase_status = public_phase.get("status")
    require(
        phase_status in ("mainnet_prelaunch_testing", "live_test_active", "production_live"),
        "agent-start status must be mainnet_prelaunch_testing, live_test_active, or production_live",
    )
    if phase_status == "production_live":
        require(public_phase.get("network_phase") == "production", "production agent-start network_phase must be production")
        require(public_phase.get("not_final_public_launch") is False, "not_final_public_launch must be false during production live")
        require(public_phase.get("official_live_records_allowed") is True, "official live records must be allowed during production live")
        require(public_phase.get("production_enablement_marker_recorded") is True, "production enablement marker must be recorded")
    else:
        require(public_phase.get("not_final_public_launch") is True, "not_final_public_launch must be true during prelaunch/live-test")
        require(public_phase.get("official_live_records_allowed") is False, "official live records must be false during prelaunch/live-test")
    require(public_phase.get("receipt_is_intake_only") is True, "receipt_is_intake_only must be true")

    gateway_phase = gateway.get("public_phase", {})
    require(gateway_phase.get("gateway_operational") is True, "gateway must be operational")
    require(gateway_phase.get("receipt_is_not_final_inclusion") is True, "receipt must not be final inclusion")
    require(gateway_phase.get("receipt_is_not_active_guardian_status") is True, "receipt must not be active guardian status")
    if phase_status == "production_live":
        require(gateway_phase.get("network_phase") == "production", "gateway network_phase must be production during production live")
        require(gateway_phase.get("status") == "production_live", "gateway status must be production_live")
        require(gateway_phase.get("official_live_records_allowed") is True, "gateway official live records must be allowed during production live")

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
    require(readiness.get("formal_applicant_name_reserved") == "刘烘炬", "formal applicant must be 刘烘炬")

    formal_window_open = readiness.get("formal_window_open") is True
    if formal_window_open:
        require(readiness.get("status") == "formal_window_open", "readiness status must be formal_window_open when window is open")
        require(readiness.get("founding_guardian_application_formal_window_open") is True, "founding guardian formal window must be true")
        require(readiness.get("must_not_submit_formal_application_yet") is False, "must_not_submit_formal_application_yet must be false when window is open")
    else:
        require(readiness.get("status") in ("prelaunch_blocked", "formal_window_blocked"), "readiness status must be blocked when window is closed")
        require(readiness.get("founding_guardian_application_formal_window_open") is False, "founding guardian formal window must be false")
        require(readiness.get("must_not_submit_formal_application_yet") is True, "must_not_submit_formal_application_yet must be true when window is closed")

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

    cooldown = policy.get("global_acceptance_cooldown", {})
    require(cooldown.get("minimum_seconds") == 3600, "global cooldown minimum must be 3600 seconds")
    require(cooldown.get("maximum_seconds") == 7200, "global cooldown maximum must be 7200 seconds")
    require(cooldown.get("randomized") is True, "global cooldown must be randomized")
    require(cooldown.get("exact_reopening_time_disclosed") is False, "exact reopening time must not be disclosed")
    require(cooldown.get("reopening_time_not_computable_from_public_repository_state") is True,
            "public repository state must not reveal the reopening time")

    secondary = policy.get("secondary_submit_attempt_limits", {})
    require(secondary.get("global_submit_limit_per_hour") == 100,
            "secondary global_submit_limit_per_hour must be 100")
    require(secondary.get("participant_submit_limit_per_hour") == 10,
            "secondary participant_submit_limit_per_hour must be 10")

    content_limits = policy.get("content_limits", {})
    require(content_limits.get("request_max_bytes") == 98304, "request limit must be 96 KiB")
    require(content_limits.get("persistent_record_draft_max_bytes") == 49152,
            "record draft limit must be 48 KiB")
    require(content_limits.get("text_field_max_characters") == 4000,
            "text field limit must be 4000 characters")

    rate_types = set(policy.get("applies_to_record_types", []))
    for rt in ["echo", "verification", "guardian_application"]:
        require(rt in rate_types, f"rate limit must apply to {rt}")

    limited = rate.get("response_when_limited", {})
    require(limited.get("cooldown_http_status") == 429, "cooldown http_status must be 429")
    require(limited.get("content_http_status") == 413, "content http_status must be 413")
    require(limited.get("semantic_content_http_status") == 422, "semantic content http_status must be 422")
    require(limited.get("accepted") is False, "limited response accepted must be false")
    require(limited.get("cost_explanation_required") is True, "limited response must explain cost")
    require(limited.get("project_purpose_explanation_required") is True,
            "limited response must explain project purpose")

    impl = rate.get("implementation_status", {})
    require(impl.get("server_side_enforcement_required_before_formal_window") is True, "rate enforcement must be required before formal window")
    require(impl.get("server_side_enforcement_verified") is True, "server-side enforcement must be verified")
    require(impl.get("durable_across_restart") is True, "acceptance cooldown must survive restart")
    require(impl.get("multi_instance_safe") is False, "single-process final gate must disclose multi-instance limitation")

    entry_count = head.get("entry_count", 0)
    require(entry_count >= 1, "main chain expects at least genesis entry")

    print("PASS: Phase 7A prelaunch contracts with layered production resource protection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
