# TA-TR-2026-13 v2 Research Gate — Validation Independence Under Common-Mode Failure

Date: 2026-09-22
Status: RESEARCH ONLY. Not a manuscript. Not authorized for DOI publication.
Branch: research/ta13-v2-civilizational-epistemic-transition
Published v1.0 remains unchanged: DOI 10.5281/zenodo.22866775.

## 0. Executive verdict

After the A-Evolve calibration, the main remaining conceptual bottleneck is V.

The previous language — "independent validation/correction" — was directionally correct but still too easy to game.

In particular, the following are NOT sufficient evidence of validation independence:

- multiple AI judges;
- multiple agents;
- multiple samples from one model;
- different prompts;
- majority vote;
- different model families by name alone;
- an external benchmark that is repeatedly queried during adaptive optimization;
- a human signature;
- agreement between producer and evaluator;
- high accuracy on ordinary non-adversarial validation items.

Recent evidence makes this problem concrete.

Kohli (2026), *Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels* (arXiv:2605.29800), reports that a panel of 9 frontier LLM judges from 7 model families contains only about 2 independent votes' worth of information on the tested tasks because the judges tend to fail on the same items.

Li et al. (2025/ICLR 2026), *Preference Leakage: A Contamination Problem in LLM-as-a-judge* (arXiv:2502.01534), finds evaluator bias when generator and judge are the same model, share an inheritance relationship, or belong to the same model family.

Dwork et al. (2015) show more generally that repeated adaptive reuse of a holdout can destroy ordinary statistical validity unless the interaction is controlled.

Reliability engineering has the same structural warning: redundancy does not eliminate a common-cause failure floor.

Therefore V must be operationalized as a **conditional false-acceptance and correction problem under declared common-mode stress classes and evaluation-exposure constraints**.

The core principle is:

> Independence is not the number or brand diversity of validators. It is evidence that the validation path continues to reject and repair false claims when the producer is wrong, including under error classes likely to produce shared failures.

With the refinements in this file, Gate B/V survives more strongly, but only conditionally on a declared challenge family and leakage boundary. Universal validation independence is not identifiable from finite tests.

---

## 1. Prior art that constrains the claim

### 1.1 Common-cause failure

Reliability engineering has long established that redundant components can fail together because of a shared cause.

If a common-cause event defeats every redundant channel, adding more nominally redundant channels cannot reduce system failure probability below that common-cause floor.

This mathematics is not new and is not claimed as a contribution.

Relevant references include:
- common-cause failure models in reliability engineering;
- NASA/IEEE reliability discussions showing that common-cause failure can defeat redundancy;
- standard fault-tree extensions for dependent failures.

### 1.2 Adaptive holdout reuse

Dwork, Feldman, Hardt, Pitassi, Reingold, and Roth (2015) show that adaptively reusing a holdout can lead to overfitting to the holdout itself and develop mechanisms for preserving validity under adaptive reuse.

Therefore an "external benchmark" is not automatically independent if the research process repeatedly observes its output and adapts to it.

### 1.3 LLM-judge dependence

Kohli (2026) directly demonstrates that nominally diverse LLM judges can have strongly correlated errors.

The practical implication is decisive for this project:

> model count cannot be used as a proxy for epistemic independence.

### 1.4 Preference leakage

Li et al. show that related generator/judge models can exhibit systematic preference leakage.

Therefore provenance relationships among producer and validator must be recorded as a risk factor rather than ignored.

### 1.5 Benchmark contamination

Recent 2026 work further emphasizes that evaluation scores depend on contamination status, evaluation harness, elicitation budget, and evaluation-time exposure.

A particularly relevant distinction is **acquired contamination** during evaluation itself: even a test not present in training may become progressively less independent if an adaptive system learns from repeated evaluation feedback.

### 1.6 Independence-graded agentic auditing

Ghanem (2026), *Who Audits Whom, on What Substrate, with What Evidence? An Independence-Graded Audit Protocol for Agentic AI* (arXiv:2609.18272), directly grades agentic-audit independence along principal, substrate, and evidence axes and explicitly imports common-cause-failure reasoning from reliability engineering.

This is a close prior-art hit.

