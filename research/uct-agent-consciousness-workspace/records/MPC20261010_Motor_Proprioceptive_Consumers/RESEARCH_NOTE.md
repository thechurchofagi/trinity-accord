# Motor and Proprioceptive Consumers
## Missing counterfactuals, endpoint vectors, and the limits of active–passive contrasts

**Research ID:** MPC20261010  
**Result:** MPC-RESULT-v0.1.0  
**Status:** bounded theoretical/design result; no actual human installation admitted; no named phenomenal endpoint calibrated; pending disabled map candidate

## 1. Problem and contribution boundary

Active movement, passive transport, and rest are often compared when studying self-produced touch, tactile gating, agency, or ownership. Those labels compress several different facts: whether a motor-command branch exists, whether a selected consumer actually reads it, whether proprioceptive or visual state information is available, whether the overt movement and tactile consequence match, and which endpoint is measured. The present note asks one narrower question:

> What does the usual active/passive/rest triangle identify about a motor-command versus proprioceptive consumer, and what remains unmeasured?

The finite result is elementary but exact. If a binary endpoint depends on two frozen consumer inputs, the usual three cells `(00,01,11)` always leave exactly two deterministic response laws, differing only at the missing `(10)` cell. For an active-only profile, the surviving laws are motor sufficiency `M` and motor–proprioceptive synergy `M AND P`. For an active-plus-passive profile, they are proprioceptive sufficiency `P` and substitution `M OR P`. With `k` unrelated endpoints, the same design leaves `2^k` joint completions. Filling the fourth cell identifies the endpoint response table under the frozen model, but still does not identify actual read events: eager and short-circuit implementations can realize the same table while consuming different inputs on the same trial.

This is not a new Boolean-algebra theorem, a universal model of touch, or a consciousness test. Its proposed increment is a source-explicit protocol correction tied to current primary evidence: **the missing consumer counterfactual and endpoint vector must be stated before an active/passive contrast is interpreted as motor-source use, proprioceptive-source use, agency, ownership, or familiar mineness.** R204, R205 and SCU already establish broader success/alignment/use and source/read distinctions; those are inherited rather than republished here.

## 2. Frozen model and actual-application contract

Let `M,P in {0,1}` denote **inputs at one selected downstream consumer**, not the mere existence of a motor command or proprioceptive signal elsewhere.

- `M=1`: the declared consumer is supplied the frozen motor-command/efference input.
- `P=1`: the declared consumer is supplied the frozen proprioceptive or substitute state-estimate input.
- `Y_e(M,P)`: one prospectively selected endpoint `e` under a common bearer, interval, boundary, movement/touch consequence, endpoint instrument, reset distribution, attention instruction, body-state context, and timing.

The four cells are:

| Cell | Consumer input contract | Familiar shorthand |
| --- | --- | --- |
| `00` | neither selected input reaches the consumer | baseline/rest control |
| `01` | proprioceptive/state input only | passive matched movement |
| `10` | motor input only, selected state input gated/replayed away | branch-isolating counterfactual |
| `11` | both selected inputs | active matched movement |

The shorthand does not establish the contract. In an actual installation, the action-to-plant route must be separated from the branch entering the selected predictor or endpoint mechanism. Otherwise setting `M=0` may remove movement, and setting `P=0` may change kinematics, muscle state, attention, effort, or tactile stimulation. A valid comparison must freeze or measure those changes rather than naming the cells after the desired interpretation.

For a human protocol, the `10` cell is especially difficult: deafferentation, temporary block, motor imagery, brain stimulation, or a robotic bypass changes different parts of the organization. This note therefore treats `10` first as a strict thought-experimental and engineering-design target. It does not claim that any listed manipulation is ethically or scientifically adequate.

## 3. Stable claims

### MPC20261010-C1 — three-corner completion theorem

**Type.** Exact finite identifiability result.  
**Domain.** Deterministic functions `Y:{0,1}^2->{0,1}` with fixed input meaning and fixed context.  
**Claim.** Observation of `Y(0,0)`, `Y(0,1)` and `Y(1,1)` leaves exactly two functions compatible with any observed three-bit profile. The functions agree on the observed cells and differ only at `Y(1,0)`.

**Proof.** A Boolean function on two inputs is a four-bit table. Fixing three coordinates leaves one unconstrained bit, hence two completions. `model.py` enumerates all 16 functions, finds eight observation fibers, and verifies that every fiber has size two with its members differing only at `10`.

**Useful special cases.**

- Profile `001` in observed order `(00,01,11)` has completions `M AND P` and `M`.
- Profile `011` has completions `P` and `M OR P`.

