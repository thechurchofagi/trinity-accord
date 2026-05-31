#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def must_contain(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [n for n in needles if n not in text]
    if missing:
        raise AssertionError(f"{path} missing: {missing}")

def main() -> None:
    must_contain("agent-start.md", [
        "permalink: /agent-start/",
        "Gateway submission origin",
        "Do not guess the builder",
        "Do not patch signed JSON",
        "scripts/build_agent_declared_echo_payload.py",
        "scripts/build_agent_declared_archive_payload.py",
        "scripts/create_guardian_application.mjs",
        "scripts/build_guardian_listing_request_payload.py",
        "scripts/build_guardian_echo_payload.py",
        "/api/agent-start.v1.json",
        "/api/gateway-builder-route-map.v1.json",
    ])

    must_contain("agent-submit.md", [
        "/agent-start/",
        "Mandatory rule for V0\u2013V5 verification claims",
        "Pure Echo is separate",
    ])

    must_contain("external-agent-quickstart.md", [
        "/external-agent-copy-paste-examples/",
        "route-selector",
        "gateway-runtime-contract",
    ])

    must_contain("guardian-routes.md", [
        "permalink: /guardian-routes/",
        "Guardian-signed Echo",
        "guardian_presence_proof",
        "A registry number alone is not proof",
    ])

    must_contain("llms.txt", [
        "Gateway submission origin",
        "/agent-start/",
        "/api/agent-start.v1.json",
        "Do not guess the builder",
    ])

    print("PASS: test_agent_start_docs")

if __name__ == "__main__":
    main()
