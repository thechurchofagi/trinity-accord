# Independent DVC scientific and map-compatibility review

**Review date:** 10 October 2026.  
**Reviewer role:** independent coverage/prior-art and publication reviewer; no publication or canonical-map mutation performed by this reviewer.  
**Decision:** retain DVC20261010 as a **disabled device-validation checkpoint** with its exploratory reanalysis of public human data. No remaining scientific blocker was found for that bounded disposition. Do not describe it as a deployed apparatus experiment, a human consumer intervention, an H result, a newly completed map release, or an additional standalone paper. The separate SCU publication need not be reopened to incorporate DVC.

## 1. What was reviewed

The DVC research note, 483-line reference implementation, protocol, device timing contract, six-claim ledger, typed extension, local map audit, failures, review response and gap ledger were read. The last C3 wording repair was read separately after the initial extension review. The independent public-data reanalysis code was read in full, as were its report, timing audit and apparatus contract. Selected original article Methods/Results passages, the archive README, the published fitting README and the first 165 lines of its MATLAB fitting script were also inspected. This is not a claim to have read all the apparatus worker's external sources or every raw CSV row personally.

The exact files, hashes, per-file reading limits and baseline-map field paths are in the accompanying manifests. The project guide's existing separation of organization, conditional UCT interpretation and actual evidence governs this review; C1/U1 acquire no new threshold.

## 2. Scientific findings

### Last capture, actual intake and warm caches

DVC-C1 is correct in its declared sequential reference semantics. An accepted capture replaces a selected buffer; invalidation clears it; gate closure preserves it. Induction on these writes identifies the last surviving token at a particular snapshot's commit boundary. An immutable snapshot then preserves that occurrence until the selected eager consumer reads it. The result requires the specified consumer and read object: an uninspected short-circuit, gate-label reflex or live-buffer consumer is a different class.

The warm-buffer counterexample is useful because a commanded availability factorial need not be the consumer-input factorial. With old marker values one on both branches, closing a capture gate can preserve an old token. All four nominal settings can therefore produce the same AND output. Explicit invalidation repairs the displayed reference implementation, but a matching truth table alone does not independently certify either the invalidation or the subsequent reads.

The model correctly distinguishes absence (`None`) from an actually supplied zero-valued token. The fixed-gate zero-payload challenge therefore probes the displayed label reflex; it does not manufacture MPC's missing availability cell and does not eliminate every possible rival.

The 720-order enumeration has the correct combinatorial partition. A fresh pair needs the two arrival-before-capture chains, then commit, then consumption. There are six interleavings of the two length-two chains. Of the other schedules, 360 attempt consumption before commit, and 354 consume an already committed but nonfresh pair while preserving the displayed output. These counts are neither device failure probabilities nor participant observations.

### Timing and asynchronous retention

DVC-C2's endpoint conventions are internally consistent. With token validity `[a,b)` and closed sampler aperture `[s-u,s+h]`, correctness for every independent bounded arrival/departure pair is exactly

`a_max + u <= s < b_min - h`.

The upper bound must be strict. The proof uses attainable extremal bounds in the stated rectangular uncertainty class. It supplies no physical clock calibration, jitter estimate or hardware setup/hold specification. Gate and writer validity are additional conjuncts.

The asynchronous-pair construction also works. Source-port validity windows `[2,4)` and `[6,8)` need not overlap when the earlier capture survives until an atomic or equivalently validated commit. In the final trace, the P port explicitly receives an epoch-two replacement at tick 8; the epoch-one token captured at tick 7 remains in its buffer and is copied at commit. The two captured tokens are a retained same-episode pair, not a simultaneous global state. The claim separately requires actual source identity, the episode relation, storage survival, resources and the consumer deadline.

### Lineage, metadata, bypass and prediction

The old-origin/new-header witness preserves its old source occurrence. The port-swap witness separates current epoch labels from physical lane identity. The bypass example preserves output while changing the immediate intake carrier. These are proper finite countermodels to the corresponding stronger identifications. A real logger cannot establish its own source ancestry simply by printing the same fields used in the model.

DVC-C4 is a correctly indexed chronology limit. A state token generated by the current consequence and consumed subsequently cannot constitute an earlier prediction of that same consequence. An earlier state sample or a later target remains allowed. This is an inherited temporal principle applied to the proposed port, not a new prohibition on proprioceptive prediction.

