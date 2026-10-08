"""R174 exact route-signature checks; not neural data or a C1/B_order test."""
from fractions import Fraction as F
from pathlib import Path
import json


def route(name, delta, beta, s, q_clamp=None):
    if name == "S":
        q = delta - beta if q_clamp is None else q_clamp
        return {"q": q, "z": q, "u": q / s}
    if name == "C":
        q = delta if q_clamp is None else q_clamp
        return {"q": q, "z": q - beta, "u": q / s}
    if name == "H":
        q = delta if q_clamp is None else q_clamp
        return {"q": q, "z": q - beta, "u": (q - beta) / s}
    raise ValueError(name)


def difference(after, before):
    return tuple(after[k] - before[k] for k in ("z", "u"))


def signature(name, delta, beta, s, c, qbar):
    normal = difference(route(name, delta, beta + c, s), route(name, delta, beta, s))
    clamped = difference(
        route(name, delta, beta + c, s, q_clamp=qbar),
        route(name, delta, beta, s, q_clamp=qbar),
    )
    return normal + clamped


def serial(value):
    if isinstance(value, F):
        return {"exact": str(value), "decimal": float(value)}
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def run():
    delta, beta, s, c, qbar = F(20), F(90), F(100), F(10), F(-5)
    checks = []

    def check(name, truth, scope):
        assert truth, name
        checks.append({"name": name, "pass": True, "scope": scope})

    baseline = {name: route(name, delta, beta, s) for name in "SCH"}
    check(
        "baseline_report_drive_equivalence",
        len({v["z"] for v in baseline.values()}) == 1,
        "Exact stipulated S/C/H class; z is a physical decision drive, not experience.",
    )
    check(
        "previous_two_route_contrast_has_hidden_bypass",
        baseline["S"]["u"] != baseline["C"]["u"] and baseline["S"]["u"] == baseline["H"]["u"],
        "Shows why the S/C nonreport contrast does not identify unrestricted routes.",
    )
    signatures = {name: signature(name, delta, beta, s, c, qbar) for name in "SCH"}
    expected = {
        "S": (-c, -c / s, F(0), F(0)),
        "C": (-c, F(0), -c, F(0)),
        "H": (-c, -c / s, -c, -c / s),
    }
    check(
        "exact_signature_formula",
        signatures == expected,
        "Same binding, nonzero c, positive s, faithful source perturbation and q clamp.",
    )
    check(
        "three_rivals_pairwise_separated",
        len(set(signatures.values())) == 3,
        "Identification is relative to the predeclared S/C/H rival class.",
    )

    tested = ("baseline", "beta_shift", "q_clamp_beta_shift")
    hidden_gate = {x: F(0) for x in tested}
    hidden_gate["untested_context"] = F(1)
    check(
        "hidden_bypass_silent_on_finite_tests",
        all(hidden_gate[x] == 0 for x in tested) and hidden_gate["untested_context"] == 1,
        "Finite tested support cannot establish unrestricted absence of a context-gated bypass.",
    )

    for d in map(F, (-50, 0, 20, 100)):
        for b in map(F, (-30, 0, 50, 100)):
            sig = {name: signature(name, d, b, s, c, qbar) for name in "SCH"}
            check(
                f"pairwise_signature_{d}_{b}",
                len(set(sig.values())) == 3,
                "Boundary regression only; general separation follows from c!=0 and s>0.",
            )

    return serial({
        "status": "EXACT_STIPULATED_ROUTE_MODEL_ONLY",
        "parameters": {"delta": delta, "beta": beta, "s": s, "c": c, "qbar": qbar},
        "baseline": baseline,
        "signatures": signatures,
        "checks": checks,
        "limits": [
            "No actual neural or hardware route certified",
            "No intervention fidelity or mechanism closure established",
            "No experience measurement, C1 validation or B_order proof",
            "Finite tests do not identify unrestricted mechanisms",
        ],
    })


if __name__ == "__main__":
    result = run()
    target = Path(__file__).with_name("MODEL_RESULTS.json")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"checks_passed": len(result["checks"]), "signatures": result["signatures"]}, ensure_ascii=False))
