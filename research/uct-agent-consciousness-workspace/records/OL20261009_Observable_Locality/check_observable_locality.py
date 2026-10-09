#!/usr/bin/env python3
"""Exact and numerical checks of observable-locality quotient. No phenomenal measurements."""
from __future__ import annotations
import json, math, itertools, random, argparse, pathlib
from fractions import Fraction
import numpy as np
import sympy as sp

def sym_gap(K, v, J, Rinv=None):
    K=sp.Matrix(K);v=sp.Matrix(v)
    n=K.cols
    E=sp.eye(n)[:,list(J)] if J else sp.zeros(n,0)
    Q=sp.eye(K.rows) if Rinv is None else sp.Matrix(Rinv)
    W=K.T*Q*K
    if J:
        M=E.T*W*E
        residual=(v.T*(W-W*E*M.pinv()*E.T*W)*v)[0]
    else: residual=(v.T*W*v)[0]
    return sp.simplify(residual)

def best_gap(K, v, k, Rinv=None):
    n=sp.Matrix(K).cols
    return min((sym_gap(K,v,J,Rinv),tuple(J)) for m in range(k+1) for J in itertools.combinations(range(n),m))

def numeric_gap(K, v, J, Rinv):
    K=np.array(K,dtype=float);v=np.array(v,dtype=float).reshape(-1)
    E=np.eye(K.shape[1])[:,list(J)]
    Q=np.array(Rinv,dtype=float)
    L=np.linalg.cholesky(Q).T
    Z=L @ K
    if not J:return float((Z@v)@(Z@v))
    fit=np.linalg.lstsq(Z@E,Z@v,rcond=None)[0]
    x=Z@v-Z@E@fit
    return float(x@x)

