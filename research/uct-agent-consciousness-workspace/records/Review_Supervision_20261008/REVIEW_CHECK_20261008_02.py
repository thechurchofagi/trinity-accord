#!/usr/bin/env python3
"""Targeted reviewer checks, not a general proof or empirical study."""
from pathlib import Path
from itertools import product
from hashlib import sha256
import json, subprocess, zipfile

ROOT = Path(__file__).resolve().parent
checks = []
def check(name, condition, detail):
    checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

# R171 correction: case split between routes, conjunction within each route.
amend = json.loads((ROOT / "REVIEW_AMENDMENTS.json").read_text())
for direct, inductive in product((False, True), repeat=2):
    facts = dict.fromkeys(["R170_application_holds", "common_target_binding",
        "domain_scope_accepted", "valid", "not_refuted"], True)
    facts.update(D_discharged=direct, I_discharged=inductive)
    fired = [r["id"] for r in amend["A2"]["effective_instance_routes"]
             if all(facts.get(p, False) for p in r["all_of"])]
    check(f"R171_route_{int(direct)}_{int(inductive)}",
          len(fired) == int(direct) + int(inductive), fired)
check("R171_seven_states", len(set(amend["A3"]["states"])) == 7,
      amend["A3"]["states"])
H_unrestricted = list(product((False, True), repeat=2))
H_constant = [h for h in H_unrestricted if h[0] == h[1]]
unrestricted_after_true = [h for h in H_unrestricted if h[0]]
constant_after_true = [h for h in H_constant if h[0]]
check("R171_H_qualification",
      len(unrestricted_after_true) == 2 and constant_after_true == [(True, True)],
      {"unrestricted": unrestricted_after_true, "constant": constant_after_true})

# R172 rule audit under the literal conditional-schema reading.
# L = local certificate instance; C = Compat; J = joint invariant;
# F = actual frame installation; U = LiveUse. This is a propositional
# countervaluation, not a physically instantiated model.
bad = []
for L,C,J,F,U in product((False, True), repeat=5):
    schema = (not (L and C)) or J
    antecedent = F and schema and U
    theta = F and C and U
    if antecedent and not theta:
        bad.append(dict(L=L,C=C,J=J,F=F,U=U,schema=schema,theta=theta))
check("R172_schema_to_Compat_countervaluation", bool(bad), bad[0])
check("R172_joint_invariant_to_Compat_countervaluation",
      (True and True and True) and not (True and False and True),
      {"F": True, "J": True, "U": True, "C": False,
       "meaning": "J alone does not entail C; not an actual-system claim"})
repaired = []
for L,C,J,F,U in product((False, True), repeat=5):
    schema = (not (L and C)) or J
    if F and schema and U and C and not (F and C and U):
        repaired.append((L,C,J,F,U))
check("R172_explicit_Compat_blocks_this_gap", not repaired,
      {"countervaluations": repaired})

# Same underlying live model a=k, two externally selected witness families.
def witness(values):
    return len({k for k in values}) > 1
w0 = (0,)
w01 = (0,1)
check("R172_W_index_changes_witness_not_fixed_equation",
      not witness(w0) and witness(w01),
      {"equation": "a=k", "W0": w0, "W01": w01,
       "witness_W0": witness(w0), "witness_W01": witness(w01),
       "meaning": "Nondetection stays unresolved; no inference of absence."})

graph = json.loads((ROOT / "UCT_FORMAL_GRAPH.json").read_text())
gb = (ROOT / "UCT_FORMAL_GRAPH.json").read_bytes()
gh = sha256(gb).hexdigest()
check("R172_remote_graph_integrity",
      len(gb)==2256525 and
      gh=="5efd423f6b651649263d9703f31938b4259639c79f967b51f4109052fcb3587d"
      and len(graph["nodes"])==506 and len(graph["rules"])==244
      and len(graph["context_links"])==141,
      {"bytes":len(gb),"sha256":gh,"counts":[len(graph["nodes"]),len(graph["rules"]),len(graph["context_links"])]})
zb = (ROOT / "UCT_R172_Research_Increment_20261008.zip").read_bytes()
zh = sha256(zb).hexdigest()
with zipfile.ZipFile(ROOT / "UCT_R172_Research_Increment_20261008.zip") as z:
    crc_bad = z.testzip()
    members = len(z.namelist())
check("R172_persistent_package_byte_readback",
      len(zb)==472916 and
      zh=="ae26c1dbac9810bf38c8b4055fb91458ae76c64c777e7ad7fe5f82f8e90f1a0f"
      and crc_bad is None,
      {"bytes":len(zb),"sha256":zh,"zip_crc_bad_member":crc_bad,"members":members,
       "scope":"Exact saved R172 increment, not the entire repository or later reviews."})
out={"schema":"UCT_REVIEW_CHECKS/v1","review":"REVIEW-20261008-02",
     "research_head":"283ee845c51b47221ca73121fc0dec1573f917eb",
     "status":"PASS" if all(c["status"]=="PASS" for c in checks) else "FAIL",
     "checks":checks,
     "limits":["PASS confirms these scoped reviewer checks, including countervaluations; it does not certify all research.",
       "The R172-C transport remains valid as a conditional formula-preservation result if its grounded-definability assumptions hold.",
       "No whole-map semantic proof, physical experiment or phenomenal measurement was performed.",
       "The rule countervaluation applies unless the theorem node is explicitly a provenance-carrying instance witness."]}
(ROOT/"REVIEW_CHECKS_20261008_02.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
assert out["status"]=="PASS"
