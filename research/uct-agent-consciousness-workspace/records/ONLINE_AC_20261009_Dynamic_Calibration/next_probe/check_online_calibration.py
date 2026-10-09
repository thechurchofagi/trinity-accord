#!/usr/bin/env python3
"""Exact finite probe of online calibration; not empirical UCT evidence.

Three binary action/effect ports, a known initial identity permutation, and a
fixed goal: each round's net effect must toggle effect port 0 only. Before each
round an identity or one arbitrary effect-port transposition occurs. Wiring is
fixed within that round. A probe and terminal action are both full parallel
binary command vectors, and both physically toggle the same plant. Probe
feedback is the complete effect vector. The main model also returns the full
terminal effect vector; a separately labelled variant withholds it.

All 16 length-two drift sequences are fixed obliviously and equally weighted.
The dynamic program enumerates every first probe and every first terminal
policy. For each resulting observable history it independently enumerates all
second probes and all eight possible terminal actions in each response cell.
Maximization separates over disjoint observable histories, giving the complete
deterministic two-round policy optimum, without using the proposed theorem.
"""

from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations, product
from pathlib import Path
import hashlib
import json


def compose(left, right):
    return tuple(left[right[i]] for i in range(len(left)))


def apply_wiring(wiring, command):
    effect = 0
    for i, destination in enumerate(wiring):
        if command & (1 << i):
            effect |= 1 << destination
    return effect


def drift_family(n):
    identity = tuple(range(n))
    family = [identity]
    for a, b in combinations(range(n), 2):
        moved = list(identity)
        moved[a], moved[b] = moved[b], moved[a]
        family.append(tuple(moved))
    return tuple(family)


def one_round_search(old_family, n=3, goal=1):
    """Full command/effect enumeration; no graph or information-bound shortcut."""
    worlds = [compose(drift, old) for old in old_family
              for drift in drift_family(n)]
    details = []
    for probe in range(1 << n):
        cells = defaultdict(list)
        for wiring in worlds:
            cells[apply_wiring(wiring, probe)].append(wiring)
        maximum = 0
        conflicts = []
        for observed, compatible in sorted(cells.items()):
            scores = {
                terminal: sum(apply_wiring(w, probe ^ terminal) == goal
                              for w in compatible)
                for terminal in range(1 << n)
            }
            maximum += max(scores.values())
            required = defaultdict(list)
            for wiring in compatible:
                correct = [v for v in range(1 << n)
                           if apply_wiring(wiring, probe ^ v) == goal]
                assert len(correct) == 1
                required[correct[0]].append(wiring)
            if len(required) > 1:
                alternatives = list(required.items())[:2]
                conflicts.append({
                    "observed": observed,
                    "world_1": alternatives[0][1][0],
                    "terminal_1": alternatives[0][0],
                    "world_2": alternatives[1][1][0],
                    "terminal_2": alternatives[1][0],
                })
        details.append({"probe": probe, "correct_worlds": maximum,
                        "total_worlds": len(worlds), "conflicts": conflicts})
    return details


