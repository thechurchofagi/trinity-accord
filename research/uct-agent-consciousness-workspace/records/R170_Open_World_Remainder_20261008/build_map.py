#!/usr/bin/env python3
"""Apply the one-way R170 extension to the exact R169 graph."""

from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT = HERE / "MAP_EXTENSION.json"

raw = GRAPH.read_bytes()
ext = json.loads(EXT.read_text(encoding="utf-8"))
assert sha256(raw).hexdigest() == ext["parent_sha256"]
g = json.loads(raw)
assert g["revision"] == ext["parent_revision"]
assert (len(g["nodes"]), len(g["rules"]), len(g["context_links"])) == (477, 227, 129)
old_nodes = json.dumps(g["nodes"], ensure_ascii=False, sort_keys=True)
old_rules = json.dumps(g["rules"], ensure_ascii=False, sort_keys=True)
old_links = json.dumps(g["context_links"], ensure_ascii=False, sort_keys=True)
g["nodes"].extend(ext["nodes"])
g["rules"].extend(ext["rules"])
g["context_links"].extend(ext["context_links"])
g["revision"] = "R170-v1.0"
g["research_R170"] = {
    "start_head": "021ff63e99aa36b7c795323216628ec205060836",
    "checkpoint_head": "ed51f5d1eccf4f54fd517bb1056b04f4c189eec2",
    "parent_graph_sha256": ext["parent_sha256"],
    "note": "records/R170_Open_World_Remainder_20261008/Open_World_Remainder_Certificates_v0_1.md",
    "new_nodes": len(ext["nodes"]),
    "new_rules": len(ext["rules"]),
    "new_context_links": len(ext["context_links"]),
    "status": "SHARP_OPEN_WORLD_REMAINDER_AMPLITUDE_MEAN_MASS_BOUNDARY",
    "actual_target_domain_validated": False,
    "actual_cell_cover_validated": False,
    "target_measure_validated": False,
    "remainder_mass_validated": False,
    "complete_route_inventory_validated": False,
    "B_min_validated": False,
    "C1_derived": False,
    "basal_experience_gate_added": False,
}
assert (len(g["nodes"]), len(g["rules"]), len(g["context_links"])) == (487, 234, 133)
assert json.dumps(g["nodes"][:477], ensure_ascii=False, sort_keys=True) == old_nodes
assert json.dumps(g["rules"][:227], ensure_ascii=False, sort_keys=True) == old_rules
assert json.dumps(g["context_links"][:129], ensure_ascii=False, sort_keys=True) == old_links
node_ids = [n["id"] for n in g["nodes"]]
rule_ids = [r["id"] for r in g["rules"]]
assert len(node_ids) == len(set(node_ids))
assert len(rule_ids) == len(set(rule_ids))
nodes = set(node_ids)
for rule in g["rules"]:
    assert rule["conclusion"] in nodes and set(rule["all_of"]) <= nodes
for link in g["context_links"]:
    assert link["from"] in nodes and link["to"] in nodes
adj = {n: [] for n in nodes}
indeg = {n: 0 for n in nodes}
for rule in g["rules"]:
    for premise in rule["all_of"]:
        adj[premise].append(rule["conclusion"])
        indeg[rule["conclusion"]] += 1
queue = [n for n, degree in indeg.items() if degree == 0]
seen = 0
while queue:
    current = queue.pop()
    seen += 1
    for nxt in adj[current]:
        indeg[nxt] -= 1
        if indeg[nxt] == 0:
            queue.append(nxt)
assert seen == len(nodes)
GRAPH.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(
    json.dumps(
        {
            "revision": g["revision"],
            "nodes": len(g["nodes"]),
            "rules": len(g["rules"]),
            "context_links": len(g["context_links"]),
            "dag": "PASS",
            "graph_sha256": sha256(GRAPH.read_bytes()).hexdigest(),
        },
        indent=2,
    )
)
