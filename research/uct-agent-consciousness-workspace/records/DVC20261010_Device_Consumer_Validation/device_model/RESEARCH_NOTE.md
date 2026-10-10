# Device consumer validation: arrival, latching, and same-episode consumption

**Module:** DVC20261010  
**Result:** DVC-RESULT-v0.1.0  
**Status:** finite digital model and proposed instrument contract; candidate disabled. This is a research checkpoint, not an additional publication or a completed human experiment.  
**Source baseline:** the parent verified remote `8bac31cc0b9fb4c70d87f688dabbadeb6166addb`; completed map UCT-MAP-v1.1.2; supplied coverage UCT-PUB-v1.0.19. Current publication actions and any later coverage version belong to the parent task.

## 1. Precise problem and inherited scope

MPC20261010 shows that the usual three consumer-input cells leave a missing motor-only counterfactual; even all four response values do not identify actual reads. SCU distinguishes source dependence, intake identity and predictive chronology. The present question is the implementation step between those results and a proposed instrument: **when do two gate settings actually realize the intended pair of inputs in the designated consumer on the intended trial?**

A capture gate does not necessarily clear a previously written register. A source command can be issued without reaching an acquisition port before sampling. Two channels can contain equal values from different trial epochs. An investigator can therefore record the intended four gate configurations while the consumer receives a different four-cell design.

The retained increment is an explicit last-capture contract, an exact bounded-latency capture window, and countermodels for a proposed separate digital consumer. These are applications and repairs using familiar sequential-state and timing reasoning. They are not new general results about memory, snapshots, causality, or consciousness.

There is also direct device-interface prior art. The OpenHaptics Programmer's Guide describes frame snapshots, previous-frame query behavior outside frames, synchronous scheduler snapshots, and replacement of an earlier force setting before frame-end transmission [4]. Those documented distinctions already separate stored/query state from a physical output transition. The API reference exposes position and raw-encoder queries [5]. These are candidate interface capabilities, not evidence that the published experiment used those calls or that our proposed command-copy, capture and read instrumentation exists.

The empirical apparatus selected by the parent is the published Touch X/Arduino rail experiment of D’Onofrio Pacheco and Zimmermann [1]. The authors describe active stylus movement, passive rail transport driven through Arduino Leonardo, and separately triggered vibrotactile stimulation. That apparatus is an existing public experiment. We have not connected to it, deployed firmware, acquired its raw signal streams, or measured a person. Its publication does not establish the new shadow ports or their timing.

## 2. Proposed device roles and three distinct coordinates

Use a new, separate digital **shadow consumer** whose output is logged and does not drive the movement or tactile stimulus. The proposed inputs are:

- `M_D`: a copy of a specifically identified device movement-control command. In passive rail operation this is a device drive command, not the participant's efference copy.
- `P_E`: an explicitly identified encoder or position/state sample. It is a device measurement, not automatically a proprioceptive neural signal or a feeling.

The exact command-copy port, position API or added sensor, firmware, source timing, and capture hardware remain unverified. In active human movement there may be no corresponding rail-drive command. One cannot populate that missing command by renaming an instruction, movement label or electromyogram. Any active–passive transport of this device contract needs a separate argument.

Three coordinates are never conflated:

1. **Availability mask** `g=(g_M,g_P)`: whether the designated source is to be supplied to this consumer in the current design cell.
2. **Payload value** `x_i`: a bit carried by an actually supplied token. A supplied zero remains an input token.
3. **Consumed occurrence**: the actual modeled source ancestry and immediate snapshot cell read by the selected consumer.

For the elementary gate-factorial witness, every supplied marker token has payload one and an absent slot produces a separately recorded neutral zero. Thus the output can implement a function of availability. A later payload-zero challenge holds availability fixed and changes data; it is not a realization of the missing `10` cell.

