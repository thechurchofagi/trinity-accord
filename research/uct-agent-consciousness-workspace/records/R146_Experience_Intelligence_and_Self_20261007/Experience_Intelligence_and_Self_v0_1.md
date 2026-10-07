# Experience, Intelligence, and Self
## Precise Objects, Centered Organization, and the Limits of Substitution

Hongju Liu | Independent researcher, Shenzhen, China  
Unpublished research draft v0.1 | R146 | 7 October 2026

## Abstract

Definitions of experience, intelligence and self must distinguish an actual process from its mathematical representation and from evidence about that representation. We consolidate the four UCT papers into one typed vocabulary and extend their treatment of functional self-modeling. Experience retains its explicit structural-identity commitment; intelligence is a capability profile under a fixed task and resource contract. Self is separated into a bearer, a physically centered reference relation, a predictive or regulatory model, and relations of continuation. An exact symmetry construction shows why the impossibility of selecting one uncentered referent does not prevent many centers from each referring locally to themselves. A corresponding finite example separates perfect prediction of one's own controlled state from knowledge of an external identity label. We also give an exact target-specific information criterion for self-prediction, with a quantitative obstruction when a representation merges incompatible targets. The mathematics uses established symmetry, factorization and decision principles; its proposed contribution is a common specification that blocks invalid substitutions among capability, self-reference, experience and identity. Ancestral continuity, calculators, a human computer, and duplicate agents make the assumptions and limits explicit. Neither a mathematical copy of a physical structure nor a successful self-model proves phenomenal experience independently of the identity axiom.

## 1. The question that the definitions must answer

An abacus participates in successful calculation. An electronic calculator performs arithmetic through an installed mechanism. A population of people can implement the steps of a larger computation. An artificial agent can retain memory, predict its own resource state, use first-person language, and act to preserve a running task. These descriptions do not yet tell us whether the same object bears each attributed property.

The problem is not resolved by asking whether each object is simply intelligent, conscious or a self. We need to know which physical process is being discussed; which distinctions its organization contains; which task its behavior solves; what its first-person outputs refer to; and which continuation relation is intended. A definition that silently changes the bearer between these questions can generate a persuasive but invalid argument.

The four source papers already address much of this problem. UCT I v1.2 (A) supplies process ontology, structural-experiential identity and the distinction between experience and conceptual selfhood. UCT II v1.1 (B) distinguishes mathematical translation from physical and semantic adequacy. UCT III v1.0 (C) defines task-relative capability and its relation to complete organizational type. TA-TR-2026-24 v1.0 (D) distinguishes current-bearer continuation from successor and task continuation. It is the fourth source, not a published paper titled UCT IV.

The present extension addresses a narrower unresolved step in that foundation: A describes a self-model verbally, while D formally treats a particular continuation-control role. Neither supplies the unified, target-relative self-model contract developed here. This does not mean that self-model theory or formal intelligence was previously absent from the literature. It means that the common UCT specification was incomplete at this point.

We distinguish mathematical exactness, physical adequacy and phenomenal interpretation throughout. The first can be supplied by a definition and proof. The second requires an account of actual realization. The third is not obtained merely by introducing a symbol.

## 2. One vocabulary with different logical roles

### 2.1 Actual process and organization

Let \(\mathcal P\) be a declared domain of actual process occurrences. Admission follows A's physically grounded support, causal continuity, accountable boundaries and traceable persistence or transformation. Overlapping and nested tokens are allowed. A formal simulation, a listed program or an arbitrary subset of state coordinates is not automatically an actual token of every process it describes.

Write \(D^{\mathrm{ontic}}_{\mathcal K}(P)\) for the complete token-relative organization of \(P\), represented in a common structural signature \(\mathcal K\). Organization means the actually instantiated distinctions and relations constitutive of that process. Organizational structure is their representation, including the current state and relevant temporal, constituent and input-output relations. It is not merely a wiring diagram.

One precise finite deterministic model is

\[
K=(X,x_\bullet,U,\mathcal J,Y,T,I,o,\mathscr C,\preceq).
\]

