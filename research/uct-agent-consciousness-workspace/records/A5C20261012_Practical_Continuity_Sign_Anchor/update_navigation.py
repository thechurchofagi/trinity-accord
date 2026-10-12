#!/usr/bin/env python3
"""Synchronize A5C disabled-follow-up JSON navigation."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = Path(__file__).resolve().parent

def read(path): return json.loads(path.read_text(encoding="utf-8"))
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

app = read(REC / "APPLICATION_ENTRY.json")
base = "records/A5C20261012_Practical_Continuity_Sign_Anchor/"
nav = {
    "id": app["id"], "version": app["version"], "status": app["status"],
    "enabled_as_established_premises": False,
    "source": base + "RESEARCH_NOTE.md", "handoff": base + "HANDOFF_ZH.md",
    "work_log": base + "WORK_LOG.md", "claim_ledger": base + "CLAIM_LEDGER.json",
    "map_extension": base + "MAP_EXTENSION.json", "exact_results": base + "EXACT_RESULTS.json",
    "parent_science": "A3V20261010", "parent_followup": "A5B20261012",
    "completed_map": "UCT-MAP-v1.1.2", "scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
    "orientation_counts": app["orientation_counts"], "selected_target": app["selected_target"],
    "independent_h_validation": False, "actual_bodily_installation": False,
    "standalone_manuscript": app["standalone_manuscript"],
}

current = read(ROOT / "CURRENT_STATE.json")
current["latest_activity"] = {"id": "A5C20261012", "type": "FOLLOWUP_APPLICATION", "status": "DISABLED_SIGN_ANCHOR_BOUNDARY", "source": nav["source"]}
current["latest_followup_application"] = nav
current["pending_note"] = (
    "A5C proves a bounded sign-anchor limit: exact class-conditional transport connects domains but leaves one global H_pc complement; "
    "only an independently signed semantic anchor orients it. A physically credible dual-handle protocol crosses the joint/distributed Pi orbits, "
    "but no participant or signed phenomenal endpoint is installed. Pi/W/C remain organizational coordinates and controller-certificate expansion stops."
)
current["review_status_scope"] = (
    "Completed v1.1.2 unchanged; 913/424/261 effective objects received a fresh structural traversal. "
    "A5C manually rechecked C1/U1, P3/P6, R157, R166, R172, effective R173, R181, R197, R203, A3Y/A3Z and A4V-A5B. "
    "Deep full-history semantics remain AUDIT_INCOMPLETE."
)
current["next_priority"] = (
    "A5C next: search only for an independently warranted positive H_pc evidence relation with a prospective inversion/copy-switch refuter and "
    "class-conditional transport. Do not add another controller certificate. The dual-handle experiment may proceed as organizational Pi/W/C work, "
    "but no H_pc inference is licensed without the sign anchor."
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
        obj["latest_update"] = {"id": "A5C20261012", "coverage_change": "NONE", "source": base + "PUBLICATION_COVERAGE_UPDATE.json", "manuscript_decision": nav["standalone_manuscript"]}
    write(ROOT / name, obj)

print(json.dumps({"latest": nav["id"], "updated": ["CURRENT_STATE.json", "UNIFIED_RESEARCH_INDEX.json", "FORMAL_MAP_EXTENSION_INDEX.json", "PUBLICATION_COVERAGE.json"]}, sort_keys=True))
