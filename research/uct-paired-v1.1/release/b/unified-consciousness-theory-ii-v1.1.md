# Unified Consciousness Theory II
## Consciousness Theories as Effective Organization Theories

**Author:** Hongju Liu  
**Affiliation:** Independent researcher, Shenzhen, China  
**Report:** TA-TR-2026-21  
**Version:** 1.1  
**Date:** 29 September 2026  
**DOI:** 10.5281/zenodo.23030320  
**Prior published version:** v1.0, DOI 10.5281/zenodo.23008262  
**Depends on:** *Unified Consciousness Theory I*, v1.1 (Liu, 2026), DOI 10.5281/zenodo.23030207. The earlier UCT I v1.0 remains available at DOI 10.5281/zenodo.23005588.  
**Status:** Theoretical preprint prepared for open-access DOI publication; not peer reviewed.  
**AI assistance disclosure:** Substantial ChatGPT (OpenAI GPT-5.6 Sol) assistance was used for literature retrieval, formalization, adversarial review, toy-model analysis, drafting, editing, and publication preparation under human direction. The human author of record is responsible for the decision to publish. The paired v1.1 revision additionally used ChatGPT (GPT-6 Astra Pro) for source checking, signature and interface repair, exact transformation analysis, numerical reimplementation, editing, and release preparation. This is not independent peer review; no separate final human line-by-line verification is claimed.

## Abstract

Major theories of consciousness emphasize different mechanisms (Seth & Bayne, 2022): integrated causal structure, recurrent processing, global availability, higher-order representation, predictive modeling, dendritic integration, memory assembly, attention modeling, and temporospatial organization. Their competition is partly intensified by treating a favored mechanism as a candidate universal boundary between experience and nonexperience.

UCT I (Liu, 2026) adopts a different basal ontology: every actual valid process token possesses experience, identified with its complete token-relative ontic organization. UCT I v1.1 distinguishes that organization from finite physically anchored scientific views and estimates. Under that assumption, nonuniversal mechanisms cannot be universal experience-existence gates. UCT II asks whether their *operational cores* can instead be reconstructed, embedded, reinterpreted, or shown to conflict as effective organization theories.

We introduce an admissible translation framework, explicit bridge-admissibility conditions, a two-axis classification separating formal recovery from empirical validation, and anti-triviality criteria requiring translators to be constructive, non-circular, structurally invariant, reusable, failure-prone, and explanatorily nontrivial. A Translation Fidelity Requirement additionally preserves each target theory's distinctive signature, strongest phenomenal/ontological claim, and unrecovered empirical residue. We then fidelity-audit nine theories: IIT 4.0 (Albantakis et al., 2023), recurrent processing theory, GNWT, higher-order theories, predictive processing/active inference, dendritic integration theory, memory theory of consciousness, attention schema theory, and temporospatial theory. The result is not a universal endorsement: theory subclaims receive different relation types, formal classes, and validation statuses, including direct conflicts.

Two fixed-parameter toy models provide quantitative cross-theory proof of concept using one fixed parameterization across their theory-linked outputs: a DIT→RPT→GNWT chain and an independent MToC→HOT→GNWT chain. Negative controls dissociate upstream primitives from downstream recurrent, higher-order, and global-access organization. These results establish shared-law reuse only at formal-conditional / toy-model level (F3/V1); they do not constitute held-out human-data recovery (V3), replicated empirical recovery (V4), or robust full-theory compression.

The proposed unification is therefore partial, fidelity-audited, and failure-prone by design. Its governing distinction is that mechanistic recovery, ontological endorsement, and empirical confirmation are separate operations.

**Keywords:** consciousness; theory unification; intertheory translation; causal organization; IIT; GNWT; higher-order theory; recurrent processing; predictive processing; memory theory; temporospatial theory

---

# 1. Why intertheory unification needs constraints

A sufficiently rich mother state can be mapped to arbitrary target labels by lookup.

Therefore:

\[
\boxed{
\text{existence of a map}
\neq
\text{theoretical unification}.
}
\]

A legitimate UCT translator must satisfy:

1. constructive shared basis;
2. non-circular bridges;
3. structural invariance;
4. cross-instance reuse;
5. failure possibility;
6. nontrivial shared reuse or explanatory constraint beyond lookup.


These conditions are necessary but not sufficient. Criterion 6 requires at least nontrivial shared reuse or explanatory constraint; robust whole-theory description-length compression is a stronger optional test, not a prerequisite. A translator can still satisfy the basic constraints while translating only a weakened generic mechanism rather than the actual target theory.

Therefore Paper II adds a **Translation Fidelity Requirement (TFR)**.

A faithful translation must also preserve:

1. source fidelity to the target theory's published formulation;
2. a minimal distinctive signature \(\Sigma_T\);
3. the target theory's strongest central phenomenal/ontological claim, even when UCT rejects it;
4. target-specific empirical predictions as explicit residue;
5. the distinction between exact primitive recovery and full theory recovery;
6. explicit labeling of any UCT reinterpretation;
7. the possibility that theory fidelity fails even when a generic UCT functional exists.

Thus:

\[
\boxed{
\text{nontrivial mapping}
\neq
\text{faithful theory recovery}.
}
\]

---

# 2. Source formalism and the v1.1 interface

UCT I v1.1 uses tokenwise structural identity in a declared signature:

\[
h_P:\mathbf D^{ontic}_{\mathcal K}(P)\cong\Phi_{\mathcal K}(P).
\]

The identity concerns complete organization, not an analyst-selected representation. A finite intertheory translator instead receives a physically anchored view:

\[
D^{PA}_v(P):=\Pi_v[\mathbf D^{ontic}(P)],\qquad
O_T=\mathcal T_T(D^{PA}_v(P),B_T).
\]

Here \(v\) declares time, horizon, grain, represented boundary, intervention family, and relevant signature; \(B_T\) contains the fixed, non-oracular theory-specific conventions. A familiar representation of a view is

\[
D^{PA}_v=(P,s_t,\Theta,C^{PA}_v,
\bar{\mathcal I}^{MF}_v,R_{\Theta,v},\mathcal R_v).
\]

The tuple makes the current state, mechanism, physical chart, permitted interventions, response relation, and retained structural relations explicit. It does not certify ontic completeness. This is the replacement for the ambiguous finite-translation use of \(\mathfrak D^{PA}\) in v1.0; prior published statements are not overwritten.

## 2.1 Pointed and port-aware translation

The explicit finite signature in UCT I Section 3.5 requires state, input, intervention, and output mappings to commute with updates, resets, and readout; to map the actual pointed state correctly; and to preserve the declared temporal and constituent relations. An input/output trajectory match is not automatically such an isomorphism. A constituent port permutation must be declared as allowable; a noninvertible view is not a coordinate relabeling.

Every translation operation is labeled as one of: (i) a mechanism-fixed constitutive query in the declared physical model, (ii) a derived mathematical operation, (iii) a diagnostic mechanism change producing a separately indexed process/model, or (iv) a semantic/empirical bridge. This prevents changing the mechanism or view from being silently treated as another observation of an unchanged complete token.

## 2.2 Estimates and identified output sets

