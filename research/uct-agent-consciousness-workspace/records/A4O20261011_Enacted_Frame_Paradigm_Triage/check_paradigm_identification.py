#!/usr/bin/env python3
"""Exact finite checks for the A4O source screen and endpoint twin."""

from itertools import product
import json


SOURCES = {
    "Cordo1995": ["YES", "YES", "PARTIAL", "PARTIAL", "NO", "YES"],
    "Iriki1996": ["PARTIAL", "NO", "PARTIAL", "PARTIAL", "PARTIAL", "PARTIAL"],
    "Cardinali2009": ["PARTIAL", "NO", "NO", "NO", "PARTIAL", "PARTIAL"],
    "Cardinali2016": ["PARTIAL", "PARTIAL", "NO", "NO", "PARTIAL", "PARTIAL"],
    "Takahashi2017": ["NO", "NO", "PARTIAL", "PARTIAL", "NO", "YES"],
    "ZografosThemelis2026": ["PARTIAL", "NO", "YES", "PARTIAL", "NO", "YES"],
}

CRITERIA = ["C_ext", "C_anchor", "C_remap", "C_route", "C_compare", "C_bind"]


def main():
    eligibility = {name: all(v == "YES" for v in grades) for name, grades in SOURCES.items()}
    worlds = []
    for external_fixed, perturb, bearer_remap, same_route, compensator, report in product([0, 1], repeat=6):
        endpoint_signature = int(bool(perturb and ((bearer_remap and same_route) or compensator)))
        frame_route = int(bool(bearer_remap and same_route))
        route_block_signature = int(bool(perturb and compensator))
        same_interface_rescue = endpoint_signature
        worlds.append({
            "external_fixed": external_fixed,
            "perturb": perturb,
            "bearer_remap": bearer_remap,
            "same_route": same_route,
            "compensator": compensator,
            "report": report,
            "endpoint_signature": endpoint_signature,
            "frame_route": frame_route,
            "route_block_signature": route_block_signature,
            "same_interface_rescue": same_interface_rescue,
        })

    endpoint_key = lambda w: (w["external_fixed"], w["perturb"], w["endpoint_signature"], w["report"])
    endpoint_twin_keys = []
    for key in sorted({endpoint_key(w) for w in worlds}):
        fibre = [w for w in worlds if endpoint_key(w) == key]
        if {w["frame_route"] for w in fibre} == {0, 1}:
            endpoint_twin_keys.append(key)

    frame_only = next(w for w in worlds if w["external_fixed"] == 1 and w["perturb"] == 1 and w["bearer_remap"] == 1 and w["same_route"] == 1 and w["compensator"] == 0 and w["report"] == 1)
    compensator_only = next(w for w in worlds if w["external_fixed"] == 1 and w["perturb"] == 1 and w["bearer_remap"] == 0 and w["same_route"] == 0 and w["compensator"] == 1 and w["report"] == 1)

    result = {
        "version": "A4O-EFP-CHECK-v0.1.0",
        "criteria_order": CRITERIA,
        "source_grades": SOURCES,
        "eligible_sources": [k for k, v in eligibility.items() if v],
        "source_count": len(SOURCES),
        "world_count": len(worlds),
        "endpoint_observation_keys_with_both_frame_route_values": [list(k) for k in endpoint_twin_keys],
        "endpoint_twin_key_count": len(endpoint_twin_keys),
        "declared_pair": {
            "frame_only": frame_only,
            "compensator_only": compensator_only,
            "same_endpoint_observation": endpoint_key(frame_only) == endpoint_key(compensator_only),
            "route_block_separates_under_closed_declared_model": frame_only["route_block_signature"] != compensator_only["route_block_signature"],
        },
        "checks": {
            "no_reviewed_source_has_full_joint_package": not any(eligibility.values()),
            "endpoint_only_does_not_identify_frame_route": len(endpoint_twin_keys) > 0,
            "declared_pair_matches_endpoint_and_report": endpoint_key(frame_only) == endpoint_key(compensator_only),
            "declared_route_block_separates_pair_conditionally": frame_only["route_block_signature"] != compensator_only["route_block_signature"],
            "no_phenomenal_assignment": True,
        },
    }
    assert all(result["checks"].values())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

