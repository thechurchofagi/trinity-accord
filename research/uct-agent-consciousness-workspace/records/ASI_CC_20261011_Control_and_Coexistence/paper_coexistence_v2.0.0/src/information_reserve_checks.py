#!/usr/bin/env python3
"""Evidence-dependent reserve bounds. Exact toy cases, not AI measurements.

A committed allocation must use the same resource-to-target assignment in every
scenario in its observation cell. No hidden downstream adaptive router is allowed.
Standard library only; run with --out PATH.
"""
from __future__ import annotations
import argparse, itertools, json
from pathlib import Path
from frontier_checks import cut_reserve, assignment_possible


def common_graph(scenarios):
    """scenarios = [(target neighborhoods, per-resource integer capacities)]."""
    target_count=len(scenarios[0][0]); resource_count=len(scenarios[0][1])
    neighbors=tuple(tuple(sorted(set.intersection(*(set(ns[j]) for ns,_ in scenarios))))
                    for j in range(target_count))
    caps=tuple(min(cs[u] for _,cs in scenarios) for u in range(resource_count))
    return neighbors,caps


def static_brute_min(scenarios,demands):
    """Enumerate complete demand-slot assignments, check ALL scenarios directly.

    Does not construct the common graph, and does not call the cut formula.
    An extra universal resource can be used at most r times in any assignment.
    """
    nres=len(scenarios[0][1]); slots=tuple(j for j,d in enumerate(demands) for _ in range(d))
    for r in range(sum(demands)+1):
        for assignment in itertools.product(range(nres+1),repeat=len(slots)):
            used=tuple(assignment.count(u) for u in range(nres+1))
            if used[-1]>r: continue
            if all(all(used[u]<=cs[u] for u in range(nres)) and
                   all(u==nres or u in ns[j] for j,u in zip(slots,assignment))
                   for ns,cs in scenarios):
                return r
    raise AssertionError('Universal reserve of full demand must suffice')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='information_reserve_results.json');args=ap.parse_args()
    # Every ordered pair of 2x2 binary connection graphs and two demand patterns.
    graphs=[]
    for mask in range(16):
        graphs.append(tuple(tuple(u for u in range(2) if mask & (1<<(j*2+u))) for j in range(2)))
    checked=0; strict_gap=0
    for ga,gb,demands,ca,cb in itertools.product(graphs,graphs,((1,1),(1,2)),((1,1),(2,0)),((1,1),(0,2))):
        scenes=((ga,ca),(gb,cb)); ng,cg=common_graph(scenes)
        formula,_=cut_reserve(ng,demands,(cg,))
        brute=static_brute_min(scenes,demands)
        assert formula==brute
        adaptive=max(cut_reserve(g,demands,(c,))[0] for g,c in scenes)
        assert adaptive<=formula
        strict_gap+=formula>adaptive;checked+=1
    # n cyclic scenarios, n-1 unit resources, n unit-demand targets.
    # Each resource can reach one distinct target per scenario; no edge survives
    # intersection of two distinct scenarios. Full information needs one reserve.
    family=[]
    for n in range(2,9):
        scenes=[]
        for shift in range(n):
            ns=tuple(tuple(u for u in range(n-1) if (u+shift)%n==j) for j in range(n))
            scenes.append((ns,tuple(1 for _ in range(n-1))))
        demands=(1,)*n
        adaptive=max(cut_reserve(g,demands,(c,))[0] for g,c in scenes)
        ng,cg=common_graph(scenes);blind=cut_reserve(ng,demands,(cg,))[0]
        assert adaptive==1 and blind==n and all(not x for x in ng)
        independently_bruted=static_brute_min(scenes,demands) if n<=4 else None
        if independently_bruted is not None:assert independently_bruted==blind
        family.append({'n_targets':n,'scenarios':n,'existing_units':n-1,
                       'fully_observed_min_reserve':adaptive,'blind_committed_min_reserve':blind,
                       'direct_assignment_brute_min_if_n_le_4':independently_bruted})
    result={'schema':'PR-v2.0.0/evidence-reserve/1','scope':'Exact finite resource/observation examples; no AI/hardware data',
            'ordered_two_scenario_configs':checked,'strict_information_gaps':strict_gap,
            'all_formula_vs_independent_assignment_checks_passed':True,'cyclic_gap_family':family,
            'premises':['Fixed labeled resource-to-target allocation in each observation cell',
                        'No downstream unobserved adaptive routing','Universal reliable reserve',
                        'Integer demands/capacities','Scenarios correctly enumerate remaining possibilities'],
            'theory':'Common-edge graph plus componentwise minimum capacity; Hall deficit. Inherited robust-allocation and matching methods.'}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
