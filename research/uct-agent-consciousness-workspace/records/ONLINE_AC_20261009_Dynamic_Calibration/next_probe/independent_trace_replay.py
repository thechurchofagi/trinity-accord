#!/usr/bin/env python3
"""Scoped independent receipt replay; does not import or run the policy search.

Checks the four serialized attaining policies on their 16 legal drift paths,
then solves only the eight response-cell problems for old wiring {I, (12)}.
The controller receives returned effects only. The separate environment owns
the wiring and the persistent, physically toggled three-coordinate plant.
Run without arguments for JSON on stdout, or --output NEW_PATH to save once.
"""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path


IDENTITY = (0, 1, 2)
DRIFTS = (("I", None), ("s01", (0, 1)), ("s02", (0, 2)), ("s12", (1, 2)))
CHECKS = 0


def require(condition, message):
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical_digest(data):
    return digest(json.dumps(data, sort_keys=True, separators=(",", ":")).encode())


def encoded(vector):
    return sum(bit * (2 ** coordinate) for coordinate, bit in enumerate(vector))


def drifted(wiring, swap):
    if swap is None:
        return tuple(wiring)
    a, b = swap
    return tuple(b if effect == a else a if effect == b else effect for effect in wiring)


def command(plant, wiring, action):
    """Apply a command physically, retaining the same mutable plant object."""
    require(type(action) is int and 0 <= action < 8, "illegal command")
    effect = [0, 0, 0]
    for source_port in range(3):
        bit = (action // (2 ** source_port)) % 2
        target_port = wiring[source_port]
        effect[target_port] ^= bit
        plant[target_port] ^= bit
    return encoded(effect)


class ObservableController:
    """No wiring, drift, true plant state, or success flag is an input."""

    def __init__(self, policy, feedback):
        self.policy = policy
        self.feedback = feedback
        self.second = {}
        for entry in policy["second"]:
            history = tuple(entry["observed_first_history"])
            require(len(history) == (2 if feedback else 1), "wrong observation interface")
            require(history not in self.second, "duplicate first-history policy row")
            self.second[history] = entry

    def first_probe(self):
        return self.policy["probe"]

    def first_terminal(self, probe_effect):
        self.first_effect = probe_effect
        return self.policy["terminal_by_probe_effect"][str(probe_effect)]

    def second_probe(self, terminal_observation=None):
        if self.feedback:
            require(terminal_observation is not None, "missing terminal observation")
            self.history = (self.first_effect, terminal_observation)
        else:
            require(terminal_observation is None, "withheld terminal effect leaked")
            self.history = (self.first_effect,)
        self.selected = self.second[self.history]
        return self.selected["probe"]

    def second_terminal(self, probe_effect):
        return self.selected["terminal_by_probe_effect"][str(probe_effect)]


def replay_policy(search):
    feedback = search["terminal_feedback"]
    policy = search["attaining_policy"]
    original = {}
    for trace in search["attainment_traces"]:
        key = (tuple(trace["drift_1"]), tuple(trace["drift_2"]))
        require(key not in original, "duplicate saved drift path")
        original[key] = trace
    require(len(original) == 16, "not 16 distinct saved paths")
    all_replayed = []
    observed_actions = defaultdict(dict)
    first_histories = Counter()
    comparisons = 0
    failures = []

    def common_action(stage, history, action):
        table = observed_actions[stage]
        if history in table:
            require(table[history] == action, "observable-history nondeterminism")
        table[history] = action

    for (name1, swap1), (name2, swap2) in itertools.product(DRIFTS, repeat=2):
        controller = ObservableController(policy, feedback)
        plant = [0, 0, 0]
        wiring1 = drifted(IDENTITY, swap1)
        probe1 = controller.first_probe()
        common_action("first_probe", (), probe1)
        effect1 = command(plant, wiring1, probe1)
        terminal1 = controller.first_terminal(effect1)
        common_action("first_terminal", (probe1, effect1), terminal1)
        terminal_effect1 = command(plant, wiring1, terminal1)
        end1 = encoded(plant)
        first_success = end1 == 1

        # Drift changes the wiring only: plant is neither relabeled nor reset.
        start2 = encoded(plant)
        wiring2 = drifted(wiring1, swap2)
        visible_terminal = terminal_effect1 if feedback else None
        probe2 = controller.second_probe(visible_terminal)
        visible_history = (probe1, effect1, terminal1, visible_terminal)
        common_action("second_probe", visible_history, probe2)
        first_histories[controller.history] += 1
        effect2 = command(plant, wiring2, probe2)
        terminal2 = controller.second_terminal(effect2)
        common_action("second_terminal", visible_history + (probe2, effect2), terminal2)
        terminal_effect2 = command(plant, wiring2, terminal2)
        end2 = encoded(plant)
        second_success = (end2 ^ start2) == 1

        replay = {
            "drift_1": list(drifted(IDENTITY, swap1)),
            "drift_2": list(drifted(IDENTITY, swap2)),
            "wiring_1": list(wiring1), "wiring_2": list(wiring2),
            "probe_1": probe1, "probe_2": probe2,
            "probe_effect_1": effect1, "probe_effect_2": effect2,
            "terminal_1": terminal1, "terminal_2": terminal2,
            "terminal_effect_1": terminal_effect1,
            "terminal_effect_2": terminal_effect2,
            "end_state_1": end1, "end_state_2": end2,
            "first_success": first_success, "second_success": second_success,
            "all_prefix_success": first_success and second_success,
        }
        key = (tuple(replay["drift_1"]), tuple(replay["drift_2"]))
        require(key in original, "legal path omitted from receipt")
        require(set(replay) == set(original[key]), "trace schema differs")
        for field in replay:
            require(replay[field] == original[key][field], f"trace mismatch {name1}/{name2}/{field}")
            comparisons += 1
        all_replayed.append(replay)
        objective_success = replay["all_prefix_success"] if search["objective"] == "all_prefixes" else second_success
        if not objective_success:
            failures.append({"drift_path": [name1, name2], "end_state_1": end1, "end_state_2": end2})

    require(search["objective"] in {"all_prefixes", "last_round_increment_only"}, "unknown objective")
    score = 16 - len(failures)
    require(search["oblivious_sequences"] == 16, "denominator differs")
    require(search["correct_sequences"] == score, "attaining score differs")
    require(Fraction(search["optimal_success"]) == Fraction(score, 16), "claimed value not attained")
    require(set(first_histories) == {tuple(row["observed_first_history"]) for row in policy["second"]}, "unreachable or omitted serialized first history")
    ordered_saved = [original[(tuple(t["drift_1"]), tuple(t["drift_2"]))] for t in all_replayed]
    require(canonical_digest(all_replayed) == canonical_digest(ordered_saved), "canonical trace digest differs")
    return {
        "terminal_feedback": feedback, "objective": search["objective"],
        "status": "PASS", "paths_replayed": 16, "trace_fields_compared": comparisons,
        "correct_sequences": score, "attained_fraction": str(Fraction(score, 16)),
        "first_round_successes": sum(t["first_success"] for t in all_replayed),
        "second_round_increment_successes": sum(t["second_success"] for t in all_replayed),
        "all_prefix_successes": sum(t["all_prefix_success"] for t in all_replayed),
        "final_state_equals_initial": sum(t["end_state_2"] == 0 for t in all_replayed),
        "distinct_observable_action_rows": {stage: len(rows) for stage, rows in observed_actions.items()},
        "first_history_world_counts": [{"history": list(h), "worlds": count} for h, count in sorted(first_histories.items())],
        "scored_failure_paths": failures,
        "canonical_replayed_trace_sha256": canonical_digest(all_replayed),
        "canonical_saved_trace_sha256": canonical_digest(ordered_saved),
        "scope": "Verifies attainment and serialization; does not independently establish global two-round optimality.",
    }


def ambiguous_response_cells(receipt):
    worlds = [drifted(old, swap) for old in (IDENTITY, (0, 2, 1)) for _, swap in DRIFTS]
    distribution = Counter(worlds)
    results = []
    candidate_tests = 0
    for probe in range(8):
        cell_scores = defaultdict(lambda: [0] * 8)
        cell_worlds = Counter()
        for wiring in worlds:
            # A nonzero starting state makes probe perturbation and its correction explicit.
            initial = [1, 0, 1]
            after_probe = initial.copy()
            observed = command(after_probe, wiring, probe)
            cell_worlds[observed] += 1
            successful = []
            for terminal in range(8):
                final = after_probe.copy()
                command(final, wiring, terminal)
                success = (encoded(final) ^ encoded(initial)) == 1
                cell_scores[observed][terminal] += success
                candidate_tests += 1
                if success:
                    successful.append(terminal)
            require(successful == [probe ^ (1 << wiring.index(0))], "physical correction disagrees with unique inverse command")
        cells = []
        for observed, scores in sorted(cell_scores.items()):
            best = max(scores)
            cells.append({"probe_effect": observed, "worlds": cell_worlds[observed],
                          "correct_worlds_by_terminal_0_through_7": scores,
                          "best_correct_worlds": best,
                          "maximizing_terminal_actions": [v for v, score in enumerate(scores) if score == best]})
        correct = sum(cell["best_correct_worlds"] for cell in cells)
        results.append({"probe": probe, "total_worlds": 8, "correct_worlds": correct,
                        "optimal_success": str(Fraction(correct, 8)), "response_cells": cells})

    matching = [row for row in receipt["one_round_two_old_wirings"]
                if row["old_wirings"] == [[0, 1, 2], [0, 2, 1]]]
    require(len(matching) == 1, "ambiguous family receipt missing or duplicated")
    original = {row["probe"]: row for row in matching[0]["probe_search"]}
    require(set(original) == set(range(8)), "ambiguous probe coverage differs")
    for row in results:
        require(row["correct_worlds"] == original[row["probe"]]["correct_worlds"], "ambiguous optimum differs")
        require(row["total_worlds"] == original[row["probe"]]["total_worlds"], "ambiguous denominator differs")
    require([row["correct_worlds"] for row in results] == [4, 6, 6, 6, 6, 6, 6, 4], "unexpected ambiguous values")
    return {
        "status": "PASS", "old_wirings": [[0, 1, 2], [0, 2, 1]],
        "prior": "Uniform over two old wirings times four legal next drifts; eight labeled worlds.",
        "current_wiring_world_counts": [{"wiring": list(w), "worlds": count} for w, count in sorted(distribution.items())],
        "terminal_candidate_world_tests": candidate_tests,
        "plant_initial_state": 5,
        "scoring": "final plant XOR initial plant equals 1 after both physical commands",
        "optimization": "Each returned-effect cell chooses one common terminal action among all eight commands; disjoint cells optimize independently.",
        "probe_results": results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("EXACT_RESULTS.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    receipt = json.loads(raw)
    require(receipt["result_id"] == "ONLINE-AC-PROBE-20261009", "wrong receipt identifier")
    require(receipt["contract"]["n"] == 3, "wrong port count")
    require(receipt["contract"]["goal_vector_integer"] == 1, "wrong goal")
    require(receipt["contract"]["initial_wiring"] == list(IDENTITY), "wrong initial wiring")
    source = args.input.with_name("check_online_calibration.py")
    require(digest(source.read_bytes()) == receipt["code_sha256"], "source/receipt hash mismatch")
    searches = receipt["two_round_policy_search"]
    require(len(searches) == 4, "wrong policy count")
    require({(s["terminal_feedback"], s["objective"]) for s in searches} ==
            set(itertools.product((False, True), ("all_prefixes", "last_round_increment_only"))), "policy-interface/objective coverage differs")
    policies = [replay_policy(search) for search in searches]
    cells = ambiguous_response_cells(receipt)
    require(args.input.read_bytes() == raw, "receipt changed during replay")
    result = {
        "check_id": "ONLINE-AC-INDEPENDENT-TRACE-REPLAY-20261009",
        "status": "SCOPED_RECEIPT_CHECK_PASS",
        "source_receipt_sha256": digest(raw),
        "source_search_code_sha256_verified_without_execution": receipt["code_sha256"],
        "independent_check_script_sha256": digest(Path(__file__).read_bytes()),
        "independence": "Fresh coordinate-wise simulator and observable controller; original search code was not imported or executed.",
        "limits": ["No independent enumeration of all 3088 first-round policies.",
                   "No general n theorem, prior-art, whole-map, or premise-realization review.",
                   "Receipt agreement is not a new claim of global optimality; only the ambiguous one-round response-cell subproblem is independently optimized."],
        "assertions_passed": CHECKS, "traces_replayed": 64,
        "trace_fields_compared": sum(p["trace_fields_compared"] for p in policies),
        "policy_replays": policies, "ambiguous_family_response_cell_check": cells,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x") as handle:
            handle.write(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
