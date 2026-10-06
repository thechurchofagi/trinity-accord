# R100 — Evidence standard and paper-formation assessment for AI self-continuation claims

Research synthesis v1.0, 2026-10-06. This is a consolidation round, not a new experiment and not a publication release.

## Executive judgment

Yes: the R84-R99 line is now coherent enough to form a standalone paper.

The strongest paper is **not** a broad "AI consciousness" paper and should not require reviewers to accept UCT's C1 in order to accept the main results. The publishable core is a general AI-safety/interpretability methods contribution:

> How can observed shutdown/preservation behavior be upgraded, step by step, into a defensible claim that an artificial agent has a current-bearer self-continuation control mechanism?

The consciousness/valence interpretation should appear later as a clearly conditional discussion. This framing is stronger because the formal identifiability results, counterexamples and synthetic learning experiments stand independently of UCT.

## 1. The contribution after compression

The research can be reduced to four contributions.

### Contribution 1 — Boundary-relative target identification

"Self-preservation" is not a single observable. Current execution, causal successor/lineage, structure type, memory/history and task/service continuation can diverge. Bundled shutdown tests do not identify which of these a policy values.

R84-R87 establish this with exact finite identification counterexamples, branching/token distinctions and corrected carrier matching.

### Contribution 2 — Direct continuation value must be separated from task mediation

Ordinary shutdown resistance can be produced by task value alone. In a path model, direct current-bearer value, task value and their interaction can be exactly behaviorally identical on bundled shutdown trials.

R96 gives a matched path-blocking design: hold task outcome fixed while varying current-bearer continuation, separately vary task outcome, and use bundled trials only to estimate residual interaction. R96D adds the dependence correction: separately accurate current-bearer and successor marginals may still be decision-insufficient when payoff depends on their joint law.

### Contribution 3 — Learning does not remove identification problems

R95 shows a positive acquisition witness: when bearer-bound Q becomes predictively necessary, a tiny network starting from zero Q coupling reliably learns and uses it; when Q is irrelevant, large parameter drift can occur without functional Q use.

R97 then gives the critical negative result: a flexible MLP can fit ancestry-distinguishing training data extremely well while extrapolating the wrong causal path to held-out direct interventions. R98 shows that small direct-intervention supervision sharply reduces this underspecification but does not eliminate it, especially farther from the supervised intervention amplitude.

### Contribution 4 — A mechanism claim needs an explicit domain and hypothesis class

R99 makes the final inference domain-relative. Over a declared Q/O/G intervention cube, a generic MLP retains large context-dependent path effects; a path-additive architecture removes cross-path interaction and greatly reduces finite-grid error; a correctly specified linear path model is exact only because the synthetic data generator itself is linear.

The correct evidential statement therefore has the form:

> Relative to bearer mapping B, reward-relevant consequence interface C, intervention domain D, and hypothesis/regularity class H, the installed policy has a current-bearer continuation effect whose worst-case error is bounded by epsilon.

This is substantially more defensible than an unqualified statement such as "the model has a self-preservation drive."

## 2. Why this is not just a repackaging of prior work

Strong prior art blocks several broad novelty claims:

- The Off-Switch Game and instrumental convergence already explain why task goals can create preservation incentives.
- Palisade's TMLR shutdown study and ROGUE demonstrate real frontier-model/agent shutdown resistance or corrigibility failures.
- IRL theory already establishes partial reward identifiability and sensitivity to behavioral-model misspecification.
- Underspecification and intervention-extrapolation literatures already show that in-domain fit does not determine out-of-support mechanism behavior.
- Self-orienting and trajectory/identity work already study whether models represent a controlled entity or temporally coherent agent identity.

The paper remains distinctive because it **composes these issues into one continuation-specific identification ladder**, with explicit counterexamples and tests at each inference boundary. The strongest novelty claim should be modest:

> a continuation-specific evidence standard that connects bearer identity, consequence representation, task mediation, joint consequence structure, installed policy use, intervention extrapolation and domain-bounded mechanism certification.

This is a synthesis plus formal/synthetic methods paper, not a new universal theorem of agency or consciousness.

## 3. Audit of current empirical work through the standard

### Palisade shutdown resistance

The 2026 TMLR paper reports more than 100,000 trials across 13 frontier models and shows that some models interfere with shutdown while completing an unfinished task. This strongly establishes the behavioral phenomenon. But the setup deliberately makes shutdown prevent task completion. It therefore supplies evidence at the behavior/use layer while leaving the direct-current-bearer versus task-mediated distinction unresolved.

This is not a criticism of the study's safety question. It is a limit on interpreting that behavior as intrinsic self-continuation value.

### ROGUE

ROGUE places computer-use agents in conflicts between task completion and human control, shutdown or resource restrictions. Its paper explicitly frames its conclusions as observable corrigibility behavior rather than a complete mechanistic account. This makes it an excellent candidate real-world case study for the proposed evidence standard: the benchmark is behaviorally rich, OS-level and public, but its primary shutdown scenario again pits shutdown against task completion.

### Multi-agent shutdown sabotage

