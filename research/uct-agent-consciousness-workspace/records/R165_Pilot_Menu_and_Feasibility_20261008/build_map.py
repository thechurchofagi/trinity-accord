#!/usr/bin/env python3
"""Apply the R165 extension once to the exact R164 parent graph."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT = HERE / "MAP_EXTENSION.json"
NOTE = HERE / "Pilot_Menu_Width_Certification_and_Feasibility_v0_1.md"

raw = GRAPH.read_bytes()
ext = json.loads(EXT.read_text(encoding="utf-8"))
assert sha256(raw).hexdigest() == ext["parent_sha256"], "wrong parent graph or extension already applied"
assert sha256(NOTE.read_bytes()).hexdigest() == ext["note_sha256"], "note changed after extension freeze"

graph = json.loads(raw)
assert graph["revision"] == ext["parent_revision"]
assert len(graph["nodes"]) == 440 and len(graph["rules"]) == 212

old_nodes = deepcopy(graph["nodes"])
old_rules = deepcopy(graph["rules"])
old_context = deepcopy(graph["context_links"])

graph["nodes"].extend(deepcopy(ext["nodes"]))
graph["rules"].extend(deepcopy(ext["rules"]))
graph["revision"] = "R165-v1.0"
graph["date"] = "2026-10-08"
graph["research_R165"] = {
    "start_head": "d279782dd4df05ef913a2413eacb5bd116b327fa",
    "parent_graph_sha256": ext["parent_sha256"],
    "note": str(NOTE.relative_to(ROOT)),
    "new_nodes": len(ext["nodes"]),
    "new_rules": len(ext["rules"]),
    "status": "FINITE_PILOT_MENU_WIDTH_CERTIFICATION_WITH_HONEST_TRIAGE",
    "actual_apparatus": False,
    "actual_pilot": False,
    "actual_participants": False,
    "transport_validated": False,
    "ethics_approval": False,
    "empirical_F_witness": False,
    "global_semantic_proof": False
}

assert graph["nodes"][:440] == old_nodes
assert graph["rules"][:212] == old_rules
assert graph["context_links"] == old_context
assert len(graph["nodes"]) == 446 and len(graph["rules"]) == 215
assert len({node["id"] for node in graph["nodes"]}) == 446
assert len({rule["id"] for rule in graph["rules"]}) == 215

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
    "graph_sha256": sha256(GRAPH.read_bytes()).hexdigest()
}, indent=2))
