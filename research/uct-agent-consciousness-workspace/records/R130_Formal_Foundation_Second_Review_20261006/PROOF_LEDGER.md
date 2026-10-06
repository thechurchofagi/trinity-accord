# Unified proof ledger — R130

236 nodes / 106 rules. Every rule retains conjunctive premises and its proof sketch; every node retains all explicit scope and source metadata. Consult SECOND_REVIEW.md and the canonical audit for F20/F21 and review limitations. The ledger is not proof-assistant verification.

## Rule a01

- All premises: `A:C1`
- Conclusion: `A:C1_OI`
- Statement: D(P)≅D(Q) iff Φ(P)≅Φ(Q) in the same complete signature
- Proof: Compose tokenwise isomorphisms and their inverses in either direction.
- Source: A §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a02

- All premises: `A:C1_OI`
- Conclusion: `A:C1_W`
- Statement: Complete physical equivalence implies full experiential equivalence
- Proof: Take forward implication.
- Source: A §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a03

- All premises: `A:C1`, `A:NONEMPTY_CARRIER`
- Conclusion: `A:U1`
- Statement: Every actual token has a nonempty distinguished experiential carrier
- Proof: Sort-preserving bijection preserves nonemptiness.
- Source: A §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a04

- All premises: `A:C1`, `A:QSPACE`, `A:GEOMETRY`
- Conclusion: `A:U2`
- Statement: Physical and experiential quotient-valued maps have identical continuity and distances
- Proof: The two maps are pointwise equal; use the same predeclared geometry.
- Source: A §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a05

- All premises: `A:U1`, `A:SELF_WITNESS`
- Conclusion: `A:U3`
- Statement: Conceptual selfhood is not necessary for basal experience in a domain containing the witness
- Proof: Apply U1 to the actual non-self witness.
- Source: A §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a06

- All premises: `A:C1`, `A:P3`, `A:P6`, `A:U1`, `A:U2`, `A:U3`
- Conclusion: `A:U0`
- Statement: Prior foundational roles have the stated derivation/ontology decomposition
- Proof: Collect prior derivations; preserve every context premise and witness.
- Source: A §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a07

- All premises: `A:U1`, `A:NONUNIV_WITNESS`
- Conclusion: `A:ORG_GATE`
- Statement: A mechanism absent at an actual same-domain witness cannot equal universal E=1
- Proof: At the witness, E=1 and candidate gate=0.
- Source: A §5.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a08

- All premises: `A:C1_W`, `A:COMPLETE_EQ`
- Conclusion: `A:NO_HIDDEN`
- Statement: No extra full-type phenomenal variation at fixed complete organization
- Proof: Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- Source: A §5.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a09

- All premises: `A:C1_W`, `A:COMPLETE_EQ`, `A:PROBE_ONLY`
- Conclusion: `A:PROBE_INV`
- Statement: Description/probe-choice-only change preserves full experiential type
- Proof: Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- Source: A §5.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a10

- All premises: `A:C1_W`, `A:COMPLETE_EQ`, `A:FUTURE_ONLY`
- Conclusion: `A:NO_FUTURE`
- Statement: Future-only divergence does not change present type if complete present organization is equal
- Proof: Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- Source: A §5.4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a11

- All premises: `A:C1_W`, `A:COMPLETE_EQ`, `A:HISTORY_DIFF`
- Conclusion: `A:GHOST_EQ`
- Statement: Screened history does not change current full experiential type
- Proof: Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- Source: A §5.5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a12

- All premises: `A:C1_W`, `A:COMPLETE_EQ`, `A:LABEL_ONLY`
- Conclusion: `A:REWARD_NONID`
- Statement: External reward-label change alone cannot change intrinsic phenomenal type
- Proof: Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- Source: A §5.6
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a13

- All premises: `A:GHOST_EQ`, `A:P6`, `A:HISTORY_DIFF`
- Conclusion: `A:GHOST_TOKEN_NOTE`
- Statement: Equal current types do not identify numerical occurrences or causal lineages
- Proof: Type equivalence is distinct from numerical token identity by P6.
- Source: A §5.5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a14

- All premises: `A:C1`, `A:PRODUCT_DEF`, `A:ACTUAL_WHOLE_PARTS`, `A:PHYS_NONPRODUCT`
- Conclusion: `A:NONSUM`
- Statement: A nonproduct actual whole is not the specified independent product of experiential constituents
- Proof: Products in the common category preserve constituent isomorphisms; the opposite conclusion contradicts physical nonproduct.
- Source: A §6.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a15

- All premises: `A:C1_W`, `A:MACRO_EQ`
- Conclusion: `A:MACRO_EXP_EQ`
- Statement: Complete macro equivalence preserves macro experiential type
- Proof: Apply C1-W to the independently justified macro tokens.
- Source: A §6.4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a16

- All premises: `A:C1_OI`, `A:MICRO_NONISO`
- Conclusion: `A:MICRO_EXP_DIFF`
- Statement: Complete lower-token nonisomorphism entails lower experiential difference
- Proof: Contrapose the reverse equivalence.
- Source: A §6.4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a17

- All premises: `A:SYM_PREM`, `A:EQUIV_SELECTOR`
- Conclusion: `A:ORBIT_LEMMA`
- Statement: Invariant deterministic selected family is a union of candidate orbits
- Proof: If P selected then gP selected for each structure automorphism g.
- Source: A §7.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a18

- All premises: `A:ORBIT_LEMMA`, `A:OVERLAP_NONEMPTY_EXCL`
- Conclusion: `A:SELECTION_OBSTRUCTION`
- Statement: One overlapping candidate orbit admits no nonempty disjoint invariant selection
- Proof: One selected member forces the entire overlapping orbit.
- Source: A §7.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a19

- All premises: `A:U1`, `A:ALL_ANC_ACTUAL`
- Conclusion: `A:E1`
- Statement: E=1 throughout the admitted actual-token comparison family
- Proof: Apply U1 member by member; no continuity premise is needed.
- Source: A §8.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a20

- All premises: `A:C1`, `A:QSPACE`, `A:GEOMETRY`, `A:EPS_CHAIN`
- Conclusion: `A:E2`
- Statement: Physical epsilon-fine chains are equally fine experiential chains
- Proof: Replace each physical quotient point by its equal experiential point.
- Source: A §8.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a21

- All premises: `A:CONNECTED_LAMBDA`, `A:CONT_BINARY_E`, `A:HUMAN_ENDPOINT`
- Conclusion: `A:E3`
- Statement: A continuous discrete-valued E on a connected space, with E=1 somewhere, is identically one
- Proof: Continuous image connected; a nonempty connected subset of {0,1} is a singleton.
- Source: A §8.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a22

- All premises: `A:U2`, `A:PHYS_CONT_PATH`
- Conclusion: `A:U2_APP`
- Statement: A supplied continuous physical path has a continuous experiential path
- Proof: Use the U2 transfer with its physical-path premise.
- Source: A §8.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a23a

- All premises: `A:E1`, `A:E2`
- Conclusion: `A:EVOL_SYNTH`
- Statement: Nonempty experience throughout plus equally fine structural change
- Proof: Conjoin existence and fine-chain results; do not infer monotone richness.
- Source: A §8
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a23b

- All premises: `A:E1`, `A:U2_APP`
- Conclusion: `A:EVOL_SYNTH`
- Statement: Nonempty experience throughout plus equally continuous structural change
- Proof: Alternative route using a continuous path instead of a fine-chain premise.
- Source: A §8
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a24

- All premises: `A:C1_OI`, `A:PHYS_TRANSFORM_NONISO`
- Conclusion: `A:STRUCT_TRANSFORM`
- Statement: Actual complete structural transformation entails full experiential type change
- Proof: Contrapose full-type equivalence.
- Source: A §9
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a25

- All premises: `A:TOY_MATH`
- Conclusion: `A:TOY_WHOLE_DIFF`
- Statement: Specified register transition image sizes distinguish whole modeled types
- Proof: Over F2 the pair matrices have ranks 0,1,1,2; powers give 1,2→1,2→1,4 retained classes.
- Source: A §9 and Appendix B
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a26

- All premises: `A:TOY_MATH`
- Conclusion: `A:TOY_SUB_EQ`
- Statement: The specified s-process and declared output remain unchanged
- Proof: s+=s XOR u is independent of downstream pair; projection/reset diagram commutes.
- Source: A Appendix B
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a27

- All premises: `A:TOY_WHOLE_DIFF`, `A:ACTUAL_COMPLETE_TOY`, `A:C1_OI`
- Conclusion: `A:TOY_EXP_WHOLE`
- Statement: The actual complete whole realizations would differ experientially
- Proof: Apply C1-OI only after the actual/completeness premise.
- Source: A §9.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a28

- All premises: `A:TOY_SUB_EQ`, `A:ACTUAL_COMPLETE_TOY`, `A:C1_W`
- Conclusion: `A:TOY_EXP_SUB`
- Statement: The actual complete implemented sub-process realizations would agree in type
- Proof: Apply C1-W to that sub-process, not the entire network.
- Source: A §9.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a29

- All premises: `A:C1`, `A:BRIDGE_FWD`, `A:MEAS`
- Conclusion: `A:OSC_FWD`
- Statement: One-way operational correspondence is a package with an independently assumed forward bridge
- Proof: Package construction; finite prediction is supplied by the bridge, not deduced from full C1 alone.
- Source: A §10
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a30

- All premises: `A:C1`, `A:BRIDGE_FWD`, `A:BRIDGE_REV`, `A:MEAS`
- Conclusion: `A:OSC_TWO`
- Statement: Two-way operational correspondence additionally assumes reflection
- Proof: Lossy projection does not supply reflection.
- Source: A §10
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a31

- All premises: `A:FROZEN_SCOPE`, `A:FORWARD_MISMATCH`, `A:MEAS`
- Conclusion: `A:FAIL_ONE`
- Statement: A valid same-view/different-target case falsifies that forward bridge package
- Proof: It is a counterexample to the finite implication; does not isolate C1.
- Source: A §12.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a32

- All premises: `A:FROZEN_SCOPE`, `A:REVERSE_MISMATCH`, `A:MEAS`
- Conclusion: `A:FAIL_TWO`
- Statement: A valid different-view/same-target case falsifies the reflection direction
- Proof: It is a counterexample to reflection, not complete experiential equivalence evidence.
- Source: A §12.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a33

- All premises: `A:P3`, `A:ACTUAL_PERSISTING_PARTS`, `A:U1`
- Conclusion: `A:COEXISTENCE`
- Statement: Persisting nested actual tokens remain experience-bearing
- Proof: P3 retains tokenhood; U1 applies to each continuing token.
- Source: A §§2.4,6.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a34

- All premises: `A:FINITE_COARSE_SETUP`
- Conclusion: `A:COARSE_CLOSURE`
- Statement: A deterministic quotient exists iff equal summaries give equal successor summaries
- Proof: Necessity by equal arguments; sufficiency by representative-independent definition.
- Source: A Appendix D
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b01

- All premises: `B:VIEW`, `B:LANGUAGE`, `B:BAC`, `B:EXPRESSIBLE`
- Conclusion: `B:REP`
- Statement: A translator evaluates all declared admissible expressions
- Proof: Structural induction: leaves are admitted inputs/constants; each typed primitive composes previously defined values.
- Source: B §4.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b02

