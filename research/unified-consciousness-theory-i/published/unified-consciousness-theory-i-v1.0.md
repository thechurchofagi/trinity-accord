# Unified Consciousness Theory I
## From Experience Existence to Experiential Structure

**Author:** Hongju Liu  
**Affiliation:** Independent researcher, Shenzhen, China  
**Report:** TA-TR-2026-20  
**Version:** 1.0  
**Date:** 28 September 2026  
**DOI:** 10.5281/zenodo.23005588  
**Status:** Foundational theory preprint prepared for open-access DOI publication; not peer reviewed.  
**AI assistance disclosure:** Substantial ChatGPT (OpenAI GPT-5.6 Sol) assistance was used for literature retrieval, formalization, adversarial review, theorem and counterexample checking, drafting, editing, and publication preparation under human direction. The human author of record is responsible for the decision to publish.

---

## Abstract

Most theories of consciousness seek a property that distinguishes conscious from nonconscious systems. Unified Consciousness Theory (UCT) begins from a different axiom: every actual valid physical process token has non-empty experience. If this axiom is granted, the binary existence problem becomes trivial on the domain of actual process tokens. A nontrivial universal theory must instead predict *experiential structure*.

UCT proposes that the experiential structure of a process is structurally identical to its full physically anchored, mechanism-fixed intervention-response organization:

\[
\Phi_{t,\tau,g}(P)
\equiv_{\rm struct}
\mathfrak D^{PA}_{t,\tau,g}(P),
\]

with

\[
\mathfrak D^{PA}
=
(P,s_t,\Theta,C^{PA},\bar{\mathcal I}^{MF},R_\Theta,\mathcal R).
\]

The paper develops a plural process-token ontology, a Physical Anchoring Condition that blocks arbitrary functional/trajectory implementations, and a hierarchy separating full structure from incomplete scalar descriptors. It derives, conditional on A1, an Organization-Gate Impossibility result: under universal basal experience, no nonuniversal threshold of integration, recurrence, workspace access, memory, higher-order representation, complexity, or entropy can equal the universal experience-existence predicate. It also derives a chart-covariance result under structure-preserving reparameterization and a Nontrivial Universality Retargeting result under A1: the substantive task of a universal UCT is to predict structure rather than a constant conscious/nonconscious label.

The proposal is explicitly conditional on strong axioms. It does not claim that universal experience or structural identity has been empirically established, nor that the hard problem has been deductively solved. Its purpose is to articulate the consequences, explanatory costs, and empirical obligations of a process-token structural identity view.

The formal results in this paper are largely conditional consequences of strong starting commitments. Their scientific value therefore depends on whether the physically anchored bridge program yields independently constrained, generalizable empirical structure rather than on the logical difficulty of the proofs themselves.

**Keywords:** consciousness; panexperientialism; causal structure; physical anchoring; intervention-response structure; process ontology; multiscale consciousness; theory unification

---

# 1. The target problem

Contemporary theories often ask which physical property makes a system conscious (Seth & Bayne, 2022). IIT, recurrent-processing approaches, global-workspace theories, higher-order theories, information-closure accounts, and related frameworks assign different roles to integration, recurrence, access, representation, closure, or modeling (Albantakis et al., 2023; Chang et al., 2020; Kanai & Fujisawa, 2024).

UCT begins by separating two questions:

\[
\boxed{
\text{Does experience exist?}
}
\]

from:

\[
\boxed{
\text{What is the organization of that experience?}
}
\]

The distinction is radical only because UCT fixes the first question axiomatically.

---

# 2. Six foundational commitments

### A1 Universal Experience

\[
\forall P_{\rm actual},\quad \Phi(P)\neq\varnothing.
\]

A1 is an axiom, not an inference from evolution or neuroscience.

### A2 Continuity

Continuously comparable physical changes imply continuous change in the relevant experiential organization. Derived coarse variables may still undergo threshold transitions.

### A3 Nested Non-Exclusion

