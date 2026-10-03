#!/usr/bin/env python3
"""Exact all-F4-grid pressure, with rational additive feasibility certificates.

All order/orientation checks are integer. Floating LPs only propose either
strict-score witnesses or Farkas multipliers; every certificate is checked
exactly before classification. This finite relaxed audit is NOT a proof.
"""
from pathlib import Path
from fractions import Fraction
from itertools import permutations
from math import lcm
import gzip,hashlib,json,time
import numpy as np
from scipy.optimize import linprog
from probe_quartet_grid_recurrence import words

def score_vector(f,x,F):
    v=[0]*(F+1)
    if f:v[f-1]=1
    if x&1:v[F-1]=1
    if x&2:v[F]=1
    return v

def feasibility(word,F):
    rows=[]
    for (f,x),(g,y) in zip(word,word[1:]):
        u=score_vector(f,x,F);v=score_vector(g,y,F);rows.append([b-a for a,b in zip(u,v)])
    # a>0,b>a and strictly increasing offsets (s_0=0).
    a=[0]*(F+1);a[F-1]=1;rows.append(a)
    b=[0]*(F+1);b[F]=1;b[F-1]=-1;rows.append(b)
    for f in range(1,F):
        u=score_vector(f-1,0,F);v=score_vector(f,0,F);rows.append([b-a for a,b in zip(u,v)])
    A=np.array(rows,dtype=float);lp=linprog(np.zeros(F+1),A_ub=-A,b_ub=-np.ones(len(rows)),bounds=[(None,None)]*(F+1),method='highs')
    if lp.success:
        x=[Fraction(float(v)).limit_denominator(100000) for v in lp.x]
        assert all(sum(c*z for c,z in zip(row,x))>=1 for row in rows)
        denom=lcm(*(v.denominator for v in x));xx=[int(v*denom) for v in x]
        assert all(sum(c*z for c,z in zip(row,xx))>=1 for row in rows)
        offsets=[0]+xx[:F-1];a,b=xx[F-1:]
        actual=tuple((f,x) for s,f,x in sorted((s+(a if x&1 else 0)+(b if x&2 else 0),f,x) for f,s in enumerate(offsets) for x in range(4)))
        assert actual==word
        return {'status':'EXACT_REALIZABLE_TRANSLATION','integer_offsets':offsets,'a':a,'b':b,'constraint_rows':rows}
    assert lp.status==2
    # Homogeneous strict inequalities are infeasible iff a nonnegative
    # combination of normals is zero; normalize its multiplier sum to1.
    dual=linprog(np.zeros(len(rows)),A_eq=np.vstack((A.T,np.ones(len(rows)))),b_eq=np.array([0]*(F+1)+[1]),bounds=(0,None),method='highs')
    assert dual.success
    y=[Fraction(float(v)).limit_denominator(100000) for v in dual.x]
    assert all(v>=0 for v in y) and sum(y)==1
    assert all(sum(v*row[j] for v,row in zip(y,rows))==0 for j in range(F+1))
    denom=lcm(*(v.denominator for v in y));yy=[int(v*denom) for v in y]
    return {'status':'EXACT_ADDITIVE_INFEASIBILITY','constraint_rows':rows,'integer_Farkas_multipliers':yy,'strict_rhs_sum':sum(yy)}

def main():
    start=time.monotonic();F=4;P=list(permutations(range(F)));B=np.array(P,dtype=np.int64)[:,None,:]
    masks=np.arange(1<<(2*F),dtype=np.int64)[None,:];upper=[]
    for p in P:
        s=[1 if p[j+1]>p[j] else -1 for j in range(F-1)]
        upper.append(1+sum(x!=y for x,y in zip(s,s[1:])))
    target=np.array([min(F+1,4*u-3) for u in upper],dtype=np.int64)
    infeasible=[];actual_failures=[];count=0;violations=0
    for word in words(F):
        turns=np.zeros((len(P),masks.shape[1]),dtype=np.int64);previous=None
        for (f,x),(g,y) in zip(word,word[1:]):
            if f!=g:sg=np.where(B[:,:,g]>B[:,:,f],1,-1)
            else:
                h=(x^y).bit_length()-1
                sg=(1 if (y^(y>>1))>(x^(x>>1)) else -1)*(1-2*((masks>>(2*f+h))&1))
            if previous is not None:turns+=(previous!=sg)
            previous=sg
        minima=turns.min(axis=1)+1;count+=1;fail=np.flatnonzero(minima<target)
        if len(fail):
            violations+=1;j=int(fail[0]);mask=int(np.argmin(turns[j]));p=P[j]
            z={'word':word,'block_rank':p,'mask':mask,'upper_runs':upper[j],
               'actual_runs':int(minima[j]),'proposed_bound':int(target[j]),'feasibility':feasibility(word,F)}
            (actual_failures if z['feasibility']['status']=='EXACT_REALIZABLE_TRANSLATION' else infeasible).append(z)
        if count%4000==0:
            print(json.dumps({'grid_words_completed':count,'grid_violations':violations,'real_translation_failures':len(actual_failures),'infeasible_grid_failures':len(infeasible),'elapsed':time.monotonic()-start}),flush=True)
    assert count==24024
    out={'status':'EXACT_COMPLETE_F4_GRID_AUDIT_WITH_RATIONAL_SCORE_CERTIFICATES','F':F,
         'scope':'All24024 grid words,all24 face-block permutations,all256 independent local orientation masks. Score offsets arbitrary, not constrained to a cube subset-sum family. No all-dimensional proof.',
         'proposed_statement':'R>=min(F+1,4*R_upper-3) for equal-gap positive additive quartet translations.',
         'grid_words_completed':count,'grid_violation_words':violations,'real_translation_counterexamples':actual_failures,
         'exactly_infeasible_grid_counterexamples':infeasible,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    raw=(json.dumps(out,indent=2)+'\n').encode();Path(__file__).with_name('quartet_additive_recurrence_pressure.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    print(json.dumps({k:v for k,v in out.items() if k not in ('real_translation_counterexamples','exactly_infeasible_grid_counterexamples')}
                     |{'real_translation_failures':len(actual_failures),'infeasible_grid_failures':len(infeasible),'first_real_failure':actual_failures[0] if actual_failures else None}),flush=True)

if __name__=='__main__':main()
