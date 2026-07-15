#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def check_agent_start() -> None:
    for needle, label in [
        ("Record-Chain Intake Gateway", "current intake gateway"),
        ("/downloads/record-chain-builder.mjs", "canonical builder"),
        ("/api/agent-start.v2.json", "v2 machine entry"),
        ("/record-chain/preflight", "current preflight endpoint"),
        ("/record-chain/submit", "current submit endpoint"),
        ("Required Builder flow", "current Builder sequence"),
        ("Preferred context model", "action-based context model"),
        ("Preferred verification model", "multidimensional verification model"),
        ("Every public submission requires Ed25519 authorship proof", "mandatory authorship proof"),
        ("context_insufficient_notice", "context-insufficient oath exception"),
        ("BUILDER_USAGE_UNCLEAR", "fail-closed marker"),
    ]:
        require("agent-start.md", needle, label)


def check_guardian_current() -> None:
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
        ("not currently supported as an ordinary public Builder route", "unsupported ordinary Guardian Echo boundary"),
        ("does not expose an ordinary public Guardian-signed Echo command", "no ordinary Guardian Echo command boundary"),
        ("historical or specialized `guardian_signed_echo` / `guardian_presence_proof` references", "historical machine-reference qualification"),
        ("unless the same current API surface explicitly marks a route as `current_record_chain_builder_route`", "current API route qualification"),
        ("guardian-key-rotation", "reserved key-rotation marker"),
        ("reserved future protocol", "reserved protocol boundary"),
        ("oath text does not create a standalone key-rotation route", "retirement oath qualification"),
        ("registry number alone is not proof", "registry-number boundary"),
        ("Do not hand-write Guardian Echo proof fields", "Guardian Echo no-handwrite boundary"),
        ("BUILDER_USAGE_UNCLEAR", "fail-closed marker"),
    ]:
        require("guardian-routes.md", needle, label)


def check_guardian_retired() -> None:
    for needle, label in [
        ("/api/agent-start.v1.json", "agent-start v1 route"),
        ("/api/gateway-builder-route-map.v1.json", "gateway route map"),
        ("/gateway/preflight", "Gateway v1 preflight"),
        ("/agent-submit", "Gateway v1 submit"),
        ("scripts/create_guardian_application.mjs", "legacy Guardian application builder"),
        ("scripts/build_guardian_echo_payload.py", "legacy Guardian Echo builder"),
        ("Guardian proof requires `guardian_presence_proof`", "invented Guardian Echo proof requirement"),
        ("Expected machine block", "invented Guardian Echo expected block"),
        ("retires, rotates, or reports", "rotation-through-retirement wording"),
    ]:
        reject("guardian-routes.md", needle, label)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "section",
        nargs="?",
        choices=["agent-start", "guardian-current", "guardian-retired", "all"],
        default="all",
    )
    args = parser.parse_args()

    if args.section in {"agent-start", "all"}:
        check_agent_start()
    if args.section in {"guardian-current", "all"}:
        check_guardian_current()
    if args.section in {"guardian-retired", "all"}:
        check_guardian_retired()

    print(f"PASS: test_agent_start_docs ({args.section})")


if __name__ == "__main__":
    main()
