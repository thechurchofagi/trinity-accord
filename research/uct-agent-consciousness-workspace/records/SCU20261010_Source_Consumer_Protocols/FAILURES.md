# SCU20261010 failures, rejected interpretations, and corrections

## Scientific candidates rejected by explicit constructions

1. **Nominal success and zero prediction error identify shared source.** Rejected: all nine three-source allocations match every nominal target word, including the forward-table state trace.
2. **The logarithmic single-source protocol works with arbitrary redundancy.** Rejected: a four-source actuator using `{3}` and predictor using `{1,2}` through OR return zero mismatch for the two-bit code, despite disjoint root sets. Unit probes expose the difference. Correct scope: pure-route pair equality `ceil(log2 n)`; arbitrary nonempty OR-set equality `n`, for `n>=2`.
3. **`ceil(log2 n)` is the universal bound even when the actuator source is known.** Rejected before implementation following the parent's review: one complement probe is both sufficient and necessary for a known single actuator root (`n>=2`). The note separates the decision problems.
4. **Source probes identify immediate carrier occurrence.** Rejected: shared relay and separate equal-valued relays have identical responses for the complete source input cube. Root ancestry and intake carrier identity are different targets.
5. **A predictor-branch injection determines upstream sharing.** Rejected: the injection produces `(0,1)` in both relay architectures. Only the separately justified node write produces different cross-consumer effects in this restricted pair.
6. **Correct source signatures establish pre-consequence prediction.** Rejected: a post-consequence sensory copy reproduces every source/readout value. Audited chronology is an independent requirement.
7. **A reflex twin must be experientially different.** Rejected as an unsupported extra premise. External reflex/deliberate labels do not change the declared organization; complete actual twins cannot have different complete experiential types inside C1. No phenomenal variable is generated.

## Code-review corrections, accepted and applied

- The initial OR implementation used `any(generator)` but listed every source as an event parent. Python can short-circuit generator consumption, so the parent record would overstate actual sequential reads. The corrected implementation first reads every input value into a tuple, then aggregates that tuple. Event ancestry records actual modeled intake, while outcome sensitivity remains separately contextual.
- Initial `action_roots`/`prediction_roots` fields retained source configuration under a node or edge injection. They could not be interpreted as actual event ancestry after an injected value replaced the original. The corrected fields are explicitly `installed_action_sources`/`installed_prediction_sources`, and new `action_origins`/`prediction_origins` are computed recursively from the executed event-parent graph. An injection has its own leaf occurrence. Controls now check that shared-node injection reaches both consumers and a branch injection reaches only its addressed consumer.
- A development clone-label check merely constructed and inverted a renaming. It was replaced with executed source-coordinate transport: source values and route addresses move jointly and an actual new episode is evaluated. Complete-clone experiential invariance is inherited from C1/R192/R199 and is not claimed as an independently discovered experimental result.

These were review-found semantic defects; no failed assertion had exposed them. Earlier program PASS did not establish correct event interpretation. The revised result is `SCU-RESULT-v0.2.0`; the final receipt binds the corrected code and result hashes.

## Retrieval and operational limitations

- One local read path was mistyped and returned no file; it was corrected. Some large batch read output was truncated, and the affected guide/AGENTS/R191/R192 text was reread in full.
- The publisher URL for Zaadnoordijk et al. (2019) returned an inaccessible redirect, and PMC showed a browser interstitial. This worker retrieved the primary abstract and selected original text via search, and credits the separate coverage worker for the fuller comparison. Bollobás–Scott's six-page author manuscript was fully retrieved.
- First development run counts (v0.1) were 406 nominal episodes; 576 coded episodes; 5,045 matrix-fiber pairs; 203 known-root probes; 256 relay comparisons; 256 simple renamed-clone guards; 1,244 OR pairs. A later development check added 1,116 nominal-word/forward-state comparisons and improved coordinate transport. These local draft outputs were superseded during development before a canonical save; this paragraph preserves their interpretation and is not a claim to retain byte-identical old receipts.
- No actual neural/human/robot experiment, measured `H`, complete physical process admission, whole-map semantic closure, or remote-save verification was performed by this worker. The parent owns integration, current remote state, source-version census and dual saving.

## Final graph-contract omission and coverage wording

The first typed C6 export specified correct carrier targeting and timing but omitted a value-changing intervention. Writing 0 to an existing 0 need not affect either consumer, so the generic wording was too broad. The final premise explicitly sets all sources to 0 and writes/injects 1 before the relevant reads, with no intervening overwrite or compensation. This matches the existing proof/code and required no new model class or run.

The 5,045 matrix checks validate zero mismatch iff source columns coincide for every declared small matrix/route pair. They do not compare the full collection of nonzero observation fibers. Those exact fibers are proved algebraically. The note and review now state that computational scope precisely.
