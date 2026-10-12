#!/usr/bin/env python3
"""Exact finite checks for A5D's constitutive/semantic/evidential separation."""

import json
from fractions import Fraction
from pathlib import Path


def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0


def main():
    # R is an independently grounded directed actual relation. C1 transport fixes X=R.
    # s_b complements the proposed X->H interpretation; s_e complements H->E evidence.
    rows = []
    p_hi, p_lo = Fraction(4, 5), Fraction(1, 5)
    for s_b in (0, 1):
        for s_e in (0, 1):
            # H = X xor s_b; E's high-probability class = H xor s_e = 1.
            probs = {}
            for r in (0, 1):
                x = r
                h = x ^ s_b
                probs[r] = p_hi if (h ^ s_e) == 1 else p_lo
            contrast = probs[1] - probs[0]
            rows.append({
                "semantic_complement_s_b": s_b,
                "evidence_complement_s_e": s_e,
                "P_E1_given_R0": str(probs[0]),
                "P_E1_given_R1": str(probs[1]),
                "observable_contrast": str(contrast),
                "contrast_sign": sign(contrast),
            })

    positive = [r for r in rows if r["contrast_sign"] == 1]
    negative = [r for r in rows if r["contrast_sign"] == -1]
    assert {(r["semantic_complement_s_b"], r["evidence_complement_s_e"]) for r in positive} == {(0, 0), (1, 1)}
    assert {(r["semantic_complement_s_b"], r["evidence_complement_s_e"]) for r in negative} == {(0, 1), (1, 0)}

    # If the actual relation is not grounded, a third complement restores 8 conventions.
    ungrounded = []
    for s_x in (0, 1):
        for s_b in (0, 1):
            for s_e in (0, 1):
                observed_sign = 1 if (s_x ^ s_b ^ s_e) == 0 else -1
                ungrounded.append((s_x, s_b, s_e, observed_sign))
    assert len(ungrounded) == 8
    assert sum(r[3] == 1 for r in ungrounded) == 4

    # A directed typed relation is not complemented by a label change. Reversing its ports
    # produces a different relation unless reversal was explicitly admitted as a symmetry.
    directed_edges = {("bearer_state", "target")}
    reversed_edges = {(b, a) for a, b in directed_edges}
    assert directed_edges != reversed_edges

    # Copy/switch refuter: copied endpoint code is fixed while actual current relation changes.
    copy_switch = [
        {"world": "source", "R": 1, "copied_E": 1},
        {"world": "switched_route", "R": 0, "copied_E": 1},
    ]
    assert len({w["copied_E"] for w in copy_switch}) == 1
    assert len({w["R"] for w in copy_switch}) == 2

    result = {
        "schema": "a5d-orientation-layers/1",
        "constitutive_orientation": {
            "grounded_directed_relation_orientations": 1,
            "reason": "The typed directed relation symbol and port order are preserved by the declared C1 signature; external code complementation is not an automorphism.",
            "conditional_on": ["actual relation grounding", "complete relevant signature", "C1", "no admitted port-reversal symmetry"],
        },
        "semantic_and_evidential_orientations": rows,
        "positive_observable_contrast_compatible_pairs": [[0, 0], [1, 1]],
        "negative_observable_contrast_compatible_pairs": [[0, 1], [1, 0]],
        "ungrounded_total_conventions": 8,
        "ungrounded_positive_conventions": 4,
        "grounding_reduction": "8 total layer conventions to 4, while H semantics and evidence direction remain unresolved",
        "copy_switch_refuter": copy_switch,
        "scope": "Exact Boolean/rational model only; not physical installation, C1 evidence, H_pc identity, endpoint calibration, or a new mathematical theorem.",
        "status": "PASS",
    }
    out = Path(__file__).with_name("EXACT_RESULTS.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "rows": len(rows), "positive_pairs": 2, "negative_pairs": 2}, sort_keys=True))


if __name__ == "__main__":
    main()
