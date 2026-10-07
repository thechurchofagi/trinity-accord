#!/usr/bin/env python3
"""Exact finite checks for the R169 compositional route theorem."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
OUT = HERE / "EXACT_CHECKS.json"

def connected_graphs(n):
    possible = list(combinations(range(n), 2))
    for mask in range(1, 1 << len(possible)):
        edges = [possible[i] for i in range(len(possible)) if mask >> i & 1]
        seen = {0}; changed = True
        while changed:
            changed = False
            for a, b in edges:
                if a in seen and b not in seen: seen.add(b); changed = True
                if b in seen and a not in seen: seen.add(a); changed = True
        if len(seen) == n: yield edges

def shortest(n, edges, weights):
    inf = Fraction(10**9)
    d = [[inf] * n for _ in range(n)]
    for i in range(n): d[i][i] = Fraction(0)
    for (a, b), w in zip(edges, weights):
        d[a][b] = d[b][a] = min(d[a][b], w)
    for k in range(n):
        for i in range(n):
            for j in range(n): d[i][j] = min(d[i][j], d[i][k] + d[k][j])
    return d

values = (Fraction(0), Fraction(1, 2), Fraction(1))
graph_count = assignment_count = pair_checks = envelope_checks = specific_checks = 0
graph_counts = {}

for n in range(2, 5):
    graphs = list(connected_graphs(n)); graph_counts[str(n)] = len(graphs); graph_count += len(graphs)
    for edges in graphs:
        for flat in product(values, repeat=2*n):
            assignment_count += 1
            p = [flat[:n], flat[n:]]
            b = [max(abs(p[k][a]-p[k][c]) for k in range(2)) for a,c in edges]
            D = shortest(n, edges, b)
            e = [abs(p[0][z]-p[1][z]) for z in range(n)]
            for a in range(n):
                for c in range(n):
                    assert abs(e[a]-e[c]) <= 2*D[a][c]
                    pair_checks += 1
            # Pair-specific distances cannot be weaker than the uniform 2D route.
            D0 = shortest(n, edges, [abs(p[0][a]-p[0][c]) for a,c in edges])
            D1 = shortest(n, edges, [abs(p[1][a]-p[1][c]) for a,c in edges])
            for a in range(n):
                for c in range(n):
                    assert abs(e[a]-e[c]) <= D0[a][c] + D1[a][c] <= 2*D[a][c]
                    specific_checks += 1
            # All nonempty test sets for n<=3; singleton tests for n=4.
            masks = range(1, 1 << n) if n <= 3 else (1 << i for i in range(n))
            for mask in masks:
                tested = [i for i in range(n) if mask >> i & 1]
                for z in range(n):
                    env = min(Fraction(1), min(e[s] + 2*D[z][s] for s in tested))
                    assert e[z] <= env
                    envelope_checks += 1

# Scale gauge: L*d is exactly invariant under positive rational rescaling.
gauge_cases = 0
for d_num in range(0, 8):
    for l_num in range(0, 8):
        for c_num in range(1, 9):
            d = Fraction(d_num, 3); L = Fraction(l_num, 4); c = Fraction(c_num, 5)
            assert (L/c) * (c*d) == L*d
            gauge_cases += 1

# Exhaustive priority logic. Invalid dominates; then refuted; then certified; else unresolved.
status_counts = {}
for invalid, lower_violation, all_upper, coverage, challenge_valid in product((False, True), repeat=5):
    if invalid: status = "INVALID_ROUTE_PROTOCOL"
    elif challenge_valid and lower_violation: status = "CALIBRATION_REFUTED"
    elif all_upper and coverage: status = "ROUTE_ENVELOPE_CERTIFIED"
    else: status = "UNRESOLVED"
    status_counts[status] = status_counts.get(status, 0) + 1
assert sum(status_counts.values()) == 32

payload = {
    "schema": "UCT_R169_EXACT_CHECKS/v1",
    "finite_route_theorem": {
        "node_sizes": [2,3,4],
        "connected_graphs": graph_count,
        "graphs_by_nodes": graph_counts,
        "bernoulli_law_assignments": assignment_count,
        "effect_pair_checks": pair_checks,
        "route_envelope_checks": envelope_checks,
        "intervention_specific_checks": specific_checks,
        "probability_grid": ["0", "1/2", "1"]
    },
    "metric_scale_gauge": {"exact_rational_cases": gauge_cases, "identity": "(L/c)*(c*d)=L*d"},
    "status_priority": {"boolean_assignments": 32, "counts": status_counts},
    "claim_limits": {
        "actual_graph": False,
        "actual_edge_interventions": False,
        "physical_route_coverage": False,
        "continuum_cell_bound": False,
        "consumer_geometry_validated": False,
        "complete_organization_identified": False,
        "C1_derived": False,
        "B_min_validated": False,
        "basal_experience_gate": False
    }
}
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({
    "status": "PASS",
    "output": OUT.name,
    "sha256": sha256(OUT.read_bytes()).hexdigest(),
    "connected_graphs": graph_count,
    "assignments": assignment_count,
    "pair_checks": pair_checks,
    "envelope_checks": envelope_checks,
    "specific_checks": specific_checks,
    "gauge_cases": gauge_cases,
    "status_assignments": 32
}, indent=2))
