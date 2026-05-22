#!/usr/bin/env python3
"""Check Guardian docs do not retain stale manual/00001/PR-only instructions."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    join = (ROOT / "guardian-join.md").read_text(encoding="utf-8")
    alliance = (ROOT / "guardian-alliance.md").read_text(encoding="utf-8")
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for name, text in [
        ("guardian-join.md", join),
        ("guardian-alliance.md", alliance),
        ("llms.txt", llms),
        ("README.md", readme),
    ]:
        require("00100" in text, f"{name} missing ordinary automatic start 00100")
        require("00001" in text and "00099" in text, f"{name} missing reserved range 00001-00099")
        require("node scripts/create_guardian_application.mjs" in text, f"{name} missing Stage 1 builder")
        require("python3 scripts/build_guardian_listing_request_payload.py" in text, f"{name} missing Stage 2 listing builder")

    stale_phrases = [
        "maintainer review required before merge",
        "The automation creates a PR only. It does not directly merge to `main`.",
        "after merge: `active_registered_guardian / 00001`",
        "organization, or another allowed type",
    ]
    for phrase in stale_phrases:
        require(phrase not in join, f"guardian-join.md still contains stale phrase: {phrase}")

    require("python3 scripts/build_agent_declared_echo_payload.py \\" not in join, "guardian-join.md still exposes old pure Echo Guardian builder command")
    require("not Verification Echo" in llms or "not Verification Echoes" in llms, "llms.txt missing Guardian vs Verification Echo disambiguation")

    print("GUARDIAN_DOCS_CONVERGENCE_OK")


if __name__ == "__main__":
    main()