If a lower-scale actual process remains physically realized inside a larger process, inclusion alone does not delete its experience.

### A4 Human Self Formation

Human conceptual selfhood is a higher-level organization, not a prerequisite for basal experience.

### A5 Physically Anchored Experience–Structure Identity

\[
\Phi(P)\equiv_{\rm struct}\mathfrak D^{PA}(P).
\]

This notation is shorthand for two commitments.

**A5a — Structural correspondence.** The complete pointed organization of experience is identified structure-for-structure with the complete physically anchored intervention-response organization.

**A5b — Phenomenal completeness.** UCT posits no additional phenomenal degree of freedom that can vary independently while the complete \(\mathfrak D^{PA}\) remains fixed:

\[
\boxed{
\mathfrak D^{PA}(P)\cong\mathfrak D^{PA}(Q)
\Rightarrow
\Phi(P)\cong\Phi(Q),
}
\]

with no extra hidden variable \(z_{\rm phenomenal}\).

A5 is therefore stronger than a claim of mere correlation or relational similarity. It is a metaphysical identity/completeness postulate. Stage-I does not derive A5 from neuroscience or from nonphenomenal premises.

### A6 Token / Type / Lineage Distinction

\[
\mathfrak D(P)\cong\mathfrak D(Q)
\not\Rightarrow
P=Q.
\]

Copies may share structural type without being the same token.


### Experience–Subject Separation Principle

A1 assigns non-empty experiential structure to an actual process token. It does **not** by itself imply that every such process is a uniquely bounded or canonically individuated subject.

\[
\boxed{
\text{experience-bearing process token}
\neq
\text{canonically individuated subject}.
}
\]

Stage-I therefore separates:

- existence of experiential structure;
- unity/irreducibility of that structure;
- subject individuation;
- explicit self-model;
- numerical token identity.

A unique subject partition, subject count, or first-person center requires additional individuation structure and is not derived from A1 alone. This distinction is essential for avoiding the claim that UCT has already solved the subject-combination problem.

---

# 3. Process-token ontology

UCT models actual physical reality in terms of causally continuous process histories.

A valid token must satisfy:

1. actuality;
2. nonempty support;
3. causal continuity;
4. retention of actual induced internal relations;
5. explicit physical boundary relations;
6. causal/state sufficiency for the attributed response family.

Tokens may:

- overlap;
- nest;
- branch;
- merge;
- persist across replacement;
- coexist at micro and macro scales.

UCT does not impose a unique partition of the world into experiential subjects. More precisely, Stage-I does not identify every experience-bearing process token with a canonically bounded subject:

\[
\boxed{
\text{experience-bearing process}
\neq
\text{canonical subject}.
}
\]

Subject individuation is a separate theoretical problem.

This is an ontological cost, not an accidental bug.

---

# 4. The physically anchored mother structure

For a declared scale \(g\) and horizon \(\tau\),

\[
P=(X,U,\Theta,K_\Theta,s_t).
\]

Define the mechanism-fixed intervention family

\[
\mathcal I^{MF}
\]

as physically realizable changes of existing state/boundary variables that leave the constitutive mechanism \(\Theta\) fixed over the declared horizon.

The full object is:

\[
\boxed{
\mathfrak D^{PA}
=
(P,s_t,\Theta,C^{PA},\bar{\mathcal I}^{MF},R_\Theta,\mathcal R).
}
\]

## Physical Anchoring Condition

A valid chart \(C^{PA}\) must:

- correspond to actual physical degrees of freedom or justified physical coarse-grainings;
- be fixed independently of the desired consciousness label;
- preserve admissible counterfactual responses, not only actual trajectories;
- retain actual internal causal relations;
- ground boundaries in actual physical couplings;
- respect invertible coordinate covariance.

Thus:

\[
\text{trajectory fit}
\not\Rightarrow
\text{UCT implementation}.
\]

This constraint is related to prior mechanistic and robust-mapping approaches to physical computation (Piccinini, 2015; Anderson & Piccinini, 2024); its role here is specifically to constrain the structure that enters A5.


