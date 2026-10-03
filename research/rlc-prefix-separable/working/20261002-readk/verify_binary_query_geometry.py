#!/usr/bin/env python3
"""Exact audits, separated from the analytic all-dimensional proof."""
import hashlib,json,time,random
from pathlib import Path
from functools import lru_cache
from itertools import product,permutations
from math import comb
from adaptive_query_research import rank_table,direct_counts,graph,validate,additive_order,exact_orientation_minimum,random_queries,separator
from adaptive_query_exact_optimizer import exact_minimum
from binary_query_geometry import *

def all_queries(free,u=1):
    if not free:yield {};return
    for j in free:
        rem=tuple(k for k in free if k!=j)
        for a,b in product(all_queries(rem,2*u),all_queries(rem,2*u+1)):
            yield {u:j,**a,**b}

def independent_rank(q,n,bits):
    order=[]
    def visit(u,x,used):
        if len(used)==n:order.append(x);return
        j=q[u];assert j not in used
        for b in (bits.get(u,0),1-bits.get(u,0)):
            visit(2*u+b,x|(b<<j),used+(j,))
    visit(1,0,());assert sorted(order)==list(range(1<<n))
    r=[0]*(1<<n)
    for i,x in enumerate(order):r[x]=i
    return r,order

def full_mask_values(n):
    full=(1<<n)-1
    @lru_cache(None)
    def solve(free,j):
        fixed=full^free;d=free.bit_count()
        m=(fixed&-fixed).bit_length()-1 if fixed else n
        own=(2**(d-j-1)-2**(d-m)) if j<m else 0
        rem=free^(1<<j)
        if not rem:return own
        values=sorted(solve(rem,k) for k in range(n) if rem>>k&1)
        return own+(sum(values[:2]) if len(values)>1 else 2*values[0])
    return [solve(full,j) for j in range(n)],solve.cache_info().currsize

@lru_cache(None)
def constructed_cost(m,h):
    if m<=1:return 0
    if h:return constructed_cost(m,h-1)+constructed_cost(m-1,h)
    return constructed_cost(m-1,0)+1+constructed_cost(m-2,1)

@lru_cache(None)
def constructed_active_pair(m,h):
    if m==0:return 0
    if h:return 1+constructed_active_pair(m,h-1)+constructed_active_pair(m-1,h)
    if m==1:return 2
    return 2+constructed_active_pair(m-1,0)+constructed_active_pair(m-2,1)

def prefix_audit(q,n,bits):
    rr,order=independent_rank(q,n,bits);checks=0
    for k in range(1,1<<n):
        z=order[k];c=separator(q,n,bits,z)
        for x in range(1<<n):
            score=sum(c[j]*(((x>>j)&1)-((z>>j)&1)) for j in range(n))
            assert score<=-1 if rr[x]<k else score>=0
            checks+=1
    return checks

