#!/usr/bin/env python3
"""Apply the R161 extension once to the exact R160 parent graph."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT = HERE / "MAP_EXTENSION.json"
NOTE = HERE / "Concrete_Body_Tool_Protocol_and_Falsifier_v0_1.md"

raw = GRAPH.read_bytes()
ext = json.loads(EXT.read_text(encoding="utf-8"))
assert sha256(raw).hexdigest() == ext["parent_sha256"], "wrong parent graph or extension already applied"
assert sha256(NOTE.read_bytes()).hexdigest() == ext["note_sha256"], "note changed after extension freeze"

graph = json.loads(raw)
assert graph["revision"] == ext["parent_revision"]
assert len(graph["nodes"]) == 422 and len(graph["rules"]) == 202

old_nodes = deepcopy(graph["nodes"])
old_rules = deepcopy(graph["rules"])
old_context = deepcopy(graph["context_links"])

contract = {
    "object_domain": "Prospective fixed human upper-limb protocol; actual execution and ethics approval are not claimed.",
    "quantifiers": "For one fixed protocol, eight conditional simple effects, simultaneous intervals, six fidelity gates and epsilon>0; no universal body/F_O equivalence.",
    "bearer_time_signature": "Each trial/session fixes its own P_omega,I_omega,K_omega,D_omega,Phi_omega,h_omega; participant lineage supplies no common complete organization.",
    "source_anchor": {
        "path": str(NOTE.relative_to(ROOT)),
        "sha256": ext["note_sha256"],
        "locator": "§§2–13"
    },
    "purpose": "Make the R160 physical-witness profile prospectively executable and distinguish exclusion from invalid manipulation and uncertainty.",
    "thought_experiments": str((HERE / "Concrete_Body_Tool_Protocol_and_Falsifier_v0_1.md").relative_to(ROOT)) + " §10",
    "open_obligations": ["F153-09", "F153-10", "F153-11", "F153-12", "F153-17", "R161-G1", "R161-G5", "R161-G7"],
    "machine_formalized": False
}

for node in ext["new_nodes"]:
    n = deepcopy(node)
    n["formal_contract_R161"] = deepcopy(contract)
    n["formal_contract_R161"]["premise_routes"] = [
        {"rule": rule["id"], "all_of": rule["all_of"]}
        for rule in ext["new_rules"] if rule["conclusion"] == n["id"]
    ]
    graph["nodes"].append(n)

for rule in ext["new_rules"]:
    rr = deepcopy(rule)
    rr["formal_contract_R161"] = {
        "premise_connective": "AND",
        "bindings_required": [
            "same fixed protocol and normalization",
            "all six fidelity gates for classification",
            "same simultaneous interval family and epsilon",
            "no profile-to-C1, B_min or F_O reverse inference"
        ],
        "quantification": "One preregistered protocol instance; terminal decisions have simultaneous-coverage qualification.",
        "proof_location": str(NOTE.relative_to(ROOT)) + " §§6–9",
        "source_sha256": ext["note_sha256"],
        "machine_proof": False
    }
    graph["rules"].append(rr)

graph["revision"] = "R161-v1.0"
graph["date"] = "2026-10-08"
graph["research_R161"] = {
    "start_head": "2f8988729ad63b55ba3850b11d421a65a9015fe2",
    "parent_graph_sha256": ext["parent_sha256"],
    "note": str(NOTE.relative_to(ROOT)),
    "new_nodes": 3,
    "new_rules": 2,
    "status": "CONCRETE_PROTOCOL_AND_STRONG_FALSIFIER_WITH_BRIDGE_OPEN",
    "actual_experiment": False,
    "ethics_approval": False,
    "empirical_F_witness": False,
    "global_semantic_proof": False
}

assert graph["nodes"][:422] == old_nodes
assert graph["rules"][:202] == old_rules
assert graph["context_links"] == old_context
assert len(graph["nodes"]) == 425 and len(graph["rules"]) == 204
assert len({n["id"] for n in graph["nodes"]}) == 425
assert len({r["id"] for r in graph["rules"]}) == 204

node_ids = {n["id"] for n in graph["nodes"]}
for rule in graph["rules"]:
    assert rule["conclusion"] in node_ids
    assert set(rule["all_of"]) <= node_ids

# DAG check over registered deductive rules.
adj = {nid: [] for nid in node_ids}
indeg = {nid: 0 for nid in node_ids}
for rule in graph["rules"]:
    for premise in rule["all_of"]:
        adj[premise].append(rule["conclusion"])
        indeg[rule["conclusion"]] += 1
queue = [n for n, d in indeg.items() if d == 0]
seen = 0
while queue:
    u = queue.pop()
    seen += 1
    for v in adj[u]:
        indeg[v] -= 1
        if indeg[v] == 0:
            queue.append(v)
assert seen == len(node_ids), "cycle detected"

GRAPH.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({
    "revision": graph["revision"],
    "nodes": len(graph["nodes"]),
    "rules": len(graph["rules"]),
    "context_links": len(graph["context_links"]),
    "parent_prefix_preserved": True,
    "dag": "PASS",
    "graph_sha256": sha256(GRAPH.read_bytes()).hexdigest()
}, indent=2))
