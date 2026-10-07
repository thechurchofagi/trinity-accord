#!/usr/bin/env python3
"""Structural, exact-result, scope, and direction validation for R169."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
GRAPH=ROOT/"UCT_FORMAL_GRAPH.json"; EXT=HERE/"MAP_EXTENSION.json"
NOTE=HERE/"Compositional_Route_Calibration_and_Falsification_v0_1.md"
RESULTS=HERE/"EXACT_CHECKS.json"; OUT=HERE/"MAP_AUDIT.json"
def digest(p): return sha256(p.read_bytes()).hexdigest()
g=json.loads(GRAPH.read_text()); ext=json.loads(EXT.read_text()); results=json.loads(RESULTS.read_text())
checks=[]
def record(name,ok,detail): checks.append({"name":name,"status":"PASS" if ok else "FAIL","detail":detail})
record("note_hash_frozen",digest(NOTE)==ext["note_sha256"],digest(NOTE))
record("graph_revision",g["revision"]=="R169-v1.0",g["revision"])
record("graph_counts",(len(g["nodes"]),len(g["rules"]),len(g["context_links"]))==(477,227,129),{"nodes":len(g["nodes"]),"rules":len(g["rules"]),"context_links":len(g["context_links"])})
node_ids=[n["id"] for n in g["nodes"]]; rule_ids=[r["id"] for r in g["rules"]]; nodes=set(node_ids)
record("unique_ids",len(node_ids)==len(nodes) and len(rule_ids)==len(set(rule_ids)),{"nodes":len(nodes),"rules":len(set(rule_ids))})
bad_rules=[r["id"] for r in g["rules"] if r["conclusion"] not in nodes or not set(r["all_of"])<=nodes]
bad_links=[l for l in g["context_links"] if l["from"] not in nodes or l["to"] not in nodes]
record("all_endpoints_exist",not bad_rules and not bad_links,{"rules":bad_rules,"links":bad_links})
adj={n:[] for n in nodes}; indeg={n:0 for n in nodes}
for r in g["rules"]:
    for p in r["all_of"]: adj[p].append(r["conclusion"]); indeg[r["conclusion"]]+=1
q=[n for n,d in indeg.items() if d==0]; seen=0
while q:
    cur=q.pop(); seen+=1
    for nxt in adj[cur]:
        indeg[nxt]-=1
        if indeg[nxt]==0:q.append(nxt)
record("dag",seen==len(nodes),{"visited":seen,"total":len(nodes)})
parent=deepcopy(g); parent["nodes"]=parent["nodes"][:468]; parent["rules"]=parent["rules"][:222]; parent["context_links"]=parent["context_links"][:125]; parent["revision"]="R168-v1.0"; parent.pop("research_R169")
parent_hash=sha256((json.dumps(parent,indent=2,ensure_ascii=False)+"\n").encode()).hexdigest()
record("exact_parent_reconstruction",parent_hash==ext["parent_sha256"],parent_hash)
rnodes=g["nodes"][468:]; rrules=g["rules"][222:]
fields=("statement","domain","scope","source","source_lineage","status","proof","counterexamples_and_limits","formal_contract_R169")
record("new_node_contract_fields",all(all(n.get(f) for f in fields) for n in rnodes),[n["id"] for n in rnodes])
record("new_rules_explicit_all_of",all(r.get("all_of") and r["formal_contract_R169"]["premise_connective"]=="AND" for r in rrules),{r["id"]:r["all_of"] for r in rrules})
expected={r["id"]:r["all_of"] for r in ext["rules"]}; actual={r["id"]:r["all_of"] for r in rrules}
record("joint_premises_exact",actual==expected,actual)
record("route_bound_requires_actual_graph_and_local_cert",set(actual["r169_compositional_effect_bound"])=={"R168:STOCHASTIC_CONTEXTUAL_EFFECT","R169:ACTUAL_ROUTE_GRAPH_CONTRACT","R169:LOCAL_CHANNEL_UPPER_CERTIFICATE"},actual["r169_compositional_effect_bound"])
record("partial_view_obstruction_retained","R168:PARTIAL_VIEW_NONENTAILMENT" in actual["r169_partial_view_direct_radius"],actual["r169_partial_view_direct_radius"])
record("application_keeps_R166_R168_package",set(actual["r169_route_application_boundary"])=={"R166:TOKEN_INSTALLATION_WITNESS_CONTRACT","R167:OPERATIONAL_MEDIATOR_ARCHITECTURE","R168:R167_WITNESS_STOCHASTIC_BOUNDARY","R169:ROUTE_CALIBRATION_TRIAGE"},actual["r169_route_application_boundary"])
forbidden={"A:C1","A:U1","F153-11","F153-17","R166:EXPERIENTIAL_COUNTERPART_BOUNDARY"}
record("no_reverse_to_C1_basal_gate_or_familiar_mineness",not any(r["conclusion"] in forbidden for r in rrules),[r["conclusion"] for r in rrules])
markers=("context only","non-deductive","obstruction retained","no route validity")
record("context_links_non_deductive",all(any(m in l["relation"].lower() for m in markers) for l in ext["context_links"]),ext["context_links"])
fr=results["finite_route_theorem"]
record("finite_route_enumeration",fr["connected_graphs"]==43 and fr["bernoulli_law_assignments"]==252315 and fr["effect_pair_checks"]==4015656 and fr["route_envelope_checks"]==4050810 and fr["intervention_specific_checks"]==4015656,fr)
record("metric_gauge",results["metric_scale_gauge"]["exact_rational_cases"]==512,results["metric_scale_gauge"])
record("status_priority",results["status_priority"]["boolean_assignments"]==32 and sum(results["status_priority"]["counts"].values())==32,results["status_priority"])
record("claim_limits",all(v is False for v in results["claim_limits"].values()),results["claim_limits"])
required=["ROUND_RECORD.md","Compositional_Route_Calibration_and_Falsification_v0_1.md","PROOF_LEDGER.json","GAP_LEDGER.json","SOURCE_LEDGER.json","MAP_EXTENSION.json","verify_route_bounds.py","EXACT_CHECKS.json","build_map.py"]
record("required_core_artifacts_present",all((HERE/f).exists() for f in required),required)
payload={"schema":"UCT_R169_MAP_AUDIT/v1","round":"R169","status":"PASS" if all(c["status"]=="PASS" for c in checks) else "FAIL","checks":checks,"graph_sha256":digest(GRAPH),"exact_results_sha256":digest(RESULTS),"limitations":["DAG and finite exhaustive checks do not establish physical route validity, graph completeness or theory truth.","Every actual node, executable edge, upper budget, challenge lower bound and continuum-cell claim remains an application obligation.","No neural completeness, C1 derivation, B_min validation, basal-experience gate or unique owner follows."]}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"status":payload["status"],"checks":len(checks),"graph_sha256":payload["graph_sha256"],"exact_results_sha256":payload["exact_results_sha256"]},indent=2))
if payload["status"]!="PASS": raise SystemExit(1)
