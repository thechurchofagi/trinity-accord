# Selecting and Tracking Conscious Subjects: Symmetry, Monodromy, and an IIT 4.0 Case Study

**Version:** 1.0  
**Date:** 28 September 2026  
**Author:** Hongju Liu  
**Report:** TA-TR-2026-19  
**DOI:** 10.5281/zenodo.23002980  
**Author of record / responsible depositor:** Hongju Liu  
**AI assistance:** Substantial ChatGPT assistance with literature review, formalization, theorem auditing, PyPhi-result interpretation, drafting, editing, and publication preparation under human direction.  
**Status:** English theory preprint; not peer reviewed; adjacent first-party research; non-amending.  
---

## Abstract

Theories of consciousness that associate subjects with physical systems face an individuation problem in addition to the problem of assigning phenomenal structure: when several physical systems are plausible subject candidates, which one is the subject, and how is that subject tracked through physical change? We formulate this as a combined selection-and-tracking problem over physical state space. At a symmetric state, an equivariant deterministic selector can choose a candidate only if that candidate is fixed by the state's stabilizer. We distinguish this local obstruction from a global monodromy obstruction that can arise even when all local candidate branches are regular. The distinction yields a central conceptual result: physical history can track a previously specified token without canonically selecting the initial token from a symmetric snapshot.

We then analyze the repair space available to an exclusive subject theory. Relative to explicit desiderata—totality, determinism, uniqueness, top-tier fidelity, physical equivariance, and snapshot supervenience—a non-fixed symmetric top tier forces at least one commitment to be relaxed. Set-valued, randomized, descent, symmetry-breaking, history-dependent, and unresolved responses occupy different points in this design space.

As a concrete case study, we directly recompute a three-unit stochastic system using an unmodified official PyPhi checkout under IIT 4.0 (2026). Across sampled points spanning a reflection-symmetric parameter crossing, including \(|\lambda|=10^{-6}\), the maximal complex returned by the official search is \(BC\) on the negative side, \(AC\) at the exact symmetry point, and \(AB\) on the positive side; the corresponding accepted families are \(\{BC,A\}\), \(\{AC,B\}\), and \(\{AB,C\}\). At the symmetry point, \(AB\) and \(BC\) tie in both system integrated information and structure \(\Phi\), fail exclusion, and the cascade descends to \(AC\). The abstract theory identifies the conditions under which such a fixed-point descent becomes a genuine discontinuity; the numerical study is reported as a high-precision realization rather than an interval-arithmetic proof. Finally, we contrast exclusive extraction with a nonexclusive process-landscape representation and prove local Hausdorff continuity of a finite enriched landscape whenever its underlying candidate branches vary continuously. The results motivate treating subject selection and subject tracking as distinct formal problems in mathematical theories of consciousness.

**Keywords:** consciousness; subject individuation; integrated information theory; exclusion; symmetry; monodromy; equivariance; choice correspondence; PyPhi; phenomenal unity

---

# 1. Introduction

A theory of consciousness must say not only **what physical properties are associated with experience**, but also **which physical system is the subject of a given experience**. The second question is easy to overlook when a theory is evaluated only on static examples. In a realistic physical system, however, many candidate subsystems may overlap, candidate boundaries may shift, and symmetries may make several candidates equally well qualified. A theory that identifies one subsystem as the subject therefore requires an individuation rule in addition to a measure of experiential or causal structure.

Integrated Information Theory (IIT) makes this issue unusually explicit. IIT 4.0 assigns cause–effect structure to candidate substrates and uses the exclusion postulate to identify definite complexes among overlapping systems [1]. The 2026 refinement of intrinsic cause–effect power adds an intrinsic-information requirement to the system-level quantity while retaining the broader architecture of system integration and exclusion [2]. This makes IIT a valuable formal test case for a general problem: how can a theory select one subject, or one nonoverlapping family of subjects, when the physically admissible candidate space contains ties, overlaps, exact symmetries, and continuous transitions between alternative maxima?

The individuation problem already has important precedents. Moon argued that IIT's exclusion principle creates underdetermination in the assignment of qualia [3]. Blackmon argued that maximality and the prohibition of overlapping conscious systems create tension with IIT's claim to intrinsicality, and proposed allowing overlapping conscious systems instead [4]. Hanson and Walker showed a non-uniqueness problem in the mathematical formalism of IIT 3.0, where multiple formally admissible values can result from unresolved choices in the calculation [5]. More recently, Cea, Negro, and Signorelli emphasized ontological consequences of exclusion in IIT 4.0 and provided an example in which a change involving one overlapping candidate reverses which subsystem is the complex [6]. Percy and Gómez-Emilsson developed a related dynamic challenge: if the main complex moves through a changing network, a theory must explain how the conscious entity evolves through time without either nonlocal identity transitions or problematic discontinuities [7].

