#!/usr/bin/env python3
"""Exact finite checks for the A4D actuator-writer completeness argument."""

from itertools import product
import argparse
import json
from pathlib import Path


MODES = ("baseline", "block", "rescue")


def genuine(q: int, mode: str) -> int:
    return 0 if mode == "block" else q


def table_from_bits(bits):
    return {mode: bit for mode, bit in zip(MODES, bits)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cells = [(q, mode) for mode in MODES for q in (0, 1)]
    expected = {f"q={q}|mode={mode}": genuine(q, mode) for q, mode in cells}

    # An uncut hidden writer with timely access to both challenge and mode can
    # implement any Boolean table on the six tested cells.
    unrestricted_match_count = 0
    for bits in product((0, 1), repeat=len(cells)):
        if all(bit == genuine(*cell) for cell, bit in zip(cells, bits)):
            unrestricted_match_count += 1

    # A hidden writer that is fixed across the paired q=0/q=1 challenges and
    # sees mode but not the current challenge has only 2^3 possible tables.
    mode_only_matches = []
    for bits in product((0, 1), repeat=len(MODES)):
        h = table_from_bits(bits)
        if all(h[mode] == genuine(q, mode) for q, mode in cells):
            mode_only_matches.append(h)

    # With only q=1 tested, one mode-only writer exactly mimics all three arms.
    one_challenge_matches = []
    for bits in product((0, 1), repeat=len(MODES)):
        h = table_from_bits(bits)
        if all(h[mode] == genuine(1, mode) for mode in MODES):
            one_challenge_matches.append(h)

    # Explicit observational twin: target disconnected, hidden writer copies
    # the full genuine table after observing q and mode.
    twin_rows = []
    for q, mode in cells:
        target_connected_genuine = mode != "block"
        target_connected_twin = False
        hidden_value = genuine(q, mode)
        actuator_genuine = genuine(q, mode)
        actuator_twin = hidden_value
        twin_rows.append(
            {
                "challenge": q,
                "mode": mode,
                "logged_command": genuine(q, mode),
                "genuine_target_connected": target_connected_genuine,
                "twin_target_connected": target_connected_twin,
                "twin_hidden_writer_value": hidden_value,
                "actuator_genuine": actuator_genuine,
                "actuator_twin": actuator_twin,
                "observational_match": actuator_genuine == actuator_twin,
            }
        )

    checks = {
        "six_cells_enumerated": len(cells) == 6,
        "unrestricted_hidden_writer_function_count": 2 ** len(cells) == 64,
        "unrestricted_exact_twin_count": unrestricted_match_count == 1,
        "mode_only_function_count": 2 ** len(MODES) == 8,
        "mode_only_exact_twin_count": len(mode_only_matches) == 0,
        "single_challenge_mode_only_twin_count": len(one_challenge_matches) == 1,
        "explicit_twin_matches_every_actuator_cell": all(
            row["observational_match"] for row in twin_rows
        ),
        "explicit_twin_target_is_idle_everywhere": all(
            not row["twin_target_connected"] for row in twin_rows
        ),
    }
    assert all(checks.values())

    result = {
        "schema": "a4d-writer-completeness-exact/1.0",
        "domain": {
            "challenge": [0, 1],
            "modes": list(MODES),
            "cell_count": len(cells),
            "meaning": "Boolean actuator-transition abstraction; not a robot or human experiment.",
        },
        "expected_genuine_table": expected,
        "negative_result": {
            "unrestricted_hidden_writer_tables": 64,
            "exact_observational_twins": unrestricted_match_count,
            "interpretation": "If an uncut writer sees current challenge and intervention mode, one target-idle table reproduces all tested actuator transitions."
        },
        "bounded_positive_result": {
            "mode_only_hidden_writer_tables": 8,
            "exact_twins_under_paired_challenges": len(mode_only_matches),
            "exact_twins_if_only_q_equals_1_is_tested": len(one_challenge_matches),
            "interpretation": "Paired challenge variation rejects every mode-only writer, but only if physical evidence independently establishes that all non-target writers are challenge-blind or cut."
        },
        "explicit_twin": twin_rows,
        "checks": checks,
        "limits": [
            "Enumeration proves only the stated finite Boolean claims.",
            "Challenge blindness, writer enumeration, cut fidelity and probe placement are physical premises, not consequences of the table.",
            "No complete K signature, RetBind, H_way, familiar mineness or consciousness status is established."
        ]
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
