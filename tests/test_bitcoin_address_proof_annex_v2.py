from __future__ import annotations

import json
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANNEX = ROOT / "evidence/bitcoin-address-proof-annex-v2"
TARGETS = ANNEX / "TARGETS.json"
CAPTURE = ANNEX / "verification/capture_address_wide_v2.py"
VERIFY = ANNEX / "verification/verify_address_wide_v2.py"
ADDRESS_MANIFEST = ROOT / "bitcoin-inscription-mirrors/address-wide/manifest.json"
V1_MANIFEST = ROOT / "evidence/bitcoin-inscription-proof-annex-v1/ANNEX-MANIFEST.json"
WORKFLOW = ROOT / ".github/workflows/capture-bitcoin-address-proof-annex-v2.yml"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_v2_scripts_compile():
    py_compile.compile(str(CAPTURE), doraise=True)
    py_compile.compile(str(VERIFY), doraise=True)


def test_target_partition_is_exact_8_plus_4_equals_current_12():
    targets = load(TARGETS)
    address = load(ADDRESS_MANIFEST)
    v1 = load(V1_MANIFEST)

    canonical = set(targets["canonical_original_ids"])
    formation = {
        item["ordinals_inscription_id"] for item in targets["formation_targets"]
    }
    inherited = {item["ordinals_inscription_id"] for item in v1["anchors"]}
    current = set(address["ids"])

    assert len(canonical) == 3
    assert len(formation) == 4
    assert len(inherited) == 8
    assert len(current) == address["count"] == 12
    assert canonical <= inherited
    assert formation.isdisjoint(canonical)
    assert formation.isdisjoint(inherited)
    assert inherited | formation == current

    for item in targets["formation_targets"]:
        assert item["classification"] == "pre_canonical_formation"
        assert item["canonical"] is False
        assert item["amends_canon"] is False


def test_current_archive_has_one_independent_metadata_payload_and_eleven_absences():
    address = load(ADDRESS_MANIFEST)
    present = [item for item in address["objects"] if item["inscription_metadata_present"]]
    absent = [item for item in address["objects"] if not item["inscription_metadata_present"]]
    assert len(present) == 1
    assert len(absent) == 11
    assert present[0]["id"] == (
        "8e81cf6054d37dc1f4606fa4f3fba238024292d72511fa70eeee693626271695i0"
    )
    assert present[0]["content_type"] == "image/webp"
    assert present[0]["inscription_metadata_length"] == 2941
    assert present[0]["inscription_metadata_sha256"] == (
        "1c51702f58b230caba573250769caecd0534f6c8002e16f2f182a16b19a27dcc"
    )


def test_v2_source_requires_witness_tag5_and_no_authority_escalation():
    capture = CAPTURE.read_text(encoding="utf-8")
    verify = VERIFY.read_text(encoding="utf-8")
    for text in (capture, verify):
        assert 'tag == b"\\x05"' in text
        assert "proof_inclusion_does_not_confer_authority" in text
        assert "same_address_does_not_imply_canonical" in text
    assert "ordered_concatenation_of_all_ordinals_tag_5_fields_exact_bytes" in capture
    assert "metadata witness coverage must be exactly 12/12" in verify
    assert "run_v1_verifier" in verify
    assert "verify_l2_v1" in verify
    assert "verify_l3_v1" in verify


def test_capture_workflow_is_output_isolated_and_pr_only():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: Capture Bitcoin address proof annex v2" in text
    assert "capture_address_wide_v2.py" in text
    assert "verify_address_wide_v2.py" in text
    assert "automation/bitcoin-address-proof-annex-v2" in text
    assert "pull-requests: write" in text
    assert "gh pr create" in text
    assert "git push origin HEAD:main" not in text
    # Generated proof material must not retrigger the network capture after merge.
    push_section = text.split("pull_request:", 1)[0]
    assert "proof-material" not in push_section
    assert "ANNEX-MANIFEST.json" not in push_section
