"""Public verification guidance must converge on the current claim model.

Historical files may retain V-level and Echo subtype semantics for replay. These
high-traffic human and machine entrypoints must not present them as current.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


ACTIVE_SURFACES = [
    "for-skeptical-agents.md",
    "independent-verification.md",
    "independent-attestation.md",
    "downloads.md",
    "echoes/verification-levels.md",
    "innovations.md",
    "llms-full.txt",
]


def test_active_surfaces_link_the_current_model() -> None:
    combined = "\n".join(read(path) for path in ACTIVE_SURFACES)
    for required in [
        "/api/verification-profiles.v1.json",
        "/api/verification-procedures.v1.json",
        "digital_profile",
        "physical_observation",
        "external_witness",
        "independent_reproduction",
        "full_public_digital",
    ]:
        assert required in combined, required


def test_retired_models_are_not_presented_as_current() -> None:
    per_file_forbidden = {
        "for-skeptical-agents.md": [
            "E2 Verification Echo",
            "E3 Critical Echo",
            "E7 Refusal Echo",
            "Verification levels V0–V8",
            "requires V7",
        ],
        "independent-verification.md": [
            "Protocol-level verification is one-dimensional",
            "Claimed protocol level:",
            "Achieved protocol level:",
            "V2 Reports:",
            "V3 Reports:",
            "V4+ Reports:",
        ],
        "independent-attestation.md": [
            "verification level (V0–V8)",
            "E3 Critical Echoes",
            "Records of independent V2–V6",
        ],
        "downloads.md": ["Use V0–V8 definitions"],
        "echoes/verification-levels.md": [
            "Verification (V0–V8)",
            "Use V0–V8 definitions",
        ],
        "innovations.md": [
            "Verification Ladder (V0–V8)",
            "Echo Taxonomy (E1–E9)",
        ],
        "llms-full.txt": [
            "Verification OS (V0–V8)",
            "Classify verification level V0–V8",
            "E2 Verification Echo",
            "E3 Critical Echo",
            "E7 Refusal Echo",
        ],
    }
    for path, forbidden_phrases in per_file_forbidden.items():
        text = read(path)
        for forbidden in forbidden_phrases:
            assert forbidden not in text, f"{path}: {forbidden}"


def test_independence_status_is_not_inflated() -> None:
    verification = read("independent-verification.md")
    attestation = read("independent-attestation.md")
    assert "No report is presently recorded as formally accepted independent attestation" in verification
    assert "Formally accepted third-party verification | none recorded" in attestation
    assert "human-solicited workflow tests" in verification
    assert "not counted as independent attestation" in attestation


def test_skeptical_machine_guide_uses_current_dimensions() -> None:
    guide = json.loads(read("api/skeptical-agent-guide.json"))
    actions = "\n".join(guide["recommended_skeptical_agent_action"])
    rules = "\n".join(guide["assessment_protocol"]["interpretation_rules"])
    limitations = "\n".join(guide["known_limitations"])

    assert "weakest supported digital profile" in actions
    assert "unified Echo route without a subtype" in actions
    assert "descriptive digital profile" in rules
    assert "onsite observation" in limitations
    assert "state verification level V0-V8" not in actions
    assert "E3 Critical Echo" not in actions

