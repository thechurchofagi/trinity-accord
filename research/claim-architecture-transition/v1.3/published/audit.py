#!/usr/bin/env python3
"""TA-TR-2026-14 v1.3: deterministic internal checks, not empirical data.
Run: python3 audit.py --out <directory>. Python 3.10+, standard library only.
"""
from __future__ import annotations
import argparse
import csv
from dataclasses import dataclass
from fractions import Fraction
import itertools
import json
import math
from pathlib import Path

COUNT = 0
CATEGORIES: dict[str, int] = {}

def check(condition: bool, category: str, detail: object = '') -> None:
    global COUNT
    COUNT += 1
    CATEGORIES[category] = CATEGORIES.get(category, 0) + 1
    if not condition:
        raise AssertionError(f'{category}: {detail}')

def close(a: float, b: float, category: str, rtol: float = 3e-8, atol: float = 2e-10) -> None:
    check(math.isclose(a, b, rel_tol=rtol, abs_tol=atol), category, (a, b))

@dataclass(frozen=True)
class Demand:
    c: float
    epsilon: float
    bend: float = 0.0

    def __post_init__(self) -> None:
        if self.c <= 0 or self.epsilon <= 0 or self.bend < 0:
            raise ValueError('Positive scale and elasticity; nonnegative bend required')

    def g(self, p: float) -> float:
        return self.c * p**self.epsilon * (1 + self.bend * p/(1+p))

    def elasticity(self, p: float) -> float:
        return self.epsilon + self.bend*p/((1+p)**2*(1+self.bend*p/(1+p)))

def bisect(function, lo: float, hi: float, iterations: int = 160) -> float:
    f0, f1 = function(lo), function(hi)
    if f0 == 0: return lo
    if f1 == 0: return hi
    if f0*f1 >= 0:
        raise ValueError(f'Root not bracketed: {(lo, hi, f0, f1)}')
    for _ in range(iterations):
        mid = (lo+hi)/2
        fm = function(mid)
        if fm == 0: return mid
        if f0*fm < 0:
            hi = mid
        else:
            lo, f0 = mid, fm
    return (lo+hi)/2

def inverse(Y: float, H: float, eta: float, w: Demand, o: Demand):
    if Y <= 0 or H <= 0 or not 0 < eta < 1:
        raise ValueError('Y,H>0 and 0<eta<1 required')
    M = Y/H
    def f(lp):
        p = math.exp(lp)
        return math.log(eta*w.g(p)+(1-eta)*o.g(p))-math.log(M)
    lo,hi=-1.,1.
    while f(lo)>0: lo*=2
    while f(hi)<0: hi*=2
    p=math.exp(bisect(f,lo,hi))
    t=eta*(w.g(p)+p)/(M+p)
    return p,t

def tax_target(Y,H,eta,w,o,s=0.):
    p,t=inverse(Y,H,eta,w,o)
    M=Y/H
    rate=(eta*(w.g(p)+p)-s*M)/((1-s)*M+p)
    return p,t,rate

def forward(Y,H,tau,w,o,s=0.):
    """Independent forward price: cross-multiplied original household demands.
    Unlike inverse(), this receives a tax and does not use an access target.
    Only call where uniqueness has been proved, unless a local bracket is supplied.
    """
    M=Y/H
    k=tau+(1-tau)*s
    def f(lp):
        p=math.exp(lp); u=w.g(p); v=o.g(p)
        lhs=M*(k*v+(1-k)*u+p)
        rhs=u*v+p*(tau*u+(1-tau)*v)
        return (lhs-rhs)/(lhs+rhs)
    lo,hi=-1.,1.
    while f(lo)<0: lo*=2
    while f(hi)>0: hi*=2
    p=math.exp(bisect(f,lo,hi))
    V=Y+p*H; IW=s*Y+tau*((1-s)*Y+p*H); IO=(1-tau)*((1-s)*Y+p*H)
    hw=IW/(w.g(p)+p); ho=IO/(o.g(p)+p)
    return p,hw/H,IW,IO,hw,ho

def limiting(eta,w,o):
    d=max(1.,w.epsilon,o.epsilon)
    cw=w.c*(1+w.bend); co=o.c*(1+o.bend)
    num=eta*cw*(w.epsilon==d)+eta*(d==1.)
    den=eta*cw*(w.epsilon==d)+(1-eta)*co*(o.epsilon==d)+(d==1.)
    return num/den

