#!/usr/bin/env python3
"""Exact rational primal/dual pressure for compatible half path/cycle packing.

The floating-point LP is only a candidate generator. Every reported
optimum is validated with Fraction arithmetic against ALL enumerated
simple terminal paths and ALL simple negative cycles. This is a finite
audit and never an all-dimensional lower-bound proof.
"""
from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction
import gzip,hashlib,json,random,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csc_matrix
from verify_gray_reflection_graph import order_and_scores,positive_chambers
from verify_paired_sibling_ranks import linear_graph
from paired_antipodal_half_graph import split
from paired_sibling_ancestor_optimizer import optimize

def enumerate_objects(edges,source,sink,limit=200000):
    J={tuple(sorted((a,b))):v for a,b,v in edges};adj=defaultdict(list)
    for a,b in J:adj[a].append(b);adj[b].append(a)
    for a in adj:adj[a].sort()
    paths=[];cycles=[];steps=0
    def path(z):
        nonlocal steps
        steps+=1
        if steps>limit:raise OverflowError('complete enumeration limit')
        if z[-1]==sink:paths.append(tuple(z));return
        for b in adj[z[-1]]:
            if b not in z:path(z+[b])
    path([source]);steps=0
    def cycle(z,sign):
        nonlocal steps
        steps+=1
        if steps>limit:raise OverflowError('complete enumeration limit')
        for b in adj[z[-1]]:
            sg=1 if J[tuple(sorted((z[-1],b)))]>0 else -1
            if b==z[0] and len(z)>=3 and z[1]<z[-1]:
                if sign*sg<0:cycles.append(tuple(z))
            elif b>z[0] and b not in z:cycle(z+[b],sign*sg)
    for a in sorted(adj):cycle([a],1)
    assert len(set(paths))==len(paths) and len(set(cycles))==len(cycles)
    return paths,cycles

def qjson(v):return [v.numerator,v.denominator]

def solve(w,retain=False):
    n=len(w);p=order_and_scores(w)
    if p is None:return {'n':n,'weights':w,'status':'nongeneric'}
    g=linear_graph(p[0],n);half=split(g,n);edges=half['edges'];a=half['root'];r=half['top']
    opt=optimize(g,n);phi=(g['W']-opt['E_max'])//2
    try:paths,cycles=enumerate_objects(edges,a,r)
    except OverflowError:return {'n':n,'weights':w,'status':'enumeration_limited','phi':phi}
    keys=[(u,v) for u,v,c in edges];index={e:i for i,e in enumerate(keys)};caps=[abs(c) for u,v,c in edges]
    objects=[('path',z,1) for z in paths]+[('cycle',z,2) for z in cycles]
    columns=[];ii=[];jj=[]
    for j,(kind,z,reward) in enumerate(objects):
        pairs=zip(z,z[1:]) if kind=='path' else zip(z,z[1:]+z[:1])
        es=[index[tuple(sorted((u,v)))] for u,v in pairs];columns.append(es)
        for i in es:ii.append(i);jj.append(j)
    if objects:
        matrix=csc_matrix((np.ones(len(ii)),(ii,jj)),shape=(len(edges),len(objects)))
        lp=linprog([-reward for kind,z,reward in objects],A_ub=matrix,b_ub=caps,bounds=(0,None),method='highs')
        assert lp.success
        primal=[Fraction(float(v)).limit_denominator(10000) for v in lp.x]
        dual=[Fraction(float(-v)).limit_denominator(10000) for v in lp.ineqlin.marginals]
    else:primal=[];dual=[Fraction(0) for e in edges]
    assert all(v>=0 for v in primal+dual)
    loads=[Fraction(0) for e in edges]
    for j,v in enumerate(primal):
        for i in columns[j]:loads[i]+=v
    assert all(v<=cap for v,cap in zip(loads,caps))
    assert all(sum(dual[i] for i in es)>=objects[j][2] for j,es in enumerate(columns))
    primal_value=sum(v*objects[j][2] for j,v in enumerate(primal));dual_value=sum(v*cap for v,cap in zip(dual,caps))
    assert primal_value==dual_value<=phi
    budget=Fraction(g['D']+g['K'])+primal_value
    out={'n':n,'weights':w,'status':'exact_rational_optimum','D':g['D'],'K':g['K'],'W':g['W'],
         'phi':phi,'R_min':1+g['D']+g['K']+phi,'half_edges':edges,'source':a,'sink':r,
         'simple_paths':len(paths),'simple_negative_cycles':len(cycles),
         'packing_value':qjson(primal_value),'phi_minus_packing':qjson(Fraction(phi)-primal_value),
         'D_K_plus_packing':qjson(budget),'quarter_budget':(1<<n)//4,
         'exact_packing':[[objects[j][0],objects[j][1],qjson(v)] for j,v in enumerate(primal) if v],
         'exact_dual':[(u,v,qjson(dual[i])) for i,(u,v) in enumerate(keys) if dual[i]],
         'object_list_sha256':hashlib.sha256(json.dumps(objects,separators=(',',':')).encode()).hexdigest()}
    if retain or primal_value<phi or budget<(1<<n)//4:out['all_objects']=objects
    return out

def main():
    start=time.monotonic();rng=random.Random(202610031145);rows=[];gaps=[];fails=[];counts=Counter();digest=hashlib.sha256()
    scans=list(positive_chambers(4))
    scans += [(16,1,6,8,4),(1,6,8,4,20),(1,14,4,8,16),(34,36,40,33,48)]
    for n,amount in ((5,256),(6,128),(7,32)):
        for t in range(amount):
            if t%3==0:
                B=1<<n;w=[B+(1<<j) for j in range(n)];rng.shuffle(w)
            else:w=[rng.randrange(1,100000) for j in range(n)]
            scans.append(tuple(w))
    for index,w in enumerate(scans):
        z=solve(w,retain=w in ((16,1,6,8,4),(1,6,8,4,20)));rows.append(z);counts[z['status']]+=1
        digest.update(json.dumps(z,sort_keys=True).encode())
        if z['status']=='exact_rational_optimum':
            if z['phi_minus_packing'][0]>0:gaps.append(z)
            if Fraction(*z['D_K_plus_packing'])<z['quarter_budget']:fails.append(z)
        if index%64==0 or (z['status']=='exact_rational_optimum' and z['phi_minus_packing'][0]>0):
            print(json.dumps({'completed':index+1,'counts':dict(counts),'exactness_gaps':len(gaps),'quarter_failures':len(fails),'elapsed':time.monotonic()-start}),flush=True)
    out={'status':'EXACT_RATIONAL_JOINT_PACKING_PRESSURE_ONLY','seed':202610031145,'counts':dict(counts),
         'all_positive_Q4_representative_metrics':336,'coverage_warning':'Higher dimensions are finite samples; enumeration-limited cases certify no packing optimum.',
         'exactness_gaps':gaps,'quarter_failures':fails,'rows':rows,'seconds':time.monotonic()-start,'audit_sha256':digest.hexdigest()}
    raw=(json.dumps(out,indent=2)+'\n').encode()
    Path(__file__).with_name('paired_joint_fractional_pressure.json').write_bytes(raw)
    Path(__file__).with_name('paired_joint_fractional_pressure.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    print(json.dumps({j:v for j,v in out.items() if j not in ('exactness_gaps','quarter_failures','rows')}),flush=True)

if __name__=='__main__':main()
