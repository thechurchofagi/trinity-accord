# Organization, Capability, and Experience: Definitions and Limits of Identification

R138 consolidation draft, 7 October 2026, Asia/Shanghai. Not a published paper or a new axiom system. Source basis: A / UCT I 1.2, B / UCT II 1.1, C / UCT III 1.0, D / TA-TR-2026-24 1.0; canonical proof content through R137. Parent commit: d4d9e72b0bd02d53ac257855419b995cc0a69ad6.

Source texts: [A 1.2](../R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md), [B 1.1](../R128_Unified_Formal_Map_Audit_20261006/sources/B_UCT_II_v1_1.md), [C 1.0](../R128_Unified_Formal_Map_Audit_20261006/sources/C_UCT_III_v1_0.md), [D / TA24 1.0](../R129_Four_Paper_Integration_20261006/sources/D_TA24_v1_0.md).

## 1. Decision and contribution boundary

Pause the automatic sequence of additional interface/control extensions. The immediate deliverable is a common definition contract and a small theorem spine. Existing mathematics is substantial enough for consolidation; a new research-paper contribution is not yet established merely by its volume.

Three distinctions govern the manuscript:

1. A mathematical definition fixes an object and its admissible comparisons.
2. A physical interpretation identifies an actual realization and the adequacy of its representation.
3. A consciousness-specific axiom gives an experiential interpretation. It is not proved by defining a symbol.

The present document restates and selects existing map results. It adds zero deductive nodes and zero rules. Editorial definition labels below are cross-reference handles, not new theorem IDs. Published source bytes and claims are preserved. Any later strengthening must receive a scoped map amendment and proof.

## 2. Core definition contract

### DC01. Actual process token

Work over a declared family of actual physical process occurrences, denoted by \(\mathcal P\). Follow A §§2.1–2.5: actual support, inherited physical relations, causal continuity, accountable boundaries, and traceable persistence or transformation. In A's finite classical example, a token is a physically grounded causal event subhistory satisfying those conditions. Merely calculating a feature or renaming a model does not create a physical token.

Tokens may overlap and nest. Neither a unique maximal subject nor autonomous Markov closure is an admission condition. The finite Markov models used below are a restricted scientific modeling class, not the universal definition of an experience-bearing process. Distinct occurrences may instantiate the same type; continuation and branching are separate lineage relations.

### DC02. Organization and organizational structure

Use **actual organization** for the instantiated distinctions and relations constitutive of the selected token. Use **organizational model** for their representation in a declared signature. These are two levels of description, not two independently acting substances.

A §3.1 writes the complete token-relative organization as \(D^{\mathrm{ontic}}_t(P)\). Completeness includes all distinctions constitutive of that token, not every microscopic fact anywhere in its substrate. This is a domain-level specification. It is not, by itself, a constructive universal procedure for deciding which physical distinctions are constitutive in an arbitrary brain or machine. That adequacy question must be answered for the chosen application, without introducing a new experience threshold or demanding an exclusive universal subject partition.

### DC03. A precise finite structural model

A §3.5 supplies a pointed, port-aware signature. Its deterministic finite example is

\[
\mathcal M_v=(X,x_\bullet,U,\mathcal J,Y,T,I,o,\mathscr C,\preceq).
\]

Here \(X\) is the state set, \(x_\bullet\) the current pointed state, \(U\) input ports, \(\mathcal J\) permitted reset/intervention ports, \(Y\) outputs, \(T_u:X\to X\) update maps, \(I_j:X\to X\) reset maps, \(o:X\to Y\) readout, and \(\mathscr C,\preceq\) declared constituent/incidence and temporal relations. The notation \(\mathcal J\) only avoids collision with the capability symbol \(J\); A's original uses \(J\) for the intervention sort.

The tuple is a model in a signature, not the signature itself. An admissible isomorphism has the necessary bijections and preserves pointing, operations and relations, in particular

\[
f_X(x_\bullet)=x'_\bullet,\quad
f_XT_u=T'_{f_U(u)}f_X,\quad
f_XI_j=I'_{f_{\mathcal J}(j)}f_X,\quad
f_Yo=o'f_X.
\]

Ports may be permuted only when the comparison permits it. A mechanism change, time reversal, lost intervention, or arbitrary mixing of constituent roles is not a mere coordinate rename. A wiring graph or transition law without the relevant current state is generally a less informative description. Stochastic dynamics below use joint kernels rather than pretending to be this deterministic tuple. Neither finite representation establishes complete physical constitution.

### DC04. Structural type, view and estimate

For a declared admissible model class and isomorphism relation, write the type as \([D]_{\cong}\); work in a fixed set-sized comparison domain when applying set-theoretic factorization. Type equality does not imply numerical token identity.

Following A §§3.2–3.3,

\[
D_v(P)=\Pi_v[D^{\mathrm{ontic}}(P)],\qquad
\widehat D_v(P\mid\mathcal E,\mathcal H)
\]

