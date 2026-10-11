#!/usr/bin/env python3
"""Exact finite check for the A4P anchor-route intervention contract."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def route_on(use_route: int, block: int, rescue: int, block_faithful: int, rescue_faithful: int) -> int:
    if not use_route:
        return 0
    if not block:
        return 1
    if not block_faithful:
        return 1
    return int(bool(rescue and rescue_faithful))


def response(world: dict[str, int], anchor_perturbed: int, block: int, rescue: int) -> int:
    if not anchor_perturbed:
        return 0
    target = route_on(
        world["use_route"], block, rescue,
        world["block_faithful"], world["rescue_faithful"],
    )
    ordinary_compensator = world["compensator"]
    hidden_mimic = world["hidden_controller"] and ((not block) or rescue)
    return int(bool(target or ordinary_compensator or hidden_mimic))


def signature(world: dict[str, int]) -> list[int]:
    # no-anchor baseline, anchor/native, anchor/block, anchor/block+same-interface rescue
    conditions = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)]
    return [response(world, *condition) for condition in conditions]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    names = ["use_route", "compensator", "hidden_controller", "block_faithful", "rescue_faithful"]
    worlds = []
    for bits in itertools.product((0, 1), repeat=len(names)):
        world = dict(zip(names, bits))
        world["signature"] = signature(world)
        worlds.append(world)

    target_signature = [0, 1, 0, 1]
    fibre = [w for w in worlds if w["signature"] == target_signature]
    closed = [
        w for w in worlds
        if w["compensator"] == 0
        and w["hidden_controller"] == 0
        and w["block_faithful"] == 1
        and w["rescue_faithful"] == 1
    ]
    closed_fibre = [w for w in closed if w["signature"] == target_signature]

    result = {
        "schema": "uct-a4p-anchor-route-check/1.0",
        "model_status": "finite_abstract_declared_model_not_physical_installation",
        "world_count": len(worlds),
        "conditions": [
            "no_anchor_baseline",
            "anchor_native",
            "anchor_route_input_block",
            "anchor_same_interface_rescue",
        ],
        "target_signature": target_signature,
        "unrestricted_target_fibre_count": len(fibre),
        "unrestricted_target_fibre_route_values": sorted({w["use_route"] for w in fibre}),
        "unrestricted_target_fibre": fibre,
        "closed_model_world_count": len(closed),
        "closed_target_fibre_count": len(closed_fibre),
        "closed_target_fibre_route_values": sorted({w["use_route"] for w in closed_fibre}),
        "closed_target_fibre": closed_fibre,
        "checks": {
            "unrestricted_signature_does_not_identify_route": sorted({w["use_route"] for w in fibre}) == [0, 1],
            "closure_and_fidelity_make_signature_identify_route": sorted({w["use_route"] for w in closed_fibre}) == [1],
            "closed_target_fibre_is_singleton": len(closed_fibre) == 1,
            "no_phenomenal_assignment": True,
        },
        "interpretation": {
            "positive": "In this declared Boolean model, the 0-1-0-1 signature identifies declared route use only after ordinary compensators and intervention-aware hidden controllers are excluded and block/rescue fidelity is fixed.",
            "negative": "Without those closure premises, the same signature is compatible with both route-use values.",
            "limit": "The truth table does not prove physical controller completeness, route equivalence, incorporation, complete UCT actuality, C1, H_cf, report validity, or unique ownership.",
        },
    }

    assert all(result["checks"].values())
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
