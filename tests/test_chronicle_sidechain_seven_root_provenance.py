import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCEPTIONS = ROOT / "evidence/chronicle-sidechain-historical-payload-exceptions.json"
PROVENANCE = ROOT / "evidence/chronicle-sidechain-seven-root-provenance-review.v1.json"
REAUDIT = ROOT / "evidence/chronicle-sidechain-seven-root-provenance.json"
WORKFLOW = ROOT / ".github/workflows/chronicle-sidechain-mirror-v3.yml"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_provenance_covers_exact_historical_exception_set_without_promoting_payloads():
    exceptions = load_json(EXCEPTIONS)
    provenance = load_json(PROVENANCE)

    expected = {item["root_cid"] for item in exceptions["exceptions"]}
    reviewed = {item["root_cid"] for item in provenance["records"]}

    assert len(expected) == 7
    assert reviewed == expected
    # Raw external payload bytes are still unavailable; do not promote them to verified.
    assert all(item["exact_recovery_pending"] for item in exceptions["exceptions"])
    assert provenance["summary"]["external_delivery_confirmed"] == 7
    assert provenance["summary"]["payload_exact_verification_changed"] is False
    assert provenance["preservation_boundary"]["unresolved_root_count_remains"] == 7


def test_project_completeness_scope_excludes_verified_external_deliveries():
    exceptions = load_json(EXCEPTIONS)
    policy = exceptions["policy"]

    assert policy["provenance_audit_status"] == "verified_external_delivery"
    assert policy["external_wallet_observation_count"] == 7
    assert policy["project_content_gap_count"] == 0
    assert policy["payload_bytes_recovered"] is False
    assert policy["recovery_required_for_project_completeness"] is False
    assert policy["optional_forensic_recovery_allowed"] is True
    assert policy["provenance_record"] == "evidence/chronicle-sidechain-seven-root-provenance-review.v1.json"
    assert policy["independent_reaudit_record"] == "evidence/chronicle-sidechain-seven-root-provenance.json"

    for item in exceptions["exceptions"]:
        assert item["status"] == "historical_payload_unavailable"
        assert item["payload_verified"] is False
        assert item["exact_recovery_pending"] is True
        assert item["recovery_required_for_project_completeness"] is False
        assert item["project_scope"] == "out_of_scope_external_wallet_asset"
        assert item["provenance_classification"] == "externally_delivered_not_self_minted"
        assert item["target_initiated_transaction"] is False
        assert item["official_project_contract"] is False


def test_independent_reaudit_reproduces_external_delivery_totals():
    exceptions = load_json(EXCEPTIONS)
    reaudit = load_json(REAUDIT)

    assert reaudit["scope"]["declared_historical_roots"] == 7
    assert reaudit["scope"]["externally_delivered_not_self_minted"] == 7
    assert reaudit["scope"]["external_zero_address_mints"] == 2
    assert reaudit["scope"]["external_transfers"] == 5
    assert reaudit["scope"]["project_originated"] == 0
    assert reaudit["scope"]["project_content_gap_count"] == 0
    assert reaudit["scope"]["payload_recovery_claimed"] is False

    expected = {item["root_cid"] for item in exceptions["exceptions"]}
    audited = {item["root_cid"] for item in reaudit["items"]}
    assert audited == expected


def test_every_record_is_inbound_external_delivery_with_public_sources():
    provenance = load_json(PROVENANCE)
    target = provenance["target_address"]

    workflow = WORKFLOW.read_text(encoding="utf-8").lower()
    declared = re.search(r'chronicle_address:\s*["\']?(0x[0-9a-f]{40})', workflow)
    assert declared is not None
    assert declared.group(1) == target

    for record in provenance["records"]:
        assert record["transfer_to"] == target
        assert record["transfer_from"] != target
        assert record["transaction_initiator"] != target
        assert record["classification"] == "externally_delivered_not_self_minted"
        assert record["delivery_mode"] in {"external_batch_mint", "external_transfer"}
        assert len(record["sources"]) >= 2
        assert all(source.startswith("https://") for source in record["sources"])


def test_delivery_mode_totals_are_fail_closed():
    provenance = load_json(PROVENANCE)
    modes = [item["delivery_mode"] for item in provenance["records"]]

    assert modes.count("external_batch_mint") == 2
    assert modes.count("external_transfer") == 5
    assert provenance["summary"]["target_initiated_transactions"] == 0
    assert provenance["methodology"]["ownership_inference_prohibited"] is True
    assert provenance["preservation_boundary"]["legal_or_beneficial_ownership_claimed"] is False
