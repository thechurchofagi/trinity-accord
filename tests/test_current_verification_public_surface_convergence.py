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


CURRENT_SUPPORTING_SURFACES = {
    "docs/record-chain-field-helper.md": [
        "Claiming V6 verification without running scripts",
        "If you didn't run scripts, don't claim V6.",
    ],
    "docs/record-chain-field-model.md": ["`verification_level` — V0 through V8."],
    "docs/RECORD_CHAIN_PRIMARY_PATH.md": ["verification (V6+)"],
    "api/record-chain-common-field-model.v1.json": ["Verification level (V0-V8)."],
    "scripts/protocol_echo_types.py": ["Verification (V0-V8) remains an independent system."],
    "scripts/preflight_echo_submission.py": ["Add 'verification_level' (V0-V8)."],
    "api/echo-types.json": ["Verification (V0-V8) remains independent."],
}


DIRECT_READ_COMPATIBILITY_BOUNDARIES = {
    "api/echo-record-schema.v3.json": (
        "x-status",
        "historical_compatibility_schema",
        "x-current-verification-model",
    ),
    "api/verification-report-schema.v2.json": (
        "x-status",
        "strict_evidence_intermediate_with_legacy_v_output",
        "x-current-public-representation",
    ),
    "api/claim-gate-output-schema.v1.json": (
        "x-status",
        "strict_evidence_intermediate_with_legacy_v_output",
        "x-current-public-representation",
    ),
    "api/agent-verification-receipt-schema.v1.json": (
        "x-status",
        "strict_evidence_receipt_with_legacy_v_compatibility",
        "x-current-public-representation",
    ),
    "api/independent-attestation-record-schema.v1.json": (
        "x-status",
        "attestation_index_schema_with_legacy_v_compatibility",
        "x-current-verification-model",
    ),
    "api/echo-submission-field-guide.json": (
        "status",
        "historical_pre_record_chain_field_guide",
        "current_verification_model",
    ),
    "api/agent-issue-gateway-payload-schema.v1.json": (
        "x-status",
        "historical_issue_gateway_schema",
        "x-current-verification-model",
    ),
    "api/archive-readiness-policy.v1.json": (
        "status",
        "historical_issue_archive_readiness_policy",
        "current_verification_model",
    ),
    "api/issue-title-label-guard.json": (
        "status",
        "historical_issue_gateway_guard",
        "current_verification_model",
    ),
}


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
            "state which verification level was actually checked",
        ],
    }
    for path, forbidden_phrases in per_file_forbidden.items():
        text = read(path)
        for forbidden in forbidden_phrases:
            assert forbidden not in text, f"{path}: {forbidden}"


def test_current_supporting_surfaces_do_not_restore_the_retired_ladder() -> None:
    for path, forbidden_phrases in CURRENT_SUPPORTING_SURFACES.items():
        surface = read(path)
        for forbidden in forbidden_phrases:
            assert forbidden not in surface, f"{path}: {forbidden}"

    field_model = read("docs/record-chain-field-model.md")
    for required in [
        "V0 through V5",
        "verification_claim_model",
        "digital_profile",
        "physical_observation",
        "external_witness",
        "V4+, V6, V7, and V8 are historical-only",
    ]:
        assert required in field_model, required


