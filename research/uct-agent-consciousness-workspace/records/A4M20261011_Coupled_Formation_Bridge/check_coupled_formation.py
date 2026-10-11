#!/usr/bin/env python3
"""Exact finite checks for A4M's coupled-formation witness.

The program checks a stipulated Boolean model.  It does not assign experience,
identify a biological mechanism, or test C1.
"""

from __future__ import annotations

import itertools
import json


FIELDS = (
    "same_lineage_trace",
    "target_consumer_reads_trace",
    "fit_generator_reads_same_trace",
    "joint_formation",
    "ordered_same_event",
    "present_fit",
    "matched_output",
    "matched_report",
)


def predicates(world: dict[str, int]) -> dict[str, int]:
    retained_use = int(
        world["same_lineage_trace"]
        and world["target_consumer_reads_trace"]
        and world["ordered_same_event"]
    )
    coupling = int(
        retained_use
        and world["fit_generator_reads_same_trace"]
        and world["joint_formation"]
        and world["present_fit"]
    )
    return {
        "R": retained_use,
        "F": world["present_fit"],
        "C": coupling,
        "O": world["matched_output"],
        "J": world["matched_report"],
    }


def main() -> None:
    worlds = []
    for bits in itertools.product((0, 1), repeat=len(FIELDS)):
        world = dict(zip(FIELDS, bits))
        worlds.append({**world, **predicates(world)})

    marginal_groups: dict[tuple[int, ...], set[int]] = {}
    for world in worlds:
        key = (world["R"], world["F"], world["O"], world["J"])
        marginal_groups.setdefault(key, set()).add(world["C"])

    ambiguous = {
        str(key): sorted(values)
        for key, values in marginal_groups.items()
        if len(values) > 1
    }

    native = {
        "same_lineage_trace": 1,
        "target_consumer_reads_trace": 1,
        "fit_generator_reads_same_trace": 1,
        "joint_formation": 1,
        "ordered_same_event": 1,
        "present_fit": 1,
        "matched_output": 1,
        "matched_report": 1,
    }
    yoked = {
        **native,
        "fit_generator_reads_same_trace": 0,
        "joint_formation": 0,
    }
    copied = {
        **native,
        "same_lineage_trace": 0,
    }
    named = []
    for name, world in (("native_coformation", native), ("yoked_marginal_twin", yoked), ("copied_trace", copied)):
        named.append({"name": name, **world, **predicates(world)})

    assert named[0]["R"] == named[1]["R"] == 1
    assert named[0]["F"] == named[1]["F"] == 1
    assert named[0]["O"] == named[1]["O"] == 1
    assert named[0]["J"] == named[1]["J"] == 1
    assert named[0]["C"] == 1 and named[1]["C"] == 0
    assert named[2]["R"] == 0 and named[2]["C"] == 0
    assert ambiguous["(1, 1, 1, 1)"] == [0, 1]

    coupled_worlds = [world for world in worlds if world["C"]]
    assert all(world["R"] and world["F"] for world in coupled_worlds)
    assert any(world["R"] and world["F"] and not world["C"] for world in worlds)

    result = {
        "schema": "uct-a4m-exact-results/1",
        "model_scope": "stipulated finite Boolean organizational witness; no phenomenal assignments",
        "world_count": len(worlds),
        "definition": {
            "R": "same_lineage_trace AND target_consumer_reads_trace AND ordered_same_event",
            "F": "present_fit",
            "C": "R AND fit_generator_reads_same_trace AND joint_formation AND F",
            "observed_marginal_view": ["R", "F", "O", "J"],
        },
        "named_worlds": named,
        "marginal_keys_with_both_coupling_values": ambiguous,
        "checks": {
            "native_and_yoked_match_R_F_output_report": True,
            "native_and_yoked_differ_in_coupling": True,
            "coupling_implies_R_and_F_in_this_model": True,
            "R_and_F_do_not_imply_coupling": True,
            "copied_value_does_not_supply_same_lineage_R": True,
            "no_experience_value_assigned": True,
        },
        "status": "PASS_WITH_DECLARED_FINITE_SCOPE",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
