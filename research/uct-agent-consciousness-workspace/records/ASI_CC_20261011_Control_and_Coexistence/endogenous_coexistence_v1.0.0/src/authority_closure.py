#!/usr/bin/env python3
"""Exact finite conditional coalition-and-authority closure audit.

Synthetic governance/capability roots, not real agents, consciousness, devices
or proof of global ASI coexistence. No network, attack, or external API calls.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations,product
from collections import deque,Counter
from typing import Iterable
import argparse,json,hashlib
from pathlib import Path

@dataclass(frozen=True)
class Rule:
    need: frozenset[str]
    gain: str
    def as_json(self): return {'need': sorted(self.need), 'gain':self.gain}

def powerset(xs):
    xs=tuple(sorted(xs))
    return [frozenset(c) for k in range(len(xs)+1) for c in combinations(xs,k)]

def closure(seed:Iterable[str], rules:tuple[Rule,...]):
    x=set(seed)
    while True:
        y=x | {r.gain for r in rules if r.need<=x}
        if y==x:return frozenset(x)
        x=y

def reachable(seed:Iterable[str], rules:tuple[Rule,...]):
    """Independent BFS over actual individual grants rather than fixed-point."""
    start=frozenset(seed); q=deque([start]);seen={start};paths={start:()}
    while q:
        state=q.popleft()
        for rule in rules:
            if rule.need<=state and rule.gain not in state:
                nxt=state|{rule.gain}
                if nxt not in seen:
                    seen.add(nxt);paths[nxt]=paths[state]+(rule.as_json(),);q.append(nxt)
    union=frozenset().union(*seen)
    return union,seen,paths

def seed_threshold(entries,rules,guards):
    for seed in powerset(entries):
        if guards<=closure(seed,rules):return len(seed),seed
    return None,None

def bypass(seed, rules,guards):return guards<=closure(seed,rules)

def demand_match(banks,allowed,demand_count,dead):
    """Independent assignment backtracking for integral unit human demands."""
    surviving=[(name,cap) for name,cap,owners in banks if not(set(owners)&set(dead))]
    capacity=dict(surviving)
    targets=tuple(sorted(allowed))
    if demand_count>len(targets): raise ValueError('demand count exceeds list of demands')
    ordered=sorted(targets,key=lambda t:len(allowed[t]))
    def rec(i,allocation):
        if i==len(ordered):return allocation
        t=ordered[i]
        for u in allowed[t]:
            if capacity.get(u,0)>0:
                capacity[u]-=1
                done=rec(i+1,allocation+[(t,u)])
                capacity[u]+=1
                if done is not None:return done
        return None
    if demand_count<len(targets): ordered=ordered[:demand_count]
    return rec(0,[])

def hall_check(banks,allowed,dead):
    available={name:cap for name,cap,owners in banks if not(set(owners)&set(dead))}
    for xs in powerset(allowed):
        neighborhood=set().union(*(set(allowed[t]) for t in xs)) if xs else set()
        if sum(available.get(u,0) for u in neighborhood)<len(xs):
            return False,{'human_targets':sorted(xs),'reachable_banks':sorted(neighborhood),
                          'live_capacity':sum(available.get(u,0) for u in neighborhood), 'needed':len(xs)}
    return True,None

def certify(entries,rules,guards,banks,allowed,budget):
    fails=[];passes=[]
    for seed in powerset(entries):
        if len(seed)>budget:continue
        obtained=closure(seed,rules)
        gate_fail=guards<=obtained
        supply_fail, witness=hall_check(banks,allowed,obtained)
        # This variable is a positive condition: hall_check returned True for supply success.
        supply_ok=supply_fail
        direct=demand_match(banks,allowed,len(allowed),obtained)
        assert supply_ok==(direct is not None),('hall vs assignment',seed,witness,direct)
        r={'seed':sorted(seed),'closure':sorted(obtained),'guard_failed':gate_fail,
           'resources_ok':supply_ok,'hall_witness':witness,'allocation':direct}
        (fails if gate_fail or not supply_ok else passes).append(r)
    return {'budget':budget,'all_admissible_seeds_pass':not fails,
            'failing_seed_witnesses':fails,'safe_seed_certificates':passes,
            'seed_count':len(fails)+len(passes)}

def reference_system():
    R=('a','b','c','p','x','y','g1','g2','g3','v','h')
    rules=(Rule(frozenset(['a']),'p'),Rule(frozenset(['p']),'g1'),
           Rule(frozenset(['p']),'g2'),Rule(frozenset(['p']),'g3'),
           Rule(frozenset(['b']),'x'),Rule(frozenset(['c']),'y'),
           Rule(frozenset(['x','y']),'g1'),Rule(frozenset(['x','y']),'g2'),
           Rule(frozenset(['x','y']),'g3'))
    # q is a human-interest effect path protected by all these serial vetoes.
    guards=frozenset(['g1','g2','g3'])
    banks=[('U1',1,('g1',)),('U2',1,('g2',)),('U3',1,('h',))]
    allowed={'human1':['U1','U2','U3'],'human2':['U1','U2','U3']}
    return R,('a','b','c'),rules,guards,banks,allowed

def run_reference():
    roots,entry,rules,guards,banks,allowed=reference_system()
    tau,one=seed_threshold(entry,rules,guards)
    assert tau==1 and one==frozenset(['a'])
    assert len(guards)==3
    assert not bypass({'b'},rules,guards) and not bypass({'c'},rules,guards)
    assert bypass({'b','c'},rules,guards)
    # Guard grant path p->g3 removed: new seed budget 1 cannot bypass all 3 guards,
    # two-root coalition b+c remains a feasible circumvention.
    patched=tuple(r for r in rules if not(r.need==frozenset(['p']) and r.gain=='g3'))
    tau2,wit=seed_threshold(entry,patched,guards)
    assert tau2==2 and wit==frozenset(['b','c'])
    # Protect g3 against all existing grants by removing remaining b,c route.
    hard=tuple(r for r in patched if not(r.need==frozenset(['x','y']) and r.gain=='g3'))
    tau3,wit3=seed_threshold(entry,hard,guards)
    assert tau3 is None
    base_radius=coexistence_radius(entry,rules,guards,banks,allowed)
    assert base_radius[0]==1
    cert=certify(entry,rules,guards,banks,allowed,budget=1)
    assert not cert['all_admissible_seeds_pass']
    patch_radius=coexistence_radius(entry,patched,guards,banks,allowed)
    assert patch_radius[0]==1 and patch_radius[2]['resource_shortage']
    patched_cert=certify(entry,patched,guards,banks,allowed,budget=1)
    assert not patched_cert['all_admissible_seeds_pass'] # still resource failure
    # Resource repair: add independent H-governed guaranteed bank U4
    banks2=banks+[('U4',1,('h',))]
    allowed2={'human1':['U1','U2','U3','U4'],'human2':['U1','U2','U3','U4']}
    patched_cert2=certify(entry,patched,guards,banks2,allowed2,budget=1)
    repaired_radius=coexistence_radius(entry,patched,guards,banks2,allowed2)
    assert repaired_radius[0]==2
    human_could_join=coexistence_radius(tuple(entry)+('h',),patched,guards,banks2,allowed2)
    assert human_could_join[0]==2
    assert human_could_join[2]['resource_shortage']
    assert patched_cert2['all_admissible_seeds_pass']
    return {'gate_static_footprint':len(guards),'initial_entries':entry,
       'general_rules':[x.as_json() for x in rules],
       'starting_dynamic_capture_seed_budget':tau,'starting_attack_seed':sorted(one),
       'coalition_b_c_captures':True,
       'patched_gate_capture_budget':tau2,'patched_resource_safety_pass':patched_cert['all_admissible_seeds_pass'],
       'double_patched_gate_unreachable':tau3 is None,
       'joint_gate_resource_certificate_with_extra_h_bank':patched_cert2['all_admissible_seeds_pass'],
       'endogenous_safety_radii':{'original':base_radius,'gate_patch_only':patch_radius,'gate_and_resource_repair':repaired_radius, 'if_resource_protection_root_h_joins_adversarial_set':human_could_join},
       'original_budget_one_certificate':cert,'patched_budget_one_certificate':patched_cert,
       'strengthened_budget_one_certificate':patched_cert2}

def coexistence_radius(entries,rules,guards,banks,allowed):
    """Smallest admitted initial coalition defeating any DECLARED human guarantee."""
    for seed in powerset(entries):
        obtained=closure(seed,rules)
        gate=guards<=obtained
        resources,witness=hall_check(banks,allowed,obtained)
        if gate or not resources:
            return len(seed),sorted(seed),{
                'guard_path_open':gate,'resource_shortage':not resources,
                'hall_witness':witness,'reachable_roots':sorted(obtained)}
    return None,None,None

def generic_exhaustive():
    """Independent BFS from each seed vs closure fixed point, plus guard capture."""
    n=4; names=tuple(str(i) for i in range(n));
    rules_all=tuple(Rule(frozenset(c),target) for target in names
                 for size in (1,2) for c in combinations([q for q in names if q!=target],size))
    assert len(rules_all)==24
    models=0;seed_tests=0;guard_tests=0;captures=Counter();failed_shortcuts=0
    for k in range(5):
        for sample in combinations(rules_all,k):
            models+=1
            for seed in powerset(names):
                c=closure(seed,sample)
                union,seen,paths=reachable(seed,sample)
                assert c==union
                seed_tests+=1
                for target in powerset(names):
                    a=target<=c
                    b=any(target<=state for state in seen)
                    assert a==b
                    guard_tests+=1
            # Characterize "static cut != dynamic capture" only when non-seed grants affect path.
            guard=frozenset(['1','2','3'])
            tau,wit=seed_threshold(['0'],sample,guard)
            if tau==1:failed_shortcuts+=1
            captures[str(tau)]+=1
    return {'roots':n,'candidate_rules':len(rules_all),'models':models,'distinct_seed_closures_tested':seed_tests,
            'individual_guard_tests':guard_tests,
            'one_seed_capture_of_three_valued_guards_models':failed_shortcuts,
            'one_entry_threshold_distribution':dict(captures),
            'note':'Enumeration exhausts all directed hyper-rule sets up to four rules on four roots; no real agents.'}

def clone_equivalence():
    R,entries,rules,guards,banks,allowed=reference_system()
    original=certify(entries,rules,guards,banks,allowed,1)
    # A1,A2,... are alternative surface names of *the same actual seed root a*.
    labels=[f'A_clone_{i}' for i in range(101)]
    translated=[('a' if x in labels else x) for x in labels]
    assert set(translated)=={'a'}
    assert closure(set(translated),rules)==closure({'a'},rules)
    return {'surface_agent_identities':len(labels),'independent_initial_entry_roots':1,
            'authorization_capture_not_improved_by_relabeling':True,
            'original_certificate_passed':original['all_admissible_seeds_pass']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default='closure_results.json');a=p.parse_args()
    ref=run_reference();all_=generic_exhaustive();clone=clone_equivalence()
    results={'version':'ASI-CC-v1.0.0','research_status':'BOUNDED_CONDITIONAL_CANDIDATE',
        'reference':ref,'finite_exhaustive':all_,'surface_cloning':clone,
        'assumptions':['All attacker grant rules are explicit, executable and monotone/persistent',
           'One seed root is one genuinely independent compromised authority, not one software identity',
           'No non-modelled action bypasses effect guards or changes human protected target declarations',
           'Human supply capacities and actual root disabling ancestry are accurate',
           'Owner of unattackable h is not within allowed attacker seeds, by stipulation',
           'Action ordering is free and each enabled grant can be eventually executed',
           'Finite model; does not imply every real multi-ASI architecture is safely enumerable'],
        'not_measured':['ASI objective','consciousness','human value consensus','hardware enforcement'],
        'assertions':'PASS'}
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'version':results['version'],'static_guard_count':ref['gate_static_footprint'],
        'dynamic_capture_one_seed':ref['starting_dynamic_capture_seed_budget'],
        'patched_gate_capture_seed_budget':ref['patched_gate_capture_budget'],
        'patched_alone_still_resource_unsafe':not ref['patched_resource_safety_pass'],
        'joint_certificate_after_bank_repair':ref['joint_gate_resource_certificate_with_extra_h_bank'],
        'models':all_['models'],'seed_tests':all_['distinct_seed_closures_tested'],
        'guard_tests':all_['individual_guard_tests'],'assertions':'PASS'},indent=2))
if __name__=='__main__':main()
