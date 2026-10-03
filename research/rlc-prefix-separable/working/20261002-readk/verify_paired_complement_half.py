#!/usr/bin/env python3
"""Audit new structural identities, not a weight-chamber classification."""
from pathlib import Path
from collections import defaultdict,Counter
import hashlib,json,random,time
from verify_gray_reflection_graph import order_and_scores,counts
from verify_paired_sibling_ranks import linear_graph,rank,fast_runs
from paired_sibling_ancestor_optimizer import optimize,plain_optimize,layout
from paired_complement_half_graph import decompose,conditional,balance,terminal_cut


def brute_half(H,r,a):
    vertices=sorted({r,a}|{u for x,y,c in H for u in(x,y)})
    free=[u for u in vertices if u!=r];ix={u:i for i,u in enumerate(free)}
    records=[];best={1:None,-1:None}
    for mask in range(1<<len(free)):
        s={r:1,**{u:(-1 if mask>>ix[u]&1 else 1) for u in free}}
        cost=sum(abs(c) for u,v,c in H if c*s[u]*s[v]<0)
        best[s[a]]=cost if best[s[a]] is None else min(best[s[a]],cost)
        records.append((s,cost))
    formula=None;witness=None
    others=[u for u in vertices if u not in(r,a)]
    for mask in range(1<<len(others)):
        S={a}|{u for i,u in enumerate(others) if mask>>i&1}
        cap=sum(abs(c) for u,v,c in H if (u in S)!=(v in S))
        residual=min(sum(abs(c) for u,v,c in H if (u in S)==(v in S) and c*s[u]*s[v]<0) for s,cost in records)
        value=cap+2*residual
        if formula is None or value<formula:formula=value;witness={'S':sorted(S),'cut':cap,'residual_phi':residual}
    assert best[1]+best[-1]==formula
    return best,formula,witness


def audit(w,brute=False):
    n=len(w);N=1<<n;out=order_and_scores(w)
    if out is None:return None
    p=out[0];assert all(p[N-1-i]==p[i]^(N-1) for i in range(N))
    g=linear_graph(p,n);H,r,a,tau=decompose(g,n)
    e0,m0=conditional(H,n,1);e1,m1=conditional(H,n,-1)
    W_H=sum(abs(c) for u,v,c in H)
    f0=(W_H-e0)//2;f1=(W_H-e1)//2
    assert W_H-e0==2*f0 and W_H-e1==2*f1
    z=optimize(g,n);assert z['E_max']==e0+e1
    if n<=7:assert plain_optimize(g,n)[0]==z['E_max']
    phi=(g['W']-z['E_max'])//2;assert phi==f0+f1
    cut,part=terminal_cut(H,r,a);assert phi>=cut
    balanced,bc=balance(H)
    if balanced:assert phi==cut
    else:
        J={tuple(sorted((u,v))):c for u,v,c in H};product=1
        for u,v in zip(bc,bc[1:]+bc[:1]):product*=1 if J[tuple(sorted((u,v)))]>0 else -1
        assert product==-1
    R=fast_runs([rank(x,n,z['mask']) for x in range(N)],p)
    assert R==1+g['D']+g['K']+phi
    raw=None
    if brute:
        bb,formula,wit=brute_half(H,r,a);assert bb=={1:f0,-1:f1};raw={'formula':formula,'cut_formula_witness':wit}
    return {'n':n,'weights':w,'D':g['D'],'K':g['K'],'W':g['W'],'phi_equal':f0,'phi_opposite':f1,
            'phi':phi,'cut':cut,'balanced':balanced,'R_min':R,'mask':z['mask'],
            'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest(),
            'half_edges':H,'cut_source_side':part,'negative_cycle':None if balanced else bc,'brute':raw}


def lifted_certificate(n):
    base=(34,36,40,33,48);ell=n-5;T=1<<ell
    w=tuple(192*(1<<j) for j in range(ell))+base
    p=order_and_scores(w)[0];core=order_and_scores(base)[0]
    expected=tuple((x<<ell)|row for row in range(T) for x in core)
    assert p==expected
    g=linear_graph(p,n);H,r,a,tau=decompose(g,n);shift=(1<<(n-1))-16
    expected_H=tuple((shift+u,shift+v,T*c) for u,v,c in ((8,12,1),(8,15,-1),(9,12,1),(9,15,-1),(12,15,2)))
    assert H==expected_H
    assert (g['D'],g['K'],g['W'])==(8*T,6*T-1,12*T)
    J={tuple(sorted((u,v))):c for u,v,c in H};load=defaultdict(int)
    cycles=((shift+8,shift+12,shift+15),(shift+9,shift+12,shift+15))
    for cy in cycles:
        product=1
        for u,v in zip(cy,cy[1:]+cy[:1]):
            key=tuple(sorted((u,v)));product*=1 if J[key]>0 else -1;load[key]+=T
        assert product==-1
    assert all(v<=abs(J[k]) for k,v in load.items())
    # Each conditional half has frustration >=2T from the capacity packing.
    for spin in (1,-1):
        E,mask=conditional(H,n,spin);assert E==2*T
        assert (sum(abs(c) for u,v,c in H)-E)//2==2*T
    cut,_=terminal_cut(H,r,a);assert cut==0
    z=optimize(g,n);assert z['E_max']==4*T and (g['W']-z['E_max'])//2==4*T
    observed=counts([rank(x,n,0) for x in p]);assert observed[:2]==(18*T,18*T)
    assert 1+g['D']+g['K']+4*T==18*T
    return {'n':n,'T':T,'weights':w,'D':g['D'],'K':g['K'],'W':g['W'],'cut':cut,
            'phi':4*T,'R_min':18*T,'C_at_mask_0':18*T,'attaining_mask':0,'half_edges':H,
            'half_negative_cycles':cycles,'each_cycle_capacity':T}