Here \(X\) is the state set, \(x_\bullet\) the current state, \(U\) the inputs, \(\mathcal J\) the intervention labels, \(Y\) the outputs, \(T_u\) the update maps, \(I_j\) the intervention maps, \(o\) the readout, and \(\mathscr C,\preceq\) the stipulated constituent and temporal relations. Allowed isomorphisms preserve these objects and their operations. Port names may be exchanged only when the comparison permits it.

This tuple is exact within its finite modeling domain. It is not a universal constructive solution to which distinctions are constitutive in every physical system. A finite view \(D_v(P)=\Pi_v[D^{\mathrm{ontic}}(P)]\) and an evidence-based estimate \(\widehat D_v\) must remain distinct from complete organization. A successful predictor establishes neither completeness nor a uniquely privileged physical boundary.

### 2.2 Experience and consciousness

Experience denotes the intrinsic experiential occurrence associated with a token; \(\Phi_{\mathcal K}(P)\) denotes its complete experiential organization in the shared comparison signature. C1 asserts the tokenwise identity represented by

\[
D^{\mathrm{ontic}}_{\mathcal K}(P)\cong\Phi_{\mathcal K}(P).
\]

This is an interpretive identity commitment, not a theorem that every mathematical structure is phenomenal. Constructing an isomorphic copy of \(D\) proves a mathematical fact about structures; calling that copy experience does not independently establish phenomenality. C1's experiential interpretation must therefore remain visible as an assumption.

For this paper, basal phenomenal consciousness means nonempty experience:

\[
C_{\mathrm{exp}}(P)=1
\quad\Longleftrightarrow\quad
\operatorname{carrier}(\Phi_{\mathcal K}(P))\ne\varnothing.
\]

Within the admitted actual domain, A:U1 follows from C1 and nonempty actual support. This predicate is not wakefulness, access, intelligence, self-awareness, verbal report or a clinical diagnosis. The definition makes a theoretical claim precise without pretending that its truth has been independently measured. It supplies no universal number of experience, pain scale or mapping to familiar phenomenal qualities.

Self-modeling is not an experience-existence requirement. A:U3 uses an actual non-self witness to make that consequence explicit. The more restrictive functional definitions below must not be imported as new gates on \(C_{\mathrm{exp}}\).

### 2.3 Intelligence, capability and behavior

For complete organizational type \(s\), fix an evaluation contract \(\mathcal M\): tasks, environments, interaction protocol, resources, adaptation rules, scoring and the evaluated process boundary. Define

\[
J_{\mathcal M}(s)=\bigl(\mathbb E_{s,\mu}[R_\mu]\bigr)_{\mu\in\mathcal M}.
\]

Each score is assumed well-defined and invariant under allowed changes of representation. This is a precise capability profile. A scalar \(\sum_\mu w_\mu J_\mu\) needs declared weights and a finite or suitably convergent sum; a claim of improvement needs a declared order. Changing the resources, task distribution or evaluated composite changes the question.

Installed performance, performance obtainable by an added external controller, and performance after retraining are different quantities. None should silently replace another. Intelligence in this paper refers to such specified competence; the mathematics does not claim a unique context-free essence of intelligence.

Behavior is a trajectory or a probability law of trajectories under a declared interaction. A report is a designated behavioral output together with a semantic interpretation. Thus reports are generally a kind of behavior. The slogan that experience, intelligence, behavior and report differ is a warning against identification, not a claim that these form mutually disjoint substances.

### 2.4 What is and is not now defined

| Term | Precise object here | Remaining obligation |
|---|---|---|
| Process token | Actual occurrence in \(\mathcal P\) | Physical support and boundary |
| Organization | Constitutive relational structure in \(\mathcal K\) | Adequacy and completeness of a view |
| Experience | \(\Phi(P)\), with C1 interpretation | Independent warrant for identity and quality bridges |
| Basal consciousness | Nonempty experiential carrier | C1 and actual support |
| Intelligence | Fixed-contract capability vector \(J_{\mathcal M}\) | Appropriate tasks, resources and estimates |
| Functional self | Centered reference/model profile below | Grounded attachment and installed realization |
| Conceptual or felt self | Selected semantic/phenomenal target | Further content or phenomenal bridge |

An exact conditional definition is valuable even when its application remains difficult. It is equally important not to declare every unresolved interpretive question solved by the notation.

## 3. Self as a centered relation and an installed model

