#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def find_record_type_enum(value):
    found = []
    if isinstance(value, dict):
        if isinstance(value.get("record_type"), dict) and isinstance(value["record_type"].get("enum"), list):
            found.extend(value["record_type"]["enum"])
        for child in value.values():
            found.extend(find_record_type_enum(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(find_record_type_enum(child))
    return set(found)


def main() -> None:
    schema_types = find_record_type_enum(load("api/record-chain-submission-schema.v1.json"))
    first = load("api/agent-first-contact.json")
    start = load("api/agent-start.v2.json")
    mission = load("api/mission-governance.v1.json")
    router = load("api/agent-task-router.v1.json")
    homepage = (ROOT / "index.md").read_text(encoding="utf-8")

    first_types = set(next(item["supported_record_types"] for item in first["choose_one"] if "supported_record_types" in item))
    start_types = set(start["builder_usage_safety_protocol"]["record_type_commands"])
    mission_types = set(mission["supported_public_actions"]["formal_record_chain_routes"])
    errors = []
    for label, values in [("agent-first-contact", first_types), ("agent-start", start_types), ("mission-governance", mission_types)]:
        if values != schema_types:
            errors.append(f"{label} routes differ from public schema: missing={sorted(schema_types-values)} extra={sorted(values-schema_types)}")

    current_names = ["Echo", "Verification", "Guardian Application", "Guardian Retirement", "Propagation", "Correction", "Classification Update", "Context-Insufficient Notice"]
    for name in current_names:
        if name not in homepage:
            errors.append(f"homepage current submission list omits {name}")

    supported = mission["supported_public_actions"]
    if "guardian_signed_echo" in supported["echo_actions"] or "guardian_signed_echo" in supported["guardian_actions"]:
        errors.append("historical guardian_signed_echo is advertised as a current supported public action")
    guardian_route = mission["action_semantics"]["guardian"]["guardian_signed_echo"]
    if guardian_route.get("status") != "historical_or_specialized_not_current_public_route" or guardian_route.get("do_not_use_for_new_public_submissions") is not True:
        errors.append("guardian_signed_echo historical/current boundary is incomplete")

    routes = router["zero_clone_builder_routes"]
    if routes.get("_status") != "mixed_current_and_historical":
        errors.append("agent-task-router container hides its mixed current/historical route state")
    for key in ("pure_echo", "guardian_signed_echo"):
        route = routes[key]
        if route.get("status") != "historical_archive_only" or route.get("do_not_use_for_new_submissions") is not True:
            errors.append(f"{key} lacks an explicit historical do-not-use boundary")
        if str(route.get("bundle", "")).startswith("/downloads/record-chain-builder.mjs#/bundles/"):
            errors.append(f"{key} points to a nonexistent current Builder fragment")

    required_lifecycle = "Final chain inclusion occurs only after server-side validation, append, and index publication. OTS and Arweave are later durability and archive stages; they do not define inclusion."
    if required_lifecycle not in homepage:
        errors.append("homepage conflates final inclusion with later OTS/Arweave archive completion")

    if errors:
        raise SystemExit("FAIL:\n- " + "\n- ".join(errors))
    print(f"PASS: mission, schema, first-contact, agent-start, task-router, and homepage agree on {len(schema_types)} current public record types")


if __name__ == "__main__":
    main()