def cut_failure_certificate(n):
    ell=n-5;T=1<<ell;shift=(1<<(n-1))-16
    w=tuple(44*(1<<j) for j in range(ell))+(1,14,4,8,16)
    p=order_and_scores(w)[0];core=order_and_scores((1,14,4,8,16))[0]
    assert p==tuple((x<<ell)|row for row in range(T) for x in core)
    g=linear_graph(p,n);H,r,a,tau=decompose(g,n)
    raw=((0,12,T),(0,14,T),(0,15,-(2*T-1)),(1,12,T),(1,14,T),
         (2,12,-T),(2,14,T),(3,12,-T),(3,14,-T))
    expected=tuple((shift+u,shift+v,c) for u,v,c in raw);assert H==expected
    assert (g['D'],g['K'],g['W'])==(0,6*T,20*T-2)
    paths=((r,shift+0,a),(r,shift+0,shift+12,shift+3,a))
    amounts=(T,T-1);cycle=(shift+1,shift+12,shift+2,a)
    J={tuple(sorted((u,v))):c for u,v,c in H};load=defaultdict(int)
    for path,amount in zip(paths,amounts):
        assert path[0]==r and path[-1]==a and len(set(path))==len(path)
        for u,v in zip(path,path[1:]):load[tuple(sorted((u,v)))]+=amount
    product=1
    for u,v in zip(cycle,cycle[1:]+cycle[:1]):
        key=tuple(sorted((u,v)));load[key]+=T;product*=1 if J[key]>0 else -1
    assert product==-1 and all(c<=abs(J[k]) for k,c in load.items())
    cut,_=terminal_cut(H,r,a);assert cut==2*T-1
    energies=[conditional(H,n,s)[0] for s in (1,-1)];assert energies==[4*T+1,8*T-1]
    z=optimize(g,n);phi=(g['W']-z['E_max'])//2
    assert z['E_max']==12*T and phi==4*T-1==sum(amounts)+2*T
    mask=56<<shift;R,C,_=counts([rank(x,n,mask) for x in p]);assert R==C==10*T
    assert g['D']+g['K']+cut==(1<<n)//4-1
    return {'n':n,'T':T,'weights':w,'D':g['D'],'K':g['K'],'W':g['W'],'cut':cut,'phi':phi,
            'cut_budget':g['D']+g['K']+cut,'quarter_budget':(1<<n)//4,'R_min':R,'C_at_witness':C,
            'attaining_mask':mask,'half_edges':H,'paths':paths,'path_amounts':amounts,
            'negative_cycle':cycle,'cycle_amount':T,'joint_certificate_value':sum(amounts)+2*T}


def main():
    start=time.monotonic();rng=random.Random(202610031153);digest=hashlib.sha256();summaries=[];rejected=0;rows=0;strict=0
    seeds=((1,6,8,4),(34,36,40,33,48),(14,12,10,15,6))
    witnesses=[audit(w,brute=True) for w in seeds]
    for n in range(2,11):
        stats=Counter()
        for i in range(40):
            if i%2:
                b=rng.sample(range(-100000,100001),n);B=1+sum(abs(x) for x in b);w=tuple(B+x for x in b)
            else:w=tuple(rng.sample(range(1,1000001),n))
            if i%3==0:w=tuple(-z if rng.randrange(2) else z for z in w)
            row=audit(w,brute=n<=4 or(n==5 and i<4))
            if row is None:rejected+=1;continue
            rows+=1;digest.update(json.dumps(row,sort_keys=True).encode());stats['checked']+=1
            stats['balanced']+=row['balanced'];stats['strict_cut_gap']+=row['phi']>row['cut'];strict+=row['phi']>row['cut']
            stats['cut_quarter_failures']+=(row['D']+row['K']+row['cut']<(1<<n)//4)
        summaries.append({'n':n,**stats});print(json.dumps(summaries[-1]),flush=True)
    lifts=[lifted_certificate(n) for n in range(5,13)]
    cut_failures=[cut_failure_certificate(n) for n in range(5,13)]
    for row in witnesses+lifts+cut_failures:digest.update(json.dumps(row,sort_keys=True).encode())
    data={'seed':202610031153,'checked_scans':rows,'rejected_ties':rejected,'strict_cut_gaps':strict,'summaries':summaries,
          'exact_small_witnesses':witnesses,'all_dimension_family_audit':lifts,'all_dimension_cut_failure_audit':cut_failures,'digest_sha256':digest.hexdigest(),
          'seconds':time.monotonic()-start,'scope':'General identities have analytic proofs; audit coverage is listed finite samples, not chambers. No universal quarter or main M_n theorem claimed.'}
    Path(__file__).with_name('paired_complement_half_certificate.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k not in('summaries','exact_small_witnesses','all_dimension_family_audit','all_dimension_cut_failure_audit')}),flush=True)

if __name__=='__main__':main()