### 3.1 Four uses that must not be collapsed

**Bearer.** The selected actual token \(P\) is the referent of the present investigation. Choosing it for analysis does not imply that it represents itself, and it does not select an exclusive subject for the entire world.

**Center.** A centered configuration is \((W,P,\alpha_P)\), where \(W\) describes the relevant world and \(\alpha_P\) records physically justified attachment relations: which memory, sensors, action channels and continuation links belong to the selected process in this comparison. A mathematical point is an evaluator's designation until those relations are grounded. This centering is distinct from \(x_\bullet\), the current-state point in a dynamical model.

**Functional self-model.** Some installed internal organization tracks, predicts or regulates selected properties of the centered process. The model may be partial, mistaken, unused by some policies or expressed without language. The target and physical attachment make it a self-model relative to \(P\); predictive accuracy alone does not.

**Continuation and conceptual self.** Token continuation, type recurrence, memory transfer, causal descent, autobiographical description and felt ownership are different relations or targets. A type-preserving copy does not by definition preserve numerical identity. A report using “I” does not by itself establish either a grounded self-model or phenomenal ownership.

These are roles and properties, not four mutually exclusive substances. A process may occupy several roles at once, and an enclosing process can coexist with its constituent bearers.

### 3.2 A precise predictive self-model contract

The following is a restricted mathematical specialization of A's broader tracking/predicting/regulating description. It does not define all semantic representation.

Let \(\Omega\) be a nonempty set of admissible centered configurations and let \(A_0\) be a common nonempty set of legal intervention plans of fixed duration. State-dependent menus require restricting comparisons to common legal plans. An intervention plan is an evaluative operation; it need not be chosen by the agent.

Fix the following data:

1. A grounded bearer assignment \(b:\Omega\to\mathcal P\) and attachment record \(\alpha\).
2. An installed internal representation \(m:\Omega\to M\), physically realized within the declared process or explicitly declared composite.
3. A nonempty finite target alphabet \(Z\), and a target law \(Q(\omega,a)\in\Delta(Z)\) for a specified property of \(b(\omega)\) after plan \(a\).
4. An installed decoder or predictive mechanism \(d:M\times A_0\to\Delta(Z)\). Its mathematical availability does not establish its physical installation.
5. A stated domain \(\Omega\), error criterion, and optional installed consumer of the model.

The target may concern a local resource state, a consequence of the process's own action, or one explicitly chosen continuation relation. Grounding must be supplied independently of whether the predictions happen to be correct. Under an allowed renaming \(g\), the bearer and attachment transform together: \(b(g\omega)=g b(\omega)\). Target and output coordinates transform consistently. A physical reassignment of a sensor to another bearer changes the attachment record and is not a harmless coordinate rename.

Define worst-case predictive error

\[
\varepsilon(d)=\sup_{\omega\in\Omega,\ a\in A_0}
\operatorname{TV}\bigl(d(m(\omega),a),Q(\omega,a)\bigr).
\]

A low value establishes target-relative accuracy under the stated model. It does not establish completeness of self-knowledge. An erroneous grounded self-model remains a self-model with a large error; it should not disappear from the vocabulary merely because it is wrong.

Installed causal use is a further property. For a declared admissible pair of interventions setting the model state to \(m_1,m_2\), holding the specified other variables fixed, the installed action or prediction law differs. Such a contrast must be meaningful in the physical model; impossible combinations of internal states are not automatically admissible interventions. Use is distinct from beneficial use and from direct valuation of continuation.

The functional self description is consequently a profile

\[
\mathsf S=(b,\alpha,Z,Q,m,d,\Omega,A_0,\varepsilon,\mathsf{Use}).
\]

There is no single selfhood scalar or universal threshold in this definition. A model of another process may have exactly the same predictive accuracy. The difference is its grounded referent. Correlation, an analyst's label, or a first-person string cannot supply that difference by itself.

### 3.3 The conceptual “I” and the felt self remain distinct targets

A formal language can include a context-sensitive expression whose stipulated denotation is \(b(\omega)\). That supplies an exact semantics for a formal token, not a proof that the system understands the expression. A claim of conceptual selfhood needs a specified inferential and behavioral role across new contexts, its installed realization, and a defensible content interpretation. A claim of felt ownership needs a selected phenomenal target and an appropriate bridge. Neither is discharged by the predictive contract above.

