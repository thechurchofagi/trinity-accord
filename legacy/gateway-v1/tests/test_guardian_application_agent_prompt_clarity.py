#!/usr/bin/env python3
"""Ensure docs tell external agents to use one-shot builder and not hand-fill proof fields."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    join = read("guardian-join.md")
    llms = read("llms.txt")
    readme = read("README.md")

    combined = "\n".join([join, llms, readme])

    required = [
        "scripts/create_guardian_application.mjs",
        "Do not hand-calculate",
        "Do not hand-fill proof fields",
        "guardian_presence_proof",
        "authorship_proof",
        "guardian_registry_number",
        "Private keys",
        "joint_human_ai",
        "human_with_ai_agent",
    ]

    for item in required:
        require(item in combined, f"missing required external-agent clarity text: {item}")

    forbidden = [
        "hand-write guardian_presence_proof",
        "hand-write authorship_proof",
        "manually calculate signed_payload_sha256",
        "include guardian_registry_number in payload",
    ]

    for item in forbidden:
        require(item not in combined.lower(), f"forbidden confusing wording present: {item}")

    print("GUARDIAN_APPLICATION_AGENT_PROMPT_CLARITY_OK")


if __name__ == "__main__":
    main()
