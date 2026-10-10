#!/usr/bin/env python3
"""Exact finite checks for the A3R selector-participation contract.

This is an intentionally small structural-causal model, not a model of a
particular biological or artificial selector.  It tests logical separation of
weak dispatch/log evidence from a conjunctive same-instance certificate.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


OUT = Path(__file__).with_name("EXACT_RESULTS.json")


def episode(cfg: dict[str, int], loser_value: int) -> dict[str, object]:
    """Evaluate one episode under a controlled losing-token value."""
    live_value = loser_value if cfg["live_loser"] else 0
    resolver_loser = live_value if cfg["resolver_reads_loser"] else 0
    # The public log can be a faithful resolver trace or a side-recorder copy.
    logged_loser = live_value if cfg["log_side_copy"] else resolver_loser

    # Winner policy is fixed at 1.  The resolution-to-dispatch edge and a
    # direct bypass are explicit and independently variable.
    dispatch = int(bool(cfg["resolution_mediates"] or cfg["direct_bypass"]))
    dispatch_after_resolution_cut = int(bool(cfg["direct_bypass"]))
    dispatch_after_faithful_replay = int(
        bool(cfg["direct_bypass"] or (cfg["resolution_mediates"] and cfg["replay_faithful"]))
    )

    return {
        "dispatch": dispatch,
        "public_log": [1, logged_loser],
        "validated_resolver_port": [1, resolver_loser],
        "dispatch_after_resolution_cut": dispatch_after_resolution_cut,
        "dispatch_after_faithful_replay": dispatch_after_faithful_replay,
    }


def target(cfg: dict[str, int]) -> bool:
    """Bounded target: live loser is locally read and resolution is necessary."""
    return bool(
        cfg["live_loser"]
        and cfg["same_event_clock"]
        and cfg["resolver_reads_loser"]
        and cfg["resolution_mediates"]
        and not cfg["direct_bypass"]
    )


def certificate(cfg: dict[str, int]) -> bool:
    e0, e1 = episode(cfg, 0), episode(cfg, 1)
    return bool(
        cfg["live_loser"]
        and cfg["same_event_clock"]
        and cfg["readout_validated"]
        and e0["validated_resolver_port"] != e1["validated_resolver_port"]
        and e1["dispatch_after_resolution_cut"] == 0
        and cfg["replay_faithful"]
        and e1["dispatch_after_faithful_replay"] == e1["dispatch"] == 1
    )


def weak_signature(cfg: dict[str, int]) -> tuple[object, ...]:
    """Dispatch plus unvalidated public log under loser 0/1 interventions."""
    result: list[object] = []
    for value in (0, 1):
        e = episode(cfg, value)
        result.extend([e["dispatch"], tuple(e["public_log"])])
    return tuple(result)


def main() -> None:
    names = [
        "live_loser",
        "same_event_clock",
        "resolver_reads_loser",
        "resolution_mediates",
        "direct_bypass",
        "log_side_copy",
        "readout_validated",
        "replay_faithful",
    ]
    configs = [dict(zip(names, bits)) for bits in itertools.product((0, 1), repeat=len(names))]

    targets = [c for c in configs if target(c)]
    certs = [c for c in configs if certificate(c)]
    false_positive = [c for c in certs if not target(c)]
    false_negative = [c for c in targets if not certificate(c)]

    classes: dict[tuple[object, ...], list[dict[str, int]]] = {}
    for cfg in configs:
        classes.setdefault(weak_signature(cfg), []).append(cfg)
    mixed = [members for members in classes.values() if {target(c) for c in members} == {False, True}]

    use = {
        "live_loser": 1,
        "same_event_clock": 1,
        "resolver_reads_loser": 1,
        "resolution_mediates": 1,
        "direct_bypass": 0,
        "log_side_copy": 0,
        "readout_validated": 1,
        "replay_faithful": 1,
    }
    ignore = {
        "live_loser": 1,
        "same_event_clock": 1,
        "resolver_reads_loser": 0,
        "resolution_mediates": 0,
        "direct_bypass": 1,
        "log_side_copy": 1,
        "readout_validated": 0,
        "replay_faithful": 0,
    }
    assert weak_signature(use) == weak_signature(ignore)
    assert target(use) and certificate(use)
    assert not target(ignore) and not certificate(ignore)
    assert not false_positive

    payload = {
        "schema": "uct-a3r-exact-results/1",
        "research_id": "A3R20261010",
        "model_scope": {
            "boolean_factors": names,
            "configurations": len(configs),
            "losing_token_interventions_per_configuration": 2,
            "episodes_evaluated": 2 * len(configs),
            "fixed": [
                "one live winner token",
                "winner and loser routes mutually exclusive under frozen rho",
                "one declared resolver window",
            ],
        },
        "counts": {
            "target_true": len(targets),
            "certificate_true": len(certs),
            "certificate_false_positives": len(false_positive),
            "target_without_full_certificate": len(false_negative),
            "weak_observation_classes": len(classes),
            "weak_classes_mixing_target_and_nontarget": len(mixed),
            "configurations_in_mixed_weak_classes": sum(len(m) for m in mixed),
        },
        "theorems_checked": {
            "A3R_T1_dispatch_log_nonidentification": bool(mixed),
            "A3R_T2_certificate_sound_in_declared_model": not false_positive,
            "A3R_T3_certificate_not_necessary_without_validation_premises": bool(false_negative),
        },
        "canonical_observational_twins": {
            "actual_joint_consumption": {
                "configuration": use,
                "weak_signature": weak_signature(use),
                "episodes": [episode(use, 0), episode(use, 1)],
                "target": target(use),
                "certificate": certificate(use),
            },
            "side_recorder_plus_bypass": {
                "configuration": ignore,
                "weak_signature": weak_signature(ignore),
                "episodes": [episode(ignore, 0), episode(ignore, 1)],
                "target": target(ignore),
                "certificate": certificate(ignore),
            },
        },
        "interpretive_limits": [
            "Finite-model implication is not physical installation.",
            "The certificate is sufficient in this declared family, not necessary for every selector architecture.",
            "A failed or invalid certificate does not imply no experience, mineness, intelligence, or policy use by another mechanism.",
        ],
    }
    encoded = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    OUT.write_text(encoded, encoding="utf-8")
    print(json.dumps(payload["counts"], sort_keys=True))
    print("sha256", hashlib.sha256(encoded.encode()).hexdigest())


if __name__ == "__main__":
    main()
