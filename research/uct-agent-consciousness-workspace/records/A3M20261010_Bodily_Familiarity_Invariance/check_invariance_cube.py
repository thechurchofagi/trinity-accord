#!/usr/bin/env python3
"""Exact finite checks for the A3M bodily-familiarity invariance cube."""

from itertools import combinations, product
from pathlib import Path
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path)
args = parser.parse_args()

ROWS = list(product((0, 1), repeat=3))  # (R,Q,L)
PURE = {
    "B_ret": tuple(r for r, q, l in ROWS),
    "B_cue": tuple(q for r, q, l in ROWS),
    "B_fit": tuple(l for r, q, l in ROWS),
}


def invariant_to(table, axes):
    for x in ROWS:
        for axis in axes:
            y = list(x)
            y[axis] ^= 1
            if table[ROWS.index(x)] != table[ROWS.index(tuple(y))]:
                return False
    return True


def positive_on(table, axis):
    for x in ROWS:
        if x[axis] == 0:
            y = list(x)
            y[axis] = 1
            if table[ROWS.index(tuple(y))] <= table[ROWS.index(x)]:
                return False
    return True


def separating(subset):
    signatures = {
        name: tuple(values[i] for i in subset) for name, values in PURE.items()
    }
    return len(set(signatures.values())) == len(signatures), signatures


tables = list(product((0, 1), repeat=8))
route_invariant = [t for t in tables if invariant_to(t, (1, 2))]
route_positive = [t for t in route_invariant if positive_on(t, 0)]
cue_invariant = [t for t in tables if invariant_to(t, (0, 2))]
cue_positive = [t for t in cue_invariant if positive_on(t, 1)]
fit_invariant = [t for t in tables if invariant_to(t, (0, 1))]
fit_positive = [t for t in fit_invariant if positive_on(t, 2)]

minimal = []
for size in range(1, 9):
    for subset in combinations(range(8), size):
        ok, signatures = separating(subset)
        if ok:
            minimal.append(
                {
                    "indices": subset,
                    "rows": [ROWS[i] for i in subset],
                    "signatures": signatures,
                }
            )
    if minimal:
        break

diagonal = [ROWS.index((0, 0, 0)), ROWS.index((1, 1, 1))]
route_fit_plane = [i for i, (r, q, l) in enumerate(ROWS) if r == l]
star = [ROWS.index(x) for x in ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))]
held_out = [ROWS.index(x) for x in ((0, 1, 1), (1, 0, 1), (1, 1, 0))]

result = {
    "result_id": "A3M-EXACT-v0.1.0",
    "row_order": ROWS,
    "truth_tables_checked": len(tables),
    "pure_candidates": PURE,
    "route_only_invariant_tables": len(route_invariant),
    "route_only_positive_tables": len(route_positive),
    "cue_only_invariant_tables": len(cue_invariant),
    "cue_only_positive_tables": len(cue_positive),
    "fit_only_invariant_tables": len(fit_invariant),
    "fit_only_positive_tables": len(fit_positive),
    "minimal_observational_separating_size": len(minimal[0]["indices"]),
    "minimal_separating_examples": minimal,
    "natural_diagonal_signatures": {
        k: tuple(v[i] for i in diagonal) for k, v in PURE.items()
    },
    "route_equals_fluency_plane_signatures": {
        k: tuple(v[i] for i in route_fit_plane) for k, v in PURE.items()
    },
    "star_calibration_rows": [ROWS[i] for i in star],
    "star_signatures": {k: tuple(v[i] for i in star) for k, v in PURE.items()},
    "held_out_mismatch_rows": [ROWS[i] for i in held_out],
    "held_out_signatures": {
        k: tuple(v[i] for i in held_out) for k, v in PURE.items()
    },
}

assert len(route_invariant) == 4 and len(route_positive) == 1
assert len(cue_invariant) == 4 and len(cue_positive) == 1
assert len(fit_invariant) == 4 and len(fit_positive) == 1
assert len(minimal[0]["indices"]) == 2
assert len(set(tuple(v[i] for i in diagonal) for v in PURE.values())) == 1
assert PURE["B_ret"] != PURE["B_fit"] != PURE["B_cue"]
rendered = json.dumps(result, indent=2) + "\n"
if args.output:
    args.output.write_text(rendered)
print(rendered, end="")
