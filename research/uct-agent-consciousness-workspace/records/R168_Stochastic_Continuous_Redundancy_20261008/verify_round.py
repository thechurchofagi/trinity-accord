#!/usr/bin/env python3
"""Structural, exact-result, scope, and direction validation for R168."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH_PATH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT_PATH = HERE / "MAP_EXTENSION.json"
NOTE_PATH = HERE / "Stochastic_Continuous_and_Partially_Observed_Redundancy_v0_1.md"
RESULTS_PATH = HERE / "EXACT_CHECKS.json"
OUT_PATH = HERE / "MAP_AUDIT.json"

def digest(path): return sha256(path.read_bytes()).hexdigest()

graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
ext = json.loads(EXT_PATH.read_text(encoding="utf-8"))
results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
checks = []
def record(name, ok, detail): checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})

record("note_hash_frozen", digest(NOTE_PATH) == ext["note_sha256"], digest(NOTE_PATH))
record("graph_revision", graph["revision"] == "R168-v1.0", graph["revision"])
record("graph_counts", (len(graph["nodes"]), len(graph["rules"]), len(graph["context_links"])) == (468, 222, 125), {"nodes": len(graph["nodes"]), "rules": len(graph["rules"]), "context_links": len(graph["context_links"])})
node_ids = [n["id"] for n in graph["nodes"]]
rule_ids = [r["id"] for r in graph["rules"]]
node_set = set(node_ids)
record("unique_ids", len(node_ids) == len(node_set) and len(rule_ids) == len(set(rule_ids)), {"nodes": len(node_set), "rules": len(set(rule_ids))})
bad_endpoints = [r["id"] for r in graph["rules"] if r["conclusion"] not in node_set or not set(r["all_of"]) <= node_set]
bad_links = [l for l in graph["context_links"] if l["from"] not in node_set or l["to"] not in node_set]
record("all_rule_and_context_endpoints_exist", not bad_endpoints and not bad_links, {"rules": bad_endpoints, "links": bad_links})
adj = {n: [] for n in node_set}; indeg = {n: 0 for n in node_set}
for rule in graph["rules"]:
    for premise in rule["all_of"]:
        adj[premise].append(rule["conclusion"]); indeg[rule["conclusion"]] += 1
queue = [n for n,d in indeg.items() if d == 0]; seen = 0
while queue:
    cur = queue.pop(); seen += 1
    for nxt in adj[cur]:
        indeg[nxt] -= 1
        if indeg[nxt] == 0: queue.append(nxt)
record("dag", seen == len(node_set), {"visited": seen, "total": len(node_set)})

parent = deepcopy(graph)
parent["nodes"] = parent["nodes"][:459]
parent["rules"] = parent["rules"][:219]
parent["context_links"] = parent["context_links"][:121]
parent["revision"] = "R167-v1.0"
parent.pop("research_R168")
parent_bytes = (json.dumps(parent, indent=2, ensure_ascii=False) + "\n").encode()
record("exact_parent_reconstruction", sha256(parent_bytes).hexdigest() == ext["parent_sha256"], sha256(parent_bytes).hexdigest())

rnodes = graph["nodes"][459:]
rrules = graph["rules"][219:]
fields = ("statement", "domain", "scope", "source", "source_lineage", "status", "proof", "counterexamples_and_limits", "formal_contract_R168")
record("new_node_contract_fields", all(all(n.get(f) for f in fields) for n in rnodes), [n["id"] for n in rnodes])
record("new_rules_explicit_all_of", all(r.get("all_of") and r["formal_contract_R168"]["premise_connective"] == "AND" for r in rrules), {r["id"]: r["all_of"] for r in rrules})
expected = {
  "r168_lifted_hidden_context_bound": ["R168:SHARP_METRIC_ENVELOPE", "R168:PARTIAL_VIEW_NONENTAILMENT", "R168:PARTIAL_VIEW_LIFT_CONTRACT"],
  "r168_envelope_relative_triage": ["R167:CLOSURE_RELATIVE_TRIAGE", "R168:STOCHASTIC_CONTEXTUAL_EFFECT", "R168:SHARP_METRIC_ENVELOPE", "R168:LIFTED_HIDDEN_CONTEXT_BOUND", "R168:RANDOM_CONTEXT_MASS_BOUND", "R168:AMPLITUDE_MASS_SEPARATION"],
  "r168_stochastic_witness_refinement": ["R166:TOKEN_INSTALLATION_WITNESS_CONTRACT", "R167:TOKEN_LINEAGE_INTERVAL_CONTRACT", "R167:OPERATIONAL_MEDIATOR_ARCHITECTURE", "R168:ENVELOPE_RELATIVE_TRIAGE"]
}
actual = {r["id"]: r["all_of"] for r in rrules}
record("joint_premises_exact", actual == expected, actual)
record("no_partial_view_shortcut", not any(r["conclusion"] == "R168:LIFTED_HIDDEN_CONTEXT_BOUND" and "R168:PARTIAL_VIEW_LIFT_CONTRACT" not in r["all_of"] for r in rrules), "hidden-fiber bound requires lift contract")
record("mass_never_promoted_to_amplitude", not any(r["conclusion"] == "R168:SHARP_METRIC_ENVELOPE" and "R168:RANDOM_CONTEXT_MASS_BOUND" in r["all_of"] for r in rrules), "mass and amplitude remain distinct")
forbidden = {"A:C1", "A:U1", "F153-11", "F153-17", "R166:EXPERIENTIAL_COUNTERPART_BOUNDARY"}
record("no_reverse_to_C1_basal_gate_or_familiar_mineness", not any(r["conclusion"] in forbidden for r in rrules), [r["conclusion"] for r in rrules])
non_deductive_markers = ("not a replacement", "context only", "analogous quantifier warning", "no envelope")
record("all_context_links_non_deductive", all(any(marker in l.get("relation", "").lower() for marker in non_deductive_markers) for l in ext["context_links"]), ext["context_links"])

record("metric_envelope_enumeration", results["metric_envelope"]["finite_line_cases"] == 3896 and results["metric_envelope"]["pointwise_upper_checks"] == 18536 and results["metric_envelope"]["pointwise_sharpness_checks"] == 18536, results["metric_envelope"])
record("fill_distance_sharpness", results["fill_distance"] == {"context_sets": 1012, "sharp_equalities": 1012}, results["fill_distance"])
record("partial_view_counterexample", results["partial_observation_nonidentification"]["max_effect_gap"] == 1, results["partial_observation_nonidentification"])
record("mass_bound_cases", results["random_context_mass"]["exact_fraction_cases"] == 1100, results["random_context_mass"])
record("status_priority", results["status_priority"]["boolean_assignments"] == 16, results["status_priority"])
record("claim_limits", all(v is False for v in results["claim_limits"].values()), results["claim_limits"])
required = ["ROUND_RECORD.md", "Stochastic_Continuous_and_Partially_Observed_Redundancy_v0_1.md", "PROOF_LEDGER.json", "GAP_LEDGER.json", "SOURCE_LEDGER.json", "MAP_EXTENSION.json", "verify_envelope.py", "EXACT_CHECKS.json", "build_map.py"]
record("required_core_artifacts_present", all((HERE/f).exists() for f in required), required)

payload = {"schema": "UCT_R168_MAP_AUDIT/v1", "round": "R168", "status": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL", "checks": checks, "graph_sha256": digest(GRAPH_PATH), "exact_results_sha256": digest(RESULTS_PATH), "limitations": ["DAG, exact finite checks and a sharp envelope do not establish theory truth or empirical installation.", "The metric, Lipschitz constant, tested upper bounds, hidden-context lift, sampling measure and sensitivity remain application premises.", "No complete neural route, C1 derivation, B_min validation, basal-experience gate or unique owner follows."]}
OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"status": payload["status"], "checks": len(checks), "graph_sha256": payload["graph_sha256"], "exact_results_sha256": payload["exact_results_sha256"]}, indent=2))
if payload["status"] != "PASS": raise SystemExit(1)