def optimize_two_rounds(terminal_feedback, objective):
    assert objective in ("all_prefixes", "last_round_increment_only")
    n, goal = 3, 1
    identity = tuple(range(n))
    drift = drift_family(n)
    command_count = 1 << n
    counters = Counter()

    @lru_cache(None)
    def best_second(eligible_wiring_counts):
        """Optimize actual observable cells after one more probe.

        First-failed worlds have zero weight for all-prefix scoring. Omitting
        their score weight does not give the policy an oracle: the returned
        action remains one fixed action for each actually observed cell, and a
        failed world cannot contribute to the joint objective under any action.
        """
        counters["distinct_second_subproblems"] += 1
        best_score = -1
        best_policy = None
        for probe in range(command_count):
            counters["second_probe_candidates"] += 1
            cells = defaultdict(list)
            for wiring, count in eligible_wiring_counts:
                cells[apply_wiring(wiring, probe)].append((wiring, count))
            score = 0
            terminal_table = {}
            for observed, weighted_worlds in sorted(cells.items()):
                options = []
                for terminal in range(command_count):
                    counters["second_terminal_action_cell_checks"] += 1
                    success = sum(count for wiring, count in weighted_worlds
                                  if apply_wiring(wiring, probe ^ terminal) == goal)
                    options.append(success)
                chosen = max(range(command_count), key=lambda v: options[v])
                score += options[chosen]
                terminal_table[observed] = chosen
            if score > best_score:
                best_score = score
                best_policy = {"probe": probe, "terminal_by_probe_effect": terminal_table}
        return best_score, best_policy

    best_value = -1
    best_first = None
    perfect_first_candidates = []
    for first_probe in range(command_count):
        counters["first_probe_candidates"] += 1
        first_cells = defaultdict(list)
        for first_drift in drift:
            first_wiring = compose(first_drift, identity)
            first_cells[apply_wiring(first_wiring, first_probe)].append(first_wiring)
        responses = sorted(first_cells)
        for actions in product(range(command_count), repeat=len(responses)):
            counters["first_terminal_policies"] += 1
            first_terminal = dict(zip(responses, actions))
            histories = defaultdict(list)
            first_correct_count = 0
            for first_wiring in drift:
                y = apply_wiring(first_wiring, first_probe)
                terminal = first_terminal[y]
                z = apply_wiring(first_wiring, terminal)
                first_correct = (y ^ z) == goal
                first_correct_count += first_correct
                key = (y, z) if terminal_feedback else (y,)
                for second_drift in drift:
                    second_wiring = compose(second_drift, first_wiring)
                    eligible = first_correct if objective == "all_prefixes" else True
                    histories[key].append((second_wiring, eligible))
            if first_correct_count == len(drift):
                perfect_first_candidates.append({"probe": first_probe,
                                                 "terminal": first_terminal})
            value = 0
            second_policies = {}
            for history, worlds in sorted(histories.items()):
                counts = Counter(wiring for wiring, eligible in worlds if eligible)
                key = tuple(sorted(counts.items()))
                local_value, policy = best_second(key)
                value += local_value
                second_policies[history] = policy
            if value > best_value:
                best_value = value
                best_first = {"probe": first_probe,
                              "terminal_by_probe_effect": first_terminal,
                              "second": second_policies}

    traces = []
    for first_drift, second_drift in product(drift, repeat=2):
        first_wiring = first_drift
        second_wiring = compose(second_drift, first_wiring)
        u1 = best_first["probe"]
        y1 = apply_wiring(first_wiring, u1)
        v1 = best_first["terminal_by_probe_effect"][y1]
        z1 = apply_wiring(first_wiring, v1)
        history = (y1, z1) if terminal_feedback else (y1,)
        second_policy = best_first["second"][history]
        u2 = second_policy["probe"]
        y2 = apply_wiring(second_wiring, u2)
        # Cells reached only by already failed histories may have no table
        # entry; zero is a fixed legal completion of that policy.
        v2 = second_policy["terminal_by_probe_effect"].get(y2, 0)
        z2 = apply_wiring(second_wiring, v2)
        first_success, second_success = (y1 ^ z1) == goal, (y2 ^ z2) == goal
        traces.append({
            "drift_1": first_drift, "drift_2": second_drift,
            "wiring_1": first_wiring, "wiring_2": second_wiring,
            "probe_1": u1, "probe_effect_1": y1,
            "terminal_1": v1, "terminal_effect_1": z1,
            "end_state_1": y1 ^ z1,
            "probe_2": u2, "probe_effect_2": y2,
            "terminal_2": v2, "terminal_effect_2": z2,
            "end_state_2": y1 ^ z1 ^ y2 ^ z2,
            "first_success": first_success, "second_success": second_success,
            "all_prefix_success": first_success and second_success,
        })
    achieved = sum(t["all_prefix_success"] if objective == "all_prefixes"
                   else t["second_success"] for t in traces)
    assert achieved == best_value
    first_serializable = dict(best_first)
    first_serializable["second"] = [
        {"observed_first_history": history, **policy}
        for history, policy in sorted(best_first["second"].items())
    ]
    return {
        "terminal_feedback": terminal_feedback,
        "objective": objective,
        "optimal_success": str(Fraction(best_value, len(traces))),
        "correct_sequences": best_value,
        "oblivious_sequences": len(traces),
        "enumeration_counters": dict(counters),
        "first_policies_perfect_on_all_first_drifts": perfect_first_candidates,
        "attaining_policy": first_serializable,
        "attainment_traces": traces,
    }


