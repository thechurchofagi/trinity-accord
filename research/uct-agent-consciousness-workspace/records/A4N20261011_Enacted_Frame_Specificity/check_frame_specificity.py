#!/usr/bin/env python3
"""Exact finite checks for A4N. No phenomenal values are represented."""

from itertools import product
import json
from pathlib import Path


def frame_bind(anchor: int, remap: int, perturb_dep: int, same_route: int, ordered: int) -> int:
    return int(all((anchor, remap, perturb_dep, same_route, ordered)))


worlds = []
for member, anchor, remap, perturb_dep, same_route, ordered in product((0, 1), repeat=6):
    worlds.append(
        {
            "member": member,
            "anchor": anchor,
            "remap": remap,
            "perturbation_dependence": perturb_dep,
            "same_route_use": same_route,
            "ordered": ordered,
            "enacted_frame_bind": frame_bind(anchor, remap, perturb_dep, same_route, ordered),
            "coupled_form": 1,
            "retained_use": 1,
            "present_fit": 1,
            "output": 1,
            "report_code": 1,
        }
    )

square = [
    {"case": "native_limb", "member": 1, "anchor": 1, "remap": 1, "perturbation_dependence": 1, "same_route_use": 1, "ordered": 1},
    {"case": "incorporated_tool", "member": 0, "anchor": 1, "remap": 1, "perturbation_dependence": 1, "same_route_use": 1, "ordered": 1},
    {"case": "external_tool", "member": 0, "anchor": 0, "remap": 0, "perturbation_dependence": 0, "same_route_use": 0, "ordered": 1},
    {"case": "anatomical_label_only", "member": 1, "anchor": 0, "remap": 0, "perturbation_dependence": 0, "same_route_use": 0, "ordered": 1},
]
for row in square:
    row["enacted_frame_bind"] = frame_bind(row["anchor"], row["remap"], row["perturbation_dependence"], row["same_route_use"], row["ordered"])
    row.update({"coupled_form": 1, "retained_use": 1, "present_fit": 1, "output": 1, "report_code": 1})

assert {(r["member"], r["enacted_frame_bind"]) for r in square} == {(0, 0), (0, 1), (1, 0), (1, 1)}
assert len({(r["coupled_form"], r["retained_use"], r["present_fit"], r["output"], r["report_code"]) for r in square}) == 1

member_fibres = {
    str(m): sorted({r["enacted_frame_bind"] for r in square if r["member"] == m}) for m in (0, 1)
}
frame_fibres = {
    str(e): sorted({r["member"] for r in square if r["enacted_frame_bind"] == e}) for e in (0, 1)
}
assert all(v == [0, 1] for v in member_fibres.values())
assert all(v == [0, 1] for v in frame_fibres.values())

# Conjunct audit: every missing primitive blocks the relation, and all five suffice by definition.
single_failures = []
keys = ["anchor", "remap", "perturbation_dependence", "same_route_use", "ordered"]
for key in keys:
    vals = {k: 1 for k in keys}
    vals[key] = 0
    value = frame_bind(vals["anchor"], vals["remap"], vals["perturbation_dependence"], vals["same_route_use"], vals["ordered"])
    assert value == 0
    single_failures.append({"missing": key, "enacted_frame_bind": value})
assert frame_bind(1, 1, 1, 1, 1) == 1

result = {
    "schema": "a4n-frame-specificity-results/1",
    "status": "PASS_BOUNDED_LOGICAL_CHECK_NO_PHENOMENAL_ASSIGNMENTS",
    "world_count": len(worlds),
    "fixed_view": {"coupled_form": 1, "retained_use": 1, "present_fit": 1, "output": 1, "report_code": 1},
    "counterexample_square": square,
    "member_fibres_over_frame": member_fibres,
    "frame_fibres_over_member": frame_fibres,
    "member_recovers_frame": False,
    "frame_recovers_member": False,
    "single_conjunct_failures": single_failures,
    "phenomenal_assignments": 0,
    "physical_installations": 0,
    "interpretation": "Organism membership and enacted-frame binding are logically independent in the declared model; toolhood alone cannot witness absence of frame binding.",
}

out = Path(__file__).with_name("EXACT_RESULTS.json")
out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"status": result["status"], "world_count": len(worlds), "square": [(r["member"], r["enacted_frame_bind"]) for r in square]}, sort_keys=True))

