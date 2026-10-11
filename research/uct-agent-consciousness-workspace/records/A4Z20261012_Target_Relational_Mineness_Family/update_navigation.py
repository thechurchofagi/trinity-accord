#!/usr/bin/env python3
"""Synchronize A4Z disabled-follow-up JSON navigation."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

app = read(REC / "APPLICATION_ENTRY.json")
base = "records/A4Z20261012_Target_Relational_Mineness_Family/"
nav = {
    "id": app["id"], "version": app["version"], "status": app["status"],
    "enabled_as_established_premises": False,
    "source": base + "RESEARCH_NOTE.md",
    "handoff": base + "HANDOFF_ZH.md",
    "work_log": base + "WORK_LOG.md",
    "claim_ledger": base + "CLAIM_LEDGER.json",
    "map_extension": base + "MAP_EXTENSION.json",
    "exact_results": base + "EXACT_RESULTS.json",
    "parent_science": "A3V20261010", "parent_followup": "A4Y20261012",
    "completed_map": "UCT-MAP-v1.1.2",
    "scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
    "covered_relation_matrices": 9, "locally_unique_matrices": 4,
    "global_single_owner_matrices": 2, "route_label_swap_orbits": 5,
    "independent_h_validation": False, "actual_bodily_installation": False,
    "standalone_manuscript": "HOLD_MERGE_A4V_TO_A4Z_SYNTHESIS"
}
current = read(ROOT / "CURRENT_STATE.json")
current["latest_activity"] = {
    "id": "A4Z20261012", "type": "FOLLOWUP_APPLICATION",
    "status": "DISABLED_TARGET_RELATIONAL_MINENESS_FAMILY_APPLICATION",
    "source": nav["source"]
}
current["latest_followup_application"] = nav
current["next_priority"] = (
    "A4Z next: independently predeclare one fallible phenomenal target that distinguishes joint-source from distributed-source practical mineness while holding target coverage, route-label orbit, conceptual self and report fixed. If no target/evidence bridge is available, preserve B_pc^family/H_cf as OPEN and do not resume certificate expansion."
)
write(ROOT / "CURRENT_STATE.json", current)
for name in ("UNIFIED_RESEARCH_INDEX.json", "FORMAL_MAP_EXTENSION_INDEX.json", "PUBLICATION_COVERAGE.json"):
    obj = read(ROOT / name)
    assert not any(item.get("id") == nav["id"] for item in obj["followup_applications"])
    item = dict(nav)
    if name == "FORMAL_MAP_EXTENSION_INDEX.json":
        item.pop("actual_bodily_installation")
        item["actual_route_use_instantiated"] = False
    obj["followup_applications"].append(item)
    obj["latest_followup_application"] = item
    if name == "PUBLICATION_COVERAGE.json":
        obj["latest_update"] = {
            "id": "A4Z20261012", "coverage_change": "NONE",
            "source": base + "PUBLICATION_COVERAGE_UPDATE.json",
            "manuscript_decision": nav["standalone_manuscript"]
        }
    write(ROOT / name, obj)
print(json.dumps({"latest": nav["id"], "updated": [
    "CURRENT_STATE.json", "UNIFIED_RESEARCH_INDEX.json",
    "FORMAL_MAP_EXTENSION_INDEX.json", "PUBLICATION_COVERAGE.json"]}, sort_keys=True))
