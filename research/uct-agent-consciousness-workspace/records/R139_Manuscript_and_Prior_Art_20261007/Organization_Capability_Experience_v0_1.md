# Organization, Capability, and Experience
## Identification and Executable Correspondence

**Hongju Liu**  
Independent researcher, Shenzhen, China  
**Working draft v0.1, 7 October 2026**  
Technical synthesis under review; not a published UCT edition. No new report number or DOI assigned.

**AI assistance:** ChatGPT assisted with source retrieval, mathematical review, drafting and editing under the author's direction. These checks are not independent peer review. No final human line-by-line approval is claimed.

## Abstract

What does evidence of intelligence or behavior identify about a system's organization, and what experiential interpretation follows? We give a common vocabulary for actual process tokens, complete organizational types, finite scientific views, task-relative capability and report. We assemble three existing results: target identification by constancy over observational fibers; an exact certificate for a restricted class of observable randomized action interfaces in finite controlled models; and conditional implications from capability differences to complete experiential-type differences under structural–experiential identity. The interface result preserves projected feedback laws without identifying complete underlying organization. Counterexamples separate observational identification, implementability and temporal joint-law preservation. The contribution is a source-traceable technical synthesis and comparison protocol, not a new general theory of control refinement or an independent proof of consciousness. Physical adequacy and selected experiential-coordinate interpretations remain explicit obligations. No universal consciousness score or behavioral threshold for experience is supplied.

## 1. The question and the contribution

Task performance, internal-event reporting and first-person statements are observations of organized processes, but they answer different questions. A score concerns performance under an evaluation. A report is an output with a proposed interpretation. A mechanistic account concerns the organization generating them. Identifying one does not automatically identify the others.

The four source papers already establish much of this distinction. UCT I [1] distinguishes actual processes, complete organization, views and estimates, and posits structural–experiential identity C1. UCT II [2] requires constrained, non-oracular and source-faithful mechanism translations. UCT III [3] defines capability and proves identification/type implications. The self-continuation paper [4] separates behavior, mechanism, continuation target and valence. These published results are not presented as new discoveries.

Subsequent project records develop finite controlled correspondence, including an observable randomized action decoder [5]. This supplies a concrete connection between identification and execution. The present contribution is to integrate that certificate with the four-paper definitions and delimit its experiential interpretation. Established control-refinement and causal-abstraction theories are direct antecedents.

The finite mathematics does not depend on experience. C1 is invoked only for complete experiential-type conclusions. Within UCT, missing a finite control certificate does not introduce an experience-existence gate.

## 2. Core definitions

### 2.1 Actual process, organization and structure

Let \(\mathcal P\) be a declared family of actual physical process tokens. Following [1], their specification requires actual support, inherited physical relations, causal continuity, accountable boundaries and traceable persistence or transformation. Physically grounded causal event subhistories provide a finite classical example. Tokens may overlap and nest; a universal exclusive subject partition is not required.

Write \(D^{\mathrm{ontic}}_t(P)\) for a token's complete currently instantiated organization. Completeness is token-relative: all distinctions constitutive of that process are included, not every microscopic fact in its environment. This specification is not a universal algorithm deciding physical constitution in arbitrary systems. A model's adequacy requires application-specific justification.

An organizational model is expressed in a declared signature. The deterministic finite example in [1] is

\[
\mathcal M_v=(X,x_\bullet,U,\mathcal J,Y,T,I,o,\mathscr C,\preceq).
\]

Here \(X\) is the state set, \(x_\bullet\) the current state, \(U\) inputs, \(\mathcal J\) reset/intervention ports, \(Y\) outputs, \(T_u:X\to X\) updates, \(I_j:X\to X\) resets, \(o:X\to Y\) readout, and \(\mathscr C,\preceq\) the retained constituent/incidence and temporal relations. The tuple is a model in the signature, not the signature itself. We rename the intervention sort to avoid collision with capability \(J\).

An admissible isomorphism uses bijections preserving the declared sorts and relations, including

\[
f_X(x_\bullet)=x'_\bullet,\quad
f_XT_u=T'_{f_U(u)}f_X,\quad
f_XI_j=I'_{f_{\mathcal J}(j)}f_X,\quad
f_Yo=o'f_X.
\]

