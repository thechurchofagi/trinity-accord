#!/usr/bin/env python3
"""Exact real odd-K5 support, diagnostic LP gap, and every-dimensional lift.

All arithmetic in the verifier is integer or Fraction. No LP solver is
used here. Finite high-dimensional audits check the analytic lift proof.
"""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction
import hashlib,itertools,json,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph
from paired_complement_half_graph import decompose,conditional,balance
from paired_sibling_ancestor_optimizer import layout
from probe_paired_signed_k5 import certificate,key

ROOT=Path(__file__).parent
SEED=json.loads((ROOT/'paired_signed_k5_seed_certificate.json').read_text())

def all_negative_cycles(H):
    J={key(u,v):c for u,v,c in H};adj=defaultdict(list);out=[]
    for u,v in J:adj[u].append(v);adj[v].append(u)
    def dfs(path,sign):
        u=path[-1]
        for v in sorted(adj[u]):
            s=1 if J[key(u,v)]>0 else -1
            if v==path[0] and len(path)>=3 and path[1]<path[-1]:
                if sign*s<0:out.append(tuple(path))
            elif v>path[0] and v not in path:dfs(path+[v],sign*s)
    for u in sorted(adj):dfs([u],1)
    assert len(set(out))==len(out)
    return out

def check_packing(H,packing):
    J={key(u,v):c for u,v,c in H};loads=defaultdict(Fraction);mass=Fraction(0)
    for cycle,amount in packing:
        cycle=tuple(cycle);amount=Fraction(amount)
        assert len(cycle)>=3 and len(set(cycle))==len(cycle) and amount>=0
        s=1
        for u,v in zip(cycle,cycle[1:]+cycle[:1]):
            e=key(u,v);assert e in J;s*=1 if J[e]>0 else -1;loads[e]+=amount
        assert s==-1;mass+=amount
    assert all(load<=abs(J[e]) for e,load in loads.items())
    return mass,loads

def lift_joint(paths,cycles,tau):
    full=[]
    for path,amount in paths:
        path=tuple(path)
        full.append((path+tuple(tau(u) for u in reversed(path[1:-1])),amount))
    for z,amount in cycles:
        z=tuple(z);full.extend([(z,amount),(tuple(tau(u) for u in z),amount)])
    return full

def project_full(full,keep,r,a,tau):
    paths=[];cycles=[]
    for z,amount in full:
        z=tuple(z);amount=Fraction(amount)
        if set(z)<=keep:cycles.append((z,amount/2));continue
        if {tau(u) for u in z}<=keep:
            cycles.append((tuple(tau(u) for u in z),amount/2));continue
        assert r in z and a in z
        i=z.index(a);z=z[i:]+z[:i];j=z.index(r)
        for p in (z[:j+1],(a,)+tuple(reversed(z[j:]))):
            assert p[0]==a and p[-1]==r
            if not set(p)<=keep:p=tuple(tau(u) for u in p)
            assert set(p)<=keep
            paths.append((p,amount/2))
    return paths,cycles

def check_joint(H,r,a,paths,cycles):
    mass,loads=check_packing(H,cycles);J={key(u,v):c for u,v,c in H};P=Fraction(0)
    for p,amount in paths:
        amount=Fraction(amount);assert p[0]==a and p[-1]==r and len(set(p))==len(p)
        assert amount>=0;P+=amount
        for u,v in zip(p,p[1:]):loads[key(u,v)]+=amount
    assert all(e in J and v<=abs(J[e]) for e,v in loads.items())
    return P+2*mass

def audit_joint_full_reduction():
    # An unsymmetric full packing contains both an internal negative cycle
    # and a crossing cycle with different half paths of the same parity.
    H=((0,2,2),(1,2,2),(0,3,2),(1,3,2),(2,3,2),(3,4,2),(2,4,-2))
    r,a=1,0;keep={0,1,2,3,4};mapping={0:0,1:1,2:5,3:6,4:7,5:2,6:3,7:4}
    tau=lambda u:mapping[u]
    eps=lambda u:1 if u==r else -1
    G=H+tuple((*key(tau(u),tau(v)),c*eps(u)*eps(v)) for u,v,c in H)
    full=[((2,3,4),Fraction(1)),((0,2,1,6),Fraction(1))]
    original,_=check_packing(G,full);assert original==2
    paths,cycles=project_full(full,keep,r,a,tau)
    projected=check_joint(H,r,a,paths,cycles);assert projected==original
    lifted=lift_joint(paths,cycles,tau);lifted_mass,_=check_packing(G,lifted)
    assert lifted_mass==original
    return {'full_original_mass':str(original),'half_projected_value':str(projected),
            'relifted_full_mass':str(lifted_mass),'projected_paths':[(z,str(s)) for z,s in paths],
            'projected_cycles':[(z,str(s)) for z,s in cycles],
            'scope':'Audits both directions of the general analytic fractional packing identity, including an unsymmetric full packing and mixed terminal paths.'}

