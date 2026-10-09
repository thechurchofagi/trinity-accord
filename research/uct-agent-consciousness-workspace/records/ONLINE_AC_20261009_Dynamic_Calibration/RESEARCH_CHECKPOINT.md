# Dynamic action calibration: the five-port uncertainty invariant

**Result:** ONLINE-AC-RESULT-v0.2.0. **Record:** ONLINE-AC-PROBE-20261009.  
**Date:** 2026-10-09. **Publication coverage:** UCT-PUB-v1.0.0.  
**Status:** locally proved and independently checked mathematical result; PENDING_MAP.  
**Manuscript:** ONLINE-AC-PAPER-v0.1.0, complete scoped working paper; no new formal publication.

## Current decision and exact increment

The version 0.1.0 note established an old-wiring injectivity requirement for one-probe adaptation, a two-round obstruction from known initial wiring, and the exact three-port value 7/8. Those precise results and their actual verifier are preserved. The note's original call for independent review and its unresolved n>=5 question are historical states, not the latest disposition.

Version 0.2.0 resolves the first open case, n=5: a uniform cap of two physical binary-vector probes per round sustains one fixed unit goal at every finite horizon under arbitrary identity-or-one-transposition drift between rounds. Complete current-wiring identification under the same initial knowledge and drift contract requires three probes. The positive controller preserves exact singleton beliefs or a pair of wirings differing by a non-goal transposition. It deliberately permits unresolved wiring while retaining a repairable uncertainty state.

The compact proof consists of two canonical decision tables, transport by relabeling, and induction over a closed family of 480 beliefs. A discovered controller has 240 reachable beliefs. A different deterministic implementation obtained by canonicalizing the two templates has 260 reachable beliefs. These are two valid implementations; neither count is a minimal-memory claim, and the 480-element proof family is not asserted to be entirely reachable.

This specific positive result, together with the matched lower bounds and three-port benchmark, now supports one focused technical working paper. This changes the earlier dynamic-note HOLD assessment, not the R188 standalone HOLD decision. Ordinary binary coding, indistinguishable-world proofs, belief-state control and inductive closure are credited as inherited methods. UCT III section6.4 Proposition6 already covers the general transition-closure issue. Global historical priority remains UNVERIFIED.

## Full proofs and reusable interface

Read [PAPER.md](PAPER.md), especially sections2-6, for the self-contained contract, all proofs and both canonical tables. The precise question is continued net-goal action, not retained target content or experience. A probe and terminal vector physically toggle the same XOR plant; every round's net increment must equal e_g. All effect vectors are returned, every old wiring and allowed change must be considered for zero-error claims, and wiring is fixed during the round. Successful terminal feedback is determined by the preceding probe effects and e_g, so it gives no extra identification on a guaranteed-success leaf.

The one-probe n! state bound applies only when the admitted uncertain old-wiring family is the full symmetric group. For a known initial identity that family is a singleton, and no such initial memory burden follows. The three-port 7/8 result is an exact average over 16 equally weighted fixed two-round drift sequences; it is not a per-sequence guarantee or a final-plant-state score. The five-port two-probe result is a worst-case uniform per-round cap, not an average-use lower bound.

## Actual evidence

- `next_probe/check_online_calibration.py` and `EXACT_RESULTS.json`: executed exact policy optimization and attaining traces; actual corrected-run receipt retained. Independent manual proof reviews and a separate trace replay are in `reviews/` and `next_probe/`.
- `next_probe_n5/search_sustainable.py` and `SEARCH_RESULTS.json`: actual bounded discovery through horizons1-6. Positive finite horizons were not used as an indefinite proof.
- `next_probe_n5/extract_closed_controller.py` and `CLOSED_CONTROLLER.json`: actual stationary-policy extraction closed at240 states. Lookahead selected a witness; explicit closure is what permits induction.
- `next_probe_n5/verify_closed_controller_independent.py` and `CERTIFICATE_INDEPENDENT_VALIDATION.json`: separately implemented verification of all240 states,3960 old/drift worlds,3360 exact posterior leaves and126720 world/plant-state runs. No discovery recursion imported.
- `next_probe_n5/CANONICAL_TEMPLATES.json` and `CANONICAL_TABLES.md`: extracted proof tables,33 old/drift worlds and28 observation leaves.
- `next_probe_n5/canonical_transport_independent.py` and `CANONICAL_TRANSPORT_INDEPENDENT_VALIDATION.json`: independent field-by-field template comparison and transport across all480 beliefs,9240 old/drift worlds and7680 exact posterior leaves. This verifier replays one nonzero plant initial state per world; translation-independent XOR algebra and the earlier all32-state verifier have separate evidence scopes.

The independent review reports bind the exact manuscript, code and source hashes. The new result is not an empirical agent experiment, and none of R188's old computation was rerun in this task.

## Map, publication and remaining obligations

The current scientific map remains UCT-MAP-v1.1.2 with 1608 review objects. The candidate module has stable claim IDs, explicit dependencies and disabled status. Relevant prior proofs and shared-interface compatibility were independently reviewed; a new complete1608-item semantic integration pass and all downstream rederivations have not been completed for this module. Do not call this a completed v1.1.3 release or use pending claims as already enabled scientific premises.

Paper completion is distinct from actual publication. The coverage ledger records the paper as a new working manuscript and keeps the verified publication census unchanged. No DOI, OTS or Arweave action was performed. A formal release must first satisfy the existing map/publication requirements and preserve precise prior attribution.

The next mathematical unknown is the minimum sustainable probe budget for n>=6, under this exact contract. It remains between2 and ceil(log2 n). Nothing here proves a universal two-probe strategy, a lower memory requirement, a biological calibration mechanism, a measure of experience, or a named experiential bridge. QC10, IA-QC11, QC12 and QC13 remain open.
