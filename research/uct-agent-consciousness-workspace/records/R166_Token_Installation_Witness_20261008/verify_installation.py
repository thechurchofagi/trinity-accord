#!/usr/bin/env python3
"""Exact bounded checks for R166's two obstructions and conjunctive contract."""

from itertools import product, permutations
from pathlib import Path
import hashlib
import json


HERE = Path(__file__).resolve().parent


def population_checks():
    checked = 0
    witnesses = 0
    for n in range(2, 7):
        for vector in product((0, 1), repeat=n):
            if len(set(vector)) == 1:
                continue
            checked += 1
            base = (sum(vector), tuple(sorted(vector)))
            changed = False
            for perm in set(permutations(vector)):
                assert (sum(perm), tuple(sorted(perm))) == base
                if perm[0] != vector[0]:
                    changed = True
                    break
            assert changed
            witnesses += 1
    return {"nonconstant_vectors_checked": checked, "named_token_swap_witnesses": witnesses}


def path_model(b, do_r=None, do_k=None):
    r = b if do_r is None else do_r
    k = r if do_k is None else do_k
    u = k
    return (r, k, u)


def bypass_model(b, do_r=None, do_k=None):
    r = b if do_r is None else do_r
    k = r if do_k is None else do_k
    u = r
    return (r, k, u)


def finite_trace_checks():
    natural_and_anchor = []
    mediator_discriminations = []
    for b in (0, 1):
        assert path_model(b) == bypass_model(b)
        natural_and_anchor.append({"b": b, "do_r": None, "tuple": path_model(b)})
        for x in (0, 1):
            assert path_model(b, do_r=x) == bypass_model(b, do_r=x)
            natural_and_anchor.append({"b": b, "do_r": x, "tuple": path_model(b, do_r=x)})
            if x != b:
                pm = path_model(b, do_k=x)
                bm = bypass_model(b, do_k=x)
                assert pm != bm and pm[2] != bm[2]
                mediator_discriminations.append({"b": b, "do_k": x, "path": pm, "bypass": bm})
    assert len(mediator_discriminations) == 2
    return {
        "indistinguishable_natural_or_anchor_cases": len(natural_and_anchor),
        "mediator_discriminations": mediator_discriminations,
    }


def conjunction_checks():
    clauses = ("W1", "W2", "W3", "W4", "W5", "W6")
    cases = []
    for values in product((False, True), repeat=len(clauses)):
        supported = all(values)
        assert supported == (sum(values) == len(clauses))
        cases.append({"true_clauses": sum(values), "supported": supported})
    assert sum(case["supported"] for case in cases) == 1
    return {"boolean_assignments": len(cases), "supporting_assignments": 1}


result = {
    "schema": "UCT_R166_EXACT_CHECKS/v1",
    "population_token_obstruction": population_checks(),
    "finite_trace_obstruction": finite_trace_checks(),
    "installation_contract_conjunction": conjunction_checks(),
    "interpretation": [
        "Permutation-invariant population summaries do not identify a named token property.",
        "Natural and anchor-intervention traces do not distinguish an operative k-mediated path from a bypass.",
        "Mediator intervention distinguishes the two declared models, but only relative to their variables and intervention semantics.",
        "The witness contract is an all-of sufficient package; a missing clause never defaults to no experience."
    ],
    "claim_limits": {
        "actual_data": False,
        "actual_apparatus": False,
        "complete_mechanism_identified": False,
        "B_min_validated": False,
        "basal_experience_gate": False
    }
}

out = HERE / "EXACT_CHECKS.json"
out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({
    "status": "PASS",
    "output": out.name,
    "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
    "population_cases": result["population_token_obstruction"]["nonconstant_vectors_checked"],
    "interface_cases": result["finite_trace_obstruction"]["indistinguishable_natural_or_anchor_cases"],
    "conjunction_cases": result["installation_contract_conjunction"]["boolean_assignments"]
}, indent=2))
