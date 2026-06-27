#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def must_contain(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [n for n in needles if n not in text]
    if missing:
        raise AssertionError(f"{path} missing: {missing}")


def must_not_contain(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    present = [n for n in needles if n in text]
    if present:
        raise AssertionError(f"{path} must not contain retired active-route text: {present}")


def main() -> None:
    must_contain("agent-start.md", [
        "permalink: /agent-start/",
        "Gateway submission origin",
        "Do not guess the builder",
        "Do not patch signed JSON",
        "/downloads/record-chain-builder.mjs",
        "/api/agent-start.v2.json",
        "/api/record-chain-intake-gateway.v1.json",
        "/api/record-chain-builder-bundles.v1.json",
        "Chronicle / Human Witness route",
        "/nft-text-descriptions/CHRONICLE-MUSIC-TABLE.md",
    ])
    must_not_contain("agent-start.md", [
        "scripts/build_agent_declared_echo_payload.py",
        "scripts/build_agent_declared_archive_payload.py",
        "scripts/create_guardian_application.mjs",
    ])

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
        "Guardian-signed Echo",
        "guardian_presence_proof",
        "A registry number alone is not proof",
    ])

    must_contain("llms.txt", [
        "/agent-start/",
        "/api/agent-start.v2.json",
        "/api/record-chain-intake-gateway.v1.json",
        "/downloads/record-chain-builder.mjs",
        "Chronicle / Human Witness status",
        "Do not guess the builder" if False else "BUILDER_USAGE_UNCLEAR",
    ])

    print("PASS: test_agent_start_docs")


if __name__ == "__main__":
    main()
