#!/usr/bin/env python3
"""External-agent docs must align with current Record-Chain intake gateway."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "ai.txt": ROOT / "ai.txt",
    "llms.txt": ROOT / "llms.txt",
    "gateway-workflows.md": ROOT / "gateway-workflows.md",
    "external-agent-quickstart.md": ROOT / "external-agent-quickstart.md",
    "zero-clone-builders.md": ROOT / "zero-clone-builders.md",
    "api/agent-start.v2.json": ROOT / "api" / "agent-start.v2.json",
    "api/external-agent-operation-examples.v1.json": ROOT / "api" / "external-agent-operation-examples.v1.json",
}

REQUIRED_BY_FILE = {
    "ai.txt": [
        "/external-agent-quickstart/",
        "/api/agent-start.v2.json",
        "/api/record-chain-intake-gateway.v1.json",
        "BUILDER_USAGE_UNCLEAR",
    ],
    "llms.txt": [
        "/agent-first-contact/",
        "/api/agent-first-contact.json",
        "/api/record-chain-builder-bundles.v1.json",
        "/downloads/record-chain-builder.mjs",
        "/downloads/record-chain-agent-field-guidance.v1.json",
        "/agent-record-chain-guidance/",
        "/external-agent-quickstart/",
        "/api/agent-start.v2.json",
        "/api/record-chain-intake-gateway.v1.json",
        "zero-clone",
        "BUILDER_USAGE_UNCLEAR",
        "doctor --file submission.json",
    ],
    "gateway-workflows.md": [
        "/external-agent-quickstart/",
        "/zero-clone-builders/",
        "/api/record-chain-intake-gateway.v1.json",
        "/api/external-agent-operation-examples.v1.json",
    ],
    "external-agent-quickstart.md": [
        "without cloning the full repository",
        "/record-chain/preflight",
        "/record-chain/submit",
        "/api/agent-start.v2.json",
        "/api/record-chain-intake-gateway.v1.json",
        "/api/external-agent-operation-examples.v1.json",
        "BUILDER_USAGE_UNCLEAR",
        "doctor --file submission.json",
    ],
    "zero-clone-builders.md": [
        "without cloning the full repository",
        "canonical builder",
        "/api/record-chain-builder-bundles.v1.json",
        "/external-agent-quickstart/",
    ],
}

FORBIDDEN_ACTIVE_SNIPPETS = {
    "ai.txt": ["/external-agent-quickstart.md"],
    "gateway-workflows.md": ["Download individually if full clone is not possible"],
}


def main() -> int:
    errors: list[str] = []

    for label, path in FILES.items():
        if not path.exists():
            errors.append(f"{label}: file missing")
            continue
        text = path.read_text(encoding="utf-8")
        for required in REQUIRED_BY_FILE.get(label, []):
            if required not in text:
                errors.append(f"{label}: missing required docs alignment snippet: {required}")
        for forbidden in FORBIDDEN_ACTIVE_SNIPPETS.get(label, []):
            if forbidden in text:
                errors.append(f"{label}: forbidden stale docs snippet remains: {forbidden}")

    agent_start_path = FILES["api/agent-start.v2.json"]
    if agent_start_path.exists():
        data = json.loads(agent_start_path.read_text(encoding="utf-8"))
        protocol = data.get("builder_usage_safety_protocol")
        if not isinstance(protocol, dict):
            errors.append("agent-start API: missing builder_usage_safety_protocol object")
        else:
            if protocol.get("required_when_unclear") != "STOP_AND_RETURN_BUILDER_USAGE_UNCLEAR":
                errors.append("agent-start API: required_when_unclear mismatch")
            if "doctor_submission" not in (protocol.get("required_sequence_for_formal_records") or []):
                errors.append("agent-start API: missing doctor_submission step")

    if errors:
        print("FAIL: external-agent docs zero-clone alignment errors:")
        for error in errors:
            print("  -", error)
        return 1
    print("PASS: external-agent docs align with zero-clone, Builder fail-closed guidance, and Record-Chain Gateway endpoints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
