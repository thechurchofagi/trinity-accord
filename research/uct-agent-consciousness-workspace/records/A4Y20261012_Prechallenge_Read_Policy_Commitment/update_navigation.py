#!/usr/bin/env python3
"""Mechanically synchronize A4Y disabled-follow-up JSON navigation."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REC = Path(__file__).resolve().parent


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


app = read(REC / "APPLICATION_ENTRY.json")
nav = {
    "id": app["id"],
    "version": app["version"],
    "status": app["status"],
    "enabled_as_established_premises": False,
    "source": "records/A4Y20261012_Prechallenge_Read_Policy_Commitment/RESEARCH_NOTE.md",
    "handoff": "records/A4Y20261012_Prechallenge_Read_Policy_Commitment/HANDOFF_ZH.md",
    "work_log": "records/A4Y20261012_Prechallenge_Read_Policy_Commitment/WORK_LOG.md",
    "claim_ledger": "records/A4Y20261012_Prechallenge_Read_Policy_Commitment/CLAIM_LEDGER.json",
    "map_extension": "records/A4Y20261012_Prechallenge_Read_Policy_Commitment/MAP_EXTENSION.json",
    "exact_results": "records/A4Y20261012_Prechallenge_Read_Policy_Commitment/EXACT_RESULTS.json",
    "parent_science": "A3V20261010",
    "parent_followup": "A4X20261012",
    "completed_map": "UCT-MAP-v1.1.2",
    "scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
    "challenge_indexed_policies_per_target": 256,
    "challenge_indexed_exact_mimics_per_target": 16,
    "fixed_one_port_policies_per_target": 4,
    "fixed_one_port_exact_mimics_per_target": 0,
    "independent_h_validation": False,
    "actual_bodily_installation": False,
    "standalone_manuscript": "HOLD_MERGE_WITH_A4V_A4W_A4X_FAMILY",
}

current = read(ROOT / "CURRENT_STATE.json")
current["latest_activity"] = {
    "id": "A4Y20261012",
    "type": "FOLLOWUP_APPLICATION",
    "status": "DISABLED_PRECHALLENGE_READ_POLICY_COMMITMENT_APPLICATION",
    "source": nav["source"],
}
current["latest_followup_application"] = nav
current["next_priority"] = (
    "A4Y next: on one actual accessible consumer boundary, determine whether an independently controlled witness can bind a prechallenge read-policy state to the actual named-port read event while challenge labels, schedules and shared randomness are physically excluded. If no such interface is available, stop the certificate branch and return to independent B_pc^family/H_cf target semantics rather than enumerate broader controllers."
)
write(ROOT / "CURRENT_STATE.json", current)

unified = read(ROOT / "UNIFIED_RESEARCH_INDEX.json")
assert not any(item.get("id") == nav["id"] for item in unified["followup_applications"])
unified["followup_applications"].append(nav)
unified["latest_followup_application"] = nav
write(ROOT / "UNIFIED_RESEARCH_INDEX.json", unified)

formal = read(ROOT / "FORMAL_MAP_EXTENSION_INDEX.json")
formal_nav = dict(nav)
formal_nav.pop("actual_bodily_installation")
formal_nav["actual_route_use_instantiated"] = False
assert not any(item.get("id") == nav["id"] for item in formal["followup_applications"])
formal["followup_applications"].append(formal_nav)
formal["latest_followup_application"] = formal_nav
write(ROOT / "FORMAL_MAP_EXTENSION_INDEX.json", formal)

coverage = read(ROOT / "PUBLICATION_COVERAGE.json")
assert not any(item.get("id") == nav["id"] for item in coverage["followup_applications"])
coverage["followup_applications"].append(nav)
coverage["latest_followup_application"] = nav
coverage["latest_update"] = {
    "id": "A4Y20261012",
    "coverage_change": "NONE",
    "source": "records/A4Y20261012_Prechallenge_Read_Policy_Commitment/PUBLICATION_COVERAGE_UPDATE.json",
    "manuscript_decision": "HOLD_MERGE_WITH_A4V_A4W_A4X_FAMILY",
}
write(ROOT / "PUBLICATION_COVERAGE.json", coverage)

print(json.dumps({"updated": ["CURRENT_STATE.json", "UNIFIED_RESEARCH_INDEX.json", "FORMAL_MAP_EXTENSION_INDEX.json", "PUBLICATION_COVERAGE.json"], "latest": nav["id"]}, sort_keys=True))