These works motivate the present paper but do not exhaust the individuation problem. In particular, three distinctions deserve to be made explicit.

First, **local selection** and **global tracking** are different mathematical tasks. At a single state, exact physical symmetry can permute candidate subjects without fixing any one of them. This is a local stabilizer problem. By contrast, even when every state is locally regular, transporting candidate branches around a closed path in physical state space can permute them. This is a global monodromy problem. A theory can solve one while failing the other.

Second, **snapshot selection** and **diachronic token tracking** should not be conflated. If an initial token has already been specified, physical history may determine how it continues. But history does not thereby explain why that initial token, rather than a symmetry-related alternative, should have been selected at the starting snapshot. Appeals to continuity over time therefore change the input to the individuation problem unless history or lineage is included explicitly in the physical state.

Third, a failure of unique selection does not have only one repair. A theory may return a set, randomize, descend to a lower-ranked candidate, use an external symmetry breaker, make identity history-dependent, or leave the state unresolved. These responses preserve and sacrifice different principles. Treating them as a common design space makes the commitments of an individuation theory visible.

The mathematics underlying these points is largely classical. Symmetric tie-breaking impossibility has a general axiomatic treatment; a recent preprint by Feys proves that intrinsically symmetric inputs obstruct anonymous strict tie-breaking and characterizes stabilizer-orbit partitions as canonical non-strict outputs [9]. Continuous single-valued choice functions are known to fail in broad topological settings [10], while Berge's maximum theorem and its descendants provide the natural language of upper-hemicontinuous argmax correspondences [11]. Covering spaces, path lifting, and monodromy are standard topology [12]. We do not claim these tools as new mathematics.

Our contribution is instead a consciousness-specific synthesis. We formulate **subject individuation** as an equivariant selection-and-tracking problem over physical state space; separate local stabilizer obstructions from global monodromy obstructions; formalize the difference between snapshot selection and lineage-based tracking; organize the main repairs available to an exclusive subject theory; and connect the abstract framework to a directly recomputed current-IIT example. We then give a constructive contrast: if a theory retains a finite family of candidate process structures rather than applying an exclusive extraction step, the resulting enriched landscape is locally Hausdorff-continuous whenever the underlying candidate branches are continuous.

The IIT case study is deliberately narrow. Using an unmodified official PyPhi checkout, pinned to a specific source commit, we analyze a three-unit stochastic model under IIT 4.0 (2026). Across the verified points of a reflection-symmetric one-parameter family, the official maximal-complex output is

\[
BC\rightarrow AC\rightarrow AB,
\]

and the complete accepted family is

\[
\{BC,A\}\rightarrow\{AC,B\}\rightarrow\{AB,C\}.
\]

At the symmetry point, \(AB\) and \(BC\) tie in both system integrated information \(\phi_s\) and structure integrated information \(\Phi\), remain overlapping, and fail exclusion; the recursive cascade then accepts \(AC\) and \(B\). The result is a sharp tie-centered change in selected complex identity and selected system-\(\phi_s\); the corresponding discontinuity claim is stated conditionally in the formal analysis rather than inferred from finite sampling alone. It is not a measurement of a corresponding discontinuity in phenomenal intensity.

The paper proceeds as follows. Section 2 situates the framework relative to IIT exclusion, overlapping-subject debates, dynamic-complex identity, general tie-breaking/choice theory, and recent topological approaches to consciousness. Section 3 defines the formal state and candidate spaces. Section 4 proves the local fixed-point necessity result. Section 5 develops the global monodromy obstruction and the selection–tracking distinction. Section 6 classifies repair strategies. Section 7 presents the official IIT 4.0 (2026) case study. Section 8 clarifies what the case study does and does not establish. Section 9 develops a nonexclusive landscape alternative, followed by discussion and limitations.

The intended claim is therefore modest but precise: a mathematically explicit theory of conscious subjects should distinguish the generation of candidate structures from their exclusive selection and from their diachronic tracking. Symmetry and topology impose different constraints on these operations, and making those constraints explicit reveals theoretical tradeoffs that are otherwise easy to hide inside a scalar maximization rule.

---

# 2. Related Work

## 2.1 Subject boundaries, overlap, and subject–subject parthood

Questions about the boundaries of conscious subjects predate the present formalism. In panpsychism and cosmopsychism, the combination and de-combination problems raise the possibility that subjects may stand in part–whole relations to other subjects. Miller explicitly formulates the de-combination problem in terms of subject–subject proper parthood and phenomenal unity [13]. Crummett develops the possibility that ordinary humans may contain multiple morally relevant conscious subjects, illustrating that multiplicity is not only a technical issue for information-theoretic theories [14].

