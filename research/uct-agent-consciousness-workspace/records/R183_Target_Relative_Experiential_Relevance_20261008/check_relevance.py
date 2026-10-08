#!/usr/bin/env python3
"""Exact finite checks for R183 target-relative constitutive relevance.

The set-family facts are standard finite order/set theory.  The program checks
the R183 application and its boundary conditions; it is not evidence for C1 or
for any named phenomenal interpretation.
"""

from itertools import combinations
import json


def powerset(items):
    items = tuple(items)
    return tuple(
        frozenset(c)
        for r in range(len(items) + 1)
        for c in combinations(items, r)
    )


def minimal_members(family):
    return frozenset(s for s in family if not any(t < s for t in family))


def intersection(family, universe):
    out = set(universe)
    for s in family:
        out.intersection_update(s)
    return frozenset(out)


def is_upward_closed(family, all_sets):
    return all(not (s <= t) or t in family for s in family for t in all_sets)


def inclusion_minimal_hitting_sets(family, all_sets):
    hits = [h for h in all_sets if all(h & s for s in family)]
    return frozenset(h for h in hits if not any(g < h for g in hits))


def canonical(family):
    return sorted([sorted(s) for s in family], key=lambda s: (len(s), s))


def main():
    universe = frozenset(range(4))
    all_sets = powerset(universe)
    nonempty_families = 0
    upward_families = []
    checked_relation_instances = 0
    core_size_distribution = {str(k): 0 for k in range(5)}

    for mask in range(1, 1 << len(all_sets)):
        family = frozenset(all_sets[i] for i in range(len(all_sets)) if mask >> i & 1)
        nonempty_families += 1
        minima = minimal_members(family)
        core_all = intersection(family, universe)
        core_min = intersection(minima, universe)
        assert core_all == core_min
        for r in universe:
            checked_relation_instances += 1
            assert ((r in core_min) == all(r in s for s in family))
        if is_upward_closed(family, all_sets):
            upward_families.append(family)
            core_size_distribution[str(len(core_min))] += 1
            assert universe in family
            for r in universe:
                deletion_critical_at_full = frozenset(universe - {r}) not in family
                assert deletion_critical_at_full == (r in core_min)

    assert nonempty_families == 65535
    assert len(upward_families) == 167

    # Three inherited EI route architectures, now classified by the typed R183
    # criterion. B is a background relation held fixed in this tiny view.
    h, q, b = "H", "Q", "B"
    views = frozenset({h, q, b})
    view_sets = powerset(views)
    architecture_predicates = {
        "shared": lambda s: h in s and b in s,
        "bypass": lambda s: q in s and b in s,
        "redundant": lambda s: (h in s or q in s) and b in s,
    }
    architecture_results = {}
    for name, success in architecture_predicates.items():
        family = frozenset(s for s in view_sets if success(s))
        minima = minimal_members(family)
        architecture_results[name] = {
            "minimal_supports": canonical(minima),
            "unavoidable_individual_relations": sorted(intersection(minima, views)),
            "minimal_disjunctive_hitting_sets": canonical(
                inclusion_minimal_hitting_sets(minima, view_sets)
            ),
        }

    assert architecture_results["shared"]["unavoidable_individual_relations"] == ["B", "H"]
    assert architecture_results["bypass"]["unavoidable_individual_relations"] == ["B", "Q"]
    assert architecture_results["redundant"]["unavoidable_individual_relations"] == ["B"]
    assert ["H", "Q"] in architecture_results["redundant"]["minimal_disjunctive_hitting_sets"]

    # A report relation can change a declared complete signature without
    # changing the selected arithmetic target. This checks logical separation,
    # not actual realization or a phenomenal report interpretation.
    report = "R"
    selected_with_report = frozenset({h, b, report})
    selected_without_report = frozenset({h, b})
    shared_success = architecture_predicates["shared"]
    assert shared_success(selected_with_report)
    assert shared_success(selected_without_report)
    assert selected_with_report != selected_without_report

    result = {
        "schema": "uct-r183-exact-checks-v1",
        "universe_size": 4,
        "all_nonempty_success_families": nonempty_families,
        "all_relation_family_instances_checked": checked_relation_instances,
        "nonempty_upward_closed_families": len(upward_families),
        "upward_family_core_size_distribution": core_size_distribution,
        "verified": [
            "intersection of all successes equals intersection of all inclusion-minimal successes",
            "a relation is in that intersection iff every successful support contains it",
            "for nonempty upward-closed families, full-support single deletion is critical iff the relation is in the intersection",
            "all 167 monotone success families agree on intact full-support success yet can have different dependence profiles",
            "shared, bypass and redundant EI witnesses have different unavoidable individual relations",
            "redundancy can require the disjunction {H,Q} while requiring neither H nor Q individually",
            "a selected report relation can change while the fixed arithmetic target remains successful",
        ],
        "architecture_results": architecture_results,
        "limits": [
            "finite selected-support families only",
            "monotonicity is required only for the full-support single-deletion equivalence",
            "no actual human, AI or calculator token is established",
            "no C1 validation or named-feeling measurement is performed",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