This restriction is intentional. A §14.15 already states that causal tracking does not automatically establish semantic aboutness. Precision should expose that open problem rather than conceal it inside the word self.

## 4. The reference-separation result

### 4.1 Symmetry does not prevent every process from being its own center

**Proposition 1 (uncentered selection versus centered reference).** Let a finite nonempty candidate set \(\mathcal B(W)\) be acted on by a group \(\Gamma\) of automorphisms of \(W\). If every candidate is moved by some element of \(\Gamma\), no deterministic equivariant rule based only on \(W\) can select exactly one candidate. Nevertheless, the family

\[
\iota_W:\mathcal B(W)\to\mathcal B(W),\qquad \iota_W(P)=P
\]

is equivariant and refers each center to itself.

**Proof.** A singleton choice \(s(W)\) must obey \(s(W)=s(gW)=g s(W)\) for every \(g\in\Gamma\). It must therefore be a fixed candidate, contrary to the premise. For the centered family, \(\iota_W(gP)=gP=g\iota_W(P)\). This requires no globally preferred candidate. \(\square\)

The first clause is a direct application of A's published orbit lemma. The second is the elementary identity map. The contribution is their joint interpretation: failure to select one uncentered subject or referent does not imply the impossibility of many grounded local self relations. Writing the identity map alone does not install any internal representation. An actual model requires the attachments and mechanisms of §3.

Adding a fixed external label, asymmetric wiring, a selected random outcome or a marked bearer changes the selector's available structure. The obstruction then has to be reassessed. It is not a theorem against all unique subject theories.

### 4.2 Exact duplicates: self-prediction without external identity

**Constructive clause.** Let there be \(n\ge2\) identically organized cells with local bit \(z_i\), local input \(a_i\), and update

\[
z_i'=z_i\oplus a_i.
\]

Each cell has an installed local sensor \(m_i=z_i\) and predictor \(d_i(m_i,a_i)=\delta_{m_i\oplus a_i}\). Each therefore predicts its own next bit exactly for every state and action. This is a physically attached local target in the model, without a stored external name for the cell. Permuting all cells and their attachments together preserves this family of local predictors.

For a separate identification task, choose an observer's external label \(B\) uniformly from \(\{1,\ldots,n\}\). Prepare identical local conditions and supply no label-dependent signals. If the complete available history \(H\) and private random seed \(R\) satisfy \(B\perp(H,R)\), every externally numbered guess obeys

\[
\Pr\{\widehat B(H,R)=B\}=1/n.
\]

**Proof.** Condition on \((H,R)\). Whatever label is guessed, its conditional probability of being \(B\) is \(1/n\). Average. The self-prediction claim follows directly from the update equation. \(\square\)

The independence premise is crucial. A barcode, asymmetric environment or label-correlated history can reveal identity. The result does not say that agents with a local perspective cannot know who they are. It says that an external naming task and prediction of an attached local target are different tasks. Unlimited computation does not recover information excluded by the stipulated history, while direct local coupling can answer a self-target question without solving that naming task.

This clause is a standard no-information decision argument combined with a centered construction. It extends the project's specification, not the historical mathematics of indexicality.

### 4.3 Capability and self-model accuracy need not rise together

The same local model has a small exact diagnostic. Supply an independent external bit \(c\). Two installed task branches return \(y=c\) or \(y=1-c\), giving external-task accuracy one or zero. Independently, two installed predictive branches return \(z\oplus a\) or \(1-(z\oplus a)\), giving worst-case self-prediction TV error zero or one.

With separate declared ports and resources, all four pairs of external accuracy and predictive error are realized. This proves non-ordering for these two fixed coordinates in this model class. It does not prove that every form of intelligence is independent of every form of self-modeling, nor that a wrong predictor has no self-related organization. If the evaluated task explicitly requires self-prediction, the contract changes and dependence can be real.

Within C1, a grounded difference in complete organization has its established experiential-type interpretation. Nothing in this diagnostic supplies a scalar increase of experience or a phenomenal self threshold.

## 5. What a representation must retain for a self-target