Within IIT-focused philosophy, Blackmon argues that excluding overlapping conscious systems creates tension with intrinsicality: whether one candidate is conscious can depend on its relation to overlapping alternatives rather than only on its own intrinsic organization [4]. His proposed response is to permit overlapping conscious systems. This is directly relevant to the alternative considered in Section 9. The present paper does not claim that overlap is thereby metaphysically correct; instead, it treats nonexclusive representation as one possible response to an individuation obstruction.

These precedents show that "one organism, one subject" cannot simply be assumed as a mathematically innocent starting point. They do not, however, formulate the local-versus-global selection problem developed here.

---

## 2.2 IIT exclusion, non-uniqueness, and tie resolution

IIT 4.0 treats definiteness as an essential property of experience and implements it physically through exclusion: among overlapping candidate substrates, the theory identifies definite complexes using system integrated information and a tie-resolution procedure [1]. The 2026 intrinsic cause–effect-power refinement changes the system-level criterion by incorporating intrinsic differentiation and specification into \(ii(s)\), with

\[
\phi_s=\min\{\phi_c,\phi_e,ii(s)\},
\]

while maintaining the role of a definite substrate [2].

Several authors have already identified problems surrounding exclusion. Moon argues that the relation between the phenomenal exclusion axiom and the physical exclusion postulate is unclear and develops a quale-underdetermination problem [3]. Hanson and Walker show that the IIT 3.0 calculation can produce multiple formally valid values, including cases in which zero and positive integrated information are simultaneously admissible, undermining uniqueness unless further choices are imposed [5]. These are strong precedents for the general claim that IIT requires care about uniqueness.

The current paper differs in target. We are not re-deriving the Hanson–Walker non-uniqueness result, and we do not argue that the current IIT 4.0 algorithm is undefined. Instead, we ask what happens when the **current official exclusion rule is defined and deterministic but encounters a physically symmetric top candidate orbit**. The resulting question is about the regularity and ontology of a completed selection rule, not the existence of ambiguities left unspecified by an algorithm.

---

## 2.3 Overlapping competitors and dynamic complex identity

Cea, Negro, and Signorelli criticize IIT 4.0's ontology by considering overlapping candidate systems. In their worked example, the complex can switch between \(AB\) and \(AC\) after changes involving the overlapping alternative, even while the previously selected subsystem is held fixed in relevant respects [6]. This is a direct precedent for **complex replacement** and for the claim that exclusion has substantive ontological consequences.

Percy and Gómez-Emilsson move the discussion explicitly into time. They formulate a "dynamic entity evolution problem" for IIT: if the main complex moves through a biological neural network, the theory must reconcile changing physical boundaries with a coherent account of the evolving conscious entity [7]. Their analysis discusses movement, continuity, and possible splitting or bifurcation of complexes.

These works are the closest consciousness-specific predecessors to our diachronic motivation. The present framework adds a formal decomposition of the problem. We distinguish:

1. **local selection:** whether a candidate can be chosen at one symmetric state;
2. **global selection:** whether one branch can be chosen consistently across a region of state space;
3. **tracking:** whether a previously specified token can be followed along an actual history.

The distinction allows a theory to be locally well defined yet globally obstructed, or globally trackable after an initial choice while remaining unable to make that initial choice canonically.

---

## 2.4 Tie-breaking, continuous choice, and correspondences

The abstract symmetry problem is not unique to consciousness. In a 2026 arXiv preprint, Feys develops an axiomatic theory of tie-breaking in which the symmetric group acts on the input and proves that intrinsically symmetric situations obstruct anonymous strict tie-breaking; when partition-valued outputs are permitted, stabilizer orbits provide the canonical symmetric partition [9]. This result is close to the group-theoretic backbone of our local fixed-point and orbit-valued propositions. We therefore present those propositions as a specialization to subject individuation, not as a new theorem in tie-breaking theory.

Likewise, the regularity issues have classical precedents. Berge's maximum theorem provides a standard framework in which optimized values can be continuous while argmax sets are naturally set-valued and upper hemicontinuous [11]. Nishimura and Ok prove broad non-existence results for continuous single-valued choice functions and emphasize the alternative of multivalued choice correspondences [10].

These precedents motivate our use of correspondences rather than justify a priority claim. The consciousness-specific question is what each mathematical repair means ontologically: does a set-valued output represent several subjects, indeterminate subjecthood, an equivalence class, or merely an unresolved algorithmic state? Similarly, a randomized selector may preserve symmetry but changes the ontology from a definite subject to a probability law over subjects. Section 6 makes these commitments explicit.

---

## 2.5 Global topology, phenomenal unity, and mathematical consciousness

Mathematical consciousness research increasingly uses global structural tools. Lee-Youngzie, Tsuchiya, Robinson, Dietz, and Monti develop a category- and sheaf-theoretic framework for global phenomenal consciousness, using local-to-global structure to model relationships among narrow and broad qualia and conditions for phenomenal unity [8]. Their object of study is different from ours: they formalize the structure and unity of phenomenal qualities, whereas we formalize the selection and tracking of candidate subject tokens over **physical state space**.

