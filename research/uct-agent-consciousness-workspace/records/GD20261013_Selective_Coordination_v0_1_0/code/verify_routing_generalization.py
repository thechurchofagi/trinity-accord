#!/usr/bin/env python3
"""General reflected-module copying: fresh source response and killing limit.
All state models are finite, explicit, and noisy. No consciousness labels.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import numpy as np
from scipy.linalg import expm
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_gradual_differentiation import generator,float_matrix,assert_close


def laplacian(n,edges):
    L=np.zeros((n,n))
    for i,j,w in edges:
        L[i,i]+=w;L[j,j]+=w;L[i,j]-=w;L[j,i]-=w
    return L


def main(out):
    out.mkdir(parents=True,exist_ok=True)
    n=3;edges=[(0,1,.1),(1,2,.2)];L=laplacian(n,edges)
    counts={};maxerr=0.;cases=0
    # Full 64-state evolution versus n-state reduction: actual freshly written source.
    for mu,gvec,t in product([.02,.1],[(0,0,0),(.2,0,0),(1,0,0),(.3,.3,.3),(1,.05,.1)], [.25,1.,5.]):
        full_edges=[(i,j,F(str(w))) for i,j,w in edges]+[(i+n,j+n,F(str(w))) for i,j,w in edges]
        full_edges += [(i,i+n,F(str(gvec[i]))) for i in range(n)]
        xs,q=generator(2*n,F(str(mu)),full_edges)
        p=expm(float_matrix(q)*t)
        initial=tuple([1]*n+[-1]*n);k=xs.index(initial)
        spin=np.array(xs)
        actual=p[k]@spin[:,:n]
        B=2*mu*np.eye(n)+L+2*np.diag(gvec)
        predicted=expm(-B*t)@np.ones(n)
        maxerr=max(maxerr,assert_close(actual,predicted))
        # Common message: all + vs all -; mean readback doesn't depend on routing.
        same=xs.index(tuple([1]*(2*n)))
        maxerr=max(maxerr,assert_close(p[same]@spin[:,:n],np.exp(-2*mu*t)*np.ones(n)))
        bound=np.exp(-(2*mu+np.diag(L)+2*np.array(gvec))*t)
        assert np.all(predicted>=bound-1e-12)
        cases+=1
    counts['full_64_state_models_and_time_windows']=cases
    counts['source_and_common_mean_checks']=cases*n*2
    # Large growth limit: NOT recomputing boundary degrees after cutting links.
    tests=[];mu=.02;t=5.
    for avec,bvec in [([1,0,0],[0,0,0]),([1,1,0],[0,.01,.02]),([1,1,1],[0,0,0])]:
        a=np.array(avec);b=np.array(bvec);Z=np.where(a==0)[0]
        target=np.zeros(n)
        if len(Z):
            Bz=2*mu*np.eye(len(Z))+L[np.ix_(Z,Z)]+2*np.diag(b[Z])
            target[Z]=expm(-Bz*t)@np.ones(len(Z))
        errors=[]
        for G in (1.,10.,100.,1000.,10000.):
            d=expm(-(2*mu*np.eye(n)+L+2*np.diag(G*a+b))*t)@np.ones(n)
            error=float(np.max(np.abs(d-target)));errors.append(error)
        assert errors[-1]<1e-4
        tests.append({'a':avec,'b':bvec,'target':target.tolist(),'errors':errors})
    counts['killing_limit_families']=len(tests)
    counts['killing_limit_parameter_points']=15
    # Incorrect boundary renormalization: explicitly keep as a counterexample.
    Z=np.array([1,2])
    # Induced graph Laplacian would discard the hazard of leaving through node 0.
    Linduced=laplacian(2,[(0,1,.2)])
    vproper=expm(-(2*mu*np.eye(2)+L[np.ix_(Z,Z)])*5)@np.ones(2)
    vwrong=expm(-(2*mu*np.eye(2)+Linduced)*5)@np.ones(2)
    assert np.max(vwrong-vproper)>.1
    result={'study':'UCT-GD-20261013-GENERAL-v0.1.0','counts':counts,
            'max_full_state_reduction_error':maxerr,'killing_limits':tests,
            'boundary_deletion_counterexample':{'correct_limit':vproper.tolist(),'incorrect_reflecting_boundary':vwrong.tolist()},
            'claims':'Classical generator/ancestry machinery; conditional routing application. No empirical evolutionary or phenomenal inference.'}
    (out/'ROUTING_GENERALIZATION_RESULTS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'results')
    main(ap.parse_args().out)
