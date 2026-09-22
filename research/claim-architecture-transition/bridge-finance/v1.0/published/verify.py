#!/usr/bin/env python3
"""Reproduce deterministic examples in Public Upside Claims v1.0-rc1.
Not an economic calibration, simulation of a country, or investment tool.
Run: python verify.py. Requires NumPy and SciPy.
"""
from __future__ import annotations
import json
import math
import platform
from pathlib import Path
from typing import Any
import numpy as np
import scipy
from scipy.optimize import brentq, minimize

OUT = Path(__file__).resolve().parent
CHECKS: list[dict[str, Any]] = []


def record(name: str, condition: bool, **details: Any) -> None:
    CHECKS.append({"name": name, "pass": bool(condition), **details})
    if not condition:
        raise AssertionError(name)


def lam(x: np.ndarray, y: np.ndarray, p: np.ndarray, beta: float = 1.0) -> float:
    if np.any(x < 0) or np.any(y <= 0) or not np.isclose(p.sum(), 1):
        raise ValueError("Invalid payments, incomes, or state probabilities")
    return float(beta * np.sum(p * x / (y + x)))


def price(x: np.ndarray, y: np.ndarray, p: np.ndarray, W: float = 100., beta: float = 1.) -> float:
    v = lam(x, y, p, beta)
    return W * v / (1 + v)


def cost(x: np.ndarray, R: np.ndarray, p: np.ndarray) -> float:
    if np.any(x >= R):
        return float("inf")
    return float(np.sum(p * np.log(R / (R - x))))


def least_cost(target: float, R: np.ndarray, cap: np.ndarray, y: np.ndarray,
               p: np.ndarray, W: float = 100., beta: float = 1.) -> tuple[np.ndarray, float | None]:
    max_b = price(cap, y, p, W, beta)
    if target < 0 or target > max_b + 1e-10:
        raise ValueError("Support target outside financing frontier")
    if target == 0:
        return np.zeros_like(R), 0.0
    if abs(target-max_b) < 1e-10:
        return cap.copy(), None

    def payments(k: float) -> np.ndarray:
        # Stable root of x^2 + y(2+k)x + y^2-k*y*R = 0.
        disc = np.sqrt(k*k*y*y + 4*k*y*(y+R))
        root = 2*(k*y*R-y*y)/(disc+y*(2+k))
        return np.clip(root, 0, cap)

    hi = 1.0
    while price(payments(hi), y, p, W, beta) < target:
        hi *= 2
        if hi > 1e14:
            raise RuntimeError("Multiplier bracket not found")
    k = brentq(lambda z: price(payments(z), y, p, W, beta)-target,
               0., hi, xtol=1e-13)
    return payments(k), float(k)


def investment(theta: float, tau: float = .2, W: float = 100., b: float = .5,
               a: float = 100., yH: float = 20.) -> dict[str, float]:
    if not (0 <= theta <= 1 and 0 < tau < 1 and min(W,b,a,yH)>0):
        raise ValueError("Invalid investment benchmark parameters")
    g = theta*tau/(1-tau)
    v = yH/(a*(1-tau))
    Q = 2+b+2*(1+b)*g
    r = b*W/(math.sqrt(v*v+Q*b*W)+v)
    I = r*r
    B = 2*g*I
    F = a*r
    D = theta*tau*F
    c0 = W-I-B
    cH = yH+(1-tau)*F+D
    return dict(theta=theta,tau=tau,I=I,B=B,F=F,D=D,c0=c0,cH=cH,
                g=g,v=v,Q=Q,r=r)