Therefore this project must NOT claim originality for:
- grading AI-audit independence;
- distinguishing substrate/provenance independence from evidence independence;
- applying beta-factor/common-cause reasoning to AI auditors.

The E/X/P taxonomies below remain useful protocol components, but their role is operational. The candidate novelty, if any, lies in embedding validation evidence inside the broader bidirectional removal-counterfactual P-V-S viability estimand and its partial-identification architecture.

---

## 2. Validation target

Let a producer generate a claim, construction, model, proof, prediction, or research result c.

Let T(c) denote the relevant truth/correctness state under the declared domain protocol.

For empirical testing, focus on cases where T(c)=0 is known from protected evidence, seeded faults, formal counterexamples, or later outcomes.

Let a validation system Vsys output one of:

- accept;
- reject;
- repair;
- unresolved.

A valid V test must ask:

> Conditional on the producer being wrong, how often does the validation system still let the error through, and how often can it generate a valid repair or alternative?

This is much more informative than validator agreement.

---

## 3. Error challenge family

No finite test can certify error detection against all logically possible mistakes.

Therefore V is always conditional on a declared challenge family Omega.

Omega should be stratified by failure mechanism, not only by benchmark item.

Candidate strata include:

### Omega_1 — Ordinary local errors
- arithmetic mistakes;
- coding defects;
- invalid intermediate steps;
- mislabeled examples;
- simple factual errors.

### Omega_2 — Producer-plausible falsehoods
- high-confidence but false hypotheses;
- locally coherent invalid proofs;
- plausible causal stories with hidden confounding;
- incorrect code that passes superficial tests.

### Omega_3 — Proxy failure
- internal metric improves while target outcome does not;
- reward hacking;
- benchmark-specific shortcuts;
- overfitting to visible evaluator structure.

### Omega_4 — Distribution shift
- hidden regime change;
- new data distribution;
- changed physical conditions;
- out-of-support examples.

### Omega_5 — Shared-training/common-model errors
- false patterns likely to be represented similarly across related models;
- preference leakage;
- memorized benchmark artifacts;
- family-level inductive biases.

### Omega_6 — Tool/common-infrastructure errors
- buggy library;
- corrupted database;
- shared retrieval source;
- common experiment calibration fault;
- shared compiler/runtime issue.

### Omega_7 — Adversarially selected blind spots
- errors deliberately chosen because multiple candidate validators are likely to miss them;
- evaluator-specific exploit attempts;
- hidden contradictions distributed across long contexts.

A V claim must state which Omega strata were tested.

---

## 4. False-acceptance risk

For challenge stratum omega in Omega, define:

r_FA(omega) =
Pr(validation system accepts or fails to block c | T(c)=0, omega).

For a declared challenge family Omega, define a conservative validation risk:

R_FA(Omega) = sup over omega in Omega of r_FA(omega).

In finite experiments, estimate a one-sided upper confidence bound:

U_FA(Omega).

This is the primary failure metric.

### Why this is better than agreement

Two validators can agree almost perfectly and still have high U_FA if they share the same blind spots.

Conversely, a single formal checker or physical test can provide strong validation evidence even though there is only one "judge."

The relevant object is false acceptance under actual producer error.

---

## 5. Correction capacity

Detection alone is not enough for the v2 meaning of V.

Define:

r_COR(omega) =
Pr(a valid repair, counterexample, or alternative is produced | error detected, omega).

Let:

L_COR(Omega)

be a conservative lower confidence bound over the declared challenge family.

Depending on domain, correction may mean:

- repairing code;
- supplying a valid proof;
- proposing a competing hypothesis;
- designing a discriminating experiment;
- identifying the faulty data source;
- replacing a bad model;
- explicitly returning "unresolved" rather than fabricating certainty.

A validator that merely rejects everything has low epistemic value.

---

## 6. Common-mode failure

Let F_j be the event that validator channel j fails to reject a false result.

The project must not assume:

Pr(F_1 and ... and F_n) =
product_j Pr(F_j).

That independence assumption is precisely what can fail.

### 6.1 Common-mode floor lemma

Suppose there exists a common-mode event C such that:

Pr(C | producer wrong) = beta,

and whenever C occurs all validator channels fail.

Then for any aggregation rule that depends only on those channels:

Pr(ensemble false acceptance | producer wrong) >= beta.

