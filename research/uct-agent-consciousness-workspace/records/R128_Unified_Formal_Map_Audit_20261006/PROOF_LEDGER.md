# R128 — Complete formal-rule and node ledger

Generated from UCT_FORMAL_GRAPH.json. All premises in one rule are conjunctive. Alternative rules are separate. Consult source statements and the audit for full scope; sketches are not proof-assistant terms.

## a01: A:C1_OI

- Premises (all): `A:C1`
- Kind: DEDUCTIVE
- Claim: D(P)≅D(Q) iff Φ(P)≅Φ(Q) in the same complete signature
- Proof: Compose tokenwise isomorphisms and their inverses in either direction.
- Source: A §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a02: A:C1_W

- Premises (all): `A:C1_OI`
- Kind: DEDUCTIVE
- Claim: Complete physical equivalence implies full experiential equivalence
- Proof: Take forward implication.
- Source: A §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a03: A:U1

- Premises (all): `A:C1`, `A:NONEMPTY_CARRIER`
- Kind: DEDUCTIVE
- Claim: Every actual token has a nonempty distinguished experiential carrier
- Proof: Sort-preserving bijection preserves nonemptiness.
- Source: A §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a04: A:U2

- Premises (all): `A:C1`, `A:QSPACE`, `A:GEOMETRY`
- Kind: DEDUCTIVE
- Claim: Physical and experiential quotient-valued maps have identical continuity and distances
- Proof: The two maps are pointwise equal; use the same predeclared geometry.
- Source: A §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a05: A:U3

- Premises (all): `A:U1`, `A:SELF_WITNESS`
- Kind: DEDUCTIVE
- Claim: Conceptual selfhood is not necessary for basal experience in a domain containing the witness
- Proof: Apply U1 to the actual non-self witness.
- Source: A §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a06: A:U0

- Premises (all): `A:C1`, `A:P3`, `A:P6`, `A:U1`, `A:U2`, `A:U3`
- Kind: META_DEPENDENCY_RESULT
- Claim: Prior foundational roles have the stated derivation/ontology decomposition
- Proof: Collect prior derivations; preserve every context premise and witness.
- Source: A §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a07: A:ORG_GATE

- Premises (all): `A:U1`, `A:NONUNIV_WITNESS`
- Kind: DEDUCTIVE
- Claim: A mechanism absent at an actual same-domain witness cannot equal universal E=1
- Proof: At the witness, E=1 and candidate gate=0.
- Source: A §5.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a08: A:NO_HIDDEN

- Premises (all): `A:C1_W`, `A:COMPLETE_EQ`
- Kind: DEDUCTIVE
- Claim: No extra full-type phenomenal variation at fixed complete organization
- Proof: Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- Source: A §5.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a09: A:PROBE_INV

- Premises (all): `A:C1_W`, `A:COMPLETE_EQ`, `A:PROBE_ONLY`
- Kind: DEDUCTIVE
- Claim: Description/probe-choice-only change preserves full experiential type
- Proof: Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- Source: A §5.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a10: A:NO_FUTURE

- Premises (all): `A:C1_W`, `A:COMPLETE_EQ`, `A:FUTURE_ONLY`
- Kind: DEDUCTIVE
- Claim: Future-only divergence does not change present type if complete present organization is equal
- Proof: Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- Source: A §5.4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a11: A:GHOST_EQ

- Premises (all): `A:C1_W`, `A:COMPLETE_EQ`, `A:HISTORY_DIFF`
- Kind: DEDUCTIVE
- Claim: Screened history does not change current full experiential type
- Proof: Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- Source: A §5.5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a12: A:REWARD_NONID

- Premises (all): `A:C1_W`, `A:COMPLETE_EQ`, `A:LABEL_ONLY`
- Kind: DEDUCTIVE
- Claim: External reward-label change alone cannot change intrinsic phenomenal type
- Proof: Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- Source: A §5.6
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a13: A:GHOST_TOKEN_NOTE

- Premises (all): `A:GHOST_EQ`, `A:P6`, `A:HISTORY_DIFF`
- Kind: ONTOLOGICAL_ADDENDUM
- Claim: Equal current types do not identify numerical occurrences or causal lineages
- Proof: Type equivalence is distinct from numerical token identity by P6.
- Source: A §5.5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a14: A:NONSUM

- Premises (all): `A:C1`, `A:PRODUCT_DEF`, `A:ACTUAL_WHOLE_PARTS`, `A:PHYS_NONPRODUCT`
- Kind: DEDUCTIVE
- Claim: A nonproduct actual whole is not the specified independent product of experiential constituents
- Proof: Products in the common category preserve constituent isomorphisms; the opposite conclusion contradicts physical nonproduct.
- Source: A §6.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a15: A:MACRO_EXP_EQ

- Premises (all): `A:C1_W`, `A:MACRO_EQ`
- Kind: DEDUCTIVE
- Claim: Complete macro equivalence preserves macro experiential type
- Proof: Apply C1-W to the independently justified macro tokens.
- Source: A §6.4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a16: A:MICRO_EXP_DIFF

- Premises (all): `A:C1_OI`, `A:MICRO_NONISO`
- Kind: DEDUCTIVE
- Claim: Complete lower-token nonisomorphism entails lower experiential difference
- Proof: Contrapose the reverse equivalence.
- Source: A §6.4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a17: A:ORBIT_LEMMA

- Premises (all): `A:SYM_PREM`, `A:EQUIV_SELECTOR`
- Kind: DEDUCTIVE
- Claim: Invariant deterministic selected family is a union of candidate orbits
- Proof: If P selected then gP selected for each structure automorphism g.
- Source: A §7.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a18: A:SELECTION_OBSTRUCTION

- Premises (all): `A:ORBIT_LEMMA`, `A:OVERLAP_NONEMPTY_EXCL`
- Kind: DEDUCTIVE
- Claim: One overlapping candidate orbit admits no nonempty disjoint invariant selection
- Proof: One selected member forces the entire overlapping orbit.
- Source: A §7.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a19: A:E1

- Premises (all): `A:U1`, `A:ALL_ANC_ACTUAL`
- Kind: DEDUCTIVE
- Claim: E=1 throughout the admitted actual-token comparison family
- Proof: Apply U1 member by member; no continuity premise is needed.
- Source: A §8.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a20: A:E2

- Premises (all): `A:C1`, `A:QSPACE`, `A:GEOMETRY`, `A:EPS_CHAIN`
- Kind: DEDUCTIVE
- Claim: Physical epsilon-fine chains are equally fine experiential chains
- Proof: Replace each physical quotient point by its equal experiential point.
- Source: A §8.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a21: A:E3

- Premises (all): `A:CONNECTED_LAMBDA`, `A:CONT_BINARY_E`, `A:HUMAN_ENDPOINT`
- Kind: DEDUCTIVE
- Claim: A continuous discrete-valued E on a connected space, with E=1 somewhere, is identically one
- Proof: Continuous image connected; a nonempty connected subset of {0,1} is a singleton.
- Source: A §8.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a22: A:U2_APP

- Premises (all): `A:U2`, `A:PHYS_CONT_PATH`
- Kind: DEDUCTIVE
- Claim: A supplied continuous physical path has a continuous experiential path
- Proof: Use the U2 transfer with its physical-path premise.
- Source: A §8.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a23a: A:EVOL_SYNTH

- Premises (all): `A:E1`, `A:E2`
- Kind: CONDITIONAL_SYNTHESIS
- Claim: Nonempty experience throughout plus equally fine structural change
- Proof: Conjoin existence and fine-chain results; do not infer monotone richness.
- Source: A §8
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a23b: A:EVOL_SYNTH

- Premises (all): `A:E1`, `A:U2_APP`
- Kind: CONDITIONAL_SYNTHESIS
- Claim: Nonempty experience throughout plus equally continuous structural change
- Proof: Alternative route using a continuous path instead of a fine-chain premise.
- Source: A §8
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a24: A:STRUCT_TRANSFORM

- Premises (all): `A:C1_OI`, `A:PHYS_TRANSFORM_NONISO`
- Kind: DEDUCTIVE
- Claim: Actual complete structural transformation entails full experiential type change
- Proof: Contrapose full-type equivalence.
- Source: A §9
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a25: A:TOY_WHOLE_DIFF

