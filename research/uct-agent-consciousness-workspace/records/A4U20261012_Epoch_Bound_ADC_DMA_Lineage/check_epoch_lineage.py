#!/usr/bin/env python3
"""Exact finite checks for the disabled A4U epoch-bound lineage contract.

This is an audit model, not a hardware execution or a proof of RP2040 silicon.
"""

from itertools import product
import json
from pathlib import Path


PREMISES = (
    "known_empty_start",
    "fixed_source_schedule",
    "adc_fifo_dreq_binding",
    "no_fifo_loss",
    "linear_unwrapped_destination",
    "alternate_writer_closure",
    "read_before_reuse",
)


def lineage_for(bits):
    """Return the modeled origin of destination slot 1.

    Each failed premise is assigned one explicit adversarial witness. All
    payload values are deliberately identical, so value inspection cannot
    distinguish the modeled origins.
    """
    state = dict(zip(PREMISES, bits))
    origin = "epoch0:adc:channel0:conversion1"
    failure = None
    if not state["known_empty_start"]:
        origin, failure = "epoch-1:stale-fifo", "stale_fifo_shift"
    elif not state["fixed_source_schedule"]:
        origin, failure = "epoch0:adc:channel1:conversion0", "round_robin_fanin"
    elif not state["adc_fifo_dreq_binding"]:
        origin, failure = "epoch0:unrelated-bus-source", "wrong_dma_source_or_pacing"
    elif not state["no_fifo_loss"]:
        origin, failure = "none:dropped-conversion", "fifo_overflow_or_underflow"
    elif not state["linear_unwrapped_destination"]:
        origin, failure = "epoch0:adc:channel0:conversion2", "ring_wrap_overwrite"
    elif not state["alternate_writer_closure"]:
        origin, failure = "epoch0:alternate-writer", "alternate_writer_overwrite"
    elif not state["read_before_reuse"]:
        origin, failure = "epoch1:adc:channel0:conversion1", "late_read_after_reuse"
    return origin, failure


def run():
    worlds = []
    for bits in product((False, True), repeat=len(PREMISES)):
        origin, failure = lineage_for(bits)
        route = origin == "epoch0:adc:channel0:conversion1"
        worlds.append(
            {
                "premises": dict(zip(PREMISES, bits)),
                "observed_payload": "0x555",
                "observed_terminal_registers": {
                    "dma_transfer_count_remaining": 0,
                    "dma_busy": False,
                    "adc_ready": True,
                    "fifo_level_after_cleanup": 0,
                },
                "slot1_origin": origin,
                "failure": failure,
                "epoch_bound_route": route,
            }
        )

    route_worlds = [w for w in worlds if w["epoch_bound_route"]]
    nonroute_worlds = [w for w in worlds if not w["epoch_bound_route"]]
    assert len(worlds) == 128
    assert len(route_worlds) == 1
    assert len(nonroute_worlds) == 127
    assert {w["observed_payload"] for w in worlds} == {"0x555"}
    assert len({json.dumps(w["observed_terminal_registers"], sort_keys=True) for w in worlds}) == 1

    # Constructive queue-order check under the complete contract.
    induction_checks = []
    for n in range(1, 9):
        fifo = [f"epoch0:adc:channel0:conversion{k}" for k in range(n)]
        memory = []
        while fifo:
            memory.append(fifo.pop(0))
        expected = [f"epoch0:adc:channel0:conversion{k}" for k in range(n)]
        ok = memory == expected
        assert ok
        induction_checks.append({"n": n, "order_preserved": ok})

    drop_one = {}
    for premise in PREMISES:
        bits = [True] * len(PREMISES)
        bits[PREMISES.index(premise)] = False
        origin, failure = lineage_for(bits)
        assert origin != "epoch0:adc:channel0:conversion1"
        drop_one[premise] = {"witness": failure, "slot1_origin": origin}

    # Explicit observational twin requested by the research question.
    shared_observation = {
        "buffer_values": ["0x555", "0x555"],
        "dma_transfer_count_remaining": 0,
        "dma_busy": False,
        "adc_ready": True,
        "fifo_level_after_cleanup": 0,
        "consumer_value": "0x555",
    }
    observational_twin = {
        "drained_start": {
            "observation": shared_observation,
            "buffer_lineage": [
                "epoch0:adc:channel0:conversion0",
                "epoch0:adc:channel0:conversion1",
            ],
            "target_reached_consumer": True,
        },
        "stale_start_then_cleanup": {
            "observation": shared_observation,
            "buffer_lineage": [
                "epoch-1:stale-fifo",
                "epoch0:adc:channel0:conversion0",
            ],
            "target_reached_consumer": False,
        },
    }
    assert observational_twin["drained_start"]["observation"] == observational_twin["stale_start_then_cleanup"]["observation"]

    return {
        "schema": "a4u-epoch-lineage-exact-results/1",
        "model_status": "FINITE_AUDIT_MODEL_NOT_HARDWARE_EXECUTION",
        "premises": list(PREMISES),
        "world_count": len(worlds),
        "epoch_bound_route_worlds": len(route_worlds),
        "nonroute_worlds": len(nonroute_worlds),
        "all_worlds_payload_equal": True,
        "all_worlds_terminal_registers_equal": True,
        "constructive_fifo_lengths_checked": induction_checks,
        "drop_one_witnesses": drop_one,
        "observational_twin": observational_twin,
        "interpretive_limit": "The enumeration proves only the declared finite model and the constructive queue-order check. It neither verifies an RP2040 run nor establishes a UCT experiential bridge.",
    }


if __name__ == "__main__":
    result = run()
    target = Path(__file__).with_name("EXACT_RESULTS.json")
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("world_count", "epoch_bound_route_worlds", "nonroute_worlds")}, sort_keys=True))
