#!/usr/bin/env python3
"""Exact finite checks for consumer-relative motor/proprioceptive isolation."""

from itertools import product
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = []
    for motor, action, transduction, delivery, read in product((0, 1), repeat=5):
        proprio_intake = int(bool(action and transduction and delivery and read))
        rows.append({
            "M": motor,
            "A": action,
            "T": transduction,
            "L": delivery,
            "R": read,
            "P": proprio_intake,
        })

    missing_cell_realizations = [
        row for row in rows if row["M"] == 1 and row["A"] == 1 and row["P"] == 0
    ]
    single_cut_realizations = [
        row for row in missing_cell_realizations
        if row["T"] + row["L"] + row["R"] == 2
    ]
    intact_branch_counterexamples = [
        row for row in missing_cell_realizations
        if row["T"] == row["L"] == row["R"] == 1
    ]

    result = {
        "id": "CBI-RESULT-v0.1.0",
        "definition": "P := A AND T AND L AND R for the selected movement-evoked signal, consumer and time window",
        "variables": {
            "M": "verified motor-command intake/use at the selected consumer",
            "A": "declared actual distal movement/contact event occurs",
            "T": "that event is transduced into the declared proprioceptive/state carrier",
            "L": "the carrier is delivered to the selected consumer",
            "R": "the consumer reads it inside the declared time window",
            "P": "actual selected proprioceptive/state intake event",
        },
        "enumerated_rows": len(rows),
        "motor_action_present_P_absent_rows": len(missing_cell_realizations),
        "single_branch_cut_rows": len(single_cut_realizations),
        "single_branch_cut_labels": [
            "transduction_cut" if not row["T"] else
            "delivery_cut" if not row["L"] else
            "read_cut"
            for row in single_cut_realizations
        ],
        "intact_branch_counterexamples": intact_branch_counterexamples,
        "checks": {
            "truth_table_has_32_rows": len(rows) == 32,
            "motor_action_present_P_absent_has_7_cut_sets": len(missing_cell_realizations) == 7,
            "exactly_three_minimal_single_cuts": len(single_cut_realizations) == 3,
            "no_P_absent_case_with_all_branch_conditions_intact": not intact_branch_counterexamples,
            "motor_variable_does_not_define_proprioceptive_intake": all(
                row["P"] == int(bool(row["A"] and row["T"] and row["L"] and row["R"]))
                for row in rows
            ),
        },
        "scope_limit": "Finite definitional consequence for one declared branch; not a biological impossibility theorem, phenomenal bridge, or consciousness test.",
    }
    assert all(result["checks"].values())
    rendered = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()

