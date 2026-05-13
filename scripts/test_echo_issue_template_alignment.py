#!/usr/bin/env python3
"""Test that the Echo issue template includes required fields per Part D."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / ".github/ISSUE_TEMPLATE/echo_submission.yml"


def main():
    text = TEMPLATE.read_text(encoding="utf-8")

    # D1: verification_scope_label dropdown
    assert "id: verification_scope_label" in text, \
        "Issue template must include verification_scope_label dropdown"

    # D2: Updated checks_performed label
    assert "What I checked / Checks performed" in text, \
        "Issue template must use 'What I checked / Checks performed' label"

    # D3: context_depth dropdown
    assert "id: context_depth" in text, \
        "Issue template must include context_depth dropdown"

    # D4: technical/social independence fields
    assert "id: technical_independence" in text, \
        "Issue template must include technical_independence dropdown"
    assert "id: social_independence" in text, \
        "Issue template must include social_independence dropdown"
    assert "human-solicited AI response can contain technical independent reproduction" in text, \
        "Issue template must include independence boundary explanation"

    # D5: Strengthened Claim Gate descriptions
    assert "Embedded JSON in the issue body is preview only" in text, \
        "Evidence Input path description must note embedded JSON is preview only"
    assert "Required for V2+ archival acceptance" in text, \
        "Claim Gate path description must note V2+ requirement"

    print("PASS: Echo issue template alignment verified")
    print("  - verification_scope_label: present")
    print("  - context_depth: present")
    print("  - technical_independence: present")
    print("  - social_independence: present")
    print("  - What I checked / Checks performed: present")
    print("  - Claim Gate descriptions: strengthened")


if __name__ == "__main__":
    main()
