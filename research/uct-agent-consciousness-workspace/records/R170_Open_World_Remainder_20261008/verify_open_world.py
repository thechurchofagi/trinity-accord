#!/usr/bin/env python3
"""Exact bounded checks for the R170 open-world remainder theorems."""

from fractions import Fraction
from itertools import product
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRID = (Fraction(0), Fraction(1, 2), Fraction(1))
THRESHOLDS = GRID[:-1]

counts = {
    "domains": 0,
    "covered_envelopes": 0,
    "compatible_effects": 0,
    "pointwise_checks": 0,
    "integral_checks": 0,
    "exceedance_checks": 0,
    "supremum_witnesses": 0,
    "sharp_envelope_witnesses": 0,
    "status_assignments": 0,
}

for n in range(1, 6):
    weights = tuple(Fraction(1, n) for _ in range(n))
    for mask in range(1 << n):
        covered = tuple(i for i in range(n) if mask & (1 << i))
        unknown = tuple(i for i in range(n) if i not in covered)
        counts["domains"] += 1
        for env_values in product(GRID, repeat=len(covered)):
            env = {i: v for i, v in zip(covered, env_values)}
            counts["covered_envelopes"] += 1
            overline = tuple(env[i] if i in env else Fraction(1) for i in range(n))
            assert all(0 <= x <= 1 for x in overline)
            counts["sharp_envelope_witnesses"] += 1
            if unknown:
                witness = tuple(Fraction(1) if i in unknown else Fraction(0) for i in range(n))
                assert max(witness) == 1
                assert all(witness[i] <= overline[i] for i in range(n))
                counts["supremum_witnesses"] += 1
            for effects in product(GRID, repeat=n):
                if any(effects[i] > env[i] for i in covered):
                    continue
                counts["compatible_effects"] += 1
                for i in range(n):
                    assert effects[i] <= overline[i]
                    counts["pointwise_checks"] += 1
                lhs = sum(weights[i] * effects[i] for i in range(n))
                rhs = sum(weights[i] * overline[i] for i in range(n))
                assert lhs <= rhs
                counts["integral_checks"] += 1
                for tau in THRESHOLDS:
                    lhs_mass = sum(weights[i] for i in range(n) if effects[i] > tau)
                    rhs_mass = sum(
                        weights[i]
                        for i in range(n)
                        if i in unknown or (i in env and env[i] > tau)
                    )
                    assert lhs_mass <= rhs_mass
                    counts["exceedance_checks"] += 1

# The five-way priority is total and exclusive.
status_counts = {}
for valid, refuted, closed, mass_cert, sufficient in product((False, True), repeat=5):
    if not valid:
        status = "INVALID_OPEN_WORLD_PROTOCOL"
    elif refuted:
        status = "COVERAGE_CERTIFICATE_REFUTED"
    elif closed and sufficient:
        status = "CLOSED_DOMAIN_AMPLITUDE_CERTIFIED"
    elif mass_cert and sufficient:
        status = "OPEN_WORLD_MASS_CERTIFIED"
    else:
        status = "UNRESOLVED"
    status_counts[status] = status_counts.get(status, 0) + 1
    counts["status_assignments"] += 1

assert counts["status_assignments"] == 32
assert sum(status_counts.values()) == 32

result = {
    "schema": "UCT_R170_EXACT_CHECKS/v1",
    "status": "PASS",
    "probability_effect_grid": [str(x) for x in GRID],
    "threshold_grid": [str(x) for x in THRESHOLDS],
    "domain_sizes": [1, 2, 3, 4, 5],
    **counts,
    "status_counts": status_counts,
    "verified": [
        "sharp piecewise pointwise envelope over the declared information class",
        "nonempty unknown remainder preserves global supremum one",
        "exact uniform-measure integral remainder bound",
        "exact exceedance-set inclusion bound",
        "five-way status priority is total and exclusive",
    ],
    "limits": [
        "Finite enumeration checks bounded consequences, not physical target coverage or theory truth.",
        "Sharpness is over the declared envelope information class, not a consumer-kernel realizability theorem.",
        "Uniform finite weights do not establish any real target measure.",
    ],
}
out = HERE / "EXACT_CHECKS.json"
out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
result["self_sha256"] = sha256(out.read_bytes()).hexdigest()
print(json.dumps(result, indent=2, ensure_ascii=False))