Actual data produce \(\widehat D^{PA}_v\), not guaranteed access to \(D^{PA}_v\). If evidence permits an identified set \(\mathfrak I_v\), the corresponding translated output is

\[
\mathfrak O_T=
\{\mathcal T_T(D,B_T):D\in\mathfrak I_v,\ B_T\text{ applicable to }D\}.
\]

Any cases where the bridge is undefined are also reported, rather than silently discarded. A point result requires identification sufficient for that particular output; it does not require a unique universal process or subject partition.

## 2.3 Four distinct inferential operations

| Operation | What supplies the implication | What it does not establish |
|---|---|---|
| Reconstruct a physical/theory-specific output | fixed physical view, shared operators, admissible \(B_T\) | A1 or A5 empirical truth |
| Reject a universal organization gate within UCT | A1 plus a scoped actual nonuniversality witness | failure of a domain-limited perceptual claim |
| Interpret full physical organization experientially | A5-SI or its stated weaker consequence | sensitivity of a finite report measure |
| Predict a finite phenomenal/psychophysical target | fixed operational bridge and measurement assumptions | full identity from successful prediction alone |

The additional apparatus identifies scientific inputs and logical dependencies. It does not introduce a second mechanism for experience, a macro-experience threshold, or a compulsory exclusive subject selector.

---

# 3. Shared operator language

A compact candidate toolkit is:

\[
\boxed{
\mathbf{Res},
\mathbf{DoResp},
\mathbf{Diff},
\mathbf{Comp},
\mathbf{Struct},
\mathbf{Opt}.
}
\]

These denote:

- restriction/coarse-graining;
- intervention-response extraction;
- response comparison;
- composition;
- structural graph/partition/invariant operations;
- explicitly declared selection/optimization rules.

The toolkit is not claimed mathematically minimal.

---

# 4. Bridge admissibility and mechanism representation

## 4.1 Bridge Admissibility Conditions

A theory-specific bridge package \(B_T\) is **admissible** only if the following conditions are satisfied.

### BAC-1 — Source anchoring

Theory-specific primitives in \(B_T\) must be motivated by canonical target-theory sources or by independently identified/measured system structure.

### BAC-2 — Output blindness / non-oracularity

\(B_T\) may not contain the desired target output, its instance label, or an equivalent lookup oracle for the case being translated. In particular, the bridge cannot count as a recovery device merely because it encodes the answer that \(\mathcal T_T\) is supposed to reconstruct.

### BAC-3 — Cross-instance fixation

For a declared domain \(D_T\), the bridge rules are fixed independently of the particular target result. Instance-specific measured variables may vary; the bridge definition itself may not be redesigned for each case.

### BAC-4 — No post-hoc target refitting

Translator structure, thresholds, and bridge semantics must not be changed after observing the target-theory output for each evaluated instance.

### BAC-5 — Structural covariance

When both UCT and the target observable are invariant under an admissible structure-preserving reparameterization, the translated result must be invariant as well.

### BAC-6 — Failure possibility

There must exist possible systems or cases for which the translation can fail source fidelity, fail a target prediction, or remain undefined because the required bridge conditions are absent.

### BAC-7 — Residual transparency

Anything imported from the target theory rather than generated by the shared UCT formalism must remain explicit in \(B_T\) or in the unrecovered residual set \(R_T^{res}\).

These conditions formalize the anti-lookup and anti-oracle requirements used throughout Paper II.

## 4.2 Admissible Mechanism Representation Proposition

Call a mechanism theory \(T\) admissible over domain \(D_T\) if each operational observable can be written:

\[
O_j
=
E_j(D^{PA}_v,B_T)
\]

using the shared language and a **BAC-admissible**, fixed bridge package \(B_T\).

Then a compositional translator exists:

\[
\mathcal T_T:
(D^{PA}_v,B_T)
\mapsto
O_T.
\]

The proof is structural induction over the declared expression tree.

This proposition establishes compositional closure of the admissible translation language. It does **not** by itself establish that a proposed \(B_T\) satisfies BAC, that every consciousness theory belongs to the class, that the target theory is empirically correct, or that the translated theory has been fully reduced.

---

# 5. Two-axis classification and effective organization descriptions

The earlier single R0–R5 ladder mixed formal relation/recovery status with empirical validation. Paper II therefore uses two independent axes.

## 5.1 Formal relation/recovery class \(F\)

| Class | Meaning |
|---|---|
| F0 | direct conflict for the specified subclaim |
| F1 | logical compatibility only |
| F2 | embedding / representability |
| F3 | conditional derivation under an explicit BAC-admissible bridge |
| F4 | exact/local formal reduction of the specified primitive |

These classes apply to **subclaims or primitives**, not whole theories. They are a formal classification vocabulary, not a total-order score over whole theories; different subclaims of the same theory may occupy different classes. They are not empirical validation scores.

## 5.2 Empirical validation class \(V\)

| Class | Meaning |
|---|---|
| V0 | no empirical validation claim |
| V1 | toy-model / model-organism proof of concept |
| V2 | fitted or in-sample empirical recovery |
| V3 | preregistered or otherwise fixed held-out recovery against relevant baselines |
| V4 | replicated / cross-system empirical effective recovery |

The two axes are independent. In particular:

\[
F4\not\Rightarrow V3
\]

and:

\[
V3\not\Rightarrow F4.
\]

An exact graph-theoretic primitive may be \(F4/V0\), while an empirically successful effective model could be \(F2\) or \(F3\) with \(V3\) or \(V4\).

## 5.3 Relation labels and residuals

For each target subclaim, the UCT relation label is drawn from:

- **REC** — formal reconstruction;
- **EMB** — embedding;
- **REI** — UCT reinterpretation;
- **CON** — direct conflict.

Empirical/unrecovered material is **not** a fifth relation type. It is recorded separately in:

\[
R_T^{res}
\]

and in the empirical validation class \(V_T\).

This separation prevents logical relation, residual content, and evidential status from being conflated.

## 5.4 Effective organization description

A target-theory subclaim \(c\) is an **effective organization description relative to UCT** when:

1. \(c\) concerns a nonuniversal organization property rather than the universal existence predicate for experience;
2. its operational content is reconstructible or embeddable from \((D^{PA}_v,B_T)\) under BAC;
3. any target-specific phenomenal or ontological interpretation is separately labeled rather than silently inherited;
4. unrecovered commitments remain explicit in \(R_c^{res}\).

Thus:

\[
\boxed{
EOD_{\rm UCT}(c)
\Rightarrow
\text{organization recovery without automatic ontological endorsement}.
}
\]

This is the sense in which Paper II treats recoverable parts of consciousness theories as **effective organization theories**.


## 5.5 Scope and nonuniversality-witness rule

Any use of the Organization-Gate Impossibility result or any F0/CON classification must state the relevant domain and the condition that makes the target mechanism nonuniversal.

For a candidate organization predicate \(M(P)\), “nonuniversal” means that there exists at least one actual valid UCT token in the declared domain for which the predicate is absent or falls outside the target region:

\[
\exists Q_{\rm actual}\in D:
\neg M(Q).
\]

