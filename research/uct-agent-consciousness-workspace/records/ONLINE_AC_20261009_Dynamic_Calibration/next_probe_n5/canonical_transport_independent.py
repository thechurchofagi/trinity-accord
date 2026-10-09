#!/usr/bin/env python3
"""Independent two-template and canonical-transport certificate verification.

Reads only CLOSED_CONTROLLER.json and CANONICAL_TEMPLATES.json as source data.
It uses original states 1 and 3, not any other controller tree, and never reads,
imports, or executes a search, winning recursion, or extractor implementation.
All 480 singleton/non-goal-swap-pair beliefs and every legal drift are checked.
--output creates a new file exclusively; without it JSON is written to stdout.
"""

import argparse
from collections import Counter, defaultdict, deque
import hashlib
import itertools
import json
from pathlib import Path


N = 5
I = tuple(range(N))
GOAL = 1
PLANT_START = 21
CHECK_COUNT = 0


def check(condition, message):
    global CHECK_COUNT
    CHECK_COUNT += 1
    if not condition:
        raise AssertionError(message)


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        check(key not in value, f"duplicate JSON key: {key}")
        value[key] = item
    return value


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def object_digest(value):
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def compose(left, right):
    return tuple(left[right[j]] for j in range(N))


def inverse(permutation):
    return tuple(permutation.index(j) for j in range(N))


def transposition(a, b):
    permutation = list(I)
    permutation[a], permutation[b] = permutation[b], permutation[a]
    return tuple(permutation)


def push(permutation, bits):
    """Move input-coordinate i to coordinate permutation[i]."""
    return sum(((bits >> i) & 1) << permutation[i] for i in range(N))


def signal(wiring, command):
    """Independent inverse-port evaluation of a command's full effect."""
    return sum(((command >> wiring.index(j)) & 1) << j for j in range(N))


def encode(plant):
    return sum(bit << j for j, bit in enumerate(plant))


def physical_command(plant, wiring, command):
    check(type(command) is int and 0 <= command < 32, "illegal physical command")
    before = plant.copy()
    for source in range(N):
        if (command >> source) & 1:
            plant[wiring[source]] ^= 1
    return encode(before) ^ encode(plant)


def belief(wirings):
    return tuple(sorted(set(wirings)))


def differing_non_goal_swap(family):
    if len(family) != 2:
        return None
    difference = compose(family[1], inverse(family[0]))
    moved = tuple(j for j in range(N) if difference[j] != j)
    if len(moved) == 2 and 0 not in moved and difference == transposition(*moved):
        return moved
    return None


def admissible(family):
    return len(family) == 1 or differing_non_goal_swap(family) is not None


def decode_mask(mask, source_basis):
    check(type(mask) is str and mask.isdecimal() and str(int(mask)) == mask, "invalid belief-mask syntax")
    value = int(mask)
    check(0 < value < (1 << 120), "invalid belief-mask range")
    return belief(source_basis[j] for j in range(120) if (value >> j) & 1)


def canonicalize(family):
    """Choose maps from the known belief; rho is not the actual hidden wire."""
    rho = min(family)
    if len(family) == 1:
        f = I
        template_id = "1"
    else:
        ports = differing_non_goal_swap(family)
        check(ports is not None, "pair is not a non-goal transposition family")
        r, s = ports
        unused = sorted(set(range(N)) - {0, r, s})
        f = (0, unused[0], unused[1], r, s)
        template_id = "3"
    c = compose(inverse(rho), f)
    return rho, f, c, template_id


class TransportController:
    """Only the known belief and returned effects influence commands/memory."""

    def __init__(self, family, templates):
        self.rho, self.f, self.c, self.template_id = canonicalize(family)
        self.f_inverse = inverse(self.f)
        self.c_inverse = inverse(self.c)
        self.template = templates[self.template_id]

    def first_probe(self):
        self.u1 = self.template["first_probe"]
        return push(self.c, self.u1)

    def observe_first(self, actual_effect):
        self.y1 = push(self.f_inverse, actual_effect)
        self.u2 = self.template["second_probe"][self.y1]
        return push(self.c, self.u2)

    def observe_second(self, actual_effect):
        self.y2 = push(self.f_inverse, actual_effect)
        self.leaf = self.template["leaves"][(self.y1, self.y2)]
        self.v = self.leaf["terminal_command"]
        return push(self.c, self.v)

    def successor(self):
        return belief(compose(self.f, compose(eta, self.c_inverse))
                      for eta in self.leaf["posterior"])


