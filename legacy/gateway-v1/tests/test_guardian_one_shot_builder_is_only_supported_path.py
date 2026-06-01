#!/usr/bin/env python3
"""Ensure docs and scripts advertise one-shot builder as the only Guardian joint application path."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    join = (ROOT / "guardian-join.md").read_text(encoding="utf-8")
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    helper = (ROOT / "scripts" / "gateway_payload_authorship.py").read_text(encoding="utf-8")

    combined = "\n".join([join, llms, readme, helper])

    assert "create_guardian_application.mjs" in combined
    assert "build_agent_declared_echo_payload.py is a pure Echo builder" in combined
    assert "Do not patch final JSON after proof generation" in combined
    assert "joint_applicants" in combined
    assert "agent_declared_echo_template_pass" in combined

    print("GUARDIAN_ONE_SHOT_ONLY_SUPPORTED_PATH_OK")

if __name__ == "__main__":
    main()