A source claim confined to human conscious access or a specified perceptual domain must not be silently extrapolated to every actual physical process. A witness outside the target's stated domain establishes a conflict only with an explicitly universalized extension, not with the domain-limited claim itself. In particular, the strong universal MToC contrast in Section 12 is labeled as such; a biological source's wording does not itself establish that it intended an ontology of elementary interactions.

Only then does A1 yield the gate contradiction:

\[
E(Q)=1
\quad\text{while}\quad
M(Q)=0.
\]

Likewise, a direct conflict classification must identify the exact target-theory necessity/identity claim being contradicted, rather than infer conflict from a theory label alone. This rule makes domain and existence witnesses explicit rather than leaving them as hidden premises.


## 5.6 Dependency separation: reconstruction, no-gate relocation, and experiential interpretation

Paper II distinguishes three logically different operations.

### Formal reconstruction

Whether a target operational observable can be reconstructed or embedded from:

\[
(D^{PA}_v,B_T)
\]

under BAC is a formal/mechanistic question. The existence of such a translator does not, by itself, empirically prove A1 or A5.

### No-universal-gate relocation

For a target mechanism that is nonuniversal on the declared UCT domain, A1 plus the required nonuniversality witness imply that the mechanism cannot equal the universal experience-existence predicate.

### Experiential-organization interpretation

Treating a BAC-admissibly recovered physical organization as part of **experiential organization** additionally depends on A5:

\[
\Phi_{\mathcal K}(P)\cong\mathbf D^{ontic}_{\mathcal K}(P).
\]

Thus:

\[
\begin{gathered}
\text{formal reconstruction}\neq\text{no-gate relocation},\\
\text{neither equals experiential-organization interpretation}.
\end{gathered}
\]

The empirical validation axis \(V\) is separate from all three.

---

# 6. IIT 4.0

Given:

- an IIT-compatible chart;
- current state;
- mechanism-fixed transition/intervention data;
- IIT's prior, intrinsic-difference metric, partition family, max/min rules and tie conventions;

IIT computational quantities are conditionally reconstructible once IIT's own formal conventions are supplied.

Thus:

\[
\boxed{
IIT_{\rm computational}:F3/V0.
}
\]

The levels of IIT quantities must remain distinct. In IIT 4.0, \(\phi_s\) denotes **system integrated information**. A mechanism specifying a causal distinction is evaluated using **distinction integrated information** \(\phi_d\); relation integrated information is \(\phi_r\), and their sum in a complex's cause-effect structure is structure integrated information \(\Phi\) (Albantakis et al., 2023, sections “System integrated information,” “Composition,” and “Relations”). None is identified with UCT's whole experiential object merely because the same Greek letter is used.

For a specified candidate system in a specified current state, if an admissible IIT system partition makes no difference to its relevant cause or effect probabilities, the corresponding system reducibility criterion yields
\[
\phi_s=0.
\]
This is a statement at the **system** level, under IIT's own repertoires, prior, intrinsic-difference measure, normalized partition selection, and tie conventions. Generic factorization of an arbitrary graph or observation distribution is not substituted for those requirements. Distinction-level claims would require the separate mechanism/purview calculation and \(\phi_d\); this paper does not infer them from the displayed system-level statement.

However UCT does not inherit maximal exclusion.

\[
\boxed{
IIT_{\rm exclusion\ ontology}:F0
}
\]

because, when the lower process remains an actual valid UCT token, A3 does not permit overlap or nonmaximality **alone** to erase that lower process's experience.

This is a model of formal reconstruction plus explicit reinterpretation/conflict, not a full reduction of IIT as a phenomenal theory.

---

# 7. Recurrent Processing Theory

The sensory/perceptual scope follows Lamme (2006); a generic cycle detector is not a complete theory of conscious vision.

From the intervention-defined directed causal graph \(G_C(P)\), strongly connected components identify recurrent causal modules.

This yields exact recovery only of a **primitive graph-recurrence property**:

\[
Primitive_{\rm graph\ recurrence}:F4_{\rm local}/V0.
\]

A faithful RPT translation additionally requires a sensory/perceptual chart, content-sensitive recurrence, theory-relevant timing, and a stabilization/perceptual consequence. Therefore the theory-level status remains:

\[
RPT_{\rm theory}:F3/V0.
\]

But the claim that a particular recurrent neural regime is necessary/sufficient for perceptual consciousness remains a theory-specific empirical bridge:

\[
RPT_{\rm phenomenology}:\text{residual empirical claim; current }V0.
\]

---

# 8. Global Neuronal Workspace

The workspace signature follows Dehaene and Changeux (2011) and Mashour et al. (2020): amplification, sustained representation, and broad availability are retained, rather than identifying a graph-reachability primitive with the complete theory.

For content process \(S_c\) and declared consumers \(K_j\), define causal access:

\[
a_j(c,t;\tau)
=
d_j[
P(X^{K_j}_{t+\tau}\mid do(C_c=c)),
P(X^{K_j}_{t+\tau}\mid do(C_c=c_0))
].
\]

This yields an access vector, breadth and coverage measures, persistence, and workspace macrostate.

Thus:

\[
GNWT_{\rm core}:F3/V0.
\]

UCT does not equate workspace ignition with experience existence.

Strong GNWT anatomical/timing predictions remain empirical and may fail independently of the existence of a generic access functional.

---

# 9. Higher-Order Theory and Attention Schema Theory

A higher-order process may causally track a lower-order state.

AST further specializes this into a simplified internal model of attention used to control future attention.

These causal organizations are representable.

But:

\[
\boxed{
\text{causal targeting}
\neq
\text{fully grounded semantic aboutness}.
}
\]

Therefore:

\[
Primitive_{\rm hierarchical\ causal\ tracking}:F4_{\rm local}/V0,
\qquad
HOT_{\rm theory}:F3/V0,
\]

and:

\[
AST_{\rm mechanistic}:F3/V0.
\]

A unified representation-grounding bridge remains required.

---

# 10. Predictive Processing and Active Inference

A PP/AI chart requires extra structure:

- agent/environment partition;
- internal model state;
- latent variables;
- \(p_\theta\);
- \(q_\phi\);
- prediction/error relations;
- policies;
- preferences/objectives.

Once those bridges are fixed, free-energy and policy quantities are computable functionals of the process chart.

Thus:

\[
PP/AI:F3_{\rm conditional}/V0.
\]

UCT does not infer generative-model semantics from bare topology alone. Pezzulo et al. (2024) explicitly use a notion of basic sentient behavior without phenomenological commitments. Their terminology must not be converted into a universal phenomenal-existence claim merely to manufacture a conflict with A1.

Furthermore, PP/AI recovery requires independently motivated model-state identification and comparison against plausible non-PP/AI computational alternatives. A generative-model fit that can be redefined per instance does not satisfy TFR.


---

# 11. Dendritic Integration Theory

Specify biologically identified:

- apical input/state;
- basal input/state;
- somatic output;
- thalamic modulation.

Nonlinear interventional interaction and downstream propagation become response functionals of the physical process.

However, nonlinear gating alone is not DIT. A faithful DIT signature must preserve:

- pyramidal-cell compartment structure;
- bottom-up / top-down integration;
- apical/basal interaction;
- thalamocortical modulation/propagation;
- the biological conscious-state claims associated with the theory.