- Premises (all): `A:TOY_MATH`
- Kind: DEDUCTIVE
- Claim: Specified register transition image sizes distinguish whole modeled types
- Proof: Over F2 the pair matrices have ranks 0,1,1,2; powers give 1,2→1,2→1,4 retained classes.
- Source: A §9 and Appendix B
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a26: A:TOY_SUB_EQ

- Premises (all): `A:TOY_MATH`
- Kind: DEDUCTIVE
- Claim: The specified s-process and declared output remain unchanged
- Proof: s+=s XOR u is independent of downstream pair; projection/reset diagram commutes.
- Source: A Appendix B
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a27: A:TOY_EXP_WHOLE

- Premises (all): `A:TOY_WHOLE_DIFF`, `A:ACTUAL_COMPLETE_TOY`, `A:C1_OI`
- Kind: DEDUCTIVE
- Claim: The actual complete whole realizations would differ experientially
- Proof: Apply C1-OI only after the actual/completeness premise.
- Source: A §9.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a28: A:TOY_EXP_SUB

- Premises (all): `A:TOY_SUB_EQ`, `A:ACTUAL_COMPLETE_TOY`, `A:C1_W`
- Kind: DEDUCTIVE
- Claim: The actual complete implemented sub-process realizations would agree in type
- Proof: Apply C1-W to that sub-process, not the entire network.
- Source: A §9.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a29: A:OSC_FWD

- Premises (all): `A:C1`, `A:BRIDGE_FWD`, `A:MEAS`
- Kind: ASSUMPTION_PACKAGE
- Claim: One-way operational correspondence is a package with an independently assumed forward bridge
- Proof: Package construction; finite prediction is supplied by the bridge, not deduced from full C1 alone.
- Source: A §10
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a30: A:OSC_TWO

- Premises (all): `A:C1`, `A:BRIDGE_FWD`, `A:BRIDGE_REV`, `A:MEAS`
- Kind: ASSUMPTION_PACKAGE
- Claim: Two-way operational correspondence additionally assumes reflection
- Proof: Lossy projection does not supply reflection.
- Source: A §10
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a31: A:FAIL_ONE

- Premises (all): `A:FROZEN_SCOPE`, `A:FORWARD_MISMATCH`, `A:MEAS`
- Kind: DEDUCTIVE
- Claim: A valid same-view/different-target case falsifies that forward bridge package
- Proof: It is a counterexample to the finite implication; does not isolate C1.
- Source: A §12.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a32: A:FAIL_TWO

- Premises (all): `A:FROZEN_SCOPE`, `A:REVERSE_MISMATCH`, `A:MEAS`
- Kind: DEDUCTIVE
- Claim: A valid different-view/same-target case falsifies the reflection direction
- Proof: It is a counterexample to reflection, not complete experiential equivalence evidence.
- Source: A §12.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a33: A:COEXISTENCE

- Premises (all): `A:P3`, `A:ACTUAL_PERSISTING_PARTS`, `A:U1`
- Kind: DEDUCTIVE
- Claim: Persisting nested actual tokens remain experience-bearing
- Proof: P3 retains tokenhood; U1 applies to each continuing token.
- Source: A §§2.4,6.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a34: A:COARSE_CLOSURE

- Premises (all): `A:FINITE_COARSE_SETUP`
- Kind: DEDUCTIVE
- Claim: A deterministic quotient exists iff equal summaries give equal successor summaries
- Proof: Necessity by equal arguments; sufficiency by representative-independent definition.
- Source: A Appendix D
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b01: B:REP

- Premises (all): `B:VIEW`, `B:LANGUAGE`, `B:BAC`, `B:EXPRESSIBLE`
- Kind: DEDUCTIVE
- Claim: A translator evaluates all declared admissible expressions
- Proof: Structural induction: leaves are admitted inputs/constants; each typed primitive composes previously defined values.
- Source: B §4.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b02: B:GATE

- Premises (all): `A:U1`, `B:TARGET_DOMAIN`
- Kind: DEDUCTIVE
- Claim: The stipulated universal rival gate conflicts at its admitted witness
- Proof: E=1 but the necessary gate is absent; a witness outside the rival domain does not work.
- Source: B §5.5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b03: B:EXCLUSION_CONFLICT

- Premises (all): `A:P3`, `A:U1`, `B:OVERLAP_WITNESS`
- Kind: DEDUCTIVE
- Claim: Overlap/nonmaximality alone cannot erase a persisting token's UCT experience
- Proof: P3 preserves the actual token; U1 gives nonempty experience, contrary to the scoped rival assignment.
- Source: B §6
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b_IIT: B:IIT

- Premises (all): `B:VIEW`, `B:BAC`, `B:TFR`, `B:IIT_BRIDGE`
- Kind: CONDITIONAL_TRANSLATION
- Claim: Conditional IIT mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §6
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b_RPT: B:RPT

- Premises (all): `B:VIEW`, `B:BAC`, `B:TFR`, `B:RPT_BRIDGE`
- Kind: CONDITIONAL_TRANSLATION
- Claim: Conditional RPT mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §7
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b_GNWT: B:GNWT

- Premises (all): `B:VIEW`, `B:BAC`, `B:TFR`, `B:GNWT_BRIDGE`
- Kind: CONDITIONAL_TRANSLATION
- Claim: Conditional GNWT mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §8
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b_HOT: B:HOT

- Premises (all): `B:VIEW`, `B:BAC`, `B:TFR`, `B:HOT_BRIDGE`
- Kind: CONDITIONAL_TRANSLATION
- Claim: Conditional HOT mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §9
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b_AST: B:AST

- Premises (all): `B:VIEW`, `B:BAC`, `B:TFR`, `B:AST_BRIDGE`
- Kind: CONDITIONAL_TRANSLATION
- Claim: Conditional AST mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §9
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b_PP_AI: B:PP_AI

- Premises (all): `B:VIEW`, `B:BAC`, `B:TFR`, `B:PP_AI_BRIDGE`
- Kind: CONDITIONAL_TRANSLATION
- Claim: Conditional PP_AI mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §10
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b_DIT: B:DIT

- Premises (all): `B:VIEW`, `B:BAC`, `B:TFR`, `B:DIT_BRIDGE`
- Kind: CONDITIONAL_TRANSLATION
- Claim: Conditional DIT mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §11
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b_MTOC: B:MTOC

- Premises (all): `B:VIEW`, `B:BAC`, `B:TFR`, `B:MTOC_BRIDGE`
- Kind: CONDITIONAL_TRANSLATION
- Claim: Conditional MTOC mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §12
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b_TTC: B:TTC

- Premises (all): `B:VIEW`, `B:BAC`, `B:TFR`, `B:TTC_BRIDGE`
- Kind: CONDITIONAL_TRANSLATION
- Claim: Conditional TTC mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §13
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b04: B:CYCLE_PRIMITIVE

- Premises (all): `B:GRAPH`
- Kind: DEDUCTIVE
- Claim: A vertex is on a directed cycle iff it lies in an SCC with at least two vertices or has a self-loop
- Proof: Positive cycle implies mutual reachability; mutual reachability of distinct vertices gives a closed walk containing a cycle; handle singleton self-loops separately.
- Source: B §7 / R128
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b05: B:EDGE_CYCLE

- Premises (all): `B:GRAPH`, `B:NEW_EDGE_RETURN`
- Kind: DEDUCTIVE
- Claim: A newly added edge lies in a directed cycle iff the old graph has its reverse-direction return path
- Proof: Remove new edge from cycle to get path; concatenate path with edge for converse.
- Source: B §16
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b06: B:SPECTRAL

- Premises (all): `B:MODEL19`
- Kind: DEDUCTIVE
- Claim: rho=sqrt(6q); rho=1 at g=0.5-log(5)/10; cycle exists for all finite stated g
- Proof: Eigenvalues of [[0,2],[3q,0]] are ±sqrt(6q); invert q=sigmoid(10(g-.5)); q>0.
- Source: B §19.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## b07: B:RECURRENCE_ENABLES

- Premises (all): `B:MODEL19`, `B:NONLINEAR_WORKSPACE`
- Kind: CONDITIONAL_ENABLING
- Claim: Nonlinear stability must use the state-dependent Jacobian, not just weighted connectivity
- Proof: Differentiate sigmoid updates; slopes include x_i(1-x_i), so structural radius alone does not determine dynamical stability.
- Source: B §§16,19
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a35: A:UCTII_RECON

