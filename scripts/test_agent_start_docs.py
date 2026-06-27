#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RETIRED_AGENT_START_TOKENS = [
    "scripts/build_agent_declared_echo_payload.py",
    "scripts/build_agent_declared_archive_payload.py",
    "scripts/create_guardian_application.mjs",
    "/api/gateway-builder-route-map.v1.json",
]

RETIRED_GUARDIAN_ROUTE_TOKENS = [
    "/api/agent-start.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/gateway/preflight",
    "/agent-submit",
    "scripts/create_guardian_application.mjs",
    "scripts/build_guardian_echo_payload.py",
]


def must_contain(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [n for n in needles if n not in text]
    if missing:
        raise AssertionError(f"{path} missing: {missing}")
    print(f"PASS: {path} contains required current-route text")


def must_not_contain(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    present = [n for n in needles if n in text]
    if present:
        raise AssertionError(f"{path} must not contain retired active-route text: {present}")
    print(f"PASS: {path} contains no retired active-route text")


def main() -> None:
    must_contain("agent-start.md", [
        "permalink: /agent-start/",
        "Record-Chain Intake Gateway",
        "/downloads/record-chain-builder.mjs",
        "/api/agent-start.v2.json",
        "/api/record-chain-builder-bundles.v1.json",
        "/record-chain/preflight",
        "/record-chain/submit",
        "BUILDER_USAGE_UNCLEAR",
    ])
    must_not_contain("agent-start.md", RETIRED_AGENT_START_TOKENS)

    must_contain("agent-submit.md", [
        "/agent-start/",
        "Mandatory rule for V0–V5 verification claims",
        "Pure Echo is separate",
    ])

    must_contain("external-agent-quickstart.md", [
        "/agent-first-contact/",
        "/api/agent-start.v2.json",
        "/api/record-chain-intake-gateway.v1.json",
        "/downloads/record-chain-builder.mjs",
        "BUILDER_USAGE_UNCLEAR",
    ])

    must_contain("guardian-routes.md", [
        "permalink: /guardian-routes/",
        "Record-Chain Intake Gateway",
        "/api/agent-start.v2.json",
        "/api/record-chain-intake-gateway.v1.json",
        "/downloads/record-chain-builder.mjs",
        "/record-chain/preflight",
        "/record-chain/submit",
        "guardian_application",
        "guardian_retirement",
        "Guardian-signed Echo",
        "guardian_presence_proof",
        "A registry number alone is not proof",
        "BUILDER_USAGE_UNCLEAR",
    ])
    must_not_contain("guardian-routes.md", RETIRED_GUARDIAN_ROUTE_TOKENS)

    must_contain("llms.txt", [
        "/agent-start/",
        "/api/agent-start.v2.json",
        "/api/record-chain-intake-gateway.v1.json",
        "/downloads/record-chain-builder.mjs",
        "BUILDER_USAGE_UNCLEAR",
    ])

    print("PASS: test_agent_start_docs")


if __name__ == "__main__":
    main()