The distinction matters. A global section in a sheaf of phenomenal data and a global section of a candidate-subject covering answer different questions. We cite this work to make clear that the use of global sections, sheaves, and local-to-global mathematics in consciousness research is not itself novel. Our proposed increment lies in applying local stabilizers, monodromy, and selection/tracking separation specifically to physical subject individuation.

The monodromy results themselves use standard covering-space mathematics [12]. Their significance is therefore application-level: they identify a way in which a subject-individuation rule can fail globally even in the absence of any local tie.

---


## 2.6 Recent structural accounts of subject individuation

The 2026 literature places additional pressure on any broad originality claim about subject individuation.

Sawyer develops a structural account of subjectivity in terms of **origin-tracking**: an organizational asymmetry by which a system distinguishes self-generated from externally generated events and maintains a privileged standpoint across perception and action [16]. This is directly relevant to our treatment of diachronic tracking. Our distinction is narrower: origin-tracking may supply a physical mechanism for persistence, whereas Proposition 4 asks a formal question about whether tracking a previously specified token can substitute for canonical selection of an initial token at a symmetric snapshot.

Hearst proposes a consciousness-first account in which subjects emerge as dynamically stable regimes satisfying an **Integration Dominance Criterion**, with persistence grounded in stability of constraint organization across time [17]. This is a close precedent for structural subject formation and diachronic persistence, though it does not formulate the local stabilizer/global monodromy selection problem developed here.

Kirsch's 2026 preprint is especially close to the local-symmetry component of our framework. It asks how candidate perspectival centers can be individuated by relational structure without primitive labels and uses automorphism-based interchangeability as the exact criterion of structural indiscernibility [18]. We therefore do not claim novelty for applying automorphism symmetry to candidate first-person centers. Our narrower contribution lies in connecting that local symmetry limit to a global monodromy condition, separating selection from tracking, and testing one repair class in a current IIT implementation.

Recent work also weakens any assumption that conscious subjects must come in one determinate whole-number decomposition. Schwitzgebel and Nelson argue that the number of conscious subjects may be non-integer or indeterminate in sufficiently complex or partially unified cases [19]. McIntyre defends a multiplicity hypothesis according to which a normal human brain may contain numerous conscious minds associated with proper parts of the brain [20]. These works reinforce the need to treat exclusivity and unique counting as substantive theoretical commitments rather than neutral defaults.

Taken together, these papers substantially narrow the originality claim of the present manuscript. The paper does not introduce the problem of subject individuation, symmetry-based indiscernibility, structural persistence, or multiplicity. Its target is the **combined selection-and-tracking architecture** and its local/global obstruction structure.


## 2.7 PyPhi and reproducible formal analysis

PyPhi is the principal open-source computational implementation of IIT and has long served as a reference toolbox for applying the formalism to finite discrete systems [15]. IIT 4.0 introduced a substantially updated formalism [1], and the 2026 intrinsic cause–effect-power work further modified the system-level criterion [2].

Because the present paper makes a theory-specific computational claim, reproducibility is essential. Our case study is not based solely on an independent reimplementation. It was recomputed using an unmodified official PyPhi checkout at a pinned source commit, exhaustively evaluating all seven nonempty subsystems of the three-node model and invoking the official complex search. Independent calculations were used as a cross-check rather than as the authority for the final values.

This matters because earlier exploratory calculations in this project produced values that were later corrected after the official implementation was audited. The manuscript therefore reports only the officially recomputed values and explicitly distinguishes IIT 4.0 (2023) from IIT 4.0 (2026).

---

## 2.8 Gap addressed by the present paper

The literatures above establish many components individually:

- subject overlap and subject–subject parthood [4,13,14];
- exclusion and non-uniqueness in IIT [3,5];
- ontological consequences of overlapping candidate competition [6];
- dynamic motion and bifurcation of IIT complexes [7];
- general symmetric tie-breaking impossibility [9];
- multivalued choice and continuity theory [10,11];
- local-to-global mathematics in consciousness studies [8].

The closest recent work now covers most ingredients separately: Kirsch applies automorphism symmetry directly to perspectival individuation [18]; Sawyer and Hearst develop structural accounts of subject persistence and formation [16,17]; Schwitzgebel–Nelson and McIntyre challenge simple unique-subject counting [19,20]; and Percy–Gómez-Emilsson analyze dynamic IIT complex identity [7].

What is not directly supplied by the literature identified in our search is the combined framework:

\[
\boxed{
\text{local stabilizer obstruction}
+
\text{global monodromy obstruction}
+
\text{selection/tracking separation}
+
\text{repair mapping}
}
\]

together with a directly recomputed current-IIT case study and a nonexclusive landscape contrast.

