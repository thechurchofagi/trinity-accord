#!/usr/bin/env python3
"""Exact finite audit for veridical-to-illusion calibration transport.

V is a veridical calibration context.  There the experienced target H_V and
the contextual cue C_V are both equal to the actual contact P, so ordinary
calibration cannot distinguish an H-reading channel from a cue-reading one.
I is an illusion context with sequence cue X.  H_I may track X with either
orientation or remain invariant.  A channel Z can select H or the contextual
cue separately in each context and can also change orientation.

The observed transfer pattern is Z_V=P and Z_I=X.  The audit counts all exact
models that reproduce it, then adds three independently stated restrictions:

  D: source-discordant calibration fixes the V selector to H;
  S: the selector is transported unchanged from V to I;
  O: the channel orientation is transported unchanged from V to I.

This is an identification calculation, not a consciousness criterion.
"""

from collections import Counter
import json


def target_value(kind, parameter, x):
    return x ^ parameter if kind == "tracking" else parameter


def channel_value(source, orientation, h, cue):
    return (h if source == "H" else cue) ^ orientation


models = []
for target_kind in ("tracking", "invariant"):
    for target_parameter in (0, 1):
        for selector_v in ("H", "C"):
            for selector_i in ("H", "C"):
                for orientation_v in (0, 1):
                    for orientation_i in (0, 1):
                        v_ok = all(
                            channel_value(selector_v, orientation_v, p, p) == p
                            for p in (0, 1)
                        )
                        i_ok = all(
                            channel_value(
                                selector_i,
                                orientation_i,
                                target_value(target_kind, target_parameter, x),
                                x,
                            ) == x
                            for x in (0, 1)
                        )
                        if v_ok and i_ok:
                            models.append({
                                "target_kind": target_kind,
                                "target_parameter": target_parameter,
                                "selector_v": selector_v,
                                "selector_i": selector_i,
                                "orientation_v": orientation_v,
                                "orientation_i": orientation_i,
                            })


def restrict(*, discordant=False, selector=False, orientation=False):
    selected = models
    if discordant:
        # In a factorial V calibration with H=P while C varies independently,
        # exact Z=P forces the calibrated source to H.
        selected = [m for m in selected if m["selector_v"] == "H"]
    if selector:
        selected = [m for m in selected if m["selector_v"] == m["selector_i"]]
    if orientation:
        selected = [m for m in selected if m["orientation_v"] == m["orientation_i"]]
    return selected


def compact_count(selected):
    return {
        "count": len(selected),
        "by_target_kind": dict(sorted(Counter(m["target_kind"] for m in selected).items())),
        "target_hypotheses": sorted({
            f'{m["target_kind"]}:{m["target_parameter"]}' for m in selected
        }),
    }


restrictions = {
    "none": compact_count(restrict()),
    "D_source_discordant_calibration": compact_count(restrict(discordant=True)),
    "S_selector_transport": compact_count(restrict(selector=True)),
    "O_orientation_transport": compact_count(restrict(orientation=True)),
    "S_and_O": compact_count(restrict(selector=True, orientation=True)),
    "D_and_S": compact_count(restrict(discordant=True, selector=True)),
    "D_and_O": compact_count(restrict(discordant=True, orientation=True)),
    "D_and_S_and_O": compact_count(restrict(
        discordant=True, selector=True, orientation=True
    )),
}


def witness(selected, predicate):
    return next(m for m in selected if predicate(m))


result = {
    "schema": "a5i-context-transport/1",
    "observations": {
        "veridical": "for P in {0,1}, H_V=C_V=P and Z_V=P",
        "illusion": "for X in {0,1}, C_I=X and Z_I=X",
    },
    "restriction_legend": {
        "D": "A source-discordant veridical calibration independently forces selector_v=H.",
        "S": "The selected source class is identical across calibration and illusion contexts.",
        "O": "The channel orientation is identical across calibration and illusion contexts.",
    },
    "counts": restrictions,
    "all_of_audit": {
        "all_three": restrictions["D_and_S_and_O"],
        "drop_D_keep_S_O": restrictions["S_and_O"],
        "drop_S_keep_D_O": restrictions["D_and_O"],
        "drop_O_keep_D_S": restrictions["D_and_S"],
    },
    "countermodel_witnesses": {
        "ordinary_calibration_context_switch": witness(
            models,
            lambda m: m["selector_v"] == "H"
            and m["selector_i"] == "C"
            and m["target_kind"] == "invariant"
            and m["target_parameter"] == 0,
        ),
        "drop_D_cue_channel": witness(
            restrict(selector=True, orientation=True),
            lambda m: m["selector_v"] == "C"
            and m["target_kind"] == "invariant",
        ),
        "drop_O_polarity_flip": witness(
            restrict(discordant=True, selector=True),
            lambda m: m["target_kind"] == "tracking"
            and m["target_parameter"] == 1,
        ),
    },
    "identified_model": restrict(discordant=True, selector=True, orientation=True),
    "conclusion": (
        "Veridical calibration and a frozen transfer output do not identify the "
        "illusion target when target and cue are co-aligned in calibration. "
        "Within this finite domain, source-discordant calibration, selector "
        "transport, and orientation transport are jointly sufficient; dropping "
        "any one leaves an observationally equivalent non-target or opposite-pole model."
    ),
}

print(json.dumps(result, indent=2, sort_keys=True))
