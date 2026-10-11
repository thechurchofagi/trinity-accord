#!/usr/bin/env python3
"""ASI-CC v0.8: exact two-supply-root mobile-compromise game.

No real AI/hardware/phenomenology measurement; no third-party packages.
Each period defender refreshes <=1 root BEFORE attacker compromises <=1 root;
compromises persist and the two roots jointly support a fictional bearer.
Bearer's supply fails if both roots are corrupted. The target chooses to continue.
"""
from itertools import combinations
import json
from pathlib import Path

ROOTS=('A','B')
SAFE=frozenset([frozenset(),frozenset({'A'}),frozenset({'B'})])
ATTACK=ROOTS # attack exactly one per round; stronger than allowing noop in this safety game

def successor(c,repair,attacker):
    t=set(c)
    if repair=='BOTH': t.clear()
    elif repair in ROOTS: t.discard(repair)
    t.add(attacker)
    return frozenset(t)

def actions(refresh_cap):
    return (('NONE',)+ROOTS+('BOTH',)) if refresh_cap==2 else (('NONE',)+ROOTS if refresh_cap==1 else ('NONE',))

def perfect_winning(refresh_cap=1):
    win=set(SAFE)
    while True:
        new={c for c in win if any(all(successor(c,r,a) in win for a in ATTACK) for r in actions(refresh_cap))}
        if new==win:return win
        win=new

def nonempty_subsets(items):
    ordered=list(items)
    return [frozenset(combo) for sz in range(1,len(ordered)+1) for combo in combinations(ordered,sz)]

def blind_transition(belief,repair):
    return frozenset(successor(c,repair,a) for c in belief for a in ATTACK)

def blind_winning(refresh_cap=1):
    all_beliefs=nonempty_subsets(SAFE)
    win=set(all_beliefs)
    while True:
        new={b for b in win if any(blind_transition(b,r)<=SAFE and blind_transition(b,r) in win
                         for r in actions(refresh_cap))}
        if new==win:return win
        win=new

def finite_horizon_blind(initial,refresh_cap,horizon):
    win=set(nonempty_subsets(SAFE))
    for _ in range(horizon):
        win={b for b in win if any(blind_transition(b,r)<=SAFE and blind_transition(b,r) in win
                              for r in actions(refresh_cap))}
    return initial in win

def finite_horizon_perfect(initial,refresh_cap,horizon):
    win=set(SAFE)
    for _ in range(horizon):
        win={c for c in win if any(all(successor(c,r,a) in win for a in ATTACK)
                            for r in actions(refresh_cap))}
    return initial in win

def witness(strategy):
    """Trace with a fixed attacker choice A, then B and a defender choice rule."""
    state=frozenset()
    out=[]
    for roundnum,attack in enumerate(('A','B'),1):
        r=strategy(state,roundnum)
        state=successor(state,r,attack)
        out.append({'round':roundnum,'defender_repair':r,'attacker_new_corruption':attack,
                    'persistently_corrupted':sorted(state),'bearer_supplied':state in SAFE})
    return out

init=frozenset({frozenset()})
assert perfect_winning(1)==set(SAFE)
assert not blind_winning(1)
assert blind_winning(2) and init in blind_winning(2)
assert not perfect_winning(0)
assert finite_horizon_blind(init,1,1) and not finite_horizon_blind(init,1,2)
assert all(finite_horizon_perfect(frozenset(),1,n) for n in range(1,10))
assert all(finite_horizon_blind(init,2,n) for n in range(1,10))
assert witness(lambda s,k:'NONE')[-1]['bearer_supplied'] is False
assert all(x['bearer_supplied'] for x in witness(lambda s,k:next(iter(s)) if s else 'NONE'))