We therefore make a **formal synthesis claim**, not a claim that the underlying mathematics, the individuation problem, or any one component idea is unprecedented. The paper's intended contribution is to organize subject individuation into mathematically distinct operations and to show, in one current formal theory, how a specific exclusive repair behaves at a symmetry obstruction.

---

# 3. Formal Setup

## 3.1 The subject-individuation problem

A theory of consciousness may assign phenomenal significance to many physical processes while still requiring an additional rule that determines **which process, if any, constitutes a subject**. This creates an individuation problem that is logically distinct from the problem of assigning experiential structure to a physical process.

The present paper isolates this problem. We do not assume, in the formal results below, any particular theory of phenomenal quality, valence, selfhood, or metaphysical composition. We assume only that a theory supplies, at each physical state, a family of candidate subject-bearing processes or candidate exclusive subject assignments, together with whatever structure is required to compare or rank them.

Let

\[
X
\]

be a topological space of complete physical states at the descriptive scale relevant to the individuation rule. A point

\[
x\in X
\]

is intended to contain all physical information that the theory treats as relevant to **snapshot-based** subject individuation. If a theory requires additional information—such as physical history, causal lineage, or an external labeling convention—then that information must be represented explicitly by enlarging \(X\). This requirement will matter below when we distinguish selection from tracking.

For each \(x\in X\), let

\[
\mathcal C_x
\]

denote the nonempty family of candidate subject assignments available at \(x\). Depending on the theory, an element \(P\in\mathcal C_x\) may be:

1. a physical subsystem;
2. a process token;
3. a nonoverlapping family of processes;
4. a complex selected from overlapping candidate systems;
5. another explicitly specified object that the theory treats as a possible subject assignment.

We deliberately keep the definition generic. The central question is not initially what makes a candidate conscious, but what is required to **select and track** a subject once candidate assignments exist.

Throughout this paper, **selection is model-theoretic and ontological rather than epistemic**: it is the theory's own mapping from a physical state and its candidate assignments to the subject ontology that the theory says obtains. It is not an observer's act of guessing, measuring, or choosing among hypotheses.

Throughout this paper, **selection is model-theoretic and ontological rather than epistemic**. A selector is the theory's own mapping from a physical state and its candidate assignments to the subject ontology the theory says obtains. It is not an observer's act of guessing, measuring, or choosing among hypotheses.

---

## 3.2 Candidate bundles and local branch structure

It is useful to collect all candidate assignments into a total space

\[
E
=
\{(x,P): x\in X,\ P\in\mathcal C_x\}
\]

with projection

\[
\pi:E\to X,
\qquad
\pi(x,P)=x.
\]

The fiber

\[
E_x=\pi^{-1}(x)
\]

is the candidate family at \(x\).

The structure of \(\pi\) can be complicated in a general theory: candidates may appear, disappear, split, merge, or change scale. We therefore distinguish a **regular region**

\[
X^\circ\subseteq X
\]

on which candidate branches can be tracked locally without such singular changes.

### Regularity assumption

On \(X^\circ\), we assume that

\[
\pi^\circ:E^\circ\to X^\circ
\]

is a finite covering map, or equivalently for the finite-state applications considered here, that every \(x\in X^\circ\) has a neighborhood \(U\) over which the candidate family decomposes into finitely many continuously trackable local branches.

This assumption is not asserted as a universal fact about all possible physical subject theories. It is a modeling condition under which the local/global distinction can be stated cleanly. States at which the assumption fails—because of exact ties, branch creation, mergers, or other degeneracies—may be treated separately as a discriminant or singular locus.

---

## 3.3 Symmetry and physical objectivity

Let a group

\[
G
\]

act on the physical state space \(X\). The action is intended to represent transformations that preserve the intrinsic physical content relevant to the theory: for example, relabelings or genuine physical automorphisms.

Assume the action lifts to candidate assignments:

\[
g:(x,P)\mapsto(gx,gP),
\]

with

\[
\pi(gP)=g\pi(P).
\]

For a state \(x\), define its stabilizer

\[
G_x
=
\{g\in G:gx=x\}.
\]

The stabilizer contains the symmetries that leave the physical state itself unchanged while possibly permuting candidate assignments in the fiber \(E_x\).

### Physical automorphisms versus arbitrary labels

Throughout the paper, a transformation counts as a relevant symmetry only if it is an automorphism of the **complete physical description used by the individuation theory**. A mere change of notation should therefore act covariantly on both the state and its candidate descriptions, while a label that encodes genuine extra physical structure is not a removable symmetry.

This point blocks a common but uninformative escape from the fixed-point result. If a selector distinguishes two candidates by appealing to some additional physical feature, then that feature must be represented in the state space \(X\). The theorem can then be re-applied to the enlarged state. If, by contrast, the distinction is supplied only by node numbering, lexical order, memory address, or another representational convention, the resulting selector is not intrinsic to the symmetric physical state.

