#!/usr/bin/env python3
"""Exact two-route/two-target check for A4Z."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

ROUTES = ("r1", "r2")
TARGETS = ("tau1", "tau2")
NONEMPTY_MASKS = (1, 2, 3)

def members(mask: int) -> list[str]:
    return [r for i, r in enumerate(ROUTES) if mask & (1 << i)]

def swap_routes(matrix: tuple[int, int]) -> tuple[int, int]:
    swap = {1: 2, 2: 1, 3: 3}
    return tuple(swap[m] for m in matrix)

def canonical_orbit(matrix: tuple[int, int]) -> tuple[int, int]:
    return min(matrix, swap_routes(matrix))

def main() -> None:
    matrices = list(itertools.product(NONEMPTY_MASKS, repeat=len(TARGETS)))
    local_unique = [m for m in matrices if all(x in (1, 2) for x in m)]
    global_owner = [m for m in local_unique if len(set(m)) == 1]
    coverage_countermodels = [m for m in matrices if m not in global_owner]
    local_unique_not_global = [m for m in local_unique if m not in global_owner]
    fixed_under_swap = [m for m in matrices if swap_routes(m) == m]
    orbits = {}
    for m in matrices:
        orbits.setdefault(canonical_orbit(m), []).append(m)
    rows = [{
        "matrix": {t: members(mask) for t, mask in zip(TARGETS, m)},
        "mask_tuple": list(m),
        "target_coverage": True,
        "local_target_uniqueness": m in local_unique,
        "global_single_owner": m in global_owner,
        "route_swap_orbit": list(canonical_orbit(m)),
    } for m in matrices]
    result = {
        "schema": "uct-a4z-exact-results/1.0",
        "round": "A4Z20261012_Target_Relational_Mineness_Family",
        "model": {
            "routes": list(ROUTES), "targets": list(TARGETS),
            "admitted_column_states": {"1": ["r1"], "2": ["r2"], "3": ["r1", "r2"]},
            "meaning": "Each target is indexed by a nonempty set of actual bearer-centred participating routes."
        },
        "counts": {
            "covered_relation_matrices": len(matrices),
            "locally_unique_matrices": len(local_unique),
            "global_single_owner_matrices": len(global_owner),
            "coverage_without_global_single_owner": len(coverage_countermodels),
            "local_uniqueness_without_global_single_owner": len(local_unique_not_global),
            "route_label_swap_fixed_matrices": len(fixed_under_swap),
            "route_label_swap_orbits": len(orbits),
        },
        "burnside_check": {
            "identity_fixed": len(matrices), "swap_fixed": len(fixed_under_swap),
            "orbit_count": (len(matrices) + len(fixed_under_swap)) // 2,
        },
        "rows": rows,
        "orbits": [{"canonical": list(k), "members": [list(m) for m in v]} for k, v in sorted(orbits.items())],
        "assertions": {
            "three_nonempty_states_per_target": len(matrices) == 3 ** 2 == 9,
            "coverage_does_not_entail_global_owner": len(coverage_countermodels) == 7,
            "local_uniqueness_does_not_entail_global_owner": len(local_unique_not_global) == 2,
            "route_label_swap_has_five_orbits": len(orbits) == 5,
            "only_all_both_is_swap_fixed": fixed_under_swap == [(3, 3)],
        },
        "scope_limit": "Finite exact combinatorics only; no actual installation, phenomenal identity, report validity, C1 confirmation, or subject count."
    }
    assert all(result["assertions"].values())
    Path(__file__).with_name("EXACT_RESULTS.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], sort_keys=True))

if __name__ == "__main__":
    main()