Thus a local interaction functional is only a primitive. The theory-level relation remains:

\[
DIT_{\rm theory}:F3/V0.
\]

Dendritic gating can affect later recurrence and global propagation without being the universal origin of experience.

---

# 12. Memory Theory of Consciousness

A minimal temporal-retention relation can be defined by whether changing an earlier state changes a later independently specified retained/trace-candidate state.

This gives:

\[
Primitive_{\rm temporal\ causal\ retention}:F4_{\rm local}/V0.
\]

Identifying working, episodic, semantic, and assembly systems requires empirical bridges:

\[
MToC_{\rm mechanistic}:F3/V0.
\]

On the strong necessity reading preserved in the source-trace ledger, explicit memory is not the universal experience-existence gate **provided that the declared UCT domain contains at least one actual valid process token lacking the target explicit-memory system**.

Let \(M_{\rm explicit}(P)\) denote possession of that target system. If:

\[
\exists Q_{\rm actual}:
\neg M_{\rm explicit}(Q),
\]

then A1 gives \(E(Q)=1\), whereas a universal explicit-memory necessity claim gives \(E(Q)=0\). Under this explicit nonuniversality witness, the strong identity is an F0/CON conflict:

\[
\boxed{
MToC_{\rm all-experience\ via\ explicit-memory}:F0.
}
\]

Thus temporal causal retention is an exactly recoverable structural primitive, identifying that retained state as a memory system remains bridge-dependent at F3/V0, and the strongest universal MToC identity remains visible as a rejected claim.


---

# 13. Temporospatial Theory

UCT's scientific views are indexed by time horizon and measurement/representation grain:
\[
D^{PA}_v(P)=\Pi_v[\mathbf D^{ontic}(P)].
\]
Different actual process tokens may also instantiate different organizations at different physical scales. Merely changing the analyst's horizon or grain does not change the experience of an unchanged token.

Nestedness, alignment, expansion, and globalization can therefore be represented by cross-scale causal relations, state-input interaction, causal support growth, and global reachability.

Thus:

\[
TTC_{\rm structural}:F3/V0
\]

with several local direct functionals.

The mapping from these quantities to phenomenology remains an empirical or theoretical bridge. In the source formulation, nestedness concerns a predisposition for state/level, alignment a prerequisite for content/form, expansion phenomenal correlates, and globalization cognitive consequences (Northoff & Huang, 2017). The translation must preserve this differentiated assignment; four generic scale-sensitive functions are not, by themselves, a faithful recovery of TTC.

---

# 14. Fidelity-audited nine-theory matrix

## 14.1 Distinctive signatures retained

| Theory | Distinctive signature retained |
|---|---|
| IIT | IIT priors/ID metric, partitions, max-min rules, and composition |
| RPT | sensory/content-sensitive recurrence plus timing and stabilization |
| GNWT | broad consumer access, amplification/persistence, and ignition |
| HOT | higher-order representation, not mere causal tracking |
| PP/AI | fixed generative, inference, and policy architecture |
| DIT | dendritic, pyramidal, and thalamocortical signature |
| MToC | explicit-memory architecture plus the strong all-experience claim |
| AST | internal attention model plus control role |
| TTC | nestedness, alignment, expansion, and globalization |

## 14.2 Formal relation and validation matrix

| Theory | Formal status | Relation labels | Validation |
|---|---|---|---|
| IIT | computational F3; exclusion F0 under scoped overlap witness | REC + REI + CON | V0 |
| RPT | graph recurrence F4; theory F3 | REC + EMB + REI | V0 |
| GNWT | core F3 | EMB + REI | V0 |
| HOT | causal-tracking primitive F4; theory F3 | REC + EMB + REI | V0 |
| PP/AI | F3 conditional | EMB + REI | V0 |
| DIT | local interaction F4; theory F3 | REC + EMB + REI | V0 |
| MToC | temporal retention F4; theory F3; strong identity F0 given nonuniversality witness | REC + EMB + CON | V0 |
| AST | F3 | EMB + REI | V0 |
| TTC | F3 | EMB + REI | V0 |

## 14.3 Residual and conflict status

| Theory | Main residual/conflict |
|---|---|
| IIT | exclusion conflict; neural/temporal predictions |
| RPT | phenomenal/perceptual sufficiency, timing/localization |
| GNWT | strong neural/temporal implementation |
| HOT | representational semantics and phenomenal sufficiency |
| PP/AI | model semantics + comparative validation |
| DIT | biological necessity/sufficiency and implementation |
| MToC | strong ontology conflict; timing/anatomy |
| AST | semantic aboutness, awareness attribution, control predictions |
| TTC | neurophenomenal mapping and scale/frequency predictions |

\[
\boxed{
F4_{\rm primitive}
\not\Rightarrow
F4_{\rm theory}
}
\]

and independently:

\[
\boxed{
F4\not\Rightarrow V3.
}
\]

**Comparison-only frameworks.** Information Closure Theory (ICT) and Integrated World Modeling Theory (IWMT) remain important comparison/unification competitors in Section 15, but they are not counted as members of the nine-theory source-trace atlas audited in Section 14.

---

# 15. Nearest unification competitors and novelty boundary

UCT does not claim to be the first framework to integrate, reconcile, decompose, or compare existing consciousness theories.

Important prior art includes:

- hierarchical causal descriptions (Coward & Sun, 2004);
- IWMT as a synthetic framework combining IIT, GNWT, the Free Energy Principle, and active inference (Safron, 2022), with a 2026 extension relating IWMT to the Human Consciousness Hypothesis (Safron et al., 2026);
- Information Closure Theory (Chang et al., 2020);
- TICL (Winters, 2020, 2021);
- universal-theory criteria that seek intrinsic mathematical formulations (Kanai & Fujisawa, 2024);
- the temporal-hierarchy/minimal-model unification of six prominent consciousness theories by Singhal and Srinivasan (2026);
- the building-block approach of Lopez and Wiese (2025), which explicitly recommends shifting from whole theories to simpler elements that can support assessment, integration, and unification;
- Tonetto's (2026) preprint separating recurring structural findings from broader ontological commitments across major consciousness theories.

These works substantially narrow any defensible novelty claim. Paper II therefore does **not** claim novelty for the general ideas that theories may be complementary, that whole theories can be decomposed into smaller commitments, or that multiple theories can be organized inside a larger synthesis.

The contribution claimed here is the conjunction of four more specific moves:

1. a physically anchored mother formalism inherited from UCT I;
2. explicit **Bridge Admissibility Conditions** plus a **Translation Fidelity Requirement** that preserve non-oracular fixed bridges, a target-specific signature \(\Sigma_T\), the strongest target claim, and explicit residual commitments \(R_T^{res}\);
3. independent relation labels for formal reconstruction, embedding, UCT reinterpretation, and direct conflict, with empirical validation and unrecovered residual commitments tracked on separate axes rather than collapsed into a single global claim that a theory has been "reduced";
4. failure-prone quantitative shared-law reuse in fixed-parameter toy models with negative controls and a single parameterization shared across the theory-linked outputs.

The UCT-specific methodological rule is therefore:

