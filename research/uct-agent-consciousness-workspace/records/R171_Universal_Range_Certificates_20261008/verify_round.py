#!/usr/bin/env python3
"""Structural, exact-result, scope and direction validation for R171."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
EXT = HERE / "MAP_EXTENSION.json"
NOTE = HERE / "Universal_Target_Range_Certificates_v0_1.md"
RESULTS = HERE / "EXACT_CHECKS.json"
OUT = HERE / "MAP_AUDIT.json"

def digest(p): return sha256(p.read_bytes()).hexdigest()
g=json.loads(GRAPH.read_text()); ext=json.loads(EXT.read_text()); results=json.loads(RESULTS.read_text()); checks=[]
def record(name,ok,detail): checks.append({"name":name,"status":"PASS" if ok else "FAIL","detail":detail})
record("note_hash_frozen",digest(NOTE)==ext["note_sha256"],digest(NOTE))
record("graph_revision",g["revision"]=="R171-v1.0",g["revision"])
record("graph_counts",(len(g["nodes"]),len(g["rules"]),len(g["context_links"]))==(497,240,137),{"nodes":len(g["nodes"]),"rules":len(g["rules"]),"context_links":len(g["context_links"])})
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
parent=deepcopy(g); parent["nodes"]=parent["nodes"][:487]; parent["rules"]=parent["rules"][:234]; parent["context_links"]=parent["context_links"][:133]; parent["revision"]="R170-v1.0"; parent.pop("research_R171")
parent_hash=sha256((json.dumps(parent,indent=2,ensure_ascii=False)+"\n").encode()).hexdigest()
record("exact_parent_reconstruction",parent_hash==ext["parent_sha256"],parent_hash)
rnodes=g["nodes"][487:]; rrules=g["rules"][234:]
fields=("statement","domain","scope","source","source_lineage","status","proof","counterexamples_and_limits","formal_contract_R171")
record("new_node_contract_fields",all(all(n.get(f) for f in fields) for n in rnodes),[n["id"] for n in rnodes])
record("new_rules_explicit_all_of",all(r.get("all_of") and r["formal_contract_R171"]["premise_connective"]=="AND" for r in rrules),{r["id"]:r["all_of"] for r in rrules})
expected={r["id"]:r["all_of"] for r in ext["rules"]}; actual={r["id"]:r["all_of"] for r in rrules}
record("joint_premises_exact",actual==expected,actual)
record("direct_requires_target_common_and_D1_D3",set(actual["r171_direct_range_closure"])=={"R170:TARGET_DOMAIN_ADMISSION_CONTRACT","R171:UNIVERSAL_RANGE_CERTIFICATE_CONTRACT","R171:DIRECT_TOTAL_RANGE_CERTIFICATE"},actual["r171_direct_range_closure"])
record("inductive_requires_target_common_and_I1_I5",set(actual["r171_inductive_range_closure"])=={"R170:TARGET_DOMAIN_ADMISSION_CONTRACT","R171:UNIVERSAL_RANGE_CERTIFICATE_CONTRACT","R171:INDUCTIVE_REACHABLE_RANGE_CERTIFICATE"},actual["r171_inductive_range_closure"])
record("fitted_nonentailment_keeps_challenge_boundary",set(actual["r171_fitted_cover_nonentailment"])=={"R170:COVERAGE_CHALLENGE_FALSIFIER","R171:PREMISE_INDEPENDENCE_COUNTERMODELS"},actual["r171_fitted_cover_nonentailment"])
record("application_keeps_both_routes_and_fit_limit",set(actual["r171_four_domain_application"])=={"R171:DIRECT_RANGE_CLOSURE","R171:INDUCTIVE_RANGE_CLOSURE","R171:FITTED_COVER_NONENTAILMENT"},actual["r171_four_domain_application"])
record("final_application_keeps_R170_and_scope",set(actual["r171_range_application_boundary"])=={"R170:R169_OPEN_WORLD_APPLICATION_BOUNDARY","R171:DIRECT_RANGE_CLOSURE","R171:INDUCTIVE_RANGE_CLOSURE","R171:FOUR_DOMAIN_APPLICATION_BOUNDARY","R171:RANGE_CERTIFICATE_TRIAGE"},actual["r171_range_application_boundary"])
forbidden={"A:C1","A:U1","F153-11","F153-17","R166:EXPERIENTIAL_COUNTERPART_BOUNDARY"}
record("no_reverse_to_C1_basal_or_mineness",not any(r["conclusion"] in forbidden for r in rrules),[r["conclusion"] for r in rrules])
markers=("context only","non-deductive","obstruction retained","no type")
record("context_links_non_deductive",all(any(m in x["relation"].lower() for m in markers) for x in ext["context_links"]),ext["context_links"])
record("exact_range_enumeration",results["direct_inclusion_checks"]==21844 and results["proper_sample_nondetermination_witnesses"]==3025 and results["inductive_certificates"]==1838 and results["inductive_reachability_state_checks"]==2530,{k:results[k] for k in ("direct_inclusion_checks","proper_sample_nondetermination_witnesses","inductive_certificates","inductive_reachability_state_checks")})
pw=results["premise_independence_witnesses"]
record("four_premises_independently_required",len(pw)==4 and all(not v["conclusion"] and sum(v[k] for k in ("initial","closure","refinement","fiber"))==3 for v in pw.values()),pw)
record("status_priority",results["status_assignments"]==64 and sum(results["status_counts"].values())==64 and set(results["status_counts"])=={"INVALID_RANGE_PROTOCOL","RANGE_CERTIFICATE_REFUTED","UNIVERSAL_RANGE_CERTIFIED_DIRECT","UNIVERSAL_RANGE_CERTIFIED_REACHABLE","SPECIFICATION_ONLY","EMPIRICAL_COVER_ONLY","UNRESOLVED"},results["status_counts"])
record("four_domain_families_audited",set(results["domain_family_audit"])=={"finite_hardware","typed_program","sensorimotor","biological_safety"},results["domain_family_audit"])
record("claim_limits",all(v is False for v in results["claim_limits"].values()),results["claim_limits"])
required=["ROUND_RECORD.md","Universal_Target_Range_Certificates_v0_1.md","PROOF_LEDGER.json","GAP_LEDGER.json","SOURCE_LEDGER.json","MAP_EXTENSION.json","verify_range_certificates.py","EXACT_CHECKS.json","build_map.py"]
record("required_core_artifacts_present",all((HERE/n).exists() for n in required),required)
payload={"schema":"UCT_R171_MAP_AUDIT/v1","round":"R171","status":"PASS" if all(c["status"]=="PASS" for c in checks) else "FAIL","checks":checks,"graph_sha256":digest(GRAPH),"exact_results_sha256":digest(RESULTS),"limitations":["DAG and finite checks do not instantiate an actual hardware, program, sensorimotor or biological certificate.","Direct and inductive closure are target-relative and do not establish complete mechanism or compositional closure.","No neural completeness, C1 derivation, B_min validation, basal-experience gate or unique owner follows."]}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"status":payload["status"],"checks":len(checks),"graph_sha256":payload["graph_sha256"],"exact_results_sha256":payload["exact_results_sha256"]},indent=2))
if payload["status"]!="PASS": raise SystemExit(1)
