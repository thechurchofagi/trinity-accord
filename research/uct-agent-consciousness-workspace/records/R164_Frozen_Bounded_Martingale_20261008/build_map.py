#!/usr/bin/env python3
"""Apply the R164 extension once to the exact R163 parent graph."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT = HERE / "MAP_EXTENSION.json"
NOTE = HERE / "Frozen_Bounded_Martingale_Coverage_v0_1.md"

raw = GRAPH.read_bytes()
ext = json.loads(EXT.read_text(encoding="utf-8"))
assert sha256(raw).hexdigest() == ext["parent_sha256"], "wrong parent graph or extension already applied"
assert sha256(NOTE.read_bytes()).hexdigest() == ext["note_sha256"], "note changed after extension freeze"

graph = json.loads(raw)
assert graph["revision"] == ext["parent_revision"]
assert len(graph["nodes"]) == 436 and len(graph["rules"]) == 209

old_nodes = deepcopy(graph["nodes"])
old_rules = deepcopy(graph["rules"])
old_context = deepcopy(graph["context_links"])

contract = {
    "object_domain": "One fixed R161 bounded eight-component confirmatory protocol, R162 independent-pilot freezing, and R163 finite-design/missingness targets; no human work occurred.",
    "quantifiers": "Finite N and m; every component and two tails; every pilot-selected constant bet/predictor plan; every well-defined lower/upper missingness endpoint when that target is invoked.",
    "bearer_time_signature": "Participant vectors, within-participant components, pilot and confirmatory samples, conditional means, finite-design means, endpoint means, actual token organization and experience remain differently typed.",
    "source_anchor": {
        "path": str(NOTE.relative_to(ROOT)),
        "sha256": ext["note_sha256"],
        "locator": "sections 2-11",
    },
    "purpose": "Improve finite bounded protocol precision without target weighting, i.i.d. inflation, rare-event erasure, missingness identification inflation or experience-level reversal.",
    "thought_experiments": str(NOTE.relative_to(ROOT)) + " section 9",
    "open_obligations": [
        "F153-09", "F153-10", "F153-11", "F153-12", "F153-17",
        "R161-G1", "R161-G5", "R161-G7", "R163-G2", "R163-G3", "R163-G6", "R163-G8",
        "R164-G1", "R164-G2", "R164-G3", "R164-G4", "R164-G5"
    ],
    "machine_formalized": False,
}

for node in ext["new_nodes"]:
    item = deepcopy(node)
    item["formal_contract_R164"] = deepcopy(contract)
    item["formal_contract_R164"]["premise_routes"] = [
        {"rule": rule["id"], "all_of": rule["all_of"]}
        for rule in ext["new_rules"]
        if rule["conclusion"] == item["id"]
    ]
    graph["nodes"].append(item)

for rule in ext["new_rules"]:
    item = deepcopy(rule)
    item["formal_contract_R164"] = {
        "premise_connective": "AND",
        "bindings_required": [
            "same fixed R161 components, signs, order, normalization and decision margin",
            "same R163 finite-design or explicitly declared average-conditional-mean target",
            "constant component bet across confirmatory i for the unweighted target",
            "predictor rule measurable before the observation it predicts",
            "independent pilot selection and no confirmatory-outcome method search",
            "independent participant vectors for the fixed R163 target; within-vector component dependence allowed",
            "well-defined would-be outcomes only when the missingness endpoint route is invoked",
            "population coverage kept distinct from actual organization and experience-level interpretation",
        ],
        "quantification": "Every selected confirmatory plan and frozen component must satisfy the boundedness, constant-bet, predictability, target and independence premises simultaneously.",
        "proof_location": str(NOTE.relative_to(ROOT)) + " sections 4-8",
        "source_sha256": ext["note_sha256"],
        "machine_proof": False,
    }
    graph["rules"].append(item)

graph["revision"] = "R164-v1.0"
graph["date"] = "2026-10-08"
graph["research_R164"] = {
    "start_head": "41ae6f6df1f7db8c0d0c799ab010638c5e6555b4",
    "parent_graph_sha256": ext["parent_sha256"],
    "note": str(NOTE.relative_to(ROOT)),
    "new_nodes": 4,
    "new_rules": 3,
    "status": "FROZEN_BOUNDED_MARTINGALE_COVERAGE_WITH_TARGET_DISCIPLINE",
    "actual_apparatus": False,
    "actual_participants": False,
    "ethics_approval": False,
    "empirical_F_witness": False,
    "global_semantic_proof": False,
}

assert graph["nodes"][:436] == old_nodes
assert graph["rules"][:209] == old_rules
assert graph["context_links"] == old_context
assert len(graph["nodes"]) == 440 and len(graph["rules"]) == 212
assert len({node["id"] for node in graph["nodes"]}) == 440
assert len({rule["id"] for rule in graph["rules"]}) == 212

node_ids = {node["id"] for node in graph["nodes"]}
for rule in graph["rules"]:
    assert rule["conclusion"] in node_ids
    assert set(rule["all_of"]) <= node_ids

adj = {node_id: [] for node_id in node_ids}
indeg = {node_id: 0 for node_id in node_ids}
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
assert seen == len(node_ids), "cycle detected"

GRAPH.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({
    "revision": graph["revision"],
    "nodes": len(graph["nodes"]),
    "rules": len(graph["rules"]),
    "context_links": len(graph["context_links"]),
    "parent_prefix_preserved": True,
    "dag": "PASS",
    "graph_sha256": sha256(GRAPH.read_bytes()).hexdigest(),
}, indent=2))
