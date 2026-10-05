"""R80: archived tiny network, implemented activation interventions; no training.

All initial/final checkpoints included. Frozen mathematical questions:
input-to-unit dependence; node-local preservation obstruction; global inverse;
single-node interchange effects and routing of the R78 mixed contrast.
These are finite software-mechanism checks, not a complete hardware signature.
"""
import json, hashlib, platform, csv
from pathlib import Path
import numpy as np

src=Path('r78_results/R78_Summary.json')
data=json.loads(src.read_text())
X=np.array(data['input_domain']); S=X[:,0]*X[:,1]
out=[]; table=[]; atol=1e-10
for run in data['runs']:
 rec={'seed':run['seed'],'condition':run['condition'],'checkpoints':{}}
 for name in ['initial','final']:
  cp=run[name];p=np.array(cp['weights']);W=p[:4].reshape(2,2);b=p[4:6];v=p[6:8];c=p[8]
  H=np.tanh(X@W.T+b);L=H@v+c
  assert np.max(np.abs(H-np.array(cp['hidden'])))<atol
  patches=[]; maxerr=0.
  for base in range(4):
   for source in range(4):
    for j in range(2):
     hp=H[base].copy();hp[j]=H[source,j]
     lp=float(hp@v+c);delta=lp-float(L[base]);expected=float(v[j]*(H[source,j]-H[base,j]))
     maxerr=max(maxerr,abs(delta-expected))
     patches.append({'base':base,'source':source,'unit':j,'patched_logit':lp,'delta':delta,'expected_delta':expected})
  assert maxerr<atol
  # Input flips at each context, and a one-unit clamp to the base activation.
  routes=[]
  for i in range(2):
   for j in range(2):
    effects=[]
    for ctx in [-1.,1.]:
     lo=next(k for k,x in enumerate(X) if x[i]==-1 and x[1-i]==ctx)
     hi=next(k for k,x in enumerate(X) if x[i]==1 and x[1-i]==ctx)
     patched=H[hi].copy();patched[j]=H[lo,j]
     clamped_logit=float(patched@v+c)
     mediated=float(L[hi]-clamped_logit)
     expected=float(v[j]*(H[hi,j]-H[lo,j]))
     assert abs(mediated-expected)<atol
     effects.append({'context':ctx,'hidden_change':float(H[hi,j]-H[lo,j]),'mediated_logit_change':mediated})
    q=(effects[1]['mediated_logit_change']-effects[0]['mediated_logit_change'])/4
    expected_q=float(v[j]*np.mean(S*H[:,j]))
    assert abs(q-expected_q)<atol
    routes.append({'input':i,'unit':j,'effects':effects,'mixed_contribution':q})
  d=float(np.mean(S*L))
  for i in range(2):assert abs(sum(r['mixed_contribution'] for r in routes if r['input']==i)-d)<atol
  det=float(np.linalg.det(W));inv_err=None
  if det!=0 and np.all(np.abs(H)<1):
   recovered=np.linalg.solve(W,(np.arctanh(H)-b).T).T
   inv_err=float(np.max(np.abs(recovered-X)))
   assert inv_err<1e-5 # saturation makes the inverse numerically ill-conditioned
  item={'weights':p.tolist(),'det_W':det,'W_condition_number':float(np.linalg.cond(W)),
   'active_input_edges':(W!=0).astype(int).tolist(),'hidden':H.tolist(),'logits':L.tolist(),
   'distinct_values_per_unit':[len(set(H[:,j])) for j in range(2)],
   'inverse_reconstruction_max_error':inv_err,'patch_max_error':maxerr,
   'interchanges':patches,'routes':routes,'mixed_logit':d}
  rec['checkpoints'][name]=item
  table.append({'seed':run['seed'],'condition':run['condition'],'checkpoint':name,
   'input_edge_count':int(np.count_nonzero(W)),'det_W':det,'inverse_error':inv_err,
   'unit0_distinct':item['distinct_values_per_unit'][0],'unit1_distinct':item['distinct_values_per_unit'][1],
   'mixed_logit':d,'unit0_mixed':routes[0]['mixed_contribution'],'unit1_mixed':routes[1]['mixed_contribution']})
 a=rec['checkpoints']['initial'];z=rec['checkpoints']['final']
 rec['local_bijection_cardinality_obstruction']=any(x!=y for x,y in zip(a['distinct_values_per_unit'],z['distinct_values_per_unit']))
 if run['condition']=='readout_only':
  assert a['hidden']==z['hidden']
  assert not rec['local_bijection_cardinality_obstruction']
 else:
  assert a['active_input_edges']==[[1,0],[0,1]] and z['active_input_edges']==[[1,1],[1,1]]
  assert rec['local_bijection_cardinality_obstruction']
 out.append(rec)

# Scope counterexample: nonzero input dependence does not ensure downstream use.
# An existing final checkpoint is re-evaluated with its readout disabled.
p=np.array(data['runs'][6]['final']['weights']);W=p[:4].reshape(2,2);b=p[4:6]
unused_H=np.tanh(X@W.T+b);unused_L=unused_H@np.zeros(2)+p[8]
assert np.all(unused_L==unused_L[0])
unused={'description':'seed 3 full final, both readout weights set to zero; no retraining',
 'hidden':unused_H.tolist(),'logits':unused_L.tolist(),'mixed_logit':float(np.mean(S*unused_L))}
assert abs(unused['mixed_logit'])<atol
symH=np.tanh(X@np.array([[1.,2.],[2.,1.]]).T)
symL=symH@np.array([1.,1.])
assert abs(float(np.mean(S*symL)))<atol
nonlinearL=X[:,0]*X[:,1]
nonlinear_loss=float(np.logaddexp(0,-S*nonlinearL).mean())
assert nonlinear_loss<np.log(2)
counterexamples={'dense_but_odd_hidden':{'W':[[1,2],[2,1]],'b':[0,0],'v':[1,1],
 'hidden':symH.tolist(),'logits':symL.tolist(),'mixed_logit':float(np.mean(S*symL))},
 'nonlinear_consumer':{'hidden':'h=x; separate channels','readout':'logit=h0*h1',
 'logits':nonlinearL.tolist(),'loss':nonlinear_loss,'purpose':'affine-readout premise is necessary for hidden-route necessity'}}
result={'scope':'new small activation-intervention evaluations of archived R78 checkpoints, no training or subjective data',
 'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'python':platform.python_version(),'numpy':np.__version__,
 'absolute_tolerance':atol,'checkpoints':32,'interchanges':1024,'route_clamps':256,
 'runs':out,'unused_readout_counterexample':unused,'analytic_scope_counterexamples':counterexamples}
Path('R80_Constituent_Audit_Results.json').write_text(json.dumps(result,indent=2)+'\n')
with open('R80_Constituent_Audit_Table.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=table[0].keys());w.writeheader();w.writerows(table)
print(json.dumps({'checkpoints':32,'interchanges':1024,'route_clamps':256,
 'max_patch_error':max(z['patch_max_error'] for r in out for z in r['checkpoints'].values()),
 'max_inverse_error':max(z['inverse_reconstruction_max_error'] or 0 for r in out for z in r['checkpoints'].values()),
 'final_full':[t for t in table if t['checkpoint']=='final' and t['condition']=='full'],
 'unused_readout_counterexample':unused},indent=2))
