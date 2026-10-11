#!/usr/bin/env python3
"""Mechanically synchronize A4X disabled-follow-up JSON navigation."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REC = Path(__file__).resolve().parent


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


app = read(REC / "APPLICATION_ENTRY.json")
nav = {
    "id": app["id"],
    "version": app["version"],
    "status": app["status"],
    "enabled_as_established_premises": False,
    "source": "records/A4X20261012_Redundant_Port_Participation/RESEARCH_NOTE.md",
    "handoff": "records/A4X20261012_Redundant_Port_Participation/HANDOFF_ZH.md",
    "work_log": "records/A4X20261012_Redundant_Port_Participation/WORK_LOG.md",
    "claim_ledger": "records/A4X20261012_Redundant_Port_Participation/CLAIM_LEDGER.json",
    "map_extension": "records/A4X20261012_Redundant_Port_Participation/MAP_EXTENSION.json",
    "exact_results": "records/A4X20261012_Redundant_Port_Participation/EXACT_RESULTS.json",
    "parent_science": "A3V20261010",
    "parent_followup": "A4W20261012",
    "completed_map": "UCT-MAP-v1.1.2",
    "scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
    "merge_functions": 16,
    "normal_output_correct": 4,
    "dual_port_contingently_relevant": 2,
    "one_input_projections": 2,
    "universal_two_port_but_for_on_all_normal_rows": 0,
    "independent_h_validation": False,
    "actual_bodily_installation": False,
    "standalone_manuscript": "HOLD_MERGE_WITH_A4V_A4W_FAMILY",
}

current = read(ROOT / "CURRENT_STATE.json")
current["latest_activity"] = {
    "id": "A4X20261012",
    "type": "FOLLOWUP_APPLICATION",
    "status": "DISABLED_REDUNDANT_PORT_PARTICIPATION_APPLICATION",
    "source": nav["source"],
}
current["latest_followup_application"] = nav
current["next_priority"] = (
    "A4X next: at one fixed consumer boundary, test whether intervention-dependent hidden internal modes can reproduce every finite port challenge while preserving apparent lineage, and identify the minimum independently recorded mechanism state that blocks the twin. Stop if this becomes unbounded controller enumeration; return to B_pc^family/H_cf."
)
write(ROOT / "CURRENT_STATE.json", current)

unified = read(ROOT / "UNIFIED_RESEARCH_INDEX.json")
assert not any(x.get("id") == nav["id"] for x in unified["followup_applications"])
unified["followup_applications"].append(nav)
unified["latest_followup_application"] = nav
write(ROOT / "UNIFIED_RESEARCH_INDEX.json", unified)

formal = read(ROOT / "FORMAL_MAP_EXTENSION_INDEX.json")
formal_nav = dict(nav)
formal_nav.pop("actual_bodily_installation")
formal_nav["actual_route_use_instantiated"] = False
assert not any(x.get("id") == nav["id"] for x in formal["followup_applications"])
formal["followup_applications"].append(formal_nav)
formal["latest_followup_application"] = formal_nav
write(ROOT / "FORMAL_MAP_EXTENSION_INDEX.json", formal)

coverage = read(ROOT / "PUBLICATION_COVERAGE.json")
assert not any(x.get("id") == nav["id"] for x in coverage["followup_applications"])
coverage["followup_applications"].append(nav)
coverage["latest_followup_application"] = nav
coverage["latest_update"] = {
    "id": "A4X20261012",
    "coverage_change": "NONE",
    "source": "records/A4X20261012_Redundant_Port_Participation/PUBLICATION_COVERAGE_UPDATE.json",
    "manuscript_decision": "HOLD_MERGE_WITH_A4V_A4W_FAMILY",
}
write(ROOT / "PUBLICATION_COVERAGE.json", coverage)

print(json.dumps({"updated": ["CURRENT_STATE.json", "UNIFIED_RESEARCH_INDEX.json", "FORMAL_MAP_EXTENSION_INDEX.json", "PUBLICATION_COVERAGE.json"], "latest": nav["id"]}, sort_keys=True))
