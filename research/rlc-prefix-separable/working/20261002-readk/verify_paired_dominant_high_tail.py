#!/usr/bin/env python3
"""Exact audit of a proved four-boundary-state recurrence, not chamber coverage."""
from pathlib import Path
import hashlib,json,time
from itertools import product
from collections import defaultdict
from verify_gray_reflection_graph import order_and_scores,counts
from verify_paired_sibling_ranks import linear_graph,rank
from paired_sibling_ancestor_optimizer import optimize,layout
from paired_complement_half_graph import decompose,terminal_cut

STATES=tuple(product((1,-1),repeat=2))

def seed_profile():
    F={}
    for s,t in STATES:
        F[s,t]=max(s*(b+a-1)+2*abs(b+a)+abs(a-b)+t*(c+a+1)+2*abs(c+a)+abs(a-c)
                   for a,b,c in product((1,-1),repeat=3))
    assert F=={(1,1):12,(1,-1):6,(-1,1):10,(-1,-1):12}
    return F


def grow(F):
    out={};choices={}
    for s,t in STATES:
        candidates=[]
        for a,u,v in product((1,-1),repeat=3):
            # Shared old top spin a; second copy negates its top incidences.
            value=(F[s,u] if a==1 else F[-s,-u])+(F[-v,-t] if a==1 else F[v,t])-u+v
            candidates.append((value,(a,u,v)))
        out[s,t],choices[s,t]=max(candidates)
    return out,choices


def embedding_check(old,new,n):
    oldr,oldnodes,info=layout(n);r,nodes,_=layout(n+1);a=nodes[(0,0)]
    J=defaultdict(int)
    def image(u,side):
        if u==oldr:return a
        d,p=info[u];return nodes[(d+1,p+side*(1<<d))]
    for side in (0,1):
        for u,v,c in old['edges']:
            sign=-1 if side and oldr in(u,v) else 1
            J[tuple(sorted((image(u,side),image(v,side))))]+=sign*c
    endpoint=(1<<(n-2))-1
    J[tuple(sorted((r,image(endpoint,0))))]-=1
    J[tuple(sorted((r,image(0,1))))]+=1
    expected=tuple((u,v,c) for (u,v),c in sorted(J.items()) if c)
    assert expected==new['edges']
    assert new['D']==2*old['D']==0 and new['K']==2*old['K']
    assert new['W']==2*old['W']+2


def main():
    start=time.monotonic();F=seed_profile();rows=[];digest=hashlib.sha256();previous=None
    for n in range(5,13):
        T=1<<(n-5);w=(1,14,4,8,16)+tuple(44*(1<<j) for j in range(n-5))
        p=order_and_scores(w)[0];core=order_and_scores(w[:5])[0]
        assert p==tuple((row<<5)|x for row in range(T) for x in core)
        g=linear_graph(p,n);z=optimize(g,n);H,r,a,tau=decompose(g,n);cut,_=terminal_cut(H,r,a)
        if previous is not None:embedding_check(previous,g,n-1)
        assert (g['D'],g['K'],g['W'],cut)==(0,6*T,20*T-2,1)
        E=max(F.values());c=1 if n%2 else 2;phi=(10*T-c)//3;R=(28*T+3-c)//3
        assert 10*T-c==3*phi and 28*T+3-c==3*R
        assert E==z['E_max']==g['W']-2*phi
        RR,CC,_=counts([rank(x,n,z['mask']) for x in p]);assert RR==R
        # Exact nonnegative negative-cycle packing inherited independently per row.
        oldr,oldnodes,oldinfo=layout(5);_,nodes,_=layout(n)
        def image(u,row):
            if u==oldr:return nodes[(n-6,row>>1)] if n>5 else r
            d,P=oldinfo[u];return nodes[(d+n-5,(row<<d)|P)]
        cycles=((14,1,12,2),(14,6,13,5),(14,0,15,7));J={tuple(sorted((u,v))):v0 for u,v,v0 in g['edges']};loads=defaultdict(int)
        for row in range(T):
            for cy in cycles:
                cy=tuple(image(u,row) for u in cy);sgn=1
                for u,v in zip(cy,cy[1:]+cy[:1]):
                    key=tuple(sorted((u,v)));sgn*=1 if J[key]>0 else -1;loads[key]+=1
                assert sgn==-1
        assert all(amount<=abs(J[key]) for key,amount in loads.items()) and phi>=3*T
        profile={(str(s)+','+str(t)):F[s,t] for s,t in STATES}
        row={'n':n,'T':T,'weights':w,'D':0,'K':6*T,'W':g['W'],'cut':1,'phi':phi,'R_min':R,
             'C_at_DP_witness':CC,'attaining_mask':z['mask'],'boundary_profile':profile,
             'cut_budget':6*T+1,'quarter_budget':8*T,'seed_cycle_packing':3*T,
             'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest()}
        rows.append(row);digest.update(json.dumps(row,sort_keys=True).encode());print(json.dumps({k:v for k,v in row.items() if k not in('attaining_mask','weights','boundary_profile')}),flush=True)
        previous=g;F,_=grow(F)
    # Beyond any vertex enumeration, verify the two algebraic profile forms
    # on representative arbitrary integer energy scales.
    for A in (0,1,12,10**20):
        odd={(1,1):A,(1,-1):A-2,(-1,1):A-2,(-1,-1):A}
        even={(1,1):2*A,(1,-1):2*A-2,(-1,1):2*A+2,(-1,-1):2*A}
        assert grow(odd)[0]==even
        assert grow(even)[0]=={(1,1):4*A+4,(1,-1):4*A+2,(-1,1):4*A+2,(-1,-1):4*A+4}
    result={'rows':rows,'audit_digest':digest.hexdigest(),'seconds':time.monotonic()-start,
            'scope':'All-dimensional recurrence proved analytically; finite audit n=5..12 checks genuine scans, graph embedding, optima and cycle capacities. No main constant-density claim.'}
    Path(__file__).with_name('paired_dominant_high_tail_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)

if __name__=='__main__':main()