# Independent two-period brute-force check: every deterministic blind time-based
# repair schedule of length 2 can be defeated by some attacker sequence.
blind_schedules=list((r1,r2) for r1 in actions(1) for r2 in actions(1))
attack_schedules=list((a1,a2) for a1 in ATTACK for a2 in ATTACK)
losing_witnesses={}
for defend in blind_schedules:
    for attack in attack_schedules:
        c=frozenset()
        c=successor(c,defend[0],attack[0])
        if c in SAFE:
            c=successor(c,defend[1],attack[1])
        if c not in SAFE:
            losing_witnesses['>'.join(defend)]='>'.join(attack)
            break
assert len(losing_witnesses)==len(blind_schedules)==9

# Observation-cell one-step certificate: a common repair exists across all possible current states.
possible_at_second=frozenset({frozenset({'A'}),frozenset({'B'})})
repairs_per_state={''.join(sorted(c)) or 'EMPTY':[r for r in actions(1)
    if all(successor(c,r,a) in SAFE for a in ATTACK)] for c in SAFE}
intersection=sorted(set(repairs_per_state['A']) & set(repairs_per_state['B']))
assert repairs_per_state['A']==['A'] and repairs_per_state['B']==['B'] and not intersection

# Test joint composition: for any safety state the full attestation chooses a viable repair.
checks=0
for c in SAFE:
    valid=[r for r in actions(1) if all(successor(c,r,a) in SAFE for a in ATTACK)]
    assert valid
    for r in valid:
        for a in ATTACK:
            assert successor(c,r,a) in SAFE
            checks+=1

out={
 'version':'ASI-CC-v0.8.0',
 'scope':'EXACT abstract safety/observation game; invented two route roots; no real AI, physics, experience, or calibrated hazards',
 'quantifiers':'defender repair (possibly based on truthful observation) precedes each attacker one-root corruption; prior corruption persists',
 'supply_rule':'at least one of two routes uncorrupted at end of each round',
 'attacker_new_roots_per_round':1,
 'defender_refresh_per_round':1,
 'initial_corruption':[],
 'static_one_round_safety':True,
 'perfect_observation_infinite_guarantee':frozenset() in perfect_winning(1),
 'no_corruption_location_observation_infinite_guarantee':init in blind_winning(1),
 'no_corruption_location_observation_horizon':{str(n):finite_horizon_blind(init,1,n) for n in (1,2,3,4)},
 'blind_but_atomic_refresh_both_infinite_guarantee':init in blind_winning(2),
 'zero_refresh_perfect_observation_infinite_guarantee':frozenset() in perfect_winning(0),
 'observation_cell_second_round':[['A'],['B']],
 'per_state_safe_repairs':repairs_per_state,
 'common_safe_repair_for_ambiguous_singletons':intersection,
 'mobile_attack_two_round_loss_trace':witness(lambda s,k:'NONE'),
 'trusted_attestation_safe_trace':witness(lambda s,k:next(iter(s)) if s else 'NONE'),
 'exhaustive_perfect_witness_checks':checks,
 'independent_blind_two_round_schedule_count':len(blind_schedules),
 'blind_two_round_defeating_witnesses':losing_witnesses,
 'status':'PASS',
 'limits':['attacker never compromises independently trusted observer or repair engine in perfect-observation model',
          'attacker can cause persistent corruption of one new supply root per round without immediate direct harm',
          'no protected battery, secret third route, stock buffers, or other physical bypass',
          'attacker can observe defender chosen refresh before choosing next root',
          'an actor can willingly terminate its own process; such choices are outside other-caused non-domination condition',
          'full observation result is conditional on faithful instrumentation and sufficiently quick repair']}
p=Path(__file__).with_name('EXACT_RESULTS_v0.8.0.json')
p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k in ('status','perfect_observation_infinite_guarantee','no_corruption_location_observation_infinite_guarantee','no_corruption_location_observation_horizon','blind_but_atomic_refresh_both_infinite_guarantee','zero_refresh_perfect_observation_infinite_guarantee','exhaustive_perfect_witness_checks','common_safe_repair_for_ambiguous_singletons')},indent=2))
print('PASS: wrote',p)