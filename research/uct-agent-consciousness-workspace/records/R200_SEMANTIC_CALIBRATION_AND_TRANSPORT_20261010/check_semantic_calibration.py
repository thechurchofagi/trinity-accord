#!/usr/bin/env python3
"""Exact finite checks for R200 semantic calibration and transport.

The checker does not identify phenomenal familiarity.  It verifies four small
claims used by the research note: latent-label symmetry survives arbitrary
multi-proxy observation, an independently signed fallible channel breaks that
symmetry inside its calibration domain, equal marker marginals do not imply
class-conditional transport, and a formation-by-use interaction can be
generated with the target held fixed.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from pathlib import Path


def marginal(pi: Fraction, q0: tuple[int, ...], q1: tuple[int, ...]) -> tuple[Fraction, ...]:
    """Observed law for a deterministic proxy-vector conditional on H."""
    states = list(itertools.product((0, 1), repeat=4))
    return tuple((1 - pi) * (s == q0) + pi * (s == q1) for s in states)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    proxy_vectors = list(itertools.product((0, 1), repeat=4))
    prevalences = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))
    latent_models = 0
    complement_mismatches = 0
    for pi, q0, q1 in itertools.product(prevalences, proxy_vectors, proxy_vectors):
        latent_models += 1
        original = marginal(pi, q0, q1)
        complemented = marginal(1 - pi, q1, q0)
        complement_mismatches += original != complemented

    # Four-trial conditional frequencies.  A signed channel is positively
    # oriented precisely when its success count is larger under H=1.
    signed_pairs = [(n1, n0) for n1 in range(5) for n0 in range(5) if n1 > n0]
    flipped_pairs_preserving_sign = [(n1, n0) for n1, n0 in signed_pairs if n0 > n1]

    # Exhaust every deterministic Boolean response table g(F,U) and compute
    # the ordinary difference-in-differences interaction.
    did_counts: dict[str, int] = {}
    positive_examples = []
    for table in itertools.product((0, 1), repeat=4):
        g00, g01, g10, g11 = table
        did = g11 - g10 - g01 + g00
        did_counts[str(did)] = did_counts.get(str(did), 0) + 1
        if did > 0:
            positive_examples.append({"table_F0U0_F0U1_F1U0_F1U1": table, "did": did})

    # Counterexample: both domains have H prevalence 1/2 and marker marginal
    # 1/2, but the marker's direction reverses.
    cal = {"p_M1_given_H1": Fraction(3, 4), "p_M1_given_H0": Fraction(1, 4)}
    tgt = {"p_M1_given_H1": Fraction(1, 4), "p_M1_given_H0": Fraction(3, 4)}
    cal_marginal = (cal["p_M1_given_H1"] + cal["p_M1_given_H0"]) / 2
    tgt_marginal = (tgt["p_M1_given_H1"] + tgt["p_M1_given_H0"]) / 2

    # Shared-confound witness: two objective proxies agree perfectly because
    # both copy success S, while H is fixed at zero in every cell.
    shared_confound_rows = []
    for f, u in itertools.product((0, 1), repeat=2):
        s = f & u
        shared_confound_rows.append({"F": f, "U": u, "H": 0, "M1": s, "M2": s})

    result = {
        "schema": "uct-r200-semantic-calibration-check/1",
        "multi_proxy_label_symmetry": {
            "observed_proxy_bits": 4,
            "proxy_vectors": len(proxy_vectors),
            "prevalences": [str(x) for x in prevalences],
            "latent_models_checked": latent_models,
            "complement_mismatches": complement_mismatches,
            "scope": "Every enumerated deterministic four-proxy latent model has an observationally identical H-complement model.",
        },
        "signed_channel_orientation": {
            "trials_per_class": 4,
            "strictly_positive_channel_pairs": len(signed_pairs),
            "complemented_pairs_still_satisfying_same_positive_sign": len(flipped_pairs_preserving_sign),
            "scope": "A predeclared independent positive-direction premise excludes the H-complement inside the calibration domain; the premise is not proved by this enumeration.",
        },
        "marginal_transport_counterexample": {
            "calibration": {k: str(v) for k, v in cal.items()},
            "target": {k: str(v) for k, v in tgt.items()},
            "calibration_marker_marginal": str(cal_marginal),
            "target_marker_marginal": str(tgt_marginal),
            "same_marginal": cal_marginal == tgt_marginal,
            "signed_relation_reverses": cal["p_M1_given_H1"] > cal["p_M1_given_H0"] and tgt["p_M1_given_H1"] < tgt["p_M1_given_H0"],
        },
        "formation_by_use_interaction": {
            "boolean_response_tables_checked": 16,
            "did_counts": did_counts,
            "positive_interaction_tables": len(positive_examples),
            "positive_examples": positive_examples,
            "shared_confound_witness": shared_confound_rows,
            "scope": "A positive formation-by-use interaction can occur with H fixed, including when two agreeing proxies merely copy task success.",
        },
        "all_exact_checks_pass": complement_mismatches == 0
        and len(flipped_pairs_preserving_sign) == 0
        and cal_marginal == tgt_marginal
        and len(positive_examples) > 0,
        "not_proved": [
            "that any report or objective proxy actually measures phenomenal retentive familiarity H",
            "that class-conditional invariance holds in infants, animals, prosthesis users, artificial agents, or any other target domain",
            "that route telemetry establishes actual same-episode consumer use",
            "that C1 is empirically true",
        ],
    }
    a.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "latent_models": latent_models,
        "complement_mismatches": complement_mismatches,
        "signed_pairs": len(signed_pairs),
        "positive_did_tables": len(positive_examples),
        "all_exact_checks_pass": result["all_exact_checks_pass"],
    }, sort_keys=True))
    if not result["all_exact_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
