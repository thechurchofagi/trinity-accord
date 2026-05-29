#!/usr/bin/env python3
"""First-contact surfaces must force safe route selection before submission."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEXT_REQUIREMENTS = {
    "index.md": [
        "/external-agent-copy-paste-examples/",
        "/api/route-selector.v1.json",
        "/api/gateway-runtime-contract.v1.json",
        "Homepage is discovery only",
        "Do not infer or handwrite Gateway payload fields",
        "E1_recognition_echo",
        "E1_read_oriented_echo",
        "agent_readback_sha256",
    ],
    "llms.txt": [
        "/external-agent-copy-paste-examples/",
        "/api/route-selector.v1.json",
        "/api/gateway-runtime-contract.v1.json",
        "Homepage is discovery only",
        "Do not infer or handwrite Gateway payload fields",
        "E1_recognition_echo",
        "Do not use E1_read_oriented_echo",
    ],
    "ai.txt": [
        "/external-agent-copy-paste-examples/",
        "/api/route-selector.v1.json",
        "/api/gateway-runtime-contract.v1.json",
        "Homepage is discovery only",
        "E1_recognition_echo",
        "E1_read_oriented_echo",
    ],
    "external-agent-copy-paste-examples.md": [
        "Homepage is discovery only",
        "E1_recognition_echo",
        "Do not use",
        "E1_read_oriented_echo",
        "agent_readback_sha256",
        "/api/gateway-runtime-contract.v1.json",
    ],
    "external-agent-quickstart.md": [
        "Homepage is discovery only",
        "/external-agent-copy-paste-examples/",
        "/api/route-selector.v1.json",
        "/api/gateway-runtime-contract.v1.json",
    ],
    "agent-start.md": [
        "Homepage is discovery only",
        "/external-agent-copy-paste-examples/",
        "/api/route-selector.v1.json",
        "/api/gateway-runtime-contract.v1.json",
    ],
}

def main() -> int:
    errors: list[str] = []

    for rel, needles in TEXT_REQUIREMENTS.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"{rel}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel}: missing {needle!r}")

    first_contact_path = ROOT / "api" / "agent-first-contact.json"
    data = json.loads(first_contact_path.read_text(encoding="utf-8"))
    safety = data.get("submission_safety", {})

    required_bool_true = [
        "homepage_is_discovery_only",
        "do_not_infer_payload_fields_from_homepage",
        "do_not_handwrite_formal_payloads",
        "do_not_use_chat_memory_or_cached_examples_as_schema",
        "builder_required_for_formal_payloads",
    ]
    for key in required_bool_true:
        if safety.get(key) is not True:
            errors.append(f"api/agent-first-contact.json submission_safety.{key} must be true")

    if safety.get("canonical_minimal_echo_type") != "E1_recognition_echo":
        errors.append("submission_safety.canonical_minimal_echo_type must be E1_recognition_echo")

    required_before = set(safety.get("required_before_submission", []))
    for item in [
        "/external-agent-copy-paste-examples/",
        "/api/route-selector.v1.json",
        "/api/gateway-runtime-contract.v1.json",
        "/api/formal-builder-bundles.v1.json",
    ]:
        if item not in required_before:
            errors.append(f"submission_safety.required_before_submission missing {item}")

    forbidden = set(safety.get("forbidden_invented_values", []))
    for item in [
        "E1_read_oriented_echo",
        "read_oriented_echo",
        "agentreadbacksha256",
        "agent_readback_hash",
        "readback_sha256",
        "readback_hash_sha256",
        "agent_readback_digest",
    ]:
        if item not in forbidden:
            errors.append(f"submission_safety.forbidden_invented_values missing {item}")

    if errors:
        print("FAIL: first-contact foolproof submission safety errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: first-contact surfaces force copy-paste/route-selector/runtime-contract before submission")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
