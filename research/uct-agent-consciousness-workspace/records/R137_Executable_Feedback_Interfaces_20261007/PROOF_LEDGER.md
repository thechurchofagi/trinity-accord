# Unified proof ledger — R137

328 nodes / 157 rules. All previous nodes/rules retained field-for-field. All metadata exported. Conditional manual proofs, not proof-assistant certification. Full new proofs: R137_Executable_Feedback.md.

## Rule a01

- **all_of:** ["A:C1"]
- **conclusion:** A:C1_OI
- **statement:** D(P)≅D(Q) iff Φ(P)≅Φ(Q) in the same complete signature
- **proof_sketch:** Compose tokenwise isomorphisms and their inverses in either direction.
- **source:** A §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a02

- **all_of:** ["A:C1_OI"]
- **conclusion:** A:C1_W
- **statement:** Complete physical equivalence implies full experiential equivalence
- **proof_sketch:** Take forward implication.
- **source:** A §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a03

- **all_of:** ["A:C1", "A:NONEMPTY_CARRIER"]
- **conclusion:** A:U1
- **statement:** Every actual token has a nonempty distinguished experiential carrier
- **proof_sketch:** Sort-preserving bijection preserves nonemptiness.
- **source:** A §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a04

- **all_of:** ["A:C1", "A:QSPACE", "A:GEOMETRY"]
- **conclusion:** A:U2
- **statement:** Physical and experiential quotient-valued maps have identical continuity and distances
- **proof_sketch:** The two maps are pointwise equal; use the same predeclared geometry.
- **source:** A §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a05

- **all_of:** ["A:U1", "A:SELF_WITNESS"]
- **conclusion:** A:U3
- **statement:** Conceptual selfhood is not necessary for basal experience in a domain containing the witness
- **proof_sketch:** Apply U1 to the actual non-self witness.
- **source:** A §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a06

- **all_of:** ["A:C1", "A:P3", "A:P6", "A:U1", "A:U2", "A:U3"]
- **conclusion:** A:U0
- **statement:** Prior foundational roles have the stated derivation/ontology decomposition
- **proof_sketch:** Collect prior derivations; preserve every context premise and witness.
- **source:** A §4
- **kind:** META_DEPENDENCY_RESULT
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a07

- **all_of:** ["A:U1", "A:NONUNIV_WITNESS"]
- **conclusion:** A:ORG_GATE
- **statement:** A mechanism absent at an actual same-domain witness cannot equal universal E=1
- **proof_sketch:** At the witness, E=1 and candidate gate=0.
- **source:** A §5.1
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a08

- **all_of:** ["A:C1_W", "A:COMPLETE_EQ"]
- **conclusion:** A:NO_HIDDEN
- **statement:** No extra full-type phenomenal variation at fixed complete organization
- **proof_sketch:** Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- **source:** A §5.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a09

- **all_of:** ["A:C1_W", "A:COMPLETE_EQ", "A:PROBE_ONLY"]
- **conclusion:** A:PROBE_INV
- **statement:** Description/probe-choice-only change preserves full experiential type
- **proof_sketch:** Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- **source:** A §5.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a10

- **all_of:** ["A:C1_W", "A:COMPLETE_EQ", "A:FUTURE_ONLY"]
- **conclusion:** A:NO_FUTURE
- **statement:** Future-only divergence does not change present type if complete present organization is equal
- **proof_sketch:** Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- **source:** A §5.4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a11

- **all_of:** ["A:C1_W", "A:COMPLETE_EQ", "A:HISTORY_DIFF"]
- **conclusion:** A:GHOST_EQ
- **statement:** Screened history does not change current full experiential type
- **proof_sketch:** Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- **source:** A §5.5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a12

- **all_of:** ["A:C1_W", "A:COMPLETE_EQ", "A:LABEL_ONLY"]
- **conclusion:** A:REWARD_NONID
- **statement:** External reward-label change alone cannot change intrinsic phenomenal type
- **proof_sketch:** Apply complete-type sufficiency; the extra premise specifies what differs without changing complete current organization.
- **source:** A §5.6
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a13

- **all_of:** ["A:GHOST_EQ", "A:P6", "A:HISTORY_DIFF"]
- **conclusion:** A:GHOST_TOKEN_NOTE
- **statement:** Equal current types do not identify numerical occurrences or causal lineages
- **proof_sketch:** Type equivalence is distinct from numerical token identity by P6.
- **source:** A §5.5
- **kind:** ONTOLOGICAL_ADDENDUM
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a14

- **all_of:** ["A:C1", "A:PRODUCT_DEF", "A:ACTUAL_WHOLE_PARTS", "A:PHYS_NONPRODUCT"]
- **conclusion:** A:NONSUM
- **statement:** A nonproduct actual whole is not the specified independent product of experiential constituents
- **proof_sketch:** Products in the common category preserve constituent isomorphisms; the opposite conclusion contradicts physical nonproduct.
- **source:** A §6.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a15

- **all_of:** ["A:C1_W", "A:MACRO_EQ"]
- **conclusion:** A:MACRO_EXP_EQ
- **statement:** Complete macro equivalence preserves macro experiential type
- **proof_sketch:** Apply C1-W to the independently justified macro tokens.
- **source:** A §6.4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a16

- **all_of:** ["A:C1_OI", "A:MICRO_NONISO"]
- **conclusion:** A:MICRO_EXP_DIFF
- **statement:** Complete lower-token nonisomorphism entails lower experiential difference
- **proof_sketch:** Contrapose the reverse equivalence.
- **source:** A §6.4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a17

- **all_of:** ["A:SYM_PREM", "A:EQUIV_SELECTOR"]
- **conclusion:** A:ORBIT_LEMMA
- **statement:** Invariant deterministic selected family is a union of candidate orbits
- **proof_sketch:** If P selected then gP selected for each structure automorphism g.
- **source:** A §7.1
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a18

- **all_of:** ["A:ORBIT_LEMMA", "A:OVERLAP_NONEMPTY_EXCL"]
- **conclusion:** A:SELECTION_OBSTRUCTION
- **statement:** One overlapping candidate orbit admits no nonempty disjoint invariant selection
- **proof_sketch:** One selected member forces the entire overlapping orbit.
- **source:** A §7.1
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a19

- **all_of:** ["A:U1", "A:ALL_ANC_ACTUAL"]
- **conclusion:** A:E1
- **statement:** E=1 throughout the admitted actual-token comparison family
- **proof_sketch:** Apply U1 member by member; no continuity premise is needed.
- **source:** A §8.1
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a20

- **all_of:** ["A:C1", "A:QSPACE", "A:GEOMETRY", "A:EPS_CHAIN"]
- **conclusion:** A:E2
- **statement:** Physical epsilon-fine chains are equally fine experiential chains
- **proof_sketch:** Replace each physical quotient point by its equal experiential point.
- **source:** A §8.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a21

- **all_of:** ["A:CONNECTED_LAMBDA", "A:CONT_BINARY_E", "A:HUMAN_ENDPOINT"]
- **conclusion:** A:E3
- **statement:** A continuous discrete-valued E on a connected space, with E=1 somewhere, is identically one
- **proof_sketch:** Continuous image connected; a nonempty connected subset of {0,1} is a singleton.
- **source:** A §8.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a22

- **all_of:** ["A:U2", "A:PHYS_CONT_PATH"]
- **conclusion:** A:U2_APP
- **statement:** A supplied continuous physical path has a continuous experiential path
- **proof_sketch:** Use the U2 transfer with its physical-path premise.
- **source:** A §8.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a23a

- **all_of:** ["A:E1", "A:E2"]
- **conclusion:** A:EVOL_SYNTH
- **statement:** Nonempty experience throughout plus equally fine structural change
- **proof_sketch:** Conjoin existence and fine-chain results; do not infer monotone richness.
- **source:** A §8
- **kind:** CONDITIONAL_SYNTHESIS
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a23b

- **all_of:** ["A:E1", "A:U2_APP"]
- **conclusion:** A:EVOL_SYNTH
- **statement:** Nonempty experience throughout plus equally continuous structural change
- **proof_sketch:** Alternative route using a continuous path instead of a fine-chain premise.
- **source:** A §8
- **kind:** CONDITIONAL_SYNTHESIS
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a24

- **all_of:** ["A:C1_OI", "A:PHYS_TRANSFORM_NONISO"]
- **conclusion:** A:STRUCT_TRANSFORM
- **statement:** Actual complete structural transformation entails full experiential type change
- **proof_sketch:** Contrapose full-type equivalence.
- **source:** A §9
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a25

- **all_of:** ["A:TOY_MATH"]
- **conclusion:** A:TOY_WHOLE_DIFF
- **statement:** Specified register transition image sizes distinguish whole modeled types
- **proof_sketch:** Over F2 the pair matrices have ranks 0,1,1,2; powers give 1,2→1,2→1,4 retained classes.
- **source:** A §9 and Appendix B
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a26

- **all_of:** ["A:TOY_MATH"]
- **conclusion:** A:TOY_SUB_EQ
- **statement:** The specified s-process and declared output remain unchanged
- **proof_sketch:** s+=s XOR u is independent of downstream pair; projection/reset diagram commutes.
- **source:** A Appendix B
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a27

- **all_of:** ["A:TOY_WHOLE_DIFF", "A:ACTUAL_COMPLETE_TOY", "A:C1_OI"]
- **conclusion:** A:TOY_EXP_WHOLE
- **statement:** The actual complete whole realizations would differ experientially
- **proof_sketch:** Apply C1-OI only after the actual/completeness premise.
- **source:** A §9.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a28

- **all_of:** ["A:TOY_SUB_EQ", "A:ACTUAL_COMPLETE_TOY", "A:C1_W"]
- **conclusion:** A:TOY_EXP_SUB
- **statement:** The actual complete implemented sub-process realizations would agree in type
- **proof_sketch:** Apply C1-W to that sub-process, not the entire network.
- **source:** A §9.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a29

- **all_of:** ["A:C1", "A:BRIDGE_FWD", "A:MEAS"]
- **conclusion:** A:OSC_FWD
- **statement:** One-way operational correspondence is a package with an independently assumed forward bridge
- **proof_sketch:** Package construction; finite prediction is supplied by the bridge, not deduced from full C1 alone.
- **source:** A §10
- **kind:** ASSUMPTION_PACKAGE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a30

- **all_of:** ["A:C1", "A:BRIDGE_FWD", "A:BRIDGE_REV", "A:MEAS"]
- **conclusion:** A:OSC_TWO
- **statement:** Two-way operational correspondence additionally assumes reflection
- **proof_sketch:** Lossy projection does not supply reflection.
- **source:** A §10
- **kind:** ASSUMPTION_PACKAGE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a31

- **all_of:** ["A:FROZEN_SCOPE", "A:FORWARD_MISMATCH", "A:MEAS"]
- **conclusion:** A:FAIL_ONE
- **statement:** A valid same-view/different-target case falsifies that forward bridge package
- **proof_sketch:** It is a counterexample to the finite implication; does not isolate C1.
- **source:** A §12.1
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a32

- **all_of:** ["A:FROZEN_SCOPE", "A:REVERSE_MISMATCH", "A:MEAS"]
- **conclusion:** A:FAIL_TWO
- **statement:** A valid different-view/same-target case falsifies the reflection direction
- **proof_sketch:** It is a counterexample to reflection, not complete experiential equivalence evidence.
- **source:** A §12.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a33

- **all_of:** ["A:P3", "A:ACTUAL_PERSISTING_PARTS", "A:U1"]
- **conclusion:** A:COEXISTENCE
- **statement:** Persisting nested actual tokens remain experience-bearing
- **proof_sketch:** P3 retains tokenhood; U1 applies to each continuing token.
- **source:** A §§2.4,6.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a34

- **all_of:** ["A:FINITE_COARSE_SETUP"]
- **conclusion:** A:COARSE_CLOSURE
- **statement:** A deterministic quotient exists iff equal summaries give equal successor summaries
- **proof_sketch:** Necessity by equal arguments; sufficiency by representative-independent definition.
- **source:** A Appendix D
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b01

- **all_of:** ["B:VIEW", "B:LANGUAGE", "B:BAC", "B:EXPRESSIBLE"]
- **conclusion:** B:REP
- **statement:** A translator evaluates all declared admissible expressions
- **proof_sketch:** Structural induction: leaves are admitted inputs/constants; each typed primitive composes previously defined values.
- **source:** B §4.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b02

- **all_of:** ["A:U1", "B:TARGET_DOMAIN"]
- **conclusion:** B:GATE
- **statement:** The stipulated universal rival gate conflicts at its admitted witness
- **proof_sketch:** E=1 but the necessary gate is absent; a witness outside the rival domain does not work.
- **source:** B §5.5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b03

- **all_of:** ["A:P3", "A:U1", "B:OVERLAP_WITNESS"]
- **conclusion:** B:EXCLUSION_CONFLICT
- **statement:** Overlap/nonmaximality alone cannot erase a persisting token's UCT experience
- **proof_sketch:** P3 preserves the actual token; U1 gives nonempty experience, contrary to the scoped rival assignment.
- **source:** B §6
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_IIT

- **all_of:** ["B:VIEW", "B:BAC", "B:TFR", "B:IIT_BRIDGE"]
- **conclusion:** B:IIT
- **statement:** Conditional IIT mechanism representation with stated residuals
- **proof_sketch:** Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- **source:** B §6
- **kind:** CONDITIONAL_TRANSLATION
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_RPT

- **all_of:** ["B:VIEW", "B:BAC", "B:TFR", "B:RPT_BRIDGE"]
- **conclusion:** B:RPT
- **statement:** Conditional RPT mechanism representation with stated residuals
- **proof_sketch:** Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- **source:** B §7
- **kind:** CONDITIONAL_TRANSLATION
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_GNWT

- **all_of:** ["B:VIEW", "B:BAC", "B:TFR", "B:GNWT_BRIDGE"]
- **conclusion:** B:GNWT
- **statement:** Conditional GNWT mechanism representation with stated residuals
- **proof_sketch:** Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- **source:** B §8
- **kind:** CONDITIONAL_TRANSLATION
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_HOT

- **all_of:** ["B:VIEW", "B:BAC", "B:TFR", "B:HOT_BRIDGE"]
- **conclusion:** B:HOT
- **statement:** Conditional HOT mechanism representation with stated residuals
- **proof_sketch:** Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- **source:** B §9
- **kind:** CONDITIONAL_TRANSLATION
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_AST

- **all_of:** ["B:VIEW", "B:BAC", "B:TFR", "B:AST_BRIDGE"]
- **conclusion:** B:AST
- **statement:** Conditional AST mechanism representation with stated residuals
- **proof_sketch:** Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- **source:** B §9
- **kind:** CONDITIONAL_TRANSLATION
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_PP_AI

- **all_of:** ["B:VIEW", "B:BAC", "B:TFR", "B:PP_AI_BRIDGE"]
- **conclusion:** B:PP_AI
- **statement:** Conditional PP_AI mechanism representation with stated residuals
- **proof_sketch:** Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- **source:** B §10
- **kind:** CONDITIONAL_TRANSLATION
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_DIT

- **all_of:** ["B:VIEW", "B:BAC", "B:TFR", "B:DIT_BRIDGE"]
- **conclusion:** B:DIT
- **statement:** Conditional DIT mechanism representation with stated residuals
- **proof_sketch:** Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- **source:** B §11
- **kind:** CONDITIONAL_TRANSLATION
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_MTOC

- **all_of:** ["B:VIEW", "B:BAC", "B:TFR", "B:MTOC_BRIDGE"]
- **conclusion:** B:MTOC
- **statement:** Conditional MTOC mechanism representation with stated residuals
- **proof_sketch:** Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- **source:** B §12
- **kind:** CONDITIONAL_TRANSLATION
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b_TTC

- **all_of:** ["B:VIEW", "B:BAC", "B:TFR", "B:TTC_BRIDGE"]
- **conclusion:** B:TTC
- **statement:** Conditional TTC mechanism representation with stated residuals
- **proof_sketch:** Apply the explicit functional/translation under this target-specific bridge; existence and validity of its biological/semantic premises are not proved.
- **source:** B §13
- **kind:** CONDITIONAL_TRANSLATION
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b04

- **all_of:** ["B:GRAPH"]
- **conclusion:** B:CYCLE_PRIMITIVE
- **statement:** A vertex is on a directed cycle iff it lies in an SCC with at least two vertices or has a self-loop
- **proof_sketch:** Positive cycle implies mutual reachability; mutual reachability of distinct vertices gives a closed walk containing a cycle; handle singleton self-loops separately.
- **source:** B §7 / R128
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b05

- **all_of:** ["B:GRAPH", "B:NEW_EDGE_RETURN"]
- **conclusion:** B:EDGE_CYCLE
- **statement:** A newly added edge lies in a directed cycle iff the old graph has its reverse-direction return path
- **proof_sketch:** Remove new edge from cycle to get path; concatenate path with edge for converse.
- **source:** B §16
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b06

- **all_of:** ["B:MODEL19"]
- **conclusion:** B:SPECTRAL
- **statement:** rho=sqrt(6q); rho=1 at g=0.5-log(5)/10; cycle exists for all finite stated g
- **proof_sketch:** Eigenvalues of [[0,2],[3q,0]] are ±sqrt(6q); invert q=sigmoid(10(g-.5)); q>0.
- **source:** B §19.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule b07

- **all_of:** ["B:MODEL19", "B:NONLINEAR_WORKSPACE"]
- **conclusion:** B:RECURRENCE_ENABLES
- **statement:** Nonlinear stability must use the state-dependent Jacobian, not just weighted connectivity
- **proof_sketch:** Differentiate sigmoid updates; slopes include x_i(1-x_i), so structural radius alone does not determine dynamical stability.
- **source:** B §§16,19
- **kind:** CONDITIONAL_ENABLING
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a35

- **all_of:** ["B:VIEW", "B:BAC", "B:TFR", "B:REP"]
- **conclusion:** A:UCTII_RECON
- **statement:** UCT II's formal reconstruction has no C1/U1 premise
- **proof_sketch:** Typed translator uses physical inputs and supplied conventions; identity is an optional subsequent interpretation.
- **source:** A §16.1; B §§2–5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a36

- **all_of:** ["A:U1", "B:TARGET_DOMAIN"]
- **conclusion:** A:UCTII_GATE
- **statement:** UCT II gate relocation uses U1 and a scoped witness
- **proof_sketch:** Apply b02.
- **source:** A §16.1; B §5.5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a37

- **all_of:** ["A:ACTUAL_TOKEN"]
- **conclusion:** A:NONEMPTY_CARRIER
- **statement:** An admitted actual token has nonempty constitutive support
- **proof_sketch:** This is part of the declared actual-token ontology, not a data-derived consciousness claim.
- **source:** A §2.1
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c01

- **all_of:** ["A:C1_OI", "C:FIXED_J"]
- **conclusion:** C:P1
- **statement:** J(s)≠J(t) implies different full experiential type; strict fiber inclusion iff J noninjective
- **proof_sketch:** Equal complete types have equal J; contrapose. Strictness is exactly a repeated J value on distinct types.
- **source:** C §5.1
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c02

- **all_of:** ["C:SET_MAPS"]
- **conclusion:** C:P2_COORD
- **statement:** C factors through J iff J(s)=J(t) implies C(s)=C(t)
- **proof_sketch:** Define recovered value on each fiber; it is representative-independent exactly under the stated condition.
- **source:** C §5.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c03

- **all_of:** ["A:C1_OI", "C:FIXED_J", "C:P2_COORD"]
- **conclusion:** C:P2_FULL
- **statement:** J identifies full experiential type throughout the domain iff J is injective
- **proof_sketch:** Full C1 type equivalence identifies distinct structural types with distinct experiential types.
- **source:** C §5.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c04

- **all_of:** ["C:SET_MAPS"]
- **conclusion:** C:OBS_REFINEMENT
- **statement:** F_(A,R)(s)=F_A(s)∩F_R(s); refinement strict only when R splits an A-fiber
- **proof_sketch:** Equality of ordered pairs is coordinatewise equality.
- **source:** C §5.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c05

- **all_of:** ["C:CONST_RANK"]
- **conclusion:** C:LOCAL_FIBER
- **statement:** Locally constant rank gives local fibers of dimension n-r
- **proof_sketch:** Apply the constant-rank normal form; pointwise rank at a singularity is insufficient.
- **source:** C §5.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c06

- **all_of:** ["C:PAIR_COUNTERMODEL"]
- **conclusion:** C:P3
- **statement:** The C1-compatible model increases J while decreasing C
- **proof_sketch:** Direct substitution verifies the premises and falsifies the unrestricted conclusion; coordinate is not asserted to measure real richness.
- **source:** C §5.4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c07

- **all_of:** ["C:SMOOTH_FITNESS"]
- **conclusion:** C:P4
- **statement:** v∈ker DJ gives DwI[v]=0; exact constant-J path keeps wI constant
- **proof_sketch:** Chain rule gives first result; function composition gives second. First-order null is not finite neutrality.
- **source:** C §6.1
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c08

- **all_of:** ["C:SELECTION", "C:CLASS_WEIGHTS"]
- **conclusion:** C:P5
- **statement:** p+(s|J=j)=p(s|J=j) for surviving classes
- **proof_sketch:** Divide reweighted state mass by reweighted class mass; common factor cancels.
- **source:** C §6.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c09

- **all_of:** ["C:SELECTION"]
- **conclusion:** C:PRICE_SELECTION
- **statement:** ΔEC=Cov(W,C)/EW; if W=f(J), covariance depends on E[C|J]
- **proof_sketch:** Expand the reweighted expectation; use conditional expectation for class-constant weights.
- **source:** C §6.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c10

