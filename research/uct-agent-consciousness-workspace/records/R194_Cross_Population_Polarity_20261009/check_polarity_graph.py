#!/usr/bin/env python3
"""Exact finite checks for relative versus absolute polarity in R194."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict, deque
from pathlib import Path


NODES = ("Z", "A1", "A2", "B1", "B2", "C1", "C2")
# A connected signed tree: within-population marker reversals and cross-population
# correspondences.  Z is the *unoriented* latent structural coordinate.
TREE = (
    ("Z", "A1", 0, "observed latent/marker partition correspondence"),
    ("A1", "A2", 1, "known marker reversal in population A"),
    ("A1", "B1", 0, "cross-population marker-1 alignment"),
    ("B1", "B2", 1, "known marker reversal in population B"),
    ("B1", "C1", 1, "known reversed marker-1 coding in population C"),
    ("C1", "C2", 1, "known marker reversal in population C"),
)


def satisfies(bits: dict[str, int], edges: tuple[tuple[str, str, int, str], ...]) -> bool:
    return all((bits[a] ^ bits[b]) == parity for a, b, parity, _ in edges)


def solutions(edges: tuple[tuple[str, str, int, str], ...], anchors: dict[str, int] | None = None) -> list[dict[str, int]]:
    anchors = anchors or {}
    out = []
    for values in itertools.product((0, 1), repeat=len(NODES)):
        bits = dict(zip(NODES, values))
        if all(bits[k] == v for k, v in anchors.items()) and satisfies(bits, edges):
            out.append(bits)
    return out


def component_count(edges: tuple[tuple[str, str, int, str], ...]) -> int:
    graph: dict[str, set[str]] = defaultdict(set)
    for a, b, _, _ in edges:
        graph[a].add(b)
        graph[b].add(a)
    seen: set[str] = set()
    count = 0
    for node in NODES:
        if node in seen:
            continue
        count += 1
        queue = deque([node])
        seen.add(node)
        while queue:
            cur = queue.popleft()
            for nxt in graph[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
    return count


def canonical(solution: dict[str, int]) -> tuple[int, ...]:
    return tuple(solution[n] for n in NODES)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    relative = solutions(TREE)
    marker_anchored = solutions(TREE, {"A1": 1})
    semantic_anchored = solutions(TREE, {"Z": 1})
    complement_pair = (
        len(relative) == 2
        and all(a ^ b == 1 for a, b in zip(canonical(relative[0]), canonical(relative[1])))
    )

    # Remove the two cross-population edges: three unanchored components remain.
    disconnected = tuple(edge for i, edge in enumerate(TREE) if i not in (2, 4))
    disconnected_solutions = solutions(disconnected)

    # A consistent extra cycle leaves the global complement pair; the opposite
    # parity falsifies the declared parity model rather than orienting it.
    consistent_cycle = TREE + (("A2", "C2", 1, "redundant consistent cycle"),)
    inconsistent_cycle = TREE + (("A2", "C2", 0, "deliberately inconsistent cycle"),)
    consistent_solutions = solutions(consistent_cycle)
    inconsistent_solutions = solutions(inconsistent_cycle)

    # Exhaust every parity assignment on the same seven-node tree.  Each of the
    # 2^6 signed trees must admit exactly the two globally complemented labellings.
    tree_parity_counts = []
    for parities in itertools.product((0, 1), repeat=len(TREE)):
        edges = tuple((a, b, p, label) for (a, b, _, label), p in zip(TREE, parities))
        tree_parity_counts.append(len(solutions(edges)))

    checks = {
        "connected_relative_constraints_leave_two_solutions": len(relative) == 2,
        "remaining_solutions_are_global_complements": complement_pair,
        "marker_convention_anchor_leaves_one_numeric_solution": len(marker_anchored) == 1,
        "independent_target_anchor_leaves_one_solution": len(semantic_anchored) == 1,
        "three_unanchored_components_leave_eight_solutions": component_count(disconnected) == 3 and len(disconnected_solutions) == 8,
        "consistent_cycle_does_not_orient": len(consistent_solutions) == 2,
        "inconsistent_cycle_falsifies_model": len(inconsistent_solutions) == 0,
        "all_64_signed_tree_instances_have_two_solutions": len(tree_parity_counts) == 64 and set(tree_parity_counts) == {2},
    }

    result = {
        "schema": "uct-r194-cross-population-polarity/1",
        "domain": {
            "nodes": list(NODES),
            "interpretation": "Z is an unoriented latent structural coordinate; A1..C2 are marker-channel polarities across three populations and two markers.",
            "assignments_enumerated_per_instance": 2 ** len(NODES),
            "tree_parity_instances_exhausted": 2 ** len(TREE),
            "total_assignment_checks_for_tree_family": (2 ** len(NODES)) * (2 ** len(TREE)),
        },
        "declared_tree_edges": [
            {"a": a, "b": b, "xor": p, "meaning": meaning} for a, b, p, meaning in TREE
        ],
        "counts": {
            "relative_alignment_only": len(relative),
            "plus_marker_convention_anchor_A1_equals_1": len(marker_anchored),
            "plus_independent_target_anchor_Z_equals_1": len(semantic_anchored),
            "three_disconnected_unanchored_components": len(disconnected_solutions),
            "plus_consistent_cycle": len(consistent_solutions),
            "plus_inconsistent_cycle": len(inconsistent_solutions),
        },
        "relative_solutions": relative,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretive_boundary": (
            "The marker anchor fixes a numeric coding convention but does not by itself warrant the name familiar mineness. "
            "Only an independently target-directed anchor could orient the phenomenal interpretation, and its warrant is the open bridge."
        ),
        "claim_scope": (
            "Exact for finite binary signed constraints invariant under simultaneous global complement. "
            "Not a claim that every future evidence class is complement-invariant."
        ),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(json.dumps({"all_checks_pass": result["all_checks_pass"], "counts": result["counts"], "sha256": digest}))
    if not result["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
