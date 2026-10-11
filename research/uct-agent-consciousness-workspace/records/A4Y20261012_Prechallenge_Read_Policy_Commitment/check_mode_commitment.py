#!/usr/bin/env python3
"""Exact finite check for A4Y's declared challenge-aware one-port twin family."""

from __future__ import annotations

import itertools
import json
from pathlib import Path


ROWS = ((0, 0), (0, 1), (1, 0), (1, 1))
MODES = (("u", 0), ("u", 1), ("v", 0), ("v", 1))


def target(name: str, u: int, v: int) -> int:
    return (u & v) if name == "AND" else (u | v)


def run_mode(mode: tuple[str, int], u: int, v: int) -> int:
    port, invert = mode
    value = u if port == "u" else v
    return value ^ invert


def table(policy: tuple[tuple[str, int], ...]) -> tuple[int, ...]:
    return tuple(run_mode(mode, *row) for mode, row in zip(policy, ROWS))


def main() -> None:
    results = {
        "schema": "uct-a4y-prechallenge-read-policy-exact/1.0",
        "scope": "deterministic Boolean AND/OR targets and a declared one-port identity/negation mode family at one fixed consumer boundary",
        "challenge_rows": ROWS,
        "modes": [{"port": p, "invert": bool(i)} for p, i in MODES],
        "counts": {},
        "drop_one_countermodels": {},
        "not_tested": [
            "physical witness independence or tamper resistance",
            "completeness of cue/alternate-path inventory",
            "actual port lineage/read or complete UCT organization",
            "B_pc^family, H_cf, report reliability or subject count",
            "arbitrary hidden-controller classes outside the declared one-port mode family",
        ],
    }

    adaptive = list(itertools.product(MODES, repeat=len(ROWS)))
    static = [tuple([mode] * len(ROWS)) for mode in MODES]
    for name in ("AND", "OR"):
        wanted = tuple(target(name, *row) for row in ROWS)
        adaptive_matches = [p for p in adaptive if table(p) == wanted]
        static_matches = [p for p in static if table(p) == wanted]
        assert len(adaptive) == 4 ** 4
        assert len(adaptive_matches) == 2 ** 4
        assert len(static_matches) == 0
        results["counts"][name] = {
            "target_table_00_01_10_11": wanted,
            "challenge_indexed_policies": len(adaptive),
            "challenge_indexed_exact_matches": len(adaptive_matches),
            "prechallenge_static_policies": len(static),
            "prechallenge_static_exact_matches": len(static_matches),
            "example_adaptive_match": [
                {"row": ROWS[i], "port": mode[0], "invert": bool(mode[1])}
                for i, mode in enumerate(adaptive_matches[0])
            ],
        }

    # PRE without BLIND: a preloaded dispatcher can still index the same 16 matching policies.
    results["drop_one_countermodels"]["drop_challenge_blindness"] = {
        "construction": "commit a challenge-indexed dispatch table before the draw, then reveal the challenge label to the dispatcher",
        "exact_matches_per_target": 16,
    }
    # BIND without PRE: the actual one-port mode is selected after seeing the challenge.
    results["drop_one_countermodels"]["drop_temporal_precedence"] = {
        "construction": "select the bound port/polarity mode after the challenge is known",
        "exact_matches_per_target": 16,
    }
    # PRE+BLIND without BIND: a sidecar state is clean while an unbound dispatcher remains adaptive.
    results["drop_one_countermodels"]["drop_consumer_binding"] = {
        "construction": "record an isolated sidecar state before the draw while the actual consumer dispatcher remains challenge-indexed",
        "exact_matches_per_target": 16,
    }
    results["bounded_result"] = (
        "A public finite challenge suite is exactly mimicked by 16 challenge-indexed one-port policies for each target. "
        "Within the declared family, a consumer-bound policy fixed before an independently drawn challenge and blind to every pre-read cue except the named data ports has no one-port exact match to AND or OR."
    )

    out = Path(__file__).with_name("EXACT_RESULTS.json")
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "targets": list(results["counts"]), "adaptive_matches": 16, "static_matches": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