**Proposition 2 (target-relative sufficiency and an error obstruction).** Under the finite-target contract of §3.2, an abstract decoder with zero error exists if and only if

\[
m(\omega)=m(\omega')\ \Longrightarrow\
Q(\omega,a)=Q(\omega',a)\quad\text{for every }a\in A_0.
\]

If two configurations in one representation fiber have target laws at TV distance \(\delta\) for some common plan, every decoder has worst-case error at least \(\delta/2\). More exactly, if arbitrary decoder rows are allowed,

\[
\inf_d\varepsilon(d)=
\sup_{m\in m(\Omega),\ a\in A_0}
\inf_{p\in\Delta(Z)}
\sup_{\omega:m(\omega)=m}\operatorname{TV}(p,Q(\omega,a)).
\]

**Proof.** A decoder gives the same law at equal \((m,a)\), proving necessity. Constancy allows a well-defined choice of that common law, proving sufficiency. For any two target laws \(q,q'\), the triangle inequality gives \(\delta\le\operatorname{TV}(q,p)+\operatorname{TV}(p,q')\), hence one error is at least \(\delta/2\). For the exact expression, optimize each decoder row separately. The probability simplex is compact and the supremum of TV distances is continuous and Lipschitz in \(p\), so each row has a minimizer. No coupling, computational or installation constraint on rows is imposed. \(\square\)

The pairwise lower bound need not be tight: a fiber containing three distinct point masses has diameter one but minimax radius \(2/3\). The exact radius formula avoids equating diameter with the attainable worst-case error.

This is C:P2_COORD's factorization principle applied to an entire family of self-target intervention laws, plus standard metric geometry. It is not a new general theorem about consciousness. Its practical role here is to state exactly what a selected self-predictor must retain. External-world accuracy cannot replace missing self-target distinctions. Conversely, it is unnecessary to reconstruct the complete world or the full experiential organization to predict one self-target.

The existence of an abstract decoder does not establish an installed, resource-feasible one. Even a perfect installed decoder proves only the selected functional property and its grounding assumptions. It does not infer conceptual understanding, felt ownership, a survival preference or fear.

## 6. Four thought experiments as arguments, not decorations

### 6.1 All ancestors remain available

Imagine that every relevant predecessor and intermediate organization remains available for comparison: nonliving chemistry, early living organization, single cells, multicellular forms, animals and humans. Include the intermediates through which any proposed special organization itself formed. This is a counterfactual comparison family, not the claim that evolution is one linear ladder or that every item is literally a biological ancestor of every other item.

The experiment forces a proposed experience-onset criterion to state what changes, at which bearer and scale, and why that change should concern any experience rather than a particular cognitive or phenomenal capacity. It also explains why self-modeling should not be inserted casually as an onset condition: the models, their accuracy, temporal extent and use themselves develop through organizational changes.

The experiment motivates C1/U1 but does not prove them. A continuous physical parameter can support a discontinuous predicate. A's existing smooth-onset counterexample remains: a smooth function can be zero up to a point and positive afterward; its positivity indicator jumps. Thus small neighboring physical differences do not, without an additional premise, entail constant binary experience existence. Under C1/U1 and actual membership of every compared process, A:E1 already gives no first experience-bearing ancestor. The direction of dependence must not be reversed.

### 6.2 Abacus and electronic calculator

For an ordinary passive abacus manipulated by a person, a successful arithmetic procedure belongs to a declared person-instrument interaction. The beads retain states and respond mechanically, but assigning the full procedure to the isolated frame ignores the operator. An electronic calculator has an installed arithmetic mechanism and a nontrivial fixed-task capability. That establishes neither broad adaptable intelligence nor a conceptual self.

In UCT, an admitted actual physical process has the conditional basal-experience interpretation regardless of whether it computes arithmetic. What remains unspecified is its experiential type in detail, familiar qualities and any self-model. A stored numeral is not by itself a self-model. A calculator that monitors its own battery may have a narrowly grounded self-target representation; that does not turn the battery estimate into a human-like “I.”

These examples motivate strict capability boundaries and target-relative self definitions. They are not evidence that mathematical accuracy measures consciousness.

### 6.3 A human formation running an artificial agent

