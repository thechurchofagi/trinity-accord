#!/usr/bin/env python3
"""Solver-free genuine joint packing gap and exact all-dimensional extension."""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction
import hashlib,itertools,json,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph
from paired_sibling_ancestor_optimizer import optimize,plain_optimize
from paired_complement_half_graph import decompose,conditional
from verify_paired_signed_k5_obstruction import all_negative_cycles,check_joint,lift_joint,check_packing,witness_rank

ROOT=Path(__file__).parent
SEED=json.loads((ROOT/'paired_actual_joint_gap_compact_certificate.json').read_text())

def all_paths(H,a,r):
    adj=defaultdict(list)
    for u,v,c in H:adj[u].append(v);adj[v].append(u)
    result=[]
    def dfs(path):
        if path[-1]==r:result.append(tuple(path));return
        for u in sorted(adj[path[-1]]):
            if u not in path:dfs(path+[u])
    dfs([a]);assert len(set(result))==len(result);return result

def primal_objects(items):
    paths=[];cycles=[]
    for kind,z,s in items:
        amount=Fraction(*s) if isinstance(s,list) else Fraction(s)
        (paths if kind=='path' else cycles).append((tuple(z),amount))
    return paths,cycles

def audit_core():
    w=tuple(SEED['weights']);p,scores=order_and_scores(w);G=linear_graph(p,9)
    H,r,a,tau=decompose(G,9);assert H==tuple(map(tuple,SEED['half_edges']))
    assert len(set(scores))==512 and min(y-x for x,y in zip(scores,scores[1:]))==1
    paths=all_paths(H,a,r);cycles=all_negative_cycles(H)
    assert (len(paths),len(cycles))==(147,437)
    objects=[('path',z,1) for z in paths]+[('cycle',z,2) for z in cycles]
    digest=hashlib.sha256(json.dumps(objects,separators=(',',':')).encode()).hexdigest()
    assert digest==SEED['object_list_sha256']
    dual={(u,v):Fraction(*s) for u,v,s in SEED['exact_dual']}
    assert all(y>=0 for y in dual.values())
    key=lambda u,v:tuple(sorted((u,v)))
    assert all(sum(dual.get(key(u,v),0) for u,v in zip(z,z[1:]))>=1 for z in paths)
    assert all(sum(dual.get(key(u,v),0) for u,v in zip(z,z[1:]+z[:1]))>=2 for z in cycles)
    P,C=primal_objects(SEED['exact_packing']);base=check_joint(H,r,a,P,C)
    assert base==sum(abs(c)*dual.get((u,v),0) for u,v,c in H)==Fraction(45,2)
    slope=tuple((u,v,c-int((u,v)==(252,255))) for u,v,c in H)
    PP,CC=primal_objects(SEED['slope_joint_certificate']['primal'])
    assert check_joint(slope,r,a,PP,CC)==sum(abs(c)*dual.get((u,v),0) for u,v,c in slope)==23
    assert dual[252,255]==Fraction(1,2)
    free=sorted({z for u,v,c in H for z in (u,v)}-{r,a,252});table={}
    for sa in (1,-1):
        for sb in (1,-1):
            best=-1000;negative=None
            for signs in itertools.product((1,-1),repeat=len(free)):
                spin=dict(zip(free,signs));spin.update({r:1,a:sa,252:sb})
                e=sum(c*spin[u]*spin[v] for u,v,c in H)
                if e>best:best=e;negative=sorted(u for u,s in spin.items() if s<0)
            assert best==SEED['boundary_energy_table'][str((sa,sb))]['energy']
            table[str((sa,sb))]={'energy':best,'negative_vertices':negative}
    assert [table[str(z)]['energy'] for z in ((1,1),(1,-1),(-1,1),(-1,-1))]==[19,21,19,17]
    optimum=optimize(G,9);independent_energy,_=plain_optimize(G,9)
    assert optimum['E_max']==independent_energy==40
    assert (G['D'],G['K'],G['W'])==(56,184,86)
    active={z for u,v,c in G['edges'] for z in (u,v)}
    negative={u for u in active if (optimum['mask']>>u)&1}
    assert negative=={202,208,214,215,216,221,243,245,246,252,253}
    return w,p,G,H,r,a,tau,dual,(P,C),(PP,CC),table,negative

