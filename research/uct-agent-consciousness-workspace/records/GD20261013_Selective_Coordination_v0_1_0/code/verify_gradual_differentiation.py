#!/usr/bin/env python3
"""Finite-rate copying models: exact generator checks and numerical readback.

This is a structural pressure test, not a consciousness test or a simulated
biological evolutionary history. All inputs are explicit. No data are fetched.
Requires Python 3.10+, NumPy, SciPy. Run from anywhere with --out DIR.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import csv, hashlib, json, math, platform
import numpy as np
import scipy
from scipy.linalg import expm


def states(n: int):
    return list(product((-1, 1), repeat=n))


def generator(n: int, mu: F, edges: list[tuple[int, int, F]]):
    """Each spin flips at mu, copies each neighbor at undirected edge rate w."""
    if mu <= 0 or any(w < 0 or i == j or not (0<=i<n and 0<=j<n) for i,j,w in edges):
        raise ValueError('Positive flip noise and valid nonnegative edge rates required')
    xs = states(n); idx = {x: k for k, x in enumerate(xs)}
    q = [[F(0) for _ in xs] for _ in xs]
    for k, x in enumerate(xs):
        for i in range(n):
            y = list(x); y[i] *= -1
            q[k][idx[tuple(y)]] += mu
        for i, j, w in edges:
            if x[i] != x[j]:
                for target, source in ((i,j),(j,i)):
                    y=list(x); y[target]=x[source]
                    q[k][idx[tuple(y)]] += w
        q[k][k] = -sum(q[k])
    return xs,q


def apply(q, values):
    return [sum(x*y for x,y in zip(row,values)) for row in q]


def float_matrix(q):
    return np.array([[float(x) for x in row] for row in q])


def assert_close(a,b,tol=3e-11):
    err=float(np.max(np.abs(np.asarray(a)-np.asarray(b))))
    if not math.isfinite(err) or err>tol:
        raise AssertionError((err,tol,a,b))
    return err


def stationary(q):
    n=q.shape[0]; m=q.T.copy(); m[-1,:]=1
    b=np.zeros(n);b[-1]=1
    return np.linalg.solve(m,b)


def uniformization(q,t,tol=1e-14):
    """Independent Poisson expansion, nonnegative matrices; <=tol tail mass."""
    r=max(-np.diag(q))
    if r==0 or t==0: return np.eye(q.shape[0]),0.0
    z=r*t
    if z>650: raise ValueError('Scale problem before using this verification route')
    p=np.eye(q.shape[0])+q/r
    term=np.eye(q.shape[0]);w=math.exp(-z); out=w*term; mass=w
    k=0
    while k < max(100,int(2*z+50)) or 1-mass>tol:
        k+=1;term=term@p;w*=z/k;out+=w*term;mass+=w
        # For large k roundoff in the tail mass must not cause an infinite loop.
        if k>z and w < tol*0.01: break
        if k>5000: raise RuntimeError('Uniformization failed to converge')
    return out,max(0.0,1-mass)


def formula(mu,lam,g,h,t):
    """Difference response on internal node v1 for initial means (0,1,0,-1)."""
    b=2*mu+lam+g+h; d=g-h; z=math.hypot(d,lam)
    if z==0:return math.exp(-b*t)
    # Stable spectral expression, avoiding overflow of cosh.
    return .5*(1+d/z)*math.exp(-(b-z)*t)+.5*(1-d/z)*math.exp(-(b+z)*t)


def common(mu,lam,t):
    return .5*(math.exp(-2*mu*t)+math.exp(-(2*mu+2*lam)*t))


def prep4(xs, r: int, opposite: bool):
    if r not in (-1,1): raise ValueError('r must be a sign')
    return np.array([.25 if (x[1]==r and x[3]==(-r if opposite else r)) else 0 for x in xs])


def main(out: Path):
    out.mkdir(parents=True,exist_ok=True)
    counts={}; maxerr=0.;maxtail=0.
    # 1. Exact generator identities for every state, not sampled trajectories.
    mvals=[F(1,50),F(1,10),F(1,2)]
    rvals=[F(0),F(1,20),F(1,5),F(1),F(3)]
    pairs=0; equations=0
    for mu,g in product(mvals,rvals):
        xs,q=generator(2,mu,[(0,1,g)])
        sx=[F(x[0]) for x in xs]; sy=[F(x[1]) for x in xs]
        sr=[F(x[0]*x[1]) for x in xs]
        assert apply(q,sx)==[-(2*mu+g)*x+g*y for x,y in zip(sx,sy)]
        assert apply(q,sy)==[g*x-(2*mu+g)*y for x,y in zip(sx,sy)]
        assert apply(q,sr)==[2*g-(4*mu+2*g)*r for r in sr]
        c=g/(2*mu+g)
        pi=[(1+c*r)/4 for r in sr]
        assert all(sum(pi[i]*q[i][j] for i in range(4))==0 for j in range(4))
        pairs+=1;equations+=16
    counts['two_node_exact_parameter_cases']=pairs
    counts['two_node_exact_state_equations']=equations
    cases=0;eqs=0
    for mu,lam,g,h in product(mvals,[F(1,20),F(1,5),F(1)],rvals,rvals):
        xs,q=generator(4,mu,[(0,1,lam),(2,3,lam),(0,2,g),(1,3,h)])
        for i in range(4):
            v=[F(x[i]) for x in xs]
            pred=[]
            for x in xs:
                d=-2*mu*x[i]
                for a,b,w in [(0,1,lam),(2,3,lam),(0,2,g),(1,3,h)]:
                    if i==a:d+=w*(x[b]-x[a])
                    if i==b:d+=w*(x[a]-x[b])
                pred.append(d)
            assert apply(q,v)==pred
            eqs+=len(xs)
        assert all(sum(row)==0 for row in q)
        cases+=1
    counts['four_node_exact_parameter_cases']=cases
    counts['four_node_exact_state_equations']=eqs
    # 2. Full law propagation independently versus closed formula and Poisson method.
    numerical=0;readouts=0
    for mu,lam,g,h,t in product([.02,.2],[.1,.6],[0.,.1,1.,3.],[0.,.05,.4],[.25,1.,5.]):
        xs,q0=generator(4,F(str(mu)),[(0,1,F(str(lam))),(2,3,F(str(lam))),
                                     (0,2,F(str(g))),(1,3,F(str(h)))])
        q=float_matrix(q0); p=expm(q*t)
        p2,tail=uniformization(q,t)
        maxerr=max(maxerr,assert_close(p,p2));maxtail=max(maxtail,tail)
        maxerr=max(maxerr,assert_close(p.sum(axis=1),np.ones(16)))
        if p.min() < -1e-13:raise AssertionError('Negative transition probability')
        internal=np.array([x[1] for x in xs]); public=np.array([x[0] for x in xs])
        d=formula(mu,lam,g,h,t)
        c=common(mu,lam,t)
        for r in (-1,1):
            po=prep4(xs,r,True)@p; pc=prep4(xs,r,False)@p
            maxerr=max(maxerr,assert_close(po@internal,r*d),assert_close(pc@internal,r*c))
            readouts+=2
        # Fresh opposite preparation, fixed one-register decoder; not full-state optimum.
        pp=prep4(xs,1,True)@p;pm=prep4(xs,-1,True)@p
        success=.5*(pp[internal==1].sum()+pm[internal==-1].sum())
        maxerr=max(maxerr,assert_close(success,(1+d)/2))
        # Leakage bounds require public copying at least internal copying.
        if g>=h:
            lo=math.exp(-(2*mu+lam+2*h)*t); hi=math.exp(-(2*mu+2*h)*t)
            assert lo-1e-12<=d<=hi+1e-12
        numerical+=1
    counts['four_node_full_law_parameter_time_cases']=numerical
    counts['prepared_mean_response_checks']=readouts
    # 3. Two-node full probability discrimination, stationary agreement and relation bit.
    trials=0
    for mu,g,t in product([.02,.1,.5],[0.,.01,.1,1.,5.],[.25,1.,5.,10.]):
        xs,q0=generator(2,F(str(mu)),[(0,1,F(str(g)))])
        q=float_matrix(q0);p=expm(q*t)
        i=xs.index((1,-1));j=xs.index((-1,1))
        tv=.5*np.abs(p[i]-p[j]).sum()
        maxerr=max(maxerr,assert_close(tv,math.exp(-2*(mu+g)*t)))
        i=xs.index((1,1));j=xs.index((-1,-1))
        tv2=.5*np.abs(p[i]-p[j]).sum()
        maxerr=max(maxerr,assert_close(tv2,math.exp(-2*mu*t)))
        pi=stationary(q);r=np.array([x[0]*x[1] for x in xs])
        c=g/(2*mu+g)
        maxerr=max(maxerr,assert_close(pi@r,c))
        cov=np.sum(pi*(r-c)*(p@r-c))
        maxerr=max(maxerr,assert_close(cov/(1-c*c),math.exp(-(4*mu+2*g)*t)))
        trials+=1
    counts['two_node_full_distribution_time_cases']=trials
    # 4. Equal total cross-rate budget: selective versus uniform routing.
    dominance=0
    for mu,lam,budget,t in product([.02,.1,.5],[.05,.2,1.],[.01,.1,.5,1.,5.],[.25,1.,5.]):
        sel=formula(mu,lam,budget,0.,t)
        uni=formula(mu,lam,budget/2,budget/2,t)
        assert sel>uni
        for eta in (.1,.2,.3,.4):
            mid=formula(mu,lam,(1-eta)*budget,eta*budget,t)
            assert sel>mid>uni
        dominance+=1
    counts['equal_budget_order_checks']=dominance
    rows=[]
    mu=.02;lam=.1;t=5.
    for budget in (0.,.1,.25,.5,1.,2.,5.):
        ds=formula(mu,lam,budget,0,t);du=formula(mu,lam,budget/2,budget/2,t)
        rows.append(dict(mu=mu,internal_rate=lam,time=t,total_cross_rate=budget,
                         selective_private_response=ds,uniform_private_response=du,
                         selective_readout_success=(1+ds)/2,uniform_readout_success=(1+du)/2,
                         common_private_response=common(mu,lam,t)))
    with (out/'EQUAL_BUDGET_RESULTS.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    leak=[]
    for g in (1.,10.,100.,1000.):
        leak.append(dict(public_rate=g,bounded_leak=formula(mu,lam,g,.01,t),
                         one_percent_leak=formula(mu,lam,g,.01*g,t),
                         bounded_leak_floor=math.exp(-(2*mu+lam+.02)*t)))
    result={
      'study':'UCT-GD-20261013-v0.1.0','status':'CONDITIONAL_MODELS_NOT_PHENOMENAL_MEASUREMENTS',
      'counts':counts,'max_numerical_absolute_error':maxerr,'max_uniformization_missing_mass':maxtail,
      'equal_budget_example':rows[4],'leakage_examples':leak,
      'methods':['Exact Fraction generator identities','SciPy full transition exponential',
                 'Independent Poisson uniformization','Analytic moment and decoding formulae'],
      'no_human_animal_model_consciousness_or_biological_evolution_experiment':True,
      'standalone_publication_recommended':False,
      'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__}}
    (out/'VERIFICATION_RESULTS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'results')
    args=ap.parse_args();main(args.out)
