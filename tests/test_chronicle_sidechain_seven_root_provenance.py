import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCEPTIONS = ROOT / "evidence/chronicle-sidechain-historical-payload-exceptions.json"
PROVENANCE = ROOT / "evidence/chronicle-sidechain-seven-root-provenance-review.v1.json"
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
    assert all(item["exact_recovery_pending"] for item in exceptions["exceptions"])
    assert provenance["summary"]["external_delivery_confirmed"] == 7
    assert provenance["summary"]["payload_exact_verification_changed"] is False
    assert provenance["preservation_boundary"]["unresolved_root_count_remains"] == 7


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
