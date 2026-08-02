import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "preservation" / "repository-capsule-arweave-mirror-81b151245d70.json"
CATALOG_PATH = ROOT / "preservation" / "recovery-catalog.json"

EXPECTED = {
    "txid": "42UQsjG7gcUs5mFu9ZcwN6sYbskR533q_SpnFpaSxKs",
    "capsule_id": "repository-81b151245d70",
    "source_commit": "81b151245d70f6b775418de60f7b8a1366f28944",
    "git_tree_oid": "c63cb393713f9824970bab80b07c214dc79e561a",
    "recovery_commit": "247f254229de1d148f299a2cbfacf7102950d5df",
    "package_identity": "ab3e0c54dce4b51330060e88133399553442f091d6f98adf06b8439e27be00c2",
    "payload_bytes": 36_925_440,
    "payload_sha256": "132cc58496f903990447f06847325b7393d1dedf8b4eae24ad888f4145b1df14",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_arweave_mirror_record_is_exact_and_non_amending() -> None:
    record = load(RECORD_PATH)

    assert record["status"] == "uploaded_and_publicly_verified"
    assert record["non_amending_boundary"] is True
    assert record["canonical_authority"] == "Bitcoin Originals only"

    capsule = record["capsule"]
    assert capsule["capsule_id"] == EXPECTED["capsule_id"]
    assert capsule["source_git_commit_sha"] == EXPECTED["source_commit"]
    assert capsule["git_tree_oid"] == EXPECTED["git_tree_oid"]
    assert capsule["recovery_commit_sha"] == EXPECTED["recovery_commit"]
    assert capsule["package_identity_sha256"] == EXPECTED["package_identity"]
    assert capsule["tracked_file_count"] == 4330
    assert capsule["published_file_count"] == 8
    assert capsule["live_main_equivalence_claimed"] is False

    transport = record["transport"]
    assert transport["bytes"] == EXPECTED["payload_bytes"]
    assert transport["sha256"] == EXPECTED["payload_sha256"]

    arweave = record["arweave"]
    assert arweave["txid"] == EXPECTED["txid"]
    assert arweave["block_height"] == 1_971_626
    assert int(arweave["transaction_reward_winston"]) <= 400_000_000_000
    assert int(arweave["observed_balance_after_winston"]) >= int(
        arweave["minimum_remaining_winston"]
    )

    verification = record["verification"]
    assert verification["graphql_tag_lookup"] == "passed"
    assert verification["required_tags_verified"] is True
    assert verification["primary_gateway_readback"] == "passed"
    assert verification["readback_bytes"] == EXPECTED["payload_bytes"]
    assert verification["readback_sha256"] == EXPECTED["payload_sha256"]

    boundaries = record["boundaries"]
    assert boundaries["capsule_is_a_non_authoritative_mirror"] is True
    assert boundaries["recovery_does_not_amend_canonical_material"] is True
    assert boundaries["bitcoin_originals_prevail"] is True


def test_recovery_catalog_points_to_the_exact_verified_mirror() -> None:
    catalog = load(CATALOG_PATH)
    mirror = catalog["core_repository"]["verified_arweave_mirror"]

    assert mirror["record"] == RECORD_PATH.relative_to(ROOT).as_posix()
    assert mirror["txid"] == EXPECTED["txid"]
    assert mirror["capsule_id"] == EXPECTED["capsule_id"]
    assert mirror["source_git_commit_sha"] == EXPECTED["source_commit"]
    assert mirror["git_tree_oid"] == EXPECTED["git_tree_oid"]
    assert mirror["package_identity_sha256"] == EXPECTED["package_identity"]
    assert mirror["payload_bytes"] == EXPECTED["payload_bytes"]
    assert mirror["payload_sha256"] == EXPECTED["payload_sha256"]
    assert mirror["public_readback"] == "passed"
    assert catalog["github_required_for_discovery"] is False
    assert catalog["github_required_for_recovery"] is False