In the IIT case study below, this issue was checked computationally: all six permutations of the three node labels were run and mapped back to the original labels, yielding the same center complex family. Thus the symmetry used in the example is not an artifact of one arbitrary naming convention.

A snapshot subject selector is a section

\[
s:X\to E
\]

satisfying

\[
\pi\circ s=\operatorname{id}_X.
\]

A selector is **physically equivariant** if

\[
\boxed{
s(gx)=g\,s(x)
}
\tag{1}
\]

for every \(g\in G\) and every \(x\) in its domain.

Equation (1) formalizes a minimal objectivity condition: applying a physical symmetry or a merely representational relabeling should not create an intrinsically different subject assignment.

Nothing in (1) assumes that a unique subject must exist. Rather, it states what a unique selector would have to satisfy if one were claimed.

---

## 3.4 Scores and the top tier

Many theories rank candidate systems by a real-valued quantity. Let

\[
m(x,P)\in\mathbb R
\]

denote such a score when needed.

Define the top-tier correspondence

\[
T(x)
=
\operatorname*{arg\,max}_{P\in\mathcal C_x}
m(x,P).
\]

This generic score model is used only for the first stage of the abstract selection problem. It should not be confused with a claim that every complete theory is globally representable as maximization of one scalar. In particular, IIT's official exclusion rule is hierarchical: \(\phi_s\) determines tiers, Composition \(\Phi\) is used inside certain ties, and unresolved overlapping cliques can be rejected before the search continues at a lower \(\phi_s\) tier.

This generic score construction models only a ranking stage. It does not assume that a complete consciousness theory is globally reducible to maximization of one scalar. IIT, in particular, uses a hierarchical \(\phi_s\to\Phi\to\) exclusion-failure \(\to\) lower-tier cascade.

We assume that the score respects the same physical symmetries as the underlying theory:

\[
\boxed{
m(gx,gP)=m(x,P).
}
\tag{2}
\]

A **top-tier selector** satisfies

\[
s(x)\in T(x).
\]

The local impossibility result below does not require that the score be continuous. It requires only that, at the state under consideration, the relevant highest-ranked candidates form a symmetry orbit with no fixed member.

Continuity becomes important later when we ask how an individuation rule behaves under physical change.

---

## 3.5 Snapshot selection

We define the **selection problem** as follows:

> Given a complete current physical state \(x\), choose a subject assignment \(P\in\mathcal C_x\) on the basis of that current state alone.

A snapshot selector therefore represents a claim of **current-state supervenience**:

