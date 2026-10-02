#!/usr/bin/env python3
"""Exact verification of the forward-Gray 5/16 row-lift ceiling."""

from __future__ import annotations

import hashlib
import json
import random
import time
from pathlib import Path


BASE_WEIGHTS = (-1, -14, -4, -12, -20)
EXPECTED_TOP_ORDER = (
    31, 30, 27, 26, 23, 22, 29, 28,
    19, 18, 25, 24, 15, 14, 11, 10,
    21, 20, 17, 16, 7, 6, 13, 12,
    3, 2, 9, 8, 5, 4, 1, 0,
)
EXPECTED_TOP_RANKS = (
    16, 17, 22, 23, 28, 29, 19, 18,
    26, 27, 21, 20, 8, 9, 14, 15,
    31, 30, 25, 24, 4, 5, 11, 10,
    2, 3, 13, 12, 7, 6, 1, 0,
)
SEED = 202610030510


def gray_rank(x: int) -> int:
    return x ^ (x >> 1)


def subset_score(x: int, weights: tuple[int, ...]) -> int:
    return sum(w * ((x >> j) & 1) for j, w in enumerate(weights))


def additive_order(n: int, weights: tuple[int, ...]) -> tuple[list[int], list[int]]:
    vertices = list(range(1 << n))
    scores = [subset_score(x, weights) for x in vertices]
    assert len(set(scores)) == len(scores)
    return sorted(vertices, key=scores.__getitem__), scores


def run_data(values: list[int]) -> tuple[int, list[int]]:
    signs = [1 if b > a else -1 for a, b in zip(values, values[1:])]
    runs = 1 + sum(a != b for a, b in zip(signs, signs[1:]))
    return runs, signs


def explicit_weights(n: int) -> tuple[int, ...]:
    assert n >= 5
    m = n - 5
    return tuple(64 << j for j in range(m)) + BASE_WEIGHTS


def verify_base() -> dict[str, object]:
    order, scores = additive_order(5, BASE_WEIGHTS)
    assert tuple(order) == EXPECTED_TOP_ORDER
    assert min(scores) == -51 and max(scores) == 0
    values = [gray_rank(x) for x in order]
    assert tuple(values) == EXPECTED_TOP_RANKS
    runs, signs = run_data(values)
    assert runs == 10
    boundary_sign = -1 if values[-1] > values[0] else 1
    endpoint_penalty = int(signs[-1] != boundary_sign) + int(boundary_sign != signs[0])
    assert endpoint_penalty == 1
    return {
        "weights": list(BASE_WEIGHTS),
        "score_range": [min(scores), max(scores)],
        "order": order,
        "gray_values": values,
        "runs": runs,
        "boundary_sign": boundary_sign,
        "endpoint_penalty": endpoint_penalty,
    }


def verify_dimension(n: int, digest: hashlib._Hash) -> dict[str, object]:
    m = n - 5
    row_length = 1 << 5
    row_count = 1 << m
    weights = explicit_weights(n)
    order, scores = additive_order(n, weights)
    expected_order = [z * row_count + y for y in range(row_count) for z in EXPECTED_TOP_ORDER]
    assert order == expected_order
    assert all(scores[order[i]] < scores[order[i + 1]] for i in range(len(order) - 1))

    values = [gray_rank(x) for x in order]
    runs, _ = run_data(values)
    expected_runs = 10 * row_count
    assert runs == expected_runs
    assert expected_runs * 16 == 5 * (1 << n)

    # Independently check that each fixed high prefix occupies its claimed
    # forward-Gray macro interval.  This permits arbitrary low-bit order.
    for z in range(row_length):
        block = [gray_rank(z * row_count + y) for y in range(row_count)]
        lo = gray_rank(z) * row_count
        assert sorted(block) == list(range(lo, lo + row_count))

    digest.update(
        n.to_bytes(1, "little")
        + bytes((v & 0xFF) for v in EXPECTED_TOP_ORDER)
        + runs.to_bytes(4, "little")
        + len(set(scores)).to_bytes(4, "little")
    )
    return {
        "n": n,
        "vertices": 1 << n,
        "rows": row_count,
        "runs": runs,
        "expected_runs": expected_runs,
        "density_numerator": 5,
        "density_denominator": 16,
        "generic": True,
        "violations": 0,
    }


def sampled_falsification() -> list[dict[str, object]]:
    """Search only: not part of the proof or any optimality claim."""
    rng = random.Random(SEED)
    results = []
    for n, samples in ((5, 20_000), (6, 10_000), (7, 4_000), (8, 1_000)):
        best = 1 << n
        generic = 0
        for _ in range(samples):
            weights = tuple(rng.randint(-10_000, 10_000) for _ in range(n))
            scores = [subset_score(x, weights) for x in range(1 << n)]
            if len(set(scores)) != 1 << n:
                continue
            generic += 1
            order = sorted(range(1 << n), key=scores.__getitem__)
            runs, _ = run_data([gray_rank(x) for x in order])
            best = min(best, runs)
        results.append({
            "n": n,
            "samples_requested": samples,
            "generic_samples": generic,
            "best_sampled_runs": best,
            "is_optimality_claim": False,
        })
    return results


def main() -> None:
    started = time.monotonic()
    digest = hashlib.sha256()
    base = verify_base()
    dimensions = [verify_dimension(n, digest) for n in range(5, 17)]
    receipt = {
        "theorem": "RLC(forward Gray rank on Q_n) <= 5*2^n/16 for every n >= 5",
        "construction": "five-dimensional chamber plus exact separated row lift",
        "base": base,
        "dimensions_verified": dimensions,
        "sampled_falsification": sampled_falsification(),
        "proof_dependency": "exact row-interleaving identity",
        "arithmetic": "integer",
        "violations": 0,
        "digest": digest.hexdigest(),
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    out = Path(__file__).with_name("forward_gray_row_lift_verification.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