The model separates source issue, physical-port arrival, accepted sample/latch, snapshot copying, snapshot commit, and selected-consumer read. These are different event kinds with explicit parent relations. `None` denotes absence; it is not identified with an input whose data value is zero. `model.py` is an executable reference semantics, not a hardware driver.

## 3. DVC20261010-C1 — exact last-capture and retention contract

### 3.1 Definitions

Fix one device installation, two physically identified source ports and buffer registers, one preparation/reset contract, one total event order, and a designated consumer operation. These premises apply jointly to the same episode family.

For channel `i`, an **accepted capture** occurs only when its capture gate is open and an input token is available. It writes that token's value and identity into buffer `B_i`. A closed gate prevents a new capture but leaves `B_i` unchanged. An explicit invalidation sets the buffer to absence.

At commit event `q`, the model copies both buffer cells into an immutable snapshot `S_q`. The selected eager consumer later reads each snapshot cell at event `r`, with `q<r`. Other consumer algorithms are separate classes; readiness of a cell does not prove that a short-circuit consumer read it.

Let `c_i(q)` be the last accepted capture before `q` after the last buffer invalidation, if such a capture exists. With no subsequent invalidation, let `tok(c_i(q))` be its source token; otherwise the snapshot cell is absent. The actual source identity is independently stipulated in the model. A packet's claimed epoch is a separate, fallible metadata field.

### 3.2 Claim and proof

**Claim.** For every execution of this declared model, the token copied into snapshot cell `i` is exactly `tok(c_i(q))`, or absence if there is no surviving accepted capture. Consequently, the eager selected consumer reads the intended current tokens `tau_M^e,tau_P^e` exactly when the last surviving captures before `q` contain those respective tokens and the committed snapshot is the object actually read.

For a disabled channel, realizing absence instead requires no surviving source token in the selected cell. The current gate being zero is insufficient.

**Proof.** Induct over buffer-changing events. An accepted capture replaces the buffer by its input token; invalidation replaces it by absence; source issue, arrival without capture, gate closure, and activity in another channel do not change that buffer. Hence its value at commit is the last surviving write or absence. The immutable snapshot preserves this cell until the specified consumer reads it. This proves the statement without inferring token identity from equal data values.

**Corollaries.** Closing a gate after capture does not revoke the captured token. Closing before the current capture may leave a previous trial's token. A later overwrite of the live buffer cannot alter an already committed immutable snapshot, but committing a new snapshot may assemble two different epochs. A software design that reads live buffers at separate times needs its own exclusion or version-validation contract.

### 3.3 The exact finite ordering witness

Begin with both buffers containing epoch-zero marker tokens of value one. Issue two epoch-one tokens, also of value one. Keep both gates open, do not invalidate, and execute each of six operations exactly once:

`arrival_M, arrival_P, capture_M, capture_P, commit, consume`.

There are exactly `6!=720` total orders. Both intended new tokens are consumed exactly when

`arrival_M < capture_M < commit < consume`

and

`arrival_P < capture_P < commit`.

The two arrival–capture chains can be interleaved in `binom(4,2)=6` ways before commit and consume. These six executions are the only fresh-pair executions. Of the remaining orders, 360 attempt consumption before commit and are rejected. The other 354 consume a snapshot and output one, just like the valid executions, but at least one consumed source token is not the intended current token.

| Mutually exclusive category | Count | Exact denominator |
|---|---:|---|
| Both intended current tokens read | 6 | All 720 total orders |
| Consume attempted before snapshot commit | 360 | All 720 total orders |
| Committed output matches, but at least one intended current token is missing | 354 | All 720 total orders |
| Total | 720 | Complete six-operation enumeration |

These are exhaustive counts in a deliberately adversarial finite schedule family. They are not estimated device error rates or probabilities of human misattribution. The implementation computes provenance; the independent order predicate checks the above condition.

## 4. DVC20261010-C2 — robust capture windows and asynchronous pairing

### 4.1 One channel

Suppose a specified current token is stable at the **actual sampled port** during `[a_i,b_i)`. Arrival and departure bounds are independently validated:

`a_i in [a_i^-,a_i^+]`, `b_i in [b_i^-,b_i^+]`, with `a_i^+<b_i^-`.

Let the sampler require stability over the closed aperture `[s_i-u_i,s_i+h_i]`, where `u_i,h_i>=0` are declared setup and hold margins. The gate and writer must also be valid throughout any required aperture; the source bounds do not grant that premise.

**Claim.** A fixed sample time is correct for every arrival/departure pair in this rectangular uncertainty class exactly when

`a_i^+ + u_i <= s_i < b_i^- - h_i`.

**Proof.** Every possible arrival must precede the aperture's left endpoint, so the largest arrival gives `s_i-u_i>=a_i^+`. Every possible departure must follow its right endpoint, so the smallest departure gives `s_i+h_i<b_i^-`. These inequalities are sufficient for all pairs. If either fails, choose the corresponding extremal arrival or departure, giving an admissible failed capture. The upper inequality is strict because the stated valid-port interval is half-open.

This result is a model condition, not a measured timing margin of Touch X, an Arduino board or a host operating system. Gate setup/hold, transport jitter, ADC or encoder latency, clock alignment, and firmware service times require real evidence before numerical margins can be supplied.

### 4.2 Two channels

Write the two robust sample windows as `I_i=[L_i,U_i)`. A common sample time exists exactly when

`max(L_M,L_P)<min(U_M,U_P)`.

Separate channel captures can instead be valid whenever each window is nonempty, **provided** the captures have independently grounded same-episode source identities, their stored cells survive until commit, pairing is atomic or equivalently validated, no resource conflict prevents the two captures, and the later consumer meets its stated deadline. The distinct captures do not become simultaneous events merely because they share an epoch label.

A concrete execution has the command token valid at its port during `[2,4)` and the state token during `[6,8)`. Capture them at 3 and 7, preserve the first latch, commit at 8, and consume at 9. There is no common valid source-port sampling time, yet the actual stored pair has the two specified epoch-one ancestors. The first port can already carry epoch two when the preserved epoch-one pair is consumed.

This pairing result does not say that the two source-port values coexisted at a single instant. It specifies which earlier tokens the selected consumer encounters. Non-simultaneous local records and global consistency are longstanding problems; Chandy and Lamport's snapshot work is relevant prior context [2], but this two-buffer episode join neither implements nor proves their distributed snapshot algorithm.

## 5. DVC20261010-C3 — implementation witnesses that defeat stronger readings

The result JSON retains nine concrete witness records, including event traces where helpful. Each execution holds its own declared implementation and source/time roles fixed. Paired rivals share the stated observations but may differ in consumer or pathway; same-instance binding does not require rival implementations to be identical:

| Witness | Matched or misleading observation | Actual difference or failure |
|---|---|---|
| Closed gate with warm latches | All four gate settings are issued | With no invalidation the eager AND consumer receives `(1,1)` in all cells, including old tokens on closed branches. Preparation with explicit invalidation restores the intended availability table. |
| Gate closed at consumption | Both gate flags are zero | Both current tokens were captured before closure and are still read. |
| Issued but unarrived probe | Transmitter recorded a current issue and output matches | The state channel captures its old port token; the new token arrives only after consumption. |
| Later overwrite and mixed epochs | Identical output values | The original immutable snapshot reads epochs `(1,1)`; a new commit after an overwrite reads `(1,2)`. |
| Ports swapped | Both metadata epochs are current | Physical M and P source origins are exchanged. Epoch-only checking passes; independently grounded source matching fails. |
| Reheaded old token | A packet claims the current epoch | The retained source ancestor is still the older command/state occurrence. A new header is not a new source occurrence. |
| Gate-label reflex | The full nominal gate-factorial OR table matches | The rival reads experiment gate labels rather than M/P data. A fixed-gate payload challenge rejects this displayed rival; it does not close the space of arbitrary rivals. |
| Direct port bypass | Values agree with the snapshot consumer | The immediate carriers read are live acquisition ports rather than the committed snapshot cells. |
| Disjoint capture windows | No common source-port capture time exists | Separate valid captures and retained same-epoch pairing still succeed under the additional storage/commit contract. |