def main():
    started=time.monotonic();stream=hashlib.sha256();checks=0;counts=[]
    # All unrestricted geometries, not only locally-distinct ones.
    # Coordinate permutation covers every positive superincreasing priority.
    for n in range(1,5):
        total=0;active_words=0
        for q in all_queries(tuple(range(n))):
            base=direct_counts(rank_table(q,n),range(1<<n))[1]
            exact=exact_minimum(q,n,list(range(1<<n)))
            brute=exact_orientation_minimum(q,n,list(range(1<<n)))[3]
            assert exact['C']==base==brute['min_C']
            formula,active=controller_cost(q,n)
            assert formula==base and graph(q,n,list(range(1<<n)),True)['q']==active
            active_words+=1<<brute['q'];total+=1;checks+=1
            stream.update(json.dumps((n,sorted(q.items()),base,exact['table_sha256']),sort_keys=True).encode())
        counts.append({'n':n,'all_unrestricted_geometries':total,'exact_active_orientation_words':active_words})
    boundary_checks=0
    for f0,l0,f1,l1,z0,z1,t in product((-1,1),repeat=7):
        v=-t
        local=(l0!=z0)+(z0!=f0)+(l1!=z1)+(z1!=f1)
        global_cost=(l0!=t)+(t!=f1)+(l1!=v)+(v!=f0)
        assert global_cost-local>=-2;boundary_checks+=1
    # Independent full-subset DP versus reduced integer state (m,h).
    table=[]
    for n in range(1,15):
        values,states=full_mask_values(n);best,reduced=minimum_binary_cyclic(n)
        assert values==reduced
        table.append({'n':n,'minimum_over_all_local_geometries_and_orientations_for_binary_scan':best,
                      'forced_root_costs':values,'full_subset_states':states})
    bigger=[]
    for n in range(15,65):
        v,_=minimum_binary_cyclic(n);bigger.append({'n':n,'exact_binary_geometry_minimum':v})
    rng=random.Random(202610032125);random_checks=0
    for n in range(3,10):
        for _ in range(50):
            q=random_queries(n,rng);priority=list(range(n));rng.shuffle(priority)
            weights=[0]*n
            for j,c in enumerate(priority):weights[c]=1<<j
            p=additive_order(weights)
            assert exact_minimum(q,n,p)['C']==direct_counts(rank_table(q,n),p)[1]
            random_checks+=1
    q7=optimal_queries(7);validate(q7,7);r7,o7=independent_rank(q7,7,{})
    assert direct_counts(r7,range(128))==(25,26)
    assert exact_minimum(q7,7,list(range(128)))['C']==26
    prefix_checks=prefix_audit(q7,7,{})
    sparse=[]
    for n in range(2,17):
        q,k=sparse_queries(n);validate(q,n)
        rr,_=independent_rank(q,n,{})
        R,C=direct_counts(rr,range(1<<n));formula,active=controller_cost(q,n)
        h=n-k-1
        assert C==formula==(1<<(n-k))+2*constructed_cost(k,h)
        assert active==constructed_active_pair(k,h) and R==C-1
        bound=sparse_bounds(n,k)
        assert C<=bound['C_upper'] and active<=bound['q_upper']
        if n<=12:
            g=graph(q,n,list(range(1<<n)),True)
            assert g['q']==active and g['D']+g['K']+active<=bound['budget_upper']
        sparse.append({'n':n,'root':k,'R':R,'C':C,'active_q':active,**bound,
                       'query_sha256':hashlib.sha256(json.dumps(sorted(q.items())).encode()).hexdigest()})
    state_bound_checks=0
    for m in range(21):
        for h in range(41):
            b=constructed_cost(m,h);a=constructed_active_pair(m,h)
            assert b<=2**m*comb(m+h,m)
            assert a+1<=2**(m+1)*comb(m+h,m)
            state_bound_checks+=1
    # Positive weights without superincreasing dominance invalidate extension.
    q3={1:1,2:2,3:0,4:0,5:0,6:2,7:2};w=(177,314,284)
    bits={3:1};p=additive_order(w);r0,_=independent_rank(q3,3,{});r1,_=independent_rank(q3,3,bits)
    validate(q3,3)
    assert direct_counts(r0,p)[1]==6 and direct_counts(r1,p)[1]==4
    prefix_checks+=prefix_audit(q3,3,bits)
    counter={'weights':w,'queries':sorted(q3.items()),'bits':bits,'scan':p,
             'baseline_rank_word':[r0[x] for x in p],'attaining_rank_word':[r1[x] for x in p],
             'baseline_C':6,'attaining_C':4}
    out={'status':'EXACT_BINARY_QUERY_GEOMETRY_AUDIT','all_unrestricted_small_checks':counts,
         'exact_contexts':checks,'boundary_checks':boundary_checks,'full_and_reduced_dp':table,
         'larger_reduced_dp_only':bigger,'random_exact_binary_contexts':random_checks,
         'q7_strict_counterexample':{'queries':sorted(q7.items()),'weights':[1<<j for j in range(7)],
                                   'bits':{},'R':25,'C':26,'rank_word':r7},
         'sparse_family_direct_audits':sparse,'state_bound_checks':state_bound_checks,
         'integer_prefix_vertex_checks':prefix_checks,'non_superincreasing_obstruction':counter,
         'stream_sha256':stream.hexdigest(),'violations':0,'seconds':time.monotonic()-started,
         'scope':'All-n statements require accompanying analytic proof. Binary-scan geometry minima are not M_n or all-generic minima. Local universal quarter and universal positive density are false; existential main target stays OPEN.'}
    out['receipt_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('binary_query_geometry_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('q7_strict_counterexample','sparse_family_direct_audits','full_and_reduced_dp','larger_reduced_dp_only','non_superincreasing_obstruction')}),flush=True)
    for row in table:print(json.dumps(row),flush=True)
    for row in sparse:print(json.dumps(row),flush=True)
if __name__=='__main__':main()
