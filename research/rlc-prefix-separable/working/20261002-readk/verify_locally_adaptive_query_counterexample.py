#!/usr/bin/env python3
"""Solver-free independent audit of a genuine Q5 linear quarter counterexample."""
import hashlib,json
from pathlib import Path

def main():
    x=json.loads(Path('locally_adaptive_query_pressure.json').read_text())['quarter_counterexample']
    n=x['n'];N=1<<n;q=dict(x['queries']);bits=dict(x['orientation_bits']);w=x['signed_weights']
    assert n==5 and bits.get(1,0)==0
    # Independent recursive traversal, not the heap-rank formula.
    paths={}
    def visit(u,free,base,path):
        if not free:paths[base]=path;return [base]
        j=q[u];assert j in free;rest=tuple(k for k in free if k!=j)
        if len(rest)>=2:assert q[2*u]!=q[2*u+1]
        lo=visit(2*u,rest,base,path+((j,bits.get(u,0)),))
        hi=visit(2*u+1,rest,base|(1<<j),path+((j,bits.get(u,0)),))
        return hi+lo if bits.get(u,0) else lo+hi
    traversal=visit(1,tuple(range(n)),0,());rr=[0]*N
    for k,a in enumerate(traversal):rr[a]=k
    scores=[sum(w[h]*((a>>h)&1) for h in range(n)) for a in range(N)]
    assert len(set(scores))==N;p=sorted(range(N),key=scores.__getitem__)
    rankword=[rr[a] for a in p];signs=[1 if b>a else -1 for a,b in zip(rankword,rankword[1:])]
    R=1+sum(a!=b for a,b in zip(signs,signs[1:]));full=signs+[1 if rankword[0]>rankword[-1] else -1]
    C=sum(full[i]!=full[(i+1)%N] for i in range(N));assert (R,C)==(7,8)
    assert p==x['scan'] and rankword==x['rank_word']
    separators=[]
    for k in range(1,N):
        z=traversal[k];c=[0]*n
        for t,(j,b) in enumerate(paths[z]):c[j]=(-1 if b else 1)*3**(n-1-t)
        values=[sum(c[j]*(((a>>j)&1)-((z>>j)&1)) for j in range(n)) for a in range(N)]
        assert max(values[a] for a in range(N) if rr[a]<k)<=-1
        assert min(values[a] for a in range(N) if rr[a]>=k)>=0
        separators.append({'prefix_size':k,'boundary_vertex':z,'coefficients':c,'threshold_for_centered_score':'-1/2'})
    out={'status':'EXACT_ACTUAL_Q5_LINEAR_QUARTER_COUNTEREXAMPLE','n':n,'queries':x['queries'],'orientation_bits':x['orientation_bits'],
         'signed_weights':w,'scores_by_vertex':scores,'scan':p,'rank_word':rankword,'R':R,'C':C,'all_strict_prefix_separators':separators,
         'scope':'Refutes universal R>=2^n/4 from local child-query inequality. C=8 does NOT refute C>=2^n/4 or asymptotic positive-density existence.',
         'prefix_vertex_checks':(N-1)*N,'violations':0}
    out['receipt_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('locally_adaptive_query_counterexample_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k in ('status','signed_weights','R','C','scope','prefix_vertex_checks','violations','receipt_sha256')}))
if __name__=='__main__':main()