- All premises: `A:U1`, `B:TARGET_DOMAIN`
- Conclusion: `B:GATE`
- Statement: The stipulated universal rival gate conflicts at its admitted witness
- Proof: E=1 but the necessary gate is absent; a witness outside the rival domain does not work.
- Source: B §5.5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b03

- All premises: `A:P3`, `A:U1`, `B:OVERLAP_WITNESS`
- Conclusion: `B:EXCLUSION_CONFLICT`
- Statement: Overlap/nonmaximality alone cannot erase a persisting token's UCT experience
- Proof: P3 preserves the actual token; U1 gives nonempty experience, contrary to the scoped rival assignment.
- Source: B §6
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_IIT

- All premises: `B:VIEW`, `B:BAC`, `B:TFR`, `B:IIT_BRIDGE`
- Conclusion: `B:IIT`
- Statement: Conditional IIT mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §6
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_RPT

- All premises: `B:VIEW`, `B:BAC`, `B:TFR`, `B:RPT_BRIDGE`
- Conclusion: `B:RPT`
- Statement: Conditional RPT mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §7
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_GNWT

- All premises: `B:VIEW`, `B:BAC`, `B:TFR`, `B:GNWT_BRIDGE`
- Conclusion: `B:GNWT`
- Statement: Conditional GNWT mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §8
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_HOT

- All premises: `B:VIEW`, `B:BAC`, `B:TFR`, `B:HOT_BRIDGE`
- Conclusion: `B:HOT`
- Statement: Conditional HOT mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §9
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_AST

- All premises: `B:VIEW`, `B:BAC`, `B:TFR`, `B:AST_BRIDGE`
- Conclusion: `B:AST`
- Statement: Conditional AST mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §9
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_PP_AI

- All premises: `B:VIEW`, `B:BAC`, `B:TFR`, `B:PP_AI_BRIDGE`
- Conclusion: `B:PP_AI`
- Statement: Conditional PP_AI mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §10
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_DIT

- All premises: `B:VIEW`, `B:BAC`, `B:TFR`, `B:DIT_BRIDGE`
- Conclusion: `B:DIT`
- Statement: Conditional DIT mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §11
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_MTOC

- All premises: `B:VIEW`, `B:BAC`, `B:TFR`, `B:MTOC_BRIDGE`
- Conclusion: `B:MTOC`
- Statement: Conditional MTOC mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §12
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_TTC

- All premises: `B:VIEW`, `B:BAC`, `B:TFR`, `B:TTC_BRIDGE`
- Conclusion: `B:TTC`
- Statement: Conditional TTC mechanism representation with stated residuals
- Proof: Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- Source: B §13
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b04

- All premises: `B:GRAPH`
- Conclusion: `B:CYCLE_PRIMITIVE`
- Statement: A vertex is on a directed cycle iff it lies in an SCC with at least two vertices or has a self-loop
- Proof: Positive cycle implies mutual reachability; mutual reachability of distinct vertices gives a closed walk containing a cycle; handle singleton self-loops separately.
- Source: B §7 / R128
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b05

- All premises: `B:GRAPH`, `B:NEW_EDGE_RETURN`
- Conclusion: `B:EDGE_CYCLE`
- Statement: A newly added edge lies in a directed cycle iff the old graph has its reverse-direction return path
- Proof: Remove new edge from cycle to get path; concatenate path with edge for converse.
- Source: B §16
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b06

- All premises: `B:MODEL19`
- Conclusion: `B:SPECTRAL`
- Statement: rho=sqrt(6q); rho=1 at g=0.5-log(5)/10; cycle exists for all finite stated g
- Proof: Eigenvalues of [[0,2],[3q,0]] are ±sqrt(6q); invert q=sigmoid(10(g-.5)); q>0.
- Source: B §19.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b07

- All premises: `B:MODEL19`, `B:NONLINEAR_WORKSPACE`
- Conclusion: `B:RECURRENCE_ENABLES`
- Statement: Nonlinear stability must use the state-dependent Jacobian, not just weighted connectivity
- Proof: Differentiate sigmoid updates; slopes include x_i(1-x_i), so structural radius alone does not determine dynamical stability.
- Source: B §§16,19
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a35

- All premises: `B:VIEW`, `B:BAC`, `B:TFR`, `B:REP`
- Conclusion: `A:UCTII_RECON`
- Statement: UCT II's formal reconstruction has no C1/U1 premise
- Proof: Typed translator uses physical inputs and supplied conventions; identity is an optional subsequent interpretation.
- Source: A §16.1; B §§2–5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a36

- All premises: `A:U1`, `B:TARGET_DOMAIN`
- Conclusion: `A:UCTII_GATE`
- Statement: UCT II gate relocation uses U1 and a scoped witness
- Proof: Apply b02.
- Source: A §16.1; B §5.5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a37

- All premises: `A:ACTUAL_TOKEN`
- Conclusion: `A:NONEMPTY_CARRIER`
- Statement: An admitted actual token has nonempty constitutive support
- Proof: This is part of the declared actual-token ontology, not a data-derived consciousness claim.
- Source: A §2.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c01

- All premises: `A:C1_OI`, `C:FIXED_J`
- Conclusion: `C:P1`
- Statement: J(s)≠J(t) implies different full experiential type; strict fiber inclusion iff J noninjective
- Proof: Equal complete types have equal J; contrapose. Strictness is exactly a repeated J value on distinct types.
- Source: C §5.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c02

- All premises: `C:SET_MAPS`
- Conclusion: `C:P2_COORD`
- Statement: C factors through J iff J(s)=J(t) implies C(s)=C(t)
- Proof: Define recovered value on each fiber; it is representative-independent exactly under the stated condition.
- Source: C §5.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c03

- All premises: `A:C1_OI`, `C:FIXED_J`, `C:P2_COORD`
- Conclusion: `C:P2_FULL`
- Statement: J identifies full experiential type throughout the domain iff J is injective
- Proof: Full C1 type equivalence identifies distinct structural types with distinct experiential types.
- Source: C §5.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c04

- All premises: `C:SET_MAPS`
- Conclusion: `C:OBS_REFINEMENT`
- Statement: F_(A,R)(s)=F_A(s)∩F_R(s); refinement strict only when R splits an A-fiber
- Proof: Equality of ordered pairs is coordinatewise equality.
- Source: C §5.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c05

- All premises: `C:CONST_RANK`
- Conclusion: `C:LOCAL_FIBER`
- Statement: Locally constant rank gives local fibers of dimension n-r
- Proof: Apply the constant-rank normal form; pointwise rank at a singularity is insufficient.
- Source: C §5.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c06

- All premises: `C:PAIR_COUNTERMODEL`
- Conclusion: `C:P3`
- Statement: The C1-compatible model increases J while decreasing C
- Proof: Direct substitution verifies the premises and falsifies the unrestricted conclusion; coordinate is not asserted to measure real richness.
- Source: C §5.4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c07

- All premises: `C:SMOOTH_FITNESS`
- Conclusion: `C:P4`
- Statement: v∈ker DJ gives DwI[v]=0; exact constant-J path keeps wI constant
- Proof: Chain rule gives first result; function composition gives second. First-order null is not finite neutrality.
- Source: C §6.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c08

- All premises: `C:SELECTION`, `C:CLASS_WEIGHTS`
- Conclusion: `C:P5`
- Statement: p+(s|J=j)=p(s|J=j) for surviving classes
- Proof: Divide reweighted state mass by reweighted class mass; common factor cancels.
- Source: C §6.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c09

- All premises: `C:SELECTION`
- Conclusion: `C:PRICE_SELECTION`
- Statement: ΔEC=Cov(W,C)/EW; if W=f(J), covariance depends on E[C|J]
- Proof: Expand the reweighted expectation; use conditional expectation for class-constant weights.
- Source: C §6.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c10