\[
\boxed{\begin{gathered}
\text{Reconstruct or embed an operational mechanism;}\\
\text{separately classify ontology, conflict, and empirical residue.}
\end{gathered}}
\]

When UCT changes a target theory's explanatory role—from consciousness generator or universal criterion to organization phenotype—that move is labeled **reinterpretation**, not neutral reduction.

The **no-universal-gate relocation** follows from A1 together with the relevant nonuniversality witness. Interpreting a BAC-admissibly recovered physical mechanism as part of **experiential organization** additionally depends on A5. Paper II therefore does not treat A1 alone as sufficient for the full experiential-organization interpretation.

---

# 16. Cross-theory consequences

A mother framework becomes more interesting when it generates constrained relations between theory-linked mechanisms. The arrow-like notation in this section denotes **conditional enabling**, not unconditional sufficiency.

Examples:

### DIT-like gating \(\leadsto\) RPT-like recurrence under a return-path condition

Opening a causal edge \(u\to v\) creates a new directed cycle iff a return path \(v\leadsto u\) already exists. Interpreting the gated edge as DIT-relevant and the resulting cycle as RPT-relevant additionally requires the corresponding DIT and RPT bridge conditions.

### Recurrence as an enabling condition for ignition-like transitions

Restricted recurrent dynamical systems **can** undergo saddle-node/bistable transitions yielding GNWT-like ignition when the required nonlinear feedback, drive, and workspace conditions are present. Recurrence alone is not asserted to be sufficient:

\[
\text{recurrence}
\not\Rightarrow
\text{global access}.
\]

### Grounded representation + broad availability \(\leadsto\) globally available internal model

An independently grounded representation that becomes causally available to a declared broad consumer family yields a globally available internal model relative to that declared access architecture.

These are conditional/enabling cross-theory statements, not unconditional implications and not proofs of the target theories.

---

# 17. Empirical program

Paper II can be complete as a formal theoretical preprint at V0/V1; the **empirical-recovery program** is not complete until at least fixed held-out recovery against relevant baselines (V3), with cross-system replication (V4) as the stronger target.

Required tests include:

1. preregistered bridge laws;
2. fixed translator parameters across systems;
3. held-out recovery of target-theory quantitative effects using fixed bridge and translator rules, with only declared measured inputs allowed to vary;
4. baseline comparison;
5. cross-theory predictions not imported from the target theory;
6. explicit failure leading to bridge revision rather than post-hoc relabeling.

The earlier GNWT toy dynamics and the present shared-law examples are V1 model evidence, not V3/V4 empirical recovery. The 2025 adversarial collaboration is especially important because it directly challenged key preregistered predictions of both IIT and GNWT rather than merely comparing verbal frameworks (Cogitate Consortium et al., 2025).

---

# 18. Faithfulness as a publication constraint

Paper II should not count a target theory as "recovered" unless a reader who endorses that target theory could recognize its distinctive machinery and its strongest claim in the translated representation.

The following failure mode is now explicitly prohibited:

\[
\begin{gathered}
\text{delete target-specific commitments}\\
\longrightarrow\text{retain generic mechanism}\\
\longrightarrow\text{declare unification}.
\end{gathered}
\]

For each theory \(T\), the release package should preserve:

1. source passages/formal definitions establishing \(\Sigma_T\);
2. the UCT translator;
3. the relation labels REC/EMB/REI/CON, the formal class F, and empirical validation class V;
4. theory-specific predictions left in \(R_T^{res}\);
5. conditions under which the translation would fail fidelity.

This is stronger than the original anti-lookup criterion because it prevents **conceptual overcompression** as well as mathematical overfitting.

---

# 19. Quantitative shared-law example: DIT → RPT → GNWT

Paper II's nontriviality criterion requires more than writing compatible translation formulas. At least one shared dynamical law should generate observables associated with more than one target-theory signature under one fixed parameterization shared across the linked outputs.

A minimal fixed model was therefore constructed with one scalar gate parameter:

\[
g\in[0,1],
\]

mapped to:

\[
q(g)=\sigma[10(g-0.5)].
\]

The same gate enters all three theory-linked observables.

## 19.1 DIT-like local interaction

For apical-like input \(a\) and basal-like input \(b\),

\[
d(a,b;g)
=
\sigma[-2+1.2a+1.2b+3q(g)ab].
\]

Define:

\[
\Delta_{AB}
=
d(1,1)-d(1,0)-d(0,1)+d(0,0).
\]

This gives a smooth DIT-like nonlinear interaction measure.

## 19.2 Recurrent topology and a structural spectral diagnostic

A two-node recurrent core contains one fixed return edge \(r=2\) and one gated edge \(3q(g)\).

The structural spectral gain is:

\[
\rho(g)=\sqrt{6q(g)}.
\]

Therefore:

\[
\boxed{
\rho=1
\quad\text{at}\quad
g\approx0.339.
}
\]

This \(\rho\) is the spectral radius of the declared weighted connection matrix, not of the nonlinear fixed-point Jacobian. Since \(q(g)>0\) throughout the stated finite interval, the two-edge directed cycle exists throughout that interval; \(\rho=1\) is not the first appearance of recurrence. For the synchronous update specified in Section 19.3, local linear stability at a fixed point instead depends on
\[
J=\begin{pmatrix}
0 & 10x_1(1-x_1)\\
15q(g)x_2(1-x_2) & 0
\end{pmatrix}.
\]
Its spectral radius depends on state and drive as well as the connection weights. The numerical \(\rho=1\) crossing is therefore reported only as a structural diagnostic crossing, not a demonstrated bifurcation or universal RPT threshold.

## 19.3 GNWT-like access

The same gated edge enters a fixed nonlinear workspace:

\[
x_1=\sigma(5[-0.5+s+2x_2]),
\]

\[
x_2=\sigma(5[-0.5+3q(g)x_1]).
\]

Five fixed downstream consumers define global availability \(G\).

With baseline content drive \(s=0.3\), the high-access operational criterion

\[
G\ge0.8
\]

is first reached at approximately:

\[
\boxed{
g\approx0.403.
}
\]

The reported model uses the same shared gate parameter and fixed GNWT readout architecture across the DIT-, RPT-, and GNWT-linked outputs; no separate gate parameter is introduced for the GNWT readout.

## 19.4 Negative control

The local DIT-like interaction is left unchanged, but the gated return edge \(x_1\to x_2\) is removed in the workspace update: its coefficient \(3q(g)\) is set to zero. The fixed \(x_2\to x_1\) coefficient remains 2. Consequently \(x_2=\sigma(-2.5)\), independently of \(g\), and the loop is broken. This specifies the control that reproduces the archived table; cutting the other edge is a different intervention.

Then:

\[
\rho=0
\]

for the recurrent core and the maximum global-access score remains approximately:

\[
G_{\max}\approx0.0397.
\]

Thus:

\[
\boxed{
\text{local gating alone}
\not\Rightarrow
\text{a structural spectral crossing}
\not\Rightarrow
\text{global access}.
}
\]

## 19.5 Unrefitted drive perturbation sweep

All model parameters are held fixed while only content drive is changed. This is a **model-level unrefitted perturbation sweep**, not empirical held-out validation in the V3 sense.

