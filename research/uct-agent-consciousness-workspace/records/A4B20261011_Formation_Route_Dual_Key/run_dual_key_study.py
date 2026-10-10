#!/usr/bin/env python3
"""A4B exact countermodels and an installed software formation/route study.

The installation is deliberately narrow.  It establishes a persistent
software trace, a later exact read by a named consumer, and an independently
randomized read-block intervention.  It does not identify a complete physical
UCT signature or a phenomenal endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
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
SEED = 2026101101
BEARER = "A4B-software-bearer-v1"
CONSUMER = "A4B-later-consumer-v1"


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


def form(trace_path: Path, assignment: int, bearer: str, trial: str) -> None:
    payload = {
        "schema": "A4B-TRACE-v1",
        "bearer_id": bearer,
        "carrier_id": f"{bearer}:persistent-json-carrier",
        "formation_event_id": str(uuid.uuid4()),
        "formation_assignment": assignment,
        "retained_value": assignment,
        "trial_id": trial,
        "formed_at_utc": utc_now(),
    }
    envelope = {"payload": payload, "payload_sha256": digest(payload)}
    write_json(trace_path, envelope)


def validate_trace(envelope: dict, expected_bearer: str, expected_trial: str) -> tuple[bool, str]:
    payload = envelope.get("payload", {})
    if envelope.get("payload_sha256") != digest(payload):
        return False, "digest_mismatch"
    if payload.get("bearer_id") != expected_bearer:
        return False, "bearer_mismatch"
    if payload.get("trial_id") != expected_trial:
        return False, "trial_mismatch"
    if payload.get("schema") != "A4B-TRACE-v1":
        return False, "schema_mismatch"
    return True, "accepted"


def test(trace_path: Path, block_read: int, bearer: str, trial: str, output: Path) -> None:
    event = {
        "consumer_id": CONSUMER,
        "bearer_id": bearer,
        "trial_id": trial,
        "block_read": block_read,
        "tested_at_utc": utc_now(),
        "trace_path": str(trace_path.relative_to(ROOT)),
    }
    if block_read:
        event.update(
            trace_opened=False,
            trace_validated=False,
            validation_reason="read_blocked_by_assignment",
            consumed_value=0,
            endpoint_j_org=0,
        )
    else:
        envelope = read_json(trace_path)
        valid, reason = validate_trace(envelope, bearer, trial)
        event.update(
            trace_opened=True,
            trace_validated=valid,
            validation_reason=reason,
            trace_payload_sha256=envelope.get("payload_sha256"),
        )
        if not valid:
            event.update(consumed_value=None, endpoint_j_org=None)
        else:
            value = int(envelope["payload"]["retained_value"])
            event.update(consumed_value=value, endpoint_j_org=value)
    write_json(output, event)


def run_subprocess(*args: str) -> None:
    subprocess.run([sys.executable, str(Path(__file__).resolve()), *args], check=True)


def mean(rows: list[dict], key: str = "endpoint_j_org") -> float:
    return sum(float(row[key]) for row in rows) / len(rows)


def logical_countermodels() -> list[dict]:
    models = []
    for model_id in ("A", "B", "C", "D"):
        cells = []
        for f in (0, 1):
            for d in (0, 1):
                if model_id == "A":
                    j, route_used = f, False
                elif model_id == "B":
                    retained = f if d == 0 else 0
                    j, route_used = retained ^ f, True
                elif model_id == "C":
                    retained = f if d == 0 else 0
                    j, route_used = retained, True
                else:
                    j, route_used = 0, False
                cells.append({"F": f, "D_block": d, "J": j})
        lookup = {(x["F"], x["D_block"]): x["J"] for x in cells}
        tau_intact = lookup[(1, 0)] - lookup[(0, 0)]
        route_interaction = (lookup[(1, 0)] - lookup[(1, 1)]) - (
            lookup[(0, 0)] - lookup[(0, 1)]
        )
        models.append(
            {
                "model": model_id,
                "cells": cells,
                "formation_effect_in_intact_regime": tau_intact,
                "route_gate_interaction": route_interaction,
                "route_structurally_used": route_used,
            }
        )
    return models


def orchestrate() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)

    primary_assignments = [0] * 8 + [1] * 8
    rng.shuffle(primary_assignments)
    primary_rows = []
    for index, f in enumerate(primary_assignments):
        trial = f"primary-{index:02d}"
        trial_dir = ARTIFACTS / trial
        trace_path = trial_dir / "trace.json"
        output = trial_dir / "test_event.json"
        run_subprocess("form", str(trace_path), str(f), BEARER, trial)
        run_subprocess("test", str(trace_path), "0", BEARER, trial, str(output))
        row = read_json(output)
        row["F"] = f
        primary_rows.append(row)

    factorial = [(f, d) for f in (0, 1) for d in (0, 1) for _ in range(4)]
    rng.shuffle(factorial)
    diagnostic_rows = []
    for index, (f, d) in enumerate(factorial):
        trial = f"diagnostic-{index:02d}"
        trial_dir = ARTIFACTS / trial
        trace_path = trial_dir / "trace.json"
        output = trial_dir / "test_event.json"
        run_subprocess("form", str(trace_path), str(f), BEARER, trial)
        run_subprocess("test", str(trace_path), str(d), BEARER, trial, str(output))
        row = read_json(output)
        row.update(F=f, D_block=d)
        diagnostic_rows.append(row)

    p0 = [x for x in primary_rows if x["F"] == 0]
    p1 = [x for x in primary_rows if x["F"] == 1]
    cell_means = {}
    for f in (0, 1):
        for d in (0, 1):
            cell_means[f"F{f}_D{d}"] = mean(
                [x for x in diagnostic_rows if x["F"] == f and x["D_block"] == d]
            )
    interaction = (cell_means["F1_D0"] - cell_means["F1_D1"]) - (
        cell_means["F0_D0"] - cell_means["F0_D1"]
    )

    challenge_dir = ARTIFACTS / "copy_challenge"
    source_trace = challenge_dir / "source_trace.json"
    copied_trace = challenge_dir / "equal_value_foreign_trace.json"
    run_subprocess("form", str(source_trace), "1", BEARER, "copy-challenge")
    foreign = read_json(source_trace)
    foreign["payload"]["bearer_id"] = "foreign-bearer-same-value"
    foreign["payload"]["carrier_id"] = "foreign-bearer-same-value:persistent-json-carrier"
    foreign["payload_sha256"] = digest(foreign["payload"])
    write_json(copied_trace, foreign)
    accepted, reason = validate_trace(foreign, BEARER, "copy-challenge")

    all_read_events_valid = all(
        x["trace_opened"] and x["trace_validated"] for x in primary_rows
    ) and all(
        (not x["trace_opened"]) if x["D_block"] else x["trace_validated"]
        for x in diagnostic_rows
    )
    countermodels = logical_countermodels()
    observed_quadrants = {
        (
            x["formation_effect_in_intact_regime"] != 0,
            x["route_structurally_used"],
        )
        for x in countermodels
    }
    assert observed_quadrants == {(False, False), (False, True), (True, False), (True, True)}
    assert interaction == 1.0 and mean(p1) - mean(p0) == 1.0
    assert not accepted and reason == "bearer_mismatch"

    result = {
        "schema": "A4B-EXACT-RESULTS-v1",
        "generated_at_utc": utc_now(),
        "declared_seed": SEED,
        "claim_scope": {
            "established": "declared software-bearer formation effect and exact later trace route",
            "not_established": [
                "complete physical UCT signature",
                "human or biological route",
                "phenomenal endpoint identity",
                "C1 empirical truth",
                "consciousness of any present assistant",
            ],
        },
        "logical_independence": {
            "models": countermodels,
            "all_four_truth_value_quadrants_realized": True,
            "conclusion": "formation effect and actual route use are logically independent",
        },
        "installed_study": {
            "bearer_id": BEARER,
            "consumer_id": CONSUMER,
            "primary_intact_block": {
                "n": len(primary_rows),
                "balanced_randomized_assignment": True,
                "mean_F0": mean(p0),
                "mean_F1": mean(p1),
                "randomized_total_effect_in_declared_intact_regime": mean(p1) - mean(p0),
            },
            "independent_route_probe": {
                "n": len(diagnostic_rows),
                "balanced_randomized_F_by_D": True,
                "cell_means": cell_means,
                "formation_by_route_gate_interaction": interaction,
                "all_read_and_block_events_conform": all_read_events_valid,
            },
            "equal_value_copy_challenge": {
                "same_retained_value": True,
                "foreign_copy_accepted_as_original": accepted,
                "rejection_reason": reason,
            },
            "same_event_route_verified": all_read_events_valid and interaction == 1.0,
        },
        "rows": {"primary": primary_rows, "diagnostic": diagnostic_rows},
    }
    write_json(RESULTS, result)
    print(json.dumps(result["installed_study"], indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run")
    p_form = sub.add_parser("form")
    p_form.add_argument("trace_path", type=Path)
    p_form.add_argument("assignment", type=int, choices=(0, 1))
    p_form.add_argument("bearer")
    p_form.add_argument("trial")
    p_test = sub.add_parser("test")
    p_test.add_argument("trace_path", type=Path)
    p_test.add_argument("block_read", type=int, choices=(0, 1))
    p_test.add_argument("bearer")
    p_test.add_argument("trial")
    p_test.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "run":
        orchestrate()
    elif args.command == "form":
        form(args.trace_path, args.assignment, args.bearer, args.trial)
    else:
        test(args.trace_path, args.block_read, args.bearer, args.trial, args.output)


if __name__ == "__main__":
    main()