def ancestor_budget(graph,n):
    r,nodes,info=layout(n);loads=defaultdict(int)
    for u,v,c in graph['edges']:
        if u==r:u,v=v,u
        elif v!=r and info[u][0]<info[v][0]:u,v=v,u
        loads[u]+=abs(c)
    assert all(load<=1<<(n-info[u][0]) for u,load in loads.items())
    return loads

def audit_nonadditive_budget_obstruction():
    rows=[]
    for n in range(2,15):
        N=1<<n;first=sorted(range(N//2),key=lambda x:x^(x>>1))
        p=tuple(first+[N-1-x for x in reversed(first)])
        assert all(p[N-1-i]==N-1-p[i] for i in range(N))
        ranks=[x^(x>>1) for x in p]
        assert ranks==list(range(N//2))+list(range(N-1,N//2-1,-1))
        g=linear_graph(p,n);ancestor_budget(g,n);decompose(g,n)
        assert g['D']==0
        if n==2:assert g['K']==1 and g['W']==0
        else:
            assert p[:4]==(0,1,3,2) and g['K']==0
            balanced,cycle=balance(g['edges']);assert not balanced
            value,_=check_packing(g['edges'],[(cycle,1)]);assert value==1
            E=sum(c for u,v,c in g['edges']);assert (g['W']-E)//2==1
        rows.append({'n':n,'D':g['D'],'K':g['K'],'R_at_Gray':2,
                     'ancestor_budget_passed':True,'antipodal_order':True,
                     'nonadditive_for_n_ge_3':n>=3})
    return {'rows':rows,'analytic_statement':'Ancestor incident budgets hold for every vertex permutation. Even adding ancestor support and antipodal order permits a nonadditive all-dimensional R=2 scan. This does not satisfy additive coordinate-direction consistency.'}

def check_minor(H,shift=0):
    branches=SEED['signed_minor']['branches'];groups={};trees={};clique=[]
    for i,B in enumerate(branches):
        groups[i]={u+shift:s for u,s in B['gauges']}
        trees[i]=[(u+shift,v+shift) for u,v in B['positive_tree']]
        clique.append((i,1))
    return certificate(H,groups,trees,clique)

def diagnostic(H,n):
    cert=check_minor(H);trees={key(u,v) for B in cert['branches'] for u,v in B['positive_tree']}
    bridges={key(*z[2][:2]) for z in cert['negative_bridges']}
    caps=SEED['diagnostic_capacities']
    C=tuple((u,v,(1 if c>0 else -1)*(caps['tree'] if (u,v) in trees else caps['bridge'] if (u,v) in bridges else caps['other'])) for u,v,c in H)
    assert len(trees)==6 and len(bridges)==10 and trees.isdisjoint(bridges)
    # Independent exhaustive active-spin optimum fixes the global gauge.
    vs=sorted({z for u,v,c in C for z in (u,v)});fixed=vs[-1]
    best=-sum(abs(c) for u,v,c in C);attainer=None;enumerated=0
    for signs in itertools.product((1,-1),repeat=len(vs)-1):
        spin=dict(zip(vs[:-1],signs));spin[fixed]=1
        e=sum(c*spin[u]*spin[v] for u,v,c in C);enumerated+=1
        if e>best:best=e;attainer=sorted(u for u,s in spin.items() if s<0)
    W=sum(abs(c) for u,v,c in C);integer_phi=(W-best)//2
    assert best==max(conditional(C,n,s)[0] for s in (1,-1))
    lp=SEED['diagnostic_fractional_packing'];packing=[(z,Fraction(s)) for z,s in lp['cycles']]
    primal,loads=check_packing(C,packing)
    dual={tuple(e):Fraction(s) for e,s in lp['dual']};assert all(y>=0 for y in dual.values())
    cycles=all_negative_cycles(C)
    assert all(sum(dual.get(key(u,v),0) for u,v in zip(z,z[1:]+z[:1]))>=1 for z in cycles)
    dual_value=sum(abs(c)*dual.get((u,v),0) for u,v,c in C)
    assert primal==dual_value==Fraction(535,3) and integer_phi==211
    assert integer_phi-primal==Fraction(98,3)>0
    return {'signed_edges':C,'all_simple_negative_cycles':len(cycles),
            'active_spin_assignments':enumerated,'integer_frustration':integer_phi,
            'integer_attaining_negative_vertices':attainer,
            'fractional_optimum':str(primal),'integrality_gap':str(integer_phi-primal),
            'scope':'Positive integral alternative capacities on a genuine signed support; these capacities are not actual scan couplings.'}

def witness_rank(x,n,negative):
    q=1<<(n-1);value=0
    for h in range(n-1):
        u=q-(1<<(n-h-1))+(x>>(h+2))
        value|=(((x>>h)^(x>>(h+1))^int(u in negative))&1)<<h
    return value|(((x>>(n-1))&1)<<(n-1))

def audit_lift(w,n,oldp,oldg):
    d=len(w);m=n-d;T=1<<m;L=sum(w)+1;v=tuple(L*(1<<j) for j in range(m))+w
    result=order_and_scores(v);assert result is not None;p,scores=result
    assert p==tuple((x<<m)|row for row in range(T) for x in oldp)
    assert all(scores[i+1]>scores[i] for i in range(len(scores)-1))
    G=linear_graph(p,n);shift=(1<<(n-1))-(1<<(d-1));pred=defaultdict(int)
    for a,b,c in oldg['edges']:pred[a+shift,b+shift]+=T*c
    pred[252+shift,255+shift]-=T-1;pred[253+shift,255+shift]+=T-1
    assert G['edges']==tuple((u,v,c) for (u,v),c in sorted(pred.items()) if c)
    assert (G['D'],G['K'],G['W'])==(64*T,178*T,92*T-2)
    H,r,a,tau=decompose(G,n);minor=check_minor(H,shift)
    packing=[]
    for z in SEED['slope_negative_cycles']:
        amount=T-1 if z==SEED['reduced_cycle'] else T
        packing.append((tuple(u+shift for u in z),amount))
    mass,loads=check_packing(H,packing);assert mass==12*T-1
    full=packing+[(tuple(tau(u) for u in z),amount) for z,amount in packing]
    full_mass,_=check_packing(G['edges'],full);assert full_mass==24*T-2
    negative={u+shift for u in SEED['negative_witness_vertices']}
    energy=sum(c*(-1 if (u in negative)!=(v in negative) else 1) for u,v,c in G['edges'])
    assert energy==44*T+2 and (G['W']-energy)//2==full_mass
    # Verify the actual rank along the actual scan, independently of energy.
    R=1;last=None;previous=witness_rank(p[0],n,negative)
    for x in p[1:]:
        value=witness_rank(x,n,negative);s=1 if value>previous else -1
        assert value!=previous
        if last is not None and s!=last:R+=1
        previous=value;last=s
    assert R==266*T-1==1+G['D']+G['K']+full_mass
    return {'n':n,'weights':v,'T':T,'shift':shift,'D':G['D'],'K':G['K'],'W':G['W'],
            'half_negative_cycle_mass':str(mass),'full_negative_cycle_mass':str(full_mass),
            'E_max_certified':energy,'phi_certified':str(full_mass),'R_min_certified':R,
            'odd_K5_minor':minor,'order_sha256':hashlib.sha256(json.dumps(p,separators=(',',':')).encode()).hexdigest()}

def main():
    start=time.monotonic();w=tuple(SEED['weights']);oldp,scores=order_and_scores(w);oldg=linear_graph(oldp,len(w))
    assert len(set(scores))==512 and min(b-a for a,b in zip(scores,scores[1:]))==1
    H,r,a,tau=decompose(oldg,9);assert len(H)==33
    diagnostic_result=diagnostic(H,9);reduction=audit_joint_full_reduction()
    budget_obstruction=audit_nonadditive_budget_obstruction();rows=[];digest=hashlib.sha256()
    for n in range(9,19):
        z=audit_lift(w,n,oldp,oldg);rows.append(z);digest.update(json.dumps(z,sort_keys=True).encode())
        print(json.dumps({k:z[k] for k in ('n','T','D','K','W','R_min_certified')}),flush=True)
    out={'status':'VERIFIED_REAL_ODD_K5_SUPPORT_IN_EVERY_N_GE_9_AND_EXACT_SCAN_PACKING',
         'analytic_statement':'For every n>=9, dominant new low coordinates lift a genuine signed odd-K5 minor. On the same genuine scan family, a capacity-respecting integral negative-cycle packing of mass 24T-2 attain the exact frustration and R_min=266T-1, T=2^(n-9).',
         'scope':'Refutes universal weak bipartiteness of genuine half/full supports. The diagnostic capacity gap is not an actual-scan packing gap. The primary constant-density M_n theorem remains open.',
         'seed_weights':w,'diagnostic':diagnostic_result,'general_packing_reduction_audit':reduction,
         'ancestor_budget_obstruction':budget_obstruction,'rows':rows,'violations':0,
         'seconds':time.monotonic()-start,'audit_sha256':digest.hexdigest()}
    (ROOT/'paired_signed_k5_obstruction_verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','diagnostic')}),flush=True)

if __name__=='__main__':main()
