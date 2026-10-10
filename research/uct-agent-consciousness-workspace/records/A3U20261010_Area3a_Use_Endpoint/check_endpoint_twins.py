#!/usr/bin/env python3
"""Exact finite checks for A3U endpoint-use claims.

This is a four-variable Boolean audit, not a biological simulation.
"""

from itertools import product
import json


def use_model(s: int, g: int, q: int) -> tuple[int, int]:
    """Selective area-3a block g; faithful downstream replay q."""
    r = s & (1 - g)
    y = r | (q & s)
    return r, y


def spill_model(s: int, g: int, q: int) -> tuple[int, int]:
    """No R->Y use; g directly suppresses the endpoint."""
    r = s & (1 - g)
    y = s & (1 - g)
    return r, y


baseline_rows = []
rescue_rows = []
for s, g in product((0, 1), repeat=2):
    u = use_model(s, g, 0)
    d = spill_model(s, g, 0)
    baseline_rows.append({"s": s, "g": g, "q": 0, "use": {"r": u[0], "y": u[1]}, "spill": {"r": d[0], "y": d[1]}})
for s in (0, 1):
    u = use_model(s, 1, 1)
    d = spill_model(s, 1, 1)
    rescue_rows.append({"s": s, "g": 1, "q": 1, "use": {"r": u[0], "y": u[1]}, "spill": {"r": d[0], "y": d[1]}})

baseline_equal = all(row["use"] == row["spill"] for row in baseline_rows)
rescue_separates = any(row["use"] != row["spill"] for row in rescue_rows)
assert baseline_equal
assert rescue_separates
assert next(row for row in rescue_rows if row["s"] == 1)["use"]["y"] == 1
assert next(row for row in rescue_rows if row["s"] == 1)["spill"]["y"] == 0

print(json.dumps({
    "schema": "uct-exact-results/1",
    "record": "A3U20261010_Area3a_Use_Endpoint",
    "baseline_interventional_twin": {
        "rows": baseline_rows,
        "same_observables_for_all_s_g_cells": baseline_equal,
        "interpretation": "The area-3a-mediated model and direct-spillover model agree on S,G,R,Y for every source/block cell when rescue is absent."
    },
    "path_specific_rescue": {
        "rows": rescue_rows,
        "separates_models": rescue_separates,
        "discriminating_cell": {"s": 1, "g": 1, "q": 1, "use_y": 1, "spill_y": 0},
        "conditional_on": [
            "g blocks the declared area-3a contribution without directly changing Y",
            "q faithfully substitutes the relevant area-3a output at the declared downstream port",
            "q has no independent path to Y",
            "source, event window and endpoint semantics are fixed"
        ]
    },
    "novelty": "No new general causal-mediation mathematics is claimed; this is a finite UCT probe-contract witness."
}, indent=2, sort_keys=True))
