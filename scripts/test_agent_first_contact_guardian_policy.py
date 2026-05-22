#!/usr/bin/env python3
"""Check Guardian joining policy in first-contact docs."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    md = (ROOT / "agent-first-contact.md").read_text(encoding="utf-8")
    data = json.loads((ROOT / "api" / "agent-first-contact.json").read_text(encoding="utf-8"))

    require("node scripts/create_guardian_application.mjs" in md, "missing Stage 1 builder in agent-first-contact.md")
    require("python3 scripts/build_guardian_listing_request_payload.py" in md, "missing Stage 2 builder in agent-first-contact.md")
    require("Ordinary automatic Guardian registrations start at `00100`" in md, "missing 00100 numbering in agent-first-contact.md")

    guardian = next((item for item in data["choose_one"] if item.get("intent") == "guardian_stewardship"), None)
    require(guardian is not None, "agent-first-contact.json missing guardian_stewardship")

    join_path = guardian["join_path"]
    require(join_path["active_registry_listing_is_automatic"] is True, "active registry listing must be automatic")
    require("active_registry_listing_is_automatic" not in guardian.get("forbidden_claims", []), "automatic active listing must not be forbidden")

    require(join_path["stage_1_self_registration"]["builder"] == "scripts/create_guardian_application.mjs", "wrong Stage 1 builder")
    require(join_path["stage_2_active_registry_listing"]["builder"] == "scripts/build_guardian_listing_request_payload.py", "wrong Stage 2 builder")

    policy = guardian["guardian_registry_number_policy"]
    require(policy["ordinary_auto_start"] == "00100", "ordinary_auto_start must be 00100")
    require(policy["special_reserved_range"] == "00001-00099", "reserved range must be 00001-00099")
    require(policy["submitter_must_not_supply"] is True, "submitter must not supply registry number")

    require(guardian["not_verification_echo"] is True, "Guardian path must be marked not Verification Echo")
    require(guardian["does_not_raise_verification_level"] is True, "Guardian path must not raise verification level")

    # Stage 2 error_recovery must include runtime preflight guidance
    er = join_path["stage_2_active_registry_listing"].get("error_recovery", {})
    require(
        "preflight_guardian_listing_payload.py" in er.get("runtime_preflight", ""),
        "error_recovery missing runtime_preflight script"
    )
    caps = er.get("required_gateway_capabilities", [])
    require(len(caps) >= 7, f"error_recovery.required_gateway_capabilities too short: {len(caps)}")
    require(
        "guardian_registry_listing_request" in caps,
        "error_recovery.required_gateway_capabilities missing guardian_registry_listing_request"
    )
    require(
        "authorship_canonical.trinity.agent_authorship_common.v1" in caps,
        "error_recovery.required_gateway_capabilities missing authorship_canonical"
    )
    require(
        "do_not_resign_manually" in er.get("signed_payload_sha256_mismatch_after_local_pass", ""),
        "error_recovery missing signed_payload_sha256_mismatch_after_local_pass guidance"
    )

    print("AGENT_FIRST_CONTACT_GUARDIAN_POLICY_OK")


if __name__ == "__main__":
    main()
