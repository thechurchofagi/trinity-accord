# Organization, Capability, and Experience
## A Formal Companion to Four Papers

**Hongju Liu**  
Independent researcher, Shenzhen, China  
**Review version 0.2, 7 October 2026**  
Companion technical note to UCT I/II/III and TA-TR-2026-24. Unpublished; no new report number or DOI assigned.

**AI assistance:** ChatGPT assisted with source retrieval, mathematical review, drafting and editing under the author's direction. These checks are not independent peer review. No final human line-by-line approval is claimed.

## Abstract

What does evidence of intelligence or behavior identify about a system's organization, and what experiential interpretation follows? We give a common vocabulary for actual process tokens, complete organizational types, finite scientific views, task-relative capability and report. We assemble three existing results: target identification by constancy over observational fibers; an exact certificate for a restricted class of observable randomized action interfaces in finite controlled models; and conditional implications from capability differences to complete experiential-type differences under structural-experiential identity. The interface result preserves projected feedback laws without identifying complete underlying organization. Counterexamples separate observational identification, implementability and temporal joint-law preservation. The contribution is a source-traceable technical synthesis and comparison protocol, not a new general theory of control refinement or an independent proof of consciousness. Physical adequacy and selected experiential-coordinate interpretations remain explicit obligations. No universal consciousness score or behavioral threshold for experience is supplied.

## 1. Purpose and contribution

Task performance, internal-event reporting and first-person statements are observations of organized processes, but they answer different questions. A score concerns performance under an evaluation. A report is an output with a proposed interpretation. A mechanistic account concerns the organization generating them. Identifying one does not automatically identify the others.

The four source papers already establish much of this distinction. UCT I [1] distinguishes actual processes, complete organization, views and estimates, and posits structural-experiential identity C1. UCT II [2] requires constrained, non-oracular and source-faithful mechanism translations. UCT III [3] defines capability and proves identification/type implications. The self-continuation paper [4] separates behavior, mechanism, continuation target and valence. These published results are not presented as new discoveries.

Subsequent project records develop finite controlled correspondence, including an observable randomized action decoder [5]. This supplies a concrete connection between identification and execution. This companion consolidates the definitions and uses that certificate as a worked finite application. The detailed control proof is placed in Appendix A. Established control-refinement and causal-abstraction theories are direct antecedents.

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

**Proposition 1 (target identification; restated from [3]).** Let \(S\) be a fixed set of admitted types or models, \(F:S\to\mathcal O\) an exact observation map, and \(Q:S\to V\) a specified target. A decoder

\[
g:F(S)\to V,\qquad Q=g\circ F
\]

exists if and only if

\[
F(s)=F(t)\ \Longrightarrow\ Q(s)=Q(t),\qquad s,t\in S.
\]

**Proof.** Necessity follows by applying \(g\) to equal observations. Conversely, define \(g(y)\) to be the common target value on the nonempty fiber \(F^{-1}(y)\). Fiber constancy makes this definition unambiguous for every \(y\in F(S)\). It then satisfies \(Q=g\circ F\). \(\square\)

For the complete type itself, take \(Q\) to be the identity on \(S\). Identification then requires \(F\) to be injective. The result is set-theoretic: it does not supply continuity, a computable decoder, stable estimation or statistical confidence. Domain restrictions can change injectivity. A finite number of real-valued observations does not alone prove noninjectivity.

The finite linear certificate from R131 is given in Appendix B. In the main argument, the important distinction is between determining a selected target and determining the whole type. A many-to-one observation can determine some coordinates while failing to determine others.

## 4. What an interface can execute

An organizational description may identify a target without providing an executable interface. The finite model from [5] makes the difference precise.

Let \(S,Z,A,O\) be finite nonempty sets and let \(\alpha:S\to Z\) be onto. The current observation \(z=\alpha(s)\) is actually available to the interface. The concrete state is Markov-sufficient, retaining relevant memory, persistent mechanism labels, resources and clock. Let \(A(s)\subseteq A\) be legal actions and \(K(s,a;s',o)\) the joint successor/output kernel for legal actions. An abstract model supplies finite nonempty requests \(U(z)\) and joint rows \(\bar K(z,u;z',o)\). Initial states are paired by \(z_0=\alpha(s_0)\), and time/output meanings are fixed.

