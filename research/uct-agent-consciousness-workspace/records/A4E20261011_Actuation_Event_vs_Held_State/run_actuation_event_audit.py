#!/usr/bin/env python3
"""Exact finite checks for level-state versus actuation-event evidence."""

import json
from collections import Counter, defaultdict


def main():
    sources = ("none", "target", "hidden")
    histories = []
    for pre in (0, 1):
        for challenge in (0, 1):
            for source in sources:
                final = pre if source == "none" else challenge
                histories.append({
                    "pre_state": pre,
                    "challenge": challenge,
                    "source": source,
                    "commit": source != "none",
                    "final_level": final,
                })

    level_classes = defaultdict(list)
    event_classes = defaultdict(list)
    for h in histories:
        level_classes[(h["pre_state"], h["challenge"], h["final_level"])].append(h["source"])
        event_classes[(h["pre_state"], h["challenge"], h["final_level"], h["commit"], h["source"])].append(h["source"])

    level_sizes = Counter(len(v) for v in level_classes.values())
    event_sizes = Counter(len(v) for v in event_classes.values())

    protocol = []
    for pre in (0, 1):
        q = 1 - pre
        for arm in ("baseline", "target_cut", "same_interface_rescue"):
            if arm == "baseline":
                source, final = "target", q
            elif arm == "target_cut":
                source, final = "none", pre
            else:
                source, final = "rescue", q
            protocol.append({"pre_state": pre, "challenge": q, "arm": arm, "source": source, "final_level": final})

    out = {
        "schema": "a4e-actuation-event-exact/1.0",
        "single_cell_enumeration": {
            "histories": len(histories),
            "level_only_signatures": len(level_classes),
            "level_class_size_distribution": {str(k): v for k, v in sorted(level_sizes.items())},
            "event_witness_signatures": len(event_classes),
            "event_class_size_distribution": {str(k): v for k, v in sorted(event_sizes.items())},
            "same_value_cells_with_three_level_indistinguishable_histories": sum(1 for k, v in level_classes.items() if len(v) == 3),
            "changed_value_cells_with_target_hidden_ambiguity": sum(1 for k, v in level_classes.items() if len(v) == 2),
        },
        "exact_counterexamples": {
            "held_state_vs_target_write_when_challenge_equals_pre_state": {
                "pre_state": 0,
                "challenge": 0,
                "history_a": {"source": "none", "commit": False, "final_level": 0},
                "history_b": {"source": "target", "commit": True, "final_level": 0},
                "level_observation_equal": True,
                "event_observation_equal": False
            },
            "target_vs_hidden_write_when_level_changes": {
                "pre_state": 0,
                "challenge": 1,
                "history_a": {"source": "target", "commit": True, "final_level": 1},
                "history_b": {"source": "hidden", "commit": True, "final_level": 1},
                "level_observation_equal": True,
                "writer_identity_equal": False
            }
        },
        "anti_current_protocol": protocol,
        "bounded_consequence": "With verified pre-state, q != pre-state, complete writer inventory, faithful target cut, isolated non-target writers and same-interface rescue, the baseline/cut/rescue level pattern establishes a current device-relative target-route contribution. Without q != pre-state or an event witness, a same-value level cannot establish a current write.",
        "limits": [
            "The enumeration concerns a finite binary hold-or-write abstraction, not a physical robot or human.",
            "A level change establishes that some timely write occurred, not which writer, unless A4D writer-completeness premises are independently satisfied.",
            "A commit/source tag is evidence only if physically bound to the post-arbitration event; a software label can be forged or misplaced.",
            "No complete K signature, RetBind, H_way, familiar mineness or consciousness status follows."
        ],
        "checks": {
            "twelve_histories": len(histories) == 12,
            "six_level_signatures": len(level_classes) == 6,
            "two_three_way_same_value_classes": level_sizes[3] == 2,
            "two_target_hidden_change_classes": level_sizes[2] == 2,
            "twelve_unique_event_witnesses": len(event_classes) == 12 and event_sizes[1] == 12,
            "six_protocol_cells": len(protocol) == 6,
            "anti_current_baseline_changes": all(x["final_level"] != x["pre_state"] for x in protocol if x["arm"] == "baseline"),
            "cut_holds_pre_state": all(x["final_level"] == x["pre_state"] for x in protocol if x["arm"] == "target_cut"),
            "rescue_restores_change": all(x["final_level"] != x["pre_state"] for x in protocol if x["arm"] == "same_interface_rescue")
        }
    }
    assert all(out["checks"].values())
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
