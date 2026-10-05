#!/usr/bin/env python3
"""Post hoc training-only least-squares audit; leaves frozen runs unchanged."""
import json
import numpy as np
from r92_delayed_retention import ROOT,TRAIN,forward,metrics

out=[]
for kind in ('linear','tanh'):
    for seed in range(4):
        name=f'{kind}_d2_readout_s{seed}'
        r=json.loads((ROOT/'R92_runs'/(name+'.json')).read_text())
        p={k:np.array(v) for k,v in r['checkpoints'][-1]['parameters'].items()}
        _,hs=forward(p,TRAIN,kind)
        coef,residuals,rank,svals=np.linalg.lstsq(hs[-1],TRAIN,rcond=None)
        q={**p,'B':coef.T}
        out.append({'run':name,'status':'posthoc diagnostic, not replacement of frozen result','design_rank':int(rank),'design_singular_values':svals.tolist(),'design_condition':float(svals[0]/svals[-1]),'least_squares_B':q['B'].tolist(),'training':metrics(q,kind,x=TRAIN),'heldout':metrics(q,kind,detail=True),'original_Adam_N':r['final']['normalized_error']})
(ROOT/'R92_Posthoc_Readout_Results.json').write_text(json.dumps(out,indent=2)+'\n')
for r in out:
    print(r['run'],'condition=',r['design_condition'],'Adam_N=',r['original_Adam_N'],'LS_test_N=',r['heldout']['normalized_error'],'LS_J_error=',r['heldout']['max_jacobian_identity_error'])
