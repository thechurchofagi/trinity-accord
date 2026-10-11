#!/usr/bin/env python3
"""Exact finite checker for A4T's boundary-mode contract."""

from itertools import product
import json


MODES = ("N", "I", "T")


def main() -> None:
    worlds = []
    for mode_sc, mode_cw, value_sc, value_cw in product(MODES, MODES, (0, 1), (0, 1)):
        route = mode_sc != "N" and mode_cw != "N"
        strict_identity = mode_sc == "I" and mode_cw == "I"
        worlds.append(
            {
                "mode_sc": mode_sc,
                "mode_cw": mode_cw,
                "value_equal_sc": value_sc,
                "value_equal_cw": value_cw,
                "route": route,
                "strict_identity": strict_identity,
            }
        )

    equal_fiber = [w for w in worlds if w["value_equal_sc"] and w["value_equal_cw"]]
    mode_pairs = [w for w in worlds if not w["value_equal_sc"] and not w["value_equal_cw"]]
    coherent_modes = [w for w in mode_pairs if w["route"]]
    strict_modes = [w for w in coherent_modes if w["strict_identity"]]
    result = {
        "schema": "uct-a4t-exact/1.0",
        "valid_worlds": len(worlds),
        "boundary_mode_pairs": len(mode_pairs),
        "coherent_boundary_modes": len(coherent_modes),
        "strict_identity_modes": len(strict_modes),
        "coherent_non_strict_modes": len(coherent_modes) - len(strict_modes),
        "all_value_equal_fiber": {
            "worlds": len(equal_fiber),
            "route_worlds": sum(w["route"] for w in equal_fiber),
            "nonroute_worlds": sum(not w["route"] for w in equal_fiber),
            "mode_pairs": [[w["mode_sc"], w["mode_cw"]] for w in equal_fiber],
        },
        "coherent_mode_pairs": [[w["mode_sc"], w["mode_cw"]] for w in coherent_modes],
        "strict_false_negative_pairs": [
            [w["mode_sc"], w["mode_cw"]]
            for w in coherent_modes
            if not w["strict_identity"]
        ],
        "interpretation": {
            "N": "no established boundary stitch",
            "I": "actual identity relay",
            "T": "actual transduction to a distinct successor occurrence",
        },
        "scope_warning": "Exact only for the declared finite modes; not a physical installation or exhaustive causal model.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
