"""Exact counterexample to point inversion under merely bounded residual error.

This audits the R202 assumption wording; it does not change canonical research.
"""
from fractions import Fraction as F
from pathlib import Path
import json

pi, a, c = F(1, 2), F(3, 4), F(1, 4)
q = {0: F(1, 4), 1: F(3, 4)}
endpoint = {0: c, 1: a}
residual = F(1, 32)
conditional_tables = {}
for h in (0, 1):
    p11 = q[h] * endpoint[h] + residual
    cells = {(1, 1): p11,
             (1, 0): q[h] - p11,
             (0, 1): endpoint[h] - p11,
             (0, 0): 1 - q[h] - endpoint[h] + p11}
    assert all(v >= 0 for v in cells.values())
    assert sum(cells.values()) == 1
    conditional_tables[h] = cells
m = sum(F(1, 2) * q[h] for h in (0, 1))
j = sum(F(1, 2) * endpoint[h] for h in (0, 1))
r = sum(F(1, 2) * conditional_tables[h][(1, 1)] for h in (0, 1))
naive = {1: (r - c * m) / (j - c), 0: (a * m - r) / (a - j)}
corrected = {1: (r - c * m - residual) / (j - c),
             0: (a * m - r + residual) / (a - j)}
assert c < j < a
assert naive != q
assert corrected == q
result = {
    "status": "EXACT_COUNTEREXAMPLE_TO_OVERBROAD_POINT_IDENTIFICATION",
    "source": "R202 RESEARCH_NOTE.md section 4 assumption 3 and MAP_EXTENSION CONDITIONAL_NONDIFFERENTIALITY",
    "pi": str(pi), "a": str(a), "c": str(c),
    "true_q": {str(h): str(v) for h, v in q.items()},
    "conditional_MJ_tables": {str(h): {str(k): str(v) for k, v in d.items()} for h, d in conditional_tables.items()},
    "bounded_weighted_residual": str(residual),
    "observed": {"m": str(m), "j": str(j), "r": str(r)},
    "unadjusted_inversion": {str(h): str(v) for h, v in naive.items()},
    "residual_adjusted_inversion": {str(h): str(v) for h, v in corrected.items()},
    "interpretation": "Exact point inversion is valid at residual zero; a nonzero bound permits a jointly constrained identified set, not the displayed equalities."
}
path = Path(__file__).with_name("R202_RESIDUAL_COUNTEREXAMPLE.json")
path.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
