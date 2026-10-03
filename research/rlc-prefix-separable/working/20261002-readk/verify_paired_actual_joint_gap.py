#!/usr/bin/env python3
"""Exact audit of a REAL all-dimensional joint path/cycle packing gap.

The verifier does not solve a floating LP: it checks retained rational
certificates, independently enumerates every path/cycle, and exhausts all
active half spins using integer arithmetic. The asymptotic theorem follows
from the finite core and an affine capacity identity, not extrapolation.
"""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction
import gzip,hashlib,json,time
import numpy as np
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph,rank,fast_runs
from paired_antipodal_half_graph import split
from verify_paired_constant_cut_budget import raw_graph

BASE=(10480038,3358564,4427690,18199924,7393112,
      7711178,15108776,968084,2436896,16335859)
BOUNDARY=(508,511)
HERE=Path(__file__).parent

def key(a,b):return tuple(sorted((a,b)))
def q(v):return [v.numerator,v.denominator]

def independent_objects(edges,a,r):
    """Iterative exhaustive vertex-simple walks, with canonical cycles."""
    J={key(u,v):c for u,v,c in edges};adj=defaultdict(set)
    for u,v in J:adj[u].add(v);adj[v].add(u)
    paths=set();cycles=set()
    stack=[(a,(a,),frozenset((a,)))]
    while stack:
        u,z,used=stack.pop()
        if u==r:paths.add(z);continue
        for v in adj[u]-used:stack.append((v,z+(v,),used|{v}))
    for first in sorted(adj):
        stack=[(first,(first,),frozenset((first,)),1)]
        while stack:
            u,z,used,sg=stack.pop()
            if len(z)>=3 and first in adj[u] and z[1]<z[-1]:
                if sg*(1 if J[key(u,first)]>0 else -1)<0:cycles.add(z)
            for v in adj[u]-used:
                if v>first:stack.append((v,z+(v,),used|{v},sg*(1 if J[key(u,v)]>0 else -1)))
    return paths,cycles

def verify_joint(edges,paths,cycles,packing,dual):
    J={key(u,v):c for u,v,c in edges};loads=defaultdict(Fraction)
    y={e:Fraction(0) for e in J};value=Fraction(0)
    for u,v,mass in dual:y[key(u,v)]=Fraction(*mass)
    assert all(mass>=0 for mass in y.values())
    for kind,z,mass in packing:
        mass=Fraction(*mass);z=tuple(z);assert mass>=0
        assert z in (paths if kind=='path' else cycles)
        walk=zip(z,z[1:]) if kind=='path' else zip(z,z[1:]+z[:1])
        for u,v in walk:loads[key(u,v)]+=mass
        value+=mass*(1 if kind=='path' else 2)
    assert all(loads[e]<=abs(c) for e,c in J.items())
    for z in paths:assert sum(y[key(u,v)] for u,v in zip(z,z[1:]))>=1
    for z in cycles:assert sum(y[key(u,v)] for u,v in zip(z,z[1:]+z[:1]))>=2
    upper=sum(abs(c)*y[e] for e,c in J.items());assert value==upper
    return {'value':q(value),'primal':packing,'dual':dual,
            'loads':[(u,v,q(mass)) for (u,v),mass in sorted(loads.items()) if mass]}

def integer_exhaustion(edges):
    """All active half-spin assignments: no ancestor-DP dependence."""
    free=sorted({u for a,b,c in edges for u in (a,b)}-{510,511})
    index={u:i for i,u in enumerate(free)};count=1<<len(free);norm=sum(abs(c) for a,b,c in edges)
    out=[]
    for root in (1,-1):
        best=-10**9;best_state=None;boundary_satisfied_best=None
        for first in range(0,count,32768):
            states=np.arange(first,min(count,first+32768),dtype=np.int64)
            def spin(u):
                return 1 if u==511 else root if u==510 else 1-2*((states>>index[u])&1)
            energy=np.zeros(len(states),dtype=np.int64)
            for u,v,c in edges:energy+=c*spin(u)*spin(v)
            now=int(energy.max())
            if now>best:
                best=now;best_state=int(states[np.flatnonzero(energy==now)[0]])
                boundary_satisfied_best=None
            hit=np.flatnonzero((energy==now)&(spin(508)==1))
            if now==best and len(hit):boundary_satisfied_best=int(states[hit[0]])
        # A boundary-satisfying global optimum must exist; check its exact energy.
        assert boundary_satisfied_best is not None
        negative={free[j] for j in range(len(free)) if boundary_satisfied_best>>j&1}
        if root<0:negative.add(510)
        assert 508 not in negative
        observed=sum(c*(-1 if ((u in negative)!=(v in negative)) else 1) for u,v,c in edges)
        assert observed==best
        out.append({'root_spin':root,'maximum_energy':best,'minimum_frustration':(norm-best)//2,
                    'attaining_negative_vertices':sorted(negative),'assignments_exhausted':count})
    return out

def lifted_half(T,edges):
    return [(u,v,T*c-(T-1 if (u,v)==BOUNDARY else 0)) for u,v,c in edges]