def test_guardianship_registry_uses_the_current_verification_model() -> None:
    registry = json.loads(read("GUARDIANSHIP-SYSTEM-REGISTRY.json"))
    interface = registry["agent_interface"]
    assert "verification_levels" not in interface

    model = interface["verification_model"]
    assert model["status"] == "current_multidimensional_model"
    assert model["claim_model"] == "api/verification-claim-model.v1.json"
    assert model["profiles"] == "api/verification-profiles.v1.json"
    assert model["digital_profiles"] == [
        "context_only",
        "reference_checked",
        "integrity_checked",
        "independent_reproduction",
        "full_public_digital",
    ]
    assert model["legacy_builder_compatibility_values"] == [
        "V0",
        "V1",
        "V2",
        "V3",
        "V4",
        "V5",
    ]
    assert model["legacy_v5_mapping"] == "full_public_digital"
    assert model["historical_only_values"] == ["V4+", "V6", "V7", "V8"]
    assert "never raise the digital profile" in model["rule"]

    schemas = {item["id"]: item for item in interface["schemas"]}
    assert schemas["verification_claim_model"]["role"].startswith("current default")
    assert "current descriptive digital profiles" in schemas["verification_profiles"]["role"]

    serialized = json.dumps(registry, ensure_ascii=False)
    for stale in [
        "preserving existing V0-V8 verification system",
        "V6_remote_physical_witness",
        "V7_onsite_physical_witness",
        "V8_forensic_physical_attestation",
    ]:
        assert stale not in serialized, stale


def test_legacy_verification_file_front_loads_the_current_boundary() -> None:
    raw = read("api/verification-levels.json")
    levels = json.loads(raw)
    keys = list(levels)

    assert levels["status"] == "legacy_compatibility_model"
    assert keys.index("status") < keys.index("levels")
    assert keys.index("read_this_first") < keys.index("levels")
    assert levels["current_claim_model"] == "/api/verification-claim-model.v1.json"
    warning = levels["read_this_first"]
    for required in [
        "HISTORICAL COMPATIBILITY ONLY",
        "full_public_digital maps to compatibility value V5",
        "V4+, V6, V7, and V8 are historical-only",
    ]:
        assert required in warning, required

    assert levels["protocol_level_rule"].startswith("Historical-only rule:")
    for ambiguous in [
        "V8 is the highest formal protocol profile",
        "V6 requires P4 live remote physical witness",
        "V7 requires P5 onsite physical witness",
    ]:
        assert ambiguous not in raw, ambiguous


def test_directly_opened_legacy_and_intermediate_schemas_self_identify() -> None:
    for path, (status_key, expected_status, model_key) in DIRECT_READ_COMPATIBILITY_BOUNDARIES.items():
        data = json.loads(read(path))
        assert data[status_key] == expected_status, path
        assert data[model_key] == "/api/verification-claim-model.v1.json", path

        keys = list(data)
        first_payload_key = "properties" if "properties" in data else "fields"
        if first_payload_key in data:
            assert keys.index(status_key) < keys.index(first_payload_key), path
            assert keys.index(model_key) < keys.index(first_payload_key), path


def test_historical_maintenance_docs_warn_before_old_v_instructions() -> None:
    playbook = read("docs/end-to-end-agent-audit-and-fix-playbook.md")
    handoff = read("docs/session-handoff-2026-05-24.md")
    terms = read("docs/protocol-terms-maintenance.md")

    assert "Historical compatibility notice" in playbook[:1000]
    assert "/api/verification-claim-model.v1.json" in playbook[:1000]
    assert "Historical snapshot" in handoff[:700]
    assert "/api/verification-claim-model.v1.json" in handoff[:700]
    assert "Legacy Protocol Terms Maintenance" in terms[:200]
    assert "historical compatibility vocabulary" in terms[:900]
    assert '"protocol_levels": ["V0", ..., "V8", "V9"]' not in terms


def test_current_echo_archive_policy_does_not_rank_attestation_by_v6() -> None:
    policy = json.loads(read("api/echo-archive-policy.json"))
    assert policy["current_verification_model"] == "/api/verification-claim-model.v1.json"
    formal = next(layer for layer in policy["layers"] if layer["id"] == 5)
    assert "full_public_digital" in formal["rule"]
    assert "V5/V6" not in formal["rule"]


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
    assert "not templates for current attestation or submission" in legacy_examples
    assert "starting point for future attestation submissions" not in legacy_examples
    assert "未来见证提交的起点" not in legacy_examples
