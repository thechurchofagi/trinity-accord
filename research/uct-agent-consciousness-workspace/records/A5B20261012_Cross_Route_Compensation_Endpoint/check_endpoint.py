#!/usr/bin/env python3
"""Exact finite checks for A5B's route-compensation endpoint.

The checker deliberately treats the observed compensation vector C as a
separate object from the participation relation Pi.  It then adds three
possible faithfulness contracts and reports the remaining ambiguity.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


ROUTES = (0, 1)
TARGETS = (0, 1)
NONEMPTY_ROUTE_SETS = ((0,), (1,), (0, 1))


def swap_relation(pi: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(sorted(1 - r for r in incident)) for incident in pi)


def canonical_orbit(pi: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    return min(pi, swap_relation(pi))


def joint_vector(pi: tuple[tuple[int, ...], ...]) -> tuple[int, int]:
    return tuple(int(len(incident) == 2) for incident in pi)  # type: ignore[return-value]


def strict_distributed(pi: tuple[tuple[int, ...], ...]) -> bool:
    return len(pi[0]) == len(pi[1]) == 1 and pi[0] != pi[1]


def global_single_owner(pi: tuple[tuple[int, ...], ...]) -> bool:
    return len(pi[0]) == len(pi[1]) == 1 and pi[0] == pi[1]


def compatible(c: tuple[int, int], j: tuple[int, int], mode: str) -> bool:
    if mode == "unconstrained":
        return True
    if mode == "no_spurious":  # C_t -> J_t
        return all(not c_t or j_t for c_t, j_t in zip(c, j))
    if mode == "no_missed":  # J_t -> C_t
        return all(not j_t or c_t for c_t, j_t in zip(c, j))
    if mode == "biconditional":
        return c == j
    raise ValueError(mode)


relations = tuple(itertools.product(NONEMPTY_ROUTE_SETS, repeat=2))
endpoints = tuple(itertools.product((0, 1), repeat=2))

results: dict[str, object] = {
    "schema": "A5B-CRCE-RESULT-v0.1.0",
    "domain": {
        "named_routes": len(ROUTES),
        "named_targets": len(TARGETS),
        "covered_relations": len(relations),
        "endpoint_vectors": len(endpoints),
        "unconstrained_joint_worlds": len(relations) * len(endpoints),
    },
}

orbits = {canonical_orbit(pi) for pi in relations}
results["route_swap_orbits"] = len(orbits)
results["relation_classes"] = {
    "strict_distributed": sum(strict_distributed(pi) for pi in relations),
    "global_single_owner": sum(global_single_owner(pi) for pi in relations),
    "joint_vector_distribution": dict(
        sorted(Counter("".join(map(str, joint_vector(pi))) for pi in relations).items())
    ),
}

contracts: dict[str, object] = {}
for mode in ("unconstrained", "no_spurious", "no_missed", "biconditional"):
    worlds = [
        (pi, c)
        for pi in relations
        for c in endpoints
        if compatible(c, joint_vector(pi), mode)
    ]
    by_endpoint: dict[str, object] = {}
    for c in endpoints:
        pis = [pi for pi, observed in worlds if observed == c]
        key = "".join(map(str, c))
        by_endpoint[key] = {
            "compatible_relations": len(pis),
            "compatible_orbits": len({canonical_orbit(pi) for pi in pis}),
            "includes_strict_distributed": any(strict_distributed(pi) for pi in pis),
            "includes_global_single_owner": any(global_single_owner(pi) for pi in pis),
            "joint_vectors": sorted({"".join(map(str, joint_vector(pi))) for pi in pis}),
        }
    contracts[mode] = {"worlds": len(worlds), "by_endpoint": by_endpoint}
results["faithfulness_contracts"] = contracts

# Explicit independence witnesses.
fixed_pi = ((0, 1), (0,))
same_endpoint = (0, 0)
results["countermodels"] = {
    "same_pi_different_W_endpoint": {
        "pi": fixed_pi,
        "endpoint_a": (0, 0),
        "endpoint_b": (1, 0),
        "interpretation": "A separately actual controller law W can change C while Pi is fixed.",
    },
    "different_orbits_same_endpoint": {
        "pi_global_single_owner": ((0,), (0,)),
        "pi_strict_distributed": ((0,), (1,)),
        "endpoint": same_endpoint,
        "distinct_orbits": canonical_orbit(((0,), (0,)))
        != canonical_orbit(((0,), (1,))),
        "interpretation": "C does not identify the Pi orbit without a faithfulness premise.",
    },
    "biconditional_residual_ambiguity": {
        "endpoint": (0, 0),
        "compatible_orbits": contracts["biconditional"]["by_endpoint"]["00"][
            "compatible_orbits"
        ],
        "interpretation": "Even C=J identifies targetwise jointness, not same-owner versus strict distribution.",
    },
}

assert len(relations) == 9
assert len(orbits) == 5
assert contracts["unconstrained"]["worlds"] == 36
assert contracts["no_spurious"]["worlds"] == 16
assert contracts["no_missed"]["worlds"] == 25
assert contracts["biconditional"]["worlds"] == 9
assert contracts["unconstrained"]["by_endpoint"]["00"]["compatible_orbits"] == 5
assert contracts["no_spurious"]["by_endpoint"]["00"]["compatible_orbits"] == 5
assert contracts["no_missed"]["by_endpoint"]["11"]["compatible_orbits"] == 5
assert contracts["biconditional"]["by_endpoint"]["00"]["compatible_orbits"] == 2

output = Path(__file__).with_name("EXACT_RESULTS.json")
output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({
    "covered_relations": len(relations),
    "route_swap_orbits": len(orbits),
    "world_counts": {mode: contracts[mode]["worlds"] for mode in contracts},
    "status": "PASS",
}, sort_keys=True))
