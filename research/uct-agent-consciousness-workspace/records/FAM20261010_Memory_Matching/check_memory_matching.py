"""Exact illustrative two-rate-model checks, not human data or H measurement."""
from fractions import Fraction as F
from pathlib import Path
import json
def enc(x):
 if isinstance(x,F):return {'fraction':str(x),'decimal':float(x)}
 if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [enc(v) for v in x]
 return x
af,ass=F(1,2),F(99,100)
x,y=(F(2,5),F(1,10)),(F(1,10),F(2,5))
u=lambda z:sum(z)
nxt=lambda z:(af*z[0],ass*z[1])
q=lambda z:z[0]+2*z[1]
recover=lambda v0,v1:((ass*v0-v1)/(ass-af),(v1-af*v0)/(ass-af))
checks={}
checks['matched_total_correction']=u(x)==u(y)==F(1,2)
checks['unequal_next_correction']=u(nxt(x))==F(299,1000) and u(nxt(y))==F(223,500)
checks['two_samples_recover_declared_states']=recover(u(x),u(nxt(x)))==x and recover(u(y),u(nxt(y)))==y
checks['matched_output_does_not_match_agency_surrogate']=q(x)==F(3,5) and q(y)==F(9,10)
grid=[(F(i,10),F(j,10)) for i in range(-10,11) for j in range(-10,11)]
groups={}
for z in grid:groups.setdefault((u(z),q(z)),[]).append(z)
checks['full_rank_controls_are_injective_on_grid']=all(len(g)==1 for g in groups.values())
equalrate=F(4,5)
checks['equal_retention_rate_time_series_remains_aliased']=all(equalrate**t*u(x)==equalrate**t*u(y) for t in range(12))
cancel=(F(-2,5),F(2,5));zero=(F(0),F(0))
checks['zero_total_not_empty_memory']=u(cancel)==u(zero)==0 and u(nxt(cancel))==F(49,250)>0
extended=[{'state':[*x,r],'motor':u(x),'agency_surrogate':q(x),'extra_readout':r} for r in [F(0),F(1)]]
checks['third_coordinate_can_vary_but_is_only_assumed']=extended[0]['motor']==extended[1]['motor'] and extended[0]['agency_surrogate']==extended[1]['agency_surrogate'] and extended[0]['extra_readout']!=extended[1]['extra_readout']
bf,bs=F(1,5),F(1,20)
def history(z):
 e0=(z[0]/bf-z[1]/bs)/(af-ass);e1=z[0]/bf-af*e0
 return [e0,e1]
def form(es):
 f=s=F(0)
 for e in es:f,s=af*f+bf*e,ass*s+bs*e
 return f,s
checks['same_learning_law_reaches_witness_with_unbounded_prescribed_errors']=form(history(x))==x and form(history(y))==y
assert all(checks.values()),checks
result={'id':'FAM20261010','result_version':'FAM-APPLICATION-v0.1.0','scope':'EXACT_RATIONAL_ILLUSTRATION_OF_INHERITED_TWO_RATE_MODEL_AND_ELEMENTARY_RANK_ARGUMENT','parameters_illustrative_not_fitted':{'fast_retention':af,'slow_retention':ass},'witness':{'x':x,'y':y,'present_motor':[u(x),u(y)],'next_motor':[u(nxt(x)),u(nxt(y))],'agency_surrogate':[q(x),q(y)]},'cancellation':{'state':cancel,'present_motor':u(cancel),'next_motor':u(nxt(cancel))},'model_recovery_formula':'f=(a_s*u0-u1)/(a_s-a_f); s=(u1-a_f*u0)/(a_s-a_f), only declared zero-input known-parameter model','matched_control_argument':'det [[1,1],[c_f,c_s]]=c_s-c_f; when nonzero, matching motor and modeled agency fixes both states, so any state-only target is fixed','grid_states':len(grid),'checks':checks,'passed':True,'new_human_data':False,'physical_ports_identified':False,'phenomenal_endpoint_validated':False,'extra_coordinate_instantiated':False,'new_general_math_claim':False,'originality':'INHERITED_MODEL_AND_MATH; SCOPED_APPLICATION_AND_STOP_RULE; PRIORITY_UNVERIFIED'}
result['formation_witness']={'learning_rates':[bf,bs],'x_errors':history(x),'y_errors':history(y),'input_domain':'UNBOUNDED_PRESCRIBED_RATIONAL_ERRORS_IN_THE_ABSTRACT_MODEL','physical_feasibility':False,'note':'No bounded-error human protocol or actual route/lineage binding follows.'}
Path(__file__).with_name('EXACT_RESULTS.json').write_text(json.dumps(enc(result),ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(checks),'grid_states':len(grid),'new_H_data':False}))
