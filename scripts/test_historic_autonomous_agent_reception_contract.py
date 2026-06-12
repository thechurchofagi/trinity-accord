#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "api" / "public-home-status.json"
INDEX = ROOT / "index.md"
RECORDS_DIR = ROOT / "record-chain" / "records"

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
    match = re.search(
        r'<p class="status-label">' + re.escape(label) + r'</p>\s*'
        r'<p class="status-number">([^<]+)</p>',
        block_text,
    )
    if not match:
        raise SystemExit(f"ERROR: missing homepage card: {label}")
    return match.group(1).strip()


def main() -> int:
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

    expected = [record for record in records if is_strict_autonomous(record)]
    expected_ids = [record.get("record_id") for record in expected]

    actual_records = historic.get("records", [])
    actual_ids = [item.get("record_id") for item in actual_records if isinstance(item, dict)]

    if historic.get("count") != len(expected):
        raise SystemExit(
            f"ERROR: historic autonomous count mismatch: status={historic.get('count')} expected={len(expected)}"
        )
    if actual_ids != expected_ids:
        raise SystemExit(f"ERROR: historic autonomous records mismatch: status={actual_ids} expected={expected_ids}")

    text = INDEX.read_text(encoding="utf-8")
    generated = extract_block(text)
    card_value = card_number(generated, "Autonomous External Agent Discovery")
    if card_value != str(len(expected)):
        raise SystemExit(f"ERROR: homepage historic autonomous card mismatch: page={card_value} expected={len(expected)}")

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

    # Assert counted records are all official
    for rid in actual_ids:
        if rid not in official_ids:
            raise SystemExit(f"ERROR: historic autonomous record {rid} is not an official live reception record")

    print("PASS: historic autonomous external-agent reception contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