def main() -> None:
    p2 = np.array([.5,.5]); y2 = np.array([50.,100.]); x2=np.array([0.,100.])
    B = price(x2,y2,p2)
    record("exchange_price", abs(B-20)<1e-10, price=B)
    record("exchange_buyer_foc", abs(B/(100-B)-lam(x2,y2,p2))<1e-12)
    record("current_exchange_resources", abs((100-B)+(5+B)-105)<1e-12)
    record("future_exchange_resources", bool(np.allclose(y2+x2+np.array([100.,400.])-x2,
                                                       y2+np.array([100.,400.]))))
    investor_gain=math.log(.8)+.5*math.log(2)
    recipient_gain=math.log(5)+.5*math.log(.75)
    record("voluntary_exchange_example", investor_gain>0 and recipient_gain>0,
           investor_utility_gain=investor_gain, beneficiary_utility_gain=recipient_gain)
    record("common_abundance_scale", abs(price(100*x2,100*y2,p2)-B)<1e-12)
    record("payment_only_increase", abs(price(2*x2,y2,p2)-25)<1e-12)
    record("buyer_only_high_income", abs(price(x2,np.array([50.,10000.]),p2)-100/203)<1e-12)

    p=np.array([.25,.5,.25]); y=np.array([50.,100.,500.]); R=np.array([100.,200.,600.]); cap=np.array([0.,25.,200.])
    G=np.array([100.,150.,200.])
    table=[]
    for target in [0.,5.,10.,14.,price(cap,y,p)]:
        x,k=least_cost(target,R,cap,y,p)
        record(f"contract_target_{target:.6f}", abs(price(x,y,p)-target)<1e-8)
        record(f"contract_floor_{target:.6f}", bool(np.all(R-x>=G-1e-10)))
        if target == 0: t=0.
        elif abs(target-price(cap,y,p))<1e-8:t=1.
        else:t=brentq(lambda t:price(t*cap,y,p)-target,0,1)
        prop=t*cap
        record(f"contract_cost_vs_proportional_{target:.6f}",cost(x,R,p)<=cost(prop,R,p)+1e-10)
        if 0<target<price(cap,y,p):
            free=np.where((x>1e-8)&(x<cap-1e-8))[0]
            ratio=(y+x)**2/(y*(R-x))
            record(f"contract_free_kkt_{target:.6f}",bool(np.allclose(ratio[free],k,atol=1e-8)))
            # Independently solve the convex allocation in the two live coordinates.
            res=minimize(lambda v:cost(np.r_[0.,v],R,p), prop[1:], method='SLSQP',
                         bounds=list(zip(np.zeros(2),cap[1:])),
                         constraints=[{'type':'ineq','fun':lambda v:price(np.r_[0.,v],y,p)-target}],
                         options={'ftol':1e-12,'maxiter':1000})
            record(f"contract_independent_optimizer_{target:.6f}",
                   res.success and abs(res.fun-cost(x,R,p))<1e-7,
                   solver_message=str(res.message))
        table.append(dict(target=target,payments=x.tolist(),cost=cost(x,R,p),
                          proportional=prop.tolist(),proportional_cost=cost(prop,R,p)))
    row=table[2]
    saving=100*(1-row['cost']/row['proportional_cost'])
    record("same_transfer_beneficiary_cost_reduction",saving>16 and saving<18,
           percent=saving)
    try:least_cost(price(cap,y,p)+1,R,cap,y,p)
    except ValueError: record("reject_infeasible_target",True)
    else: record("reject_infeasible_target",False)

    inv_table=[]
    for th in [0.,.5,1.]:
        r=investment(th)
        inv_table.append(r)
        cPublicH=100+(1-th)*.2*r['F']
        record(f"production_current_resources_{th}",abs(r['c0']+(5+r['B'])+r['I']-105)<1e-10)
        record(f"production_high_resources_{th}",abs(r['cH']+cPublicH-(20+100+r['F']))<1e-10)
        record(f"production_protected_floor_{th}",cPublicH>=100 and r['c0']>0)
    for a in [20.,100.]:
        for tau in [.05,.2,.8]:
            prev=None
            for th in [.25,.5,1.]:
                r=investment(th,tau=tau,a=a)
                m=(1-tau)*a/(2*math.sqrt(r['I']))
                residual_i=1/r['c0']-.5*m/r['cH']
                residual_b=r['B']/r['c0']-.5*r['D']/r['cH']
                name=f"portfolio_foc_a{a}_tau{tau}_theta{th}"
                record(name,max(abs(residual_i),abs(residual_b))<1e-9)
                if prev is not None:
                    record(name+"_monotonic",r['I']<prev['I'] and r['B']>prev['B'])
                prev=r
    r=investment(.5)
    B0,D0=r['B'],r['D']
    def obj(z: np.ndarray)->float:
        i,h=z
        c0=100-i-B0*h
        ch=20+.8*100*math.sqrt(max(i,0))+D0*h
        if c0<=0:return 1e12 + 1e6*abs(c0)
        return -(math.log(c0)+.5*math.log(ch)+.5*math.log(50))
    res=minimize(obj,np.array([10.,.5]),method='SLSQP',bounds=[(1e-8,99.99),(0,100/B0)],
                 constraints=[{'type':'ineq','fun':lambda z:100-z[0]-B0*z[1]-1e-8}],
                 options={'ftol':1e-12,'maxiter':1000})
    record("independent_portfolio_optimizer",res.success and np.allclose(res.x,[r['I'],1.],atol=1e-3),
           optimum=res.x.tolist(),message=str(res.message))
    imin=18.;tau=.2;v=.25;b=.5;W=100.
    gi=(b*W-(2+b)*imin-2*v*math.sqrt(imin))/(2*(1+b)*imin)
    theta_i=(1-tau)/tau*gi
    lim=investment(theta_i)
    record("investment_floor_inverse",abs(lim['I']-imin)<1e-10,
           theta_max=theta_i,support_max=lim['B'])
    record("four_units_violates_investment_floor",investment(1.)['B']>4>lim['B'])
    edge_prices=[investment(.5,tau=1-eps)['B'] for eps in [1e-6,1e-7,1e-8]]
    record("tax_base_vanishes_near_one", edge_prices[0]>edge_prices[1]>edge_prices[2]>0
           and edge_prices[2]<.001, prices=edge_prices)

    result={'status':'PASS','kind':'deterministic mathematical reproduction, not empirical evidence',
            'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
            'counts':{'passed':sum(c['pass'] for c in CHECKS),'failed':sum(not c['pass'] for c in CHECKS)},
            'contract_table':table,'investment_table':inv_table,
            'cost_reduction_percent':saving,'checks':CHECKS}
    (OUT/'checks.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'counts':result['counts'],'cost_reduction_percent':saving,
                      'investment_floor_theta':theta_i,'investment_floor_support':lim['B']},indent=2))

if __name__ == '__main__':
    main()
