#!/usr/bin/env python3
"""Synchronize A5H disabled-follow-up JSON navigation."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = Path(__file__).resolve().parent

def read(path): return json.loads(path.read_text(encoding="utf-8"))
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

app = read(REC / "APPLICATION_ENTRY.json")
base = "records/A5H20261012_Coarse_O_Fixed_Tip_Contrast/"
nav = {
    "id": app["id"], "version": app["version"], "status": app["status"],
    "enabled_as_established_premises": False,
    "source": base + "RESEARCH_NOTE.md", "handoff": base + "HANDOFF_ZH.md",
    "work_log": base + "WORK_LOG.md", "claim_ledger": base + "CLAIM_LEDGER.json",
    "map_extension": base + "MAP_EXTENSION.json", "exact_results": base + "EXACT_RESULTS.json",
    "parent_science": "A3V20261010", "parent_followup": "A5G20261012",
    "completed_map": "UCT-MAP-v1.1.2", "scientific_delta": {"nodes": 0, "rules": 0, "contexts": 0},
    "selected_target": app["selected_target"], "actual_bodily_installation": False,
    "fixed_coarse_O_A5F": True, "fixed_complete_K": False,
    "same_instance_complete_bridge": False, "independent_oriented_H_tip_channel": False,
    "complete_biological_K": False, "standalone_manuscript": app["standalone_manuscript"]
}

current = read(ROOT / "CURRENT_STATE.json")
current["latest_activity"] = {"id": "A5H20261012", "type": "FOLLOWUP_APPLICATION", "status": app["status"], "source": nav["source"]}
current["latest_followup_application"] = nav
current["pending_note"] = (
    "A5H corrects the intervention domain: fix only coarse O_A5F while varying an actual relation S inside complete K. "
    "Same-binding C1 does not admit different H under literally identical complete pointed K. Existing held-stick and somatotopic-localizer evidence do not supply one same-instance bridge."
)
current["review_status_scope"] = (
    "Completed v1.1.2 unchanged; 913/424/261 effective objects received a fresh structural traversal. A5H manually rechecked C1/U1, PHEN_TARGET, R157, R159, A5F-A5G and current supervision items. Deep full-history semantics remain AUDIT_INCOMPLETE."
)
current["next_priority"] = (
    "A5H next: specify one same-participant held-tool rabbit design with a veridically trained, fixed-oriented distal-location target channel, crossed response mapping and a direct-sequence bypass test."
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
        obj["latest_update"] = {"id": "A5H20261012", "coverage_change": "NONE", "source": base + "PUBLICATION_COVERAGE_UPDATE.json", "manuscript_decision": nav["standalone_manuscript"]}
    write(ROOT / name, obj)

print(json.dumps({"latest": nav["id"], "updated": ["CURRENT_STATE.json", "UNIFIED_RESEARCH_INDEX.json", "FORMAL_MAP_EXTENSION_INDEX.json", "PUBLICATION_COVERAGE.json"]}, sort_keys=True))