are respectively a physically anchored view and an estimate from evidence \(\mathcal E\) under model assumptions \(\mathcal H\). Declare time, horizon, grain, boundaries, interventions and retained relations in \(v\). Incomparable views are allowed. An identified set is appropriate when several models remain compatible with the evidence. Successful prediction does not turn a view into the complete organization.

### DC05. Experience

Retain A's experiential organization \(\Phi_{\mathcal K}(P)\) and its consciousness-specific identity axiom:

\[
\forall P\in\mathcal P,\quad
\exists\Phi_{\mathcal K}(P),h_P:
D^{\mathrm{ontic}}_{\mathcal K}(P)\cong\Phi_{\mathcal K}(P).
\]

The physical description and intrinsic experiential presentation refer to the same token-relative organization under C1. The experiential interpretation is part of the axiom; it is not derived from the existence of an isomorphic abstract object. The formalism does not add experience as a second causal input driving the physical dynamics.

Distinguish an experiential occurrence, its complete structural type, a selected experiential coordinate, and a scalar valuation of it. C1 is not a supplied algorithm assigning familiar phenomenal labels, pain, fear or a universal amount of experience to finite measurements.

### DC06. Consciousness terminology

For this draft, use **basal phenomenal consciousness** only for the existence of experience. As an editorial abbreviation, let \(C_{\mathrm{exp}}(P)=1\) mean that the distinguished experiential carrier is nonempty. A:U1 supplies this property for every admitted actual token, conditional on C1 and nonempty actual support.

Do not use this same predicate for wakefulness, perceptual access, metacognition, linguistic report, self-representation, or a scalar level. Those must be separately named organizational/operational targets. This convention is for the present manuscript; it does not redefine clinical uses of consciousness.

Within the UCT domain, the existence predicate is universal. Consequently the proposed comparative paper concerns organizational and experiential **types and selected properties**, not another test that admits or excludes actual processes from experience. This retains U1 rather than supplying new evidence for C1.

### DC07. Intelligence / capability

Follow C §2. For complete organizational type \(s\), and a fixed evaluation contract \(\mathcal M\),

\[
J_{\mathcal M}(s)=(J_\mu(s))_{\mu\in\mathcal M}.
\]

The contract specifies tasks, environments, resources, scoring, boundaries and any admissible adaptation. Each component must be invariant under allowed representation changes. Any omitted dependence must be fixed or incorporated into the domain. Distinct vectors need not be ordered; improvement requires a declared partial order or fixed objective. A sampled score is not a distributional capability.

Do not silently identify (a) performance of an installed mechanism/policy, (b) what an allowed controller can extract from a plant, and (c) what a modified or retrained system could achieve. R134–R137's externally optimized policy/interface results concern their explicitly defined composites. Calling those optima the original process's intrinsic intelligence needs additional physical and resource premises. This is a comparison safeguard, not a withdrawal of those control results.

No universal scalar intelligence definition is adopted here. A task-relative mathematical capability profile is already sufficient for the existing C theorems.

### DC08. Behavior and report

Specify a behavioral law relative to an input/interaction protocol, horizon and environment; distinguish that law from one realized trajectory. Reports are designated outputs or functions of the behavioral record under a stated semantic convention. Report content, report accuracy and report capability are separate objects.

Report is ordinarily a kind of behavior. Therefore the earlier slogan “experience != behavior != report” should be read as a warning against identification, not three mutually disjoint ontological classes. A first-person sentence alone does not identify its causal provenance or establish its experiential referent. C §2/§4 and D's evidence separation supply the source basis.

### DC09. Translation and equivalence

Keep three comparisons distinct: complete signature-preserving isomorphism; finite view/target sufficiency; and executable one-way policy transport. B §2.1 explicitly separates coordinate changes, mathematical operations, diagnostic mechanism changes and semantic bridges. B's BAC/TFR obligations remain in force for theory translations.

A successful decoder can preserve a projected interaction while omitting internal distinctions. It is not a complete organizational isomorphism. Do not build an unconditional total hierarchy of all possible equivalence notions: their protocols and retained variables can differ.

### DC10. Richness, unity, valence and selfhood

Any proposed coordinate requires a declared domain, invariance, ordering and interpretation. C1 does not select one metric or topology, and A:U2 only transports regularity within the specified common geometry. More nodes, more parameters, greater task accuracy, or stronger coupling is not automatically more experience or one exclusive subject.

D's continuation-control evidence concerns functional paths and declared targets. Its L7 does not establish L8 negative valence or L9 fear. No new self-access, report, recurrence, integration or self-preservation requirement is inserted into experience existence.

## 3. Minimal common comparison record

Every theorem application should state the following before comparing systems:

| Field | Required declaration |
|---|---|
| Object | Actual token, complete type, finite model, or estimate |
| Signature | States, pointing, ports, outputs, constituents and temporal relations retained |
| Context | Environment, laws, boundaries and omitted variables fixed or represented |
| Information | What the system/interface can actually observe, and when |
| Intervention | Allowed operations; coordinate change versus physical mechanism change |
| Policy/resources | Installed or optimized controller; memory, randomness, time and costs |
| Target | Full type, selected coordinate, path law, payoff, or scalar score |
| Status | Definition, C1-dependent conclusion, mathematical theorem, model example, or physical bridge |

