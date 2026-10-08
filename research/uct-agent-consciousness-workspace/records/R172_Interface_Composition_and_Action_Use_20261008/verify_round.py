#!/usr/bin/env python3
"""Structural, exact-result, scope and direction validation for R172."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT = HERE / "MAP_EXTENSION.json"
NOTE = HERE / "Interface_Composition_and_Online_Action_Use_v0_1.md"
RESULTS = HERE / "EXACT_CHECKS.json"
OUT = HERE / "MAP_AUDIT.json"

def digest(p): return sha256(p.read_bytes()).hexdigest()
g=json.loads(GRAPH.read_text()); ext=json.loads(EXT.read_text()); results=json.loads(RESULTS.read_text()); checks=[]
def record(name,ok,detail): checks.append({"name":name,"status":"PASS" if ok else "FAIL","detail":detail})
record("note_hash_frozen",digest(NOTE)==ext["note_sha256"],digest(NOTE))
record("exact_checks_hash_bound",digest(RESULTS)=="b61ad9b03317ea84bf0f369934b1915aada129f7c9abe39f12249f5bac3717b8",digest(RESULTS))
record("graph_revision",g["revision"]=="R172-v1.0",g["revision"])
record("graph_counts",(len(g["nodes"]),len(g["rules"]),len(g["context_links"]))==(506,244,141),{"nodes":len(g["nodes"]),"rules":len(g["rules"]),"context_links":len(g["context_links"])})
node_ids=[n["id"] for n in g["nodes"]]; rule_ids=[r["id"] for r in g["rules"]]; nodes=set(node_ids)
record("unique_ids",len(node_ids)==len(nodes) and len(rule_ids)==len(set(rule_ids)),{"nodes":len(nodes),"rules":len(set(rule_ids))})
bad_rules=[r["id"] for r in g["rules"] if r["conclusion"] not in nodes or not set(r["all_of"])<=nodes]
bad_links=[x for x in g["context_links"] if x["from"] not in nodes or x["to"] not in nodes]
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
parent=deepcopy(g); parent["nodes"]=parent["nodes"][:497]; parent["rules"]=parent["rules"][:240]; parent["context_links"]=parent["context_links"][:137]; parent["revision"]="R171-v1.0"; parent.pop("research_R172")
parent_hash=sha256((json.dumps(parent,indent=2,ensure_ascii=False)+"\n").encode()).hexdigest()
record("exact_parent_reconstruction",parent_hash==ext["parent_sha256"],parent_hash)
rnodes=g["nodes"][497:]; rrules=g["rules"][240:]
fields=("statement","domain","scope","source","source_lineage","status","proof","counterexamples_and_limits","formal_contract_R172")
record("new_node_contract_fields",all(all(n.get(f) for f in fields) for n in rnodes),[n["id"] for n in rnodes])
record("node_quantifier_object_time_signature_actuality",all(all(k in n["formal_contract_R172"] for k in ("quantifiers","object_domain","bearer_time_signature","source_anchor","open_obligations","purpose")) for n in rnodes),[n["id"] for n in rnodes])
record("new_rules_explicit_all_of",all(r.get("all_of") and r["formal_contract_R172"]["premise_connective"]=="AND" for r in rrules),{r["id"]:r["all_of"] for r in rrules})
expected={r["id"]:r["all_of"] for r in ext["rules"]}; actual={r["id"]:r["all_of"] for r in rrules}
record("joint_premises_exact",actual==expected,actual)
record("composition_requires_local_and_interface",set(actual["r172_interface_composition"])=={"R172:LOCAL_COMPONENT_CERTIFICATE_INSTANCE","R172:INTERFACE_COMPATIBILITY_CONTRACT"},actual["r172_interface_composition"])
record("online_use_requires_install_composition_and_live_relation",set(actual["r172_witnessed_online_action_use"])=={"R166:WITNESSED_FRAME_INSTALLATION","R172:INTERFACE_COMPOSITION_THEOREM","R172:ONLINE_ACTION_USE_RELATION"},actual["r172_witnessed_online_action_use"])
record("experience_coordinate_keeps_transport_semantic_and_live_premises",set(actual["r172_experience_internal_action_coordinate"])=={"R157:COORDINATE_TRANSPORT","R157:SEMANTIC_RESIDUAL","R159:FRAME_RELATION_TRANSPORT","R172:WITNESSED_ONLINE_ACTION_USE"},actual["r172_experience_internal_action_coordinate"])
record("application_keeps_nonidentification_and_coordinate",set(actual["r172_bio_ai_application_boundary"])=={"R172:LIVE_REPLAY_NONENTAILMENT","R172:EXPERIENCE_INTERNAL_ACTION_COORDINATE"},actual["r172_bio_ai_application_boundary"])
forbidden={"A:C1","A:U1","F153-11","F153-17","R166:EXPERIENTIAL_COUNTERPART_BOUNDARY"}
record("no_reverse_to_C1_basal_or_mineness",not any(r["conclusion"] in forbidden for r in rrules),[r["conclusion"] for r in rrules])
markers=("context only","non-deductive","no interface")
record("context_links_non_deductive",all(any(m in x["relation"].lower() for m in markers) for x in ext["context_links"]),ext["context_links"])
status={c["name"]:c["status"] for c in results["checks"]}
record("all_exact_checks_pass",len(status)==9 and all(v=="PASS" for v in status.values()),status)
record("bounded_composition_512",results["counts"]["bounded_composition_cases"]==512,results["counts"])
record("live_replay_two_cases",results["counts"]["live_replay_cases"]==2,results["counts"])
record("online_use_all_six_conjuncts",results["counts"]["online_use_gate_assignments"]==64 and next(c for c in results["checks"] if c["name"]=="online_use_all_of_gate")["detail"]["supported"]==1,results["counts"])
record("claim_limits",all(v is False for v in results["claim_limits"].values()),results["claim_limits"])
required=["ROUND_RECORD.md","Interface_Composition_and_Online_Action_Use_v0_1.md","PROOF_LEDGER.json","GAP_LEDGER.json","SOURCE_LEDGER.json","MAP_EXTENSION.json","verify_interface_action.py","EXACT_CHECKS.json","build_map.py"]
record("required_core_artifacts_present",all((HERE/n).exists() for n in required),required)
payload={"schema":"UCT_R172_MAP_AUDIT/v1","round":"R172","status":"PASS" if all(c["status"]=="PASS" for c in checks) else "FAIL","checks":checks,"graph_sha256":digest(GRAPH),"exact_results_sha256":digest(RESULTS),"limitations":["DAG and finite checks do not establish theoretical truth, C1, physical instantiation or complete organization.","The composition theorem is sufficient only under the declared synchronous interface contract; asynchronous, stochastic, hybrid and overlapping cases remain open.","Online action use is intervention-family and closure relative; familiar bodily mineness still needs independent B_min/F_O/F_A.","No basal-experience gate, unique owner or current-assistant consciousness status follows."]}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"status":payload["status"],"checks":len(checks),"graph_sha256":payload["graph_sha256"],"exact_results_sha256":payload["exact_results_sha256"]},indent=2))
if payload["status"]!="PASS": raise SystemExit(1)