The chosen structural spectral crossing remains fixed at \(g\approx0.339\), whereas GNWT-like high access shifts with drive and disappears completely for sufficiently weak drive.

For example:

- \(s=-0.4\): no high-access transition over the full gate sweep;
- \(s=-0.3\): high access appears near \(g=0.575\);
- \(s=-0.2\): first tested high-access grid point \(g=0.4725\);
- \(s\ge0\): near \(g\approx0.403\).

This supplies a useful dissociation:

\[
\boxed{
\text{the chosen structural spectral criterion is not sufficient for global access.}
}
\]

The reported access crossings are the first qualifying points on the archived \(\Delta g=0.0025\) sweep, not exact analytically identified critical parameters. The high-access predicate \(G\geq0.8\) is an operational readout criterion. Calling its crossing ignition-like does not by itself prove a dynamical bifurcation. The reconstruction and stopping conventions are supplied with the executable audit.

## 19.6 Status of the result

This is not biological validation of DIT, RPT, or GNWT.

Its significance is methodological:

- one model;
- one shared gate parameter;
- three theory-linked observables;
- a negative control;
- unrefitted drive perturbation sweep;
- one fixed parameterization shared across the theory-linked outputs.

It therefore counts as:

\[
\boxed{
\text{shared quantitative-law reuse at }F3/V1\text{ level}.
}
\]

---

# 20. Second quantitative shared-law example: MToC → HOT → GNWT

To avoid relying on one biological/network chain, a second independent model was constructed around temporal retention, higher-order tracking, and global access.

A single content pulse initializes:

\[
m_0=1.
\]

Memory retention is controlled by one parameter:

\[
m_{t+1}=\lambda m_t.
\]

A fixed higher-order tracking state obeys:

\[
h_{t+1}
=
0.6h_t
+
0.4\,\sigma[12(m_t-0.35)].
\]

A fixed recurrent workspace obeys:

\[
w_{t+1}
=
0.7w_t
+
0.3\,\sigma[10(h_t+1.2w_t-0.8)].
\]

Five fixed consumer channels define the global-access score \(G\).

The same retention parameter \(\lambda\) is used across the three fixed readouts; no separate output-specific retention parameter is introduced.

## 20.1 Distinct transitions

MToC-like retention varies continuously as:

\[
m_5=\lambda^5.
\]

A primitive higher-order activation criterion:

\[
\max_t h_t\ge0.5
\]

is first reached at approximately:

\[
\boxed{
\lambda_{\rm HOT}\approx0.403.
}
\]

GNWT-like high access:

\[
\max_t G_t\ge0.8
\]

is first reached at approximately:

\[
\boxed{
\lambda_{\rm GNWT}\approx0.722.
}
\]

Thus:

\[
\boxed{
\text{retention}
\rightarrow
\text{higher-order activation}
\rightarrow
\text{global access}
}
\]

occurs in one fixed model, but the three organization coordinates are not identical.

## 20.2 Edge-cut controls

If the memory-to-higher-order edge is cut:

- the memory trace remains;
- higher-order activation collapses;
- GNWT-like high access disappears.

If the higher-order-to-workspace edge is cut:

- memory remains;
- higher-order activation remains;
- GNWT-like high access disappears.

Hence:

\[
\boxed{
\text{retention alone}
\not\Rightarrow
\text{higher-order organization}
\not\Rightarrow
\text{global availability}.
}
\]

## 20.3 Fidelity boundary

This model does **not** reconstruct full MToC, HOT, or GNWT.

- For MToC it models a retention/temporal-assembly primitive, not the strong claim that the explicit-memory system is responsible for all conscious experience.
- For HOT it models a higher-order tracking primitive, not complete semantic representation.
- For GNWT it models a recurrent global-access transition, not its full neural implementation.

Accordingly:

\[
\boxed{
F4_{\rm primitive}
\not\Rightarrow
F4_{\rm theory}.
}
\]

The archived grid uses 180 retention values from 0.1 to 0.99. Its first tested higher-order criterion crossing is \(0.4032960894\), and its first high-access crossing is \(0.7215083799\). The rounded values above identify sampled criterion crossings, not exact bifurcation parameters.

The significance is methodological: this is a second independent example in which one fixed parameterization produces observables associated with multiple target-theory signatures while preserving clear failure modes.

---

## 20.4 Exact shared transformation case from UCT I v1.1

UCT I Section 9 separately switches two physical cross-links while fixing the declared output and token comparisons. With a held common boundary, the initial pair perturbation obeys
\[
\delta z_n=A_{\alpha\beta}^{\,n}\delta z_0,\qquad
A_{\alpha\beta}=\begin{pmatrix}0&\alpha\\\beta&0\end{pmatrix}.
\]
The retained response partition has \(N_n=2^{\operatorname{rank}(A^n)}\) classes. With no cross-link it has one class after one step; with one cross-link it has two classes at one step and one thereafter; with both cross-links it has four classes at every positive horizon in the noiseless model. All settings preserve the implemented \(s\)-process and declared \(u\)-to-\(y=s\) responses.

This yields three exact translations on a fixed view: the pair's cycle property, its horizon-specific causal-retention partition, and its invariant declared consumer output. A directed cycle and persistent retention coincide in this specially specified family, but one-step causal retention does not require a pair cycle. A one-link setting is nonproduct relative to the declared split while still losing all initial pair distinctions by two steps. Thus recurrence, fixed-split nonproduct structure, and causal retention are separated by the same explicit laws rather than by changing descriptors after an outcome.

These are graph, response-partition, and access primitives. No biological RPT, explicit-memory MToC, semantic HOT, or full GNWT sufficiency claim is recovered by naming them. Their finite mathematical definitions/proofs have local formal status, and the model example has V1 status; assigning target-theory roles remains bridge-dependent. A1 and A5 are not used to calculate the table. A5 supplies the conditional experiential interpretation; a sensitive finite phenomenal measurement would still require its own bridge.

# 21. Source-trace and compression status

The Translation Fidelity Requirement uses the nine-theory v0.54 source-trace ledger as historical provenance, with the v1.0-rc4 formal-relation ledger superseding its older R/EMP taxonomy. The v1.1 package includes a current source-and-dependency ledger and restores the historical source-trace file retrieved from the research Library. The audited v1.0 Zenodo ZIP contained the repaired relation ledger and model tables but not that separately referenced v0.54 source-trace file. This packaging correction does not retroactively alter v1.0 or represent the old file as a new source audit.

For each theory \(T\), Paper II records an audit tuple:

\[
\mathcal A_T
=
(D_T,\Sigma_T,B_T,\mathcal T_T,R_T^{res},F_T,\mathfrak F_T,\Lambda_T,V_T),
\]

where \(D_T\) is the declared target domain, \(\Sigma_T\) the minimal distinctive signature, \(B_T\) the BAC-admissible bridge package, \(\mathcal T_T\) the translator, \(R_T^{res}\) the unrecovered commitments, \(F_T\) the formal relation/recovery class, \(\mathfrak F_T\) the explicit fidelity-failure conditions, \(\Lambda_T\) the relation labels, and \(V_T\) the empirical validation status.

