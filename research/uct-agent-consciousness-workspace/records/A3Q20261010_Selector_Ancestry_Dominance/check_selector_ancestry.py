#!/usr/bin/env python3
"""Exhaustive finite check for A3Q's ancestry/dominance separation.

This checks a declared graph model.  It does not discover a physical selector,
validate instrumentation, or establish a phenomenal interpretation.
"""
from itertools import product
import json

NODES = ("s", "p1", "p2", "z", "b", "d")
EDGES = (
    ("s", "p1"), ("s", "p2"),
    ("p1", "z"), ("p2", "z"), ("z", "d"),
    ("p1", "b"), ("p2", "b"), ("b", "d"), ("s", "d"),
)


def edge_set(mask):
    return {e for i, e in enumerate(EDGES) if mask & (1 << i)}


def reachable(edges, source, forbidden=None):
    if source == forbidden:
        return set()
    seen = {source}
    todo = [source]
    while todo:
        x = todo.pop()
        for a, y in edges:
            if a == x and y != forbidden and y not in seen:
                seen.add(y)
                todo.append(y)
    return seen


def ancestors(edges, target):
    return reachable({(b, a) for a, b in edges}, target)


def actual_resolution_use(edges):
    """Typed-event criterion inside this finite, faithfully interpreted DAG."""
    from_start = reachable(edges, "s")
    into_z = ancestors(edges, "z")
    from_z = reachable(edges, "z")
    return (
        {"p1", "p2", "z", "d"}.issubset(from_start)
        and {"p1", "p2"}.issubset(into_z)
        and "d" in from_z
    )


def resolver_dominates_dispatch(edges):
    """Every installed s-to-d path contains z (standard flowgraph dominance)."""
    return "d" in reachable(edges, "s") and "d" not in reachable(edges, "s", "z")


def serial(edges):
    return [f"{a}->{b}" for a, b in EDGES if (a, b) in edges]


counts = {"pairs": 0, "use_true": 0, "dominance_true": 0,
          "use_without_dominance": 0, "dominance_without_use": 0}
witnesses = {}
by_actual = {}
by_potential = {}

# Each edge is absent, potential-only, or actual (and therefore potential).
for states in product((0, 1, 2), repeat=len(EDGES)):
    potential = {e for e, state in zip(EDGES, states) if state >= 1}
    actual = {e for e, state in zip(EDGES, states) if state == 2}
    use = actual_resolution_use(actual)
    dom = resolver_dominates_dispatch(potential)
    counts["pairs"] += 1
    counts["use_true"] += int(use)
    counts["dominance_true"] += int(dom)
    counts["use_without_dominance"] += int(use and not dom)
    counts["dominance_without_use"] += int(dom and not use)
    if use and not dom and "use_without_dominance" not in witnesses:
        witnesses["use_without_dominance"] = {
            "actual": serial(actual), "potential": serial(potential)}
    actual_dispatch = "d" in reachable(actual, "s")
    if dom and not use and actual_dispatch and "dominance_without_use" not in witnesses:
        witnesses["dominance_without_use"] = {
            "actual": serial(actual), "potential": serial(potential)}
    akey = tuple(serial(actual))
    if use:
        by_actual.setdefault(akey, {})[dom] = serial(potential)
    pkey = tuple(serial(potential))
    if use or actual_dispatch:
        by_potential.setdefault(pkey, {})[use] = serial(actual)

same_actual = next((k, v) for k, v in by_actual.items() if set(v) == {False, True})
same_potential = next((k, v) for k, v in by_potential.items() if set(v) == {False, True})
witnesses["same_actual_different_dominance"] = {
    "actual": list(same_actual[0]),
    "potential_dominance_false": same_actual[1][False],
    "potential_dominance_true": same_actual[1][True],
}
witnesses["same_potential_different_actual_use"] = {
    "potential": list(same_potential[0]),
    "actual_use_false": same_potential[1][False],
    "actual_use_true": same_potential[1][True],
}

checks = {
    "use_does_not_imply_dominance": counts["use_without_dominance"] > 0,
    "dominance_does_not_imply_use": counts["dominance_without_use"] > 0,
    "one_actual_trace_allows_both_architectural_answers": bool(same_actual),
    "one_architecture_allows_both_actual_use_answers": bool(same_potential),
    "enumeration_complete": counts["pairs"] == 3 ** len(EDGES),
}
result = {
    "schema": "uct-a3q-selector-ancestry-check/1",
    "model": {
        "nodes": list(NODES),
        "candidate_edges": serial(set(EDGES)),
        "edge_states": ["absent", "potential_only", "actual_and_potential"],
        "mutual_exclusion_of_policies": "typed premise on p1 and p2",
    },
    "counts": counts,
    "checks": checks,
    "witnesses": witnesses,
    "scope": "Exact only for the declared finite graph semantics; physical fidelity is an open application premise.",
}
assert all(checks.values()), checks
print(json.dumps(result, indent=2, sort_keys=True))
