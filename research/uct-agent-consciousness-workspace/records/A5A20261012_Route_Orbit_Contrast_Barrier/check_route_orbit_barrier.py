#!/usr/bin/env python3
"""Exact finite audit for A5A's route-orbit contrast barrier."""

from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict

ROUTE_STATES = ((0,), (1,), (0, 1))


def swap_routes(matrix: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(sorted(1 - route for route in column)) for column in matrix)


def orbit_key(matrix: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    swapped = swap_routes(matrix)
    return min(matrix, swapped)


def features(matrix: tuple[tuple[int, ...], ...]) -> dict[str, int | bool]:
    joint_count = sum(len(column) == 2 for column in matrix)
    local_unique = all(len(column) == 1 for column in matrix)
    strict_distributed = local_unique and matrix[0] != matrix[1]
    global_single_owner = local_unique and matrix[0] == matrix[1]
    return {
        "joint_target_count": joint_count,
        "any_joint_source": joint_count > 0,
        "all_joint_source": joint_count == len(matrix),
        "strict_distributed": strict_distributed,
        "local_unique": local_unique,
        "global_single_owner": global_single_owner,
    }


def encode(matrix: tuple[tuple[int, ...], ...]) -> list[list[int]]:
    return [list(column) for column in matrix]


def main() -> None:
    matrices = list(itertools.product(ROUTE_STATES, repeat=2))
    orbits: dict[tuple[tuple[int, ...], ...], list[tuple[tuple[int, ...], ...]]] = defaultdict(list)
    for matrix in matrices:
        orbits[orbit_key(matrix)].append(matrix)

    invariants = [
        "joint_target_count",
        "any_joint_source",
        "all_joint_source",
        "strict_distributed",
        "local_unique",
        "global_single_owner",
    ]
    invariant_checks = {}
    for name in invariants:
        violations = []
        for key, members in orbits.items():
            values = {features(member)[name] for member in members}
            if len(values) != 1:
                violations.append({"orbit": encode(key), "values": sorted(values)})
        invariant_checks[name] = {"constant_on_route_swap_orbits": not violations, "violations": violations}

    same_orbit_contrast_counts = {}
    for name in ("any_joint_source", "all_joint_source", "strict_distributed"):
        count = 0
        witnesses = []
        for members in orbits.values():
            for left, right in itertools.combinations(members, 2):
                if features(left)[name] != features(right)[name]:
                    count += 1
                    witnesses.append([encode(left), encode(right)])
        same_orbit_contrast_counts[name] = {"count": count, "witnesses": witnesses}

    distribution = {
        "joint_target_count": dict(sorted(Counter(features(matrix)["joint_target_count"] for matrix in matrices).items())),
        "strict_distributed": sum(bool(features(matrix)["strict_distributed"]) for matrix in matrices),
        "global_single_owner": sum(bool(features(matrix)["global_single_owner"]) for matrix in matrices),
        "local_unique": sum(bool(features(matrix)["local_unique"]) for matrix in matrices),
    }

    orbit_table = []
    for key in sorted(orbits):
        members = sorted(orbits[key])
        orbit_table.append({
            "representative": encode(key),
            "size": len(members),
            "members": [encode(member) for member in members],
            "features": features(key),
        })

    result = {
        "schema": "A5A-ORBIT-BARRIER-RESULT-v0.1.0",
        "domain": {"named_routes": 2, "named_targets": 2, "covered_relations": len(matrices)},
        "route_swap_orbits": len(orbits),
        "only_fixed_point": encode(((0, 1), (0, 1))),
        "distribution": distribution,
        "invariant_checks": invariant_checks,
        "same_orbit_contrast_counts": same_orbit_contrast_counts,
        "orbit_table": orbit_table,
        "conclusion": "No same-route-swap-orbit pair differs in any joint-source or strict-distribution predicate defined from Pi alone.",
    }
    assert len(matrices) == 9
    assert len(orbits) == 5
    assert all(check["constant_on_route_swap_orbits"] for check in invariant_checks.values())
    assert all(item["count"] == 0 for item in same_orbit_contrast_counts.values())
    assert distribution["joint_target_count"] == {0: 4, 1: 4, 2: 1}
    assert distribution["strict_distributed"] == 2
    assert distribution["global_single_owner"] == 2
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
