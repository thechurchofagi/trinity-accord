#!/usr/bin/env python3
"""Apply the R162 extension once to the exact R161 parent graph."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT = HERE / "MAP_EXTENSION.json"
NOTE = HERE / "Independent_Pilot_and_Covariance_Identification_v0_1.md"

raw = GRAPH.read_bytes()
ext = json.loads(EXT.read_text(encoding="utf-8"))
assert sha256(raw).hexdigest() == ext["parent_sha256"], "wrong parent graph or extension already applied"
assert sha256(NOTE.read_bytes()).hexdigest() == ext["note_sha256"], "note changed after extension freeze"

graph = json.loads(raw)
assert graph["revision"] == ext["parent_revision"]
assert len(graph["nodes"]) == 425 and len(graph["rules"]) == 204

old_nodes = deepcopy(graph["nodes"])
old_rules = deepcopy(graph["rules"])
old_context = deepcopy(graph["context_links"])

contract = {
    "object_domain": "One fixed R161 protocol version, its public component-source audit, and a prospective disjoint pilot/confirmatory design; no human work occurred.",
    "quantifiers": "Eight participant-level signed contrasts, one joint covariance, m=8 simultaneous intervals, one pilot-selection map and every frozen plan in its range.",
    "bearer_time_signature": "Population estimators compare distinct participant/trial tokens; no common complete K,D,Phi,h or within-experience covariance is inferred.",
    "source_anchor": {
        "path": str(NOTE.relative_to(ROOT)),
        "sha256": ext["note_sha256"],
        "locator": "§§2–12"
    },
    "purpose": "Prevent covariance borrowing and same-data plan rescue while making R161 uncertainty planning prospectively testable.",
    "thought_experiments": str(NOTE.relative_to(ROOT)) + " §11",
    "open_obligations": ["F153-09", "F153-10", "F153-11", "F153-12", "F153-17", "R161-G1", "R161-G5", "R161-G7", "R162-G2", "R162-G3", "R162-G7"],
    "machine_formalized": False
}

for node in ext["new_nodes"]:
    n = deepcopy(node)
    n["formal_contract_R162"] = deepcopy(contract)
    n["formal_contract_R162"]["premise_routes"] = [
        {"rule": rule["id"], "all_of": rule["all_of"]}
        for rule in ext["new_rules"] if rule["conclusion"] == n["id"]
    ]
    graph["nodes"].append(n)

for rule in ext["new_rules"]:
    rr = deepcopy(rule)
    rr["formal_contract_R162"] = {
        "premise_connective": "AND",
        "bindings_required": [
            "same fixed R161 protocol, contrast order, normalization and epsilon",
            "source marginals distinguished from jointly observed participant vectors",
            "disjoint pilot and confirmatory records or separately valid conditional calibration",
            "same simultaneous interval family and all six R161 gates",
            "no population-statistic-to-C1, B_min or F_O reverse inference"
        ],
        "quantification": "One declared protocol version and target population; every pilot-selected frozen plan must meet the conditional-coverage premise.",
        "proof_location": str(NOTE.relative_to(ROOT)) + " §§4–8",
        "source_sha256": ext["note_sha256"],
        "machine_proof": False
    }
    graph["rules"].append(rr)

graph["revision"] = "R162-v1.0"
graph["date"] = "2026-10-08"
graph["research_R162"] = {
    "start_head": "dc5f20854ad148359a46a22efa41a1cc7ff1e558",
    "parent_graph_sha256": ext["parent_sha256"],
    "note": str(NOTE.relative_to(ROOT)),
    "new_nodes": 5,
    "new_rules": 2,
    "status": "COVARIANCE_NONIDENTIFICATION_AND_INDEPENDENT_PILOT_FREEZE_CONTRACT",
    "raw_public_data_reanalysis": False,
    "actual_pilot": False,
    "ethics_approval": False,
    "empirical_F_witness": False,
    "global_semantic_proof": False
}

assert graph["nodes"][:425] == old_nodes
assert graph["rules"][:204] == old_rules
assert graph["context_links"] == old_context
assert len(graph["nodes"]) == 430 and len(graph["rules"]) == 206
assert len({n["id"] for n in graph["nodes"]}) == 430
assert len({r["id"] for r in graph["rules"]}) == 206

node_ids = {n["id"] for n in graph["nodes"]}
for rule in graph["rules"]:
    assert rule["conclusion"] in node_ids
    assert set(rule["all_of"]) <= node_ids

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