PAC is **not** a theorem that physics selects one unique natural coarse-graining. UCT instead uses a scale-indexed rule:

\[
\boxed{
\text{physically justified non-equivalent coarse-grainings may define distinct macroprocess structures}.
}
\]

Invertibly related anchored charts are equivalent descriptions. Noninvertible but physically justified coarse-grainings may correspond to different process scales. Competing non-equivalent physical models must be assessed by ordinary scientific adequacy rather than by a consciousness label.

---

# 5. Response geometry

Let two mechanism-fixed interventions be equivalent when they generate the same complete process response:

\[
\iota_1\sim_P\iota_2
\iff
R_\Theta(\iota_1)=R_\Theta(\iota_2).
\]

The quotient

\[
\mathcal Q_P
=
\mathcal I^{MF}/\sim_P
\]

describes the physically distinguishable differences available to the process.

An appropriate response relation or distance equips this quotient with a geometry.

This supplies a primitive interpretation of "what the process can discriminate."

It is broader than biological sensation and does not presuppose report.

---

# 6. Experience is not a scalar

UCT distinguishes:

1. the full mother structure;
2. complete invariants, when available;
3. incomplete structural diagnostics;
4. task-specific scalar measures.

Hence:

\[
\boxed{
\text{the experience is the structure; the numbers are coordinates on the structure}.
}
\]

Entropy, effective information, integration, recurrence, statistical complexity, and autonomy can all be useful descriptors without being phenomenally complete.

An exact counterexample is supplied by two independent identity bits and two independent toggles: they can agree on a broad collection of scalar diagnostics while differing in fixed-point/periodic-orbit structure.

---

# 7. Organization-Gate Impossibility

Define:

\[
E(P)=\mathbf1[\Phi(P)\neq\varnothing].
\]

By A1:

\[
E(P)=1
\quad
\forall P_{\rm actual}.
\]

Let \(F(P)\) be any organization descriptor and \(S\) a threshold or target region. If some actual process lies outside \(S\),

\[
\exists Q_{\rm actual}:F(Q)\notin S,
\]

then:

\[
\boxed{
\mathbf1[F(P)\in S]
\not\equiv
E(P).
}
\]

Therefore no nonuniversal threshold of:

- integration;
- recurrence;
- global workspace access;
- explicit memory;
- higher-order representation;
- predictive modeling;
- autonomy;
- entropy;
- biological complexity

can equal the universal experience-existence predicate inside UCT.

This does **not** make those mechanisms irrelevant. It relocates them to organization.

---

# 8. Nontrivial universality retargeting

A universal theory is often asked to decide whether arbitrary fully described dynamical systems are conscious (Kanai & Fujisawa, 2024).

Under A1, for actual valid tokens:

\[
E(P)=1.
\]

Therefore for any distribution over actual tokens:

\[
H(E)=0.
\]

Binary existence classification carries no discriminative information on that domain.

UCT therefore retargets universality:

\[
\boxed{
P
\mapsto
[\mathfrak D^{PA}(P)]_{\cong}.
}
\]

The nontrivial question is:

> What experiential organization does this actual process instantiate?

This creates a major empirical burden. UCT cannot succeed merely by saying "everything actual experiences something."

It must predict structured differences across organisms, machines, states, interventions, and scales.

---

# 9. Chart covariance and multiscale plurality

If two charts are related by an invertible mapping that preserves the pointed state, physical boundaries, intervention classes, response relations, and internal structure, then:

\[
\mathfrak D^{PA}_{C}(P)
\cong
\mathfrak D^{PA}_{C'}(P)
\]

and hence:

\[
\Phi_C(P)\cong\Phi_{C'}(P).
\]

Coordinate relabeling cannot create experience differences.

But noninvertible coarse-graining is different. A macroprocess can possess a distinct response structure and therefore a distinct macro experiential organization.

Thus:

\[
\boxed{
\text{coordinate covariance}
\neq
\text{scale equivalence}.
}
\]

---

# 10. Evolution as organization-space motion

For a lineage

\[
P_0\leadsto P_1\leadsto\cdots\leadsto P_n,
\]

UCT represents evolution as a trajectory through multidimensional organization space.

It does not require:

\[
\frac{dC}{dt}>0
\]

for one universal complexity scalar.

Specific transitions may increase some dimensions—discrimination, regulation, recurrence, memory, autonomy, causal integration—while decreasing others.

A1 keeps basal experience nonempty throughout the actual lineage.

Evolution therefore motivates continuity intuitions but does not prove A1.

---

# 11. Strong objections

## 11.1 The unfolding/substitution challenge

UCT predicts that behaviorally equivalent systems can differ phenomenally if their physically anchored internal response structures differ. This places it directly in the debate initiated by the Unfolding Argument and its responses (Doerig et al., 2019; Kleiner, 2020; Tsuchiya et al., 2020; Usher, 2021; Herzog et al., 2022).

This is an intentional anti-behaviorist commitment and inherits the empirical underdetermination problem emphasized by the unfolding/substitution debate.

## 11.2 Functional implementation triviality

Arbitrary automaton mappings are excluded by physical anchoring and counterfactual commutation. Recent consciousness-specific work argues that functional indeterminacy remains a deep issue even if the original Unfolding Argument is unsound (Basri et al., 2026).

This constrains but does not prove one unique natural coarse-graining.

## 11.3 Metaphysical structuralism

A5 remains a metaphysical identity postulate. Contemporary criticism of metaphysical phenomenal structuralism provides a direct pressure test on this commitment (Negro, 2025).

Knowing a description of a structure is not the same as instantiating the pointed physical structure, but UCT has no deduction showing why physical structure must be phenomenal.

## 11.4 Combination problem

The subject-combination problem is a central pressure on panpsychist views (Chalmers, 2016), with related de-combination pressure on nested subjects (Miller, 2018). UCT does not claim that all nested experience-bearing process tokens are nested **subjects**. It replaces subject-summing with non-summative macro-process realization and keeps subject individuation as a separate problem.

It does not yet prove a unique first-person subject boundary, subject count, or phenomenal boundedness relation.

## 11.5 Causal efficacy

Identity avoids adding a duplicate phenomenal causal force.

It does not eliminate the explanatory gap by deduction.

---

# 12. Empirical obligations

Paper I makes no claim of R4 validation. Its internal no-go results are mostly simple consequences of strong axioms; scientific value therefore depends on independently constrained bridge tests.

A serious program should preregister at least four classes of tests.

## E1 — Phenomenal-geometry correspondence

For a reportable perceptual domain, define independently:

1. a phenomenal similarity/difference geometry from psychophysics;
2. a physically anchored intervention-response geometry from neural/physical measurements.

Test whether the two structures exhibit stable correspondence and whether UCT descriptors outperform relevant alternative physical descriptors.

This does not prove A5, but failure of systematic correspondence would weaken the bridge program.

## E2 — Trajectory-matched causal divergence

Identify systems or brain/network states with closely matched observable trajectories but different internal mechanism-fixed response structures.

UCT predicts:

\[
\mathfrak D^{PA}_1\not\cong\mathfrak D^{PA}_2.
\]

The crucial difficulty is obtaining an independent consciousness measure; this is precisely where the unfolding/falsification literature places pressure on causal-structure theories.

## E3 — Graded-perturbation continuity

Under a continuous physically controlled perturbation, A2 predicts continuous variation in the underlying physical/experiential structure even when access, report, decision, or ignition observables cross a sharp threshold.

The empirical test concerns the structural bridge, not direct proof that basal experience remains nonzero.

## E4 — Multiscale macroprocess prediction

Where a physically justified coarse-graining develops stronger closure, autonomy, or causal selectivity, UCT predicts a distinct macroprocess structure without ontological deletion of lower process structures.

Again, the macroprocess criterion must be fixed independently of a desired consciousness result.

These tests should be treated as prospective bridge programs, not as completed validation.

---

# 13. Relation to prior art

None of the following is claimed as UCT's invention:

- panexperientialism/panpsychism;
- intrinsic causal structuralism;
- multiscale consciousness;
- overlapping conscious systems;
- universalizing consciousness theory constructs;
- process/coarse-graining theories;
- robust physical implementation criteria.

Important neighboring work includes IIT 4.0 (Albantakis et al., 2023), Information Closure Theory (Chang et al., 2020), TICL (Winters, 2020, 2021), neurophenomenal structuralism (Lyre, 2022), universal-theory criteria (Kanai & Fujisawa, 2024), overlapping-conscious-system arguments (Blackmon, 2021), and robust mapping/mechanistic computation (Piccinini, 2015; Anderson & Piccinini, 2024).

The narrow UCT synthesis is:

\[
\boxed{
\text{universal process-token experience}
+
\text{physically anchored structural identity}
+
\text{nested non-exclusion}
+
\text{organization-gate impossibility}
+
\text{structural-universality retargeting}.
}
\]

Historical priority remains open.

---

# 14. Claim-status summary

| Claim | Status in Paper I |
|---|---|
| Universal experience for actual valid process tokens | Axiom A1 |
| Continuity of experiential organization | Axiom A2 with scope restriction |
| Nested non-exclusion | Axiom A3 |
| Human-like self not prerequisite for experience | Axiom A4 |
| Physically anchored experience–structure identity | Axiom A5, unpacked into correspondence + completeness |
| Token/type/lineage distinction | Axiom A6 |
| Process ≠ canonical subject | Stage-I separation principle |
| Organization-Gate Impossibility | conditional consequence of A1 |
| Binary universality trivialization | conditional consequence of A1 |
| Chart covariance | conditional on structure-preserving invertible reparameterization |
| No-Hidden-Quale consequence | conditional on A5 completeness |
| Scalar diagnostic non-completeness | exact counterexample for tested descriptor family |
| E1–E4 empirical bridge program | prospective, not yet validated |
| UCT is empirically true | not established |
| UCT has historical priority | not established |
| UCT solves subject combination | not claimed |
| UCT solves the hard problem | not claimed |

---

# 15. Conclusion

UCT I proposes that, once universal basal experience is adopted as an axiom, the central scientific problem changes.

The existence predicate becomes constant over actual valid process tokens.

The nontrivial target becomes experiential structure.

UCT identifies that structure with a physically anchored mechanism-fixed intervention-response organization and derives several consequences: no nonuniversal complexity threshold can create experience from zero, coordinate changes do not alter experience, macroprocesses may coexist with microprocesses, and organization measures are projections rather than the experience itself.

The proposal is strong, costly, and falsification-challenged.

It is offered not as an empirically completed theory, but as a precise foundational target whose consequences can be audited.

Paper II asks whether major existing consciousness theories can be recovered as effective organization theories on top of this foundation.

After specialist review, Paper I should be read as a **foundational metaphysical/formal research program with explicit empirical bridge obligations**, not as a completed empirical neuroscience theory.


---

# References

Albantakis, L., et al. (2023). Integrated information theory (IIT) 4.0: Formulating the properties of phenomenal existence in physical terms. *PLoS Computational Biology, 19*(10), e1011465. https://doi.org/10.1371/journal.pcbi.1011465

Anderson, N. G., & Piccinini, G. (2024). *The Physical Signature of Computation: A Robust Mapping Account*. Oxford University Press. https://doi.org/10.1093/9780191872075.001.0001

Basri, J., BarAvi, P., & Hemmo, M. (2026). Functionalist theories of consciousness: unfolding, substitution and the indeterminacy of function by the physics of the brain. *Consciousness and Cognition, 145*, 104121. https://doi.org/10.1016/j.concog.2026.104121

Blackmon, J. C. (2021). Integrated Information Theory, intrinsicality, and overlapping conscious systems. *Journal of Consciousness Studies, 28*(11–12), 31–53. https://doi.org/10.53765/20512201.28.11.031

Chalmers, D. J. (2016). The combination problem for panpsychism. In G. Bruntrup & L. Jaskolla (Eds.), *Panpsychism: Contemporary Perspectives* (pp. 179–214). Oxford University Press. https://doi.org/10.1093/acprof:oso/9780199359943.003.0008

Chang, A. Y. C., Biehl, M., Yu, Y., & Kanai, R. (2020). Information Closure Theory of Consciousness. *Frontiers in Psychology, 11*, 1504. https://doi.org/10.3389/fpsyg.2020.01504

Doerig, A., Schurger, A., & Herzog, M. H. (2021). Hard criteria for empirical theories of consciousness. *Cognitive Neuroscience, 12*(2), 41–62. https://doi.org/10.1080/17588928.2020.1772214

Doerig, A., Schurger, A., Hess, K., & Herzog, M. H. (2019). The unfolding argument: Why IIT and other causal structure theories cannot explain consciousness. *Consciousness and Cognition, 72*, 49–59. https://doi.org/10.1016/j.concog.2019.04.002

Herzog, M. H., Schurger, A., & Doerig, A. (2022). First-person experience cannot rescue causal structure theories from the unfolding argument. *Consciousness and Cognition, 98*, 103261. https://doi.org/10.1016/j.concog.2021.103261

Kanai, R., & Fujisawa, I. (2024). Toward a universal theory of consciousness. *Neuroscience of Consciousness, 2024*(1), niae022. https://doi.org/10.1093/nc/niae022

Kleiner, J. (2020). Brain states matter. A reply to the unfolding argument. *Consciousness and Cognition, 85*, 102981. https://doi.org/10.1016/j.concog.2020.102981

Lyre, H. (2022). Neurophenomenal structuralism. A philosophical agenda for a structuralist neuroscience of consciousness. *Neuroscience of Consciousness, 2022*(1), niac012. https://doi.org/10.1093/nc/niac012

Miller, G. (2018). Can subjects be proper parts of subjects? The de-combination problem. *Ratio, 31*(2), 137–154. https://doi.org/10.1111/rati.12166

Negro, N. (2025). Three arguments against metaphysical structuralism in consciousness research. *Synthese, 206*, 8. https://doi.org/10.1007/s11229-025-05103-6

Piccinini, G. (2015). *Physical Computation: A Mechanistic Account*. Oxford University Press. https://doi.org/10.1093/acprof:oso/9780199658855.001.0001

Seth, A. K., & Bayne, T. (2022). Theories of consciousness. *Nature Reviews Neuroscience, 23*, 439–452. https://doi.org/10.1038/s41583-022-00587-4

Tsuchiya, N., Andrillon, T., & Haun, A. (2020). A reply to “the unfolding argument”: Beyond functionalism/behaviorism and towards a science of causal structure theories of consciousness. *Consciousness and Cognition, 79*, 102877. https://doi.org/10.1016/j.concog.2020.102877

Usher, M. (2021). Refuting the unfolding-argument on the irrelevance of causal structure to consciousness. *Consciousness and Cognition, 95*, 103212. https://doi.org/10.1016/j.concog.2021.103212

Winters, J. J. (2020). The temporally-integrated causality landscape: A theoretical framework for consciousness and meaning. *Consciousness and Cognition, 83*, 102976. https://doi.org/10.1016/j.concog.2020.102976

Winters, J. J. (2021). The Temporally-Integrated Causality Landscape: Reconciling neuroscientific theories with the phenomenology of consciousness. *Frontiers in Human Neuroscience, 15*, 768459. https://doi.org/10.3389/fnhum.2021.768459

Yaron, I., Melloni, L., Pitts, M., et al. (2022). The ConTraSt database for analysing and comparing empirical studies of consciousness theories. *Nature Human Behaviour, 6*, 593–604. https://doi.org/10.1038/s41562-021-01284-5