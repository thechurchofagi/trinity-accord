#!/usr/bin/env python3
"""Exact audit of half reduction, integer cuts, and an unbalanced half family."""
from pathlib import Path
from itertools import product
import hashlib,json,random,time
from collections import Counter
from verify_gray_reflection_graph import positive_chambers,order_and_scores
from verify_paired_sibling_ranks import linear_graph,rank,fast_runs
from paired_sibling_ancestor_optimizer import optimize,plain_optimize
from paired_antipodal_half_graph import split,certificate

def audit(w,exhaust=False):
    n=len(w);N=1<<n;p,scores=order_and_scores(w)
    assert len(set(scores))==N
    assert all(p[N-1-i]==(p[i]^(N-1)) for i in range(N))
    g=linear_graph(p,n);c=certificate(g,n);z=optimize(g,n)
    assert c['E_max']==z['E_max']
    root=split(g,n)['root']
    for bit,mask in enumerate(c['full_attaining_masks_by_root']):
        assert ((mask>>root)&1)==bit
        assert fast_runs([rank(x,n,mask) for x in range(N)],p)==c['R_min']
    if n<=6:assert plain_optimize(g,n)[0]==z['E_max']
    if exhaust:
        by_root=[-10**9,-10**9]
        for mask in range(1<<((N//2)-1)):
            energy=sum(v*(-1 if ((mask>>a)^(mask>>b))&1 else 1) for a,b,v in g['edges'])
            bit=(mask>>root)&1;by_root[bit]=max(by_root[bit],energy)
        assert by_root==[c['E_max'],c['E_max']]
        c['exhaustive_energy_by_root']=by_root
    c.update(weights=w,n=n,D=g['D'],K=g['K'],W=g['W'],
             graph_edges=g['edges'],order_sha256=hashlib.sha256(json.dumps(p).encode()).hexdigest(),
             full_dp_table_sha256=z['table_sha256'])
    return c

def main():
    start=time.monotonic();digest=hashlib.sha256();rows=[];summaries=[];rng=random.Random(202610031101)
    for n in range(2,5):
        h=Counter();num=0;kept=set();balance_hist=Counter()
        for positive in positive_chambers(n):
            for reflection in range(1<<n):
                w=[(-a if (reflection>>j)&1 else a) for j,a in enumerate(positive)]
                c=audit(w,exhaust=n<=3)
                if n<=3:assert c['half_balance']['balanced']
                balance_hist[c['half_balance']['balanced']]+=1
                h[c['half_cut']['value']]+=1;num+=1
                digest.update(json.dumps(c,sort_keys=True).encode())
                key=(c['half_cut']['value'],c['half_balance']['balanced'])
                if key not in kept:rows.append(c);kept.add(key)
        summaries.append({'n':n,'all_signed_scan_chambers':num,'half_cut_histogram':dict(h),'balanced_unbalanced_histogram':dict(balance_hist)})
        print(json.dumps(summaries[-1]),flush=True)
    random_num=0;reject=0;balanced=0;unbalanced=0
    for n in range(5,11):
        for trial in range(24):
            w=[rng.choice((-1,1))*z for z in rng.sample(range(1,100001),n)]
            if order_and_scores(w) is None:reject+=1;continue
            c=audit(w);random_num+=1
            balanced+=int(c['half_balance']['balanced']);unbalanced+=int(not c['half_balance']['balanced'])
            digest.update(json.dumps(c,sort_keys=True).encode())
            if trial<2:rows.append(c)
    w=[1,6,8,4];lift_rows=[];previous=None
    for n in range(4,13):
        if n>4:w=w+[1+sum(w)]
        c=audit(w);assert not c['half_balance']['balanced']
        s=split(linear_graph(order_and_scores(w)[0],n),n)
        if n==4:cycle=c['half_balance']['negative_cycle'];assert cycle==[7,0,6,1]
        else:
            from paired_sibling_ancestor_optimizer import layout
            oldtop,oldnodes,oldinfo=layout(n-1);top,nodes,info=layout(n)
            def embed(u):
                if u==oldtop:return nodes[(0,0)]
                d,p=oldinfo[u];return nodes[(d+1,p)]
            cycle=[embed(u) for u in previous]
        J={tuple(sorted((a,b))):v for a,b,v in s['edges']};signed_edges=[];prod=1
        for a,b in zip(cycle,cycle[1:]+cycle[:1]):
            value=J[tuple(sorted((a,b)))];prod*=1 if value>0 else -1;signed_edges.append((a,b,value))
        assert prod==-1
        c['persistent_lift_cycle']=cycle;c['persistent_lift_cycle_edges']=signed_edges
        if n>4:assert [v for a,b,v in signed_edges]==old_values
        old_values=[v for a,b,v in signed_edges];previous=cycle
        lift_rows.append(c);digest.update(json.dumps(c,sort_keys=True).encode())
        print(json.dumps({'lift_n':n,'cycle':cycle,'cycle_signed_edges':signed_edges,'R_min':c['R_min']}),flush=True)
    out={'status':'VERIFIED_ANALYTIC_HALF_REDUCTION_AND_GENERAL_CUT_PACKING',
         'scope':'The identities and cut packing hold in all dimensions by proof. Complete signed scan chambers audited through n=4. The already known genuine four-dimensional negative cycle is the dimension-minimal unbalanced half and lifts to every n>=4. No universal positive-density lower bound proved.',
         'complete_small_summaries':summaries,'representative_certificates':rows,
         'random_seed':202610031101,'random_generic_scans':random_num,'random_nongeneric_rejections':reject,
         'random_balanced':balanced,'random_unbalanced':unbalanced,'unbalanced_lifts':lift_rows,
         'violations':0,'seconds':time.monotonic()-start,'audit_sha256':digest.hexdigest()}
    Path(__file__).with_name('paired_antipodal_half_graph_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('representative_certificates','complete_small_summaries','unbalanced_lifts')}),flush=True)

if __name__=='__main__':main()
