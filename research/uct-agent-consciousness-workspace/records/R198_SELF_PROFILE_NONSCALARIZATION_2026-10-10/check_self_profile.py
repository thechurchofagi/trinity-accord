#!/usr/bin/env python3
"""Exact finite checks for R198 self-profile non-scalarization.

This enumerates monotone Boolean functions.  It does not measure experience,
validate any coordinate in an actual system, or prove that experiential
relations are binary.  Dedekind-number combinatorics are standard mathematics.
"""

from itertools import product, permutations
import json
from pathlib import Path


def leq(x, y):
    return all(a <= b for a, b in zip(x, y))


def monotone(table, states):
    return all(not (leq(x, y) and table[x] > table[y]) for x in states for y in states)


def enumerate_monotone(n):
    states = list(product((0, 1), repeat=n))
    functions = []
    for values in product((0, 1), repeat=len(states)):
        table = dict(zip(states, values))
        if monotone(table, states):
            functions.append(table)
    return states, functions


def permutation_invariant(table, states):
    n = len(states[0])
    for x in states:
        for perm in permutations(range(n)):
            y = tuple(x[i] for i in perm)
            if table[x] != table[y]:
                return False
    return True


checks = []
summary = {}

for n, known_dedekind in ((2, 6), (3, 20), (4, 168)):
    states, functions = enumerate_monotone(n)
    assert len(functions) == known_dedekind
    nonconstant = [f for f in functions if f[(0,) * n] == 0 and f[(1,) * n] == 1]
    symmetric = [f for f in nonconstant if permutation_invariant(f, states)]
    assert len(nonconstant) == known_dedekind - 2
    assert len(symmetric) == n
    summary[str(n)] = {
        "all_monotone": len(functions),
        "endpoint_fixed_nonconstant": len(nonconstant),
        "coordinate_permutation_invariant": len(symmetric),
    }
    checks.append({
        "id": f"R198-T1-ENUM-{n}D",
        "pass": True,
        "cases": 2 ** (2 ** n),
        "statement": f"Exhaustive truth-table enumeration yields {known_dedekind - 2} nonconstant monotone scalarizations with fixed endpoints in {n} dimensions."
    })

# The two empirically motivated ownership/agency profiles are incomparable.
states2, functions2 = enumerate_monotone(2)
admissible2 = [f for f in functions2 if f[(0, 0)] == 0 and f[(1, 1)] == 1]
owned_passive = (1, 0)
controlled_unowned = (0, 1)
outcomes2 = {}
for f in admissible2:
    key = f"{f[owned_passive]}{f[controlled_unowned]}"
    outcomes2[key] = outcomes2.get(key, 0) + 1
assert outcomes2 == {"00": 1, "10": 1, "01": 1, "11": 1}
checks.append({
    "id": "R198-T2-OWNERSHIP-AGENCY-ANTICHAIN",
    "pass": True,
    "cases": len(admissible2),
    "statement": "The four admissible 2-D scalarizations realize all four label pairs on ownership-without-agency versus agency-without-ownership profiles."
})

# Four typed coordinates: ownership, agency, retentive familiarity, and current
# practical coupling.  Incomparable crossed profiles remain rank-underdetermined.
states4, functions4 = enumerate_monotone(4)
admissible4 = [f for f in functions4 if f[(0, 0, 0, 0)] == 0 and f[(1, 1, 1, 1)] == 1]
x = (1, 0, 1, 0)
y = (0, 1, 0, 1)
outcomes4 = {}
for f in admissible4:
    key = f"{f[x]}{f[y]}"
    outcomes4[key] = outcomes4.get(key, 0) + 1
assert all(outcomes4[k] > 0 for k in ("00", "01", "10", "11"))
assert sum(outcomes4.values()) == 166
checks.append({
    "id": "R198-T3-FOUR-AXIS-ANTICHAIN",
    "pass": True,
    "cases": len(admissible4),
    "statement": "All four comparative label outcomes remain possible for crossed four-coordinate profiles under admissible monotone scalarizations."
})

# Even the substantively unwarranted constraint that all typed coordinates are
# exchangeable leaves one threshold choice per possible positive count.
symmetric4 = [f for f in admissible4 if permutation_invariant(f, states4)]
threshold_vectors = sorted(tuple(f[tuple([1] * k + [0] * (4 - k))] for k in range(5)) for f in symmetric4)
expected_threshold_vectors = sorted([
    (0, 1, 1, 1, 1),
    (0, 0, 1, 1, 1),
    (0, 0, 0, 1, 1),
    (0, 0, 0, 0, 1),
])
assert threshold_vectors == expected_threshold_vectors
checks.append({
    "id": "R198-T4-SYMMETRY-INSUFFICIENT",
    "pass": True,
    "cases": len(symmetric4),
    "statement": "Even coordinate-permutation invariance leaves four different nonconstant monotone thresholds in four dimensions."
})

result = {
    "schema": "uct-r198-self-profile-check/1.0",
    "result_id": "R198-SPNS-RESULT-v0.1.0",
    "status": "PASS_DECLARED_FINITE_COMBINATORICS_ONLY",
    "coordinate_order": ["body_ownership", "action_agency", "retentive_familiarity", "current_practical_coupling"],
    "enumeration": summary,
    "two_axis_incomparable_profile_outcomes": outcomes2,
    "four_axis_incomparable_profile_outcomes": outcomes4,
    "symmetric_four_axis_threshold_vectors_by_positive_count_0_to_4": threshold_vectors,
    "total_truth_tables_examined": sum(item["cases"] for item in checks if "ENUM" in item["id"]),
    "checks": checks,
    "limitations": [
        "The result is conditional on a finite binary abstraction and coordinatewise monotonicity.",
        "The script does not establish that the four coordinates exhaust bodily or action-related self-experience.",
        "The script neither validates a scalar familiar-mineness variable nor selects an aggregation convention.",
        "No actual installation, route use, phenomenal state, report reliability, or current-system verdict is established."
    ]
}

out = Path(__file__).with_name("EXACT_RESULTS.json")
out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
