#!/usr/bin/env python3
"""R92: fixed-protocol tiny recurrent learning; NumPy float64, no API models."""
from pathlib import Path
from itertools import product
import csv,json,hashlib,platform
import numpy as np

ROOT=Path(__file__).resolve().parent
SNAPS={0,10,50,100,250,500,1000,2000,3000}
TRAIN=np.array(list(product([-1.,-.5,0.,.5,1.],repeat=2)))
TEST=np.array(list(product(np.arange(-.875,1.,.25),repeat=2)))
CONTEXTS=np.array(list(product([-.75,0.,.75],repeat=2)))

def initialize(d,seed):
    r=np.random.default_rng(seed)
    return {'E':.3*r.standard_normal((d,2)), 'A':.9*np.eye(d)+.05*r.standard_normal((d,d)), 'B':.3*r.standard_normal((2,d))}

def phi(a,kind):
    return a if kind=='linear' else np.tanh(a)

def forward(p,x,kind,cut=None):
    states=[phi(x@p['E'].T,kind)]
    for t in range(1,4):
        h=phi(states[-1]@p['A'].T,kind)
        if t==1 and cut is not None:
            h=h.copy()
            if cut=='all': h[:]=0
            elif cut!='restore': h[:,cut]=0
        states.append(h)
    return states[-1]@p['B'].T,states

def loss_grad(p,kind):
    y,hs=forward(p,TRAIN,kind)
    error=y-TRAIN
    loss=np.mean(error**2)
    dy=2*error/error.size
    g={'B':dy.T@hs[-1],'A':np.zeros_like(p['A'])}
    dh=dy@p['B']
    for t in range(3,0,-1):
        dp=dh if kind=='linear' else dh*(1-hs[t]**2)
        g['A']+=dp.T@hs[t-1]
        dh=dp@p['A']
    dp=dh if kind=='linear' else dh*(1-hs[0]**2)
    g['E']=dp.T@TRAIN
    return float(loss),g

def jacobian(p,x,kind,cut=None):
    h=phi(p['E']@x,kind)
    j=p['E'].copy() if kind=='linear' else (1-h*h)[:,None]*p['E']
    for t in range(1,4):
        h=phi(p['A']@h,kind)
        j=p['A']@j
        if kind!='linear':j=(1-h*h)[:,None]*j
        if t==1 and cut is not None and cut!='restore':
            h=h.copy();j=j.copy()
            if cut=='all': h[:]=0;j[:]=0
            else:h[cut]=0;j[cut]=0
    return p['B']@j

def metrics(p,kind,x=TEST,cut=None,detail=False):
    y,hs=forward(p,x,kind,cut)
    js=np.array([jacobian(p,c,kind,cut) for c in CONTEXTS])
    sv=np.linalg.svd(js,compute_uv=False)
    errors=np.array([np.linalg.norm(j-np.eye(2),ord=2) for j in js])
    out={'normalized_error':float(np.mean((y-x)**2)/np.mean(x*x)), 'max_jacobian_identity_error':float(errors.max()),'minimum_sigma_min':float(sv[:,-1].min()),'jacobian_ranks':[int(np.linalg.matrix_rank(j,tol=1e-9)) for j in js]}
    out['task_pass']=out['normalized_error']<.01
    out['local_certificate_pass']=out['max_jacobian_identity_error']<.2
    if detail:out.update(outputs=y.tolist(),states=[h.tolist() for h in hs],jacobians=js.tolist(),singular_values=sv.tolist(),jacobian_errors=errors.tolist())
    return out

def arrays(d):return {k:v.tolist() for k,v in d.items()}

def gradient_check():
    rows=[]
    for kind,d in product(('linear','tanh'),(1,2)):
        p=initialize(d,0);_,g=loss_grad(p,kind)
        for key in p:
            for idx in np.ndindex(p[key].shape):
                original=p[key][idx]
                p[key][idx]=original+1e-6; lp=loss_grad(p,kind)[0]
                p[key][idx]=original-1e-6; lm=loss_grad(p,kind)[0]
                p[key][idx]=original
                fd=(lp-lm)/2e-6
                rows.append({'activation':kind,'d':d,'parameter':key,'index':idx,'analytic':float(g[key][idx]),'finite_difference':fd,'abs_error':abs(fd-g[key][idx])})
    (ROOT/'R92_Gradient_Check.json').write_text(json.dumps(rows,indent=2))
    assert max(r['abs_error'] for r in rows)<1e-6
    return float(max(r['abs_error'] for r in rows))