def two_probe_indefinite_construction():
    """Read only returned effects; reconstruct all wiring before terminal action."""
    n, goal = 3, 1
    successful = 0
    for drifts in product(drift_family(n), repeat=2):
        wiring = tuple(range(n))
        state = 0
        for drift in drifts:
            wiring = compose(drift, wiring)
            start = state
            commands = (2, 4)
            observations = []
            for command in commands:
                observed = apply_wiring(wiring, command)
                observations.append(observed)
                state ^= observed
            destinations = [None,
                            observations[0].bit_length() - 1,
                            observations[1].bit_length() - 1]
            destinations[0] = (set(range(n)) - set(destinations[1:])).pop()
            learned = tuple(destinations)
            assert learned == wiring
            inverse_goal_action = 1 << learned.index(0)
            terminal = commands[0] ^ commands[1] ^ inverse_goal_action
            state ^= apply_wiring(wiring, terminal)
            assert state ^ start == goal
        successful += 1
    return {"two_round_sequences_checked": successful,
            "all_succeeded": True,
            "probe_commands": [2, 4],
            "extension_to_arbitrary_horizon": "Per-round identification and algebraic net-effect correction, with wiring fixed inside each round; proof in NEXT_RESEARCH_PROBE.md."}


def main():
    all_old = tuple(permutations(range(3)))
    singleton_checks = []
    for old in all_old:
        search = one_round_search((old,))
        perfect = [r["probe"] for r in search
                   if r["correct_worlds"] == r["total_worlds"]]
        assert len(perfect) == 2
        singleton_checks.append({"old_wiring": old, "perfect_probes": perfect})
    pair_checks = []
    for left, right in combinations(all_old, 2):
        search = one_round_search((left, right))
        assert all(r["correct_worlds"] < r["total_worlds"] for r in search)
        pair_checks.append({"old_wirings": [left, right], "probe_search": search})
    n2 = one_round_search(tuple(permutations(range(2))), n=2)
    n2_perfect = [r["probe"] for r in n2
                  if r["correct_worlds"] == r["total_worlds"]]
    assert n2_perfect == [1, 2]

    searches = [optimize_two_rounds(feedback, objective)
                for feedback in (False, True)
                for objective in ("all_prefixes", "last_round_increment_only")]
    for result in searches:
        if result["objective"] == "all_prefixes":
            assert result["optimal_success"] == "7/8"
        if result["terminal_feedback"] and result["objective"] == "last_round_increment_only":
            assert result["optimal_success"] == "1"

    result = {
        "result_id": "ONLINE-AC-PROBE-20261009",
        "status": "RESEARCH_CHECKPOINT_NOT_SCIENTIFIC_MAP_INTEGRATION",
        "contract": {
            "n": 3, "initial_wiring": [0, 1, 2], "goal_vector_integer": 1,
            "goal": "Each round's net effect toggles named effect port 0 only.",
            "command_alphabet": "All 8 parallel binary vectors; terminal action also permits all 8.",
            "probe_observation": "Entire 3-bit effect vector, not one scalar.",
            "terminal_observation": "Main branch returns entire terminal effect vector; separate branch withholds it.",
            "plant": "Both commands physically XOR-toggle the same plant. No reset is assumed; actual end states are traced.",
            "wiring_change": "Identity or one effect-port transposition before each round; no changes within a round.",
            "drift_law": "Independent uniform draws from 4 changes, equivalently uniform over 16 fixed oblivious two-round sequences.",
            "deadline": "After terminal action in each round; no claim of correct plant state immediately after calibration probe.",
            "last_round_increment_only": "Scores state_end_2 XOR state_start_2 == e_0; it does not score the final plant state relative to the initial state and is not terminal-memory recovery.",
            "memory": "All past returned observations and issued actions may be retained without bound.",
            "randomization": "Independent randomization cannot improve the fixed-prior average optimum, since it is a mixture of deterministic complete policies.",
        },
        "one_round_known_old_wiring": singleton_checks,
        "one_round_two_old_wirings": pair_checks,
        "n2_exception_perfect_probes_without_old_wiring": n2_perfect,
        "two_round_policy_search": searches,
        "two_probe_repair": two_probe_indefinite_construction(),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    output = Path(__file__).with_name("EXACT_RESULTS.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "old_singletons_checked": len(singleton_checks),
        "old_pairs_checked": len(pair_checks),
        "two_round_optima": [
            {k: r[k] for k in ("terminal_feedback", "objective", "optimal_success", "enumeration_counters")}
            for r in searches
        ],
        "two_probe_repair_sequences": result["two_probe_repair"]["two_round_sequences_checked"],
        "code_sha256": result["code_sha256"],
        "receipt_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }, indent=2))


if __name__ == "__main__":
    main()
