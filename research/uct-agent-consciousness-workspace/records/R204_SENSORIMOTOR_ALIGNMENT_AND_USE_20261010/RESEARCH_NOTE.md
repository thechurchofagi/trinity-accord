# R204 — Sensorimotor alignment and actual feedback use under matched successful behavior

Research ID: R204-SAU-20261010. Result: SAU-RESULT-v0.2.0. Date: 2026-10-10. Disabled working module.

## 1. Return to organization

R203 stopped at a valid calibration limit: marker/report statistics cannot independently certify familiar-continuity semantics. R204 returns to a concrete action organization. It separates three quantities that a claim about familiar bodily action must not silently identify: external task success, current predictor–consequence alignment, and executed feedback consumer use. A successful task output can be identical across all four combinations of alignment and use.

The contribution is an explicit UCT application and probe contract, not invention of forward models, adaptive control, permutation invariants or sensory prediction error. It refines which physical relation could be included in an experience-internal body/action descriptor under C1. It does not identify that descriptor as familiar mineness H.

## 2. Typed model

Let A be n action ports and Y be n physically grounded consequence ports. Let T=Y be the target set. Initially P:A→Y is the actual plant map, F:A→Y the presently carried forward predictor, C:T→A the task controller, and U∈{0,1} a declared consumer gate. The finite comparison class uses bijections P,F,C. Intermediate learning may yield a nonbijective F; all update rules remain total maps.

The initial task output is P(C(t)). Define exact success S iff P∘C=id_Y; define predictive alignment K iff F=P on the declared action support. U represents the actual execution of the named feedback-to-predictor consumer in this model, not conscious intention or human agency. It is distinct from an experimenter's telemetry E_U.

After action a and sensory feedback y, the specified consumer applies

F⁺(x)= y if U=1 and x=a; otherwise F(x).

For veridical feedback y=P(a), this is a feedback-driven row replacement. Neither controller nor plant is changed by this particular consumer; this is a predictor-learning module, not a claim to reproduce the full human motor system. A subsequent prediction readout tests the carrier update. Every inference retains the same P,F,C,U, action support and episode sequence. A training-history label is not a physical prior-occurrence/continuation witness.

## 3. R204-C1 — separation and a successful-output quartet

For n≥2 all eight Boolean combinations of (S,K,U) are realizable in the unrestricted permutation comparison class. Choose P=id. To select S choose C=id or a nonidentity permutation. Independently select K by F=id or a nonidentity permutation. Independently choose U. These constructions prove logical independence on this class; they do not imply independence in every biological architecture.

For the stronger matched-behavior comparison fix n=2, P=C=id. Change only F and U:

| Predictor alignment K | Consumer U | Initial task output | After real feedback at mismatched action |
| --- | --- | --- | --- |
| 1 | 1 | Every target correct | No carrier value change needed |
| 1 | 0 | Every target correct | No carrier change |
| 0 | 1 | Every target correct | Named predictor row is corrected |
| 0 | 0 | Every target correct | Mismatch remains |

Thus performance and identical overt first-episode output do not decide predictive alignment or current feedback use. The comparison holds success fixed; it does not equate arbitrary human “fluency” with success or prove that every hidden burden was matched.

## 4. R204-C2 — a probe with an explicit failure condition

Under the stated update law, veridical-feedback carrier change satisfies

F⁺≠F iff U=1 and F(a)≠P(a).

Proof: the only writable row is a; the written value differs exactly under the conjunction. Consequently a null update is compatible both with an inactive consumer and with a fully active already-calibrated consumer. Null adaptation is not proof of no use.

A prospectively introduced sensory discrepancy z≠F(a) yields F⁺≠F iff U=1. This is a diagnostic consequence of the declared model. In an actual experiment it supports the consumer only if the intervention really reaches the intended feedback port, the later readout measures the named carrier, and alternative writers, clamps and resets are excluded. It is not an unconditional human consciousness diagnostic.

A reflexive or freshly installed learner can have the same update law. A complete copied current state produces the same future updates regardless of an unused biography label, preserving R199. These alternatives defeat the claim that this response alone establishes same-lineage RetBind, H, deliberate recognition or a unique owner.

### R204-C5 — a reflex alternative to an error comparator

Compare two implementations: an error-gated writer writes iff U=1 and F(a) differs from y; an unconditional reflex writer writes whenever U=1. They induce the identical F-state transition for every (F,a,y,U): writing an equal value is state-preserving. Induction gives identical predictor-state traces for all feedback sequences. Their actual internal write-event traces differ at matching feedback. Therefore even exhaustive F-state probe success cannot independently certify an executed comparison/error-consumer architecture. Extra physically grounded interior evidence or an intervention on the comparator interface is needed. A declared write-event port can distinguish the programs; a logging signal whose source is unvalidated cannot.

