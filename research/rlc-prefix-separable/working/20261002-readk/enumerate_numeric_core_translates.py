#!/usr/bin/env python3
"""All additive central translate merges above a fixed numeric upper cone.

LP is a discovery oracle only. Every pruned cone has an exact nonnegative
integer zero-sum certificate, every admitted cone an exact integer interior
point. This is a finite subclass computation, not all Q6 or all dimensions.
"""
import gzip,hashlib,json,time
from fractions import Fraction
from math import lcm
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from verify_paired_sibling_ranks import rank
from verify_gray_reflection_graph import order_and_scores,counts
from verify_symmetric_translate_relaxation import exact_mean,project_word

def oracle(rows):
    A=np.array(rows,dtype=np.int64);n=A.shape[1]
    r=linprog(np.zeros(n),A_ub=-A,b_ub=-np.ones(len(rows)),bounds=[(None,None)]*n,method='highs')
    if r.success:
        ff=[Fraction(float(x)).limit_denominator(1000000) for x in r.x]
        scale=lcm(*(x.denominator for x in ff));w=[int(x*scale) for x in ff]
        assert all(sum(a*b for a,b in zip(row,w))>0 for row in rows)
        return True,w
    assert r.status==2,(r.status,r.message)
    dual=linprog(np.zeros(len(rows)),A_eq=np.vstack([A.T,np.ones(len(rows))]),
        b_eq=np.array([0]*n+[1]),bounds=[(0,None)]*len(rows),method='highs')
    assert dual.success
    ff=[Fraction(float(x)).limit_denominator(1000000) for x in dual.x]
    scale=lcm(*(x.denominator for x in ff));lam=[int(x*scale) for x in ff]
    assert min(lam)>=0 and sum(lam)>0
    assert all(sum(lam[j]*rows[j][h] for j in range(len(rows)))==0 for h in range(n))
    return False,[(j,a) for j,a in enumerate(lam) if a]

def run(n=5,node_limit=100000):
    st=time.monotonic();M=1<<n;N=2*M;mask=2 if n==5 else 0
    rr=[rank(x,n,mask) for x in range(M)]
    def vec(x,side):return [(x>>h)&1 for h in range(n)]+[side]
    # Numeric upper cube order iff v0>0 and vk>sum(vj:j<k).
    initial=[]
    for h in range(n):initial.append([-1 if j<h else int(j==h) for j in range(n)]+[0])
    initial.append([0]*n+[1])
    leaves=[];rejections=[];nodes=0;oracle_calls=0;best=N;complete=True
    def visit(i,j,path,rows):
        nonlocal nodes,oracle_calls,best,complete
        if nodes>=node_limit:complete=False;return
        nodes+=1
        if len(path)==M:
            a=vec((i-1) if path[-1]==0 else (j-1),path[-1])
            central=[1-2*x for x in a]
            finalrows=rows+[central];oracle_calls+=1
            ok,cert=oracle(finalrows)
            if not ok:
                rejections.append({'path':path,'terminal':True,'rows':finalrows,'zero_sum':cert});return
            full=path+[1-x for x in path[::-1]];p=project_word(full,list(range(M)))
            # Oracle variable order is upper bits first, new bottom last.
            w=[cert[-1]]+cert[:-1]
            assert order_and_scores(w)[0]==tuple(p)
            mu=exact_mean(p,rr);best=min(best,mu)
            leaves.append({'half_word':path,'actual_integer_weights':w,'exact_mean':mu})
            return
        for side in [0,1]:
            if side==1 and j>=i:continue
            newrows=rows
            if i!=j:
                first=vec(i,0);second=vec(j,1)
                d=[b-a for a,b in zip(first,second)]
                if side:d=[-x for x in d]
                newrows=rows+[d];oracle_calls+=1;ok,cert=oracle(newrows)
                if not ok:
                    rejections.append({'path':path+[side],'terminal':False,'rows':newrows,'zero_sum':cert});continue
            visit(i+int(side==0),j+int(side==1),path+[side],newrows)
            if not complete:return
    visit(1,0,[0],initial)
    out={'status':'COMPLETE_EXACT_NUMERIC_CORE_TRANSLATE_ENUMERATION' if complete else 'PARTIAL_EXACT_NUMERIC_CORE_TRANSLATE_ENUMERATION',
        'scope':'Fixed numeric upper-order cone only; genuine signed six-dimensional scans outside this cone are NOT covered. Original general target OPEN.',
        'upper_dimension':n,'parent_mask':mask,'nodes':nodes,'node_limit':node_limit,'oracle_calls':oracle_calls,
        'complete':complete,'actual_scan_chambers':len(leaves),'exact_minimum_conditional_mean':best if leaves else None,
        'actual_chamber_witnesses':leaves,'exact_infeasible_branch_certificates':rejections,
        'seconds':time.monotonic()-st,'violations':0}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    raw=(json.dumps(out,indent=2)+'\n').encode()
    Path('numeric_core_translate_certificate.json.gz').write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))
    print(json.dumps({k:v for k,v in out.items() if k not in ['actual_chamber_witnesses','exact_infeasible_branch_certificates']}),flush=True)

if __name__=='__main__':run()