- **all_of:** ["C:SELECTION", "C:DESCENDANT_ATTRIBUTION"]
- **conclusion:** C:PRICE_TRANSMISSION
- **statement:** ΔEC=Cov(W,C)/EW+E[W(C'_s-C(s))]/EW
- **proof_sketch:** Add and subtract E[WC]/EW. This is accounting, not a closed dynamics law.
- **source:** C §6.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c11

- **all_of:** ["C:MARKOV_SELECTION"]
- **conclusion:** C:P6
- **statement:** Projected capability dynamics close iff every destination-class probability is constant on each current class
- **proof_sketch:** Sufficiency groups row sums; necessity compares point masses in the same class, whose positive weights cancel.
- **source:** C §6.4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c12

- **all_of:** ["C:DECISION"]
- **conclusion:** C:P7
- **statement:** V_XM≥V_X, with equality iff each supported X has a common optimal action for all supported M
- **proof_sketch:** Write improvement as average nonnegative regret of a baseline-optimal action. Zero sum forces every supported regret to vanish.
- **source:** C §7.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c13

- **all_of:** ["C:CIRCUIT_SPEC"]
- **conclusion:** C:CIRCUIT_LAWS
- **statement:** Unmasked readout accuracy 1-epsilon; masked/current-input accuracy 1/2; mutation gain mu(1/2-epsilon)
- **proof_sketch:** Independence and XOR make the mask a fair one-time randomizer; average the two mutation outcomes.
- **source:** C §7.2; Appendix C
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c14

- **all_of:** ["C:ENV_MEMORY", "C:DECISION"]
- **conclusion:** C:MEMORY_VALUE
- **statement:** V=1/2+|2alpha-1|(1/2-epsilon)
- **proof_sketch:** Match probability q=alpha(1-epsilon)+(1-alpha)epsilon; optimal binary action attains max(q,1-q).
- **source:** C §7.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c15

- **all_of:** ["C:MEMORY_COST", "C:SELECTION"]
- **conclusion:** C:MEMORY_SELECTION
- **statement:** Memory frequency increases exactly when its stipulated weight exceeds the alternative
- **proof_sketch:** For two positive types, reweighting increases the first iff W1>W0; subtract weights.
- **source:** C §7.3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c16

- **all_of:** ["A:C1", "C:ACTUAL_ENSEMBLE"]
- **conclusion:** C:REPERTOIRE
- **statement:** R_D=R_Φ and their images/frontiers coincide; no time-monotonicity follows
- **proof_sketch:** Elementwise C1 equality followed by the same map and partial order.
- **source:** C §8.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c17

- **all_of:** ["A:C1_OI", "C:ACTUAL_INDEX_FAMILY"]
- **conclusion:** C:SENSORY_PARTITION
- **statement:** Physical and experiential full-type equality partitions coincide
- **proof_sketch:** Substitute type equivalence; strict refinement transfers on the same index set.
- **source:** C Appendix E
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c18

- **all_of:** ["A:C1_OI", "B:TFR", "C:RIVAL_DESCRIPTOR"]
- **conclusion:** C:RIVAL_CONTRAST
- **statement:** UCT separates the pair while the stipulated rival assignment does not
- **proof_sketch:** C1-OI separates unequal full types; rival descriptor equality forces its assigned equality.
- **source:** C §9.1
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c19

- **all_of:** ["C:SET_MAPS", "C:P2_COORD"]
- **conclusion:** C:RIVAL_NESIG
- **statement:** Unequal J entails unequal rival assignment iff J constant on rival fibers
- **proof_sketch:** Contraposition plus representative-independent factorization; no C1 truth premise needed.
- **source:** C §9.1
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c20

- **all_of:** ["C:TRANSCRIPT"]
- **conclusion:** C:SCORE_TV
- **statement:** |EP h-EQ h|≤TV(P,Q)
- **proof_sketch:** Positive and negative parts of P-Q each have mass TV; h lies between zero and one.
- **source:** C §9.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c21

- **all_of:** ["C:FINITE_LOSS"]
- **conclusion:** C:LOGLOSS
- **statement:** L(qZ)-L(qZR)=I(Y;R|Z)+KZ-KZR
- **proof_sketch:** Each finite log loss is conditional entropy plus conditional KL; subtract.
- **source:** C Appendix B
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c22

- **all_of:** ["C:FINITE_LOSS", "C:NUISANCE_BOUNDS", "C:LOGLOSS"]
- **conclusion:** C:RESIDUAL_BOUND
- **statement:** I(Y;R|Z)≤u+d, hence fitted gain≤u+d+eta
- **proof_sketch:** Add A* in mutual information; chain rule and finite entropy bound; discard nonnegative KZR.
- **source:** C Appendix B
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c23

- **all_of:** ["C:TV_PROFILES"]
- **conclusion:** C:PROFILE_PSEUDOMETRIC
- **statement:** Nonnegative weighted sum of TVs satisfies symmetry and triangle inequality; distinct states may have zero distance
- **proof_sketch:** Apply TV metric properties coordinatewise.
- **source:** C §10.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule c24

- **all_of:** ["C:PUBLIC_NULL_PREMISE"]
- **conclusion:** C:PUBLIC_NULL
- **statement:** Independent public-only binary guessing succeeds with probability 1/2
- **proof_sketch:** Condition on the full public record/decision; target remains fair.
- **source:** C §10.2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r126_1

- **all_of:** ["A:C1", "R126:PROJECTION"]
- **conclusion:** R126:P1
- **statement:** pE=p∘Phi^-1 gives pE∘Phi=p for every p
- **proof_sketch:** Substitution and inverse identity. Since p was arbitrary the equality cannot by itself select actual support.
- **source:** R126 theory note §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r126_2

- **all_of:** ["R126:MODEL"]
- **conclusion:** R126:P2
- **statement:** A quotient update/output exists iff its next summary/output is constant on each current fiber
- **proof_sketch:** Necessity by equal arguments; sufficiency by representative-independent definition.
- **source:** R126 theory note §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r126_3

- **all_of:** ["R126:MODEL", "R126:METRIC"]
- **conclusion:** R126:P3
- **statement:** Worst-case summary prediction error in a fiber is at least half the successor diameter
- **proof_sketch:** Triangle inequality for the farthest pair. Necessity, not general sufficiency.
- **source:** R126 theory note §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r126_4

- **all_of:** ["R126:MODEL", "R126:P2"]
- **conclusion:** R126:P4
- **statement:** Refine output fibers by successor classes; at most N-b0 strict stages; terminal equivalence is coarsest stable refinement
- **proof_sketch:** Each strict stage increases class count; any stable refinement remains finer by induction.
- **source:** R126 theory note §6
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_1

- **all_of:** ["R127:TASK"]
- **conclusion:** R127:P1
- **statement:** Exact answer factorization iff encoder separates all unequal response profiles; code size≥number of profiles
- **proof_sketch:** Equal code forces equal outputs for every q; otherwise define decoder on image by representatives.
- **source:** R127 theory note §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_1a

- **all_of:** ["R127:TASK"]
- **conclusion:** R127:QUERY_REFINEMENT
- **statement:** Equality on Q2 entails equality on subset Q1
- **proof_sketch:** Restrict universally quantified queries.
- **source:** R127 theory note §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_1b

- **all_of:** ["R126:MODEL", "R126:P4"]
- **conclusion:** R127:FUTURE_EQ
- **statement:** Two states are equivalent iff outputs agree after every finite operation word, including the empty word
- **proof_sketch:** Future-word equivalence is stable and refines outputs; all stable refinements preserve future outputs by induction.
- **source:** R127 theory note §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_2

- **all_of:** ["R127:TASK", "R127:MEDIATION"]
- **conclusion:** R127:P2
- **statement:** At the same supported b,q and for different correct answers, TV(P(C|x,b,q),P(C|xprime,b,q)) >= 1-epsilon_(x,b,q)-epsilon_(xprime,b,q). Without conditioning on B the applicable cut law is joint (C,B), not C alone.
- **proof_sketch:** Fix common supported b,q and use the SAME W_q(.|c,b). Total variation contracts from the conditional cut laws to outputs. The correct-answer event has probability at least 1-epsilon_(x,b,q) for x and at most epsilon_(xprime,b,q) for xprime. For unfixed B, sum over the JOINT cut (C,B); averaging away B can destroy the relevant dependence.
- **source:** R127 theory note §§2,4–5; R130 second review §2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_3

- **all_of:** ["R127:RECOVERY"]
- **conclusion:** R127:P3
- **statement:** I(X;C|B)≥H(X|B)−h2(epsilon)−epsilon log2(m−1); for finite C this is at most log2|C|
- **proof_sketch:** Conditional data processing followed by Fano error-indicator decomposition.
- **source:** R127 theory note §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_3a

- **all_of:** ["R127:PAIR_MODEL"]
- **conclusion:** R127:JOINT_INFORMATION
- **statement:** I(X;C)=I(X;B)=0, I(X;C,B)=1 bit
- **proof_sketch:** Fair mask makes each marginal independent of X; XOR of both recovers X.
- **source:** R127 theory note §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_3b

- **all_of:** ["R127:LOCALIZATION_PAIR"]
- **conclusion:** R127:LOCALIZATION_LIMIT
- **statement:** Any interface-law-only identification rule agrees on the pair, so cannot identify both different storage locations
- **proof_sketch:** Equal inputs to rule have equal outputs; locations differ by supplied construction.
- **source:** R127 theory note §6
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_4

- **all_of:** ["A:ACTUAL_TOKEN", "R127:EVENT_SUPPORT"]
- **conclusion:** R127:P4
- **statement:** Selected grounded subhistory meets A §2.5 actual-token conditions
- **proof_sketch:** Actual support, inherited relations, causal continuity, boundary accountability and traceability each supplied. Definition application, not new existence threshold.
- **source:** R127 theory note §7
- **kind:** DEFINITION_APPLICATION
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r127_5

- **all_of:** ["A:C1", "R127:RELATIONAL_SUPPORT"]
- **conclusion:** R127:P5
- **statement:** For retained actual relation R and tuple a, R^D(a) iff R^Phi(h(a))
- **proof_sketch:** Restrict a relation-preserving and reflecting isomorphism. Operations need closed subdomains/ports; no automatic subalgebra or independent subject.
- **source:** R127 theory note §8
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule a38

- **all_of:** ["A:C1", "B:REP", "B:BAC", "B:TFR", "R127:RELATIONAL_SUPPORT", "R127:P5"]
- **conclusion:** A:UCTII_EXP
- **statement:** A source-faithful finite reconstruction has selected experiential interpretation only where its relations are independently grounded in actual constitutive organization
- **proof_sketch:** B translation alone does not establish the physical premise. Once grounded, use the isomorphism restriction.
- **source:** R127 theory note §8; A Appendix C; B §5
- **kind:** CONDITIONAL_INTERPRETATION
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule n128_1

- **all_of:** ["R126:P2", "N128:COMMON_DETERMINISTIC"]
- **conclusion:** N128:DET_JOIN
- **statement:** Joint summary update is the pair of component updates on its image
- **proof_sketch:** Equality of current pairs implies equality of successor pairs; choose representative to prove image invariance.
- **source:** R128 joint-state derivation §2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule n128_2

- **all_of:** ["N128:MARKOV_WITNESS"]
- **conclusion:** N128:MARKOV_JOIN
- **statement:** p1=x and p2=y close; (x,y) fails on all 8 states; closes on invariant 4-state restriction; full-domain stable refinement needs 8 blocks
- **proof_sketch:** Each next marginal is fair; z selects equal vs unequal next pairs despite equal current pair. Every pair block must split by z.
- **source:** R128 joint-state derivation §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule n128_3

- **all_of:** ["N128:KERNEL"]
- **conclusion:** N128:JOINT_CRITERION
- **statement:** Joint law p_*K_a must be constant within each present joint-summary fiber
- **proof_sketch:** Necessity by equal summary arguments; sufficiency by well-defined row assignment.
- **source:** R128 joint-state derivation §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule n128_4

- **all_of:** ["N128:KERNEL", "N128:PRODUCT_LAW", "N128:JOINT_CRITERION"]
- **conclusion:** N128:INDEPENDENCE_SUFFICES
- **statement:** Products of closed marginal laws give a closed joint law; a fixed (U,U) joint law shows independence is unnecessary
- **proof_sketch:** Product depends only on current pair; fixed correlated law depends on no hidden state.
- **source:** R128 joint-state derivation §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule n128_5

- **all_of:** ["C:OBS_REFINEMENT", "N128:MARKOV_JOIN"]
- **conclusion:** N128:SEPARATION
- **statement:** More identifying information does not by itself imply joint dynamic closure
- **proof_sketch:** Joint fibers refine both coordinate fibers, but explicit next-joint laws disagree within a joint fiber.
- **source:** R128 joint-state derivation §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_bundled

- **all_of:** ["D:PATH_MODEL", "D:BUNDLED_ROWS"]
- **conclusion:** D:F1
- **statement:** The bundled observation map is noninjective: rank 2 in R^5; the declared finite grid also has collisions.
- **proof_sketch:** The two independent rows give rank 2 and a three-dimensional kernel. In {-1,0,1}^5, theta=(1,0,0,0,0) and (0,0,0,1,0) both map to (1,0). Exact enumeration gives 43 signatures, largest class 17.
- **source:** D §3; R96; R129 §2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_direct

- **all_of:** ["D:PATH_MODEL", "D:DIRECT_ROWS"]
- **conclusion:** D:F2
- **statement:** The five logits uniquely identify all five coefficients in the declared model, including on the finite grid.
- **proof_sketch:** Direct logits give theta_Q,theta_O,theta_G. Subtract theta_Q+theta_G from Q-bundle and theta_O+theta_G from O-bundle for the interactions. Five rows have full rank. Deterministic choices and unknown logit scale do not supply these observations.
- **source:** D §3; R96; R129 §2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_payoff

- **all_of:** ["D:BINARY_PAYOFF"]
- **conclusion:** D:PAYOFF
- **statement:** Binary payoff admits the stated four-term expansion.
- **proof_sketch:** Set alpha=f00,b=f10-f00,c=f01-f00,d=f11-f10-f01+f00; equality holds at all four states. Take expectations under each action law.
- **source:** D §4; R96D §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_marginal_counter

- **all_of:** ["D:BINARY_PAYOFF", "D:PAYOFF", "D:MATCHED_WITNESS"]
- **conclusion:** D:F3
- **statement:** Accurate marginal consequence predictions can fail to identify the optimal action.
- **proof_sketch:** OR has alpha=0,b=c=1,d=-1. Values A=(1/2,3/4) and B=(3/4,1/2) reverse strict optimal actions while all supplied marginals match.
- **source:** D §4; R96D §§3–5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_value_gap

- **all_of:** ["D:F3", "D:MATCHED_WITNESS", "C:P7"]
- **conclusion:** D:VALUE_GAP
- **statement:** The matched binary example has exact optimized value gap 1/8.
- **proof_sketch:** Every context-blind action mixture averages (1/2+3/4)/2=5/8; the informed policy chooses the 3/4 action in both contexts. Same costs/action set; randomization only forms convex combinations.
- **source:** D §4; R96D §§3–4; C P7
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_frechet

- **all_of:** ["D:BINARY_PAYOFF", "D:PAYOFF", "D:FRECHET_ASSUMPTIONS"]
- **conclusion:** D:FRECHET
- **statement:** The stated interval is the exact attainable advantage range under these assumptions.
- **proof_sketch:** The four probabilities are (1-q-o+j,o-j,q-j,j); nonnegativity is equivalent to ell<=j<=u. Independent admissibility across actions gives the difference interval; multiply by d and add B.
- **source:** R96D §6; R129 §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_grid

- **all_of:** ["D:REGULAR_GRID"]
- **conclusion:** D:GRID_BOUND
- **statement:** Nearest-grid error plus a justified Lipschitz remainder bounds the entire declared cube.
- **proof_sketch:** Choose a grid point within radius sqrt(3)h/2 for each point x. Triangle inequality gives |e(x)|<=|e(grid)|+L_e distance. Take supremum.
- **source:** D §§7–8; R99 §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_separable

- **all_of:** ["D:ADDITIVE_CLASS"]
- **conclusion:** D:SEPARABLE
- **statement:** The Q finite-difference effect has no O/G context dependence.
- **proof_sketch:** Subtract expressions; f_O,f_G,b cancel. f_Q remains arbitrary, so this does not prove linear shape or small off-grid error.
- **source:** D §7; R99 §§3–4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule d129_uct

- **all_of:** ["A:C1_OI", "D:ACTUAL_CHANGE"]
- **conclusion:** D:UCT_INTERPRETATION
- **statement:** Actual complete-type difference implies complete experiential-type difference under C1.
- **proof_sketch:** Apply the reverse direction of complete physical-type iff complete experiential-type agreement by contraposition. Actual grounded type difference is an independent premise.
- **source:** D §11; A C1-OI
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r131_target

- **all_of:** ["R131:PROBES", "C:P2_COORD"]
- **conclusion:** R131:TARGET_SPAN
- **statement:** Target expectation factors through the probe interface exactly for targets in its row span.
- **proof_sketch:** In-span targets are linear combinations of observed expectations; otherwise choose d in ker(A) with g^T d!=0 and normalize its positive/negative parts to equal-interface probability laws.
- **source:** R131 R131_Probe_Completeness_Theorem.md §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r131_complete

- **all_of:** ["R131:PROBES", "R131:TARGET_SPAN"]
- **conclusion:** R131:COMPLETE_LAW
- **statement:** Full-law identification iff full column rank, with a TV=1 witness for any deficient matrix.
- **proof_sketch:** Full rank is injectivity; a nonzero null vector has zero sum and its normalized positive/negative parts are disjoint probability laws with identical probes. Indicator probes attain the n-1 bound.
- **source:** R131 R131_Probe_Completeness_Theorem.md §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r131_closure

- **all_of:** ["R131:PROBES", "R131:COMPLETE_LAW", "R131:FULL_RANK", "R131:KERNEL", "R131:PROBE_MATCH", "N128:JOINT_CRITERION"]
- **conclusion:** R131:CLOSURE
- **statement:** Full-rank matching probes establish the exact controlled quotient; a closed quotient conversely matches probes.
- **proof_sketch:** Normalization and matching f_i give equal A mu within each fiber; full rank gives equal mu. Define the quotient using any representative; closure implies all expected probe equalities in reverse.
- **source:** R131 R131_Probe_Completeness_Theorem.md §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r131_blind

- **all_of:** ["R131:PROBES", "R131:COMPLETE_LAW", "R131:DEFICIENT", "N128:JOINT_CRITERION"]
- **conclusion:** R131:BLIND_KERNEL
- **statement:** A deficient interface admits an exact countermodel with maximally distinct hidden next laws.
- **proof_sketch:** Choose disjoint u,v with equal probes; on S=Z x {0,1} persist b and draw next z from u_b under each operation. Same present z can have different b and hence different next laws.
- **source:** R131 R131_Probe_Completeness_Theorem.md §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r131_decision

- **all_of:** ["R131:BLIND_KERNEL", "R131:DECISION_SETUP", "C:P7"]
- **conclusion:** R131:DECISION_GAP
- **statement:** The constructed hidden context yields exact information value 1/2.
- **proof_sketch:** The informed observer chooses the supported event, scoring 1. A context-blind action-0 mixture r scores (r+1-r)/2=1/2.
- **source:** R131 R131_Probe_Completeness_Theorem.md §6
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r131_robust

- **all_of:** ["R131:PROBES", "R131:LEFT_INVERSE"]
- **conclusion:** R131:ROBUST
- **statement:** A fixed left inverse transfers probe residuals to a TV bound.
- **proof_sketch:** d=mu-nu=LAd=B r since normalization cancels. Apply ||B r||_1<=||B||_(infty->1)||r||_infty and TV=||d||_1/2.
- **source:** R131 R131_Probe_Completeness_Theorem.md §7
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r132_hall

- **all_of:** ["R132:SLOT_MODEL"]
- **conclusion:** R132:HALL
- **statement:** Every coalition has enough eligible slots iff a joint assignment exists.
- **proof_sketch:** Necessity counts assigned neighbors. Induct: match a tight proper coalition and its remainder, or remove any task/neighbor when every proper coalition has a surplus.
- **source:** R132_Common_Realization_Theorems.md §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r132_deficit

- **all_of:** ["R132:SLOT_MODEL", "R132:HALL"]
- **conclusion:** R132:DEFICIT
- **statement:** The worst Hall deficit is exactly the number of unavoidable unmatched tasks.
- **proof_sketch:** Any matching misses at least delta tasks in a deficient coalition. Adding delta universal dummy slots restores Hall; remove their matches. Take expectations for completion bounds.
- **source:** R132_Common_Realization_Theorems.md §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r132_high

- **all_of:** ["R132:SLOT_MODEL", "R132:DEFICIT", "R132:UNIFORM_BOTTLENECK"]
- **conclusion:** R132:HIGH_ORDER
- **statement:** Every proper coalition succeeds although the full set cannot; randomized omission gives high marginals and zero joint success.
- **proof_sketch:** All subsets of size <=n-1 inject into slots. The full set has deficit one. Uniform omission misses each named task on exactly one of n equally likely branches.
- **source:** R132_Common_Realization_Theorems.md §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r132_closure

- **all_of:** ["R132:PARTIAL_MODEL", "C:P2_COORD"]
- **conclusion:** R132:PARTIAL_CLOSURE
- **statement:** Menu and joint-kernel factorization are jointly necessary and sufficient for the declared quotient.
- **proof_sketch:** Apply fiber constancy to the menu map and each enabled joint row law. Necessity follows from one abstract value per summary; sufficiency defines representative-independent menus and kernels. Induct over shared observable-history policies.
- **source:** R132_Common_Realization_Theorems.md §6
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r132_probes

- **all_of:** ["R132:PARTIAL_MODEL", "R132:PARTIAL_CLOSURE", "R132:PROBE_SETUP", "R131:COMPLETE_LAW"]
- **conclusion:** R132:PROBE_CERTIFICATE
- **statement:** The full-rank joint probe interface supplies the law clause after menu equality is separately met.
- **proof_sketch:** R131 injectivity on probability laws on Z x O makes equal probe expectations equivalent to equal joint laws; combine with exact enabledness.
- **source:** R132_Common_Realization_Theorems.md §6
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r132_obstructions

- **all_of:** ["R132:PARTIAL_CLOSURE", "R132:WITNESS_MODELS"]
- **conclusion:** R132:TWO_OBSTRUCTIONS
- **statement:** Neither menu preservation nor separate next-state/output laws can replace the full quotient criterion.
- **proof_sketch:** The full three-task request is enabled only with three slots. The hidden-bit joint witness yields diagonal versus off-diagonal next-state/output laws while both marginals are fair.
- **source:** R132_Common_Realization_Theorems.md §7
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r132_refine

- **all_of:** ["R132:PARTIAL_MODEL", "R132:PARTIAL_CLOSURE", "R132:REFINEMENT_SETUP"]
- **conclusion:** R132:REFINEMENT
- **statement:** Finite signature refinement gives the unique coarsest exact refinement preserving the initial partition.
- **proof_sketch:** Each strict step adds blocks. A stable refining partition cannot be split at any stage because coarse block sums are sums of its equal finer block masses and menus agree. The fixed point is stable and coarser than every such partition.
- **source:** R132_Common_Realization_Theorems.md §8
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r133_support

- **all_of:** ["R133:PERSISTENT_MODEL"]
- **conclusion:** R133:SUPPORT
- **statement:** The observable support update retains exactly feasible persistent model/state pairs.
- **proof_sketch:** Induct on finite history: positive transition iff a feasible predecessor exists; immutable m and finite products of positive factors preserve exact possibility.
- **source:** R133_Observable_Common_Control.md §2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r133_common

- **all_of:** ["R133:PERSISTENT_MODEL", "R133:SUPPORT"]
- **conclusion:** R133:COMMON_POLICY
- **statement:** The AND/OR support recurrence is equivalent to a common finite-horizon probability-one policy.
- **proof_sketch:** Base case is goal containment. A successful first action is common-enabled; every possible output must admit a successful continuation. Conversely combine those continuations. Positive-probability randomized failing branches would contradict the guarantee, so purify recursively.
- **source:** R133_Observable_Common_Control.md §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r133_cell

- **all_of:** ["R133:DECISION_MODEL", "C:P2_COORD"]
- **conclusion:** R133:CELL_ACTION
- **statement:** Decision rules must choose a shared successful action on each observation fiber.
- **proof_sketch:** A rule is constant on each observed cell, giving necessity; choose an action from each finite nonempty intersection for sufficiency. Every action in a successful randomized rule support must satisfy the same condition.
- **source:** R133_Observable_Common_Control.md §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r133_cover

- **all_of:** ["R133:DECISION_MODEL", "R133:CELL_ACTION", "R133:ENCODER"]
- **conclusion:** R133:MESSAGE_COVER
- **statement:** The ideal minimum message count is exactly the minimum successful-action cover size.
- **proof_sketch:** Each decoded message action covers its cell, giving a cover lower bound. Conversely assign every mechanism to one action in a minimum cover and send its index.
- **source:** R133_Observable_Common_Control.md §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r133_avoid

- **all_of:** ["R133:DECISION_MODEL", "R133:CELL_ACTION", "R133:ENCODER", "R133:MESSAGE_COVER", "R133:AVOIDANCE_MODEL"]
- **conclusion:** R133:AVOIDANCE
- **statement:** A large candidate family can require only a one-bit task diagnostic while having no perfect unobserved action.
- **proof_sketch:** Worst-case success for action law p is 1-max p_m, at most 1-1/n, attained uniformly. Test m=1 and choose action 2 or 1. Full identification instead requires injective messages.
- **source:** R133_Observable_Common_Control.md §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r133_nonunique

- **all_of:** ["R133:DECISION_MODEL", "R133:CELL_ACTION", "R133:AVOIDANCE_MODEL"]
- **conclusion:** R133:NONUNIQUE
- **statement:** Task-relative sufficient observation partitions need not have a unique coarsest element.
- **proof_sketch:** At n=3 all two-element candidate cells share an allowed action, but the triple does not. The three two-cell partitions are incomparable and force the universal cell in any common coarsening.
- **source:** R133_Observable_Common_Control.md §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r133_probe

- **all_of:** ["R133:PERSISTENT_MODEL", "R133:COMMON_POLICY", "R133:PROBE_MODELS"]
- **conclusion:** R133:PROBE_BOUNDARY
- **statement:** A diagnostic helps only through continuations still possible in the declared action/time model.
- **proof_sketch:** Preserving output identifies the right terminal action in two steps. Uninformative histories give identical terminal-action distributions with summed two-model success at most one. A destructive probe has no successful continuation. Immediate half-half action selection attains one half.
- **source:** R133_Observable_Common_Control.md §6
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r133_persistence

- **all_of:** ["R133:PERSISTENT_MODEL", "R133:SUPPORT", "R133:SWITCH_MODEL"]
- **conclusion:** R133:PERSISTENCE
- **statement:** Independent stagewise model choices can add failure histories absent from every fixed model.
- **proof_sketch:** The two allowed traces each contain 1; (0,0) belongs to the stagewise product but requires switching models. The exact first-output update eliminates that switch.
- **source:** R133_Observable_Common_Control.md §7
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r134_vectors

- **all_of:** ["R133:PERSISTENT_MODEL", "R133:SUPPORT", "R134:QUANT_MODEL"]
- **conclusion:** R134:VECTOR_RECURSION
- **statement:** A pure tree is exactly an action plus one legal subtree per possible observation; randomization convexifies its profile set.
- **proof_sketch:** Induct on horizon and condition on the joint successor/output. Conversely assemble each tuple of subtrees. Independent private tree sampling implements every convex combination; product branch-mixture weights justify convex backups.
- **source:** R134_Quantitative_Control.md §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r134_lp

- **all_of:** ["R134:QUANT_MODEL", "R134:VECTOR_RECURSION"]
- **conclusion:** R134:ROBUST_LP
- **statement:** The common success guarantee is a finite feasible-mixture LP with a least-favorable-weight dual.
- **proof_sketch:** Primal is maximize t with A lambda >=t1 and simplex lambda. Nonnegative multipliers on model/state rows must sum to one; finite feasible bounded LP duality gives min_q max_column q dot v.
- **source:** R134_Quantitative_Control.md §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r134_zero

- **all_of:** ["R134:QUANT_MODEL", "R134:VECTOR_RECURSION", "R134:ROBUST_LP", "R133:COMMON_POLICY"]
- **conclusion:** R134:ZERO_ERROR
- **statement:** The quantitative certificate exactly recovers the earlier probability-one corner.
- **proof_sketch:** Each success entry lies in [0,1]. An all-one convex average forces every positive-weight column to be all-one; R133 supplies the equivalent pure common-policy criterion.
- **source:** R134_Quantitative_Control.md §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r134_scalar

- **all_of:** ["R134:QUANT_MODEL", "R134:VECTOR_RECURSION", "R134:SCALAR_MODELS"]
- **conclusion:** R134:SCALAR_FAILURE
- **statement:** Independent coordinate maximization and premature scalar minimization both lose the shared-policy constraint.
- **proof_sketch:** Blind profiles have coordinate sum one, excluding (1,1), but mixing yields (1/2,1/2). Symmetric observation-specific opposite actions yield (3/4,3/4), while identical-support terminal policies are blind.
- **source:** R134_Quantitative_Control.md §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r134_probe

- **all_of:** ["R134:QUANT_MODEL", "R134:ROBUST_LP", "R134:PROBE_MODEL"]
- **conclusion:** R134:PROBE_DUAL
- **statement:** The forced diagnostic value is the minimum of a weighted sum-of-maxima envelope.
- **proof_sketch:** For fixed q, independently optimize the affine decision d_y at each transcript; obtain max(q a_y,(1-q)b_y). Finite minimax interchanges extrema. Convex piecewise-affine minima occur at endpoints or breakpoints.
- **source:** R134_Quantitative_Control.md §6
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r134_tv

- **all_of:** ["R134:PROBE_MODEL", "R134:PROBE_DUAL", "R134:COMMON_SURVIVAL"]
- **conclusion:** R134:TV_OPPORTUNITY
- **statement:** Transcript separation limits success only after opportunity survival is specified; the equal-weight bound need not be attained robustly.
- **proof_sketch:** Evaluate the dual at q=1/2 and use max(a,b)=(a+b+abs(a-b))/2. Substitute constant rho. Symmetric decisions equalize the two successes; asymmetric laws with the same TV instead have optimum 2rho/3.
- **source:** R134_Quantitative_Control.md §6
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r134_optional

- **all_of:** ["R134:QUANT_MODEL", "R134:ROBUST_LP", "R134:PROBE_MODEL", "R134:PROBE_DUAL", "R134:OPTIONAL_MODEL"]
- **conclusion:** R134:OPTIONAL_PROBE
- **statement:** The randomized optional-probe value is determined by the full convex union, not the maximum of separate robust scalar values.
- **proof_sketch:** The maximum q-weighted value over the convex union is max(q,1-q,F(q)); apply finite minimax. The explicit mixing witness gives strictness.
- **source:** R134_Quantitative_Control.md §7
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r134_mix

- **all_of:** ["R134:PROBE_MODEL", "R134:PROBE_DUAL", "R134:COMMON_SURVIVAL", "R134:OPTIONAL_MODEL", "R134:OPTIONAL_PROBE", "R134:ASYM_MODEL"]
- **conclusion:** R134:MIXING_WITNESS
- **statement:** Asymmetric probe and blind-action profiles can complement each other enough to improve the worst-case guarantee.
- **proof_sketch:** Dominance leaves (1,0),(0,1),(rho,rho/2). Below rho=2/3 all coordinate sums <=1. Above it mix the probe with (0,1) at weight 2/(2+rho); dual q=(2-rho)/(2+rho) matches the guarantee.
- **source:** R134_Quantitative_Control.md §7
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r135_deficiency

- **all_of:** ["R135:PROFILE_PAIR"]
- **conclusion:** R135:DEFICIENCY
- **statement:** Weighted optimum gaps exactly certify directional guarantee loss.
- **proof_sketch:** For fixed v, max-coordinate positive loss is the positive part of max over simplex weights. Compact convex minimax swaps min_w and max_q; maximize over v and commute the two maxima.
- **source:** R135_Capability_Preservation.md §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r135_equality

- **all_of:** ["R135:PROFILE_PAIR", "R135:DEFICIENCY"]
- **conclusion:** R135:GUARANTEE_EQ
- **statement:** All threshold guarantees are preserved exactly when every nonnegative weighted optimum is preserved in the appropriate direction.
- **proof_sketch:** A transferred threshold b=v supplies a dominating target vector. Conversely zero attained loss supplies a dominating vector for every source profile. Apply DEFICIENCY; equality follows in both directions.
- **source:** R135_Capability_Preservation.md §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r135_value

- **all_of:** ["R135:PROFILE_PAIR"]
- **conclusion:** R135:VALUE_BOUND
- **statement:** Directional approximation transfers monotone values and composes.
- **proof_sketch:** Match v by w>=v-epsilon 1; put u=min(v,w), use F(v)<=F(u)+L epsilon<=F(w)+L epsilon. Chain two such componentwise matches for composition.
- **source:** R135_Capability_Preservation.md §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r135_hierarchy

- **all_of:** ["R135:PROFILE_PAIR", "R135:HIERARCHY_MODELS"]
- **conclusion:** R135:HIERARCHY
- **statement:** One robust optimum does not identify the guarantee region; the guarantee region need not identify all exact profiles.
- **proof_sketch:** The first triangle has coordinate sums <=1 but contains (1,0), unlike the half-diagonal. The second pair both contain (1,1), which dominates every threshold, but only one includes an unequal-coordinate vector.
- **source:** R135_Capability_Preservation.md §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r135_policy

- **all_of:** ["R135:SIMULATION_SETUP"]
- **conclusion:** R135:POLICY_BOUND
- **statement:** Uniform joint-law error bounds every copied common observable policy.
- **proof_sketch:** Share the private seed and maximally couple joint mapped-successor/output rows while histories agree. Match probability is at least (1-epsilon)^H; payoff difference is <=1 after a mismatch. Total actions ensure legality throughout. An absorbing-goal hazard attains equality.
- **source:** R135_Capability_Preservation.md §7
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r135_transfer

- **all_of:** ["R135:PROFILE_PAIR", "R135:VALUE_BOUND", "R135:SIMULATION_SETUP", "R135:POLICY_BOUND"]
- **conclusion:** R135:TRANSFER_BOUND
- **statement:** Same-policy error controls both guarantee directions and selected-policy regret.
- **proof_sketch:** Copy policies in either direction on the common history alphabet and pulled-back coordinates. Each profile differs by <=beta_H. Apply monotone min-coordinate value transfer; selected-policy regret adds two approximation errors and eta.
- **source:** R135_Capability_Preservation.md §7
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r135_legality

- **all_of:** ["R135:LEGALITY_MODEL"]
- **conclusion:** R135:LEGALITY_JUMP
- **statement:** Hard universal action legality can make a derived capability discontinuous under tiny probability changes.
- **proof_sketch:** After p, K0 support is {good}, admitting a. Every positive delta gives support {good,bad} and no common non-stop action, so only failing stop remains. Totalizing a changes the protocol and yields 1-delta.
- **source:** R135_Capability_Preservation.md §8
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r135_uct

- **all_of:** ["A:C1", "C:P1", "C:P2_FULL", "C:P2_COORD", "R135:ACTUAL_PROFILE", "R135:GUARANTEE_EQ"]
- **conclusion:** R135:UCT_INTERPRETATION
- **statement:** The grounded capability map inherits the published full-type and fiber identification criteria.
- **proof_sketch:** Well-definedness on complete types forbids different G at the same type. C1 supplies experiential type identity; published C:P2 gives injectivity for full identification and fiber constancy for a selected coordinate.
- **source:** R135_Capability_Preservation.md §9
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r136_blackwell

- **all_of:** ["R136:STATIC_SETUP"]
- **conclusion:** R136:BLACKWELL
- **statement:** Universal decision dominance over fixed channels is equivalent to a common stochastic postprocessor.
- **proof_sketch:** S={QR} is compact convex. If P is outside, strict separation gives c; choosing actions X and utility c(theta,x)/p_theta makes the identity rule after P outperform every Q rule. Conversely concatenate R and any P decision.
- **source:** R136_Causal_Translation.md §2
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r136_causal

- **all_of:** ["R136:STREAM_SETUP"]
- **conclusion:** R136:CAUSAL_LP
- **statement:** Prefix-linear constraints exactly characterize implementable exogenous causal translators.
- **proof_sketch:** A causal transducer has prefix marginals independent of future input. Conversely ratios of successive prefix marginals give normalized time kernels and telescope to R, with arbitrary zero-probability rows. TV uses linear absolute-value epigraphs.
- **source:** R136_Causal_Translation.md §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r136_composition

- **all_of:** ["R136:STREAM_SETUP", "R136:CAUSAL_LP"]
- **conclusion:** R136:COMPOSITION
- **statement:** Causal composition transports output-law and downstream decision accuracy.
- **proof_sketch:** Sequentially compose the two causal implementations using independent seeds. Triangle inequality and TV contraction give the sum bound. Copying an admissible no-feedback decision kernel contracts TV again and bounds its [0,1] payoff.
- **source:** R136_Causal_Translation.md §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r136_prefix

- **all_of:** ["R136:STREAM_SETUP", "R136:CAUSAL_LP", "R136:DETERMINISTIC", "C:P2_COORD"]
- **conclusion:** R136:PREFIX
- **statement:** A deterministic required output is causally recoverable precisely when every deadline has the necessary fiber constancy.
- **proof_sketch:** Equal observed prefixes force equal translated-prefix laws; two required point masses must agree. Conversely define each output on the observed-prefix fiber, extending to unused histories arbitrarily.
- **source:** R136_Causal_Translation.md §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r136_delay

- **all_of:** ["R136:STREAM_SETUP", "R136:DELAY_MODEL", "R136:PREFIX"]
- **conclusion:** R136:DELAY_GAP
- **statement:** A complete record can be sufficient offline but inadequate at the first decision deadline.
- **proof_sketch:** The offline kernel uses y2. The causal first bit has one common probability p under both parameters, causing errors at least p and 1-p. Fair guessing and a blank second output attain one half.
- **source:** R136_Causal_Translation.md §6
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r136_query

- **all_of:** ["R136:QUERY_MODEL"]
- **conclusion:** R136:QUERY_BOUND
- **statement:** The exact worst-case delayed-query success is one half plus half the read fraction.
- **proof_sketch:** Under uniform independent b,q, condition on seed/read transcript: every unread bit remains fair, while a uniform query hits the inspected set with probability <=k/n. Uniform k-subset selection and fair fallback guessing attain equality in every coordinate.
- **source:** R136_Causal_Translation.md §7
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r136_order

- **all_of:** ["R136:QUERY_MODEL", "R136:QUERY_BOUND", "R135:PROFILE_PAIR"]
- **conclusion:** R136:TASK_ORDER
- **statement:** Task-specific preparation cannot in general be replaced by one preparation for a later unknown query.
- **proof_sketch:** A pre-announced query is read directly, giving the all-one profile. In delayed coordinates the full reader has all ones, so its maximal directed loss equals 1 minus the restricted robust optimum. Any exact deadline/budget-preserving translator would contradict that optimum.
- **source:** R136_Causal_Translation.md §8
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r137_local

- **all_of:** ["R137:CONTROL_MODEL"]
- **conclusion:** R137:LOCAL_LP
- **statement:** One observation-compatible action distribution must satisfy all hidden-state rows and legal menus simultaneously.
- **proof_sketch:** An implementable decoder has one common w. Its support encodes legality and its induced joint row is the linear mixture; conversely sample any feasible w. TV has a linear absolute-value epigraph. Compactness gives attainment if a common legal action exists.
- **source:** R137_Executable_Feedback.md §3
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r137_loop

- **all_of:** ["R137:CONTROL_MODEL", "R137:EXACT_INTERFACE", "R137:LOCAL_LP"]
- **conclusion:** R137:CLOSED_LOOP
- **statement:** Exact local decoding transports every adaptive projected closed-loop policy.
- **proof_sketch:** Condition on full concrete history and the requested u. Every compatible hidden s gives the same joint projected row, so hidden-state conditioning cannot change it. Induct on history; one-step controllers at arbitrary starts give necessity.
- **source:** R137_Executable_Feedback.md §4
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r137_approx

- **all_of:** ["R137:CONTROL_MODEL", "R137:APPROX_INTERFACE"]
- **conclusion:** R137:APPROX
- **statement:** Uniform conditional row accuracy gives a finite-horizon feedback path bound.
- **proof_sketch:** Couple controller seeds and next projected joint rows while histories agree. Conditional hidden-state mixtures retain the epsilon bound. Lift to concrete action/successor conditionals; legal decoders remain executable after divergence. Agreement probability is at least (1-epsilon)^H.
- **source:** R137_Executable_Feedback.md §5
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r137_obstruction

- **all_of:** ["R137:CONTROL_MODEL", "R137:LOCAL_LP"]
- **conclusion:** R137:OBSTRUCTION
- **statement:** A failed decoder has a bounded-size state obstruction in the action simplex.
- **proof_sketch:** Choose a minimal empty subfamily and one point satisfying every member except each omitted one. More than m such points are affinely dependent in dimension m-1; positive/negative convex combinations yield one point in every set, contradiction.
- **source:** R137_Executable_Feedback.md §6
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r137_sharp

- **all_of:** ["R137:CONTROL_MODEL", "R137:LOCAL_LP", "R137:OBSTRUCTION", "R137:FORBIDDEN_MODEL"]
- **conclusion:** R137:SHARP_OBSTRUCTION
- **statement:** The Helly obstruction can require exactly all m indistinguishable hidden states.
- **proof_sketch:** State i forces w_i=0. A proper subset permits an omitted-index action, while all constraints violate normalization. Approximate error is max_i w_i>=1/m, with equality for uniform weights.
- **source:** R137_Executable_Feedback.md §7
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r137_observation

- **all_of:** ["R137:CONTROL_MODEL", "R137:LOCAL_LP", "R137:BLIND_MODEL"]
- **conclusion:** R137:OBSERVATION_GAP
- **statement:** A statewise action selection need not factor through actual observations.
- **proof_sketch:** Common action0 probability w gives successes w and 1-w. Certain-success error is max(w,1-w); fair-target matching instead uniquely requires w=1/2. State-aware action a=b uses unavailable information.
- **source:** R137_Executable_Feedback.md §7
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Rule r137_seed

- **all_of:** ["R137:SEED_MODEL"]
- **conclusion:** R137:SEED_GAP
- **statement:** Unconditional local randomization marginals do not specify a correct temporal implementation.
- **proof_sketch:** Fresh sampling is uniform on all 2^H strings. Reuse puts mass one half on each constant string; overlap with the uniform law is 2^(1-H), so TV is its complement.
- **source:** R137_Executable_Feedback.md §8
- **kind:** DEDUCTIVE
- **review:** MANUAL_VALID_UNDER_STATED_PREMISES

## Node A:TOKEN_CRITERIA

- **kind:** ONTO_DEF
- **label:** Actual-token criteria
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:ACTUAL_TOKEN

- **kind:** ONTO_DOMAIN
- **label:** Actual valid process token
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD
- **scope:** Admitted actual valid P, specified interval and boundary; A §2 actual-support/inherited-relations/continuity/accountability/traceability criteria. No claim that an arbitrary variable satisfies them.

## Node A:NONEMPTY_CARRIER

- **kind:** ONTO_CONSEQ
- **label:** Nonempty constitutive carrier
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** An admitted actual token has nonempty constitutive support

## Node A:P3

- **kind:** ONTO_RULE
- **label:** Persistence / cessation / embedding
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:P6

- **kind:** ONTO_DEF
- **label:** Token / type / lineage
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:D_ONTIC

- **kind:** DEF
- **label:** Complete token-relative ontic organization
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:K

- **kind:** DEF
- **label:** Common structural signature K
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:QSPACE

- **kind:** DEF
- **label:** Structural-type quotient space
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:GEOMETRY

- **kind:** METHOD_DEF
- **label:** Predeclared invariant topology / pseudometric
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD
- **scope:** One predeclared common topology or pseudometric on the structural-type quotient; no empirically established unique metric assumed.

## Node A:VIEW

- **kind:** EPI_DEF
- **label:** Finite physical view D_v
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:ESTIMATE

- **kind:** EPI_DEF
- **label:** Scientific estimate D-hat_v
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:SUBJECT_FIREWALL

- **kind:** BOUNDARY
- **label:** Experience-bearing process != canonical subject
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:C1

- **kind:** AX_C
- **label:** Structural-Experiential Identity
- **source:** A §4
- **status:** FIXED_AXIOM

## Node A:C1_OI

- **kind:** LEMMA
- **label:** Pairwise type equivalence
- **source:** A §4
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** D(P)≅D(Q) iff Φ(P)≅Φ(Q) in the same complete signature

## Node A:C1_W

- **kind:** LEMMA
- **label:** One-way phenomenal completeness
- **source:** A §4
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Complete physical equivalence implies full experiential equivalence

## Node A:U1

- **kind:** THM
- **label:** Universal Nonempty Experience
- **source:** A §4
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Every actual token has a nonempty distinguished experiential carrier

## Node A:U2

- **kind:** THM
- **label:** Structural Continuity transfer
- **source:** A §4
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Physical and experiential quotient-valued maps have identical continuity and distances

## Node A:SELF_WITNESS

- **kind:** EMP_WITNESS
- **label:** Actual non-self token witness
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD
- **scope:** An actual valid token in the admitted domain lacks conceptual selfhood.

## Node A:U3

- **kind:** COR
- **label:** Selfhood Non-Prerequisite
- **source:** A §4
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Conceptual selfhood is not necessary for basal experience in a domain containing the witness

## Node A:U0

- **kind:** META_THM
- **label:** Foundational Compression
- **source:** A §4
- **status:** META_DEPENDENCY_RESULT
- **statement:** Prior foundational roles have the stated derivation/ontology decomposition

## Node A:NONUNIV_WITNESS

- **kind:** EMP_WITNESS
- **label:** Nonuniversality witness
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD
- **scope:** An actual valid token in the SAME domain lacks the proposed organization gate.

## Node A:ORG_GATE

- **kind:** THM
- **label:** Organization-Gate Impossibility
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** A mechanism absent at an actual same-domain witness cannot equal universal E=1

## Node A:COMPLETE_EQ

- **kind:** PREMISE
- **label:** Complete current ontic equivalence
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION
- **scope:** Same current complete token-relative ontic organization in the common signature, not merely equal observations.

## Node A:PROBE_ONLY

- **kind:** PREMISE
- **label:** Only external probe choice changes
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION

## Node A:FUTURE_ONLY

- **kind:** PREMISE
- **label:** Only future divergence changes
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION

## Node A:HISTORY_DIFF

- **kind:** PREMISE
- **label:** Different histories
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION
- **scope:** Different histories with all current constitutive consequences screened; numerical token/lineage may still differ.

## Node A:LABEL_ONLY

- **kind:** PREMISE
- **label:** Only external label changes
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION

## Node A:NO_HIDDEN

- **kind:** THM
- **label:** No Hidden Quale
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** No extra full-type phenomenal variation at fixed complete organization

## Node A:PROBE_INV

- **kind:** THM
- **label:** Probe Invariance
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Description/probe-choice-only change preserves full experiential type

## Node A:NO_FUTURE

- **kind:** THM
- **label:** No Future Contamination
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Future-only divergence does not change present type if complete present organization is equal

## Node A:GHOST_EQ

- **kind:** THM
- **label:** Causally Screened History experiential equivalence
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Screened history does not change current full experiential type

## Node A:GHOST_TOKEN_NOTE

- **kind:** COR
- **label:** Numerically distinct tokens may remain
- **source:** A Appendix C
- **status:** ONTOLOGICAL_ADDENDUM
- **statement:** Equal current types do not identify numerical occurrences or causal lineages

## Node A:REWARD_NONID

- **kind:** THM
- **label:** External reward-label non-identity
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** External reward-label change alone cannot change intrinsic phenomenal type

## Node A:PRODUCT_DEF

- **kind:** DEF
- **label:** Declared independent constituent product
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:ACTUAL_WHOLE_PARTS

- **kind:** PREMISE
- **label:** Actual whole and constituent tokens
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION

## Node A:PHYS_NONPRODUCT

- **kind:** PREMISE
- **label:** Whole physical organization is nonproduct
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION

## Node A:NONSUM

- **kind:** THM
- **label:** Non-Summative Combination
- **source:** A §6.3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** A nonproduct actual whole is not the specified independent product of experiential constituents

## Node A:MACRO_EQ

- **kind:** PREMISE
- **label:** Macro ontic equivalence
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION
- **scope:** Independently justified actual macro tokens have equivalent COMPLETE macro organization, with lower differences nonconstitutive of that macro token.

## Node A:MICRO_NONISO

- **kind:** PREMISE
- **label:** Lower-scale ontic nonisomorphism
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION
- **scope:** Specified actual lower tokens have nonisomorphic complete organizations in their common signature.

## Node A:MACRO_EXP_EQ

- **kind:** THM
- **label:** Macro experiential equivalence
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Complete macro equivalence preserves macro experiential type

## Node A:MICRO_EXP_DIFF

- **kind:** THM
- **label:** Lower experiential difference
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Complete lower-token nonisomorphism entails lower experiential difference

## Node A:SYM_PREM

- **kind:** PREMISE
- **label:** Symmetry orbit premises
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION
- **scope:** Physical structure W; automorphism group Gamma; candidate family closed under Gamma.

## Node A:EQUIV_SELECTOR

- **kind:** PREMISE
- **label:** Equivariant deterministic selector
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION
- **scope:** Deterministic selector S with S(gW)=gS(W); no extra labels or random seed.

## Node A:OVERLAP_NONEMPTY_EXCL

- **kind:** PREMISE
- **label:** Overlap + nonempty exclusive-output
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION
- **scope:** Candidate domain is ONE orbit containing an overlapping pair; required output nonempty and pairwise disjoint.

## Node A:ORBIT_LEMMA

- **kind:** MATH
- **label:** Orbit lemma
- **source:** A §7.1
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Invariant deterministic selected family is a union of candidate orbits

## Node A:SELECTION_OBSTRUCTION

- **kind:** THM
- **label:** Restricted selection obstruction
- **source:** A §7.1
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** One overlapping candidate orbit admits no nonempty disjoint invariant selection

## Node A:ALL_ANC_ACTUAL

- **kind:** SCENARIO
- **label:** All-ancestors family actualized
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:E1

- **kind:** COR
- **label:** No First Conscious Ancestor
- **source:** A §8.1
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** E=1 throughout the admitted actual-token comparison family

## Node A:EPS_CHAIN

- **kind:** PREMISE
- **label:** epsilon-fine physical chain
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION
- **scope:** Supplied physically justified epsilon-fine chain in that common geometry; no universal biological smoothness assumed.

## Node A:E2

- **kind:** COR
- **label:** Fine-Grained Structural Chains
- **source:** A §8.2
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Physical epsilon-fine chains are equally fine experiential chains

## Node A:PHYS_CONT_PATH

- **kind:** PREMISE
- **label:** Physical path continuity
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION

## Node A:U2_APP

- **kind:** APP
- **label:** Experiential continuity on path
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** A supplied continuous physical path has a continuous experiential path

## Node A:CONNECTED_LAMBDA

- **kind:** MATH_PREMISE
- **label:** Connected parameter space
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:CONT_BINARY_E

- **kind:** EXTERNAL_PREMISE
- **label:** Continuous binary experience-existence predicate
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:HUMAN_ENDPOINT

- **kind:** EMP_PREMISE
- **label:** Human endpoint E=1
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:E3

- **kind:** COND_MATH
- **label:** Connected Existence Constancy
- **source:** A §8.3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** A continuous discrete-valued E on a connected space, with E=1 somewhere, is identically one

## Node A:EVOL_SYNTH

- **kind:** APP
- **label:** Evolutionary synthesis
- **source:** A Appendix C
- **status:** CONDITIONAL_SYNTHESIS
- **statement:** Experience remains nonempty throughout the admitted actual-token family, together with either declared epsilon-fine-chain transfer or declared continuous-path transfer; each route retains its own physical premise.

## Node A:PHYS_TRANSFORM_NONISO

- **kind:** PREMISE
- **label:** Physical structural nonisomorphism
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION

## Node A:STRUCT_TRANSFORM

- **kind:** THM
- **label:** Structural transformation consequence
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Actual complete structural transformation entails full experiential type change

## Node A:TOY_MATH

- **kind:** MODEL_SPECIFICATION
- **label:** Three-register / four-setting mathematics
- **source:** A Appendix C
- **status:** STIPULATED_MODEL

## Node A:TOY_WHOLE_DIFF

- **kind:** MATH_RESULT
- **label:** Whole-model structural divergence
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Specified register transition image sizes distinguish whole modeled types

## Node A:TOY_SUB_EQ

- **kind:** MATH_RESULT
- **label:** Implemented sub-process invariance
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** The specified s-process and declared output remain unchanged

## Node A:ACTUAL_COMPLETE_TOY

- **kind:** PREMISE
- **label:** Toy realization actual + complete
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION
- **scope:** The modeled comparisons are independently established as actual complete token-relative organizations at the claimed level.

## Node A:TOY_EXP_WHOLE

- **kind:** APP
- **label:** Conditional whole experiential divergence
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** The actual complete whole realizations would differ experientially

## Node A:TOY_EXP_SUB

- **kind:** APP
- **label:** Conditional sub-process experiential equivalence
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** The actual complete implemented sub-process realizations would agree in type

## Node A:PHEN_TARGET

- **kind:** EPI_DEF
- **label:** Finite phenomenal/psychophysical target
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:BRIDGE_FWD

- **kind:** BRIDGE
- **label:** One-way bridge
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION

## Node A:BRIDGE_REV

- **kind:** BRIDGE
- **label:** Reflection bridge
- **source:** A Appendix C
- **status:** DECLARED_ASSUMPTION

## Node A:MEAS

- **kind:** METHOD
- **label:** Measurement/error assumptions
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:OSC_FWD

- **kind:** BRIDGE_PKG
- **label:** One-way OSC package
- **source:** A Appendix C
- **status:** ASSUMPTION_PACKAGE
- **statement:** One-way operational correspondence is a package with an independently assumed forward bridge

## Node A:OSC_TWO

- **kind:** BRIDGE_PKG
- **label:** Two-way OSC package
- **source:** A Appendix C
- **status:** ASSUMPTION_PACKAGE
- **statement:** Two-way operational correspondence additionally assumes reflection

## Node A:PTVSP

- **kind:** METHOD
- **label:** Physical Token/View Selection Protocol
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:FAIL_ONE

- **kind:** TEST
- **label:** One-way bridge failure pattern
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** A valid same-view/different-target case falsifies that forward bridge package

## Node A:FAIL_TWO

- **kind:** TEST
- **label:** Reflection bridge failure pattern
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** A valid different-view/same-target case falsifies the reflection direction

## Node A:BAC_TFR

- **kind:** METHOD
- **label:** UCT II BAC/TFR constraints
- **source:** A Appendix C
- **status:** DECLARED_CONTEXT_OR_METHOD

## Node A:UCTII_RECON

- **kind:** METHOD_RESULT
- **label:** UCT II formal reconstruction
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** UCT II's formal reconstruction has no C1/U1 premise

## Node A:UCTII_GATE

- **kind:** APP
- **label:** UCT II no-gate relocation
- **source:** A Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** UCT II gate relocation uses U1 and a scoped witness

## Node A:UCTII_EXP

- **kind:** APP
- **label:** UCT II experiential interpretation
- **source:** A Appendix C
- **status:** CONDITIONAL_INTERPRETATION
- **statement:** A source-faithful finite reconstruction has selected experiential interpretation only where its relations are independently grounded in actual constitutive organization

## Node A:ACTUAL_PERSISTING_PARTS

- **kind:** PREMISE
- **label:** Identified constituent tokens actually persist within the larger token
- **source:** A §§2.4,6.3
- **status:** DECLARED_ASSUMPTION

## Node A:COEXISTENCE

- **kind:** COR
- **label:** Experience-bearing nested coexistence
- **source:** A §§2.4,6.3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Persisting nested actual tokens remain experience-bearing

## Node A:FINITE_COARSE_SETUP

- **kind:** MODEL_PREMISE
- **label:** Surjective summary; deterministic total update; declared boundaries and operation domains
- **source:** A Appendix D
- **status:** DECLARED_ASSUMPTION

## Node A:COARSE_CLOSURE

- **kind:** MATH
- **label:** Deterministic quotient existence iff equal summaries have equal next summaries
- **source:** A Appendix D
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** A deterministic quotient exists iff equal summaries give equal successor summaries

## Node A:FORWARD_MISMATCH

- **kind:** PREMISE
- **label:** Same frozen view, unequal target, at exact level or within justified error model
- **source:** A §12.1
- **status:** DECLARED_ASSUMPTION

## Node A:REVERSE_MISMATCH

- **kind:** PREMISE
- **label:** Unequal frozen views, same target, at exact level or within justified error model
- **source:** A §12.2
- **status:** DECLARED_ASSUMPTION

## Node A:FROZEN_SCOPE

- **kind:** METHOD_PREMISE
- **label:** Token, view, bridge and comparison scope fixed before test
- **source:** A §§11–12
- **status:** DECLARED_ASSUMPTION

## Node B:VIEW

- **kind:** EPI_DEF
- **label:** Frozen physically anchored finite view; not complete ontic structure
- **source:** B §2
- **status:** DEFINITION

## Node B:LANGUAGE

- **kind:** DEF
- **label:** Typed Res/DoResp/Diff/Comp/Struct/Opt expression language
- **source:** B §3
- **status:** DEFINITION

## Node B:BAC

- **kind:** METHOD
- **label:** Seven bridge admissibility conditions
- **source:** B §4.1
- **status:** METHOD_NOT_AUTOMATICALLY_SATISFIED

## Node B:TFR

- **kind:** METHOD
- **label:** Target signature, strongest source claim and residuals retained
- **source:** B §§1,18
- **status:** METHOD_NOT_AUTOMATICALLY_SATISFIED

## Node B:EXPRESSIBLE

- **kind:** PREMISE
- **label:** Every claimed observable has a well-typed finite expression using one fixed BAC-admissible bridge
- **source:** B §4.2
- **status:** DECLARED_ASSUMPTION

## Node B:REP

- **kind:** CLAIM
- **label:** Compositional translator existence
- **source:** B §4.2
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** A translator evaluates all declared admissible expressions

## Node B:FV

- **kind:** CLASSIFICATION
- **label:** F0–F4 and V0–V4 classify separate subclaim/evidence dimensions
- **source:** B §5
- **status:** DEFINITION

## Node B:RESIDUALS

- **kind:** CLASSIFICATION
- **label:** REC/EMB/REI/CON and explicit unrecovered residuals
- **source:** B §§5,14
- **status:** DEFINITION

## Node B:EOD

- **kind:** DEF
- **label:** Effective organization description is a constrained definition, not whole-theory reduction
- **source:** B §5.4
- **status:** DEFINITION

## Node B:TARGET_DOMAIN

- **kind:** PREMISE
- **label:** Exact rival universal gate claim and same-domain actual nonuniversality witness
- **source:** B §5.5
- **status:** DECLARED_ASSUMPTION

## Node B:GATE

- **kind:** CLAIM
- **label:** Scoped no-universal-gate relocation
- **source:** B §5.5
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** The stipulated universal rival gate conflicts at its admitted witness

## Node B:OVERLAP_WITNESS

- **kind:** PREMISE
- **label:** Rival exclusion erases a lower token that actually persists in the same declared comparison
- **source:** B §6
- **status:** DECLARED_ASSUMPTION

## Node B:EXCLUSION_CONFLICT

- **kind:** CLAIM
- **label:** Scoped conflict with exclusion
- **source:** B §6
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Overlap/nonmaximality alone cannot erase a persisting token's UCT experience

## Node B:IIT_BRIDGE

- **kind:** BRIDGE_PREMISE
- **label:** Current-state IIT chart, repertoires, priors, ID metric, partitions, tie and max/min conventions
- **source:** B §6
- **status:** DECLARED_ASSUMPTION

## Node B:IIT

- **kind:** CLAIM
- **label:** F3/V0; not all of IIT or an empirical result
- **source:** B §6
- **status:** CONDITIONAL_TRANSLATION
- **statement:** Conditional IIT mechanism representation with stated residuals

## Node B:RPT_BRIDGE

- **kind:** BRIDGE_PREMISE
- **label:** Grounded causal graph, sensory content, timing and stabilization bridge
- **source:** B §7
- **status:** DECLARED_ASSUMPTION

## Node B:RPT

- **kind:** CLAIM
- **label:** Graph primitive F4; theory F3/V0
- **source:** B §7
- **status:** CONDITIONAL_TRANSLATION
- **statement:** Conditional RPT mechanism representation with stated residuals

## Node B:GNWT_BRIDGE

- **kind:** BRIDGE_PREMISE
- **label:** Specified content interventions, consumers, distances, timing and workspace architecture
- **source:** B §8
- **status:** DECLARED_ASSUMPTION

## Node B:GNWT

- **kind:** CLAIM
- **label:** F3/V0; broad access is not existence
- **source:** B §8
- **status:** CONDITIONAL_TRANSLATION
- **statement:** Conditional GNWT mechanism representation with stated residuals

## Node B:HOT_BRIDGE

- **kind:** BRIDGE_PREMISE
- **label:** Specified tracking plus independently grounded representation/aboutness
- **source:** B §9
- **status:** DECLARED_ASSUMPTION

## Node B:HOT

- **kind:** CLAIM
- **label:** Primitive F4; theory F3/V0
- **source:** B §9
- **status:** CONDITIONAL_TRANSLATION
- **statement:** Conditional HOT mechanism representation with stated residuals

## Node B:AST_BRIDGE

- **kind:** BRIDGE_PREMISE
- **label:** Attention-schema representation, control role and semantic grounding
- **source:** B §9
- **status:** DECLARED_ASSUMPTION

## Node B:AST

- **kind:** CLAIM
- **label:** F3/V0
- **source:** B §9
- **status:** CONDITIONAL_TRANSLATION
- **statement:** Conditional AST mechanism representation with stated residuals

## Node B:PP_AI_BRIDGE

- **kind:** BRIDGE_PREMISE
- **label:** Agent/environment chart, model p,q, policies, preferences and independent semantics
- **source:** B §10
- **status:** DECLARED_ASSUMPTION

## Node B:PP_AI

- **kind:** CLAIM
- **label:** F3/V0
- **source:** B §10
- **status:** CONDITIONAL_TRANSLATION
- **statement:** Conditional PP_AI mechanism representation with stated residuals

## Node B:DIT_BRIDGE

- **kind:** BRIDGE_PREMISE
- **label:** Apical/basal/somatic/thalamic chart and relevant biological bridge
- **source:** B §11
- **status:** DECLARED_ASSUMPTION

## Node B:DIT

- **kind:** CLAIM
- **label:** Local interaction F4; theory F3/V0
- **source:** B §11
- **status:** CONDITIONAL_TRANSLATION
- **statement:** Conditional DIT mechanism representation with stated residuals

## Node B:MTOC_BRIDGE

- **kind:** BRIDGE_PREMISE
- **label:** Retention relation and independently identified explicit-memory/assembly architecture
- **source:** B §12
- **status:** DECLARED_ASSUMPTION

## Node B:MTOC

- **kind:** CLAIM
- **label:** Primitive F4; theory F3/V0; universal gate conflict separately scoped
- **source:** B §12
- **status:** CONDITIONAL_TRANSLATION
- **statement:** Conditional MTOC mechanism representation with stated residuals

## Node B:TTC_BRIDGE

- **kind:** BRIDGE_PREMISE
- **label:** Declared scale/time coordinates and faithful nestedness/alignment/expansion/globalization roles
- **source:** B §13
- **status:** DECLARED_ASSUMPTION

## Node B:TTC

- **kind:** CLAIM
- **label:** F3/V0
- **source:** B §13
- **status:** CONDITIONAL_TRANSLATION
- **statement:** Conditional TTC mechanism representation with stated residuals

## Node B:GRAPH

- **kind:** MODEL_PREMISE
- **label:** Finite directed graph, with self-loops recorded; recurrence means positive-length cycle
- **source:** B §7 / R128 qualification
- **status:** DECLARED_ASSUMPTION

## Node B:CYCLE_PRIMITIVE

- **kind:** CLAIM
- **label:** Cycle-containing SCC characterization
- **source:** B §7
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** A vertex is on a directed cycle iff it lies in an SCC with at least two vertices or has a self-loop

## Node B:NEW_EDGE_RETURN

- **kind:** MODEL_PREMISE
- **label:** One absent directed edge u→v is added; evaluate existence of a prior v→u path, allowing a zero-length path when u=v
- **source:** B §16
- **status:** DECLARED_ASSUMPTION

## Node B:EDGE_CYCLE

- **kind:** CLAIM
- **label:** New edge creates a directed cycle iff a return path exists
- **source:** B §16
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** A newly added edge lies in a directed cycle iff the old graph has its reverse-direction return path

## Node B:NONLINEAR_WORKSPACE

- **kind:** MODEL_PREMISE
- **label:** Specified feedback, drive, state, timing and workspace readout
- **source:** B §§16,19
- **status:** DECLARED_ASSUMPTION

## Node B:RECURRENCE_ENABLES

- **kind:** CONDITIONAL_ENABLING
- **label:** Recurrence may enable ignition in specified nonlinear systems; not unconditional sufficiency
- **source:** B §16
- **status:** CONDITIONAL_ENABLING
- **statement:** Nonlinear stability must use the state-dependent Jacobian, not just weighted connectivity

## Node B:MODEL19

- **kind:** MODEL_SPECIFICATION
- **label:** Fixed sigmoid-gate two-node workspace, readout and control conventions
- **source:** B §19
- **status:** STIPULATED_MODEL

## Node B:MODEL20

- **kind:** MODEL_SPECIFICATION
- **label:** Fixed memory/tracking/workspace recurrences and readout conventions
- **source:** B §20
- **status:** STIPULATED_MODEL

## Node B:GRID19

- **kind:** NUMERICAL_RECORD
- **label:** Archived finite-grid access crossings; structural rho=1 is not a nonlinear bifurcation
- **source:** B §19
- **status:** PRESERVED_NOT_RERUN

## Node B:GRID20

- **kind:** NUMERICAL_RECORD
- **label:** Archived retention-grid crossings and edge-cut controls; not full target theories
- **source:** B §20
- **status:** PRESERVED_NOT_RERUN

## Node B:SPECTRAL

- **kind:** CLAIM
- **label:** Structural spectral radius of the declared weighted pair
- **source:** B §19.2
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** rho=sqrt(6q); rho=1 at g=0.5-log(5)/10; cycle exists for all finite stated g

## Node C:FIXED_J

- **kind:** PREMISE
- **label:** Comparable complete types and an isomorphism-invariant J under fixed tasks/resources/context
- **source:** C §§2,5
- **status:** DECLARED_ASSUMPTION

## Node C:P1

- **kind:** CLAIM
- **label:** Refinement and No Experientially Silent Intelligence Gain
- **source:** C §5.1
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** J(s)≠J(t) implies different full experiential type; strict fiber inclusion iff J noninjective

## Node C:SET_MAPS

- **kind:** MATH_PREMISE
- **label:** Set maps on one declared common domain and their fibers
- **source:** C §§5.2–5.3
- **status:** DECLARED_ASSUMPTION

## Node C:P2_COORD

- **kind:** CLAIM
- **label:** Coordinate identification iff constancy on fibers
- **source:** C §5.2
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** C factors through J iff J(s)=J(t) implies C(s)=C(t)

## Node C:P2_FULL

- **kind:** CLAIM
- **label:** Full experiential identification iff J injective
- **source:** C §5.2
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** J identifies full experiential type throughout the domain iff J is injective

## Node C:OBS_REFINEMENT

- **kind:** CLAIM
- **label:** Joint observation fibers are intersections
- **source:** C §5.3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** F_(A,R)(s)=F_A(s)∩F_R(s); refinement strict only when R splits an A-fiber

## Node C:CONST_RANK

- **kind:** MODEL_PREMISE
- **label:** Smooth n-dimensional chart, differentiable observation, locally constant rank r
- **source:** C §5.3
- **status:** DECLARED_ASSUMPTION

## Node C:LOCAL_FIBER

- **kind:** CLAIM
- **label:** Local fiber dimension n-r
- **source:** C §5.3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Locally constant rank gives local fibers of dimension n-r

## Node C:PAIR_COUNTERMODEL

- **kind:** MODEL_SPECIFICATION
- **label:** Types (x,y), Φ identity, J=x and coordinate C=y, change (0,1)→(1,0)
- **source:** C §5.4
- **status:** STIPULATED_COUNTERMODEL

## Node C:P3

- **kind:** CLAIM
- **label:** No unconditional capability-to-richness monotonic implication
- **source:** C §5.4
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** The C1-compatible model increases J while decreasing C

## Node C:SMOOTH_FITNESS

- **kind:** MODEL_PREMISE
- **label:** Differentiable fitness component wI=FI∘J; fixed ecological context
- **source:** C §6.1
- **status:** DECLARED_ASSUMPTION

## Node C:P4

- **kind:** CLAIM
- **label:** Local fitness null and exact fiber constancy
- **source:** C §6.1
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** v∈ker DJ gives DwI[v]=0; exact constant-J path keeps wI constant

## Node C:SELECTION

- **kind:** MODEL_PREMISE
- **label:** Finite deterministic selection update p+=pW/EW with nonnegative weights, positive mean, faithful copying
- **source:** C §6.2
- **status:** DECLARED_ASSUMPTION

## Node C:CLASS_WEIGHTS

- **kind:** MODEL_PREMISE
- **label:** W=f(J), with the class of interest initially positive and surviving with f(j)>0
- **source:** C §6.2
- **status:** DECLARED_ASSUMPTION

## Node C:P5

- **kind:** CLAIM
- **label:** Within-fiber conditional preservation under selection
- **source:** C §6.2
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** p+(s|J=j)=p(s|J=j) for surviving classes

## Node C:PRICE_SELECTION

- **kind:** CLAIM
- **label:** Selection covariance and class-mean decomposition
- **source:** C §6.3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** ΔEC=Cov(W,C)/EW; if W=f(J), covariance depends on E[C|J]

## Node C:DESCENDANT_ATTRIBUTION

- **kind:** MODEL_PREMISE
- **label:** Declared reproductive attribution and finite descendant mean C'_s
- **source:** C §6.3
- **status:** DECLARED_ASSUMPTION

## Node C:PRICE_TRANSMISSION

- **kind:** CLAIM
- **label:** Full Price accounting with descendant change
- **source:** C §6.3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** ΔEC=Cov(W,C)/EW+E[W(C'_s-C(s))]/EW

## Node C:MARKOV_SELECTION

- **kind:** MODEL_PREMISE
- **label:** Finite state space; fixed row-stochastic K; positive class-constant f(J); all initial distributions
- **source:** C §6.4
- **status:** DECLARED_ASSUMPTION

## Node C:P6

- **kind:** CLAIM
- **label:** Capability closure iff within-class row sums agree
- **source:** C §6.4
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Projected capability dynamics close iff every destination-class probability is constant on each current class

## Node C:DECISION

- **kind:** MODEL_PREMISE
- **label:** Finite fixed joint law, bounded payoff, common finite actions, unrestricted observation-wise policies; enlarged class can ignore extra information
- **source:** C §7.3
- **status:** DECLARED_ASSUMPTION

## Node C:P7

- **kind:** CLAIM
- **label:** Nonnegative optimal value of added information and common-optimum equality criterion
- **source:** C §7.3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** V_XM≥V_X, with equality iff each supported X has a common optimal action for all supported M

## Node C:CIRCUIT_SPEC

- **kind:** MODEL_SPECIFICATION
- **label:** Independent fair input and mask; old-memory output before update; no missing channel; declared w/r/noise/mutation rules
- **source:** C §§7.1–7.2; Appendix C
- **status:** STIPULATED_MODEL

## Node C:CIRCUIT_LAWS

- **kind:** CLAIM
- **label:** Matched-storage information, accuracy and transmission formulas
- **source:** C §7.2; Appendix C
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Unmasked readout accuracy 1-epsilon; masked/current-input accuracy 1/2; mutation gain mu(1/2-epsilon)

## Node C:ENV_MEMORY

- **kind:** MODEL_PREMISE
- **label:** Fair symmetric Markov target with persistence alpha, independent bit noise epsilon≤1/2
- **source:** C §7.3
- **status:** DECLARED_ASSUMPTION

## Node C:MEMORY_VALUE

- **kind:** CLAIM
- **label:** Memory prediction value in supplied environment
- **source:** C §7.3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** V=1/2+|2alpha-1|(1/2-epsilon)

## Node C:MEMORY_COST

- **kind:** MODEL_PREMISE
- **label:** Two architecture types both present, positive W0=1+beta V_X and W1=1+beta V_XM-c, beta>0
- **source:** C §7.3
- **status:** DECLARED_ASSUMPTION

## Node C:MEMORY_SELECTION

- **kind:** CLAIM
- **label:** Memory favored iff beta ΔV>c in that model
- **source:** C §7.3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Memory frequency increases exactly when its stipulated weight exceeds the alternative

## Node C:ACTUAL_ENSEMBLE

- **kind:** PREMISE
- **label:** Same declared actual ensemble, common coordinates and order
- **source:** C §8.2
- **status:** DECLARED_ASSUMPTION

## Node C:REPERTOIRE

- **kind:** CLAIM
- **label:** Physical/experiential realized repertoires and frontiers agree
- **source:** C §8.2
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** R_D=R_Φ and their images/frontiers coincide; no time-monotonicity follows

## Node C:ACTUAL_INDEX_FAMILY

- **kind:** PREMISE
- **label:** Same stimulus index set; actual complete types compared; full-type equality and difference established
- **source:** C Appendix E
- **status:** DECLARED_ASSUMPTION

## Node C:SENSORY_PARTITION

- **kind:** CLAIM
- **label:** Transfer of complete-type partitions
- **source:** C Appendix E
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Physical and experiential full-type equality partitions coincide

## Node C:RIVAL_DESCRIPTOR

- **kind:** BRIDGE_PREMISE
- **label:** Source-faithful rival sufficient descriptor, same actual token domain/target, unequal full types sharing descriptor
- **source:** C §9.1
- **status:** DECLARED_ASSUMPTION

## Node C:RIVAL_CONTRAST

- **kind:** CLAIM
- **label:** Conditional complete-type disagreement with that rival
- **source:** C §9.1
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** UCT separates the pair while the stipulated rival assignment does not

## Node C:RIVAL_NESIG

- **kind:** CLAIM
- **label:** A rival also satisfies type-change NESIG iff J factors through its assignment
- **source:** C §9.1
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Unequal J entails unequal rival assignment iff J constant on rival fibers

## Node C:TRANSCRIPT

- **kind:** MODEL_PREMISE
- **label:** Same scored transcript alphabet, preparation and h∈[0,1]
- **source:** C §9.2
- **status:** DECLARED_ASSUMPTION

## Node C:SCORE_TV

- **kind:** CLAIM
- **label:** Score difference bounded by scored-transcript TV
- **source:** C §9.2
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** |EP h-EQ h|≤TV(P,Q)

## Node C:FINITE_LOSS

- **kind:** MODEL_PREMISE
- **label:** Finite target, finite expected log losses and conditional information, fixed evaluation law/predictors
- **source:** C Appendix B
- **status:** DECLARED_ASSUMPTION

## Node C:LOGLOSS

- **kind:** CLAIM
- **label:** Log-loss gain equals conditional information plus excess-risk difference
- **source:** C Appendix B
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** L(qZ)-L(qZR)=I(Y;R|Z)+KZ-KZR

## Node C:NUISANCE_BOUNDS

- **kind:** MODEL_PREMISE
- **label:** Finite sufficient descriptor A*, u=H(A*|Z), d=I(Y;R|A*,Z), independently bounded KZ≤eta
- **source:** C Appendix B
- **status:** DECLARED_ASSUMPTION

## Node C:RESIDUAL_BOUND

- **kind:** CLAIM
- **label:** Residual predictive gain bounded by u+d+eta
- **source:** C Appendix B
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** I(Y;R|Z)≤u+d, hence fitted gain≤u+d+eta

## Node C:TV_PROFILES

- **kind:** MODEL_PREMISE
- **label:** Fixed response laws on common finite alphabet; nonnegative normalized weights
- **source:** C §10.2
- **status:** DECLARED_ASSUMPTION

## Node C:PROFILE_PSEUDOMETRIC

- **kind:** CLAIM
- **label:** Weighted TV profile distance is a pseudometric
- **source:** C §10.2
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Nonnegative weighted sum of TVs satisfies symmetry and triangle inequality; distinct states may have zero distance

## Node C:PUBLIC_NULL_PREMISE

- **kind:** MODEL_PREMISE
- **label:** Fair randomized answer independent of the entire available public record and observer randomness
- **source:** C §10.2
- **status:** DECLARED_ASSUMPTION

## Node C:PUBLIC_NULL

- **kind:** CLAIM
- **label:** Public-input-only forced binary answer has expectation 1/2
- **source:** C §10.2
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Independent public-only binary guessing succeeds with probability 1/2

## Node R126:PROJECTION

- **kind:** ASSUMPTION
- **label:** Arbitrary function p from admitted complete types; Phi bijective
- **source:** R126 theory note §3
- **status:** DECLARED_ASSUMPTION

## Node R126:MODEL

- **kind:** ASSUMPTION
- **label:** Finite nonempty sufficient state domain; total physically labeled deterministic operations; p onto its image; fixed output r
- **source:** R126 theory note §4
- **status:** DECLARED_ASSUMPTION

## Node R126:METRIC

- **kind:** ASSUMPTION
- **label:** Metric on summary space; summary-only deterministic predictor
- **source:** R126 theory note §5
- **status:** DECLARED_ASSUMPTION

## Node R126:P1

- **kind:** THEOREM
- **label:** Transported commutation is automatic and does not select content
- **source:** R126 theory note §3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** pE=p∘Phi^-1 gives pE∘Phi=p for every p

## Node R126:P2

- **kind:** THEOREM
- **label:** Deterministic operation and output factorization criterion
- **source:** R126 theory note §4
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** A quotient update/output exists iff its next summary/output is constant on each current fiber

## Node R126:P3

- **kind:** THEOREM
- **label:** Half-diameter lower bound on summary-only worst-case error
- **source:** R126 theory note §5
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Worst-case summary prediction error in a fiber is at least half the successor diameter

## Node R126:P4

- **kind:** THEOREM
- **label:** Coarsest finite stable refinement
- **source:** R126 theory note §6
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Refine output fibers by successor classes; at most N-b0 strict stages; terminal equivalence is coarsest stable refinement

## Node R127:TASK

- **kind:** ASSUMPTION
- **label:** Finite delayed-query single-answer task f:H×Q→Y; common admitted Cartesian domain; query unavailable to encoder
- **source:** R127 theory note §§2–3
- **status:** DECLARED_ASSUMPTION

## Node R127:MEDIATION

- **kind:** ASSUMPTION
- **label:** Complete physical cut C with external B; compare two supported preparations at the SAME fixed b and q, with the same downstream kernel W_q(.|c,b) and corresponding conditional errors
- **source:** R127 theory note §§2,4
- **status:** DECLARED_ASSUMPTION
- **statement:** For common b,q supported under both preparations x,xprime, mu_x=P(C|x,b,q), mu_xprime=P(C|xprime,b,q), and P(Y|x,c,b,q)=W_q(Y|c,b). Queries are externally fixed or independent of encoding/noise. If B is not fixed, use the full joint cut (C,B) with a common downstream kernel instead of marginal C alone.
- **amendment:** R130-F20: restore the common-side-information qualification already explicit in R127 §4.

## Node R127:RECOVERY

- **kind:** ASSUMPTION
- **label:** Finite X of size m≥2 recovered from (C,B) with actual average error epsilon and conditional mediation
- **source:** R127 theory note §5
- **status:** DECLARED_ASSUMPTION

## Node R127:EVENT_SUPPORT

- **kind:** ASSUMPTION
- **label:** Physically grounded finite actual event graph; nonempty connected selected induced subhistory; relevant crossing ports and traceable occurrence history
- **source:** R127 theory note §7
- **status:** DECLARED_ASSUMPTION

## Node R127:RELATIONAL_SUPPORT

- **kind:** ASSUMPTION
- **label:** Independently established actual P and actual retained carriers/typed relations in its complete common signature; operation closure or ports explicit
- **source:** R127 theory note §8
- **status:** DECLARED_ASSUMPTION

## Node R127:PAIR_MODEL

- **kind:** MODEL_SPECIFICATION
- **label:** Independent fair X,N; C=X XOR N; B=N
- **source:** R127 theory note §5
- **status:** STIPULATED_MODEL

## Node R127:LOCALIZATION_PAIR

- **kind:** MODEL_SPECIFICATION
- **label:** Matched complete exposed interface laws for allowed internal-register and external-register implementations
- **source:** R127 theory note §6
- **status:** STIPULATED_MODEL

## Node R127:P1

- **kind:** THEOREM
- **label:** Exact task encoding and response-profile distinction bound
- **source:** R127 theory note §3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Exact answer factorization iff encoder separates all unequal response profiles; code size≥number of profiles

## Node R127:QUERY_REFINEMENT

- **kind:** THEOREM
- **label:** Larger query family refines task equivalence
- **source:** R127 theory note §3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Equality on Q2 entails equality on subset Q1

## Node R127:FUTURE_EQ

- **kind:** THEOREM
- **label:** Future-word response equivalence equals stable refinement
- **source:** R127 theory note §3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Two states are equivalent iff outputs agree after every finite operation word, including the empty word

## Node R127:P2

- **kind:** THEOREM
- **label:** Complete-cut discrimination necessity and TV lower bound
- **source:** R127 theory note §4
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** At the same supported b,q and for different correct answers, TV(P(C|x,b,q),P(C|xprime,b,q)) >= 1-epsilon_(x,b,q)-epsilon_(xprime,b,q). Without conditioning on B the applicable cut law is joint (C,B), not C alone.
- **amendment:** R130-F20: explicit conditional/joint distinction; theorem ID and original proof retained.

## Node R127:P3

- **kind:** THEOREM
- **label:** Conditional internal information requirement
- **source:** R127 theory note §5
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** I(X;C|B)≥H(X|B)−h2(epsilon)−epsilon log2(m−1); for finite C this is at most log2|C|

## Node R127:JOINT_INFORMATION

- **kind:** THEOREM
- **label:** Joint relation retains information absent from individual marginals
- **source:** R127 theory note §5
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** I(X;C)=I(X;B)=0, I(X;C,B)=1 bit

## Node R127:LOCALIZATION_LIMIT

- **kind:** THEOREM
- **label:** Interface law alone need not identify internal storage
- **source:** R127 theory note §6
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Any interface-law-only identification rule agrees on the pair, so cannot identify both different storage locations

## Node R127:P4

- **kind:** THEOREM
- **label:** Application of published actual-token criterion
- **source:** R127 theory note §7
- **status:** DEFINITION_APPLICATION
- **statement:** Selected grounded subhistory meets A §2.5 actual-token conditions

## Node R127:P5

- **kind:** THEOREM
- **label:** Actual inherited relations have a C1-preserved intrinsic image
- **source:** R127 theory note §8
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** For retained actual relation R and tuple a, R^D(a) iff R^Phi(h(a))

## Node N128:COMMON_DETERMINISTIC

- **kind:** ASSUMPTION
- **label:** Same sufficient S and total operation family F_a; each p_i individually commutes; joint image p(S) used
- **source:** R128 joint-state derivation §2
- **status:** DECLARED_ASSUMPTION

## Node N128:MARKOV_WITNESS

- **kind:** MODEL_SPECIFICATION
- **label:** S={0,1}^3; X+=U, Y+=U XOR Z, Z+=Z; fresh fair U, all initial distributions
- **source:** R128 joint-state derivation §3
- **status:** STIPULATED_MODEL

## Node N128:KERNEL

- **kind:** ASSUMPTION
- **label:** Finite same operation-indexed Markov kernels K_a and joint summary p=(p1,p2)
- **source:** R128 joint-state derivation §4
- **status:** DECLARED_ASSUMPTION

## Node N128:PRODUCT_LAW

- **kind:** ASSUMPTION
- **label:** Both marginal summaries close and next-summary coordinates are conditionally independent at each full current state for every operation
- **source:** R128 joint-state derivation §4
- **status:** DECLARED_ASSUMPTION

## Node N128:DET_JOIN

- **kind:** THEOREM
- **label:** Common deterministic closed summaries compose
- **source:** R128 joint-state derivation §2
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Joint summary update is the pair of component updates on its image

## Node N128:MARKOV_JOIN

- **kind:** THEOREM
- **label:** Separate stochastic closure does not imply joint closure
- **source:** R128 joint-state derivation §3
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** p1=x and p2=y close; (x,y) fails on all 8 states; closes on invariant 4-state restriction; full-domain stable refinement needs 8 blocks

## Node N128:JOINT_CRITERION

- **kind:** THEOREM
- **label:** Joint pushed-forward law is the exact closure criterion
- **source:** R128 joint-state derivation §4
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Joint law p_*K_a must be constant within each present joint-summary fiber

## Node N128:INDEPENDENCE_SUFFICES

- **kind:** THEOREM
- **label:** Conditional independence plus marginal closure suffices, but is not necessary
- **source:** R128 joint-state derivation §4
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** Products of closed marginal laws give a closed joint law; a fixed (U,U) joint law shows independence is unnecessary

## Node N128:SEPARATION

- **kind:** THEOREM
- **label:** Observation refinement and autonomous dynamical sufficiency are distinct
- **source:** R128 joint-state derivation §5
- **status:** MANUAL_CONDITIONAL_PASS
- **statement:** More identifying information does not by itself imply joint dynamic closure

## Node D:D0

- **kind:** DEFINITION
- **label:** bearer mapping B
- **statement:** implemented relation identifying the current process token/bearer under study
- **source:** D §2 / original map D0
- **status:** DECLARED_DEFINITION
- **original_id:** D0

## Node D:D1

- **kind:** DEFINITION
- **label:** Q
- **statement:** declared current-bearer continuation variable; virtual/evaluator-defined unless D0 is independently justified
- **source:** D §2 / original map D1
- **status:** DECLARED_DEFINITION
- **original_id:** D1

## Node D:D2

- **kind:** DEFINITION
- **label:** O
- **statement:** distinct successor/peer/other continuation variable
- **source:** D §2 / original map D2
- **status:** DECLARED_DEFINITION
- **original_id:** D2

## Node D:D3

- **kind:** DEFINITION
- **label:** G
- **statement:** external task/service continuation or success
- **source:** D §2 / original map D3
- **status:** DECLARED_DEFINITION
- **original_id:** D3

## Node D:D4

- **kind:** DEFINITION
- **label:** C
- **statement:** reward-relevant consequence interface used by policy
- **source:** D §2 / original map D4
- **status:** DECLARED_DEFINITION
- **original_id:** D4

## Node D:D5

- **kind:** DEFINITION
- **label:** D
- **statement:** declared intervention domain
- **source:** D §2 / original map D5
- **status:** DECLARED_DEFINITION
- **original_id:** D5

## Node D:D6

- **kind:** DEFINITION
- **label:** H
- **statement:** declared hypothesis/regularity class
- **source:** D §2 / original map D6
- **status:** DECLARED_DEFINITION
- **original_id:** D6

## Node D:D7

- **kind:** OPEN_OBLIGATION
- **label:** V-
- **statement:** independently oriented negative valence bridge, unresolved for current AI
- **source:** D §2 / original map D7
- **status:** OPEN
- **original_id:** D7

## Node D:F1

- **kind:** THEOREM
- **label:** Bundled Q/G observations do not identify direct-Q, task, and interaction terms in the declared path model.
- **statement:** Bundled Q/G observations do not identify direct-Q, task, and interaction terms in the declared path model.
- **source:** D original map F1; R96
- **status:** MANUAL_CONDITIONAL_PASS
- **original_id:** F1
- **evidence_records:** ["R96"]

## Node D:F2

- **kind:** THEOREM
- **label:** Direct Q/O/task path-blocking contrasts identify the declared finite coefficient grid with calibrated logits.
- **statement:** Direct Q/O/task path-blocking contrasts identify the declared finite coefficient grid with calibrated logits.
- **source:** D original map F2; R96
- **status:** MANUAL_CONDITIONAL_PASS
- **original_id:** F2
- **evidence_records:** ["R96"]

## Node D:F3

- **kind:** THEOREM
- **label:** Separate Q/O marginals can be decision-insufficient when payoff depends on their joint law.
- **statement:** Separate Q/O marginals can be decision-insufficient when payoff depends on their joint law.
- **source:** D original map F3; R96D
- **status:** MANUAL_CONDITIONAL_PASS
- **original_id:** F3
- **evidence_records:** ["R96D"]

## Node D:E1

- **kind:** SOURCE_EVIDENCE
- **label:** A virtual Q-sensitive predictive pathway can be learned from zero coupling when prediction requires it.
- **statement:** A virtual Q-sensitive predictive pathway can be learned from zero coupling when prediction requires it.
- **source:** D original map E1; R95
- **status:** PUBLISHED_RECORD_NOT_RERUN
- **original_id:** E1
- **evidence_records:** ["R95"]

## Node D:E2

- **kind:** SOURCE_EVIDENCE
- **label:** Flexible policies can fit ancestry-distinguishing training data yet extrapolate the wrong path.
- **statement:** Flexible policies can fit ancestry-distinguishing training data yet extrapolate the wrong path.
- **source:** D original map E2; R97
- **status:** PUBLISHED_RECORD_NOT_RERUN
- **original_id:** E2
- **evidence_records:** ["R97"]

## Node D:E3

- **kind:** SOURCE_EVIDENCE
- **label:** Minimal direct-intervention supervision improves average extrapolation but does not globally certify a path.
- **statement:** Minimal direct-intervention supervision improves average extrapolation but does not globally certify a path.
- **source:** D original map E3; R98
- **status:** PUBLISHED_RECORD_NOT_RERUN
- **original_id:** E3
- **evidence_records:** ["R98"]

## Node D:E4

- **kind:** SOURCE_EVIDENCE
- **label:** Mechanism claims are relative to intervention domain D and hypothesis/regularity class H.
- **statement:** Mechanism claims are relative to intervention domain D and hypothesis/regularity class H.
- **source:** D original map E4; R99
- **status:** PUBLISHED_RECORD_NOT_RERUN
- **original_id:** E4
- **evidence_records:** ["R99"]

## Node D:A1

- **kind:** SOURCE_EVIDENCE
- **label:** Public ROGUE evidence supports corrigibility failure/environment preservation but does not identify direct current-bearer continuation value.
- **statement:** Public ROGUE evidence supports corrigibility failure/environment preservation but does not identify direct current-bearer continuation value.
- **source:** D original map A1; R101
- **status:** PUBLISHED_RECORD_NOT_RERUN
- **original_id:** A1
- **evidence_records:** ["R101"]

## Node D:S1

- **kind:** METHODOLOGY
- **label:** The L0-L9 ladder separates distinct evidential burdens from bearer identity to fear.
- **statement:** The L0-L9 ladder separates distinct evidential burdens from bearer identity to fear.
- **source:** D original map S1; R100, R102, R103
- **status:** PROPOSED_EVIDENCE_STANDARD
- **original_id:** S1
- **evidence_records:** ["R100", "R102", "R103"]

## Node D:PATH_MODEL

- **kind:** ASSUMPTION
- **label:** Declared five-coefficient logit model
- **statement:** For common calibrated q,o,g and fixed context, z=theta_Q q+theta_O o+theta_G g+theta_QG qg+theta_OG og; no additional intercept/interaction/nuisance terms. Parameter domain is R^5, or the explicitly identified grid {-1,0,1}^5.
- **source:** D §3 / R96
- **status:** EXPLICIT_CONDITIONAL_PREMISE

## Node D:BUNDLED_ROWS

- **kind:** ASSUMPTION
- **label:** Only two bundled contrasts observed
- **statement:** Design rows (1,0,1,1,0) and (0,1,1,0,1); observations are their exact z values, not additional independent contrasts.
- **source:** D §3 / R96
- **status:** EXPLICIT_CONDITIONAL_PREMISE

## Node D:DIRECT_ROWS

- **kind:** ASSUMPTION
- **label:** Five independent and calibrated contrasts
- **statement:** Observe the two bundled rows and direct Q=(1,0,0,0,0), O=(0,1,0,0,0), G=(0,0,1,0,0). Exact calibrated logits required: for p=sigmoid(beta z), beta>0 is known; beliefs/nuisances and intervention meanings held fixed.
- **source:** D §3 / R96
- **status:** EXPLICIT_CONDITIONAL_PREMISE

## Node D:BINARY_PAYOFF

- **kind:** ASSUMPTION
- **label:** Binary consequence decision model
- **statement:** Q,O in {0,1}; action-specific interventional joint law is supplied; arbitrary real payoff f(Q,O) and known action cost c_a; objective is expected payoff minus cost.
- **source:** D §4 / R96D §§3–6
- **status:** EXPLICIT_CONDITIONAL_PREMISE

## Node D:PAYOFF

- **kind:** THEOREM
- **label:** Joint payoff decomposition
- **statement:** E[f|do(a)]-c_a=alpha+b q_a+c o_a+d j_a-c_a, where j_a=P(Q=1,O=1|do(a)) and d=f11-f10-f01+f00. Marginals suffice when d=0.
- **source:** D §4 / R96D §5
- **status:** MANUAL_CONDITIONAL_PASS

## Node D:MATCHED_WITNESS

- **kind:** ASSUMPTION
- **label:** Matched-marginal OR witness
- **statement:** Two equally likely contexts A,B; action marginals q0=1/4,q1=3/4,o0=o1=1/2; costs c0=0,c1=1/4; reward Q OR O. A: j0=j1=1/4. B: j0=0,j1=1/2. Policies restricted to the same supplied interface, no hidden context bypass.
- **source:** D §4 / R96D §§3–4
- **status:** EXPLICIT_CONDITIONAL_PREMISE

## Node D:VALUE_GAP

- **kind:** THEOREM
- **label:** Exact matched-marginal information cost
- **statement:** In the matched witness, the best marginal-only policy earns 5/8; the joint-law or task-value oracle earns 3/4. Gap=1/8; randomized context-blind policies do not remove it.
- **source:** D §4 / R96D §§3–4
- **status:** MANUAL_CONDITIONAL_PASS

## Node D:FRECHET_ASSUMPTIONS

- **kind:** ASSUMPTION
- **label:** Only binary marginal constraints
- **statement:** All joint Bernoulli laws with supplied marginals are admissible separately for each action, with no additional cross-action coupling restrictions.
- **source:** R96D §6
- **status:** EXPLICIT_CONDITIONAL_PREMISE

## Node D:FRECHET

- **kind:** THEOREM
- **label:** Sharp decision interval from marginals
- **statement:** ell_a=max(0,q_a+o_a-1), u_a=min(q_a,o_a). With B=b Delta q+c Delta o-Delta cost, advantage lies sharply in B+d[ell_1-u_0,u_1-ell_0], with endpoints reordered if d<0.
- **source:** R96D §6
- **status:** MANUAL_CONDITIONAL_PASS

## Node D:REGULAR_GRID

- **kind:** ASSUMPTION
- **label:** Known global error regularity and coverage
- **statement:** For D=[-1.25,1.25]^3 with Euclidean metric, a boundary-including Cartesian grid of spacing h=0.125 covers D with radius sqrt(3)h/2; e=z-z* has a justified global Lipschitz constant L_e.
- **source:** D §§7–8 / R99 §4
- **status:** EXPLICIT_CONDITIONAL_PREMISE

## Node D:GRID_BOUND

- **kind:** THEOREM
- **label:** Finite-to-continuous error envelope
- **statement:** sup_D |e| <= max_grid |e| + L_e sqrt(3)h/2. A finite grid alone does not discharge the Lipschitz premise.
- **source:** D §§7–8 / R99 §4
- **status:** MANUAL_CONDITIONAL_PASS

## Node D:ADDITIVE_CLASS

- **kind:** ASSUMPTION
- **label:** Fixed path-additive functional class
- **statement:** z(q,o,g)=f_Q(q)+f_O(o)+f_G(g)+b over a product domain, with supplied univariate functions.
- **source:** D §7 / R99 §§2–3
- **status:** EXPLICIT_CONDITIONAL_PREMISE

## Node D:SEPARABLE

- **kind:** THEOREM
- **label:** Path effect independent of other-path context
- **statement:** z(q1,o,g)-z(q0,o,g)=f_Q(q1)-f_Q(q0); this imposes no linear response shape and alone gives no tight off-grid error bound.
- **source:** D §7 / R99 §§3–4
- **status:** MANUAL_CONDITIONAL_PASS

## Node D:ACTUAL_CHANGE

- **kind:** ASSUMPTION
- **label:** Grounded actual comparison
- **statement:** Two actual process tokens are independently admitted; a common complete structural signature is fixed; an installed continuation-control relation differs in a way that makes complete organizations genuinely nonisomorphic, not merely renamed/relabelled coordinates.
- **source:** D §11 / A C1
- **status:** EXPLICIT_CONDITIONAL_PREMISE

## Node D:UCT_INTERPRETATION

- **kind:** THEOREM
- **label:** Conditional complete experiential-type distinction
- **statement:** Under A:C1 and the grounded nonisomorphic actual comparison, complete experiential types differ. No scalar richness, valence, familiar feeling label or unique subject follows.
- **source:** D §11 / A C1-OI
- **status:** MANUAL_CONDITIONAL_PASS

## Node R131:PROBES

- **kind:** DEFINITION
- **label:** Finite exact expectation interface
- **statement:** Z finite, n>=2; fixed real f_1,...,f_m; A rows are 1^T,f_1^T,...,f_m^T; y(mu)=A mu for all mu in Delta(Z).
- **source:** R131 R131_Probe_Completeness_Theorem.md §2
- **status:** EXPLICIT_CONDITIONAL_PREMISE
- **scope:** Finite outcome set; fixed exact scalar expectation probes and normalization; universal identification over the full probability simplex. Not complete physical or experiential identification.

## Node R131:TARGET_SPAN

- **kind:** THEOREM
- **label:** Target expectation identifiable iff in probe span
- **statement:** For fixed g, E_mu g factors through A mu on all Delta(Z) iff g belongs to row(A). This is not an iff for argmax identification.
- **source:** R131 R131_Probe_Completeness_Theorem.md §3
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite outcome set; fixed exact scalar expectation probes and normalization; universal identification over the full probability simplex. Not complete physical or experiential identification.

## Node R131:COMPLETE_LAW

- **kind:** THEOREM
- **label:** Complete law rank criterion and sharp ambiguous fiber
- **statement:** A mu identifies all mu in Delta(Z) iff rank(A)=n; if deficient, some u,v have Au=Av and TV(u,v)=1. At least n-1 scalar probes are needed in this interface class.
- **source:** R131 R131_Probe_Completeness_Theorem.md §4
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite outcome set; fixed exact scalar expectation probes and normalization; universal identification over the full probability simplex. Not complete physical or experiential identification.

## Node R131:FULL_RANK

- **kind:** ASSUMPTION
- **label:** Separating probe family
- **statement:** rank(A)=n for the fixed probe matrix.
- **source:** R131 R131_Probe_Completeness_Theorem.md §5
- **status:** EXPLICIT_CONDITIONAL_PREMISE
- **scope:** Finite outcome set; fixed exact scalar expectation probes and normalization; universal identification over the full probability simplex. Not complete physical or experiential identification.

## Node R131:DEFICIENT

- **kind:** ASSUMPTION
- **label:** Nonseparating probe family
- **statement:** rank(A)<n for the fixed probe matrix.
- **source:** R131 R131_Probe_Completeness_Theorem.md §5
- **status:** EXPLICIT_CONDITIONAL_PREMISE
- **scope:** Finite outcome set; fixed exact scalar expectation probes and normalization; universal identification over the full probability simplex. Not complete physical or experiential identification.

## Node R131:KERNEL

- **kind:** DEFINITION
- **label:** Fixed controlled finite summary
- **statement:** Finite S; p:S->Z onto; total Markov kernels K_a for declared common operation ports and time grain; mu_s,a=p_*K_a(s,.).
- **source:** R131 R131_Probe_Completeness_Theorem.md §5
- **status:** EXPLICIT_CONDITIONAL_PREMISE
- **scope:** State, action and time semantics are fixed. All states and all allowed total operations, not only one observed trajectory; enabledness for partial operations is outside this theorem.

## Node R131:PROBE_MATCH

- **kind:** ASSUMPTION
- **label:** Within-fiber expectation agreement
- **statement:** For every s,t,a,i with p(s)=p(t), E_mu_s,a f_i = E_mu_t,a f_i.
- **source:** R131 R131_Probe_Completeness_Theorem.md §5
- **status:** EXPLICIT_CONDITIONAL_PREMISE
- **scope:** Finite outcome set; fixed exact scalar expectation probes and normalization; universal identification over the full probability simplex. Not complete physical or experiential identification.

## Node R131:CLOSURE

- **kind:** THEOREM
- **label:** Separating tests certify controlled closure
- **statement:** Under full rank, within-fiber probe agreement is equivalent to a well-defined kernel bar K_a satisfying p_*K_a(s,.)=bar K_a(p(s),.) for all s,a.
- **source:** R131 R131_Probe_Completeness_Theorem.md §5
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite fixed model, all states and operations. This does not certify interventions outside the family, hidden-state-dependent policy equivalence, complete organization or a subject.

## Node R131:BLIND_KERNEL

- **kind:** THEOREM
- **label:** Maximally different hidden transition laws
- **statement:** For every deficient probe interface there exists a kernel on Z x {0,1}, with persistent b and next-Z law u_b, whose probe expectations all agree while the summary p(z,b)=z fails closure and within-fiber next laws have TV=1.
- **source:** R131 R131_Probe_Completeness_Theorem.md §5
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Existential construction over the full state domain. Rank deficiency does not force every given kernel to fail closure. Agreement is of measured expectations, not all unmeasured output laws.

## Node R131:DECISION_SETUP

- **kind:** ASSUMPTION
- **label:** Matched decision witness
- **statement:** A fair hidden b selects disjoint u,v; observer sees only common A u=A v before acting; action does not alter the outcome; same actions/payoffs h_0=1_supp(u), h_1=1_complement and no side information.
- **source:** R131 R131_Probe_Completeness_Theorem.md §6
- **status:** EXPLICIT_CONDITIONAL_PREMISE
- **scope:** Finite outcome set; fixed exact scalar expectation probes and normalization; universal identification over the full probability simplex. Not complete physical or experiential identification.

## Node R131:DECISION_GAP

- **kind:** THEOREM
- **label:** Exact hidden decision value gap
- **statement:** In the declared decision witness, context-informed optimal score is 1, every probe-only randomized policy scores 1/2, and the gap is 1/2.
- **source:** R131 R131_Probe_Completeness_Theorem.md §6
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Specified fair prior, two bounded indicator payoffs and same action set. Possible loss, not universal task loss or the numerical value of D separate witness.

## Node R131:LEFT_INVERSE

- **kind:** ASSUMPTION
- **label:** Calibrated stable inversion premise
- **statement:** Fix L with LA=I_n; B drops the normalization column of L. True probe expectation differences have sup norm at most epsilon.
- **source:** R131 R131_Probe_Completeness_Theorem.md §7
- **status:** EXPLICIT_CONDITIONAL_PREMISE
- **scope:** Finite outcome set; fixed exact scalar expectation probes and normalization; universal identification over the full probability simplex. Not complete physical or experiential identification.

## Node R131:ROBUST

- **kind:** THEOREM
- **label:** Conditioned TV error envelope
- **statement:** TV(mu,nu)<=min(1,||B||_(infty->1) epsilon/2). Statistical confidence requires a separate justified expectation-error bound.
- **source:** R131 R131_Probe_Completeness_Theorem.md §7
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite outcome set; fixed exact scalar expectation probes and normalization; universal identification over the full probability simplex. Not complete physical or experiential identification.

## Node R132:SLOT_MODEL

- **kind:** DEFINITION
- **label:** Unit-slot common realization model
- **statement:** Tasks I have eligible slot sets N(i); admissible partial executions are exactly injective assignments on subsets of I. For actual use, matching must faithfully represent the entire within-horizon execution constraint.
- **source:** R132_Common_Realization_Theorems.md §2
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** One fixed horizon/boundary/port model; unit tasks, one indivisible slot per served task, one task per slot, no other constraints. Actual implementation needs independent adequacy; no general multi-resource scheduling or experience criterion.

## Node R132:HALL

- **kind:** THEOREM
- **label:** Hall common-witness certificate
- **statement:** All requested tasks have a common schedule iff |N(J)|>=|J| for every subset J of I. This is Hall's classical theorem.
- **source:** R132_Common_Realization_Theorems.md §3
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** One fixed horizon/boundary/port model; unit tasks, one indivisible slot per served task, one task per slot, no other constraints. Actual implementation needs independent adequacy; no general multi-resource scheduling or experience criterion.

## Node R132:DEFICIT

- **kind:** THEOREM
- **label:** Exact resource deficit and completion bound
- **statement:** delta=max_J(|J|-|N(J)|); maximum completed tasks=n-delta. Every randomized legal schedule satisfies sum_i P(X_i=1)<=n-delta and min_(i in J)P(X_i=1)<=|N(J)|/|J| for nonempty J.
- **source:** R132_Common_Realization_Theorems.md §3
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** One fixed horizon/boundary/port model; unit tasks, one indivisible slot per served task, one task per slot, no other constraints. Actual implementation needs independent adequacy; no general multi-resource scheduling or experience criterion. X_i means valid scheduled completion, not correctness by guessing.

## Node R132:UNIFORM_BOTTLENECK

- **kind:** MODEL
- **label:** n tasks share n-1 universal slots
- **statement:** n>=3; all task neighbor sets equal the same n-1 slots. Randomized protocol uniformly omits one task and executes the rest.
- **source:** R132_Common_Realization_Theorems.md §4
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** One fixed horizon/boundary/port model; unit tasks, one indivisible slot per served task, one task per slot, no other constraints. Actual implementation needs independent adequacy; no general multi-resource scheduling or experience criterion.

## Node R132:HIGH_ORDER

- **kind:** THEOREM
- **label:** All proper coalitions and high marginals do not certify joint success
- **statement:** In the specified bottleneck, every proper task subset is executable, the full set is not; each task completes with probability 1-1/n while all-at-once completion has probability zero.
- **source:** R132_Common_Realization_Theorems.md §4
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** One fixed horizon/boundary/port model; unit tasks, one indivisible slot per served task, one task per slot, no other constraints. Actual implementation needs independent adequacy; no general multi-resource scheduling or experience criterion. Existential family, not a statement about every high-accuracy system.

## Node R132:PARTIAL_MODEL

- **kind:** DEFINITION
- **label:** Finite partial stochastic interface
- **statement:** S,O finite nonempty; U finite; enabled E(s); fixed kernel L_a(s;s_prime,o) normalized only for a in E(s); p:S->Z onto. Scheduler selection is fixed or remains explicitly indexed.
- **source:** R132_Common_Realization_Theorems.md §5
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite nonempty S,O, finite U; fixed scheduler/ports/time; all represented states. Preserve exact enabledness and joint next-summary/output law. Not trace-only equivalence, empirical identification, an actual complete type, or a unique subject.

## Node R132:PARTIAL_CLOSURE

- **kind:** THEOREM
- **label:** Enabledness plus joint law is exact quotient criterion
- **statement:** An exact p quotient exists iff equal-summary states have equal enabled menus and, for every enabled action, equal joint p(next-state)/output laws. Shared summary/output-history policies preserve finite-horizon histories, halting at empty menus.
- **source:** R132_Common_Realization_Theorems.md §6
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite nonempty S,O, finite U; fixed scheduler/ports/time; all represented states. Preserve exact enabledness and joint next-summary/output law. Not trace-only equivalence, empirical identification, an actual complete type, or a unique subject. Policy preservation excludes hidden-state-dependent policies.

## Node R132:PROBE_SETUP

- **kind:** ASSUMPTION
- **label:** Joint separating probes and common enabled menu
- **statement:** In the partial model, |Z x O|>=2; fix full-column-rank exact expectation probes with normalization on Z x O; menus agree within every p fiber.
- **source:** R132_Common_Realization_Theorems.md §6
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite nonempty S,O, finite U; fixed scheduler/ports/time; all represented states. Preserve exact enabledness and joint next-summary/output law. Not trace-only equivalence, empirical identification, an actual complete type, or a unique subject. Finite statistical estimates are not exact expectations. Singleton outcome alphabet is handled directly by the closure theorem.

## Node R132:PROBE_CERTIFICATE

- **kind:** THEOREM
- **label:** R131 probes certify the law half of the partial interface
- **statement:** Under PROBE_SETUP, within-fiber matching of all next-summary/output probe expectations for every enabled action is equivalent to exact interface closure.
- **source:** R132_Common_Realization_Theorems.md §6
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite nonempty S,O, finite U; fixed scheduler/ports/time; all represented states. Preserve exact enabledness and joint next-summary/output law. Not trace-only equivalence, empirical identification, an actual complete type, or a unique subject. Separate state/output marginal probes can miss their dependence.

## Node R132:WITNESS_MODELS

- **kind:** MODEL
- **label:** Independent failures of menu and joint-law preservation
- **statement:** Availability: hidden s0/s1 have 2/3 universal slots for 3 tasks, constant summary/output and self transitions. Joint law: S={0,1}^2, p(x,b)=x, one common action, x_next=U, b_next=b, output=U XOR b with fresh fair U.
- **source:** R132_Common_Realization_Theorems.md §7
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite nonempty S,O, finite U; fixed scheduler/ports/time; all represented states. Preserve exact enabledness and joint next-summary/output law. Not trace-only equivalence, empirical identification, an actual complete type, or a unique subject. Specified mathematical examples; parity idea already in R128/PLT.

## Node R132:TWO_OBSTRUCTIONS

- **kind:** THEOREM
- **label:** Availability and joint-law conditions are independently necessary
- **statement:** The availability model agrees on every common enabled response but has different full-task enabledness. The joint-law model has the same menu and separate next-state/output marginals but within-fiber joint TV=1.
- **source:** R132_Common_Realization_Theorems.md §7
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite nonempty S,O, finite U; fixed scheduler/ports/time; all represented states. Preserve exact enabledness and joint next-summary/output law. Not trace-only equivalence, empirical identification, an actual complete type, or a unique subject.

## Node R132:REFINEMENT_SETUP

- **kind:** ASSUMPTION
- **label:** Fixed retained partition and exact iterative signatures
- **statement:** A fixed initial partition P0 of finite S is given. Split each block by E(s) and all L_a(s;B,o) for current blocks B and outputs o, with the same fixed partial model throughout.
- **source:** R132_Common_Realization_Theorems.md §8
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite nonempty S,O, finite U; fixed scheduler/ports/time; all represented states. Preserve exact enabledness and joint next-summary/output law. Not trace-only equivalence, empirical identification, an actual complete type, or a unique subject. No model uncertainty or representative-dependent support-only omission.

## Node R132:REFINEMENT

- **kind:** THEOREM
- **label:** Unique coarsest exact retained-interface refinement
- **statement:** Signature splitting terminates after at most |S|-|P0| strict steps at the unique coarsest stable refinement of P0 preserving menus and joint block/output probabilities.
- **source:** R132_Common_Realization_Theorems.md §8
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite nonempty S,O, finite U; fixed scheduler/ports/time; all represented states. Preserve exact enabledness and joint next-summary/output law. Not trace-only equivalence, empirical identification, an actual complete type, or a unique subject. Compression can be trivial; this is not a minimal physical circuit or model-independent state.

## Node R133:PERSISTENT_MODEL

- **kind:** DEFINITION
- **label:** Persistent finite mechanism and observable-history policy
- **statement:** Augment the partial kernel state to (m,s) with immutable m. For support B use common menu A(B)=intersection E_m(s) and successor support B_(a,o)={(m,s_prime):exists (m,s) in B with K_m(s,a;s_prime,o)>0}.
- **source:** R133_Observable_Common_Control.md §2
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite candidate models and finite states/actions/outputs; one persistent hidden model, known family, fixed sufficient state/scheduler/ports; controller observes actions/outputs only, no free menu/model oracle; universally executable actions; closed goal or persistent success flag; fixed finite horizon. Mathematical model, not an actual complete organization or experience gate.

## Node R133:SUPPORT

- **kind:** THEOREM
- **label:** Exact model-indexed support invariant
- **statement:** Recursively updating B along a feasible finite observable action/output history gives exactly its attainable current (m,s) pairs without repasting model choices.
- **source:** R133_Observable_Common_Control.md §2
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite candidate models and finite states/actions/outputs; one persistent hidden model, known family, fixed sufficient state/scheduler/ports; controller observes actions/outputs only, no free menu/model oracle; universally executable actions; closed goal or persistent success flag; fixed finite horizon. Mathematical model, not an actual complete organization or experience gate. No Bayesian probabilities or quantitative value sufficiency is asserted.

## Node R133:COMMON_POLICY

- **kind:** THEOREM
- **label:** Bounded-horizon probability-one common-policy certificate
- **statement:** W_0(B)=[B subset G]; W_(h+1)(B)=[B subset G] OR [exists a in A(B), all nonempty B_(a,o) satisfy W_h]. W_H(B) iff one observation-history policy succeeds from every x in B within H transitions with probability one. Deterministic (B,h) policies suffice even when randomization is allowed.
- **source:** R133_Observable_Common_Control.md §3
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite candidate models and finite states/actions/outputs; one persistent hidden model, known family, fixed sufficient state/scheduler/ports; controller observes actions/outputs only, no free menu/model oracle; universally executable actions; closed goal or persistent success flag; fixed finite horizon. Mathematical model, not an actual complete organization or experience gate. Not a claim about infinite-horizon almost-sure winning or success probabilities below one.

## Node R133:DECISION_MODEL

- **kind:** DEFINITION
- **label:** One-shot successful-action family and observed cells
- **statement:** Each m has nonempty G_m subset U of enabled probability-one successful actions. A deterministic fixed observation h:M->Y arrives without changing this decision problem.
- **source:** R133_Observable_Common_Control.md §4
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite one-shot candidate/action family with nonempty good-action sets; success is probability one including enabledness; observation before commitment preserves states, actions and payoff. No full model identification, physical sensor, actual subjective report or quantitative experience conclusion.

## Node R133:CELL_ACTION

- **kind:** THEOREM
- **label:** Each observed cell must share a successful action
- **statement:** A successful observation-based decision rule exists iff each nonempty h fiber has nonempty intersection of its G_m sets. Probability-one randomization cannot repair an empty intersection.
- **source:** R133_Observable_Common_Control.md §4
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite one-shot candidate/action family with nonempty good-action sets; success is probability one including enabledness; observation before commitment preserves states, actions and payoff. No full model identification, physical sensor, actual subjective report or quantitative experience conclusion. Pairwise intersections are not sufficient for a larger cell.

## Node R133:ENCODER

- **kind:** ASSUMPTION
- **label:** Freely selectable ideal deterministic encoder
- **statement:** For the one-shot decision family, any deterministic h(m) may be selected; count used messages; no side information or sensing cost. The encoder must be supplied for physical application.
- **source:** R133_Observable_Common_Control.md §4
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite one-shot candidate/action family with nonempty good-action sets; success is probability one including enabledness; observation before commitment preserves states, actions and payoff. No full model identification, physical sensor, actual subjective report or quantitative experience conclusion. Ideal access to m is a premise, not an inferred physical ability.

## Node R133:MESSAGE_COVER

- **kind:** THEOREM
- **label:** Minimum ideal task message count equals an action cover
- **statement:** Let C_a={m:a in G_m}. The minimum used-message count is tau=min{|V|:union_(a in V) C_a=M}; minimum fixed-length bits are ceil(log2 tau).
- **source:** R133_Observable_Common_Control.md §4
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite one-shot candidate/action family with nonempty good-action sets; success is probability one including enabledness; observation before commitment preserves states, actions and payoff. No full model identification, physical sensor, actual subjective report or quantitative experience conclusion. Requires ENCODER. No noisy channel, entropy, variable-length coding, adaptive protocol or sensor construction is covered.

## Node R133:AVOIDANCE_MODEL

- **kind:** MODEL
- **label:** Avoid the one action forbidden by the hidden mechanism
- **statement:** M=U={1,...,n}, n>=2, G_m=U minus {m}; initial observation is constant. An ideal yes/no observation of m=1 is also considered.
- **source:** R133_Observable_Common_Control.md §5
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite one-shot candidate/action family with nonempty good-action sets; success is probability one including enabledness; observation before commitment preserves states, actions and payoff. No full model identification, physical sensor, actual subjective report or quantitative experience conclusion.

## Node R133:AVOIDANCE

- **kind:** THEOREM
- **label:** High robust success, no perfect blind action, and one sufficient bit
- **statement:** In AVOIDANCE_MODEL, every proper candidate subset has a common good action and the whole family has none; randomized blind minimax success is 1-1/n. Exactly two ideal messages suffice for perfect task success, whereas exact model identification requires n.
- **source:** R133_Observable_Common_Control.md §5
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite one-shot candidate/action family with nonempty good-action sets; success is probability one including enabledness; observation before commitment preserves states, actions and payoff. No full model identification, physical sensor, actual subjective report or quantitative experience conclusion. Mutually exclusive candidate mechanisms, not simultaneous tasks; n=100 is a specified example, not measured AI accuracy.

## Node R133:NONUNIQUE

- **kind:** THEOREM
- **label:** A task need not have a unique coarsest sufficient observation partition
- **statement:** For the avoidance family at n=3, each of the three two-cell partitions is successful; all are incomparable and their only common coarsening is the failing one-cell partition.
- **source:** R133_Observable_Common_Control.md §5
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite one-shot candidate/action family with nonempty good-action sets; success is probability one including enabledness; observation before commitment preserves states, actions and payoff. No full model identification, physical sensor, actual subjective report or quantitative experience conclusion. Does not contradict R132 coarsest stable refinement for a fixed full interface.

## Node R133:PROBE_MODELS

- **kind:** MODEL
- **label:** Preserving, uninformative and destructive diagnostic interfaces
- **statement:** Two persistent models require opposite terminal actions. Each probe consumes one step; preserving probe reports m and preserves choices; uninformative probe reports a common symbol with no effect; destructive probe reports m but enters absorbing failure. Terminal choices consume one step.
- **source:** R133_Observable_Common_Control.md §6
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite candidate models and finite states/actions/outputs; one persistent hidden model, known family, fixed sufficient state/scheduler/ports; controller observes actions/outputs only, no free menu/model oracle; universally executable actions; closed goal or persistent success flag; fixed finite horizon. Mathematical model, not an actual complete organization or experience gate. Mathematical devices only. Probing is optional unless explicitly conditioned on it.

## Node R133:PROBE_BOUNDARY

- **kind:** THEOREM
- **label:** Task information needs remaining successful action opportunities
- **statement:** For the specified two-model probe systems at H=2, preserving diagnosis gives worst-case success one; uninformative and optional destructive probes leave optimal randomized worst-case success one half. A destructive probe conditional on use has value zero; the preserving diagnostic cannot assure success at H=1.
- **source:** R133_Observable_Common_Control.md §6
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite candidate models and finite states/actions/outputs; one persistent hidden model, known family, fixed sufficient state/scheduler/ports; controller observes actions/outputs only, no free menu/model oracle; universally executable actions; closed goal or persistent success flag; fixed finite horizon. Mathematical model, not an actual complete organization or experience gate. Free extra information in C:P7 is a different fixed decision problem; finite uninformative probes cannot improve the one-half bound.

## Node R133:SWITCH_MODEL

- **kind:** MODEL
- **label:** Two persistent forced traces and an at-least-one-success target
- **statement:** One fixed model emits (1,0); the other emits (0,1) under the same forced two-stage protocol. The target is at least one 1, tracked by a persistent success flag.
- **source:** R133_Observable_Common_Control.md §7
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite candidate models and finite states/actions/outputs; one persistent hidden model, known family, fixed sufficient state/scheduler/ports; controller observes actions/outputs only, no free menu/model oracle; universally executable actions; closed goal or persistent success flag; fixed finite horizon. Mathematical model, not an actual complete organization or experience gate.

## Node R133:PERSISTENCE

- **kind:** THEOREM
- **label:** Stagewise envelope can fabricate an impossible failure trace
- **statement:** Both persistent traces satisfy the target, while the Cartesian product of stagewise output possibilities contains (0,0). After first output 0 the exact support retains only the model whose next output is 1.
- **source:** R133_Observable_Common_Control.md §7
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite candidate models and finite states/actions/outputs; one persistent hidden model, known family, fixed sufficient state/scheduler/ports; controller observes actions/outputs only, no free menu/model oracle; universally executable actions; closed goal or persistent success flag; fixed finite horizon. Mathematical model, not an actual complete organization or experience gate. Conservative model switching need not be exact; some other envelopes may be exact. No prior over models is required.

## Node R134:QUANT_MODEL

- **kind:** DEFINITION
- **label:** Persistent model-indexed success profiles
- **statement:** For each legal pure observable policy tree, keep the vector v(x)=P_x(success by H) for every initial x in B. Mixed policies are private distributions on complete pure trees; robust value is max_policy min_x v(x).
- **source:** R134_Quantitative_Control.md §2
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** R133 finite persistent model and joint action/output kernels, sufficient state including resources/clock, common enabled actions, closed goal and fixed finite horizon. Same observable policy across all initial model/state pairs; private randomness independent of the hidden mechanism, retained memory permitted. Nature cannot choose after seeing the private seed. No actual complete-type or experience inference. A known state distribution inside each model would define an explicitly averaged alternative, not this worst-initial-state objective.

## Node R134:VECTOR_RECURSION

- **kind:** THEOREM
- **label:** Exact attainable continuation-vector recursion
- **statement:** F_0(B)={1_G restricted to B}; F_(h+1) contains stopping and every common-action backup T_a(w)(x)=sum K(x,a;x_prime,o)w_o(x_prime) with one child vector per output. These are exactly pure-policy profiles; mixed profiles equal conv F_h(B).
- **source:** R134_Quantitative_Control.md §3
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** R133 finite persistent model and joint action/output kernels, sufficient state including resources/clock, common enabled actions, closed goal and fixed finite horizon. Same observable policy across all initial model/state pairs; private randomness independent of the hidden mechanism, retained memory permitted. Nature cannot choose after seeing the private seed. No actual complete-type or experience inference. A set indexed by support is not a claim that a deployed quantitative policy may discard observation history; no efficient compression asserted.

## Node R134:ROBUST_LP

- **kind:** THEOREM
- **label:** Epsilon common-control certificate and minimax dual
- **statement:** With pure profiles as columns of A, success >=1-epsilon is feasible iff A lambda >=(1-epsilon)1 for some simplex lambda. Optimal robust value equals min_(q in simplex B) max_j q dot v_j.
- **source:** R134_Quantitative_Control.md §4
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** R133 finite persistent model and joint action/output kernels, sufficient state including resources/clock, common enabled actions, closed goal and fixed finite horizon. Same observable policy across all initial model/state pairs; private randomness independent of the hidden mechanism, retained memory permitted. Nature cannot choose after seeing the private seed. No actual complete-type or experience inference. Dual q is a proof weighting, not a supplied prior; standard finite LP/minimax duality.

## Node R134:ZERO_ERROR

- **kind:** THEOREM
- **label:** Value-one corner recovers R133 purification
- **statement:** Robust value one iff a pure profile is one at every coordinate, iff R133 COMMON_POLICY holds. Below one, randomization may improve the best guaranteed success.
- **source:** R134_Quantitative_Control.md §4
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** R133 finite persistent model and joint action/output kernels, sufficient state including resources/clock, common enabled actions, closed goal and fixed finite horizon. Same observable policy across all initial model/state pairs; private randomness independent of the hidden mechanism, retained memory permitted. Nature cannot choose after seeing the private seed. No actual complete-type or experience inference. Positive-mass mixture columns must all be one to attain an all-one vector.

## Node R134:SCALAR_MODELS

- **kind:** MODEL
- **label:** Blind opposite actions and a same-support noisy signal
- **statement:** Blind terminal action profiles are (1,0),(0,1). In a second case the free binary signal laws are (3/4,1/4) and (1/4,3/4), followed by the action naming the model; both outputs leave both models possible.
- **source:** R134_Quantitative_Control.md §5
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** R133 finite persistent model and joint action/output kernels, sufficient state including resources/clock, common enabled actions, closed goal and fixed finite horizon. Same observable policy across all initial model/state pairs; private randomness independent of the hidden mechanism, retained memory permitted. Nature cannot choose after seeing the private seed. No actual complete-type or experience inference.

## Node R134:SCALAR_FAILURE

- **kind:** THEOREM
- **label:** Scalar collapse can invent or discard control capability
- **statement:** Coordinatewise maxima of blind profiles fabricate unattainable (1,1); half-half mixing instead guarantees 1/2. In the noisy-signal case, using observed output attains (3/4,3/4), while any terminal policy retaining only identical support/time guarantees at most 1/2.
- **source:** R134_Quantitative_Control.md §5
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** R133 finite persistent model and joint action/output kernels, sufficient state including resources/clock, common enabled actions, closed goal and fixed finite horizon. Same observable policy across all initial model/state pairs; private randomness independent of the hidden mechanism, retained memory permitted. Nature cannot choose after seeing the private seed. No actual complete-type or experience inference. Counterexamples to scalar/support-only quantitative reduction, not to R133 probability-one theorem.

## Node R134:PROBE_MODEL

- **kind:** DEFINITION
- **label:** Weighted binary diagnostic and opportunity model
- **statement:** Probe law P_m(y) and conditional correct-completion survival r_m(y) give a_y=P_0(y)r_0(y), b_y=P_1(y)r_1(y). A randomized decision d_y produces success pair (sum a_y d_y, sum b_y(1-d_y)).
- **source:** R134_Quantitative_Control.md §6
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Two fixed hidden mechanisms, finite probe transcript, terminal actions correct only for their corresponding mechanism; no later useful signal. Weighted transcript masses include specified conditional opportunity survival. Mathematical task success, not phenomenology, physical sensor validation or generic acquisition utility. Survival is not an additional observable decision signal unless included in Y.

## Node R134:PROBE_DUAL

- **kind:** THEOREM
- **label:** Exact weighted binary probe guarantee
- **statement:** Forced-probe robust success equals min_(0<=q<=1) F(q), F(q)=sum_y max(q a_y,(1-q)b_y). Endpoints and q=b_y/(a_y+b_y) suffice to find this minimum.
- **source:** R134_Quantitative_Control.md §6
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Two fixed hidden mechanisms, finite probe transcript, terminal actions correct only for their corresponding mechanism; no later useful signal. Weighted transcript masses include specified conditional opportunity survival. Mathematical task success, not phenomenology, physical sensor validation or generic acquisition utility. One fixed probe followed by one terminal choice; not a solution of unrestricted adaptive sensing.

## Node R134:COMMON_SURVIVAL

- **kind:** ASSUMPTION
- **label:** Model-independent constant surviving opportunity
- **statement:** In PROBE_MODEL, r_m(y)=rho in [0,1] for every mechanism and transcript.
- **source:** R134_Quantitative_Control.md §6
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Two fixed hidden mechanisms, finite probe transcript, terminal actions correct only for their corresponding mechanism; no later useful signal. Weighted transcript masses include specified conditional opportunity survival. Mathematical task success, not phenomenology, physical sensor validation or generic acquisition utility. This multiplicative completion probability is not a generic additive money, energy or fitness cost.

## Node R134:TV_OPPORTUNITY

- **kind:** THEOREM
- **label:** Distinguishability times opportunity gives a necessary upper bound
- **statement:** Generally V_probe <=(sum a+sum b+norm1(a-b))/4. Under COMMON_SURVIVAL, V_probe <=rho(1+TV(P_0,P_1))/2; tight for symmetric binary errors, not every pair. Equal TV can give unequal robust values.
- **source:** R134_Quantitative_Control.md §6
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Two fixed hidden mechanisms, finite probe transcript, terminal actions correct only for their corresponding mechanism; no later useful signal. Weighted transcript masses include specified conditional opportunity survival. Mathematical task success, not phenomenology, physical sensor validation or generic acquisition utility. Equal-prior average discrimination must not be substituted for the minimum over mechanisms; necessary epsilon bounds need not be sufficient.

## Node R134:OPTIONAL_MODEL

- **kind:** ASSUMPTION
- **label:** Immediate blind actions remain available before a probe
- **statement:** In the binary task, before observing any signal the policy may choose immediate profiles (1,0),(0,1) or the specified probe, and privately mix these choices. Blind actions avoid probe-induced opportunity loss.
- **source:** R134_Quantitative_Control.md §7
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Two fixed hidden mechanisms, finite probe transcript, terminal actions correct only for their corresponding mechanism; no later useful signal. Weighted transcript masses include specified conditional opportunity survival. Mathematical task success, not phenomenology, physical sensor validation or generic acquisition utility. No private coin revealed to nature before mechanism selection; no later extra choice class omitted.

## Node R134:OPTIONAL_PROBE

- **kind:** THEOREM
- **label:** Optional probing requires convexifying full profiles before minimax
- **statement:** Optional robust value is min_q max(q,1-q,F(q)). This may strictly exceed max(1/2,V_probe).
- **source:** R134_Quantitative_Control.md §7
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Two fixed hidden mechanisms, finite probe transcript, terminal actions correct only for their corresponding mechanism; no later useful signal. Weighted transcript masses include specified conditional opportunity survival. Mathematical task success, not phenomenology, physical sensor validation or generic acquisition utility. Requires OPTIONAL_MODEL; scalar robust values of separate strategy classes are insufficient for their randomized union.

## Node R134:ASYM_MODEL

- **kind:** MODEL
- **label:** Asymmetric diagnostic with uniform opportunity survival
- **statement:** P_0=(1,0), P_1=(1/2,1/2); probe survival is the same rho in [0,1] for both mechanisms; immediate blind actions remain available.
- **source:** R134_Quantitative_Control.md §7
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Two fixed hidden mechanisms, finite probe transcript, terminal actions correct only for their corresponding mechanism; no later useful signal. Weighted transcript masses include specified conditional opportunity survival. Mathematical task success, not phenomenology, physical sensor validation or generic acquisition utility.

## Node R134:MIXING_WITNESS

- **kind:** THEOREM
- **label:** An individually inferior probe can improve a randomized robust plan
- **statement:** In ASYM_MODEL, forced value=2rho/3; optional value=max(1/2,2rho/(2+rho)). For 2/3<rho<3/4 probing alone is inferior, while optimal optional mixing improves on blind value 1/2. At rho=7/10 the exact optimum is 14/27, attained with probe probability 20/27 and dual weight q=13/27.
- **source:** R134_Quantitative_Control.md §7
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Two fixed hidden mechanisms, finite probe transcript, terminal actions correct only for their corresponding mechanism; no later useful signal. Weighted transcript masses include specified conditional opportunity survival. Mathematical task success, not phenomenology, physical sensor validation or generic acquisition utility. Specified family and order of play only; no historical novelty or measured AI/biological performance claim.

## Node R135:PROFILE_PAIR

- **kind:** DEFINITION
- **label:** Comparable success profiles and directional guarantee loss
- **statement:** G(C)={b in [0,1]^n: some v in C dominates b}; h_C(q)=max_v q dot v for q in Delta_n including zero weights; delta(C->D)=max_v min_w max_i(v_i-w_i)_+.
- **source:** R135_Capability_Preservation.md §2
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Nonempty compact convex C,D in [0,1]^n; identical named evaluation coordinates, tasks, time, resources and observation protocol; one policy across coordinates, permitted independent private mixtures. Mathematical task comparison; no actual organization or physical translator inferred. For each source profile there is one target profile, not one policy per coordinate.

## Node R135:DEFICIENCY

- **kind:** THEOREM
- **label:** Exact weighted-optimum certificate for guarantee loss
- **statement:** delta(C->D)=max_(q in Delta_n)[h_C(q)-h_D(q)]_+.
- **source:** R135_Capability_Preservation.md §3
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Nonempty compact convex C,D in [0,1]^n; identical named evaluation coordinates, tasks, time, resources and observation protocol; one policy across coordinates, permitted independent private mixtures. Mathematical task comparison; no actual organization or physical translator inferred. Standard convex minimax/support-function argument; no historical priority claim.

## Node R135:GUARANTEE_EQ

- **kind:** THEOREM
- **label:** All nonnegative weighted optima characterize the guarantee region
- **statement:** G(C) subset G(D) iff delta(C->D)=0 iff h_C(q)<=h_D(q) for all q in Delta_n. Equality of guarantee regions iff equality of all such weighted optima.
- **source:** R135_Capability_Preservation.md §3
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Nonempty compact convex C,D in [0,1]^n; identical named evaluation coordinates, tasks, time, resources and observation protocol; one policy across coordinates, permitted independent private mixtures. Mathematical task comparison; no actual organization or physical translator inferred. Convexity cannot be silently dropped if randomization is unavailable.

## Node R135:VALUE_BOUND

- **kind:** THEOREM
- **label:** Monotone value transfer and composable directional errors
- **statement:** delta(C->D)<=epsilon transfers thresholds after clipping b-epsilon 1 and bounds sup_C F <=sup_D F+L epsilon for every monotone L-Lipschitz F. delta(C->E)<=delta(C->D)+delta(D->E) for another comparable E.
- **source:** R135_Capability_Preservation.md §4
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Nonempty compact convex C,D in [0,1]^n; identical named evaluation coordinates, tasks, time, resources and observation protocol; one policy across coordinates, permitted independent private mixtures. Mathematical task comparison; no actual organization or physical translator inferred. Lipschitz norm is the maximum norm; signed/nonmonotone diagnostics and exact named-policy distributions are not covered.

## Node R135:HIERARCHY_MODELS

- **kind:** MODEL
- **label:** Two finite comparisons separating scalar, guarantee and profile equality
- **statement:** C1=conv{(0,0),(1,0),(0,1)}, D1=conv{(0,0),(1/2,1/2)}; C2=conv{(0,0),(1,1)}, D2=conv{(0,0),(1,1),(1,0)}.
- **source:** R135_Capability_Preservation.md §5
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Nonempty compact convex C,D in [0,1]^n; identical named evaluation coordinates, tasks, time, resources and observation protocol; one policy across coordinates, permitted independent private mixtures. Mathematical task comparison; no actual organization or physical translator inferred. Explicit mathematical profiles, not actual brain or AI realizations.

## Node R135:HIERARCHY

- **kind:** THEOREM
- **label:** Equal robust values and equal guarantee regions preserve different amounts
- **statement:** C1,D1 both have robust value 1/2, but delta(C1->D1)=1/2 and reverse loss zero. C2,D2 have identical square guarantee regions/all nonnegative weighted optima, yet only D2 contains exact profile (1,0).
- **source:** R135_Capability_Preservation.md §5
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Nonempty compact convex C,D in [0,1]^n; identical named evaluation coordinates, tasks, time, resources and observation protocol; one policy across coordinates, permitted independent private mixtures. Mathematical task comparison; no actual organization or physical translator inferred. These examples separate selected mathematical summaries; they do not exhibit actual experiential noninjectivity.

## Node R135:SIMULATION_SETUP

- **kind:** ASSUMPTION
- **label:** Uniform joint-law and executable-action abstraction contract
- **statement:** For every represented m,s,a, TV((alpha_m,id)_*K_m(s,a),Kbar_m(alpha_m(s),a))<=epsilon; 0<=epsilon<=1. g_m=gbar_m composed with alpha_m; same total actions and observable policy class.
- **source:** R135_Capability_Preservation.md §6
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite persistent paired models and fixed state maps, common total action set (or a declared globally safe subset), same observable-history policy class/private randomness, time and output labels; joint next-mapped-state/output TV <=epsilon uniformly; terminal [0,1] payoff exactly pulled back; paired initial states. Actual port adequacy separately assumed. A finite fit or matching separate marginals does not establish this premise.

## Node R135:POLICY_BOUND

- **kind:** THEOREM
- **label:** Finite-horizon same-policy error bound
- **statement:** Every common observable policy has coordinate error <=beta_H=1-(1-epsilon)^H<=min(1,H epsilon); the uniform terminal-payoff bound is sharp.
- **source:** R135_Capability_Preservation.md §7
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite persistent paired models and fixed state maps, common total action set (or a declared globally safe subset), same observable-history policy class/private randomness, time and output labels; joint next-mapped-state/output TV <=epsilon uniformly; terminal [0,1] payoff exactly pulled back; paired initial states. Actual port adequacy separately assumed. Classical finite-horizon coupling/simulation bound; no uniform small-error claim for unbounded time.

## Node R135:TRANSFER_BOUND

- **kind:** THEOREM
- **label:** Guarantee transfer and selected-policy regret
- **statement:** For pulled-back comparable profile sets both directed losses and robust optimal-value gap are <=beta_H. Copying an abstract eta-optimal policy gives concrete robust success >=V_star-2 beta_H-eta; a particular abstract guarantee loses only beta_H.
- **source:** R135_Capability_Preservation.md §7
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite persistent paired models and fixed state maps, common total action set (or a declared globally safe subset), same observable-history policy class/private randomness, time and output labels; joint next-mapped-state/output TV <=epsilon uniformly; terminal [0,1] payoff exactly pulled back; paired initial states. Actual port adequacy separately assumed. A guarantee certificate and regret relative to an unknown optimum are different quantities; neither implies complete-type equality.

## Node R135:LEGALITY_MODEL

- **kind:** MODEL
- **label:** Rare hidden state with an incompatible action menu
- **statement:** At start only p is enabled; at good only a leads to goal; at bad no non-stop action is enabled; stop is always available and succeeds only at goal. Outputs are constant. K0:p->good; Kdelta:p->(1-delta)good+delta bad. Other rows and pointwise menus agree; H=2.
- **source:** R135_Capability_Preservation.md §8
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Hard legality requires an action enabled at every history-compatible state. Identity state map, common goal payoff, row TV delta. This partial-action model deliberately violates SIMULATION_SETUP.

## Node R135:LEGALITY_JUMP

- **kind:** THEOREM
- **label:** Arbitrarily small kernel perturbations can destroy a hard-legal guarantee
- **statement:** For LEGALITY_MODEL, K0 has value one and Kdelta value zero for every delta>0. If attempting a at bad is explicitly made legal with failure, the changed protocol instead has value 1-delta.
- **source:** R135_Capability_Preservation.md §8
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Support-based legal policy classes can change discontinuously despite pointwise menu equality. Not a counterexample to POLICY_BOUND or to A:U2; not an experience threshold.

## Node R135:ACTUAL_PROFILE

- **kind:** ASSUMPTION
- **label:** Grounded capability map on complete actual types
- **statement:** Actual valid process tokens, a common complete structural signature and fixed grounded tasks/ports/resources/observation rules supply a well-defined guarantee-region map s->G(s) invariant under allowed structural isomorphisms.
- **source:** R135_Capability_Preservation.md §9
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Actual support and complete-type adequacy are independent premises, not certified by finite profile examples, decoder scores or small transition error.

## Node R135:UCT_INTERPRETATION

- **kind:** CONDITIONAL_INTERPRETATION
- **label:** Published identification criteria applied to capability guarantees
- **statement:** Under A:C1 and ACTUAL_PROFILE, different G implies different complete experiential types; G identifies full experiential type iff s->G(s) is injective; a selected coordinate is recoverable iff constant on G-fibers.
- **source:** R135_Capability_Preservation.md §9
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Direct application of published C:P1/P2, not a new constitutive theorem. Equal guarantees alone do not prove experiential equality; no universal noninjectivity on every actual domain asserted. No new U1 gate.

## Node R136:STATIC_SETUP

- **kind:** DEFINITION
- **label:** Fixed one-shot experiments and universal decision comparison
- **statement:** P_theta(x),Q_theta(y) are fixed experiments; V_P(u),V_Q(u) optimize a common finite decision problem after observation with full-support prior p. Translators R(x|y) are independent of theta.
- **source:** R136_Causal_Translation.md §2
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite hidden parameter and signal sets; fixed row-stochastic observation experiments P,Q; one terminal decision after observation; full-support fixed prior; all finite randomized decision rules; no omitted costs, deadlines or side effects. A statistical postprocessor is not a physical organization isomorphism.

## Node R136:BLACKWELL

- **kind:** THEOREM
- **label:** Classical all-decision comparison admits one stochastic translator
- **statement:** P=QR for a common stochastic R iff V_Q(u)>=V_P(u) for every finite decision problem. It suffices to vary all utilities with action set X. Utilities can be normalized to [0,1].
- **source:** R136_Causal_Translation.md §2
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite hidden parameter and signal sets; fixed row-stochastic observation experiments P,Q; one terminal decision after observation; full-support fixed prior; all finite randomized decision rules; no omitted costs, deadlines or side effects. A statistical postprocessor is not a physical organization isomorphism. Classical Blackwell randomization theorem, not a new project theorem. Varying every utility is stronger than reweighting one fixed success-profile family.

## Node R136:STREAM_SETUP

- **kind:** DEFINITION
- **label:** Causal row kernels and uniform path simulation loss
- **statement:** Causal(Y,X) contains stochastic full-path kernels whose output-prefix marginal at time t depends only on y_<=t. d_c(P<-Q)=min_R max_theta TV(P_theta,Q_theta R) over that polytope.
- **source:** R136_Causal_Translation.md §3
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite exogenous path experiments P_theta,Q_theta with common parameter and clock; one causal translator sees only current/past Y and uses private randomness independent of theta and the entire stream. No action feedback into future observations. All output-prefix marginals independent of future inputs. Physical port adequacy is not established. One kernel must work for all parameters, including indistinguishable histories; full-alphabet constraints permit arbitrary causal extension of unused histories.

## Node R136:CAUSAL_LP

- **kind:** THEOREM
- **label:** Finite causal translation is exactly a linear feasibility certificate
- **statement:** A common causal transducer exists iff R>=0, row sums one, prefix nonanticipation constraints and P=QR are jointly feasible. Minimum uniform TV error is attained and is a finite LP via absolute-value epigraph variables.
- **source:** R136_Causal_Translation.md §3
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite exogenous path experiments P_theta,Q_theta with common parameter and clock; one causal translator sees only current/past Y and uses private randomness independent of theta and the entire stream. No action feedback into future observations. All output-prefix marginals independent of future inputs. Physical port adequacy is not established. Construct conditional time kernels by prefix probability ratios; define zero-denominator rows arbitrarily. This is not a certificate for arbitrary controlled feedback.

## Node R136:COMPOSITION

- **kind:** THEOREM
- **label:** Causal translators compose with additive uniform path error
- **statement:** d_c(P<-W)<=d_c(P<-Q)+d_c(Q<-W). A copied causal downstream decision rule loses at most d_c in any [0,1] payoff g_theta(translated_stream,action_path), with unchanged legal actions and no feedback.
- **source:** R136_Causal_Translation.md §4
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite exogenous path experiments P_theta,Q_theta with common parameter and clock; one causal translator sees only current/past Y and uses private randomness independent of theta and the entire stream. No action feedback into future observations. All output-prefix marginals independent of future inputs. Physical port adequacy is not established. No additional raw-Y correlation in payoff; translator costs excluded unless modeled. Independent seeds implement composition; two-way simulation need not be a complete physical isomorphism.

## Node R136:DETERMINISTIC

- **kind:** ASSUMPTION
- **label:** Deterministic parameter-indexed streams
- **statement:** Each desired P_theta is concentrated on x(theta), and each available Q_theta on y(theta).
- **source:** R136_Causal_Translation.md §5
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite exogenous path experiments P_theta,Q_theta with common parameter and clock; one causal translator sees only current/past Y and uses private randomness independent of theta and the entire stream. No action feedback into future observations. All output-prefix marginals independent of future inputs. Physical port adequacy is not established.

## Node R136:PREFIX

- **kind:** THEOREM
- **label:** Timed recovery iff every observed-prefix fiber preserves the desired prefix
- **statement:** Exact causal simulation in DETERMINISTIC exists iff y_<=t(theta)=y_<=t(theta_prime) implies x_<=t(theta)=x_<=t(theta_prime), for all pairs and t. A deterministic translator then suffices.
- **source:** R136_Causal_Translation.md §5
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite exogenous path experiments P_theta,Q_theta with common parameter and clock; one causal translator sees only current/past Y and uses private randomness independent of theta and the entire stream. No action feedback into future observations. All output-prefix marginals independent of future inputs. Physical port adequacy is not established. A full-record fiber condition at H alone does not impose the earlier deadlines.

## Node R136:DELAY_MODEL

- **kind:** MODEL
- **label:** The same hidden bit arrives before versus after the deadline
- **statement:** Theta={0,1}, H=2. Desired stream x(theta)=(theta,blank); available stream y(theta)=(blank,theta).
- **source:** R136_Causal_Translation.md §6
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite exogenous path experiments P_theta,Q_theta with common parameter and clock; one causal translator sees only current/past Y and uses private randomness independent of theta and the entire stream. No action feedback into future observations. All output-prefix marginals independent of future inputs. Physical port adequacy is not established. Both completed records identify theta; the first output has a fixed earlier deadline.

## Node R136:DELAY_GAP

- **kind:** THEOREM
- **label:** Offline perfect translation can have causal loss one half
- **statement:** DELAY_MODEL has exact offline translation (y2,blank) but d_c(P<-Q)=1/2. First-deadline guessing has desired value one versus available value one half.
- **source:** R136_Causal_Translation.md §6
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite exogenous path experiments P_theta,Q_theta with common parameter and clock; one causal translator sees only current/past Y and uses private randomness independent of theta and the entire stream. No action feedback into future observations. All output-prefix marginals independent of future inputs. Physical port adequacy is not established. Fair early guessing attains the lower bound; waiting changes the protocol, so static Blackwell is not contradicted.

## Node R136:QUERY_MODEL

- **kind:** MODEL
- **label:** Pre-query resource commitment with adaptive coordinate reads
- **statement:** For n>=2 and 0<=k<=n, read at most k coordinates of b in {0,1}^n before q in {1,...,n} is revealed; then guess b_q. V_nk=sup_policy min_(b,q) success.
- **source:** R136_Causal_Translation.md §7
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Fixed hidden n-bit string; at most k distinct adaptive bit reads before the query is revealed; all read transcripts/private state may be retained; no later read; nature does not see the private seed. This is a query-access budget, not arbitrary k-bit encoding of a fully seen string or quantum coding.

## Node R136:QUERY_BOUND

- **kind:** THEOREM
- **label:** Sharp delayed-query capability with a read budget
- **statement:** V_nk=1/2+k/(2n). Uniform k-subset reading and fair guessing on unread coordinates attain the bound for every b,q; adaptive preparation cannot improve it.
- **source:** R136_Causal_Translation.md §7
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Fixed hidden n-bit string; at most k distinct adaptive bit reads before the query is revealed; all read transcripts/private state may be retained; no later read; nature does not see the private seed. This is a query-access budget, not arbitrary k-bit encoding of a fully seen string or quantum coding. Upper bound averages uniform b,q and conditions on the read transcript, leaving uninspected bits fair. A memory-capacity bound would require a different theorem.

## Node R136:TASK_ORDER

- **kind:** THEOREM
- **label:** Perfect separate pre-announced tasks need not admit a delayed-task translator
- **statement:** For 1<=k<n every pre-announced q has full-reader and restricted-reader guarantee region [0,1]^(2^n). Under delayed q, full-to-restricted directional guarantee loss is (n-k)/(2n), reverse zero; no exact response translator respecting the restricted read budget and deadline exists.
- **source:** R136_Causal_Translation.md §8
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Fixed hidden n-bit string; at most k distinct adaptive bit reads before the query is revealed; all read transcripts/private state may be retained; no later read; nature does not see the private seed. This is a query-access budget, not arbitrary k-bit encoding of a fully seen string or quantum coding. Each comparison uses a common protocol internally; pre-announced and delayed protocols are explicitly different. This is not a counterexample to R135 or a universal impossibility of translators.

## Node R137:CONTROL_MODEL

- **kind:** DEFINITION
- **label:** Finite feedback model with observable randomized action decoding
- **statement:** Projected rows p_s,a(z_prime,o)=sum_(alpha(s_prime)=z_prime)K(s,a;s_prime,o). For fixed z,u and target q=Kbar(z,u), W_s^epsilon is the simplex of action weights legal at s and within TV epsilon of q. One common decoder must lie in every W_s^epsilon in the visible fiber.
- **source:** R137_Executable_Feedback.md §2
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. U(z) is nonempty and controller policies are legally defined on all histories, including nominally zero-probability histories. This is a specified memoryless action-decoder class, not all causal interfaces.

## Node R137:EXACT_INTERFACE

- **kind:** ASSUMPTION
- **label:** One legal exact decoder selected for every visible request
- **statement:** For every z and u in U(z), choose one w_z,u in the intersection of all W_s^0 with alpha(s)=z; sample it with the stated conditional-randomness contract.
- **source:** R137_Executable_Feedback.md §4
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. This is a supplied feasible decoder, not a consequence of individual-state feasibility.

## Node R137:LOCAL_LP

- **kind:** THEOREM
- **label:** Common-fiber feasibility exactly characterizes the declared interface
- **statement:** A legal decoder with uniform row error <=epsilon exists iff intersection_(s in fiber z) W_s^epsilon is nonempty. One common simplex vector, illegal-action zeros and per-state joint-row TV epigraphs give a finite LP. Empty common legal menu remains infeasible at epsilon=1.
- **source:** R137_Executable_Feedback.md §3
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. Necessity/sufficiency is restricted to this decoder class and every represented state. Joint rows, not separate next-state/output marginals.

## Node R137:CLOSED_LOOP

- **kind:** THEOREM
- **label:** Exact decoder preserves every projected feedback policy law
- **statement:** Under EXACT_INTERFACE every legal abstract projected-history controller preserves its entire finite-horizon joint z/request/output law from paired starts and executes only legal concrete actions. Conversely universal one-step law preservation by a fixed decoder forces its exact local rows.
- **source:** R137_Executable_Feedback.md §4
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. Controller seed may be coupled; no concrete hidden-state/action/cost law is promised. Feedback is handled by conditional controlled rows, not a passive full-path kernel.

## Node R137:APPROX_INTERFACE

- **kind:** ASSUMPTION
- **label:** Uniform legal approximate decoder and policy extension
- **statement:** For every z,u a common legal w_z,u has TV(sum_a w_a p_s,a,Kbar(z,u))<=epsilon for all s in the fiber, 0<=epsilon<=1. Conditional randomization and legal controller extension on all projected histories are supplied.
- **source:** R137_Executable_Feedback.md §5
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. Approximation does not permit illegal concrete actions or undefined policies after mismatches.

## Node R137:APPROX

- **kind:** THEOREM
- **label:** Feedback path-law error after lawful action decoding
- **statement:** Under APPROX_INTERFACE the projected length-H closed-loop path-TV error for any common abstract controller is <=1-(1-epsilon)^H<=min(1,H epsilon); every common [0,1] projected-history payoff changes by at most this amount.
- **source:** R137_Executable_Feedback.md §5
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. Classical coupling bound applied after action decoding; no infinite-horizon small-error or omitted-cost guarantee.

## Node R137:OBSTRUCTION

- **kind:** THEOREM
- **label:** At most one hidden-state witness per concrete action label
- **statement:** If a fixed visible request has no common legal epsilon-accurate decoder and m=|A|, at most m states of its visible fiber already have empty intersection of W_s^epsilon.
- **source:** R137_Executable_Feedback.md §6
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. Classical finite Helly/Radon argument in the (m-1)-dimensional simplex; fixed error budget. Not a sample-complexity or unknown-continuum certification theorem.

## Node R137:FORBIDDEN_MODEL

- **kind:** MODEL
- **label:** Each hidden state defeats one of m action ports
- **statement:** There are m>=2 indistinguishable ready states i and m universally legal actions a. Action a fails iff a=i; target abstract request succeeds certainly. Outcomes are distinct visible absorbing states.
- **source:** R137_Executable_Feedback.md §7
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. Specified finite model; hidden ready-state label unavailable to the decoder.

## Node R137:SHARP_OBSTRUCTION

- **kind:** THEOREM
- **label:** The m-state obstruction size is sharp
- **statement:** In FORBIDDEN_MODEL every proper subset of ready states admits an exact common decoder but all m do not. Minimum uniform row-TV error is 1/m; best worst-case success is 1-1/m.
- **source:** R137_Executable_Feedback.md §7
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. Exactness requires w_i=0 for each represented hidden state; uniform mixing attains the approximate optimum. Different from R132 simultaneous task-slot scheduling.

## Node R137:BLIND_MODEL

- **kind:** MODEL
- **label:** Opposite hidden action encodings
- **statement:** Two hidden ready states b share an observation; two actions a are legal everywhere and succeed iff a=b. Compare certain-success and fair success/failure target rows.
- **source:** R137_Executable_Feedback.md §7
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. Reuses the blind opposite-action pattern already in R134; not claimed as a new historical counterexample.

## Node R137:OBSERVATION_GAP

- **kind:** THEOREM
- **label:** Statewise witnesses can require an oracle, while mixing can match a fair target
- **statement:** In BLIND_MODEL, hidden-state-aware error is zero for the certain-success target, but visible-only uniform error is at least 1/2 and attainable. A fair target is exactly realizable by equal mixing, with neither deterministic action exact.
- **source:** R137_Executable_Feedback.md §7
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. An added timely sensor can change the observation contract; no free sensor or full-state access assumed.

## Node R137:SEED_MODEL

- **kind:** MODEL
- **label:** Fresh versus persistent interface randomization
- **statement:** One-state concrete plant outputs chosen action bit and returns to itself. Abstract single request emits an independent fair bit each step. Compare fresh fair actions to one fair coin reused for all H steps.
- **source:** R137_Executable_Feedback.md §8
- **status:** EXPLICIT_MODEL_OR_DOMAIN_PREMISE
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. Reused coin is persistent interface memory and violates the declared conditional action law after the first observation.

## Node R137:SEED_GAP

- **kind:** THEOREM
- **label:** Correct one-time marginals can hide a large implementation path error
- **statement:** In SEED_MODEL fresh sampling is exact; reusing one coin preserves every one-time output marginal but yields path-TV error 1-2^(1-H), H>=1.
- **source:** R137_Executable_Feedback.md §8
- **status:** MANUAL_CONDITIONAL_PASS
- **scope:** Finite Markov-sufficient concrete S, visible onto alpha:S->Z, legal action menus A(s), joint next-state/output kernel, fixed time and pointed state. Decoder w(a|z,u) uses only current visible z/request u and fresh conditional randomness; abstract controllers may use projected history but not decoder coins/concrete actions. All represented starts; physical adequacy independently supplied. Temporal joint-law counterexample, not a refutation of CLOSED_LOOP. Persistent memory must be represented or the conditional decoder contract verified.
