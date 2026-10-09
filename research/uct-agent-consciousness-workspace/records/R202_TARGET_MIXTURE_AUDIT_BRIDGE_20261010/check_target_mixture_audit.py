#!/usr/bin/env python3
"""Exact finite checks for R202 target-mixture and audit inversion claims."""

from fractions import Fraction
import json
from pathlib import Path


def f(x: int, d: int = 8) -> Fraction:
    return Fraction(x, d)


def main() -> None:
    # Unlabelled target marginals admit both marker orientations.
    marginal_witnesses = []
    for k in range(1, 8):
        m = f(k)
        d = min(m, 1 - m, Fraction(1, 8))
        if d <= 0:
            continue
        pi = Fraction(1, 2)
        positive = {"pi": pi, "q0": m - d, "q1": m + d}
        negative = {"pi": pi, "q0": m + d, "q1": m - d}
        for model in (positive, negative):
            mix = (1 - model["pi"]) * model["q0"] + model["pi"] * model["q1"]
            assert mix == m
        assert positive["q1"] > positive["q0"]
        assert negative["q1"] < negative["q0"]
        marginal_witnesses.append((m, positive, negative))

    # Exact inversion under nondifferential endpoint error J ⟂ M | H.
    checked = 0
    recovered = 0
    for pi_n in range(1, 8):
        pi = f(pi_n)
        for q0_n in range(9):
            q0 = f(q0_n)
            for q1_n in range(9):
                q1 = f(q1_n)
                for c_n in range(0, 8):
                    c = f(c_n)
                    for a_n in range(c_n + 1, 9):
                        a = f(a_n)
                        m = (1 - pi) * q0 + pi * q1
                        j = (1 - pi) * c + pi * a
                        r = (1 - pi) * c * q0 + pi * a * q1
                        if not (c < j < a):
                            continue
                        pi_hat = (j - c) / (a - c)
                        q1_hat = (r - c * m) / (j - c)
                        q0_hat = (a * m - r) / (a - j)
                        checked += 1
                        assert (pi_hat, q0_hat, q1_hat) == (pi, q0, q1)
                        recovered += 1

    # Singular endpoint: a=c erases H from J and leaves complement models tied.
    singular = {
        "pi": Fraction(1, 2),
        "a": Fraction(1, 2),
        "c": Fraction(1, 2),
        "model_positive": (Fraction(1, 4), Fraction(3, 4)),
        "model_negative": (Fraction(3, 4), Fraction(1, 4)),
    }
    observed = []
    for q0, q1 in (singular["model_positive"], singular["model_negative"]):
        pi, a, c = singular["pi"], singular["a"], singular["c"]
        m = (1 - pi) * q0 + pi * q1
        j = (1 - pi) * c + pi * a
        r = (1 - pi) * c * q0 + pi * a * q1
        observed.append((m, j, r))
    assert observed[0] == observed[1]

    # Selective audit witness: audit inclusion depending on H can hide population prevalence.
    # Populations have different pi but selection weights make audit prevalence 1/2.
    selective = []
    for pi, s0, s1 in [
        (Fraction(1, 4), Fraction(1, 3), Fraction(1, 1)),
        (Fraction(3, 4), Fraction(1, 1), Fraction(1, 3)),
    ]:
        audit_pi = pi * s1 / ((1 - pi) * s0 + pi * s1)
        assert audit_pi == Fraction(1, 2)
        selective.append({"population_pi": pi, "s0": s0, "s1": s1, "audit_pi": audit_pi})

    def enc(value):
        if isinstance(value, Fraction):
            return f"{value.numerator}/{value.denominator}"
        raise TypeError

    result = {
        "schema": "uct-r202-exact-results/1",
        "unlabelled_marginal_grid_points": len(marginal_witnesses),
        "opposite_orientation_pairs_found": len(marginal_witnesses),
        "audit_inversion_instances_checked": checked,
        "audit_inversion_exact_recoveries": recovered,
        "audit_inversion_violations": checked - recovered,
        "singular_endpoint_observational_tie": observed[0] == observed[1],
        "selective_audit_same_audit_prevalence_different_population_prevalence": True,
        "canonical_equal_marginal_witness": {
            "source": {"q0": "1/4", "q1": "3/4"},
            "target_same": {"pi": "1/2", "q0": "1/4", "q1": "3/4", "m": "1/2"},
            "target_reversed": {"pi": "1/2", "q0": "3/4", "q1": "1/4", "m": "1/2"},
        },
        "status": "PASS",
        "scope": "Finite rational-grid implementation check plus exact witnesses; symbolic arguments carry the general claims.",
    }
    out = Path(__file__).with_name("EXACT_RESULTS.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
