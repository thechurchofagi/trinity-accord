#!/usr/bin/env python3
"""Structural, scope and exact-result validation for R166."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH_PATH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT_PATH = HERE / "MAP_EXTENSION.json"
NOTE_PATH = HERE / "Token_Installation_Witness_and_Mineness_Boundary_v0_1.md"
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
record("graph_revision", graph["revision"] == "R166-v1.0", graph["revision"])
record("graph_counts", len(graph["nodes"]) == 452 and len(graph["rules"]) == 217 and len(graph["context_links"]) == 117,
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
parent["nodes"] = parent["nodes"][:446]
parent["rules"] = parent["rules"][:215]
parent["revision"] = "R165-v1.0"
parent.pop("research_R166")
parent_bytes = (json.dumps(parent, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
record("exact_parent_reconstruction", sha256(parent_bytes).hexdigest() == ext["parent_sha256"], sha256(parent_bytes).hexdigest())

r166_nodes = graph["nodes"][446:]
r166_rules = graph["rules"][215:]
fields = ("statement", "domain", "scope", "source", "source_lineage", "status", "proof", "counterexamples_and_limits", "formal_contract_R166")
record("new_node_contract_fields", all(all(node.get(field) for field in fields) for node in r166_nodes), [n["id"] for n in r166_nodes])
record("new_rules_are_explicit_all_of", all(rule.get("all_of") and rule["formal_contract_R166"]["premise_connective"] == "AND" for rule in r166_rules),
       {r["id"]: r["all_of"] for r in r166_rules})

expected = {
    "r166_witnessed_frame_installation": ["R157:DEFINABLE_SELECTOR_SETUP", "R159:ANCHOR_BINDING_CONTRACT", "R166:TOKEN_INSTALLATION_WITNESS_CONTRACT"],
    "r166_experiential_counterpart_boundary": ["R157:SEMANTIC_RESIDUAL", "R159:FRAME_RELATION_TRANSPORT", "R166:WITNESSED_FRAME_INSTALLATION"],
}
actual = {r["id"]: r["all_of"] for r in r166_rules}
record("joint_premises_exact", actual == expected, actual)

record("no_population_to_token_rule", not any("POPULATION_TOKEN_NONENTAILMENT" in r["all_of"] and r["conclusion"] == "R166:WITNESSED_FRAME_INSTALLATION" for r in graph["rules"]), "counterexample cannot promote a population profile")
record("no_trace_to_installation_rule", not any("FINITE_TRACE_INSTALLATION_NONENTAILMENT" in r["all_of"] and r["conclusion"] == "R166:WITNESSED_FRAME_INSTALLATION" for r in graph["rules"]), "finite trace alone cannot promote installation")
record("semantic_residual_is_joint_premise", actual["r166_experiential_counterpart_boundary"][0] == "R157:SEMANTIC_RESIDUAL", actual["r166_experiential_counterpart_boundary"])

forbidden = {"A:C1", "F153-11", "F153-17", "R159:SELECTED_OWNERSHIP_APPLICATION"}
bad_reverse = [r["id"] for r in r166_rules if r["conclusion"] in forbidden]
record("no_installation_to_C1_or_familiar_target_reverse_rule", not bad_reverse, bad_reverse)

pop = results["population_token_obstruction"]
trace = results["finite_trace_obstruction"]
conj = results["installation_contract_conjunction"]
record("population_exact_checks", pop["nonconstant_vectors_checked"] == 114 and pop["named_token_swap_witnesses"] == 114, pop)
record("finite_trace_exact_checks", trace["indistinguishable_natural_or_anchor_cases"] == 6 and len(trace["mediator_discriminations"]) == 2, trace)
record("contract_conjunction_checks", conj["boolean_assignments"] == 64 and conj["supporting_assignments"] == 1, conj)
record("claim_limits", all(value is False for value in results["claim_limits"].values()), results["claim_limits"])

required = ["ROUND_RECORD.md", "Token_Installation_Witness_and_Mineness_Boundary_v0_1.md", "PROOF_LEDGER.json", "GAP_LEDGER.json", "AMENDMENTS.json", "SOURCE_LEDGER.json", "MAP_EXTENSION.json", "MAP_AUDIT.json", "verify_installation.py", "EXACT_CHECKS.json", "build_map.py", "REVIEW_ZH.md", "CURRENT_HANDOFF.md"]
record("required_artifacts_present", all((HERE / name).exists() for name in required), required)

payload = {
    "schema": "UCT_R166_VALIDATION/v1",
    "round": "R166",
    "status": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL",
    "checks": checks,
    "graph_sha256": digest(GRAPH_PATH),
    "exact_results_sha256": digest(RESULTS_PATH),
    "limitations": [
        "DAG and finite countermodel checks do not prove theory truth, actual installation or C1.",
        "The installation result is conditional on empirical realization, fidelity, consistency, locality and exclusion premises.",
        "No familiar mineness interpretation follows without independent B_min and target evidence."
    ]
}
OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))
