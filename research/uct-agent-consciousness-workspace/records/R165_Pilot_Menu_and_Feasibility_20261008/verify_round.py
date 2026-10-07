#!/usr/bin/env python3
"""Bounded structural and numeric validation for R165."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH_PATH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT_PATH = HERE / "MAP_EXTENSION.json"
NOTE_PATH = HERE / "Pilot_Menu_Width_Certification_and_Feasibility_v0_1.md"
RESULTS_PATH = HERE / "EXACT_CHECKS.json"
OUT_PATH = HERE / "VALIDATION.json"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
ext = json.loads(EXT_PATH.read_text(encoding="utf-8"))
results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
checks = []


def record(name, ok, detail):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})


record("note_hash_frozen", digest(NOTE_PATH) == ext["note_sha256"], digest(NOTE_PATH))
record("graph_revision", graph["revision"] == "R165-v1.0", graph["revision"])
record("graph_counts", len(graph["nodes"]) == 446 and len(graph["rules"]) == 215 and len(graph["context_links"]) == 117,
       {"nodes": len(graph["nodes"]), "rules": len(graph["rules"]), "context_links": len(graph["context_links"])})

node_ids = [node["id"] for node in graph["nodes"]]
rule_ids = [rule["id"] for rule in graph["rules"]]
record("unique_ids", len(node_ids) == len(set(node_ids)) and len(rule_ids) == len(set(rule_ids)),
       {"nodes": len(set(node_ids)), "rules": len(set(rule_ids))})
node_set = set(node_ids)
bad_endpoints = [rule["id"] for rule in graph["rules"]
                 if rule["conclusion"] not in node_set or not set(rule["all_of"]) <= node_set]
record("all_rule_endpoints_exist", not bad_endpoints, bad_endpoints)

adj = {node_id: [] for node_id in node_set}
indeg = {node_id: 0 for node_id in node_set}
for rule in graph["rules"]:
    for premise in rule["all_of"]:
        adj[premise].append(rule["conclusion"])
        indeg[rule["conclusion"]] += 1
queue = [node_id for node_id, degree in indeg.items() if degree == 0]
seen = 0
while queue:
    current = queue.pop()
    seen += 1
    for nxt in adj[current]:
        indeg[nxt] -= 1
        if indeg[nxt] == 0:
            queue.append(nxt)
record("dag", seen == len(node_set), {"visited": seen, "total": len(node_set)})

parent = deepcopy(graph)
parent["nodes"] = parent["nodes"][:440]
parent["rules"] = parent["rules"][:212]
parent["revision"] = "R164-v1.0"
parent.pop("research_R165")
parent_bytes = (json.dumps(parent, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
record("exact_parent_reconstruction", sha256(parent_bytes).hexdigest() == ext["parent_sha256"], sha256(parent_bytes).hexdigest())

r165_nodes = graph["nodes"][440:]
r165_rules = graph["rules"][212:]
fields = ("statement", "domain", "scope", "source", "source_lineage", "status", "proof", "counterexamples_and_limits", "formal_contract_R165")
record("new_node_contract_fields", all(all(node.get(field) for field in fields) for node in r165_nodes), [n["id"] for n in r165_nodes])
record("new_rules_are_explicit_all_of", all(rule.get("all_of") and rule["formal_contract_R165"]["premise_connective"] == "AND" for rule in r165_rules),
       {r["id"]: r["all_of"] for r in r165_rules})

expected = {
    "r165_pilot_selection_coverage_invariance": ["R162:PLANWISE_COVERAGE_PREMISE", "R164:FROZEN_BOUNDED_MARTINGALE_COVERAGE", "R165:FINITE_PILOT_MENU_CONTRACT"],
    "r165_pilot_width_regret_certificate": ["R164:FROZEN_BOUNDED_MARTINGALE_COVERAGE", "R165:FINITE_PILOT_MENU_CONTRACT", "R165:RESIDUAL_TRANSPORT_PREMISE"],
    "r165_three_way_feasibility_triage": ["R161:ADMISSIBILITY_GATE", "R165:FINITE_PILOT_MENU_CONTRACT", "R165:PILOT_WIDTH_REGRET_CERTIFICATE"],
}
actual = {r["id"]: r["all_of"] for r in r165_rules}
record("joint_premises_exact", actual == expected, actual)
record("transport_not_inferred_from_independence", not any(r["conclusion"] == "R165:RESIDUAL_TRANSPORT_PREMISE" for r in graph["rules"]), "premise remains open")

forbidden = {"A:C1", "F153-11", "F153-17", "R159:SELECTED_OWNERSHIP_APPLICATION"}
bad_reverse = [r["id"] for r in r165_rules if r["conclusion"] in forbidden]
record("no_statistic_to_experience_reverse_rule", not bad_reverse, bad_reverse)
record("exact_check_status", results["status"] == "PASS", results["status"])
record("transport_grid", results["checks"]["transport_band_grid"]["cases"] == 475 and results["checks"]["transport_band_grid"]["bounds_cover"], results["checks"]["transport_band_grid"])
record("triage_grid", results["checks"]["triage_exhaustive_grid"]["cases"] == 6125 and results["checks"]["triage_exhaustive_grid"]["pass"], results["checks"]["triage_exhaustive_grid"])
record("counterexample", results["checks"]["no_transport_reversal"]["pass"], results["checks"]["no_transport_reversal"])
record("same_data_selection_guard", results["checks"]["same_data_selection_inflation"]["pass"], results["checks"]["same_data_selection_inflation"])
record("worked_menu", results["checks"]["worked_menu"]["pass"], results["checks"]["worked_menu"]["states"])

required = ["ROUND_RECORD.md", "Pilot_Menu_Width_Certification_and_Feasibility_v0_1.md", "PROOF_LEDGER.json", "GAP_LEDGER.json", "AMENDMENTS.json", "SOURCE_LEDGER.json", "MAP_EXTENSION.json", "MAP_AUDIT.json", "exact_checks.py", "EXACT_CHECKS.json", "build_map.py", "REVIEW_ZH.md", "CURRENT_HANDOFF.md"]
record("required_artifacts_present", all((HERE / name).exists() for name in required), required)

payload = {
    "schema": "UCT_R165_VALIDATION/v1",
    "round": "R165",
    "status": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL",
    "checks": checks,
    "graph_sha256": digest(GRAPH_PATH),
    "exact_results_sha256": digest(RESULTS_PATH),
    "limitations": [
        "DAG and finite grids do not prove theory truth, transport validity, apparatus fidelity or global semantics.",
        "The general coverage, width and regret arguments remain manually reviewed mathematical proofs.",
        "Synthetic values are not human data, power guarantees or recruitment recommendations."
    ]
}
OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))
