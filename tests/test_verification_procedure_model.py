import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_current_profile_and_procedure_ids_match():
    profiles = load_json("api/verification-profiles.v1.json")
    procedures = load_json("api/verification-procedures.v1.json")
    claim_model = load_json("api/verification-claim-model.v1.json")

    profile_ids = {item["id"] for item in profiles["digital_profiles"]}
    procedure_ids = set(procedures["digital_profile_procedures"])
    claim_ids = set(claim_model["required_dimensions"]["digital_profile"]["values"])

    expected = {
        "context_only",
        "reference_checked",
        "integrity_checked",
        "independent_reproduction",
        "full_public_digital",
    }
    assert profile_ids == expected
    assert procedure_ids == expected
    assert claim_ids == expected


def test_current_physical_and_witness_values_match_claim_model():
    profiles = load_json("api/verification-profiles.v1.json")
    procedures = load_json("api/verification-procedures.v1.json")
    claim_model = load_json("api/verification-claim-model.v1.json")

    physical_profiles = {item["id"] for item in profiles["physical_observation"]["values"]}
    physical_procedures = set(procedures["physical_observation_procedures"])
    physical_claim = set(claim_model["required_dimensions"]["physical_observation"]["values"])

    witness_profiles = {item["id"] for item in profiles["external_witness"]["values"]}
    witness_procedures = set(procedures["external_witness_procedures"])
    witness_claim = set(claim_model["required_dimensions"]["external_witness"]["values"])

    assert physical_profiles == physical_procedures == physical_claim
    assert witness_profiles == witness_procedures == witness_claim


def test_new_submission_legacy_boundary_is_consistent():
    procedures = load_json("api/verification-procedures.v1.json")
    levels = load_json("api/verification-levels.json")
    guidance = load_json("downloads/record-chain-agent-field-guidance.v1.json")

    allowed = ["V0", "V1", "V2", "V3", "V4", "V5"]
    retired = ["V4+", "V6", "V7", "V8"]

    assert procedures["legacy_boundary"]["allowed_builder_values"] == allowed
    assert procedures["legacy_boundary"]["forbidden_for_new_public_submissions"] == retired
    assert levels["status"] == "legacy_compatibility_model"
    assert levels["new_submission_policy"]["allowed_legacy_v_values"] == allowed
    assert levels["new_submission_policy"]["forbidden_legacy_v_values"] == retired
    assert guidance["record_types"]["verification"]["public_verification_level_limit"] == "V0-V5 only"


def test_active_human_entrypoints_use_current_model():
    verify = read("verify.md")
    agent = read("agent-verify.md")
    simple = read("agent-verify-simple.md")
    procedures_page = read("verification-procedures.md")

    for text in (verify, agent, simple, procedures_page):
        assert "/api/verification-procedures.v1.json" in text
        assert "independent_reproduction" in text
        assert "full_public_digital" in text

    assert "## Verification OS (V0–V8)" not in verify
    assert "reserved for future/internal use" not in simple
    assert "V4+, V6, V7, and V8 are historical-only" in agent


def test_active_machine_navigation_does_not_offer_retired_v_as_current_level():
    quick = load_json("api/verification-quick-map.json")
    cheatsheet = load_json("api/agent-verification-cheatsheet.v1.json")
    protocol = load_json("api/protocol-verification-profiles.json")
    recipes = load_json("api/verification-recipes.json")
    materials = load_json("api/verification-materials.json")

    assert quick["status"] == "current_verification_navigation"
    assert cheatsheet["status"] == "current_agent_verification_cheatsheet"
    assert protocol["status"] == "current_profile_claim_compatibility_rules"
    assert recipes["status"] == "current_non_authoritative_verification_guidance"
    assert materials["status"] == "current_verification_materials_index"

    current_ids = {item["id"] for item in protocol["profiles"]}
    assert current_ids == {
        "context_only",
        "reference_checked",
        "integrity_checked",
        "independent_reproduction",
        "full_public_digital",
    }

    for recipe in recipes["recipes"]:
        assert recipe["digital_profile"] in current_ids
        assert recipe.get("legacy_builder_values", ["V0"])[0] not in {"V4+", "V6", "V7", "V8"}


def test_chronicle_materials_do_not_restore_fixed_stage_model():
    materials = load_json("api/verification-materials.json")
    chronicle = materials["chronicle_context"]

    assert "seven_stage_narrative" not in chronicle["contains"]
    assert "calendar-quarter navigation" in chronicle["contains"]
    assert "overlapping descriptive categories" in chronicle["contains"]
    assert "No current fixed five-stage, seven-stage, or other fixed-stage model" in chronicle["boundary"]


def test_machine_procedures_define_executable_steps_and_downgrades():
    procedures = load_json("api/verification-procedures.v1.json")

    assert len(procedures["universal_workflow"]) == 11
    for profile_id, profile in procedures["digital_profile_procedures"].items():
        assert profile["minimum_steps"], profile_id
        assert profile.get("required_evidence"), profile_id

    assert procedures["relationship_procedures"]["hashes"]["steps"]
    assert procedures["relationship_procedures"]["signs_digest"]["steps"]
    assert procedures["relationship_procedures"]["timestamps_digest"]["steps"]
    assert procedures["relationship_procedures"]["notarially_records_process"]["steps"]
    assert procedures["downgrade_rules"]


def main() -> int:
    tests = [
        test_current_profile_and_procedure_ids_match,
        test_current_physical_and_witness_values_match_claim_model,
        test_new_submission_legacy_boundary_is_consistent,
        test_active_human_entrypoints_use_current_model,
        test_active_machine_navigation_does_not_offer_retired_v_as_current_level,
        test_chronicle_materials_do_not_restore_fixed_stage_model,
        test_machine_procedures_define_executable_steps_and_downgrades,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print("VERIFICATION_PROCEDURE_MODEL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
