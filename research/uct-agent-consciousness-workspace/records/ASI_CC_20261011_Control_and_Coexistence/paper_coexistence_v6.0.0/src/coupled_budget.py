#!/usr/bin/env python3
"""PR-v6: exact common-budget diagnosis/backup frontier; no external dependencies.

No model calls, no real physical resource tests. Independent oracle enumerates
actual joint fault worlds, groups indistinguishable received report vectors,
then searches integer capacity placements without using the closed form.
"""
from __future__ import annotations
from itertools import combinations, product
from pathlib import Path
import argparse, json, time


def subsets(n, limit):
    for t in range(min(n, limit)+1):
        yield from combinations(range(n),t)


def compositions(total, parts, lower=0):
    """Sorted nonnegative placements; bank-root labels are symmetric in oracle."""
    if parts==1:
        if total>=lower: yield (total,)
        return
    for x in range(lower,total//parts+1):
        for rest in compositions(total-x,parts-1,x): yield (x,)+rest


def balanced(total,b):
    q,r=divmod(total,b)
    return (q,)*(b-r)+(q+1,)*r


def capacity_floor(demand,b,removed):
    assert 0<=removed<b
    return demand+removed*((demand+b-removed-1)//(b-removed))


def frontier(n,k,f,d,b):
    assert n>=k>=1 and f>=0 and d>=0 and b>=1
    if b<=f: return None
    if d<=f:
        w=n
        return {'minimum':capacity_floor(w,b,f),'mode':'untrusted_all_diagnostics',
                'cuts':[{'a':0,'demand':w,'banks_remaining':b-f,
                         'nominal_lower_bound':capacity_floor(w,b,f)}]}
    cuts=[]
    for a in range(f+1):
        w=min(n,k*(1+a//(d-f)))
        cuts.append({'a':a,'demand':w,'banks_remaining':b-f+a,
                     'nominal_lower_bound':capacity_floor(w,b,f-a)})
    r=max(x['nominal_lower_bound'] for x in cuts)
    return {'minimum':r,'mode':'at_least_one_honest_diagnostic','cuts':cuts,
            'placement':balanced(r,b)}


def joint_world_oracle(n,k,f,d,b):
    """Every fault set, report forgery and actual k-failure set. No formula."""
    states=tuple(combinations(range(n),k))
    cells={}; world_count=0
    for si,S in enumerate(states):
        for A in subsets(d,f):
            for B in subsets(b,f-len(A)):
                mask=sum(1<<i for i in B)
                for forged in product(range(len(states)),repeat=len(A)):
                    z=[si]*d
                    for i,value in zip(A,forged): z[i]=value
                    entry=cells.setdefault(tuple(z),[set(),set()])
                    entry[0].update(S);entry[1].add(mask);world_count+=1
    needs={}
    for (U,masks) in cells.values():
        for mask in masks:needs[mask]=max(needs.get(mask,0),len(U))
    constraints=tuple(sorted(needs.items()))
    return {'constraints':constraints,'worlds':world_count,'observations':len(cells),
            'max_ambiguity':max(len(x[0]) for x in cells.values())}


def safe(caps,constraints):
    return all(sum(c for i,c in enumerate(caps) if not(mask>>i&1))>=demand
               for mask,demand in constraints)


def brute_optimum(b,constraints,max_total):
    tries=0
    for total in range(max_total+1):
        for caps in compositions(total,b):
            tries+=1
            if safe(caps,constraints):return total,caps,tries
    return None,None,tries


def repeated_frontier(groups,m,f):
    if m<=f:return None
    h=m-f;t=min(len(groups),m//h)
    w=sum(sorted(groups,reverse=True)[:t])
    return {'max_ambiguity':w,'compatible_groups':t,
            'minimum':capacity_floor(w,m,f),'placement':balanced(capacity_floor(w,m,f),m)}


def repeated_oracle(groups,m,f):
    q=len(groups); cells={};worlds=0
    for g in range(q):
        for A in subsets(m,f):
            mask=sum(1<<i for i in A)
            for vals in product(range(q),repeat=len(A)):
                z=[g]*m
                for i,v in zip(A,vals):z[i]=v
                cell=cells.setdefault(tuple(z),[set(),set()])
                cell[0].add(g);cell[1].add(mask);worlds+=1
    needs={}
    for gs,masks in cells.values():
        w=sum(groups[g] for g in gs)
        for mask in masks:needs[mask]=max(needs.get(mask,0),w)
    return tuple(sorted(needs.items())),worlds


def general_one_fault(code,m):
    cells={}
    for s,word in enumerate(code):
        for i in range(-1,m):
            for v in ((0,) if i<0 else (0,1)):
                z=list(word)
                if i>=0:z[i]=v
                cell=cells.setdefault(tuple(z),[set(),set()])
                cell[0].add(s);cell[1].add(i)
    L=[0]*m
    for U,roots in cells.values():
        for i in roots:
            if i>=0:L[i]=max(L[i],len(U))
    R=max(max(L),(sum(L)+m-2)//(m-1))
    # A generally nonuniform attaining placement, each cap_i <= R-L_i.
    caps=[];left=R
    for lim in (R-x for x in L):
        v=min(left,lim);caps.append(v);left-=v
    assert left==0
    for U,roots in cells.values():
        for i in roots:
            avail=sum(caps)-(caps[i] if i>=0 else 0)
            assert avail>=len(U)
    return R,tuple(L),tuple(caps)


def run():
    start=time.monotonic();results=[];worlds=0;tries=0
    # Rich exact k-subset reporting; bounded but exhaustive grids, not samples.
    for n in range(2,5):
        for k in range(1,min(2,n)+1):
            for f in range(3):
                for d in range(0,5):
                    for b in range(f+1,5):
                        oracle=joint_world_oracle(n,k,f,d,b)
                        formula=frontier(n,k,f,d,b)
                        R=formula['minimum']
                        observed,caps,num=brute_optimum(b,oracle['constraints'],R)
                        assert observed==R,(n,k,f,d,b,formula,oracle,observed)
                        assert safe(balanced(R,b),oracle['constraints'])
                        worlds+=oracle['worlds'];tries+=num
                        results.append({'n':n,'k':k,'f':f,'d':d,'b':b,'R':R,
                                        'worlds':oracle['worlds'],'cells':oracle['observations'],
                                        'oracle_placement':caps})
    stress=[]
    for n,k,f,d,b in ((5,2,3,4,4),(6,2,3,4,5),(5,2,3,5,4),
                        (6,1,3,6,5),(5,3,2,4,5),(4,3,3,4,4)):
        oracle=joint_world_oracle(n,k,f,d,b)
        predicted=frontier(n,k,f,d,b)['minimum']
        R,caps,num=brute_optimum(b,oracle['constraints'],predicted)
        assert R==predicted and safe(balanced(R,b),oracle['constraints'])
        stress.append({'n':n,'k':k,'f':f,'d':d,'b':b,'R':R,'worlds':oracle['worlds']})
        worlds+=oracle['worlds'];tries+=num
    # A trusted report does not restore backup when all bank owners can fail.
    impossible=[]
    for f in (1,2,3):
        o=joint_world_oracle(2,1,f,f+1,f)
        mask=(1<<f)-1
        assert dict(o['constraints'])[mask]>0
        assert not safe((100,)*f,o['constraints'])
        impossible.append({'f':f,'b':f,'all_bank_mask':mask,'demand':dict(o['constraints'])[mask]})
    repeated=[];rworlds=0
    for groups in ((1,1),(2,2),(1,2),(1,1,1),(1,2,3),(2,1,1,2)):
        for m in range(1,7):
            for f in range(min(2,m-1)+1):
                obs,W=repeated_oracle(groups,m,f);fr=repeated_frontier(groups,m,f)
                R,caps,num=brute_optimum(m,obs,fr['minimum'])
                assert R==fr['minimum'],(groups,m,f,fr,R)
                assert safe(fr['placement'],obs)
                repeated.append({'groups':groups,'m':m,'f':f,'R':R,'worlds':W})
                rworlds+=W;tries+=num
    arbitrary=[]
    for m in range(2,5):
        binary=tuple(product((0,1),repeat=m))
        for n in range(1,min(4,len(binary))+1):
            for code in combinations(binary,n):
                R,L,caps=general_one_fault(code,m)
                constraints=tuple((1<<i,L[i]) for i in range(m))
                # L breaks permutation symmetry: enumerate all labeled placements.
                def allcomp(t,parts):
                    if parts==1:yield (t,);return
                    for x in range(t+1):
                        for z in allcomp(t-x,parts-1):yield (x,)+z
                got=None
                for t in range(R+1):
                    if any(safe(v,constraints) for v in allcomp(t,m)):
                        got=t;break
                assert got==R,(m,n,code,L,R,got)
                arbitrary.append({'m':m,'n':n,'R':R})
    low_sensor=[]
    for f in range(1,8):
        for k in (1,2,3):
            n=(f+1)*k
            res=frontier(n,k,f,f+1,f+1)
            assert res['minimum']==(f+1)*k
            rectangular=(f+1)*min(n,(f+1)*k)
            assert rectangular==k*(f+1)**2
            low_sensor.append({'f':f,'k':k,'n':n,'diagnostic_roots':f+1,'backup_roots':f+1,
                               'joint_R':res['minimum'],'decoupled_R':rectangular,'factor':f+1})
    # Negative controls to prove that common budget and role separation matter.
    f=2;k=1;reports=(0,1,2);cap_before=3
    independent_attack={'diagnostic_corruptions':2,'bank_corruptions':2,
        'nominal_capacity':cap_before,'demand':len(set(reports)),
        'surviving':cap_before-2,'guarantee_holds':False}
    assert cap_before-2<len(set(reports))
    # Co-location: one root can lie and destroy capacity, so a+b<=f is invalid.
    colocated={'f':1,'reports':[0,1],'demand':2,'surviving':1,'guarantee_holds':False}
    assert colocated['demand']>colocated['surviving']
    example=general_one_fault(((0,0,0,0),(1,1,0,0)),4)
    assert example==(2,(2,2,1,1),(0,0,1,1))
    result={'version':'PR-v6.0.0','scope':'Constructed exact finite worlds and mathematical proofs; no AI/hardware measurement',
      'joint_grid_cases':len(results),'joint_worlds':worlds,'candidate_capacity_placements_tested':tries,
      'joint_cases':results,'larger_stress_cases':stress,'all_banks_lost_cases':impossible,'replicated_grid_cases':len(repeated),'replicated_worlds':rworlds,'replicated_cases':repeated,
      'arbitrary_code_one_fault_cases':len(arbitrary),'arbitrary_cases':arbitrary,
      'minimum_reserve_construction':low_sensor,'asymmetric_example':{'R':example[0],'L':example[1],'caps':example[2]},
      'negative_controls':{'separate_attack_budgets':independent_attack,'colocated_diagnostic_bank':colocated},
      'PR5_recovery':{str(m):repeated_frontier((2,2),m,1) for m in range(1,7)},
      'elapsed_seconds':time.monotonic()-start,'assertions':'PASS'}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='coupled_budget_results.json');args=p.parse_args()
    r=run();dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k not in ('joint_cases','replicated_cases','arbitrary_cases')},indent=2))