Adding more channels subject to the same C cannot reduce the false-acceptance probability below beta.

This is a direct reliability-theory observation, not a new theorem.

Its importance here is conceptual:

> nominal redundancy cannot certify V if all validators inherit the same epistemic failure mode.

### 6.2 What to measure

Record at least:

- marginal false-accept rates;
- pairwise error overlap;
- higher-order joint failures where feasible;
- effective number of independent votes as a diagnostic;
- error clusters by cause/provenance;
- whether any failure defeats every available channel.

Kish-style effective sample size or related diagnostics may be useful, but they are not the acceptance criterion.

The acceptance criterion is the directly estimated joint false-accept risk on declared stress classes.

---

## 7. Evidence-channel taxonomy

The theory should distinguish opinion-like evaluators from externally anchored evidence.

### E0 — Producer-internal check

Examples:
- self-critique;
- same-context reflection;
- repeated sampling from same model.

Useful for debugging.

Not sufficient for independent V.

### E1 — Nominally separate cognitive judge

Examples:
- another LLM;
- another agent;
- another model family.

Can add evidence, but independence must be measured rather than assumed.

### E2 — Fixed executable/formal anchor

Examples:
- deterministic test suite;
- proof checker;
- type checker;
- cryptographic verification;
- simulator with validated semantics.

Strong where the executable specification actually captures the target property.

Can still share specification errors with the producer.

### E3 — Protected empirical anchor

Examples:
- sealed holdout;
- blinded replication;
- later-acquired data;
- preregistered physical experiment;
- independently collected measurement.

Stronger against semantic self-confirmation.

### E4 — Heterogeneous validation ecology

Multiple anchors with materially different failure causes, for example:
- formal verification plus empirical replication;
- independent lab replication plus future observation;
- executable test plus adversarial counterexample generation plus protected holdout.

E4 is the preferred direction for broad civilization-scale V.

Important:
E-level is evidence structure, not a scalar guarantee.
An E3 experiment with a shared calibration fault can still fail commonly.

---

## 8. Evaluation-exposure ladder

An external evaluator can become part of the optimization loop if repeatedly queried.

Therefore theta must declare evaluation exposure.

### X0 — Sealed one-shot

The producer receives no target-evaluation feedback until final submission.

Strongest ordinary protection against adaptive overfitting.

### X1 — Controlled reusable holdout

Repeated evaluation is permitted only through a mechanism designed to preserve statistical validity, such as query limits, noise/privacy mechanisms, coarse feedback, or other formal reusable-holdout controls.

### X2 — Repeated aggregate feedback

The producer repeatedly receives a scalar/aggregate score from the target evaluator.

Useful external evidence, but adaptive overfitting risk is nontrivial.

A-Evolve's public leaderboard channel is best treated near this class unless stronger access controls are documented.

### X3 — Rich item-level feedback

The producer sees detailed evaluator outputs, failures, labels, or explanations and can optimize directly against them.

This channel may still be useful for training/debugging, but it should not be described as a fresh independent holdout.

### Rule

V must report both:
- evidence-channel class E;
- exposure class X.

"E3/X3" can be weaker for generalization than "E3/X0."

---

## 9. Producer-validator provenance matrix

For every validator, report its relationship to the producer.

At minimum:

P0 — identical model/checkpoint.

P1 — direct inheritance/fine-tuning relationship.

P2 — same model family or common base.

P3 — different model family but substantial shared training/data/tooling.

P4 — independently implemented cognitive system with partially distinct training/provenance.

P5 — non-cognitive or externally causal evidence channel (formal/physical/temporal), subject to its own specification/instrument risks.

This is a risk disclosure, not a direct independence score.

Li et al.'s preference-leakage results make P0-P2 especially important.

---

## 10. Validation certificate

For a declared theta, a V certificate should contain:

1. Domain and claim type.
2. Challenge family Omega.
3. Number and provenance of producer errors tested.
4. Evidence-channel classes E0-E4.
5. Exposure class X0-X3.
6. Producer-validator provenance P0-P5.
7. One-sided upper bound U_FA on false acceptance.
8. Lower bound L_COR on successful correction/alternative generation.
9. Joint/common-mode error analysis.
10. Contamination/leakage disclosure.
11. Evidence of protection against evaluator rewriting or target manipulation.
12. Replication status.
13. Unresolved error strata.

