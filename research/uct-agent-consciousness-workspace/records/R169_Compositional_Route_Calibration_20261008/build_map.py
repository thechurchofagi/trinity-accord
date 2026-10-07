#!/usr/bin/env python3
"""Apply the one-way R169 extension to the exact R168 graph."""

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
assert (len(g["nodes"]), len(g["rules"]), len(g["context_links"])) == (468,222,125)
old_nodes = json.dumps(g["nodes"], ensure_ascii=False, sort_keys=True)
old_rules = json.dumps(g["rules"], ensure_ascii=False, sort_keys=True)
old_links = json.dumps(g["context_links"], ensure_ascii=False, sort_keys=True)
g["nodes"].extend(ext["nodes"]); g["rules"].extend(ext["rules"]); g["context_links"].extend(ext["context_links"])
g["revision"] = "R169-v1.0"
g["research_R169"] = {
  "start_head": "b2fde21589a733fe108cc41b8548f5a6fa9cbae0",
  "checkpoint_head": "516155484c1bbcb7f3479076e8c48be334e22f74",
  "parent_graph_sha256": ext["parent_sha256"],
  "note": "records/R169_Compositional_Route_Calibration_20261008/Compositional_Route_Calibration_and_Falsification_v0_1.md",
  "new_nodes": len(ext["nodes"]), "new_rules": len(ext["rules"]), "new_context_links": len(ext["context_links"]),
  "status": "COMPOSITIONAL_ACTUAL_ROUTE_CALIBRATION_AND_FALSIFICATION_BOUNDARY",
  "actual_route_graph_validated": False, "actual_edge_interventions_validated": False,
  "continuum_coverage_validated": False, "complete_route_inventory_validated": False,
  "B_min_validated": False, "C1_derived": False, "basal_experience_gate_added": False
}
assert (len(g["nodes"]), len(g["rules"]), len(g["context_links"])) == (477,227,129)
assert json.dumps(g["nodes"][:468], ensure_ascii=False, sort_keys=True) == old_nodes
assert json.dumps(g["rules"][:222], ensure_ascii=False, sort_keys=True) == old_rules
assert json.dumps(g["context_links"][:125], ensure_ascii=False, sort_keys=True) == old_links
node_ids = [n["id"] for n in g["nodes"]]; rule_ids = [r["id"] for r in g["rules"]]
assert len(node_ids) == len(set(node_ids)); assert len(rule_ids) == len(set(rule_ids))
nodes = set(node_ids)
for r in g["rules"]: assert r["conclusion"] in nodes and set(r["all_of"]) <= nodes
for l in g["context_links"]: assert l["from"] in nodes and l["to"] in nodes
adj = {n: [] for n in nodes}; indeg = {n: 0 for n in nodes}
for r in g["rules"]:
    for p in r["all_of"]: adj[p].append(r["conclusion"]); indeg[r["conclusion"]] += 1
q = [n for n,d in indeg.items() if d == 0]; seen = 0
while q:
    cur=q.pop(); seen+=1
    for nxt in adj[cur]:
        indeg[nxt]-=1
        if indeg[nxt]==0:q.append(nxt)
assert seen == len(nodes)
GRAPH.write_text(json.dumps(g, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print(json.dumps({"revision":g["revision"],"nodes":len(g["nodes"]),"rules":len(g["rules"]),"context_links":len(g["context_links"]),"dag":"PASS","graph_sha256":sha256(GRAPH.read_bytes()).hexdigest()},indent=2))