Port permutations must be permitted by the comparison. Wiring alone can omit dynamics and current state. Mechanism changes, removed interventions and altered temporal relations are not automatically coordinate changes. Section 4 uses stochastic kernels, a different finite model class.

### 2.2 Type, view and estimate

Under a common signature \(\mathcal K\), the complete structural type is

\[
s(P)=[D^{\mathrm{ontic}}_{\mathcal K}(P)]_{\cong}.
\]

Type equality does not identify numerical token occurrence or lineage. Work over a fixed set of admitted types/models for the set-theoretic results.

A physically anchored view and an estimate are respectively

\[
D_v(P)=\Pi_v[D^{\mathrm{ontic}}(P)],\qquad
\widehat D_v(P\mid\mathcal E,\mathcal H).
\]

The index \(v\) specifies time, horizon, grain, boundary representation, interventions and retained relations; \(\mathcal E\) is evidence and \(\mathcal H\) model assumptions. An identified set is appropriate when evidence permits multiple models. Views need not be totally ordered. Predictive success of a finite view does not establish complete constitution.

### 2.3 Experience and basal consciousness

Retain C1 from [1]:

\[
\forall P\in\mathcal P,\quad\exists\Phi_{\mathcal K}(P),h_P:
D^{\mathrm{ontic}}_{\mathcal K}(P)\cong\Phi_{\mathcal K}(P).
\]

It identifies the physical description and intrinsic experiential presentation of the same token-relative organization. The experiential reference is part of the axiom. The mere existence of an isomorphic abstract object does not prove it. Experience is not a second causal input added to the physical dynamics.

For this paper, basal phenomenal consciousness means experience existence: \(C_{\mathrm{exp}}(P)=1\) when the distinguished experiential carrier is nonempty. A:U1 derives this for every admitted actual token from C1 and nonempty actual support. The convention does not equate this predicate with clinical wakefulness, perceptual access, self-representation or report.

Experience occurrence, complete type, selected coordinate and scalar valuation are different objects. C1 does not select a unique richness metric or valence scale. Mathematical experience representation has an existing literature [10]; notation does not eliminate interpretive commitments.

### 2.4 Intelligence, behavior and report

Fix tasks, environments, resources, scoring, adaptation permissions and comparison boundaries in \(\mathcal M\). Following [3], define

\[
J_{\mathcal M}(s)=(J_\mu(s))_{\mu\in\mathcal M},
\]

with components invariant under allowed structural relabeling. Omitted context, laws and history must be fixed or included in the domain. Unequal profiles need not be ordered; improvement requires a stated order or objective. A sampled score is not a distributional capability.

Distinguish installed-mechanism performance, performance obtainable through an allowed external controller, and the capability of a modified or retrained process. They may all be studied, but are different comparison contracts. Section 4 studies a controlled composite; it does not silently credit the original plant with an external controller's intelligence.

Behavioral laws are protocol- and horizon-relative; trajectories are realizations. Reports are designated behavioral outputs with separately justified semantics, accuracy and access. Thus report ordinarily belongs to behavior. Experience, capability and report are not three independent substances or three disjoint physical-event classes.

## 3. What observations identify

**Proposition 1 (target identification; restated from [3]).** Let S be a fixed set of admitted types/models, F:S->O an exact observation map, and Q:S->V a specified target. A target decoder exists on the attainable observations,

\[
g:F(S)\to V,\qquad Q=g\circ F,
\]

if and only if

\[
F(s)=F(t)\ \Longrightarrow\ Q(s)=Q(t),\qquad s,t\in S.
\]

**Proof.** If Q=gF, equal F-values have equal Q-values. Conversely, when Q is constant on each fiber, define g(y) as the common Q-value for all s with F(s)=y. Every y in F(S) has a preimage and the value is unique, so g is well defined and Q=gF. QED.

For Q equal to the complete type itself, this condition is injectivity of F. No claim of continuity, computability, stable estimation or statistical confidence follows. Restricting the domain can change injectivity. A finite number of real-valued observations is not, by itself, proof of noninjectivity.

For the finite full-simplex model p in Delta_n with exact probe expectations F(p)=Ap, include normalization by defining B to have first row all ones and remaining rows A. The payoff c^T p is identified throughout Delta_n iff c lies in row(B); the full p is identified iff rank(B)=n. **Proof:** row membership constructs the payoff from known expectations and normalization. If c is not in the row space, a vector v in ker(B) has c^T v !=0; a sufficiently small signed perturbation of the uniform interior p gives two simplex points with equal observations and unequal payoff. Full-law identification similarly is ker(B)={0}. This is R131's standard linear-algebra certificate, with normalization explicit, not a result for every restricted model family.

