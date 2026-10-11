#!/usr/bin/env python3
"""Exact finite check for A4X redundant-port participation.

This classifies every deterministic Boolean two-port consumer.  It tests a
bounded mechanistic relevance criterion; it is not a general definition of
actual causation and it makes no phenomenal inference.
"""

from __future__ import annotations

import json
from pathlib import Path


OUT = Path(__file__).with_name("EXACT_RESULTS.json")
ROWS = ((0, 0), (0, 1), (1, 0), (1, 1))
NAMES = {
    (0, 0, 0, 1): "AND",
    (0, 1, 0, 1): "PROJECTION_V",
    (0, 0, 1, 1): "PROJECTION_U",
    (0, 1, 1, 1): "OR",
}


def val(bits: tuple[int, ...], u: int, v: int) -> int:
    return bits[ROWS.index((u, v))]


def classify(table_id: int) -> dict:
    bits = tuple((table_id >> i) & 1 for i in range(4))
    u_witnesses = [v for v in (0, 1) if val(bits, 0, v) != val(bits, 1, v)]
    v_witnesses = [u for u in (0, 1) if val(bits, u, 0) != val(bits, u, 1)]
    normal_rows = []
    for x in (0, 1):
        normal_rows.append(
            {
                "inputs": [x, x],
                "output": val(bits, x, x),
                "u_actual_but_for": val(bits, x, x) != val(bits, 1 - x, x),
                "v_actual_but_for": val(bits, x, x) != val(bits, x, 1 - x),
            }
        )
    return {
        "table_id": table_id,
        "name": NAMES.get(bits, f"TABLE_{table_id}"),
        "bits_00_01_10_11": list(bits),
        "normal_correct": bits[0] == 0 and bits[3] == 1,
        "depends_on_u": bool(u_witnesses),
        "depends_on_v": bool(v_witnesses),
        "u_contingency_witness_sibling_v": u_witnesses,
        "v_contingency_witness_sibling_u": v_witnesses,
        "representable_from_u_alone": bits[0] == bits[1] and bits[2] == bits[3],
        "representable_from_v_alone": bits[0] == bits[2] and bits[1] == bits[3],
        "normal_rows": normal_rows,
        "both_ports_but_for_on_every_normal_row": all(
            r["u_actual_but_for"] and r["v_actual_but_for"] for r in normal_rows
        ),
    }


def main() -> None:
    functions = [classify(i) for i in range(16)]
    correct = [f for f in functions if f["normal_correct"]]
    dual = [f for f in correct if f["depends_on_u"] and f["depends_on_v"]]
    projections = [
        f
        for f in correct
        if f["representable_from_u_alone"] ^ f["representable_from_v_alone"]
    ]
    universal_but_for = [
        f for f in correct if f["both_ports_but_for_on_every_normal_row"]
    ]

    assert len(functions) == 16
    assert {f["name"] for f in correct} == {
        "AND",
        "PROJECTION_U",
        "PROJECTION_V",
        "OR",
    }
    assert {f["name"] for f in dual} == {"AND", "OR"}
    assert {f["name"] for f in projections} == {"PROJECTION_U", "PROJECTION_V"}
    assert not universal_but_for
    assert next(f for f in dual if f["name"] == "AND")[
        "u_contingency_witness_sibling_v"
    ] == [1]
    assert next(f for f in dual if f["name"] == "OR")[
        "u_contingency_witness_sibling_v"
    ] == [0]

    # Both off-diagonal rows are needed to rule out both projections when the
    # identity of a possible one-port projection is not known in advance.
    for target in dual:
        disagreements = {
            p["name"]: [
                list(row)
                for row in ((0, 1), (1, 0))
                if val(tuple(target["bits_00_01_10_11"]), *row)
                != val(tuple(p["bits_00_01_10_11"]), *row)
            ]
            for p in projections
        }
        assert all(len(rows) == 1 for rows in disagreements.values())
        target["projection_disagreement_rows"] = disagreements

    result = {
        "schema": "uct-a4x-redundant-port-participation-exact/1.0",
        "scope": "all deterministic Boolean two-port consumers with A4W diagonal correctness",
        "all_functions": 16,
        "normal_diagonal": [[0, 0], [1, 1]],
        "normal_correct_functions": len(correct),
        "normal_correct": correct,
        "dual_port_contingently_relevant": len(dual),
        "one_port_projections": len(projections),
        "both_ports_but_for_on_every_normal_row": len(universal_but_for),
        "full_factorial_rows": [list(r) for r in ROWS],
        "result": (
            "Within the declared Boolean family, diagonal success leaves four "
            "functions. Full port-specific contingent sensitivity retains AND/OR "
            "and rejects both projections; universal actual-row but-for necessity "
            "rejects every correct function."
        ),
        "not_tested": [
            "actual port binding, read occurrence, lineage or mechanism freeze",
            "faithfulness of physical interventions or alternate-path exclusion",
            "general actual-causation definitions",
            "physical installation, complete organization or phenomenal identity",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
