#!/usr/bin/env python3
import itertools
import json
from pathlib import Path


def between(order, a, b, c):
    pos = {x: i for i, x in enumerate(order)}
    return (pos[a] < pos[b] < pos[c]) or (pos[c] < pos[b] < pos[a])


def betweenness_maps(n):
    xs = tuple(range(n))
    triples = [(a, b, c) for a, b, c in itertools.permutations(xs, 3)]
    out = []
    for p in itertools.permutations(xs):
        if all(between(xs, a, b, c) == between(xs, p[a], p[b], p[c]) for a, b, c in triples):
            out.append(p)
    return out


def main():
    h4 = betweenness_maps(4)
    h5 = betweenness_maps(5)
    inc4, dec4 = tuple(range(4)), tuple(reversed(range(4)))
    checks = []
    def ck(name, value):
        assert value, name
        checks.append(name)
    ck("chain4_exactly_two_maps", set(h4) == {inc4, dec4})
    ck("chain5_exactly_two_maps", set(h5) == {tuple(range(5)), tuple(reversed(range(5)))})
    endpoint = [p for p in h4 if p[0] == 0 and p[3] == 3]
    ck("oriented_endpoints_unique", endpoint == [inc4])
    ck("held_out_middle_order_forced", all(p[1] < p[2] for p in endpoint))
    ck("reversal_predicts_opposite", dec4[2] < dec4[1])
    ck("unanchored_maps_disagree", {p[1] < p[2] for p in h4} == {False, True})
    center = [p for p in h5 if p[2] == 2]
    ck("central_anchor_ambiguous", len(center) == 2)
    ck("central_anchor_target_disagrees", {p[1] < p[3] for p in center} == {False, True})
    incompatible = [p for p in h4 if p[0] == 0 and p[1] == 3]
    ck("incompatible_anchors_empty", incompatible == [])
    rows = list(itertools.product([0, 1], repeat=3))
    six = [r for r in rows if not r[1] or r[0]]
    ck("baseline_domain_has_six_rows", len(six) == 6)
    ck("agency_implies_availability", all((not g) or a for a, g, _ in six))
    ck("retentive_bit_crosses_each_admitted_AG", all({r for a, g, r in six if (a, g) == ag} == {0, 1} for ag in {(0,0),(1,0),(1,1)}))
    result = {
        "status": "EXACT_FINITE_MODEL_ONLY",
        "checks": checks,
        "checks_passed": len(checks),
        "chain4_maps": [list(p) for p in h4],
        "endpoint_anchored_maps": [list(p) for p in endpoint],
        "chain5_center_anchored_maps": [list(p) for p in center],
        "baseline_admitted_rows": [list(r) for r in six],
        "limits": ["No actual human or hardware instance", "No phenomenal structure inferred from enumeration", "No closure of B_order or reviewer findings"]
    }
    Path(__file__).with_name("MODEL_RESULTS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks_passed": len(checks), "chain4_maps": result["chain4_maps"]}))


if __name__ == "__main__":
    main()