### Read-only shadow and the human endpoint

DVC-C5 is valid for its fixed acyclic structural model, with other functions, inputs and disturbances held fixed and no directed path from the gate intervention to the endpoint or its ancestors. The proof is causal ancestor induction. A synthetic numerical PSE variable would provide no additional evidence, and none is needed or retained.

This result identifies the central empirical gap. `M_D` is a device drive-command copy; in passive rail operation it is not a participant's efference copy. `P_E` is an identified device position/state token; it is not a biological proprioceptive consumer input by naming. A completely isolated shadow validates its own acquisition contract while leaving a human endpoint causally untouched. Timing correlation with a concurrent human task does not close that gap. Shared resources, cueing, sound, movement or stimulus timing could violate isolation and must be checked in an actual installation.

### UCT interpretation

DVC-C6 retains the correct direction. Independently grounded relations in an admitted complete actual P/I/K instance have their transported structural counterparts under inherited C1. A selected source/read formula is not a universal admission algorithm or an independently actual sub-process. Gate eligibility, input availability, invalidation, successful capture, correct prediction and report are not conditions for basal experience. Continuing local processes are not erased by participation in a larger one.

The result does not identify familiar mineness, ownership, agency, conceptual self, RetBind, experiential intensity or a number of subjects. Labeling a mechanism a reflex or clone does not defeat C1's complete-organization invariance. These boundaries are compatible with the inspected foundational and retention/transport map contracts.

## 3. Public data: completed empirical work with a narrower target

Independent execution reproduced all six inspected reanalysis outputs byte for byte: source-file audit, timing arithmetic, archived-parameter statistics, independent psychometric fits, refit statistics and the result summary. The source and result hashes are retained in `REPRODUCTION_RECEIPT.json`.

The declared analysis contains 18 included participants, 9,704 in-range command records and 108 participant-condition cells. Two analysis variants produce 216 fitting runs, not 216 independent participants. The refitted passive Start-minus-End sigma contrast is 0.68299755, with 95% paired t interval [0.30407048, 1.06192462]; the declared three-contrast Holm family gives p = 0.00426616. The archived JND contrast is 0.49819889 with its own scale and uncertainty. These numbers are reproduced output evidence, not a new causal manipulation of an identified consumer.

The analysis code correctly separates PSE, positive normal-SD `sigma`, `Phi^-1(.75) * sigma`, and the archive's `JND` label. It uses subject-level paired contrasts, explicitly declares adjustment families, and reports the active-only available-timing sensitivity filter as a sensitivity analysis. The unavailable curvature and gaze exclusions are not invented. Nonsignificance is not recast as equivalence.

The unresolved JND scale difference and article degrees-of-freedom discrepancy should remain visible. The archive's 18-person PSE ANOVA reproduces the rounded reported effects in the [original article](https://doi.org/10.3758/s13414-026-03288-7), while another JND paragraph uses degrees of freedom compatible with 16 people without the [released summary](https://doi.org/10.5281/zenodo.18877381) identifying that population. Selecting participants to force a match would be unjustified. Likewise, reconstructing decimal-comma time fields does not establish units, clock origins, physical tactile onset or actual consumer intake. The available timing archive cannot certify the article's matched-trajectory/trigger description independently.

One source-language clarification was requested and **accepted**: the article describes physical keys 1/2, whereas the archive stores `InputValue` 0/1. Interpreting stored one as “comparison stronger” is consistent with the ascending command-response curves, but the actual key-to-stored-value conversion is not exposed in the inspected controller source. The final report states that assumption, and `RESPONSE_CODING_CORRECTION.json` narrows the earlier result-metadata wording without overwriting executed code or outputs. This correction was read and verified. It does not require refitting the stated increasing-response model. The 0.5 crossing of the same curve is invariant to exchanging p with 1−p; physical stronger/weaker naming still needs the coding bridge.

PSE remains a comparative behavioral location parameter under the specified response model. Sigma concerns discrimination precision. Neither is an interchangeable measurement of H, agency, ownership or conceptual self. A prospective PSE choice in a future protocol does not retrospectively preregister this archive reanalysis.

## 4. Correction requested and verified

The first typed C3 export inherited a generic binding saying “one specified consumer implementation,” despite its reflex and bypass comparisons allowing different implementations. The substantive counterexamples were valid, but the template could be read as requiring the same implementation on both sides.

