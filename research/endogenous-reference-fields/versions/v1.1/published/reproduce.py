#!/usr/bin/env python3
"""Reproduce all nine runs without overwriting the deposited raw results."""
import argparse, hashlib, json, math, os, platform, subprocess, sys
from pathlib import Path
import numpy as np
from train import train, sample, forward, unpack, NP
from measure import measure

SOURCE=Path(__file__).resolve().parent

def compare(a,b,path=''):
    rows=[]
    if isinstance(a,dict):
        if a.keys()!=b.keys():raise ValueError('field mismatch: '+path)
        for k in a:rows.extend(compare(a[k],b[k],path+'/'+k))
    elif isinstance(a,list):
        if len(a)!=len(b):raise ValueError('length mismatch: '+path)
        for i,(x,y) in enumerate(zip(a,b)):rows.extend(compare(x,y,path+'/'+str(i)))
    elif isinstance(a,(int,float)):
        rows.append({'field':path,'original':a,'rerun':b,'absolute_error':abs(a-b),'pass':math.isclose(a,b,rel_tol=1e-7,abs_tol=1e-10)})
    elif a!=b:raise ValueError('identity mismatch: '+path)
    return rows

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',type=Path,default=Path('rerun'))
    parser.add_argument('--reuse-weights',type=Path,help='Use deposited weights for a measurement-only check')
    args=parser.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    if out==SOURCE:raise ValueError('Use a separate output directory')
    weights=args.reuse_weights.resolve() if args.reuse_weights else None
    os.chdir(out);results=[];diagnostics=[]
    for task in ('T1','T2','T3'):
        for seed in (0,1,2):
            name=f'th_{task}_{seed}.npy'
            th=np.load(weights/name) if weights else train(task,seed)
            np.save(name,th)
            u,y=sample(task,np.random.default_rng(999),2000);lg,_=forward(th,u)
            row={'task':task,'seed':seed,'test_accuracy':float(np.mean((lg>0)==(y>0.5)))}
            p,a1,B,w,V,Bt,b=unpack(th)
            u,_=sample(task,np.random.default_rng(123),1000);u[:,5:26,2]=0
            if task=='T3':u[:,6:,3]=u[:,5:6,3]
            ua=u.copy();ua[:,0,3]*=-1
            if task=='T3':ua[:,:,3]*=-1;ua[:,0,3]=-u[:,0,3]
            _,H=forward(th,u);_,Ha=forward(th,ua);norm=np.linalg.norm(Ha[:,5]-H[:,5],axis=1)
            row.update({'A_noswitch_full':np.tanh(p).tolist(),'A_switch_full':(np.tanh(p)+a1).tolist(),'B_full':B.tolist(),'V_full':V.tolist(),'initial_state_difference_norm':{'min':float(norm.min()),'median':float(np.median(norm)),'max':float(norm.max())}})
            effects=[]
            for t in (5,10,15,20):
                effect={'index':t}
                for k in (0,1):
                    d=-2*u[:,t,k,None]*B[:,k][None,:]
                    effect[f'ch{k+1}_absolute']=float(np.mean(np.linalg.norm(d,axis=1)))
                    effect[f'ch{k+1}_relative']=float(np.mean(np.linalg.norm(d,axis=1)/(np.linalg.norm(H[:,t],axis=1)+1e-12)))
                effects.append(effect)
            row['posthoc_content_update_diagnostics']=effects
            results.append(measure(task,seed));diagnostics.append(row)
            print(task,seed,'accuracy',row['test_accuracy'],flush=True)
    results=json.loads(json.dumps(results))
    raw=(SOURCE/'results.json').read_bytes();fields=compare(json.loads(raw),results)
    passed=all(x['pass'] for x in fields)
    report={'state':'COMPUTATIONAL_REPRODUCTION_PASS' if passed else 'RESULT_MISMATCH','mode':'measurement-only from deposited weights' if weights else 'full retraining','python':platform.python_version(),'numpy':np.__version__,'platform':platform.platform(),'parameter_count':NP,'train_seeds':[0,1,2],'test_seed':999,'probe_seed':123,'train_steps':1200,'test_sequences':2000,'probe_sequences':1000,'numeric_field_count':len(fields),'exact_numeric_equality':all(x['absolute_error']==0 for x in fields),'rtol':1e-7,'atol':1e-10,'tolerance_role':'portability check only, never consciousness classification','raw_sha256':hashlib.sha256(raw).hexdigest(),'all_nine_test_accuracies':[x['test_accuracy'] for x in diagnostics],'fields':fields}
    (out/'results-rerun.json').write_text(json.dumps(results,ensure_ascii=False,indent=1))
    (out/'reproduction.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (out/'diagnostics.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
    with (out/'verification.log').open('w') as log:
        subprocess.run([sys.executable,str(SOURCE/'erf_verification.py')],stdout=log,check=True)
    if not passed:raise SystemExit('Numerical mismatch: inspect reproduction.json')
    print(report['state'],'exact=',report['exact_numeric_equality'])

if __name__=='__main__':main()
