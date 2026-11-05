"""Exact finite witnesses for UCT I rc4; no empirical consciousness inference.

Run with Python 3, no external packages. Outputs are written beside this file.
The checks exhaust the declared finite cases; general statements have analytic
proofs in the manuscript. The type-permutation counterexample targets the weak
pairwise A5-OI formula alone, not the strong tokenwise A5-SI formulation.
Passing these checks does not validate A1 or A5 empirically.
"""
from itertools import product, combinations
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent
checks = []

def check(name, condition, scope, **details):
    assert condition, name
    checks.append(dict(name=name, status="PASS", scope=scope, **details))

def relabel(n):
    return {6: 7, 7: 6}.get(n, n)

check("type_injectivity_does_not_preserve_products",
      len({relabel(n) for n in range(1, 101)}) == 100
      and 7 != 2 * 3 and relabel(7) == relabel(2) * relabel(3),
      "Finite-set isomorphism classes; the 6/7 transposition is analytically a bijection on all positive integers.",
      physical_sizes=[2, 3, 7], phenomenal_sizes=[2, 3, 6])

P, Q = frozenset("ab"), frozenset("bc")
def reflect(candidate):
    return frozenset({"a": "c", "b": "b", "c": "a"}[x] for x in candidate)
families = [frozenset(c) for k in range(3) for c in combinations([P, Q], k)]
equivariant = [f for f in families if frozenset(reflect(c) for c in f) == f]
exclusive = [f for f in families if all(not a & b for a, b in combinations(f, 2))]
check("symmetric_orbit_cannot_supply_nonempty_exclusive_family",
      not [f for f in equivariant if f and f in exclusive],
      "All four subsets of the fixed candidate orbit {ab,bc}.",
      equivariant_families=[sorted("".join(sorted(c)) for c in f) for f in equivariant])
whole = frozenset([frozenset("abc")])
singletons = frozenset(frozenset(c) for c in "abc")
check("global_invariant_partitions_remain_possible",
      all(frozenset(reflect(c) for c in f) == f for f in (whole, singletons)),
      "Explicit counterexamples to an unrestricted no-partition claim.")

check("lossy_target_does_not_inherit_full_injectivity",
      0 != 1 and (lambda d: 0)(0) == (lambda d: 0)(1),
      "Identity correspondence at the full level, constant phenomenal observation at the finite level.")

STATES = list(product((0, 1), repeat=3))
ACTIONS = list(product((None, 0, 1), repeat=3))
def step(x, u, lam):
    s, a, b = x
    return (s ^ u, s ^ (lam & b), s ^ (lam & a))
def clamp(x, intervention):
    return tuple(v if c is None else c for v, c in zip(x, intervention))
def parity_ab(x):
    return x[1] ^ x[2]
def parity_all(x):
    return x[0] ^ x[1] ^ x[2]

rows = []
for lam, u, x in product((0, 1), (0, 1), STATES):
    y = step(x, u, lam)
    rows.append(dict(lam=lam, u=u, s=x[0], a=x[1], b=x[2],
                     s_next=y[0], a_next=y[1], b_next=y[2]))
check("physical_transition_table", len(rows) == 32,
      "Both circuits, both boundary inputs, all eight states.", transitions=32)

pair_count = 0
for lam, u, x, z in product((0, 1), (0, 1), STATES, STATES):
    if x[0] == z[0]:
        assert step(x, u, lam)[0] == step(z, u, lam)[0]
        pair_count += 1
check("s_projection_exact_closure", pair_count == 128,
      "Every same-s state pair under each boundary input and circuit setting.", cases=pair_count)

intervention_count = 0
for lam, u, x, act in product((0, 1), (0, 1), STATES, ACTIONS):
    s_intervened = x[0] if act[0] is None else act[0]
    assert step(clamp(x, act), u, lam)[0] == (s_intervened ^ u)
    intervention_count += 1
check("s_projection_intervention_commutation", intervention_count == 864,
      "All 27 coordinate-clamp interventions applied immediately before the next transition.", cases=intervention_count)

check("identical_output_recurrence_across_circuits",
      all(step(x, u, lam)[0] == (x[0] ^ u)
          for lam, u, x in product((0, 1), (0, 1), STATES)),
      "The recurrence implies identical s trajectories for every finite input string and common s0 by induction.")

image_sizes = {str(lam): [len({step(x, u, lam) for x in STATES}) for u in (0, 1)]
               for lam in (0, 1)}
check("full_circuits_are_not_transition_isomorphic",
      image_sizes == {"0": [2, 2], "1": [8, 8]},
      "Image cardinality is invariant under every bijective state relabeling.", image_sizes=image_sizes)

def toggle(x, i):
    y = list(x)
    y[i] ^= 1
    return tuple(y)
dependencies = {}
for lam in (0, 1):
    dependencies[str(lam)] = [
        [int(any(step(x, u, lam)[j] != step(toggle(x, i), u, lam)[j]
                 for u, x in product((0, 1), STATES))) for i in range(3)]
        for j in range(3)]
check("interventional_dependency_matrices",
      dependencies == {"0": [[1, 0, 0], [1, 0, 0], [1, 0, 0]],
                       "1": [[1, 0, 0], [1, 0, 1], [1, 1, 0]]},
      "Rows are next-state targets (s,a,b); columns are independently resettable current registers (s,a,b).",
      matrices=dependencies)
check("hidden_pair_factorizes_relative_to_physical_ports_only_at_zero",
      all(dependencies["0"][j][i] == 0 for i, j in ((1, 2), (2, 1)))
      and all(dependencies["1"][j][i] == 1 for i, j in ((1, 2), (2, 1))),
      "Condition on the declared boundary s. This is causal factorization relative to the a|b split, not a statistical independence claim.")

check("algebraic_parity_closure_is_not_a_realization_certificate",
      all(parity_ab(step(x, u, lam)) == (lam & parity_ab(x))
          for lam, u, x in product((0, 1), (0, 1), STATES)),
      "Only the algebraic identity is checked. The existence of a separate physical q register is not inferred.")
x, z = (0, 0, 0), (1, 1, 0)
check("arbitrary_projection_can_fail_closure",
      parity_all(x) == parity_all(z)
      and parity_all(step(x, 0, 0)) != parity_all(step(z, 0, 0)),
      "Counterexample for r=s XOR a XOR b at lambda=0 and u=0.",
      states=[x, z], projected_next=[parity_all(step(x, 0, 0)), parity_all(step(z, 0, 0))])

with (HERE / "transition_table.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0])
    writer.writeheader()
    writer.writerows(rows)
result = dict(status="PASS", exact_checks=len(checks), checks=checks,
              scope="Finite mathematical witnesses only; no human/animal data and no empirical validation of consciousness axioms.")
(HERE / "verification_results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(dict(status=result["status"], exact_checks=len(checks),
                      transitions=len(rows), closure_cases=pair_count,
                      intervention_cases=intervention_count, image_sizes=image_sizes)))
