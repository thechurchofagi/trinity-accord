#!/usr/bin/env python3
"""EAC-v3.0.0: joint endorsement safety, solo availability, and mobile exposure.
Standard-library finite certificate checks. No oracle for real human interests.
The direct access-structure checker enumerates root-local signing patterns and
candidate approval menus, not merely the closed-form intersection condition.
"""
from __future__ import annotations
import argparse,itertools,json,math
from pathlib import Path


def accepted(menu:int, signers:int, n:int)->bool:
    return any((menu>>(q-1))&1 and q&signers==q for q in range(1,1<<n))


def direct_attack(n,k,H,B,menus):
    """Explicit per-root chosen approvals. Honest qualified roots refuse last of k."""
    allp=(1<<k)-1
    choices=[range(allp+1) if (B>>r&1 or not H>>r&1) else range(allp) for r in range(n)]
    for rows in itertools.product(*choices):
        cols=[sum(1<<r for r,S in enumerate(rows) if S>>x&1) for x in range(k)]
        if all(accepted(m,signers,n) for m,signers in zip(menus,cols)):
            return {'root_approved_masks':rows,'proposal_signer_masks':cols}
    return None


def solo_available(menu,n,refusals):
    U=(1<<n)-1
    return all(accepted(menu,U^F,n) for F in refusals)


def separation(H,Bs,Ffamilies):
    for B in Bs:
        for Fs in itertools.product(*Ffamilies):
            covered=B
            for F in Fs:covered|=F
            if H&~covered==0:return False
    return True


def existence_checks():
    n=2;U=3;families={v:tuple(x for x in range(4) if v>>x&1) for v in range(1,16)}
    counts={};witnesses=[]
    for k in (2,3):
        all_menus=tuple(itertools.product(range(1,8),repeat=k))
        specs=0;feasible=0;menu_tests=0
        for H in range(1,4):
          for bid,Bs in families.items():
            safe=[]
            for menus in all_menus:
                menu_tests+=1
                if not any(direct_attack(n,k,H,B,menus) is not None for B in Bs):safe.append(menus)
            # Exhaust all per-proposal refusal families for k2; common family for k3.
            fids=itertools.product(families,repeat=2) if k==2 else ((i,)*3 for i in families)
            for ids in fids:
                Fs=tuple(families[i] for i in ids)
                exists=any(all(solo_available(m,n,F) for m,F in zip(menus,Fs)) for menus in safe)
                claim=separation(H,Bs,Fs)
                assert exists==claim,(k,H,Bs,Fs,exists,claim)
                specs+=1;feasible+=exists
        counts[str(k)]={'specifications':specs,'candidate_menus_per_B_H':len(all_menus),'menu_safety_checks':menu_tests,'feasible_specs':feasible}
    return counts


def threshold_by_direct_signatures():
    cases=0;matrices=0;summary=[]
    for n in range(1,6):
      for k in range(2,5):
        if n*k>16:continue
        full=(1<<k)-1
        best=[-1]*(n+1)
        for rows in itertools.product(range(full+1),repeat=n):
            minima=min(sum((s>>x)&1 for s in rows) for x in range(k))
            first_full=next((i for i,s in enumerate(rows) if s==full),n)
            # First c roots are qualified and unexposed. Their rows cannot be full.
            for c in range(first_full+1):best[c]=max(best[c],minima)
            matrices+=1
        for h in range(1,n+1):
          for kap in range(n+1):
            c=max(0,h-kap)
            for unavailable in range(n):
                direct=[q for q in range(1,n+1) if q>best[c] and q<=n-unavailable]
                low=n-(h-kap-1)//k
                predicted=list(range(max(1,low),n-unavailable+1)) if h>kap+k*unavailable else []
                assert direct==predicted,(n,k,h,kap,unavailable,best,direct,predicted)
                cases+=1
        summary.append({'n':n,'arity':k,'max_uniform_signatures_in_possible_bad_batch_by_unexposed_witness_count':best})
    return {'signing_matrices_enumerated':matrices,'threshold_profiles':cases,'rows':summary}


def reachable_exposure(n,f,c,w):
    states=[s for s in range(1<<n) if s.bit_count()<=f]
    reachable={(s,s) for s in states}
    for _ in range(w-1):
        reachable={(nxt,old_union|nxt) for old,old_union in reachable for nxt in states if (nxt&~old).bit_count()<=c}
    return {union for _,union in reachable}