\[
x=x'
\quad\Longrightarrow\quad
s(x)=s(x').
\]

If the selector additionally uses an unrepresented historical path, an external coordinate system, or a labeling convention, then the actual domain of the selection rule is larger than \(X\). This point is conceptually important: a rule cannot simultaneously be described as snapshot-supervenient and depend on information not contained in the snapshot.

---

## 3.6 Diachronic tracking

The **tracking problem** is different.

Suppose we are given:

1. an initial state \(x_0\in X^\circ\);
2. a specified initial candidate token
   \[
   e_0\in E_{x_0};
   \]
3. an actual physical path
   \[
   \gamma:[0,1]\to X^\circ,
   \qquad
   \gamma(0)=x_0.
   \]

If \(\pi^\circ:E^\circ\to X^\circ\) is a covering, the path-lifting property gives a unique lifted path

\[
\widetilde\gamma:[0,1]\to E^\circ
\]

with

\[
\pi\circ\widetilde\gamma=\gamma
\]

and

\[
\widetilde\gamma(0)=e_0.
\]

Tracking therefore answers:

> Given a subject token already specified at the initial time, which later candidate branch is its continuation along this physical history?

Selection asks which token should be chosen at the initial state. Tracking assumes that initial choice has already been made.

This distinction will be central in Section 5.

---

## 3.7 Set-valued and probability-valued outputs

A theory need not return a single candidate.

A set-valued subject rule is a correspondence

\[
\Gamma:X\rightrightarrows E
\]

such that

\[
\Gamma(x)\subseteq E_x.
\]

A probability-valued rule assigns

\[
\mu_x\in\Delta(E_x),
\]

where \(\Delta(E_x)\) is the probability simplex over the finite fiber.

Equivariance generalizes naturally:

\[
\Gamma(gx)=g\,\Gamma(x)
\]

and

\[
\mu_{gx}=g_{*}\mu_x.
\]

These broader output types will provide two of the repair strategies in Section 6.

---

## 3.8 Scope of the formal results

The results in Sections 4–6 concern the logic of subject **individuation** under explicit assumptions. They do not establish that any candidate is phenomenally conscious, nor that one particular theory of consciousness is true.

Three layers must therefore remain distinct:

1. **mathematical structure:** symmetry, sections, coverings, monodromy, correspondences;
2. **theory-specific individuation:** how a theory defines candidate subjects and compares them;
3. **phenomenal interpretation:** what, if anything, those selected candidates mean for actual consciousness.

The paper's formal conclusions are strongest at the first two layers.

---

# 4. Local Symmetry Obstruction

## 4.1 The stabilizer problem

Consider a physical state

\[
x_0\in X
\]

with nontrivial stabilizer

\[
H=G_{x_0}.
\]

Because every \(h\in H\) satisfies

\[
hx_0=x_0,
\]

equivariance requires

\[
s(x_0)
=
s(hx_0)
=
h\,s(x_0).
\]

Thus any equivariantly selected candidate must itself be fixed by the stabilizer.

This yields the basic local obstruction.

---

## Proposition 1. Local Fixed-Point Necessity

Let \(x_0\in X\) and let

\[
H=G_{x_0}
\]

be its stabilizer. If a deterministic single-valued selector

\[
s:X\to E
\]

is \(G\)-equivariant, then

\[
\boxed{
s(x_0)\in\operatorname{Fix}_H(E_{x_0}),
}
\tag{3}
\]

where

\[
\operatorname{Fix}_H(E_{x_0})
=
\{P\in E_{x_0}:hP=P\ \forall h\in H\}.
\]

### Proof

For every \(h\in H\),

\[
hx_0=x_0.
\]

By equivariance,

\[
s(x_0)
=
s(hx_0)
=
h\,s(x_0).
\]

Therefore \(s(x_0)\) is fixed by every \(h\in H\), which gives (3).

\[
\Box
\]

---

## Corollary 1. Nonexistence on a non-fixed symmetry orbit

Suppose the admissible top tier at \(x_0\) is a single nontrivial \(H\)-orbit

\[
T(x_0)=\mathcal O
\]

with

\[
|\mathcal O|>1
\]

and

\[
\operatorname{Fix}_H(\mathcal O)=\varnothing.
\]

Then no deterministic single-valued selector can satisfy both:

\[
s(x_0)\in T(x_0)
\]

and equivariance.

### Proof

If such a selector existed, Proposition 1 would require

\[
s(x_0)\in\operatorname{Fix}_H(T(x_0)),
\]

but the latter set is empty.

\[
\Box
\]

---

## 4.2 Reflection example

The simplest example has two overlapping candidate systems \(P\) and \(Q\) and a reflection \(r\) satisfying

\[
rx_0=x_0,
\]

\[
rP=Q,
\qquad
rQ=P,
\qquad
P\neq Q.
\]

If

\[
T(x_0)=\{P,Q\},
\]

neither candidate is fixed by the reflection.

If one assumes

\[
s(x_0)=P,
\]

equivariance gives

\[
s(x_0)
=
s(rx_0)
=
r\,s(x_0)
=
Q,
\]

contradicting \(P\neq Q\).

The same argument excludes \(Q\).

The obstruction is therefore not numerical. It does not depend on how small or large the tied score is. It follows from the combination of:

1. exact physical symmetry;
2. a top tier exchanged by that symmetry;
3. deterministic single-valued selection;
4. equivariance.

---

## 4.3 Why labels do not solve the problem

A program can always implement a deterministic tie-breaker by choosing:

- the lexicographically first candidate;
- the candidate containing the lowest-indexed node;
- the candidate encountered first in memory;
- an arbitrary coordinate orientation.

Such a rule may be computationally useful. It is not an intrinsic resolution of the physical symmetry.

If relabeling the same physical state changes the output, then

\[
s(gx)\neq g\,s(x)
\]

for some symmetry \(g\).

The resulting selector is deterministic but not equivariant.

This distinction is essential. The local obstruction is not a claim that software cannot return one answer. It is a claim that no **physically objective** deterministic unique top-tier answer exists when the top orbit itself has no stabilizer-fixed member.

---

## 4.4 Relation to general tie-breaking results

The mathematical content of Proposition 1 is elementary and belongs to a broad family of symmetry-based impossibility results in canonicalization and tie-breaking [9]. Similar arguments appear whenever an intrinsically symmetric input is required to generate an anonymous or equivariant strict choice.

We therefore do not present Proposition 1 as a new result in group theory or social-choice mathematics.

Its role in this paper is narrower:

> to identify the exact local mathematical condition under which a theory of conscious-subject individuation cannot produce a unique objective snapshot subject while remaining faithful to a symmetry-related top tier.

The substantive contribution of the paper depends not on Proposition 1 alone, but on how this local obstruction interacts with diachronic tracking, global monodromy, repair strategies, and the IIT case study.

---

## 4.5 Top-tier set-valued completion

Corollary 1 blocks a single candidate, but not a set-valued output.

Suppose

\[
T(x_0)=\mathcal O
\]

is a finite transitive \(H\)-orbit.

---

## Proposition 2. Orbit-Valued Equivariant Completion

Let

\[
R\subseteq\mathcal O
\]

be nonempty and \(H\)-invariant:

\[
hR=R
\qquad
\forall h\in H.
\]

If \(H\) acts transitively on \(\mathcal O\), then

\[
\boxed{
R=\mathcal O.
}
\tag{4}
\]

### Proof

Choose any \(P\in R\). Invariance implies

\[
hP\in R
\]

for every \(h\in H\). By transitivity,

\[
H\cdot P=\mathcal O.
\]

Therefore

\[
\mathcal O\subseteq R.
\]

Since \(R\subseteq\mathcal O\), equality follows.

\[
\Box
\]

Equation (4) should not be interpreted as a new theorem in finite group theory. Its significance here is interpretive: once unique top-tier selection is blocked, the entire symmetry orbit is forced if the theory insists on a nonempty deterministic set-valued top-tier output that remains equivariant.

---

## 4.6 Local selection versus local continuity

The fixed-point obstruction is logically prior to continuity.

Allowing a selector to be discontinuous does not create a stabilizer-fixed top candidate where none exists. At \(x_0\), the selector still faces the same algebraic requirement

\[
s(x_0)=h\,s(x_0).
\]

Thus discontinuity is not, by itself, a repair of the local symmetry obstruction.

Instead, discontinuity typically appears as a **consequence** of a repair strategy. For example, a theory may preserve equivariant single-valuedness by descending to a lower symmetry-fixed candidate exactly at the tie. If nearby asymmetric states return to the higher orbit, the selected identity or selected score can then jump discontinuously.

This distinction will matter in the IIT case study.

---

# 5. Global Monodromy and Subject Tracking

## 5.1 Local regularity does not imply global selectability

The local symmetry obstruction concerns a single state with a nontrivial stabilizer. A different failure can occur even if every state along a path is locally regular and every small neighborhood admits a unique branch continuation.

Assume now that

\[
\pi:E^\circ\to X^\circ
\]

is a finite covering over a connected regular region \(X^\circ\).

Fix a base point

\[
x_0\in X^\circ
\]

and fiber

\[
F=E_{x_0}.
\]

Every loop

\[
\gamma:[0,1]\to X^\circ,
\qquad
\gamma(0)=\gamma(1)=x_0,
\]

lifts uniquely once an initial fiber element \(e\in F\) is specified. The endpoint of the lifted loop may differ from \(e\).

This defines the monodromy action

\[
\rho:
\pi_1(X^\circ,x_0)
\to
\operatorname{Sym}(F).
\]

The global obstruction arises when transport around a closed physical loop permutes candidate subject branches; the covering-space and monodromy machinery used here is standard topology [12].

---

## Proposition 3. Monodromy Fixed-Sheet Necessity

If

\[
s:X^\circ\to E^\circ
\]

is a continuous section, then the selected fiber element

\[
e_0=s(x_0)
\]

must be fixed by the monodromy action:

\[
\boxed{
\rho([\gamma])e_0=e_0
\quad
\forall[\gamma]\in\pi_1(X^\circ,x_0).
}
\tag{5}
\]

### Proof

For any loop \(\gamma\) based at \(x_0\), the curve

\[
s\circ\gamma
\]

is a lift of \(\gamma\) beginning at

\[
s(\gamma(0))=s(x_0)=e_0.
\]

Because \(\gamma(1)=x_0\) and \(s\) is single-valued,

\[
(s\circ\gamma)(1)
=
s(x_0)
=
e_0.
\]

By definition of monodromy, the endpoint of the lift beginning at \(e_0\) is

\[
\rho([\gamma])e_0.
\]

Therefore

\[
\rho([\gamma])e_0=e_0.
\]

\[
\Box
\]

---

## Corollary 2. Global no-section condition

If the monodromy action on \(F\) has no common fixed point,

\[
\bigcap_{[\gamma]\in\pi_1(X^\circ,x_0)}
\operatorname{Fix}(\rho([\gamma]))
=
\varnothing,
\]

then no continuous global section exists on that connected regular component.

This is a genuinely global obstruction: every sufficiently small neighborhood may admit perfectly regular local branches, yet no single branch can be chosen consistently over the whole region.

### Example: a two-sheet exchange with no local tie

The standard double cover of the circle gives a minimal explicit model. Let

\[
X^\circ=S^1,
\qquad
E^\circ=S^1,
\]

with covering map

\[
\pi(z)=z^2.
\]

Over the base point \(x_0=1\), the fiber contains two candidates,

\[
E_{x_0}=\{+1,-1\}.
\]

Consider the loop

\[
\gamma(t)=e^{2\pi i t},
\qquad
t\in[0,1].
\]

The lift beginning at \(+1\) is

\[
\widetilde\gamma_+(t)=e^{\pi i t},
\]

which ends at \(-1\). The lift beginning at \(-1\) ends at \(+1\). Thus the monodromy action is the transposition

\[
+1\leftrightarrow -1
\]
