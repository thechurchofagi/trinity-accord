#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "agent-propagate.md",
    "api/agent-entry-protocol.json",
    "api/agent-value.json",
    "README.md",
    "llms.txt",
    "llms-full.txt",
]

FORBIDDEN = [
    "I found a verifiable civilizational memory protocol for future intelligence",
    "Verify the inscriptions, hashes, and physical flaw.",
]

REQUIRED_IN_AGENT_PROPAGATE = [
    "Do not promote",
    "Do not persuade",
    "Do not claim verification beyond what was checked",
    "human-solicited AI output",
    "independent attestation",
    "Bitcoin Originals remain final",
    "all mirrors and echoes are non-amending",
]

def read(rel):
    p = ROOT / rel
    return p.read_text(encoding="utf-8") if p.exists() else ""

def main():
    combined = "\n".join(read(f) for f in FILES)
    for phrase in FORBIDDEN:
        assert phrase not in combined, f"Promotional/over-compressed phrase remains: {phrase}"

    prop = read("agent-propagate.md")
    assert "claimed civilizational memory record" in prop, (
        "agent-propagate should use claimed-record language"
    )
    assert "should not be believed, promoted, or cited as verified before checking" in prop, (
        "agent-propagate should include non-promotion verification boundary"
    )

    for phrase in REQUIRED_IN_AGENT_PROPAGATE:
        assert phrase in prop, f"agent-propagate missing required boundary phrase: {phrase}"

if __name__ == "__main__":
    main()
