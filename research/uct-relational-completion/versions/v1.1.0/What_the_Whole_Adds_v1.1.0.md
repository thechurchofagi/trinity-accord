---
title: "What the Whole Adds Without Erasing Its Parts"
subtitle: "Local Persistence, Overlap, and Relational Completion in Structural Accounts of Experience"
author: "Hongju Liu"
date: "12 October 2026 · UCT-RC-2026-01 · Version 1.1.0"
lang: en-US
fontsize: 11pt
papersize: a4
geometry:
  - top=24mm
  - bottom=24mm
  - left=25mm
  - right=25mm
mainfont: "Liberation Serif"
sansfont: "Liberation Sans"
monofont: "DejaVu Sans Mono"
colorlinks: true
linkcolor: black
urlcolor: black
header-includes:
  - |
    \usepackage{amsmath,amssymb,booktabs,longtable,array}
    \usepackage{fancyhdr,microtype,needspace,xurl}
    \urlstyle{same}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[L]{\small Local Persistence and Relational Completion}
    \fancyhead[R]{\small UCT-RC-2026-01}
    \fancyfoot[C]{\thepage}
    \setlength{\headheight}{14pt}
    \setlength{\emergencystretch}{3em}
    \setlength{\parskip}{4pt}
    \setlength{\parindent}{0pt}
    \clubpenalty=10000
    \widowpenalty=10000
    \displaywidowpenalty=10000
---

\begin{center}
Independent researcher, Shenzhen, China\\
English theoretical/computational preprint · Not peer reviewed\\
Final revised manuscript; DOI not assigned
\end{center}

# Abstract {.unnumbered}

What can a whole add while its constituent processes continue, and what evidence identifies that addition? We distinguish process persistence, complete structural preservation, and equality of a local observation. A finite overlap contract separates shared physical occurrences, admissibility of a joint description, and relations left undetermined by local descriptions. Exact overlap requires more than commuting maps. Under the explicitly assumed structural identity of Unified Consciousness Theory (UCT), grounded embeddings and their exact intersections transport coherently into experiential descriptions; this does not establish subjective unity. The main dynamical construction extends an explicitly credited parity-memory precedent to two overlapping, individually memoryful processes. With memoryless joint innovations, it gives a sharp interval of collective retention coefficients and a local-asymmetry bound on exponential correlation time. Two scope results substantially qualify that frontier. A lag-wise binary compatibility bound survives without Markov assumptions, whereas a fixed positive transition floor removes the unbounded-lifetime limit. More decisively, a fully positive hidden-mediator construction preserves both complete local trajectory laws and the entire observed one-step transition matrix, yet produces an arbitrarily slow collective correlation tail. A two-step semigroup defect distinguishes it from its memoryless observational twin. Fresh relation preparation also separates persistent background correlation from storage of a newly written bit. Matched-local-distribution preparations and marginal-preserving innovation interventions yield an explicit relation-sensitive test without treating a readout as experience. Exact rational verification accompanies all finite constructions. Classical completion, coupling, Markov projection, and common-drive ideas are credited. The contribution is a reproducible composition-and-inference contract with positive examples and explicit failure witnesses, not a new consciousness threshold or an empirical refutation of competing theories.

**Keywords:** consciousness; structural identity; process persistence; overlapping processes; composition; higher-order interaction; collective memory; hidden state; measurement resolution

# 1. The question is what changes, not which parts must disappear

Consider two active local processes that become involved in a larger organization. One possible account allows the local processes to remain experience-bearing while additional relations belong to the whole. Another selects a privileged overlapping substrate and does not independently attribute consciousness to the losing overlapping candidates. Before assessing either position, several questions must be distinguished. Did the local physical processes actually persist? Did their constitutive organizations remain unchanged? Did only their outputs, marginal distributions, or available measurements remain unchanged? Finally, what new structure, if any, was physically realized by the whole?

These questions cannot be answered merely by increasing a system's size, observing more successful computation, or drawing a boundary around a collection of objects. Nor does a more permissive attribution of experience automatically explain combination better. An account that permits local and whole experience must still explain their structural relationship and identify what is absent from an independent collection of the parts.

UCT I version 1.2 already provides a conditional non-summative result for constituents in **nonoverlapping** slots: under a strong structural–experiential identity commitment, a physical whole that is not the declared independent product of its constituents cannot have an experiential organization equal to that same product [1, §6]. The paper explicitly does not establish general gluing of overlapping processes. That omitted case matters. Neural, bodily, distributed, and temporally extended processes can share occurrences, boundary events, and causal routes. Treating all parts as disjoint copies would alter the system being explained.

This paper develops the omitted case in a controlled finite setting. The central proposal is **relational completion**: preserve the actual identification and continuing organization of the parts while separately specifying the relations that connect them into the particular whole. The proposal has three layers: an occurrence-level account of overlap, an admissibility and completion problem, and a conditional transport into experiential organization. It is supplemented by a dynamical example in which a physically implementable joint relation introduces collective memory without requiring cessation of every local process.

The central quantitative results are the attainable frontier in Section 7.5, its hidden-mediator counterlimit in Section 7.8, and the preparation/intervention protocol in Sections 8.4–8.5. These belong to one question: what must be retained or controlled before a relationship can be attributed to the target whole?

The result is deliberately narrower than a universal theory of phenomenal binding. The formal models do not select which real neural relations are constitutive of a given feeling. They do make that explanatory obligation more definite: a claim about a whole must name the missing relationship, the evidence that establishes it, and the reason it belongs to the target process rather than only to a measuring or reporting apparatus.

# 2. Starting commitments, predecessors, and method

## 2.1 What is inherited from UCT

UCT I distinguishes an actual physical process token, a finite scientific view, an estimate of that view, and a numerically individuated subject. Its core commitment, C1, identifies the complete token-relative physical organization with intrinsic experiential organization under a declared common structural signature [1, §§2–4]. We write the supplied isomorphism as

\[
h_P:D(P)\overset{\cong}{\longrightarrow}\Phi(P).
\]

C1 is a consciousness-specific identity commitment, not a conclusion of the present calculations. Together with the process ontology it entails nonempty experience for an actual valid process, U1. P3 states that embedding does not itself terminate a continuing actual process. Neither U1 nor P3 says that the local experience keeps the same content after coupling, or that every experience-bearing process is an independently reportable person.

The current research context also includes a distinction between concurrent local bearer-centred routes and their actual joint use by a downstream process [2]. Another result shows that manipulating a grounded organizational coordinate need not identify the particular phenomenal target intended by an investigator [3]. These restrictions remain in force. A new coupling variable cannot become a measure of felt ownership simply by being named one.

This paper's diagrams are an application of C1, not an amendment of it. Where full physical embeddings or complete constitutive signatures are unavailable, the resulting claims concern a declared finite model only. The distinction is important because a local model with boundary ports is not automatically an induced substructure of a whole that has replaced those ports with internal mechanisms.

## 2.2 Relevant external precedents

The possibility of nested minds and the distinct question of their individuation have explicit philosophical precedents. McIntyre's 2026 argument for multiplicity is especially close to the motivating issue, but the present work does not adopt its conclusion about ordinary brains as an empirical finding [4]. IIT 4.0 provides its own definite account of maximal substrates and relations within a complex [5,6]. Its composition rule must not be confused with a blanket ban on every kind of overlap. Current comparisons must also acknowledge subsequent work on intrinsic cause–effect power and causal grain [7,8]. No IIT score is calculated here.

Category-theoretic and compositional approaches to experience are established [9]. Lee-Youngzie and colleagues connect intra-phenomenal part–whole descriptions to empirical inter-phenomenal qualia measures using a presheaf and propose testable conditions for their relationship [10]. Their approach expressly distinguishes functional binding from phenomenal binding. The present problem differs: it asks what **physical and observational descriptions** must contain before a local-to-global inference is licensed. It does not refute their phenomenological hypothesis by substituting arbitrary physical variables for qualia.

The mathematics of compatible local data, global sections, and their obstructions also has extensive precedent, including the treatment of contextuality by Abramsky and Brandenburger [11]. Higher-order dependence not recoverable from lower-order marginals is classical [12]. Information-theoretic causal-emergence research already studies dynamical relationships between parts and macroscopic features [13]. In particular, Example 1 of Rosas et al. is exactly the single-parity transition family used in Section 7.1 below, after the parameter conversion \(\theta=2\gamma_{\mathrm{Rosas}}-1\). The kernel, its collective memory, and the absence of individual predictive power are inherited, not new results. Section 7.5 instead develops a specific overlapping, locally memoryful extension and its sharp completion/lifetime frontier. Its probability bounds are classical binary coupling bounds, not a newly invented probability theorem [16]. A recent synergistic self-knowledge proposal directly applies joint information to consciousness [14]. This paper neither invents those ideas nor makes synergy a sufficient condition for experience.

The distinction between a Markov process and its projections is also classical [17], as is the ability of a common drive to organize collective dynamics [18]. The hidden-state construction below is a specific audit witness, not a discovery that latent processes exist or that noise can coordinate systems. It retains exactly the local patch laws and observed one-step matrix at issue, making the additional closure premise testable in this example.

## 2.3 Contribution and review scope

The reusable increment is a composition-and-inference contract, not a collection of new names for established mathematics. RC1–RC2 apply elementary finite completion and temporal closure. RC3 applies standard transport of structure, with an explicit exact-intersection condition. RC4 is inherited from Rosas et al.; RC5 is an elementary observation calculation for that control. RC6 gives the explicit locally memoryful overlap construction and its sharp frontier. The revision adds RC7–RC10: a model-robust lag constraint, a quantitative positivity qualification, a hidden-mediator counterexample with a detectable semigroup defect, and a matched-marginal test on the main overlap model.

| Result group | Reusable content | Status |
|:--|:--|:--|
| RC1–RC3 | Grounded overlap, completion, and conditional structural transport | Classical methods; scoped UCT application; exact-overlap premise clarified |
| RC4–RC5 | Single-parity control and its observation channel | Exact precedent credited; elementary derived consequences |
| RC6–RC8 | Fixed local laws, attainable relational lifetime, and robustness limits | Classical coupling; explicit application and scope extension |
| RC9 | Positive hidden-state twin with equal observed one-step law but different long-time relation | Explicit counterexample constructed here; priority unverified |
| RC10 | Matched-local preparation, readout, and marginal-preserving coupling intervention | Model-specific causal test; not an experiential bridge |

