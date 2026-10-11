#!/usr/bin/env python3
"""Exact finite check for two simultaneous bearer-centred routes.

The model is intentionally tiny.  It classifies all Boolean mergers after two
local XOR bearer-coordinate decoders.  It is not an actuality or phenomenal
test.
"""

from __future__ import annotations

import json


def bit(table: int, u: int, v: int) -> int:
    """Truth-table bit in input order 00, 01, 10, 11."""
    return (table >> (2 * u + v)) & 1


def table_bits(table: int) -> list[int]:
    return [bit(table, u, v) for u in (0, 1) for v in (0, 1)]


def depends_on(table: int, position: int) -> bool:
    if position == 0:
        return any(bit(table, 0, v) != bit(table, 1, v) for v in (0, 1))
    return any(bit(table, u, 0) != bit(table, u, 1) for u in (0, 1))


rows = []
for x in (0, 1):
    for a in (0, 1):
        for b in (0, 1):
            r1 = x ^ a
            r2 = x ^ b
            u = r1 ^ a
            v = r2 ^ b
            assert u == x and v == x
            # Each local route has nontrivial anchor and route contrasts, while
            # the joint anchor+route toggle preserves the local coordinate.
            assert (r1 ^ (a ^ 1)) != u
            assert ((r1 ^ 1) ^ a) != u
            assert ((r1 ^ 1) ^ (a ^ 1)) == u
            assert (r2 ^ (b ^ 1)) != v
            assert ((r2 ^ 1) ^ b) != v
            assert ((r2 ^ 1) ^ (b ^ 1)) == v
            rows.append({"x": x, "a": a, "b": b, "r1": r1, "r2": r2, "u": u, "v": v})

classifications = []
for table in range(16):
    bits = table_bits(table)
    normal_correct = all(bit(table, row["u"], row["v"]) == row["x"] for row in rows)
    dep_u = depends_on(table, 0)
    dep_v = depends_on(table, 1)
    symmetric = all(bit(table, u, v) == bit(table, v, u) for u in (0, 1) for v in (0, 1))
    name = {
        (0, 0, 0, 1): "AND",
        (0, 1, 1, 1): "OR",
        (0, 0, 1, 1): "PROJECTION_U",
        (0, 1, 0, 1): "PROJECTION_V",
    }.get(tuple(bits), f"TABLE_{table}")
    classifications.append(
        {
            "table_id": table,
            "bits_00_01_10_11": bits,
            "name": name,
            "normal_correct": normal_correct,
            "depends_on_u": dep_u,
            "depends_on_v": dep_v,
            "symmetric": symmetric,
            "kind": (
                "SYMMETRIC_TWO_INPUT_MERGE"
                if normal_correct and dep_u and dep_v and symmetric
                else "ONE_INPUT_PROJECTION"
                if normal_correct and dep_u != dep_v
                else "OTHER"
            ),
        }
    )

correct = [c for c in classifications if c["normal_correct"]]
selectors = [c for c in correct if c["kind"] == "ONE_INPUT_PROJECTION"]
two_input = [c for c in correct if c["kind"] == "SYMMETRIC_TWO_INPUT_MERGE"]

assert len(rows) == 8
assert len(classifications) == 16
assert len(correct) == 4
assert {c["name"] for c in correct} == {"AND", "OR", "PROJECTION_U", "PROJECTION_V"}
assert len(selectors) == 2
assert len(two_input) == 2

result = {
    "schema": "uct-a4w-overlapping-centres-exact/1.0",
    "model_scope": "two XOR bearer-centred local routes plus every deterministic Boolean downstream merger",
    "input_worlds": len(rows),
    "merge_functions": len(classifications),
    "normal_output_correct": len(correct),
    "one_input_projections": len(selectors),
    "symmetric_two_input_merges": len(two_input),
    "correct_functions": correct,
    "normal_manifold": [[0, 0], [1, 1]],
    "off_manifold_challenge_required": [[0, 1], [1, 0]],
    "local_bcr_checks": {
        "route_1_anchor_contrast": True,
        "route_1_route_contrast": True,
        "route_1_joint_compensation": True,
        "route_2_anchor_contrast": True,
        "route_2_route_contrast": True,
        "route_2_joint_compensation": True,
    },
    "claims_not_tested": [
        "physical actuality or complete organization",
        "phenomenal identity or measurement",
        "unique subject or owner count",
        "general noisy, multibit or continuous composition",
    ],
}
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
