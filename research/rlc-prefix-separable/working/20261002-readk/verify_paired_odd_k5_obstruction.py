#!/usr/bin/env python3
"""Independent hard-coded signed odd-K5 witness and capacity-gap certificates.

The REAL scan is used only to certify its signed support and actual
capacity optimum. Alternative positive capacities are explicitly diagnostic.
Matching exact rational LP certificates never rely on a floating tolerance.
"""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction
from itertools import combinations,product
import gzip,hashlib,json,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csc_matrix
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph
from paired_antipodal_half_graph import split
from paired_complement_half_graph import conditional
from probe_paired_joint_fractional_packing import enumerate_objects,qjson

BASE=(5240019,1679282,2213845,9099962,3696556,3855589,7554388,484042,1218448,8372834)
BRANCHES=((448,449,496),(456,457,459,463,482,486,497,498,505,508),(462,499,510),(504,),(511,))
NEGATIVE_GAUGE={456,463,486,508,510}
TREES=(((448,496),(449,496)),((456,505),(457,505),(459,505),(463,505),(482,508),(486,508),(505,508),(498,505),(497,508)),((462,499),(462,510)),(),())
BRIDGES=((0,1,496,508),(0,2,449,510),(0,3,448,504),(0,4,496,511),(1,2,463,499),(1,3,497,504),(1,4,456,511),(2,3,510,504),(2,4,499,511),(3,4,504,511))

def key(a,b):return tuple(sorted((a,b)))
def gauge(u):return -1 if u in NEGATIVE_GAUGE else 1

def tree_path(i,source,sink):
    adj=defaultdict(list)
    for u,v in TREES[i]:adj[u].append(v);adj[v].append(u)
    parent={source:None};queue=deque([source])
    while queue and sink not in parent:
        u=queue.popleft()
        for v in adj[u]:
            if v not in parent:parent[v]=u;queue.append(v)
    assert sink in parent;z=[];v=sink
    while v is not None:z.append(v);v=parent[v]
    return list(reversed(z))

def triangle_cycle(triangle):
    endpoints={}
    for i,j,u,v in BRIDGES:endpoints[i,j]=(u,v);endpoints[j,i]=(v,u)
    i,j,k=triangle;a,b=endpoints[i,j];c,d=endpoints[j,k];e,f=endpoints[k,i]
    z=[a,b]+tree_path(j,b,c)[1:]+[d]+tree_path(k,d,e)[1:]+[f]+tree_path(i,f,a)[1:]
    assert z[-1]==z[0];z=z[:-1];assert len(set(z))==len(z)
    return z

def verify_minor(edges,shift=0):
    J={key(a,b):(1 if c>0 else -1) for a,b,c in edges};seen=set()
    for i,B in enumerate(BRANCHES):
        assert not seen.intersection(B);seen.update(B)
        assert len(TREES[i])==len(B)-1
        for u,v in TREES[i]:assert gauge(u)*J[key(u+shift,v+shift)]*gauge(v)==1
        for v in B:tree_path(i,B[0],v)
    assert len({(i,j) for i,j,u,v in BRIDGES})==10
    for i,j,u,v in BRIDGES:
        assert u in BRANCHES[i] and v in BRANCHES[j]
        assert gauge(u)*J[key(u+shift,v+shift)]*gauge(v)==-1
    return True

def lift_audit(n):
    m=n-10;T=1<<m;w=tuple((sum(BASE)+1)*(1<<j) for j in range(m))+BASE
    p,scores=order_and_scores(w);oldp=order_and_scores(BASE)[0]
    assert p==tuple((x<<m)|row for row in range(T) for x in oldp)
    g=linear_graph(p,n);h=split(g,n);shift=(1<<(n-1))-512;verify_minor(h['edges'],shift)
    return {'n':n,'weights':w,'T':T,'variable_shift':shift,'D':g['D'],'K':g['K'],'W':g['W'],
            'all_bridges':[(i,j,u+shift,v+shift) for i,j,u,v in BRIDGES],
            'half_support_sha256':hashlib.sha256(json.dumps(h['edges']).encode()).hexdigest()}

