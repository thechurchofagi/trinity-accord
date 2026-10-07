# Complete Organization, Selective Models, and Bearer-Relative Self-Attribution

Hongju Liu | Research extension R149 | 7 October 2026  
Unpublished theory note. The new result is a compatibility application of established factorization, not a claim of new general mathematics or independently established phenomenality.

## 1. A thought experiment that exposes a missing premise

Imagine two calculating devices that give the same answer on the displayed run. Their internal rules differ: one uses AND, the other XNOR. At input (1,1), both output 1; changing either input alone produces 0 in both. Changing both inputs to 0 distinguishes them. TA18 already supplies this construction. It proves that a trajectory or restricted probe record need not determine the selected causal structure.

Does it also prove that the two experiences differ? Not under an arbitrary bridge that merely assigns an experiential output to each causal structure. A constant bridge gives the same output to both. To infer a difference, a bridge must separate this pair. Under current UCT, C1-OI does separate different **complete actual organizational types**. But the AND/XNOR representation must first be shown to preserve a constitutive distinction of comparable actual bearers. If only one selected experiential feature is queried, even C1 need not make that feature differ.

This is the central integration question: when can a theory identify complete experience with actual organization while also treating some selected representation as sufficient for it?

## 2. Exact comparison contract

Fix a nonempty domain \(\Omega\) of admissible configurations. Each configuration specifies an actual comparison bearer, its interval, and the common complete structural signature. Write

\[
k:\Omega\to\mathcal K,\qquad e:\Omega\to\mathcal E
\]

for complete organizational and complete experiential **types**, respectively. They are not numerical token identities. Equality is equality of the appropriate isomorphism classes. All targets below refer to these same bearers and intervals. A change of bearer requires a new comparison contract.

Assume the C1-OI consequence