The permitted decoder has distribution \(w_{z,u}\in\Delta(A)\), depending only on current \(z,u\). It has that same conditional distribution at every invocation, with fresh randomness independent of the controller and plant. It cannot read hidden \(s\), private mechanism labels or additional history. Abstract controllers may use projected histories and private randomness, but not hidden states, decoder coins or concrete actions. Their policies choose legal requests on every history.

Define the projected joint row

\[
p_{s,a}(z',o)=
\sum_{s':\,\alpha(s')=z'}K(s,a;s',o).
\]

Rows for illegal actions may be assigned arbitrarily because their weights below are zero.

**Proposition 2 (restricted executable correspondence; [5]).** An exact decoder in this class exists precisely when, for every \(z,u\), one common \(w\in\Delta(A)\) satisfies

\[
w_a=0\quad\text{if }a\notin A(s),\qquad
\sum_a w_a p_{s,a}(z',o)=\bar K(z,u;z',o)
\]

for every \(s\in\alpha^{-1}(z)\) and joint outcome \((z',o)\). For a fixed decoder in this class, these conditions are equivalent to legal execution and preservation of every finite-horizon projected state/request/output law, for all paired starts and all legal abstract controllers.

The constraints form a finite linear feasibility problem. Appendix A proves both directions. The result transports the specified projected interaction; it does not identify complete organizational structure. Omitted costs, hidden states and concrete action labels are not automatically preserved. Failure rules out this decoder class only, not every history-dependent or multi-step implementation.

## 5. What follows for complete experiential type

**Proposition 3 (capability/type implications; restated from [1,3]).** Let \(S\) be complete organizational types of justified actual process tokens under a common complete signature. Fix evaluation conditions sufficiently for \(J:S\to V\) to be well defined and isomorphism invariant. Under C1, let \(E:S\to E(S)\) be the induced bijection of complete organizational and experiential types. Then

\[
J(s)\ne J(t)\ \Longrightarrow\ s\ne t
\ \Longrightarrow\ E(s)\ne E(t).
\]

**Proof.** Equal arguments have equal values under \(J\). Thus different capability profiles require different complete types. Composing C1's tokenwise isomorphisms in either direction identifies precisely the same physical and experiential type classes. Hence \(E\) is injective, giving the second implication. \(\square\)

Furthermore, \(J\) identifies \(E\) throughout \(S\) if and only if \(J\) is injective. Apply Proposition 1 with \(Q=E\): since \(E\) is injective, its constancy on a \(J\)-fiber requires that fiber to contain only one type. Conversely singleton fibers define recovery on \(J(S)\).

For a separately supplied experiential coordinate \(Q\), recovery from \(J\) requires the factorization condition of Proposition 1. Monotone recovery additionally requires order compatibility. C:P3 already gives a countermodel to an unconditional capability-to-richness monotonic conclusion. The absence of a scalar ordering does not mean that intelligence and experience are unrelated.

Equal finite-view kernels do not satisfy the complete-type premise merely because Proposition 2 holds. Different noisy estimates likewise need not imply different true \(J\)-values. U1 remains universal on admitted actual tokens; none of these propositions introduces an experience-existence gate.

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

Three examples locate distinct failures. First, Proposition 1 excludes recovering a target that varies inside an observation fiber. Second, in R137's opposite-action example, hidden \(b\in\{0,1\}\) shares one ready observation and action \(a\) succeeds exactly when \(a=b\). Choosing action zero with probability \(w\) gives statewise success \(w\) and \(1-w\); the best common worst-case success is \(1/2\), although a hidden-state oracle succeeds perfectly. Third, a single fair bit reused for \(H\ge1\) steps has the same one-time marginals as fresh fair bits but path-law total variation \(1-2^{1-H}\). It puts mass only on two constant strings, whose overlap with the fresh-bit law is \(2^{1-H}\). Both examples are restated from [5], not new cases. They establish scoped limitations rather than the failure of every finite battery on every restricted domain.

In a biological/AI comparison, a common external evidence coordinate is a candidate view correspondence. It does not yet supply a common executable transition/intervention interface, which itself would not establish complete organization. In a continuation-control comparison, avoidance behavior does not identify its bearer-specific causal path or negative valence. That distinction is already developed in [4]. The framework exposes premises rather than ruling out meaningful comparison in principle.

## 7. Related work and priority

Reissig, Weber and Rungger [6, Definition V.2 and Theorems V.4-V.5] connect enabled inputs and successor relations to controller refinement. Haesaert, Soudjani and Abate [7, Definition 6 and Theorem 2] use randomized interfaces and preserve output-event probabilities after refinement. These are direct antecedents.

Majumdar, Ozay and Schmuck [8, Definition 3.3 and Corollary 3.4] address output-feedback refinement through external history. Rubenstein et al. [9, Definition 3] require state/intervention transformations to match intervened distributions. Thus observability and intervention consistency are established concerns. Our current-observation-only finite decoder is a restricted contract; restriction alone does not establish new general mathematics.

Propositions 1 and 3 were already published in [1,3]. Proposition 2 supplies an executable finite construction relative to those publications, but general originality beyond control theory is not claimed. Mathematical representation and quotienting are not new in themselves [10]. Recent neural control-transfer work [11] is also relevant; no algorithmic or empirical superiority comparison is made.

Accordingly, this document is positioned as a formal companion to the four papers. Its value is a common reference for definitions, proof obligations and a finite application. It is not presented as a fifth paper announcing a new general consciousness theorem.

## 8. Limitations and conclusion

The actual-token and completeness premises require physical support in any application. They do not demand a universal exclusive subject selector. Finite-model failure is not a failure of experience existence within UCT.

The executable certificate assumes finite, Markov-sufficient dynamics and a current-observation randomized decoder. Hidden-state access, history-based estimation, additional sensors and multi-step implementations are different classes. Unrepresented costs and implementation details are not automatically preserved. Equal finite laws do not establish complete organization; estimated equality is weaker still.

The experiential interpretation remains conditional on C1. No experiential scalar, familiar feeling label, valence identification or biological/AI closure follows. Proof review was by the same assistant, not independent peer review or a proof assistant. No new empirical study is reported.

Task capability and report are organizationally grounded, selective descriptions. A selected target is recoverable when observations separate its alternatives. A declared interaction requires an information-compatible lawful implementation. Complete experiential-type conclusions require C1's complete-organization premise. Separating these claims and their evidence requirements is the purpose of this synthesis.


## Appendix A. Proof of executable correspondence

This proof restates R137:LOCAL_LP and R137:CLOSED_LOOP under the complete contract in Section 4.

**Feasibility.** A decoder using only \(z,u\) must use a single distribution \(w\) throughout the fiber \(\alpha^{-1}(z)\). Legal execution requires zero mass on actions illegal at each compatible state. Its induced projected row is exactly the mixture in Proposition 2, so row matching is necessary. Conversely a common feasible \(w\), sampled with the declared conditional-randomness contract, implements those legal rows. The choices for the finite set of \(z,u\) pairs do not interact within this decoder class.

**Sufficiency for feedback laws.** Conditional on the concrete history and requested \(u\), every compatible hidden state gives the same projected successor/output row \(\bar K\). Averaging over a conditional distribution of hidden states therefore leaves that row unchanged. Couple the controllers' private seeds. Equal projected histories give equal request choices, and induction yields equal finite-horizon joint projected laws. The support constraints guarantee legal concrete actions at each step.

**Necessity.** Use a one-step controller at any concrete start \(s\), requesting an arbitrary \(u\in U(\alpha(s))\). Equality of its next projected joint law forces the corresponding row equation. Legal execution forces the zero constraints. Varying \(s,u\) recovers all constraints. This uses preservation from every represented start, not merely a fixed empirical initial distribution. \(\square\)

Every bounded payoff of the projected record is preserved by equality of its law. This remains one-way transport from the abstract controller to the concrete system. It does not assert equality of all concrete capabilities or a bijective complete physical correspondence.

## Appendix B. Finite target-identification certificate

This is the standard linear-algebra certificate recorded in R131 [5]. Let \(n\ge1\), let \(p\in\Delta_n\) range over the full probability simplex, and observe exact probe expectations \(Ap\), with \(A\in\mathbb R^{m\times n}\). Include normalization through

\[
B=\begin{bmatrix}\mathbf 1^\top\\ A\end{bmatrix}.
\]

A target payoff \(c^\top p\) is identified throughout the simplex if and only if \(c\in\operatorname{row}(B)\). The full probability law is identified if and only if \(\operatorname{rank}(B)=n\).

**Proof.** Row membership expresses the target as a linear combination of normalization and known expectations. If \(c\notin\operatorname{row}(B)\), there is \(v\in\ker(B)\) with \(c^\top v\ne0\). Start from the uniform interior point \(p_0\). For sufficiently small \(\epsilon>0\), both \(p_0+\epsilon v\) and \(p_0-\epsilon v\) lie in the simplex, since \(\mathbf 1^\top v=0\). They share the observations and have distinct target payoffs. Full-law identification equivalently requires a trivial nullspace, giving the rank criterion. \(\square\)

The domain is the full simplex with exact common probes. The condition need not remain necessary on a restricted model class and is not a statistical confidence bound.

## References

1. Liu, H. (2026). *Unified Consciousness Theory I: Structural-Experiential Identity and the Continuity from Physical Process to Conceptual Self*. v1.2. https://doi.org/10.5281/zenodo.23131575.
2. Liu, H. (2026). *Unified Consciousness Theory II: Consciousness Theories as Effective Organization Theories*. v1.1. https://doi.org/10.5281/zenodo.23030320. Historical A-v1.1 labels are interpreted against A-v1.2 without editing the published edition.
3. Liu, H. (2026). *Unified Consciousness Theory III: Organization, Intelligence, and Experience - From Inorganic Processes to Artificial Agents*. v1.0. https://doi.org/10.5281/zenodo.23137088.
4. Liu, H. (2026). *From Shutdown Resistance to Self-Continuation Control: Identifiability, Intervention Stability, and Evidence Standards for Artificial Agents*. v1.0, TA-TR-2026-24. https://doi.org/10.5281/zenodo.23176685.
5. UCT workspace (2026). [R137 feedback proofs](../R137_Executable_Feedback_Interfaces_20261007/R137_Executable_Feedback.md), [R131 probe certificates](../R131_Theorem_Synthesis_and_Archive_20261006/R131_Probe_Completeness_Theorem.md), [R138 selected proofs](../R138_Definitions_and_Theorem_Consolidation_20261007/PROOF_SPINE.md). Research records, not separate peer-reviewed publications.
6. Reissig, G., Weber, A., and Rungger, M. (2017). *Feedback Refinement Relations for the Synthesis of Symbolic Controllers*. IEEE Transactions on Automatic Control 62(4), 1781-1796. https://doi.org/10.1109/TAC.2016.2593947. Preprint: https://arxiv.org/abs/1503.03715.
7. Haesaert, S., Soudjani, S. E. Z., and Abate, A. (2016). *Verification of general Markov decision processes by approximate similarity relations and policy refinement*. arXiv:1605.09557v1. https://arxiv.org/abs/1605.09557. Numbering refers to this 36-page preprint.
8. Majumdar, R., Ozay, N., and Schmuck, A.-K. (2020). *On Abstraction-Based Controller Design With Output Feedback*. arXiv:2002.02687v1. https://arxiv.org/abs/2002.02687.
9. Rubenstein, P. K., Weichwald, S., Bongers, S., Mooij, J. M., Janzing, D., Grosse-Wentrup, M., and Schölkopf, B. (2017). *Causal Consistency of Structural Equation Models*. https://arxiv.org/abs/1707.00819.
10. Kleiner, J. (2020). *Mathematical Models of Consciousness*. Entropy 22(6), 609. https://doi.org/10.3390/e22060609.
11. Nadali, A., Trivedi, A., and Zamani, M. (2025). *Stochastic Neural Simulation Relations for Control Transfer*. PMLR 288, 597-620. https://proceedings.mlr.press/v288/nadali25a.html. Abstract-level comparison only.

## Appendix C. Formal-map provenance

| Content | Existing anchors |
|---|---|
| C1 and basal existence | A:C1, A:C1_OI, A:U1; A §§2-4 |
| Signature and translation | A §§3.5-3.6; B:BAC, B:TFR; B §2.1 |
| Proposition 1 | C:P2_COORD, C:P2_FULL; R131:TARGET_SPAN, R131:COMPLETE_LAW |
| Proposition 2 | R137:CONTROL_MODEL, R137:LOCAL_LP, R137:EXACT_INTERFACE, R137:CLOSED_LOOP; R132:PARTIAL_CLOSURE |
| Counterexamples | R137:OBSERVATION_GAP, R137:SEED_GAP |
| Proposition 3 | A:C1_OI, C:P1, C:P2_FULL, C:P3 |
| Continuation/valence | D §9/§11; D:D7 |

No new nodes or deductive edges are introduced. Local proposition numbers do not rename the cross-substrate T2 certificate or A:C1.
