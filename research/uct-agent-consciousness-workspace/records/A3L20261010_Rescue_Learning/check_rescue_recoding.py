"""Finite illustration of inherited R177, not a neural learning simulation."""
import itertools
import json
from pathlib import Path

rows = []
for c, k, theta in itertools.product((0, 1), repeat=3):
    z = c ^ k
    y = z ^ theta
    rows.append(dict(c=c, k=k, theta=theta, port=z, output=y, success=y == c))
learning = []
for c in (0, 1):
    z = c ^ 1
    learned_theta = z ^ c
    future = [{"c": x, "y": (x ^ 1) ^ learned_theta} for x in (0, 1)]
    assert all(x["c"] == x["y"] for x in future)
    learning.append(dict(training_c=c, training_z=z, learned_theta=learned_theta, future=future))
checks = {
    "baseline_success": all(r["success"] for r in rows if r["k"] == r["theta"] == 0),
    "uncompensated_inversion_fails": all(not r["success"] for r in rows if r["k"] == 1 and r["theta"] == 0),
    "compensated_inversion_success": all(r["success"] for r in rows if r["k"] == r["theta"] == 1),
    "successful_code_and_reader_differ": all((c ^ 0) != (c ^ 1) for c in (0, 1)),
    "no_decoder_recovers_constant_code": all(not all(d[0] == c for c in (0, 1)) for d in itertools.product((0, 1), repeat=2)),
}
assert all(checks.values())
result = dict(schema="uct-a3l-finite-illustration/1", rows=rows, toy_supervised_updates=learning,
              checks=checks, attribution="R177 compensated-recoding theorem; standard composition",
              evidence_level="EXACT_FINITE_MODEL_ONLY", neural_algorithm_claim=False, H_assignment=None)
Path(__file__).with_name("EXACT_RESULTS.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(dict(rows=len(rows), updates=len(learning), all_checks_pass=True, H_assignment=None)))