def tests(out):
    rng=random.Random(20261009)
    count=0; invariants=0; candidate_tests=0; counterexamples=[]
    A=sp.diag(sp.Rational(1,2),sp.Rational(1,4)); B=sp.Matrix([1,1]); C=sp.Matrix([[1,1]])
    S=sp.Matrix([[1,1],[1,-1]]); A2=S*A*S.inv();B2=S*B;C2=C*S.inv()
    assert A2==sp.Matrix([[sp.Rational(3,8),sp.Rational(1,8)],[sp.Rational(1,8),sp.Rational(3,8)]])
    assert B2==sp.Matrix([2,0]) and C2==sp.Matrix([[1,0]])
    assert sp.Matrix.vstack(C2,C2*A2).det()!=0
    x=sp.Matrix([1,2]);z=S*x;d=sp.Matrix([-1,0]); v=S*d
    # IL prepared episode: x=(1,2), z=(3,-1); source x1:=0 demands delta x=-e1.
    assert z==sp.Matrix([3,-1]) and v==sp.Matrix([-1,-1])
    O1=C2
    O2=sp.Matrix.vstack(C2,C2*A2)
    assert best_gap(O1,v,1)[0]==0
    assert best_gap(O2,v,1)[0]==sp.Rational(1,73)
    # Explicit minimizers: source target z'=S*(0,2)=(2,-2). z1-only recipient optimum new z1=143/73.
    a=sp.Rational(143,73)
    diff=sp.Matrix([a-2,(3*a-1)/8-sp.Rational(1,2)])
    assert sp.simplify((diff.T*diff)[0])==sp.Rational(1,73)
    assert sp.simplify(max(abs(a-2),abs((3*a-1)/8-sp.Rational(1,2))))==sp.Rational(8,73)
    assert sp.Rational(8,73)>sp.Rational(1,11)
    example={'source_A':str(A.tolist()),'recipient_A':str(A2.tolist()),'source_B':str(B),'recipient_B':str(B2),'source_C':str(C),'recipient_C':str(C2),'source_state':[1,2],'recipient_state':[3,-1],'desired_recipient_kick':[-1,-1], 'horizon_one_squared_gap':'0','horizon_two_squared_gap':'1/73','horizon_two_gap':'1/sqrt(73)','recipient_best_z1_after_write':'143/73','older_infinity_norm_minimum':'1/11'}
    # Arbitrary fixed full rank H and positive definite weight: analytic formula = independently solved LS.
    for n in (2,3,4):
      for _ in range(70):
        while True:
          K=sp.Matrix([[rng.randint(-3,3) for j in range(n)] for i in range(n+1)])
          if K.rank()==n:break
        v=sp.Matrix([rng.randint(-3,3) for _ in range(n)])
        Q=sp.diag(*[sp.Rational(rng.randint(1,5),rng.randint(1,3)) for _ in range(n+1)])
        for k in range(n):
          for J in itertools.combinations(range(n),k):
            s=sym_gap(K,v,J,Q)
            numer=numeric_gap(K.tolist(),list(v),J,np.array(Q.tolist(),float))
            if abs(float(s)-numer)>2e-7:raise AssertionError(('projection',n,k,J,s,numer))
            assert s>=0
            candidate_tests+=1
          count+=1
    # Transform K, state change and genuine installed action subspaces together.
    for n in (2,3):
      for _ in range(55):
        while True:
          K=sp.Matrix([[rng.randint(-2,2) for _ in range(n)] for _ in range(n+1)])
          if K.rank()==n:break
        while True:
          L=sp.Matrix([[rng.randint(-2,2) for _ in range(n)] for _ in range(n)])
          if L.det()!=0:break
        v=sp.Matrix([rng.randint(-2,2) for _ in range(n)])
        Q=sp.diag(*[sp.Integer(rng.randint(1,4)) for _ in range(n+1)])
        Kp=K*L;vp=L.inv()*v
        for j in range(n):
          E=sp.eye(n)[:,j]; Ep=L.inv()*E
          W=K.T*Q*K;Wp=Kp.T*Q*Kp
          a=(v.T*(W-W*E*(E.T*W*E).inv()*E.T*W)*v)[0]
          b=(vp.T*(Wp-Wp*Ep*(Ep.T*Wp*Ep).inv()*Ep.T*Wp)*vp)[0]
          assert sp.simplify(a-b)==0
          invariants+=1
    # Structural countercontrols: an H=1 readout can hide a non-local target kick.
    assert sym_gap(O1,sp.Matrix([-1,-1]),[0])==0
    assert sym_gap(sp.Matrix([[1,0],[0,0]]),sp.Matrix([1,1]),[0])==0
    assert best_gap(sp.eye(2),sp.Matrix([1,1]),1)[0]==1
    # A passive coordinate recoding must transform admissible write subspaces; naive coordinate-sparsity need not preserve gap.
    K=sp.eye(2);v=sp.Matrix([1,1]);L=sp.Matrix([[1,1],[1,-1]])
    old=best_gap(K,v,1)[0]
    wrong=best_gap(K*L,L.inv()*v,1)[0]
    assert old==1 and wrong==0
    counterexamples.append({'label':'false gauge invariance from resetting coordinate sparsity after passive recoding','old_squared_gap':str(old),'naive_new_squared_gap':str(wrong)})
    # Positive gap implies separation under adversarial observed norm bounded by eps for both sides.
    gg=1/math.sqrt(73)
    for eps in (0.0,0.02,0.05,0.058):
       assert gg>2*eps
    for eps in (0.059,0.1):
       assert gg<=2*eps
    # Need not infer identical or disjoint physical bearer, phenomenal quality, or higher intelligence.
    result={'status':'PASS','seed':20261009,'formula':'min_{|J|<=k} vT[W-W E_J(E_J^T W E_J)^+ E_J^T W]v; W=K_H^T Q K_H; pseudoinverse in general, inverse if O_H full column rank','exact_case':example,'exact_rational_vs_independent_weighted_lstsq_cases':candidate_tests,'random_model_k_counts':count,'coordinate_transport_exact_equalities':invariants,'countercontrols':counterexamples,'two_sided_noise_separation_example':'epsilon < 1/(2 sqrt(73))','interpretation':'Finite mathematical LTI and intervention models only. No actual neural subject or phenomenal validation.'}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path('results/OBSERVABLE_LOCALITY_RESULTS.json'));a=p.parse_args();tests(a.out)