def lift_audit(n,base_edges,base_order,limit_opts):
    m=n-10;T=1<<m;L=sum(BASE)+1
    w=tuple(L*(1<<j) for j in range(m))+BASE
    p,scores=order_and_scores(w);assert p==tuple((x<<m)|row for row in range(T) for x in base_order)
    assert len(set(scores))==1<<n
    g=linear_graph(p,n);h=split(g,n);shift=(1<<(n-1))-512
    expected=tuple((u+shift,v+shift,c) for u,v,c in lifted_half(T,base_edges))
    assert tuple(h['edges'])==expected
    assert (g['D'],g['K'],g['W'])==(338*T,287*T-2,112*T+2)
    # Mirror the two finite-core attaining assignments, retaining top=+1.
    def mirror(u):
        if u==510:return 510
        if u==511:return 511
        q0=512
        for depth in range(1,9):
            off=q0-(1<<(depth+1))
            if off<=u<off+(1<<depth):return off+(1<<depth)-1-(u-off)
        raise AssertionError(u)
    left=set(limit_opts[0]['attaining_negative_vertices'])
    # Top-incident couplings reverse in the complementary half. Negate ALL
    # its non-top spins after mirroring, so shared root a becomes +1 again.
    half_active={u for a,b,c in base_edges for u in (a,b)}-{510,511}
    right={mirror(u) for u in half_active-set(limit_opts[1]['attaining_negative_vertices'])}
    neg={u+shift for u in left|right}
    E=sum(c*(-1 if ((u in neg)!=(v in neg)) else 1) for u,v,c in g['edges'])
    assert E==54*T+2
    result={'n':n,'T':T,'weights':w,'shift':shift,'D':g['D'],'K':g['K'],'W':g['W'],
            'phi':29*T,'packing_value':q(Fraction(28*T)+Fraction(1,2)),
            'strict_gap':q(Fraction(T)-Fraction(1,2)),'R_min':654*T-1,
            'attaining_negative_vertices':sorted(neg),'attaining_energy':E,
            'half_edges_sha256':hashlib.sha256(json.dumps(h['edges']).encode()).hexdigest()}
    if n<=12:
        mask=sum(1<<u for u in neg)
        assert fast_runs([rank(x,n,mask) for x in range(1<<n)],p)==result['R_min']
        result['direct_rank_scan_verified']=True
    return result

def main():
    start=time.monotonic()
    actual=json.loads(gzip.decompress((HERE/'paired_actual_joint_gap_seed_certificate.json.gz').read_bytes()))
    limit=json.loads((HERE/'paired_actual_joint_gap_limit_certificate.json').read_text())
    assert tuple(actual['weights'])==BASE
    p,scores=order_and_scores(BASE);assert len(set(scores))==1024
    g=linear_graph(p,10);raw=raw_graph(p,10)
    assert all(raw[k]==g[k] for k in ('D','K','W','edges'))
    assert (g['D'],g['K'],g['W'])==(338,285,114)
    h=split(g,10);edges=h['edges'];assert [list(e) for e in edges]==actual['half_edges']
    paths,cycles=independent_objects(edges,510,511)
    assert (len(paths),len(cycles))==(490,2148)
    retained_paths={tuple(z) for kind,z,reward in actual['all_objects'] if kind=='path'}
    retained_cycles={tuple(z) for kind,z,reward in actual['all_objects'] if kind=='cycle'}
    assert paths==retained_paths and cycles==retained_cycles
    actual_verified=verify_joint(edges,paths,cycles,actual['exact_packing'],actual['exact_dual'])
    assert actual_verified['value']==[57,2]
    lim_edges=[(u,v,c-int((u,v)==BOUNDARY)) for u,v,c in edges]
    assert [list(e) for e in lim_edges]==limit['edges']
    lim_verified=verify_joint(lim_edges,paths,cycles,limit['joint']['primal'],limit['joint']['dual'])
    assert lim_verified['value']==[28,1]
    actual_opts=integer_exhaustion(edges);limit_opts=integer_exhaustion(lim_edges)
    assert [z['minimum_frustration'] for z in actual_opts]==[11,18]
    assert [z['minimum_frustration'] for z in limit_opts]==[11,18]
    # The base dual also gives the correct limiting optimum and boundary slope.
    y={key(u,v):Fraction(*v0) for u,v,v0 in actual['exact_dual']}
    assert y[BOUNDARY]==Fraction(1,2)
    assert sum(abs(c)*y.get(key(u,v),0) for u,v,c in lim_edges)==28
    # For EVERY real T>=1: combine base packing and (T-1)*limit packing.
    # Capacity and value identities are exact affine equalities.
    combined={}
    for kind,z,mass in actual['exact_packing']:combined[(kind,tuple(z))]=[Fraction(*mass),Fraction(0)]
    for kind,z,mass in limit['joint']['primal']:
        k=kind,tuple(z);combined.setdefault(k,[Fraction(0),Fraction(0)])[1]+=Fraction(*mass)
    affine=[(kind,z,q(slope),q(base-slope)) for (kind,z),(base,slope) in sorted(combined.items())]
    rows=[lift_audit(n,edges,p,limit_opts) for n in range(10,19)]
    out={'status':'VERIFIED_REAL_ALL_DIMENSION_LINEAR_JOINT_PACKING_GAP','base_weights':BASE,
         'analytic_statement':'For every n>=10, T=2^(n-10), genuine generic low-tail weights have phi=29T, max(P+2C)=28T+1/2, gap=T-1/2=2^n/1024-1/2, and fixed-scan paired-family minimum 654T-1.',
         'scope':'Refutes actual-scan joint exactness and any uniform additive O(n) repair. Does NOT refute D+K+packing>=c*2^n, any quarter bound, or the main M_n target.',
         'half_edges':edges,'limiting_half_edges':lim_edges,
         'independent_simple_paths':len(paths),'independent_negative_cycles':len(cycles),
         'actual_rational_certificate':actual_verified,'limiting_rational_certificate':lim_verified,
         'independent_actual_integer_exhaustion':actual_opts,'independent_limit_integer_exhaustion':limit_opts,
         'all_T_affine_packing_objects_kind_vertices_slope_intercept':affine,
         'real_lift_audits':rows,'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    (HERE/'paired_actual_joint_gap_verified_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','analytic_statement','scope','independent_simple_paths','independent_negative_cycles','violations','seconds','audit_sha256')}),flush=True)

if __name__=='__main__':main()
