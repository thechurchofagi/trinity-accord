"""Independent exact checks of three disabled-candidate correction overlays.

The checks establish finite mathematical facts, not actual UCT application,
phenomenal validation, or whole-map semantic completion.
"""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import json

HERE = Path(__file__).parent


def brute_labellings(n, edges, anchors):
    return [bits for bits in product((0, 1), repeat=n)
            if all(bits[u] ^ bits[v] == parity for u, v, parity in edges)
            and all(bits[v] == value for v, value in anchors.items())]


def anchored_component_formula(n, edges, anchors):
    adjacency = [[] for _ in range(n)]
    for u, v, parity in edges:
        adjacency[u].append((v, parity))
        adjacency[v].append((u, parity))
    potential = {}
    unanchored = 0
    for root in range(n):
        if root in potential:
            continue
        potential[root] = 0
        queue = [root]
        component = []
        while queue:
            u = queue.pop()
            component.append(u)
            for v, parity in adjacency[u]:
                proposed = potential[u] ^ parity
                if v in potential:
                    if potential[v] != proposed:
                        return 0
                else:
                    potential[v] = proposed
                    queue.append(v)
        root_values = {anchors[v] ^ potential[v] for v in component if v in anchors}
        if len(root_values) > 1:
            return 0
        if not root_values:
            unanchored += 1
    return 2 ** unanchored


def check_r194():
    witness = dict(n=2, edges=[(0, 1, 0)], anchors={0: 0, 1: 1})
    solutions = brute_labellings(**witness)
    assert solutions == []
    assert anchored_component_formula(**witness) == 0
    seven_vertex_witness = dict(n=7, edges=[(0, 1, 0)], anchors={0: 0, 1: 1})
    assert brute_labellings(**seven_vertex_witness) == []
    assert anchored_component_formula(**seven_vertex_witness) == 0
    tested = 0
    for n in range(5):
        pairs = list(combinations(range(n), 2))
        for edge_states in product((None, 0, 1), repeat=len(pairs)):
            edges = [(u, v, parity) for (u, v), parity in zip(pairs, edge_states)
                     if parity is not None]
            for values in product((None, 0, 1), repeat=n):
                anchors = {v: value for v, value in enumerate(values) if value is not None}
                expected = anchored_component_formula(n, edges, anchors)
                actual = len(brute_labellings(n, edges, anchors))
                assert expected == actual, (n, edges, anchors, expected, actual)
                tested += 1
    return {
        "target": "R194:COMPONENT_COUNT / R194:r_component_count / R194-C1",
        "counterexample": {
            **witness, "cycle_consistent": True,
            "unanchored_components": 0,
            "old_unqualified_formula": 1, "actual_solution_count": 0,
            "reason": "The two anchors disagree with the equality path; no cycle is needed."
        },
        "embedding_in_original_seven_vertex_domain": {
            **seven_vertex_witness, "cycle_consistent": True,
            "unanchored_components": 5, "old_unqualified_formula": 32,
            "actual_solution_count": 0
        },
        "repair": "Zero solutions if a parity cycle or an anchor/path constraint is inconsistent; otherwise 2^c for the unanchored components.",
        "finite_check": {"vertices": "0..4", "simple_signed_graphs_and_partial_binary_anchor_maps": tested,
                         "method": "independent assignment enumeration versus parity propagation", "violations": 0},
        "limits": "The enumeration is finite. The all-finite-graph result follows by root parity propagation. Original one-anchor examples remain valid."
    }


def joint_from_conditional(p_hj, p_m_given_hj):
    law = {}
    for (h, j), mass, prob in zip(product((0, 1), repeat=2), p_hj, p_m_given_hj):
        law[h, j, 1] = mass * prob
        law[h, j, 0] = mass * (1 - prob)
    assert sum(law.values()) == 1 and all(x >= 0 for x in law.values())
    return law


def probability(law, **events):
    positions = dict(H=0, J=1, M=2)
    return sum(mass for row, mass in law.items()
               if all(row[positions[name]] == value for name, value in events.items()))


def conditional(law, target, value, given, given_value):
    denominator = probability(law, **{given: given_value})
    assert denominator > 0
    return probability(law, **{target: value, given: given_value}) / denominator


def tabulate(law):
    return [dict(H=h, J=j, M=m, p=str(p)) for (h, j, m), p in sorted(law.items())]


