#!/usr/bin/env python3
"""Exact checks for the balanced-tree reflection-pairing identity."""

from __future__ import annotations

import hashlib
import json
import random
import time
from collections import Counter
from pathlib import Path


SEED = 202610030218


def traversal_rank(n: int, code: int) -> list[int]:
    """Build ranks by recursive traversal; heap-order bits orient nodes."""
    ranks = [-1] * (1 << n)
    position = 0

    def visit(depth: int, prefix: int, vertex: int) -> None:
        nonlocal position
        if depth == n:
            ranks[vertex] = position
            position += 1
            return
        coordinate = n - 1 - depth
        node = (1 << depth) - 1 + prefix
        first = (code >> node) & 1
        for bit in (first, 1 - first):
            visit(
                depth + 1,
                (prefix << 1) | bit,
                vertex | (bit << coordinate),
            )

    visit(0, 0, 0)
    assert sorted(ranks) == list(range(1 << n))
    return ranks


def signs(values: list[int]) -> list[int]:
    return [1 if b > a else -1 for a, b in zip(values, values[1:])]


def runs_from_signs(edge_signs: list[int]) -> int:
    return 1 + sum(a != b for a, b in zip(edge_signs, edge_signs[1:]))


def score_order(n: int, reflection: int) -> list[int]:
    weights = [(1 - 2 * ((reflection >> j) & 1)) * (1 << j) for j in range(n)]
    vertices = list(range(1 << n))
    scores = [
        sum(weights[j] * ((vertex >> j) & 1) for j in range(n))
        for vertex in vertices
    ]
    assert len(set(scores)) == 1 << n
    order = sorted(vertices, key=scores.__getitem__)
    expected = [reflection ^ i for i in range(1 << n)]
    assert order == expected
    return order


def check_orientation(n: int, code: int, digest: hashlib._Hash) -> tuple[int, int]:
    n_vertices = 1 << n
    rank = traversal_rank(n, code)
    run_histogram: Counter[int] = Counter()
    turn_checks = 0
    for reflection in range(n_vertices):
        order = score_order(n, reflection)
        edge_signs = signs([rank[x] for x in order])
        paired_order = score_order(n, reflection ^ 1)
        paired_signs = signs([rank[x] for x in paired_order])
        assert len(edge_signs) == n_vertices - 1
        assert len(paired_signs) == n_vertices - 1
        for i in range(n_vertices - 1):
            carry_coordinate = ((i + 1) & -(i + 1)).bit_length() - 1
            expected = -edge_signs[i] if carry_coordinate == 0 else edge_signs[i]
            assert paired_signs[i] == expected
        for i in range(n_vertices - 2):
            assert (edge_signs[i] != edge_signs[i + 1]) != (
                paired_signs[i] != paired_signs[i + 1]
            )
            turn_checks += 1
        run_count = runs_from_signs(edge_signs)
        paired_count = runs_from_signs(paired_signs)
        assert run_count + paired_count == n_vertices
        run_histogram[run_count] += 1
        digest.update(
            n.to_bytes(1, "little")
            + code.to_bytes((n_vertices + 6) // 8, "little")
            + reflection.to_bytes((n + 7) // 8, "little")
            + run_count.to_bytes(2, "little")
        )
    assert sum(k * v for k, v in run_histogram.items()) == n_vertices * n_vertices // 2
    return n_vertices, turn_checks


def main() -> None:
    started = time.monotonic()
    digest = hashlib.sha256()
    exhaustive = []
    total_orientations = 0
    total_sweeps = 0
    total_turn_checks = 0
    for n in range(1, 5):
        n_vertices = 1 << n
        orientations = 1 << (n_vertices - 1)
        for code in range(orientations):
            sweeps, turns = check_orientation(n, code, digest)
            total_sweeps += sweeps
            total_turn_checks += turns
        total_orientations += orientations
        exhaustive.append(
            {
                "n": n,
                "orientations": orientations,
                "reflected_sweeps_each": n_vertices,
                "violations": 0,
            }
        )

    rng = random.Random(SEED)
    sampled = []
    for n in range(5, 11):
        n_vertices = 1 << n
        samples = 32 if n <= 7 else 8
        reflections = list(range(n_vertices)) if n <= 7 else [rng.randrange(n_vertices) for _ in range(64)]
        checked = 0
        for _ in range(samples):
            code = rng.getrandbits(n_vertices - 1)
            rank = traversal_rank(n, code)
            for z in reflections:
                a = signs([rank[z ^ i] for i in range(n_vertices)])
                b = signs([rank[(z ^ 1) ^ i] for i in range(n_vertices)])
                assert all(
                    b[i] == (-a[i] if (((i + 1) & -(i + 1)).bit_length() - 1) == 0 else a[i])
                    for i in range(n_vertices - 1)
                )
                assert runs_from_signs(a) + runs_from_signs(b) == n_vertices
                checked += 1
                digest.update(json.dumps([n, code, z, runs_from_signs(a)], separators=(",", ":")).encode())
        sampled.append(
            {
                "n": n,
                "orientations": samples,
                "reflections_per_orientation": len(reflections),
                "paired_checks": checked,
                "violations": 0,
            }
        )

    receipt = {
        "theorem": "R_z + R_(z xor 1) = 2^n for every balanced-tree orientation",
        "seed": SEED,
        "exhaustive": exhaustive,
        "exhaustive_orientation_count": total_orientations,
        "exhaustive_sweep_count": total_sweeps,
        "exhaustive_turn_indicator_checks": total_turn_checks,
        "sampled": sampled,
        "integer_score_realization_checked": True,
        "violations": 0,
        "digest": digest.hexdigest(),
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    out = Path(__file__).with_name("tree_reflection_verification.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
