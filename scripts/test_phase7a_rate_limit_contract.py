#!/usr/bin/env python3
"""Contract test: verify layered intake protection and policy alignment."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, msg: str) -> None:
    if not condition:
        raise SystemExit(msg)


def main() -> int:
    policy = json.loads((ROOT / "api/gateway-rate-limit-policy.v1.json").read_text(encoding="utf-8"))

    require(policy["schema"] == "trinityaccord.gateway-rate-limit-policy.v1", "schema mismatch")

    p = policy["policy"]
    cooldown = p["global_acceptance_cooldown"]
    require(cooldown["minimum_seconds"] == 3600, "cooldown minimum must be 3600 seconds")
    require(cooldown["maximum_seconds"] == 7200, "cooldown maximum must be 7200 seconds")
    require(cooldown["randomized"] is True, "cooldown must be randomized")
    require(cooldown["exact_reopening_time_disclosed"] is False,
            "exact reopening time must not be disclosed")
    require(cooldown["first_gate"] == "before request-body read and expensive validation",
            "entrance gate disclosure mismatch")
    require("immediately before" in cooldown["second_gate"],
            "final pre-persistence gate disclosure mismatch")

    secondary = p["secondary_submit_attempt_limits"]
    require(secondary["global_submit_limit_per_hour"] == 100,
            "secondary global attempt limit must be 100")
    require(secondary["participant_submit_limit_per_hour"] == 10,
            "secondary participant attempt limit must be 10")
    require(secondary["implementation"] == "single_process_in_memory_sliding_window",
            "secondary limiter must disclose process-local implementation")

    limits = p["content_limits"]
    require(limits["request_max_bytes"] == 98304, "request limit must be 96 KiB")
    require(limits["persistent_record_draft_max_bytes"] == 49152,
            "persistent draft limit must be 48 KiB")
    require(limits["text_field_max_characters"] == 4000,
            "text field limit must be 4000 characters")
    require(limits["inline_data_urls_forbidden"] is True,
            "inline data URLs must be forbidden")
    require(limits["inline_base64_or_binary_attachments_forbidden"] is True,
            "inline binary attachments must be forbidden")
    require(limits["record_total_text_character_limits"]["verification"] == 12000,
            "verification total text limit must be 12000")

    types = set(p["applies_to_record_types"])
    for rt in ["echo", "verification", "guardian_application", "context_insufficient_notice"]:
        require(rt in types, f"must apply to {rt}")

    resp = policy["response_when_limited"]
    require(resp["cooldown_http_status"] == 429, "cooldown HTTP status must be 429")
    require(resp["content_http_status"] == 413, "body-size HTTP status must be 413")
    require(resp["semantic_content_http_status"] == 422,
            "semantic content HTTP status must be 422")
    require(resp["accepted"] is False, "accepted must be false")
    require(resp["exact_reopening_time_returned"] is False,
            "response must not return exact reopening time")
    require(resp["cost_explanation_required"] is True,
            "limited response must explain storage/Arweave cost")
    require(resp["project_purpose_explanation_required"] is True,
            "limited response must explain project purpose")

    impl = policy["implementation_status"]
    require(impl["server_side_enforcement_required_before_formal_window"] is True,
            "enforcement must be required before formal window")
    require(impl["server_side_enforcement_verified"] is True,
            "server-side enforcement must remain verified")
    require(impl["rate_limit_implementation"] == "protected ASGI entrypoint plus existing core Gateway limiter",
            "implementation must disclose layered protected entrypoint")
    require(impl["durable_acceptance_state"] == "latest immutable intake materialization commit on the target branch",
            "implementation must disclose durable acceptance state")
    require(impl["multi_instance_safe"] is False,
            "single-process final lock is not multi-instance safe")
    require(impl["durable_across_restart"] is True,
            "commit-derived cooldown must survive restart")

    # Verify the defense-in-depth rate_limit module constants still match.
    spec = importlib.util.spec_from_file_location(
        "rate_limit",
        ROOT / "apps/record_chain_intake_gateway/gateway/rate_limit.py",
    )
    require(spec is not None and spec.loader is not None, "could not import rate_limit module")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    require(mod.GLOBAL_LIMIT_PER_HOUR == 100, "module global limit must be 100")
    require(mod.PARTICIPANT_LIMIT_PER_HOUR == 10, "module participant limit must be 10")

    protected_text = (
        ROOT / "apps/record_chain_intake_gateway/protected_app.py"
    ).read_text(encoding="utf-8")
    for marker in [
        "cooldown_seconds_for_commit",
        "_reject_if_blocked",
        "async with self._submit_lock",
        "REPEATED_RESOURCE_PRESSURE_WARNING",
        "RECORD_TOTAL_TEXT_TOO_LONG",
        "RECORD_DRAFT_TOO_LARGE",
        "INLINE_BINARY_CONTENT_FORBIDDEN",
    ]:
        require(marker in protected_text, f"protected entrypoint missing {marker}")

    app_text = (ROOT / "apps/record_chain_intake_gateway/app.py").read_text(encoding="utf-8")
    require("check_rate_limit" in app_text, "app.py must retain secondary check_rate_limit")
    require("rate_limit_result" in app_text, "app.py must use secondary rate-limit result")

    print("PASS: layered durable cooldown, content limits, and secondary rate-limit contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
