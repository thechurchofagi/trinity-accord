#!/usr/bin/env python3
"""Exact finite audit for a coarse-O-fixed tactile-location contrast.

X is the declared sequence/cue condition and R reverses the response mapping.
The observed raw key is Y=X xor R. H either tracks X with an unknown pole or
is invariant. A decision may read H or X directly, with an unknown orientation,
and may obey or ignore the announced response mapping.
"""

from collections import Counter
import json


def h_value(kind, parameter, x):
    return x ^ parameter if kind == "tracking" else parameter


observed = {(x, r): x ^ r for x in (0, 1) for r in (0, 1)}
compatible = []

for kind in ("tracking", "invariant"):
    for parameter in (0, 1):
        for source in ("H", "X"):
            for orientation in (0, 1):
                for mapping_policy in ("obey", "ignore"):
                    predicted = {}
                    for x, r in observed:
                        source_value = h_value(kind, parameter, x) if source == "H" else x
                        predicted[(x, r)] = source_value ^ orientation ^ (r if mapping_policy == "obey" else 0)
                    if predicted == observed:
                        compatible.append({
                            "target_kind": kind,
                            "target_parameter": parameter,
                            "decision_source": source,
                            "source_orientation": orientation,
                            "mapping_policy": mapping_policy,
                        })

def count(field):
    return dict(sorted(Counter(m[field] for m in compatible).items()))

h_source = [m for m in compatible if m["decision_source"] == "H"]
h_source_positive = [m for m in h_source if m["source_orientation"] == 0]
fixed_oriented_z = [
    m for m in compatible
    if m["target_kind"] == "tracking" and m["target_parameter"] == 0
]

result = {
    "schema": "a5h-coarse-o-contrast/1",
    "observed_raw_key": {f"X={x},R={r}": y for (x, r), y in observed.items()},
    "model": "H tracks X with either pole or is invariant; the decision reads H or X, may complement it, and may obey or ignore response mapping R.",
    "counts": {
        "total_compatible": len(compatible),
        "by_target_kind": count("target_kind"),
        "by_decision_source": count("decision_source"),
        "by_mapping_policy": count("mapping_policy"),
    },
    "compatible_models": compatible,
    "restrictions": {
        "decision_independently_H_sensitive_sign_free": {
            "count": len(h_source),
            "target_parameters": sorted({m["target_parameter"] for m in h_source}),
        },
        "decision_independently_H_sensitive_positive_orientation": {
            "count": len(h_source_positive),
            "target_parameters": sorted({m["target_parameter"] for m in h_source_positive}),
        },
        "independent_fixed_oriented_target_channel_Z_equals_X": {
            "count": len(fixed_oriented_z),
            "decision_sources": sorted({m["decision_source"] for m in fixed_oriented_z}),
        },
    },
    "conclusion": "Response-mapping reversal excludes mapping-ignoring fixed-key policies, but not a direct X-to-decision path or target-pole complementation. It therefore does not by itself identify H.",
}

print(json.dumps(result, indent=2, sort_keys=True))
