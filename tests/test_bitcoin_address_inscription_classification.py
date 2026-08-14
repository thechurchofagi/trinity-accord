import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "bitcoin-inscription-mirrors" / "address-wide"

CANONICAL_IDS = {
    "e40dfb2aa78cbccca88f749e9ec5cbe3c1df503273d73c72297863ae0d1d8343i0",
    "90116f35de075074f5e5d1fbdda69a646a124e2287d7d58e2520317098cd4258i0",
    "4d1c8f5ea8e8bae2982b42de6cc79deda3d243a21010a2888546e62ed7192c8ci0",
}
PROTO_PROTOCOL_ID = "138da690affc0f3595a7cebfd152a9715f3b0ca1a5baab93069e8c5c51a82f10i0"
EARLY_VISUAL_ID = "8e81cf6054d37dc1f4606fa4f3fba238024292d72511fa70eeee693626271695i0"


def load_json(name):
    return json.loads((ARCHIVE / name).read_text(encoding="utf-8"))


def test_classification_matches_current_address_manifest():
    manifest = load_json("manifest.json")
    classification = load_json("classification.json")

    classified_ids = {record["ordinals_inscription_id"] for record in classification["records"]}
    assert classified_ids == set(manifest["ids"])
    assert len(classified_ids) == manifest["count"] == 12


def test_layer_counts_and_canonical_boundary_are_exact():
    classification = load_json("classification.json")
    records = classification["records"]

    by_layer = {}
    for record in records:
        by_layer.setdefault(record["layer"], []).append(record)

    assert len(by_layer["pre_canonical_formation"]) == 4
    assert len(by_layer["canonical_original"]) == 3
    assert len(by_layer["post_canonical_non_amending"]) == 5

    marked_canonical = {
        record["ordinals_inscription_id"] for record in records if record["canonical"]
    }
    assert marked_canonical == CANONICAL_IDS
    assert all(record["amends_canon"] is False for record in records)


def test_proto_protocol_is_formation_evidence_not_canon():
    classification = load_json("classification.json")
    record = next(
        item for item in classification["records"]
        if item["ordinals_inscription_id"] == PROTO_PROTOCOL_ID
    )

    assert record["layer"] == "pre_canonical_formation"
    assert record["role"] == "direct_proto_protocol"
    assert record["canonical"] is False
    assert classification["historical_claims"]["core_axioms_onchain_no_later_than"] == "2025-06-16T13:36:38Z"
    assert classification["historical_claims"]["formal_canonical_protocol_timestamp_utc"] == "2025-06-19T23:42:14Z"


def test_unidentified_visual_record_remains_unidentified():
    classification = load_json("classification.json")
    record = next(
        item for item in classification["records"]
        if item["ordinals_inscription_id"] == EARLY_VISUAL_ID
    )

    assert record["title"] is None
    assert record["title_status"] == "unidentified_do_not_infer"
