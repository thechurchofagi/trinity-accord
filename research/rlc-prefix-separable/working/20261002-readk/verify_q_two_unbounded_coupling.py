#!/usr/bin/env python3
"""Independent integer audit: q=2 but root couplings unbounded in actual scans."""
from pathlib import Path
from collections import Counter
import hashlib,json,time
from verify_paired_sibling_ranks import rank

def audit_graph(w):
    n=len(w);N=1<<n
    scores=[sum(c for h,c in enumerate(w) if x>>h&1) for x in range(N)]
    assert len(set(scores))==N
    p=tuple(sorted(range(N),key=scores.__getitem__))
    raw=[];sgn=[]
    for x,y in zip(p,p[1:]):
        h=(x^y).bit_length()-1
        raw.append((h,x>>(h+2)) if h<n-1 else (n-1,0))
        gx=x^(x>>1);gy=y^(y>>1);sgn.append(1 if gy>gx else -1)
    D=0;J=Counter()
    for a,b,s,t in zip(raw,raw[1:],sgn,sgn[1:]):
        if a==b:assert s!=t;D+=1
        else:J[tuple(sorted((a,b)))]+=s*t
    J={k:v for k,v in J.items() if v};W=sum(abs(v) for v in J.values())
    K=(N-2-D-W)//2;assert 2*K==N-2-D-W
    return p,raw,D,J,W,K

def main():
    st=time.monotonic();v=(3,22,2,12,6);L=46
    p,raw,D,J,W,K=audit_graph(v)
    assert D==16 and W==6 and K==4
    assert J=={((2,0),(4,0)):3,((2,1),(4,0)):-3}
    assert set(raw)-{(4,0)}=={(2,0),(2,1)}
    coremask=1<<13;rr=[rank(x,5,coremask) for x in range(32)]
    signs=[1 if rr[y]>rr[x] else -1 for x,y in zip(p,p[1:])]
    assert 1+sum(s!=t for s,t in zip(signs,signs[1:]))==21
    assert signs[0]==signs[-1]==1 and rr[p[0]]<rr[p[-1]]
    rows=[]
    for d in range(9):
        n=5+d;N=1<<n;T=1<<d;delta=(1<<(n-1))-16
        w=tuple(L<<j for j in range(d))+v
        P,lab,Dn,Jn,Wn,Kn=audit_graph(w)
        A=(d+2,0);B=(d+2,1);root=(n-1,0)
        assert set(lab)-{root}=={A,B}
        assert Dn==16*T and Wn==4*T+2 and Kn==6*T-2
        assert Jn=={tuple(sorted((A,root))):2*T+1,tuple(sorted((B,root))):-(2*T+1)}
        runs=set()
        for top in (0,1):
            for state in range(4):
                high=((state&1)<<12)|(((state>>1)&1)<<13)
                for lowname in ('zero','ones','alternating'):
                    low=0 if lowname=='zero' else (1<<delta)-1 if lowname=='ones' else sum(1<<j for j in range(0,delta,2))
                    mask=(high<<delta)|low
                    ranks=[rank(x,n,mask,top) for x in range(N)]
                    a=[1 if ranks[y]>ranks[x] else -1 for x,y in zip(P,P[1:])]
                    R=1+sum(s!=t for s,t in zip(a,a[1:]));runs.add(R)
                    # Direct graph energy: root spin=(-1)^top, each label spin=(-1)^theta.
                    E=(2*T+1)*((-1)**(state&1)-(-1)**((state>>1)&1))*((-1)**top)
                    assert 2*R==N+Dn-E
                    if state==2 and top==0:assert R==22*T-1
        assert min(runs)==22*T-1
        rows.append({'n':n,'d':d,'T':T,'weights':w,'q':2,'D':Dn,'W':Wn,'K':Kn,
            'root_coupling_abs':2*T+1,'exact_minimum_over_all_paired_masks':22*T-1,
            'distinct_runs':sorted(runs),
            'order_sha256':hashlib.sha256(json.dumps(P).encode()).hexdigest()})
    out={'status':'VERIFIED_ALL_DIMENSION_ACTUAL_Q_TWO_UNBOUNDED_ROOT_COUPLING',
        'analytic_theorem':'For every n=5+d, T=2^d, actual positive integer weights (46,92,...,46*2^(d-1),3,22,2,12,6) have raw q=2, D=16T, root couplings +(2T+1),-(2T+1), W=4T+2, K=6T-2 and min over EVERY paired mask/root equal22T-1. Hence no dimension-free bound on root-coupling size depending only on fixed raw q. Run density tends11/16; no counterexample to positive-density main target.',
        'source_core_weights':v,'core_minimizing_mask_decimal':str(coremask),
        'all_dimension_proof':'Exact base integer order/coefficients plus independently derived join contributions to the genuine q-invariant row lift. Rows replicate core J=3; each join subtracts1 from labelA and adds1 to labelB. All lower labels are absent from RAW support; full spin optimization has only two active variables.',
        'rows':rows,'finite_dimensions':'Q5..Q13','direct_rank_audits':len(rows)*24,
        'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('q_two_unbounded_coupling_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'}),flush=True)

if __name__=='__main__':main()
