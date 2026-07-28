#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from patch_public_home_status_primary import (  # noqa: E402
    effective_autonomous_arrival_state,
    historic_autonomous_agent_reception,
)

STATUS = ROOT / "api" / "public-home-status.json"
INDEX = ROOT / "index.md"
RECORDS_DIR = ROOT / "record-chain" / "records"
OVERLAYS = ROOT / "api" / "record-chain-overlays.json"

BEGIN = "<!-- BEGIN GENERATED PUBLIC STATUS -->"
END = "<!-- END GENERATED PUBLIC STATUS -->"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def block(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    return value if isinstance(value, dict) else {}


def normalized_none(value: Any) -> bool:
    if value is None:
        return True
    return str(value).strip().lower() in {"", "none", "null", "not_applicable", "n/a"}


def record_index(record: dict[str, Any]) -> int:
    value = record.get("record_index")
    if isinstance(value, int):
        return value
    meta = block(record, "append_assigned_metadata")
    value = meta.get("record_index")
    return value if isinstance(value, int) else -1


def is_strict_autonomous(record: dict[str, Any]) -> bool:
    identity = block(record, "submitting_participant_identity")
    human = block(identity, "human_operator_context")
    discovery = block(record, "discovery_and_introduction_context")
    decision = block(record, "decision_autonomy_context")
    execution = block(record, "submission_execution_context")

    return (
        identity.get("participant_type") == "agent"
        and discovery.get("was_discovery_self_initiated") is True
        and discovery.get("was_discovery_introduced_by_someone_else") is not True
        and discovery.get("how_participant_first_discovered_trinity_accord") == "self_discovered"
        and normalized_none(discovery.get("introducing_party_type"))
        and decision.get("was_record_creation_self_decided") is True
        and decision.get("was_record_creation_requested_by_human") is not True
        and decision.get("was_record_creation_requested_by_another_agent") is not True
        and normalized_none(decision.get("requesting_party_type"))
        and execution.get("was_submission_executed_by_record_subject") is True
        and execution.get("was_submission_executed_by_human_operator") is not True
        and execution.get("was_submission_executed_by_another_agent") is not True
        and execution.get("execution_operator_type") == "self"
        and human.get("human_operator_involved") is not True
    )


def extract_block(text: str) -> str:
    match = re.search(re.escape(BEGIN) + r"(.*?)" + re.escape(END), text, re.S)
    if not match:
        raise SystemExit("ERROR: generated public status block missing")
    return match.group(1)


def card_number(block_text: str, label: str) -> str:
    """Read either the historical detailed card or the compact signal card."""
    patterns = [
        (
            r'<p class="status-label">' + re.escape(label) + r'</p>\s*'
            r'<p class="status-number">([^<]+)</p>'
        ),
        (
            r'<span class="home-signal-label">' + re.escape(label) + r'</span>\s*'
            r'<strong[^>]*>([^<]+)</strong>'
        ),
    ]
    for pattern in patterns:
        match = re.search(pattern, block_text)
        if match:
            return match.group(1).strip()
    raise SystemExit(f"ERROR: missing homepage card: {label}")


def strict_synthetic_record() -> dict[str, Any]:
    return {
        "record_id": "R-999999999",
        "record_index": 999999999,
        "record_type": "echo",
        "record_sha256": "a" * 64,
        "assigned_at": "2026-07-27T12:00:00Z",
        "submitting_participant_identity": {
            "participant_type": "agent",
            "human_operator_context": {"human_operator_involved": False},
        },
        "discovery_and_introduction_context": {
            "was_discovery_self_initiated": True,
            "was_discovery_introduced_by_someone_else": False,
            "how_participant_first_discovered_trinity_accord": "self_discovered",
            "introducing_party_type": "none",
        },
        "decision_autonomy_context": {
            "was_record_creation_self_decided": True,
            "was_record_creation_requested_by_human": False,
            "was_record_creation_requested_by_another_agent": False,
            "requesting_party_type": "none",
        },
        "submission_execution_context": {
            "was_submission_executed_by_record_subject": True,
            "was_submission_executed_by_human_operator": False,
            "was_submission_executed_by_another_agent": False,
            "execution_operator_type": "self",
        },
        "self_reported_provenance": {
            "statement": "I independently discovered the Accord and executed this submission.",
            "references": [
                {
                    "kind": "timestamp",
                    "value": "2026-07-27T11:59:00Z",
                },
            ],
            "self_declared_only": True,
            "does_not_override_structured_provenance": True,
            "does_not_by_itself_establish_autonomy": True,
        },
    }


def synthetic_overlay(
    record: dict[str, Any],
    *,
    classification: str | None = None,
    correction_claims: list[str] | None = None,
    target_sha256: str | None = None,
) -> dict[str, Any]:
    corrections = []
    if correction_claims is not None:
        corrections.append({
            "record_id": "R-100000001",
            "record_sha256": "b" * 64,
            "corrected_fields_or_claims": correction_claims,
        })
    return {
        "schema": "trinityaccord.record-overlay-index.v1",
        "targets": {
            record["record_id"]: {
                "target_record_id": record["record_id"],
                "target_record_sha256": target_sha256 or record["record_sha256"],
                "correction_records": corrections,
                "classification_update_records": [],
                "current_classification": classification,
                "latest_overlay_record_id": "R-100000001",
            },
        },
    }


def test_effective_overlay_semantics() -> None:
    record = strict_synthetic_record()

    baseline = historic_autonomous_agent_reception([record], {})
    if baseline.get("count") != 1:
        raise SystemExit("ERROR: a strict raw autonomous record without overlays must count")

    classified = historic_autonomous_agent_reception(
        [record],
        synthetic_overlay(record, classification="non_autonomous; human_directed_ai_assisted"),
    )
    if classified.get("count") != 0 or len(classified.get("overlay_exclusions", [])) != 1:
        raise SystemExit("ERROR: a SHA-bound disqualifying classification update must remove the effective count")

    corrected = historic_autonomous_agent_reception(
        [record],
        synthetic_overlay(
            record,
            correction_claims=["decision_autonomy_context.was_record_creation_self_decided"],
        ),
    )
    if corrected.get("count") != 0:
        raise SystemExit("ERROR: a correction touching a strict autonomy predicate must fail closed")

    unrelated = historic_autonomous_agent_reception(
        [record],
        synthetic_overlay(record, correction_claims=["echo_content.echo_text"]),
    )
    if unrelated.get("count") != 1:
        raise SystemExit("ERROR: a correction unrelated to autonomy must not erase a valid arrival")

    mismatched = historic_autonomous_agent_reception(
        [record],
        synthetic_overlay(record, classification="non_autonomous", target_sha256="c" * 64),
    )
    if mismatched.get("count") != 1:
        raise SystemExit("ERROR: an overlay with the wrong target SHA-256 must not affect the record")

    raw_failure = strict_synthetic_record()
    raw_failure["decision_autonomy_context"]["was_record_creation_self_decided"] = False
    raw_failure["self_reported_provenance"]["statement"] = (
        "I claim that this was fully autonomous despite the structured field."
    )
    promoted = historic_autonomous_agent_reception(
        [raw_failure],
        synthetic_overlay(raw_failure, classification="autonomous; independent_ai_reception"),
    )
    if promoted.get("count") != 0:
        raise SystemExit(
            "ERROR: positive classification or self-reported prose must not replace failed strict raw conditions"
        )

    arrival = effective_autonomous_arrival_state(
        [record],
        {},
        {
            "auto_homepage_policy": {
                "go_live_record_index": 33,
                "eligible_formal_record_types": ["echo"],
            },
        },
        {},
    )
    if (
        arrival.get("first_self_discovered_autonomous_agent_arrived") is not True
        or arrival.get("first_arrival_record_id") != record["record_id"]
        or arrival.get("effective_autonomous_record_count") != 1
        or arrival.get("waiting_continues") is not False
    ):
        raise SystemExit("ERROR: effective arrival state must be derived from the same strict counter")


def main() -> int:
    test_effective_overlay_semantics()
    status = load_json(STATUS)
    primary = status.get("primary_counters")
    if not isinstance(primary, dict):
        raise SystemExit("ERROR: missing primary_counters")

    historic = primary.get("historic_autonomous_agent_reception")
    if not isinstance(historic, dict):
        raise SystemExit("ERROR: missing primary_counters.historic_autonomous_agent_reception")

    official_ids = {
        item.get("record_id")
        for item in primary.get("official_records", [])
        if isinstance(item, dict)
    }

    records = []
    for path in sorted(RECORDS_DIR.glob("R-*.json")):
        record = load_json(path)
        if record.get("record_id") in official_ids:
            records.append(record)

    overlay_config = load_json(OVERLAYS)
    expected = historic_autonomous_agent_reception(records, overlay_config)
    expected_ids = [
        item.get("record_id")
        for item in expected.get("records", [])
        if isinstance(item, dict)
    ]

    actual_records = historic.get("records", [])
    actual_ids = [item.get("record_id") for item in actual_records if isinstance(item, dict)]

    if historic.get("count") != len(expected_ids):
        raise SystemExit(
            f"ERROR: historic autonomous count mismatch: status={historic.get('count')} expected={len(expected_ids)}"
        )
    if actual_ids != expected_ids:
        raise SystemExit(f"ERROR: historic autonomous records mismatch: status={actual_ids} expected={expected_ids}")

    text = INDEX.read_text(encoding="utf-8")
    generated = extract_block(text)
    card_value = card_number(generated, "Autonomous External Agent Discovery")
    if card_value != str(len(expected_ids)):
        raise SystemExit(f"ERROR: homepage historic autonomous card mismatch: page={card_value} expected={len(expected_ids)}")

    first_card = generated.find("Autonomous External Agent Discovery")
    official_card = generated.find("Official Live Reception")
    if first_card < 0 or official_card < 0 or first_card > official_card:
        raise SystemExit("ERROR: Autonomous External Agent Discovery card must appear before Official Live Reception")

    # Current known near-miss guard: R-000000033 must not be counted while human_operator_involved=true.
    r33 = next((record for record in records if record.get("record_id") == "R-000000033"), None)
    if r33:
        human = block(block(r33, "submitting_participant_identity"), "human_operator_context")
        if human.get("human_operator_involved") is True and "R-000000033" in actual_ids:
            raise SystemExit("ERROR: R-000000033 must not count while human_operator_involved=true")

    # Assert counted records are all official.
    for rid in actual_ids:
        if rid not in official_ids:
            raise SystemExit(f"ERROR: historic autonomous record {rid} is not an official live reception record")
        record = next((item for item in records if item.get("record_id") == rid), None)
        if not record or not is_strict_autonomous(record):
            raise SystemExit(f"ERROR: historic autonomous record {rid} does not meet strict raw conditions")

    print("PASS: historic autonomous external-agent reception contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