\[
k(\omega)=k(\omega')\quad\Longleftrightarrow\quad
e(\omega)=e(\omega'). \tag{1}
\]

This is inherited from A, conditional on C1 and the actual/completeness premises. It is not derived from a finite model. Fix any representation

\[
r:\Omega\to R.
\]

It may be a causal germ, capability profile, history record, self-model state, or joint collection of such descriptors. Its intended role must be stated; the theorem does not identify these roles with one another. Define

\[
\ker r=\{(\omega,\omega'):r(\omega)=r(\omega')\}.
\]

No assumption that \(r\) is itself an actual bearer is made. An arbitrary data summary is not promoted to one by notation.

## 3. The compatibility theorem

**Theorem (complete-target compatibility).** Under (1), the following conditions are equivalent:

1. There is a function \(h:r(\Omega)\to\mathcal E\) with \(e=h\circ r\).
2. \(\ker r\subseteq\ker k\).
3. There is a function \(a:r(\Omega)\to\mathcal K\) with \(k=a\circ r\).

The functions, when they exist, are unique on \(r(\Omega)\). If \(r\) is additionally a representation-invariant function of complete type, \(r=b\circ k\), all three conditions hold exactly when \(b\) is injective on \(k(\Omega)\).

**Proof.** For 1 to 2, equality of \(r\) implies equality of \(e\); (1) then implies equality of \(k\). For 2 to 3, define \(a(r(\omega))=k(\omega)\). Condition 2 makes this independent of the representative. For 3 to 1, (1) supplies a well-defined map \(F:k(\Omega)\to e(\Omega)\), \(F(k(\omega))=e(\omega)\); use \(h=F\circ a\). Surjectivity onto the displayed images gives uniqueness. If \(r=b\circ k\), condition 2 is exactly injectivity of \(b\) on the realized type image. \(\square\)

The domain qualification is essential. A barcode can distinguish two equal organizational types; then \(r\) need not be a function of \(k\). The first three clauses can still hold, but one must not claim \(\ker r=\ker k\) without the additional type-invariance premise. The theorem preserves that possibility instead of silently assuming every representation is an intrinsic property.

The theorem is TA15 Proposition 2 / C Proposition 2 applied to A:C1-OI. It is a new explicit compatibility check within this project, not a new factorization theorem. It establishes consistency of a **type-level sufficiency claim** with (1). It does not construct tokenwise identity, prove C1, assign familiar qualities, or provide a computable complete decoder.

### 3.1 A precise incompatible triple

The following three statements cannot all hold on the same comparison domain:

- complete organizational and experiential types obey (1);
- the representation \(r\) determines complete experiential type;
- some two configurations have equal \(r\) and different complete organizational types.

The witness in the third clause makes the contradiction immediate: the second gives equal experiential types and the first gives unequal experiential types. This is a conditional inconsistency test, not a finding that all nine source papers are inconsistent. The same bearer, interval, target completeness and actual grounding must be established before applying it.

### 3.2 Partial targets have a weaker obligation

For a selected target \(f:\Omega\to Y\), including a task score, battery state, self-location claim, or one calibrated phenomenal feature,

\[
f=\bar f\circ r
\quad\Longleftrightarrow\quad
\ker r\subseteq\ker f. \tag{2}
\]

This follows by defining \(\bar f\) on fibers exactly as in the proof above. It does not require \(\ker r\subseteq\ker k\). Thus a partial self-model can be wholly correct about its selected target while discarding many constitutive distinctions. Model incompleteness is not the same as inaccuracy on the modeled target.

An exact model of all declared future outputs is complete for that output contract. Calling those outputs “all relevant outputs” does not independently make their quotient complete for actual organization or experience. TA17's MECS remains explicitly task/intervention relative.

### 3.3 Null changes require a declared target

If an equivalence relation \(N\) is proposed as a family of changes that preserve complete experiential type under (1), consistency requires

\[
N\subseteq\ker k.
\]

Conversely that inclusion guarantees type preservation under (1). For one selected feature, only \(N\subseteq\ker f\) is required. Consequently “phenomenally null” cannot be moved without qualification between a selected feature, a macro bearer and a larger complete process. This precisely limits automatic import of TA18's null-equivalence quotient into A's full identity framework.

## 4. Repairing the TA18 inference without changing the published text

TA18 Proposition 1's intended germ counterexample first requires that its germ map \(\gamma\) retain the differing **joint** response, or equivalent mechanism information in \(\Theta_{\rm eff}\). The individual profiles in its displayed Definition 3 do not, by themselves, guarantee this: the example has equal single-input perturbation responses. With the joint distinction explicitly retained, \(\gamma\) does not factor through the chosen trajectory map \(H\). Its final assertion about phenomenology is still too strong if read as applying to every PRD bridge \(\Phi\). The correct alternatives are:

1. There exists an admissible germ-sensitive bridge for which \(\Phi\circ\gamma\) does not factor through \(H\), provided the bridge class allows separation of the witness pair.
2. For a particular bridge, nonfactorization follows if \(\Phi(\gamma_1)\ne\Phi(\gamma_2)\) for a same-trajectory witness.

Countermodel to the unrestricted inference: take \(H(0)=H(1)=0\), \(\gamma(0)=0\), \(\gamma(1)=1\), and \(\Phi(0)=\Phi(1)=c\). Then \(\gamma\) does not factor through \(H\), but \(\Phi\circ\gamma\) does. The constant bridge need not satisfy current C1 for different complete types; that is exactly why source-specific premise sets must not be silently merged.

Two additional qualifications enter the map. First, a function on raw germ encodings is not automatically invariant under germ isomorphism; TA18 Proposition 2 needs an isomorphism-respecting bridge or a domain already quotiented by that isomorphism. Second, postcomposing a bridge with a phenomenal automorphism demonstrates distinct raw functions only if the composite actually differs on the image and still satisfies the cross-scale constraints. Relabeling isomorphic experiential types alone does not establish physically different qualia. A two-class/two-output model with identity scale maps gives a direct nonuniqueness witness without that ambiguity.

The old publication bytes are preserved. These are working-map repairs and narrowed import statements, not a silently issued journal erratum.

## 5. A bearer-relative definition of modeled self-targets

Let \(\mathcal P_\omega\) be independently grounded actual tokens with a declared actual constituent relation \(\preceq_\omega\). It may permit nesting and overlap. It is not inferred from a self-report or from prediction accuracy. For a bearer \(b(\omega)\), a grounded target is a pair

\[
q(\omega)=(Q(\omega),f_{Q,\omega}),
\]

where \(Q(\omega)\) is the actual target token and \(f_{Q,\omega}\) its specified state or relational property. Target identity is not merely the current value of the property: two batteries at 50 percent are still distinct targets.

Record at least these different objects:

| Object | Meaning | What it does not establish |
|---|---|---|
| \(b,Q,\preceq\) | Actual bearer, target and constituent relation | That the system represents them |
| \(M^{\rm attr}\) | An installed attribution readout, following TA17's nonexclusive profile | That its assignment is correct |
| \(m,d\) | Installed representation and target predictor | General semantic understanding |
| \(\alpha\) | Real sensor, actuator and memory attachments | Phenomenal ownership |
| \(\varepsilon,\mathsf{Use}\) | Target error and declared causal use | Complete self-knowledge, beneficial use or fear |
| \(k,e\) | Complete actual and experiential types under C1 | Availability of those types to the predictor |

A modeled target is whole-bearer relative when \(Q=b\); a proper-constituent target when \(Q\prec b\). A disjoint external-tool target is external relative to this bearer. Overlapping targets and relations crossing the boundary require explicit additional descriptions; they must not be forced into a false exhaustive three-way partition. A target external to a person may be internal to a larger actual person-tool interaction. This change of comparison bearer does not prove that the person has ceased, that a single larger subject exists, or that every arbitrary composite is actual.

An erroneous attribution remains an actual installed attribution process. Calling it “not a self-model” whenever it is wrong would exclude the very cases the definition should explain. Operational misattribution can be measured only against a separately grounded target relation. The remaining semantic question—what makes a state about a target, rather than just correlated with it—is not solved by this tuple.

The total contract extends R146's \(\mathsf S\) with \(Q,\preceq,M^{\rm attr}\); it does not replace basal experience with accurate self-modeling. Within C1/U1, a mistake in an installed self-model does not imply that the actual bearer lacks experience. Whether that mistake is felt as ownership, alienation or anything else requires a selected phenomenal interpretation.

## 6. The four thought-experiment families apply the same criterion

### 6.1 All ancestors and the formation of every proposed gate

Keep every relevant intermediate available, including stages in the gradual formation of a proposed organizational condition. This motivates asking whether “first awareness” means any experience, a new discriminative capacity, a self-attribution mechanism, or a particular quality. The same word must not conceal a target switch. Under current C1/U1, actual intermediates do not acquire experience only when a new self-model becomes accurate. The physical trajectory alone does not prove C1 or continuity of a binary predicate; A's smooth-onset counterexample remains valid.

TA16's RRH-E is a historical conjecture about a proposed whole-level target. It cannot simply be imported as an additional necessary gate on all actual experience. If its target is basal existence and an actual token fails its right-hand condition, C1/U1 and that necessity claim conflict. If its target is a narrower kind of organization or whole-level feature, a new typed target must be stated. Neither a historical title nor similar vocabulary resolves the distinction.

### 6.2 The abacus and the electronic calculator

The calculator's arithmetic profile is an \(r\) selected for a task. It need not determine complete organization. A passive abacus's successful calculation belongs to the declared person-instrument execution; changing to the isolated frame changes the bearer. The compatibility theorem prohibits treating equal arithmetic answers as a complete experiential-type certificate while retaining constitutive differences.

A calculator may accurately represent its battery without representing every aspect of itself. Equation (2) allows exact target prediction without full reconstruction. This makes a modest self-monitoring claim precise without converting it into a conceptual “I.” Basal experience within UCT remains conditional on actual tokenhood and C1, independent of arithmetic skill.

### 6.3 The human formation executing an agent

The people, actual coordinated computation and represented algorithm are distinct objects. A participant's attribution can target that person's body; the implemented agent can track a constituent register or an ongoing whole-level task. Any claim of an actual whole requires the actual-process criterion. Participation in a larger process need not terminate a persisting constituent, by A:P3.

An algorithmic state shared with a silicon implementation is a candidate \(r\). If it identifies distinct complete types of the compared bearers, it cannot determine their complete experiential types under C1. It may still determine particular capabilities or selected features. Changing from complete physical organization to algorithm-relative structure is a change of explanatory target, not a proof of full equivalence. Neither the theorem nor the thought experiment establishes one exclusive subject for the human formation.

### 6.4 Copies, crossed connections and confident error

Use R147's two controllers and bodies. Actual containing-assembly assignment is \(\beta\), sensory binding \(\sigma\), and actuator binding \(\tau\). With independent command vectors, the full sensor law identifies \(L=\tau^{-1}\sigma\). Normal bindings and a common swap of both sensor and actuator bindings have the same \(L\), yet differ relative to fixed \(\beta\). A predictor may remain exactly correct about its closed loop while its claim that this loop is attached to its own assembly is false. Internal attribution \(M^{\rm attr}\) must not define the external ground truth \(\beta\).

For the sensor-law representation, the two configurations share \(r\). If the beta-retaining distinction is actual and constitutive for the same comparison bearer class, their complete types differ. The incompatible triple then rules out treating that \(r\) as a complete experiential specification. If beta is only an arbitrary analyst label, the grounding premise fails and no experiential-type difference follows by this route.

Copying autobiographical records does not establish current attachment or numerical identity. TA17's current membership, inheritance, successor belief, self-location and stake stay separate. R147's isolated-memory example is a restricted construction; actual memory can affect policy and recalibration when the corresponding causal paths are included.

## 7. What this advances and what remains open

The advance is a unified check on incompatible definitions and a precise distinction between complete identity, selective prediction and modeled self-attribution. It repairs a source inference and supplies one central compatibility result instead of proliferating unrelated small examples. The four thought-experiment families now serve distinct tests of the same contract: target, bearer, completeness, and grounding.

The factorization mathematics and the broad distinction between functional and phenomenal selfhood have substantial antecedents. A, C, TA15, TA16 and TA18 already contain the principal mathematical ingredients; TA17 already formalizes self-related objects. No historical priority or major breakthrough is certified. Independent original-paper readiness remains unestablished. The next substantive target is to justify an actual target/attachment criterion in a well-specified implementation class, including wrong attributions, without defining truth by the model's own success. General semantic aboutness and a specific felt-ownership bridge remain unresolved.

## Source basis

Primary fixed texts are listed in the [R148 inventory](../R148_Publication_Census_20261007/PUBLICATION_INVENTORY.json). Direct source obligations and proof repairs are indexed in [SOURCE_INTEGRATION_AND_AUDIT.md](SOURCE_INTEGRATION_AND_AUDIT.md). R146 and [R147](../R147_Self_Reference_Rewiring_20261007/SELF_REFERENCE_REWIRING.md) remain preserved. The theorem above uses A §4, C §3, TA15 §5.2, TA16 Appendix G.5 and TA18 §6.3. These are author-owned prior results; citations are source attribution, not independent corroboration. No biological experiments were conducted in R149.