Both pairs survive monotonicity. Thus monotonicity alone does not repair the missing cell.

**Limit.** The theorem concerns a frozen binary response law, not a biological mechanism, real-valued psychometric curve, or experience.

### MPC20261010-C2 — endpoint-vector multiplication

**Type.** Exact finite corollary.  
**Domain.** `k` endpoint functions with no cross-endpoint equality or structural constraint.  
**Claim.** If the same three cells are observed separately for each endpoint, exactly `2^k` joint Boolean completions remain.

**Proof.** C1 leaves two independent choices per endpoint; the Cartesian product has cardinality `2^k`. The executable checks cover `k=1,...,6`.

**Interpretation.** Adding agency, ownership, intensity, sensitivity, confidence, or report readouts without the missing intervention does not by itself repair the consumer-law ambiguity. Conversely, collapsing them into one score discards distinctions and cannot create the missing evidence.

### MPC20261010-C3 — the completed table still does not identify intake occurrence

**Type.** Exact countermodel; inherited source/use boundary applied to the concrete factorial.  
**Domain.** Two implementations of the same `M OR P` response table.

An eager implementation reads both inputs on every cell. A short-circuit implementation reads `M` first and does not read `P` when `M=1`. They agree on all four endpoint outputs. They differ in actual `P` intake on cells `10` and `11`.

Therefore a complete factorial response table can identify the declared input–output law while failing to identify an internal read occurrence. Telemetry of source availability, success, or output equality is not actual use. Identifying use requires a validated event instrument or stronger sole-route/no-cancellation premises, exactly as the R204–SCU line requires.

### MPC20261010-C4 — controlled effects are endpoint- and context-indexed

**Type.** Algebraic protocol identity.  
**Domain.** Real-valued endpoint means `mu_mp` for one fixed endpoint and one valid factorial contract.

The full table defines:

`Delta_M(P=0)=mu_10-mu_00`, `Delta_M(P=1)=mu_11-mu_01`,  
`Delta_P(M=0)=mu_01-mu_00`, `Delta_P(M=1)=mu_11-mu_10`,

and interaction `I=mu_11-mu_10-mu_01+mu_00`.

The common active/passive contrast estimates only `Delta_M(P=1)` if the `P=1` state and every other relevant condition are genuinely held fixed. Inferring `mu_10` from the other cells by setting `I=0` is an additive-model assumption, not an empirical consequence. These effects are indexed by endpoint and context; they do not transport automatically from tactile precision to perceived intensity, agency, ownership, or report.

### MPC20261010-C5 — current primary evidence supports an endpoint tensor, not a self scalar

**Type.** Source-bounded empirical constraint and inference.

D'Onofrio Pacheco and Zimmermann (2026a) report that active and passive movements matched in kinematics reduced perceived intensity similarly, while discrimination precision was better in active movement; predictable passive kinematics could restore precision. Their later open-access study (2026b) crossed active/passive/still movement with attention to start versus goal. Its abstract reports reduced perceptual bias in active and passive movement independent of attention, but preserved/high precision during active movement and during passive movement only when attention was directed to the goal.

At a qualitative threshold, the precision pattern is compatible with a substitutable `motor-based OR goal-cue` route. This is a design interpretation, not a reanalysis of raw data and not proof of an anatomical OR gate. The important point is narrower: **the same trial can exhibit a movement-related bias effect and a different precision effect, so “attenuation” cannot be treated as one scalar endpoint.**

Kilteni and Ehrsson (2017) further show that manipulating body ownership changes force attenuation, and Kalckert and Ehrsson (2012) report an active/passive by posture dissociation between agency and ownership. These results make body-state context and target semantics potential third variables. A two-input `M,P` model is therefore a minimum within a frozen context, not a complete biological model.

### MPC20261010-C6 — conditional UCT interpretation and its stopping rule

**Type.** Conditional interpretation, not empirical validation.

If one actual token, interval, complete declared signature, source carriers, consumer events, intervention fidelity, endpoint instrument, and boundary are independently established, then the selected motor/proprioceptive consumer relations are parts of its actual organization. Under C1, those same relations have token-relative structural counterparts inside experiential organization. This is the positive UCT relevance: actual body/action-source use is not outside experience waiting for a later report to make it experiential.

Nothing in C1–C5 identifies the counterpart as familiar agency, ownership, tactile intensity, discrimination sensitivity, or a conceptual `I`. Those named targets require separate bridge and evidence packages. The result adds no basal experience gate and no exclusive owner. It does not decide whether any current assistant is conscious or afraid of death.