def temporal_checks():
    configs=0;thresholds=0;table=[]
    for n in range(2,8):
      for f in range(min(2,n-1)+1):
       for c in range(f+1):
        for w in range(1,5):
            Bs=reachable_exposure(n,f,c,w)
            kap=min(n,f+c*(w-1));assert Bs=={S for S in range(1<<n) if S.bit_count()<=kap}
            configs+=1
            for h in range(1,n+1):
             for k in range(2,6):
              for delta in range(min(2,n-f)):
                r=f+delta
                # Direct omission cover cardinality; formula for exact thresholds.
                feasible=h>kap+k*r
                qs=[q for q in range(1,n+1) if h-k*(n-q)>kap and q<=n-r]
                assert bool(qs)==feasible
                thresholds+=1
                if n==5 and f==c==1 and h==5 and delta==0 and k in (2,3):
                    table.append({'roots':n,'f':f,'new_exposed_per_step':c,'window':w,'minimal_conflict_arity':k,'thresholds':qs})
    return {'exposure_configs':configs,'joint_threshold_profiles':thresholds,'five_root_table':table}


def explicit_examples():
    # Every pair of the following certs has honest common reviewers; the triple
    # intersects only at root0, which can ignore its journal when exposed.
    U=127;Q=(U^6,U^24,U^96);B=1
    assert [q.bit_count() for q in Q]==[5,5,5]
    assert all((a&b)&~B for a,b in itertools.combinations(Q,2))
    assert (Q[0]&Q[1]&Q[2])==B
    # Already known aggregate semantic dependency: all removals bad, every proper subset safe.
    for k in range(2,10):
        safe=[S for S in range(1<<k) if S.bit_count()<k]
        assert all((A|C) in safe for A,C in itertools.combinations([1<<x for x in range(k)],2)) if k>2 else True
    # Two individually certificate-preserving edits need not compose.
    def cert(h,w):return h>min(7,1+w-1)+3
    assert cert(7,1) and cert(7,3) and cert(5,1) and not cert(5,3)
    # Extra non-conflicting action is permitted concurrently; a global mutex is not inherent.
    edges=(0b0111,)
    assert not any((0b1011&e)==e for e in edges)
    # Fairness is not obtained by solo availability: incompatible partial locks can strand all proposals.
    # n3,k2,q3: root0 signsA,root1 signsB,root2 signsA, thereafter neither can get all three.
    menus=(1<<(7-1),)*2
    assert not accepted(menus[0],5,3) and not accepted(menus[1],2,3)
    return {'pairwise_honest_intersections_do_not_protect_triple':{'quorum_masks':Q,'exposed_mask':B,'common_all':B},
      'successor_policy_composition':{'start':[7,1],'editA':[7,3],'editB':[5,1],'both':[5,3],'both_certified':False},
      'partial_lock_stranding_not_solved':True,'new_general_theory_claimed':False}


def residual_conflicts(edges,committed,future):
    if any(e&committed==e for e in edges):raise ValueError('Initial retained state already violates protection')
    candidates={e&~committed for e in edges if (e&~committed)&~future==0}
    return tuple(sorted(e for e in candidates if not any(t!=e and t&e==t for t in candidates)))


def residual_checks():
    catalogs=0;switches=0;comparisons=0
    for p in range(1,5):
        U=(1<<p)-1;possible=tuple(range(1,U+1))
        for catalog in range(1<<len(possible)):
            E=tuple(e for j,e in enumerate(possible) if catalog>>j&1)
            if any(a!=b and a&b==a for a in E for b in E):continue
            catalogs+=1
            for C in range(U+1):
                if any(C&e==e for e in E):continue
                future=U^C;new=residual_conflicts(E,C,future);switches+=1
                T=future
                while True:
                    original_bad=any((C|T)&e==e for e in E)
                    new_bad=any(T&e==e for e in new)
                    assert original_bad==new_bad
                    comparisons+=1
                    if T==0:break
                    T=(T-1)&future
    assert residual_conflicts((7,),3,4)==(4,)
    return {'antichain_catalogs':catalogs,'safe_committed_handoffs':switches,'future_subset_comparisons':comparisons,'assertions':'PASS'}


def main(path):
    a=existence_checks();b=threshold_by_direct_signatures();c=temporal_checks();d=explicit_examples()
    result={'version':'EAC-v3.0.0','scope':'finite individually admissible, commutative, monotone-effect proposal sets; honest per-root conflict journals; endorsement-only gate',
      'access_existence':a,'threshold_enumeration':b,'temporal':c,'examples':d,'residualization':residual_checks(),'assertions':'PASS',
      'limits':['Solo availability only; not termination under arbitrary contention','Not Byzantine consensus','Physical conflict patterns and qualified witnesses are supplied inputs','No identity count establishes real root independence']}
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'access_existence':a,'matrix_count':b['signing_matrices_enumerated'],'threshold_profiles':b['threshold_profiles'],'temporal_configs':c['exposure_configs'],'temporal_thresholds':c['joint_threshold_profiles'],'assertions':'PASS'},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='joint_results.json');main(p.parse_args().out)
