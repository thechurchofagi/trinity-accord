#!/usr/bin/env python3
"""Exact finite check for the A5L grounded-role-reversal model."""

from itertools import product
import json


CELLS = tuple(product((0, 1), repeat=3))  # P, Q, C
H_LAWS = ("P", "notP", "C", "notC", "X", "notX", "zero", "one")
E_SOURCES = ("X", "H")


def value(law, p, q, c):
    x = p ^ q
    return {
        "P": p,
        "notP": 1 - p,
        "C": c,
        "notC": 1 - c,
        "X": x,
        "notX": 1 - x,
        "zero": 0,
        "one": 1,
    }[law]


def endpoint(model, p, q, c):
    h = value(model["H"], p, q, c)
    x = p ^ q
    base = x if model["E_source"] == "X" else h
    return base ^ model["orientation"]


models = [
    {"H": h, "E_source": source, "orientation": orient}
    for h, source, orient in product(H_LAWS, E_SOURCES, (0, 1))
]


def matches_role_signature(model):
    return all(endpoint(model, p, q, c) == (p ^ q) for p, q, c in CELLS)


def summarize(rows):
    return {
        "models": len(rows),
        "target_laws": sorted({m["H"] for m in rows}),
        "endpoint_sources": sorted({m["E_source"] for m in rows}),
        "orientations": sorted({m["orientation"] for m in rows}),
    }


signature = [m for m in models if matches_role_signature(m)]
shape = [m for m in signature if m["H"] in {"X", "notX"}]
target_sensitive = [m for m in signature if m["E_source"] == "H"]
target_sensitive_common_orientation = [
    m for m in target_sensitive if m["orientation"] == 0
]

direct_twins = [m for m in signature if m["E_source"] == "X"]
assert len(models) == 32
assert len(signature) == 10
assert len(direct_twins) == 8
assert {m["H"] for m in signature} == set(H_LAWS)
assert len(shape) == 4
assert len(target_sensitive) == 2
assert {m["H"] for m in target_sensitive} == {"X", "notX"}
assert len(target_sensitive_common_orientation) == 1
assert target_sensitive_common_orientation[0]["H"] == "X"
assert all(
    value("X", p, 0, c) != value("X", p, 1, c)
    for p, c in product((0, 1), repeat=2)
)

result = {
    "schema": "uct-a5l-role-reversal/1.0",
    "domain": {
        "cells": [dict(P=p, Q=q, C=c, X=p ^ q, R=p, A=p, Z=p) for p, q, c in CELLS],
        "H_laws": list(H_LAWS),
        "endpoint_sources": list(E_SOURCES),
        "orientations": [0, 1],
        "canonical_models": len(models),
    },
    "counts": {
        "observed_E_equals_X": summarize(signature),
        "semantic_shape_H_in_X_complement": summarize(shape),
        "target_sensitive_endpoint_no_direct_X": summarize(target_sensitive),
        "target_sensitive_plus_common_orientation": summarize(
            target_sensitive_common_orientation
        ),
    },
    "witnesses": {
        "aligned_target": {"H": "X", "E_source": "H", "orientation": 0},
        "H_free_direct_X_twin": {"H": "P", "E_source": "X", "orientation": 0},
        "complement_target": {"H": "notX", "E_source": "H", "orientation": 1},
        "constant_H_direct_X_twin": {"H": "zero", "E_source": "X", "orientation": 0},
    },
    "checks": {
        "Q_reverses_grounded_X_at_fixed_P_C": True,
        "R_and_direct_P_paths_remain_fixed": True,
        "role_signature_retains_all_H_laws": len({m["H"] for m in signature}) == 8,
        "direct_X_path_reproduces_signature_for_every_H_law": len(direct_twins) == 8,
        "target_sensitivity_reduces_to_global_complement": {m["H"] for m in target_sensitive} == {"X", "notX"},
        "common_orientation_selects_H_equals_X": target_sensitive_common_orientation == [{"H": "X", "E_source": "H", "orientation": 0}],
    },
}

print(json.dumps(result, indent=2, sort_keys=True))