- Premises (all): `B:VIEW`, `B:BAC`, `B:TFR`, `B:REP`
- Kind: DEDUCTIVE
- Claim: UCT II's formal reconstruction has no C1/U1 premise
- Proof: Typed translator uses physical inputs and supplied conventions; identity is an optional subsequent interpretation.
- Source: A §16.1; B §§2–5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a36: A:UCTII_GATE

- Premises (all): `A:U1`, `B:TARGET_DOMAIN`
- Kind: DEDUCTIVE
- Claim: UCT II gate relocation uses U1 and a scoped witness
- Proof: Apply b02.
- Source: A §16.1; B §5.5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a37: A:NONEMPTY_CARRIER

- Premises (all): `A:ACTUAL_TOKEN`
- Kind: DEDUCTIVE
- Claim: An admitted actual token has nonempty constitutive support
- Proof: This is part of the declared actual-token ontology, not a data-derived consciousness claim.
- Source: A §2.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c01: C:P1

- Premises (all): `A:C1_OI`, `C:FIXED_J`
- Kind: DEDUCTIVE
- Claim: J(s)≠J(t) implies different full experiential type; strict fiber inclusion iff J noninjective
- Proof: Equal complete types have equal J; contrapose. Strictness is exactly a repeated J value on distinct types.
- Source: C §5.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c02: C:P2_COORD

- Premises (all): `C:SET_MAPS`
- Kind: DEDUCTIVE
- Claim: C factors through J iff J(s)=J(t) implies C(s)=C(t)
- Proof: Define recovered value on each fiber; it is representative-independent exactly under the stated condition.
- Source: C §5.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c03: C:P2_FULL

- Premises (all): `A:C1_OI`, `C:FIXED_J`, `C:P2_COORD`
- Kind: DEDUCTIVE
- Claim: J identifies full experiential type throughout the domain iff J is injective
- Proof: Full C1 type equivalence identifies distinct structural types with distinct experiential types.
- Source: C §5.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c04: C:OBS_REFINEMENT

- Premises (all): `C:SET_MAPS`
- Kind: DEDUCTIVE
- Claim: F_(A,R)(s)=F_A(s)∩F_R(s); refinement strict only when R splits an A-fiber
- Proof: Equality of ordered pairs is coordinatewise equality.
- Source: C §5.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c05: C:LOCAL_FIBER

- Premises (all): `C:CONST_RANK`
- Kind: DEDUCTIVE
- Claim: Locally constant rank gives local fibers of dimension n-r
- Proof: Apply the constant-rank normal form; pointwise rank at a singularity is insufficient.
- Source: C §5.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c06: C:P3

- Premises (all): `C:PAIR_COUNTERMODEL`
- Kind: DEDUCTIVE
- Claim: The C1-compatible model increases J while decreasing C
- Proof: Direct substitution verifies the premises and falsifies the unrestricted conclusion; coordinate is not asserted to measure real richness.
- Source: C §5.4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c07: C:P4

- Premises (all): `C:SMOOTH_FITNESS`
- Kind: DEDUCTIVE
- Claim: v∈ker DJ gives DwI[v]=0; exact constant-J path keeps wI constant
- Proof: Chain rule gives first result; function composition gives second. First-order null is not finite neutrality.
- Source: C §6.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c08: C:P5

- Premises (all): `C:SELECTION`, `C:CLASS_WEIGHTS`
- Kind: DEDUCTIVE
- Claim: p+(s|J=j)=p(s|J=j) for surviving classes
- Proof: Divide reweighted state mass by reweighted class mass; common factor cancels.
- Source: C §6.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c09: C:PRICE_SELECTION

- Premises (all): `C:SELECTION`
- Kind: DEDUCTIVE
- Claim: ΔEC=Cov(W,C)/EW; if W=f(J), covariance depends on E[C|J]
- Proof: Expand the reweighted expectation; use conditional expectation for class-constant weights.
- Source: C §6.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c10: C:PRICE_TRANSMISSION

