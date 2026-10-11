#!/usr/bin/env python3
"""Synchronize A5A disabled-follow-up JSON navigation."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


app = read(REC / "APPLICATION_ENTRY.json")
base = "records/A5A20261012_Route_Orbit_Contrast_Barrier/"
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
    "parent_followup": "A4Z20261012",
    "completed_map": "UCT-MAP-v1.1.2",
    "scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
    "covered_relation_matrices": 9,
    "route_label_swap_orbits": 5,
    "same_orbit_joint_or_distributed_contrasts": 0,
    "independent_h_validation": False,
    "actual_bodily_installation": False,
    "standalone_manuscript": "HOLD_MERGE_A4V_TO_A5A_SYNTHESIS",
}

current = read(ROOT / "CURRENT_STATE.json")
current["latest_activity"] = {
    "id": "A5A20261012",
    "type": "FOLLOWUP_APPLICATION",
    "status": "DISABLED_ROUTE_ORBIT_CONTRAST_BARRIER",
    "source": nav["source"],
}
current["latest_followup_application"] = nav
current["pending_note"] = (
    "A5A proves that Pi-only joint-source and strict-distribution predicates are constant on route-label orbits. The previously requested same-orbit joint/distributed contrast is unsatisfiable. A valid Pi-only test must vary the orbit, or separately type additional actual structure W. Actual Pi, complete K, endpoint semantics, signed reliability, B_pc^family and H_cf remain open."
)
current["review_status_scope"] = (
    "Completed v1.1.2 unchanged; 913/424/261 effective objects retain a fresh per-ID structural traversal. A5A manually rechecked C1/U1, P3/P6, R157, effective R173, R181, R197, A3Z, A4M/A4N and A4V-A4Z. Deep full-history semantics remain AUDIT_INCOMPLETE."
)
current["next_priority"] = (
    "A5A next: predeclare one noncircular selected target for route-orbit-sensitive practical mineness, independently of source-count wording, with one prospective refuter across a cross-orbit Pi contrast that fixes target identity, conceptual self and report. If unavailable, retain B_pc^family/H_cf as OPEN and keep Pi as an organizational coordinate."
)
write(ROOT / "CURRENT_STATE.json", current)

for name in (
    "UNIFIED_RESEARCH_INDEX.json",
    "FORMAL_MAP_EXTENSION_INDEX.json",
    "PUBLICATION_COVERAGE.json",
):
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
            "id": "A5A20261012",
            "coverage_change": "NONE",
            "source": base + "PUBLICATION_COVERAGE_UPDATE.json",
            "manuscript_decision": nav["standalone_manuscript"],
        }
    write(ROOT / name, obj)

print(
    json.dumps(
        {
            "latest": nav["id"],
            "updated": [
                "CURRENT_STATE.json",
                "UNIFIED_RESEARCH_INDEX.json",
                "FORMAL_MAP_EXTENSION_INDEX.json",
                "PUBLICATION_COVERAGE.json",
            ],
        },
        sort_keys=True,
    )
)