**Counterlimit:** distinct complete types can have F(s)=F(t). Then any target that separates them is not determined by F. Which types are physically realized remains a separate question.

## 4. What an interface can execute

Let S,Z,A,O be finite nonempty sets and alpha:S->Z onto. The current z=alpha(s) is actually observed. Concrete s is Markov-sufficient, including any persistent hidden mechanism, memory, resources and clock needed for the kernel. Let A(s) be the legal concrete actions and K(s,a;s',o) the joint successor/output kernel. The abstract model supplies finite nonempty legal requests U(z) and joint rows bar K(z,u;z',o), on the same declared time/output contract, with paired initial state z_0=alpha(s_0).

For every z,u consider a fixed memoryless action distribution w_{z,u} in Delta(A). It must use only z,u, put zero weight on every action illegal at any compatible concrete state, and have that conditional distribution at every invocation. Randomness is fresh conditional on history and independent of controller/plant randomness. Abstract controllers may use projected histories and private randomness, but not hidden s or decoder coins/actions. Their legal policies are defined on all histories.

Define

\[
p_{s,a}(z',o)=\sum_{s':\alpha(s')=z'}K(s,a;s',o).
\]

**Proposition 2 (restricted executable correspondence; [5]).** An exact decoder exists iff, for every z,u, a **single common** simplex vector satisfies

\[
w_a=0\quad(a\notin A(s)),\qquad
\sum_a w_a p_{s,a}(z',o)=\bar K(z,u;z',o)
\]

for all s in alpha^{-1}(z) and all z',o. These are finite linear feasibility constraints.

For a fixed decoder in this class, those conditions are equivalent to legal execution and preservation of every finite-horizon projected state/request/output law for every paired start and every legal abstract feedback controller.

**Proof of feasibility.** An observable decoder uses one w throughout the fiber. Its support must be legal and its joint row is the indicated mixture, so the constraints are necessary. Conversely, sampling a feasible w with the stipulated conditional randomness supplies the decoder. Choices for each z,u are independent within this declared interface class. QED.

**Proof of path-law preservation.** Given any compatible hidden state and the requested u, the next projected joint row is the same bar K. It remains that row after averaging over any conditional distribution of hidden states. Condition on a common controller seed; identical projected histories produce identical requested actions. Induction gives equality of the complete finite-horizon projected history distributions, and the support constraints give legality at each step. For necessity, use a one-step controller requesting any u at any concrete start s; law equality forces its row equation, and legal execution forces support zeros. QED.

Every bounded payoff of that projected history is consequently preserved. Costs, concrete action labels and hidden states not included in the projected target are not thereby preserved. This is one-way abstract-to-concrete controller transport; it is not equality of every concrete capability or complete structural isomorphism. Failure is only failure in this restricted decoder class, not every possible sensor, memory or multi-step implementation.

**Existing separating examples:** R137:OBSERVATION_GAP gives two hidden states requiring opposite successful actions; each has a perfect state-aware action, but one common visible decoder has worst error at least 1/2. R137:SEED_GAP gives equal one-time fair marginals but temporal path-TV 1-2^(1-H) when one coin is reused instead of fresh draws. Thus the common-information and conditional-randomness premises cannot be dropped. These are already recorded model examples, not newly discovered cases.

## 5. What follows for complete experiential type

**Proposition 3 (capability/type implications; restated from [1,3]).** Let S be complete organizational types of justified actual process tokens in a common complete signature. Fix the evaluation environment, tasks, resources, laws and comparison conditions sufficiently for J:S->V to be well defined and isomorphism invariant. Under C1 let E:S->E(S) be the resulting bijection of complete organizational and experiential types.

Then

\[
J(s)\ne J(t)\Rightarrow s\ne t\Rightarrow E(s)\ne E(t).
\]

**Proof.** Equal arguments have equal values under the function J, so different values require different complete types. C1's tokenwise isomorphisms, composed in either direction, identify exactly the same complete-type equivalence classes. Hence E is injective and different s,t have different E-values. QED.

J identifies E throughout S iff J is injective. **Proof.** Apply Proposition 1 with Q=E: injectivity of E turns fiber constancy into singleton fibers of J. Conversely singleton fibers define the recovery map on J(S). QED.

Nothing here supplies a scalar magnitude, valence or richness order. For a separately supplied experiential coordinate Q, recovery from J requires Proposition 1's factorization condition; monotone recovery additionally requires order compatibility. C:P3 already supplies a countermodel to an unconditional capability-to-richness monotonic conclusion. Do not reinterpret the absence of a derived scalar ordering as an absence of any relation between intelligence and experience.

Equal finite-view kernels do not satisfy this theorem's complete-type premise merely because Proposition 2 holds. Likewise different noisy estimates need not mean different true J-values. U1 remains universal on admitted actual tokens; none of these theorems introduces an experience-existence gate.

## 6. The integrated comparison procedure

Proposition 1 concerns a target and observation map. Proposition 2 concerns execution of a projected interaction. Proposition 3 concerns actual complete types and C1. They do not form an unconditional chain from a score to experiential identity.

| Stage | Required declaration | Licensed conclusion |
|---|---|---|
| Object | Actual bearer, interval, boundaries, physical support | What process the claim concerns |
| Representation | Signature, view, retained relations, uncertainty/model class | What the representation includes |
| Observation | Protocol F and target Q | Proposition 1 determines target identification |
| Execution | Observable alpha, legal ports, time, randomness, policy class | Proposition 2 transports the projected interaction |
| Interpretation | Complete actual types and C1; further coordinate bridge where needed | Proposition 3 supplies its scoped type implications |

This is an application procedure, not an additional experience criterion. Absence of a report, self-model, recurrent circuit or executable decoder does not remove an actual token from U1's domain.

Three examples locate distinct failures. A many-to-one observation map fails to determine any target that varies within its fibers. Opposite hidden action encodings block an observable common decoder despite separate statewise solutions. Reusing a random bit preserves fair one-time marginals while changing the temporal joint law. These are model-relative limitations, not a proof that every finite behavioral battery fails on every restricted domain.

In a biological/AI comparison, a common external evidence coordinate is a candidate view correspondence. It does not yet supply a common executable transition/intervention interface, which itself would not establish complete organization. In a continuation-control comparison, avoidance behavior does not identify its bearer-specific causal path or negative valence. That distinction is already developed in [4]. The framework exposes premises rather than ruling out meaningful comparison in principle.

## 7. Related work and priority

Reissig, Weber and Rungger [6, Definition V.2 and Theorems V.4–V.5] connect enabled inputs and successor relations to controller refinement. Haesaert, Soudjani and Abate [7, Definition 6 and Theorem 2] use randomized interfaces and preserve output-event probabilities after refinement. These are direct antecedents.

Majumdar, Ozay and Schmuck [8, Definition 3.3 and Corollary 3.4] address output-feedback refinement through external history. Rubenstein et al. [9, Definition 3] require state/intervention transformations to match intervened distributions. Thus observability and intervention consistency are established concerns. Our current-observation-only finite decoder is a restricted contract; restriction alone does not establish new general mathematics.

Propositions 1 and 3 were already published in [1,3]. Proposition 2 supplies an executable finite construction relative to those publications, but general originality beyond control theory is not claimed. Mathematical representation and quotienting are not new in themselves [10]. Recent neural control-transfer work [11] is also relevant; no algorithmic or empirical superiority comparison is made.

The synthesis connects an explicit finite certificate to the UCT definition and interpretation discipline. Whether that warrants a separate research article, rather than a consolidated technical appendix, depends on a non-redundant contribution beyond the existing sources.

## 8. Limitations and conclusion

The actual-token and completeness premises require physical support in any application. They do not demand a universal exclusive subject selector. Finite-model failure is not a failure of experience existence within UCT.

The executable certificate assumes finite, Markov-sufficient dynamics and a current-observation randomized decoder. Hidden-state access, history-based estimation, additional sensors and multi-step implementations are different classes. Unrepresented costs and implementation details are not automatically preserved. Equal finite laws do not establish complete organization; estimated equality is weaker still.

The experiential interpretation remains conditional on C1. No experiential scalar, familiar feeling label, valence identification or biological/AI closure follows. Proof review was by the same assistant, not independent peer review or a proof assistant. No new empirical study is reported.

Task capability and report are organizationally grounded, selective descriptions. A selected target is recoverable when observations separate its alternatives. A declared interaction requires an information-compatible lawful implementation. Complete experiential-type conclusions require C1's complete-organization premise. Separating these claims and their evidence requirements is the purpose of this synthesis.

## References

1. Liu, H. (2026). *Unified Consciousness Theory I: Structural–Experiential Identity and the Continuity from Physical Process to Conceptual Self*. v1.2. https://doi.org/10.5281/zenodo.23131575.
2. Liu, H. (2026). *Unified Consciousness Theory II: Consciousness Theories as Effective Organization Theories*. v1.1. https://doi.org/10.5281/zenodo.23030320. Historical A-v1.1 labels are interpreted against A-v1.2 without editing the published edition.
3. Liu, H. (2026). *Unified Consciousness Theory III: Organization, Intelligence, and Experience—From Inorganic Processes to Artificial Agents*. v1.0. https://doi.org/10.5281/zenodo.23137088.
4. Liu, H. (2026). *From Shutdown Resistance to Self-Continuation Control: Identifiability, Intervention Stability, and Evidence Standards for Artificial Agents*. v1.0, TA-TR-2026-24. https://doi.org/10.5281/zenodo.23176685.
5. UCT workspace (2026). [R137 feedback proofs](../R137_Executable_Feedback_Interfaces_20261007/R137_Executable_Feedback.md), [R131 probe certificates](../R131_Theorem_Synthesis_and_Archive_20261006/R131_Probe_Completeness_Theorem.md), [R138 selected proofs](../R138_Definitions_and_Theorem_Consolidation_20261007/PROOF_SPINE.md). Research records, not separate peer-reviewed publications.
6. Reissig, G., Weber, A., and Rungger, M. (2017). *Feedback Refinement Relations for the Synthesis of Symbolic Controllers*. IEEE Transactions on Automatic Control 62(4), 1781–1796. https://doi.org/10.1109/TAC.2016.2593947. Preprint: https://arxiv.org/abs/1503.03715.
7. Haesaert, S., Soudjani, S. E. Z., and Abate, A. (2016). *Verification of general Markov decision processes by approximate similarity relations and policy refinement*. arXiv:1605.09557v1. https://arxiv.org/abs/1605.09557. Numbering refers to this 36-page preprint.
8. Majumdar, R., Ozay, N., and Schmuck, A.-K. (2020). *On Abstraction-Based Controller Design With Output Feedback*. arXiv:2002.02687v1. https://arxiv.org/abs/2002.02687.
9. Rubenstein, P. K., Weichwald, S., Bongers, S., Mooij, J. M., Janzing, D., Grosse-Wentrup, M., and Schölkopf, B. (2017). *Causal Consistency of Structural Equation Models*. https://arxiv.org/abs/1707.00819.
10. Kleiner, J. (2020). *Mathematical Models of Consciousness*. Entropy 22(6), 609. https://doi.org/10.3390/e22060609.
11. Nadali, A., Trivedi, A., and Zamani, M. (2025). *Stochastic Neural Simulation Relations for Control Transfer*. PMLR 288, 597–620. https://proceedings.mlr.press/v288/nadali25a.html. Abstract-level comparison only.

## Appendix: formal-map provenance

| Content | Existing anchors |
|---|---|
| C1 and basal existence | A:C1, A:C1_OI, A:U1; A §§2–4 |
| Signature and translation | A §§3.5–3.6; B:BAC, B:TFR; B §2.1 |
| Proposition 1 | C:P2_COORD, C:P2_FULL; R131:TARGET_SPAN, R131:COMPLETE_LAW |
| Proposition 2 | R137:CONTROL_MODEL, R137:LOCAL_LP, R137:EXACT_INTERFACE, R137:CLOSED_LOOP; R132:PARTIAL_CLOSURE |
| Counterexamples | R137:OBSERVATION_GAP, R137:SEED_GAP |
| Proposition 3 | A:C1_OI, C:P1, C:P2_FULL, C:P3 |
| Continuation/valence | D §9/§11; D:D7 |

No new nodes or deductive edges are introduced. Local proposition numbers do not rename the cross-substrate T2 certificate or A:C1.