The exact hidden-state witness and matched-local protocol strengthen the original application rather than form a separate paper. None establishes that an observed memory variable is a subject, or that an admitted process has a particular feeling. Global priority for the integrated construction is not certified.

The review cutoff is 12 October 2026. Source checking prioritized original articles, author manuscripts, and the project's pinned source passages. Restricted or failed access is recorded in the source ledger; the review is targeted rather than systematic. A further recent holonomy/sheaf preprint surfaced in discovery but its original text could not be retrieved, so no substantive claim of priority over that work is made. All mathematics needed for the stated results is proved in this manuscript; independent global-priority and peer-review assessments are not asserted. Existing mathematical techniques, the exact single-parity kernel of Rosas et al., and classical feasible-coupling bounds are not priority claims.

The companion program performs finite verification, not an experiment on people or language models. A proposed empirical application appears in Section 10 and is not reported as executed.

# 3. Three levels of preservation

Let a local process \(P\) be compared before and after an alteration of its environment or its involvement in a larger process \(W\). Distinguish

\[
\begin{aligned}
\text{P:}&\quad\text{the actual process and its lineage continue;}\\
\text{S:}&\quad D(P_{\mathrm{before}})\cong D(P_{\mathrm{after}});\\
\text{V:}&\quad \Pi_vD(P_{\mathrm{before}})=\Pi_vD(P_{\mathrm{after}}).
\end{aligned}
\]

Here \(\Pi_v\) is a declared observation or abstraction. P does not imply S: a continuing process may change. V does not imply S: a finite view may discard relevant distinctions. S does not establish numerical identity or continuing lineage: separately realized duplicates may share a structural type. Thus these statements should not be arranged as a simple hierarchy of increasingly strong identity claims.

Under C1 and U1, P preserves the attribution of **some** experiential organization to the continuing valid token. S supports equality of complete structural type in experiential description. V alone does neither job. This distinction is the first safeguard against a superficially attractive anti-exclusion argument that holds only reports fixed and then asserts complete intrinsic sameness.

A particularly useful comparison is an open module whose internal update law remains fixed while its input sources or output destinations change. Fixed module law does not mean fixed complete local organization. The actual boundary inputs, current state, and constitutive dispositions may have changed. What is preserved has to be specified at the appropriate level.

The same qualification protects empirical research from an opposite mistake. Failure to measure a complete organization need not preclude identifying a specific relationship. A coarse measurement can retain one targeted feature while losing most details. Section 8 characterizes this possibility exactly for the circuit family, rather than equating scientific usefulness with complete reconstruction of a brain.

# 4. Occurrences, overlapping descriptions, and relational completion

## 4.1 Grounded carrier and admissible relation atoms

Fix a finite set \(U\) of labelled actual-event referents in a declared model. The labels serve to identify occurrences, not to establish their existence. Let \(\mathcal K\) be a finite, typed relational signature. Operations may be represented by their graphs, but corresponding totality, functionality, temporal, and boundary requirements must then be retained as constraints.

Let \(\Omega\) be the allowed relation atoms of this signature over \(U\). An atom consists of a relation symbol and an appropriately typed tuple. Its **support** is the set of occurrences appearing in that tuple. A whole description is initially an assignment

\[
w:\Omega\longrightarrow\{0,1\}.
\]

A physically motivated model class \(\mathcal W\subseteq\{0,1\}^{\Omega}\) may exclude assignments inconsistent with chronology, functional mechanisms, boundary conditions, or other constraints. The unrestricted Boolean class is a counting device, not a claim that every assignment is physically realizable.

A collection \(\mathcal C=\{U_i\}\) covers the carrier: \(\bigcup_iU_i=U\). The members may overlap. Define

\[
\Omega_i=\{\omega\in\Omega:\operatorname{supp}(\omega)\subseteq U_i\},
\qquad
K_{\mathcal C}=\bigcup_i\Omega_i.
\]

A patch description \(d_i\) gives the value of **every** atom in \(\Omega_i\), including absences. If a measurement reports only positive edges or only selected relations, it defines a smaller information set and must not be treated as a full induced restriction.

This setup separates two kinds of coverage. Covering every occurrence does not necessarily cover every relation among occurrences. A tuple whose support straddles patches may remain unspecified even when all events are locally represented.

## 4.2 Theorem RC1: exact finite completion

Suppose local descriptions agree wherever they report the same atom. Then they determine a unique assignment \(d\) on \(K_{\mathcal C}\). In the unrestricted class,

\[
\left|\{w:w|_{\Omega_i}=d_i\ \text{for every }i\}\right|
=2^{|\Omega\setminus K_{\mathcal C}|}.
\tag{1}
\]

If they disagree on a shared atom, there is no completion. Consequently, compatible local descriptions determine every unrestricted global relation assignment exactly if and only if \(K_{\mathcal C}=\Omega\).

**Proof.** Agreement makes the union of the local functions well defined. Every remaining atom can independently take either value and no covered atom can change, yielding (1). A conflicting shared value cannot be the restriction of one function. If an atom is uncovered, two assignments differing only at that atom have identical restrictions; conversely, full atom coverage determines the assignment. \(\square\)

For a constrained model class the correct set is instead

\[
\operatorname{Comp}_{\mathcal W}(d)
=\{w\in\mathcal W:w|_{K_{\mathcal C}}=d\}.
\tag{2}
\]

It may be empty, a singleton, or have several members. Constraints can force an uncovered value; they can also invalidate an otherwise compatible family. Equation (1) must not be used after imposing dependencies between the free atoms. A constrained upper bound remains \(|\operatorname{Comp}_{\mathcal W}(d)|\leq2^{|\Omega\setminus K_{\mathcal C}|}\).

A useful corollary is a **scope threshold**, not an instrumentation prescription. If every permitted relation has support size at most \(r\), then observing complete induced restrictions on every subset of size at most \(r\) determines the unrestricted relational description. Observing all smaller subsets need not determine a genuine \(r\)-supported atom. Hidden mediator variables can change the required support size by changing the model; they cannot be silently omitted.

## 4.3 What overlap does and does not supply

Let \(U_1=\{a,b,c\}\) and \(U_2=\{b,c,d\}\). Identifying the same occurrences \(b,c\) gives a four-event carrier. A disjoint sum of the two descriptions has six events and describes a different object. Equality of recorded values for two separately realized copies, \(b_1\) and \(b_2\), does not identify them as the same event.

Nevertheless, the correct four-event union may still leave relations between \(a\) and \(d\) unspecified. Overlap prevents double counting; it does not automatically determine all crossing relations. Conversely, an additional labelled relation between two duplicated copies does not make them one occurrence. Actual overlap and communication between distinct events are different physical facts.

In a feature-binding analogy, knowing which colors and which shapes occur need not specify which color belongs to which shape. Retaining grounded common object or event references can determine the pairing. This illustrates a relational data requirement, not an experimentally established theory of color experience. In particular, the phenomenal appearance of a color can depend on context; a fixed color label is not a certificate that its complete experience is unchanged.

# 5. Temporal admissibility: a worked non-Boolean constraint

The unrestricted counting result is intentionally simple. A temporal-order specialization shows why a physical constraint cannot be omitted.

Let each local description give an induced strict partial order on its event set. Collect all locally asserted ordered pairs in \(P_+\), and all locally asserted absences of an ordered pair in \(P_-\). Let \(P_+^{+}\) denote transitive closure. Event referents and their overlap are already fixed.

**Theorem RC2 (temporal completion).** A global strict partial order extending the local descriptions exists if and only if

\[
P_+^{+}\cap\{(u,u):u\in U\}=\varnothing,
\qquad
P_+^{+}\cap P_-=\varnothing.
\tag{3}
\]

When (3) holds, \(P_+^{+}\) is the unique least completion under relation inclusion.

**Proof.** Every transitive extension contains the closure. A diagonal pair violates irreflexivity, and a pair in \(P_-\) contradicts an induced local absence, proving necessity. Conversely, an irreflexive transitive closure disjoint from all forbidden pairs is itself a strict partial order matching every recorded local pair. Every other completion contains it. \(\square\)

The least completion need not be the only completion or the actual one. Global causal histories may include further order relations. To test uniqueness, add each still-unassigned ordered pair in turn and recompute closure. A second completion exists exactly when at least one such addition remains irreflexive and avoids \(P_-\). Necessity follows by taking a new pair from any larger completion; sufficiency follows by using the valid enlarged closure.

Three pairwise descriptions can agree on all shared single events and nevertheless assert \(a\prec b\), \(b\prec c\), and \(c\prec a\). No temporal whole has those restrictions. Another family asserts \(a\prec b\), \(b\prec c\), and explicitly no order between \(a,c\). It has no directed cycle in the asserted edges, but closure violates a negative local fact. Thus cycle checking alone is insufficient when restrictions include absences.

These are failures of a proposed **description**, not proof that a real brain has no unified experience. Genuine restrictions of one actual temporal history already satisfy its global constraints. Incompatible estimates can arise from wrong referent matches, unsynchronized observation, omitted conditions, or a wrong model class. The explanatory task is to diagnose that mismatch rather than to infer phenomenal extinction from it.

A simple positive case is the path \(a\prec b\prec c\), represented by the overlapping histories \(\{a,b\}\) and \(\{b,c\}\). Because the middle event is the same occurrence, their closure supplies the longer temporal relation \(a\prec c\). Replacing it by unrelated same-valued copies \(b_1,b_2\) removes that argument. The whole description contains a traceable path relation, not a new substance obtained by adding two minds. Taking transitive closure does not physically install a new causal edge: it recovers a relation already implied by the specified path. Logical completion of a description and physical formation of a new coupling are different operations; the circuit comparisons below concern the latter only insofar as their declared mechanisms are actually realized.

# 6. Conditional experiential inheritance without disjoint copying

