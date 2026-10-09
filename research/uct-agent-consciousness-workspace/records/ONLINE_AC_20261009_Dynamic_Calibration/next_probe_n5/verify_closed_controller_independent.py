#!/usr/bin/env python3
"""Verify an n=5 closed controller from its certificate, without its search code.

The certificate's state is the old-wiring belief before fresh drift. Each round
uses two adaptive, physically effective binary-vector probes and a terminal
command under one fixed wiring. The verifier checks exact observation cells,
all identity/transposition drifts, physical increments, and reachable closure.

No search/recursion/extractor implementation is read, imported, or executed.
Default output is stdout. --output PATH creates a new result file exclusively.
"""

import argparse
from collections import Counter, defaultdict, deque
import hashlib
import itertools
import json
from pathlib import Path


N = 5
GOAL = 1
IDENTITY = tuple(range(N))
CHECK_COUNT = 0


def check(condition, message):
    global CHECK_COUNT
    CHECK_COUNT += 1
    if not condition:
        raise AssertionError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        check(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def digest_object(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def legal_command(value):
    return type(value) is int and 0 <= value < 2 ** N


def vector(value):
    return [(value // (2 ** coordinate)) % 2 for coordinate in range(N)]


def encode(bits):
    return sum(bit * (2 ** coordinate) for coordinate, bit in enumerate(bits))


def signal(wiring, action):
    """Predict effect by looking up each effect port's unique input port."""
    return sum(((action // (2 ** wiring.index(effect_port))) % 2) * (2 ** effect_port)
               for effect_port in range(N))


def physically_apply(plant, wiring, action):
    """Mutate one persistent plant; determine the returned effect from its change.

    This uses forward coordinate toggles, separately from signal's inverse-port
    calculation. It neither resets the plant nor permutes it when wiring drifts.
    """
    before = plant.copy()
    for input_port, input_bit in enumerate(vector(action)):
        if input_bit:
            destination = wiring[input_port]
            plant[destination] = 1 - plant[destination]
    return encode([before[j] ^ plant[j] for j in range(N)])


def fresh_drift(wiring, swapped_effect_ports):
    if swapped_effect_ports is None:
        return wiring
    a, b = swapped_effect_ports
    result = list(wiring)
    # Find the two input ports whose output labels must be exchanged.
    source_a, source_b = result.index(a), result.index(b)
    result[source_a], result[source_b] = result[source_b], result[source_a]
    return tuple(result)


class ObservableController:
    """Actions and next memory use state ID and returned probe effects only."""

    def __init__(self, states, state_id):
        self.states = states
        self.state_id = state_id

    def first_probe(self):
        self.root = self.states[self.state_id]["tree"]
        return self.root["probe"]

    def observe_first_probe(self, effect):
        self.branch = self.root["responses"][str(effect)]
        return self.branch["probe"]

    def observe_second_probe(self, effect):
        self.leaf = self.branch["responses"][str(effect)]
        return self.leaf["terminal_command"]

    def finish_round(self):
        self.state_id = self.leaf["next_belief"]
        return self.state_id


def validate_response_map(responses, description):
    check(type(responses) is dict and bool(responses), description + ": missing response map")
    for key in responses:
        check(type(key) is str and key.isdecimal(), description + ": noninteger observation")
        check(str(int(key)) == key and legal_command(int(key)), description + ": invalid observation encoding")


def verify(certificate, raw_hash, script_hash):
    check(certificate["n"] == N, "not n=5")
    check(certificate["probes_per_round"] == 2, "not two probes per round")
    check(certificate["goal_effect_port"] == 0, "not named goal port 0")
    check(certificate["pending_states"] == [], "certificate contains pending states")

    permutations = []
    for row in certificate["permutations"]:
        check(type(row) is list and len(row) == N and
              all(type(x) is int for x in row) and sorted(row) == list(IDENTITY), "invalid wiring row")
        permutations.append(tuple(row))
    check(len(permutations) == 120 and len(set(permutations)) == 120, "permutation basis size/uniqueness")
    check(set(permutations) == set(itertools.permutations(IDENTITY)), "permutation basis not exactly S5")
    index = {wiring: i for i, wiring in enumerate(permutations)}
    swaps = [None] + list(itertools.combinations(range(N), 2))
    expected_drifts = [fresh_drift(IDENTITY, swap) for swap in swaps]
    actual_drifts = []
    for row in certificate["drifts"]:
        check(type(row) is list and len(row) == N and
              all(type(x) is int for x in row) and sorted(row) == list(IDENTITY), "invalid drift row")
        actual_drifts.append(tuple(row))
    check(len(actual_drifts) == 11 and set(actual_drifts) == set(expected_drifts), "drift family is not exactly identity plus all ten transpositions")

    states = certificate["states"]
    check(type(states) is dict and bool(states), "no controller states")
    beliefs = {}
    for state_id, state in states.items():
        check(state_id.isdecimal() and str(int(state_id)) == state_id and
              0 < int(state_id) < 2 ** 120, "invalid belief ID")
        check(set(state) == {"possible_wiring_indices", "tree"}, "unexpected state schema")
        members = state["possible_wiring_indices"]
        check(type(members) is list and bool(members) and
              all(type(i) is int and 0 <= i < 120 for i in members), "invalid belief membership")
        check(len(members) == len(set(members)), "duplicate belief member")
        check(int(state_id) == sum(2 ** i for i in members), "belief bit mask and explicit members disagree")
        beliefs[state_id] = frozenset(members)
        root = state["tree"]
        check(set(root) == {"probe", "responses"} and legal_command(root["probe"]), "invalid first probe node")
        validate_response_map(root["responses"], "first probe")
        for first_response, branch in root["responses"].items():
            check(set(branch) == {"probe", "responses"} and legal_command(branch["probe"]), "invalid second probe node")
            validate_response_map(branch["responses"], "second probe")
            for second_response, leaf in branch["responses"].items():
                check(set(leaf) == {"next_belief", "net_command", "terminal_command"}, "invalid terminal leaf")
                check(legal_command(leaf["terminal_command"]) and legal_command(leaf["net_command"]), "illegal terminal/net command")
                check(type(leaf["next_belief"]) is str and leaf["next_belief"] in states, "successor state missing")

    initial = certificate["initial_belief"]
    check(initial in states, "initial state missing")
    check(beliefs[initial] == {index[IDENTITY]}, "initial belief is not exactly the known identity wiring")

    adjacency = defaultdict(set)
    state_summaries = []
    normalized_leaves = []
    posterior_sizes = Counter()
    first_commands = Counter()
    second_commands = Counter()
    first_cells_total = 0
    leaf_total = 0
    world_total = 0
    current_wiring_total = 0
    physical_cases = 0
    per_world_replay_count = 0

    for state_id in sorted(states, key=int):
        root = states[state_id]["tree"]
        u1 = root["probe"]
        first_commands[u1] += 1
        # Retain every labeled (old wiring, fresh drift) world, even when two
        # such worlds give the same current wiring. Exact posteriors are sets.
        worlds = [(old, drift_number, index[fresh_drift(permutations[old], swap)])
                  for old in sorted(beliefs[state_id]) for drift_number, swap in enumerate(swaps)]
        current = {world[2] for world in worlds}
        world_total += len(worlds)
        current_wiring_total += len(current)
        first_cells = defaultdict(set)
        for wiring_index in current:
            first_cells[signal(permutations[wiring_index], u1)].add(wiring_index)
        check({int(key) for key in root["responses"]} == set(first_cells), f"first observation coverage: {state_id}")
        first_cells_total += len(first_cells)
        state_leaf_count = 0

        for y1, first_cell in sorted(first_cells.items()):
            branch = root["responses"][str(y1)]
            u2 = branch["probe"]
            second_commands[u2] += 1
            second_cells = defaultdict(set)
            for wiring_index in first_cell:
                second_cells[signal(permutations[wiring_index], u2)].add(wiring_index)
            check({int(key) for key in branch["responses"]} == set(second_cells), f"second observation coverage: {state_id}/{y1}")

            for y2, cell in sorted(second_cells.items()):
                leaf = branch["responses"][str(y2)]
                terminal = leaf["terminal_command"]
                successor = leaf["next_belief"]
                check(leaf["net_command"] == (u1 ^ u2 ^ terminal), "net command annotation disagrees with issued commands")
                check(beliefs[successor] == cell, f"successor is not exact complete two-probe posterior: {state_id}/{y1}/{y2}")
                terminal_effects = {signal(permutations[i], terminal) for i in cell}
                check(terminal_effects == {GOAL ^ y1 ^ y2}, "terminal fails goal or changes observed leaf partition")
                z = next(iter(terminal_effects))
                complete_with_terminal_feedback = {
                    i for i in current
                    if signal(permutations[i], u1) == y1
                    and signal(permutations[i], u2) == y2
                    and signal(permutations[i], terminal) == z
                }
                check(complete_with_terminal_feedback == beliefs[successor], "full terminal transcript posterior differs")
                for i in cell:
                    check(signal(permutations[i], leaf["net_command"]) == GOAL, "net command not the goal for every compatible wiring")
                adjacency[state_id].add(successor)
                posterior_sizes[len(cell)] += 1
                leaf_total += 1
                state_leaf_count += 1
                normalized_leaves.append({
                    "state": state_id, "probe_1": u1, "effect_1": y1,
                    "probe_2": u2, "effect_2": y2, "terminal": terminal,
                    "terminal_effect": z, "successor": successor,
                    "complete_current_wiring_indices": sorted(cell),
                })

        # Execute the observable controller separately in every labeled world.
        # All 32 starting plants are covered; each plant persists across all
        # three commands. This verifies the increment independent of earlier
        # rounds' physical state, rather than assuming a reset to zero.
        for old, drift_number, wiring_index in worlds:
            wiring = permutations[wiring_index]
            for initial_plant in range(2 ** N):
                plant = vector(initial_plant)
                controller = ObservableController(states, state_id)
                actual_u1 = controller.first_probe()
                actual_y1 = physically_apply(plant, wiring, actual_u1)
                actual_u2 = controller.observe_first_probe(actual_y1)
                actual_y2 = physically_apply(plant, wiring, actual_u2)
                actual_terminal = controller.observe_second_probe(actual_y2)
                actual_z = physically_apply(plant, wiring, actual_terminal)
                next_state = controller.finish_round()
                check(actual_y1 == signal(wiring, actual_u1) and
                      actual_y2 == signal(wiring, actual_u2) and
                      actual_z == signal(wiring, actual_terminal), "physical and predicted effects disagree")
                check((encode(plant) ^ initial_plant) == GOAL, "persistent plant increment fails")
                check((actual_y1 ^ actual_y2 ^ actual_z) == GOAL, "physical net effect fails")
                check(wiring_index in beliefs[next_state], "actual current wiring lost by controller memory update")
                physical_cases += 1
            per_world_replay_count += 1

        state_summaries.append({
            "state_id": state_id, "old_belief_size": len(beliefs[state_id]),
            "fresh_drift_labeled_worlds": len(worlds),
            "distinct_current_wirings": len(current), "first_probe": u1,
            "first_observation_cells": len(first_cells),
            "terminal_leaves": state_leaf_count,
            "distinct_successor_states": len(adjacency[state_id]),
            "persistent_plant_cases": len(worlds) * (2 ** N), "status": "PASS",
        })

    distances = {initial: 0}
    queue = deque([initial])
    while queue:
        state_id = queue.popleft()
        for successor in sorted(adjacency[state_id], key=int):
            if successor not in distances:
                distances[successor] = distances[state_id] + 1
                queue.append(successor)
    check(set(distances) == set(states), "certificate contains states unreachable from its initial belief")
    check(physical_cases == world_total * 32 and per_world_replay_count == world_total, "physical coverage count mismatch")

    return {
        "verification_id": "ONLINE-AC-N5-CLOSED-INDEPENDENT-20261009",
        "status": "CERTIFICATE_VERIFIED_CONDITIONAL_ON_STATED_PROTOCOL",
        "map_status": "PENDING_MAP",
        "certificate_result_id": certificate["result_id"],
        "certificate_sha256": raw_hash,
        "independent_verifier_sha256": script_hash,
        "certificate_declared_provenance_not_independently_read_or_executed": {
            "basis_sha256": certificate.get("basis_sha256"),
            "extractor_sha256": certificate.get("extractor_sha256"),
            "heuristic_lookahead": certificate.get("heuristic_lookahead"),
        },
        "contract_checked": {
            "n": N, "initial_wiring": list(IDENTITY), "goal_effect_integer": GOAL,
            "commands": "All 32 binary vectors; zero commands are legal.",
            "probes": "Two adaptive full-vector-effect probes per round.",
            "terminal": "One physical terminal command, followed by a round-end net-increment deadline.",
            "drift": "Identity or any one of all ten effect-port transpositions before each round; wiring fixed within the round; drift does not modify the plant.",
            "observations": "Full effects. Actions and next memory depend only on controller state and returned probe effects. Terminal effect is constant on each leaf, so full terminal feedback does not shrink its posterior.",
            "plant": "The same plant is toggled by both probes and terminal; no reset. Every labeled world checked from every one of the 32 starting states.",
            "belief_semantics": "A state is the complete pre-drift old-wiring belief. A successor is exactly all fresh current wirings compatible with its complete observed transcript.",
        },
        "counts": {
            "permutations": len(permutations), "fresh_drift_choices": len(swaps),
            "controller_states": len(states), "reachable_states": len(distances),
            "initial_belief_size": len(beliefs[initial]),
            "old_belief_size_distribution": dict(sorted(Counter(map(len, beliefs.values())).items())),
            "fresh_drift_labeled_worlds_across_states": world_total,
            "distinct_current_wiring_state_pairs": current_wiring_total,
            "first_observation_cells": first_cells_total,
            "terminal_leaves_with_exact_posterior": leaf_total,
            "posterior_size_distribution_across_leaves": dict(sorted(posterior_sizes.items())),
            "distinct_directed_state_edges": sum(map(len, adjacency.values())),
            "worlds_replayed_through_observable_controller": per_world_replay_count,
            "persistent_plant_cases": physical_cases,
            "physical_commands_executed": physical_cases * 3,
            "reachable_state_distance_distribution": dict(sorted(Counter(distances.values()).items())),
            "first_probe_command_distribution_across_states": dict(sorted(first_commands.items())),
            "second_probe_command_distribution_across_first_cells": dict(sorted(second_commands.items())),
        },
        "validated_transition_rows_sha256": digest_object(normalized_leaves),
        "validated_adjacency_sha256": digest_object({s: sorted(adjacency[s], key=int) for s in sorted(states, key=int)}),
        "finite_certificate_induction": "The initial identity belongs to the verified exact initial belief. At each verified state, every legal drift and observation path has legal actions, ends with plant increment e0, and returns the exact current-wiring belief at another verified state. Induction therefore gives the round-end goal for every finite number of rounds and every legal drift sequence; no finite lookahead value is used in this argument.",
        "limits": [
            "This is an exhaustive local certificate check and closure induction, not a new controller search or a claim inferred from horizon tests.",
            "Only this n=5 protocol and certificate are checked; no general-n synthesis or memory/probe lower bound is proved here.",
            "No requirement is imposed on intermediate plant states after probes; the goal is the total physical increment at each round end.",
            "Source search/extractor provenance hashes are copied from certificate metadata, not independently validated; neither source was read, imported, or executed.",
            "No actual hardware, empirical agent, priority, or whole-map integration claim is established.",
        ],
        "discrepancies": [], "state_checks": state_summaries,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, default=Path(__file__).with_name("CLOSED_CONTROLLER.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = args.certificate.read_bytes()
    certificate = json.loads(raw, object_pairs_hook=unique_object)
    result = verify(certificate, sha256(raw), sha256(Path(__file__).read_bytes()))
    check(args.certificate.read_bytes() == raw, "certificate changed during verification")
    result["assertions_passed"] = CHECK_COUNT
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x") as handle:
            handle.write(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
