#!/usr/bin/env python3
"""Bounded structural and numeric validation for R163."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH_PATH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT_PATH = HERE / "MAP_EXTENSION.json"
NOTE_PATH = HERE / "Bounded_Planwise_Coverage_and_Missingness_v0_1.md"
RESULTS_PATH = HERE / "STRESS_TEST_RESULTS.json"
OUT_PATH = HERE / "VALIDATION.json"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
ext = json.loads(EXT_PATH.read_text(encoding="utf-8"))
results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

checks: list[dict] = []


def record(name: str, ok: bool, detail: object) -> None:
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})


record("note_hash_frozen", digest(NOTE_PATH) == ext["note_sha256"], digest(NOTE_PATH))
record("graph_revision", graph["revision"] == "R163-v1.0", graph["revision"])
record("graph_counts", len(graph["nodes"]) == 436 and len(graph["rules"]) == 209 and len(graph["context_links"]) == 117,
       {"nodes": len(graph["nodes"]), "rules": len(graph["rules"]), "context_links": len(graph["context_links"])})

node_ids = [node["id"] for node in graph["nodes"]]
rule_ids = [rule["id"] for rule in graph["rules"]]
record("unique_ids", len(node_ids) == len(set(node_ids)) and len(rule_ids) == len(set(rule_ids)),
       {"unique_nodes": len(set(node_ids)), "unique_rules": len(set(rule_ids))})
node_set = set(node_ids)
bad_endpoints = [rule["id"] for rule in graph["rules"] if rule["conclusion"] not in node_set or not set(rule["all_of"]) <= node_set]
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
parent["nodes"] = parent["nodes"][:430]
parent["rules"] = parent["rules"][:206]
parent["revision"] = "R162-v1.0"
parent.pop("research_R163")
parent_bytes = (json.dumps(parent, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
record("exact_parent_reconstruction", sha256(parent_bytes).hexdigest() == ext["parent_sha256"], sha256(parent_bytes).hexdigest())

r163_nodes = graph["nodes"][430:]
r163_rules = graph["rules"][206:]
record("new_node_contract_fields", all(
    all(field in node and node[field] for field in ("statement", "domain", "scope", "source", "status", "proof", "counterexamples_and_limits", "formal_contract_R163"))
    for node in r163_nodes), [node["id"] for node in r163_nodes])
record("new_rules_are_explicit_all_of", all(rule.get("all_of") and rule["formal_contract_R163"]["premise_connective"] == "AND" for rule in r163_rules),
       {rule["id"]: rule["all_of"] for rule in r163_rules})

coverage_rule = next(rule for rule in r163_rules if rule["id"] == "r163_bounded_planwise_coverage")
record("coverage_joint_premises_exact", coverage_rule["all_of"] == [
    "R161:CONCRETE_CROSSED_PROTOCOL", "R162:INDEPENDENT_PILOT_FREEZE_CONTRACT", "R163:BOUNDED_FINITE_DESIGN_TARGET"
], coverage_rule["all_of"])

forbidden_targets = {"A:C1", "F153-11", "F153-17", "R159:SELECTED_OWNERSHIP_APPLICATION"}
bad_reverse = [rule["id"] for rule in r163_rules if rule["conclusion"] in forbidden_targets]
record("no_r163_statistic_to_experience_reverse_rule", not bad_reverse, bad_reverse)

rare36 = next(item for item in results["rare_spike_exact"] if item["n"] == 36)
record("rare_spike_exact_value", abs(rare36["simultaneous_coverage_exact_for_8_independent_components"] - 0.2531493943720002) < 1e-15,
       rare36["simultaneous_coverage_exact_for_8_independent_components"])
record("hoeffding_width_threshold", results["n_for_half_width_at_most_005"] == 4615,
       results["n_for_half_width_at_most_005"])

support_grid_ok = True
for y_times_10 in range(-10, 11):
    y = y_times_10 / 10
    for r in (0, 1):
        lower = r * y - (1 - r)
        upper = r * y + (1 - r)
        support_grid_ok &= lower <= y <= upper
record("missingness_pointwise_support_grid", support_grid_ok, "21 outcomes x 2 observation states")

record("clipping_countermodel", min(1, max(-1, 2)) == min(1, max(-1, 100)) == 1 and 2 != 100,
       {"observed": [1, 1], "latent_means": [2, 100]})
record("order_target_countermodel", 0.4 * ((-1 + 1) / 2) == 0 and 0.4 * 1 == 0.4,
       {"balanced_mixture": 0.0, "canonical_plus": 0.4})

required_files = [
    "ROUND_RECORD.md", "Bounded_Planwise_Coverage_and_Missingness_v0_1.md", "PROOF_LEDGER.json",
    "GAP_LEDGER.json", "AMENDMENTS.json", "SOURCE_LEDGER.json", "MAP_EXTENSION.json",
    "MAP_AUDIT.json", "stress_test.py", "STRESS_TEST_RESULTS.json", "build_map.py"
]
record("required_artifacts_present", all((HERE / name).exists() for name in required_files), required_files)

payload = {
    "schema": "UCT_R163_VALIDATION/v1",
    "round": "R163",
    "status": "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL",
    "checks": checks,
    "graph_sha256": digest(GRAPH_PATH),
    "stress_results_sha256": digest(RESULTS_PATH),
    "limitations": [
        "DAG and executable checks do not prove theory truth, source completeness, apparatus fidelity or global semantics.",
        "General coverage and incompatibility arguments remain manually reviewed mathematical proofs.",
        "Monte Carlo blocks are diagnostics only; exact enumeration and analytic inequalities carry the formal claims."
    ]
}
OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))

