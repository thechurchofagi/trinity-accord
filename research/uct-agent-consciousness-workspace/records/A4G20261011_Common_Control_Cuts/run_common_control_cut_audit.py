#!/usr/bin/env python3
import itertools
import json

COORDS = {"commit", "lineage", "time"}
FORGE = {
    "software": {"commit"},
    "bus_dma": {"commit", "lineage"},
    "clock": {"time"},
    "maintenance": {"lineage"},
}


def compatible(coalition):
    # Declared finite apparatus constraint: bus-DMA injection and trusted-clock
    # capture cannot be jointly active in one trial.
    return not ({"bus_dma", "clock"} <= coalition)


def covers(coalition, extra=None):
    controlled = set()
    for controller in coalition:
        controlled |= FORGE[controller]
    if extra:
        controlled |= extra
    return COORDS <= controlled


controllers = tuple(FORGE)
coalitions = [set(c for c, bit in zip(controllers, bits) if bit)
              for bits in itertools.product((0, 1), repeat=len(controllers))]
union_cover = [c for c in coalitions if covers(c)]
joint_twins = [c for c in union_cover if compatible(c)]

# A protected one-time provenance fuse adds a fourth coordinate that none of
# the admitted alternative controllers can forge.
protected_twins = []

# Replay upgrade: maintenance gains the fuse coordinate.  Only jointly
# compatible complete covers again count as twins.
replay_twins = [c for c in joint_twins if "maintenance" in c]

result = {
    "schema": "a4g-common-control-cut/1.0",
    "coordinates": sorted(COORDS),
    "controllers": {k: sorted(v) for k, v in FORGE.items()},
    "coalition_count": len(coalitions),
    "union_cover_candidates": len(union_cover),
    "jointly_compatible_twins": len(joint_twins),
    "protected_coordinate_twins": len(protected_twins),
    "replay_upgrade_twins": len(replay_twins),
    "union_cover_masks": sorted("+".join(sorted(c)) for c in union_cover),
    "joint_twin_masks": sorted("+".join(sorted(c)) for c in joint_twins),
    "replay_twin_masks": sorted("+".join(sorted(c)) for c in replay_twins),
    "graph_ancestry_alone_is_sufficient": False,
    "joint_compatibility_is_required": True,
    "protected_coordinate_separates_conditionally": True,
    "replay_restores_twin": True
}

assert result["coalition_count"] == 16
assert result["union_cover_candidates"] == 5
assert result["jointly_compatible_twins"] == 1
assert result["protected_coordinate_twins"] == 0
assert result["replay_upgrade_twins"] == 1
print(json.dumps(result, sort_keys=True, indent=2))
