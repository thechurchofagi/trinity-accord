#!/usr/bin/env python3
"""DVC20261010: executed finite shadow-consumer timing model, no hardware I/O.

The plant has its own command path. M is a copy of a device control command;
P is a device encoder/state token. Neither is a human neural input by naming.
Events distinguish source issue, arrival, accepted sample/latch, immutable
snapshot copy, and the designated software consumer's actual modeled reads.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import permutations, product
from pathlib import Path
import hashlib
import json
import platform
import time

LANES = ("M", "P")


@dataclass(frozen=True)
class Token:
    origin_id: str
    lane: str
    epoch: int
    value: int
    claimed_epoch: int


@dataclass(frozen=True)
class Stored:
    event_id: str
    token: Token


@dataclass(frozen=True)
class Snapshot:
    epoch: int
    mask: tuple[int, int]
    slots: tuple[Stored | None, Stored | None]
    event_id: str
    tick: int


class Shadow:
    """Single-threaded reference semantics, not a hardware timing guarantee."""
    def __init__(self):
        self.events = []
        self.port = {lane: None for lane in LANES}
        self.buffer = {lane: None for lane in LANES}
        self.gate = {lane: True for lane in LANES}
        self.last_snapshot = None
        self.epoch = 0
        self.mask = (1, 1)
        self.gate_event = {}
        self.plant_trace = []

    def log(self, kind, tick, *, parents=(), **fields):
        eid = f"ev{len(self.events)}"
        self.events.append({"id": eid, "kind": kind, "tick": tick,
                            "parents": list(parents), **fields})
        return eid

    def source(self, lane, epoch, value, tick, *, claimed_epoch=None):
        eid = self.log("source_issue", tick, lane=lane, epoch=epoch, value=value)
        return Token(eid, lane, epoch, value, epoch if claimed_epoch is None else claimed_epoch)

    def plant(self, command, tick):
        # No shadow register, mask or output is read by this model plant.
        self.plant_trace.append({"tick": tick, "command": command, "position": command})
        self.log("plant_step", tick, command=command, position=command)

    def arrive(self, destination, token, tick):
        eid = self.log("port_arrival", tick, parents=(token.origin_id,),
                       destination=destination, source_lane=token.lane,
                       source_epoch=token.epoch, claimed_epoch=token.claimed_epoch,
                       value=token.value)
        self.port[destination] = Stored(eid, token)

    def set_gate(self, lane, state, tick):
        self.gate[lane] = bool(state)
        self.gate_event[lane] = self.log("capture_gate", tick, lane=lane, open=bool(state))

    def begin(self, epoch, mask, tick, *, invalidate):
        self.epoch = epoch
        self.mask = tuple(mask)
        self.log("trial_begin", tick, epoch=epoch, mask=list(mask), invalidate=invalidate)
        if invalidate:
            for lane in LANES:
                self.buffer[lane] = None
                self.log("buffer_invalidate", tick, lane=lane, epoch=epoch)
        for lane, enabled in zip(LANES, mask):
            self.set_gate(lane, enabled, tick)
        self.last_snapshot = None

    def capture(self, lane, tick):
        # Closed gate is checked before reading the current input token.
        if not self.gate[lane]:
            self.log("capture_blocked", tick, parents=(self.gate_event[lane],), lane=lane)
            return
        item = self.port[lane]
        if item is None:
            self.log("capture_empty", tick, lane=lane)
            return
        eid = self.log("sample_latch", tick, parents=(item.event_id,), lane=lane,
                       source_id=item.token.origin_id, source_epoch=item.token.epoch,
                       source_lane=item.token.lane, value=item.token.value)
        self.buffer[lane] = Stored(eid, item.token)

    def freeze(self, tick):
        # Each copy is made in one model macrostep; actual hardware must
        # implement exclusion/atomic pairing or an equivalent validated scheme.
        cells = []
        for lane in LANES:
            item = self.buffer[lane]
            if item is None:
                self.log("snapshot_absence", tick, lane=lane, epoch=self.epoch)
                cells.append(None)
            else:
                eid = self.log("snapshot_copy", tick, parents=(item.event_id,),
                               lane=lane, source_id=item.token.origin_id,
                               source_epoch=item.token.epoch, value=item.token.value)
                cells.append(Stored(eid, item.token))
        eid = self.log("snapshot_commit", tick,
                       parents=tuple(x.event_id for x in cells if x is not None),
                       epoch=self.epoch, mask=list(self.mask))
        snap = Snapshot(self.epoch, self.mask, tuple(cells), eid, tick)
        self.last_snapshot = snap
        return snap

    @staticmethod
    def validate(snapshot, expected, *, trust_metadata_only=False):
        failures = []
        for index, lane in enumerate(LANES):
            item = snapshot.slots[index]
            if not snapshot.mask[index]:
                if item is not None:
                    failures.append(lane + ":disabled_but_retained_token")
            elif item is None:
                failures.append(lane + ":enabled_but_missing_capture")
            elif trust_metadata_only:
                if item.token.claimed_epoch != snapshot.epoch:
                    failures.append(lane + ":claimed_epoch_mismatch")
            elif (item.token.origin_id != expected[lane].origin_id or
                  item.token.lane != lane or item.token.epoch != snapshot.epoch):
                failures.append(lane + ":wrong_source_token_or_epoch")
        return failures

    def consume(self, tick, *, mode="eager_or", snapshot=None):
        snap = self.last_snapshot if snapshot is None else snapshot
        if snap is None and mode != "bypass_or":
            self.log("consume_without_snapshot", tick)
            return None
        if snap is not None and tick < snap.tick:
            raise ValueError("A snapshot cannot be consumed before its commit.")
        reads = []
        if mode == "gate_reflex":
            # Predictable trial labels replace data: all marker payloads=1 is
            # the restricted family on which this reflex matches the OR task.
            values = []
            for lane in LANES:
                eid = self.log("gate_label_read", tick,
                               parents=(self.gate_event[lane],), lane=lane,
                               value=int(self.gate[lane]))
                reads.append({"lane": lane, "source_id": None, "intake": eid,
                              "value": int(self.gate[lane]), "kind": "gate_label", "read_event": eid})
                values.append(int(self.gate[lane]))
        else:
            values = []
            for index, lane in enumerate(LANES):
                item = self.port[lane] if mode == "bypass_or" else snap.slots[index]
                value = 0 if item is None else item.token.value
                parents = () if item is None else (item.event_id,)
                eid = self.log("absence_default" if item is None else "consumer_read", tick, parents=parents, lane=lane,
                               source_id=None if item is None else item.token.origin_id,
                               source_epoch=None if item is None else item.token.epoch,
                               value=value, interface="port_bypass" if mode == "bypass_or" else "immutable_snapshot")
                reads.append({"lane": lane, "source_id": None if item is None else item.token.origin_id,
                              "source_epoch": None if item is None else item.token.epoch,
                              "source_lane": None if item is None else item.token.lane,
                              "intake": None if item is None else item.event_id,
                              "value": value, "kind": "absence_default" if item is None else "data",
                              "source_supplied": item is not None, "read_event": eid})
                values.append(value)
                if mode == "lazy_or" and value:
                    break
        out = int(all(values)) if mode == "eager_and" else int(any(values))
        self.log("consumer_output", tick, parents=tuple(r["read_event"] for r in reads), output=out, mode=mode)
        return {"output": out, "reads": reads,
                "snapshot_id": None if snap is None else snap.event_id}


def warmed(old_values=(1, 1)):
    d = Shadow()
    old = {lane: d.source(lane, 0, value, -6) for lane, value in zip(LANES, old_values)}
    for lane in LANES:
        d.arrive(lane, old[lane], -5)
    for lane in LANES:
        d.set_gate(lane, 1, -4)
    for lane in LANES:
        d.capture(lane, -3)
    return d, old


def fresh_trial(mask=(1, 1), *, invalidate=True, values=(1, 1)):
    d, old = warmed()
    d.begin(1, mask, 0, invalidate=invalidate)
    tokens = {lane: d.source(lane, 1, value, 0) for lane, value in zip(LANES, values)}
    d.plant(0, 0)
    d.plant(1, 1)
    for lane in LANES:
        d.arrive(lane, tokens[lane], 2)
    for lane in LANES:
        d.capture(lane, 3)
    snap = d.freeze(4)
    return d, old, tokens, snap


def robust_window(a_lo, a_hi, b_lo, b_hi, setup, hold):
    # Port stability is [arrival,departure), sampling aperture is closed.
    # Thus the upper endpoint is strict: s+hold < departure.
    return a_hi + setup, b_lo - hold


def main():
    started = time.time()
    witnesses = []
    counts = {}
    operations = ("arrM", "arrP", "capM", "capP", "freeze", "consume")
    order_count = fresh_count = matched_but_wrong = no_snapshot = 0
    for order in permutations(operations):
        d, _ = warmed()
        d.begin(1, (1, 1), 0, invalidate=False)
        tokens = {lane: d.source(lane, 1, 1, 0) for lane in LANES}
        out = None
        for tick, op in enumerate(order, 1):
            if op.startswith("arr"):
                lane = op[-1]
                d.arrive(lane, tokens[lane], tick)
            elif op.startswith("cap"):
                d.capture(op[-1], tick)
            elif op == "freeze":
                d.freeze(tick)
            else:
                out = d.consume(tick)
        pos = {op: order.index(op) for op in order}
        expected_fresh = (pos["arrM"] < pos["capM"] < pos["freeze"] < pos["consume"]
                          and pos["arrP"] < pos["capP"] < pos["freeze"])
        actual_fresh = (out is not None and len(out["reads"]) == 2 and
                        all(r["source_id"] == tokens[r["lane"]].origin_id for r in out["reads"]))
        assert actual_fresh == expected_fresh
        order_count += 1
        fresh_count += actual_fresh
        if out is None:
            no_snapshot += 1
        elif out["output"] == 1 and not actual_fresh:
            matched_but_wrong += 1
    assert (order_count, fresh_count, no_snapshot, matched_but_wrong) == (720, 6, 360, 354)
    counts["event_order_schedules"] = order_count
    counts["both_current_tokens_consumed"] = fresh_count
    counts["consume_before_commit_rejected"] = no_snapshot
    counts["matched_output_with_wrong_epoch_or_unarrived_probe"] = matched_but_wrong

    # The gate factorial is not the intake factorial with retained old latches.
    gate_rows = []
    plant_references = []
    for mask in product((0, 1), repeat=2):
        raw, _, tokens, snap = fresh_trial(mask, invalidate=False)
        raw_result = raw.consume(5, mode="eager_and")
        fixed, _, ftokens, fsnap = fresh_trial(mask, invalidate=True)
        fixed_result = fixed.consume(5, mode="eager_and")
        assert raw_result["output"] == 1
        assert fixed_result["output"] == int(all(mask))
        assert not fixed.validate(fsnap, ftokens)
        assert bool(raw.validate(snap, tokens)) == (mask != (1, 1))
        gate_rows.append({"configured_mask_MP": list(mask),
                          "retained_buffer_input_values": [r["value"] for r in raw_result["reads"]],
                          "retained_buffer_source_epochs": [r["source_epoch"] for r in raw_result["reads"]],
                          "retained_output_AND": raw_result["output"],
                          "invalidated_input_values": [r["value"] for r in fixed_result["reads"]],
                          "invalidated_output_AND": fixed_result["output"]})
        plant_references.extend((raw.plant_trace, fixed.plant_trace))
    assert all(x == plant_references[0] for x in plant_references)
    counts["gate_factorial_pairs"] = len(gate_rows)
    witnesses.append({"id": "gate_closed_retains_old_latch", "rows": gate_rows,
                      "plant_traces_equal_in_declared_decoupled_model": True})

    # Closing after capture does not revoke a token already latched.
    d, _, tokens, snap = fresh_trial()
    for lane in LANES:
        d.set_gate(lane, 0, 5)
    result = d.consume(6, snapshot=snap)
    assert all(r["source_id"] == tokens[r["lane"]].origin_id for r in result["reads"])
    witnesses.append({"id": "closed_at_consume_but_current_tokens_read",
                      "result": result, "events": d.events})

    # A transmitter issue is not an arrival or a capture receipt.
    d, _ = warmed()
    d.begin(1, (1, 1), 0, invalidate=False)
    tokens = {lane: d.source(lane, 1, 1, 0) for lane in LANES}
    d.arrive("M", tokens["M"], 1)
    d.capture("M", 2)
    d.capture("P", 2)  # P probe has not reached the acquisition port.
    snap = d.freeze(3)
    result = d.consume(4)
    d.arrive("P", tokens["P"], 5)
    assert result["output"] == 1 and d.validate(snap, tokens)
    witnesses.append({"id": "issued_but_not_arrived_probe", "result": result,
                      "failures": d.validate(snap, tokens), "events": d.events})

    # Immutable commit prevents a later capture from changing the consumed pair.
    d, _, tokens, snap = fresh_trial()
    next_token = d.source("P", 2, 1, 5)
    d.arrive("P", next_token, 6)
    d.capture("P", 7)
    stable = d.consume(8, snapshot=snap)
    live_snap = d.freeze(9)
    mixed = d.consume(10, snapshot=live_snap)
    assert [r["source_epoch"] for r in stable["reads"]] == [1, 1]
    assert [r["source_epoch"] for r in mixed["reads"]] == [1, 2]
    assert stable["output"] == mixed["output"]
    assert not d.validate(snap, tokens) and d.validate(live_snap, tokens)
    witnesses.append({"id": "postcommit_overwrite_and_mixed_epochs", "stable": stable,
                      "mixed": mixed, "events": d.events})

    # Epoch labels can be current while physical source identities are swapped.
    d, _ = warmed()
    d.begin(1, (1, 1), 0, invalidate=True)
    tokens = {lane: d.source(lane, 1, 1, 0) for lane in LANES}
    for dest, source in (("M", "P"), ("P", "M")):
        d.arrive(dest, tokens[source], 1)
    for dest in LANES:
        d.capture(dest, 2)
    snap = d.freeze(3)
    result = d.consume(4)
    assert not d.validate(snap, tokens, trust_metadata_only=True)
    assert len(d.validate(snap, tokens)) == 2 and result["output"] == 1
    witnesses.append({"id": "epoch_valid_but_source_ports_swapped", "result": result,
                      "strict_failures": d.validate(snap, tokens), "events": d.events})

    # Updating packet metadata cannot make the ancestral token a new command.
    d, old = warmed()
    d.begin(1, (1, 1), 0, invalidate=True)
    tokens = {lane: d.source(lane, 1, 1, 0) for lane in LANES}
    d.log("metadata_relabel", 0, parents=(old["P"].origin_id,), claimed_epoch=1)
    stale = Token(old["P"].origin_id, old["P"].lane, old["P"].epoch, old["P"].value, 1)
    d.arrive("M", tokens["M"], 1)
    d.arrive("P", stale, 1)
    for lane in LANES:
        d.capture(lane, 2)
    snap = d.freeze(3)
    result = d.consume(4)
    assert not d.validate(snap, tokens, trust_metadata_only=True)
    assert d.validate(snap, tokens) == ["P:wrong_source_token_or_epoch"]
    witnesses.append({"id": "stale_origin_with_current_epoch_header", "result": result,
                      "strict_failures": d.validate(snap, tokens), "events": d.events})

    # A gate-label reflex copies every nominal gate-factorial output; a payload
    # perturbation can reject this displayed alternative, not arbitrary rivals.
    reflex_rows = []
    for mask in product((0, 1), repeat=2):
        d, _, tokens, snap = fresh_trial(mask)
        actual = d.consume(5)
        reflex = d.consume(6, mode="gate_reflex")
        assert actual["output"] == reflex["output"]
        assert all(r["source_id"] is None for r in reflex["reads"])
        reflex_rows.append({"mask": list(mask), "output": actual["output"],
                            "actual_sources": [r["source_id"] for r in actual["reads"]],
                            "reflex_sources": [r["source_id"] for r in reflex["reads"]]})
    d, _, _, _ = fresh_trial((1, 0), values=(0, 1))
    a, b = d.consume(5), d.consume(6, mode="gate_reflex")
    assert (a["output"], b["output"]) == (0, 1)
    witnesses.append({"id": "gate_label_reflex", "nominal_factorial": reflex_rows,
                      "payload_challenge_outputs": [a["output"], b["output"]]})

    # Bypass agrees in value while reading a different carrier stage.
    d, _, tokens, snap = fresh_trial()
    actual, bypass = d.consume(5), d.consume(6, mode="bypass_or")
    assert actual["output"] == bypass["output"]
    assert [r["intake"] for r in actual["reads"]] != [r["intake"] for r in bypass["reads"]]
    witnesses.append({"id": "port_bypass_same_output_different_intakes", "snapshot": actual,
                      "bypass": bypass, "events": d.events})

    # Robust timing: independent interval uncertainty, no statistical premise.
    window_cases = 0
    safe_windows = []
    for a_lo in range(3):
        for a_hi in range(a_lo, 4):
            for b_lo in range(a_hi + 1, 7):
                for b_hi in range(b_lo, 8):
                    for setup, hold in product(range(2), repeat=2):
                        lower, upper = robust_window(a_lo, a_hi, b_lo, b_hi, setup, hold)
                        for sample in range(9):
                            exhaustive = all(a <= sample - setup and sample + hold < b
                                             for a in range(a_lo, a_hi + 1)
                                             for b in range(b_lo, b_hi + 1))
                            formula = lower <= sample < upper
                            assert exhaustive == formula
                            window_cases += 1
                        if lower < upper:
                            safe_windows.append((lower, upper))
    counts["robust_window_parameter_sample_checks"] = window_cases
    paired_windows = 0
    unique = sorted(set(safe_windows))
    for (l_m, u_m), (l_p, u_p) in product(unique, repeat=2):
        simultaneous = any(l_m <= t < u_m and l_p <= t < u_p for t in range(9))
        assert simultaneous == (max(l_m, l_p) < min(u_m, u_p))
        independent = any(l_m <= m < u_m and l_p <= p < u_p
                          for m, p in product(range(9), repeat=2))
        assert independent
        paired_windows += 1
    counts["paired_nonempty_safe_window_cases"] = paired_windows

    # There need be no common sample time: preserve command e until encoder e
    # arrives, then consume their immutable same-epoch pair after both captures.
    d, _ = warmed()
    d.begin(1, (1, 1), 0, invalidate=True)
    tokens = {lane: d.source(lane, 1, 1, 0) for lane in LANES}
    next_m = d.source("M", 2, 1, 0)
    next_p = d.source("P", 2, 1, 0)
    d.arrive("M", tokens["M"], 2)
    d.capture("M", 3)
    d.arrive("M", next_m, 4)
    d.arrive("P", tokens["P"], 6)
    d.capture("P", 7)
    d.arrive("P", next_p, 8)
    snap = d.freeze(8)
    result = d.consume(9)
    assert not d.validate(snap, tokens)
    assert all(r["source_epoch"] == 1 for r in result["reads"])
    assert max(2, 6) >= min(4, 8)
    witnesses.append({"id": "disjoint_capture_windows_same_epoch_join",
                      "M_port_valid_window": [2, 4], "P_port_valid_window": [6, 8],
                      "interval_semantics": "half-open [start,end); zero aperture in this trace",
                      "no_common_sample_time": True, "result": result, "events": d.events})

    # P_e generated by consequence Y_e cannot be consumed before Y_e; a
    # pre-consequence predictor must instead use earlier state or target Y_{e+1}.
    chronological_cases = 0
    for y_tick in range(4):
        for p_latency in range(1, 4):
            for capture_latency in range(3):
                for consume_latency in range(3):
                    p_tick = y_tick + p_latency
                    capture_tick = p_tick + capture_latency
                    consume_tick = capture_tick + consume_latency
                    assert consume_tick > y_tick
                    chronological_cases += 1
    counts["current_consequence_encoder_chronology_cases"] = chronological_cases


    # The trace is a total execution order. Equal ticks use append order;
    # event parents always precede children. Validate the retained evidence.
    for witness in witnesses:
        trace = witness.get("events", [])
        assert [e["tick"] for e in trace] == sorted(e["tick"] for e in trace)
        preceding = set()
        for event in trace:
            assert set(event["parents"]) <= preceding
            preceding.add(event["id"])

    result = {"module_id": "DVC20261010", "result_id": "DVC-RESULT-v0.1.0",
              "status": "PASS", "violations": 0, "counts": counts,
              "execution_type": "Python finite event simulation and independent temporal formulas",
              "hardware_accessed": False, "human_participants": 0,
              "phenomenal_variables_generated": False,
              "primary_endpoint_design_only": "PSE from tactile comparison; sigma/JND separate; agency/ownership/H not measured",
              "witnesses": witnesses}
    here = Path(__file__).resolve().parent
    data = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    (here / "EXACT_RESULTS.json").write_text(data)
    receipt = {"module_id": result["module_id"], "result_id": result["result_id"],
               "command": "python model.py", "python": platform.python_version(),
               "elapsed_seconds": round(time.time() - started, 6), "status": "PASS",
               "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "result_sha256": hashlib.sha256(data.encode()).hexdigest(),
               "hardware_accessed": False, "human_participants": 0,
               "remote_save_verified_by_this_worker": False}
    (here / "RUN_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "counts": counts,
                      "witness_count": len(witnesses), "elapsed_seconds": receipt["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