## 4. A minimal consumer-gate protocol

1. Fix one actual bearer/process candidate, interval, boundary, movement trajectory, contact force, timing, endpoint, attention/body-state context, plant controller, consumer and reset distribution.
2. Split the plant-driving path from the two branches entering the selected consumer. Name the actual carriers and intake events.
3. Validate four branch states independently. A label such as “passive” is insufficient: verify what reaches the consumer.
4. Reproduce the four endpoint cells. Report the full vector `(intensity bias, discrimination precision, agency, ownership, report)` without scalar aggregation.
5. Instrument actual read events or run branch-local perturbations. Do not infer consumption solely from endpoint effects; preserve the eager/short-circuit and cancellation countermodels.
6. Add context controls for attention, body-state estimate, visual cue, muscle activation, stabilization effort, timing predictability, and tactile stimulation. If they cannot be held fixed, expand the model or narrow the claim.
7. Predeclare a failure condition. Examples: the `10` cell is not physically realized; branch gating changes the plant consequence; an endpoint sign changes with attention; the reported target follows a questionnaire label rather than the fixed instrument; or event logging cannot distinguish read from availability.

This protocol is a design specification, not authorization for a new human experiment.

## 5. Thought experiments and their roles

### Motor-only missing corner

Hold a robotically generated movement and tactile consequence fixed. Gate only the two predictor inputs. The active/passive/rest triangle yields `001`. If the unobserved `10` cell is high, `M` suffices in the frozen model; if low, `M AND P` survives. Fixed: plant trajectory, touch, endpoint and body context. Variable: consumer input. Counterexample role: active-only evidence does not decide motor sufficiency versus synergy.

### Motorized abacus versus hand-worked abacus

Make the bead trajectory and final answer identical. In one case a hand command and proprioceptive return enter a human consumer; in another a motorized abacus supplies the same bead states while the observer's goal-directed attention supplies a substitute predictor. Output and bead history do not identify the consumer path. This preserves the inherited abacus/calculator family while making its role specific: matched calculation is a negative control for body/action-source inference.

### Human-realized artificial consumer

A human follows a lookup table implementing `M OR P`; a software relay computes the same table. The abstract function matches, but the human process, the software process, and the coupled larger process are distinct actual candidates. Replacing one implementation with another does not license transferring complete organization or a named feeling from the abstract table.

### Copy, switch, and formation history

Train one route through active movement and a second through predictable passive motion or goal cues until both preserve tactile precision. Copy the final response table and switch which physical carrier reaches the consumer while synchronized values are maintained. Current endpoint equality does not recover formation history, same-lineage retention, or actual current intake. The experiment fixes the table and varies lineage/use; it is a counterexample to reading current functional substitutability as numerical identity or familiar mineness.

### Ancestors/formation

Across a graded family from mechanically imposed movement to actively predicted movement, no member loses basal experience merely because motor-command prediction is absent. The variable is the organization of prediction, attention and bodily reference, not experience existence. This thought experiment prevents the consumer comparison from becoming a covert consciousness threshold.

## 6. Direction check after result

The work answers one main-line question: the active/passive/rest triangle cannot by itself decide motor sufficiency, proprioceptive sufficiency, or synergy/substitution; the missing `10` branch-isolation cell is the exact functional discriminator in the frozen two-input class. The added bridge is positive but bounded: actual consumer relations, once independently grounded, are experience-internal under C1. The remaining gap is equally explicit: even the full four-cell endpoint table does not identify read occurrences or a named feeling, and real studies require attention/body-state/context dimensions.

No further source enumeration is warranted this round. The next question should be whether one physically feasible branch manipulation or naturally occurring deafferentation design can approximate the `10` contract while preserving the tactile consequence and independently measuring agency and ownership, or whether the contract is unrealizable in humans and must remain an engineering thought experiment.

## 7. Novelty and reuse boundary

The Boolean completion count, factorial contrasts, logical OR, short-circuit evaluation, and endpoint dissociation are not claimed as new mathematics. Efference-copy, forward-model, attention, sensory-attenuation, agency and ownership mechanisms are prior work. UCT I–III supply the actual-token/C1/intelligence/report framework; R181–R205 and SCU supply practical-centering, endpoint typing, actual use, source correspondence and probe limits.

The reusable increment is their exact assembly around the missing motor-only consumer counterfactual, the `2^k` endpoint-vector warning, a read-occurrence countermodel, and a current primary-evidence table that prevents “attenuation” or “self-feeling” from being used as one undifferentiated variable.