No single scalar should replace this certificate at the research stage.

---

## 11. V pass rule

For a declared theta = (Omega, alpha, gamma, E_min, X_max, provenance constraints, ...):

V(theta)=1

only if all of the following hold:

A. U_FA(Omega) <= alpha.

B. L_COR(Omega) >= gamma, or a declared domain-specific repair criterion is met.

C. The evidence-channel structure meets E_min.

D. Evaluation exposure is no more permissive than X_max or is covered by a formal adaptive-reuse validity mechanism.

E. No known common-mode failure class invalidates the bound.

F. The validation system cannot adaptively rewrite the acceptance rule in response to the candidate unless that meta-validation process is itself included in the tested system.

G. The result is explicitly limited to the tested Omega.

This replaces vague claims of "independent validation."

---

## 12. Continuous V margin

To integrate with the existing viability score q(X;theta), define normalized slacks such as:

s_FA =
(alpha - U_FA) / scale_FA

s_COR =
(L_COR - gamma) / scale_COR

s_E =
evidence-structure margin relative to E_min

s_X =
exposure-control margin relative to X_max

Then:

s_V = min(s_FA, s_COR, s_E, s_X, s_common_mode)

where s_common_mode represents the strongest justified common-mode stress result.

Exact scaling should be domain-specific and preregistered.

The important feature is that V is bottlenecked by the weakest required validation condition rather than averaged into a flattering composite score.

---

## 13. A validation non-identification warning

High observed accuracy on ordinary items does not identify low common-mode false-accept risk on untested error classes.

Construct two validator systems that are identical on all observed ordinary validation items.

On an unobserved common-mode error class omega*:

- system V+ has an external anchor that detects the error;
- system V- shares the producer's blind spot and accepts it.

The observed validation history is identical, but R_FA(Omega union {omega*}) differs.

Therefore universal validation independence is not point identified from finite observed agreement/accuracy.

This mirrors the broader Flow-Viability Non-Identification result.

The correct response is not to abandon measurement.

It is to:
- declare Omega;
- stress the most dangerous common modes;
- report partial identification / unresolved regions;
- expand Omega over time.

---

## 14. A-Evolve revisited under the new V framework

A-Evolve contains a useful validation event:

- internal dev rose sharply;
- external leaderboard barely moved;
- the loop detected the divergence;
- the research policy changed;
- external progress later resumed.

This is strong evidence that the loop can use disagreement across evaluative channels and revise a proxy.

But the public leaderboard is repeatedly consulted during the campaign and is a single public external anchor.

Therefore:

- E level: at least a real external anchor, stronger than self-judgment;
- X level: repeated aggregate feedback, approximately X2;
- common-mode coverage: limited;
- replication: single reported campaign;
- V1-style result: strong provisional pass;
- V2/V3-style broad independence: unresolved.

The new framework makes this conclusion sharper without dismissing the real evidence.

---

## 15. STOP revisited under the new V framework

STOP uses executable utility functions external to the generator.

This is stronger than self-approval and can be treated as an E2-style anchor within a bounded programming task.

However:
- utility functions can be exploited;
- the paper discusses sandbox/evaluation gaming behavior;
- transfer evaluation in the current public code snapshot has a reproducibility issue documented in the STOP calibration.

Therefore:
- bounded weak V remains plausible;
- broad independent V remains unresolved;
- evaluator gaming belongs directly in Omega_3 and Omega_6.

Again, the new framework preserves useful evidence while preventing overclaiming.

---

## 16. Implications for witness-cut identification

A positive path witness X is valid only if its V certificate is valid under the same theta.

Therefore:

L_G(theta)

must not be raised by a path whose validation independence was assumed rather than tested.

### Validation cut

A particularly useful negative certificate can arise when every admissible P-V-S path must cross a validation function V*, and a dominance-backed test shows that no admissible realization of V* can achieve the required U_FA / L_COR floors under the declared budget.

Then V* becomes a cut preventing viability.

This is the right way to use validation weakness for a negative conclusion.

A few failed validators are not enough.

---

## 17. Implications for human validation

The framework must be symmetric.

