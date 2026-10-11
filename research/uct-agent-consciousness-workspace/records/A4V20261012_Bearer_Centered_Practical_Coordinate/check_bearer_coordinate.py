#!/usr/bin/env python3
"""Exact finite check for the A4V one-bit bearer-centred route lemma.

This enumerates deterministic Boolean encoders r=f(x,a) and consumers
y=g(r,a).  It is a finite model check, not a physical or phenomenal test.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "EXACT_RESULTS.json"


def val(bits: tuple[int, ...], first: int, second: int) -> int:
    return bits[2 * first + second]


def bitstring(bits: tuple[int, ...]) -> str:
    return "".join(map(str, bits))


def classify(f: tuple[int, ...], g: tuple[int, ...]) -> dict[str, object]:
    perfect = all(val(g, val(f, x, a), a) == x for x, a in itertools.product((0, 1), repeat=2))
    route_use = all(val(g, 0, a) != val(g, 1, a) for a in (0, 1))
    anchor_to_route = all(val(f, x, 0) != val(f, x, 1) for x in (0, 1))
    anchor_at_consumer = all(val(g, r, 0) != val(g, r, 1) for r in (0, 1))
    joint_compensation = all(
        val(g, 1 - r, 1 - a) == val(g, r, a)
        for r, a in itertools.product((0, 1), repeat=2)
    )
    bearer_centred = route_use and anchor_to_route and anchor_at_consumer and joint_compensation
    return {
        "perfect_output": perfect,
        "actual_route_use_in_declared_consumer": route_use,
        "nontrivial_anchor_to_route_sensitivity": anchor_to_route,
        "nontrivial_anchor_use_at_consumer": anchor_at_consumer,
        "joint_anchor_route_compensation": joint_compensation,
        "bearer_centred_route_view": bearer_centred,
    }


def main() -> None:
    records: list[dict[str, object]] = []
    for f in itertools.product((0, 1), repeat=4):
        for g in itertools.product((0, 1), repeat=4):
            flags = classify(f, g)
            if flags["perfect_output"]:
                records.append({"encoder_f_xa": bitstring(f), "consumer_g_ra": bitstring(g), **flags})

    centred = [r for r in records if r["bearer_centred_route_view"]]
    uncentred = [r for r in records if not r["bearer_centred_route_view"]]

    # Analytic normal form: perfect recovery forces f_a(x)=x xor c_a and
    # g_a(r)=r xor c_a for one bit c_a at each anchor value.
    normal_form = []
    for c0, c1 in itertools.product((0, 1), repeat=2):
        f = tuple(x ^ (c0 if a == 0 else c1) for x, a in itertools.product((0, 1), repeat=2))
        g = tuple(r ^ (c0 if a == 0 else c1) for r, a in itertools.product((0, 1), repeat=2))
        normal_form.append((bitstring(f), bitstring(g)))

    observed = sorted((r["encoder_f_xa"], r["consumer_g_ra"]) for r in records)
    expected = sorted(normal_form)
    checks = {
        "all_256_pairs_enumerated": True,
        "perfect_pairs_equal_normal_form": observed == expected,
        "exactly_four_perfect_pairs": len(records) == 4,
        "exactly_two_bearer_centred_pairs": len(centred) == 2,
        "exactly_two_anchor_insensitive_pairs": len(uncentred) == 2,
        "route_use_alone_shared_by_all_perfect_pairs": all(r["actual_route_use_in_declared_consumer"] for r in records),
        "anchor_flip_separates_classes": all(r["nontrivial_anchor_to_route_sensitivity"] for r in centred)
        and all(not r["nontrivial_anchor_to_route_sensitivity"] for r in uncentred),
        "joint_compensation_separates_classes": all(r["joint_anchor_route_compensation"] for r in centred)
        and all(not r["joint_anchor_route_compensation"] for r in uncentred),
        "equivariance_alone_is_vacuous": classify((0, 0, 0, 0), (0, 0, 0, 0))["joint_anchor_route_compensation"]
        and not classify((0, 0, 0, 0), (0, 0, 0, 0))["actual_route_use_in_declared_consumer"],
    }

    assert all(checks.values())

    result = {
        "schema": "uct-a4v-bearer-centred-coordinate/1.0",
        "scope": "deterministic one-bit encoder r=f(x,a) and consumer y=g(r,a)",
        "interpretation_warning": "Finite organizational classification only; no actual installation, complete K, C1 verification, H_cf value or report calibration.",
        "counts": {
            "encoder_functions": 16,
            "consumer_functions": 16,
            "pairs": 256,
            "perfect_output_pairs": len(records),
            "bearer_centred_perfect_pairs": len(centred),
            "anchor_insensitive_perfect_pairs": len(uncentred),
        },
        "index_order": {"encoder": "(x,a)=(0,0),(0,1),(1,0),(1,1)", "consumer": "(r,a)=(0,0),(0,1),(1,0),(1,1)"},
        "perfect_pairs": records,
        "vacuous_counterexample": {
            "encoder_f_xa": "0000",
            "consumer_g_ra": "0000",
            "point": "Joint-flip invariance holds trivially, but the route is unused and target recovery fails. Nontrivial sensitivities and actual consumption are indispensable."
        },
        "direct_bypass_twin": {
            "law": "y=x with r ignored",
            "point": "All external outputs match both perfect classes; the bypass is excluded only by same-instance evidence of actual route consumption."
        },
        "checks": checks,
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(), "counts": result["counts"], "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
