#!/usr/bin/env python3
"""Enumerate the A5G two-channel latent-source equivalence class."""

import json
from itertools import product
from pathlib import Path


def signal(kind, parameter, intervention):
    if kind == "tracking":
        return intervention ^ parameter
    if kind == "invariant":
        return parameter
    raise ValueError(kind)


def channel(source, orientation, intervention, h_value):
    value = intervention if source == "O" else h_value
    return value ^ orientation


def main():
    compatible = []
    for kind in ("tracking", "invariant"):
        for parameter in (0, 1):
            for source_1, source_2, orientation_1, orientation_2 in product(("O", "H"), ("O", "H"), (0, 1), (0, 1)):
                trace = []
                for intervention in (0, 1):
                    h = signal(kind, parameter, intervention)
                    trace.append((
                        channel(source_1, orientation_1, intervention, h),
                        channel(source_2, orientation_2, intervention, h),
                    ))
                if trace == [(0, 0), (1, 1)]:
                    compatible.append({
                        "target_kind": kind,
                        "target_parameter": parameter,
                        "source_pattern": source_1 + source_2,
                        "orientations": [orientation_1, orientation_2],
                    })

    counts = {
        "total_compatible_models": len(compatible),
        "tracking_target_models": sum(m["target_kind"] == "tracking" for m in compatible),
        "invariant_target_models": sum(m["target_kind"] == "invariant" for m in compatible),
        "target_equals_organization_models": sum(m["target_kind"] == "tracking" and m["target_parameter"] == 0 for m in compatible),
        "target_complements_organization_models": sum(m["target_kind"] == "tracking" and m["target_parameter"] == 1 for m in compatible),
        "source_pattern_counts": {p: sum(m["source_pattern"] == p for m in compatible) for p in ("OO", "OH", "HO", "HH")},
    }
    assert counts == {
        "total_compatible_models": 10,
        "tracking_target_models": 8,
        "invariant_target_models": 2,
        "target_equals_organization_models": 4,
        "target_complements_organization_models": 4,
        "source_pattern_counts": {"OO": 4, "OH": 2, "HO": 2, "HH": 2},
    }

    h_sensitive_sign_free = [m for m in compatible if m["source_pattern"][0] == "H"]
    h_sensitive_sign_fixed = [m for m in h_sensitive_sign_free if m["orientations"][0] == 0]
    assert len(h_sensitive_sign_free) == 4
    assert {m["target_parameter"] for m in h_sensitive_sign_free} == {0, 1}
    assert len(h_sensitive_sign_fixed) == 2
    assert all(m["target_kind"] == "tracking" and m["target_parameter"] == 0 for m in h_sensitive_sign_fixed)

    result = {
        "schema": "a5g-two-channel-equivalence/1",
        "observed_trace": {"I=0": [0, 0], "I=1": [1, 1]},
        "model_class": "Each decoded channel reads O or H with an unknown binary orientation; H either tracks O with either pole or is invariant.",
        "counts": counts,
        "compatible_models": compatible,
        "conditional_independence_note": "All channels are deterministic given their selected source; two responses can therefore be conditionally independent given one shared organizational cause without being semantically or measurand-independent.",
        "h_sensitive_first_channel_sign_free": {
            "compatible_models": len(h_sensitive_sign_free),
            "remaining_target_poles": sorted({m["target_parameter"] for m in h_sensitive_sign_free}),
            "identified": False,
        },
        "h_sensitive_first_channel_sign_fixed_positive": {
            "compatible_models": len(h_sensitive_sign_fixed),
            "remaining_target_poles": sorted({m["target_parameter"] for m in h_sensitive_sign_fixed}),
            "identified_within_declared_model": True,
        },
        "conclusion": "Two convergent task channels do not identify H_tip. Independent H-sensitivity removes invariant-H alternatives, and a fixed target orientation is additionally required to identify the positive H_tip pole within this model.",
    }
    out = Path(__file__).with_name("EXACT_RESULTS.json")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()

