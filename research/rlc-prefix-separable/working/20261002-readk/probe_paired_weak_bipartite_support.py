#!/usr/bin/env python3
"""Pressure weak-bipartiteness of realizable half SIGNED SUPPORTS.

Alternative capacities are not scan graphs and must never be used as
counterexamples to scan RLC. They can refute the stronger claim that
every such signed support has an integral negative-cycle cover polyhedron.
Every LP witness has exact rational primal/dual verification.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter,defaultdict
import gzip,hashlib,json,random,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csc_matrix
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph
from paired_antipodal_half_graph import split
from paired_complement_half_graph import conditional
from probe_paired_joint_fractional_packing import enumerate_objects,qjson

def test(w,capacities,retain=False):
    n=len(w);p=order_and_scores(w)
    if p is None:return {'n':n,'weights':w,'status':'nongeneric'}
    g=linear_graph(p[0],n);s=split(g,n);original=s['edges'];a=s['root'];r=s['top']
    assert len(capacities)==len(original)
    edges=[(u,v,c*(1 if old>0 else -1)) for (u,v,old),c in zip(original,capacities)]
    try:paths,cycles=enumerate_objects(edges,a,r)
    except OverflowError:return {'n':n,'weights':w,'status':'enumeration_limited'}
    keys=[(u,v) for u,v,c in edges];index={e:i for i,e in enumerate(keys)};cols=[];ii=[];jj=[]
    for j,z in enumerate(cycles):
        es=[index[tuple(sorted((u,v)))] for u,v in zip(z,z[1:]+z[:1])];cols.append(es)
        for i in es:ii.append(i);jj.append(j)
    if cycles:
        mat=csc_matrix((np.ones(len(ii)),(ii,jj)),shape=(len(edges),len(cycles)))
        lp=linprog(-np.ones(len(cycles)),A_ub=mat,b_ub=capacities,bounds=(0,None),method='highs');assert lp.success
        primal=[Fraction(float(v)).limit_denominator(10000) for v in lp.x]
        dual=[Fraction(float(-v)).limit_denominator(10000) for v in lp.ineqlin.marginals]
    else:primal=[];dual=[Fraction(0) for e in edges]
    assert all(v>=0 for v in primal+dual)
    loads=[Fraction(0) for e in edges]
    for j,v in enumerate(primal):
        for i in cols[j]:loads[i]+=v
    assert all(v<=c for v,c in zip(loads,capacities))
    assert all(sum(dual[i] for i in es)>=1 for es in cols)
    pack=sum(primal);assert pack==sum(v*c for v,c in zip(dual,capacities))
    H=sum(capacities);opts=[conditional(edges,n,t) for t in (1,-1)]
    E=max(v[0] for v in opts);phi=(H-E)//2;assert H-E>=0 and (H-E)%2==0
    assert pack<=phi
    out={'n':n,'weights':w,'status':'exact_rational_optimum','original_half_edges':original,
         'alternative_half_edges':edges,'source':a,'sink':r,'capacities':capacities,
         'free_phi':phi,'packing_value':qjson(pack),'free_phi_minus_packing':qjson(Fraction(phi)-pack),
         'half_fixed_root_energies':[v[0] for v in opts],
         'exact_packing':[[cycles[j],qjson(v)] for j,v in enumerate(primal) if v],
         'exact_dual':[(u,v,qjson(dual[i])) for i,(u,v) in enumerate(keys) if dual[i]],
         'all_cycles_sha256':hashlib.sha256(json.dumps(cycles,separators=(',',':')).encode()).hexdigest(),
         'simple_negative_cycles':len(cycles),'attaining_mask_hex':hex(opts[int(opts[1][0]>opts[0][0])][1])}
    if retain or pack<phi:out['all_negative_cycles']=cycles
    return out

def min_fill_width(edges):
    adj=defaultdict(set)
    for a,b,v in edges:adj[a].add(b);adj[b].add(a)
    width=0;trace=[]
    while adj:
        u=min(adj,key=lambda x:(len(adj[x]),x));nb=sorted(adj[u]);width=max(width,len(nb));trace.append((u,nb))
        for a in nb:
            adj[a].remove(u)
            for b in nb:
                if a!=b:adj[a].add(b)
        del adj[u]
    return width,trace

def main():
    start=time.monotonic();rng=random.Random(202610031202);rows=[];gaps=[];hist=Counter();widths=Counter();dig=hashlib.sha256()
    seed=(36014,4119,36488,65387,58395,45969)
    s=split(linear_graph(order_and_scores(seed)[0],6),6)
    branch_sets=((16,24),(28,17,18),(30,25),(31,))
    J={tuple(sorted((a,b))) for a,b,c in s['edges']};seen=set()
    for B in branch_sets:
        assert not seen.intersection(B);seen.update(B)
        reached={B[0]}
        while True:
            bigger=reached|{v for u in reached for v in B if tuple(sorted((u,v))) in J}
            if bigger==reached:break
            reached=bigger
        assert reached==set(B)
    bridges=[]
    for i in range(4):
        for j in range(i+1,4):
            es=[(a,b) for a in branch_sets[i] for b in branch_sets[j] if tuple(sorted((a,b))) in J]
            assert es;bridges.append((i,j,es[0]))
    K4={'weights':seed,'half_edges':s['edges'],'branch_sets':branch_sets,'bridges':bridges,
        'scope':'Genuine generic Q6 half graph contains an unsigned K4 minor; rules out uniform series-parallel/treewidth-two structure, not weak bipartiteness or RLC density.'}
    scans=[seed]
    for n,amount in ((6,64),(7,64),(8,64),(9,64),(10,64),(11,32),(12,32)):
        for t in range(amount):
            if t%3==0:
                w=[(1<<n)+(1<<j) for j in range(n)];rng.shuffle(w)
            else:w=[rng.randrange(1,10000000) for j in range(n)]
            scans.append(tuple(w))
    for index,w in enumerate(scans):
        p=order_and_scores(w)
        if p is None:hist['nongeneric']+=1;continue
        s=split(linear_graph(p[0],len(w)),len(w));width,trace=min_fill_width(s['edges']);widths[width]+=1
        for alternative in (False,True):
            caps=[rng.randrange(1,6) if alternative else 1 for e in s['edges']]
            z=test(w,caps);z['capacity_mode']='fresh_1_to_5' if alternative else 'unit';z['min_degree_fill_width']=width
            rows.append(z);hist[z['status']]+=1;dig.update(json.dumps(z,sort_keys=True).encode())
            if z['status']=='exact_rational_optimum' and z['free_phi_minus_packing'][0]>0:gaps.append(z)
        if index%32==0 or gaps:
            print(json.dumps({'completed_scans':index+1,'status_counts':dict(hist),'exact_cover_gaps':len(gaps),'elapsed':time.monotonic()-start}),flush=True)
        if gaps:break
    out={'status':'WEAK_BIPARTITE_SUPPORT_PRESSURE_WITH_UNSIGNED_K4_EXCLUSION','seed':202610031202,
         'K4_minor_certificate':K4,'counts':dict(hist),'min_degree_fill_width_histogram':dict(widths),'cover_gaps':gaps,
         'scope':'Alternative-capacity cover gaps would refute signed-support idealness, not actual scan frustration. Absence of sampled gaps proves no all-dimensional structural theorem.',
         'rows':rows,'seconds':time.monotonic()-start,'audit_sha256':dig.hexdigest()}
    raw=(json.dumps(out,indent=2)+'\n').encode();Path(__file__).with_name('paired_weak_bipartite_support_pressure.json').write_bytes(raw)
    Path(__file__).with_name('paired_weak_bipartite_support_pressure.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    print(json.dumps({j:v for j,v in out.items() if j not in ('rows','cover_gaps')}),flush=True)

if __name__=='__main__':main()
