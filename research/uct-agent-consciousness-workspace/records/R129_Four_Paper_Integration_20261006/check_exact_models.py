"""Exact finite witnesses for published D/R96/R96D mathematics; no experiment."""
from collections import Counter
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json

REC=Path(__file__).resolve().parent
profiles=list(product((-1,0,1), repeat=5))
bundled=lambda t:(t[0]+t[2]+t[3],t[1]+t[2]+t[4])
direct=lambda t:t[:3]+bundled(t)
sign=lambda x:(x>0)-(x<0)
bundles=Counter(map(bundled,profiles))
all_rows=Counter(map(direct,profiles))
signs=Counter(tuple(map(sign,direct(t))) for t in profiles)
bundle_signs=Counter(tuple(map(sign,bundled(t))) for t in profiles)
assert (len(bundles),max(bundles.values()))==(43,17)
assert (len(all_rows),max(all_rows.values()))==(243,1)
assert (len(signs),max(signs.values()))==(121,9)
assert (len(bundle_signs),max(bundle_signs.values()))==(9,46)
for theta in profiles:
    q,o,g,qg,og=direct(theta)
    assert (q,o,g,qg-q-g,og-o-g)==theta

# Construct valid potential-outcome tables, not just marginal algebra.
# O is unchanged by action; Q1>=Q0 in each of four equiprobable worlds.
other=(1,1,0,0)
tables={'A':((1,0,0,0),(1,0,1,1)), 'B':((0,0,1,0),(1,1,1,0))}
values={}
witness=[]
for name,(q0,q1) in tables.items():
    assert all(a<=b for a,b in zip(q0,q1))
    actions=[]
    for action,q in enumerate((q0,q1)):
        pq=F(sum(q),4);po=F(sum(other),4)
        joint=F(sum(a*b for a,b in zip(q,other)),4)
        reward=F(sum(a or b for a,b in zip(q,other)),4)
        value=reward-F(action,4)
        assert pq==(F(1,4) if action==0 else F(3,4)) and po==F(1,2)
        assert reward==pq+po-joint
        actions.append(value)
        witness.append(dict(context=name,action=action,q=str(pq),o=str(po),joint=str(joint),value=str(value)))
    values[name]=actions
assert values=={'A':[F(1,2),F(3,4)],'B':[F(3,4),F(1,2)]}
coarse=max((values['A'][a]+values['B'][a])/2 for a in (0,1))
fine=(max(values['A'])+max(values['B']))/2
assert (coarse,fine,fine-coarse)==(F(5,8),F(3,4),F(1,8))

result={'revision':'R129-v1.0','all_pass':True,'scope':'Exact coefficient-grid enumeration and valid four-world decision witness. Not empirical validation, global neural verification, or a consciousness/valence measurement. General proofs are manual in the integration note.',
 'coefficient_grid':{'profiles':len(profiles),'bundled_signatures':len(bundles),'largest_bundled_class':max(bundles.values()),'bundled_sign_signatures':len(bundle_signs),'largest_bundled_sign_class':max(bundle_signs.values()),'five_logit_signatures':len(all_rows),'five_choice_signatures':len(signs),'largest_five_choice_class':max(signs.values()),'all_coefficients_reconstructed':True},
 'matched_marginal_witness':witness,'optimal_values':{'marginal_only':str(coarse),'joint_or_task_value':str(fine),'gap':str(fine-coarse)},'randomization_note':'A context-blind mixture has the same 5/8 value by linearity; no hidden context bypass is allowed.'}
(REC/'EXACT_MATH_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
