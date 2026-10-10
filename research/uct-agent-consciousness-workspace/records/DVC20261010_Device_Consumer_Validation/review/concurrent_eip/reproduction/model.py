#!/usr/bin/env python3
"""Exact finite identifiability check for the EIP consumer-read contract."""

import itertools
import json
from pathlib import Path


def obs(row):
    """Ordinary package: peripheral delivery, cortical arrival, aggregate state/output."""
    s, g, x = row
    arrival = s
    update = (s and g) or x
    output = update
    return (s, arrival, int(update), int(output))


def exclusive_probe(row):
    """Declared alternative writer x is disabled; consumer update is observed."""
    s, g, _x = row
    update = s and g
    return (s, int(update))


rows = [tuple(bits) for bits in itertools.product((0, 1), repeat=3)]
ordinary_groups = {}
for row in rows:
    ordinary_groups.setdefault(obs(row), []).append(row)

ambiguous = []
for evidence, group in ordinary_groups.items():
    gates = sorted({row[1] for row in group})
    if gates == [0, 1]:
        ambiguous.append({"evidence": evidence, "worlds": group})

probe_groups = {}
for row in rows:
    probe_groups.setdefault(exclusive_probe(row), []).append(row)
probe_gate_ambiguities = [
    {"evidence": evidence, "worlds": group}
    for evidence, group in probe_groups.items()
    if evidence[0] == 1 and len({row[1] for row in group}) > 1
]

result = {
    "schema": "uct-eip-exact-results/1",
    "variables": {
        "S": "selected peripheral carrier is delivered in the window",
        "G": "declared consumer actually gates/reads that carrier",
        "X": "uncontrolled alternative writer supplies the same consumer update",
        "U": "consumer update = (S AND G) OR X"
    },
    "row_count": len(rows),
    "ordinary_observation_groups": len(ordinary_groups),
    "ordinary_gate_ambiguous_groups": len(ambiguous),
    "ordinary_countermodels": ambiguous,
    "exclusive_probe_gate_ambiguities": len(probe_gate_ambiguities),
    "exact_claim": "Upstream delivery plus cortical arrival plus aggregate update/output does not identify consumer read when an alternative writer is uncontrolled.",
    "probe_claim": "After X is disabled, S=1 and U are sufficient to identify G only under the stipulated Boolean interface, sole-writer and faithful-readout premises.",
    "limits": [
        "The Boolean mechanism is a countermodel and measurement contract, not a biological identification.",
        "Neural activity or an evoked response is evidence of arrival, not by itself proof of causal consumption.",
        "The exclusive probe is invalid if another writer, common cause, off-target intervention, latency mismatch or unfaithful readout remains."
    ]
}

Path(__file__).with_name("EXACT_RESULTS.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(json.dumps({
    "rows": len(rows),
    "ordinary_gate_ambiguous_groups": len(ambiguous),
    "exclusive_probe_gate_ambiguities": len(probe_gate_ambiguities)
}))