The first four witnesses establish a missing device-validation obligation beyond simply requesting MPC's fourth cell. The remaining witnesses prevent a new event log or an epoch label from being treated as self-authenticating evidence. The model stipulates the true event parents. An actual instrument must independently justify their correspondence to executed physical reads, paths and source emissions. Complete response values cannot supply that justification, as MPC and SCU already show.

## 6. DVC20261010-C4 — current-state feedback and prediction have different deadlines

If a particular state token `P_E^e` is generated by consequence `Y_e`, and the physical ordering is

`t(Y_e)<t(P_E^e)<=t(capture_P)<=t(consume)`,

then a consumer that uses this current consequence-derived token cannot be a pre-consequence predictor of `Y_e`. This is immediate by transitivity; the model separately checks finite order instances. A later shadow consumer may be a monitor or an estimator. A predictor must instead use an earlier state sample, predict a later consequence, or supply a different independently warranted temporal role.

This does not prohibit proprioceptive information in prediction. It prevents a change of time index from being hidden by the word “prediction.” It is a device application of SCU's inherited chronology limit, not a new principle of causal order.

## 7. DVC20261010-C5 — a read-only shadow does not intervene on a human consumer

Consider a frozen acyclic structural model (or a specified acyclic time unfolding) in which the shadow receives command and state copies but has no directed path to the endpoint itself or to any of its ancestors, including the actuator, tactile stimulation, participant's received information, attention instruction, report instrument or endpoint analysis. Hold all other structural functions, inputs and disturbances fixed. Then changing only its gates leaves the participant's endpoint unchanged in that model.

**Proof.** Evaluate the causal ancestors and then the endpoint itself in dependency order. None is changed by the shadow intervention. Each retains the same parent values and disturbance, so the endpoint's value is unchanged. The result is conditional on the claimed absence of all such outgoing paths; resource contention, visible cues, sound, changed timing or instructions would violate that condition.

This proof is not a simulation of PSE and does not assume an empirical psychometric function. A tautological numerical proxy would add no evidence, so no synthetic “human endpoint” is generated. The selected primary future endpoint is the PSE of the two-stimulus tactile comparison, with independently fitted sigma and source-labelled JND separately retained; no equality between them is assumed. This future endpoint choice is not retrospective preregistration. Agency, ownership and familiar H are unmeasured targets and cannot be substituted for those outcomes.

The shadow is useful for validating **its own digital acquisition and consumer contract**. To use its manipulation as a test of human consumer organization, an actual causal link or a valid measurement bridge must be independently supplied. Neither a concurrent human task nor a timing-correlated shadow output creates that link. A purely observational shadow may remain useful as an instrument, but its event log is not a neural readout by naming.

## 8. DVC20261010-C6 — conditional UCT relevance

When a complete actual digital process, interval, source paths, persistent buffers and actual consumer operations are independently admitted, C1 conditionally gives their token-relative experiential structural counterparts. Current source consumption and retained old-token consumption may describe different selected organizations; a named feeling is not thereby identified.

The gate-off, cache, invalidation and timing distinctions concern organization within an admitted process. None creates or abolishes its basal-experience status merely by satisfying an experimenter's eligibility rule. Persisting local processes remain admitted when they also participate in larger processes; no exclusive owner is selected. A correctly implemented reflex or complete organizational clone is not assigned absent or opposite experience by its label. Human neural consumers, actual PSE mechanisms, H, RetBind and current-assistant consciousness are not established here.

This is the inherited C1/U1 direction, with the same-instance and complete-signature guards retained. It is not empirical confirmation of C1.

