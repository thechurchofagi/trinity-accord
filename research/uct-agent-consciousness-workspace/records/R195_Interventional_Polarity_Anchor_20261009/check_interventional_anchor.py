#!/usr/bin/env python3
"""Exact finite check for R195's interventional latent-pole symmetry."""

from itertools import product
import json


def output(model, q):
    z0, z1, s1, s2, y00, y01, y10, y11 = model
    z = (z0, z1)[q]
    y = ((y00, y01), (y10, y11))[z][q]
    return (z ^ s1, z ^ s2, y)


def signature(model):
    return tuple(output(model, q) for q in (0, 1))


def complement(model):
    z0, z1, s1, s2, y00, y01, y10, y11 = model
    # y'(z',q) = y(1-z',q)
    return (1-z0, 1-z1, 1-s1, 1-s2, y10, y11, y00, y01)


models = list(product((0, 1), repeat=8))
assert len(models) == 256

for m in models:
    cm = complement(m)
    assert complement(cm) == m
    assert cm != m
    assert signature(cm) == signature(m)

pairs = {tuple(sorted((m, complement(m)))) for m in models}
assert len(pairs) == 128

route_sensitive = [m for m in models if m[0] != m[1]]
route_pairs = {tuple(sorted((m, complement(m)))) for m in route_sensitive}
assert len(route_sensitive) == 128
assert len(route_pairs) == 64

two_marker_reversal = [m for m in models if m[2] != m[3]]
joint = [m for m in route_sensitive if m[2] != m[3]]
joint_pairs = {tuple(sorted((m, complement(m)))) for m in joint}
assert len(two_marker_reversal) == 128
assert len(joint) == 64
assert len(joint_pairs) == 32

marker_convention = [m for m in models if m[2] == 0]
assert len(marker_convention) == 128
assert all(complement(m) not in marker_convention for m in marker_convention)

# Prospective functional anchor: the complete consequence table is fixed to Y=Z.
functional_anchor = [
    m for m in models
    if (m[4], m[5], m[6], m[7]) == (0, 0, 1, 1)
]
assert len(functional_anchor) == 16
assert all(complement(m) not in functional_anchor for m in functional_anchor)

# Its complement Y=1-Z is an equally coherent but oppositely oriented bridge.
opposite_functional_anchor = [
    m for m in models
    if (m[4], m[5], m[6], m[7]) == (1, 1, 0, 0)
]
assert len(opposite_functional_anchor) == 16
assert {complement(m) for m in functional_anchor} == set(opposite_functional_anchor)

result = {
    "research_id": "R195-IPA-20261009",
    "domain": {
        "variables": ["Q", "Z", "M1", "M2", "Y"],
        "model_parameters": ["z(0)", "z(1)", "s1", "s2", "y(0,0)", "y(0,1)", "y(1,0)", "y(1,1)"],
        "observed_under_each_do_Q": ["M1", "M2", "Y"],
        "model_count": len(models)
    },
    "exact_counts": {
        "all_models": len(models),
        "global_complement_pairs": len(pairs),
        "route_sensitive_models_z0_ne_z1": len(route_sensitive),
        "route_sensitive_complement_pairs": len(route_pairs),
        "models_with_reversed_marker_channels_s1_ne_s2": len(two_marker_reversal),
        "route_sensitive_and_reversed_marker_models": len(joint),
        "route_sensitive_and_reversed_marker_pairs": len(joint_pairs),
        "marker_convention_s1_eq_0_models": len(marker_convention),
        "functional_anchor_Y_eq_Z_models": len(functional_anchor),
        "opposite_functional_anchor_Y_eq_not_Z_models": len(opposite_functional_anchor)
    },
    "verified": {
        "complement_is_involution": True,
        "no_complement_fixed_points": True,
        "all_do_Q_observation_tables_preserved": True,
        "route_sensitivity_does_not_break_symmetry": True,
        "reversed_second_marker_does_not_break_symmetry": True,
        "marker_convention_breaks_numeric_symmetry_only": True,
        "functional_anchor_breaks_symmetry_by_added_Y_to_Z_orientation": True,
        "functional_anchor_complements_to_opposite_bridge": True
    },
    "scope": "Finite deterministic binary SCM. Exact enumeration is not a human/AI experience experiment and does not validate C1 or B_fam."
}

print(json.dumps(result, indent=2, sort_keys=True))
