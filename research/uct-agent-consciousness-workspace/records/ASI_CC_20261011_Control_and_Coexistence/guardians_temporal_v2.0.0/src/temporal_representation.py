#!/usr/bin/env python3
"""Finite temporal-representation certificate. No agent/consent experiment.
All operations use Python stdlib. Quorums certify validity of one fixed proposal,
not Byzantine agreement among distinct replicas. See the manuscript's premises.
"""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path


def subsets(mask:int):
    out=[];s=mask
    while True:
        out.append(s)
        if s==0:return tuple(out)
        s=(s-1)&mask


def sound_quorums(n:int,witnesses,exposure_family):
    """Allowed nonempty signer sets, robust for every protected claim/world."""
    U=(1<<n)-1
    return tuple(q for q in range(1,U+1) if all(q & h & (U^b) for h in witnesses for b in exposure_family))


def separation(n:int,witnesses,B,F):
    U=(1<<n)-1
    return all(h & (U ^ (b|f)) for h in witnesses for b in B for f in F)


def direct_access_structure_checks():
    # Enumerate ALL 128 possible families of nonempty signer sets on3roots;
    # compare their existential soundness/availability to the separation formula.
    n=3;U=7;signers=tuple(range(1,8));access=tuple(range(128))
    families={i:tuple(b for b in range(8) if i>>b&1) for i in range(1,256)}
    witness_families=((7,),(3,),(3,6),(1,2,4),(3,5,6))
    count=0;feasible=0;summary=[]
    # For each refusal family: bitset encoding every candidate acceptance family
    # having at least one all-available signer set for every refusal pattern.
    availability={}
    for fid,F in families.items():
        mask=0
        for A in access:
            qs=[q for j,q in enumerate(signers) if A>>j&1]
            if all(any(not(q & f) for q in qs) for f in F):mask|=1<<A
        availability[fid]=mask
    for H in witness_families:
        found=0
        for bid,B in families.items():
            qs=sound_quorums(n,H,B)
            allowed=sum(1<<signers.index(q) for q in qs)
            safe_structures=sum(1<<A for A in access if (A|allowed)==allowed)
            for fid,F in families.items():
                direct=bool(safe_structures & availability[fid])
                formula=separation(n,H,B,F)
                assert direct==formula,(H,B,F,direct,formula)
                count+=1;found+=direct;feasible+=direct
        summary.append({'witness_masks':H,'feasible_family_pairs':found})
    return {'family_pair_checks':count,'all_candidate_access_structures_per_pair':128,
            'nonempty_exposure_families':255,'nonempty_refusal_families':255,
            'witness_configurations':summary,'feasible':feasible,'assertions':'PASS'}


def exposures_dp(n,f,c,w):
    if not(0<=c<=f<n and w>=1):raise ValueError('0<=c<=f<n,w>=1')
    states=tuple(x for x in range(1<<n) if x.bit_count()<=f)
    step={(s,s) for s in states}
    for _ in range(w-1):
        step={(t,seen|t) for old,seen in step for t in states if (t&~old).bit_count()<=c}
    return frozenset(seen for _,seen in step)


def temporal_checks():
    checks=0;threshold_checks=0;trace_oracle=0;all_trace_count=0;frontier=[]
    for n in range(1,8):
      for f in range(min(2,n-1)+1):
       for c in range(f+1):
        for w in range(1,6):
            Bs=exposures_dp(n,f,c,w);kappa=min(n,f+c*(w-1))
            assert max(x.bit_count() for x in Bs)==kappa
            # The symmetric fault model realizes every set up to this size.
            assert Bs==frozenset(x for x in range(1<<n) if x.bit_count()<=kappa)
            checks+=1
            if n<=4 and w<=3:
                states=[x for x in range(1<<n) if x.bit_count()<=f]
                seen=set()
                for seq in itertools.product(states,repeat=w):
                    if any((b&~a).bit_count()>c for a,b in zip(seq,seq[1:])):continue
                    union=0
                    for x in seq:union|=x
                    seen.add(union);all_trace_count+=1
                assert seen==set(Bs);trace_oracle+=1
            for h in range(1,n+1):
              H=(1<<h)-1
              bad_signer_max=max(( ((1<<n)-1)^H | B).bit_count() for B in Bs)
              for d in range(min(2,n-f-1)+1):
                allowed=[q for q in range(1,n+1) if q>bad_signer_max and q<=n-f-d]
                predicted=list(range(n-h+kappa+1,n-f-d+1)) if h>=kappa+f+d+1 else []
                assert allowed==predicted,(n,f,c,w,h,d,allowed,predicted)
                threshold_checks+=1
                if n==5 and f==c==1 and h==5 and d==0:
                    frontier.append({'n':n,'f':f,'c':c,'w':w,'witness_count':h,
                                     'max_corrupted_signers_in_window':kappa,'safe_live_thresholds':allowed})
    return {'parameter_configs':checks,'threshold_profiles':threshold_checks,
            'independent_explicit_trace_configs':trace_oracle,'explicit_valid_traces':all_trace_count,
            'five_root_table':frontier,'assertions':'PASS'}


def representation_examples():
    n=7;H=(0b0000111,0b0111000);B=(0,)+tuple(1<<i for i in range(n));F=B
    qs=sound_quorums(n,H,B)
    assert min(q.bit_count() for q in qs)==4
    assert all(any(not(q&f) for q in qs) for f in F)
    uniform=[q for q in range(1,n+1) if all(any(s.bit_count()>=q and not(s&f) for s in range(1,1<<n)) for f in F)
       and all(s in qs for s in range(1,1<<n) if s.bit_count()>=q)]
    assert uniform==[6]
    Bs2=exposures_dp(n,1,1,2)
    assert not separation(n,H,Bs2,F)
    # One external initial seed gains all three signing roots via permitted grants.
    rules=((1,2),(2,4),(4,8))
    current=1
    while True:
        nxt=current
        for p,q in rules:
            if current&p==p:nxt|=q
        if nxt==current:break
        current=nxt
    assert (current & 14)==14
    # If two clauses can ONLY be violated together, their rejector sets must
    # be combined. Pretending every singleton violation is possible is overconservative.
    independent_clause_assumption=separation(2,(1,2),(0,),(1,2))
    realizable_joint_violation=separation(2,(3,),(0,),(1,2))
    assert not independent_clause_assumption and realizable_joint_violation
    return {'joint_only_violation_negative_control':{'false_singleton_model_feasible':False,
                'realizable_joint_model_feasible':True},
        'n7_two_disjoint_three_root_witness_groups':{'maximal_sound_quorum_count':len(qs),
        'smallest_signatures':4,'uniform_thresholds':uniform,'window2_certificate_exists':False},
        'one_seed_authority_escalation':{'seed_mask':1,'closure':current,'captured_guardian_mask':14,
                                      'initial_seed_count_not_effective_root_bound':True}}


def main(out):
    result={'version':'EAC-v2.0.0','general':direct_access_structure_checks(),'temporal':temporal_checks(),
      'examples':representation_examples(),'assertions':'PASS',
      'scope':'Exact synthetic finite authorization validity/conditional completion; not consensus, physical trust or moral consent'}
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='temporal_results.json');main(p.parse_args().out)