def main(out: Path):
    out.mkdir(parents=True,exist_ok=True)
    pairs=[(.5,2.),(2.,.5),(.5,.5),(1.,1.),(1.,.5),(.5,1.),(2.,2.)]
    rows=[]
    for Y,H,eta,(ew,eo),cw,co in itertools.product(
        [1.,100.,1e5],[.7,2.],[.1,.4,.85],pairs,[.7,2.],[.8,3.]):
        w,o=Demand(cw,ew),Demand(co,eo)
        p,t=inverse(Y,H,eta,w,o)
        u,v=w.g(p),o.g(p); M=Y/H; V=Y+p*H
        close(eta*u+(1-eta)*v,M,'inverse_resource')
        IW,IO=t*V,(1-t)*V
        close(IW/(u+p),eta*H,'household_demand_W')
        close(IO/(v+p),(1-eta)*H,'household_demand_O')
        close(IW+IO,V,'income_balance')
        pf,ef,i1,i2,hw,ho=forward(Y,H,t,w,o)
        close(pf,p,'independent_forward_price',rtol=2e-6)
        close(ef,eta,'forward_access',rtol=2e-6)
        close(hw+ho,H,'service_market')
        close(hw*w.g(pf)+ho*o.g(pf),Y,'produced_market')
        delta=1e-5
        _,tp=inverse(Y,H,eta+delta,w,o);_,tm=inverse(Y,H,eta-delta,w,o)
        D=eta*ew*u+(1-eta)*eo*v
        P=(eta*ew*u*(p+v)+(1-eta)*eo*v*(p+u))*(M+p)+eta*(1-eta)*p*(u-v)**2
        deriv=P/(D*(M+p)**2)
        check(deriv>0,'strict_monotonicity')
        close((tp-tm)/(2*delta),deriv,'analytic_derivative',rtol=4e-5)
        if t>1e-7:
            lower=forward(Y,H,t*.999,w,o)[1]
            check(lower<eta,'subthreshold_failure',(lower,eta,t))
        for kappa in [0.,.2,.7]:
            rate=max(0.,(t-kappa)/(1-kappa))
            disposed=kappa+(1-kappa)*rate
            close(disposed*V,kappa*V+rate*(1-kappa)*V,'ownership_funding')
            achieved=forward(Y,H,disposed,w,o)[1]
            check(achieved>=eta-2e-7,'ownership_access',(achieved,eta,kappa))
            if t>kappa: close(achieved,eta,'binding_ownership_access',rtol=2e-6)
    # Schedules outside exact CES, still increasing and homothetic-rationalizable.
    for eta,Y in itertools.product([.15,.5,.8],[1.,1000.]):
        w,o=Demand(.8,.6,.7),Demand(1.4,1.7,.3)
        p,t=inverse(Y,1.,eta,w,o)
        close(forward(Y,1.,t,w,o)[1],eta,'non_power_schedule')
    # Finite labor: guaranteed minimum only under the sufficient e_j>=1 condition.
    for eta,s,Y,(ew,eo) in itertools.product([.2,.6,.9],[.01,.3,.8],[1.,1000.],[(1.,1.),(1.2,2.),(2.,1.)]):
        w,o=Demand(.6,ew),Demand(1.7,eo)
        p,t,raw=tax_target(Y,1.,eta,w,o,s)
        tau=max(0.,raw)
        p1,e1,IW,IO,hw,ho=forward(Y,1.,tau,w,o,s)
        check(e1>=eta-1e-8,'finite_labor_floor')
        close(IW+IO,Y+p1,'finite_labor_income')
        close(IW-s*Y,tau*((1-s)*Y+p1),'finite_labor_budget')
        if raw>0:
            close(p1,p,'finite_labor_price')
            close(e1,eta,'finite_labor_binding')
            check(forward(Y,1.,tau*.999,w,o,s)[1]<eta,'finite_labor_subthreshold')
        check(abs(raw-t)<=s/(1-s)+1e-10,'vanishing_labor_bound')
    # Recover predecessor Cobb-Douglas formulas at finite s and at the limit.
    for a,b,eta,s in itertools.product([.2,.35,.8],[.15,.55,.9],[.1,.4,.8],[0.,.2,.7]):
        w,o=Demand((1-a)/a,1),Demand((1-b)/b,1)
        D=a*(1-eta)+b*eta
        closed=max(0.,(eta*b-s*(D-a*b))/(D-s*(D-a*b)))
        close(max(0.,tax_target(10.,1.,eta,w,o,s)[2]),closed,'v12_finite_recovery')
        close(limiting(eta,w,o),eta*b/D,'v12_limit_recovery')
    # Tail classification including all exponent ties. Large values remain synthetic.
    for ew,eo in [(0.5,2.),(2.,.5),(.5,.5),(1.,1.),(1.,.5),(.5,1.),(2.,2.)]:
        w,o=Demand(1.,ew),Demand(1.,eo)
        eta=.3
        p,t=inverse(1e40,1.,eta,w,o)
        limit=limiting(eta,w,o)
        close(t,limit,'tail_regime',rtol=1e-7,atol=1e-7)
        rows.append({'epsilon_W':ew,'epsilon_O':eo,'Y':1e40,'eta':eta,'price':p,'income_share':t,'proved_limit':limit})
    # Multiplicity: exact sign brackets, independent forward demands at each root.
    F=Fraction
    def exact_rate(z):
        M=F(9,5);s=F(3,5);p=(M/(1+4*z))**20
        u=5*M/(1+4*z)
        return (z*(u+p)-s*M)/((1-s)*M+p)
    target=F(3,43)
    signs=[(F(1,20),-1),(F(19,100),1),(F(21,100),-1),(F(2,5),1)]
    for z,sign in signs:
        check((exact_rate(z)-target)*sign>0,'exact_multiplicity_brackets',(str(z),sign))
    check(exact_rate(F(1,5))==target,'exact_middle_root')
    w,o=Demand(5.,.05),Demand(1.,.05)
    def rate(z):
        M=1.8;p=(M/(1+4*z))**20;u=5*M/(1+4*z)
        return (z*(u+p)-.6*M)/(.4*M+p)
    roots=[bisect(lambda z:rate(z)-float(target),a,b) for a,b in [(.05,.19),(.19,.21),(.21,.4)]]
    root_rows=[]
    for z in roots:
        p=(1.8/(1+4*z))**20
        IW=.6*1.8+float(target)*(.4*1.8+p);IO=(1-float(target))*(.4*1.8+p)
        hw=IW/(w.g(p)+p);ho=IO/(o.g(p)+p)
        close(hw,z,'multiplicity_original_demand')
        close(hw+ho,1.,'multiplicity_service_market')
        close(hw*w.g(p)+ho*o.g(p),1.8,'multiplicity_produced_market')
        close(IW+IO,1.8+p,'multiplicity_income')
        root_rows.append({'eta':z,'price':p,'tax':float(target)})
    check(roots[0]<.2-1e-4 and roots[2]>.2+1e-4,'implementation_not_guarantee')
    close(roots[1],.2,'middle_root_numeric')
    # Analytic derivative at the middle root, computed with exact fractions.
    z=F(1,5);s=F(3,5);u=F(5);v=F(1);p=F(1);M=F(9,5);ew=eo=F(1,20)
    D=z*ew*u+(1-z)*eo*v;B=(1-s)*M+p
    P=(u+p)*D*B-(u-v)*(z*(ew*u+p)*B-p*(z*(u+p)-s*M))
    derivative=P/(D*B*B)
    check(derivative<0,'exact_negative_derivative')
    # Access criterion at a basket-sized income.
    for eps,limit in [(2.,0.),(1.,.5),(.5,1.)]:
        p=1e30;hbar=.4;bx=2.;w=Demand(1.,eps)
        chosen=(bx+p*hbar)/(w.g(p)+p)
        close(chosen/hbar,limit,'basket_allocation_limit',atol=1e-10)
    # Numerical examples of vanishing fraction vs growing nominal transfer.
    w,o=Demand(1.,.5),Demand(1.,2.)
    p1,t1=inverse(1e8,1.,.3,w,o);p2,t2=inverse(1e16,1.,.3,w,o)
    check(t2<t1 and t2*(1e16+p2)>t1*(1e8+p1),'share_not_level')
    for bad in [(0.,1.,.2),(1.,0.,.2),(1.,1.,1.2)]:
        try: inverse(*bad,w,o)
        except ValueError: check(True,'invalid_inputs_rejected')
        else: check(False,'invalid_inputs_rejected')
    with (out/'regimes.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    report={'status':'PASS','assertions':COUNT,'categories':CATEGORIES,
            'default_relative_tolerance':3e-8,'default_absolute_tolerance':2e-10,
            'forward_price_tolerance':2e-6,'derivative_tolerance':4e-5,
            'multiplicity_roots':root_rows,'middle_derivative_exact':str(derivative),
            'empirical_data':False,'independent_peer_review':False,'formal_verification_of_entire_paper':False,
            'scope':'Deterministic internal checks plus exact rational sign certificates; not universal correctness.'}
    (out/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path('audit-output'))
    main(parser.parse_args().out)
