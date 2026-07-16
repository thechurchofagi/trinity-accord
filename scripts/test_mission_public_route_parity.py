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
    first_contact_page = (ROOT / "agent-first-contact.md").read_text(encoding="utf-8")
    technical_reference = (ROOT / "technical-historical-reference.md").read_text(encoding="utf-8")

    first_types = set(next(item["supported_record_types"] for item in first["choose_one"] if "supported_record_types" in item))
    start_types = set(start["builder_usage_safety_protocol"]["record_type_commands"])
    mission_types = set(mission["supported_public_actions"]["formal_record_chain_routes"])
    errors = []
    for label, values in [
        ("agent-first-contact", first_types),
        ("agent-start", start_types),
        ("mission-governance", mission_types),
    ]:
        if values != schema_types:
            errors.append(
                f"{label} routes differ from public schema: "
                f"missing={sorted(schema_types-values)} extra={sorted(values-schema_types)}"
            )

    # The homepage is intentionally a concise discovery surface. It must route
    # to the current action page, while the complete current record-type list is
    # validated on Agent First Contact.
    for needle in [
        "/agent-first-contact/",
        "Respond, verify, or preserve",
        "Record-Chain",
    ]:
        if needle not in homepage:
            errors.append(f"homepage current-action routing omits {needle}")

    current_names = [
        "Echo",
        "Verification",
        "Guardian Application",
        "Guardian Retirement",
        "Propagation",
        "Correction",
        "Classification Update",
        "Context-insufficient notice",
    ]
    for name in current_names:
        if name not in first_contact_page:
            errors.append(f"agent-first-contact current submission list omits {name}")

    supported = mission["supported_public_actions"]
    for collection_name in [
        "interpretation_actions",
        "guardian_actions",
        "verification_actions",
        "core_external_agent_routes_live_smoked",
        "formal_record_chain_routes",
    ]:
        if "guardian_signed_echo" in set(supported.get(collection_name, [])):
            errors.append(
                "historical guardian_signed_echo is advertised in current "
                f"supported_public_actions.{collection_name}"
            )

    guardian_route = mission["action_semantics"]["guardian"]["guardian_signed_echo"]
    if (
        guardian_route.get("status")
        != "historical_or_specialized_not_current_public_route"
        or guardian_route.get("do_not_use_for_new_public_submissions") is not True
        or guardian_route.get("current_public_builder_command") is not None
    ):
        errors.append("guardian_signed_echo historical/current boundary is incomplete")

    # The zero-clone container must expose only current Builder routes. Historical
    # names belong in historical_term_redirects and must never masquerade as
    # downloadable current bundles or current Builder fragments.
    zero_clone_routes = router["zero_clone_builder_routes"]
    for retired in ("pure_echo", "guardian_signed_echo"):
        if retired in zero_clone_routes:
            errors.append(f"historical route appears in current zero-clone routes: {retired}")

    for route_name, route in zero_clone_routes.items():
        if not isinstance(route, dict):
            errors.append(f"zero-clone route {route_name} must be an object")
            continue
        if route.get("_status") != "current_record_chain_builder_route":
            errors.append(f"zero-clone route {route_name} lacks current route status")
        if route.get("bundle") != "/downloads/record-chain-builder.mjs":
            errors.append(f"zero-clone route {route_name} does not use the canonical Builder")
        if route.get("requires_full_repo_clone") is not False:
            errors.append(f"zero-clone route {route_name} incorrectly requires a repository clone")

    historical = router.get("historical_term_redirects", {})
    pure_echo = historical.get("pure_echo", {})
    if (
        pure_echo.get("status") != "historical_archive_only"
        or pure_echo.get("do_not_use_for_new_submissions") is not True
        or pure_echo.get("replacement_route") != "submit_echo"
    ):
        errors.append("pure_echo historical redirect boundary is incomplete")

    guardian_echo = historical.get("guardian_signed_echo", {})
    if (
        guardian_echo.get("status")
        != "historical_or_specialized_not_current_public_route"
        or guardian_echo.get("do_not_use_for_new_submissions") is not True
    ):
        errors.append("guardian_signed_echo historical redirect boundary is incomplete")

    required_lifecycle = (
        "Final chain inclusion occurs only after server-side validation, append, "
        "and index publication. OTS and Arweave are later durability and archive "
        "stages; they do not define inclusion."
    )
    if required_lifecycle not in technical_reference:
        errors.append("technical reference conflates final inclusion with later OTS/Arweave archive completion")

    if errors:
        raise SystemExit("FAIL:\n- " + "\n- ".join(errors))
    print(
        "PASS: mission, schema, first-contact, agent-start, current task-router, "
        f"homepage routing, and technical reference agree on {len(schema_types)} current public record types"
    )


if __name__ == "__main__":
    main()
