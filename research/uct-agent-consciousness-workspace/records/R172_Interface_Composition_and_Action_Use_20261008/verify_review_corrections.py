#!/usr/bin/env python3
"""Focused QC06/QC07 regressions; not theory or physical validation."""
from pathlib import Path
from hashlib import sha256
from itertools import product, permutations
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
a=json.loads((HERE/"REVIEW_AMENDMENTS.json").read_text())
checks=[]
def check(name,ok,detail):
    checks.append(dict(name=name,status="PASS" if ok else "FAIL",detail=detail))
rules={r["id"]:r for r in a["effective_rules"]}
r=rules["r172_witnessed_online_action_use_effective"]
fields=a["binding_fields"]
t=dict(zip(fields,["P0","I0","K0","D0","rho0","gamma0","sig0","sync0"]))
def accepts(rule,facts,bindings):
    return all(facts.get(p) is True for p in rule["all_of"]) and bool(bindings) and all(b==bindings[0] and set(b)==set(fields) for b in bindings)
# Countervaluations are logical worlds, not missing-evidence assignments.
for name,L,C,J,F,U in [
    ("schema_does_not_supply_C",False,False,False,True,True),
    ("invariant_does_not_supply_C",True,False,True,True,True)]:
    theorem=not(L and C) or J
    old=F and U and (theorem if name.startswith("schema") else J)
    check(name,old and not(F and C and U),dict(L=L,C=C,J=J,F=F,U=U,theorem=theorem))
positive={p:True for p in r["all_of"]}
check("positive_same_instance_accepted",accepts(r,positive,[t]*5),r["all_of"])
accepted=0
for bits in product([False,True],repeat=len(r["all_of"])):
    facts=dict(zip(r["all_of"],bits)); got=accepts(r,facts,[t]*5)
    assert got==all(bits); accepted+=got
check("all_64_joint_premise_assignments",accepted==1,{"accepted":accepted,"total":64})
wrong=[]
for f in fields:
    other=dict(t);other[f]+="_other"
    if accepts(r,positive,[t,other]):wrong.append(f)
check("all_binding_mismatches_rejected",not wrong,{"tested":fields,"failures":wrong})
tr=rules["r172_experience_internal_action_coordinate_effective"]
tc=0
for bits in product([False,True],repeat=len(tr["all_of"])):
    facts=dict(zip(tr["all_of"],bits));got=accepts(tr,facts,[t,t])
    assert got==all(bits);tc+=got
check("transport_requires_every_grounding_parameter_premise",tc==1,{"accepted":tc,"total":64})
# A fixed baseline executed path; accessible tests do not alter this path.
ontic_live=True
def status(outputs,valid=True):
    if not valid:return "INVALID"
    return "SUPPORTED" if len(set(outputs))>1 else "UNRESOLVED"
check("same_live_mechanism_different_test_sets",
      status([0])=="UNRESOLVED" and status([0,1])=="SUPPORTED" and ontic_live,
      {"W0":[0],"W01":[0,1],"ontic_path_in_both":True})
check("no_response_is_not_absent_use",status([0,0])=="UNRESOLVED",
      {"redundancy_or_insensitive_window":"UNRESOLVED"})
check("invalid_test_does_not_support_use",status([0,1],False)=="INVALID","fidelity gate")
facts=dict(positive);facts["role_bridge"]=False
check("intervention_installed_path_blocked",not accepts(r,facts,[t]*5),
      "An action response without a same-baseline-mechanism bridge cannot certify the baseline path.")
# Toy actual path evaluation independent of reports/tests.
def phi(rel,b,k,a,g):
    return b in rel["anchor"] and (b,k) in rel["bind"] and any(
        kk==k and gg==g and (q,a,e2) in rel["operand"] and (e1,e2) in rel["order"]
        for kk,q,gg,e1 in rel["transfer"] for e2 in range(8))
live={"anchor":{0},"bind":{(0,1)},"transfer":{(1,2,3,4)},"operand":{(2,5,6)},"order":{(4,6)}}
replay={**live,"operand":{(7,5,6)}}
check("selected_live_replay_path_distinction",phi(live,0,1,5,3) and not phi(replay,0,1,5,3),"same output value is allowed")
# Explicit isomorphism permutation; transport all physical parameters.
perm={i:i for i in range(8)};perm[3]=7;perm[7]=3
mapped={
 "anchor":{perm[x] for x in live["anchor"]},
 **{k:{tuple(perm[x] for x in row) for row in live[k]} for k in ["bind","transfer","operand","order"]}
}
check("parameter_transport_required",phi(mapped,perm[0],perm[1],perm[5],perm[3]) and not phi(mapped,perm[0],perm[1],perm[5],3),
      {"h_gamma":7,"untransported_gamma":3})
all_ok=True
for ps in permutations(range(4)):
    h={i:(ps[i] if i<4 else i) for i in range(8)}
    rel={"anchor":{h[x] for x in live["anchor"]},**{k:{tuple(h[x] for x in row) for row in live[k]} for k in ["bind","transfer","operand","order"]}}
    all_ok &= phi(rel,h[0],h[1],h[5],h[3])
check("24_parameter_renamings",all_ok,24)
check("external_W_E_excluded",a["actual_selector"]["parameters"]==["gamma"] and a["actual_selector"]["excluded_analyst_parameters"]==["W","E","certificate_status"],a["actual_selector"])
graw=(ROOT/"UCT_FORMAL_GRAPH.json").read_bytes()
g=json.loads(graw)
check("frozen_raw_graph_unchanged",sha256(graw).hexdigest()==a["provenance"]["graph_sha256"],sha256(graw).hexdigest())
check("frozen_note_unchanged",sha256((HERE/"Interface_Composition_and_Online_Action_Use_v0_1.md").read_bytes()).hexdigest()==a["provenance"]["note_sha256"],a["provenance"]["note_sha256"])
existing_rules={x["id"] for x in g["rules"]};existing_nodes={x["id"] for x in g["nodes"]}
check("overrides_point_to_existing_rules_and_nodes",set(a["suspended_raw_rules"])<=existing_rules and set(a["node_overrides"])<=existing_nodes and all(x["conclusion_node"] in existing_nodes for x in a["effective_rules"]),"typed overlay; no new raw nodes")
check("explicit_compatibility_survives_downstream","compat_instance" in r["all_of"] and "local_instance" in r["all_of"],r["all_of"])
out={"schema":"UCT_R172_QC06_QC07_CHECKS/v1","status":"PASS" if all(c["status"]=="PASS" for c in checks) else "FAIL","checks":checks,"limitations":["Logical guards and finite toy witnesses only; no physical realization, global theory proof, B_min or C1 validation.","Raw historical 24/24 audit did not check these semantic defects; this overlay is mandatory."]}
(HERE/"REVIEW_CORRECTION_CHECKS.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":out["status"],"checks":len(checks),"failures":[x["name"] for x in checks if x["status"]!="PASS"]}))
assert out["status"]=="PASS"