def read_templates(certificate, extracted, source_hash):
    basis = [tuple(row) for row in certificate["permutations"]]
    all_wirings = tuple(itertools.permutations(I))
    check(len(basis) == 120 and len(set(basis)) == 120 and set(basis) == set(all_wirings), "source basis is not exactly S5")
    check(certificate["n"] == 5 and certificate["probes_per_round"] == 2 and
          certificate["goal_effect_port"] == 0, "source contract mismatch")
    check(extracted["n"] == 5 and extracted["goal_effect_port"] == 0 and
          extracted["source_certificate_sha256"] == source_hash, "extracted source/contract mismatch")
    check(extracted["transport"]["family_size_for_fixed_goal"] == 480, "extracted family-size annotation mismatch")
    check(len(extracted["templates"]) == 2, "not exactly two extracted templates")
    by_name = {row["name"]: row for row in extracted["templates"]}
    check(set(by_name) == {"known_identity", "identity_or_swap_34"}, "extracted template names mismatch")
    templates = {}
    expected_old = {"1": (I,), "3": belief((I, transposition(3, 4)))}
    source_ids = {"1": "known_identity", "3": "identity_or_swap_34"}
    compared_rows = 0

    for state_id, name in source_ids.items():
        state = certificate["states"][state_id]
        old = belief(basis[j] for j in state["possible_wiring_indices"])
        check(old == expected_old[state_id] == decode_mask(state_id, basis), "canonical old belief mismatch")
        root = state["tree"]
        u1 = root["probe"]
        check(type(u1) is int and 0 <= u1 < 32 and set(root) == {"probe", "responses"}, "bad first probe")
        template = {"name": name, "old": old, "first_probe": u1, "second_probe": {}, "leaves": {}}
        expected_rows = {}
        for first_response, branch in root["responses"].items():
            check(first_response.isdecimal() and str(int(first_response)) == first_response, "bad first-effect key")
            y1, u2 = int(first_response), branch["probe"]
            check(0 <= y1 < 32 and type(u2) is int and 0 <= u2 < 32 and
                  set(branch) == {"probe", "responses"}, "bad second probe")
            template["second_probe"][y1] = u2
            for second_response, leaf in branch["responses"].items():
                check(second_response.isdecimal() and str(int(second_response)) == second_response, "bad second-effect key")
                y2 = int(second_response)
                check(0 <= y2 < 32 and set(leaf) == {"next_belief", "net_command", "terminal_command"}, "bad leaf schema")
                v, net = leaf["terminal_command"], leaf["net_command"]
                check(type(v) is int and 0 <= v < 32 and type(net) is int and 0 <= net < 32, "bad leaf command")
                check(net == (u1 ^ u2 ^ v), "net command annotation mismatch")
                posterior = decode_mask(leaf["next_belief"], basis)
                template["leaves"][(y1, y2)] = {"terminal_command": v, "net_command": net, "posterior": posterior}
                expected_rows[(y1, y2)] = {
                    "first_effect": y1, "second_probe": u2, "second_effect": y2,
                    "posterior_wirings": [list(w) for w in posterior],
                    "net_command": net, "terminal_command": v,
                }

        external = by_name[name]
        check(set(external) == {"name", "old_belief", "first_probe", "rows"}, "unexpected extracted template fields")
        check(external["old_belief"] == [list(w) for w in old] and external["first_probe"] == u1, "extracted template header differs")
        actual_rows = {}
        for row in external["rows"]:
            key = (row["first_effect"], row["second_effect"])
            check(key not in actual_rows, "duplicate extracted observation row")
            actual_rows[key] = row
        check(set(actual_rows) == set(expected_rows), "extracted row coverage differs")
        for key in expected_rows:
            check(actual_rows[key] == expected_rows[key], "extracted row differs from original tree")
            compared_rows += 1
        templates[state_id] = template

    return basis, all_wirings, templates, compared_rows


