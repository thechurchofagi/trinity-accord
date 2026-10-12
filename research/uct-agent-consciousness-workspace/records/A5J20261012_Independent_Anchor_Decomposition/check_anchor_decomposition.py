#!/usr/bin/env python3
"""Exact finite check for A5J's independent-anchor decomposition.

The model is deliberately small.  P and C are independently crossed binary
variables.  H is one of six candidate binary laws.  Two observed channels,
Z and A, each select H, P, or C and may complement the selected bit.  Both
channels are required to equal P on every factorial cell.

The program distinguishes mere channel/hardware multiplicity from semantic
source diversity.  It does not model or prove consciousness.
"""

from __future__ import annotations

import itertools
import json


CELLS = tuple(itertools.product((0, 1), repeat=2))
HYPOTHESES = ("P", "notP", "C", "notC", "zero", "one")
SELECTORS = ("H", "P", "C")


def h_value(hypothesis: str, p: int, c: int) -> int:
    return {
        "P": p,
        "notP": 1 - p,
        "C": c,
        "notC": 1 - c,
        "zero": 0,
        "one": 1,
    }[hypothesis]


def read(selector: str, polarity: int, h: int, p: int, c: int) -> int:
    source = {"H": h, "P": p, "C": c}[selector]
    return source ^ polarity


def enumerate_models() -> list[dict]:
    models = []
    for hypothesis, z_selector, z_polarity, a_selector, a_polarity in itertools.product(
        HYPOTHESES, SELECTORS, (0, 1), SELECTORS, (0, 1)
    ):
        predictions = []
        for p, c in CELLS:
            h = h_value(hypothesis, p, c)
            z = read(z_selector, z_polarity, h, p, c)
            a = read(a_selector, a_polarity, h, p, c)
            predictions.append({"P": p, "C": c, "H": h, "Z": z, "A": a})
        if all(row["Z"] == row["P"] and row["A"] == row["P"] for row in predictions):
            models.append(
                {
                    "H": hypothesis,
                    "Z_source": z_selector,
                    "Z_polarity": z_polarity,
                    "A_source": a_selector,
                    "A_polarity": a_polarity,
                    "predictions": predictions,
                }
            )
    return models


def source_diverse(model: dict) -> bool:
    """One channel reads H and the other reads the independent P reference."""
    return {model["Z_source"], model["A_source"]} == {"H", "P"}


def common_orientation(model: dict) -> bool:
    """Both source-to-output maps use the same predeclared polarity."""
    return model["Z_polarity"] == model["A_polarity"]


def summarize(models: list[dict]) -> dict:
    return {
        "model_count": len(models),
        "target_hypotheses": sorted({m["H"] for m in models}),
        "target_hypothesis_count": len({m["H"] for m in models}),
        "models": [
            {
                key: m[key]
                for key in ("H", "Z_source", "Z_polarity", "A_source", "A_polarity")
            }
            for m in models
        ],
    }


def main() -> None:
    baseline = enumerate_models()
    semantic_diversity = [m for m in baseline if source_diverse(m)]
    orientation_only = [m for m in baseline if common_orientation(m)]
    full = [m for m in semantic_diversity if common_orientation(m)]

    result = {
        "schema": "uct-a5j-anchor-decomposition/1.0",
        "domain": {
            "factorial_cells": [{"P": p, "C": c} for p, c in CELLS],
            "H_hypotheses": list(HYPOTHESES),
            "channel_selectors": list(SELECTORS),
            "channel_polarities": [0, 1],
            "observation": "Z=P and A=P in every P-by-C cell",
        },
        "conditions": {
            "hardware_multiplicity": "two named channels Z and A; already present in baseline",
            "semantic_source_diversity_SD": "{Z_source,A_source}={H,P}",
            "common_orientation_CO": "Z_polarity=A_polarity",
        },
        "results": {
            "factorial_observation_only": summarize(baseline),
            "SD_only": summarize(semantic_diversity),
            "CO_only": summarize(orientation_only),
            "SD_and_CO": summarize(full),
        },
        "checks": {
            "baseline_count_12": len(baseline) == 12,
            "SD_count_4": len(semantic_diversity) == 4,
            "CO_count_10": len(orientation_only) == 10,
            "full_count_2": len(full) == 2,
            "full_identifies_target_H_equals_P": {m["H"] for m in full} == {"P"},
            "full_does_not_identify_which_channel_reads_H": {
                (m["Z_source"], m["A_source"]) for m in full
            }
            == {("H", "P"), ("P", "H")},
            "drop_SD_restores_non_P_targets": any(m["H"] != "P" for m in orientation_only),
            "drop_CO_restores_complement_target": any(m["H"] == "notP" for m in semantic_diversity),
        },
        "interpretation_limit": (
            "The exact result is conditional on semantic source labels and polarity constraints. "
            "Different hardware, two equal outputs, or factorial P-by-C data do not establish SD or CO."
        ),
    }
    assert all(result["checks"].values())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
