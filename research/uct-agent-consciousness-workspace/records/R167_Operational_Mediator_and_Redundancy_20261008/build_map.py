#!/usr/bin/env python3
"""Apply the R167 extension once to the exact R166 graph."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT = HERE / "MAP_EXTENSION.json"
NOTE = HERE / "Operational_Mediator_Redundancy_and_Compensation_v0_1.md"

raw = GRAPH.read_bytes()
ext = json.loads(EXT.read_text(encoding="utf-8"))
assert sha256(raw).hexdigest() == ext["parent_sha256"]
assert sha256(NOTE.read_bytes()).hexdigest() == ext["note_sha256"]
graph = json.loads(raw)
assert graph["revision"] == ext["parent_revision"]
old_nodes = deepcopy(graph["nodes"])
old_rules = deepcopy(graph["rules"])
old_context = deepcopy(graph["context_links"])
graph["nodes"].extend(deepcopy(ext["nodes"]))
graph["rules"].extend(deepcopy(ext["rules"]))
graph["context_links"].extend(deepcopy(ext["context_links"]))
graph["revision"] = "R167-v1.0"
graph["date"] = "2026-10-08"
graph["research_R167"] = {
    "start_head": "8822679cca73ebb915f037e148cb19ded203aafd",
    "checkpoint_head": "11924feb613cdc54b999328fbb2d3813de3ecc38",
    "parent_graph_sha256": ext["parent_sha256"],
    "note": str(NOTE.relative_to(ROOT)),
    "new_nodes": len(ext["nodes"]),
    "new_rules": len(ext["rules"]),
    "new_context_links": len(ext["context_links"]),
    "status": "OPERATIONAL_MEDIATOR_WITH_REDUNDANCY_AND_COMPENSATION_BOUNDARY",
    "actual_apparatus": False,
    "actual_participant_or_system_token": False,
    "ethics_approval": False,
    "neural_mediator_identified": False,
    "route_closure_empirically_verified": False,
    "B_min_validated": False,
    "C1_derived": False,
    "basal_experience_gate_added": False
}
assert graph["nodes"][:452] == old_nodes
assert graph["rules"][:217] == old_rules
assert graph["context_links"][:117] == old_context
assert len(graph["nodes"]) == 459
assert len(graph["rules"]) == 219
assert len(graph["context_links"]) == 121
node_ids = {n["id"] for n in graph["nodes"]}
assert len(node_ids) == len(graph["nodes"])
assert len({r["id"] for r in graph["rules"]}) == len(graph["rules"])
for rule in graph["rules"]:
    assert rule["conclusion"] in node_ids
    assert set(rule["all_of"]) <= node_ids
for link in graph["context_links"]:
    assert link["from"] in node_ids and link["to"] in node_ids
adj = {n: [] for n in node_ids}
indeg = {n: 0 for n in node_ids}
for rule in graph["rules"]:
    for premise in rule["all_of"]:
        adj[premise].append(rule["conclusion"])
        indeg[rule["conclusion"]] += 1
queue = [n for n, d in indeg.items() if d == 0]
seen = 0
while queue:
    cur = queue.pop()
    seen += 1
    for nxt in adj[cur]:
        indeg[nxt] -= 1
        if indeg[nxt] == 0:
            queue.append(nxt)
assert seen == len(node_ids)
GRAPH.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"revision": graph["revision"], "nodes": len(graph["nodes"]), "rules": len(graph["rules"]), "context_links": len(graph["context_links"]), "dag": "PASS", "graph_sha256": sha256(GRAPH.read_bytes()).hexdigest()}, indent=2))
