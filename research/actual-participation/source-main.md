# Actual Participation Before Counterfactual Capacity
## A Token-Level Constraint on Conscious Organization

**Author:** Hongju Liu  
**Affiliation:** Independent researcher, Shenzhen, China  
**Version:** Final Preprint Manuscript v1.0  
**Date:** 27 September 2026  
**Status:** Theory preprint; not peer reviewed.

---

## Abstract

Contemporary theories of consciousness increasingly appeal to intrinsic causal organization, counterfactual structure, or relational phenomenal structure. Yet a prior question remains insufficiently separated from these proposals: **which realized physical processes are eligible to contribute to the organization of a present experience at a particular episode?** We introduce a token-level constraint that distinguishes intrinsic or mechanistic membership from episode-specific actual causal participation. A realized physical episode is represented by an **actual-participation hypergraph**, whose hyperedges encode token-level joint contributions among realized physical events or states. Counterfactual response profiles are then admitted only for processes belonging to this realized support. The resulting view, which we call **participation-restricted dispositionality (PRD)**, occupies a position between trajectory-only actualism and unrestricted dispositionalism: present phenomenal content is constrained by actual participation, while the relational role of an actual participant may depend on its locally realized dispositions.

The proposal preserves the possible relevance of silent inhibitory states, subthreshold variables, static enabling conditions, and other non-spiking physical constraints when they participate in the realized episode, while denying that a purely standby capacity must affect present phenomenology merely because it belongs to a larger intrinsic system. We formulate idle-support invariance, show why state-level or trajectory-level equivalence can erase token actual-causal differences, and develop a participation-sensitive requirement for multiscale causal abstraction. We then prove two formal limits: structural invariances do not uniquely determine an absolute psychophysical bridge, and any bridge invariant under a declared class of phenomenal-null transformations must factor through the corresponding physical quotient. Finally, we derive an empirical contrast with dispositional interpretations of silent-neuron manipulations. A secondary section records a symmetry limit on unique subject selection, but subject individuation is not a primary novelty claim of the paper.

The framework does not derive phenomenality from non-phenomenal premises, nor does it claim to solve the hard problem. Its narrower aim is to constrain **which physical facts a lawful theory of present phenomenal organization is allowed to read**.

**Keywords:** consciousness; actual causation; dispositionalism; integrated information theory; intrinsic computational functionalism; causal structure; multiscale causation; silent neurons; counterfactuals

---

# 1. Introduction

A central ambition of consciousness science is to connect the structure of experience with the physical organization of the systems that realize it. Different theories place the relevant explanatory burden on different physical or computational properties: global availability, recurrent processing, higher-order representation, predictive organization, intrinsic causal power, or other forms of functional and dynamical structure. A particularly demanding family of approaches holds that present experience depends not only on what a system is actually doing, but also on what its components **could have done under counterfactual conditions**.

Integrated Information Theory (IIT) is the clearest contemporary example. IIT 4.0 identifies experience with an intrinsic cause–effect structure specified by a physical substrate in its current state; the structure is explicitly interventionist and counterfactual rather than reducible to observed activity alone (Albantakis et al., 2023). Recent work has made a striking implication of this commitment experimentally explicit. Ponce de Leon and Yoshimi (2026) analyze IIT's "silent brain" and "disabled neuron" predictions: on the IIT interpretation they examine, neurons that are currently silent can remain constitutively relevant because they retain the capacity to enter alternative states, and disabling an already silent neuron can in principle alter phenomenal quality even when the neuron was not firing before the manipulation.

That debate exposes a general fault line. A **trajectory actualist** may insist that only the realized sequence of physical states matters. A **dispositionalist** may insist that the unrealized alternatives supported by the system are part of what makes the current state the state it is. Neither extreme is obviously satisfactory. A trajectory alone can omit the mechanism that generated it: the same observed state sequence can be produced by systems with importantly different internal organization. Yet an unrestricted appeal to counterfactual capacity risks allowing physically dormant or merely standby machinery to alter present experience despite making no contribution to the episode that actually occurs.

This is not a new problem. Maudlin's Olympia argument pressed precisely the worry that a system's counterfactual computational structure might be supplied by machinery that remains causally idle along the actual run (Maudlin, 1989). Barnes (1991) responded by emphasizing the causal history of computation. More recently, Ma and Kanai's Intrinsic Computational Functionalism (ICF) and Kanai and Ma's mechanism-enriched Intrinsic Causal-Computational Realization (ICCR) sharpen the anti-interpretivist side of the problem. Their framework requires consciousness-relevant computational organization to be intrinsic to the physical system rather than imposed by an observer, and the ICCR treatment of Olympia explicitly requires preserved counterfactual branches to be carried by components that are **load-bearing in the system's actual dynamics**, not by disconnected or appended idle machinery (Ma & Kanai, 2026; Kanai & Ma, 2026).

This development substantially narrows the space for a new proposal. It is no longer defensible to claim novelty merely for saying that counterfactuals must be physically realized, that observer-imposed computational labels are insufficient, or that a wholly idle Olympia-style appendage should not determine consciousness. Those positions now have clear precedents.

A further question nevertheless remains. **Intrinsic membership and load-bearing mechanistic realization are not yet the same thing as a token-level account of what actually contributes to a particular realized episode.** A physical component may belong to an intrinsic mechanism, participate in the system across time, and support real counterfactual transitions, while its state at a particular episode may or may not be part of the actual causal support of the target process. Conversely, a variable can be silent or unchanging while its realized value is an enabling or constraining condition for what actually happens. Redundancy, overdetermination, preemption, static enabling conditions, and conjunctive determination all make this token-level distinction nontrivial.

