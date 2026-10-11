#!/usr/bin/env python3
"""Exact finite audit for the A4R three-link anchor-route certificate."""

from itertools import product
import json


def world(bits):
    s, c, w, bs, bc, bw = bits
    observed = (int(bool(s or bs)), int(bool(c or bc)), int(bool(w or bw)))
    actual = (s, c, w)
    return {
        "sensor_provenance": s,
        "consumer_use": c,
        "actuator_provenance": w,
        "sensor_bypass": bs,
        "consumer_bypass": bc,
        "actuator_bypass": bw,
        "actual_signature": list(actual),
        "observed_local_signature": list(observed),
        "actual_conjunction": int(all(actual)),
        "observed_end_to_end_success": int(all(observed)),
    }


worlds = [world(bits) for bits in product((0, 1), repeat=6)]
target = [x for x in worlds if x["observed_local_signature"] == [1, 1, 1]]
closed = [x for x in target if not any((x["sensor_bypass"], x["consumer_bypass"], x["actuator_bypass"]))]
actual_patterns = sorted({tuple(x["actual_signature"]) for x in target})

named = {
    "physical_sample_not_used": next(x for x in target if x["actual_signature"] == [1, 0, 1] and x["consumer_bypass"] == 1),
    "used_sample_not_physical_anchor": next(x for x in target if x["actual_signature"] == [0, 1, 1] and x["sensor_bypass"] == 1),
    "command_not_current_plant_write": next(x for x in target if x["actual_signature"] == [1, 1, 0] and x["actuator_bypass"] == 1),
    "fully_bypassed_twin": next(x for x in target if x["actual_signature"] == [0, 0, 0] and x["observed_local_signature"] == [1, 1, 1]),
}

result = {
    "schema": "uct-a4r-three-link-exact/1",
    "world_count": len(worlds),
    "target_observed_signature": [1, 1, 1],
    "open_target_fibre_worlds": len(target),
    "actual_link_patterns_in_open_target_fibre": [list(x) for x in actual_patterns],
    "open_target_fibre_contains_all_eight_actual_patterns": len(actual_patterns) == 8,
    "closed_target_fibre_worlds": len(closed),
    "closed_target_actual_signature": closed[0]["actual_signature"] if len(closed) == 1 else None,
    "closed_target_identifies_full_conjunction": len(closed) == 1 and closed[0]["actual_conjunction"] == 1,
    "named_counterexamples": named,
    "phenomenal_assignments": 0,
    "formal_graph_delta": {"nodes": 0, "rules": 0, "context_links": 0},
}

assert result["world_count"] == 64
assert result["open_target_fibre_worlds"] == 27
assert result["open_target_fibre_contains_all_eight_actual_patterns"]
assert result["closed_target_fibre_worlds"] == 1
assert result["closed_target_actual_signature"] == [1, 1, 1]
assert result["closed_target_identifies_full_conjunction"]
print(json.dumps(result, separators=(",", ":"), sort_keys=True))
