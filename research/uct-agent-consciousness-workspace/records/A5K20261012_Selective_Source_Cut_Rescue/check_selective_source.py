#!/usr/bin/env python3
"""Exact finite audit for A5K selective-source cut/rescue identification."""

from itertools import product
import json


CELLS = tuple(product((0, 1), repeat=2))
H_LAWS = {
    "P": lambda p, c: p,
    "notP": lambda p, c: 1 - p,
    "C": lambda p, c: c,
    "notC": lambda p, c: 1 - c,
    "zero": lambda p, c: 0,
    "one": lambda p, c: 1,
}


def oriented(value, orientation):
    return value ^ orientation


def outputs(model, p, c):
    # R is an independently specified physical candidate route carrying P.
    # H is deliberately not used to generate the physical readout.
    r = p
    selected = r if model["source"] == "R" else p
    baseline = oriented(selected, model["orientation"])

    if model["cut_readout"]:
        cut = None
    elif model["source"] == "R" and model["cut_route"]:
        cut = None
    else:
        cut = baseline

    gate_open = (not model["cut_readout"]) or model["rescue_readout"]
    route_open = (not model["cut_route"]) or model["rescue_route"]
    if not gate_open:
        rescue = None
    elif model["source"] == "R" and not route_open:
        rescue = None
    else:
        rescue = baseline
    return baseline, cut, rescue


MODELS = []
for h_name, source, orientation, cut_route, cut_readout, rescue_route, rescue_readout in product(
    H_LAWS, ("R", "P"), (0, 1), (False, True), (False, True), (False, True), (False, True)
):
    # Canonicalize absent mechanisms: a rescue flag is meaningful only after its cut.
    if rescue_route and not cut_route:
        continue
    if rescue_readout and not cut_readout:
        continue
    model = {
        "H": h_name,
        "source": source,
        "orientation": orientation,
        "cut_route": cut_route,
        "cut_readout": cut_readout,
        "rescue_route": rescue_route,
        "rescue_readout": rescue_readout,
    }
    # Observed signature: Z=P at baseline, unavailable after cut, restored to P;
    # the separate reference channel A=P remains available in every phase.
    if all(outputs(model, p, c) == (p, None, p) for p, c in CELLS):
        MODELS.append(model)


def subset(**requirements):
    return [m for m in MODELS if all(m[k] == v for k, v in requirements.items())]


def summary(models):
    return {
        "models": len(models),
        "target_laws": sorted({m["H"] for m in models}),
        "source_classes": sorted({m["source"] for m in models}),
    }


route_effective = [m for m in MODELS if m["cut_route"] and m["rescue_route"]]
no_direct_readout = [m for m in MODELS if not m["cut_readout"]]
physical_source_identified = [m for m in no_direct_readout if m["source"] == "R"]
semantic_shape = [m for m in physical_source_identified if m["H"] in ("P", "notP")]
semantic_shape_co = [m for m in semantic_shape if m["H"] == "P"]

route_witness = next(
    m for m in MODELS
    if m["H"] == "P" and m["source"] == "R" and m["orientation"] == 0
    and m["cut_route"] and not m["cut_readout"] and m["rescue_route"]
)
direct_gate_witness = next(
    m for m in MODELS
    if m["H"] == "zero" and m["source"] == "P" and m["orientation"] == 0
    and not m["cut_route"] and m["cut_readout"] and m["rescue_readout"]
)
complement_witness = next(
    m for m in semantic_shape
    if m["H"] == "notP" and m["source"] == "R"
)

result = {
    "schema": "uct-a5k-selective-source/1.0",
    "model_status": "finite_abstract_declared_model_not_physical_or_phenomenal_installation",
    "observation": {
        "cells": [{"P": p, "C": c} for p, c in CELLS],
        "Z": {"baseline": "P", "cut": "unavailable", "rescue": "P"},
        "A": "P remains available at baseline, cut, and rescue",
    },
    "model_space": {
        "H_laws": list(H_LAWS),
        "Z_sources": ["R", "P"],
        "orientation": [0, 1],
        "mechanism_states": ["absent", "cut_not_rescued", "cut_and_rescued"],
        "total_canonical_models_before_observation": len(H_LAWS) * 2 * 2 * 3 * 3,
    },
    "counts": {
        "signature_only": summary(MODELS),
        "candidate_route_cut_and_rescue_effective_RE": summary(route_effective),
        "no_direct_readout_cut_NDR": summary(no_direct_readout),
        "NDR_plus_semantic_shape_SB": summary(semantic_shape),
        "NDR_plus_SB_plus_common_orientation_CO": summary(semantic_shape_co),
    },
    "witnesses": {
        "candidate_R_source_cut": route_witness,
        "direct_readout_gate_twin": direct_gate_witness,
        "opposite_phenomenal_pole_after_physical_source_identification": complement_witness,
    },
    "checks": {
        "signature_has_R_source_model": any(m["source"] == "R" for m in MODELS),
        "signature_has_direct_P_gate_model": any(m["source"] == "P" for m in MODELS),
        "RE_alone_does_not_remove_direct_gate": any(m["source"] == "P" for m in route_effective),
        "NDR_signature_forces_R_source_in_declared_family": {m["source"] for m in no_direct_readout} == {"R"},
        "physical_R_source_leaves_all_H_laws": {m["H"] for m in physical_source_identified} == set(H_LAWS),
        "SB_reduces_to_global_complement": {m["H"] for m in semantic_shape} == {"P", "notP"},
        "SB_and_CO_identify_H_equals_P": {m["H"] for m in semantic_shape_co} == {"P"},
    },
    "interpretation_limit": (
        "Cut/rescue plus a preserved direct-P reference can identify dependence on a declared physical route R "
        "only after direct readout interventions and alternate failure routes are excluded. It leaves every H "
        "law compatible. Relating R to H requires an additional independently warranted semantic bridge; "
        "selecting H=P over H=notP additionally requires common orientation."
    ),
}

print(json.dumps(result, indent=2, sort_keys=True))
assert all(result["checks"].values()), result["checks"]
