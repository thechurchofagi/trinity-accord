#!/usr/bin/env python3
"""Apply the R168 extension once to the exact R167 graph."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT = HERE / "MAP_EXTENSION.json"
NOTE = HERE / "Stochastic_Continuous_and_Partially_Observed_Redundancy_v0_1.md"

raw = GRAPH.read_bytes(); ext = json.loads(EXT.read_text(encoding="utf-8"))
assert sha256(raw).hexdigest() == ext["parent_sha256"]
assert sha256(NOTE.read_bytes()).hexdigest() == ext["note_sha256"]
graph = json.loads(raw); assert graph["revision"] == ext["parent_revision"]
old_nodes = deepcopy(graph["nodes"]); old_rules = deepcopy(graph["rules"]); old_context = deepcopy(graph["context_links"])
graph["nodes"].extend(deepcopy(ext["nodes"])); graph["rules"].extend(deepcopy(ext["rules"])); graph["context_links"].extend(deepcopy(ext["context_links"]))
graph["revision"] = "R168-v1.0"; graph["date"] = "2026-10-08"
graph["research_R168"] = {
    "start_head": "fe2a967749c9412b1a957cbfa63ad6beff2ad9df",
    "checkpoint_head": "5b76923f2cc78bd26682dbad5c72adfd40dfde50",
    "parent_graph_sha256": ext["parent_sha256"],
    "note": str(NOTE.relative_to(ROOT)),
    "new_nodes": len(ext["nodes"]), "new_rules": len(ext["rules"]), "new_context_links": len(ext["context_links"]),
    "status": "SHARP_STOCHASTIC_CONTINUOUS_REDUNDANCY_ENVELOPE_WITH_PARTIAL_VIEW_BOUNDARY",
    "actual_apparatus": False, "actual_participant_or_system_token": False, "physical_metric_validated": False,
    "lipschitz_constant_validated": False, "partial_view_lift_validated": False, "sampling_measure_validated": False,
    "B_min_validated": False, "C1_derived": False, "basal_experience_gate_added": False
}
assert graph["nodes"][:459] == old_nodes and graph["rules"][:219] == old_rules and graph["context_links"][:121] == old_context
assert (len(graph["nodes"]),len(graph["rules"]),len(graph["context_links"])) == (468,222,125)
node_ids = {n["id"] for n in graph["nodes"]}
assert len(node_ids) == len(graph["nodes"]) and len({r["id"] for r in graph["rules"]}) == len(graph["rules"])
for rule in graph["rules"]:
    assert rule["conclusion"] in node_ids and set(rule["all_of"]) <= node_ids
for link in graph["context_links"]: assert link["from"] in node_ids and link["to"] in node_ids
adj={n:[] for n in node_ids}; indeg={n:0 for n in node_ids}
for rule in graph["rules"]:
    for premise in rule["all_of"]: adj[premise].append(rule["conclusion"]); indeg[rule["conclusion"]]+=1
queue=[n for n,d in indeg.items() if d==0]; seen=0
while queue:
    cur=queue.pop(); seen+=1
    for nxt in adj[cur]:
        indeg[nxt]-=1
        if indeg[nxt]==0: queue.append(nxt)
assert seen == len(node_ids)
GRAPH.write_text(json.dumps(graph,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"revision":graph["revision"],"nodes":len(graph["nodes"]),"rules":len(graph["rules"]),"context_links":len(graph["context_links"]),"dag":"PASS","graph_sha256":sha256(GRAPH.read_bytes()).hexdigest()},indent=2))
