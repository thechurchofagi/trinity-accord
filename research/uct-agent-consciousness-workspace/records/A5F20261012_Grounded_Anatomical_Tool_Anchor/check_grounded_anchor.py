#!/usr/bin/env python3
"""Exact finite checks for the A5F typed anchor–grip–side model."""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass


BITS = (0, 1)
PERMS = ((0, 1), (1, 0))


@dataclass(frozen=True)
class Structure:
    # A[h]: one declared anatomical/bearer anchor on the hand sort.
    anchor: tuple[int, int]
    # G[h,t]: actual hand-to-held-tool incidence.
    grip: tuple[int, int, int, int]
    # X[t]: current membership of the distal tip in one fixed external half-space.
    side: tuple[int, int]

    def g(self, h: int, t: int) -> int:
        return self.grip[2 * h + t]


def structures():
    for bits in itertools.product(BITS, repeat=8):
        yield Structure(bits[:2], bits[2:6], bits[6:])


def transform(s: Structure, ph: tuple[int, int], pt: tuple[int, int]) -> Structure:
    # Pull relations forward along the typed bijections.
    a = [0, 0]
    g = [0, 0, 0, 0]
    x = [0, 0]
    for h in BITS:
        a[ph[h]] = s.anchor[h]
    for h in BITS:
        for t in BITS:
            g[2 * ph[h] + pt[t]] = s.g(h, t)
    for t in BITS:
        x[pt[t]] = s.side[t]
    return Structure(tuple(a), tuple(g), tuple(x))


def isomorphic(s: Structure, q: Structure) -> bool:
    return any(transform(s, ph, pt) == q for ph in PERMS for pt in PERMS)


def crossed(s: Structure) -> Structure:
    # Same hand tokens and same held-tool incidence; each distal tip changes side.
    return Structure(s.anchor, s.grip, tuple(1 - b for b in s.side))


def unique_anchor(s: Structure) -> bool:
    return sum(s.anchor) == 1


def anchored_hand(s: Structure) -> int:
    assert unique_anchor(s)
    return s.anchor.index(1)


def unique_tip_from_anchor(s: Structure) -> bool:
    if not unique_anchor(s):
        return False
    h = anchored_hand(s)
    return sum(s.g(h, t) for t in BITS) == 1


def held_tip(s: Structure) -> int:
    assert unique_tip_from_anchor(s)
    h = anchored_hand(s)
    return next(t for t in BITS if s.g(h, t))


def perfect_matching_grip(s: Structure) -> bool:
    return (
        all(sum(s.g(h, t) for t in BITS) == 1 for h in BITS)
        and all(sum(s.g(h, t) for h in BITS) == 1 for t in BITS)
    )


def opposite_tip_sides(s: Structure) -> bool:
    return sum(s.side) == 1


def main() -> None:
    all_s = list(structures())
    pair_swap = ((1, 0), (1, 0))
    pair_swap_aut = [s for s in all_s if transform(s, *pair_swap) == s]

    grounded = [s for s in all_s if unique_tip_from_anchor(s)]
    grounded_cross_noniso = [s for s in grounded if not isomorphic(s, crossed(s))]

    no_anchor_tool = [
        s
        for s in all_s
        if s.anchor == (0, 0) and perfect_matching_grip(s) and opposite_tip_sides(s)
    ]
    no_anchor_cross_iso = [s for s in no_anchor_tool if isomorphic(s, crossed(s))]

    anchored_tool = [
        s
        for s in all_s
        if unique_anchor(s) and perfect_matching_grip(s) and opposite_tip_sides(s)
    ]
    anchored_cross_noniso = [s for s in anchored_tool if not isomorphic(s, crossed(s))]
    coordinate_flips = [
        s
        for s in anchored_tool
        if s.side[held_tip(s)] != crossed(s).side[held_tip(s)]
    ]

    checks = {
        "total_structures": len(all_s),
        "pair_swap_automorphisms": len(pair_swap_aut),
        "pair_swap_nonautomorphisms": len(all_s) - len(pair_swap_aut),
        "unique_anchor_unique_grip_worlds": len(grounded),
        "unique_anchor_cross_nonisomorphic": len(grounded_cross_noniso),
        "restricted_tool_worlds_without_anchor": len(no_anchor_tool),
        "restricted_tool_cross_isomorphic_without_anchor": len(no_anchor_cross_iso),
        "restricted_tool_worlds_with_unique_anchor": len(anchored_tool),
        "restricted_tool_cross_nonisomorphic_with_anchor": len(anchored_cross_noniso),
        "anchored_side_coordinate_flips": len(coordinate_flips),
    }

    expected = {
        "total_structures": 256,
        "pair_swap_automorphisms": 16,
        "pair_swap_nonautomorphisms": 240,
        "unique_anchor_unique_grip_worlds": 64,
        "unique_anchor_cross_nonisomorphic": 64,
        "restricted_tool_worlds_without_anchor": 4,
        "restricted_tool_cross_isomorphic_without_anchor": 4,
        "restricted_tool_worlds_with_unique_anchor": 8,
        "restricted_tool_cross_nonisomorphic_with_anchor": 8,
        "anchored_side_coordinate_flips": 8,
    }
    assert checks == expected, (checks, expected)

    result = {
        "schema": "uct-a5f-grounded-anchor-check/1.0",
        "model": {
            "sorts": {"hands": 2, "tool_tips": 2},
            "relations": {
                "Anchor": "unary on hands",
                "Grip": "binary hands x tool_tips",
                "ExternalSide": "unary on tool_tips",
            },
            "crossing_intervention": "fix Anchor and Grip token incidence; complement ExternalSide on both tips",
        },
        "counts": checks,
        "claims_checked": [
            "The simultaneous hand-tip pair swap is an automorphism in exactly 16 of 256 typed structures.",
            "A unique hand anchor plus exactly one gripped tip makes the side-complement intervention non-isomorphic in all 64 declared worlds.",
            "In the restricted two-stick perfect-matching/opposite-side family, all four anchor-free crossed pairs are isomorphic, while all eight uniquely anchored pairs are non-isomorphic.",
            "The parameter-free anchored distal-side coordinate flips in all eight restricted uniquely anchored worlds.",
        ],
        "limits": [
            "Finite typed model only; it does not prove that the complete biological K has exactly these relations.",
            "ExternalSide is a declared grounded spatial relation, not an analyst label or response key.",
            "No phenomenal target, ownership, agency, mineness, report reliability or C1 truth is assigned.",
            "Non-isomorphism is sufficient here to remove the A5E automorphism barrier; it is not sufficient to validate B_pc.",
        ],
        "status": "PASS",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