def main():
    meta={'numpy':np.__version__,'python':platform.python_version(),'dtype':'float64','protocol_sha256':hashlib.sha256((ROOT/'R92_Delayed_Retention_Protocol_Frozen_20261006.md').read_bytes()).hexdigest(),'train':TRAIN.tolist(),'test':TEST.tolist(),'contexts':CONTEXTS.tolist(),'gradient_max_error':gradient_check()}
    (ROOT/'R92_Data_and_Environment.json').write_text(json.dumps(meta,indent=2))
    archive=ROOT/'R92_runs';archive.mkdir(exist_ok=True)
    summaries=[]
    with (ROOT/'R92_All_Training_Losses.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['run','step','training_mse_before_update'])
        for kind,d,mode,seed in product(('linear','tanh'),(1,2),('full','readout'),range(4)):
            name=f'{kind}_d{d}_{mode}_s{seed}'
            p=initialize(d,seed); initial={k:v.copy() for k,v in p.items()}
            m={k:np.zeros_like(v) for k,v in p.items()};v={k:np.zeros_like(a) for k,a in p.items()}
            snaps=[];failure=None
            initial_metrics=metrics(p,kind,detail=True)
            clipped=0
            for step in range(3001):
                if step in SNAPS:
                    snaps.append({'step':step,'parameters':arrays(p),'adam_m':arrays(m),'adam_v':arrays(v),'metrics':metrics(p,kind)})
                if step==3000:break
                loss,g=loss_grad(p,kind)
                writer.writerow([name,step,loss])
                active=('E','A','B') if mode=='full' else ('B',)
                norm=float(np.sqrt(sum(np.sum(g[k]**2) for k in active)))
                if not np.isfinite(loss+norm):failure={'step':step,'reason':'nonfinite loss or gradient'};break
                scale=min(1.,10./max(norm,1e-300));clipped+=int(scale<1)
                for k in active:
                    gg=g[k]*scale;m[k]=.9*m[k]+.1*gg;v[k]=.999*v[k]+.001*gg*gg
                    mh=m[k]/(1-.9**(step+1));vh=v[k]/(1-.999**(step+1))
                    p[k]-=.01*mh/(np.sqrt(vh)+1e-8)
            final=metrics(p,kind,detail=True)
            interventions={str(c):metrics(p,kind,cut=c,detail=True) for c in ['all','restore',*range(d)]}
            fd_err=0.
            for c,j in zip(CONTEXTS,np.array(final['jacobians'])):
                cols=[]
                for k in range(2):
                    delta=np.eye(2)[k]*1e-6
                    yp=forward(p,(c+delta)[None,:],kind)[0][0]
                    ym=forward(p,(c-delta)[None,:],kind)[0][0]
                    cols.append((yp-ym)/2e-6)
                fd_err=max(fd_err,float(np.max(np.abs(np.array(cols).T-j))))
            pzero={**p,'B':np.zeros_like(p['B'])}
            zero_y,zero_h=forward(pzero,TEST,kind)
            _,original_h=forward(p,TEST,kind)
            checks={'jacobian_finite_difference_max_error':fd_err,'reset_all_output_max':float(np.max(np.abs(interventions['all']['outputs']))),'restore_max_error':float(np.max(np.abs(np.array(interventions['restore']['outputs'])-np.array(final['outputs'])))),'readout_disconnection_hidden_change':float(max(np.max(np.abs(a-b)) for a,b in zip(zero_h,original_h))),'readout_disconnection_output_max':float(np.max(np.abs(zero_y))),'E_change_norm':float(np.linalg.norm(p['E']-initial['E'])),'A_change_norm':float(np.linalg.norm(p['A']-initial['A'])),'B_change_norm':float(np.linalg.norm(p['B']-initial['B']))}
            if fd_err>=1e-6:failure={'reason':'jacobian validation failed','error':fd_err}
            record={'run':name,'activation':kind,'d':d,'mode':mode,'seed':seed,'weight_count':4*d+d*d,'failure':failure,'gradient_clips':clipped,'initial':initial_metrics,'checkpoints':snaps,'final':final,'interventions':interventions,'checks':checks}
            (archive/(name+'.json')).write_text(json.dumps(record,separators=(',',':'))+'\n')
            summary={'run':name,'activation':kind,'d':d,'mode':mode,'seed':seed,'initial_N':initial_metrics['normalized_error'],'final_N':final['normalized_error'],'max_J_error':final['max_jacobian_identity_error'],'min_sigma':final['minimum_sigma_min'],'task_pass':final['task_pass'],'local_pass':final['local_certificate_pass'],'initial_rank_min':min(initial_metrics['jacobian_ranks']),'final_rank_min':min(final['jacobian_ranks']),'failure':failure,**checks}
            summaries.append(summary)
            print(name, 'N=',f"{summary['final_N']:.8g}",'Jerr=',f"{summary['max_J_error']:.6g}",'both=',summary['task_pass'] and summary['local_pass'],flush=True)
    with (ROOT/'R92_Summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=summaries[0]);w.writeheader();w.writerows(summaries)
    checks={'all_32_runs_completed':len(summaries)==32 and all(s['failure'] is None for s in summaries),'all_one_state_obey_half_error_bound':all(s['final_N']>=.5-1e-10 for s in summaries if s['d']==1),'all_jacobians_validated':all(s['jacobian_finite_difference_max_error']<1e-6 for s in summaries),'all_complete_state_resets_zero_output':all(s['reset_all_output_max']==0 for s in summaries),'all_restorations_exact':all(s['restore_max_error']==0 for s in summaries),'all_disconnected_readouts_preserve_hidden':all(s['readout_disconnection_hidden_change']==0 for s in summaries),'all_readout_only_hidden_weights_unchanged':all(s['E_change_norm']==s['A_change_norm']==0 for s in summaries if s['mode']=='readout')}
    (ROOT/'R92_Results.json').write_text(json.dumps({'checks':checks,'runs':summaries,'scope':'actual tiny-network training on synthetic grids, no subjective measurement'},indent=2)+'\n')
    print(json.dumps(checks,indent=2))
    assert all(checks.values())

if __name__=='__main__': main()