A separate symbolic description-length proxy was used to test whether the shared UCT formalism actually compresses the nine theory descriptions. Six shared operator classes are reused 44 times, so shared formal reuse is real. However the net compression gain changes sign under conservative assumptions about shared-core and bridge cost.

Therefore the compression claim remains restricted to **shared formal reuse**, not demonstrated robust explanatory compression.

The required quantitative-reuse step has now been met at proof-of-concept level by the two fixed-parameter shared-law models in Sections 19 and 20. The next major scientific burden is preregistered held-out empirical recovery, comparison against relevant baselines, and evidence that any shared representation yields predictive or compression advantages beyond the toy-model setting.

---

# 22. Claim-status summary

| Paper II claim | Status |
|---|---|
| A common physically anchored mother formalism can express target-theory primitives | formal framework claim |
| Arbitrary lookup mappings do not count as unification | methodological criterion |
| TFR is required in addition to anti-triviality | methodological requirement |
| IIT formal quantities are conditionally reconstructible | F3 / REC / V0 |
| IIT exclusion ontology is compatible with UCT | no; F0 / CON under scoped A3 |
| RPT graph-recurrence primitive is exactly definable on a fixed chart | F4 primitive / V0 |
| GNWT global-access core is conditionally embeddable | F3 / EMB / V0 |
| HOT hierarchical causal-tracking primitive is exact | F4 primitive / V0; semantics not included |
| PP/AI is recoverable without model-semantics bridges | no |
| Temporal causal retention is exact/local | F4 primitive / V0; memory identity requires bridge |
| Strong MToC explicit-memory identity is accepted by UCT | no; F0 / CON under A1 plus an explicit nonuniversality witness |
| Nine-theory source fidelity is fully proven | no; working source-trace audit only |
| Shared formal reuse exists | yes |
| Robust full-theory compression is established | no |
| First DIT→RPT→GNWT shared-law model exists | yes, F3/V1 proof of concept |
| Second MToC→HOT→GNWT shared-law model exists | yes, F3/V1 proof of concept |
| Held-out empirical recovery (V3) has been achieved | no |
| Human-data validation has been achieved | no |
| UCT II proves the target theories true | no |

---

# 23. Reproducibility and release materials

The v1.1 release package preserves the available v1.0 model specifications, archived CSVs, relation/dependency records, and compression-sensitivity results unchanged. It additionally includes the restored historical source-trace ledger, a current compatibility/source ledger, the original UCT-I rc4 finite verifier, the new exact-transformation verifier, and an explicitly labeled numerical reimplementation of the two shared-law examples. The runnable v1.1 scripts and their results are included in the deposited audit ZIP, not merely mentioned in the paper.

The original model-generation script was not preserved in the located research artifacts. During the v1.0-rc3 prepublication audit, a **release-side reconstruction script** was therefore built from the archived equations and CSV outputs. This reconstruction is explicitly not represented as the original code.

Accordingly, Paper II claims a **fixed-parameter cross-output representation in the preserved specification and release-side reconstruction**. Because the original generation script and full development chronology are unavailable, the release audit does not independently certify the stronger historical claim that no parameter tuning of any kind occurred during the original construction process.

Under the declared five-consumer readout form for the first model, the archived outputs recover the fixed consumer-bias multiset

\[
\{-5.2,-5.1,-5.0,-4.9,-4.8\},
\]

with consumer gain 7. The same readout reproduces the archived second-model access scores. For the second model, the archived aggregate traces are reproduced by 39 state transitions after \(t=0\), with \(h_0=w_0=0\), as documented in the release-side audit script.

The earlier v1.0 release audit reported agreement across six core CSV files below \(10^{-9}\), with approximately \(6.7\times10^{-11}\) as its largest discrepancy. That is a historical audit claim. The separate v1.1 numerical reimplementation writes its own per-file errors, row counts, stopping conventions, and pass/fail results; its results are not silently substituted for those of the unavailable original generation script.

The physical model equations produce the same numerical outputs without invoking A1 or A5. Accordingly, their reproducibility is not independent evidence for universal experience or structural identity; it establishes the declared model consequences and permits scrutiny of their shared organization.

The delivered v1.1 reimplementation passed all seven archived CSV comparisons: 1,354 rows and 11,336 cells, including both control suites and the nine-row drive sweep. Its largest absolute numerical discrepancy was approximately \(6.674\times10^{-11}\), below the declared \(10^{-9}\) tolerance. Model 1 uses synchronous fixed-point iteration restarted at zero for each input, a maximum state-change tolerance of \(10^{-13}\), and a 20,000-iteration limit. Model 2 uses the 39 synchronous transitions stated above. These conventions reproduce the archived numbers but are not a recovered historical development chronology.

This audit supports reproducibility of the **reported toy-model numerical claims**. It does not turn the models into biological validation, does not establish V3/V4 empirical recovery, and does not establish that the reconstruction is byte-identical to the unavailable original generation code.

---

# 24. Conclusion

UCT II proposes a constrained form of theory unification.

It does not say that IIT, RPT, GNWT, HOT, PP/AI, DIT, MToC, AST, and TTC are all literally true descriptions of the same phenomenal boundary.

It says that identifiable operational mechanisms from these theories can be represented and classified inside one physically anchored process formalism.

The governing rule is:

\[
\boxed{
\text{mechanistic recovery}
\neq
\text{ontological endorsement}
\neq
\text{empirical confirmation}.
}
\]

If this framework is useful, its strongest future evidence will not be the existence of translation formulas, but quantitative compression, held-out recovery, and genuinely novel cross-theory predictions.

Two independent shared-law toy models now satisfy a minimal quantitative-reuse criterion at F3/V1, but neither constitutes held-out human-data recovery (V3), replicated effective recovery (V4), or robust full-theory compression. The framework is therefore offered as a constrained theoretical architecture and empirical research program, not as a replacement for experimental adjudication among consciousness theories.


---

# References

