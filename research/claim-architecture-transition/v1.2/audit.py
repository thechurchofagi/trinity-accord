#!/usr/bin/env python3
"""Deterministic design checks for TA-TR-2026-14 v1.2, not empirical data.
Run: python3 audit.py --out DIRECTORY
Only the Python standard library is required. Analytical proofs are in the paper.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform

COUNTS: dict[str, int] = {}
MAX_ERROR: dict[str, float] = {}

def require(group: str, condition: bool, detail: str = '') -> None:
    COUNTS[group] = COUNTS.get(group, 0) + 1
    if not condition:
        raise AssertionError(group + ': ' + detail)

def close(group: str, actual: float, expected: float, tol: float = 2e-10) -> None:
    err = abs(actual - expected) / max(1.0, abs(actual), abs(expected))
    MAX_ERROR[group] = max(MAX_ERROR.get(group, 0.0), err)
    require(group, math.isfinite(err) and err < tol, repr((actual, expected, err, tol)))

def produced(A, L=1.0, K=1.0, R=1.0, beta=0.2, sigma=2.0, theta=0.5, Z=1.0):
    rho = (sigma - 1.0) / sigma
    X = (theta * L**rho + (1.0-theta) * (A*K)**rho)**(1.0/rho)
    return Z * R**beta * X**(1.0-beta)

def factors(A: float, beta=0.2, sigma=2.0, theta=0.5, L=1.0, K=1.0, R=1.0):
    rho = (sigma - 1.0) / sigma
    S = theta*L**rho + (1.0-theta)*(A*K)**rho
    X = S**(1.0/rho)
    y = R**beta * X**(1.0-beta)
    w = (1.0-beta)*R**beta*theta*L**(rho-1.0)*X**(1.0-rho-beta)
    rK = (1.0-beta)*R**beta*(1.0-theta)*A**rho*K**(rho-1.0)*X**(1.0-rho-beta)
    rR = beta*y/R
    return y, w, rK, rR, w*L/y

def root(f, lo: float, hi: float) -> float:
    fl, fh = f(lo), f(hi)
    if fl == 0: return lo
    if fh == 0: return hi
    if fl*fh > 0: raise ValueError('Root is not bracketed')
    for _ in range(110):
        mid = (lo+hi)/2.0
        fm = f(mid)
        if fm == 0: return mid
        if fl*fm <= 0: hi = mid
        else: lo, fl = mid, fm
    return (lo+hi)/2.0

def price_ratio(s: float, a: float, b: float, tau: float) -> float:
    k = b + tau*(a-b)
    return (k+(a-b)*(1.0-tau)*s)/(1.0-k)

def incomes(r: float, s: float, tau: float):
    # y=H=1 normalization. Specify ownership and budgets before clearing markets.
    W = s
    C = 1.0-W+r
    return W+tau*C, (1.0-tau)*C, C

def solved_ratio(s: float, a: float, b: float, tau: float) -> float:
    # Numerically solve household demand = service supply; do not reuse (11).
    def excess(r):
        IW, IO, _ = incomes(r, s, tau)
        return a*IW/r + b*IO/r - 1.0
    return root(excess, 1e-12, 1e8)

def service_share(s: float, a: float, b: float, tau: float, independent=False):
    r = solved_ratio(s,a,b,tau) if independent else price_ratio(s,a,b,tau)
    IW, IO, _ = incomes(r,s,tau)
    return a*IW/r

def minimum_tax(s: float, a: float, b: float, eta: float):
    if not (0 <= s < 1 and 0 < a < 1 and 0 < b < 1 and 0 < eta < 1):
        raise ValueError('Parameters outside the stated support domain')
    D = a*(1.0-eta)+b*eta
    return max(0.0, (eta*b-s*(D-a*b))/(D-s*(D-a*b)))

def run(out: Path) -> dict:
    # Production derivatives from a complex perturbation independently of (4).
    for beta,sigma,theta,A in itertools.product((.1,.35,.7),(1.2,2.,5.),(.2,.5,.8),(1.,10.,1000.)):
        L,K,R = 1.3,.8,1.1
        y,w,rK,rR,s = factors(A,beta,sigma,theta,L,K,R)
        h = 1e-20
        for name,x,wanted in (('L',L,w),('K',K,rK),('R',R,rR)):
            kw = dict(A=A,L=L,K=K,R=R,beta=beta,sigma=sigma,theta=theta)
            kw[name] = x+1j*h
            close('complex_step_factor_derivatives', produced(**kw).imag/h,wanted,2e-9)
        close('factor_exhaustion', w*L+rK*K+rR*R,y)
        rho=(sigma-1)/sigma
        z=(1-theta)*(A*K)**rho/(theta*L**rho+(1-theta)*(A*K)**rho)
        eps=1e-4
        wp=factors(A*math.exp(eps),beta,sigma,theta,L,K,R)[1]
        wm=factors(A*math.exp(-eps),beta,sigma,theta,L,K,R)[1]
        close('finite_log_wage_derivative',(math.log(wp)-math.log(wm))/(2*eps),(1/sigma-beta)*z,2e-8)
        require('positive_factors',min(y,w,rK,rR,s)>0 and s<1)

    for s,a,b,tau in itertools.product((.01,.15,.45,.8),(.15,.35,.65,.85),(.2,.55,.8),(0.,.1,.4,.8,.98)):
        r=price_ratio(s,a,b,tau)
        rn=solved_ratio(s,a,b,tau)
        close('independent_market_root',r,rn,2e-9)
        IW,IO,C=incomes(rn,s,tau)
        close('service_market',a*IW/rn+b*IO/rn,1.0)
        close('produced_market',(1-a)*IW+(1-b)*IO,1.0)
        close('household_aggregate_budget',IW+IO,1+rn)
        close('balanced_fiscal_budget',IW-s,tau*C)
        require('interior_consumption',min(IW,IO,rn)>0)
        t=(tau+(1-tau)*s*(1-b))/(1+(1-tau)*s*(a-b))
        close('disposable_share',IW/(1+rn),t)
        close('physical_share',a*IW/rn,a*t/(b+(a-b)*t))
        # Coverage is invariant to a change of monetary unit.
        q,bx,hbar=.7,.2,.4
        coverage=(IW/q)/(bx+rn*hbar)
        close('numeraire_invariance',coverage,(19*IW/q)/(19*bx+19*rn*hbar))
        e=1e-5
        if e<tau<1-e:
            slope=(price_ratio(s,a,b,tau+e)-price_ratio(s,a,b,tau-e))/(2*e)
            expected=(a-b)*(1-s*(1-a))/(1-(b+tau*(a-b)))**2
            close('endogenous_price_derivative',slope,expected,1e-7)

    for s,a,b,eta in itertools.product((.005,.1,.4,.8),(.15,.35,.7),(.2,.55,.8),(.05,.28,.6,.95)):
        tau=minimum_tax(s,a,b,eta)
        f=service_share(s,a,b,tau,independent=True)
        require('feasible_minimum',0<=tau<1 and f>=eta-2e-9)
        if tau>1e-8:
            close('threshold_attainment',f,eta,2e-9)
            below=max(0,tau-1e-6)
            require('strict_minimality',service_share(s,a,b,below,True)<eta)
            tnum=root(lambda t:service_share(s,a,b,t,True)-eta,0,1-1e-12)
            close('independent_policy_root',tau,tnum,2e-9)
        else:
            require('untaxed_sufficiency',service_share(s,a,b,0,True)>=eta-2e-9)
        for cap in (.1,.4,.8):
            attainable=service_share(s,a,b,cap,True)>=eta-1e-10
            require('policy_capacity_frontier',attainable==(tau<=cap+1e-10))
        require('physical_ceiling',service_share(s,a,b,.999999,True)<1.0)
        etaO=.1
        cap=.6
        low=max(service_share(s,a,b,0),eta)
        high=min(service_share(s,a,b,cap),1-etaO)
        feasible=low<=high+1e-12
        # A feasible witness must obey both floors; an empty interval has none.
        if feasible:
            tw=tau
            fw=service_share(s,a,b,tw)
            require('both_group_floors',eta-1e-10<=fw<=1-etaO+1e-10 and tw<=cap+1e-10)
        else:
            require('both_group_infeasibility',service_share(s,a,b,cap)<eta or service_share(s,a,b,0)>1-etaO or eta>1-etaO)

    # A fixed basket can be affordable while chosen service misses its floor.
    s,a,b,q,bx,hbar=.001,.35,.55,.7,.2,.4
    y,H=1000.,1.
    eta=q*hbar/H
    def basket_gap(tau):
        r=price_ratio(s,a,b,tau)
        IW,_,_=incomes(r,s,tau)
        return y*IW/q-(bx+y*r/H*hbar)
    tb=root(basket_gap,0.,.9999)
    r=price_ratio(s,a,b,tb)
    IW,_,_=incomes(r,s,tb)
    chosen=a*y*IW/(q*y*r/H)
    close('basket_boundary_identity',chosen,a*(bx/(y*r/H)+hbar))
    require('basket_not_allocation',chosen<hbar and tb<minimum_tax(s,a,b,eta))
    tinf=eta*b/(a*(1-eta)+eta*b)
    tbinf=eta*b/(1-eta*(a-b))
    close('illustrative_service_limit',tinf,.3793103448275862)
    close('illustrative_basket_limit',tbinf,.14583333333333334)
    require('different_criteria',tbinf<tinf and 1/2-.2-.35*(1-.2)>0)

    for a,b,eta in itertools.product((.15,.35,.7),(.2,.55,.8),(.05,.28,.6,.95)):
        lim=eta*b/(a*(1-eta)+eta*b)
        close('support_limit',minimum_tax(1e-10,a,b,eta),lim,2e-9)
        expected=eta*.8/(.15*(1-eta)+eta*.8)
        require('interval_sensitivity_bound',lim<=expected+1e-12)
    for A in (1e2,1e4,1e6):
        y=(1+A)**.65
        w=.65*(1+A)**(-.35)
        q=.7
        GS=q*max(.4-w,0)
        outside=max((1-q)*y*y-(y-q*w),0)
        require('subset_gap_bound',GS<=q*.4)
        require('whole_gap_counterexample',(GS+outside)/y>1)
    for j in range(1,6):
        logA=2*j*math.pi+math.pi/2
        require('unit_limit_can_exceed',1+math.sin(logA)/logA>1)
        logA=2*j*math.pi+3*math.pi/2
        require('unit_limit_can_fail',1+math.sin(logA)/logA<1)

    rows=[]
    for A in (1.,100.,1e4,1e8,1e16):
        y,w,_,_,s=factors(A)
        a,b,q,H,eta=.35,.55,.7,1.,.28
        tau=minimum_tax(s,a,b,eta)
        p0=y*price_ratio(s,a,b,0)/H
        rows.append(dict(A=A,y=y,w=w,s=s,p_untaxed=p0,
                         worker_service_untaxed=H/q*service_share(s,a,b,0),
                         minimum_service_tax=tau,
                         worker_service_at_minimum=H/q*service_share(s,a,b,tau)))
    require('rising_wage_falling_service',rows[-1]['w']>rows[0]['w'] and rows[-1]['worker_service_untaxed']<rows[0]['worker_service_untaxed'])
    out.mkdir(parents=True,exist_ok=True)
    with (out/'illustration.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    report=dict(status='PASS',report='TA-TR-2026-14',version='1.2',
                kind='deterministic_internal_design_checks_not_empirical_validation',
                python=platform.python_version(),assertions=sum(COUNTS.values()),
                groups=COUNTS,max_scaled_error=MAX_ERROR,
                default_scaled_tolerance=2e-10,largest_special_tolerance=1e-7,
                audit_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                independent_external_replication=False,formal_proof_certification=False,
                illustrative_limiting_service_tax=tinf,illustrative_limiting_basket_tax=tbinf)
    (out/'checks.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path('audit-output'))
    args=parser.parse_args()
    print(json.dumps(run(args.out),indent=2,sort_keys=True))