The proposal of this paper is therefore deliberately narrow:

> **Present phenomenal organization should depend on the counterfactual dispositions of physical processes only insofar as those processes make token-level actual causal contributions within the realized episode.**

We call this principle **participation-restricted dispositionality (PRD)**. In compact form:

\[
\boxed{
\text{actual participation first; local disposition second.}
}
\]

PRD is not pure actualism. Once a process qualifies as an actual participant, its locally realized counterfactual response profile may help characterize its relational role. Two episodes with the same coarse observed trajectory can therefore differ phenomenally if the actual participants have different local dispositions. But PRD is also not unrestricted dispositionalism. A component's latent capacity does not enter present phenomenal organization merely because the component belongs to the broader system. Eligibility is gated by episode-specific actual participation.

The proposal is motivated by four considerations.

First, **activity is not participation**. A variable need not spike, change value, or produce an obvious output to contribute to an actual transition. Static constraints, inhibitory states, synaptic efficacies, gate values, and subthreshold physical states can be causally relevant. Thus the framework must not equate actual participation with overt activity.

Second, **participation can be conjunctive**. In redundant or overdetermined systems, ordinary single-variable but-for tests can fail. We therefore represent actual participation with a hypergraph capable of encoding joint determinants, rather than presupposing a one-edge/one-cause picture.

Third, **physical scale cannot be fixed by stipulation**. A macrostate can merge microstates that differ in their token actual-causal organization. Any consciousness theory using coarse-grained physical variables therefore requires a participation-sensitive abstraction condition.

Fourth, **structural constraints have limits**. Even a carefully constructed physical support object does not, by itself, uniquely determine an absolute psychophysical bridge. We make this underdetermination explicit rather than hiding it, and show that any invariant bridge must factor through the quotient induced by the transformations the theory declares phenomenally null.

The paper makes four main contributions.

1. **Episode-level distinction.** We separate intrinsic/mechanistic membership from token-level actual causal participation in a present physical episode.
2. **Participation-restricted dispositionality.** We propose that counterfactual structure contributes to present phenomenal organization only through processes that make actual causal contributions in the realized episode.
3. **Multiscale constraint.** We show that ordinary state-level coarse graining can erase token actual-causal differences and formulate a participation-sensitive consistency requirement across physical scales.
4. **Formal limits.** We establish bridge underdetermination and quotient-factorization results. A separate appendix extension records an equivariant obstruction to unjustified unique subject selection without making subject individuation a primary novelty claim.

The paper is intentionally conditional about ontology. It is compatible with a minimal view on which actual physical processes possess an intrinsic phenomenal aspect, but none of the formal results below derives phenomenality from non-phenomenal premises. The target is more modest: the **organization** of a present experience and the physical facts that a lawful bridge is permitted to use.

---

# 2. Actualism, Dispositionalism, and Intrinsic Realization

## 2.1 Actual trajectories are not mechanisms

Suppose two systems pass through the same observed sequence of values. It does not follow that they instantiate the same transition mechanism. A recorded trajectory is a path through a state space, not the state space and transition law themselves. This point is elementary but consequential for consciousness theories. If phenomenology supervenes only on a recorded path, physically different systems that happen to produce the same path must be treated as phenomenally identical. If phenomenology depends on causal organization, the trajectory is in general insufficient.

This motivates the dispositionalist insight: the current role of a state can depend on how the system would respond to physically admissible perturbations. Chalmers's organizational-invariance arguments already make counterfactual functional organization central to the debate over fading and dancing qualia (Chalmers, 1995). IIT gives counterfactual organization a more explicitly constitutive physical role: the current experience is identified with an intrinsic cause–effect structure defined by the system's causal powers in its current state (Albantakis et al., 2023).

Yet the opposite danger is equally real. If every unrealized capacity of every component in a broadly defined system enters the current experience, a dormant backup device can become phenomenally relevant merely because it *would* respond in a different setup. The issue is therefore not whether counterfactuals matter in general, but **which counterfactuals are licensed to characterize the present episode**.

## 2.2 IIT and the silent-neuron challenge

IIT's treatment of inactive units makes the issue especially sharp. In IIT, an element's inactive state is not equivalent to absence. An inactive element can specify causes and effects because the element retains a repertoire of possible states and causal consequences. Bartlett (2022) used this feature to question whether some silent-neuron predictions are empirically testable. Ponce de Leon and Yoshimi (2026) defend their testability and distinguish two explanatory possibilities.

On a **dispositionalist** explanation of the disabled-neuron case, disabling a neuron can alter the relevant cause–effect power even when the neuron's ordinary activity has not changed. On an **actualist** explanation, disabling the silent neuron changes some actual physical condition—such as a subthreshold potential—which then causally cascades to a report. The distinction is difficult to settle experimentally because complete exclusion of all actual consequences is demanding.

PRD is designed precisely for the space between these views. It rejects the simple equation

\[
\text{actual}=\text{spiking}
\]

and therefore allows a silent neuron's realized physical state to matter. But it denies that *pure latent capacity*, considered independently of token-level participation in the realized episode, automatically enters current phenomenal organization.

## 2.3 Maudlin, Olympia, and mechanism-enriched realization

Maudlin's (1989) Olympia argument attacks a computational supervenience claim by considering machinery that supplies counterfactual computation without changing what occurs along the actual run. Barnes (1991) replied that the causal history of computational activity matters. The modern ICF/ICCR framework offers a more systematic anti-interpretivist response.