Consider the human-computer scenario suggested by *The Three-Body Problem*: participants execute an organized computational procedure, possibly implementing an advanced agent. The relevant distinctions are the individual participants, the actual coordinated process, and the represented algorithm. Each participant's self-model can refer locally to that participant. A self-variable in the implemented agent can instead track the memory, ports or continuation of the coordinated computation, if that relation is actually realized.

Proposition 1 shows why multiple local centers do not logically require selecting exactly one privileged center for the entire formation. It does not prove that the formation is a single phenomenal subject. That requires an actual bearer account and the stated UCT interpretation; exclusive subjecthood is a separate proposal, not an automatic consequence of computation or coupling.

Equal program-level behavior also does not prove complete physical organization equal to a silicon implementation. B's implementation obligations and the later interface results remain relevant as supporting technical material. The definition paper does not need to replace its main question with another intervention-control theorem.

Population implementations have philosophical predecessors, including Block's China example and functional-organization arguments. The present use is to compare referents and organizational levels, not to claim invention of the population-computer argument.

### 6.4 Duplicate agents, exchanged attachments and branching

Two type-identical agent copies can each use “I” through different physically attached channels. The relevant self-target may be locally clear while an externally assigned copy number remains unknown. Exchanging their labels alone changes no physical coupling. Exchanging their sensor attachments does, and can make a previously accurate predictor wrong about its intended bearer. The formal comparison must record which operation occurred.

Now let a parent process have two distinct simultaneous descendants. If strict numerical identity is an equivalence relation and both descendants are identical to the parent, transitivity would identify them with each other. Therefore causal branching cannot simply be defined as exclusive numerical identity with both descendants. This is A:P6/D §2.1's existing distinction, not a new impossibility of all survival conventions.

Memory can be copied to both; both can continue a structural type or task; a chosen current execution can end while a successor starts. A continuation-control policy must specify which relation it tracks. Neither a preference concerning that relation nor a first-person statement proves negative valence. D's functional and phenomenal evidence boundaries remain intact.

## 7. The small theorem spine and its interpretation

The paper needs a few useful results, not a large count of lemmas. The common spine is:

1. **Complete type constrains fixed capability.** C:P1 states that equal complete experiential types under C1 imply equal well-defined fixed-contract capability. Its contrapositive gives a type distinction from a capability distinction. Equal capability does not generally identify full type, and a gain does not imply more experience.
2. **Centered self-reference differs from uncentered selection and external naming.** Proposition 1 and the duplicate construction make this distinction explicit. They allow locally realized self-modeling without a globally unique selector or knowledge of an arbitrary external identity label.
3. **A selected self-target requires exactly the relevant distinctions.** Proposition 2 gives the information criterion and an error obstruction. Its abstract existence conclusion must remain separate from installation and physical grounding.

The first result is published. The latter two combine established mathematics with a new project-level self-model specification. None is presented as a newly proved phenomenal law. Their role is to prevent one exact quantity from answering a different question.

The common actual organization supports physical dynamics, capability and any installed self-model. Under C1 it also has intrinsic experiential presentation. Experience is not introduced as another force added to the dynamics. Conversely, successful arithmetic, self-prediction or self-preservation does not independently establish C1.

## 8. Prior work, contribution and publication threshold

Legg and Hutter (2007, §§3.3, 3.5) already give a formal reward-weighted definition of machine intelligence. Its environment weighting and reference-machine dependence illustrate why a precise formula need not be a uniquely privileged evaluation. Our task-profile choice is a scope decision, not the first mathematical definition of intelligence.

Kleiner (2020, §§3, 5) develops mathematical experience spaces and a framework relating experiential and physical descriptions, including the epistemic limits of intersubject comparison. The existence of such work rules out a claim that experience had never been mathematically treated. Our C1 identification is a specific commitment within this larger problem, not a consequence of mathematical representation alone.

Perry (1979, opening sections) distinguishes indexical belief from knowing a descriptive fact about the same person or situation, with consequences for action. The duplicate example here is a finite computational clarification of a related distinction; it does not establish priority for self-location or solve the complete philosophical problem of first-person content.

