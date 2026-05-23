#!/usr/bin/env python3
"""Test that gateway-workflows.md and related docs contain required content."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def must_contain(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [n for n in needles if n not in text]
    if missing:
        raise AssertionError(f"{path} missing: {missing}")

def main() -> None:
    must_contain("gateway-workflows.md", [
        "permalink: /gateway-workflows/",
        "Gateway Workflows",
        "Route selection",
        "Payload generation",
        "Preflight validation",
        "Submission",
        "Error recovery",
        "Artifact custody",
        "/api/gateway-workflows.v1.json",
        "/api/gateway-artifact-custody.v1.json",
        "scripts/build_agent_declared_echo_payload.py",
        "scripts/build_agent_declared_archive_payload.py",
        "scripts/create_guardian_application.mjs",
        "scripts/build_guardian_listing_request_payload.py",
        "scripts/build_guardian_echo_payload.py",
        "Do not guess the builder",
        "Do not patch signed JSON",
        "/gateway/preflight",
        "/agent-submit",
    ])

    must_contain("agent-start.md", [
        "/gateway-workflows/",
        "/api/gateway-workflows.v1.json",
    ])

    must_contain("agent-submit.md", [
        "/gateway-workflows/",
    ])

    must_contain("external-agent-quickstart.md", [
        "/gateway-workflows/",
    ])

    must_contain("llms.txt", [
        "/gateway-workflows/",
        "/api/gateway-workflows.v1.json",
    ])

    print("PASS: test_gateway_workflow_docs")

if __name__ == "__main__":
    main()
