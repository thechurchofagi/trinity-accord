"""Exact logical/causal witnesses only. Not phenomenal observations."""
from itertools import permutations,product
import json
from pathlib import Path
labels=('a','b','c','d')
orders=[p for p in permutations(labels) if p[0]=='a' and p[-1]=='d']
def before(o,x,y): return o.index(x)<o.index(y)
def between(o,x,y,z): return before(o,x,y) and before(o,y,z) or before(o,z,y) and before(o,y,x)
checks={}
checks['partial_data_exactly_two_completions']=len(orders)==2
checks['fixed_named_target_disagrees']={before(o,'b','c') for o in orders}=={True,False}
checks['same_endpoint_interior_facts']=all(between(o,'a',b,'d') for o in orders for b in ['b','c'])
checks['existential_oriented_maps_do_not_select_named_target']=all(all(between((0,1,2,3),i,j,k)==between(o,o[i],o[j],o[k]) for i,j,k in product(range(4),repeat=3)) for o in orders)
checks['image_order_true_in_both']=all(before(o,o[1],o[2]) for o in orders)
q=labels
q_orders=[o for o in orders if all(between((0,1,2,3),i,j,k)==between(o,q[i],q[j],q[k]) for i,j,k in product(range(4),repeat=3))]
checks['fixed_q_bridge_selects_one']=q_orders==[labels]
checks['target_not_used_in_partial_filter']=len(orders)==2 and len(q_orders)==1
witnesses=[]
for g,dB,dC in product(range(1,5),range(5),range(5)):
 tB=1;tC=1+g;uB=tB+dB;uC=tC+dC
 assert (uB>uC)==(dB-dC>g)
 assert (uB==uC)==(dB-dC==g)
 assert (uB<uC)==(dB-dC<g)
 assert uB>=tB and uC>=tC
 witnesses.append((g,dB,dC))
checks['delay_trichotomy_100_cases']=len(witnesses)==100
checks['causal_reversal_witness']=(1+2>2+0) and 1<2
checks['baseline_agreement']=(1<2) and (1+0<2+0)
checks['tie_is_not_strict_order']=(1+1==2+0)
results={'scope':'Finite exact models and algebra; no actual experiential instance or general semantic map proof','checks':checks,'passed':all(checks.values()),'named_completions':[{'order':o,'T_b_before_c':before(o,'b','c'),'f_image_order':before(o,o[1],o[2])} for o in orders],'delay_case_count':len(witnesses),'causal_witness':{'production':{'B':1,'C':2},'use':{'B':3,'C':2},'candidate_H_prod':'B before C','candidate_H_use':'C before B','phenomenal_observation':None}}
Path(__file__).with_name('MODEL_RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
assert results['passed']
print(json.dumps({'passed':True,'checks':len(checks),'delay_cases':len(witnesses)}))
