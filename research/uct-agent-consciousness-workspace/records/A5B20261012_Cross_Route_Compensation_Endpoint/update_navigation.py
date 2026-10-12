#!/usr/bin/env python3
"""Synchronize A5B disabled-follow-up JSON navigation."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


app = read(REC / "APPLICATION_ENTRY.json")
base = "records/A5B20261012_Cross_Route_Compensation_Endpoint/"
nav = {
    "id": app["id"],
    "version": app["version"],
    "status": app["status"],
    "enabled_as_established_premises": False,
    "source": base + "RESEARCH_NOTE.md",
    "handoff": base + "HANDOFF_ZH.md",
    "work_log": base + "WORK_LOG.md",
    "claim_ledger": base + "CLAIM_LEDGER.json",
    "map_extension": base + "MAP_EXTENSION.json",
    "exact_results": base + "EXACT_RESULTS.json",
    "parent_science": "A3V20261010",
    "parent_followup": "A5A20261012",
    "completed_map": "UCT-MAP-v1.1.2",
    "scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
    "finite_world_counts": app["finite_world_counts"],
    "selected_target": app["selected_target"],
    "independent_h_validation": False,
    "actual_bodily_installation": False,
    "standalone_manuscript": app["standalone_manuscript"],
}

current = read(ROOT / "CURRENT_STATE.json")
current["latest_activity"] = {
    "id": "A5B20261012",
    "type": "FOLLOWUP_APPLICATION",
    "status": "DISABLED_CROSS_ROUTE_COMPENSATION_ENDPOINT",
    "source": nav["source"],
}
current["latest_followup_application"] = nav
current["pending_note"] = (
    "A5B predeclares H_pc, felt practical continuity across a perturbation, without source-count wording. "
    "The compensation vector C is a separate organizational endpoint. Exact 36/16/25/9 world counts show "
    "that C does not identify Pi without faithfulness premises, and even biconditional targetwise faithfulness "
    "does not distinguish global-single-owner from strict-distributed Pi when C=00. B_pc^comp, B_pc^family and H_cf remain open."
)
current["review_status_scope"] = (
    "Completed v1.1.2 unchanged; 913/424/261 effective objects received a fresh structural traversal. "
    "A5B manually rechecked C1/U1, P3/P6, R157, R159, R166, R172, effective R173, R181, R197, A3Z and A4V-A5A. "
    "Deep full-history semantics remain AUDIT_INCOMPLETE."
)
current["next_priority"] = (
    "A5B next: independently justify the positive sign and class-conditional reliability of E_pc for H_pc, "
    "then specify one physically credible cross-orbit Pi/W perturbation with target identity, conceptual self and report mechanism fixed. "
    "If either cannot be installed, retain Pi and C as organizational coordinates and do not expand controller certificates."
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
            "id": "A5B20261012",
            "coverage_change": "NONE",
            "source": base + "PUBLICATION_COVERAGE_UPDATE.json",
            "manuscript_decision": nav["standalone_manuscript"],
        }
    write(ROOT / name, obj)

print(json.dumps({"latest": nav["id"], "updated": ["CURRENT_STATE.json", "UNIFIED_RESEARCH_INDEX.json", "FORMAL_MAP_EXTENSION_INDEX.json", "PUBLICATION_COVERAGE.json"]}, sort_keys=True))
