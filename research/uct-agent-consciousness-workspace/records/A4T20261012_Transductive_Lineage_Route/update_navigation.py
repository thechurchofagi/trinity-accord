#!/usr/bin/env python3
"""Register the disabled A4T follow-up without changing the completed graph."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ROUND = ROOT / "records" / "A4T20261012_Transductive_Lineage_Route"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(items, entry):
    return [x for x in items if x.get("id") != entry["id"]] + [entry]


def main():
    app = load(ROUND / "APPLICATION_ENTRY.json")["application"]

    state_path = ROOT / "CURRENT_STATE.json"
    state = load(state_path)
    previous_priority = state["next_priority"]
    state["next_priority_before_A4T"] = previous_priority
    state["latest_activity"] = {
        "id": app["id"],
        "type": "FOLLOWUP_APPLICATION",
        "status": app["status"],
        "source": app["source"],
    }
    state["latest_followup_application"] = app
    state["followup_applications"] = append_once(state.get("followup_applications", []), app)
    state["pending_note"] = "All prior pending identities retained. A4T adds a disabled 0/0/0 correction: an actual boundary stitch may be an identity relay or a directed transduction to a distinct successor; value equality does not identify either."
    state["publication_coverage"]["latest_update"] = "records/A4T20261012_Transductive_Lineage_Route/PUBLICATION_COVERAGE_UPDATE.json"
    state["publication_coverage"]["latest_followup_application"] = "records/A4T20261012_Transductive_Lineage_Route/PUBLICATION_COVERAGE_UPDATE.json"
    state["review_status_scope"] = "Completed v1.1.2 unchanged; 913/424/261 effective objects retain the fresh structural traversal. A4T manually rechecked C1/U1, P3/P6, R157, R159, effective R173, A4R and A4S. Deep full-history semantics remain AUDIT_INCOMPLETE."
    state["next_priority"] = "A4T next: select one accessible sampler→consumer interface and test a source-side event-incidence plus controlled-input lineage witness while independently inventorying and challenging replay, buffer and fan-in paths; stop before H_cf if the directed edge or closure is not warranted."
    save(state_path, state)

    for name in ("UNIFIED_RESEARCH_INDEX.json", "RESEARCH_REGISTRY.json", "RESEARCH_SESSION_LOG_INDEX.json"):
        path = ROOT / name
        obj = load(path)
        obj["latest_followup_application"] = app
        obj["followup_applications"] = append_once(obj.get("followup_applications", []), app)
        save(path, obj)

    coverage_path = ROOT / "PUBLICATION_COVERAGE.json"
    coverage = load(coverage_path)
    coverage["latest_update"] = {
        "id": app["id"],
        "coverage_change": "NONE",
        "source": "records/A4T20261012_Transductive_Lineage_Route/PUBLICATION_COVERAGE_UPDATE.json",
        "manuscript_decision": "HOLD",
    }
    coverage["latest_followup_application"] = app
    coverage["followup_applications"] = append_once(coverage.get("followup_applications", []), app)
    save(coverage_path, coverage)


if __name__ == "__main__":
    main()
