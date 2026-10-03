#!/usr/bin/env python3
"""LP-free exact covering-tree audit and signed/permuted cone transfer.

All branch inequalities are reconstructed from scratch. A finite cover of
the entire central-shuffle tree is verified using integer zero-sum cuts or
integer actual scan witnesses. No LP result/status is trusted.
"""
import gzip,hashlib,json,time
from itertools import permutations
from pathlib import Path
import numpy as np
from verify_paired_sibling_ranks import rank
from verify_gray_reflection_graph import order_and_scores
from verify_symmetric_translate_relaxation import project_word,exact_mean
from probe_selected_parent_conditional_minima import conditional_vector

def main():
    st=time.monotonic();blob=Path('numeric_core_translate_certificate.json.gz').read_bytes()
    c=json.loads(gzip.decompress(blob));assert c['complete'] and c['upper_dimension']==5
    claimed=c.pop('audit_sha256');assert hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()==claimed
    M=32;n=5;initial=[[-1 if j<h else int(j==h) for j in range(n)]+[0] for h in range(n)]+[[0]*n+[1]]
    reject={tuple(r['path']):r for r in c['exact_infeasible_branch_certificates']}
    leaves={tuple(r['half_word']):r for r in c['actual_chamber_witnesses']}
    assert len(reject)==len(c['exact_infeasible_branch_certificates'])
    assert len(leaves)==len(c['actual_chamber_witnesses']) and not (set(reject)&set(leaves))
    visited_reject=set();visited_leaf=set();nodes=0
    def vec(i,b):return [(i>>h)&1 for h in range(n)]+[b]
    def visit(i,j,path,rows):
        nonlocal nodes
        nodes+=1;p=tuple(path)
        if p in reject:
            r=reject[p];checkrows=rows
            if r['terminal']:
                assert len(path)==M
                a=vec(i-1 if path[-1]==0 else j-1,path[-1]);checkrows=rows+[[1-2*x for x in a]]
            assert checkrows==r['rows']
            lam=dict(r['zero_sum']);assert len(lam)==len(r['zero_sum']) and sum(lam.values())>0
            assert all(0<=k<len(checkrows) and v>0 for k,v in lam.items())
            assert all(sum(checkrows[k][h]*v for k,v in lam.items())==0 for h in range(6))
            visited_reject.add(p);return
        if len(path)==M:
            assert p in leaves
            r=leaves[p];w=r['actual_integer_weights'];params=w[1:]+w[:1]
            a=vec(i-1 if path[-1]==0 else j-1,path[-1]);checkrows=rows+[[1-2*x for x in a]]
            assert all(sum(a*b for a,b in zip(row,params))>0 for row in checkrows)
            full=path+[1-x for x in path[::-1]];order=project_word(full,list(range(M)))
            assert order_and_scores(w)[0]==tuple(order)
            rr=[rank(x,5,2) for x in range(32)]
            assert exact_mean(order,rr)==r['exact_mean']
            visited_leaf.add(p);return
        for side in [0,1]:
            if side==1 and j>=i:continue
            newrows=rows
            if i!=j:
                first=vec(i,0);second=vec(j,1);d=[b-a for a,b in zip(first,second)]
                if side:d=[-x for x in d]
                newrows=rows+[d]
            visit(i+int(side==0),j+int(side==1),path+[side],newrows)
    visit(1,0,[0],initial)
    assert visited_reject==set(reject) and visited_leaf==set(leaves)
    assert min(r['exact_mean'] for r in leaves.values())==c['exact_minimum_conditional_mean']==28
    # All signed/permuted upper lex cones share the same geometric cover.
    # Coordinate maps need not preserve the fixed paired hierarchy: transform
    # the rank table directly rather than silently permuting its hierarchy.
    rr=[];maps=[]
    for perm in permutations(range(5)):
        for z in range(32):
            mp=[sum(((x>>h)&1)<<perm[h] for h in range(5))^z for x in range(32)]
            rr.append([rank(mp[x],5,2) for x in range(32)]);maps.append((perm,z))
    rr=np.array(rr,dtype=np.uint8);minima=np.full(len(rr),64,dtype=np.int64)
    args=[None]*len(rr);stream=hashlib.sha256()
    for k,r in enumerate(leaves.values()):
        p=np.array(order_and_scores(r['actual_integer_weights'])[0]);mu=conditional_vector(p,rr)
        for i in np.flatnonzero(mu<minima):args[int(i)]=r['actual_integer_weights']
        minima=np.minimum(minima,mu);stream.update(bytes(map(int,mu)))
        if (k+1)%2000==0:print(json.dumps({'certified_base_cones':k+1,'minimum_so_far':int(minima.min())}),flush=True)
    i=int(np.argmin(minima));perm,z=maps[i];basew=args[i]
    w=[basew[0]]+[0]*5
    for h,coord in enumerate(perm):w[coord+1]=basew[h+1]*(-1 if (z>>coord)&1 else 1)
    p=order_and_scores(w)[0];original=[rank(x,5,2) for x in range(32)]
    assert exact_mean(p,original)==int(minima[i])
    out={'status':'LP_FREE_VERIFIED_COMPLETE_SIGNED_PERMUTED_UPPER_LEX_CONES',
        'scope':'ANY genuine Q6 weights whose absolute upper-five weights are superincreasing in SOME coordinate order. New bottom weight arbitrary nonzero (reflection preserves fresh-label mean). Not all generic Q6 weights; not all-dimensional M_n.',
        'compressed_certificate_sha256':hashlib.sha256(blob).hexdigest(),
        'source_audit_sha256':claimed,'cover_tree_nodes_checked':nodes,
        'exact_integer_zero_sum_cuts':len(reject),'base_actual_cones':len(leaves),
        'all_signed_permuted_upper_maps':len(maps),'map_cone_pairs':len(maps)*len(leaves),
        'unsigned_numeric_minimum_mean':28,'all_signed_permuted_minimum_mean':int(minima.min()),
        'attaining_original_actual_signed_weights':w,
        'per_map_conditional_minima':minima.tolist(),'audit_stream_sha256':stream.hexdigest(),
        'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('numeric_core_translate_independent_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='per_map_conditional_minima'}),flush=True)

if __name__=='__main__':main()