## 6.1 The physical embedding contract

Suppose \(P_i\) and \(W\) are actual valid tokens, and an independently grounded diagram of constitutive structures includes embeddings

\[
e_i:D(P_i)\hookrightarrow D(W).
\]

For every declared shared constituent structure \(D(O_{ij})\), assume maps \(a_{ij,i}\) and \(a_{ij,j}\) satisfy

\[
e_i a_{ij,i}=e_j a_{ij,j}.
\tag{4}
\]

Commutation is only an agreement condition. To preserve the **exact** declared overlap, additionally require equality of carrier intersections:

\[
e_i[D(P_i)]\cap e_j[D(P_j)]
=e_i a_{ij,i}[D(O_{ij})].
\tag{5}
\]

This is the finite embedding version of an exact intersection, or pullback, condition. Without it, two individually injective maps may identify an undeclared extra pair: let \(P=\{a,b\}\), \(Q=\{b,c\}\), with declared overlap \(\{b\}\), and map \(a,c\) both to 0 and \(b\) to 1. The maps commute on \(b\), but wrongly identify the distinct events \(a,c\). Correct occurrence grounding must exclude this example.

An intersection is not automatically an actual experience-bearing process. If \(O_{ij}\) is only an interface substructure, it is transported as an interface image; C1 and U1 are not applied to it as though it were an independently admitted token. The notation \(\Phi(O_{ij})\) below is used only when that additional token premise holds.

The diagram may be restricted to a declared constitutive sub-signature. In that case only that sub-signature is transported; a result about its images must not be promoted to a statement about all qualitative content. In particular, a boundary-conditioned local causal repertoire is not automatically embedded in an unconditioned global repertoire. One must justify the arrow, not only the inclusion of node names.

## 6.2 Theorem RC3: coherent transport

Assume C1 for the actual tokens and their relevant shared structures. Define

\[
f_i=h_W e_i h_i^{-1},
\qquad
b_{ij,i}=h_i a_{ij,i}h_{O_{ij}}^{-1}.
\tag{6}
\]

Then the transported maps are embeddings of the same declared structural kind, and

\[
f_i b_{ij,i}=f_j b_{ij,j}.
\tag{7}
\]

Thus identifying shared physical occurrences is compatible with retaining the local experiential descriptions in a coherent part–whole diagram. The construction does not require disjoint copying of a shared occurrence or deletion of a local carrier.

**Proof.** Composition with isomorphisms preserves the embedding property. Substituting (6), both sides of (7) reduce to \(h_W e_i a_{ij,i}h_{O_{ij}}^{-1}\), using (4). The same cancellation shows that every commuting relation in the grounded physical diagram remains commuting after transport. \(\square\)

If the physical exact-intersection condition (5) also holds, the corresponding experiential image intersection is exact:

\[
f_i[\Phi(P_i)]\cap f_j[\Phi(P_j)]
=f_i b_{ij,i}[\Phi(O_{ij})].
\tag{8}
\]

Indeed, both sides are the image under the bijection \(h_W\) of the corresponding sides of (5). With an interface-only overlap, the right-hand side is instead the transported interface image. Without (5), RC3 proves coherent agreement, not the absence of accidental extra identifications. This distinction strengthens the overlap contract; it does not add a consciousness axiom.

