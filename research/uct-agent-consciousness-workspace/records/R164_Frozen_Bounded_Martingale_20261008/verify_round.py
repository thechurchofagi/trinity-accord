#!/usr/bin/env python3
"""Bounded structural and numeric validation for R164."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH_PATH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT_PATH = HERE / "MAP_EXTENSION.json"
NOTE_PATH = HERE / "Frozen_Bounded_Martingale_Coverage_v0_1.md"
RESULTS_PATH = HERE / "EXACT_CHECKS.json"
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
record("graph_revision", graph["revision"] == "R164-v1.0", graph["revision"])
record(
    "graph_counts",
    len(graph["nodes"]) == 440 and len(graph["rules"]) == 212 and len(graph["context_links"]) == 117,
    {"nodes": len(graph["nodes"]), "rules": len(graph["rules"]), "context_links": len(graph["context_links"])},
)

node_ids = [node["id"] for node in graph["nodes"]]
rule_ids = [rule["id"] for rule in graph["rules"]]
record(
    "unique_ids",
    len(node_ids) == len(set(node_ids)) and len(rule_ids) == len(set(rule_ids)),
    {"unique_nodes": len(set(node_ids)), "unique_rules": len(set(rule_ids))},
)
node_set = set(node_ids)
bad_endpoints = [
    rule["id"]
    for rule in graph["rules"]
    if rule["conclusion"] not in node_set or not set(rule["all_of"]) <= node_set
]
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
parent["nodes"] = parent["nodes"][:436]
parent["rules"] = parent["rules"][:209]
parent["revision"] = "R163-v1.0"
parent.pop("research_R164")
parent_bytes = (json.dumps(parent, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
record(
    "exact_parent_reconstruction",
    sha256(parent_bytes).hexdigest() == ext["parent_sha256"],
    sha256(parent_bytes).hexdigest(),
)

r164_nodes = graph["nodes"][436:]
r164_rules = graph["rules"][209:]
required_node_fields = (
    "statement", "domain", "scope", "source", "source_lineage", "status",
    "proof", "counterexamples_and_limits", "formal_contract_R164"
)
record(
    "new_node_contract_fields",
    all(all(field in node and node[field] for field in required_node_fields) for node in r164_nodes),
    [node["id"] for node in r164_nodes],
)
record(
    "new_rules_are_explicit_all_of",
    all(rule.get("all_of") and rule["formal_contract_R164"]["premise_connective"] == "AND" for rule in r164_rules),
    {rule["id"]: rule["all_of"] for rule in r164_rules},
)

coverage_rule = next(rule for rule in r164_rules if rule["id"] == "r164_frozen_bounded_martingale_coverage")
expected_coverage_premises = [
    "R161:CONCRETE_CROSSED_PROTOCOL",
    "R162:INDEPENDENT_PILOT_FREEZE_CONTRACT",
    "R163:BOUNDED_FINITE_DESIGN_TARGET",
    "R164:CONSTANT_BET_AVERAGE_TARGET",
]
record("coverage_joint_premises_exact", coverage_rule["all_of"] == expected_coverage_premises, coverage_rule["all_of"])

missing_rule = next(rule for rule in r164_rules if rule["id"] == "r164_missingness_endpoint_martingale_band")
record(
    "missingness_joint_premises_exact",
    missing_rule["all_of"] == ["R163:ARBITRARY_MISSINGNESS_BAND", "R164:FROZEN_BOUNDED_MARTINGALE_COVERAGE"],
    missing_rule["all_of"],
)

forbidden_targets = {"A:C1", "F153-11", "F153-17", "R159:SELECTED_OWNERSHIP_APPLICATION"}
bad_reverse = [rule["id"] for rule in r164_rules if rule["conclusion"] in forbidden_targets]
record("no_r164_statistic_to_experience_reverse_rule", not bad_reverse, bad_reverse)

record("exact_check_status", results["status"] == "PASS", results["status"])
record(
    "rare_spike_event_probability",
    abs(results["rare_spike"]["probability_at_least_one_no_spike_component_at_n36"] - 0.746832681569142) < 1e-15,
    results["rare_spike"]["probability_at_least_one_no_spike_component_at_n36"],
)
record(
    "rare_spike_event_only_threshold",
    results["rare_spike"]["minimum_n_to_control_this_event_alone"] == 99,
    results["rare_spike"]["minimum_n_to_control_this_event_alone"],
)
record(
    "zero_residual_width_threshold",
    results["zero_residual"]["n_for_half_width_at_most_005"] == 257,
    results["zero_residual"]["n_for_half_width_at_most_005"],
)
row36 = next(row for row in results["rare_spike"]["rows"] if row["n"] == 36)
record(
    "rare_spike_n36_all_counts_and_width",
    row36["all_success_counts_covered"] and abs(row36["expected_half_width"] - 0.3970804573002857) < 1e-15,
    {"all_counts": row36["all_success_counts_covered"], "expected_half_width": row36["expected_half_width"]},
)
record(
    "one_step_grid",
    results["checks"]["one_step_exponential_grid"]["pass_leq_one_with_tolerance"],
    results["checks"]["one_step_exponential_grid"],
)
record("missingness_pointwise_grid", results["checks"]["missingness_pointwise_bounds"], "41 outcomes x 2 observation states")

required_files = [
    "ROUND_RECORD.md", "Frozen_Bounded_Martingale_Coverage_v0_1.md", "PROOF_LEDGER.json",
    "GAP_LEDGER.json", "AMENDMENTS.json", "SOURCE_LEDGER.json", "MAP_EXTENSION.json",
    "MAP_AUDIT.json", "exact_checks.py", "EXACT_CHECKS.json", "build_map.py", "REVIEW_ZH.md",
]
record("required_artifacts_present", all((HERE / name).exists() for name in required_files), required_files)

payload = {
    "schema": "UCT_R164_VALIDATION/v1",
    "round": "R164",
    "status": "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL",
    "checks": checks,
    "graph_sha256": digest(GRAPH_PATH),
    "exact_results_sha256": digest(RESULTS_PATH),
    "limitations": [
        "DAG and executable checks do not prove theory truth, source completeness, apparatus fidelity or global semantics.",
        "The general supermartingale, target and coverage arguments remain manually reviewed mathematical proofs.",
        "Finite grids and distribution-specific enumeration check constants and counterexamples; they do not replace analytic coverage proofs.",
    ],
}
OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))
