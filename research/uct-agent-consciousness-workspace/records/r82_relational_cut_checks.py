"""Exact finite checks of a stochastic interface bound, not trained-model data."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json

states=list(product([0,1],repeat=2))
def tv(p,q):return sum(abs(a-b) for a,b in zip(p,q))/2
def parity_laws(K):
 return [[sum(K[a,b][k] for a,b in states if a^b==t)/2 for k in range(4)] for t in [0,1]]
def optimum(p,q):
 scores=[]
 for d in product([0,1],repeat=4):
  score=sum((p[k] if d[k]==0 else q[k]) for k in range(4))/2
  scores.append((score,d))
 best=max(s[0] for s in scores)
 assert best==(1+tv(p,q))/2
 return best,[d for v,d in scores if v==best]
def bern(p,u):return p if u else 1-p
grid=[F(0),F(1,2),F(1)]
rows=[]
for a0,a1,b0,b1 in product(grid,repeat=4):
 A=[a0,a1];B=[b0,b1]
 K={(a,b):[bern(A[a],u)*bern(B[b],v) for u,v in states] for a,b in states}
 p,q=parity_laws(K);best,decoders=optimum(p,q)
 da=abs(a1-a0);db=abs(b1-b0)
 assert tv(p,q)==da*db
 rows.append({'pU1_given_A':[a0,a1],'pV1_given_B':[b0,b1],
  'conditional_joint':{f'{a}{b}':v for (a,b),v in K.items()},
  'target_conditional_laws':[p,q],'delta_A':da,'delta_B':db,'joint_delta':tv(p,q),
  'best_accuracy':best,'optimal_decoders':decoders})

def masked(same_mask):
 K={}
 for a,b in states:
  probs=[F(0)]*4
  coins=[(r,r,F(1,2)) for r in [0,1]] if same_mask else [(r,s,F(1,4)) for r,s in states]
  for r,s,p in coins:probs[states.index((a^r,b^s))]+=p
  K[a,b]=probs
 p,q=parity_laws(K);best,ds=optimum(p,q)
 margu=[[sum(K[a,b][k] for b in [0,1] for k,(u,v) in enumerate(states) if u==x)/2 for x in [0,1]] for a in [0,1]]
 margv=[[sum(K[a,b][k] for a in [0,1] for k,(u,v) in enumerate(states) if v==x)/2 for x in [0,1]] for b in [0,1]]
 da=tv(*margu);db=tv(*margv)
 assert da==db==0
 actual=sum(K[a,b][k]/4 for a,b in states for k,(u,v) in enumerate(states) if u^v==a^b)
 assert actual==best
 return {'conditional_joint':{f'{a}{b}':v for (a,b),v in K.items()},
  'target_conditional_laws':[p,q],'local_delta_A':da,'local_delta_B':db,
  'joint_delta':tv(p,q),'best_accuracy':best,'installed_xor_accuracy':actual}
shared=masked(True);broken=masked(False);restored=masked(True)
assert shared['best_accuracy']==1 and broken['best_accuracy']==F(1,2) and restored==shared
# Fixed full-information channel; selecting a different consumer changes use only.
use={'joint_delta':F(1),'coin_consumer_accuracy':F(1,2),'parity_consumer_accuracy':F(1)}
out={'scope':'formal finite probability models and exact enumeration only',
 'independent_channel_cases':rows,'shared_mask_counterexample':shared,
 'independent_masks_intervention':broken,'shared_mask_restoration':restored,
 'fixed_encoding_different_use':use,
 'coverage':{'independent_channels':len(rows),'decoders_per_case':16},
 'claims':'All assertion checks passed; no new learning or subjective data'}
def convert(v):
 if isinstance(v,F):return str(v)
 if isinstance(v,dict):return {k:convert(x) for k,x in v.items()}
 if isinstance(v,(tuple,list)):return [convert(x) for x in v]
 return v
Path('R82_Relational_Cut_Results.json').write_text(json.dumps(convert(out),indent=2)+'\n')
print(json.dumps(convert({'independent_channel_cases':len(rows),
 'shared_mask':shared,'broken_correlation':broken,'readout_control':use}),indent=2))
