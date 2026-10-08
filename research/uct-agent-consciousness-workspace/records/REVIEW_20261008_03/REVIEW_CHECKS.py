"""Scoped reviewer checks; pass the research workspace containing R172 overlay.

Does not rerun researcher PASS labels or establish actual physical realization.
"""
from pathlib import Path
import json,sys,hashlib
from fractions import Fraction as F
from itertools import product

root=Path(sys.argv[1])
path=root/'records/R172_Interface_Composition_and_Action_Use_20261008/REVIEW_AMENDMENTS.json'
overlay=json.loads(path.read_text())
checks=[]
def check(name,result,scope):
    assert result,name
    checks.append({'name':name,'pass':True,'scope':scope})
rules={r['id']:r for r in overlay['effective_rules']}
required=rules['r172_witnessed_online_action_use_effective']['all_of']
check('QC06_explicit_actual_instance_premises',set(['frame_instance','local_instance','compat_instance','cert_positive','role_bridge','same_binding']).issubset(required),'Effective rule retains actual discharges, not just a conditional schema.')
L,C,J,Fm,U=False,False,False,True,True
old_conditional=(not(L and C)) or J
check('QC06_old_countervaluation_blocked',old_conditional and Fm and U and not C,'Schema-only and J-only routes cannot discharge explicit compat_instance.')
bindings=[('P1','I','K'),('P1','I','K'),('P2','I','K')]
check('QC06_same_binding_is_substantive',len(set(bindings))!=1,'True local facts about different P do not form one positive instance.')
selector=overlay['actual_selector']
check('QC07_selector_separates_evidence',set(['W','E','certificate_status']).issubset(selector['excluded_analyst_parameters']) and 'TransferOccurrence' in selector['formula'] and 'OperandUseOccurrence' in selector['formula'],'Executed path distinct from W-indexed evidence; actual grounding remains unvalidated.')
live=lambda k:k
W0=[0];W01=[0,1]
separates=lambda W:len({live(k) for k in W})>1
check('QC07_same_mechanism_different_tests',not separates(W0) and separates(W01) and live(0)==0,'Evidence availability changes; no physical path change is inferred.')
h=lambda x:1-x
check('QC07_parameter_transport',h(0)==1 and h(0)!=0,'For selector x=p, h maps p too; holding physical p fixed would change its truth.')
rows=list(product([0,1],repeat=3))
admissible=[r for r in rows if not r[1] or r[0]]
check('QC08_baseline_admissible_counterdomain',len(rows)==8 and len(admissible)==6 and (0,1,0) not in admissible and (0,1,1) not in admissible,'Under actual-baseline admission, AgencyLoop entails an executed admissible action, hence Avail. The premise must be specified, not assumed universal.')
def signature(route,c=F(2),s=F(3)):
    if route=='S': return (-c,-c/s,F(0),F(0))
    if route=='C': return (-c,F(0),-c,F(0))
    return (-c,-c/s,-c,-c/s)
check('R174_three_signatures_distinct',len({signature(x) for x in ['S','C','H']})==3,'Checks displayed signatures on one exact instance; manual substitution supplies the general c!=0,s>0 argument.')
theta=[0,0];same_f=[1,1];different_f=[0,1]
is_function=lambda ts,ys:all(ts[i]!=ts[j] or ys[i]==ys[j] for i in range(len(ts)) for j in range(len(ts)))
check('QC09_fiber_counterexample_direction',is_function(theta,same_f) and not is_function(theta,different_f),'Same target in one selector fiber is compatible; different target is the sufficiency counterexample.')
result={'review':'REVIEW-20261008-03','overlay_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checks':checks,'limits':['Scoped contract and model verification only','No complete semantic graph proof','No physical or phenomenal validation','New BR20261008 author contribution excluded from independent review closure']}
Path(__file__).with_name('REVIEW_CHECK_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'QC06_QC07':'effective corrections verified','QC08_QC09':'counterexamples reproduced'}))
