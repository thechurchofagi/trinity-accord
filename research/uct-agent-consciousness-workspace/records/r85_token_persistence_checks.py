#!/usr/bin/env python3
"""Exact checks for R85's token-persistence distinctions.

This script audits logical relations and declared scenario vectors. It does not
query a model or measure consciousness, identity experience, fear, or welfare.
"""

from itertools import combinations
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NODES = ("p_prebranch", "x_clone", "y_clone")
AXES = (
    "C_causal_lineage",
    "B_unique_nonbranching_bridge",
    "S_declared_structure_type",
    "M_memory_history",
    "G_task_service",
)


def set_partitions(items):
    """Yield every set partition as a tuple of frozenset blocks."""
    if not items:
        yield ()
        return
    first, *rest = items
    for partition in set_partitions(rest):
        yield (frozenset((first,)),) + partition
        for i in range(len(partition)):
            yield partition[:i] + (partition[i] | frozenset((first,)),) + partition[i + 1 :]


def related(partition, a, b):
    return any(a in block and b in block for block in partition)


def main():
    # Equivalence relations on three stages are exactly the five set partitions.
    partitions = list(set_partitions(list(NODES)))
    both_descendants_identical = [
        p for p in partitions if related(p, NODES[0], NODES[1]) and related(p, NODES[0], NODES[2])
    ]
    branching_identity_with_distinct_descendants = [
        p
        for p in both_descendants_identical
        if not related(p, NODES[1], NODES[2])
    ]

    # Values are declared comparison features, not observations of any real AI.
    scenarios = {
        "continuous_adaptation": (1, 1, 0, 1, 1),
        "single_checkpoint_resume_storage_in_boundary": (1, 1, 1, 1, 1),
        "each_of_two_checkpoint_clones": (1, 0, 1, 1, 1),
        "independent_same_type_instance": (0, 0, 1, 0, 0),
        "memory_transplant_source_also_continues": (1, 0, 0, 1, 0),
        "task_successor_without_memory": (1, 0, 0, 0, 1),
        "continuous_thread_with_amnesia": (1, 1, 0, 0, 1),
        "unrelated_same_type_task_service": (0, 0, 1, 0, 1),
        "unrelated_replacement_continues_task": (0, 0, 0, 0, 1),
    }
    patterns = {
        axis: tuple(row[i] for row in scenarios.values()) for i, axis in enumerate(AXES)
    }
    distinct_axis_pairs = {
        f"{a}__vs__{b}": patterns[a] != patterns[b] for a, b in combinations(AXES, 2)
    }

    # A proposed strict-thread surrogate: lineage plus a unique nonbranching bridge.
    strict_thread = {name: bool(row[0] and row[1]) for name, row in scenarios.items()}

    # Same physical pause/resume can be classified differently if the process
    # boundary excludes or includes the causally persistent storage carrier.
    pause_boundary_audit = {
        "active_episode_only": {
            "causal_bridge_inside_boundary": False,
            "strict_thread": False,
        },
        "storage_inclusive_system": {
            "causal_bridge_inside_boundary": True,
            "strict_thread": True,
        },
    }

    # Static type and copied memory are matched, while branch structure differs.
    type_only_counterexample = {
        "single_resume": {"same_type": True, "same_memory": True, "strict_thread": True},
        "parallel_clone": {"same_type": True, "same_memory": True, "strict_thread": False},
    }

    assertions = {
        "five_equivalence_relations_on_three_nodes": len(partitions) == 5,
        "both_descendants_identity_forces_one_universal_block": len(both_descendants_identical) == 1,
        "no_equivalence_relation_makes_both_descendants_identical_to_parent_but_distinct_from_each_other": len(branching_identity_with_distinct_descendants) == 0,
        "all_five_persistence_axes_have_distinct_scenario_patterns": len(set(patterns.values())) == len(AXES),
        "every_axis_pair_has_a_counterexample": all(distinct_axis_pairs.values()),
        "single_resume_and_clone_match_static_type": type_only_counterexample["single_resume"]["same_type"] == type_only_counterexample["parallel_clone"]["same_type"],
        "single_resume_and_clone_match_memory": type_only_counterexample["single_resume"]["same_memory"] == type_only_counterexample["parallel_clone"]["same_memory"],
        "static_type_and_memory_do_not_fix_strict_thread": type_only_counterexample["single_resume"]["strict_thread"] != type_only_counterexample["parallel_clone"]["strict_thread"],
        "pause_classification_changes_with_declared_boundary": pause_boundary_audit["active_episode_only"]["strict_thread"] != pause_boundary_audit["storage_inclusive_system"]["strict_thread"],
    }
    assert all(assertions.values()), assertions

    result = {
        "status": "formal_exact_check_only_not_identity_or_subjective_measurement",
        "axes": AXES,
        "equivalence_relation_audit": {
            "node_count": len(NODES),
            "partition_count": len(partitions),
            "both_descendants_identical_to_parent_count": len(both_descendants_identical),
            "both_identical_to_parent_while_mutually_distinct_count": len(branching_identity_with_distinct_descendants),
            "partitions": [[sorted(block) for block in p] for p in partitions],
        },
        "scenario_vectors": {name: dict(zip(AXES, row)) for name, row in scenarios.items()},
        "axis_patterns": patterns,
        "strict_thread_surrogate": strict_thread,
        "pause_boundary_audit": pause_boundary_audit,
        "type_and_memory_counterexample": type_only_counterexample,
        "assertions": assertions,
        "limits": [
            "Strict-thread continuity is a declared operational surrogate, not a theorem that fixes metaphysical identity.",
            "Causal lineage, structure type, memory and task continuity can branch and are not numerical identity.",
            "Pause/resume classification depends on whether a persistent carrier is inside the process boundary.",
            "No scenario row measures experience, subjecthood, fear or current-system preference.",
        ],
    }

    (ROOT / "R85_Token_Persistence_Results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (ROOT / "R85_Persistence_Vector_Table.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("scenario",) + AXES + ("N_star_strict_thread_surrogate",))
        for name, row in scenarios.items():
            writer.writerow((name,) + row + (int(strict_thread[name]),))

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
