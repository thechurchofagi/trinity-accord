#!/usr/bin/env python3
"""A distinct cancellation-consistent relaxation, beyond additive scans.

Boolean term orders/flips and noncoherent examples are Maclagan's prior work
(arXiv:math/9809134v2). New work tests paired run minima, with exact order
checks and integer feasibility/Farkas certificates. Never treat noncoherent
orders as genuine scans. The flip component alone is NOT a completeness proof.
"""
from pathlib import Path
from itertools import permutations
from collections import deque,Counter
from fractions import Fraction
from math import lcm
import gzip,hashlib,json,time
import numpy as np
from scipy.optimize import linprog
from verify_paired_sibling_ranks import rank,fast_runs,linear_graph
from paired_sibling_ancestor_optimizer import optimize

def term_check(p,n):
    N=1<<n;assert len(p)==N and len(set(p))==N and p[0]==0
    pos=[0]*N
    for i,x in enumerate(p):pos[x]=i
    checks=0
    for a in range(N):
        for b in range(a+1,N):
            z=a&b;aa=a^z;bb=b^z
            assert (pos[a]<pos[b])==(pos[aa]<pos[bb]);checks+=1
    assert all(p[i]^p[-1-i]==N-1 for i in range(N))
    return checks

def neighbors(p,n):
    N=1<<n;pos={x:i for i,x in enumerate(p)}
    for a,b in zip(p,p[1:]):
        if a==0 or a&b:continue
        # Preserve singleton order 1<2<4<... in the sorted quotient.
        if a.bit_count()==b.bit_count()==1:continue
        free=(N-1)^(a|b);sub=free;pairs=[]
        while True:
            if pos[b|sub]!=pos[a|sub]+1:break
            pairs.append((pos[a|sub],pos[b|sub]))
            if sub==0:
                q=list(p)
                for i,j in pairs:q[i],q[j]=q[j],q[i]
                yield tuple(q),(a,b)
                break
            sub=(sub-1)&free

def coherence(p,n):
    A=np.array([[((b>>j)&1)-((a>>j)&1) for j in range(n)] for a,b in zip(p,p[1:])],dtype=int)
    ans=linprog(np.zeros(n),A_ub=-A,b_ub=-np.ones(len(A)),bounds=[(None,None)]*n,method='highs')
    if ans.success:
        f=[Fraction(float(x)).limit_denominator(1000000) for x in ans.x];scale=lcm(*(x.denominator for x in f));w=[int(x*scale) for x in f]
        assert all(sum(int(a)*b for a,b in zip(row,w))>0 for row in A)
        return {'coherent':True,'integer_weights':w}
    assert ans.status==2
    ans=linprog(np.zeros(len(A)),A_eq=np.vstack([A.T,np.ones(len(A))]),b_eq=np.array([0]*n+[1]),bounds=[(0,None)]*len(A),method='highs')
    assert ans.success
    fs=[Fraction(float(x)).limit_denominator(1000000) for x in ans.x];scale=lcm(*(x.denominator for x in fs));y=[int(x*scale) for x in fs]
    assert all(x>=0 for x in y) and sum(y)>0
    assert all(sum(y[i]*int(A[i,j]) for i in range(len(y)))==0 for j in range(n))
    return {'coherent':False,'integer_farkas':[(i,x) for i,x in enumerate(y) if x]}

def permute(p,perm):
    n=len(perm);mapping=[sum(((x>>j)&1)<<perm[j] for j in range(n)) for x in range(1<<n)]
    return tuple(mapping[x] for x in p)

def test_all_priorities(p,n):
    minimum=10**9;hist=Counter();attainer=None
    for perm in permutations(range(n)):
        pp=permute(p,perm);g=linear_graph(pp,n);opt=optimize(g,n);R=(2**n+g['D']-opt['E_max'])//2
        assert R==fast_runs([rank(x,n,opt['mask']) for x in range(1<<n)],pp)
        hist[R]+=1
        if R<minimum:minimum=R;attainer={'permutation':perm,'mask':opt['mask'],'order':pp}
    return {'minimum_all_paired_masks_and_priorities':minimum,'priority_histogram':dict(hist),'attainer':attainer}

def bits(labels):return tuple(sum(1<<(int(j)-1) for j in str(x)) if x else 0 for x in labels)

def main():
    start=time.monotonic();n=5;p=tuple(range(32));queue=deque([p]);seen={p};directed=0
    while queue:
        p=queue.popleft()
        for q,pair in neighbors(p,n):
            directed+=1
            if q not in seen:seen.add(q);queue.append(q)
    assert len(seen)==546
    rows=[];coherent=0;minimum=10**9
    for i,p in enumerate(sorted(seen)):
        term_check(p,n);certificate=coherence(p,n)
        coherent+=certificate['coherent']
        row={'order':p,'coherence_certificate':certificate}
        if not certificate['coherent']:
            row['paired_test']=test_all_priorities(p,n);minimum=min(minimum,row['paired_test']['minimum_all_paired_masks_and_priorities'])
        rows.append(row)
    assert coherent==516
    print(json.dumps({'n5_flip_component':len(seen),'coherent':coherent,'noncoherent':len(seen)-coherent,'noncoherent_paired_minimum':minimum,'elapsed':time.monotonic()-start}),flush=True)
    # Two distinct original-paper six-variable noncoherent examples; reconstruct
    # their second halves using complement-reversal, then verify every cancellation.
    halves=[
      bits([0,1,2,12,3,13,4,23,14,123,24,5,124,34,15,25,6,134,234,125,35,16,26,1234,135,45,235,126,145,36,1235,136]),
      bits([0,1,2,12,3,13,23,123,4,14,24,124,34,5,134,234,15,25,1234,125,35,135,235,6,1235,16,45,145,26,126,36,136])]
    six=[]
    for half in halves:
        p=half+tuple(x^63 for x in reversed(half));checks=term_check(p,6);cc=coherence(p,6);assert not cc['coherent']
        six.append({'order':p,'cancellation_pair_checks':checks,'coherence_certificate':cc,'paired_test':test_all_priorities(p,6)})
    out={'status':'EXACT_PAIRED_BOOLEAN_TERM_ORDER_RELAXATION_PRESSURE',
         'primary_source':'Diane Maclagan, Boolean Term Orders and the Root System B_n, arXiv:math/9809134v2 (10 March1999), Definitions1.1,3.4, Proposition3.7, Section6 and Remark3.10.',
         'scope':'The connected sortedQ5flip component has546 orders, matching the primary-literature total; all546 satisfy translation cancellation. This run does NOT prove all term-order flip graphs connected or all-dimensional completeness. Only30 NONCOHERENTQ5orders and two noncoherentQ6examples are new paired pressure. The coherentQ5base is inherited and not rerun for optimizer minima.',
         'n5_component_orders':546,'n5_directed_flips':directed,'n5_coherent_integer_witnesses':coherent,
         'n5_noncoherent_integer_farkas_certificates':30,'new_n5_paired_scan_cases':3600,
         'n5_noncoherent_paired_minimum':minimum,'n5_orders_and_certificates':rows,
         'n6_examples':six,'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    raw=(json.dumps(out,indent=2)+'\n').encode();Path(__file__).with_name('paired_boolean_term_orders_certificate.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    print(json.dumps({k:v for k,v in out.items() if k not in ('n5_orders_and_certificates','n6_examples')}|{'n6_minima':[x['paired_test']['minimum_all_paired_masks_and_priorities'] for x in six]}),flush=True)

if __name__=='__main__':main()