The AND/OR outputs instantiate small information-processing tasks. Their correctness is not a measurement of general intelligence. No conceptual-self representation or self-report mechanism is implemented here. C1–C5 therefore distinguish selected organization and task evidence; C6 states only their guarded UCT relevance. A task output, a reported judgment, an independently specified experiential endpoint and familiar mineness remain separate targets whose connections require their own actual evidence.

## 9. Reproduction, originality and stopping decision

Run `python model.py` in this record. The final result records 720 order schedules in the three mutually exclusive categories above, four warm-versus-invalidated gate-factorial pairs, 4,896 comparisons between a bounded-uncertainty timing formula and explicit arrival/departure assignments, 400 ordered pairs of nonempty safe windows, and 108 current-feedback chronology instances. The nine retained witnesses are constructive examples, not additional participant groups. Counts with different denominators are not added into one sample size.

The general last-writer statement, robust-window equivalence and causal-isolation argument are supported by the proofs here. Finite enumeration checks the stated subsets. No hardware, robot, neural or human experiment was executed. The final code/JSON hashes are in RUN_RECEIPT.json; a provisional development run and semantic corrections are retained in history/ and FAILURES.md.

Internal inheritance includes MPC's missing-cell/read-event limits; SCU's actual ancestry and intake/timing limits; R173's actual retention requirement; R174's fixed-route/interior-probe contract; and R187's overwrite, port-fidelity and lineage boundaries. Ordinary register semantics, setup/hold logic and snapshot ideas are prior foundations. The proposed reusable increment is the explicit consumer-gate implementation repair and the specific device-to-human evidence boundary. Worldwide priority of this application remains unverified.

**Decision:** preserve as a disabled device-validation checkpoint and implementation supplement. Do not add it to the frozen SCU paper during its publication step or declare a new standalone-paper breakthrough. The next experiment is a concrete acquisition/firmware validation with independent actual timing and source-path evidence; a human endpoint interpretation remains a separate task.

## References and inspected scope

[1] D’Onofrio Pacheco, P. N., and Zimmermann, E. (2026). *Effects of prediction and attention on tactile precision in somatosensory gating*. Attention, Perception, & Psychophysics 88, article 145. https://doi.org/10.3758/s13414-026-03288-7. This worker directly inspected the article metadata and apparatus passages; the independent device/evidence worker read the complete paper and checked the available dataset. The article does not describe this proposed shadow consumer.

[2] Chandy, K. M., and Lamport, L. (1985). *Distributed snapshots: determining global states of distributed systems*. ACM Transactions on Computer Systems 3(1), 63–75. https://doi.org/10.1145/214451.214456. Author-hosted source: https://lamport.azurewebsites.net/pubs/chandy.pdf. This worker inspected §§1–2 and selected §3–4 passages, not the entire original proof. This is background attribution, not a deduction of DVC's stronger episode or physical-port premises.

[3] Internal source records: MPC20261010 RESEARCH_NOTE.md, PROTOCOL.md, model.py, EXACT_RESULTS.json and FAILURES.md (full reads); SCU20261010 proofs/protocol/code and prior review; RESEARCH_MASTER_GUIDE.md v2.3 (complete fresh read). Precise source hashes and limited historical-source rereading are in SOURCE_SCOPE.json.

[4] 3D Systems. *OpenHaptics Programmer's Guide*, 3.4.0 (2015 footer), relevant haptic-frame, scheduler and state passages on printed pp. 88–91. https://s3.amazonaws.com/dl.3dsystems.com/binaries/Sensable/OH/OpenHaptics_Programmers_Guide.pdf. Selected relevant passages read directly; not a complete-manual read. Timing bounds for a particular host, firmware and wiring remain unmeasured.

[5] 3D Systems. *OpenHaptics API Reference Guide*. Position/encoder and frame-query passages on printed pp. 7 and 56–57. https://s3.amazonaws.com/dl.3dsystems.com/binaries/Sensable/OH/OpenHaptics_API_Reference_Guide.pdf. Selected relevant passages read directly; availability in a document does not establish the actual port used in the selected experiment.
