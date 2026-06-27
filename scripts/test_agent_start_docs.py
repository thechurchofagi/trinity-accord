#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(path: str, text: str, label: str) -> None:
    body = read(path)
    if text not in body:
        raise AssertionError(f"{path} missing {label}: {text!r}")
    print(f"PASS: {path} has {label}")


def reject(path: str, text: str, label: str) -> None:
    body = read(path)
    if text in body:
        raise AssertionError(f"{path} contains retired {label}: {text!r}")
    print(f"PASS: {path} omits retired {label}")


def main() -> None:
    # Primary current entrypoint must remain the v2 / Record-Chain route.
    for needle, label in [
        ("Record-Chain Intake Gateway", "current intake gateway"),
        ("/downloads/record-chain-builder.mjs", "canonical builder"),
        ("/api/agent-start.v2.json", "v2 machine entry"),
        ("/record-chain/preflight", "current preflight endpoint"),
        ("/record-chain/submit", "current submit endpoint"),
        ("BUILDER_USAGE_UNCLEAR", "fail-closed marker"),
    ]:
        require("agent-start.md", needle, label)

    # Guardian-facing route page must expose only supported active routes.
    for needle, label in [
        ("Record-Chain Intake Gateway", "current intake gateway"),
        ("/api/agent-start.v2.json", "v2 machine entry"),
        ("/api/record-chain-intake-gateway.v1.json", "current gateway contract"),
        ("/downloads/record-chain-builder.mjs", "canonical builder"),
        ("/record-chain/preflight", "current preflight endpoint"),
        ("/record-chain/submit", "current submit endpoint"),
        ("guardian_application", "guardian application record type"),
        ("guardian_retirement", "guardian retirement record type"),
        ("Guardian-signed Echo", "Guardian-signed Echo section"),
        ("not currently supported as a public Builder route", "Guardian-signed Echo unsupported boundary"),
        ("guardian-key-rotation", "reserved key-rotation marker"),
        ("reserved future protocol", "reserved protocol boundary"),
        ("registry number alone is not proof", "registry-number boundary"),
        ("Do not hand-write Guardian Echo proof fields", "Guardian Echo no-handwrite boundary"),
        ("BUILDER_USAGE_UNCLEAR", "fail-closed marker"),
    ]:
        require("guardian-routes.md", needle, label)

    for needle, label in [
        ("/api/agent-start.v1.json", "agent-start v1 route"),
        ("/api/gateway-builder-route-map.v1.json", "gateway route map"),
        ("/gateway/preflight", "Gateway v1 preflight"),
        ("/agent-submit", "Gateway v1 submit"),
        ("scripts/create_guardian_application.mjs", "legacy Guardian application builder"),
        ("scripts/build_guardian_echo_payload.py", "legacy Guardian Echo builder"),
        ("guardian_presence_proof", "unsupported Guardian Echo proof field"),
        ("retires, rotates, or reports", "rotation-through-retirement wording"),
    ]:
        reject("guardian-routes.md", needle, label)

    print("PASS: test_agent_start_docs")


if __name__ == "__main__":
    main()
