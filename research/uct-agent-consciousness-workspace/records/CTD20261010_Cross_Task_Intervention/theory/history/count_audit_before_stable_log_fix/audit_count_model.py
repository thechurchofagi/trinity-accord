#!/usr/bin/env python3
"""Read-only numerical audit of the empirical agent's count-model code/results."""
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
EMP=ROOT.parent/'empirical'
spec=importlib.util.spec_from_file_location('audit_target',EMP/'fit_count_clock.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
fits=np.load(EMP/'results/count_model_fits.npz')
source=np.load(EMP/'alignment_diagnostic.npz')
counts=fits['counts']
res={"role":"independent read-only audit; no full bootstrap rerun"}
res['count_shape']=list(counts.shape)
res['original_count_noninteger_max']=float(np.max(np.abs(source['counts']-np.round(source['counts']))))
res['embedding_max_probability_error']=float(max(np.max(np.abs(mod.decode(th,True)[0]-mod.decode(mod.null_to_alt(th),False)[0])) for th in fits['nulltheta']))
res['null_embedding_within_alt_bounds']=all(all(low-1e-12<=value<=high+1e-12 for value,(low,high) in zip(mod.null_to_alt(th),mod.bounds(False))) for th in fits['nulltheta'])
res['fits']={}
res['gradient_checks']=[]
for shared,key in [(True,'nulltheta'),(False,'alttheta')]:
    ths=fits[key]
    bound=np.array(mod.bounds(shared))
    pb=np.array([mod.decode(th,shared)[0] for th in ths])
    near_lower=np.abs(ths-bound[:,0])<1e-6
    near_upper=np.abs(ths-bound[:,1])<1e-6
    projected_max=[]
    for th,y in zip(ths,counts):
        _,grad=mod.lossgrad(th,y,shared)
        grad=grad.copy()
        grad[((th-bound[:,0]<1e-6)&(grad>0))|((bound[:,1]-th<1e-6)&(grad<0))]=0
        projected_max.append(float(np.max(np.abs(grad))))
    res['fits'][key]={
        'probability_min':float(pb.min()),'probability_max':float(pb.max()),
        'lower_probability_clips':int((pb<=1e-12).sum()),
        'upper_probability_clips':int((pb>=1-1e-12).sum()),
        'params_near_lower_by_index':near_lower.sum(axis=0).tolist(),
        'params_near_upper_by_index':near_upper.sum(axis=0).tolist(),
        'participants_any_bound':int(np.any(near_lower|near_upper,axis=1).sum()),
        'projected_gradient_max_over_people':max(projected_max),
        'projected_gradient_median':float(np.median(projected_max)),
    }
    for person in (0,3,4,14,23,29):
        th=ths[person].copy()
        # Move bound parameters slightly inside before a symmetric derivative check.
        th=np.maximum(bound[:,0]+1e-4,np.minimum(bound[:,1]-1e-4,th))
        # Jitter free dimensions to avoid checking only gradients near zero.
        th += .002*np.sin(np.arange(len(th))+1)
        th=np.maximum(bound[:,0]+1e-4,np.minimum(bound[:,1]-1e-4,th))
        y=counts[person]
        _,analytical=mod.lossgrad(th,y,shared)
        numerical=[]
        step=1e-6
        for index in range(len(th)):
            left=th.copy();right=th.copy()
            left[index]-=step;right[index]+=step
            numerical.append((mod.lossgrad(right,y,shared)[0]-mod.lossgrad(left,y,shared)[0])/(2*step))
        numerical=np.array(numerical)
        error=np.abs(analytical-numerical)
        res['gradient_checks'].append({'model':key,'person_index':person,
                                      'max_abs_error':float(error.max()),
                                      'max_scaled_error':float(np.max(error/(1+np.abs(numerical)))),
                                      'clipped_cells_at_check':int((mod.decode(th,shared)[0]<=1e-12).sum())})

nullvals=np.array([mod.lossgrad(th,y,True)[0] for th,y in zip(fits['nulltheta'],counts)])
altvals=np.array([mod.lossgrad(th,y,False)[0] for th,y in zip(fits['alttheta'],counts)])
obs=float(2*np.sum(nullvals-altvals))
res['recomputed_LRT']=obs
res['minimum_person_LRT']=float(np.min(2*(nullvals-altvals)))
boot=np.load(EMP/'results/count_model_bootstrap.npz')
bad=boot['converged']!=len(counts)
values=boot['lrt']
good_exceed=int(((values>=obs)&~bad).sum())
res['bootstrap']={
    'B':len(values),'flagged_replicates':int(bad.sum()),
    'flagged_subject_fit_pairs':int(np.sum(len(counts)-boot['converged'])),
    'flagged_indices':np.flatnonzero(bad).tolist(),
    'flagged_values':values[bad].tolist(),
    'flagged_tail_exceedances':int(((values>=obs)&bad).sum()),
    'known_good_tail_exceedances':good_exceed,
    'worst_case_plus_one_p_interval_if_flagged_unknown':[(1+good_exceed)/(len(values)+1),(1+good_exceed+int(bad.sum()))/(len(values)+1)],
}
# Expose the gradient inconsistency introduced by probability clipping in a
# concrete admissible parameter state.  This is not a claim that saved fits clip.
th=fits['alttheta'][0].copy();th[12:]=-6
y=np.ones((2,3,7),dtype=int)
_,g=mod.lossgrad(th,y,False)
idx=12;step=1e-6
lo=th.copy();hi=th.copy();lo[idx]-=step;hi[idx]+=step
ng=(mod.lossgrad(hi,y,False)[0]-mod.lossgrad(lo,y,False)[0])/(2*step)
res['clipping_gradient_counterexample']={'parameter_index':idx,'analytic_gradient':float(g[idx]),'numerical_gradient':float(ng),'clipped_cells':int((mod.decode(th,False)[0]<=1e-12).sum())}
(ROOT/'COUNT_MODEL_AUDIT.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
