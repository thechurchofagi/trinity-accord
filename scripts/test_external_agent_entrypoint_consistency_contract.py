#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_text(rel: str) -> str:
    p = ROOT / rel
    require(p.exists(), f"missing {rel}")
    return p.read_text(encoding="utf-8")


def read_json(rel: str) -> dict:
    return json.loads(read_text(rel))


def main() -> int:
    first = read_json("api/agent-first-contact.json")
    start = read_json("api/agent-start.v2.json")
    helper = read_json("api/record-chain-field-helper.v1.json")
    gateway = read_json("api/record-chain-intake-gateway.v1.json")
    schema = read_json("api/record-chain-submission-schema.v1.json")
    builder_manifest = read_json("api/record-chain-builder-bundles.v1.json")

    agent_start_md = read_text("agent-start.md")
    quickstart_md = read_text("external-agent-quickstart.md")
    llms = read_text("llms.txt")
    ai = read_text("ai.txt")

    schema_types = set(schema["properties"]["record_type"]["enum"])
    builder_supports = set(builder_manifest["canonical_builder"]["supports"])

    require("classification_update" in schema_types, "schema supports classification_update")
    require("classification_update" in builder_supports, "builder manifest supports classification_update")
    require(gateway["public_phase"]["status"] == "production_live", "gateway must be production_live")

    submit_action = next(
        item for item in first["choose_one"]
        if item.get("intent") == "submit_record"
    )

    require(
        "classification_update" in submit_action.get("supported_record_types", []),
        "agent-first-contact supported_record_types missing classification_update",
    )

    zero_clone = first.get("zero_clone_formal_builder_policy", {})
    require(
        "classification_update" in zero_clone.get("supported_zero_clone_routes", []),
        "zero_clone supported routes missing classification_update",
    )

    commands = start["builder_usage_safety_protocol"]["record_type_commands"]
    require("classification_update" in commands, "agent-start.v2 record_type_commands missing classification_update")
    require(
        "classification-update" in commands["classification_update"]["build_command"],
        "classification_update build_command must use builder classification-update",
    )

    require(
        "Classification Update" in agent_start_md and "classification-update" in agent_start_md,
        "agent-start.md supported table missing Classification Update",
    )

    require(
        helper.get("current_public_phase") == "production_live",
        "field helper current_public_phase must be production_live",
    )

    diagnostic_help = helper.get("diagnostic_code_help", {})
    for code in [
        "AUTHORSHIP_CLAIM_BOUNDARY_INVALID",
        "CLIENT_SUPPLIED_UNSIGNED_PROJECTION_FIELD",
        "MISSING_CLASSIFICATION_UPDATE_CONTENT",
        "INVALID_CLASSIFICATION_TARGET_SHA",
    ]:
        require(code in diagnostic_help, f"field helper missing diagnostic help for {code}")

    submit_readback = submit_action.get("post_submit_readback", {})
    require(
        submit_readback.get("guardian_state") == "/record-chain/indexes/guardian-state.json",
        "first-contact guardian_state must point to record-chain guardian-state",
    )
    require(
        submit_readback.get("legacy_guardian_registry_is_historical_archive_only") is True,
        "first-contact must mark legacy guardian registry historical-only",
    )

    observation = first["post_submit_observation_protocol"]
    claim = observation["claim_discipline"]

    require(
        claim.get("guardian_active_status_requires_record_chain_guardian_state_readback") is True,
        "guardian active status must require record-chain guardian-state readback",
    )
    require(
        claim.get("guardian_active_status_requires_registry_readback") is False,
        "guardian_active_status_requires_registry_readback must be false",
    )
    require(
        observation["record_specific_indexes"].get("guardian_application") == "/record-chain/indexes/guardian-state.json",
        "guardian_application public index must be guardian-state",
    )

    for label, text in [("llms.txt", llms), ("ai.txt", ai)]:
        require(
            "/record-chain/indexes/guardian-state.json" in text,
            f"{label} must mention current guardian-state source",
        )
        forbidden_active = "Guardian application → `/api/guardian-registry.json`"
        require(
            forbidden_active not in text,
            f"{label} must not present legacy guardian registry as active Guardian application index",
        )

    require(
        "Use `/api/agent-first-contact.json` and `/api/record-chain-intake-gateway.v1.json`" in quickstart_md,
        "external-agent-quickstart must point to current route/gateway contract",
    )
    require(
        "confirm the gateway-runtime-contract before submission" not in quickstart_md,
        "external-agent-quickstart must not tell agents to use gateway-runtime-contract for current submissions",
    )
    require(
        "select the current route through the route-selector" not in quickstart_md,
        "external-agent-quickstart must not tell agents to use route-selector for current submissions",
    )

    print("PASS: external agent entrypoint consistency contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