Albantakis, L., et al. (2023). Integrated information theory (IIT) 4.0: Formulating the properties of phenomenal existence in physical terms. *PLoS Computational Biology, 19*(10), e1011465. [doi:10.1371/journal.pcbi.1011465](https://doi.org/10.1371/journal.pcbi.1011465)

Aru, J., Suzuki, M., & Larkum, M. E. (2020). Cellular mechanisms of conscious processing. *Trends in Cognitive Sciences, 24*(10), 814–825. [doi:10.1016/j.tics.2020.07.006](https://doi.org/10.1016/j.tics.2020.07.006)

Blackmon, J. C. (2021). Integrated Information Theory, intrinsicality, and overlapping conscious systems. *Journal of Consciousness Studies, 28*(11–12), 31–53. [doi:10.53765/20512201.28.11.031](https://doi.org/10.53765/20512201.28.11.031)

Brown, R., Lau, H., & LeDoux, J. E. (2019). Understanding the higher-order approach to consciousness. *Trends in Cognitive Sciences, 23*(9), 754–768. [doi:10.1016/j.tics.2019.06.009](https://doi.org/10.1016/j.tics.2019.06.009)

Budson, A. E., & Paller, K. A. (2025). Memory, sleep, dreams, and consciousness: A perspective based on the Memory Theory of Consciousness. *Nature and Science of Sleep, 17*, 1957–1972. [doi:10.2147/NSS.S522975](https://doi.org/10.2147/NSS.S522975)

Budson, A. E., Richman, K. A., & Kensinger, E. A. (2022). Consciousness as a memory system. *Cognitive and Behavioral Neurology, 35*(4), 263–297. [doi:10.1097/WNN.0000000000000319](https://doi.org/10.1097/WNN.0000000000000319)

Chang, A. Y. C., Biehl, M., Yu, Y., & Kanai, R. (2020). Information Closure Theory of Consciousness. *Frontiers in Psychology, 11*, 1504. [doi:10.3389/fpsyg.2020.01504](https://doi.org/10.3389/fpsyg.2020.01504)

Cogitate Consortium, Ferrante, O., Gorska-Klimowska, U., et al. (2025). Adversarial testing of global neuronal workspace and integrated information theories of consciousness. *Nature, 642*, 133–142. [doi:10.1038/s41586-025-08888-1](https://doi.org/10.1038/s41586-025-08888-1)

Coward, L. A., & Sun, R. (2004). Criteria for an effective theory of consciousness and some preliminary attempts. *Consciousness and Cognition, 13*(2), 268–301. [doi:10.1016/j.concog.2003.09.002](https://doi.org/10.1016/j.concog.2003.09.002)

Dehaene, S., & Changeux, J.-P. (2011). Experimental and theoretical approaches to conscious processing. *Neuron, 70*(2), 200–227. [doi:10.1016/j.neuron.2011.03.018](https://doi.org/10.1016/j.neuron.2011.03.018)

Graziano, M. S. A., & Webb, T. W. (2015). The attention schema theory: A mechanistic account of subjective awareness. *Frontiers in Psychology, 6*, 500. [doi:10.3389/fpsyg.2015.00500](https://doi.org/10.3389/fpsyg.2015.00500)

Hodson, R., Mehta, M., & Smith, R. (2024). The empirical status of predictive coding and active inference. *Neuroscience & Biobehavioral Reviews, 157*, 105473. [doi:10.1016/j.neubiorev.2023.105473](https://doi.org/10.1016/j.neubiorev.2023.105473)

Huang, Z. (2023). Temporospatial nestedness in consciousness: An updated perspective on the Temporospatial Theory of Consciousness. *Entropy, 25*(7), 1074. [doi:10.3390/e25071074](https://doi.org/10.3390/e25071074)

Kanai, R., & Fujisawa, I. (2024). Toward a universal theory of consciousness. *Neuroscience of Consciousness, 2024*(1), niae022. [doi:10.1093/nc/niae022](https://doi.org/10.1093/nc/niae022)

Lamme, V. A. F. (2006). Towards a true neural stance on consciousness. *Trends in Cognitive Sciences, 10*(11), 494–501. [doi:10.1016/j.tics.2006.09.001](https://doi.org/10.1016/j.tics.2006.09.001)

Liu, H. (2026). *Unified Consciousness Theory I: Ontic Structure, Physical Views, and the Structural Continuity from Physical Process to Conceptual Self* (TA-TR-2026-20, v1.1). Zenodo. [doi:10.5281/zenodo.23030207](https://doi.org/10.5281/zenodo.23030207). Prior v1.0: [doi:10.5281/zenodo.23005588](https://doi.org/10.5281/zenodo.23005588)

Lopez, A., & Wiese, W. (2025). Building blocks for theories of consciousness. *Consciousness and Cognition, 134*, 103919. [doi:10.1016/j.concog.2025.103919](https://doi.org/10.1016/j.concog.2025.103919)

Mashour, G. A., Roelfsema, P., Changeux, J.-P., & Dehaene, S. (2020). Conscious processing and the global neuronal workspace hypothesis. *Neuron, 105*(5), 776–798. [doi:10.1016/j.neuron.2020.01.026](https://doi.org/10.1016/j.neuron.2020.01.026)

Northoff, G., & Huang, Z. (2017). How do the brain's time and space mediate consciousness and its different dimensions? Temporo-spatial theory of consciousness (TTC). *Neuroscience & Biobehavioral Reviews, 80*, 630–645. [doi:10.1016/j.neubiorev.2017.07.013](https://doi.org/10.1016/j.neubiorev.2017.07.013)

Northoff, G., & Zilio, F. (2022). Temporo-spatial Theory of Consciousness (TTC)—Bridging the gap of neuronal activity and phenomenal states. *Behavioural Brain Research, 424*, 113788. [doi:10.1016/j.bbr.2022.113788](https://doi.org/10.1016/j.bbr.2022.113788)

Pezzulo, G., Parr, T., & Friston, K. (2024). Active inference as a theory of sentient behavior. *Biological Psychology, 186*, 108741. [doi:10.1016/j.biopsycho.2023.108741](https://doi.org/10.1016/j.biopsycho.2023.108741)

Safron, A. (2022). Integrated world modeling theory expanded: Implications for the future of consciousness. *Frontiers in Computational Neuroscience, 16*, 642397. [doi:10.3389/fncom.2022.642397](https://doi.org/10.3389/fncom.2022.642397)

Safron, A., Klimaj, V., & Sheikhbahaee, Z. (2026). Integrated World Modeling Theory (IWMT) and the Human Consciousness Hypothesis (HCH). *Proceedings of the AAAI Symposium Series, 8*(1), 345–351. [doi:10.1609/aaaiss.v8i1.42564](https://doi.org/10.1609/aaaiss.v8i1.42564)

Seth, A. K., & Bayne, T. (2022). Theories of consciousness. *Nature Reviews Neuroscience, 23*, 439–452. [doi:10.1038/s41583-022-00587-4](https://doi.org/10.1038/s41583-022-00587-4)

Singhal, I., & Srinivasan, N. (2026). Just one moment: Unifying theories of consciousness based on a phenomenological “now” and temporal hierarchy. *Psychology of Consciousness: Theory, Research, and Practice, 13*(2), 283–299. [doi:10.1037/cns0000393](https://doi.org/10.1037/cns0000393)

Tonetto, B. (2026). *Theories of Consciousness: Constraints, Commitments, and Complementarity* [Preprint]. Zenodo. [doi:10.5281/zenodo.19068807](https://doi.org/10.5281/zenodo.19068807)

Wilterson, A. I., Kemper, C. M., Kim, N., Webb, T. W., Reblando, A. M., & Graziano, M. S. A. (2020). Attention control and the attention schema theory of consciousness. *Progress in Neurobiology, 195*, 101844. [doi:10.1016/j.pneurobio.2020.101844](https://doi.org/10.1016/j.pneurobio.2020.101844)

Winters, J. J. (2020). The temporally-integrated causality landscape: A theoretical framework for consciousness and meaning. *Consciousness and Cognition, 83*, 102976. [doi:10.1016/j.concog.2020.102976](https://doi.org/10.1016/j.concog.2020.102976)

Winters, J. J. (2021). The Temporally-Integrated Causality Landscape: Reconciling neuroscientific theories with the phenomenology of consciousness. *Frontiers in Human Neuroscience, 15*, 768459. [doi:10.3389/fnhum.2021.768459](https://doi.org/10.3389/fnhum.2021.768459)