Ma and Kanai (2026) argue that computational properties relevant to consciousness must be intrinsic to the system, invariant under merely representational relabelings, and grounded in causal-dynamical organization exposed under intervention. Kanai and Ma (2026) enrich this program with internal mechanisms, intervention profiles, joint readouts, and physical implementation. Their ICCR discussion of Olympia is particularly important for the present proposal: a counterfactual branch counts only if it is borne by a component recognized by the intrinsic partition, and an idle component that plays no role in producing the current state fails that requirement.

PRD should therefore be read as a **refinement**, not as a re-discovery of the Olympia response. ICCR addresses whether a mechanism belongs to a physically intrinsic causal-computational realization. PRD adds a second, episode-relative question:

> **Within an already intrinsic realization, which realized token relations constitute the actual causal support of this present episode, and therefore which local dispositions are eligible to enter its phenomenal organization?**

The distinction becomes visible in cases where multiple mechanisms are genuinely internal, physically realized, and non-idle at the level of system architecture, yet token causal contribution to a particular outcome is distributed, redundant, preempted, conjunctive, or state-dependent.

### 2.3.1 Novelty boundary relative to ICCR

This paper therefore does **not** claim priority for the idea that consciousness-relevant counterfactual structure must be physically intrinsic, mechanistically realized, or load-bearing in actual dynamics. ICCR explicitly advances those commitments. The narrower proposal tested here is that present phenomenal organization should be parameterized by an **episode-indexed token-support object** rather than by intrinsic membership or mechanism-level availability alone. The paper should be read as asking whether this additional tokenization is explanatory, formally useful, and empirically consequential. If not, PRD collapses into a restatement of an already adequate load-bearing criterion.

## 2.4 Actual causation as infrastructure, not as the novelty claim

Actual or token causation asks "what caused what?" in a particular realized occurrence, rather than whether one *type* of event generally causes another. Albantakis, Marshall, Hoel, and Tononi (2019) provide a quantitative account for dynamical causal networks and explicitly distinguish actual causation from general causal structure. Halpern-style approaches and related philosophical work offer alternative accounts, especially for preemption and overdetermination.

This paper does not attempt to settle that literature. Instead, it treats token causation as an **input module**. The consciousness proposal will depend only on a small set of requirements that an admissible participation relation must satisfy. The aim is to prevent the consciousness theory from collapsing if one formalism of actual causation is revised.

---

# 3. Formal Framework

## 3.1 Physical model and realized episode

Let a physical model at scale \(\sigma\) be

\[
M^\sigma=(V^\sigma,F^\sigma,\Theta^\sigma),
\]

where:

- \(V^\sigma\) is a set of physical variables or process variables;
- \(F^\sigma\) specifies lawful dynamical dependence;
- \(\Theta^\sigma\) records physically effective implementation/type information not already represented in \(F^\sigma\).

Let

\[
h_{[t-\Delta,t]}
\]

denote the realized physical episode over a finite interval. A **physical token** is a realized variable-value occurrence, event, or physically instantiated constraint in this episode.

The formalism is deliberately agnostic about whether the most useful variables are neurons, synapses, microcircuits, continuous field variables, molecular states, or some multiscale combination. Scale constraints are introduced later.

## 3.2 An admissible participation relation

Let

\[
\mathsf{AP}_M(X\Rightarrow Y\mid h)
\]

denote an admissible **actual-participation relation** for episode \(h\). It may be implemented using an actual-causation theory, an actual-enabling relation, or a hybrid formalism. We require only the following desiderata.

### AP1. Realization

Every member of \(X\) and \(Y\) is physically realized in \(h\). Purely hypothetical variables or absent pieces of machinery are not tokens in the episode merely because they can be described.

### AP2. Jointness

The relation can represent a jointly sufficient or jointly relevant set:

\[
\{X_1,\ldots,X_k\}\Rightarrow Y.
\]

The framework must not hard-code single-variable but-for causation.

### AP3. Preemption sensitivity

A mechanism that would have produced \(Y\) under a different history is not thereby an actual participant in the production of the realized \(Y\).

### AP4. Static-state eligibility

A state need not change value or emit a spike in order to participate. A realized inhibitory state, gate value, fixed synaptic efficacy, or other physical constraint can be included if its realized value is part of the token-level determination of the transition.

These desiderata leave substantial room for formal development. That is intentional. The core thesis of the paper is not that one particular account of causation is uniquely correct. It is that **whichever admissible token-participation relation is used, present phenomenal dispositions should be gated by its realized support**. This shifts one burden rather than eliminating it: a mature PRD theory must show that its predictions are robust across reasonable participation modules or justify why one module is physically privileged.

## 3.3 Definition 1: Actual Participation Hypergraph

For realized episode \(h\), define the **Actual Participation Hypergraph**

\[
\boxed{
\mathcal H^{AP}(h)=
\left(V_h,E_h^{AP}\right),
}
\]

where \(V_h\) is the set of realized physical tokens admitted at the chosen scale and

\[
X\to Y\in E_h^{AP}
\]

iff

\[
\mathsf{AP}_M(X\Rightarrow Y\mid h).
\]

The use of hyperedges is essential. If \(X=\{X_1,X_2\}\) jointly participates in producing \(Y\), forcing the relation into independent arrows \(X_1\to Y\) and \(X_2\to Y\) can destroy the causal structure one is trying to preserve.

## 3.4 Definition 2: Episode support

Let \(R\subseteq V_h\) be a target realized region or target family of events whose present phenomenal organization is under consideration. Define

\[
\boxed{
\operatorname{Supp}_h(R)
}
\]

as the theory-relevant ancestral, enabling, and reciprocal sub-hypergraph of \(\mathcal H^{AP}(h)\) within a specified temporal depth.

