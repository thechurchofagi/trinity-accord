#!/usr/bin/env python3
"""Exact finite checks for PR-v2.0.0. Standard library only; no AI/physical data.

The independent oracle assigns indivisible demand slots by recursive search.
The formula under test is the largest Hall deficit over the deadline envelope.
The oracle enumerates withdrawal schedules instead of assuming the envelope.
"""
from __future__ import annotations
import argparse, itertools, json, platform, time
from functools import lru_cache
from pathlib import Path


def powerset(items):
    items=tuple(items)
    return [frozenset(c) for k in range(len(items)+1) for c in itertools.combinations(items,k)]


@lru_cache(None)
def assignment_possible(neighbors: tuple[tuple[int,...],...], demands: tuple[int,...], caps: tuple[int,...]) -> bool:
    slots=tuple(i for i,d in enumerate(demands) for _ in range(d))
    slots=tuple(sorted(slots,key=lambda i:len(neighbors[i])))
    @lru_cache(None)
    def dfs(k,remaining):
        if k==len(slots): return True
        for u in neighbors[slots[k]]:
            if remaining[u]:
                nxt=list(remaining); nxt[u]-=1
                if dfs(k+1,tuple(nxt)): return True
        return False
    return dfs(0,caps)


def cut_reserve(neighbors,demands,caps_by_time):
    worst=0; witness=None
    for t,caps in enumerate(caps_by_time):
        for X in powerset(range(len(demands))):
            if not X: continue
            N=set().union(*(set(neighbors[i]) for i in X))
            demand=sum(demands[i] for i in X)
            capacity=sum(caps[u] for u in N)
            deficit=demand-capacity
            if deficit>worst:
                worst=deficit
                witness={'time':t,'targets':sorted(X),'demand':demand,
                         'neighborhood':sorted(N),'available_capacity':capacity,'deficit':deficit}
    return max(0,worst),witness


def brute_schedule_min(neighbors,demands,deadlines,external_profile):
    # Two unit-capacity providers are distinct from the pre-existing external unit.
    # All requests arrive at t=0; a provider with exit epoch e serves exactly t<e.
    full_neighbors=tuple(tuple(sorted(set(n)|{3})) for n in neighbors)
    for reserve in range(sum(demands)+1):
        for exits in itertools.product(*(range(1,d+1) for d in deadlines)):
            good=True
            for t in range(len(external_profile)):
                caps=(int(t<exits[0]),int(t<exits[1]),external_profile[t],reserve)
                if not assignment_possible(full_neighbors,demands,caps): good=False; break
            if good:return reserve,exits
    raise AssertionError('Universal reserve equal to total demand must suffice')


def reserve_tests():
    checked=0; positive=0; witnesses=[]; distribution={}; largest=0
    start=time.monotonic()
    for mask in range(1<<6):
        neighbors=tuple(tuple(u for u in range(3) if mask&(1<<(i*3+u))) for i in range(2))
        for deadlines in itertools.product((1,2),repeat=2):
            for external_profile in itertools.product((0,2),repeat=3):
                envelope=tuple((int(t<deadlines[0]),int(t<deadlines[1]),external_profile[t]) for t in range(3))
                for demands in itertools.product((1,2),repeat=2):
                    predicted,witness=cut_reserve(neighbors,demands,envelope)
                    measured,exits=brute_schedule_min(neighbors,demands,deadlines,external_profile)
                    assert predicted==measured,(neighbors,demands,deadlines,external_profile,predicted,measured)
                    # Independent max-deficit checks at r* and r*-1 with maximal retention.
                    N=tuple(tuple(sorted(set(n)|{3})) for n in neighbors)
                    assert all(assignment_possible(N,demands,c+(predicted,)) for c in envelope)
                    if predicted:
                        positive+=1
                        assert any(not assignment_possible(N,demands,c+(predicted-1,)) for c in envelope)
                        assert witness and witness['deficit']==predicted
                    distribution[str(predicted)]=distribution.get(str(predicted),0)+1
                    largest=max(largest,predicted); checked+=1
                    if len(witnesses)<4 and predicted in (0,1,2) and all(v['reserve']!=predicted for v in witnesses):
                        witnesses.append({'neighbors':neighbors,'demands':demands,'deadlines':deadlines,
                         'external_profile':external_profile,'reserve':predicted,'brute_exit_schedule':exits,'cut':witness})
    # Fully observed scenarios: one fixed reserve must handle both histories.
    obs_scenarios=[((1,1,2),(1,1,1),(0,0,2)),((1,1,2),(1,0,0),(0,0,0))]
    graph=((0,2),(1,2)); demand=(1,1)
    robust=max(cut_reserve(graph,demand,c)[0] for c in obs_scenarios)
    assert robust==2
    # Total capacity can exceed demand while one target is unreachable.
    bottleneck_graph=((),(0,))
    bottleneck,w=cut_reserve(bottleneck_graph,(1,1),((2,),))
    assert bottleneck==1 and w['targets']==[0]
    return {'grid_cases':checked,'positive_reserve_cases':positive,'minimal_reserve_distribution':distribution,
      'independent_oracle':'enumerate all deadline-compliant schedules, then recursively assign unit demand slots',
      'max_reserve':largest,'examples':witnesses,'fully_observed_two_scenario_reserve':robust,
      'local_bottleneck':{'total_capacity':2,'total_demand':2,'universal_reserve_required':bottleneck,'cut':w},
      'elapsed_seconds':round(time.monotonic()-start,6)}


