#!/usr/bin/env python3
"""Exact raw-turn certificates for the analytic cardinality/numeric theorem.

Finite audits check the formulas; the all-dimensional proof is in the
accompanying note. No claim of covering arbitrary additive scans.
"""
from pathlib import Path
from collections import defaultdict
import hashlib,json,time
from verify_paired_sibling_ranks import rank,linear_graph,fast_runs
from verify_paired_all_lex_quarter import labels_signs
from paired_sibling_ancestor_optimizer import optimize,plain_optimize

def certify(n):
    N=1<<n;weights=[N+(1<<j) for j in range(n)]
    scores=[sum(weights[j] for j in range(n) if (x>>j)&1) for x in range(N)]
    assert len(set(scores))==N
    p=sorted(range(N),key=scores.__getitem__)
    assert p==sorted(range(N),key=lambda x:(x.bit_count(),x))
    pos={x:i for i,x in enumerate(p)};labels,signs=labels_signs(p,n)
    g=linear_graph(p,n);pairs=[];loads=defaultdict(int)
    def triple(v):
        i=pos[v[0]]
        assert p[i:i+3]==list(v),('not consecutive',n,v)
        return i
    def raw(i):
        a,b=labels[i:i+2];assert a!=b
        return tuple(sorted((a,b))),signs[i]*signs[i+1]
    for t in range(1,n-1):
        for P in range(1<<(n-t-2)):
            U=P<<(t+2)
            A=(U+(1<<(t-1)),U+(1<<t),U+(1<<(t+1)))
            B=(U+(1<<(t+1))-1,
               U+(1<<(t+1))+(1<<t)-1,
               U+(1<<(t+1))+(1<<t)+(1<<(t-1))-1)
            a,b=triple(A),triple(B)
            aa,sa=raw(a);bb,sb=raw(b)
            assert aa==bb and sa==-sb
            pairs.append((a,b));loads[aa]+=1
    assert len(pairs)==N//4-1
    forced=[triple((N//4,N//2,3)),triple((N-4,N//2-1,3*N//4-1))]
    for i in forced:assert labels[i]==labels[i+1] and signs[i]==-signs[i+1]
    used=forced+[i for pp in pairs for i in pp]
    assert len(used)==len(set(used))
    products=defaultdict(lambda:[0,0]);D=0
    for i in range(N-2):
        if labels[i]==labels[i+1]:
            D+=1;assert signs[i]==-signs[i+1]
        else:
            key,s=raw(i);products[key][int(s<0)]+=1
    assert D==g['D'] and D>=2
    assert all(load<=min(products[key]) for key,load in loads.items())
    assert sum(min(z) for z in products.values())==g['K']>=N//4-1
    digest=hashlib.sha256(json.dumps((p,forced,pairs,sorted(loads.items()),g),separators=(',',':')).encode()).hexdigest()
    result={'n':n,'weights':weights,'D':D,'K':g['K'],'W':g['W'],
            'matching_count':len(pairs),'forced_indices':forced,
            'certified_all_family_lower_bound':N//4+2,'certificate_sha256':digest}
    if n<=8:result.update(order=p,opposite_raw_pairs=pairs,pair_loads=[(a,b,v) for (a,b),v in sorted(loads.items())])
    if n<=12:
        z=optimize(g,n);phi=(g['W']-z['E_max'])//2
        assert g['W']-z['E_max']>=0 and (g['W']-z['E_max'])%2==0
        r=[rank(x,n,z['mask']) for x in range(N)]
        R=fast_runs(r,p)
        assert R==1+D+g['K']+phi>=N//4+2
        if n<=8:assert plain_optimize(g,n)[0]==z['E_max']
        result.update(optimum=z,phi=phi,exact_family_minimum_R=R)
    if n<=4:
        minimum=min(fast_runs([rank(x,n,m) for x in range(N)],p) for m in range(1<<(N//2-1)))
        assert minimum==result['exact_family_minimum_R']
        result['exhaustive_rank_masks']=1<<(N//2-1)
    return result

def main():
    start=time.monotonic();rows=[]
    for n in range(3,19):
        row=certify(n);rows.append(row)
        print(json.dumps({k:row[k] for k in ('n','D','K','matching_count','certified_all_family_lower_bound')},sort_keys=True),flush=True)
    output={'status':'VERIFIED_ALL_DIMENSION_RESTRICTED_SCAN_THEOREM',
            'theorem':'Every paired-sibling rank has at least 2^(n-2)+2 runs for n>=3 on the cardinality-first, within-layer numerical scan, and its coordinate reflections.',
            'scope':'This is one restricted scan class. Arbitrary cardinality perturbations and arbitrary generic additive scans remain open.',
            'rows':rows,'violations':0,'seconds':time.monotonic()-start}
    output['rows_sha256']=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('paired_cardinality_numeric_certificate.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k!='rows'},sort_keys=True),flush=True)

if __name__=='__main__':main()
