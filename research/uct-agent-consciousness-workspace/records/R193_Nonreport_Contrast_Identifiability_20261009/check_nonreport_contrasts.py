#!/usr/bin/env python3
"""Exact finite checks for R193's nonreport contrast-identifiability boundary.

This script enumerates every Boolean bridge on a four-bit toy domain.  It
checks only finite extensional facts about predeclared constraints.  It does
not measure a feeling, establish an actual installation, or test consciousness.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import defaultdict, deque
from pathlib import Path


FEATURES = ("actual_same_lineage_history", "actual_present_use", "positive_test", "positive_report")
STATES = tuple(itertools.product((0, 1), repeat=4))
STATE_TO_INDEX = {state: i for i, state in enumerate(STATES)}
BRIDGE_COUNT = 1 << len(STATES)


def value(mask: int, state: tuple[int, int, int, int]) -> int:
    return (mask >> STATE_TO_INDEX[state]) & 1


def invariant_to_epistemic_coordinates(mask: int) -> bool:
    for h, u in itertools.product((0, 1), repeat=2):
        vals = {value(mask, (h, u, e, r)) for e, r in itertools.product((0, 1), repeat=2)}
        if len(vals) != 1:
            return False
    return True


def contrast_edges() -> tuple[tuple[tuple[int, ...], tuple[int, ...], int], ...]:
    """Two difference constraints, instantiated for all E/R nuisance values."""
    edges = []
    for e, r in itertools.product((0, 1), repeat=2):
        edges.append(((0, 1, e, r), (1, 1, e, r), 1))
        edges.append(((1, 0, e, r), (1, 1, e, r), 1))
    return tuple(edges)


def baseline_edges() -> tuple[tuple[tuple[int, ...], tuple[int, ...], int], ...]:
    """Declare H=0,U=0/1 and H=1,U=0 as one negative-or-complement class."""
    edges = []
    for e, r in itertools.product((0, 1), repeat=2):
        edges.extend(
            [
                ((0, 0, e, r), (0, 1, e, r), 0),
                ((0, 0, e, r), (1, 0, e, r), 0),
            ]
        )
    return tuple(edges)


def satisfies_edges(mask: int, edges: tuple[tuple[tuple[int, ...], tuple[int, ...], int], ...]) -> bool:
    return all((value(mask, a) ^ value(mask, b)) == parity for a, b, parity in edges)


def signed_graph_count(edges: tuple[tuple[tuple[int, ...], tuple[int, ...], int], ...], anchors=()) -> dict:
    graph: dict[tuple[int, ...], list[tuple[tuple[int, ...], int]]] = defaultdict(list)
    for a, b, parity in edges:
        graph[a].append((b, parity))
        graph[b].append((a, parity))
    assignment: dict[tuple[int, ...], int] = {}
    components = []
    consistent = True
    anchored_components = 0
    anchors = dict(anchors)
    for root in STATES:
        if root in assignment:
            continue
        component = []
        assignment[root] = 0
        queue = deque([root])
        while queue:
            node = queue.popleft()
            component.append(node)
            for nxt, parity in graph[node]:
                expected = assignment[node] ^ parity
                if nxt in assignment:
                    consistent &= assignment[nxt] == expected
                else:
                    assignment[nxt] = expected
                    queue.append(nxt)
        oriented = []
        for state in component:
            if state in anchors:
                oriented.append(anchors[state] ^ assignment[state])
        if oriented:
            anchored_components += 1
            consistent &= len(set(oriented)) == 1
        components.append(component)
    count = 0 if not consistent else 2 ** (len(components) - anchored_components)
    return {
        "consistent": consistent,
        "components": len(components),
        "anchored_components": anchored_components,
        "predicted_bridge_count": count,
    }


def main() -> None:
    masks = range(BRIDGE_COUNT)
    nuisance_invariant = [mask for mask in masks if invariant_to_epistemic_coordinates(mask)]
    contrasts = contrast_edges()
    baselines = baseline_edges()
    contrast_selected = [mask for mask in nuisance_invariant if satisfies_edges(mask, contrasts)]
    baseline_selected = [mask for mask in contrast_selected if satisfies_edges(mask, baselines)]
    anchor_state = (1, 1, 0, 0)
    oriented = [mask for mask in baseline_selected if value(mask, anchor_state) == 1]

    conjunction_mask = 0
    complement_mask = 0
    for state in STATES:
        h, u, _e, _r = state
        conjunction_mask |= (h & u) << STATE_TO_INDEX[state]
        complement_mask |= (1 - (h & u)) << STATE_TO_INDEX[state]

    # The graph count is computed over all sixteen states.  E/R invariance is
    # represented by zero-parity edges inside each H/U fiber.
    invariance_edges = []
    for h, u in itertools.product((0, 1), repeat=2):
        root = (h, u, 0, 0)
        for e, r in itertools.product((0, 1), repeat=2):
            invariance_edges.append((root, (h, u, e, r), 0))
    graph_edges = tuple(invariance_edges) + contrasts + baselines
    graph_unoriented = signed_graph_count(graph_edges)
    graph_oriented = signed_graph_count(graph_edges, anchors=((anchor_state, 1),))

    checks = {
        "unconstrained_count_is_2_pow_16": BRIDGE_COUNT == 2**16,
        "test_and_report_invariance_leaves_16": len(nuisance_invariant) == 16,
        "two_predeclared_contrasts_leave_4": len(contrast_selected) == 4,
        "baseline_equivalence_leaves_complement_pair": len(baseline_selected) == 2,
        "remaining_pair_is_conjunction_and_complement": set(baseline_selected) == {conjunction_mask, complement_mask},
        "positive_polarity_anchor_selects_unique_conjunction": oriented == [conjunction_mask],
        "signed_graph_predicts_unoriented_count": graph_unoriented["predicted_bridge_count"] == 2,
        "signed_graph_predicts_oriented_count": graph_oriented["predicted_bridge_count"] == 1,
        "actual_use_and_positive_test_are_logically_independent": set(itertools.product((0, 1), repeat=2)) == {(0, 0), (0, 1), (1, 0), (1, 1)},
    }

    output = {
        "schema": "uct-r193-nonreport-contrast-check/1",
        "research_id": "R193-NCI-20261009",
        "domain": {
            "features": FEATURES,
            "state_count": len(STATES),
            "candidate_boolean_bridges": BRIDGE_COUNT,
            "actuality_note": "H and U are typed as actual same-instance relations; E and R are evidence/output coordinates, not experiential constituents.",
        },
        "constraint_ladder": [
            {"package": "none", "compatible_bridges": BRIDGE_COUNT},
            {"package": "E/R invariance", "compatible_bridges": len(nuisance_invariant)},
            {"package": "E/R invariance + H-at-U=1 and U-at-H=1 contrasts", "compatible_bridges": len(contrast_selected)},
            {"package": "previous + one baseline equivalence class", "compatible_bridges": len(baseline_selected)},
            {"package": "previous + positive-pole anchor at H=U=1", "compatible_bridges": len(oriented)},
        ],
        "signed_constraint_graph": {
            "unoriented": graph_unoriented,
            "oriented": graph_oriented,
            "standard_result": "For a consistent Boolean XOR/equality graph, compatible labelings equal 2^(components without an oriented anchor).",
        },
        "surviving_unoriented_functions": ["H AND U", "NOT(H AND U)"],
        "oriented_function": "H AND U",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation_boundary": (
            "The unique oriented truth table is unique only relative to the declared anchor. "
            "The enumeration does not show that the positive pole is familiar mineness, that any proxy is valid, "
            "or that H/U/E/R are actually instantiated in a particular system."
        ),
    }
    canonical = json.dumps(output, sort_keys=True, separators=(",", ":")).encode()
    output["content_sha256_without_this_field"] = hashlib.sha256(canonical).hexdigest()
    target = Path(__file__).with_name("EXACT_RESULTS.json")
    target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_checks_pass": output["all_checks_pass"], "counts": [x["compatible_bridges"] for x in output["constraint_ladder"]]}))
    if not output["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
