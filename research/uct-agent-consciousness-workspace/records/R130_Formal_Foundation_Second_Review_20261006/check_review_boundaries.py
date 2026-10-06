"""Exact targeted checks of mathematical scope; no data fitting or simulation."""
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path

P=Path(__file__).resolve().parent
def tv(p,q):
    return sum(abs(p.get(k,0)-q.get(k,0)) for k in set(p)|set(q))/2
def law(rows,key):
    result={}
    for row,w in rows:
        k=key(row);result[k]=result.get(k,F(0))+w
    return result
preparations={x:[((x^b,b),F(1,2)) for b in (0,1)] for x in (0,1)}
marginals=[law(preparations[x],lambda z:z[0]) for x in (0,1)]
joints=[law(preparations[x],lambda z:z) for x in (0,1)]
outputs=[law(preparations[x],lambda z:z[0]^z[1]) for x in (0,1)]
assert tv(*marginals)==0 and tv(*joints)==1 and tv(*outputs)==1
conditional_tvs=[]
for b in (0,1):
    conditional_tvs.append(tv({b:F(1)},{1^b:F(1)}))
assert conditional_tvs==[F(1),F(1)]

S=range(3)
summaries=list(product((0,1),repeat=3))
def closed(update,p):
    return all(p[s]!=p[t] or p[update[s]]==p[update[t]] for s in S for t in S)
composition_cases=0;admissible_pairs=0
for update in product(S,repeat=3):
    for p1,p2 in product(summaries,repeat=2):
        composition_cases+=1
        if closed(update,p1) and closed(update,p2):
            admissible_pairs+=1
            joint=list(zip(p1,p2));assert closed(update,joint)
            quotient={joint[s]:joint[update[s]] for s in S}
            assert set(quotient.values())<=set(joint)

decision_cases=0;zero_gain=0;strict_gain=0;tie_cases=0
for vals in product((-1,0,1),repeat=4):
    u=[vals[:2],vals[2:]]
    argmax=[{a for a in (0,1) if row[a]==max(row)} for row in u]
    common=bool(argmax[0]&argmax[1])
    for w in (F(1,4),F(1,2),F(3,4)):
        base=max(w*u[0][a]+(1-w)*u[1][a] for a in (0,1))
        enhanced=w*max(u[0])+(1-w)*max(u[1])
        assert enhanced>=base
        assert (enhanced==base)==common
        decision_cases+=1;zero_gain+=enhanced==base;strict_gain+=enhanced>base
        tie_cases+=any(len(a)>1 for a in argmax)
result={'revision':'R130-v1.0','all_pass':True,
 'scope':'Exact finite checks of the documented scope risks. General claims remain analytically proved; no empirical model or subjective state is measured.',
 'F20_mask_witness':{'internal_marginal_TV':str(tv(*marginals)),'joint_cut_TV':str(tv(*joints)),'output_TV':str(tv(*outputs)),'common_b_conditional_TV':[str(x) for x in conditional_tvs],'decoding_errors':[0,0],'unqualified_marginal_bound_fails':True,'conditional_and_joint_bounds_hold':True},
 'deterministic_composition':{'states':3,'total_maps':27,'binary_summaries':8,'map_summary_pair_cases':composition_cases,'individually_closed_pairs':admissible_pairs,'joint_closure_and_image_invariance_pass':True},
 'information_value':{'payoff_tables':81,'strictly_positive_weight_pairs':3,'cases':decision_cases,'zero_gain_cases':zero_gain,'strict_gain_cases':strict_gain,'cases_with_conditional_ties':tie_cases,'common_optimum_iff_zero_gain':True}}
(P/'BOUNDARY_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
