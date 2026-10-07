#!/usr/bin/env python3
"""Apply the R163 extension once to the exact R162 parent graph."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT = HERE / "MAP_EXTENSION.json"
NOTE = HERE / "Bounded_Planwise_Coverage_and_Missingness_v0_1.md"

raw = GRAPH.read_bytes()
ext = json.loads(EXT.read_text(encoding="utf-8"))
assert sha256(raw).hexdigest() == ext["parent_sha256"], "wrong parent graph or extension already applied"
assert sha256(NOTE.read_bytes()).hexdigest() == ext["note_sha256"], "note changed after extension freeze"

graph = json.loads(raw)
assert graph["revision"] == ext["parent_revision"]
assert len(graph["nodes"]) == 430 and len(graph["rules"]) == 206

old_nodes = deepcopy(graph["nodes"])
old_rules = deepcopy(graph["rules"])
old_context = deepcopy(graph["context_links"])

contract = {
    "object_domain": "One fixed R161 bounded eight-contrast protocol, its R162 pilot-freeze contract, and a frozen finite-design statistical target; no human work occurred.",
    "quantifiers": "N independent participant vectors, m frozen components, every pilot-selected plan in the declared bounded family, and every lower/upper missingness endpoint when full outcomes are defined.",
    "bearer_time_signature": "Population estimators compare distinct participant/trial tokens; order mixtures, clipped targets, latent variables, complete organization and within-experience relations remain distinct.",
    "source_anchor": {
        "path": str(NOTE.relative_to(ROOT)),
        "sha256": ext["note_sha256"],
        "locator": "sections 2-12"
    },
    "purpose": "Repair the bounded/Gaussian contradiction and provide exact but conservative planwise coverage without target, order, clipping, missingness or experience-level inflation.",
    "thought_experiments": str(NOTE.relative_to(ROOT)) + " section 10",
    "open_obligations": ["F153-09", "F153-10", "F153-11", "F153-12", "F153-17", "R161-G1", "R161-G5", "R161-G7", "R163-G2", "R163-G3", "R163-G6", "R163-G8"],
    "machine_formalized": False
}

for node in ext["new_nodes"]:
    n = deepcopy(node)
    n["formal_contract_R163"] = deepcopy(contract)
    n["formal_contract_R163"]["premise_routes"] = [
        {"rule": rule["id"], "all_of": rule["all_of"]}
        for rule in ext["new_rules"] if rule["conclusion"] == n["id"]
    ]
    graph["nodes"].append(n)

for rule in ext["new_rules"]:
    rr = deepcopy(rule)
    rr["formal_contract_R163"] = {
        "premise_connective": "AND",
        "bindings_required": [
            "same fixed R161 protocol, bounded component definitions, order and normalization",
            "same finite-design target and randomization distribution before outcomes",
            "independent participant vectors, distinct from within-vector component dependence",
            "same interval and missingness family for every pilot-selected plan",
            "clipped observed targets distinguished from latent effects and population statistics distinguished from token experience"
        ],
        "quantification": "One declared protocol and target; every selected bounded plan and every frozen component must satisfy the stated range and independence premises.",
        "proof_location": str(NOTE.relative_to(ROOT)) + " sections 4-9",
        "source_sha256": ext["note_sha256"],
        "machine_proof": False
    }
    graph["rules"].append(rr)

graph["revision"] = "R163-v1.0"
graph["date"] = "2026-10-08"
graph["research_R163"] = {
    "start_head": "eadf483d569df787ce421eabe83fb8b09ff7bc67",
    "parent_graph_sha256": ext["parent_sha256"],
    "note": str(NOTE.relative_to(ROOT)),
    "new_nodes": 6,
    "new_rules": 3,
    "status": "BOUNDED_PLANWISE_COVERAGE_AND_TARGET_BOUNDARIES",
    "actual_apparatus": False,
    "actual_participants": False,
    "ethics_approval": False,
    "empirical_F_witness": False,
    "global_semantic_proof": False
}

assert graph["nodes"][:430] == old_nodes
assert graph["rules"][:206] == old_rules
assert graph["context_links"] == old_context
assert len(graph["nodes"]) == 436 and len(graph["rules"]) == 209
assert len({n["id"] for n in graph["nodes"]}) == 436
assert len({r["id"] for r in graph["rules"]}) == 209

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
