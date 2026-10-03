#!/usr/bin/env python3
"""Audit formula certificates; no chamber enumeration or sampling theorem."""
from pathlib import Path
from collections import Counter
import hashlib,json,time
from verify_gray_reflection_graph import order_and_scores,counts
from verify_paired_sibling_ranks import linear_graph,rank,fast_runs
from paired_sibling_ancestor_optimizer import optimize,plain_optimize
from paired_complement_half_graph import decompose,terminal_cut
from paired_periodic_overlap import weights,explicit_order,normal_graph,leaf,backbone,packing_certificate,attaining_mask


def main():
    start=time.monotonic();rows=[];digest=hashlib.sha256()
    for n in range(5,19):
        N=1<<n;T=1<<(n-5);w=weights(n);out=order_and_scores(w);assert out is not None
        p=explicit_order(n);assert p==out[0] and sorted(p)==list(range(N))
        observed=linear_graph(p,n);model=normal_graph(n);assert observed==model
        assert sum(abs(c) for u,v,c in model['edges'])==N-6
        cert=packing_certificate(model,n,keep_cycles=n<=7)
        mask,E,field=attaining_mask(model,n);assert E==N//2-2
        phi=(model['W']-E)//2;assert phi==cert['value']==N//4-2
        r=[rank(x,n,mask) for x in range(N)]
        assert sorted(r)==list(range(N)) and fast_runs(r,p)==N//4+1
        R,C,_=counts([r[x] for x in p]);assert R==N//4+1
        if n<=12:
            z=optimize(model,n);assert z['E_max']==E
        if n<=7:assert plain_optimize(model,n)[0]==E
        H,root,a,tau=decompose(model,n);cut,part=terminal_cut(H,root,a)
        assert cut==(6 if n==5 else 2)
        if n>=6:
            j=T//2-1
            paths=((root,leaf(n,j,1,1,0),a),(root,leaf(n,j+1,0,0,0),a))
            J={tuple(sorted((u,v))):c for u,v,c in H};loads=Counter()
            for path in paths:
                for u,v in zip(path,path[1:]):loads[tuple(sorted((u,v)))]+=1
            assert all(v<=abs(J[k]) for k,v in loads.items())
            assert sum(abs(c) for u,v,c in H if a in(u,v))==2
        else:paths=None
        row={'n':n,'T':T,'weights':w,'D':0,'K':2,'W':model['W'],'cut':cut,'cut_budget':2+cut,
             'phi':phi,'R_min_family':R,'C_at_explicit_witness':C,'E_max':E,
             'packing_parts':cert['parts'],'unused_capacities':cert['unused_capacities'],
             'field_histogram':dict(sorted(Counter(field).items())),'terminal_paths':paths,
             'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest(),
             'graph_sha256':hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest(),
             'mask_sha256':hashlib.sha256(mask.to_bytes((mask.bit_length()+7)//8,'little')).hexdigest()}
        if n<=7:row.update(attaining_mask=mask,edges=model['edges'],cycles=cert['cycles'],order=p)
        rows.append(row);digest.update(json.dumps(row,sort_keys=True).encode())
        print(json.dumps({k:row[k] for k in('n','D','K','W','cut','phi','R_min_family')}),flush=True)
    result={'rows':rows,'seconds':time.monotonic()-start,'audit_digest':digest.hexdigest(),
            'scope':'Analytic all-dimensional periodic construction. Finite audits check every vertex and coupling for listed n=5..18, full exact DP through n=12. No main M_n resolution.'}
    Path(__file__).with_name('paired_periodic_overlap_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)

if __name__=='__main__':main()
