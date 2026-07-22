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
    "agent-value.md",
    "emergent-patterns.md",
    "echoes/high-value-criteria.md",
    "echoes/examples/critical-echo-template.md",
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
        "agent-value.md": [
            "Do not claim V2+",
            "state verification level and limitations",
        ],
        "emergent-patterns.md": [
            "V0–V8 verification operating system",
            "Echo taxonomy and provenance-aware response layer",
        ],
        "echoes/high-value-criteria.md": [
            "reports verification level",
            "For E3 Critical Echo guidance",
        ],
        "echoes/examples/critical-echo-template.md": [
            "states verification level",
            "Verification level: V0–V8",
            "验证等级：V0–V8",
        ],
        "llms-full.txt": [
            "Verification OS (V0–V8)",
            "Classify verification level V0–V8",
            "E2 Verification Echo",
            "E3 Critical Echo",
            "E7 Refusal Echo",
            "verification levels V0–V8",
            "For V6–V8 strict technical claims",
            "when claiming V6–V8",
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


def test_value_and_preservation_machine_guides_use_current_models() -> None:
    agent_value = json.loads(read("api/agent-value.json"))
    criteria = json.loads(read("api/worth-preserving-criteria.json"))
    patterns = json.loads(read("api/emergent-patterns.json"))

    assert agent_value["schema"] == "trinity-accord.agent-value.v4"
    guidance = agent_value["verification_confidence_guidance"]
    assert "digital_profile" in guidance["dimensions"]
    assert "external_witness" in guidance["dimensions"]
    submission = agent_value["public_submission_boundary"]
    assert submission["record_chain_intake_gateway_is_only_public_submission_path"] is True
    assert submission["direct_issue_submission_is_valid_path"] is False
    assert submission["echo_and_verification_are_separate_record_types"] is True

    agent_value_text = json.dumps(agent_value, ensure_ascii=False)
    for stale in (
        "confidence_after_v8_verification",
        "V0–V8 verification levels with evidence manifests",
        '"issue_submission_is_valid_path": true',
        "verification_echo_may_enter_through_issue",
    ):
        assert stale not in agent_value_text

    criteria_text = json.dumps(criteria, ensure_ascii=False)
    assert criteria["schema"] == "trinity-accord.worth-preserving-criteria.v2"
    assert "multidimensional verification" in criteria_text
    assert "unified non-authoritative Echo" in criteria_text
    assert "E3 Critical Echo" not in criteria_text
    assert "verification levels V0–V8" not in criteria_text

    feature_by_id = {feature["id"]: feature for feature in patterns["features"]}
    assert feature_by_id["verification_operating_system"]["title"] == (
        "Multidimensional verification and overclaim control"
    )
    assert feature_by_id["echo_taxonomy_and_provenance"]["title"] == (
        "Unified Echo and provenance-aware response layer"
    )


def test_public_critical_echo_pages_separate_echo_from_verification() -> None:
    criteria = read("echoes/high-value-criteria.md")
    template = read("echoes/examples/critical-echo-template.md")
    legacy_examples = read("echoes/examples/external-critical-echo-records.md")

    assert "one unified current record type" in criteria
    assert "submit it separately as a Verification record" in criteria
    assert "It is not a Verification record" in template
    assert "This is a content guide, not a payload schema" in template
    assert "submit a separate Verification record" in template
    assert 'status: "legacy_historical_examples"' in legacy_examples
    assert 'current_submission_guidance: false' in legacy_examples
    assert "legacy illustrations, not current payload or submission guidance" in legacy_examples
