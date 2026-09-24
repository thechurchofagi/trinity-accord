"""Reproduce the manuscript's finite formal checks; not a consciousness test.

Run with Python 3.10 or later. Only the standard library is used.
Checks remain active when Python is run with optimization enabled.
"""
from collections import defaultdict
from fractions import Fraction
from itertools import product
import json
from typing import Callable, Hashable, Iterable, TypeVar

TargetState = tuple[int, int, int]
SourceState = tuple[int, int]
A = TypeVar("A", bound=Hashable)
B = TypeVar("B", bound=Hashable)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def alpha(state: TargetState) -> SourceState:
    a, b, h = state
    return a ^ h, b


def source_step(state: SourceState, action: str) -> SourceState:
    u, b = state
    if action == "I":
        return state
    if action == "C":
        return u ^ 1, b
    if action == "V":
        return u, b ^ 1
    raise ValueError(f"Unknown source action: {action}")


def target_step(state: TargetState, action: str) -> TargetState:
    a, b, h = state
    if action == "I":
        return state
    if action == "C":
        return a ^ 1, b, h
    if action == "V":
        return a, b ^ 1, h
    if action == "H":
        return a ^ 1, b, h ^ 1
    raise ValueError(f"Unknown target action: {action}")


def candidate_valence_1(state: TargetState) -> int:
    return state[1]


def candidate_valence_2(state: TargetState) -> int:
    return state[1] ^ state[2]


def fiber_constant(
    states: Iterable[TargetState],
    query: Callable[[TargetState], Hashable],
) -> bool:
    fibers: dict[SourceState, set[Hashable]] = defaultdict(set)
    for state in states:
        fibers[alpha(state)].add(query(state))
    return all(len(values) == 1 for values in fibers.values())


def relation_image(relation: set[tuple[A, B]], values: set[A]) -> set[B]:
    return {v for u, v in relation if u in values}


def run_checks() -> dict[str, object]:
    states: tuple[TargetState, ...] = tuple(product((0, 1), repeat=3))
    training = tuple(x for x in states if x[2] == 0)
    actions = ("I", "C", "V")

    commutation = [
        alpha(target_step(x, action)) == source_step(alpha(x), action)
        for x in states for action in actions
    ]
    require(all(commutation), "Causal commutation failed")

    holdout_projection = [alpha(target_step(x, "H")) == alpha(x) for x in states]
    require(all(holdout_projection), "Holdout projection invariance failed")

    character_constant = fiber_constant(states, lambda x: alpha(x)[0])
    valence_1_constant = fiber_constant(states, candidate_valence_1)
    valence_2_constant = fiber_constant(states, candidate_valence_2)
    require(character_constant, "Character was not fiber-constant")
    require(valence_1_constant, "Candidate valence 1 was not fiber-constant")
    require(not valence_2_constant, "Expected aliasing in candidate valence 2")

    training_agreements = [
        candidate_valence_1(target_step(x, action))
        == candidate_valence_2(target_step(x, action))
        for x in training for action in actions
    ]
    require(all(training_agreements), "Calibration-successor agreement failed")

    # Compare CHANGE signatures, not equality of final values between models.
    holdout_change_disagreements = []
    for x in states:
        y = target_step(x, "H")
        v1_preserved = candidate_valence_1(y) == candidate_valence_1(x)
        v2_preserved = candidate_valence_2(y) == candidate_valence_2(x)
        require(v1_preserved, "Model 1 did not predict preservation")
        require(not v2_preserved, "Model 2 did not predict a category flip")
        holdout_change_disagreements.append(v1_preserved != v2_preserved)

    # This particular baseline-replay device ignores the C intervention.
    replay_failures = sum(
        alpha(x) != source_step(alpha(x), "C") for x in states
    )
    require(replay_failures == len(states), "Replay control was not distinguished")

    r_st = {("s0", "t0"), ("s1", "t1")}
    r_tu = {("t0", "u0"), ("t1", "u1")}
    r_bad = {("t2", "u2")}
    valid_path = relation_image(r_tu, relation_image(r_st, {"s0"}))
    invalid_path = relation_image(r_bad, relation_image(r_st, {"s0"}))
    require(valid_path == {"u0"}, "Compatible relation path failed")
    require(invalid_path == set(), "Incompatible relation path was not empty")

    # Invented local metric coordinates, not a scalar consciousness measure.
    eps_st, eps_tu = Fraction(3, 100), Fraction(4, 100)
    lipschitz = 3
    bound = eps_tu + lipschitz * eps_st
    metric_checks = []
    for integer in range(-5, 6):
        x = Fraction(integer)
        y = 2 * x + eps_st
        z = 3 * y + eps_tu
        metric_checks.append(abs(z - 3 * (2 * x)) <= bound)
    require(all(metric_checks), "Metric error bound failed")
    require(bound == Fraction(13, 100), "Unexpected metric bound")

    return {
        "target_states": len(states),
        "causal_commutation_checks": len(commutation),
        "holdout_projection_checks": len(holdout_projection),
        "training_transition_agreements": sum(training_agreements),
        "holdout_change_signature_disagreements": sum(holdout_change_disagreements),
        "replay_C_failures_detected": replay_failures,
        "fiber_constant_character": character_constant,
        "fiber_constant_valence_1": valence_1_constant,
        "fiber_constant_valence_2": valence_2_constant,
        "compatible_relation_path": "PASS",
        "incompatible_relation_path": "EMPTY_IMAGE_NOT_ABSENCE",
        "metric_bound_checks": len(metric_checks),
        "metric_bound": str(bound),
        "empirical_consciousness_claim": "NONE",
    }


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2))