def verify_templates(templates, drifts):
    summaries = []
    for state_id, template in templates.items():
        worlds = [(old, drift, compose(drift, old)) for old in template["old"] for drift in drifts]
        current = {w for _, _, w in worlds}
        observed = defaultdict(set)
        terminal_effects = defaultdict(set)
        for old, drift, wiring in worlds:
            plant = [(PLANT_START >> j) & 1 for j in range(N)]
            u1 = template["first_probe"]
            y1 = physical_command(plant, wiring, u1)
            u2 = template["second_probe"][y1]
            y2 = physical_command(plant, wiring, u2)
            leaf = template["leaves"][(y1, y2)]
            z = physical_command(plant, wiring, leaf["terminal_command"])
            check((encode(plant) ^ PLANT_START) == GOAL and (y1 ^ y2 ^ z) == GOAL, "canonical physical net goal failed")
            observed[(y1, y2)].add(wiring)
            terminal_effects[(y1, y2)].add(z)
        check(set(observed) == set(template["leaves"]), "canonical terminal observation coverage differs")
        check({y1 for y1, _ in observed} == set(template["second_probe"]), "canonical first observation coverage differs")
        pair_leaves = []
        for history, compatible in sorted(observed.items()):
            y1, y2 = history
            leaf = template["leaves"][history]
            check(belief(compatible) == leaf["posterior"], "canonical posterior not exact")
            check(admissible(leaf["posterior"]), "canonical leaf leaves singleton/non-goal-pair family")
            check(terminal_effects[history] == {GOAL ^ y1 ^ y2}, "canonical terminal feedback varies within leaf")
            u2, v = template["second_probe"][y1], leaf["terminal_command"]
            complete = {w for w in current if signal(w, template["first_probe"]) == y1
                        and signal(w, u2) == y2 and signal(w, v) == (GOAL ^ y1 ^ y2)}
            check(complete == compatible, "canonical full-transcript posterior differs")
            if len(compatible) == 2:
                pair_leaves.append({"effects": list(history), "posterior": [list(w) for w in leaf["posterior"]],
                                    "differing_non_goal_effect_swap": list(differing_non_goal_swap(leaf["posterior"]))})
        summaries.append({"source_state": state_id, "name": template["name"], "status": "PASS",
                          "old_wirings": len(template["old"]), "old_drift_worlds": len(worlds),
                          "distinct_current_wirings": len(current), "first_effect_cells": len(template["second_probe"]),
                          "terminal_leaves": len(observed), "pair_leaves": pair_leaves,
                          "physical_nonzero_start_cases": len(worlds)})
    return summaries


