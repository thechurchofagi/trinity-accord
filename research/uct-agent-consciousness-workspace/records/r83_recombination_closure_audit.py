"""R83: fixed-checkpoint support closure and matched mechanism permutations.

This is a finite computational audit of archived R78 networks, not a
phenomenal measurement and not a language-model experiment.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "r78_results" / "R78_Summary.json"
OUT_JSON = ROOT / "R83_Recombination_Audit_Results.json"
OUT_CSV = ROOT / "R83_Recombination_Audit_Table.csv"
X = np.array([[-1.0, -1.0], [-1.0, 1.0], [1.0, -1.0], [1.0, 1.0]])
S = X[:, 0] * X[:, 1]
Y = (S + 1.0) / 2.0
TOL = 1e-11


def unpack(values):
    p = np.asarray(values, dtype=float)
    return p[:4].reshape(2, 2), p[4:6], p[6:8], p[8]


def state(weights):
    W, b, v, c = unpack(weights)
    H = np.tanh(X @ W.T + b)
    logits = H @ v + c
    return W, b, v, c, H, logits


def measures(H, v, c):
    logits = H @ v + c
    margins = S * logits
    return {
        "accuracy": float(np.mean((logits >= 0) == Y)),
        "loss": float(np.logaddexp(0, -margins).mean()),
        "d": float(margins.mean()),
        "min_margin": float(margins.min()),
        "logits": logits.tolist(),
    }


def unique_rows(a):
    return np.unique(np.round(np.asarray(a, dtype=float), 12), axis=0)


def row_in_support(row, support):
    return bool(np.any(np.all(np.isclose(support, row, atol=TOL, rtol=0), axis=1)))


def conditional_sorted(values):
    values = np.asarray(values)
    return {
        "target_0": np.sort(values[Y == 0]).tolist(),
        "target_1": np.sort(values[Y == 1]).tolist(),
    }


SYMMETRIES = {
    "identity": np.array([0, 1, 2, 3]),
    "swap_inputs": np.array([0, 2, 1, 3]),
    "negate_both": np.array([3, 2, 1, 0]),
    "swap_and_negate": np.array([3, 1, 2, 0]),
}


def transformed_second_unit(W, b, name):
    W2 = W.copy()
    if name == "identity":
        pass
    elif name == "swap_inputs":
        W2[1] = W[1, ::-1]
    elif name == "negate_both":
        W2[1] = -W[1]
    elif name == "swap_and_negate":
        W2[1] = -W[1, ::-1]
    else:
        raise ValueError(name)
    return np.tanh(X @ W2.T + b), W2


def audit_checkpoint(seed, condition, stage, checkpoint):
    W, b, v, c, H, logits = state(checkpoint["weights"])
    assert np.max(np.abs(H - np.asarray(checkpoint["hidden"]))) < 1e-10
    assert np.max(np.abs(logits - np.asarray(checkpoint["logits"]))) < 1e-10

    support = unique_rows(H)
    u0 = len(np.unique(np.round(H[:, 0], 12)))
    u1 = len(np.unique(np.round(H[:, 1], 12)))
    closure_size = u0 * u1
    base = measures(H, v, c)

    permutation_records = []
    label_preserving_records = []
    for perm in itertools.permutations(range(4)):
        perm = np.asarray(perm, dtype=int)
        Hpatch = np.column_stack([H[:, 0], H[perm, 1]])
        rec = {
            "permutation": perm.tolist(),
            "identity": bool(np.array_equal(perm, np.arange(4))),
            "fully_on_original_support": bool(all(row_in_support(row, support) for row in Hpatch)),
            **measures(Hpatch, v, c),
        }
        permutation_records.append(rec)
        if np.array_equal(S[perm], S):
            assert conditional_sorted(Hpatch[:, 1]) == conditional_sorted(H[:, 1])
            assert abs(rec["d"] - base["d"]) < 1e-10
            label_preserving_records.append(rec)

    assert len(permutation_records) == 24
    assert len(label_preserving_records) == 4

    symmetry_records = []
    for name, perm in SYMMETRIES.items():
        H2, W2 = transformed_second_unit(W, b, name)
        Hpatch = np.column_stack([H[:, 0], H[perm, 1]])
        assert np.max(np.abs(H2 - Hpatch)) < 1e-10
        assert np.allclose(np.sort(H2[:, 1]), np.sort(H[:, 1]), atol=TOL, rtol=0)
        assert conditional_sorted(H2[:, 1]) == conditional_sorted(H[:, 1])
        z = measures(H2, v, c)
        assert abs(z["d"] - base["d"]) < 1e-10
        symmetry_records.append({
            "name": name,
            "source_row_permutation": perm.tolist(),
            "second_unit_weights": W2[1].tolist(),
            "fully_on_original_support": bool(all(row_in_support(row, support) for row in H2)),
            **z,
        })

    return {
        "seed": seed,
        "condition": condition,
        "stage": stage,
        "original": base,
        "hidden_unique_values": [u0, u1],
        "natural_support_size": int(len(support)),
        "coordinate_product_size": int(closure_size),
        "recombination_closure_fraction": float(len(support) / closure_size),
        "fully_on_support_patch_permutations": int(sum(r["fully_on_original_support"] for r in permutation_records)),
        "nonidentity_label_preserving_on_support": int(sum((not r["identity"]) and r["fully_on_original_support"] for r in label_preserving_records)),
        "label_preserving_accuracy_range": [
            min(r["accuracy"] for r in label_preserving_records),
            max(r["accuracy"] for r in label_preserving_records),
        ],
        "label_preserving_loss_range": [
            min(r["loss"] for r in label_preserving_records),
            max(r["loss"] for r in label_preserving_records),
        ],
        "label_preserving_d_range": [
            min(r["d"] for r in label_preserving_records),
            max(r["d"] for r in label_preserving_records),
        ],
        "label_preserving_permutations": label_preserving_records,
        "mechanism_symmetries": symmetry_records,
    }


def main():
    raw = SOURCE.read_bytes()
    source_sha = hashlib.sha256(raw).hexdigest()
    summary = json.loads(raw)
    audits = []
    for run in summary["runs"]:
        for stage, checkpoint in (("initial", run["initial"]), ("final", run["final"])):
            audits.append(audit_checkpoint(run["seed"], run["condition"], stage, checkpoint))

    initial = [a for a in audits if a["stage"] == "initial"]
    frozen_final = [a for a in audits if a["stage"] == "final" and a["condition"] == "readout_only"]
    learned_final = [a for a in audits if a["stage"] == "final" and a["condition"] == "full"]
    assert all(a["recombination_closure_fraction"] == 1.0 for a in initial)
    assert all(a["fully_on_support_patch_permutations"] == 24 for a in initial)
    assert all(a["recombination_closure_fraction"] == 1.0 for a in frozen_final)
    assert all(a["fully_on_support_patch_permutations"] == 24 for a in frozen_final)
    assert all(a["hidden_unique_values"] == [4, 4] for a in learned_final)
    assert all(abs(a["recombination_closure_fraction"] - 0.25) < TOL for a in learned_final)
    assert all(a["fully_on_support_patch_permutations"] == 1 for a in learned_final)
    assert all(a["nonidentity_label_preserving_on_support"] == 0 for a in learned_final)

    successful = [a for a in learned_final if a["seed"] in (3, 6)]
    assert all(a["original"]["accuracy"] == 1.0 for a in successful)
    assert all(a["label_preserving_accuracy_range"][0] < 1.0 for a in successful)

    result = {
        "scope": "R78 fixed-checkpoint finite support audit and matched second-unit mechanism permutations; no new training, language model, biological data, or phenomenal measurement",
        "r78_summary_sha256": source_sha,
        "definitions": {
            "natural_support": "the four hidden vectors produced by the declared four-input domain at a fixed checkpoint",
            "coordinate_product": "the Cartesian product of the separately observed values of hidden units 1 and 2",
            "recombination_closure_fraction": "natural_support_size / coordinate_product_size",
            "label_preserving_permutation": "a reassignment of unit-2 activations across input rows that preserves both target classes and hence unit-2 target-conditional marginals",
        },
        "counts": {
            "checkpoints": len(audits),
            "coordinate_patch_permutations_per_checkpoint": 24,
            "label_preserving_permutations_per_checkpoint": 4,
            "mechanism_symmetries_per_checkpoint": 4,
        },
        "audits": audits,
        "summary": {
            "initial_closure_fraction": sorted(set(a["recombination_closure_fraction"] for a in initial)),
            "readout_only_final_closure_fraction": sorted(set(a["recombination_closure_fraction"] for a in frozen_final)),
            "full_final_closure_fraction": sorted(set(a["recombination_closure_fraction"] for a in learned_final)),
            "full_final_original_accuracies": {str(a["seed"]): a["original"]["accuracy"] for a in learned_final},
            "full_final_matched_accuracy_ranges": {str(a["seed"]): a["label_preserving_accuracy_range"] for a in learned_final},
            "successful_seed_details": {str(a["seed"]): {
                "original_accuracy": a["original"]["accuracy"],
                "matched_accuracy_range": a["label_preserving_accuracy_range"],
                "original_loss": a["original"]["loss"],
                "matched_loss_range": a["label_preserving_loss_range"],
                "fixed_d": a["original"]["d"],
                "nonidentity_on_original_support": a["nonidentity_label_preserving_on_support"],
            } for a in successful},
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")

    fields = [
        "seed", "condition", "stage", "original_accuracy", "original_loss", "d",
        "unit1_unique", "unit2_unique", "natural_support_size", "coordinate_product_size",
        "recombination_closure_fraction", "fully_on_support_patch_permutations",
        "nonidentity_label_preserving_on_support", "matched_accuracy_min", "matched_accuracy_max",
        "matched_loss_min", "matched_loss_max",
    ]
    with OUT_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for a in audits:
            writer.writerow({
                "seed": a["seed"], "condition": a["condition"], "stage": a["stage"],
                "original_accuracy": a["original"]["accuracy"], "original_loss": a["original"]["loss"],
                "d": a["original"]["d"], "unit1_unique": a["hidden_unique_values"][0],
                "unit2_unique": a["hidden_unique_values"][1],
                "natural_support_size": a["natural_support_size"],
                "coordinate_product_size": a["coordinate_product_size"],
                "recombination_closure_fraction": a["recombination_closure_fraction"],
                "fully_on_support_patch_permutations": a["fully_on_support_patch_permutations"],
                "nonidentity_label_preserving_on_support": a["nonidentity_label_preserving_on_support"],
                "matched_accuracy_min": a["label_preserving_accuracy_range"][0],
                "matched_accuracy_max": a["label_preserving_accuracy_range"][1],
                "matched_loss_min": a["label_preserving_loss_range"][0],
                "matched_loss_max": a["label_preserving_loss_range"][1],
            })

    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