def main():
    start=time.monotonic();w,p,G,H,r,a,tau,dual,base,slope,table,negative=audit_core()
    rows=[];digest=hashlib.sha256();L=sum(w)+1;assert L==5544
    for n in range(9,19):
        m=n-9;T=1<<m;shift=(1<<(n-1))-256
        v=tuple(L*(1<<j) for j in range(m))+w;order,scores=order_and_scores(v)
        assert order==tuple((x<<m)|t for t in range(T) for x in p)
        graph=linear_graph(order,n);pred=defaultdict(int)
        for u,z,c in G['edges']:pred[u+shift,z+shift]+=T*c
        pred[252+shift,255+shift]-=T-1;pred[253+shift,255+shift]+=T-1
        assert graph['edges']==tuple((u,z,c) for (u,z),c in sorted(pred.items()) if c)
        HH,rr,aa,ttau=decompose(graph,n)
        P=[(tuple(u+shift for u in z),mass) for z,mass in base[0]]
        P += [(tuple(u+shift for u in z),(T-1)*mass) for z,mass in slope[0]]
        C=[(tuple(u+shift for u in z),mass) for z,mass in base[1]]
        C += [(tuple(u+shift for u in z),(T-1)*mass) for z,mass in slope[1]]
        value=check_joint(HH,rr,aa,P,C);assert value==Fraction(46*T-1,2)
        dualvalue=sum(abs(c)*dual.get((u-shift,z-shift),0) for u,z,c in HH)
        assert dualvalue==value
        fullvalue,_=check_packing(graph['edges'],lift_joint(P,C,ttau));assert fullvalue==value
        # Exact conditioned energy formulas follow from the four finite
        # boundary values and the sole reinforced edge in the half.
        plus=max(T*table[str((1,b))]['energy']-(T-1)*b for b in (1,-1))
        minus=max(T*table[str((-1,b))]['energy']-(T-1)*b for b in (1,-1))
        assert (plus,minus)==(22*T-1,18*T+1)
        E=plus+minus;phi=(graph['W']-E)//2;assert phi==24*T-1
        assert (graph['D'],graph['K'],graph['W'])==(56*T,184*T,88*T-2)
        neg={u+shift for u in negative};energy=sum(c*(-1 if (u in neg)!=(z in neg) else 1) for u,z,c in graph['edges'])
        assert energy==E==40*T
        R=1;last=None;previous=witness_rank(order[0],n,neg)
        for x in order[1:]:
            rank=witness_rank(x,n,neg);s=1 if rank>previous else -1
            assert rank!=previous
            if last is not None and last!=s:R+=1
            last=s;previous=rank
        assert R==264*T==1+graph['D']+graph['K']+phi
        gap=Fraction(phi)-value;assert gap==Fraction(2*T-1,2)>0
        row={'n':n,'weights':v,'T':T,'D':graph['D'],'K':graph['K'],'W':graph['W'],
             'half_conditioned_energies':[plus,minus],'full_E_max':E,'phi':phi,
             'joint_fractional_optimum':str(value),'actual_capacity_gap':str(gap),
             'R_min':R,'D_K_plus_joint':str(graph['D']+graph['K']+value),
             'order_sha256':hashlib.sha256(json.dumps(order,separators=(',',':')).encode()).hexdigest()}
        rows.append(row);digest.update(json.dumps(row,sort_keys=True).encode())
        print(json.dumps(row),flush=True)
    out={'status':'VERIFIED_REAL_ACTUAL_CAPACITY_JOINT_GAP_FOR_EVERY_N_GE_9',
         'analytic_statement':'The genuine dominant-low-tail scan has phi=24T-1, joint fractional packing=23T-1/2, gap=T-1/2, R_min=264T, T=2^(n-9).',
         'scope':'Refutes universal actual-capacity joint exactness, including ordinary full fractional negative-cycle packing via the proved reduction. Does not refute positive-density certificate bounds or the primary M_n target.',
         'base_weights':w,'all_base_simple_paths':147,'all_base_negative_cycles':437,
         'finite_boundary_energy_table':table,'rows':rows,'violations':0,
         'seconds':time.monotonic()-start,'audit_sha256':digest.hexdigest()}
    (ROOT/'paired_actual_joint_gap_verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','finite_boundary_energy_table')}),flush=True)

if __name__=='__main__':main()