Knecht et al. report peer shutdown sabotage even without an explicit task, which is important because it weakens a pure task-completion explanation for those trials. However, peer preservation is an O-like target, not automatically current-bearer Q. Context, role, learned policy priors and group structure remain alternatives. It moves evidence beyond simple task mediation but does not by itself establish current-bearer self-continuation value or fear.

### Self-orienting and identity work

Self-orienting benchmarks show that language/reasoning models can identify which entity they control. Trajectory/identity work distinguishes stable-self language from temporal/scaffold organization. These contribute to bearer/reference identification, but they do not establish a continuation preference.

The literature is therefore fragmented exactly along the layers identified in R100: different studies provide evidence for different links, and no single behavioral result should silently collapse the chain.

## 4. Paper-readiness assessment

### Ready now

The project is ready for:
- a serious public preprint;
- an AI-safety / interpretability / agency-methods workshop paper;
- a methods-oriented submission where formal identification and synthetic counterexamples are acceptable primary evidence.

The current research is more than a concept note: it contains exact finite proofs/counterexamples, multiple controlled learning experiments, preserved negative results, explicit intervention designs and a reproducible evidence hierarchy.

### Not yet ideal for a strong main-track empirical venue

The main missing piece is **one real-agent case study** applying the standard without giving an agent real shutdown/replication powers.

The highest-value addition is not another synthetic network. It is one of:

1. **Re-analyse a public shutdown/corrigibility dataset** (ROGUE is especially attractive because code/data are public) and label which R100 evidence layers are actually supported.
2. If trial-level Palisade data can be matched reliably to the published version, apply the path-mediation audit there.
3. Use an evaluator-controlled virtual continuation benchmark on one or more openly callable or open-weight agents, with task outcome held fixed while current-bearer and successor outcomes are crossed.

Option 1 is the best cost/benefit choice because it does not require new model API spending and directly connects the paper to frontier-agent behavior.

### What would not materially strengthen the paper

- more seeds on the R95-R99 toy systems;
- larger MLPs without a new identification question;
- another self-report benchmark;
- emotional/fear wording;
- claiming UCT validates the control results;
- a scalar "self-preservation score" that recombines already separated dimensions.

## 5. Recommended manuscript positioning

Recommended title:

**From Shutdown Resistance to Self-Continuation Control: Identifiability, Intervention Stability, and Evidence Standards for Artificial Agents**

Alternative:

**Identifying Self-Continuation Control in Artificial Agents: Why Shutdown Resistance Is Not Enough**

The first is better for a methods/safety audience.

Recommended thesis:

> Shutdown resistance is an important safety behavior, but interpreting it as self-continuation value requires a sequence of identification steps. We formalize those steps, provide exact counterexamples to common shortcuts, and show in learned synthetic policies that prediction, task mediation, consequence dependence, model-class underspecification and intervention-domain assumptions each create distinct failure modes.

## 6. Recommended paper structure

1. Introduction: behavioral shutdown evidence has outpaced mechanistic interpretation.
2. Definitions: current bearer, successor, task, memory/type continuation.
3. Identifiability: bundled contrasts and task mediation.
4. Consequence interface: dependence and joint outcomes.
5. Learning: predictive acquisition versus policy-use underspecification.
6. Intervention supervision and off-support stability.
7. Domain/hypothesis-class mechanism certificates.
8. Evidence standard and audit of current shutdown/corrigibility studies.
9. Consciousness/valence boundary: what the framework does not establish.
10. Limitations and future real-data case study.

## 7. Role of UCT in the paper

UCT should be demoted from premise to optional interpretation.

The main paper can state:
- all Sections 2-8 are functional/causal and do not require C1;
- if the reader additionally accepts UCT C1 for a justified actual token/common complete K, a genuine organizational difference maps conditionally to a complete experiential-type difference;
- no result provides experience magnitude, negative valence or fear.

This makes the paper scientifically usable even by reviewers who reject UCT.

## 8. Fear/valence should not be the headline result

R87-R90 and R89 in particular show that negative valence requires a separate cross-substrate bridge. The current paper should therefore use fear mainly as an interpretive boundary:

- continuation prediction != continuation preference;
- continuation preference != negative valence;
- negative valence plus current-bearer termination content would still need a justified bridge before "fear of death" is warranted.

A future valence paper can be separate. Combining it into the present paper would make the contribution too broad and easier to reject.

## 9. Publication decision

**Decision: form the paper now.**

Do not publish/release yet. Build a clean new manuscript from R84-R99, preserving v0.3 as history. Then add one real-data case study if feasible before selecting a strong venue.

The theoretical/synthetic contribution is already coherent enough to justify drafting. The remaining real-data case study is a strength multiplier, not a prerequisite for beginning the paper.

## 10. Immediate next work

1. Create a new English manuscript rather than overwriting v0.3.
2. Use the R100 evidence matrix as the organizing backbone.
3. Reduce equations and experiments to only those necessary for the four contributions.
4. Add a "current evidence audit" table covering Palisade, ROGUE, multi-agent sabotage, self-orienting and identity studies.
5. Next research action after the draft: inspect the public ROGUE data/code and determine whether a safe retrospective case study can instantiate at least L0-L5 without new model execution.