def verify_transport(basis, all_wirings, templates, drifts):
    non_goal_swaps = tuple(transposition(a, b) for a, b in itertools.combinations(range(1, N), 2))
    family = {(rho,) for rho in all_wirings}
    family.update(belief((rho, compose(swap, rho))) for rho in all_wirings for swap in non_goal_swaps)
    check(len(family) == 480 and Counter(map(len, family)) == {1: 120, 2: 360}, "full transport family count mismatch")
    basis_index = {w: j for j, w in enumerate(basis)}

    def family_id(members):
        return str(sum(1 << basis_index[w] for w in members))

    adjacency = defaultdict(set)
    normalization_rows = []
    transition_rows = []
    normalization_examples = {}
    counts = Counter()
    posterior_sizes = Counter()

    for old_family in sorted(family):
        sid = family_id(old_family)
        rho, f, c, template_id = canonicalize(old_family)
        finv, cinv = inverse(f), inverse(c)
        check(sorted(f) == list(I) and f[0] == 0 and sorted(c) == list(I), "invalid transport maps")
        check(c == compose(inverse(rho), f), "wrong command map")
        normalized_old = belief(compose(finv, compose(w, c)) for w in old_family)
        check(normalized_old == templates[template_id]["old"], "old family does not normalize to canonical family")
        check({compose(finv, compose(drift, f)) for drift in drifts} == set(drifts), "fresh drift family not preserved")
        normalization = {"belief_id": sid, "old_belief": [list(w) for w in old_family],
                         "rho": list(rho), "f": list(f), "c": list(c), "template": template_id}
        normalization_rows.append(normalization)
        if old_family == (I,):
            normalization_examples["initial_identity"] = normalization
        if rho[0] != 0 and len(old_family) == 1 and "nonidentity_singleton" not in normalization_examples:
            normalization_examples["nonidentity_singleton"] = normalization
        if len(old_family) == 2 and rho[0] != 0 and differing_non_goal_swap(old_family) != (3, 4) and "nonidentity_pair" not in normalization_examples:
            normalization_examples["nonidentity_pair"] = normalization

        worlds = [(old, drift, compose(drift, old)) for old in old_family for drift in drifts]
        current = {w for _, _, w in worlds}
        cells = defaultdict(set)
        cell_terminal_effects = defaultdict(set)
        cell_predictions = {}
        cell_commands = {}
        second_command_by_first_effect = {}
        seen_canonical_histories = set()

        for old, drift, wiring in worlds:
            normalized_current = compose(finv, compose(wiring, c))
            normalized_drift = compose(finv, compose(drift, f))
            normalized_previous = compose(finv, compose(old, c))
            check(normalized_current == compose(normalized_drift, normalized_previous), "drift/normalization square does not commute")
            controller = TransportController(old_family, templates)
            plant = [(PLANT_START >> j) & 1 for j in range(N)]
            u1 = controller.first_probe()
            y1 = physical_command(plant, wiring, u1)
            u2 = controller.observe_first(y1)
            y2 = physical_command(plant, wiring, u2)
            terminal = controller.observe_second(y2)
            z = physical_command(plant, wiring, terminal)
            successor = controller.successor()
            check((encode(plant) ^ PLANT_START) == GOAL and (y1 ^ y2 ^ z) == GOAL, "transported persistent plant goal failed")
            check(controller.y1 == signal(normalized_current, controller.u1) and
                  controller.y2 == signal(normalized_current, controller.u2) and
                  push(finv, z) == signal(normalized_current, controller.v), "effect/command transport does not commute")
            check(wiring in successor, "actual wiring lost by transported leaf")
            check(admissible(successor) and successor in family, "transported successor outside F")
            history = (y1, y2)
            if y1 in second_command_by_first_effect:
                check(second_command_by_first_effect[y1] == u2, "second probe depends on hidden wiring")
            second_command_by_first_effect[y1] = u2
            if history in cell_commands:
                check(cell_commands[history] == (u1, u2, terminal), "terminal action depends on hidden wiring")
                check(cell_predictions[history] == successor, "memory update depends on hidden wiring")
            cell_commands[history] = (u1, u2, terminal)
            cell_predictions[history] = successor
            cells[history].add(wiring)
            cell_terminal_effects[history].add(z)
            seen_canonical_histories.add((controller.y1, controller.y2))

        check(seen_canonical_histories == set(templates[template_id]["leaves"]), "transported template leaf coverage differs")
        for history, compatible in sorted(cells.items()):
            y1, y2 = history
            u1, u2, terminal = cell_commands[history]
            predicted = cell_predictions[history]
            check(belief(compatible) == predicted, "transported posterior is not the exact complete two-effect cell")
            check(cell_terminal_effects[history] == {GOAL ^ y1 ^ y2}, "terminal feedback distinguishes purported leaf")
            complete_with_terminal = {w for w in current if signal(w, u1) == y1 and
                                      signal(w, u2) == y2 and signal(w, terminal) == (GOAL ^ y1 ^ y2)}
            check(complete_with_terminal == compatible, "complete physical transcript posterior differs")
            successor_id = family_id(predicted)
            adjacency[sid].add(successor_id)
            posterior_sizes[len(predicted)] += 1
            transition_rows.append({"belief": sid, "first_probe": u1, "first_effect": y1,
                                    "second_probe": u2, "second_effect": y2, "terminal": terminal,
                                    "terminal_effect": GOAL ^ y1 ^ y2, "successor": successor_id})
        counts["old_drift_worlds"] += len(worlds)
        counts["distinct_current_wiring_belief_pairs"] += len(current)
        counts["first_effect_cells"] += len(second_command_by_first_effect)
        counts["terminal_leaves"] += len(cells)
        counts["beliefs_checked"] += 1

    initial_id = family_id((I,))
    distances = {initial_id: 0}
    queue = deque([initial_id])
    while queue:
        source = queue.popleft()
        for target in sorted(adjacency[source], key=int):
            if target not in distances:
                distances[target] = distances[source] + 1
                queue.append(target)
    family_by_id = {family_id(b): b for b in family}
    check(set(adjacency) == set(family_by_id), "not every F belief was checked")
    check(set(distances) <= set(family_by_id), "reachable state outside F")
    return {
        "status": "PASS", "family_size": len(family),
        "family_belief_size_distribution": dict(sorted(Counter(map(len, family)).items())),
        "counts": dict(counts), "distinct_state_edges": sum(map(len, adjacency.values())),
        "posterior_size_distribution_across_leaves": dict(sorted(posterior_sizes.items())),
        "physical_nonzero_start_cases": counts["old_drift_worlds"],
        "physical_commands_executed": 3 * counts["old_drift_worlds"],
        "deterministic_canonicalization": "rho is the lexicographically smallest member of the known belief. For a singleton, f=I. For a pair, infer sorted non-goal swap r<s; set f=(0, remaining_non_goal_labels_in_sorted_order, r, s). In both cases c=inverse(rho) composed with f.",
        "normalization_examples": normalization_examples,
        "all_normalization_rows_sha256": object_digest(normalization_rows),
        "all_verified_transition_rows_sha256": object_digest(transition_rows),
        "reachable_from_identity": {
            "count": len(distances), "unreachable_members_of_closed_family": len(family) - len(distances),
            "belief_size_distribution": dict(sorted(Counter(len(family_by_id[s]) for s in distances).items())),
            "distance_distribution": dict(sorted(Counter(distances.values()).items())),
            "belief_ids": sorted(distances, key=int),
            "note": "Closure was checked for all 480 beliefs. Reachability is separately computed for this deterministic canonicalization; all 480 need not be reachable.",
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, default=Path(__file__).with_name("CLOSED_CONTROLLER.json"))
    parser.add_argument("--templates", type=Path, default=Path(__file__).with_name("CANONICAL_TEMPLATES.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    certificate_raw = args.certificate.read_bytes()
    extracted_raw = args.templates.read_bytes()
    certificate = json.loads(certificate_raw, object_pairs_hook=unique_object)
    extracted = json.loads(extracted_raw, object_pairs_hook=unique_object)
    basis, all_wirings, templates, compared_rows = read_templates(certificate, extracted, digest(certificate_raw))
    drifts = (I,) + tuple(transposition(a, b) for a, b in itertools.combinations(range(N), 2))
    check(len(certificate["drifts"]) == 11 and {tuple(d) for d in certificate["drifts"]} == set(drifts), "source drift list differs from independently constructed family")
    template_results = verify_templates(templates, drifts)
    transported = verify_transport(basis, all_wirings, templates, drifts)
    check(args.certificate.read_bytes() == certificate_raw and args.templates.read_bytes() == extracted_raw, "source data changed during verification")
    result = {
        "verification_id": "ONLINE-AC-N5-CANONICAL-TRANSPORT-INDEPENDENT-20261009",
        "status": "TWO_CANONICAL_TEMPLATES_AND_FULL_TRANSPORT_FAMILY_VERIFIED",
        "map_status": "PENDING_MAP",
        "source_certificate_sha256": digest(certificate_raw),
        "source_canonical_templates_sha256": digest(extracted_raw),
        "independent_script_sha256": digest(Path(__file__).read_bytes()),
        "extracted_rows_matched_exactly_to_original_certificate": compared_rows,
        "source_tree_ids_used": ["1", "3"], "other_controller_trees_used": False,
        "declared_formatter_hash_not_verified_by_reading_or_execution": extracted.get("formatter_sha256"),
        "assertions_passed": CHECK_COUNT,
        "template_checks": template_results,
        "transport_family_check": transported,
        "physical_start_state": PLANT_START,
        "total_nonzero_start_physical_cases": sum(t["physical_nonzero_start_cases"] for t in template_results) + transported["physical_nonzero_start_cases"],
        "algebra_checked": {
            "old_family": "inverse(f) composed with B composed with c equals {I} or {I,(34)} exactly",
            "fresh_drift": "inverse(f) composed with sigma composed with f remains identity or one transposition",
            "commands": "Actual command is c applied to the canonical command vector",
            "observations": "Canonical effect is inverse(f) applied to the actual effect vector",
            "successor": "Each canonical posterior eta maps to f composed with eta composed with inverse(c)",
            "closure": "Every mapped posterior is exactly the compatible current-wiring set and is a singleton or pair differing by a non-goal effect transposition",
        },
        "induction": "The identity singleton belongs to F. Every B in F and every legal fresh drift has executable observation-only commands, physical net effect e0, and an exact successor in F. Recanonicalizing that known successor and repeating gives the round-end goal at every finite horizon. This uses closed-family induction, not a lookahead test.",
        "limits": [
            "Only the stated n=5, goal-port-0, two-full-vector-probe protocol is verified; commands may be zero.",
            "Physical probes and terminal act on one persistent plant, and drift changes the wiring only. The goal is the round-end net increment; intermediate states are unrestricted.",
            "One nonzero plant start is replayed here per labeled world; the net-effect identities give translation-independent increments. The earlier all-32-state verifier was not imported or rerun.",
            "All 480 family members are closed, but only the separately reported subset is reachable under this particular deterministic canonicalization. The family size is not a memory lower bound.",
            "No search, recursion, extractor, or formatter source was read, imported, or executed; their metadata provenance is not independently established.",
            "No general-n synthesis, new probe lower bound, empirical realization, external priority, or whole-map integration claim is made.",
        ],
        "discrepancies": [],
    }
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x") as handle:
            handle.write(output)
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