This record is a documentation contract, not an added consciousness criterion.

## 4. Proposed three-result spine

### Main result 1: target-relative identification

Reuse C:P2_COORD/C:P2_FULL, with R131:TARGET_SPAN and R131:COMPLETE_LAW as finite certificates. The exact statement and proof are in PROOF_SPINE.md. The theorem tells us when observations determine a selected target and prevents conflating identification of one property with identification of the whole organization.

**Priority:** already published core plus classical factorization/linear algebra. Do not claim a new mathematical theorem.

### Main result 2: executable finite organizational abstraction

Reuse R137:LOCAL_LP and R137:CLOSED_LOOP under R137:CONTROL_MODEL, with R132:PARTIAL_CLOSURE as antecedent. The common decoder must preserve legal operations and joint controlled rows using actually available information. These conditions characterize its declared memoryless randomized interface class, and transport all projected adaptive finite-horizon policy laws.

**Priority:** post-publication project development; closely related established feedback refinement, probabilistic abstraction and controller transport. Its general mathematical novelty is not established. The sharp bounded obstruction may be a compact corollary, explicitly credited to Helly/Radon geometry.

### Main result 3: conditional capability/type implications

Reuse A:C1_OI, C:P1, C:P2_FULL and C:P3. A difference in a well-defined fixed capability profile implies a complete-type difference, and under C1 a complete experiential-type difference. Equal profiles identify full type only under the required injectivity. No scalar richness/valence ordering follows without a further coordinate relation.

**Priority:** published results, retained as the consciousness interpretation and boundary of the technical center. They are not independent confirmation of C1.

## 5. What this proposed paper would and would not contribute

The unifying question is: which actual organizational claims are warranted by capability, behavioral and intervention evidence, and which experiential conclusions remain conditional?

The working contribution is a consistent interface between four published foundations and the later finite executable certificates. It separates observational target identification, implementability under available information, and complete-type interpretation. It is not a proof that intelligence generates consciousness, an experiential scalar, or biological/AI T2 closure.

The existing C paper already distinguishes several kinds of sufficiency; B already requires constructive, non-oracular bridges; D already separates bundled behavior from mechanism. A new paper must acknowledge that overlap. If no sufficiently substantive extension beyond these papers and prior control literature remains after comparison, this document should become a technical synthesis or appendix, rather than a paper marketed as a major new theorem.

Use at most three representative counterexamples in the body: a many-to-one observation map; the hidden opposite-action decoder obstruction; and equal one-time marginals with unequal temporal joint laws. Keep the historical 38 named cases / 47 family crosswalk and auxiliary technical results in appendices. The complete thousands-case archive has not been recovered or re-audited.

## 6. Remaining obligations, in priority order

| Priority | Question | Deliverable needed | What is not required now |
|---|---|---|---|
| 1 | Are the same words used at the same mathematical level? | Adopt this definition contract; repair ambiguous manuscript sentences with source traceability | Another round of unrelated lemmas |
| 2 | Do the three selected statements retain all assumptions? | Proof spine with exact domains, legal policies, information access and counterlimits | Large numerical benchmarks |
| 3 | What is new beyond C/B/D and feedback-refinement literature? | Focused claim-by-claim comparison of the exact technical center | Broad unsupported originality claims |
| 4 | What makes a chosen model physically adequate? | One scoped token/view/implementation account, with omitted distinctions explicit | Universal exclusive subject selector |
| 5 | What selected experiential conclusion is intended? | State C1 dependence and any additional coordinate/valence bridge explicitly | An arbitrary universal consciousness score |

Definitions can be exact while physical adequacy remains open. This is not a reason to replace missing interpretation with more formal symbols. Conversely an open physical bridge does not invalidate a correctly scoped finite theorem.

## 7. Reading and review scope

This round checked A §§2–4 and the map's C1/U1/type statements; B §2/§2.1–2.3 and bridge distinctions; C §2 and the mapped §5 identification/type results; D §9/§11; the R131 catalog and the full R137 proof document. It did not re-read all four manuscripts line by line, rerun experiments, or complete a new exhaustive literature review. Prior map/source qualifications remain active. Review was by the same assistant, not independent peer review or proof-assistant certification.

Primary comparison sources already recorded in the project include Kleiner, Mathematical Models of Consciousness (2020), DOI 10.3390/e22060609; and Reissig, Weber and Rungger, Feedback Refinement Relations for the Synthesis of Symbolic Controllers (2017), DOI 10.1109/TAC.2016.2593947. These are antecedents, not evidence that the current manuscript has established originality.

Next action: edit a compact English manuscript around this spine and perform the focused overlap audit before promoting a new-paper contribution. Finite-memory interface research is parked unless that audit identifies a specific indispensable gap. T2 OPEN; biological/AI C3 intervention transport NOT_TESTED; valence OPEN.
