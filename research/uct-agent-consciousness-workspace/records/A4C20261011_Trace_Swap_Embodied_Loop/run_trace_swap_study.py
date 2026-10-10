#!/usr/bin/env python3
"""A4C same-bearer trace-content intervention in a bounded embodied loop.

The program installs a deterministic one-dimensional body/action simulation.
Formation and testing are separate operating-system processes.  Two calibration
traces are formed in one bearer.  At test, one named consumer receives either
the native trace, the same-bearer opposite-context trace, no trace, or a
faithful consumer-interface rescue.  Intervention code cannot write the plant
state or endpoint.  This is a software/simulation witness, not a physical robot,
human experiment, phenomenal measurement, or complete UCT token certificate.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import inspect
import json
import random
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "run_artifacts"
RESULTS = ROOT / "EXACT_RESULTS.json"
SEED = 2026101102
BEARER = "A4C-embodied-simulation-bearer-v1"
CONSUMER = "A4C-body-loop-consumer-v1"
K_GAIN = 0.5
STEPS = 12
CONTEXT_BIAS = {"plus": 1.0, "minus": -1.0}
MODES = ("intact", "swap", "block", "rescue")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def read_json(path: Path) -> object:
    return json.loads(path.read_text())


def form(store: Path) -> None:
    """Calibrate both contexts and retain both traces in the same bearer."""
    store.mkdir(parents=True, exist_ok=True)
    events = []
    for context, bias in CONTEXT_BIAS.items():
        observations = []
        for index in range(4):
            before = float(index) / 10.0
            after = before + bias
            observations.append(
                {
                    "calibration_event_id": str(uuid.uuid4()),
                    "before": before,
                    "after": after,
                    "observed_delta": after - before,
                }
            )
        estimate = sum(x["observed_delta"] for x in observations) / len(observations)
        payload = {
            "schema": "A4C-FORMATION-TRACE-v1",
            "bearer_id": BEARER,
            "carrier_id": f"{BEARER}:retained-trace-store",
            "formation_event_id": str(uuid.uuid4()),
            "formation_context": context,
            "formation_observations": observations,
            "retained_bias_estimate": estimate,
            "formed_at_utc": utc_now(),
        }
        envelope = {"payload": payload, "payload_sha256": digest(payload)}
        write_json(store / f"trace_{context}.json", envelope)
        events.append(
            {
                "context": context,
                "trace_path": f"trace_{context}.json",
                "payload_sha256": envelope["payload_sha256"],
                "estimate": estimate,
            }
        )
    write_json(
        store / "formation_manifest.json",
        {
            "schema": "A4C-FORMATION-MANIFEST-v1",
            "bearer_id": BEARER,
            "consumer_id": CONSUMER,
            "events": events,
        },
    )


def validate_trace(envelope: dict, expected_context: str | None = None) -> tuple[bool, str]:
    payload = envelope.get("payload", {})
    if envelope.get("payload_sha256") != digest(payload):
        return False, "digest_mismatch"
    if payload.get("schema") != "A4C-FORMATION-TRACE-v1":
        return False, "schema_mismatch"
    if payload.get("bearer_id") != BEARER:
        return False, "bearer_mismatch"
    if expected_context is not None and payload.get("formation_context") != expected_context:
        return False, "context_mismatch"
    return True, "accepted"


def select_consumer_input(store: Path, context: str, mode: str) -> dict:
    """Return only the value delivered at the named consumer interface.

    This function deliberately has no plant-state or endpoint argument.  The
    structural audit below also rejects endpoint/state writes in this function.
    """
    native = read_json(store / f"trace_{context}.json")
    opposite = "minus" if context == "plus" else "plus"
    if mode == "block":
        return {
            "source": "blocked",
            "trace_opened": False,
            "trace_context": None,
            "trace_payload_sha256": None,
            "consumed_bias_estimate": 0.0,
            "validation_reason": "native_read_blocked",
        }
    if mode == "swap":
        selected = read_json(store / f"trace_{opposite}.json")
        expected = opposite
        source = "same_bearer_opposite_context_trace"
    else:
        selected = native
        expected = context
        source = "native_trace" if mode == "intact" else "consumer_interface_rescue"
    valid, reason = validate_trace(selected, expected)
    if not valid:
        raise ValueError(reason)
    return {
        "source": source,
        "trace_opened": mode != "rescue",
        "native_read_blocked": mode == "rescue",
        "rescue_delivered_at_consumer_interface": mode == "rescue",
        "trace_context": selected["payload"]["formation_context"],
        "trace_payload_sha256": selected["payload_sha256"],
        "consumed_bias_estimate": float(selected["payload"]["retained_bias_estimate"]),
        "validation_reason": reason,
    }


def run_trial(store: Path, context: str, mode: str, trial_id: str, event_path: Path, endpoint_path: Path) -> None:
    intervention = select_consumer_input(store, context, mode)
    bias = CONTEXT_BIAS[context]
    estimate = intervention["consumed_bias_estimate"]
    state = 0.0
    actions = []
    for step in range(STEPS):
        action = -K_GAIN * state - estimate
        next_state = state + action + bias
        actions.append(
            {
                "step": step,
                "state_before": state,
                "trace_value_used": estimate,
                "action": action,
                "physical_bias": bias,
                "state_after": next_state,
            }
        )
        state = next_state
    event = {
        "schema": "A4C-TEST-EVENT-v1",
        "trial_id": trial_id,
        "bearer_id": BEARER,
        "consumer_id": CONSUMER,
        "test_context": context,
        "intervention_mode": mode,
        "intervention": intervention,
        "controller_gain": K_GAIN,
        "steps": STEPS,
        "actions": actions,
        "final_state": state,
        "final_context_aligned_error": bias * state,
        "tested_at_utc": utc_now(),
    }
    # The blinded endpoint record contains no mode or trace-source label.
    endpoint = {
        "schema": "A4C-BLINDED-ENDPOINT-v1",
        "trial_id": trial_id,
        "test_context": context,
        "steps": STEPS,
        "final_context_aligned_error": bias * state,
    }
    write_json(event_path, event)
    write_json(endpoint_path, endpoint)


def run_subprocess(*args: str) -> None:
    subprocess.run([sys.executable, str(Path(__file__).resolve()), *args], check=True)


def selector_locality_audit() -> dict:
    source = inspect.getsource(select_consumer_input)
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    forbidden = sorted(names.intersection({"state", "next_state", "endpoint", "final_state"}))
    args = [a.arg for a in tree.body[0].args.args]
    return {
        "selector_arguments": args,
        "forbidden_endpoint_or_state_names": forbidden,
        "passes": not forbidden and args == ["store", "context", "mode"],
        "scope": "static audit of the declared Python selector, not proof about unrepresented physical channels",
    }


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def orchestrate() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    store = ARTIFACTS / "same_bearer_trace_store"
    run_subprocess("form", str(store))
    rng = random.Random(SEED)
    assignments = [(c, m) for c in CONTEXT_BIAS for m in MODES for _ in range(4)]
    rng.shuffle(assignments)
    registry = []
    for index, (context, mode) in enumerate(assignments):
        trial_id = f"trial-{index:03d}"
        trial_dir = ARTIFACTS / "trials" / trial_id
        event_path = trial_dir / "event_ledger.json"
        endpoint_path = trial_dir / "blinded_endpoint.json"
        run_subprocess(
            "trial", str(store), context, mode, trial_id, str(event_path), str(endpoint_path)
        )
        registry.append({"trial_id": trial_id, "test_context": context, "mode": mode})
    write_json(ARTIFACTS / "sealed_intervention_registry.json", registry)

    # Endpoint collection precedes the registry join in this executable order.
    endpoints = {
        p.parent.name: read_json(p)
        for p in sorted((ARTIFACTS / "trials").glob("*/blinded_endpoint.json"))
    }
    rows = []
    for assignment in registry:
        endpoint = endpoints[assignment["trial_id"]]
        event = read_json(
            ARTIFACTS / "trials" / assignment["trial_id"] / "event_ledger.json"
        )
        rows.append({**assignment, **endpoint, "event": event})

    by_mode = {}
    for mode in MODES:
        selected = [r for r in rows if r["mode"] == mode]
        by_mode[mode] = {
            "n": len(selected),
            "mean_context_aligned_error": mean(
                [r["final_context_aligned_error"] for r in selected]
            ),
            "contexts_balanced": {c: sum(r["test_context"] == c for r in selected) for c in CONTEXT_BIAS},
        }

    all_same_bearer_consumer = all(
        r["event"]["bearer_id"] == BEARER and r["event"]["consumer_id"] == CONSUMER
        for r in rows
    )
    action_replay_exact = all(
        abs(
            r["event"]["actions"][-1]["state_after"]
            - r["event"]["final_state"]
        )
        < 1e-12
        for r in rows
    )
    swap_is_same_bearer = all(
        validate_trace(
            read_json(store / f"trace_{r['event']['intervention']['trace_context']}.json")
        )[0]
        for r in rows
        if r["mode"] == "swap"
    )
    locality = selector_locality_audit()

    # Counterexample: the same numerical swap endpoint can be written directly
    # while leaving the intact action trajectory unchanged.  Replay exposes it.
    intact_example = next(r for r in rows if r["mode"] == "intact" and r["test_context"] == "plus")
    swap_example = next(r for r in rows if r["mode"] == "swap" and r["test_context"] == "plus")
    direct_twin = {
        "reported_endpoint": swap_example["final_context_aligned_error"],
        "replayed_endpoint_from_action_ledger": intact_example["final_context_aligned_error"],
        "endpoint_matches_swap": True,
        "action_ledger_matches_swap": False,
        "violates_no_direct_endpoint_write": True,
    }

    expected_order = (
        abs(by_mode["intact"]["mean_context_aligned_error"])
        < by_mode["block"]["mean_context_aligned_error"]
        < by_mode["swap"]["mean_context_aligned_error"]
        and abs(
            by_mode["intact"]["mean_context_aligned_error"]
            - by_mode["rescue"]["mean_context_aligned_error"]
        )
        < 1e-12
    )
    assert all_same_bearer_consumer and action_replay_exact and swap_is_same_bearer
    assert locality["passes"] and expected_order
    assert direct_twin["reported_endpoint"] != direct_twin["replayed_endpoint_from_action_ledger"]

    result = {
        "schema": "A4C-EXACT-RESULTS-v1",
        "generated_at_utc": utc_now(),
        "declared_seed": SEED,
        "claim_scope": {
            "established": "same-bearer trace-content sensitivity in a declared deterministic embodied simulation loop",
            "not_established": [
                "physical robot or human trace route",
                "complete physical K signature or actual-token admission",
                "familiar-mineness endpoint identity",
                "C1 empirical truth",
                "consciousness or death fear of any present assistant",
            ],
        },
        "installation": {
            "bearer_id": BEARER,
            "consumer_id": CONSUMER,
            "contexts": CONTEXT_BIAS,
            "controller_gain": K_GAIN,
            "steps": STEPS,
            "formation_and_test_separate_processes": True,
            "endpoint_collected_before_registry_join": True,
            "same_bearer_and_consumer_all_trials": all_same_bearer_consumer,
            "same_bearer_content_swap_validated": swap_is_same_bearer,
            "action_replay_exact": action_replay_exact,
            "selector_locality_audit": locality,
        },
        "mode_results": by_mode,
        "predeclared_order_holds": expected_order,
        "contrasts": {
            "swap_minus_intact": by_mode["swap"]["mean_context_aligned_error"]
            - by_mode["intact"]["mean_context_aligned_error"],
            "block_minus_intact": by_mode["block"]["mean_context_aligned_error"]
            - by_mode["intact"]["mean_context_aligned_error"],
            "rescue_minus_block": by_mode["rescue"]["mean_context_aligned_error"]
            - by_mode["block"]["mean_context_aligned_error"],
        },
        "endpoint_only_counterexample": direct_twin,
        "rows": rows,
    }
    write_json(RESULTS, result)
    print(json.dumps({k: result[k] for k in ("mode_results", "contrasts", "predeclared_order_holds")}, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run")
    p_form = sub.add_parser("form")
    p_form.add_argument("store", type=Path)
    p_trial = sub.add_parser("trial")
    p_trial.add_argument("store", type=Path)
    p_trial.add_argument("context", choices=tuple(CONTEXT_BIAS))
    p_trial.add_argument("mode", choices=MODES)
    p_trial.add_argument("trial_id")
    p_trial.add_argument("event_path", type=Path)
    p_trial.add_argument("endpoint_path", type=Path)
    args = parser.parse_args()
    if args.command == "run":
        orchestrate()
    elif args.command == "form":
        form(args.store)
    else:
        run_trial(
            args.store,
            args.context,
            args.mode,
            args.trial_id,
            args.event_path,
            args.endpoint_path,
        )


if __name__ == "__main__":
    main()