This repairs a tempting overinterpretation of the minimal update model. It does not imply complete organizational sameness or complete experiential sameness. It shows only that the selected state/feedback view loses an implementation distinction. The code enumerates the pair, retaining the failure of the proposed comparator interpretation.

## 5. R204-C3 — port covariance and gradual organization

Relabel actions by α and consequences by β, transporting all maps:

P′=β∘P∘α⁻¹, F′=β∘F∘α⁻¹, C′=α∘C∘β⁻¹.

Then P′∘C′=β∘(P∘C)∘β⁻¹, so exact success is preserved. F′=P′ iff F=P. The fraction of action rows on which F differs from P is also preserved under uniform transported support. Changing F's labels alone while leaving the physical plant/ports fixed is a model change, not a harmless isomorphism. Nonuniform action weights must be transported too.

For stochastic predictor rows F_λ=(1−λ)F+λP, define mean total-variation prediction mismatch E_λ against the deterministic plant. For λ∈[0,1],

E_λ=(1−λ)E_0.

Proof: the mass on the actual consequence at each row increases linearly toward one; TV from a point mass is one minus that mass. This gives a continuous selected organizational coordinate without a new experience threshold. It does not prove that H is linear in λ or that complete physical organization follows this one-dimensional path.

## 6. Actual experience interpretation and its limit

Under C1, *independently grounded actual* predictor, plant, feedback and consumer relations may have structural counterparts inside the experience of the specified actual process. This conditional transport inherits the complete-signature and same-instance contract; finite model alignment is not a complete signature, and telemetry is not actual use. Neither calibration nor consumer use is required for basal experience. Local and whole actual processes may coexist; no exclusive extra owner is inferred.

The positive organizational distinction survives without report or “self” labels: the same successful action can be embedded in different current prediction/use relations. Whether these relations correspond to familiarity, agency, ownership, mere unnoticed adaptation or something else remains an independent semantic bridge. Successful control is not identical to the selected experience structure; no general experiential level follows from the three bits.

## 7. Concrete experimental contract

Use a programmable robot or cursor controller first, where the named maps, carrier update and gate can be audited. Freeze plant and task controller so target output remains matched. Cross a correct predictor with a swapped predictor and an enabled writer with a blocked writer. Feed actual feedback, then a predeclared discrepancy, and query the same row before and after. Confirm the quartet and the conditional probe predictions. This is feasible mechanism testing without claiming a human H measurement.

For a later adult task, compensation that preserves target accuracy while perturbing sensory expectations is only an analogy. Do not presume control of human F or U. Collect separate prediction evidence, retention/aftereffect traces and independently justified H evidence. Reject the named route model if, with intervention/readout validity established, blocked writers still change the carrier or enabled writers fail under a forced mismatch. Alternative routes may explain such a failure, so narrow the claim rather than denying experience. No participants or physiological data were collected here.

## 8. Exact execution and prior-art comparison

check_alignment_and_use.py executed 28,096 models over n=2,3,4, 111,920 veridical-feedback probes, 333,088 action/output relabelings and 6,776 exact rational mixtures; zero violations. It realizes all eight combinations and exports the success-matched quartet. The code checks the stated model; it neither measures H nor proves a general biological mechanism.

Wolpert, Ghahramani and Jordan (1995), DOI 10.1126/science.7569931, studied internal forward models; author-hosted abstract inspected. Mazzoni and Krakauer (2006), DOI 10.1523/JNEUROSCI.5317-05.2006, observed that an initially successful explicit compensation strategy did not prevent implicit adaptation; institutional abstract inspected. Tseng et al. (2007), DOI 10.1152/jn.00266.2007, distinguish sensory prediction error from online motor correction; institutional abstract inspected. These are direct antecedents, not evidence for H or C1. Publisher access failures prevented full-text proof-level comparison; priority remains unverified. The 2026 cortico-cerebellar preprint found in search also combines predictive representations and feedback; only search abstract obtained, and none of its numerical claims is used.

Internal antecedents: R173 separated actual retention/use from current competence, R190 separated bodily coupling and action organization, R199 limited lineage inference, and R203 separated measurement evidence from target semantics. R204's net addition is the explicit physically typed alignment/use quartet, forced-discrepancy versus null-update contract, and continuous/relabel-compatible coordinate. It does not replace or republish those broader conclusions as new.

## 9. Decision and next question

This is a bounded positive mechanism module with exact code and falsifiers, suitable for a combined future organization/familiarity paper. It is not an independent empirical breakthrough. Decision: CONTINUE_RESEARCH_HOLD_STANDALONE. Completed map remains v1.1.2; candidate disabled; all four review findings remain open.

Next: distinguish discrepancy-based calibration from *action-source* organization. Can matched self-produced, passively imposed and remotely produced consequences differ in which command-origin carrier is actually consumed, even when prediction error and task success match? Define that physical origin relation without assuming feeling, then test a reflex/clone alternative. Do not repeat generic sign calibration.
