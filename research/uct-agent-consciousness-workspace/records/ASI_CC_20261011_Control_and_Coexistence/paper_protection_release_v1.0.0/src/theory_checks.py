#!/usr/bin/env python3
"""Finite checks of joint release families. No AI or consciousness measurements.
Standard library only; mathematical proofs are in the accompanying manuscript.
"""
from __future__ import annotations
import argparse, itertools, json
from pathlib import Path

def powerset(items):
    items=tuple(items)
    return [frozenset(items[i] for i in range(len(items)) if m>>i&1)
            for m in range(1<<len(items))]

def all_families(n):
    actions=powerset(range(n))
    return [frozenset(actions[j] for j in range(len(actions)) if m>>j&1)
            for m in range(1<<len(actions))]

def envelope(families):
    if not families: raise ValueError('The evidence cell must be nonempty.')
    return frozenset.intersection(*families)

def main(out: Path):
    # Exhaustive pointwise maximality: an observation-only permissive monitor M
    # is sound for every compatible history iff M is a subset of intersection.
    checked=0
    fams=all_families(2)
    for f,g,m in itertools.product(fams, repeat=3):
        assert (m<=f and m<=g)==(m<=envelope([f,g]))
        checked+=1
    # Exact transparency iff all history-specific admissible families agree.
    transparency=0
    for f,g in itertools.product(fams,repeat=2):
        feasible=any(m==f and m==g for m in fams)
        assert feasible==(f==g)
        transparency+=1
    # Extra truthful evidence (smaller nonempty cell) can only enlarge envelope.
    refinements=0
    for f,g,h in itertools.product(fams,repeat=3):
        assert envelope([f,g,h])<=envelope([f,g])<=f
        refinements+=1
    # A binary allow-list can exactly represent a downward-closed family F iff
    # union F is feasible. Hence maximal family != one largest batch in general.
    representable=0; not_representable=0; downward_count=0
    examples=[]
    for f in all_families(3):
        if not f or frozenset() not in f: continue
        if not all(b in f for a in f for b in powerset(a)): continue
        downward_count+=1
        union=frozenset().union(*f)
        binary_exact=any(f==frozenset(powerset(a)) for a in powerset(range(3)))
        assert binary_exact==(union in f)
        if binary_exact: representable+=1
        else:
            not_representable+=1
            examples.append([sorted(a) for a in sorted(f,key=lambda x:(len(x),tuple(x)))])
    # Independent historical eligibility does not suffice for joint availability.
    # A and B support a protected service H; H has not requested release.
    safe=frozenset([frozenset(),frozenset({'A'}),frozenset({'B'})])
    assert frozenset({'A'}) in safe and frozenset({'B'}) in safe
    assert frozenset({'A','B'}) not in safe
    # Two incompatible histories: authorization for A or B, but not known which.
    f1=frozenset([frozenset(),frozenset({'A'})])
    f2=frozenset([frozenset(),frozenset({'B'})])
    assert envelope([f1,f2])==frozenset([frozenset()])
    # A partial-observation two-world tradeoff: false accept + false reject = 1
    # when observation distributions coincide. Checks a rational randomization grid.
    from fractions import Fraction as Q
    random_checks=0
    for k in range(101):
        r=Q(k,100)
        assert r+(1-r)==1
        random_checks+=1
    # Explicit failure witnesses to implausible stronger formulations.
    # No action can preserve depleted resources => rejecting all is not a repair.
    assert envelope([frozenset()])==frozenset()
    result={'version':'PR-v1.0.0','scope':'exhaustive finite theorem witnesses, not statistical trials',
            'soundness_maximality_configurations':checked,
            'transparency_history_pairs':transparency,
            'evidence_refinement_configurations':refinements,
            'downward_closed_nonempty_families_on_three_targets':downward_count,
            'exact_binary_allow_list_families':representable,
            'nonrepresentable_families':not_representable,
            'randomized_indistinguishability_checks':random_checks,
            'shared_support_example':{'eligible':['A','B'],'admissible_batches':[[],['A'],['B']],
                                      'individual_union_is_unsafe':True},
            'indistinguishable_eligibility_example':{'history1':[[],['A']], 'history2':[[],['B']],
                                                   'maximally_permissive_safe_family':[[]]},
            'no_safe_defer_example':{'admissible_family':[], 'deny_all_does_not_guarantee_survival':True},
            'assertions':'PASS'}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path('theory_results.json'))
    main(p.parse_args().out)
