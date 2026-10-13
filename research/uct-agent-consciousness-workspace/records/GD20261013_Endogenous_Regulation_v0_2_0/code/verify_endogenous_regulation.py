#!/usr/bin/env python3
"""Reproduce UCT-GD v0.2's structural feedback examples, not consciousness tests.

One model of two physical deviations x_i, memory variables m_i and interface
variables u_i. Rates/diffusion intensities are explicit. No training data,
network calls, human subjects, consciousness scores, or random runs.

Use normal Python (not -O). Requires NumPy, SciPy, SymPy.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, platform
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
import numpy as np
import scipy, sympy as sp
from scipy.integrate import quad, solve_ivp
from scipy.linalg import expm, solve_continuous_lyapunov
from scipy.optimize import minimize_scalar

@dataclass(frozen=True)
class Parameters:
    a: float=.1
    b: float=.3
    s: float=.3
    c: float=.04
    d: float=.04
    ell: float=.1
    def validate(self):
        if min(self.a,self.b,self.s,self.c,self.d,self.ell)<=0:
            raise ValueError('All base parameters must be strictly positive')

P=Parameters()

def difference_matrix(g: float,h: float,p: Parameters=P) -> np.ndarray:
    p.validate()
    if min(g,h)<0:raise ValueError('Nonnegative cross-coupling required')
    C=p.c+p.ell+2*h;D=p.d+p.ell+2*g
    return np.array([[p.a,-p.b,0.],[p.s,-C,p.ell],[0.,p.ell,-D]])

def full_matrix(g: float,h: float,p: Parameters=P) -> np.ndarray:
    """Order x1,m1,u1,x2,m2,u2; two actual 3-state feedback modules."""
    A0=difference_matrix(0,0,p)
    Q=np.diag([0.,h,g])
    return np.block([[A0-Q,Q],[Q,A0-Q]])

def alpha(A: np.ndarray)->float:
    return float(np.linalg.eigvals(A).real.max())

def covariance(A: np.ndarray,Q: np.ndarray)->np.ndarray:
    if alpha(A)>=-1e-12:
        raise ValueError('No stationary covariance: model is not strictly stable')
    return solve_continuous_lyapunov(A,-Q)

def bench_memory(g,h,t,p=P):
    """Clamped sensory input s*x=0, m_-(0)=1,u_-(0)=0. Not in-vivo memory."""
    C=p.c+p.ell+2*h;D=p.d+p.ell+2*g
    M=np.array([[-C,p.ell],[p.ell,-D]])
    return float(expm(M*t)[0,0])

def limiting_variance(C,a,K,qx=1.,B=0.):
    """B=b^2*q_m, independent body and controller driving noise."""
    if not (0<a<math.sqrt(K) and a<C<K/a and qx>0 and B>=0):
        raise ValueError('Stable interval and nonnegative noise required')
    return (qx*(C*C-a*C+K)+B)/(2*(C-a)*(K-a*C))

def optimum_C(a,K,qx=1.,B=0.):
    r=B/(qx*K)
    return -a*r+math.sqrt(K+r*(K+a*a)+a*a*r*r)

def assert_close(x,y,tol=1e-9):
    e=float(np.max(np.abs(np.asarray(x)-np.asarray(y))))
    if not math.isfinite(e) or e>tol:raise AssertionError((e,tol))
    return e

def solve_rational_covariance(g,h):
    """Independent exact rational linear-system solution, selected examples only."""
    a,b,s,c,d,ell=map(sp.Rational,['1/10','3/10','3/10','1/25','1/25','1/10'])
    g,h=sp.Rational(str(g)),sp.Rational(str(h))
    A=sp.Matrix([[a,-b,0],[s,-(c+ell+2*h),ell],[0,ell,-(d+ell+2*g)]])
    r=sp.symbols('p0:6');p00,p01,p02,p11,p12,p22=r
    V=sp.Matrix([[p00,p01,p02],[p01,p11,p12],[p02,p12,p22]])
    R=A*V+V*A.T+sp.diag(1,0,0)
    sol=sp.solve([R[i,j] for i in range(3) for j in range(i,3)],r,dict=True)
    if len(sol)!=1:raise AssertionError('Covariance equations not unique')
    return V.subs(sol[0])

def symbolic_checks():
    a,b,s,C,D,l,z,qx,B=sp.symbols('a b s C D l z qx B', positive=True)
    K=b*s;A=sp.Matrix([[a,-b,0],[s,-C,l],[0,l,-D]])
    coeff=[1,C+D-a,C*D-l*l-a*(C+D)+K,D*(K-a*C)+a*l*l]
    assert sp.expand((z*sp.eye(3)-A).det()-sum(coeff[i]*z**(3-i) for i in range(4)))==0
    rh=(C+D)*((C-a)*(D-a)-l*l)+K*(C-a)
    assert sp.expand(coeff[1]*coeff[2]-coeff[3]-rh)==0
    k=sp.symbols('k',positive=True)
    den=(C-a)*(k-a*C)
    J=(qx*(C*C-a*C+k)+B)/(2*den)
    deriv=(qx*k*(C*C-k)+B*(2*a*C-k-a*a))/(2*den**2)
    assert sp.simplify(sp.diff(J,C)-deriv)==0
    # The claimed two-state covariance solves the full Lyapunov equations.
    J2=J.subs(k,b*s)
    cross=(a*J2+qx/2)/b
    vm=s*cross/C+B/(2*b*b*C)
    V=sp.Matrix([[J2,cross],[cross,vm]])
    A2=sp.Matrix([[a,-b],[s,-C]])
    Q2=sp.diag(qx,B/(b*b))
    assert all(sp.simplify(v)==0 for v in A2*V+V*A2.T+Q2)
    return {'characteristic_polynomial':'PASS','Routh_factorization':'PASS',
            'noisy_variance_derivative':'PASS','two_state_Lyapunov_identity':'PASS'}

def main(out: Path):
    out.mkdir(parents=True,exist_ok=True)
    sym=symbolic_checks();counts={};max_errors={}
    T=np.block([[np.eye(3),np.eye(3)],[np.eye(3),-np.eye(3)]])/math.sqrt(2)
    assert_close(T@T.T,np.eye(6),1e-15)
    n=0;me=0.;stable_n=unstable_n=0
    # Exact rational Routh classification vs double-precision eigenvalues.
    for g,h in product([Fraction(k,20) for k in range(31)],repeat=2):
        a=Fraction(1,10);K=Fraction(9,100);ell=Fraction(1,10)
        C=Fraction(7,50)+2*h;D=Fraction(7,50)+2*g
        p1=C+D-a;p2=C*D-ell*ell-a*(C+D)+K;p3=D*(K-a*C)+a*ell*ell
        assert p1>0 and p2>0 and p1*p2>p3
        expected=p3>0
        A=difference_matrix(float(g),float(h));observed=alpha(A)<0
        if p3!=0:assert expected==observed
        Af=full_matrix(float(g),float(h));target=np.zeros((6,6))
        target[:3,:3]=difference_matrix(0,0);target[3:,3:]=A
        me=max(me,assert_close(T@Af@T.T,target,3e-15))
        stable_n+=expected;unstable_n+=(not expected);n+=1
    counts['rational_stability_and_full_modal_cases']=n
    counts['stable_cases']=stable_n;counts['unstable_cases']=unstable_n
    max_errors['modal_decomposition']=me
    # Full transient equals modal solution, verified independently by solve_ivp.
    nt=0;me=0.
    for g,h in [(0.,0.),(.5,0.),(.25,.25),(1.,0.),(.92,.08),(.5,.5),(.2,.3)]:
        Af=full_matrix(g,h)
        for init in [np.array([1.,0,0,1,0,0])/math.sqrt(2),np.array([1.,0,0,-1,0,0])/math.sqrt(2)]:
            for t in [.2,2.,10.]:
                exact=expm(Af*t)@init
                sol=solve_ivp(lambda _,v:Af@v,[0,t],init,rtol=2e-11,atol=2e-12,method='DOP853')
                assert sol.success
                me=max(me,assert_close(exact,sol.y[:,-1],5e-10));nt+=1
    counts['independent_ODE_vs_exponential_checks']=nt;max_errors['ODE_vs_exponential']=me
    # Only stable models: positive covariance and Lyapunov residual.
    n=0;me=0.;full_error=0.
    Q=np.diag([1.,0,0])
    for G,eta in product([.1,.3,.5,.7,1.,2.],[0.,.05,.1,.2,.4,.5]):
        g=(1-eta)*G;h=eta*G;A=difference_matrix(g,h)
        if alpha(A)>=-1e-9:continue
        V=covariance(A,Q)
        assert np.linalg.eigvalsh(V).min()>-1e-10
        me=max(me,assert_close(A@V+V@A.T+Q,np.zeros((3,3)),3e-11))
        Vcommon=covariance(difference_matrix(0,0),Q)
        Vfull=covariance(full_matrix(g,h),np.diag([1.,0,0,1,0,0]))
        modal=np.zeros((6,6));modal[:3,:3]=Vcommon;modal[3:,3:]=V
        full_error=max(full_error,assert_close(T@Vfull@T.T,modal,2e-8));n+=1
    counts['stable_full_covariance_checks']=n
    max_errors['Lyapunov_residual']=me;max_errors['full_vs_modal_covariance']=full_error
    # Rational independent check for main comparisons.
    rational=[]
    for g,h in [('1','0'),('0.92','0.08'),('0.5','0'),('0.25','0.25')]:
        Vrat=solve_rational_covariance(g,h)
        V=covariance(difference_matrix(float(g),float(h)),Q)
        err=assert_close(np.array(Vrat,float),V,3e-10)
        rational.append({'g':g,'h':h,'J_exact_rational':str(Vrat[0,0]),'J':float(Vrat[0,0]),'error':err})
    # H2 via direct integration of physical pulse response, independent of Lyapunov solve.
    integration=[]
    for g,h in [(1.,0.),(.92,.08),(.25,.25)]:
        A=difference_matrix(g,h);V=covariance(A,Q)
        val,err=quad(lambda t: float(expm(A*t)[0,0]**2),0,np.inf,epsabs=3e-8,epsrel=3e-9,limit=500)
        assert abs(val-V[0,0])<3e-7
        integration.append({'g':g,'h':h,'impulse_energy':val,'covariance':float(V[0,0]),'quadrature_error_estimate':err})
    # Closed fast-interface formula and independent noisy covariance optimum.
    nl=0;me=0.;noise_opt=[]
    for a,K,Cfraction,b,qx,qm in product([.05,.1],[.09,.25],[.15,.35,.55,.75],[.3,.5],[.5,1.],[0.,.1,1.]):
        s=K/b;C=a+(K/a-a)*Cfraction
        A2=np.array([[a,-b],[s,-C]])
        V=covariance(A2,np.diag([qx,qm]));j=limiting_variance(C,a,K,qx,b*b*qm)
        me=max(me,assert_close(V[0,0],j,3e-9));nl+=1
    for qm in [0.,.1,1.,10.]:
        Cstar=optimum_C(.1,.09,1.,.09*qm)
        opt=minimize_scalar(lambda C:limiting_variance(C,.1,.09,1.,.09*qm),bounds=(.10001,.89999),method='bounded',options={'xatol':1e-12})
        assert abs(opt.x-Cstar)<1e-7
        noise_opt.append({'memory_noise_intensity':qm,'analytic_C_star':Cstar,'numeric_C_star':float(opt.x),'J_star':float(opt.fun)})
    counts['two_state_noisy_variance_checks']=nl;max_errors['two_state_variance']=me
    # Stationary covariance converges for the three example fixed leakage values.
    limits=[]
    for h in [0.,.08,.2]:
        C=.14+2*h;target=limiting_variance(C,.1,.09)
        js=[float(covariance(difference_matrix(g,h),Q)[0,0]) for g in [10.,100.,1000.,10000.]]
        assert abs(js[-1]-target)<1e-3
        limits.append({'h':h,'C':C,'limiting_J':target,'finite_g':[10.,100.,1000.,10000.],'J':js})
    # Display cases: no fake finite J for unstable systems.
    cases=[]
    for label,g,h in [('maximal_source_retention',1.,0.),('regulated_leakage',.92,.08),('uniform_mixing',.5,.5)]:
        A=difference_matrix(g,h);ar=alpha(A)
        J=float(covariance(A,Q)[0,0]) if ar<0 else None
        cases.append({'route':label,'g':g,'h':h,'total_G':g+h,
                      'bench_memory_at_t5':bench_memory(g,h,5.),'max_growth_rate':ar,'J_physical_error':J,
                      'status':'STABLE' if ar<0 else 'UNSTABLE_NO_STATIONARY_J'})
    common_J=float(covariance(difference_matrix(0,0),Q)[0,0])
    # Finite route continuous scan and a numerical optimum, not a new theorem.
    rows=[]
    for h in np.linspace(0,.5,101):
        A=difference_matrix(1-float(h),float(h));ar=alpha(A)
        rows.append({'h':float(h),'g':float(1-h),'bench_memory_t5':bench_memory(1-h,h,5.),
                     'max_growth_rate':ar,'J':float(covariance(A,Q)[0,0]) if ar< -1e-10 else ''})
    assert all(rows[i]['bench_memory_t5']>rows[i+1]['bench_memory_t5'] for i in range(len(rows)-1))
    opt=minimize_scalar(lambda h:float(covariance(difference_matrix(1-h,h),Q)[0,0]),
                        bounds=(0,.37),method='bounded',options={'xatol':1e-12})
    assert .08<float(opt.x)<.09 and opt.fun<cases[0]['J_physical_error']
    # Actuator rewiring: only the physical sensor-to-body relationship changes.
    base=difference_matrix(.92,.08);wrong=base.copy();wrong[0,1]*=-1
    repaired=wrong.copy();repaired[1,0]*=-1
    assert alpha(base)<0<alpha(wrong)
    S=np.diag([1.,-1.,-1.]);assert_close(repaired,S@base@S)
    for t in [.1,1.,10.]:
        assert_close(expm(repaired*t)[0,0],expm(base*t)[0,0],1e-13)
    # Yoked replay versus genuine feedback: same nominal behavior, different new disturbances.
    # For replay identical pre-challenge m(t) the error delta(t)=delta(0)exp(a*t).
    replay=[]
    for t in [0.,5.,25.,100.]:
        live=float(expm(base*t)[0,0]);yoked=math.exp(P.a*t)
        replay.append({'time':t,'live_body_response':live,'replay_body_response':yoked})
    # State-coordinate and clock-scaling checks in the reduced closed-loop limit.
    A2=np.array([[.1,-.3],[.3,-.3]]);V=covariance(A2,np.diag([1.,.1]))
    for r in [.1,.7,3.,10.]:
        Aclock=A2/r;Qclock=np.diag([1.,.1])/r
        assert_close(covariance(Aclock,Qclock),V,1e-10)
        assert_close(expm(Aclock*(5*r)),expm(A2*5),1e-12)
        U=np.diag([1.,r]);Ur=np.linalg.inv(U)
        assert_close(covariance(U@A2@Ur,U@np.diag([1.,.1])@U.T),U@V@U.T,1e-8)
    # Nonlinear saturation counterlimit (not a simulation of biology).
    x=3.1;assert P.a*x-P.b>0
    result={'checkpoint':'UCT-GD-20261013-v0.2.0','symbolic_checks':sym,'counts':counts,
      'max_errors':max_errors,'main_equal_budget_cases':cases,'common_J_unchanged':common_J,
      'rational_covariance_checks':rational,'impulse_energy_checks':integration,
      'fast_interface_limits':limits,'noise_dependent_optima':noise_opt,
      'uniform_mixing_critical_G':(.9+math.sqrt(.85))/2-.14,
      'finite_G1_optimum':{'h':float(opt.x),'g':float(1-opt.x),'J':float(opt.fun)},
      'replay_checks':replay,
      'rewiring_growth_rates':{'base':alpha(base),'wrong_actuator':alpha(wrong),'sensor_compensated':alpha(repaired)},
      'nonlinear_saturation_counterlimit':{'a':P.a,'b':P.b,'x':x,'minimum_x_dot':P.a*x-P.b},
      'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'sympy':sp.__version__},
      'science_scope':{'exact_for_declared_linear_models':True,'control_tools_new_inventions':False,
       'endogenous_norm_or_life_derived':False,'subjective_experience_measured':False,
       'natural_evolution_simulated':False,'full_map_semantic_audit_complete':False}}
    (out/'REGULATION_RESULTS.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    with (out/'ROUTING_SCAN.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O; assertions are part of verification')
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'results')
    main(ap.parse_args().out)
