#!/usr/bin/env python3
"""Exact finite checks for A3O. Elementary partition mathematics; no novelty claim."""
import itertools, json
from pathlib import Path

def partitions(xs):
    if not xs:
        yield []
        return
    first, *rest = xs
    for p in partitions(rest):
        yield [{first}] + [set(b) for b in p]
        for i in range(len(p)):
            q = [set(b) for b in p]
            q[i].add(first)
            yield q

def retained(partition, current, past):
    block = next(b for b in partition if current in b)
    return int(bool(block & set(past)))

X = ["past", "current", "other"]
P = ["past"]
parts = list(partitions(X))
vals = [retained(p, "current", P) for p in parts]

# Fixed-grain organizational witnesses. L_sel is selector topology, not RT/error.
witnesses = [
  {"family":"mapping", "cell":"R1_L0", "R":1, "L_sel":0,
   "route":"same retained effector route", "selector":"two incompatible live mappings plus resolution"},
  {"family":"mapping", "cell":"R0_L1", "R":0, "L_sel":1,
   "route":"new fine-grained effector route", "selector":"retained compiler emits one eligible route"},
  {"family":"sequence", "cell":"R1_L0", "R":1, "L_sel":0,
   "route":"same retained action chunk", "selector":"two live boundary parses plus resolution"},
  {"family":"sequence", "cell":"R0_L1", "R":0, "L_sel":1,
   "route":"new fine-grained sequence", "selector":"deterministic grammar emits one eligible sequence"},
]
assert {w["R"] for w in witnesses} == {0,1}
assert {w["L_sel"] for w in witnesses} == {0,1}
assert all(w["R"] != w["L_sel"] for w in witnesses)
assert {w["family"] for w in witnesses} == {"mapping","sequence"}
assert set(vals) == {0,1}

out = {
  "schema":"A3O_EXACT_RESULTS/v1",
  "partition_count":len(parts),
  "retained_zero_partitions":vals.count(0),
  "retained_one_partitions":vals.count(1),
  "same_physical_history_supports_both_R_values_when_grain_varies":True,
  "fixed_grain_off_diagonal_witnesses":witnesses,
  "checks":{"partition_variation":True,"two_families":True,"all_witnesses_off_diagonal":True},
  "limits":["logical/organizational witnesses, not a human installation", "selector topology is not identified by latency or error", "no J_H or H value is generated"]
}
Path(__file__).with_name("EXACT_RESULTS.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