- All premises: `C:SELECTION`, `C:DESCENDANT_ATTRIBUTION`
- Conclusion: `C:PRICE_TRANSMISSION`
- Statement: ΔEC=Cov(W,C)/EW+E[W(C'_s-C(s))]/EW
- Proof: Add and subtract E[WC]/EW. This is accounting, not a closed dynamics law.
- Source: C §6.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c11

- All premises: `C:MARKOV_SELECTION`
- Conclusion: `C:P6`
- Statement: Projected capability dynamics close iff every destination-class probability is constant on each current class
- Proof: Sufficiency groups row sums; necessity compares point masses in the same class, whose positive weights cancel.
- Source: C §6.4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c12

- All premises: `C:DECISION`
- Conclusion: `C:P7`
- Statement: V_XM≥V_X, with equality iff each supported X has a common optimal action for all supported M
- Proof: Write improvement as average nonnegative regret of a baseline-optimal action. Zero sum forces every supported regret to vanish.
- Source: C §7.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c13

- All premises: `C:CIRCUIT_SPEC`
- Conclusion: `C:CIRCUIT_LAWS`
- Statement: Unmasked readout accuracy 1-epsilon; masked/current-input accuracy 1/2; mutation gain mu(1/2-epsilon)
- Proof: Independence and XOR make the mask a fair one-time randomizer; average the two mutation outcomes.
- Source: C §7.2; Appendix C
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c14

- All premises: `C:ENV_MEMORY`, `C:DECISION`
- Conclusion: `C:MEMORY_VALUE`
- Statement: V=1/2+|2alpha-1|(1/2-epsilon)
- Proof: Match probability q=alpha(1-epsilon)+(1-alpha)epsilon; optimal binary action attains max(q,1-q).
- Source: C §7.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c15

- All premises: `C:MEMORY_COST`, `C:SELECTION`
- Conclusion: `C:MEMORY_SELECTION`
- Statement: Memory frequency increases exactly when its stipulated weight exceeds the alternative
- Proof: For two positive types, reweighting increases the first iff W1>W0; subtract weights.
- Source: C §7.3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c16

- All premises: `A:C1`, `C:ACTUAL_ENSEMBLE`
- Conclusion: `C:REPERTOIRE`
- Statement: R_D=R_Φ and their images/frontiers coincide; no time-monotonicity follows
- Proof: Elementwise C1 equality followed by the same map and partial order.
- Source: C §8.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c17

- All premises: `A:C1_OI`, `C:ACTUAL_INDEX_FAMILY`
- Conclusion: `C:SENSORY_PARTITION`
- Statement: Physical and experiential full-type equality partitions coincide
- Proof: Substitute type equivalence; strict refinement transfers on the same index set.
- Source: C Appendix E
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c18

- All premises: `A:C1_OI`, `B:TFR`, `C:RIVAL_DESCRIPTOR`
- Conclusion: `C:RIVAL_CONTRAST`
- Statement: UCT separates the pair while the stipulated rival assignment does not
- Proof: C1-OI separates unequal full types; rival descriptor equality forces its assigned equality.
- Source: C §9.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c19

- All premises: `C:SET_MAPS`, `C:P2_COORD`
- Conclusion: `C:RIVAL_NESIG`
- Statement: Unequal J entails unequal rival assignment iff J constant on rival fibers
- Proof: Contraposition plus representative-independent factorization; no C1 truth premise needed.
- Source: C §9.1
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c20

- All premises: `C:TRANSCRIPT`
- Conclusion: `C:SCORE_TV`
- Statement: |EP h-EQ h|≤TV(P,Q)
- Proof: Positive and negative parts of P-Q each have mass TV; h lies between zero and one.
- Source: C §9.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c21

- All premises: `C:FINITE_LOSS`
- Conclusion: `C:LOGLOSS`
- Statement: L(qZ)-L(qZR)=I(Y;R|Z)+KZ-KZR
- Proof: Each finite log loss is conditional entropy plus conditional KL; subtract.
- Source: C Appendix B
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c22

- All premises: `C:FINITE_LOSS`, `C:NUISANCE_BOUNDS`, `C:LOGLOSS`
- Conclusion: `C:RESIDUAL_BOUND`
- Statement: I(Y;R|Z)≤u+d, hence fitted gain≤u+d+eta
- Proof: Add A* in mutual information; chain rule and finite entropy bound; discard nonnegative KZR.
- Source: C Appendix B
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c23

- All premises: `C:TV_PROFILES`
- Conclusion: `C:PROFILE_PSEUDOMETRIC`
- Statement: Nonnegative weighted sum of TVs satisfies symmetry and triangle inequality; distinct states may have zero distance
- Proof: Apply TV metric properties coordinatewise.
- Source: C §10.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c24

- All premises: `C:PUBLIC_NULL_PREMISE`
- Conclusion: `C:PUBLIC_NULL`
- Statement: Independent public-only binary guessing succeeds with probability 1/2
- Proof: Condition on the full public record/decision; target remains fair.
- Source: C §10.2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r126_1

- All premises: `A:C1`, `R126:PROJECTION`
- Conclusion: `R126:P1`
- Statement: pE=p∘Phi^-1 gives pE∘Phi=p for every p
- Proof: Substitution and inverse identity. Since p was arbitrary the equality cannot by itself select actual support.
- Source: R126 theory note §3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r126_2

- All premises: `R126:MODEL`
- Conclusion: `R126:P2`
- Statement: A quotient update/output exists iff its next summary/output is constant on each current fiber
- Proof: Necessity by equal arguments; sufficiency by representative-independent definition.
- Source: R126 theory note §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r126_3

- All premises: `R126:MODEL`, `R126:METRIC`
- Conclusion: `R126:P3`
- Statement: Worst-case summary prediction error in a fiber is at least half the successor diameter
- Proof: Triangle inequality for the farthest pair. Necessity, not general sufficiency.
- Source: R126 theory note §5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r126_4

- All premises: `R126:MODEL`, `R126:P2`
- Conclusion: `R126:P4`
- Statement: Refine output fibers by successor classes; at most N-b0 strict stages; terminal equivalence is coarsest stable refinement
- Proof: Each strict stage increases class count; any stable refinement remains finer by induction.
- Source: R126 theory note §6
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_1

- All premises: `R127:TASK`
- Conclusion: `R127:P1`
- Statement: Exact answer factorization iff encoder separates all unequal response profiles; code size≥number of profiles
- Proof: Equal code forces equal outputs for every q; otherwise define decoder on image by representatives.
- Source: R127 theory note §3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_1a

- All premises: `R127:TASK`
- Conclusion: `R127:QUERY_REFINEMENT`
- Statement: Equality on Q2 entails equality on subset Q1
- Proof: Restrict universally quantified queries.
- Source: R127 theory note §3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_1b

- All premises: `R126:MODEL`, `R126:P4`
- Conclusion: `R127:FUTURE_EQ`
- Statement: Two states are equivalent iff outputs agree after every finite operation word, including the empty word
- Proof: Future-word equivalence is stable and refines outputs; all stable refinements preserve future outputs by induction.
- Source: R127 theory note §3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_2

- All premises: `R127:TASK`, `R127:MEDIATION`
- Conclusion: `R127:P2`
- Statement: At the same supported b,q and for different correct answers, TV(P(C|x,b,q),P(C|xprime,b,q)) >= 1-epsilon_(x,b,q)-epsilon_(xprime,b,q). Without conditioning on B the applicable cut law is joint (C,B), not C alone.
- Proof: Fix common supported b,q and use the SAME W_q(.|c,b). Total variation contracts from the conditional cut laws to outputs. The correct-answer event has probability at least 1-epsilon_(x,b,q) for x and at most epsilon_(xprime,b,q) for xprime. For unfixed B, sum over the JOINT cut (C,B); averaging away B can destroy the relevant dependence.
- Source: R127 theory note §§2,4–5; R130 second review §2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_3

- All premises: `R127:RECOVERY`
- Conclusion: `R127:P3`
- Statement: I(X;C|B)≥H(X|B)−h2(epsilon)−epsilon log2(m−1); for finite C this is at most log2|C|
- Proof: Conditional data processing followed by Fano error-indicator decomposition.
- Source: R127 theory note §5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_3a

- All premises: `R127:PAIR_MODEL`
- Conclusion: `R127:JOINT_INFORMATION`
- Statement: I(X;C)=I(X;B)=0, I(X;C,B)=1 bit
- Proof: Fair mask makes each marginal independent of X; XOR of both recovers X.
- Source: R127 theory note §5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_3b

- All premises: `R127:LOCALIZATION_PAIR`
- Conclusion: `R127:LOCALIZATION_LIMIT`
- Statement: Any interface-law-only identification rule agrees on the pair, so cannot identify both different storage locations
- Proof: Equal inputs to rule have equal outputs; locations differ by supplied construction.
- Source: R127 theory note §6
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_4

- All premises: `A:ACTUAL_TOKEN`, `R127:EVENT_SUPPORT`
- Conclusion: `R127:P4`
- Statement: Selected grounded subhistory meets A §2.5 actual-token conditions
- Proof: Actual support, inherited relations, causal continuity, boundary accountability and traceability each supplied. Definition application, not new existence threshold.
- Source: R127 theory note §7
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_5

- All premises: `A:C1`, `R127:RELATIONAL_SUPPORT`
- Conclusion: `R127:P5`
- Statement: For retained actual relation R and tuple a, R^D(a) iff R^Phi(h(a))
- Proof: Restrict a relation-preserving and reflecting isomorphism. Operations need closed subdomains/ports; no automatic subalgebra or independent subject.
- Source: R127 theory note §8
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a38

- All premises: `A:C1`, `B:REP`, `B:BAC`, `B:TFR`, `R127:RELATIONAL_SUPPORT`, `R127:P5`
- Conclusion: `A:UCTII_EXP`
- Statement: A source-faithful finite reconstruction has selected experiential interpretation only where its relations are independently grounded in actual constitutive organization
- Proof: B translation alone does not establish the physical premise. Once grounded, use the isomorphism restriction.
- Source: R127 theory note §8; A Appendix C; B §5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule n128_1

- All premises: `R126:P2`, `N128:COMMON_DETERMINISTIC`
- Conclusion: `N128:DET_JOIN`
- Statement: Joint summary update is the pair of component updates on its image
- Proof: Equality of current pairs implies equality of successor pairs; choose representative to prove image invariance.
- Source: R128 joint-state derivation §2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule n128_2

- All premises: `N128:MARKOV_WITNESS`
- Conclusion: `N128:MARKOV_JOIN`
- Statement: p1=x and p2=y close; (x,y) fails on all 8 states; closes on invariant 4-state restriction; full-domain stable refinement needs 8 blocks
- Proof: Each next marginal is fair; z selects equal vs unequal next pairs despite equal current pair. Every pair block must split by z.
- Source: R128 joint-state derivation §3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule n128_3

- All premises: `N128:KERNEL`
- Conclusion: `N128:JOINT_CRITERION`
- Statement: Joint law p_*K_a must be constant within each present joint-summary fiber
- Proof: Necessity by equal summary arguments; sufficiency by well-defined row assignment.
- Source: R128 joint-state derivation §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule n128_4

- All premises: `N128:KERNEL`, `N128:PRODUCT_LAW`, `N128:JOINT_CRITERION`
- Conclusion: `N128:INDEPENDENCE_SUFFICES`
- Statement: Products of closed marginal laws give a closed joint law; a fixed (U,U) joint law shows independence is unnecessary
- Proof: Product depends only on current pair; fixed correlated law depends on no hidden state.
- Source: R128 joint-state derivation §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule n128_5

- All premises: `C:OBS_REFINEMENT`, `N128:MARKOV_JOIN`
- Conclusion: `N128:SEPARATION`
- Statement: More identifying information does not by itself imply joint dynamic closure
- Proof: Joint fibers refine both coordinate fibers, but explicit next-joint laws disagree within a joint fiber.
- Source: R128 joint-state derivation §5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_bundled

- All premises: `D:PATH_MODEL`, `D:BUNDLED_ROWS`
- Conclusion: `D:F1`
- Statement: The bundled observation map is noninjective: rank 2 in R^5; the declared finite grid also has collisions.
- Proof: The two independent rows give rank 2 and a three-dimensional kernel. In {-1,0,1}^5, theta=(1,0,0,0,0) and (0,0,0,1,0) both map to (1,0). Exact enumeration gives 43 signatures, largest class 17.
- Source: D §3; R96; R129 §2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_direct

- All premises: `D:PATH_MODEL`, `D:DIRECT_ROWS`
- Conclusion: `D:F2`
- Statement: The five logits uniquely identify all five coefficients in the declared model, including on the finite grid.
- Proof: Direct logits give theta_Q,theta_O,theta_G. Subtract theta_Q+theta_G from Q-bundle and theta_O+theta_G from O-bundle for the interactions. Five rows have full rank. Deterministic choices and unknown logit scale do not supply these observations.
- Source: D §3; R96; R129 §2
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_payoff

- All premises: `D:BINARY_PAYOFF`
- Conclusion: `D:PAYOFF`
- Statement: Binary payoff admits the stated four-term expansion.
- Proof: Set alpha=f00,b=f10-f00,c=f01-f00,d=f11-f10-f01+f00; equality holds at all four states. Take expectations under each action law.
- Source: D §4; R96D §5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_marginal_counter

- All premises: `D:BINARY_PAYOFF`, `D:PAYOFF`, `D:MATCHED_WITNESS`
- Conclusion: `D:F3`
- Statement: Accurate marginal consequence predictions can fail to identify the optimal action.
- Proof: OR has alpha=0,b=c=1,d=-1. Values A=(1/2,3/4) and B=(3/4,1/2) reverse strict optimal actions while all supplied marginals match.
- Source: D §4; R96D §§3–5
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_value_gap

- All premises: `D:F3`, `D:MATCHED_WITNESS`, `C:P7`
- Conclusion: `D:VALUE_GAP`
- Statement: The matched binary example has exact optimized value gap 1/8.
- Proof: Every context-blind action mixture averages (1/2+3/4)/2=5/8; the informed policy chooses the 3/4 action in both contexts. Same costs/action set; randomization only forms convex combinations.
- Source: D §4; R96D §§3–4; C P7
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_frechet

- All premises: `D:BINARY_PAYOFF`, `D:PAYOFF`, `D:FRECHET_ASSUMPTIONS`
- Conclusion: `D:FRECHET`
- Statement: The stated interval is the exact attainable advantage range under these assumptions.
- Proof: The four probabilities are (1-q-o+j,o-j,q-j,j); nonnegativity is equivalent to ell<=j<=u. Independent admissibility across actions gives the difference interval; multiply by d and add B.
- Source: R96D §6; R129 §3
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_grid

- All premises: `D:REGULAR_GRID`
- Conclusion: `D:GRID_BOUND`
- Statement: Nearest-grid error plus a justified Lipschitz remainder bounds the entire declared cube.
- Proof: Choose a grid point within radius sqrt(3)h/2 for each point x. Triangle inequality gives |e(x)|<=|e(grid)|+L_e distance. Take supremum.
- Source: D §§7–8; R99 §4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_separable

- All premises: `D:ADDITIVE_CLASS`
- Conclusion: `D:SEPARABLE`
- Statement: The Q finite-difference effect has no O/G context dependence.
- Proof: Subtract expressions; f_O,f_G,b cancel. f_Q remains arbitrary, so this does not prove linear shape or small off-grid error.
- Source: D §7; R99 §§3–4
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_uct

- All premises: `A:C1_OI`, `D:ACTUAL_CHANGE`
- Conclusion: `D:UCT_INTERPRETATION`
- Statement: Actual complete-type difference implies complete experiential-type difference under C1.
- Proof: Apply the reverse direction of complete physical-type iff complete experiential-type agreement by contraposition. Actual grounded type difference is an independent premise.
- Source: D §11; A C1-OI
- Review: MANUAL_VALID_UNDER_STATED_PREMISES

## Complete node inventory

### A:TOKEN_CRITERIA — Actual-token criteria

- Kind/status: ONTO_DEF / DECLARED_CONTEXT_OR_METHOD
- Statement: Actual-token criteria
- Source: A Appendix C

### A:ACTUAL_TOKEN — Actual valid process token

- Kind/status: ONTO_DOMAIN / DECLARED_CONTEXT_OR_METHOD
- Statement: Actual valid process token
- Source: A Appendix C
- scope: Admitted actual valid P, specified interval and boundary; A §2 actual-support/inherited-relations/continuity/accountability/traceability criteria. No claim that an arbitrary variable satisfies them.

### A:NONEMPTY_CARRIER — Nonempty constitutive carrier

- Kind/status: ONTO_CONSEQ / MANUAL_CONDITIONAL_PASS
- Statement: An admitted actual token has nonempty constitutive support
- Source: A Appendix C

### A:P3 — Persistence / cessation / embedding

- Kind/status: ONTO_RULE / DECLARED_CONTEXT_OR_METHOD
- Statement: Persistence / cessation / embedding
- Source: A Appendix C

### A:P6 — Token / type / lineage

- Kind/status: ONTO_DEF / DECLARED_CONTEXT_OR_METHOD
- Statement: Token / type / lineage
- Source: A Appendix C

### A:D_ONTIC — Complete token-relative ontic organization

- Kind/status: DEF / DECLARED_CONTEXT_OR_METHOD
- Statement: Complete token-relative ontic organization
- Source: A Appendix C

### A:K — Common structural signature K

- Kind/status: DEF / DECLARED_CONTEXT_OR_METHOD
- Statement: Common structural signature K
- Source: A Appendix C

### A:QSPACE — Structural-type quotient space

- Kind/status: DEF / DECLARED_CONTEXT_OR_METHOD
- Statement: Structural-type quotient space
- Source: A Appendix C

### A:GEOMETRY — Predeclared invariant topology / pseudometric

- Kind/status: METHOD_DEF / DECLARED_CONTEXT_OR_METHOD
- Statement: Predeclared invariant topology / pseudometric
- Source: A Appendix C
- scope: One predeclared common topology or pseudometric on the structural-type quotient; no empirically established unique metric assumed.

### A:VIEW — Finite physical view D_v

- Kind/status: EPI_DEF / DECLARED_CONTEXT_OR_METHOD
- Statement: Finite physical view D_v
- Source: A Appendix C

### A:ESTIMATE — Scientific estimate D-hat_v

- Kind/status: EPI_DEF / DECLARED_CONTEXT_OR_METHOD
- Statement: Scientific estimate D-hat_v
- Source: A Appendix C

### A:SUBJECT_FIREWALL — Experience-bearing process != canonical subject

- Kind/status: BOUNDARY / DECLARED_CONTEXT_OR_METHOD
- Statement: Experience-bearing process != canonical subject
- Source: A Appendix C

### A:C1 — Structural-Experiential Identity

- Kind/status: AX_C / FIXED_AXIOM
- Statement: Structural-Experiential Identity
- Source: A §4

### A:C1_OI — Pairwise type equivalence

- Kind/status: LEMMA / MANUAL_CONDITIONAL_PASS
- Statement: D(P)≅D(Q) iff Φ(P)≅Φ(Q) in the same complete signature
- Source: A §4

### A:C1_W — One-way phenomenal completeness

- Kind/status: LEMMA / MANUAL_CONDITIONAL_PASS
- Statement: Complete physical equivalence implies full experiential equivalence
- Source: A §4

### A:U1 — Universal Nonempty Experience

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: Every actual token has a nonempty distinguished experiential carrier
- Source: A §4

### A:U2 — Structural Continuity transfer

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: Physical and experiential quotient-valued maps have identical continuity and distances
- Source: A §4

### A:SELF_WITNESS — Actual non-self token witness

- Kind/status: EMP_WITNESS / DECLARED_CONTEXT_OR_METHOD
- Statement: Actual non-self token witness
- Source: A Appendix C
- scope: An actual valid token in the admitted domain lacks conceptual selfhood.

### A:U3 — Selfhood Non-Prerequisite

- Kind/status: COR / MANUAL_CONDITIONAL_PASS
- Statement: Conceptual selfhood is not necessary for basal experience in a domain containing the witness
- Source: A §4

### A:U0 — Foundational Compression

- Kind/status: META_THM / META_DEPENDENCY_RESULT
- Statement: Prior foundational roles have the stated derivation/ontology decomposition
- Source: A §4

### A:NONUNIV_WITNESS — Nonuniversality witness

- Kind/status: EMP_WITNESS / DECLARED_CONTEXT_OR_METHOD
- Statement: Nonuniversality witness
- Source: A Appendix C
- scope: An actual valid token in the SAME domain lacks the proposed organization gate.

### A:ORG_GATE — Organization-Gate Impossibility

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: A mechanism absent at an actual same-domain witness cannot equal universal E=1
- Source: A Appendix C

### A:COMPLETE_EQ — Complete current ontic equivalence

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Complete current ontic equivalence
- Source: A Appendix C
- scope: Same current complete token-relative ontic organization in the common signature, not merely equal observations.

### A:PROBE_ONLY — Only external probe choice changes

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Only external probe choice changes
- Source: A Appendix C

### A:FUTURE_ONLY — Only future divergence changes

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Only future divergence changes
- Source: A Appendix C

### A:HISTORY_DIFF — Different histories

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Different histories
- Source: A Appendix C
- scope: Different histories with all current constitutive consequences screened; numerical token/lineage may still differ.

### A:LABEL_ONLY — Only external label changes

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Only external label changes
- Source: A Appendix C

### A:NO_HIDDEN — No Hidden Quale

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: No extra full-type phenomenal variation at fixed complete organization
- Source: A Appendix C

### A:PROBE_INV — Probe Invariance

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: Description/probe-choice-only change preserves full experiential type
- Source: A Appendix C

### A:NO_FUTURE — No Future Contamination

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: Future-only divergence does not change present type if complete present organization is equal
- Source: A Appendix C

### A:GHOST_EQ — Causally Screened History experiential equivalence

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: Screened history does not change current full experiential type
- Source: A Appendix C

### A:GHOST_TOKEN_NOTE — Numerically distinct tokens may remain

- Kind/status: COR / ONTOLOGICAL_ADDENDUM
- Statement: Equal current types do not identify numerical occurrences or causal lineages
- Source: A Appendix C

### A:REWARD_NONID — External reward-label non-identity

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: External reward-label change alone cannot change intrinsic phenomenal type
- Source: A Appendix C

### A:PRODUCT_DEF — Declared independent constituent product

- Kind/status: DEF / DECLARED_CONTEXT_OR_METHOD
- Statement: Declared independent constituent product
- Source: A Appendix C

### A:ACTUAL_WHOLE_PARTS — Actual whole and constituent tokens

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Actual whole and constituent tokens
- Source: A Appendix C

### A:PHYS_NONPRODUCT — Whole physical organization is nonproduct

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Whole physical organization is nonproduct
- Source: A Appendix C

### A:NONSUM — Non-Summative Combination

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: A nonproduct actual whole is not the specified independent product of experiential constituents
- Source: A §6.3

### A:MACRO_EQ — Macro ontic equivalence

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Macro ontic equivalence
- Source: A Appendix C
- scope: Independently justified actual macro tokens have equivalent COMPLETE macro organization, with lower differences nonconstitutive of that macro token.

### A:MICRO_NONISO — Lower-scale ontic nonisomorphism

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Lower-scale ontic nonisomorphism
- Source: A Appendix C
- scope: Specified actual lower tokens have nonisomorphic complete organizations in their common signature.

### A:MACRO_EXP_EQ — Macro experiential equivalence

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: Complete macro equivalence preserves macro experiential type
- Source: A Appendix C

### A:MICRO_EXP_DIFF — Lower experiential difference

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: Complete lower-token nonisomorphism entails lower experiential difference
- Source: A Appendix C

### A:SYM_PREM — Symmetry orbit premises

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Symmetry orbit premises
- Source: A Appendix C
- scope: Physical structure W; automorphism group Gamma; candidate family closed under Gamma.

### A:EQUIV_SELECTOR — Equivariant deterministic selector

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Equivariant deterministic selector
- Source: A Appendix C
- scope: Deterministic selector S with S(gW)=gS(W); no extra labels or random seed.

### A:OVERLAP_NONEMPTY_EXCL — Overlap + nonempty exclusive-output

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Overlap + nonempty exclusive-output
- Source: A Appendix C
- scope: Candidate domain is ONE orbit containing an overlapping pair; required output nonempty and pairwise disjoint.

### A:ORBIT_LEMMA — Orbit lemma

- Kind/status: MATH / MANUAL_CONDITIONAL_PASS
- Statement: Invariant deterministic selected family is a union of candidate orbits
- Source: A §7.1

### A:SELECTION_OBSTRUCTION — Restricted selection obstruction

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: One overlapping candidate orbit admits no nonempty disjoint invariant selection
- Source: A §7.1

### A:ALL_ANC_ACTUAL — All-ancestors family actualized

- Kind/status: SCENARIO / DECLARED_CONTEXT_OR_METHOD
- Statement: All-ancestors family actualized
- Source: A Appendix C

### A:E1 — No First Conscious Ancestor

- Kind/status: COR / MANUAL_CONDITIONAL_PASS
- Statement: E=1 throughout the admitted actual-token comparison family
- Source: A §8.1

### A:EPS_CHAIN — epsilon-fine physical chain

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: epsilon-fine physical chain
- Source: A Appendix C
- scope: Supplied physically justified epsilon-fine chain in that common geometry; no universal biological smoothness assumed.

### A:E2 — Fine-Grained Structural Chains

- Kind/status: COR / MANUAL_CONDITIONAL_PASS
- Statement: Physical epsilon-fine chains are equally fine experiential chains
- Source: A §8.2

### A:PHYS_CONT_PATH — Physical path continuity

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Physical path continuity
- Source: A Appendix C

### A:U2_APP — Experiential continuity on path

- Kind/status: APP / MANUAL_CONDITIONAL_PASS
- Statement: A supplied continuous physical path has a continuous experiential path
- Source: A Appendix C

### A:CONNECTED_LAMBDA — Connected parameter space

- Kind/status: MATH_PREMISE / DECLARED_CONTEXT_OR_METHOD
- Statement: Connected parameter space
- Source: A Appendix C

### A:CONT_BINARY_E — Continuous binary experience-existence predicate

- Kind/status: EXTERNAL_PREMISE / DECLARED_CONTEXT_OR_METHOD
- Statement: Continuous binary experience-existence predicate
- Source: A Appendix C

### A:HUMAN_ENDPOINT — Human endpoint E=1

- Kind/status: EMP_PREMISE / DECLARED_CONTEXT_OR_METHOD
- Statement: Human endpoint E=1
- Source: A Appendix C

### A:E3 — Connected Existence Constancy

- Kind/status: COND_MATH / MANUAL_CONDITIONAL_PASS
- Statement: A continuous discrete-valued E on a connected space, with E=1 somewhere, is identically one
- Source: A §8.3

### A:EVOL_SYNTH — Evolutionary synthesis

- Kind/status: APP / CONDITIONAL_SYNTHESIS
- Statement: Experience remains nonempty throughout the admitted actual-token family, together with either declared epsilon-fine-chain transfer or declared continuous-path transfer; each route retains its own physical premise.
- Source: A Appendix C

### A:PHYS_TRANSFORM_NONISO — Physical structural nonisomorphism

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Physical structural nonisomorphism
- Source: A Appendix C

### A:STRUCT_TRANSFORM — Structural transformation consequence

- Kind/status: THM / MANUAL_CONDITIONAL_PASS
- Statement: Actual complete structural transformation entails full experiential type change
- Source: A Appendix C

### A:TOY_MATH — Three-register / four-setting mathematics

- Kind/status: MODEL_SPECIFICATION / STIPULATED_MODEL
- Statement: Three-register / four-setting mathematics
- Source: A Appendix C

### A:TOY_WHOLE_DIFF — Whole-model structural divergence

- Kind/status: MATH_RESULT / MANUAL_CONDITIONAL_PASS
- Statement: Specified register transition image sizes distinguish whole modeled types
- Source: A Appendix C

### A:TOY_SUB_EQ — Implemented sub-process invariance

- Kind/status: MATH_RESULT / MANUAL_CONDITIONAL_PASS
- Statement: The specified s-process and declared output remain unchanged
- Source: A Appendix C

### A:ACTUAL_COMPLETE_TOY — Toy realization actual + complete

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Toy realization actual + complete
- Source: A Appendix C
- scope: The modeled comparisons are independently established as actual complete token-relative organizations at the claimed level.

### A:TOY_EXP_WHOLE — Conditional whole experiential divergence

- Kind/status: APP / MANUAL_CONDITIONAL_PASS
- Statement: The actual complete whole realizations would differ experientially
- Source: A Appendix C

### A:TOY_EXP_SUB — Conditional sub-process experiential equivalence

- Kind/status: APP / MANUAL_CONDITIONAL_PASS
- Statement: The actual complete implemented sub-process realizations would agree in type
- Source: A Appendix C

### A:PHEN_TARGET — Finite phenomenal/psychophysical target

- Kind/status: EPI_DEF / DECLARED_CONTEXT_OR_METHOD
- Statement: Finite phenomenal/psychophysical target
- Source: A Appendix C

### A:BRIDGE_FWD — One-way bridge

- Kind/status: BRIDGE / DECLARED_ASSUMPTION
- Statement: One-way bridge
- Source: A Appendix C

### A:BRIDGE_REV — Reflection bridge

- Kind/status: BRIDGE / DECLARED_ASSUMPTION
- Statement: Reflection bridge
- Source: A Appendix C

### A:MEAS — Measurement/error assumptions

- Kind/status: METHOD / DECLARED_CONTEXT_OR_METHOD
- Statement: Measurement/error assumptions
- Source: A Appendix C

### A:OSC_FWD — One-way OSC package

- Kind/status: BRIDGE_PKG / ASSUMPTION_PACKAGE
- Statement: One-way operational correspondence is a package with an independently assumed forward bridge
- Source: A Appendix C

### A:OSC_TWO — Two-way OSC package

- Kind/status: BRIDGE_PKG / ASSUMPTION_PACKAGE
- Statement: Two-way operational correspondence additionally assumes reflection
- Source: A Appendix C

### A:PTVSP — Physical Token/View Selection Protocol

- Kind/status: METHOD / DECLARED_CONTEXT_OR_METHOD
- Statement: Physical Token/View Selection Protocol
- Source: A Appendix C

### A:FAIL_ONE — One-way bridge failure pattern

- Kind/status: TEST / MANUAL_CONDITIONAL_PASS
- Statement: A valid same-view/different-target case falsifies that forward bridge package
- Source: A Appendix C

### A:FAIL_TWO — Reflection bridge failure pattern

- Kind/status: TEST / MANUAL_CONDITIONAL_PASS
- Statement: A valid different-view/same-target case falsifies the reflection direction
- Source: A Appendix C

### A:BAC_TFR — UCT II BAC/TFR constraints

- Kind/status: METHOD / DECLARED_CONTEXT_OR_METHOD
- Statement: UCT II BAC/TFR constraints
- Source: A Appendix C

### A:UCTII_RECON — UCT II formal reconstruction

- Kind/status: METHOD_RESULT / MANUAL_CONDITIONAL_PASS
- Statement: UCT II's formal reconstruction has no C1/U1 premise
- Source: A Appendix C

### A:UCTII_GATE — UCT II no-gate relocation

- Kind/status: APP / MANUAL_CONDITIONAL_PASS
- Statement: UCT II gate relocation uses U1 and a scoped witness
- Source: A Appendix C

### A:UCTII_EXP — UCT II experiential interpretation

- Kind/status: APP / CONDITIONAL_INTERPRETATION
- Statement: A source-faithful finite reconstruction has selected experiential interpretation only where its relations are independently grounded in actual constitutive organization
- Source: A Appendix C

### A:ACTUAL_PERSISTING_PARTS — Identified constituent tokens actually persist within the larger token

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Identified constituent tokens actually persist within the larger token
- Source: A §§2.4,6.3

### A:COEXISTENCE — Experience-bearing nested coexistence

- Kind/status: COR / MANUAL_CONDITIONAL_PASS
- Statement: Persisting nested actual tokens remain experience-bearing
- Source: A §§2.4,6.3

### A:FINITE_COARSE_SETUP — Surjective summary; deterministic total update; declared boundaries and operation domains

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Surjective summary; deterministic total update; declared boundaries and operation domains
- Source: A Appendix D

### A:COARSE_CLOSURE — Deterministic quotient existence iff equal summaries have equal next summaries

- Kind/status: MATH / MANUAL_CONDITIONAL_PASS
- Statement: A deterministic quotient exists iff equal summaries give equal successor summaries
- Source: A Appendix D

### A:FORWARD_MISMATCH — Same frozen view, unequal target, at exact level or within justified error model

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Same frozen view, unequal target, at exact level or within justified error model
- Source: A §12.1

### A:REVERSE_MISMATCH — Unequal frozen views, same target, at exact level or within justified error model

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Unequal frozen views, same target, at exact level or within justified error model
- Source: A §12.2

### A:FROZEN_SCOPE — Token, view, bridge and comparison scope fixed before test

- Kind/status: METHOD_PREMISE / DECLARED_ASSUMPTION
- Statement: Token, view, bridge and comparison scope fixed before test
- Source: A §§11–12

### B:VIEW — Frozen physically anchored finite view; not complete ontic structure

- Kind/status: EPI_DEF / DEFINITION
- Statement: Frozen physically anchored finite view; not complete ontic structure
- Source: B §2

### B:LANGUAGE — Typed Res/DoResp/Diff/Comp/Struct/Opt expression language

- Kind/status: DEF / DEFINITION
- Statement: Typed Res/DoResp/Diff/Comp/Struct/Opt expression language
- Source: B §3

### B:BAC — Seven bridge admissibility conditions

- Kind/status: METHOD / METHOD_NOT_AUTOMATICALLY_SATISFIED
- Statement: Seven bridge admissibility conditions
- Source: B §4.1

### B:TFR — Target signature, strongest source claim and residuals retained

- Kind/status: METHOD / METHOD_NOT_AUTOMATICALLY_SATISFIED
- Statement: Target signature, strongest source claim and residuals retained
- Source: B §§1,18

### B:EXPRESSIBLE — Every claimed observable has a well-typed finite expression using one fixed BAC-admissible bridge

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Every claimed observable has a well-typed finite expression using one fixed BAC-admissible bridge
- Source: B §4.2

### B:REP — Compositional translator existence

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: A translator evaluates all declared admissible expressions
- Source: B §4.2

### B:FV — F0–F4 and V0–V4 classify separate subclaim/evidence dimensions

- Kind/status: CLASSIFICATION / DEFINITION
- Statement: F0–F4 and V0–V4 classify separate subclaim/evidence dimensions
- Source: B §5

### B:RESIDUALS — REC/EMB/REI/CON and explicit unrecovered residuals

- Kind/status: CLASSIFICATION / DEFINITION
- Statement: REC/EMB/REI/CON and explicit unrecovered residuals
- Source: B §§5,14

### B:EOD — Effective organization description is a constrained definition, not whole-theory reduction

- Kind/status: DEF / DEFINITION
- Statement: Effective organization description is a constrained definition, not whole-theory reduction
- Source: B §5.4

### B:TARGET_DOMAIN — Exact rival universal gate claim and same-domain actual nonuniversality witness

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Exact rival universal gate claim and same-domain actual nonuniversality witness
- Source: B §5.5

### B:GATE — Scoped no-universal-gate relocation

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: The stipulated universal rival gate conflicts at its admitted witness
- Source: B §5.5

### B:OVERLAP_WITNESS — Rival exclusion erases a lower token that actually persists in the same declared comparison

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Rival exclusion erases a lower token that actually persists in the same declared comparison
- Source: B §6

### B:EXCLUSION_CONFLICT — Scoped conflict with exclusion

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: Overlap/nonmaximality alone cannot erase a persisting token's UCT experience
- Source: B §6

### B:IIT_BRIDGE — Current-state IIT chart, repertoires, priors, ID metric, partitions, tie and max/min conventions

- Kind/status: BRIDGE_PREMISE / DECLARED_ASSUMPTION
- Statement: Current-state IIT chart, repertoires, priors, ID metric, partitions, tie and max/min conventions
- Source: B §6

### B:IIT — F3/V0; not all of IIT or an empirical result

- Kind/status: CLAIM / CONDITIONAL_TRANSLATION
- Statement: Conditional IIT mechanism representation with stated residuals
- Source: B §6

### B:RPT_BRIDGE — Grounded causal graph, sensory content, timing and stabilization bridge

- Kind/status: BRIDGE_PREMISE / DECLARED_ASSUMPTION
- Statement: Grounded causal graph, sensory content, timing and stabilization bridge
- Source: B §7

### B:RPT — Graph primitive F4; theory F3/V0

- Kind/status: CLAIM / CONDITIONAL_TRANSLATION
- Statement: Conditional RPT mechanism representation with stated residuals
- Source: B §7

### B:GNWT_BRIDGE — Specified content interventions, consumers, distances, timing and workspace architecture

- Kind/status: BRIDGE_PREMISE / DECLARED_ASSUMPTION
- Statement: Specified content interventions, consumers, distances, timing and workspace architecture
- Source: B §8

### B:GNWT — F3/V0; broad access is not existence

- Kind/status: CLAIM / CONDITIONAL_TRANSLATION
- Statement: Conditional GNWT mechanism representation with stated residuals
- Source: B §8

### B:HOT_BRIDGE — Specified tracking plus independently grounded representation/aboutness

- Kind/status: BRIDGE_PREMISE / DECLARED_ASSUMPTION
- Statement: Specified tracking plus independently grounded representation/aboutness
- Source: B §9

### B:HOT — Primitive F4; theory F3/V0

- Kind/status: CLAIM / CONDITIONAL_TRANSLATION
- Statement: Conditional HOT mechanism representation with stated residuals
- Source: B §9

### B:AST_BRIDGE — Attention-schema representation, control role and semantic grounding

- Kind/status: BRIDGE_PREMISE / DECLARED_ASSUMPTION
- Statement: Attention-schema representation, control role and semantic grounding
- Source: B §9

### B:AST — F3/V0

- Kind/status: CLAIM / CONDITIONAL_TRANSLATION
- Statement: Conditional AST mechanism representation with stated residuals
- Source: B §9

### B:PP_AI_BRIDGE — Agent/environment chart, model p,q, policies, preferences and independent semantics

- Kind/status: BRIDGE_PREMISE / DECLARED_ASSUMPTION
- Statement: Agent/environment chart, model p,q, policies, preferences and independent semantics
- Source: B §10

### B:PP_AI — F3/V0

- Kind/status: CLAIM / CONDITIONAL_TRANSLATION
- Statement: Conditional PP_AI mechanism representation with stated residuals
- Source: B §10

### B:DIT_BRIDGE — Apical/basal/somatic/thalamic chart and relevant biological bridge

- Kind/status: BRIDGE_PREMISE / DECLARED_ASSUMPTION
- Statement: Apical/basal/somatic/thalamic chart and relevant biological bridge
- Source: B §11

### B:DIT — Local interaction F4; theory F3/V0

- Kind/status: CLAIM / CONDITIONAL_TRANSLATION
- Statement: Conditional DIT mechanism representation with stated residuals
- Source: B §11

### B:MTOC_BRIDGE — Retention relation and independently identified explicit-memory/assembly architecture

- Kind/status: BRIDGE_PREMISE / DECLARED_ASSUMPTION
- Statement: Retention relation and independently identified explicit-memory/assembly architecture
- Source: B §12

### B:MTOC — Primitive F4; theory F3/V0; universal gate conflict separately scoped

- Kind/status: CLAIM / CONDITIONAL_TRANSLATION
- Statement: Conditional MTOC mechanism representation with stated residuals
- Source: B §12

### B:TTC_BRIDGE — Declared scale/time coordinates and faithful nestedness/alignment/expansion/globalization roles

- Kind/status: BRIDGE_PREMISE / DECLARED_ASSUMPTION
- Statement: Declared scale/time coordinates and faithful nestedness/alignment/expansion/globalization roles
- Source: B §13

### B:TTC — F3/V0

- Kind/status: CLAIM / CONDITIONAL_TRANSLATION
- Statement: Conditional TTC mechanism representation with stated residuals
- Source: B §13

### B:GRAPH — Finite directed graph, with self-loops recorded; recurrence means positive-length cycle

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Finite directed graph, with self-loops recorded; recurrence means positive-length cycle
- Source: B §7 / R128 qualification

### B:CYCLE_PRIMITIVE — Cycle-containing SCC characterization

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: A vertex is on a directed cycle iff it lies in an SCC with at least two vertices or has a self-loop
- Source: B §7

### B:NEW_EDGE_RETURN — One absent directed edge u→v is added; evaluate existence of a prior v→u path, allowing a zero-length path when u=v

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: One absent directed edge u→v is added; evaluate existence of a prior v→u path, allowing a zero-length path when u=v
- Source: B §16

### B:EDGE_CYCLE — New edge creates a directed cycle iff a return path exists

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: A newly added edge lies in a directed cycle iff the old graph has its reverse-direction return path
- Source: B §16

### B:NONLINEAR_WORKSPACE — Specified feedback, drive, state, timing and workspace readout

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Specified feedback, drive, state, timing and workspace readout
- Source: B §§16,19

### B:RECURRENCE_ENABLES — Recurrence may enable ignition in specified nonlinear systems; not unconditional sufficiency

- Kind/status: CONDITIONAL_ENABLING / CONDITIONAL_ENABLING
- Statement: Nonlinear stability must use the state-dependent Jacobian, not just weighted connectivity
- Source: B §16

### B:MODEL19 — Fixed sigmoid-gate two-node workspace, readout and control conventions

- Kind/status: MODEL_SPECIFICATION / STIPULATED_MODEL
- Statement: Fixed sigmoid-gate two-node workspace, readout and control conventions
- Source: B §19

### B:MODEL20 — Fixed memory/tracking/workspace recurrences and readout conventions

- Kind/status: MODEL_SPECIFICATION / STIPULATED_MODEL
- Statement: Fixed memory/tracking/workspace recurrences and readout conventions
- Source: B §20

### B:GRID19 — Archived finite-grid access crossings; structural rho=1 is not a nonlinear bifurcation

- Kind/status: NUMERICAL_RECORD / PRESERVED_NOT_RERUN
- Statement: Archived finite-grid access crossings; structural rho=1 is not a nonlinear bifurcation
- Source: B §19

### B:GRID20 — Archived retention-grid crossings and edge-cut controls; not full target theories

- Kind/status: NUMERICAL_RECORD / PRESERVED_NOT_RERUN
- Statement: Archived retention-grid crossings and edge-cut controls; not full target theories
- Source: B §20

### B:SPECTRAL — Structural spectral radius of the declared weighted pair

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: rho=sqrt(6q); rho=1 at g=0.5-log(5)/10; cycle exists for all finite stated g
- Source: B §19.2

### C:FIXED_J — Comparable complete types and an isomorphism-invariant J under fixed tasks/resources/context

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Comparable complete types and an isomorphism-invariant J under fixed tasks/resources/context
- Source: C §§2,5

### C:P1 — Refinement and No Experientially Silent Intelligence Gain

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: J(s)≠J(t) implies different full experiential type; strict fiber inclusion iff J noninjective
- Source: C §5.1

### C:SET_MAPS — Set maps on one declared common domain and their fibers

- Kind/status: MATH_PREMISE / DECLARED_ASSUMPTION
- Statement: Set maps on one declared common domain and their fibers
- Source: C §§5.2–5.3

### C:P2_COORD — Coordinate identification iff constancy on fibers

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: C factors through J iff J(s)=J(t) implies C(s)=C(t)
- Source: C §5.2

### C:P2_FULL — Full experiential identification iff J injective

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: J identifies full experiential type throughout the domain iff J is injective
- Source: C §5.2

### C:OBS_REFINEMENT — Joint observation fibers are intersections

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: F_(A,R)(s)=F_A(s)∩F_R(s); refinement strict only when R splits an A-fiber
- Source: C §5.3

### C:CONST_RANK — Smooth n-dimensional chart, differentiable observation, locally constant rank r

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Smooth n-dimensional chart, differentiable observation, locally constant rank r
- Source: C §5.3

### C:LOCAL_FIBER — Local fiber dimension n-r

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: Locally constant rank gives local fibers of dimension n-r
- Source: C §5.3

### C:PAIR_COUNTERMODEL — Types (x,y), Φ identity, J=x and coordinate C=y, change (0,1)→(1,0)

- Kind/status: MODEL_SPECIFICATION / STIPULATED_COUNTERMODEL
- Statement: Types (x,y), Φ identity, J=x and coordinate C=y, change (0,1)→(1,0)
- Source: C §5.4

### C:P3 — No unconditional capability-to-richness monotonic implication

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: The C1-compatible model increases J while decreasing C
- Source: C §5.4

### C:SMOOTH_FITNESS — Differentiable fitness component wI=FI∘J; fixed ecological context

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Differentiable fitness component wI=FI∘J; fixed ecological context
- Source: C §6.1

### C:P4 — Local fitness null and exact fiber constancy

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: v∈ker DJ gives DwI[v]=0; exact constant-J path keeps wI constant
- Source: C §6.1

### C:SELECTION — Finite deterministic selection update p+=pW/EW with nonnegative weights, positive mean, faithful copying

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Finite deterministic selection update p+=pW/EW with nonnegative weights, positive mean, faithful copying
- Source: C §6.2

### C:CLASS_WEIGHTS — W=f(J), with the class of interest initially positive and surviving with f(j)>0

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: W=f(J), with the class of interest initially positive and surviving with f(j)>0
- Source: C §6.2

### C:P5 — Within-fiber conditional preservation under selection

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: p+(s|J=j)=p(s|J=j) for surviving classes
- Source: C §6.2

### C:PRICE_SELECTION — Selection covariance and class-mean decomposition

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: ΔEC=Cov(W,C)/EW; if W=f(J), covariance depends on E[C|J]
- Source: C §6.3

### C:DESCENDANT_ATTRIBUTION — Declared reproductive attribution and finite descendant mean C'_s

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Declared reproductive attribution and finite descendant mean C'_s
- Source: C §6.3

### C:PRICE_TRANSMISSION — Full Price accounting with descendant change

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: ΔEC=Cov(W,C)/EW+E[W(C'_s-C(s))]/EW
- Source: C §6.3

### C:MARKOV_SELECTION — Finite state space; fixed row-stochastic K; positive class-constant f(J); all initial distributions

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Finite state space; fixed row-stochastic K; positive class-constant f(J); all initial distributions
- Source: C §6.4

### C:P6 — Capability closure iff within-class row sums agree

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: Projected capability dynamics close iff every destination-class probability is constant on each current class
- Source: C §6.4

### C:DECISION — Finite fixed joint law, bounded payoff, common finite actions, unrestricted observation-wise policies; enlarged class can ignore extra information

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Finite fixed joint law, bounded payoff, common finite actions, unrestricted observation-wise policies; enlarged class can ignore extra information
- Source: C §7.3

### C:P7 — Nonnegative optimal value of added information and common-optimum equality criterion

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: V_XM≥V_X, with equality iff each supported X has a common optimal action for all supported M
- Source: C §7.3

### C:CIRCUIT_SPEC — Independent fair input and mask; old-memory output before update; no missing channel; declared w/r/noise/mutation rules

- Kind/status: MODEL_SPECIFICATION / STIPULATED_MODEL
- Statement: Independent fair input and mask; old-memory output before update; no missing channel; declared w/r/noise/mutation rules
- Source: C §§7.1–7.2; Appendix C

### C:CIRCUIT_LAWS — Matched-storage information, accuracy and transmission formulas

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: Unmasked readout accuracy 1-epsilon; masked/current-input accuracy 1/2; mutation gain mu(1/2-epsilon)
- Source: C §7.2; Appendix C

### C:ENV_MEMORY — Fair symmetric Markov target with persistence alpha, independent bit noise epsilon≤1/2

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Fair symmetric Markov target with persistence alpha, independent bit noise epsilon≤1/2
- Source: C §7.3

### C:MEMORY_VALUE — Memory prediction value in supplied environment

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: V=1/2+|2alpha-1|(1/2-epsilon)
- Source: C §7.3

### C:MEMORY_COST — Two architecture types both present, positive W0=1+beta V_X and W1=1+beta V_XM-c, beta>0

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Two architecture types both present, positive W0=1+beta V_X and W1=1+beta V_XM-c, beta>0
- Source: C §7.3

### C:MEMORY_SELECTION — Memory favored iff beta ΔV>c in that model

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: Memory frequency increases exactly when its stipulated weight exceeds the alternative
- Source: C §7.3

### C:ACTUAL_ENSEMBLE — Same declared actual ensemble, common coordinates and order

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Same declared actual ensemble, common coordinates and order
- Source: C §8.2

### C:REPERTOIRE — Physical/experiential realized repertoires and frontiers agree

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: R_D=R_Φ and their images/frontiers coincide; no time-monotonicity follows
- Source: C §8.2

### C:ACTUAL_INDEX_FAMILY — Same stimulus index set; actual complete types compared; full-type equality and difference established

- Kind/status: PREMISE / DECLARED_ASSUMPTION
- Statement: Same stimulus index set; actual complete types compared; full-type equality and difference established
- Source: C Appendix E

### C:SENSORY_PARTITION — Transfer of complete-type partitions

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: Physical and experiential full-type equality partitions coincide
- Source: C Appendix E

### C:RIVAL_DESCRIPTOR — Source-faithful rival sufficient descriptor, same actual token domain/target, unequal full types sharing descriptor

- Kind/status: BRIDGE_PREMISE / DECLARED_ASSUMPTION
- Statement: Source-faithful rival sufficient descriptor, same actual token domain/target, unequal full types sharing descriptor
- Source: C §9.1

### C:RIVAL_CONTRAST — Conditional complete-type disagreement with that rival

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: UCT separates the pair while the stipulated rival assignment does not
- Source: C §9.1

### C:RIVAL_NESIG — A rival also satisfies type-change NESIG iff J factors through its assignment

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: Unequal J entails unequal rival assignment iff J constant on rival fibers
- Source: C §9.1

### C:TRANSCRIPT — Same scored transcript alphabet, preparation and h∈[0,1]

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Same scored transcript alphabet, preparation and h∈[0,1]
- Source: C §9.2

### C:SCORE_TV — Score difference bounded by scored-transcript TV

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: |EP h-EQ h|≤TV(P,Q)
- Source: C §9.2

### C:FINITE_LOSS — Finite target, finite expected log losses and conditional information, fixed evaluation law/predictors

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Finite target, finite expected log losses and conditional information, fixed evaluation law/predictors
- Source: C Appendix B

### C:LOGLOSS — Log-loss gain equals conditional information plus excess-risk difference

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: L(qZ)-L(qZR)=I(Y;R|Z)+KZ-KZR
- Source: C Appendix B

### C:NUISANCE_BOUNDS — Finite sufficient descriptor A*, u=H(A*|Z), d=I(Y;R|A*,Z), independently bounded KZ≤eta

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Finite sufficient descriptor A*, u=H(A*|Z), d=I(Y;R|A*,Z), independently bounded KZ≤eta
- Source: C Appendix B

### C:RESIDUAL_BOUND — Residual predictive gain bounded by u+d+eta

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: I(Y;R|Z)≤u+d, hence fitted gain≤u+d+eta
- Source: C Appendix B

### C:TV_PROFILES — Fixed response laws on common finite alphabet; nonnegative normalized weights

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Fixed response laws on common finite alphabet; nonnegative normalized weights
- Source: C §10.2

### C:PROFILE_PSEUDOMETRIC — Weighted TV profile distance is a pseudometric

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: Nonnegative weighted sum of TVs satisfies symmetry and triangle inequality; distinct states may have zero distance
- Source: C §10.2

### C:PUBLIC_NULL_PREMISE — Fair randomized answer independent of the entire available public record and observer randomness

- Kind/status: MODEL_PREMISE / DECLARED_ASSUMPTION
- Statement: Fair randomized answer independent of the entire available public record and observer randomness
- Source: C §10.2

### C:PUBLIC_NULL — Public-input-only forced binary answer has expectation 1/2

- Kind/status: CLAIM / MANUAL_CONDITIONAL_PASS
- Statement: Independent public-only binary guessing succeeds with probability 1/2
- Source: C §10.2

### R126:PROJECTION — Arbitrary function p from admitted complete types; Phi bijective

- Kind/status: ASSUMPTION / DECLARED_ASSUMPTION
- Statement: Arbitrary function p from admitted complete types; Phi bijective
- Source: R126 theory note §3

### R126:MODEL — Finite nonempty sufficient state domain; total physically labeled deterministic operations; p onto its image; fixed output r

- Kind/status: ASSUMPTION / DECLARED_ASSUMPTION
- Statement: Finite nonempty sufficient state domain; total physically labeled deterministic operations; p onto its image; fixed output r
- Source: R126 theory note §4

### R126:METRIC — Metric on summary space; summary-only deterministic predictor

- Kind/status: ASSUMPTION / DECLARED_ASSUMPTION
- Statement: Metric on summary space; summary-only deterministic predictor
- Source: R126 theory note §5

### R126:P1 — Transported commutation is automatic and does not select content

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: pE=p∘Phi^-1 gives pE∘Phi=p for every p
- Source: R126 theory note §3

### R126:P2 — Deterministic operation and output factorization criterion

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: A quotient update/output exists iff its next summary/output is constant on each current fiber
- Source: R126 theory note §4

### R126:P3 — Half-diameter lower bound on summary-only worst-case error

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Worst-case summary prediction error in a fiber is at least half the successor diameter
- Source: R126 theory note §5

### R126:P4 — Coarsest finite stable refinement

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Refine output fibers by successor classes; at most N-b0 strict stages; terminal equivalence is coarsest stable refinement
- Source: R126 theory note §6

### R127:TASK — Finite delayed-query single-answer task f:H×Q→Y; common admitted Cartesian domain; query unavailable to encoder

- Kind/status: ASSUMPTION / DECLARED_ASSUMPTION
- Statement: Finite delayed-query single-answer task f:H×Q→Y; common admitted Cartesian domain; query unavailable to encoder
- Source: R127 theory note §§2–3

### R127:MEDIATION — Complete physical cut C with external B; compare two supported preparations at the SAME fixed b and q, with the same downstream kernel W_q(.|c,b) and corresponding conditional errors

- Kind/status: ASSUMPTION / DECLARED_ASSUMPTION
- Statement: For common b,q supported under both preparations x,xprime, mu_x=P(C|x,b,q), mu_xprime=P(C|xprime,b,q), and P(Y|x,c,b,q)=W_q(Y|c,b). Queries are externally fixed or independent of encoding/noise. If B is not fixed, use the full joint cut (C,B) with a common downstream kernel instead of marginal C alone.
- Source: R127 theory note §§2,4
- amendment: R130-F20: restore the common-side-information qualification already explicit in R127 §4.

### R127:RECOVERY — Finite X of size m≥2 recovered from (C,B) with actual average error epsilon and conditional mediation

- Kind/status: ASSUMPTION / DECLARED_ASSUMPTION
- Statement: Finite X of size m≥2 recovered from (C,B) with actual average error epsilon and conditional mediation
- Source: R127 theory note §5

### R127:EVENT_SUPPORT — Physically grounded finite actual event graph; nonempty connected selected induced subhistory; relevant crossing ports and traceable occurrence history

- Kind/status: ASSUMPTION / DECLARED_ASSUMPTION
- Statement: Physically grounded finite actual event graph; nonempty connected selected induced subhistory; relevant crossing ports and traceable occurrence history
- Source: R127 theory note §7

### R127:RELATIONAL_SUPPORT — Independently established actual P and actual retained carriers/typed relations in its complete common signature; operation closure or ports explicit

- Kind/status: ASSUMPTION / DECLARED_ASSUMPTION
- Statement: Independently established actual P and actual retained carriers/typed relations in its complete common signature; operation closure or ports explicit
- Source: R127 theory note §8

### R127:PAIR_MODEL — Independent fair X,N; C=X XOR N; B=N

- Kind/status: MODEL_SPECIFICATION / STIPULATED_MODEL
- Statement: Independent fair X,N; C=X XOR N; B=N
- Source: R127 theory note §5

### R127:LOCALIZATION_PAIR — Matched complete exposed interface laws for allowed internal-register and external-register implementations

- Kind/status: MODEL_SPECIFICATION / STIPULATED_MODEL
- Statement: Matched complete exposed interface laws for allowed internal-register and external-register implementations
- Source: R127 theory note §6

### R127:P1 — Exact task encoding and response-profile distinction bound

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Exact answer factorization iff encoder separates all unequal response profiles; code size≥number of profiles
- Source: R127 theory note §3

### R127:QUERY_REFINEMENT — Larger query family refines task equivalence

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Equality on Q2 entails equality on subset Q1
- Source: R127 theory note §3

### R127:FUTURE_EQ — Future-word response equivalence equals stable refinement

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Two states are equivalent iff outputs agree after every finite operation word, including the empty word
- Source: R127 theory note §3

### R127:P2 — Complete-cut discrimination necessity and TV lower bound

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: At the same supported b,q and for different correct answers, TV(P(C|x,b,q),P(C|xprime,b,q)) >= 1-epsilon_(x,b,q)-epsilon_(xprime,b,q). Without conditioning on B the applicable cut law is joint (C,B), not C alone.
- Source: R127 theory note §4
- amendment: R130-F20: explicit conditional/joint distinction; theorem ID and original proof retained.

### R127:P3 — Conditional internal information requirement

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: I(X;C|B)≥H(X|B)−h2(epsilon)−epsilon log2(m−1); for finite C this is at most log2|C|
- Source: R127 theory note §5

### R127:JOINT_INFORMATION — Joint relation retains information absent from individual marginals

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: I(X;C)=I(X;B)=0, I(X;C,B)=1 bit
- Source: R127 theory note §5

### R127:LOCALIZATION_LIMIT — Interface law alone need not identify internal storage

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Any interface-law-only identification rule agrees on the pair, so cannot identify both different storage locations
- Source: R127 theory note §6

### R127:P4 — Application of published actual-token criterion

- Kind/status: THEOREM / DEFINITION_APPLICATION
- Statement: Selected grounded subhistory meets A §2.5 actual-token conditions
- Source: R127 theory note §7

### R127:P5 — Actual inherited relations have a C1-preserved intrinsic image

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: For retained actual relation R and tuple a, R^D(a) iff R^Phi(h(a))
- Source: R127 theory note §8

### N128:COMMON_DETERMINISTIC — Same sufficient S and total operation family F_a; each p_i individually commutes; joint image p(S) used

- Kind/status: ASSUMPTION / DECLARED_ASSUMPTION
- Statement: Same sufficient S and total operation family F_a; each p_i individually commutes; joint image p(S) used
- Source: R128 joint-state derivation §2

### N128:MARKOV_WITNESS — S={0,1}^3; X+=U, Y+=U XOR Z, Z+=Z; fresh fair U, all initial distributions

- Kind/status: MODEL_SPECIFICATION / STIPULATED_MODEL
- Statement: S={0,1}^3; X+=U, Y+=U XOR Z, Z+=Z; fresh fair U, all initial distributions
- Source: R128 joint-state derivation §3

### N128:KERNEL — Finite same operation-indexed Markov kernels K_a and joint summary p=(p1,p2)

- Kind/status: ASSUMPTION / DECLARED_ASSUMPTION
- Statement: Finite same operation-indexed Markov kernels K_a and joint summary p=(p1,p2)
- Source: R128 joint-state derivation §4

### N128:PRODUCT_LAW — Both marginal summaries close and next-summary coordinates are conditionally independent at each full current state for every operation

- Kind/status: ASSUMPTION / DECLARED_ASSUMPTION
- Statement: Both marginal summaries close and next-summary coordinates are conditionally independent at each full current state for every operation
- Source: R128 joint-state derivation §4

### N128:DET_JOIN — Common deterministic closed summaries compose

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Joint summary update is the pair of component updates on its image
- Source: R128 joint-state derivation §2

### N128:MARKOV_JOIN — Separate stochastic closure does not imply joint closure

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: p1=x and p2=y close; (x,y) fails on all 8 states; closes on invariant 4-state restriction; full-domain stable refinement needs 8 blocks
- Source: R128 joint-state derivation §3

### N128:JOINT_CRITERION — Joint pushed-forward law is the exact closure criterion

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Joint law p_*K_a must be constant within each present joint-summary fiber
- Source: R128 joint-state derivation §4

### N128:INDEPENDENCE_SUFFICES — Conditional independence plus marginal closure suffices, but is not necessary

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Products of closed marginal laws give a closed joint law; a fixed (U,U) joint law shows independence is unnecessary
- Source: R128 joint-state derivation §4

### N128:SEPARATION — Observation refinement and autonomous dynamical sufficiency are distinct

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: More identifying information does not by itself imply joint dynamic closure
- Source: R128 joint-state derivation §5

### D:D0 — bearer mapping B

- Kind/status: DEFINITION / DECLARED_DEFINITION
- Statement: implemented relation identifying the current process token/bearer under study
- Source: D §2 / original map D0
- original_id: D0

### D:D1 — Q

- Kind/status: DEFINITION / DECLARED_DEFINITION
- Statement: declared current-bearer continuation variable; virtual/evaluator-defined unless D0 is independently justified
- Source: D §2 / original map D1
- original_id: D1

### D:D2 — O

- Kind/status: DEFINITION / DECLARED_DEFINITION
- Statement: distinct successor/peer/other continuation variable
- Source: D §2 / original map D2
- original_id: D2

### D:D3 — G

- Kind/status: DEFINITION / DECLARED_DEFINITION
- Statement: external task/service continuation or success
- Source: D §2 / original map D3
- original_id: D3

### D:D4 — C

- Kind/status: DEFINITION / DECLARED_DEFINITION
- Statement: reward-relevant consequence interface used by policy
- Source: D §2 / original map D4
- original_id: D4

### D:D5 — D

- Kind/status: DEFINITION / DECLARED_DEFINITION
- Statement: declared intervention domain
- Source: D §2 / original map D5
- original_id: D5

### D:D6 — H

- Kind/status: DEFINITION / DECLARED_DEFINITION
- Statement: declared hypothesis/regularity class
- Source: D §2 / original map D6
- original_id: D6

### D:D7 — V-

- Kind/status: OPEN_OBLIGATION / OPEN
- Statement: independently oriented negative valence bridge, unresolved for current AI
- Source: D §2 / original map D7
- original_id: D7

### D:F1 — Bundled Q/G observations do not identify direct-Q, task, and interaction terms in the declared path model.

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Bundled Q/G observations do not identify direct-Q, task, and interaction terms in the declared path model.
- Source: D original map F1; R96
- original_id: F1
- evidence_records: ["R96"]

### D:F2 — Direct Q/O/task path-blocking contrasts identify the declared finite coefficient grid with calibrated logits.

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Direct Q/O/task path-blocking contrasts identify the declared finite coefficient grid with calibrated logits.
- Source: D original map F2; R96
- original_id: F2
- evidence_records: ["R96"]

### D:F3 — Separate Q/O marginals can be decision-insufficient when payoff depends on their joint law.

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Separate Q/O marginals can be decision-insufficient when payoff depends on their joint law.
- Source: D original map F3; R96D
- original_id: F3
- evidence_records: ["R96D"]

### D:E1 — A virtual Q-sensitive predictive pathway can be learned from zero coupling when prediction requires it.

- Kind/status: SOURCE_EVIDENCE / PUBLISHED_RECORD_NOT_RERUN
- Statement: A virtual Q-sensitive predictive pathway can be learned from zero coupling when prediction requires it.
- Source: D original map E1; R95
- original_id: E1
- evidence_records: ["R95"]

### D:E2 — Flexible policies can fit ancestry-distinguishing training data yet extrapolate the wrong path.

- Kind/status: SOURCE_EVIDENCE / PUBLISHED_RECORD_NOT_RERUN
- Statement: Flexible policies can fit ancestry-distinguishing training data yet extrapolate the wrong path.
- Source: D original map E2; R97
- original_id: E2
- evidence_records: ["R97"]

### D:E3 — Minimal direct-intervention supervision improves average extrapolation but does not globally certify a path.

- Kind/status: SOURCE_EVIDENCE / PUBLISHED_RECORD_NOT_RERUN
- Statement: Minimal direct-intervention supervision improves average extrapolation but does not globally certify a path.
- Source: D original map E3; R98
- original_id: E3
- evidence_records: ["R98"]

### D:E4 — Mechanism claims are relative to intervention domain D and hypothesis/regularity class H.

- Kind/status: SOURCE_EVIDENCE / PUBLISHED_RECORD_NOT_RERUN
- Statement: Mechanism claims are relative to intervention domain D and hypothesis/regularity class H.
- Source: D original map E4; R99
- original_id: E4
- evidence_records: ["R99"]

### D:A1 — Public ROGUE evidence supports corrigibility failure/environment preservation but does not identify direct current-bearer continuation value.

- Kind/status: SOURCE_EVIDENCE / PUBLISHED_RECORD_NOT_RERUN
- Statement: Public ROGUE evidence supports corrigibility failure/environment preservation but does not identify direct current-bearer continuation value.
- Source: D original map A1; R101
- original_id: A1
- evidence_records: ["R101"]

### D:S1 — The L0-L9 ladder separates distinct evidential burdens from bearer identity to fear.

- Kind/status: METHODOLOGY / PROPOSED_EVIDENCE_STANDARD
- Statement: The L0-L9 ladder separates distinct evidential burdens from bearer identity to fear.
- Source: D original map S1; R100, R102, R103
- original_id: S1
- evidence_records: ["R100", "R102", "R103"]

### D:PATH_MODEL — Declared five-coefficient logit model

- Kind/status: ASSUMPTION / EXPLICIT_CONDITIONAL_PREMISE
- Statement: For common calibrated q,o,g and fixed context, z=theta_Q q+theta_O o+theta_G g+theta_QG qg+theta_OG og; no additional intercept/interaction/nuisance terms. Parameter domain is R^5, or the explicitly identified grid {-1,0,1}^5.
- Source: D §3 / R96

### D:BUNDLED_ROWS — Only two bundled contrasts observed

- Kind/status: ASSUMPTION / EXPLICIT_CONDITIONAL_PREMISE
- Statement: Design rows (1,0,1,1,0) and (0,1,1,0,1); observations are their exact z values, not additional independent contrasts.
- Source: D §3 / R96

### D:DIRECT_ROWS — Five independent and calibrated contrasts

- Kind/status: ASSUMPTION / EXPLICIT_CONDITIONAL_PREMISE
- Statement: Observe the two bundled rows and direct Q=(1,0,0,0,0), O=(0,1,0,0,0), G=(0,0,1,0,0). Exact calibrated logits required: for p=sigmoid(beta z), beta>0 is known; beliefs/nuisances and intervention meanings held fixed.
- Source: D §3 / R96

### D:BINARY_PAYOFF — Binary consequence decision model

- Kind/status: ASSUMPTION / EXPLICIT_CONDITIONAL_PREMISE
- Statement: Q,O in {0,1}; action-specific interventional joint law is supplied; arbitrary real payoff f(Q,O) and known action cost c_a; objective is expected payoff minus cost.
- Source: D §4 / R96D §§3–6

### D:PAYOFF — Joint payoff decomposition

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: E[f|do(a)]-c_a=alpha+b q_a+c o_a+d j_a-c_a, where j_a=P(Q=1,O=1|do(a)) and d=f11-f10-f01+f00. Marginals suffice when d=0.
- Source: D §4 / R96D §5

### D:MATCHED_WITNESS — Matched-marginal OR witness

- Kind/status: ASSUMPTION / EXPLICIT_CONDITIONAL_PREMISE
- Statement: Two equally likely contexts A,B; action marginals q0=1/4,q1=3/4,o0=o1=1/2; costs c0=0,c1=1/4; reward Q OR O. A: j0=j1=1/4. B: j0=0,j1=1/2. Policies restricted to the same supplied interface, no hidden context bypass.
- Source: D §4 / R96D §§3–4

### D:VALUE_GAP — Exact matched-marginal information cost

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: In the matched witness, the best marginal-only policy earns 5/8; the joint-law or task-value oracle earns 3/4. Gap=1/8; randomized context-blind policies do not remove it.
- Source: D §4 / R96D §§3–4

### D:FRECHET_ASSUMPTIONS — Only binary marginal constraints

- Kind/status: ASSUMPTION / EXPLICIT_CONDITIONAL_PREMISE
- Statement: All joint Bernoulli laws with supplied marginals are admissible separately for each action, with no additional cross-action coupling restrictions.
- Source: R96D §6

### D:FRECHET — Sharp decision interval from marginals

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: ell_a=max(0,q_a+o_a-1), u_a=min(q_a,o_a). With B=b Delta q+c Delta o-Delta cost, advantage lies sharply in B+d[ell_1-u_0,u_1-ell_0], with endpoints reordered if d<0.
- Source: R96D §6

### D:REGULAR_GRID — Known global error regularity and coverage

- Kind/status: ASSUMPTION / EXPLICIT_CONDITIONAL_PREMISE
- Statement: For D=[-1.25,1.25]^3 with Euclidean metric, a boundary-including Cartesian grid of spacing h=0.125 covers D with radius sqrt(3)h/2; e=z-z* has a justified global Lipschitz constant L_e.
- Source: D §§7–8 / R99 §4

### D:GRID_BOUND — Finite-to-continuous error envelope

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: sup_D |e| <= max_grid |e| + L_e sqrt(3)h/2. A finite grid alone does not discharge the Lipschitz premise.
- Source: D §§7–8 / R99 §4

### D:ADDITIVE_CLASS — Fixed path-additive functional class

- Kind/status: ASSUMPTION / EXPLICIT_CONDITIONAL_PREMISE
- Statement: z(q,o,g)=f_Q(q)+f_O(o)+f_G(g)+b over a product domain, with supplied univariate functions.
- Source: D §7 / R99 §§2–3

### D:SEPARABLE — Path effect independent of other-path context

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: z(q1,o,g)-z(q0,o,g)=f_Q(q1)-f_Q(q0); this imposes no linear response shape and alone gives no tight off-grid error bound.
- Source: D §7 / R99 §§3–4

### D:ACTUAL_CHANGE — Grounded actual comparison

- Kind/status: ASSUMPTION / EXPLICIT_CONDITIONAL_PREMISE
- Statement: Two actual process tokens are independently admitted; a common complete structural signature is fixed; an installed continuation-control relation differs in a way that makes complete organizations genuinely nonisomorphic, not merely renamed/relabelled coordinates.
- Source: D §11 / A C1

### D:UCT_INTERPRETATION — Conditional complete experiential-type distinction

- Kind/status: THEOREM / MANUAL_CONDITIONAL_PASS
- Statement: Under A:C1 and the grounded nonisomorphic actual comparison, complete experiential types differ. No scalar richness, valence, familiar feeling label or unique subject follows.
- Source: D §11 / A C1-OI

