#!/usr/bin/env python3
"""Exact rational witness for A3Y's measurand-identity barrier."""

from fractions import Fraction as F
import json

PREVALENCES = (F(1, 4), F(3, 4))
TESTS = {
    "T1": {1: F(3, 4), 0: F(1, 4)},
    "T2": {1: F(4, 5), 0: F(1, 5)},
}
KERNELS = {
    "aligned_H_equals_Z": {1: F(1), 0: F(0)},
    "independent_H_from_Z": {1: F(1, 2), 0: F(1, 2)},
    "opposed_H_equals_not_Z": {1: F(0), 0: F(1)},
}


def joint_table(pz):
    table = {}
    for t1 in (1, 0):
        for t2 in (1, 0):
            total = F(0)
            for z, p in ((1, pz), (0, 1 - pz)):
                q1 = TESTS["T1"][z] if t1 else 1 - TESTS["T1"][z]
                q2 = TESTS["T2"][z] if t2 else 1 - TESTS["T2"][z]
                total += p * q1 * q2
            table[f"{t1}{t2}"] = total
    return table


def test_delta_given_h(pz, kernel, test):
    joint = {}
    for h in (1, 0):
        for t in (1, 0):
            joint[h, t] = sum(
                (pz if z else 1 - pz)
                * (kernel[z] if h else 1 - kernel[z])
                * (TESTS[test][z] if t else 1 - TESTS[test][z])
                for z in (1, 0)
            )
    ph1 = joint[1, 1] + joint[1, 0]
    ph0 = joint[0, 1] + joint[0, 0]
    return joint[1, 1] / ph1 - joint[0, 1] / ph0


tables = [joint_table(p) for p in PREVALENCES]
expected = [
    {"11": F(15, 80), "10": F(15, 80), "01": F(13, 80), "00": F(37, 80)},
    {"11": F(37, 80), "10": F(13, 80), "01": F(15, 80), "00": F(15, 80)},
]
assert tables == expected
assert all(sum(table.values()) == 1 for table in tables)

deltas = {}
for name, kernel in KERNELS.items():
    deltas[name] = []
    for pz in PREVALENCES:
        deltas[name].append(
            {test: test_delta_given_h(pz, kernel, test) for test in TESTS}
        )

for population in deltas["aligned_H_equals_Z"]:
    assert population == {"T1": F(1, 2), "T2": F(3, 5)}
for population in deltas["independent_H_from_Z"]:
    assert population == {"T1": F(0), "T2": F(0)}
for population in deltas["opposed_H_equals_not_Z"]:
    assert population == {"T1": F(-1, 2), "T2": F(-3, 5)}

def frac(x):
    return f"{x.numerator}/{x.denominator}"

result = {
    "schema": "uct-a3y-exact-witness-v1",
    "status": "PASS_EXACT_RATIONAL_WITNESS",
    "population_tables": [{key: frac(value) for key, value in t.items()} for t in tables],
    "h_kernels_checked": list(KERNELS),
    "test_deltas_by_kernel_and_population": {
        name: [{test: frac(value) for test, value in pop.items()} for pop in pops]
        for name, pops in deltas.items()
    },
    "observable_tables_invariant_across_h_kernels": True,
    "interpretive_ceiling": "The witness fixes a statistical latent Z and its test law; it does not prove that Z is H_way.",
}
print(json.dumps(result, ensure_ascii=False, sort_keys=True))