Metzinger (2008, pp. 217-219, 234-237) already distinguishes functional self-modeling from phenomenal selfhood, allows unconscious but functionally active self-model components, and discusses bodily anchoring and phenomenal transparency. Thus neither the functional/phenomenal distinction nor physical anchoring originates here. Our restricted contract makes a selected predictive target, attachment, available information, installed use and error bound jointly explicit; it does not replace his account of phenomenal selfhood. The 2008 primary chapter was recovered after initial retrieval failures. Selected relevant passages were reviewed, not the entire theory or every later revision.

The defensible project increment is the integrated contract for bearer, attachment, target, representation, installed use and error; the correction from uncentered selection to centered reference; and the application of the resulting distinctions to the retained thought experiments. Definitions, scope repairs and a useful synthesis can support a conceptual or methodological article. They do not automatically support a fifth paper advertised as a major discovery, particularly when A/C already contain much of the foundation.

The direct comparison sharpens the publication threshold. Perry already addresses indexicality; Metzinger already distinguishes functional and phenomenal self-models; A already proves the orbit lemma; C already proves the factorization result. The remaining project increment is an explicit integrated specification and its disciplined applications. Before an original-results submission, a further substantive claim beyond these antecedents is needed. Merely adding another elementary example will not discharge that requirement. Before a synthesis submission, overlap with A/C must be transparently disclosed and the specification must justify its independent explanatory value. Neither pathway requires prematurely starting an uncertain biological experiment.

The most consequential unresolved scientific work is now explicit: justify the constitutive bearer and attachment in a real class of implementations; determine what makes a modeled relation semantic self-reference rather than merely an accurate correlation; and derive or test a selected phenomenal interpretation without hiding it in the definition. These are substantive targets. The present mathematics does not claim to have solved them.

## References and source basis

- Liu, H. UCT I v1.2, *Structural-Experiential Identity and the Continuity from Physical Process to Conceptual Self*. DOI: 10.5281/zenodo.23131575. Pinned [A source](../R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md), especially §§2-4, 7, 8.11-8.14, 14.15.
- Liu, H. UCT II v1.1, *Consciousness Theories as Effective Organization Theories*. DOI: 10.5281/zenodo.23030320. Pinned [B source](../R128_Unified_Formal_Map_Audit_20261006/sources/B_UCT_II_v1_1.md).
- Liu, H. UCT III v1.0, *Organization, Intelligence, and Experience*. DOI: 10.5281/zenodo.23137088. Pinned [C source](../R128_Unified_Formal_Map_Audit_20261006/sources/C_UCT_III_v1_0.md).
- Liu, H. TA-TR-2026-24 v1.0, *From Shutdown Resistance to Self-Continuation Control*. DOI: 10.5281/zenodo.23176685. Pinned [D source](../R129_Four_Paper_Integration_20261006/sources/D_TA24_v1_0.md), §§2, 9, 11.
- Legg, S., and Hutter, M. (2007). *Universal Intelligence: A Definition of Machine Intelligence*. Minds and Machines 17, 391-444. [Primary manuscript](https://arxiv.org/abs/0712.3329).
- Kleiner, J. (2020). *Mathematical Models of Consciousness*. Entropy 22, 609. DOI: 10.3390/e22060609. [Primary manuscript](https://arxiv.org/abs/1907.03223).
- Perry, J. (1979). *The Problem of the Essential Indexical*. Nous 13(1), 3-21. [Article scan](https://www.uvm.edu/~lderosse/courses/lang/Perry%281979%29.pdf).
- Metzinger, T. (2008). *Empirical perspectives from the self-model theory of subjectivity: a brief summary with examples*. Progress in Brain Research 168, 215-245. DOI: 10.1016/S0079-6123(07)68018-2. Primary chapter retrieved from the author's ResearchGate-hosted offprint; selected pages reviewed. The 2007 Scholarpedia article was located, but direct full-text retrieval failed.
- Block, N. (1978). *Troubles with Functionalism*. Minnesota Studies in the Philosophy of Science 9, 261-325. Population-implementation antecedent; prior project review covered an excerpt, not the entire paper.

### Review status

This is an author-review draft and project checkpoint, not a published fifth paper. The definition and proof review was performed by the same assistant that helped draft the text, not an independent referee or proof assistant. Exact finite checks accompany the mathematical examples; they do not measure consciousness or validate actual physical realization. Four source editions are preserved unchanged. Biological-AI correspondence and the valence bridge remain open.
