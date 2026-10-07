"""Finite witnesses for R157; not proof-assistant or empirical validation."""
from itertools import permutations, product
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
checks=[]
def check(name, value, scope):
    assert value, name
    checks.append(dict(name=name, passed=True, scope=scope))

# A finite two-sorted proxy flattened to U={0,1,2}: unary Body and binary Route.
# theta(x): Body(x) and exists y Route(y,x). Verify all 3! renamings.
U=range(3); Body={1,2}; Route={(0,1),(2,1)}
def selected(body,route):
    return {x for x in U if x in body and any((y,x) in route for y in U)}
S=selected(Body,Route)
covariant=True
for p_tuple in permutations(U):
    p=dict(zip(U,p_tuple))
    body2={p[x] for x in Body}; route2={(p[x],p[y]) for x,y in Route}
    covariant &= {p[x] for x in S} == selected(body2,route2)
check('definable_selector_covariant_under_all_renamings',covariant,'all 6 permutations of the finite witness; general proof is formula induction')

# Observer-only label is not covariant when the structure is renamed but the label is frozen.
frozen={1}
p={0:0,1:2,2:1}
check('frozen_external_label_fails_covariance',{p[x] for x in frozen}!={1},'one transposition; demonstrates need for declared parameter transport')

# Same transported support admits two metalinguistic naming assignments without changing K-data.
naming1={'mineness':tuple(sorted(S))}
naming2={'body_role':tuple(sorted(S)),'mineness':None}
check('semantic_name_not_fixed_by_K_structure',naming1!=naming2 and tuple(sorted(S))==naming1['mineness']==naming2['body_role'],'metalinguistic witness only; not two experiences')

# Report measure partial on a domain containing a nonreporting token.
Omega=('reporter','nonreporter')
M={'reporter':1}
check('report_measure_not_total',set(M)!=set(Omega),'declared mixed domain')
extensions=[dict(M,nonreporter=v) for v in (0,1)]
check('report_extension_not_unique',len({tuple(sorted(x.items())) for x in extensions})==2,'two total Boolean extensions agree on reporter')

# Conjunction requires every body-role component; dropping one changes the selected set.
states=list(product((0,1),repeat=4))
theta=lambda s:all(s)
check('candidate_conjunction_has_explicit_all_of',sum(theta(s) for s in states)==1,'four Boolean role components; method witness, not biological law')

out=dict(status='BOUNDED_CHECKS_PASS',check_count=len(checks),checks=checks,
         proof_assistant_certified=False,physical_realization_validated=False,phenomenal_target_measured=False)
(HERE/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(status=out['status'],checks=len(checks))))