The worker accepted and repaired the note, claim ledger, C3 node and r_C3 rule. The final binding fixes all premises within each execution while allowing two declared rival instances to differ in implementation or pathway and share exactly the stated nominal observations. The rule now explicitly records `paired_rival_instances_allowed: true`. This review item is **closed**; it is not grounds to reopen the mathematical protocol work.

## 5. Exact map-reading scope and remaining work

The baseline remains UCT-MAP-v1.1.2: 913 nodes, 424 active conditional rules, 261 non-deductive contexts and ten suspended historical rules, for 1,608 ledger IDs. This reviewer freshly inspected core fields for **314 nodes, 137 active rules, all 261 context links and all ten suspension entries: 722 IDs**. The node selection covers A/B/C/D, TA18, R147, R169, R171–R174, R187–R188 and the four additional transport/report/selection/time anchors referenced by DVC. Readable cards preserve the actual inspected text. Repeated field values are represented only by explicit references to an earlier fully displayed identical value.

For nodes, the inspected fields include their displayed statement and scope, plus the selected domain/quantifier/boundary/limit fields where present. For active rules, the inspected fields include statement, `all_of`, conclusion, same-instance requirement and the displayed binding/alternative-route fields. This does **not** claim that every nested formal-contract field or historical proof was freshly read. The four CM context records and the ten suspension ledger entries received complete displayed-record reads. The exact JSON paths and omitted top-level fields are listed per ID.

The remaining **886 IDs** comprise 599 nodes and 287 active rules. They were inventoried for coverage, not freshly semantically reviewed. Their earlier recorded review is preserved but is not attributed to this reviewer. Historic gaps of 1,034 IDs / 1,828 deeper fields and 1,347 proof IDs remain OPEN. QC10, IA-QC11, QC12 and QC13 remain OPEN. This is a substantial scoped compatibility review, not full-map semantic completion.

All 39 new typed DVC items—21 nodes, six rules and 12 context links—were read. Their external references resolve to the inspected baseline anchors. Their evidence-to-actual and named-experience obligations remain false/open, and the extension is disabled. DVC's conclusions are compatible with the inspected existing statements: it gives an acquisition implementation repair, not a refutation of valid source-routing, same-instance, retention, temporal, selected-coordinate or report-domain results. The ten historical suspensions are not reinstated.

A structural comparison finds no old rule whose premise or conclusion names DVC, and no canonical graph mutation is made. That permits preservation of the existing release; it is **not** a semantic proof of the unread historical region. No new full-map version should be claimed from this review or from schema checks.

## 6. Originality and disposition

Ordinary register semantics, setup/hold reasoning, snapshot consistency, causal isolation and output-versus-implementation nonidentifiability are inherited. The note credits manufacturer interface behavior and selected Chandy–Lamport context without claiming to implement that distributed algorithm. Its defensible increment is the explicit application of those ideas to admitting MPC/SCU consumer-input cells, with constructive cache/arrival/episode faults and a precise device-to-human boundary. Worldwide priority was not established in this bounded review.

The public-data reanalysis is actual new work on existing observations, and its discrepancies and limits are valuable. It does not supply the missing joint actual apparatus/consumer/endpoint premises. The appropriate outcome is therefore to preserve the finite model, proofs, typed disabled extension, source audit, reanalysis and open installation contract together. Keep the frozen SCU publication separate. The next empirical advance requires an accessible actual acquisition path and measured source/capture/read/timing evidence; the current result must not be represented as already obtaining them.

## Reproduction and release-byte note

The independently executed DVC code had SHA256 `ebd0b0ac69d28cb62887b505a0db228eafe1b79c4900d1ea3083a7808909a440`, and its result was exactly `9272a41c5fec78a50811bf43d8e763120a9cbbd553d81744cf2be5093e4cff4a`.

After that reproduction, the worker replaced only the `primary_endpoint_design_only` text to distinguish prospective PSE, independently fitted sigma and source-labelled JND. The final reviewed code is `028a090a4b2826fd58b78738fc80ea5c7a0cd3454da71c751c781f5ea95e1d30`; the final result is `ec0ca95e7eb0aab624d3eeed8093c9b00d398f24e0928522ff31a28335d51d2f`. A direct diff verified that the algorithm, counts and every witness remained identical. This review records that exact editorial equivalence; it does not claim a second independent execution of the final bytes.
