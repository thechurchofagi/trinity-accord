#!/usr/bin/env python3
"""Every cube ranking admits a genuine additive monotone block of length n.

This excludes a proposed dimension-free maximum-run-length shortcut.
It does not bound the total number of runs or refute a density lower bound.
"""
import hashlib,json,time
from itertools import permutations
from pathlib import Path
from verify_paired_sibling_ranks import rank
from verify_gray_reflection_graph import order_and_scores

def certificate(rr,n):
    N=1<<n;B=N;delta=[B*rr[1<<h]+(1<<h) for h in range(n)]
    M=1+sum(delta);w=[M+a for a in delta]
    p,scores=order_and_scores(w)
    assert len(set(scores))==N
    onehots=list(p[1:n+1]);assert set(onehots)=={1<<h for h in range(n)}
    assert [rr[x] for x in onehots]==sorted(rr[1<<h] for h in range(n))
    assert all(p[i].bit_count()<=p[i+1].bit_count() for i in range(N-1))
    return {'n':n,'weights':w,'B':B,'M':M,'onehot_order':onehots,
        'strictly_increasing_rank_block':[rr[x] for x in onehots]}

def main():
    st=time.monotonic();stream=hashlib.sha256();counts=[]
    for n in [1,2,3]:
        k=0
        for rr in permutations(range(1<<n)):
            c=certificate(rr,n);stream.update(json.dumps((rr,c),sort_keys=True).encode());k+=1
        counts.append({'n':n,'all_arbitrary_rankings':k})
    for n in [4,5]:
        k=0
        for m in range(1<<((1<<(n-1))-1)):
            c=certificate([rank(x,n,m) for x in range(1<<n)],n)
            stream.update(json.dumps((n,m,c),sort_keys=True).encode());k+=1
        counts.append({'n':n,'all_normalized_paired_rankings':k})
    large=[]
    for n in range(6,17):
        # These are illustrations of the analytic arbitrary-ranking theorem.
        rr=[x^(x>>1) for x in range(1<<n)];large.append(certificate(rr,n))
    out={'status':'VERIFIED_UNIVERSAL_UNBOUNDED_MONOTONE_BLOCK',
        'analytic_theorem':'For EVERYdimension n and EVERYranking of Q_n, explicit positive generic additive weights yield a consecutive strictly increasing rank block of n one-hot vertices. B=2^n, delta_i=B*rho(e_i)+2^i, M=1+sum(delta_i), w_i=M+delta_i. Hence no choice of rankings has a dimension-free maximum monotone segment length over ALLgenuine scans.',
        'scope':'Elementary simplex/cardinality construction, not a new concentration method. Does NOT bound total runs or refute M_n>=c*2^n; the protected block occupies only n vertices.',
        'small_complete_audits':counts,'larger_dimension_examples':large,
        'audit_stream_sha256':stream.hexdigest(),'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('universal_long_monotone_block_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='larger_dimension_examples'}),flush=True)

if __name__=='__main__':main()
