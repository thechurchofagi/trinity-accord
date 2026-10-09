#!/usr/bin/env python3
"""Exact rational checks for the R197 fallible-endpoint result.

The script checks a finite grid of binary endpoint channels with fractions.  It
does not simulate experience, people, or artificial systems.  It verifies only
the declared sign-identification algebra and explicit transport countermodels.
"""

from fractions import Fraction
import json
from pathlib import Path


def structural_contrast(s: int, p1: Fraction, p0: Fraction) -> Fraction:
    """P(E=1|A=1)-P(E=1|A=0) when F=A xor s."""
    if s == 0:
        return p1 - p0
    return p0 - p1


grid = [Fraction(i, 8) for i in range(9)]
directed = [(p1, p0) for p1 in grid for p0 in grid if p1 > p0]
undirected = [(p1, p0) for p1 in grid for p0 in grid]

checks = []

# Exact sign theorem on every positively directed finite channel.
for p1, p0 in directed:
    assert structural_contrast(0, p1, p0) > 0
    assert structural_contrast(1, p1, p0) < 0
checks.append({
    "id": "R197-T1-GRID",
    "pass": True,
    "cases": 2 * len(directed),
    "statement": "Every p1>p0 channel has opposite nonzero structural-contrast signs under the two complement orientations."
})

# If direction is not assumed, both orientations fit the same observed channel
# after swapping the unobserved endpoint semantics.
ambiguous = 0
for p1, p0 in undirected:
    d = structural_contrast(0, p1, p0)
    swapped_d = structural_contrast(1, p0, p1)
    assert d == swapped_d
    ambiguous += 1
checks.append({
    "id": "R197-T2-LABEL-SWAP",
    "pass": True,
    "cases": ambiguous,
    "statement": "Without a signed reliability premise, swapping endpoint semantics and channel rates preserves every observed structural contrast."
})

# Marginal equality across domains does not establish class-conditional
# invariance: both domains have prevalence 1/2 and marker marginal 1/2, while
# the marker direction reverses.
pi = Fraction(1, 2)
cal = {"p1": Fraction(4, 5), "p0": Fraction(1, 5)}
target = {"p1": Fraction(1, 5), "p0": Fraction(4, 5)}
cal_marginal = pi * cal["p1"] + (1 - pi) * cal["p0"]
target_marginal = pi * target["p1"] + (1 - pi) * target["p0"]
assert cal_marginal == target_marginal == Fraction(1, 2)
assert cal["p1"] - cal["p0"] == Fraction(3, 5)
assert target["p1"] - target["p0"] == Fraction(-3, 5)
checks.append({
    "id": "R197-T3-MARGINAL-TRANSPORT-FAILURE",
    "pass": True,
    "cases": 1,
    "statement": "Equal marker marginals can coexist with a complete reversal of the endpoint-conditioned marker direction."
})

# Full class-conditional invariance preserves the sign for every directed grid
# channel.  This is a conditional transport result, not evidence that the
# invariance premise holds in any actual system.
for p1, p0 in directed:
    cal_sign = structural_contrast(0, p1, p0)
    target_sign = structural_contrast(0, p1, p0)
    assert cal_sign == target_sign > 0
checks.append({
    "id": "R197-T4-CONDITIONAL-TRANSPORT",
    "pass": True,
    "cases": len(directed),
    "statement": "Exact class-conditional endpoint-channel invariance preserves the directed contrast."
})

# A verbal and a nonverbal endpoint with the same confusion matrix are
# algebraically indistinguishable.  Modality alone supplies no reliability.
verbal = (Fraction(3, 4), Fraction(1, 4))
nonverbal = (Fraction(3, 4), Fraction(1, 4))
assert structural_contrast(0, *verbal) == structural_contrast(0, *nonverbal)
checks.append({
    "id": "R197-T5-MODALITY-NEUTRALITY",
    "pass": True,
    "cases": 2,
    "statement": "At fixed signed channel behavior, verbal versus nonverbal modality does not alter the orientation algebra."
})

# Copy/switch witness: copy the observable marginal and numeric marker code but
# reverse which latent endpoint state generates the marker.
copy_original = (Fraction(7, 8), Fraction(1, 8))
copy_switched = (Fraction(1, 8), Fraction(7, 8))
assert pi * sum(copy_original) == pi * sum(copy_switched) == Fraction(1, 2)
assert structural_contrast(0, *copy_original) == Fraction(3, 4)
assert structural_contrast(0, *copy_switched) == Fraction(-3, 4)
checks.append({
    "id": "R197-T6-COPY-SWITCH",
    "pass": True,
    "cases": 1,
    "statement": "Copied marker prevalence and code do not preserve the endpoint-conditioned direction after a generator switch."
})

result = {
    "schema": "uct-r197-fallible-endpoint-check/1.0",
    "result_id": "R197-FEO-RESULT-v0.1.0",
    "status": "PASS_DECLARED_FINITE_ALGEBRA_ONLY",
    "grid_denominator": 8,
    "directed_channels": len(directed),
    "all_channels": len(undirected),
    "total_checked_instances": sum(item["cases"] for item in checks),
    "checks": checks,
    "transport_countermodel": {
        "prevalence": "1/2",
        "calibration_rates": {"p1": "4/5", "p0": "1/5", "marginal": "1/2", "contrast": "3/5"},
        "target_rates": {"p1": "1/5", "p0": "4/5", "marginal": "1/2", "contrast": "-3/5"}
    },
    "limitations": [
        "No actual token, episode, phenomenal target, report reliability, marker reliability or transport invariance is established.",
        "The checker does not validate C1, familiar mineness, consciousness, agency, ownership or current route use.",
        "The sign argument and label-swap symmetry use standard probability and identifiability mathematics."
    ]
}

out = Path(__file__).with_name("EXACT_RESULTS.json")
out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
