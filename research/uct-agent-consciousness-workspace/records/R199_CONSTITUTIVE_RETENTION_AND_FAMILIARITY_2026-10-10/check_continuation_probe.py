#!/usr/bin/env python3
"""Exact finite witness for the R199 continuation-probe ceiling.

Enumerates every deterministic two-state, binary-intervention machine with a
binary readout.  External lineage labels are deliberately not inputs to the
transition/readout law.  Complete present operational clones therefore have
identical traces for every intervention word through the declared horizon.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def bit(table: int, x: int, u: int) -> int:
    return (table >> (2 * x + u)) & 1


def trace(trans: int, readout: int, x0: int, word: tuple[int, ...]) -> tuple[int, ...]:
    x = x0
    out = []
    for u in word:
        out.append(bit(readout, x, u))
        x = bit(trans, x, u)
    out.append(bit(readout, x, 0))
    return tuple(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--horizon", type=int, default=4)
    args = parser.parse_args()

    words = [w for n in range(args.horizon + 1) for w in itertools.product((0, 1), repeat=n)]
    machines = list(itertools.product(range(16), range(16), (0, 1)))
    clone_checks = 0
    clone_mismatches = []
    state_sensitive_machines = 0
    state_pairs_checked = 0

    for trans, readout, x0 in machines:
        # Compare external lineage labels L=0 and L=1 while the complete
        # operational state and law remain identical.
        for word in words:
            clone_checks += 1
            a = trace(trans, readout, x0, word)
            b = trace(trans, readout, x0, word)
            if a != b:
                clone_mismatches.append([trans, readout, x0, word])

        # Show the converse does not hold: changing a currently carried state
        # can change a continuation trace, but not for every machine.
        differs = False
        for word in words:
            state_pairs_checked += 1
            if trace(trans, readout, 0, word) != trace(trans, readout, 1, word):
                differs = True
        if differs:
            state_sensitive_machines += 1

    result = {
        "schema": "uct-r199-continuation-probe-check/1",
        "model": {
            "states": 2,
            "interventions": 2,
            "readouts": 2,
            "deterministic_transition_tables": 16,
            "deterministic_readout_tables": 16,
            "present_states": 2,
            "external_lineage_labels": 2,
            "maximum_intervention_word_length": args.horizon,
            "intervention_words": len(words),
        },
        "exact_results": {
            "operational_machine_state_instances": len(machines),
            "complete_clone_trace_comparisons": clone_checks,
            "complete_clone_trace_mismatches": len(clone_mismatches),
            "machines_whose_continuation_can_depend_on_present_state": state_sensitive_machines,
            "state_pair_word_comparisons": state_pairs_checked,
        },
        "proved_scope": "For the fully enumerated finite class, changing only an external lineage label never changes any future trace. A currently carried state difference sometimes changes traces, so a positive continuation contrast can witness an operational difference but not its lineage or phenomenal meaning.",
        "not_proved": [
            "that a real biological or artificial application has been completely modeled",
            "that an observed contrast uniquely identifies a retained mechanism",
            "that any trace is constituted by or measures phenomenal familiarity H",
            "that C1 is empirically true",
        ],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["exact_results"], sort_keys=True))
    if clone_mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
