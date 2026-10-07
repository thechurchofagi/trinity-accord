#!/usr/bin/env python3
"""Structural, scope, exact-result, and boundary validation for R167."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH_PATH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT_PATH = HERE / "MAP_EXTENSION.json"
NOTE_PATH = HERE / "Operational_Mediator_Redundancy_and_Compensation_v0_1.md"
RESULTS_PATH = HERE / "EXACT_CHECKS.json"
OUT_PATH = HERE / "VALIDATION.json"

def digest(path): return sha256(path.read_bytes()).hexdigest()

graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
ext = json.loads(EXT_PATH.read_text(encoding="utf-8"))
results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
checks = []
def record(name, ok, detail): checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})

record("note_hash_frozen", digest(NOTE_PATH) == ext["note_sha256"], digest(NOTE_PATH))
record("graph_revision", graph["revision"] == "R167-v1.0", graph["revision"])
record("graph_counts", (len(graph["nodes"]), len(graph["rules"]), len(graph["context_links"])) == (459, 219, 121), {"nodes": len(graph["nodes"]), "rules": len(graph["rules"]), "context_links": len(graph["context_links"])})
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
parent["nodes"] = parent["nodes"][:452]
parent["rules"] = parent["rules"][:217]
parent["context_links"] = parent["context_links"][:117]
parent["revision"] = "R166-v1.0"
parent.pop("research_R167")
parent_bytes = (json.dumps(parent, indent=2, ensure_ascii=False) + "\n").encode()
record("exact_parent_reconstruction", sha256(parent_bytes).hexdigest() == ext["parent_sha256"], sha256(parent_bytes).hexdigest())

rnodes = graph["nodes"][452:]
rrules = graph["rules"][217:]
fields = ("statement", "domain", "scope", "source", "source_lineage", "status", "proof", "counterexamples_and_limits", "formal_contract_R167")
record("new_node_contract_fields", all(all(n.get(f) for f in fields) for n in rnodes), [n["id"] for n in rnodes])
record("new_rules_explicit_all_of", all(r.get("all_of") and r["formal_contract_R167"]["premise_connective"] == "AND" for r in rrules), {r["id"]: r["all_of"] for r in rrules})
expected = {
  "r167_closure_relative_triage": ["R167:TOKEN_LINEAGE_INTERVAL_CONTRACT", "R167:OPERATIONAL_MEDIATOR_ARCHITECTURE", "R167:CONTEXTUAL_USE_CRITERION", "R167:SINGLE_CUT_REDUNDANCY_OBSTRUCTION", "R167:COMPENSATION_TIMING_OBSTRUCTION"],
  "r167_operational_witness_application": ["R157:DEFINABLE_SELECTOR_SETUP", "R159:ANCHOR_BINDING_CONTRACT", "R166:TOKEN_INSTALLATION_WITNESS_CONTRACT", "R167:TOKEN_LINEAGE_INTERVAL_CONTRACT", "R167:OPERATIONAL_MEDIATOR_ARCHITECTURE", "R167:CLOSURE_RELATIVE_TRIAGE"]
}
actual = {r["id"]: r["all_of"] for r in rrules}
record("joint_premises_exact", actual == expected, actual)
record("no_obstruction_directly_promoted_to_installation", not any(r["conclusion"] == "R167:R166_WITNESS_APPLICATION_BOUNDARY" and ("R167:SINGLE_CUT_REDUNDANCY_OBSTRUCTION" in r["all_of"] or "R167:COMPENSATION_TIMING_OBSTRUCTION" in r["all_of"]) for r in rrules), "obstructions act through bounded triage, not positive evidence")
forbidden = {"A:C1", "A:U1", "F153-11", "F153-17", "R166:EXPERIENTIAL_COUNTERPART_BOUNDARY"}
record("no_reverse_to_C1_basal_gate_or_familiar_mineness", not any(r["conclusion"] in forbidden for r in rrules), [r["conclusion"] for r in rrules])
record("all_context_links_non_deductive", all("deduction" in l["relation"] or "context" in l["relation"] or "not a replacement" in l["relation"] or "no operational" in l["relation"] for l in ext["context_links"]), ext["context_links"])

ctx = results["contextual_redundancy"]
record("boolean_function_enumeration", ctx["functions_checked"] == 65812 and ctx["by_backup_count"]["3"]["boolean_functions"] == 65536, ctx)
record("single_cut_counterexample", results["single_cut_false_negative"]["single_context_null_is_false_negative"] is True, results["single_cut_false_negative"])
record("compensation_counterexample", results["compensation_timing_obstruction"]["late_endpoint_masks_initial_contribution"] is True, results["compensation_timing_obstruction"])
record("status_priority", results["status_priority"]["boolean_assignments"] == 128, results["status_priority"])
record("claim_limits", all(v is False for v in results["claim_limits"].values()), results["claim_limits"])
required = ["ROUND_RECORD.md", "Operational_Mediator_Redundancy_and_Compensation_v0_1.md", "PROOF_LEDGER.json", "GAP_LEDGER.json", "SOURCE_LEDGER.json", "MAP_EXTENSION.json", "verify_redundancy.py", "EXACT_CHECKS.json", "build_map.py"]
record("required_core_artifacts_present", all((HERE/f).exists() for f in required), required)

payload = {"schema": "UCT_R167_VALIDATION/v1", "round": "R167", "status": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL", "checks": checks, "graph_sha256": digest(GRAPH_PATH), "exact_results_sha256": digest(RESULTS_PATH), "limitations": ["DAG and exhaustive finite checks do not establish theory truth or empirical installation.", "Operational discharge remains conditional on actual token lineage, realization, intervention fidelity, route closure and sensitivity.", "No neural completeness, C1 derivation, B_min validation, basal-experience gate, or unique owner follows."]}
OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"status": payload["status"], "checks": len(checks), "graph_sha256": payload["graph_sha256"], "exact_results_sha256": payload["exact_results_sha256"]}, indent=2))
if payload["status"] != "PASS": raise SystemExit(1)
