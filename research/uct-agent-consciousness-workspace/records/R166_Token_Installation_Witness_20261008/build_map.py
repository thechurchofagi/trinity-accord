#!/usr/bin/env python3
"""Apply the R166 extension once to the exact R165 parent graph."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT = HERE / "MAP_EXTENSION.json"
NOTE = HERE / "Token_Installation_Witness_and_Mineness_Boundary_v0_1.md"

raw = GRAPH.read_bytes()
ext = json.loads(EXT.read_text(encoding="utf-8"))
assert sha256(raw).hexdigest() == ext["parent_sha256"], "wrong parent graph or extension already applied"
assert sha256(NOTE.read_bytes()).hexdigest() == ext["note_sha256"], "note changed after extension freeze"

graph = json.loads(raw)
assert graph["revision"] == ext["parent_revision"]
assert len(graph["nodes"]) == 446 and len(graph["rules"]) == 215

old_nodes = deepcopy(graph["nodes"])
old_rules = deepcopy(graph["rules"])
old_context = deepcopy(graph["context_links"])

graph["nodes"].extend(deepcopy(ext["nodes"]))
graph["rules"].extend(deepcopy(ext["rules"]))
graph["revision"] = "R166-v1.0"
graph["date"] = "2026-10-08"
graph["research_R166"] = {
    "start_head": "86c95474d99a9916c4302e6898e045ce141634d4",
    "checkpoint_head": "6b99b8fc738a997ab06df4c0a58f565a81688a05",
    "parent_graph_sha256": ext["parent_sha256"],
    "note": str(NOTE.relative_to(ROOT)),
    "new_nodes": len(ext["nodes"]),
    "new_rules": len(ext["rules"]),
    "status": "SAME_TOKEN_INSTALLATION_WITNESS_WITH_C1_AND_SEMANTIC_BOUNDARY",
    "actual_apparatus": False,
    "actual_participant_or_system_token": False,
    "installation_empirically_witnessed": False,
    "B_min_validated": False,
    "C1_derived": False,
    "basal_experience_gate_added": False
}

assert graph["nodes"][:446] == old_nodes
assert graph["rules"][:215] == old_rules
assert graph["context_links"] == old_context
assert len(graph["nodes"]) == 452 and len(graph["rules"]) == 217
assert len({node["id"] for node in graph["nodes"]}) == 452
assert len({rule["id"] for rule in graph["rules"]}) == 217

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