def verify_packing(edges,cycles,paths=()):
    J={key(a,b):c for a,b,c in edges};load=defaultdict(Fraction)
    for z,mass in cycles:
        sg=1
        for u,v in zip(z,z[1:]+z[:1]):sg*=1 if J[key(u,v)]>0 else -1;load[key(u,v)]+=mass
        assert sg==-1
    for z,mass in paths:
        for u,v in zip(z,z[1:]):load[key(u,v)]+=mass
    assert all(v<=abs(J[e]) for e,v in load.items())
    return [(u,v,qjson(mass)) for (u,v),mass in sorted(load.items())]

def exact_joint_lp(edges,objects):
    index={key(u,v):i for i,(u,v,c) in enumerate(edges)};cols=[];ii=[];jj=[];caps=[abs(c) for u,v,c in edges]
    for j,(kind,z,reward) in enumerate(objects):
        walk=zip(z,z[1:]) if kind=='path' else zip(z,z[1:]+z[:1])
        es=[index[key(u,v)] for u,v in walk];cols.append(es)
        for i in es:ii.append(i);jj.append(j)
    mat=csc_matrix((np.ones(len(ii)),(ii,jj)),shape=(len(edges),len(objects)))
    lp=linprog([-reward for kind,z,reward in objects],A_ub=mat,b_ub=caps,bounds=(0,None),method='highs');assert lp.success
    primal=[Fraction(float(v)).limit_denominator(10000) for v in lp.x]
    dual=[Fraction(float(-v)).limit_denominator(10000) for v in lp.ineqlin.marginals]
    assert all(v>=0 for v in primal+dual);loads=[Fraction(0) for e in edges]
    for j,mass in enumerate(primal):
        for i in cols[j]:loads[i]+=mass
    assert all(mass<=cap for mass,cap in zip(loads,caps))
    assert all(sum(dual[i] for i in es)>=objects[j][2] for j,es in enumerate(cols))
    value=sum(mass*objects[j][2] for j,mass in enumerate(primal));assert value==sum(y*cap for y,cap in zip(dual,caps))
    return {'value':qjson(value),'primal':[(objects[j][0],objects[j][1],qjson(v)) for j,v in enumerate(primal) if v],
            'dual':[(u,v,qjson(dual[i])) for i,(u,v,c) in enumerate(edges) if dual[i]],
            'loads':[(u,v,qjson(loads[i])) for i,(u,v,c) in enumerate(edges) if loads[i]]}