"Specified temporal depth" does not mean an arbitrary universal number such as 300 ms. Different physical scales can carry different intrinsic timescales. The multiscale section below treats a family of episode descriptions rather than assuming a single privileged window.

Crucially, episode support is:

- token-level;
- episode-relative;
- not identical to the full transition table of the system;
- not identical to its set of anatomical components;
- not identical to its overtly active units.

## 3.5 Definition 3: Local dispositional profile

For an actual participant

\[
v\in\operatorname{Supp}_h(R),
\]

define its physically admissible local response profile

\[
\boxed{
\rho_h(v)=
\left\{
P\!\left(
Y' \mid
do_{\rm phys}(v\mapsto v'),
h_{\rm context}
\right)
\right\}_{v'\in\mathcal I_v},
}
\]

where \(\mathcal I_v\) contains physically admissible local interventions and \(h_{\rm context}\) fixes the relevant realized context.

The profile is not a catalogue of worlds that are themselves occurring. It is a relational characterization of an **actual participant**.

We then define the **episode causal germ**

\[
\boxed{
\Gamma_h(R)=
\left(
\operatorname{Supp}_h(R),
\{\rho_h(v)\}_{v\in\operatorname{Supp}_h(R)},
\Theta_{\rm eff}
\right),
}
\]

where \(\Theta_{\rm eff}\) retains physically effective implementation information that has not been shown to be eliminable.

---

# 4. Participation-Restricted Dispositionality

## 4.1 Central postulate

Let \(\mathcal E_h(R)\) denote the organized phenomenal structure associated with target episode \(R\). The central postulate is:

### Participation-Restricted Dispositionality (PRD)

\[
\boxed{
\mathcal E_h(R)
=
\Phi\!\left(\Gamma_h(R)\right),
}
\]

with counterfactual response profiles included only for processes in the actual episode support.

Equivalently:

> **Actual participation determines which physical processes are eligible; local dispositions determine how eligible processes are relationally characterized.**

PRD is a constraint on the **domain of a lawful psychophysical bridge**. It does not by itself specify the full function \(\Phi\), and Section 6 shows why the structural constraints developed here cannot uniquely determine such a bridge.

## 4.2 PRD is not trajectory-only actualism

Consider binary variables \(A,B,Y\), with actual state

\[
A=1,\qquad B=1,\qquad Y=1.
\]

Compare two systems:

\[
M_1:\quad Y=A\land B
\]

and

\[
M_2:\quad Y=(A\leftrightarrow B),
\]

where \(\leftrightarrow\) is logical equivalence (XNOR).

At the actual state, both systems realize the same transition outcome. Moreover, single-variable perturbations from \((1,1)\) produce the same immediate effect:

\[
(0,1)\mapsto0,\qquad
(1,0)\mapsto0.
\]

But the joint intervention differs:

\[
M_1(0,0)=0,
\qquad
M_2(0,0)=1.
\]

Thus a coarse trajectory—or even a limited collection of single-variable effects—can be identical while the local joint dispositional profile differs.

PRD permits

\[
\mathcal E_h(M_1)\neq\mathcal E_h(M_2)
\]

if the differing joint response profile is part of the actual participants' phenomenal organization. It therefore rejects the claim that the realized trajectory is always sufficient.

### Proposition 1. Trajectory Insufficiency

There exist systems \(M_1,M_2\) and realized episodes \(h_1,h_2\) such that

\[
H(h_1)=H(h_2)
\]

under a chosen trajectory representation while

\[
\Gamma_{h_1}\not\cong\Gamma_{h_2}.
\]

Therefore PRD does not, in general, factor through trajectory alone.

**Proof.** The \(M_1/M_2\) construction above supplies a witness: the realized state can be held fixed while the joint local response profile differs. \(\square\)

The point is not that every counterfactual difference is phenomenal. The point is only that **actuality is insufficient unless it includes the relational organization of the actual participants**.

## 4.3 PRD is not unrestricted dispositionalism

Now consider a component \(z\) physically present in the broader system but absent from the token support:

\[
z\notin\operatorname{Supp}_h(R).
\]

Suppose systems \(M\) and \(M'\) differ only in the latent response capacity of \(z\), while their episode germs are isomorphic:

\[
\Gamma_h^M(R)\cong
\Gamma_h^{M'}(R).
\]

PRD requires

\[
\boxed{
\mathcal E_h^M(R)\cong
\mathcal E_h^{M'}(R).
}
\]

The latent capacity difference is not admitted merely because \(z\) belongs to the larger system.

This is the central contrast with unrestricted dispositional views.

## 4.4 Four canonical cases

### 4.4.1 Redundancy and overdetermination

Let

\[
Y=A\lor B,
\qquad A=B=1.
\]

A naïve but-for test asks whether setting \(A=0\) changes \(Y\). It does not:

\[
Y(0,1)=1.
\]

The same is true for \(B\). It would be a mistake for a consciousness theory to infer from this alone that neither realized input participated.

Different actual-causation theories handle overdetermination differently. PRD does not legislate a unique answer, but it requires the physical support formalism to be capable of representing **joint or distributed participation** rather than assuming independent one-variable causes. A hyperedge such as

\[
\{A,B\}\to Y
\]

can encode a distributed determination if the adopted token-causation module licenses it.

### 4.4.2 Static enablers

Let

\[
Y=A\land E,
\qquad A=E=1.
\]

The variable \(E\) may remain unchanged throughout the episode. Yet if its realized value is a physical enabling condition for the realized transition, a theory that equates participation with state change will wrongly omit it.

This matters biologically. A membrane state, inhibitory gate, synaptic efficacy, receptor availability, or field configuration can contribute to a transition without being an "active spike." Whether a particular token-causation formalism labels such a factor a "cause," an "enabler," or a constitutive constraint is secondary to PRD; the participation module must be able to preserve such realized dependencies rather than exclude them merely because the variable is static. PRD therefore insists:

\[
\boxed{
\text{no change}
\not\Rightarrow
\text{no participation}.
}
\]

### 4.4.3 Preempted backup

Suppose a primary route produces \(Y\) and a backup route would have produced \(Y\) had the primary route failed. The backup is causally competent at the type level but is not part of the realized route. An admissible token-causation module should therefore be sensitive to preemption.

The lesson is:

\[
\boxed{
\text{available causal capacity}
\not\Rightarrow
\text{actual participation}.
}
\]

### 4.4.4 Intrinsic silent standby

The hardest case is not an external Olympia appendage but a component that is indisputably internal to the system.

Let \(z\):

- belong to the intrinsic physical architecture;
- participate in the system over other episodes;
- retain latent excitability or another counterfactual capacity;
- yet, at the target episode, make no token-level contribution to the target support.

PRD predicts that changing **only** the pure latent capacity of \(z\), while leaving \(\Gamma_h(R)\) unchanged, does not alter the current organized phenomenology.

This is not a claim that silent units are irrelevant. If a silent neuron's subthreshold state, inhibitory action, synaptic state, or other physical property belongs to the actual support, the neuron is an actual participant and its local dispositional structure may matter. The relevant distinction is therefore:

\[
\boxed{
\text{silent}
\neq
\text{idle}.
}
\]

## 4.5 Idle-Support Invariance

### Proposition 2. Idle-Support Invariance

Let \(M\) and \(M'\) be two physical systems whose target episode germs are isomorphic:

\[
\Gamma_h^M(R)\cong\Gamma_h^{M'}(R).
\]

Suppose all differences between \(M\) and \(M'\) lie outside the target episode support. Under PRD,

\[
\boxed{
\mathcal E_h^M(R)\cong
\mathcal E_h^{M'}(R).
}
\]

**Proof.** PRD defines organized phenomenology as a function of \(\Gamma_h(R)\). Isomorphic episode germs therefore have the same phenomenal organization up to the corresponding phenomenal isomorphism. \(\square\)

This proposition is conditional on PRD. It is not presented as an independently proven law of nature. Its value is that it makes the theory's commitment explicit and therefore exposes it to empirical pressure.

---

# 5. Multiscale Actual Participation

## 5.1 Why ordinary state abstraction is not enough

Consciousness theories routinely move between physical descriptions: ion channels, synapses, neurons, populations, cortical areas, whole-brain networks, or computational variables. A theory that depends on actual participation cannot assume that an ordinary causal abstraction automatically preserves it.

Consider again

\[
Y=X_1\lor X_2.
\]

Define a macrovariable

\[
A=X_1\lor X_2
\]

and macro rule

\[
Y=A.
\]

The microstates

\[
(X_1,X_2)=(1,0)
\]

and

\[
(X_1,X_2)=(1,1)
\]

both map to

\[
A=1,\quad Y=1.
\]

But the token-level causal organization can differ. In the first microstate, \(X_1\) can be uniquely necessary relative to the actual context. In the second, the output is redundantly supported. The macrostate \(A=1\) erases this difference.

Thus:

\[
\boxed{
\text{state-level macro equivalence}
\not\Rightarrow
\text{actual-participation equivalence}.
}
\]

This does not mean that every microscopic difference must be retained in phenomenology. It means that a coarse graining that erases a participation difference incurs a burden: the theory must either represent the difference elsewhere or justify why the erased distinction is phenomenal-null.

## 5.2 Causal abstraction as background

Beckers and Halpern (2019) distinguish increasingly strong forms of causal abstraction and transformation, while Beckers, Eberhardt, and Halpern (2019) extend this program to approximate abstraction. Their central lesson is that a high-level model should preserve appropriate relations between low-level interventions and high-level interventions.

PRD adds an episode-sensitive condition. A mapping can be adequate for macro intervention behavior yet still merge low-level episodes with different token participation structures.

## 5.3 Definition 4: Participation-preserving abstraction

Let

\[
\alpha_{\sigma\to\sigma'}:
M^\sigma\to M^{\sigma'}
\]

be a causal abstraction from a finer scale \(\sigma\) to a coarser scale \(\sigma'\).

We call \(\alpha\) **structurally participation-preserving for episode class \(\mathcal K\)** if, for episodes in \(\mathcal K\), token participation relations erased by \(\alpha\) are either:

1. represented by corresponding macro participation relations; or
2. explicitly marked as unresolved rather than silently identified.

A stronger notion, **phenomenally admissible abstraction**, additionally requires that any erased participation distinction has independently been shown to lie in a phenomenal-null direction of the bridge.

The distinction is important because the latter condition depends partly on \(\Phi\). We should not smuggle a phenomenal assumption into a purportedly purely physical abstraction rule.

## 5.4 Cross-scale consistency

Suppose a physical abstraction \(\alpha\) is phenomenally admissible, and let

\[
\pi_\alpha:
\mathcal E^\sigma\to\mathcal E^{\sigma'}
\]

be the corresponding phenomenal coarse graining. Then a consistent bridge should satisfy

\[
\boxed{
\pi_\alpha\circ\Phi_\sigma
=
\Phi_{\sigma'}\circ\alpha.
}
\]

The interpretation is straightforward:

> Bridging at the fine scale and then coarse-graining should agree with coarse-graining the physical description first and then bridging.

This is a consistency requirement, not a claim that category-theoretic or naturality-style reasoning is novel in consciousness science. The substantive issue is the **participation-sensitive admissibility condition** imposed on the physical abstraction.

## 5.5 No single privileged scale is assumed

PRD does not require that neurons, molecules, or cortical areas constitute the unique "true scale" of consciousness. A multiscale family of descriptions can coexist, provided their bridge outputs are mutually compatible under admissible abstraction.

This is preferable to solving the grain problem by stipulation. It also leaves open the possibility that some coarse variables reveal stable causal organization not conveniently visible at a microscopic description, while forbidding a macro description from erasing episode-level distinctions that the bridge later needs.

---

# 6. Limits of Structural Bridging

## 6.1 Bridge underdetermination

One might hope that the invariances introduced above uniquely determine the psychophysical bridge. They do not.

Let \(\mathfrak G\) denote the class of admissible episode germs and \(\mathfrak E\) the class of phenomenal structures. Consider bridge functions

\[
\Phi:\mathfrak G\to\mathfrak E
\]

satisfying physical relabeling invariance, idle-support invariance, and cross-scale consistency.

These requirements do not generally select a unique nontrivial \(\Phi\).

### Proposition 3. Bridge Underdetermination

The stated structural constraints are insufficient, in general, to determine a unique bridge.

**Proof sketch.**

First, a constant map

\[
\Phi_0(\Gamma)=E_0
\quad\forall\Gamma
\]

will satisfy many invariance conditions automatically.

Second, suppose \(g:\mathfrak E\to\mathfrak E\) is a nontrivial automorphism preserving all phenomenal structure referenced by the constraints. If \(\Phi\) is admissible, then

\[
g\circ\Phi
\]

can satisfy the same purely structural conditions. Therefore those conditions cannot, by themselves, select one absolute labeling of phenomenal structure. \(\square\)

The proposition is intentionally modest. It formalizes a familiar structuralist limitation: invariance constraints can sharply reduce the admissible domain without uniquely deriving absolute qualitative identity.

## 6.2 A physical equivalence quotient

Although the bridge cannot be uniquely derived, the physical side can still be normalized.

Define an equivalence relation

\[
\Gamma\sim_0\Gamma'
\]

whenever the difference between \(\Gamma\) and \(\Gamma'\) consists entirely of transformations the theory independently declares phenomenally null, such as:

- pure variable relabeling;
- support-external idle modifications;
- representational redundancy;
- admissibly equivalent multiscale descriptions.

Let

\[
\boxed{
Z=\mathfrak G/\sim_0
}
\]

and let

\[
q:\mathfrak G\to Z
\]

be the quotient map.

## 6.3 Forced bridge factorization

### Proposition 4. Forced Bridge Factorization

If \(\Phi\) is invariant on equivalence classes of \(\sim_0\), then there exists a unique function

\[
\widetilde\Phi:Z\to\mathfrak E
\]

such that

\[
\boxed{
\Phi=
\widetilde\Phi\circ q.
}
\]

**Proof.** Define

\[
\widetilde\Phi([\Gamma])=\Phi(\Gamma).
\]

Invariance under \(\sim_0\) makes this well-defined. The factorization follows immediately, and uniqueness follows from surjectivity of \(q\). \(\square\)

The mathematics is the standard universal property of a quotient. The substantive content lies in the theory's specification of \(\sim_0\). PRD therefore contributes not a new theorem of abstract mathematics, but a proposed **physical equivalence structure through which any compatible phenomenal bridge must pass**.

## 6.4 What the theory does not derive

The factorization result should not be mistaken for a derivation of "why red feels red." At most, the framework constrains which physical differences can matter and which must be ignored under its own commitments.

A complete psychophysical theory would still need one of the following:

1. additional psychophysical laws;
2. empirical calibration linking physical and phenomenal relational structure;
3. an identity thesis according to which the relevant physical structure and phenomenal organization are two aspects of the same underlying structure.

The present paper remains neutral among these possibilities.

---

# 7. Secondary Extension: A Symmetry Limit on Subject Selection

The main argument concerns present phenomenal support, not a full theory of subjects. The following result is included only as a secondary structural extension and should not be read as the paper's main novelty claim: even if an episode supports a rich phenomenal organization, does that organization uniquely determine **one subject**?

Recent work makes this question increasingly explicit. Sawyer (2026) develops an organizational account of subject individuation in terms of origin-tracking asymmetry. Khadangi's Causal Liability Theory (2026) argues that candidate-bearer individuation should be separated from first-person linguistic performance and introduces liability closure as a bearer criterion. IIT addresses a related problem with an exclusion/maximality principle.

The present paper adds only a narrow formal observation.

## 7.1 Candidate structures and equivariance

Let

\[
\mathcal C(M)
\]

be a set of candidate subject structures generated by an independently specified rule. We do not assume that \(\mathcal C(M)\) contains exactly one element.

Let a deterministic selector

\[
S(M)\in\mathcal C(M)
\]

be required to respect structure-preserving relabelings. For an isomorphism \(f\),

\[
S(fM)=fS(M).
\]

In particular, for an automorphism

\[
g\in Aut(M),
\]

we have \(gM=M\).

## 7.2 Theorem: Equivariant Selection Obstruction

If

\[
\operatorname{Fix}_{Aut(M)}
\left(\mathcal C(M)\right)
=
\varnothing,
\]

then no deterministic, relabeling-equivariant selector can choose exactly one candidate from \(\mathcal C(M)\).

**Proof.** Suppose \(S\) exists. For every \(g\in Aut(M)\),

\[
S(M)=S(gM)=gS(M).
\]

Thus \(S(M)\) must be fixed by every automorphism. This contradicts the assumption that the candidate set contains no such fixed element. \(\square\)

The theorem does **not** show that there are no subjects, and it does not show that symmetric candidates are numerically identical. Two physically distinct but structurally exchangeable brains can still be two subject tokens. The theorem establishes only a limitation on **privileged unique selection from structure alone**.

## 7.3 Physical anchoring

Let \(A\) be a set of physically real anchors. Replace \(Aut(M)\) by the stabilizer

\[
G_A=
\operatorname{Stab}_{Aut(M)}(A).
\]

A candidate \(x\) is structurally individuated relative to \(A\) iff

\[
\boxed{
\operatorname{Orb}_{G_A}(x)=\{x\}.
}
\]

The criterion is target-relative: irrelevant symmetries elsewhere in the universe need not be eliminated.

This extension supports a general methodological principle:

> **A theory should not assign unique identity beyond the asymmetry actually contained in its physical description.**

Subject individuation is not developed further here. Its full treatment requires candidate generation, temporal continuity, overlap, and embodiment, and is left for separate work.

---

# 8. Empirical Consequences

## 8.1 The silent-versus-idle contrast

PRD's sharpest empirical contrast concerns a component that is:

- intrinsic to the relevant physical system;
- currently silent in the ordinary electrophysiological sense;
- physically capable of alternative responses;
- but hypothesized to be outside the token actual support of the target episode.

The experiment of interest would compare two conditions \(C_0\) and \(C_1\) that match, as closely as physically possible, on:

- spiking trajectory;
- subthreshold membrane trajectory;
- synaptic outputs;
- field effects;
- neuromodulatory consequences;
- downstream realized causal effects;
- report pathway.

The target manipulation would change only the neuron's **latent counterfactual capacity**.

This is technologically difficult, perhaps impossible with current biological control. Its value is conceptual and programmatic: it specifies the evidence that would separate PRD from a stronger dispositional view.

## 8.2 Divergent predictions

A strong dispositional interpretation allows:

\[
\Delta\text{latent capacity}
\Rightarrow
\Delta\text{phenomenology}
\]

even when the altered capacity is not manifested in an ordinary actual causal cascade.

PRD predicts:

\[
\boxed{
\Delta\Gamma_h=0
\Rightarrow
\Delta\text{present organized phenomenology}=0.
}
\]

If phenomenal reports change, PRD predicts that an actual causal consequence of the manipulation was missed.

The contrast directly mirrors the actualist/dispositionalist distinction analyzed by Ponce de Leon and Yoshimi (2026), but PRD is neither of their simplest poles. It accepts dispositional characterization **inside actual support** and denies unrestricted constitutive relevance outside it.

## 8.3 Falsification condition

PRD would be under strong pressure if repeated experiments established all of the following:

1. a manipulation changes latent counterfactual capacity;
2. all theory-specified actual causal consequences are held fixed or excluded with adequate sensitivity;
3. experience-sensitive reports or other justified phenomenal measures change systematically;
4. no actual-participation path mediates the change.

Such a result would favor a stronger dispositional account.

Conversely, merely showing that disabling a silent neuron changes a report would not by itself distinguish the theories. The manipulation might alter subthreshold potentials, inhibitory balance, field effects, downstream gain, or another actual physical condition. The empirical burden is therefore to isolate **capacity change from actual causal change**.

## 8.4 Relation to unfolding arguments

Unfolding arguments show that systems with different internal causal topology can sometimes reproduce the same input-output mapping. Recent work has emphasized that plasticity, history dependence, and temporal encoding can restore empirically measurable differences that a static feedforward unfolding cannot capture (O'Reilly-Shah, Selvitella, & Schurger, 2026).

PRD's relevant equivalence is neither input-output equivalence nor a simple "recurrent versus feedforward" dichotomy. The comparison is at the level of the **realized episode support plus the local response profiles of actual participants**. If a purported unfolding preserves only behavior but changes \(\Gamma_h\), PRD permits a phenomenal difference. If a physical realization genuinely preserves the entire relevant \(\Gamma_h\) up to admissible multiscale isomorphism, PRD does not permit the theory to invoke recurrence labels alone as a phenomenal difference.

## 8.5 Secondary experimental route: dynamic self-boundaries

A second experimental program follows from the same logic. If threat, pain, or interoception changes body ownership or self-boundary, PRD-compatible extensions predict that the change must be mediated by an actual reorganization of the causal processes generating the relevant subject/body representation. Changes in valence alone should not be sufficient.

This program is developed elsewhere because it requires a theory of valence and subject dynamics beyond the scope of the present paper.

---

# 9. Discussion

## 9.1 What PRD adds to the actualism/dispositionalism debate

The usual actualism/dispositionalism contrast is too coarse for present purposes. "Actual" can mean overt activity, observed trajectory, or token causal contribution. "Dispositional" can mean any unrealized capacity of the substrate, or only the intervention-sensitive role of processes already engaged in the realized episode.

PRD separates these questions.

A process can be **silent but actual** if its current state participates in the episode. A process can be **intrinsic but episode-idle** if it belongs to the system yet does not participate in the target token relation. Counterfactual structure is then retained, but only locally around actual participants.

This yields a three-way distinction:

\[
\text{trajectory actualism}
\quad\neq\quad
\text{PRD}
\quad\neq\quad
\text{unrestricted dispositionalism}.
\]

The resulting view is intended to preserve the strongest motivation on each side. From actualism it inherits sensitivity to the causal history of the episode. From dispositionalism it inherits the idea that an actual state's relational identity can depend on nearby intervention-sensitive alternatives.

## 9.2 Relation to IIT

IIT 4.0 is substantially more developed than PRD as a theory of phenomenal structure. It specifies phenomenological axioms, physical postulates, irreducibility measures, exclusion criteria, and a structured mapping from physical cause–effect structure to experience. PRD does not attempt to reproduce that machinery.

The disagreement is narrower. IIT gives a component's intrinsic cause–effect power constitutive relevance when the component belongs to the relevant complex. This supports the silent-neuron predictions analyzed by Ponce de Leon and Yoshimi (2026). PRD inserts an additional episode-level gate:

\[
\boxed{
\text{membership in the relevant system}
\not\Rightarrow
\text{membership in the current token support}.
}
\]

Only dispositions borne by actual participants enter the present episode germ.

This difference has costs. PRD must supply a defensible token participation relation, whereas IIT derives relevance from its own intrinsic causal calculus. But it also gains a clearer response to cases in which latent capacity appears disconnected from the realized causal history of the episode.

## 9.3 Relation to ICF/ICCR

ICF/ICCR is the closest contemporary neighbor. The comparison is deliberately conservative: ICCR explicitly requires preserved counterfactual branches to be carried by components that are load-bearing in actual dynamics, and excludes idle Olympia-style machinery. PRD therefore does not claim priority for the load-bearing requirement itself. Its proposed added value is the explicit episode-indexed token-support object and the use of that object as a gate on dispositions admitted to the present phenomenal bridge.

ICF/ICCR is the closest contemporary neighbor. It already rejects observer-imposed mappings, requires physically realized intrinsic partitions, enriches functional structure with interventions and internal readouts, and excludes purely idle Olympia machinery. PRD therefore should not be advertised as a replacement for ICCR.

The proposed distinction is second-order:

\[
\boxed{
\text{intrinsic realization}
\rightarrow
\text{episode-specific token participation}.
}
\]

ICCR asks whether the physical system realizes the correct intrinsic causal-computational organization. PRD asks, given a physically intrinsic realization, which **token-level realized relations** are eligible to constitute the present episode.

The two frameworks could ultimately be complementary. ICCR can supply a principled intrinsic variable partition and admissible intervention structure; PRD can then ask whether an additional episode-specific support relation is needed inside that intrinsic realization.

The novelty claim here must therefore be interpreted conservatively. ICCR already states that components carrying preserved counterfactual branches must be load-bearing in actual dynamics, and its recurrent toy model emphasizes variables that are read and written during the actual run. That commitment is close to the motivation of PRD. If ICCR's load-bearing condition is itself developed into a complete token-level account of episode-specific actual causal contribution, including redundancy, preemption, static enabling, and conjunctive determination, then PRD should be understood as an explicit formalization or refinement of that condition rather than as a competing principle.

The intended added value of PRD is narrower: it promotes episode-specific token causal support to an explicit object used by the phenomenal bridge, distinguishes this object from system-level intrinsic membership, and imposes participation-sensitive constraints on coarse graining. The distinction is substantive only if intrinsic load-bearing membership and token support can come apart in theoretically or empirically relevant cases, or if formalizing token participation yields predictions not fixed by ICCR alone. Establishing either point is a central task for future work.

## 9.4 Relation to actual causation

PRD's main vulnerability is obvious: token causation is contested. Different actual-causation theories can disagree about overdetermination, omissions, preemption, and causal granularity.

The modular formulation is meant to expose rather than conceal this dependence. A future version of PRD should compare multiple participation modules and identify which phenomenal predictions are robust across them.

This is scientifically preferable to defining actual participation informally and then adjusting it case by case. A consciousness theory that makes token contribution constitutive must inherit some of the hard problems of causation.

## 9.5 Relation to phenomenal structuralism

Quality-space and structural approaches argue that phenomenal quality depends in part on relations among experiences or possible experiences. Fleming and Shea (2024) emphasize that conscious sensory states can be located in quality spaces defined by relations to other possible sensory states. Recent IIT work similarly develops structured accounts of spatial extendedness, temporal flow, and objects (Grasso, Hendren, & Tononi, 2026).

PRD is orthogonal to much of that project. It does not tell us the final geometry of red, pain, space, or time. It asks a prior physical question:

> Which physical relations are eligible to enter the present phenomenal structure in the first place?

The answer proposed here is not "all relations in the full transition table," nor "only the realized trajectory," but "the actual-participation support plus the local dispositions of its realized participants."

## 9.6 Subject individuation and the non-overreach principle

The equivariant selection obstruction illustrates a broader principle running through the framework:

\[
\boxed{
\text{structure should not license identity beyond the asymmetry it actually contains}.
}
\]

This principle also motivates PRD itself. A latent capacity outside the actual support should not receive present phenomenal status merely because a broader model can describe it. Similarly, a symmetric candidate-subject structure should not be forced into a unique subject merely because a theory demands the integer one.

The principle is methodological rather than metaphysically complete. A theorist can always add primitive haecceities, absolute psychophysical labels, or additional exclusion rules. The burden is then to state those additions explicitly rather than present them as consequences of the original structure.

## 9.7 What the framework does not solve

Several major problems remain.

First, PRD does not explain why there is phenomenality at all. It constrains organization conditional on a phenomenal ontology.

Second, it does not uniquely determine the bridge \(\widetilde\Phi\) from normalized physical structure to phenomenal structure. Proposition 3 makes that underdetermination explicit.
