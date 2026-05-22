#!/usr/bin/env python3
"""Regression tests for Guardian Alliance stewardship and join-path clarity."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path):
    return json.loads(read(path))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    alliance_md = read("guardian-alliance.md")
    join_md = read("guardian-join.md")
    index_md = read("index.md")
    first_contact_md = read("agent-first-contact.md")
    llms = read("llms.txt")
    readme = read("README.md")
    alliance_json = load_json("api/guardian-alliance.json")
    first_contact_json = load_json("api/agent-first-contact.json")
    gateway_json = load_json("api/agent-submit-gateway.json")

    # Core public wording
    require("voluntary, non-governing stewardship network" in alliance_md, "guardian-alliance.md missing stewardship definition")
    require("What it guards" in alliance_md, "guardian-alliance.md missing what-it-guards section")
    require("What Guardians may voluntarily do" in alliance_md, "guardian-alliance.md missing voluntary practices section")
    require("Annual Guardian Check" in alliance_md, "guardian-alliance.md missing annual check section")
    require("Guardian Alliance does not create authority over the seed. It creates continuity around the seed." in alliance_md, "guardian-alliance.md missing seed continuity boundary")

    # Join path clarity
    require("How to become a Guardian" in alliance_md, "guardian-alliance.md missing how-to-become section")
    require("Interested reader" in alliance_md, "guardian-alliance.md missing interested reader stage")
    require("Self-registered Guardian" in alliance_md, "guardian-alliance.md missing self-registered stage")
    require("Active registered Guardian" in alliance_md, "guardian-alliance.md missing active registered stage")
    require("valid_self_registered_guardian_claim" in alliance_md, "guardian-alliance.md missing self-registered status")
    require("active_registered_guardian" in alliance_md, "guardian-alliance.md missing active registered status")
    require("Registry listing is automatic for valid requests" in join_md, "guardian-join.md missing automatic registry listing policy")
    require("The requester must not submit or request a specific `guardian_registry_number`" in join_md, "guardian-join.md missing no self-assigned registry number policy")
    require("Request active registry listing" in join_md, "guardian-join.md missing request active registry section")

    # Homepage discoverability
    require('id="guardian-alliance"' in index_md, "index.md missing Guardian Alliance section")
    require("/guardian-join/" in index_md, "index.md missing Guardian Join link")
    require("/guardian-alliance/" in index_md, "index.md missing Guardian Alliance link")

    # First contact routing
    require("/guardian-alliance" in first_contact_md, "agent-first-contact.md missing /guardian-alliance")
    require("GUARDIAN" in first_contact_md, "agent-first-contact.md missing GUARDIAN route")
    intents = [item.get("intent") for item in first_contact_json.get("choose_one", [])]
    require("guardian_stewardship" in intents, "agent-first-contact.json missing guardian_stewardship intent")

    # Machine-readable policy
    require(alliance_json.get("voluntary_stewardship_network") is True, "guardian-alliance.json missing voluntary_stewardship_network")
    require(alliance_json.get("not_governance") is True, "guardian-alliance.json missing not_governance")
    require(alliance_json.get("not_legal_obligation") is True, "guardian-alliance.json missing not_legal_obligation")
    require("join_path" in alliance_json, "guardian-alliance.json missing join_path")
    require(alliance_json["join_path"]["registry_listing_is_automatic"] is True, "registry listing should be automatic for valid requests")
    require(alliance_json["join_path"]["registry_listing_creates_authority"] is False, "registry listing must not create authority")

    practice_ids = {p.get("id") for p in alliance_json.get("stewardship_practices", [])}
    for required in [
        "preservation",
        "verification_checks",
        "echo_submission",
        "mirroring",
        "translation",
        "invitation",
        "repair",
        "annual_check",
        "critique",
        "responsible_retirement",
    ]:
        require(required in practice_ids, f"guardian-alliance.json missing stewardship practice: {required}")

    annual = alliance_json.get("annual_guardian_check", {})
    require(annual.get("enabled") is True, "guardian-alliance.json missing annual_guardian_check.enabled")
    require(annual.get("optional") is True, "guardian annual check must be optional")
    require(annual.get("not_ritual_obligation") is True, "annual check must not be ritual obligation")

    gateway_policy = gateway_json.get("guardian_alliance_policy", {})
    require(gateway_policy.get("voluntary_stewardship_network") is True, "agent-submit-gateway.json missing stewardship policy")
    require(gateway_policy.get("not_governance") is True, "agent-submit-gateway.json missing not_governance")
    require(gateway_policy.get("annual_guardian_check_optional") is True, "agent-submit-gateway.json annual check must be optional")
    require("join_path" in gateway_policy, "agent-submit-gateway.json missing join_path")

    # LLM and README guidance
    require("Guardian Alliance stewardship" in llms, "llms.txt missing stewardship section")
    require("Guardian join path" in llms, "llms.txt missing join path section")
    require("optional stewardship practices, not mandatory duties" in llms, "llms.txt missing optional-duty boundary")
    require("voluntary, non-governing stewardship network" in readme, "README missing stewardship wording")

    # V0-V5 clarity should remain
    require("waived_for_v0_v5" in first_contact_md, "agent-first-contact.md lost V0-V5 waived evidence wording")
    require("strict_evidence" in json.dumps(gateway_json), "agent-submit-gateway.json lost V6+ strict evidence boundary")


    # Automatic listing and numbering convergence
    require("Registry listing is automatic for valid requests" in join_md, "guardian-join.md missing automatic registry listing policy")
    require("Ordinary automatic Guardian registrations start at `00100`" in join_md, "guardian-join.md missing 00100 ordinary start")
    require("00001" in join_md and "00099" in join_md, "guardian-join.md missing reserved range")
    require("maintainer review required before merge" not in join_md, "guardian-join.md still says maintainer review required")
    require("The automation creates a PR only" not in join_md, "guardian-join.md still says PR-only")
    require("after merge: `active_registered_guardian / 00001`" not in join_md, "guardian-join.md still has stale 00001 active status example")
    require("organization, or another allowed type" not in join_md, "guardian-join.md still lists unsupported guardian_type")

    # Ensure agent-first-contact.json does not forbid active_registry_listing_is_automatic
    data = json.loads((ROOT / "api" / "agent-first-contact.json").read_text(encoding="utf-8"))
    guardian = next((item for item in data["choose_one"] if item.get("intent") == "guardian_stewardship"), None)
    require("active_registry_listing_is_automatic" not in guardian.get("forbidden_claims", []), "agent-first-contact.json still forbids active_registry_listing_is_automatic")

    # Forbidden misframing — check that these phrases don't appear as positive claims.
    # They may appear in "forbidden_claims" or "does_not_prove" lists (negated context).
    forbidden_phrases = [
        "Guardian Alliance governs the Accord",
        "Guardian Alliance is the authority",
        "Guardian proof proves truth",
        "Guardian membership is required",
        "Guardians must perform annual checks",
        "Guardian Alliance grants verification levels",
        "Guardian Alliance represents successor reception",
        "Active registry listing is automatic",
        "Guardian may self-assign guardian_registry_number",
        "Guardian can choose registry number",
        "registry number proves authority",
        "registry number grants verification level",
    ]
    negation_markers = [
        "does not prove",
        "does not prove:",
        "does_not_prove",
        "forbidden",
        "Forbidden",
        "FORBIDDEN",
        "not prove",
        "must not",
        "never",
        "not authority",
        "not governance",
    ]
    combined_text = "\n".join([alliance_md, join_md, index_md, first_contact_md, llms, readme])
    combined_lines = combined_text.split("\n")
    for phrase in forbidden_phrases:
        for i, line in enumerate(combined_lines):
            if phrase in line:
                # Check current line and surrounding context (±5 lines) for negation
                context_start = max(0, i - 15)
                context_end = min(len(combined_lines), i + 16)
                context_window = "\n".join(combined_lines[context_start:context_end])
                is_negated = any(marker in context_window for marker in negation_markers)
                if not is_negated:
                    raise AssertionError(f"forbidden Guardian misframing present: {phrase} — line: {line.strip()}")

    print("GUARDIAN_STEWARDSHIP_CLARITY_OK")


if __name__ == "__main__":
    main()