def diagnostic():
    actual=split(linear_graph(order_and_scores(BASE)[0],10),10)['edges'];verify_minor(actual)
    tree_keys={key(u,v) for tree in TREES for u,v in tree};bridge_keys={key(u,v) for i,j,u,v in BRIDGES}
    assert len(tree_keys)==13 and len(bridge_keys)==10 and not tree_keys.intersection(bridge_keys)
    J={key(u,v):c for u,v,c in actual};selected=[(u,v,(11 if e in tree_keys else 1)*(1 if J[e]>0 else -1)) for e in sorted(tree_keys|bridge_keys) for u,v in [e]]
    paths,cycles=enumerate_objects(selected,510,511);free_dual={e:(Fraction(1,3) if e in bridge_keys else Fraction(0)) for e in tree_keys|bridge_keys}
    special=key(499,511);joint_dual={e:(Fraction(1) if e==special else Fraction(2,3) if e in bridge_keys else Fraction(0)) for e in tree_keys|bridge_keys}
    def length(z,y,close):
        walk=zip(z,z[1:]+z[:1]) if close else zip(z,z[1:])
        return sum(y[key(u,v)] for u,v in walk)
    assert all(length(z,free_dual,True)>=1 and length(z,joint_dual,True)>=2 for z in cycles)
    assert all(length(z,joint_dual,False)>=1 for z in paths)
    all_triangles=[(triangle_cycle(t),Fraction(1,3)) for t in combinations(range(5),3)]
    free_loads=verify_packing(selected,all_triangles)
    assert sum(abs(c)*free_dual[key(u,v)] for u,v,c in selected)==Fraction(10,3)
    other=(0,1,3);joint_cycles=[(triangle_cycle((terminal,a,b)),Fraction(1,2)) for terminal in (2,4) for a,b in combinations(other,2)]
    joint_path=[510,462,499,511];joint_loads=verify_packing(selected,joint_cycles,[(joint_path,Fraction(1))])
    assert sum(abs(c)*joint_dual[key(u,v)] for u,v,c in selected)==7
    costs=[]
    for spins in product((1,-1),repeat=4):
        sigma=[*spins,1];negative={u for i,B in enumerate(BRANCHES) for u in B if gauge(u)*sigma[i]<0}
        cost=sum(abs(c) for u,v,c in selected if ((-1 if (u in negative)!=(v in negative) else 1)*(1 if c>0 else -1))<0)
        costs.append((sigma,cost))
    assert min(c for s,c in costs)==4
    assert all(min(c for s,c in costs if s[2]==r)==4 for r in (1,-1))
    # A violated positive branch-tree edge costs 11>10, so no optimum violates one.
    opts=[conditional(selected,10,t)[0] for t in (1,-1)];H=sum(abs(c) for u,v,c in selected)
    assert [(H-E)//2 for E in opts]==[4,4]
    # Keep EVERY original edge with a strictly positive integer capacity.
    Q=100;positive=[(u,v,(1100 if key(u,v) in tree_keys else 100 if key(u,v) in bridge_keys else 1)*(1 if c>0 else -1)) for u,v,c in actual]
    absent=set(J)-(tree_keys|bridge_keys);assert len(absent)==15
    full_paths,full_cycles=enumerate_objects(actual,510,511)
    free_y={e:(Fraction(1) if e in absent else free_dual[e]) for e in J}
    joint_y={e:(Fraction(2) if e in absent else joint_dual[e]) for e in J}
    assert all(length(z,free_y,True)>=1 and length(z,joint_y,True)>=2 for z in full_cycles)
    assert all(length(z,joint_y,False)>=1 for z in full_paths)
    free_upper=sum(abs(c)*free_y[key(u,v)] for u,v,c in positive)
    joint_upper=sum(abs(c)*joint_y[key(u,v)] for u,v,c in positive)
    assert free_upper==Fraction(1045,3)<400 and joint_upper==730<800
    opts_pos=[conditional(positive,10,t)[0] for t in (1,-1)];Hp=sum(abs(c) for u,v,c in positive)
    phi_pos=[(Hp-E)//2 for E in opts_pos];assert min(phi_pos)>=400 and sum(phi_pos)>=800
    objects=[('path',z,1) for z in full_paths]+[('cycle',z,2) for z in full_cycles]
    pos_joint=exact_joint_lp(positive,objects);assert Fraction(*pos_joint['value'])<sum(phi_pos)
    return {'actual_half_edges':actual,'selected_diagnostic_edges':selected,'all_original_positive_capacity_diagnostic_edges':positive,
            'branch_sets':BRANCHES,'negative_gauge_indices':sorted(NEGATIVE_GAUGE),'positive_branch_trees':TREES,'ten_negative_bridges':BRIDGES,
            'selected_free_phi':4,'selected_fractional_cycle_packing':qjson(Fraction(10,3)),
            'selected_full_two_copy_phi':8,'selected_fractional_joint_packing':7,
            'ten_triangle_cycles':[(z,qjson(v)) for z,v in all_triangles],'free_cycle_loads':free_loads,
            'six_half_mass_joint_cycles':[(z,qjson(v)) for z,v in joint_cycles],'joint_unit_path':joint_path,'joint_combined_loads':joint_loads,
            'selected_simple_negative_cycles':len(cycles),'selected_simple_paths':len(paths),
            'all_original_simple_negative_cycles':len(full_cycles),'all_original_simple_paths':len(full_paths),
            'positive_diagnostic_free_phi_by_root':phi_pos,'positive_diagnostic_free_packing_exact_upper':qjson(free_upper),
            'positive_diagnostic_joint_explicit_upper':int(joint_upper),'positive_diagnostic_joint_exact_LP':pos_joint,
            'positive_diagnostic_joint_gap':qjson(Fraction(sum(phi_pos))-Fraction(*pos_joint['value'])),
            'scope':'Alternative capacities are NOT actual scan couplings. They refute uniform signed-support idealness and arbitrary-capacity joint exactness, not the main M_n or actual-scan joint density target.'}

def verify_actual_certificate(actual):
    edges=split(linear_graph(order_and_scores(BASE)[0],10),10)['edges']
    assert [list(e) for e in edges]==actual['half_edges']
    paths,cycles=enumerate_objects(edges,510,511)
    objects=[('path',z,1) for z in paths]+[('cycle',z,2) for z in cycles]
    assert hashlib.sha256(json.dumps(objects,separators=(',',':')).encode()).hexdigest()==actual['object_list_sha256']
    pset=set(paths);cset=set(cycles);packed_paths=[];packed_cycles=[];value=Fraction(0)
    for kind,z,mass in actual['exact_packing']:
        z=tuple(z);mass=Fraction(*mass);assert mass>=0
        assert z in (pset if kind=='path' else cset)
        (packed_paths if kind=='path' else packed_cycles).append((list(z),mass))
        value+=mass*(1 if kind=='path' else 2)
    verify_packing(edges,packed_cycles,packed_paths)
    y={key(u,v):Fraction(0) for u,v,c in edges}
    for u,v,q in actual['exact_dual']:y[key(u,v)]=Fraction(*q)
    assert all(q>=0 for q in y.values())
    for z in paths:assert sum(y[key(u,v)] for u,v in zip(z,z[1:]))>=1
    for z in cycles:assert sum(y[key(u,v)] for u,v in zip(z,z[1:]+z[:1]))>=2
    assert value==sum(abs(c)*y[key(u,v)] for u,v,c in edges)==21
    H=sum(abs(c) for u,v,c in edges);F=[]
    for spin in (1,-1):
        E,mask=conditional(edges,10,spin)
        assert sum(c*(-1 if ((mask>>u)^(mask>>v))&1 else 1) for u,v,c in edges)==E
        F.append(E)
    assert sum((H-E)//2 for E in F)==21
    return {'value':qjson(value),'half_integer_energies':F,'enumerated_paths':len(paths),'enumerated_negative_cycles':len(cycles),'all_primal_dual_inequalities_verified':True}

def main():
    start=time.monotonic();d=diagnostic();rows=[lift_audit(n) for n in range(10,19)]
    actual=json.loads(gzip.decompress(Path(__file__).with_name('paired_odd_k5_actual_joint_certificate.json.gz').read_bytes()))
    assert tuple(actual['weights'])==BASE and actual['packing_value']==[21,1] and actual['phi']==21
    independent_actual=verify_actual_certificate(actual)
    out={'status':'VERIFIED_ALL_DIMENSION_REAL_SIGNED_ODD_K5_SUPPORT_OBSTRUCTION_WITH_DIAGNOSTIC_CAPACITY_GAPS',
         'weights':BASE,'diagnostic':d,'real_weight_joint_packing':{k:v for k,v in actual.items() if k!='all_objects'},
         'independent_actual_capacity_audit':independent_actual,'all_dimension_support_lifts':rows,'violations':0,'seconds':time.monotonic()-start,
         'audit_sha256':hashlib.sha256(json.dumps((d,rows),sort_keys=True).encode()).hexdigest()}
    Path(__file__).with_name('paired_odd_k5_obstruction_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('diagnostic','real_weight_joint_packing','all_dimension_support_lifts')}),flush=True)
    print(json.dumps({k:d[k] for k in ('selected_free_phi','selected_fractional_cycle_packing','selected_full_two_copy_phi','selected_fractional_joint_packing','positive_diagnostic_free_phi_by_root','positive_diagnostic_free_packing_exact_upper','positive_diagnostic_joint_explicit_upper','positive_diagnostic_joint_exact_LP','positive_diagnostic_joint_gap') if k!='positive_diagnostic_joint_exact_LP'}),flush=True)

if __name__=='__main__':main()
