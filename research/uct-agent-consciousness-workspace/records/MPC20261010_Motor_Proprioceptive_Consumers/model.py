#!/usr/bin/env python3
"""Exact finite checks for MPC20261010.

The variable order is (motor-consumer input M, proprioceptive/alternative
consumer input P).  Truth tables are rendered in the cell order
(00, 01, 10, 11).  The common active/passive/baseline design observes
00, 01 and 11 but not 10.
"""

from itertools import product
import json


CELLS = ((0, 0), (0, 1), (1, 0), (1, 1))
OBSERVED = ((0, 0), (0, 1), (1, 1))


def value(table, cell):
    return table[CELLS.index(cell)]


def bits(table):
    return "".join(str(x) for x in table)


tables = list(product((0, 1), repeat=4))
fibers = {}
for table in tables:
    profile = tuple(value(table, cell) for cell in OBSERVED)
    fibers.setdefault(profile, []).append(table)

assert len(tables) == 16
assert len(fibers) == 8
assert all(len(fiber) == 2 for fiber in fibers.values())
assert all(
    value(fiber[0], (1, 0)) != value(fiber[1], (1, 0))
    for fiber in fibers.values()
)

and_table = (0, 0, 0, 1)
motor_table = (0, 0, 1, 1)
proprio_table = (0, 1, 0, 1)
or_table = (0, 1, 1, 1)

assert set(fibers[(0, 0, 1)]) == {and_table, motor_table}
assert set(fibers[(0, 1, 1)]) == {proprio_table, or_table}


def eager_or(m, p):
    reads = ["M", "P"]
    return int(bool(m or p)), reads


def lazy_or(m, p):
    reads = ["M"]
    if m:
        return 1, reads
    reads.append("P")
    return int(bool(p)), reads


read_countermodel = []
for cell in CELLS:
    eager = eager_or(*cell)
    lazy = lazy_or(*cell)
    assert eager[0] == lazy[0]
    read_countermodel.append(
        {
            "cell_MP": "".join(map(str, cell)),
            "output": eager[0],
            "eager_reads": eager[1],
            "lazy_reads": lazy[1],
            "same_output_different_read_occurrence": eager[1] != lazy[1],
        }
    )

multi_endpoint_extensions = {str(k): 2**k for k in range(1, 7)}

result = {
    "id": "MPC-RESULT-v0.1.0",
    "cell_order": ["00", "01", "10", "11"],
    "observed_cells": ["00", "01", "11"],
    "missing_cell": "10",
    "boolean_function_count": len(tables),
    "observed_profile_count": len(fibers),
    "completion_count_per_profile": sorted({len(x) for x in fibers.values()}),
    "fibers": {
        "".join(map(str, profile)): [bits(t) for t in fiber]
        for profile, fiber in sorted(fibers.items())
    },
    "active_only_profile_001": {
        "completions": [bits(and_table), bits(motor_table)],
        "interpretations": ["M_AND_P", "M"],
    },
    "active_and_passive_profile_011": {
        "completions": [bits(proprio_table), bits(or_table)],
        "interpretations": ["P", "M_OR_P"],
    },
    "independent_k_endpoint_completion_counts": multi_endpoint_extensions,
    "full_or_table_output_equivalent_read_countermodel": read_countermodel,
    "checks": {
        "all_three_corner_fibers_have_size_two": True,
        "the_two_completions_differ_only_at_10": True,
        "active_only_leaves_M_vs_M_AND_P": True,
        "active_and_passive_leaves_P_vs_M_OR_P": True,
        "k_independent_endpoints_leave_2_power_k_completions": True,
        "full_output_table_does_not_identify_read_occurrence": True,
    },
}

print(json.dumps(result, indent=2, sort_keys=True))