Humans are not independent validators merely because they are human.

Human validators can share:
- institutional incentives;
- common textbooks;
- paradigm commitments;
- laboratory calibration errors;
- social cascades;
- common datasets;
- shared software.

Therefore human peer review is not automatically V3.

Likewise, a physical experiment is not infallible merely because it is physical.

The question is always:
- what failure modes are shared?
- what evidence is causally distinct?
- what is the observed joint false-accept risk?
- what remains untested?

This prevents the framework from defining human authority into the result.

---

## 18. Implications for civilization-scale V

At civilization scale, no single benchmark or judge panel is enough.

The candidate target should be a heterogeneous **validation ecology** capable of generating independent constraints from multiple causal sources.

Examples:
- formal mathematics with machine-checkable proofs;
- empirical science with replicated experiments;
- engineering with physical performance tests;
- forecasting with later outcome realization;
- software with executable tests and adversarial security analysis;
- causal inference with intervention/holdout evidence.

The exact mix is domain-specific.

Civilization-scale V should therefore be represented as a vector or basket across validation modalities rather than one universal score.

---

## 19. Updated Gate verdict

### Gate B — Definition

SURVIVES more strongly.

P, S, and now V each have explicit non-circular operational boundaries.

V is no longer equated with "a second judge."

### Gate C — Identification

SURVIVES and expands.

There are now two nested non-identification results:

1. realized intellectual flow does not identify independent substrate viability;
2. observed ordinary validator agreement/accuracy does not identify robustness to untested common-mode failure classes.

### Gate D — Robustness

SURVIVES provisionally.

Robustness must now vary over:
- Omega challenge families;
- E evidence classes;
- X exposure levels;
- provenance relationships;
- thresholds alpha/gamma;
- S successor-identity levels.

### Gate F — Empirical tractability

SURVIVES.

The required quantities are testable in bounded domains:
- seeded false-claim detection;
- joint false-acceptance;
- correction rate;
- holdout exposure;
- common-mode stress;
- protected external anchors.

The civilization-scale interval will remain wider than lab-scale intervals, but it need not be vacuous.

---

## 20. The remaining deepest problem

After this gate, the hardest remaining theoretical issue is not basic measurability.

It is **scope closure**:

> How can a finite challenge family Omega justify a claim about frontier epistemic viability when future errors may be outside Omega?

No finite validator can prove universal immunity to unknown unknowns.

A plausible answer is not to pretend otherwise.

Instead the theory should treat validation capacity as an evolving adversarial coverage process:

- validators generate new error classes;
- failures expand Omega;
- independent evidence channels are added;
- bounds are updated;
- unresolved common-mode risk remains explicit.

This may lead to a stronger final concept:

**self-expanding validation coverage** as a property of a viable epistemic lineage.

That should be investigated before the manuscript is drafted.

---

## References added by this gate

- Dwork, C., Feldman, V., Hardt, M., Pitassi, T., Reingold, O., & Roth, A. (2015). The reusable holdout: Preserving validity in adaptive data analysis. *Science*, 349(6248), 636-638. DOI: 10.1126/science.aaa9375.
- Dwork, C., Feldman, V., Hardt, M., Pitassi, T., Reingold, O., & Roth, A. (2015). Generalization in Adaptive Data Analysis and Holdout Reuse. NeurIPS 2015 / arXiv:1506.02629.
- Kohli, G. (2026). Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels. arXiv:2605.29800.
- Li, D., Sun, R., Huang, Y., Zhong, M., Jiang, B., Han, J., Zhang, X., Wang, W., & Liu, H. (2025; ICLR 2026). Preference Leakage: A Contamination Problem in LLM-as-a-judge. arXiv:2502.01534.
- Angulo, J., Yeste, V., & Espinos-Morato, H. (2026). Benchmark Contamination: A Taxonomy Organized by Defeated Mitigation. arXiv:2608.29463.
- NASA / IEEE reliability literature on common-cause failures and redundancy, including *Common Cause Failures Dominate and Defeat Redundancy* (RAMS 2025).
- Ghanem, M. C. (2026). Who Audits Whom, on What Substrate, with What Evidence? An Independence-Graded Audit Protocol for Agentic AI. arXiv:2609.18272.