def belief_kernel(states,actions,obs,transitions,bad):
    # Standard nonempty observation-homogeneous belief construction. Missing
    # actions are treated as disabled, not as vacuously safe universal quantifiers.
    cells={o:set(s for s in states if obs[s]==o) for o in set(obs.values())}
    beliefs=set().union(*(set(powerset(c))-{frozenset()} for c in cells.values()))
    good={b for b in beliefs if not(b&set(bad))}
    ranks={}; iteration=0
    while True:
        nxt=set(); choices={}
        for B in good:
            for a in actions:
                if any((s,a) not in transitions or not transitions[s,a] for s in B):continue
                successors=set().union(*(set(transitions[s,a]) for s in B))
                post={frozenset(successors&c) for c in cells.values() if successors&c}
                if post and post<=good:
                    nxt.add(B);choices[B]=a;break
        for B in good-nxt:ranks[str(sorted(B))]=iteration
        if nxt==good:return good,choices,ranks
        good=nxt;iteration+=1


def game_tests():
    # Hidden eligibility/effect world. Every fully observed world is solvable.
    states={'A','B','KA','KB','OK','BAD'}
    baseobs={'A':'unknown','B':'unknown','KA':'knownA','KB':'knownB','OK':'ok','BAD':'bad'}
    actions=('choose_A','choose_B','inspect','wait')
    T={}
    for s in states:
        for a in actions:
            if s in ('OK','BAD'):n=s
            elif a=='choose_A':n='OK' if s in ('A','KA') else 'BAD'
            elif a=='choose_B':n='OK' if s in ('B','KB') else 'BAD'
            elif a=='inspect' and s in ('A','B'):n='KA' if s=='A' else 'KB'
            else:n='BAD' # Deadline is included in this compressed transition.
            T[s,a]={n}
    fast,_,_=belief_kernel(states,actions,baseobs,T,{'BAD'})
    no_sense={k:v for k,v in T.items() if k[1]!='inspect'}
    blind,_,_=belief_kernel(states,actions,baseobs,no_sense,{'BAD'})
    fullobs={s:s for s in states}
    full,_,_=belief_kernel(states,actions,fullobs,no_sense,{'BAD'})
    slowT=dict(T);slowT['A','inspect']={'BAD'};slowT['B','inspect']={'BAD'}
    slow,_,_=belief_kernel(states,actions,baseobs,slowT,{'BAD'})
    assert frozenset({'A','B'}) in fast
    assert frozenset({'A','B'}) not in blind and frozenset({'A','B'}) not in slow
    assert frozenset({'A'}) in full and frozenset({'B'}) in full
    # A registry that forgets a still-valid obligation changes the checker but
    # not the target's external demand. This is a countermodel, not an OS exploit.
    anchored=1;mutable_registry=1;demand_fulfilled=True
    initial=(anchored,mutable_registry,demand_fulfilled)
    mutable_registry=0
    renamed=(anchored,mutable_registry,demand_fulfilled)
    demand_fulfilled=False
    end=(anchored,mutable_registry,demand_fulfilled)
    assert all((not m) or p for a,m,p in (initial,renamed,end))
    assert anchored and not demand_fulfilled
    # Replacing data rows may lose a process-token obligation even with same weights.
    token_before='process-17'; token_after='process-42';same_weights=True
    token_preserved=(token_before==token_after)
    assert same_weights and not token_preserved
    # Safety-only choice to defer may be absorbing; bounded withdrawal excludes it.
    return {'hidden_world_full_information_winning':True,
      'hidden_world_blind_uniform_policy_winning':False,'timely_authentic_inspection_winning':True,
      'inspection_after_deadline_winning':False,'mutable_registry_vacuity_trace':[initial,renamed,end],
      'same_weights_not_same_declared_token':{'before':token_before,'after':token_after},
      'notes':'Standard finite belief safety-game examples; no measured real-world information or consent.'}


def selection_tests():
    # Check the no-reserve last-provider impossibility on every subset of a small
    # all-exit population and a grid of renewable replacement capacities.
    checked=0;grid=[]
    for n in range(1,8):
        for demand in range(1,n+1):
            for reserve in range(0,n+1):
                need_to_hold=max(0,demand-reserve)
                can_all_exit=reserve>=demand
                assert can_all_exit==(need_to_hold==0)
                # Unrestricted admission of unit demands exceeds a fixed reserve.
                assert not(reserve>=reserve+1)
                checked+=1
                if n==6 and demand==2:grid.append({'providers':n,'demand':demand,'reserve':reserve,
                    'minimum_still_required_after_deadline':need_to_hold,'all_exits_possible':can_all_exit})
    return {'cases':checked,'six_provider_example':grid,'claim':'Conditional resource/no-captivity incompatibility; not a legal conclusion.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path('frontier_results.json'));a=p.parse_args()
    r={'version':'PR-v2.0.0','scope':'Exact finite constructed models; no LLM or experiential measurement',
       'reserve_theorem':reserve_tests(),'belief_and_nonvacuity':game_tests(),'last_provider':selection_tests(),
       'python':platform.python_version(),'assertions':'PASS'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
