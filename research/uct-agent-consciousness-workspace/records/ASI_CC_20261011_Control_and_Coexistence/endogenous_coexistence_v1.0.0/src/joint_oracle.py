#!/usr/bin/env python3
"""Independent bounded attack-trace oracle across guards AND resources.

Enumerates actual individual persistent grants, root disabling, and per-demand
allocation at every reachable intermediate state. Compares with a separately
computed maximal closure + Hall criterion. Tests are synthetic role diagrams.
"""
from __future__ import annotations
from itertools import combinations,product
import argparse,json
from pathlib import Path
from authority_closure import Rule,powerset,reachable,closure,hall_check,demand_match


def individual_attack_bfs(seed,rules,guards,banks,allowed):
    obtained, states, paths=reachable(seed,rules)
    bad=[]
    for state in sorted(states,key=lambda z:(len(z),tuple(sorted(z)))):
        if guards<=state:
            bad.append({'state':sorted(state),'violation':'guard_path_open'})
        if demand_match(banks,allowed,len(allowed),state) is None:
            bad.append({'state':sorted(state),'violation':'human_support_missing'})
    return bool(bad),bad,len(states)

def terminal_certificate(seed,rules,guards,banks,allowed):
    last=closure(seed,rules)
    hall,obs=hall_check(banks,allowed,last)
    return guards<=last or not hall

def run():
    roots=('a','b','g1','g2')
    candidates=tuple(Rule(frozenset(pre),dst) for dst in roots
        for sz in (1,2) for pre in combinations([r for r in roots if r!=dst],sz))
    # Deterministic sparse/dense sweep rather than pseudo-random sampling.
    selected=[]
    for size in range(5):
        for idx,subset in enumerate(combinations(candidates,size)):
            if size<=2 or idx%max(1, [1,1,1,40,250][size])==0:
                selected.append(subset)
    guards=frozenset({'g1','g2'}); allowed={'human_A':['B1','B2','B3'], 'human_B':['B1','B2','B3']}
    oracle_checks=0;reachable_state_checks=0;unsafe=0;counter=[]
    for rules in selected:
        for assignments in product(('g1','g2','h'),repeat=3):
            banks=tuple((f'B{i+1}',1,(assignments[i],)) for i in range(3))
            for seed in powerset(('a','b')):
                got_bad,violations,nstates=individual_attack_bfs(seed,rules,guards,banks,allowed)
                pred_bad=terminal_certificate(seed,rules,guards,banks,allowed)
                assert pred_bad==got_bad,(rules,assignments,seed,violations)
                oracle_checks+=1;reachable_state_checks+=nstates
                if got_bad:unsafe+=1
                if got_bad and len(counter)<3:counter.append({'seed':sorted(seed),'owners':assignments,
                    'grant_rules':[{'need':sorted(r.need),'gain':r.gain} for r in rules],
                    'failure':violations[0]})
    return {'tested_rule_sets':len(selected),'seed_bank_assignments':oracle_checks,
        'explicit_reachable_states_audited':reachable_state_checks,
        'unsafe_seed_bank_instances':unsafe,
        'independent_BFS_vs_closure_and_Hall_exact_match':True,
        'adversarial_failure_samples':counter}

def main():
    a=argparse.ArgumentParser();a.add_argument('--out',default='joint_oracle_results.json');args=a.parse_args()
    d={'version':'ASI-CC-v1.0.0','scope':'Finite synthetic persistent authority grants and single-slot human-resource assignments',
       'result':run(),'assertions':'PASS'}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps({'result':{k:v for k,v in d['result'].items() if k!='adversarial_failure_samples'},'status':'PASS'},indent=2))
if __name__=='__main__':main()
