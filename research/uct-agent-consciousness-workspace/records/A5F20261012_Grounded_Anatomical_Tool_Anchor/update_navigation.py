#!/usr/bin/env python3
"""Synchronize A5F disabled-follow-up JSON navigation."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = Path(__file__).resolve().parent

def read(path): return json.loads(path.read_text(encoding="utf-8"))
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

app = read(REC / "APPLICATION_ENTRY.json")
base = "records/A5F20261012_Grounded_Anatomical_Tool_Anchor/"
nav = {
    "id": app["id"], "version": app["version"], "status": app["status"],
    "enabled_as_established_premises": False,
    "source": base + "RESEARCH_NOTE.md", "handoff": base + "HANDOFF_ZH.md",
    "work_log": base + "WORK_LOG.md", "claim_ledger": base + "CLAIM_LEDGER.json",
    "map_extension": base + "MAP_EXTENSION.json", "exact_results": base + "EXACT_RESULTS.json",
    "parent_science": "A3V20261010", "parent_followup": "A5E20261012",
    "completed_map": "UCT-MAP-v1.1.2", "scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
    "selected_target": app["selected_target"], "actual_bodily_installation": False,
    "actual_protocol_candidate": True, "independent_asymmetric_anchor_at_protocol_level": True,
    "complete_biological_K": False, "independent_H_tip_validation": False,
    "independent_B_pc_validation": False, "standalone_manuscript": app["standalone_manuscript"]
}

current = read(ROOT / "CURRENT_STATE.json")
current["latest_activity"] = {"id": "A5F20261012", "type": "FOLLOWUP_APPLICATION", "status": app["status"], "source": nav["source"]}
current["latest_followup_application"] = nav
current["pending_note"] = (
    "A5F identifies a real crossed-tool protocol where anatomical anchor plus actual grip and distal side removes the A5E automorphism barrier and defines a changing distal coordinate. "
    "The protocol does not establish complete biological K, and its temporal-order reports do not independently identify H_tip, ownership, agency or H_pc."
)
current["review_status_scope"] = (
    "Completed v1.1.2 unchanged; 913/424/261 effective objects received a fresh structural traversal. A5F manually rechecked C1/U1, P3/P6, PHEN_TARGET, R157, R159, A5E and all current supervision items. Deep full-history semantics remain AUDIT_INCOMPLETE."
)
current["next_priority"] = (
    "A5F next: predeclare one crossed-tool or tool-substitution comparison with a non-report-fitted independent H_tip measure and failure outcome while holding anatomical anchor and grip route fixed. If unavailable, retain only the protocol-level grounded-coordinate candidate and keep B_tip/B_pc open."
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
        obj["latest_update"] = {"id": "A5F20261012", "coverage_change": "NONE", "source": base + "PUBLICATION_COVERAGE_UPDATE.json", "manuscript_decision": nav["standalone_manuscript"]}
    write(ROOT / name, obj)

print(json.dumps({"latest": nav["id"], "updated": ["CURRENT_STATE.json", "UNIFIED_RESEARCH_INDEX.json", "FORMAL_MAP_EXTENSION_INDEX.json", "PUBLICATION_COVERAGE.json"]}, sort_keys=True))