def check_r201():
    p_hj = [F(3, 8), F(1, 8), F(1, 8), F(3, 8)]
    inputs = [
        ("equality_collapse", [F(7, 15), F(3, 5), F(2, 5), F(8, 15)],
         [F(1, 2), F(1, 2)], [F(0), F(0)]),
        ("below_threshold_reversal", [F(5, 12), F(11, 20), F(9, 20), F(7, 12)],
         [F(11, 20), F(9, 20)], [F(1, 10), F(1, 10)])
    ]
    examples = []
    for name, conditional_m, q_t, eps in inputs:
        law = joint_from_conditional(p_hj, conditional_m)
        rho = conditional(law, "H", 1, "J", 1) - conditional(law, "H", 1, "J", 0)
        delta = conditional(law, "M", 1, "J", 1) - conditional(law, "M", 1, "J", 0)
        q_c = [conditional(law, "M", 1, "H", h) for h in (0, 1)]
        delta_c = q_c[1] - q_c[0]
        bias = delta - rho * delta_c
        beta = F(1, 10)
        threshold = beta + sum(eps)
        assert 0 < rho <= 1 and abs(bias) <= beta
        assert all(abs(q_t[h] - q_c[h]) <= eps[h] for h in (0, 1))
        if name == "equality_collapse":
            assert delta == threshold and q_t[1] == q_t[0]
        else:
            assert delta < threshold and q_t[1] < q_t[0]
        examples.append(dict(name=name, joint_law=tabulate(law),
            q_C=list(map(str, q_c)), q_T=list(map(str, q_t)),
            rho=str(rho), delta=str(delta), Delta_C=str(delta_c), b=str(bias),
            beta=str(beta), epsilon=list(map(str, eps)), threshold=str(threshold),
            Delta_T=str(q_t[1]-q_t[0])))
    reversed_endpoint = {(0, 1, 1): F(1, 2), (1, 0, 0): F(1, 2)}
    reverse_rho = conditional(reversed_endpoint, "H", 1, "J", 1) - conditional(reversed_endpoint, "H", 1, "J", 0)
    reverse_delta = conditional(reversed_endpoint, "M", 1, "J", 1) - conditional(reversed_endpoint, "M", 1, "J", 0)
    reverse_target = conditional(reversed_endpoint, "M", 1, "H", 1) - conditional(reversed_endpoint, "M", 1, "H", 0)
    assert (reverse_rho, reverse_delta, reverse_target) == (-1, 1, -1)
    return {
        "targets": ["R201:STRICTNESS_COUNTERMODELS", "R201:r_strictness_witnesses", "R201-C2"],
        "withdrawn_witness_reason": "rho=1 and supported J strata force H=J almost surely, so delta=Delta_C and b=0. The original b=1/10 tuple cannot arise from the defined joint law.",
        "coherent_replacements": examples,
        "unsigned_endpoint_witness": {"joint_law": tabulate(reversed_endpoint), "rho": str(reverse_rho),
            "delta": str(reverse_delta), "Delta_C": str(reverse_target)},
        "sufficient_theorem": "Unchanged: positive rho, bounded residual and both class drifts plus strict delta>beta+epsilon0+epsilon1 imply Delta_T>=delta-beta-epsilon0-epsilon1>0.",
        "limits": "The equality example has zero total drift; it defeats global non-strict replacement but is not arbitrary-positive-budget sharpness. The three examples are separate coherent worlds, not one strict-margin world."
    }


def check_r202():
    # Conditional cells are in (M,J) order 00,01,10,11; H masses are 1/2.
    law = {(h, j, m): F(numerator, 100)
           for h, numerators in enumerate(((19, 1, 21, 9), (9, 21, 1, 19)))
           for (m, j), numerator in zip(product((0, 1), repeat=2), numerators)}
    assert sum(law.values()) == 1 and all(p >= 0 for p in law.values())
    pi = probability(law, H=1)
    a, c = [conditional(law, "J", 1, "H", h) for h in (1, 0)]
    q = [conditional(law, "M", 1, "H", h) for h in (0, 1)]
    m, j, r = probability(law, M=1), probability(law, J=1), probability(law, M=1, J=1)
    residual = sum(probability(law, H=h) *
                   (probability(law, H=h, M=1, J=1) / probability(law, H=h)
                    - q[h] * conditional(law, "J", 1, "H", h)) for h in (0, 1))
    assert c < j < a and (j-c)/(a-c) == pi
    naive = [(a*m-r)/(a-j), (r-c*m)/(j-c)]
    corrected = [(a*m-r+residual)/(a-j), (r-c*m-residual)/(j-c)]
    assert naive != q and corrected == q
    assert naive[1]-naive[0] > 0 > q[1]-q[0]
    assert residual == F(3, 50)
    return {
        "targets": ["R202:CONDITIONAL_NONDIFFERENTIALITY", "R202:AUDIT_INVERSION_RESULT", "R202:r_audit_inversion"],
        "counterexample_source": "R203-C2 dependent twin, independently reconstructed here",
        "joint_law": tabulate(law), "pi": str(pi), "a": str(a), "c": str(c),
        "observed": {"m": str(m), "j": str(j), "r": str(r)}, "common_residual_R": str(residual),
        "true_q0_q1": list(map(str, q)), "invalid_zero_residual_inversion": list(map(str, naive)),
        "corrected_inversion": list(map(str, corrected)),
        "repair": "Conditional independence suffices for R=0. A bound |R|<=kappa yields one common-residual coherent feasible set, not exact point values.",
        "limits": "This is an exact abstract binary law. Endpoint calibration, audit ignorability, positivity, same-target transport and actual U=1 remain independent application premises."
    }


if __name__ == "__main__":
    result = {"version": "SCU-CORRECTIONS-CHECK-v0.1.0", "base_completed_map": "UCT-MAP-v1.1.2",
              "status": "EXACT_FINITE_CORRECTION_CHECKS_COMPLETED",
              "actual_premises_discharged": False, "phenomenal_validation": False,
              "R194": check_r194(), "R201": check_r201(), "R202": check_r202()}
    destination = HERE / "EFFECTIVE_CORRECTION_EXACT_RESULTS.json"
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"file": str(destination), "R194_designs": result["R194"]["finite_check"]["simple_signed_graphs_and_partial_binary_anchor_maps"],
                      "R201_coherent_cases": 3, "R202_direction_reversal_verified": True,
                      "actual_premises_discharged": False}))