- Premises (all): `C:SELECTION`, `C:DESCENDANT_ATTRIBUTION`
- Kind: DEDUCTIVE
- Claim: ΔEC=Cov(W,C)/EW+E[W(C'_s-C(s))]/EW
- Proof: Add and subtract E[WC]/EW. This is accounting, not a closed dynamics law.
- Source: C §6.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c11: C:P6

- Premises (all): `C:MARKOV_SELECTION`
- Kind: DEDUCTIVE
- Claim: Projected capability dynamics close iff every destination-class probability is constant on each current class
- Proof: Sufficiency groups row sums; necessity compares point masses in the same class, whose positive weights cancel.
- Source: C §6.4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c12: C:P7

- Premises (all): `C:DECISION`
- Kind: DEDUCTIVE
- Claim: V_XM≥V_X, with equality iff each supported X has a common optimal action for all supported M
- Proof: Write improvement as average nonnegative regret of a baseline-optimal action. Zero sum forces every supported regret to vanish.
- Source: C §7.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c13: C:CIRCUIT_LAWS

- Premises (all): `C:CIRCUIT_SPEC`
- Kind: DEDUCTIVE
- Claim: Unmasked readout accuracy 1-epsilon; masked/current-input accuracy 1/2; mutation gain mu(1/2-epsilon)
- Proof: Independence and XOR make the mask a fair one-time randomizer; average the two mutation outcomes.
- Source: C §7.2; Appendix C
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c14: C:MEMORY_VALUE

- Premises (all): `C:ENV_MEMORY`, `C:DECISION`
- Kind: DEDUCTIVE
- Claim: V=1/2+|2alpha-1|(1/2-epsilon)
- Proof: Match probability q=alpha(1-epsilon)+(1-alpha)epsilon; optimal binary action attains max(q,1-q).
- Source: C §7.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c15: C:MEMORY_SELECTION

- Premises (all): `C:MEMORY_COST`, `C:SELECTION`
- Kind: DEDUCTIVE
- Claim: Memory frequency increases exactly when its stipulated weight exceeds the alternative
- Proof: For two positive types, reweighting increases the first iff W1>W0; subtract weights.
- Source: C §7.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c16: C:REPERTOIRE

- Premises (all): `A:C1`, `C:ACTUAL_ENSEMBLE`
- Kind: DEDUCTIVE
- Claim: R_D=R_Φ and their images/frontiers coincide; no time-monotonicity follows
- Proof: Elementwise C1 equality followed by the same map and partial order.
- Source: C §8.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c17: C:SENSORY_PARTITION

- Premises (all): `A:C1_OI`, `C:ACTUAL_INDEX_FAMILY`
- Kind: DEDUCTIVE
- Claim: Physical and experiential full-type equality partitions coincide
- Proof: Substitute type equivalence; strict refinement transfers on the same index set.
- Source: C Appendix E
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c18: C:RIVAL_CONTRAST

- Premises (all): `A:C1_OI`, `B:TFR`, `C:RIVAL_DESCRIPTOR`
- Kind: DEDUCTIVE
- Claim: UCT separates the pair while the stipulated rival assignment does not
- Proof: C1-OI separates unequal full types; rival descriptor equality forces its assigned equality.
- Source: C §9.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c19: C:RIVAL_NESIG

- Premises (all): `C:SET_MAPS`, `C:P2_COORD`
- Kind: DEDUCTIVE
- Claim: Unequal J entails unequal rival assignment iff J constant on rival fibers
- Proof: Contraposition plus representative-independent factorization; no C1 truth premise needed.
- Source: C §9.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c20: C:SCORE_TV

- Premises (all): `C:TRANSCRIPT`
- Kind: DEDUCTIVE
- Claim: |EP h-EQ h|≤TV(P,Q)
- Proof: Positive and negative parts of P-Q each have mass TV; h lies between zero and one.
- Source: C §9.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c21: C:LOGLOSS

- Premises (all): `C:FINITE_LOSS`
- Kind: DEDUCTIVE
- Claim: L(qZ)-L(qZR)=I(Y;R|Z)+KZ-KZR
- Proof: Each finite log loss is conditional entropy plus conditional KL; subtract.
- Source: C Appendix B
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c22: C:RESIDUAL_BOUND

- Premises (all): `C:FINITE_LOSS`, `C:NUISANCE_BOUNDS`, `C:LOGLOSS`
- Kind: DEDUCTIVE
- Claim: I(Y;R|Z)≤u+d, hence fitted gain≤u+d+eta
- Proof: Add A* in mutual information; chain rule and finite entropy bound; discard nonnegative KZR.
- Source: C Appendix B
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c23: C:PROFILE_PSEUDOMETRIC

- Premises (all): `C:TV_PROFILES`
- Kind: DEDUCTIVE
- Claim: Nonnegative weighted sum of TVs satisfies symmetry and triangle inequality; distinct states may have zero distance
- Proof: Apply TV metric properties coordinatewise.
- Source: C §10.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## c24: C:PUBLIC_NULL

- Premises (all): `C:PUBLIC_NULL_PREMISE`
- Kind: DEDUCTIVE
- Claim: Independent public-only binary guessing succeeds with probability 1/2
- Proof: Condition on the full public record/decision; target remains fair.
- Source: C §10.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r126_1: R126:P1

- Premises (all): `A:C1`, `R126:PROJECTION`
- Kind: DEDUCTIVE
- Claim: pE=p∘Phi^-1 gives pE∘Phi=p for every p
- Proof: Substitution and inverse identity. Since p was arbitrary the equality cannot by itself select actual support.
- Source: R126 theory note §3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r126_2: R126:P2

- Premises (all): `R126:MODEL`
- Kind: DEDUCTIVE
- Claim: A quotient update/output exists iff its next summary/output is constant on each current fiber
- Proof: Necessity by equal arguments; sufficiency by representative-independent definition.
- Source: R126 theory note §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r126_3: R126:P3

- Premises (all): `R126:MODEL`, `R126:METRIC`
- Kind: DEDUCTIVE
- Claim: Worst-case summary prediction error in a fiber is at least half the successor diameter
- Proof: Triangle inequality for the farthest pair. Necessity, not general sufficiency.
- Source: R126 theory note §5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r126_4: R126:P4

- Premises (all): `R126:MODEL`, `R126:P2`
- Kind: DEDUCTIVE
- Claim: Refine output fibers by successor classes; at most N-b0 strict stages; terminal equivalence is coarsest stable refinement
- Proof: Each strict stage increases class count; any stable refinement remains finer by induction.
- Source: R126 theory note §6
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r127_1: R127:P1

- Premises (all): `R127:TASK`
- Kind: DEDUCTIVE
- Claim: Exact answer factorization iff encoder separates all unequal response profiles; code size≥number of profiles
- Proof: Equal code forces equal outputs for every q; otherwise define decoder on image by representatives.
- Source: R127 theory note §3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r127_1a: R127:QUERY_REFINEMENT

- Premises (all): `R127:TASK`
- Kind: DEDUCTIVE
- Claim: Equality on Q2 entails equality on subset Q1
- Proof: Restrict universally quantified queries.
- Source: R127 theory note §3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r127_1b: R127:FUTURE_EQ

- Premises (all): `R126:MODEL`, `R126:P4`
- Kind: DEDUCTIVE
- Claim: Two states are equivalent iff outputs agree after every finite operation word, including the empty word
- Proof: Future-word equivalence is stable and refines outputs; all stable refinements preserve future outputs by induction.
- Source: R127 theory note §3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r127_2: R127:P2

- Premises (all): `R127:TASK`, `R127:MEDIATION`
- Kind: DEDUCTIVE
- Claim: For differing correct answers TV(mu_x,mu_xprime)≥1−epsilon_x−epsilon_xprime
- Proof: Shared kernel contracts TV; correct-answer event lower-bounds output TV. Exact finite case forces disjoint cut supports.
- Source: R127 theory note §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r127_3: R127:P3

- Premises (all): `R127:RECOVERY`
- Kind: DEDUCTIVE
- Claim: I(X;C|B)≥H(X|B)−h2(epsilon)−epsilon log2(m−1); for finite C this is at most log2|C|
- Proof: Conditional data processing followed by Fano error-indicator decomposition.
- Source: R127 theory note §5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r127_3a: R127:JOINT_INFORMATION

- Premises (all): `R127:PAIR_MODEL`
- Kind: DEDUCTIVE
- Claim: I(X;C)=I(X;B)=0, I(X;C,B)=1 bit
- Proof: Fair mask makes each marginal independent of X; XOR of both recovers X.
- Source: R127 theory note §5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r127_3b: R127:LOCALIZATION_LIMIT

- Premises (all): `R127:LOCALIZATION_PAIR`
- Kind: DEDUCTIVE
- Claim: Any interface-law-only identification rule agrees on the pair, so cannot identify both different storage locations
- Proof: Equal inputs to rule have equal outputs; locations differ by supplied construction.
- Source: R127 theory note §6
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r127_4: R127:P4

- Premises (all): `A:ACTUAL_TOKEN`, `R127:EVENT_SUPPORT`
- Kind: DEFINITION_APPLICATION
- Claim: Selected grounded subhistory meets A §2.5 actual-token conditions
- Proof: Actual support, inherited relations, causal continuity, boundary accountability and traceability each supplied. Definition application, not new existence threshold.
- Source: R127 theory note §7
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## r127_5: R127:P5

- Premises (all): `A:C1`, `R127:RELATIONAL_SUPPORT`
- Kind: DEDUCTIVE
- Claim: For retained actual relation R and tuple a, R^D(a) iff R^Phi(h(a))
- Proof: Restrict a relation-preserving and reflecting isomorphism. Operations need closed subdomains/ports; no automatic subalgebra or independent subject.
- Source: R127 theory note §8
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## a38: A:UCTII_EXP

- Premises (all): `A:C1`, `B:REP`, `B:BAC`, `B:TFR`, `R127:RELATIONAL_SUPPORT`, `R127:P5`
- Kind: CONDITIONAL_INTERPRETATION
- Claim: A source-faithful finite reconstruction has selected experiential interpretation only where its relations are independently grounded in actual constitutive organization
- Proof: B translation alone does not establish the physical premise. Once grounded, use the isomorphism restriction.
- Source: R127 theory note §8; A Appendix C; B §5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## n128_1: N128:DET_JOIN

- Premises (all): `R126:P2`, `N128:COMMON_DETERMINISTIC`
- Kind: DEDUCTIVE
- Claim: Joint summary update is the pair of component updates on its image
- Proof: Equality of current pairs implies equality of successor pairs; choose representative to prove image invariance.
- Source: R128 joint-state derivation §2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## n128_2: N128:MARKOV_JOIN

- Premises (all): `N128:MARKOV_WITNESS`
- Kind: DEDUCTIVE
- Claim: p1=x and p2=y close; (x,y) fails on all 8 states; closes on invariant 4-state restriction; full-domain stable refinement needs 8 blocks
- Proof: Each next marginal is fair; z selects equal vs unequal next pairs despite equal current pair. Every pair block must split by z.
- Source: R128 joint-state derivation §3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## n128_3: N128:JOINT_CRITERION

- Premises (all): `N128:KERNEL`
- Kind: DEDUCTIVE
- Claim: Joint law p_*K_a must be constant within each present joint-summary fiber
- Proof: Necessity by equal summary arguments; sufficiency by well-defined row assignment.
- Source: R128 joint-state derivation §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## n128_4: N128:INDEPENDENCE_SUFFICES

- Premises (all): `N128:KERNEL`, `N128:PRODUCT_LAW`, `N128:JOINT_CRITERION`
- Kind: DEDUCTIVE
- Claim: Products of closed marginal laws give a closed joint law; a fixed (U,U) joint law shows independence is unnecessary
- Proof: Product depends only on current pair; fixed correlated law depends on no hidden state.
- Source: R128 joint-state derivation §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## n128_5: N128:SEPARATION

- Premises (all): `C:OBS_REFINEMENT`, `N128:MARKOV_JOIN`
- Kind: DEDUCTIVE
- Claim: More identifying information does not by itself imply joint dynamic closure
- Proof: Joint fibers refine both coordinate fibers, but explicit next-joint laws disagree within a joint fiber.
- Source: R128 joint-state derivation §5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Node inventory

| ID | Kind / status | Meaning and scope | Source |
|---|---|---|---|
| A:TOKEN_CRITERIA | ONTO_DEF; DECLARED_CONTEXT_OR_METHOD | Actual-token criteria | A Appendix C |
| A:ACTUAL_TOKEN | ONTO_DOMAIN; DECLARED_CONTEXT_OR_METHOD | Actual valid process token — Admitted actual valid P, specified interval and boundary; A §2 actual-support/inherited-relations/continuity/accountability/traceability criteria. No claim that an arbitrary variable satisfies them. | A Appendix C |
| A:NONEMPTY_CARRIER | ONTO_CONSEQ; MANUAL_CONDITIONAL_PASS | Nonempty constitutive carrier | A Appendix C |
| A:P3 | ONTO_RULE; DECLARED_CONTEXT_OR_METHOD | Persistence / cessation / embedding | A Appendix C |
| A:P6 | ONTO_DEF; DECLARED_CONTEXT_OR_METHOD | Token / type / lineage | A Appendix C |
| A:D_ONTIC | DEF; DECLARED_CONTEXT_OR_METHOD | Complete token-relative ontic organization | A Appendix C |
| A:K | DEF; DECLARED_CONTEXT_OR_METHOD | Common structural signature K | A Appendix C |
| A:QSPACE | DEF; DECLARED_CONTEXT_OR_METHOD | Structural-type quotient space | A Appendix C |
| A:GEOMETRY | METHOD_DEF; DECLARED_CONTEXT_OR_METHOD | Predeclared invariant topology / pseudometric — One predeclared common topology or pseudometric on the structural-type quotient; no empirically established unique metric assumed. | A Appendix C |
| A:VIEW | EPI_DEF; DECLARED_CONTEXT_OR_METHOD | Finite physical view D_v | A Appendix C |
| A:ESTIMATE | EPI_DEF; DECLARED_CONTEXT_OR_METHOD | Scientific estimate D-hat_v | A Appendix C |
| A:SUBJECT_FIREWALL | BOUNDARY; DECLARED_CONTEXT_OR_METHOD | Experience-bearing process != canonical subject | A Appendix C |
| A:C1 | AX_C; FIXED_AXIOM | Structural-Experiential Identity | A §4 |
| A:C1_OI | LEMMA; MANUAL_CONDITIONAL_PASS | Pairwise type equivalence | A §4 |
| A:C1_W | LEMMA; MANUAL_CONDITIONAL_PASS | One-way phenomenal completeness | A §4 |
| A:U1 | THM; MANUAL_CONDITIONAL_PASS | Universal Nonempty Experience | A §4 |
| A:U2 | THM; MANUAL_CONDITIONAL_PASS | Structural Continuity transfer | A §4 |
| A:SELF_WITNESS | EMP_WITNESS; DECLARED_CONTEXT_OR_METHOD | Actual non-self token witness — An actual valid token in the admitted domain lacks conceptual selfhood. | A Appendix C |
| A:U3 | COR; MANUAL_CONDITIONAL_PASS | Selfhood Non-Prerequisite | A §4 |
| A:U0 | META_THM; META_DEPENDENCY_RESULT | Foundational Compression | A §4 |
| A:NONUNIV_WITNESS | EMP_WITNESS; DECLARED_CONTEXT_OR_METHOD | Nonuniversality witness — An actual valid token in the SAME domain lacks the proposed organization gate. | A Appendix C |
| A:ORG_GATE | THM; MANUAL_CONDITIONAL_PASS | Organization-Gate Impossibility | A Appendix C |
| A:COMPLETE_EQ | PREMISE; DECLARED_ASSUMPTION | Complete current ontic equivalence — Same current complete token-relative ontic organization in the common signature, not merely equal observations. | A Appendix C |
| A:PROBE_ONLY | PREMISE; DECLARED_ASSUMPTION | Only external probe choice changes | A Appendix C |
| A:FUTURE_ONLY | PREMISE; DECLARED_ASSUMPTION | Only future divergence changes | A Appendix C |
| A:HISTORY_DIFF | PREMISE; DECLARED_ASSUMPTION | Different histories — Different histories with all current constitutive consequences screened; numerical token/lineage may still differ. | A Appendix C |
| A:LABEL_ONLY | PREMISE; DECLARED_ASSUMPTION | Only external label changes | A Appendix C |
| A:NO_HIDDEN | THM; MANUAL_CONDITIONAL_PASS | No Hidden Quale | A Appendix C |
| A:PROBE_INV | THM; MANUAL_CONDITIONAL_PASS | Probe Invariance | A Appendix C |
| A:NO_FUTURE | THM; MANUAL_CONDITIONAL_PASS | No Future Contamination | A Appendix C |
| A:GHOST_EQ | THM; MANUAL_CONDITIONAL_PASS | Causally Screened History experiential equivalence | A Appendix C |
| A:GHOST_TOKEN_NOTE | COR; ONTOLOGICAL_ADDENDUM | Numerically distinct tokens may remain | A Appendix C |
| A:REWARD_NONID | THM; MANUAL_CONDITIONAL_PASS | External reward-label non-identity | A Appendix C |
| A:PRODUCT_DEF | DEF; DECLARED_CONTEXT_OR_METHOD | Declared independent constituent product | A Appendix C |
| A:ACTUAL_WHOLE_PARTS | PREMISE; DECLARED_ASSUMPTION | Actual whole and constituent tokens | A Appendix C |
| A:PHYS_NONPRODUCT | PREMISE; DECLARED_ASSUMPTION | Whole physical organization is nonproduct | A Appendix C |
| A:NONSUM | THM; MANUAL_CONDITIONAL_PASS | Non-Summative Combination | A §6.3 |
| A:MACRO_EQ | PREMISE; DECLARED_ASSUMPTION | Macro ontic equivalence — Independently justified actual macro tokens have equivalent COMPLETE macro organization, with lower differences nonconstitutive of that macro token. | A Appendix C |
| A:MICRO_NONISO | PREMISE; DECLARED_ASSUMPTION | Lower-scale ontic nonisomorphism — Specified actual lower tokens have nonisomorphic complete organizations in their common signature. | A Appendix C |
| A:MACRO_EXP_EQ | THM; MANUAL_CONDITIONAL_PASS | Macro experiential equivalence | A Appendix C |
| A:MICRO_EXP_DIFF | THM; MANUAL_CONDITIONAL_PASS | Lower experiential difference | A Appendix C |
| A:SYM_PREM | PREMISE; DECLARED_ASSUMPTION | Symmetry orbit premises — Physical structure W; automorphism group Gamma; candidate family closed under Gamma. | A Appendix C |
| A:EQUIV_SELECTOR | PREMISE; DECLARED_ASSUMPTION | Equivariant deterministic selector — Deterministic selector S with S(gW)=gS(W); no extra labels or random seed. | A Appendix C |
| A:OVERLAP_NONEMPTY_EXCL | PREMISE; DECLARED_ASSUMPTION | Overlap + nonempty exclusive-output — Candidate domain is ONE orbit containing an overlapping pair; required output nonempty and pairwise disjoint. | A Appendix C |
| A:ORBIT_LEMMA | MATH; MANUAL_CONDITIONAL_PASS | Orbit lemma | A §7.1 |
| A:SELECTION_OBSTRUCTION | THM; MANUAL_CONDITIONAL_PASS | Restricted selection obstruction | A §7.1 |
| A:ALL_ANC_ACTUAL | SCENARIO; DECLARED_CONTEXT_OR_METHOD | All-ancestors family actualized | A Appendix C |
| A:E1 | COR; MANUAL_CONDITIONAL_PASS | No First Conscious Ancestor | A §8.1 |
| A:EPS_CHAIN | PREMISE; DECLARED_ASSUMPTION | epsilon-fine physical chain — Supplied physically justified epsilon-fine chain in that common geometry; no universal biological smoothness assumed. | A Appendix C |
| A:E2 | COR; MANUAL_CONDITIONAL_PASS | Fine-Grained Structural Chains | A §8.2 |
| A:PHYS_CONT_PATH | PREMISE; DECLARED_ASSUMPTION | Physical path continuity | A Appendix C |
| A:U2_APP | APP; MANUAL_CONDITIONAL_PASS | Experiential continuity on path | A Appendix C |
| A:CONNECTED_LAMBDA | MATH_PREMISE; DECLARED_CONTEXT_OR_METHOD | Connected parameter space | A Appendix C |
| A:CONT_BINARY_E | EXTERNAL_PREMISE; DECLARED_CONTEXT_OR_METHOD | Continuous binary experience-existence predicate | A Appendix C |
| A:HUMAN_ENDPOINT | EMP_PREMISE; DECLARED_CONTEXT_OR_METHOD | Human endpoint E=1 | A Appendix C |
| A:E3 | COND_MATH; MANUAL_CONDITIONAL_PASS | Connected Existence Constancy | A §8.3 |
| A:EVOL_SYNTH | APP; CONDITIONAL_SYNTHESIS | Evolutionary synthesis | A Appendix C |
| A:PHYS_TRANSFORM_NONISO | PREMISE; DECLARED_ASSUMPTION | Physical structural nonisomorphism | A Appendix C |
| A:STRUCT_TRANSFORM | THM; MANUAL_CONDITIONAL_PASS | Structural transformation consequence | A Appendix C |
| A:TOY_MATH | MODEL_SPECIFICATION; STIPULATED_MODEL | Three-register / four-setting mathematics | A Appendix C |
| A:TOY_WHOLE_DIFF | MATH_RESULT; MANUAL_CONDITIONAL_PASS | Whole-model structural divergence | A Appendix C |
| A:TOY_SUB_EQ | MATH_RESULT; MANUAL_CONDITIONAL_PASS | Implemented sub-process invariance | A Appendix C |
| A:ACTUAL_COMPLETE_TOY | PREMISE; DECLARED_ASSUMPTION | Toy realization actual + complete — The modeled comparisons are independently established as actual complete token-relative organizations at the claimed level. | A Appendix C |
| A:TOY_EXP_WHOLE | APP; MANUAL_CONDITIONAL_PASS | Conditional whole experiential divergence | A Appendix C |
| A:TOY_EXP_SUB | APP; MANUAL_CONDITIONAL_PASS | Conditional sub-process experiential equivalence | A Appendix C |
| A:PHEN_TARGET | EPI_DEF; DECLARED_CONTEXT_OR_METHOD | Finite phenomenal/psychophysical target | A Appendix C |
| A:BRIDGE_FWD | BRIDGE; DECLARED_ASSUMPTION | One-way bridge | A Appendix C |
| A:BRIDGE_REV | BRIDGE; DECLARED_ASSUMPTION | Reflection bridge | A Appendix C |
| A:MEAS | METHOD; DECLARED_CONTEXT_OR_METHOD | Measurement/error assumptions | A Appendix C |
| A:OSC_FWD | BRIDGE_PKG; ASSUMPTION_PACKAGE | One-way OSC package | A Appendix C |
| A:OSC_TWO | BRIDGE_PKG; ASSUMPTION_PACKAGE | Two-way OSC package | A Appendix C |
| A:PTVSP | METHOD; DECLARED_CONTEXT_OR_METHOD | Physical Token/View Selection Protocol | A Appendix C |
| A:FAIL_ONE | TEST; MANUAL_CONDITIONAL_PASS | One-way bridge failure pattern | A Appendix C |
| A:FAIL_TWO | TEST; MANUAL_CONDITIONAL_PASS | Reflection bridge failure pattern | A Appendix C |
| A:BAC_TFR | METHOD; DECLARED_CONTEXT_OR_METHOD | UCT II BAC/TFR constraints | A Appendix C |
| A:UCTII_RECON | METHOD_RESULT; MANUAL_CONDITIONAL_PASS | UCT II formal reconstruction | A Appendix C |
| A:UCTII_GATE | APP; MANUAL_CONDITIONAL_PASS | UCT II no-gate relocation | A Appendix C |
| A:UCTII_EXP | APP; CONDITIONAL_INTERPRETATION | UCT II experiential interpretation | A Appendix C |
| A:ACTUAL_PERSISTING_PARTS | PREMISE; DECLARED_ASSUMPTION | Identified constituent tokens actually persist within the larger token | A §§2.4,6.3 |
| A:COEXISTENCE | COR; MANUAL_CONDITIONAL_PASS | Experience-bearing nested coexistence | A §§2.4,6.3 |
| A:FINITE_COARSE_SETUP | MODEL_PREMISE; DECLARED_ASSUMPTION | Surjective summary; deterministic total update; declared boundaries and operation domains | A Appendix D |
| A:COARSE_CLOSURE | MATH; MANUAL_CONDITIONAL_PASS | Deterministic quotient existence iff equal summaries have equal next summaries | A Appendix D |
| A:FORWARD_MISMATCH | PREMISE; DECLARED_ASSUMPTION | Same frozen view, unequal target, at exact level or within justified error model | A §12.1 |
| A:REVERSE_MISMATCH | PREMISE; DECLARED_ASSUMPTION | Unequal frozen views, same target, at exact level or within justified error model | A §12.2 |
| A:FROZEN_SCOPE | METHOD_PREMISE; DECLARED_ASSUMPTION | Token, view, bridge and comparison scope fixed before test | A §§11–12 |
| B:VIEW | EPI_DEF; DEFINITION | Frozen physically anchored finite view; not complete ontic structure | B §2 |
| B:LANGUAGE | DEF; DEFINITION | Typed Res/DoResp/Diff/Comp/Struct/Opt expression language | B §3 |
| B:BAC | METHOD; METHOD_NOT_AUTOMATICALLY_SATISFIED | Seven bridge admissibility conditions | B §4.1 |
| B:TFR | METHOD; METHOD_NOT_AUTOMATICALLY_SATISFIED | Target signature, strongest source claim and residuals retained | B §§1,18 |
| B:EXPRESSIBLE | PREMISE; DECLARED_ASSUMPTION | Every claimed observable has a well-typed finite expression using one fixed BAC-admissible bridge | B §4.2 |
| B:REP | CLAIM; MANUAL_CONDITIONAL_PASS | Compositional translator existence | B §4.2 |
| B:FV | CLASSIFICATION; DEFINITION | F0–F4 and V0–V4 classify separate subclaim/evidence dimensions | B §5 |
| B:RESIDUALS | CLASSIFICATION; DEFINITION | REC/EMB/REI/CON and explicit unrecovered residuals | B §§5,14 |
| B:EOD | DEF; DEFINITION | Effective organization description is a constrained definition, not whole-theory reduction | B §5.4 |
| B:TARGET_DOMAIN | PREMISE; DECLARED_ASSUMPTION | Exact rival universal gate claim and same-domain actual nonuniversality witness | B §5.5 |
| B:GATE | CLAIM; MANUAL_CONDITIONAL_PASS | Scoped no-universal-gate relocation | B §5.5 |
| B:OVERLAP_WITNESS | PREMISE; DECLARED_ASSUMPTION | Rival exclusion erases a lower token that actually persists in the same declared comparison | B §6 |
| B:EXCLUSION_CONFLICT | CLAIM; MANUAL_CONDITIONAL_PASS | Scoped conflict with exclusion | B §6 |
| B:IIT_BRIDGE | BRIDGE_PREMISE; DECLARED_ASSUMPTION | Current-state IIT chart, repertoires, priors, ID metric, partitions, tie and max/min conventions | B §6 |
| B:IIT | CLAIM; CONDITIONAL_TRANSLATION | F3/V0; not all of IIT or an empirical result | B §6 |
| B:RPT_BRIDGE | BRIDGE_PREMISE; DECLARED_ASSUMPTION | Grounded causal graph, sensory content, timing and stabilization bridge | B §7 |
| B:RPT | CLAIM; CONDITIONAL_TRANSLATION | Graph primitive F4; theory F3/V0 | B §7 |
| B:GNWT_BRIDGE | BRIDGE_PREMISE; DECLARED_ASSUMPTION | Specified content interventions, consumers, distances, timing and workspace architecture | B §8 |
| B:GNWT | CLAIM; CONDITIONAL_TRANSLATION | F3/V0; broad access is not existence | B §8 |
| B:HOT_BRIDGE | BRIDGE_PREMISE; DECLARED_ASSUMPTION | Specified tracking plus independently grounded representation/aboutness | B §9 |
| B:HOT | CLAIM; CONDITIONAL_TRANSLATION | Primitive F4; theory F3/V0 | B §9 |
| B:AST_BRIDGE | BRIDGE_PREMISE; DECLARED_ASSUMPTION | Attention-schema representation, control role and semantic grounding | B §9 |
| B:AST | CLAIM; CONDITIONAL_TRANSLATION | F3/V0 | B §9 |
| B:PP_AI_BRIDGE | BRIDGE_PREMISE; DECLARED_ASSUMPTION | Agent/environment chart, model p,q, policies, preferences and independent semantics | B §10 |
| B:PP_AI | CLAIM; CONDITIONAL_TRANSLATION | F3/V0 | B §10 |
| B:DIT_BRIDGE | BRIDGE_PREMISE; DECLARED_ASSUMPTION | Apical/basal/somatic/thalamic chart and relevant biological bridge | B §11 |
| B:DIT | CLAIM; CONDITIONAL_TRANSLATION | Local interaction F4; theory F3/V0 | B §11 |
| B:MTOC_BRIDGE | BRIDGE_PREMISE; DECLARED_ASSUMPTION | Retention relation and independently identified explicit-memory/assembly architecture | B §12 |
| B:MTOC | CLAIM; CONDITIONAL_TRANSLATION | Primitive F4; theory F3/V0; universal gate conflict separately scoped | B §12 |
| B:TTC_BRIDGE | BRIDGE_PREMISE; DECLARED_ASSUMPTION | Declared scale/time coordinates and faithful nestedness/alignment/expansion/globalization roles | B §13 |
| B:TTC | CLAIM; CONDITIONAL_TRANSLATION | F3/V0 | B §13 |
| B:GRAPH | MODEL_PREMISE; DECLARED_ASSUMPTION | Finite directed graph, with self-loops recorded; recurrence means positive-length cycle | B §7 / R128 qualification |
| B:CYCLE_PRIMITIVE | CLAIM; MANUAL_CONDITIONAL_PASS | Cycle-containing SCC characterization | B §7 |
| B:NEW_EDGE_RETURN | MODEL_PREMISE; DECLARED_ASSUMPTION | One absent directed edge u→v is added; evaluate existence of a prior v→u path, allowing a zero-length path when u=v | B §16 |
| B:EDGE_CYCLE | CLAIM; MANUAL_CONDITIONAL_PASS | New edge creates a directed cycle iff a return path exists | B §16 |
| B:NONLINEAR_WORKSPACE | MODEL_PREMISE; DECLARED_ASSUMPTION | Specified feedback, drive, state, timing and workspace readout | B §§16,19 |
| B:RECURRENCE_ENABLES | CONDITIONAL_ENABLING; CONDITIONAL_ENABLING | Recurrence may enable ignition in specified nonlinear systems; not unconditional sufficiency | B §16 |
| B:MODEL19 | MODEL_SPECIFICATION; STIPULATED_MODEL | Fixed sigmoid-gate two-node workspace, readout and control conventions | B §19 |
| B:MODEL20 | MODEL_SPECIFICATION; STIPULATED_MODEL | Fixed memory/tracking/workspace recurrences and readout conventions | B §20 |
| B:GRID19 | NUMERICAL_RECORD; PRESERVED_NOT_RERUN | Archived finite-grid access crossings; structural rho=1 is not a nonlinear bifurcation | B §19 |
| B:GRID20 | NUMERICAL_RECORD; PRESERVED_NOT_RERUN | Archived retention-grid crossings and edge-cut controls; not full target theories | B §20 |
| B:SPECTRAL | CLAIM; MANUAL_CONDITIONAL_PASS | Structural spectral radius of the declared weighted pair | B §19.2 |
| C:FIXED_J | PREMISE; DECLARED_ASSUMPTION | Comparable complete types and an isomorphism-invariant J under fixed tasks/resources/context | C §§2,5 |
| C:P1 | CLAIM; MANUAL_CONDITIONAL_PASS | Refinement and No Experientially Silent Intelligence Gain | C §5.1 |
| C:SET_MAPS | MATH_PREMISE; DECLARED_ASSUMPTION | Set maps on one declared common domain and their fibers | C §§5.2–5.3 |
| C:P2_COORD | CLAIM; MANUAL_CONDITIONAL_PASS | Coordinate identification iff constancy on fibers | C §5.2 |
| C:P2_FULL | CLAIM; MANUAL_CONDITIONAL_PASS | Full experiential identification iff J injective | C §5.2 |
| C:OBS_REFINEMENT | CLAIM; MANUAL_CONDITIONAL_PASS | Joint observation fibers are intersections | C §5.3 |
| C:CONST_RANK | MODEL_PREMISE; DECLARED_ASSUMPTION | Smooth n-dimensional chart, differentiable observation, locally constant rank r | C §5.3 |
| C:LOCAL_FIBER | CLAIM; MANUAL_CONDITIONAL_PASS | Local fiber dimension n-r | C §5.3 |
| C:PAIR_COUNTERMODEL | MODEL_SPECIFICATION; STIPULATED_COUNTERMODEL | Types (x,y), Φ identity, J=x and coordinate C=y, change (0,1)→(1,0) | C §5.4 |
| C:P3 | CLAIM; MANUAL_CONDITIONAL_PASS | No unconditional capability-to-richness monotonic implication | C §5.4 |
| C:SMOOTH_FITNESS | MODEL_PREMISE; DECLARED_ASSUMPTION | Differentiable fitness component wI=FI∘J; fixed ecological context | C §6.1 |
| C:P4 | CLAIM; MANUAL_CONDITIONAL_PASS | Local fitness null and exact fiber constancy | C §6.1 |
| C:SELECTION | MODEL_PREMISE; DECLARED_ASSUMPTION | Finite deterministic selection update p+=pW/EW with nonnegative weights, positive mean, faithful copying | C §6.2 |
| C:CLASS_WEIGHTS | MODEL_PREMISE; DECLARED_ASSUMPTION | W=f(J), with the class of interest initially positive and surviving with f(j)>0 | C §6.2 |
| C:P5 | CLAIM; MANUAL_CONDITIONAL_PASS | Within-fiber conditional preservation under selection | C §6.2 |
| C:PRICE_SELECTION | CLAIM; MANUAL_CONDITIONAL_PASS | Selection covariance and class-mean decomposition | C §6.3 |
| C:DESCENDANT_ATTRIBUTION | MODEL_PREMISE; DECLARED_ASSUMPTION | Declared reproductive attribution and finite descendant mean C'_s | C §6.3 |
| C:PRICE_TRANSMISSION | CLAIM; MANUAL_CONDITIONAL_PASS | Full Price accounting with descendant change | C §6.3 |
| C:MARKOV_SELECTION | MODEL_PREMISE; DECLARED_ASSUMPTION | Finite state space; fixed row-stochastic K; positive class-constant f(J); all initial distributions | C §6.4 |
| C:P6 | CLAIM; MANUAL_CONDITIONAL_PASS | Capability closure iff within-class row sums agree | C §6.4 |
| C:DECISION | MODEL_PREMISE; DECLARED_ASSUMPTION | Finite fixed joint law, bounded payoff, common finite actions, unrestricted observation-wise policies; enlarged class can ignore extra information | C §7.3 |
| C:P7 | CLAIM; MANUAL_CONDITIONAL_PASS | Nonnegative optimal value of added information and common-optimum equality criterion | C §7.3 |
| C:CIRCUIT_SPEC | MODEL_SPECIFICATION; STIPULATED_MODEL | Independent fair input and mask; old-memory output before update; no missing channel; declared w/r/noise/mutation rules | C §§7.1–7.2; Appendix C |
| C:CIRCUIT_LAWS | CLAIM; MANUAL_CONDITIONAL_PASS | Matched-storage information, accuracy and transmission formulas | C §7.2; Appendix C |
| C:ENV_MEMORY | MODEL_PREMISE; DECLARED_ASSUMPTION | Fair symmetric Markov target with persistence alpha, independent bit noise epsilon≤1/2 | C §7.3 |
| C:MEMORY_VALUE | CLAIM; MANUAL_CONDITIONAL_PASS | Memory prediction value in supplied environment | C §7.3 |
| C:MEMORY_COST | MODEL_PREMISE; DECLARED_ASSUMPTION | Two architecture types both present, positive W0=1+beta V_X and W1=1+beta V_XM-c, beta>0 | C §7.3 |
| C:MEMORY_SELECTION | CLAIM; MANUAL_CONDITIONAL_PASS | Memory favored iff beta ΔV>c in that model | C §7.3 |
| C:ACTUAL_ENSEMBLE | PREMISE; DECLARED_ASSUMPTION | Same declared actual ensemble, common coordinates and order | C §8.2 |
| C:REPERTOIRE | CLAIM; MANUAL_CONDITIONAL_PASS | Physical/experiential realized repertoires and frontiers agree | C §8.2 |
| C:ACTUAL_INDEX_FAMILY | PREMISE; DECLARED_ASSUMPTION | Same stimulus index set; actual complete types compared; full-type equality and difference established | C Appendix E |
| C:SENSORY_PARTITION | CLAIM; MANUAL_CONDITIONAL_PASS | Transfer of complete-type partitions | C Appendix E |
| C:RIVAL_DESCRIPTOR | BRIDGE_PREMISE; DECLARED_ASSUMPTION | Source-faithful rival sufficient descriptor, same actual token domain/target, unequal full types sharing descriptor | C §9.1 |
| C:RIVAL_CONTRAST | CLAIM; MANUAL_CONDITIONAL_PASS | Conditional complete-type disagreement with that rival | C §9.1 |
| C:RIVAL_NESIG | CLAIM; MANUAL_CONDITIONAL_PASS | A rival also satisfies type-change NESIG iff J factors through its assignment | C §9.1 |
| C:TRANSCRIPT | MODEL_PREMISE; DECLARED_ASSUMPTION | Same scored transcript alphabet, preparation and h∈[0,1] | C §9.2 |
| C:SCORE_TV | CLAIM; MANUAL_CONDITIONAL_PASS | Score difference bounded by scored-transcript TV | C §9.2 |
| C:FINITE_LOSS | MODEL_PREMISE; DECLARED_ASSUMPTION | Finite target, finite expected log losses and conditional information, fixed evaluation law/predictors | C Appendix B |
| C:LOGLOSS | CLAIM; MANUAL_CONDITIONAL_PASS | Log-loss gain equals conditional information plus excess-risk difference | C Appendix B |
| C:NUISANCE_BOUNDS | MODEL_PREMISE; DECLARED_ASSUMPTION | Finite sufficient descriptor A*, u=H(A*\|Z), d=I(Y;R\|A*,Z), independently bounded KZ≤eta | C Appendix B |
| C:RESIDUAL_BOUND | CLAIM; MANUAL_CONDITIONAL_PASS | Residual predictive gain bounded by u+d+eta | C Appendix B |
| C:TV_PROFILES | MODEL_PREMISE; DECLARED_ASSUMPTION | Fixed response laws on common finite alphabet; nonnegative normalized weights | C §10.2 |
| C:PROFILE_PSEUDOMETRIC | CLAIM; MANUAL_CONDITIONAL_PASS | Weighted TV profile distance is a pseudometric | C §10.2 |
| C:PUBLIC_NULL_PREMISE | MODEL_PREMISE; DECLARED_ASSUMPTION | Fair randomized answer independent of the entire available public record and observer randomness | C §10.2 |
| C:PUBLIC_NULL | CLAIM; MANUAL_CONDITIONAL_PASS | Public-input-only forced binary answer has expectation 1/2 | C §10.2 |
| R126:PROJECTION | ASSUMPTION; DECLARED_ASSUMPTION | Arbitrary function p from admitted complete types; Phi bijective | R126 theory note §3 |
| R126:MODEL | ASSUMPTION; DECLARED_ASSUMPTION | Finite nonempty sufficient state domain; total physically labeled deterministic operations; p onto its image; fixed output r | R126 theory note §4 |
| R126:METRIC | ASSUMPTION; DECLARED_ASSUMPTION | Metric on summary space; summary-only deterministic predictor | R126 theory note §5 |
| R126:P1 | THEOREM; MANUAL_CONDITIONAL_PASS | Transported commutation is automatic and does not select content | R126 theory note §3 |
| R126:P2 | THEOREM; MANUAL_CONDITIONAL_PASS | Deterministic operation and output factorization criterion | R126 theory note §4 |
| R126:P3 | THEOREM; MANUAL_CONDITIONAL_PASS | Half-diameter lower bound on summary-only worst-case error | R126 theory note §5 |
| R126:P4 | THEOREM; MANUAL_CONDITIONAL_PASS | Coarsest finite stable refinement | R126 theory note §6 |
| R127:TASK | ASSUMPTION; DECLARED_ASSUMPTION | Finite delayed-query single-answer task f:H×Q→Y; common admitted Cartesian domain; query unavailable to encoder | R127 theory note §§2–3 |
| R127:MEDIATION | ASSUMPTION; DECLARED_ASSUMPTION | Complete physical cut C with all declared external B; same downstream Wq; queries externally fixed or independent of encoding/noise; errors specified | R127 theory note §§2,4 |
| R127:RECOVERY | ASSUMPTION; DECLARED_ASSUMPTION | Finite X of size m≥2 recovered from (C,B) with actual average error epsilon and conditional mediation | R127 theory note §5 |
| R127:EVENT_SUPPORT | ASSUMPTION; DECLARED_ASSUMPTION | Physically grounded finite actual event graph; nonempty connected selected induced subhistory; relevant crossing ports and traceable occurrence history | R127 theory note §7 |
| R127:RELATIONAL_SUPPORT | ASSUMPTION; DECLARED_ASSUMPTION | Independently established actual P and actual retained carriers/typed relations in its complete common signature; operation closure or ports explicit | R127 theory note §8 |
| R127:PAIR_MODEL | MODEL_SPECIFICATION; STIPULATED_MODEL | Independent fair X,N; C=X XOR N; B=N | R127 theory note §5 |
| R127:LOCALIZATION_PAIR | MODEL_SPECIFICATION; STIPULATED_MODEL | Matched complete exposed interface laws for allowed internal-register and external-register implementations | R127 theory note §6 |
| R127:P1 | THEOREM; MANUAL_CONDITIONAL_PASS | Exact task encoding and response-profile distinction bound | R127 theory note §3 |
| R127:QUERY_REFINEMENT | THEOREM; MANUAL_CONDITIONAL_PASS | Larger query family refines task equivalence | R127 theory note §3 |
| R127:FUTURE_EQ | THEOREM; MANUAL_CONDITIONAL_PASS | Future-word response equivalence equals stable refinement | R127 theory note §3 |
| R127:P2 | THEOREM; MANUAL_CONDITIONAL_PASS | Complete-cut discrimination necessity and TV lower bound | R127 theory note §4 |
| R127:P3 | THEOREM; MANUAL_CONDITIONAL_PASS | Conditional internal information requirement | R127 theory note §5 |
| R127:JOINT_INFORMATION | THEOREM; MANUAL_CONDITIONAL_PASS | Joint relation retains information absent from individual marginals | R127 theory note §5 |
| R127:LOCALIZATION_LIMIT | THEOREM; MANUAL_CONDITIONAL_PASS | Interface law alone need not identify internal storage | R127 theory note §6 |
| R127:P4 | THEOREM; DEFINITION_APPLICATION | Application of published actual-token criterion | R127 theory note §7 |
| R127:P5 | THEOREM; MANUAL_CONDITIONAL_PASS | Actual inherited relations have a C1-preserved intrinsic image | R127 theory note §8 |
| N128:COMMON_DETERMINISTIC | ASSUMPTION; DECLARED_ASSUMPTION | Same sufficient S and total operation family F_a; each p_i individually commutes; joint image p(S) used | R128 joint-state derivation §2 |
| N128:MARKOV_WITNESS | MODEL_SPECIFICATION; STIPULATED_MODEL | S={0,1}^3; X+=U, Y+=U XOR Z, Z+=Z; fresh fair U, all initial distributions | R128 joint-state derivation §3 |
| N128:KERNEL | ASSUMPTION; DECLARED_ASSUMPTION | Finite same operation-indexed Markov kernels K_a and joint summary p=(p1,p2) | R128 joint-state derivation §4 |
| N128:PRODUCT_LAW | ASSUMPTION; DECLARED_ASSUMPTION | Both marginal summaries close and next-summary coordinates are conditionally independent at each full current state for every operation | R128 joint-state derivation §4 |
| N128:DET_JOIN | THEOREM; MANUAL_CONDITIONAL_PASS | Common deterministic closed summaries compose | R128 joint-state derivation §2 |
| N128:MARKOV_JOIN | THEOREM; MANUAL_CONDITIONAL_PASS | Separate stochastic closure does not imply joint closure | R128 joint-state derivation §3 |
| N128:JOINT_CRITERION | THEOREM; MANUAL_CONDITIONAL_PASS | Joint pushed-forward law is the exact closure criterion | R128 joint-state derivation §4 |
| N128:INDEPENDENCE_SUFFICES | THEOREM; MANUAL_CONDITIONAL_PASS | Conditional independence plus marginal closure suffices, but is not necessary | R128 joint-state derivation §4 |
| N128:SEPARATION | THEOREM; MANUAL_CONDITIONAL_PASS | Observation refinement and autonomous dynamical sufficiency are distinct | R128 joint-state derivation §5 |
