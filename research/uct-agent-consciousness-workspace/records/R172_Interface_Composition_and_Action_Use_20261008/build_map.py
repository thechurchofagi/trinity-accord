#!/usr/bin/env python3
"""Apply the one-way R172 extension to the exact R171 graph."""

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
assert (len(g["nodes"]), len(g["rules"]), len(g["context_links"])) == (497, 240, 137)
old_nodes = json.dumps(g["nodes"], ensure_ascii=False, sort_keys=True)
old_rules = json.dumps(g["rules"], ensure_ascii=False, sort_keys=True)
old_links = json.dumps(g["context_links"], ensure_ascii=False, sort_keys=True)
g["nodes"].extend(ext["nodes"])
g["rules"].extend(ext["rules"])
g["context_links"].extend(ext["context_links"])
g["revision"] = "R172-v1.0"
g["research_R172"] = {
    "start_head": "47f0088b58e37a438be331458ddb8efa714c0751",
    "core_checkpoint_head": "b32685bef98812281ff9929f82fb98e76dcaa615",
    "parent_graph_sha256": ext["parent_sha256"],
    "note": "records/R172_Interface_Composition_and_Action_Use_20261008/Interface_Composition_and_Online_Action_Use_v0_1.md",
    "new_nodes": len(ext["nodes"]), "new_rules": len(ext["rules"]), "new_context_links": len(ext["context_links"]),
    "status": "INTERFACE_COMPOSITION_AND_ONLINE_ACTION_USE_BOUNDARY",
    "actual_biological_system_tested": False,
    "actual_AI_system_tested": False,
    "complete_organization_identified": False,
    "B_min_validated": False, "F_O_validated": False, "C1_derived": False,
    "basal_experience_gate_added": False, "unique_owner_selected": False,
    "current_assistant_consciousness_decided": False
}
assert (len(g["nodes"]), len(g["rules"]), len(g["context_links"])) == (506, 244, 141)
assert json.dumps(g["nodes"][:497], ensure_ascii=False, sort_keys=True) == old_nodes
assert json.dumps(g["rules"][:240], ensure_ascii=False, sort_keys=True) == old_rules
assert json.dumps(g["context_links"][:137], ensure_ascii=False, sort_keys=True) == old_links
node_ids = [n["id"] for n in g["nodes"]]
rule_ids = [r["id"] for r in g["rules"]]
assert len(node_ids) == len(set(node_ids)) and len(rule_ids) == len(set(rule_ids))
nodes = set(node_ids)
for rule in g["rules"]:
    assert rule["conclusion"] in nodes and set(rule["all_of"]) <= nodes
for link in g["context_links"]:
    assert link["from"] in nodes and link["to"] in nodes
adj = {n: [] for n in nodes}; indeg = {n: 0 for n in nodes}
for rule in g["rules"]:
    for premise in rule["all_of"]:
        adj[premise].append(rule["conclusion"]); indeg[rule["conclusion"]] += 1
queue = [n for n,d in indeg.items() if d == 0]; seen = 0
while queue:
    cur = queue.pop(); seen += 1
    for nxt in adj[cur]:
        indeg[nxt] -= 1
        if indeg[nxt] == 0: queue.append(nxt)
assert seen == len(nodes)
GRAPH.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"revision":g["revision"],"nodes":len(g["nodes"]),"rules":len(g["rules"]),"context_links":len(g["context_links"]),"dag":"PASS","graph_sha256":sha256(GRAPH.read_bytes()).hexdigest()},indent=2))