Different choices of tokenwise isomorphisms do not create incompatible diagram types. If \(h'_P\) is another family, write \(\alpha_P=h'_Ph_P^{-1}\). Then \(f'_i\alpha_i=\alpha_W f_i\). The two descriptions are related by a coherent family of relabelings. This is a standard transport-of-structure argument; its role is to prevent arbitrary independent coordinates from being mistaken for different part–whole organizations.

The theorem does **not** show that independently measured local and global phenomenological data admit these maps. That would require an empirical bridge. Nor does equality of images in \(\Phi(W)\) identify the local tokens as numerically one subject. The conclusion concerns a structural diagram, not a count of experiencers.

## 6.3 Relational surplus and no erasure by construction

Call a global relation atom a **cover-relative relational surplus** when it is present in \(D(W)\) but not supplied by any embedded local description. The term means surplus relative to the declared cover, not surplus over physics. It is not a scalar consciousness measure. Adding a mediator to the cover or retaining a previously discarded interface may eliminate the reconstruction gap without changing the actual system.

Under RC3, an actual surplus atom is present in experiential description with the same structural role and remains outside the corresponding union of local images. In a finite common-signature comparison, adding such atoms while preserving the carrier and all local atoms changes the relation interpretation; it cannot be explained as deleting a constituent to make room for a whole. If the addition increases the number of tuples of a relation, the resulting structure is not isomorphic to the uncompleted union. This comparison object need not itself be an actual token.

Combine this with P3 and U1: **where the local processes actually persist, their experiential attribution remains; where an actual constitutive relationship is added to a whole, C1 retains that relationship in the whole's experiential organization.** This is a conditional account of coexistence and structural contribution. The persistence conclusion is inherited; the present addition spells out how overlap and missing relations are handled without using a disjoint product.

It remains possible that a physically larger system fails to form the particular human-like integrated subject of interest. The diagram alone neither proves nor requires otherwise. “More global relations” is not an experience ignition threshold, and “more experiences allowed” is not a measure of theoretical success.

# 7. A constructive whole-level relation: distributed temporal memory

The preceding account would be weak if the additional relation remained unnamed. We therefore give a circuit-level example in which the whole contributes a precise capability: memory of a joint bit. It illustrates organization, not consciousness.

## 7.1 The transition family

Let \(X_t\in\{0,1\}^n\), with \(n\geq2\), and define the signed parity

\[
\chi(x)=(-1)^{x_1+\cdots+x_n}.
\]

For \(-1\leq\theta\leq1\), take the time-homogeneous Markov kernel

\[
K_\theta(y\mid x)=2^{-n}\bigl[1+\theta\chi(x)\chi(y)\bigr].
\tag{9}
\]

The kernel is nonnegative, row-stochastic, and column-stochastic. The uniform state distribution is stationary. For \(|\theta|<1\), all transitions have positive probability; the construction does not require a disconnected state space. At \(\theta=1\), parity is conserved; at \(\theta=-1\), it alternates; at \(\theta=0\), the next full state is independent uniform noise.

Equation (9) has a direct Boolean stochastic realization. Generate \(n-1\) independent fair bits \(R_1,\ldots,R_{n-1}\), and an independent bit \(B\) with \(\Pr(B=1)=(1-\theta)/2\). Set

\[
Y_i=R_i\ (i<n),\qquad
Y_n=\bigoplus_{i=1}^nX_i\ \oplus\!\bigoplus_{i=1}^{n-1}R_i\ \oplus B.
\tag{10}
\]

XOR gates and delayed registers realize the declared stochastic computation. Intermediate gates and noise sources are part of a physical implementation; (9) is an effective register-level description. No hardware construction is claimed by running the verifier. This exact register-level kernel is the parity-preservation example of Rosas et al. [13], here reparameterized and explicitly realized for use as a control.

For fixed \(x,y\), the required random bits and final noise value give probability (9). This independently checks that the proposed joint distribution is not an inconsistent collection of marginal rules.

## 7.2 Proposition RC4: inherited parity example and explicit consequences

For every proper coordinate subset \(J\subsetneq\{1,\ldots,n\}\), every \(x\), and every \(y_J\),

\[
\Pr_\theta(Y_J=y_J\mid X=x)=2^{-|J|}.
\tag{11}
\]

Consequently, under a uniform initial state, the trajectory of any one fixed proper patch is independent uniform at all sampled times for every \(\theta\). Nonetheless,

\[
\mathbb E[\chi(X_{t+k})\mid X_t=x]=\theta^k\chi(x),
\qquad
K_\theta^k=K_{\theta^k}.
\tag{12}
\]

**Proof.** In marginalizing (9), summation over any missing output bit cancels the parity term, giving (11). Since this conditional distribution is independent of the complete preceding state, it is independent of the preceding history; induction gives the proper-patch trajectory assertion. For (12), the matrix has the decomposition

\[
K_\theta=\frac{\mathbf1\mathbf1^{\mathsf T}}{2^n}
+\theta\frac{\boldsymbol\chi\boldsymbol\chi^{\mathsf T}}{2^n}.
\]

The two displayed matrices are orthogonal rank-one projections, since \(\sum_x\chi(x)=0\) and \(\sum_x\chi(x)^2=2^n\). Raising the matrix to the \(k\)-th power gives (12). \(\square\)

Let \(Z_t=\chi(X_t)\). In stationarity this is a uniform binary Markov chain with flip probability \((1-\theta)/2\). Its temporal information is

\[
I(Z_t;Z_{t+k})
=1-h_2\!\left(\frac{1-\theta^k}{2}\right),
\tag{13}
\]

where \(h_2\) is binary entropy. For example, at \(\theta=3/4\) the one-step information is approximately \(0.4564\) bits, while every fixed proper-patch time series has zero temporal mutual information. This numerical value is an illustrative consequence of the model, not an observed biological effect.

The one-dimensional whole-level mode is dynamically meaningful: opposite initial parities induce different future parity distributions whenever \(\theta\neq0\). It is not made into a new causal force; it is realized by (10). It also is not an arbitrary difference of notation. The nontrivial eigenvalue is \(\theta\), so kernels with different \(\theta\) cannot be related by a simultaneous permutation of input and output state labels.

## 7.3 Preserving rich local activity

The fair register marginals do not require the entire local system to have no memory. Append a local state \(S_i\) with any fixed transition kernel \(L_i(s'_i\mid s_i)\), and take

\[
\widetilde K_\theta(s',y\mid s,x)
=\prod_iL_i(s'_i\mid s_i)K_\theta(y\mid x).
\tag{14}
\]

Every proper collection of the extended modules has the same marginal transition law for all \(\theta\); their local \(S_i\) processes can retain arbitrary modelled state. Meanwhile, the collective register mode changes as before. The verifier checks a persistent-copy example, \(S_i(t+1)=S_i(t)\), not arbitrary biological richness.

A connected implementation can read persistent local registers without rewriting them, while the coupling circuitry has its own changing relations. This illustrates how ongoing local computation and additional joint memory can coexist. It does not prove that the complete physical organization of each extended module, including its boundary relations, stays identical as \(\theta\) changes. An actual implementation must separately establish which tokens persist and which relationships are constitutive of each token.

## 7.4 Why this is not hidden irreducibility in a complete micro-model

Conditional output independence would imply

\[
K(y\mid x)=\prod_iK_i(y_i\mid x).
\]

If all singleton kernels are those in (11), that product is the uniform kernel \(K_0\). Thus nonzero \(\theta\) is incompatible with independent output mechanisms **at the register-level description used in (9)**. The joint mechanism, shared innovations, or omitted intermediates have to be represented.

This is a safeguard, not a defect to conceal. A causally complete circuit expanded to include its intermediate variables can have ordinary independent exogenous noises. After marginalizing those variables, its coarse outputs need not be conditionally independent. No irreducible physical magic or violation of classical computation is required. Conversely, feeding (9) directly into an IIT implementation that requires a product of node transition probabilities would discard the very relation under study. Any IIT comparison must use a suitably justified expanded system and the appropriate state, grain, background, and partition rules.

Higher-order information and dynamically meaningful macrovariables have clear predecessors [12,13]. The use here is not to introduce another information-based consciousness criterion. It supplies an explicit **constitutive candidate relation** that a structural account must either retain, justify excluding from the token, or admit it has not measured.


## 7.5 An overlapping extension with persistent local memory

The inherited example deliberately makes every proper patch memoryless. A closer realization of the motivating problem should preserve nonzero local temporal organization and specify a shared physical occurrence, rather than merely add an unrelated memory register. The following three-register extension does that at the level of complete marginal process laws.

For \(x=(x_1,x_2,x_3)\), define

\[
S(x)=(-1)^{x_1+x_2},\quad
T(x)=(-1)^{x_2+x_3},\quad
R(x)=S(x)T(x)=(-1)^{x_1+x_3}.
\tag{15}
\]

The two declared patches are \(P=\{1,2\}\) and \(Q=\{2,3\}\). They share the same second register and its update occurrence. Their relational modes are \(S\) and \(T\); the cross-patch relation \(R\) is supported on the two outer registers and is not contained in either patch alone. This is a **cover-relative**, not an irreducible three-body, distinction: an instrument reading registers 1 and 3 directly can observe \(R\). An invertible change to coordinates \((S,T,X_2)\) also does not establish that all three physical registers are a minimal or unique experiential carrier. For \(\alpha,\beta\in[-1,1]\), consider the kernel

\[
L_{\alpha,\beta,\gamma}(y\mid x)=\frac18
\left[1+\alpha S(x)S(y)+\beta T(x)T(y)+\gamma R(x)R(y)\right].
\tag{16}
\]

**Theorem RC6 (overlap-compatible memory frontier).** Within (16):

(a) The kernel is stochastic if and only if

\[
-1+|\alpha+\beta|\ \leq\ \gamma\ \leq\ 1-|\alpha-\beta|.
\tag{17}
\]

(b) Every allowed value of \(\gamma\) has the same full local transition laws on \(P\) and \(Q\). Their marginal laws depend respectively only on \(\alpha\) and \(\beta\), and each local process is Markov with that transition even when the full state is known. With the same initial local distribution, the complete sampled local trajectory law is consequently unchanged by varying \(\gamma\).

(c) Under the uniform stationary law,

\[
\mathbb E[S_{t+k}\mid X_t]=\alpha^k S_t,\quad
\mathbb E[T_{t+k}\mid X_t]=\beta^k T_t,\quad
\mathbb E[R_{t+k}\mid X_t]=\gamma^k R_t.
\tag{18}
\]

For \(0\leq\alpha,\beta\leq1\), the largest attainable absolute retention coefficient of \(R\) is exactly \(1-|\alpha-\beta|\). If \(\alpha\ne\beta\) and \(|\alpha-\beta|<1\), the e-folding correlation time satisfies the sharp bound

\[
\tau_R:=\frac{-1}{\log|\gamma|}
\ \leq\ \frac{-1}{\log(1-|\alpha-\beta|)}.
\tag{19}
\]

Here \(\tau_R=0\) when \(\gamma=0\), and \(\tau_R=\infty\) when \(|\gamma|=1\). If \(|\alpha-\beta|=1\), only \(\gamma=0\) is possible. If \(\alpha=\beta=r\in(0,1)\), no finite upper bound on \(\tau_R\) follows from the two fixed local laws, even when every entry of the whole kernel is required to be strictly positive.

**Proof.** For fixed \(x,y\), put \(u=S(x)S(y)\) and \(v=T(x)T(y)\). Then \(R(x)R(y)=uv\), and all four sign pairs \((u,v)\) occur. Nonnegativity of the four quantities \(1+\alpha u+\beta v+\gamma uv\) is equivalent to (17); summing the nonconstant characters over \(y\) gives row sums one. Uniform stationarity follows similarly from column sums. This is the classical feasible-coupling interval for two binary innovations with means \(\alpha,\beta\), here applied to overlapping temporal modes.

Summing over \(y_3\) cancels the \(T\) and \(R\) terms, leaving

\[
\Pr(Y_1=y_1,Y_2=y_2\mid X=x)
=\frac14[1+\alpha S(x)S(y)].
\tag{20}
\]

The right side depends on \(x\) only through its \(P\)-coordinates. The analogous formula for \(Q\) uses \(\beta\). The Markov property and induction establish the whole local trajectory statement. It remains a *marginal* statement: synchronized joint records from the two patches still determine the full register state.

The four characters \(1,S,T,R\) are mutually orthogonal on the eight states. Their normalized outer products give (16), with eigenvalues \(1,\alpha,\beta,\gamma\), and the other four eigenvalues zero. Thus \(L^k=L_{\alpha^k,\beta^k,\gamma^k}\) for integer \(k\geq1\), yielding (18). For nonnegative \(\alpha,\beta\), direct comparison of the two endpoints in (17) gives \(\max |\gamma|=1-|\alpha-\beta|\), which is attained. Monotonicity of \(-1/\log r\) for \(0<r<1\) proves (19). When \(\alpha=\beta=r\in(0,1)\), choose \(\gamma=1-\epsilon\) with \(0<\epsilon<2(1-r)\) and sufficiently small \(\epsilon\). All four sign probabilities are positive, while \(\tau_R\to\infty\) as \(\epsilon\downarrow0\). The local timescales remain fixed. \(\square\)

An explicit circuit realizes the entire interval. Draw a sign pair \((U,V)\) with

\[
\Pr(U=u,V=v)=\frac14(1+\alpha u+\beta v+\gamma uv),
\tag{21}
\]

independently at each update, and an independent fair shared bit \(G\). Set \(Y_2=G\). Choose \(Y_1\) so that \(S(Y)=S(X)U\), and choose \(Y_3\) so that \(T(Y)=T(X)V\). Given these signs and \(G\), the output state is unique. Circuit enumeration therefore gives exactly (16). The joint innovation generator, its shared bit, gates, and delays must be included in a full physical description. Keeping its two marginal innovation laws unchanged while changing their coupling is not proof that the full boundary-sensitive local organizations or local experiences remain unchanged.

For \(\alpha=\beta=1/2\), all \(0\leq\gamma\leq1\) are allowed. Both patch modes keep exactly the same retention \(1/2\). With independent innovations, \(\gamma=\alpha\beta=1/4\); the cross-patch relation decays faster. With perfectly coordinated innovations, \(\gamma=1\); \(R\) is preserved although both local modes continue to flip. Full-support choices \(\gamma=0.9,0.99,0.999\) give relational correlation times approximately \(9.49,99.50,999.50\) updates while both local correlation times stay \(1.44\) updates. These are computed properties of the stipulated circuit, not estimates of biological memory or experiential duration.

This is a positive description of the surplus: the whole can maintain a relation between two overlapping local modes while both local processes remain active and retain their fixed local process laws. It does not require a new elementary carrier or the deletion of the old carriers. Its underdetermination is also bounded: unequal local retention restricts how long this particular relational mode can persist. For example, \(\alpha=3/4,\beta=1/4\) implies \(|\gamma|\leq1/2\), so \(\tau_R\leq1/\log2\). The result is confined to the declared binary, stationary, character-diagonal family; it is not a universal upper bound on memory in every overlapping system.

Even coarse measurements may constrain this example. If independently calibrated local retention estimates have absolute errors bounded by \(\delta_\alpha,\delta_\beta\), then

\[
d=\max\{0,|\widehat\alpha-\widehat\beta|-\delta_\alpha-\delta_\beta\}
\]

is a lower bound on local asymmetry. Under the assumptions above, \(|\gamma|\leq1-d\). A positive \(d<1\) therefore provides an upper bound on this collective correlation time without uniquely reconstructing the whole. If \(d=0\), the same data give no finite uniform upper bound. This is conditional error propagation, not a claim that current neural measurements satisfy the model.

The specific extension should not be mislabelled. Classical binary coupling determines the interval, and diagonalization determines the lifetimes. The application-level increment is the explicit combination of a grounded overlapping carrier, fixed *nonzero* local process memories, an attainable whole-level completion interval, and a sharp limit that disappears at local symmetry. Whether this integration has an exact prior treatment outside the reviewed literature remains an open priority question. It does not revise the established attribution of the single-parity example to Rosas et al.



## 7.6 What remains true without a Markov model

The single-coefficient lifetime in RC6 depends on a closed, time-homogeneous register model with fresh, state-independent innovation pairs. A weaker relation constraint requires none of those assumptions.

For any jointly defined sign processes \(S_t,T_t\in\{-1,1\}\), put \(R_t=S_tT_t\). For one fixed pair of times \(t,t+k\), define the raw sign-product moments

\[
A_k=\mathbb E[S_tS_{t+k}],\quad
B_k=\mathbb E[T_tT_{t+k}],\quad
C_k=\mathbb E[R_tR_{t+k}].
\]

These are normalized autocorrelations only when the relevant signs are unbiased. Otherwise they are raw moments, and a nonzero limit need not represent retained information about fluctuations.

**Proposition RC7 (model-independent, lag-wise compatibility).** For each such pair of times,

\[
-1+|A_k+B_k|\ \leq\ C_k\ \leq\ 1-|A_k-B_k|.
\tag{22}
\]

**Proof.** The signs \(U=S_tS_{t+k}\) and \(V=T_tT_{t+k}\) have means \(A_k,B_k\) and product mean \(C_k\). Their four probabilities are \((1+A_ku+B_kv+C_kuv)/4\). Their nonnegativity gives (22), exactly as in the elementary binary coupling argument in RC6. Conversely, every triple satisfying these inequalities defines a valid distribution for this one pair of signs. \(\square\)

The result does not require stationarity, independent increments, or a Markovian joint process. It is sharp **at one lag**; it does not assert that arbitrary choices within the intervals at every lag admit a single consistent trajectory law. When the two local chains retain the laws of RC6, \(A_k=\alpha^k\) and \(B_k=\beta^k\), but (22) alone does not imply \(C_k=\gamma^k\), or the envelope \(|C_k|\leq(1-|\alpha-\beta|)^k\). Section 7.8 gives an explicit failure of that extrapolation while preserving the complete local process laws.

## 7.7 Strict positivity is not a fixed robustness margin

Every member of a sequence can have positive transition probabilities while its smallest probability approaches zero. Consequently, the unbounded-lifetime statement in RC6 is not an assertion of robustness to a fixed amount of process noise.

**Proposition RC8 (uniform transition-floor frontier).** Fix \(0\leq\rho<1\) and require \(L_{\alpha,\beta,\gamma}(y\mid x)\geq\rho/8\) for all \(x,y\). Writing \(z=1-\rho\), this holds exactly when

\[
-z+|\alpha+\beta|\ \leq\gamma\leq\ z-|\alpha-\beta|.
\tag{23}
\]

For feasible nonnegative \(\alpha,\beta\), the largest \(|\gamma|\) is \(z-|\alpha-\beta|\). Thus a fixed \(\rho>0\) restores a finite maximal exponential correlation time even when \(\alpha=\beta\).

**Proof.** Subtract \(\rho/8\) from the four distinct entries in (16). Their nonnegativity is equivalent to \(z+\alpha u+\beta v+\gamma uv\geq0\) for all signs \(u,v\), giving (23). The endpoint comparison for nonnegative local coefficients is the same as in RC6. Equivalently, the kernel contains a fixed uniform reset component \(\rho\), with the remaining stochastic component weighted by \(z\). \(\square\)

For equal local retention \(1/2\), taking \(\gamma\uparrow1\) necessarily sends the admissible floor to zero. This qualification separates an exact mathematical possibility from a robust implementation claim. The floor is a condition on the **process transition law**, not the noise of a sensor; no thermodynamic law or universal physical noise floor is assumed.

## 7.8 A positive hidden-mediator twin defeats the unrestricted lifetime inference

A more serious question is whether correctly recording the complete one-step transition table is enough to justify the closed Markov model. It is not. The following fully positive construction keeps the same overlapping carrier and local trajectory laws, and has an exactly matching observed one-step table, but a different long-time relational mode.

**Proposition RC9 (hidden-mediator scope witness).** Let

\[
\alpha=\frac34,\qquad \beta=\frac14,\qquad
q=\frac14,\qquad d=\frac15,\qquad \frac12\leq\lambda<1.
\]

Add one explicitly represented mediator sign \(H_t\) to the three-register state, with transition probability \(\Pr(H_{t+1}=h'\mid H_t=h)=(1+\lambda hh')/2\). In the circuit of (21), replace the state-independent coupling coefficient by

\[
c(x,h)=q+d\,hR(x).
\tag{24}
\]

Given the current state, update the registers and mediator using independent fresh randomness, with kernel

\[
\mathcal T((y,h')\mid(x,h))
=L_{\alpha,\beta,c(x,h)}(y\mid x)\,
\frac{1+\lambda hh'}2.
\tag{25}
\]

Then all 256 entries of this 16-state transition matrix are positive. Both declared patches retain exactly the transition and trajectory laws from RC6. A stationary law is

\[
\pi(x,h)=\frac{1+\mu R(x)h}{16},\qquad
\mu=\frac{d\lambda}{1-q\lambda}.
\tag{26}
\]

The register vector alone is uniform under this law. Its complete stationary **observational** one-step conditional table is exactly

\[
\Pr(X_{t+1}=y\mid X_t=x)
=L_{\alpha,\beta,\gamma_{\rm eff}}(y\mid x),\qquad
\gamma_{\rm eff}=q+d\mu.
\tag{27}
\]

Nevertheless, its stationary collective autocorrelation is

\[
C_k=w\lambda^k+(1-w)q^k,\qquad
w=\frac{d\mu}{\lambda-q},\qquad 0<w<1.
\tag{28}
\]

Every apparent table in (27) has entries at least \(59/2400\), a fixed positive bound independent of \(\lambda\). Nevertheless, the actual correlation is not \(\gamma_{\rm eff}^{\,k}\). In particular, the two-step defect is

\[
C_2-C_1^2=d\mu(\lambda-\gamma_{\rm eff})>0.
\tag{29}
\]

As \(\lambda\uparrow1\), the slow-mode weight tends to \(16/225\), not zero. The tail time \(-1/\log\lambda\) and integrated autocorrelation time

\[
\mathcal T_R=1+2\sum_{k\geq1}C_k
=1+2\left[(1-w)\frac{q}{1-q}
+w\frac{\lambda}{1-\lambda}\right]
\tag{30}
\]

both diverge, despite the fixed unequal local retentions.

**Proof.** Here \(c\) is either \(1/20\) or \(9/20\), strictly inside the feasible interval \([0,1/2]\) for the stipulated \(\alpha,\beta\). Every register output and every mediator transition therefore has positive probability. Marginalizing a register row over the other outer register cancels its \(c\)-dependent term, leaving (20) independently of \(h\). Thus the two local patches remain Markov under every full-state history, with their original laws.

The conditional moment recursions are

\[
\mathbb E[R_{t+1}\mid X_t,H_t]=qR_t+dH_t,\qquad
\mathbb E[H_{t+1}\mid H_t]=\lambda H_t.
\]

For the candidate stationary law, \(\mathbb E[R_tH_t]=\mu\). Independence of the two fresh updates conditional on the current state gives the stationarity equation \(\mu=\lambda(q\mu+d)\), solved by (26). Direct substitution verifies the full law: the fresh middle bit is uniform, and all sign moments other than the constant and \(RH\) vanish. Given \(X_t=x\), (26) gives \(\mathbb E[H_t\mid x]=\mu R(x)\); averaging (24) therefore gives \(\gamma_{\rm eff}\), proving (27).

Iterating the conditional recursions yields

\[
\mathbb E[R_{t+k}\mid X_t,H_t]
=q^kR_t+d\,\frac{\lambda^k-q^k}{\lambda-q}H_t.
\]

Multiplication by \(R_t\) and stationary averaging give (28). The stated range of \(\lambda\) and fixed \(q,d\) ensure \(0<w<1\). Subtracting the square of \(C_1=q+d\mu\) gives (29). Summing the two geometric series gives (30); \(w\to d^2/(1-q)^2=16/225\) proves divergence. \(\square\)

| Mediator retention \(\lambda\) | \(C_8\) | Slow-tail time | Integrated autocorrelation time |
|---:|---:|---:|---:|
| 0.90 | 0.030777 | 9.491 | 2.905 |
| 0.99 | 0.065635 | 99.499 | 15.700 |
| 0.999 | 0.070558 | 999.500 | 143.699 |

The falsely extrapolated asymmetry envelope at lag eight would be \((1-|3/4-1/4|)^8=1/256\), approximately 0.003906. All three examples exceed it. They continue to satisfy the genuinely model-independent bound (22). A tail time, an integrated autocorrelation time, and the first crossing of the level \(1/e\) are different quantities; the table does not identify them. In particular, a slow tail of modest amplitude need not delay the first \(1/e\) crossing.

The apparent-table floor follows from \(\gamma_{\rm eff}<91/300\) and the four possible row entries. It cannot be used in RC8 to bound this hidden process: the apparent table is not its closed transition kernel. The full 16-state minimum instead approaches zero as \(\lambda\uparrow1\) and the mediator becomes persistent.

**Freshly written information is a separate test.** Prepare \(R_0=r\) with otherwise uniform register states and independently distributed fair \(H_0\). The same recursion now gives \(\mathbb E[R_k\mid\text{this preparation}]=q^kr\), not the slow mixture (28). The natural stationary tail partly reflects a prior relation to the mediator; it does not by itself demonstrate storage of a newly written bit in the observed registers. Writing the mediator as part of the preparation would be a different protocol and a different declared carrier.

The matching table is observational, not equality of all intervention responses. Resetting the visible register vector independently of the mediator already changes the one-step comparison; such an intervention must not be relabelled as passive conditioning.

This counterexample does not contradict RC6, because \(X_t\) alone is not a closed Markov state in (25). It shows why a correct stationary **observational one-step** table cannot discharge that premise. It also does not prove that all memory comes from a hidden mediator. The operational alternatives are to identify and control the relevant mediator, test longer-time closure, or report only the lag-wise bound. The comparison is between explicit organizations, not between a measured system and an unexplained mathematical residual.

# 8. When a coarse measurement can detect the whole-level relation

## 8.1 Exact observation-channel criterion

Let \(W(o\mid y)\) be a known observation channel. Define

\[
a_o=2^{-n}\sum_yW(o\mid y),\qquad
b_o=2^{-n}\sum_y\chi(y)W(o\mid y).
\]

Then after \(k\geq1\) updates from prepared state \(x\),

\[
\Pr_\theta(O=o\mid x,k)=a_o+\theta^k\chi(x)b_o.
\tag{31}
\]

**Theorem RC5 (target-sensitive resolution).** For a known initial parity, known channel, and one-step observation distributions, \(\theta\) is identifiable in the family (9) exactly when some \(b_o\neq0\). At a fixed lag \(k\), observations identify \(\theta^k\) under the same condition; this need not identify \(\theta\).

**Proof.** Substitute (12) into the observation channel. If all \(b_o\) vanish, the resulting distribution is constant in the parameter. Otherwise any one nonzero coefficient gives a linear inverse for \(\theta^k\), and \(k=1\) gives \(\theta\). \(\square\)

A channel reporting only a proper coordinate subset has \(b_o=0\) for every output. A single parity detector has nonzero coefficients and suffices. Total active-bit count also retains parity because its evenness determines \(\chi\); it is not invisible in this example. This differs from the permutation-network example in the precursor note [15], where total count was invariant under rewiring. Whether a coarse statistic helps is target-dependent.

At even lags, \(\theta\) and \(-\theta\) are exactly aliased. At \(|\theta|<1\), the signal decreases with lag. A very precise instrument with an unsuitable temporal schedule can therefore fail to distinguish different organizations. More decimal places do not undo an exact zero in the observation operator.

For a deterministic binary reader \(f:\{0,1\}^n\to\{0,1\}\), invisibility is equivalent to selecting equally many even- and odd-parity states into \(f^{-1}(1)\). Consequently, of the \(2^{2^n}\) binary readers, exactly

\[
\sum_{j=0}^{2^{n-1}}\binom{2^{n-1}}j^2
=\binom{2^n}{2^{n-1}}
\tag{32}
\]

are invisible. This is a combinatorial classification of this family, not the probability that a real instrument misses consciousness.

## 8.2 Noise, calibration, and precision

If each output bit is independently flipped with known probability \(\eta_i\), the observed signed parity has conditional mean

\[
\mathbb E[\widetilde Z_{t+k}\mid X_t=x]
=\chi(x)\theta^k\prod_i(1-2\eta_i).
\tag{33}
\]

Independent bit-flip noise is a specific error model. Correlated errors, drifting clocks, biased selection, and wrong event matching require different analyses. If one \(\eta_i=1/2\), this readout destroys the mode exactly; increasing repetition does not restore it under the same channel.

Let the calibrated mean for each of two candidate parameters have an additional unknown error bounded in absolute value by \(\epsilon\). Their possible mean intervals are disjoint exactly when

\[
|\theta_1^k-\theta_0^k|\left|\prod_i(1-2\eta_i)\right|>2\epsilon.
\tag{34}
\]

This is a worst-case mean-uncertainty condition, not a single-trial discrimination claim. Independent sampling error can be reduced by repetition; a systematic bound need not shrink. Instrument calibration must justify the stated bound.

Equations (31)–(34) separate three remedies: retain the correct joint mode, sample at a distinguishing time, and reduce the relevant error. Only the last is conventional numerical precision. None requires reconstructing every state or causal detail of a human brain.

## 8.3 The synchronized-record qualification

“All proper local laws coincide” does not mean that all simultaneously retained local data fail. If a collection of proper patches covers every coordinate **in the same trial and time step**, retaining their raw aligned records reconstructs the full vector. The parity can then be calculated. For instance, the pairs \((X_1,X_2)\), \((X_2,X_3)\), and \((X_1,X_3)\) jointly reveal a triple when their shared occurrences are identified.

Separate marginal tables discard that joint matching. Arbitrarily accurate marginal estimates cannot recreate it without an additional model. Local recording devices with synchronized trials can therefore recover the collective relation; independently tabulated local distributions need not. This is a distinction between restricting an actual assignment and marginalizing a probability law, not a claim against local physical measurement or classical process tomography.


## 8.4 The observation contract for the main overlapping model

RC5 concerns the inherited single-parity control, not automatically every collective mode. For the overlapping family (16), define \(b_o^S=8^{-1}\sum_yS(y)W(o\mid y)\), and similarly \(b_o^T,b_o^R\), with \(a_o=8^{-1}\sum_yW(o\mid y)\). For integer \(k\geq1\),

\[
\Pr(O=o\mid X_0=x)
=a_o+\alpha^kS(x)b_o^S+\beta^kT(x)b_o^T
+\gamma^kR(x)b_o^R.
\tag{35}
\]

When \(\alpha,\beta\) are fixed and known, the \(\gamma^k\) term is identifiable exactly when some \(b_o^R\ne0\). Unknown local coefficients can be nuisance parameters; a preparation contrast removes them in this model rather than silently assuming them known.

**Proposition RC10 (matched-local preparation and relation-sensitive test).** Let \(M_r\), for \(r\in\{-1,1\}\), prepare a uniform state from the four states with \(R(x)=r\):

\[
M_r(x)=\frac14\,\mathbf1\{R(x)=r\}.
\tag{36}
\]

The two preparations have the same full distributions on each declared local patch \(P,Q\), and under every fixed \(L_{\alpha,\beta,\gamma}\) they induce the same complete trajectory law for each patch separately. Their observation laws satisfy

\[
\Pr(O=o\mid M_r,k)=a_o+r\gamma^k b_o^R.
\tag{37}
\]

A noiseless outer-pair reader consequently obeys

\[
\mathbb E[R_k\mid M_+]-\mathbb E[R_k\mid M_-]=2\gamma^k.
\tag{38}
\]

**Proof.** Under either preparation, \(X_2\) is fair and independent of the fair outer bit used to select \(X_1,X_3\). Each pair \((X_1,X_2)\) and \((X_2,X_3)\) is therefore uniform. The local Markov law proved in RC6 extends this equality to every sampled local trajectory. Also \(\mathbb E_{M_r}S=\mathbb E_{M_r}T=0\) and \(\mathbb E_{M_r}R=r\). Averaging (35) gives (37), and reading \(R\) gives (38). \(\square\)

If a balanced input bit is encoded by these two preparations and only \(R_k\) is read, the optimal decoding success in this stipulated channel is \((1+|\gamma|^k)/2\). The whole therefore has an explicitly writable and readable relation in the closed model, not merely a stationary correlation. The shared preparation mechanism must be recorded and disconnected afterward; no claim of an uncaused nonlocal preparation is made.

A reader of \(P\) alone or \(Q\) alone has \(b_o^R=0\); reading the outer pair can suffice. This is different from RC4, where every proper coordinate subset misses the global parity. Independently flipping outer readout bits with known error probabilities multiplies the signed relation by \((1-2\eta_1)(1-2\eta_3)\); noise on the middle readout bit does not enter this particular \(R\). The noise and even-lag qualifications of Section 8.2 apply to this **declared** mode, not indiscriminately to every coordinate.

## 8.5 Changing the relation without changing the marginal innovation laws

A second controlled comparison changes the joint generator rather than the initial relation. In (21), retain the distribution of \(U\), but replace \(V\) by an independently drawn sign with its original mean \(\beta\). The new joint law is

\[
\Pr(U=u)\Pr(V=v)
=\frac14(1+\alpha u+\beta v+\alpha\beta uv).
\tag{39}
\]

Thus this replacement sends \(\gamma\) to \(\alpha\beta\), while leaving the complete trajectory law of each local patch unchanged, for matched initial local distributions. With the preparations of RC10 and a readout that does not feed back, the resulting contrast changes from \(2\gamma^k\) to \(2(\alpha\beta)^k\). For \(\alpha=\beta=1/2\), \(\gamma=0.9\), and \(k=4\), the contrasts are 1.3122 and 0.0078125 respectively. These are differences of two sign means, whose allowed range is \([-2,2]\), not probabilities.

This is a physical mechanism intervention when the generator is implemented as specified; randomly re-pairing data **after** an experiment only changes an analysis. Nor does the intervention preserve the actual realized local trajectories or the complete boundary-sensitive local organizations. It preserves their stipulated marginal probability laws. The ordinary correlated-innovation mechanism and an actual information consumer, if present, must remain inside the declared implementation record.

The combined protocol therefore asks three separate questions. Do matched preparations produce the predicted one-step relation contrast? Does it propagate across multiple lags as the closed model predicts? Does a generator-side marginal-preserving replacement change that propagation while a disconnected readout leaves it unchanged? RC9 supplies a concrete alternative when the second answer fails. Passing these tests identifies the stated computational relation within the model and intervention scope; it does not by itself decide whether the relation belongs to a particular phenomenal token or corresponds to felt unity.

# 9. What the construction establishes about combination

## 9.1 A positive, conditional explanatory step

The joint temporal mode answers one concrete version of “what does the whole add?” It adds a relation between a present configuration and later configurations that is absent from the proper-patch marginal dynamics. The circuit makes the mechanism explicit, and the observation-channel criterion says how to detect it. Equation (14) shows a simple independent-factor extension; RC6 supplies the closer overlapping case with fixed nonzero local process memories and a sharp attainable lifetime frontier. The inherited single-parity kernel is a control, not the claimed new contribution.

Under C1, an independently established complete constitutive structure retains its relations in experiential description. Under P3 and U1, continued local tokens are not deleted by their participation in a larger actual token. RC3 joins these inherited commitments to a coherent overlap diagram rather than a disjoint sum. This is a constructive account of **relational organization without obligatory local erasure**.

The claim is not that a parity bit feels like bodily ownership, that any correlated network is a person, or that an experimenter creates a new experience by computing a statistic. An actual register-level implementation and its constitutive relations must be identified; a variable chosen only for analysis is not automatically another actual process. The examples describe a possible structural contribution and the conditions for transporting it, not a universal semantic dictionary from logic gates to feelings.

The hidden-mediator witness adds an equally important lesson: "the whole" cannot be equated with the visible register boundary merely because all visible one-step transitions have been recorded. A relation can partly track a continuing process outside that boundary. Conversely, the closed generator and matched-preparation example shows how a relation can carry a newly written bit through the specified implementation. These are different organizational explanations; neither is licensed by a long correlation curve alone.

## 9.2 Where the disagreement with exclusion remains

IIT may accept all of the physical calculations and still require its maximal-substrate selection before assigning consciousness. UCT instead applies its basal identity commitment to admitted actual tokens, including continuing local processes. The empirical status of that disagreement is not settled by (9), especially because the effective kernel must be expanded before applying a conditionally independent node formalism.

The present advance is therefore not a refutation of IIT. It makes the nonexclusive alternative less promissory by specifying how overlap, local continuation, and new global relations can be jointly represented. Whether that is a better theory of experience depends on independent support for its premises and on particular empirical bridges, not on permissiveness alone.

Nor is IIT the only relevant comparison. A sheaf-based phenomenological model can impose a carefully specified local-to-global relation without being committed to a physical exclusion rule. Its empirical restriction maps have to be evaluated on the appropriate phenomenal data. RC1 and RC4 show why arbitrary agreement of **physical summaries** is insufficient to infer its hypotheses, not why its hypotheses must be false.

## 9.3 Four errors excluded together

The first error is **erasure by mere embedding**: cancellation of local experiential attribution without a corresponding premise that the local token has ceased or that an independently defended exclusion rule applies. The second is **combination by duplication**: treating one shared occurrence as two independent copies. The third is **combination by omission**: assuming compatible local descriptions fix all crossing relations. The fourth is **phenomenology by statistic**: identifying a successful readout or an information value with the intended feeling without an independently supported bridge.

Avoiding all four is more demanding than avoiding any one. The overlap contract, constrained-completion theorem, circuit, and observational criterion are intended to be used together.

# 10. Thought experiments and a bounded empirical route

## 10.1 Gradually coupled processes

Keep two local causal lineages active and progressively change their physically realized interface. Track token persistence separately from complete structural invariance and from measurement invariance. The organizational hypothesis concerns the formation of specified crossing relations; UCT's experience-existence attribution is not switched on at a coupling threshold.

The decisive question is not whether the coupled whole is “more conscious” on an unspecified scale. It is which relationships changed, which continuing local processes they involve, and what further premises support a particular experiential interpretation. A stronger whole need not be introduced by turning the continuing parts into nonentities.

## 10.2 Shared relay versus copied relay

Compare \(a\to b\to c\) with \(a\to b_1\) and \(b_2\to c\), where \(b_1,b_2\) display the same values but are separately realized. Local recordings can look similar. The occurrence and intervention structure differs. An intervention affecting the first relay need not affect the second in the copied case. This distinguishes actual joining from coincident values, while leaving any experiential claim conditional on the physical and semantic premises.

## 10.3 A slow distributed memory

Uniformly slow an implemented version of (10), including its noise generation and boundary interactions, while preserving a declared correspondence of operations. An observer may fail because no relevant transition falls within the window, or because only even logical lags are sampled. Neither result shows the absence of an underlying organizational distinction. Conversely, arbitrary time rescaling in a mathematical model does not establish equivalent physical organization if environmental effects or constitutive timescales change.

## 10.4 Persistent processors in a joint computation

Let continuing local processors carry out their own stateful activities while an explicit interface establishes an additional joint memory or comparison. The construction (14) supplies a finite analogue. Local activity and collective capability coexist. This does not establish that the encompassing process has one human-like subject, and increased task performance does not establish maximal integrated information.

## 10.5 From model to actual evidence

A first implementable study should now center on (16), using (10) as a credited control: archive the joint generator, prepared inputs, intermediate variables, complete synchronized outputs, and readout calibration. Preregister the matched-patch preparations, several odd and even lags, the closed-model semigroup predictions, and the generator-side independent replacement in Sections 8.4–8.5. Include (25) as an explicit hidden-memory alternative. This would validate an implementation and its observation model, not a consciousness theory. The present study executes their finite mathematical verifiers, not physical hardware.

For human work, the target must be independently specified, for example a declared relational aspect of perceived feature binding or bodily ownership. One would need paired local and global phenomenal measures, a candidate mechanism that predicts their relationship, and a credible control for attention, report formation, common input, and changes in the target itself. Preserving trial alignment is important; pooling local summaries before testing the proposed relation may destroy the contrast.

Existing aggregate behavioural curves cannot automatically supply this experiment. A better fit to a noisy ownership response is not evidence that a specific whole-level constitutive relation has been identified. Nor should the experiment be added merely to obtain a new report endpoint after a known identification failure [3]. The role of the present result is to specify what relation-sensitive data and physical scope would be required. It does not announce a completed empirical bridge or an observational prediction unique to UCT.

## 10.6 Two apparently identical boxes and a hidden relay

Present an investigator with a closed three-register box and the hidden-mediator box of RC9. Under stationarity they match on all visible one-step transition probabilities and on the complete separate histories of the two local patches. A stationary conditional one-step survey, even covering every visible starting state, does not locate the memory. This is not a claim that all one-step interventions are indistinguishable. A two-step relation check distinguishes the boxes in this construction; an independently prepared relation also separates their responses. The point is not that an inaccessible variable must always exist, but that a proposed state boundary carries a falsifiable closure commitment.

This sharpens the "instrument sees one point" thought experiment. The missing information need not be spatial resolution: even a full visible-state one-step table can omit temporal organization. Keeping grounded joint timing and checking the consequences of an actual intervention can add information that arbitrarily precise single-step summaries cannot.

# 11. Verification results

The three standard-library verification programs use exact rational arithmetic for transition probabilities, matrix products, marginals, and circuit enumeration. Entropy and displayed logarithmic times are floating-point evaluations only; transition probabilities, stationary laws, moment identities, and defect checks use exact rational arithmetic. General claims rest on the written proofs; enumerations are consistency checks, not proofs by unlimited extrapolation.

## 11.1 Relational and temporal checks

For unordered binary and ternary candidate relation atoms, the verifier exhausts all 16 whole descriptions on three events across 109 covers, and all 1,024 whole descriptions on four events across the 361 covers containing at most three patches. Direct restriction groups reproduce the completion counts in RC1, covering 125,553 local-data fibers. This does not enumerate all possible typed signatures.

All 27 complete pair-patch temporal families on three events contain 19 admissible orders and 8 rejected families. On four events, all 729 pair-patch families contain 219 admissible orders and 510 rejected families. The criterion in (3) agrees with direct enumeration. For the overlapping cover \(\{a,b,c\},\{b,c,d\}\), 121 compatible local-order pairs have 42 one-completion, 60 two-completion, and 19 three-completion cases. Least-completion existence and the uniqueness test agree in all cases.

Independent local and whole relabelings are checked in 864 overlap-transport fixtures. The shared two-event overlap remains shared; it is not counted as four different occurrences.

## 11.2 Dynamical and readout checks

| Units | States | Proper-patch distributions | Circuit rows | Matrix-power comparisons |
|---:|---:|---:|---:|---:|
| 2 | 4 | 56 | 28 | 28 |
| 3 | 8 | 336 | 56 | 28 |
| 4 | 16 | 1,568 | 112 | 28 |
| 5 | 32 | 6,720 | 224 | 28 |

Each row uses seven parameters: \(-1,-3/4,-1/2,0,1/2,3/4,1\). Ordinary matrix multiplication is compared with (12) through lag four, and circuit rows are independently generated from (10). An explicit three-time example sums 512 microscopic trajectories into 64 equal-probability proper-patch trajectories. A persistent local-state extension passes 1,152 proper-patch checks. All 124 binary states for sizes two through six are reconstructed from aligned leave-one-out records.

| Units | Binary readers | Invisible readers | Visible readers |
|---:|---:|---:|---:|
| 2 | 16 | 6 | 10 |
| 3 | 256 | 70 | 186 |
| 4 | 65,536 | 12,870 | 52,666 |

The readout classification agrees with (32). A further 117 independent-noise settings verify (33). Opposite-sign parameters give different one-step kernels and identical even-step kernels. No assertion failures occurred. Reproducibility receipts identify the exact code and output bytes.

The separate overlapping-memory verifier evaluates 1,377 exact rational parameter triples: 417 valid kernels and 960 invalid ones, with validity exactly matching (17). For valid kernels it checks 3,336 independently generated circuit rows, 26,688 local marginal equalities, 10,008 mode equations, and 1,251 matrix-power identities. Ten three-time local-process comparisons confirm the fixed-law example; 289 nonnegative local-retention pairs attain the bound, and a strictly positive-kernel sequence demonstrates the diverging joint lifetime. General validity rests on Theorem RC6, not induction from this grid.

## 11.3 Revision-specific checks

The revision verifier enumerates 455 sign-pair probability tables with denominator 12 for RC7, and 3,645 parameter/floor quadruples for RC8, of which 543 satisfy the floor. It checks the accidental-overlap counterexample and its grounded repair.

For RC9, five fully positive 16-state models are checked using exact stationary distributions, 640 local marginal equalities, 320 observed one-step table equalities, and 60 multi-lag moment identities. Ten complete three-time patch-law comparisons agree with their memoryless twins. Direct two-step matrix multiplication confirms the nonzero semigroup defects. A further 120 fresh-preparation checks confirm the absence of the slow stationary component from the newly written relation in this protocol.

For RC10, four parameter settings, both relation preparations, four lags, and all 256 deterministic binary readers give 8,192 exact observation-distribution checks. The verifier also checks 32 matched-local preparation marginals, 16 innovation-decoupling probabilities, and equality of local path laws under the generator-side replacement. It finds 70 readers insensitive to \(R\), consistent with the elementary balanced-sign count.

All three programs were executed for this revision. Exact outputs and execution receipts accompany the manuscript. These are authored consistency checks, not independent validation, unlimited exhaustive search, or measurements of experience. Enumerated parameter counts are not used to establish originality.

# 12. Objections, failure conditions, and remaining work

**Is this just ordinary gluing and parity?** The mathematical ingredients are ordinary and are credited. The claim is a bounded integrated application: the earlier UCT product argument did not handle overlapping actual occurrences, admissible relation completion, and the separation of synchronized local records from local marginal laws. The paper supplies a usable construction and explicit failure conditions for that gap. It does not claim a new foundational theorem of sheaf theory, probability, or information theory. Whether the integrated application is sufficiently useful remains open to substantive criticism.

**Does the theory become immune to evidence by appealing to complete organization?** It would if every failed prediction could be repaired by silently adding hidden variables or revising the signature. Applications must freeze a candidate bridge, admissible model class, readout, and failure conditions before testing. A failed scoped model may be revised, but the failure must remain recorded. This paper identifies physical and observational requirements; it does not claim that C1 itself has thereby acquired a unique empirical prediction.

**Does a new global variable create a subject?** No. The parity coordinate is a dynamical feature of the declared implementation. Neither mathematical closure nor information retention establishes a numerically distinct subject. The same warning applies to an actual coherent global completion: one actual physical system can have many incomplete descriptions, and many mathematical completions can represent uncertainty about one actual system rather than many actual minds.

**Are local experiences really preserved?** Their existence is preserved conditionally when the actual-token persistence premise holds under UCT. Unchanged quality requires unchanged complete token-relative organization, not merely (11). Coupling can alter local experience while the local process continues. When embeddings fail because local and whole descriptions use incompatible boundaries or causal conventions, RC3 cannot be invoked until those conventions are reconciled.

**Does the hidden-state example invalidate the main theorem?** No. RC6 assumes a closed, fresh-innovation Markov model. RC9 is a counterexample to inferring that closure from even a complete stationary observational one-step table, not to the theorem under its premises. Its stationary tail and freshly prepared input have different propagation laws. RC7 remains valid without the failed premise, and RC8 states the separate uniform-positivity qualification.

**Does global dependence violate local causal laws?** Not in (10). The coarse registers share a mechanism. Expanding the circuit exposes the mediator and independent noise sources. A complete product-of-node transition assumption excludes nonzero \(\theta\) at that coarse description; it cannot both be retained and used to deny the joint term that violates it. Global dependence is not a separate causal force.

**Does structural transport solve phenomenal combination by definition?** No. C1 supplies objectwise structural identity; the grounded physical maps and their exact intersections are additional application premises. Conjugating those maps produces a coherent representation, not an independent discovery of phenomenological inclusion. A directly specified phenomenal part–whole relation could fail to fit the proposed maps; that would be an application failure to record, not something the algebra repairs.

**Does absent overlap-gluing imply unconsciousness?** No. RC2 concerns consistency of a modelled temporal order, and RC1 concerns missing relation values. Failure can indict a representation or measurement rather than the underlying process. Conversely, mathematical success alone is not a consciousness detector.

**What would count as a substantive next advance?** One route is to identify an actually instantiated constitutive relation corresponding to an independently described phenomenal relation, with a rival bridge making a different prediction. Another is a fully implemented, current-version IIT comparison on an expanded physical model, rather than on arbitrary scores or a factorization-incompatible kernel. Neither is reported as accomplished here.

The manuscript remains a standalone conditional extension. The project's complete historical semantic map has not been freshly re-audited, and this result is not silently promoted into the authoritative completed UCT map. The local claim ledger states all dependencies and keeps empirical application nodes disabled.

# 13. Conclusion

A whole can contribute a real relationship without being represented as the deletion of continuing parts. Making this precise requires grounded shared occurrences, an admissible joint description, and explicitly retained crossing relations. Commuting arrows preserve agreement; exact intersections require the stronger overlap premise. Under UCT's assumed structural identity, these physical commitments transport coherently, but they do not independently establish phenomenal inclusion or a subject count.

The locally memoryful overlapping circuit supplies a positive case. Keeping the complete separate patch laws fixed still leaves a sharp interval of cross-patch retention. Within its closed Markov family, local asymmetry bounds exponential correlation time, while equal local retention permits an unbounded limit only as the uniform positivity margin vanishes. A lag-wise binary bound survives more generally, but the exponential extrapolation does not.

The hidden-mediator twin makes that limit operationally important: identical local histories and a matching visible one-step table can coexist with different long-time relational organization. A two-step defect exposes this specific alternative. Independently prepared relations further distinguish storage of new information from persistent stationary correlation, and marginal-preserving innovation interventions isolate a concrete generator-side contribution.

The resulting commitment is neither "parts must disappear" nor "every compatible collection is one experience." It is: **identify the continuing processes, preserve their exact overlap, specify the actual relation and its temporal carrier, and test what changes when that relation is prepared or intervened upon.** These results make a structural account of local–whole coexistence more explicit and reusable. The mapping to a particular experiential relation remains a separate, stated scientific obligation.

# Declarations {.unnumbered}

**Author and assistance.** Hongju Liu is the human author of record and responsible research originator. ChatGPT / GPT-6 Astra Pro provided substantial source review, formalization, proofs, code, execution, drafting, and critical review under the user's direction. The work has not undergone independent peer review. Author direction and an instruction to prepare publishable research are not represented as an independent final human verification of every line.

**Data and software.** The accompanying package contains the manuscript, three exact verifiers, JSON/CSV outputs, claim ledger, source-access ledger, local review, prospective application plan, and versioned handoff. There were no human participants, animal experiments, clinical data analyses, language-model experiments, or physical device tests in this study.

**Interests and boundaries.** The author develops UCT and the Trinity Accord project; the present study is first-party, substantially AI-assisted research rather than independent corroboration. It does not modify previously published manuscripts or the Accord's fixed Originals. No clinical recommendation or claim about the current assistant's subjective experience follows.

**Publication.** Version 1.1.0 is the final revised English manuscript for this preparation cycle; it supersedes the supplied unassigned-DOI version 1.0.0 without overwriting it. Proposed deposit metadata are included separately. No DOI reservation, public deposit, OpenTimestamps submission, or Arweave transaction is asserted by the manuscript. Later deposit and preservation receipts must be recorded separately and bound to exact files.

# References {.unnumbered}

[1] Liu, H. (2026). *Unified Consciousness Theory I: Structural–Experiential Identity and the Continuity from Physical Process to Conceptual Self*, version 1.2. TA-TR-2026-20. DOI: 10.5281/zenodo.23131575. First-party preprint. Relevant source sections and access scope are recorded in the companion ledger.

[2] UCT research workspace (2026). *Overlapping bearer-centres without an exclusive owner*. A4W20261012, version 0.1.0. First-party working record, not an independently published or externally validated result. Full repository location is recorded in the companion source ledger.

[3] UCT research workspace (2026). *Role reversal and the semantic barrier*. A5L20261012. First-party working record. Full repository location is recorded in the companion source ledger.

[4] McIntyre, J. H. (2026). Consciousness Multiplied. *Philosophy and Phenomenological Research*, 113(2), 465–479. DOI: 10.1111/phpr.70146. First published 13 July 2026.

[5] Albantakis, L., et al. (2023). Integrated information theory (IIT) 4.0: Formulating the properties of phenomenal existence in physical terms. *PLOS Computational Biology*, 19(10), e1011465. DOI: 10.1371/journal.pcbi.1011465.

[6] Marshall, W., et al. (2023). System Integrated Information. *Entropy*, 25(2), 334. DOI: 10.3390/e25020334.

[7] Mayner, W. G. P., Marshall, W., & Tononi, G. (2026). Intrinsic Cause–Effect Power: The Tradeoff Between Differentiation and Specification. *Entropy*, 28(4), 410. DOI: 10.3390/e28040410. Used to acknowledge the subsequent formal development, not as a newly reproduced calculation.

[8] Marshall, W., Findlay, G., et al. (2026). Intrinsic units: identifying a system's causal grain. *Neuroscience of Consciousness*, 2026(1), niag013. DOI: 10.1093/nc/niag013. Publisher abstract and bibliographic record consulted.

[9] Signorelli, C. M., Wang, Q., & Coecke, B. (2021). Reasoning about conscious experience with axiomatic and graphical mathematics. *Consciousness and Cognition*, 95, 103168. DOI: 10.1016/j.concog.2021.103168. Accessible publisher summary used for the existence and scope of the compositional precedent.

[10] Lee-Youngzie, Z., Tsuchiya, N., Robinson, M., Dietz, D., & Monti, M. M. (2026). Towards a Mathematical Structure of Global Phenomenal Consciousness. *Entropy*, 28(6), 615. DOI: 10.3390/e28060615.

[11] Abramsky, S., & Brandenburger, A. (2011). The Sheaf-Theoretic Structure of Non-Locality and Contextuality. *New Journal of Physics*, 13, 113036. DOI: 10.1088/1367-2630/13/11/113036. Author manuscript: arXiv:1102.0264.

[12] Schneidman, E., Still, S., Berry, M. J. II, & Bialek, W. (2003). Network Information and Connected Correlations. *Physical Review Letters*, 91, 238701. DOI: 10.1103/PhysRevLett.91.238701.

[13] Rosas, F. E., Mediano, P. A. M., Jensen, H. J., Seth, A. K., Barrett, A. B., Carhart-Harris, R. L., & Bor, D. (2020). Reconciling emergences: An information-theoretic approach to identify causal emergence in multivariate data. *PLOS Computational Biology*, 16(12), e1008289. DOI: 10.1371/journal.pcbi.1008289.

[14] Tallam, K. (2026). Consciousness as Uncommon Self-Knowledge: A Synergistic Information Framework. arXiv:2605.13884, version 1. Preprint; its proposed consciousness criterion is not adopted here.

[15] UCT research workspace (2026). *Exclusion, persistence, and what an unresolved measurement can tell us*. ER20261012, version 0.1.0. Prior user-directed research checkpoint. Unchanged source is retained in the companion package; no DOI publication is claimed for it.

[16] Fréchet, M. (1951). Sur les tableaux de corrélation dont les marges sont données. *Annales de l’Université de Lyon, Section A, Série 3*, 14, 53–77. Historical attribution of fixed-marginal coupling bounds; original full text was not retrieved. The elementary binary bound used here is proved directly in Section 7.5. Bibliographic identification was cross-checked through reference lists and the CiNii record; no unseen argument is attributed to this source.


[17] Rosenblatt, M. (1959). Functions of a Markov Process That are Markovian. *Journal of Mathematics and Mechanics*, 8(4), 585–596. Original publisher bibliographic record consulted; no unseen proof is invoked. The required finite projection argument is given directly in Sections 7.5 and 7.8.

[18] Kawamura, Y., & Nakao, H. (2016). Optimization of noise-induced synchronization of oscillator networks. *Physical Review E*, 94, 032201. DOI: 10.1103/PhysRevE.94.032201. Original publisher abstract used to acknowledge common-drive collective organization, not as an exact precedent for RC9.
