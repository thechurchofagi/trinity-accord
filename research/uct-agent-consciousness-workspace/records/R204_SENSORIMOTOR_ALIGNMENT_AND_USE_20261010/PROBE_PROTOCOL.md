# R204 probe protocol v0.2 — software mechanism, not H calibration

Fixed maps, ports and chronological interval: target t→controller C→action a→plant P→outcome y; predictor F reads a; the named U consumer may write the F carrier after y; later query uses that same row. Freeze P and C during the quartet. Do not classify a static table as an actual historical token.

1. Initialize P=C=id on two ports; choose F=id or swap and U=0 or 1 before the episode.
2. Run both targets and confirm exact matching initial task output.
3. Feed veridical outcome for action 0; inspect before/after predictor state.
4. Restore the identical initial state, inject z≠F(0) at the feedback port, and inspect the same carrier. The blocked-writer control must preserve F.
5. Copy full current causal state into a fresh implementation; future probe traces should match. Record actual copy/history metadata separately; do not infer RetBind or H.

Falsifiers: under the specified closed implementation, a change with writer disabled refutes sole-writer/no-alternative premises; absence of change with enabled writer plus a valid nonmatching input refutes the update/readout contract. A null natural error is uninformative about use when prediction is correct. The intervention and readout require separate instrumentation checks.

The executed Python checker implements these operations. Its results are model-level evidence, not tests on humans. Translation to humans requires instruments for the actual named carrier/consumer plus independent semantics; no claimed brain predictor has been selected.

Comparator control: error-gated and unconditional reflex writers have the same F-state law. Add a validated write-event or comparator-intervention port if distinguishing those implementations is the claim; the minimal quartet cannot certify an error consumer.
