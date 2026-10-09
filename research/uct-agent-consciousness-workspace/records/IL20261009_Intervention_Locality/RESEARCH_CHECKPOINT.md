# IL20261009 — Identical boundary behavior does not preserve constituent-local organization

**Result:** IL-RESULT-v0.1.0 (2026-10-09). **Method:** MGTD v1.0.1 and highest UCT guide v2.0. **Parent completed map:** UCT-MAP-v1.1.0, sequence 2; read at e1ceadd3097bec5ac6abb4510ae613ff7e41bbc3. **Status:** conditional mathematical results checked; PENDING_MAP / AUDIT_INCOMPLETE for current whole-map integration. No new publication, DOI, OTS, Arweave or scheduling action.

This compact remote record preserves all substantive conclusions and proofs. The downloadable UCT_Intervention_Locality_20261009_v0.1.0 package contains the expanded manuscript, larger verifier, exact results, full local module, historical source scan and per-claim audit. Compact and expanded serializations are not claimed byte-identical.

## 1. Prior-result correction and research question

UCT I v1.2 §3.5 already requires physically grounded part, reset, readout and timing relations in organizational comparison. R77 (2026-10-05) already proves that a diagonalized coordinate diagram does not imply independent physical constituents; TF20261008 §5.1 repeats this. R127 already limits inference from exposed behavior. RT/TH's published target-readout analysis (DOI 10.5281/zenodo.23251651) does not require preservation of every part-local operation. These are antecedents, not new results.

The present increment is: (i) an exact classification of all bijections preserving the complete primitive local-reset family; (ii) an externally identical pair with no redundant linear state mode; (iii) a sharp two-readout discrepancy even when the single-part intervention is chosen optimally; (iv) a general limited-write and finite-detection bound. Mathematical foundations are credited to product automorphisms, causal abstraction and linear realization theory. Historical priority of this combined specialization is not established.

Keep boundary behavior, state dynamics under conjugacy and physical constituent-local organization separate. A local reset immediately changes one nominated carrier before the next update. This does not assert autonomous subsequent dynamics. A virtual coordinate is not automatically an actual process; an independently justified actual macroprocess is not excluded either.

## 2. L1: exact local-reset normal form

Let X=product_i X_i and Y=product_j Y_j have finitely many factors, each with at least two states; factor sets may be infinite. Every Cartesian combination and every local reset value is admitted. R_i^a overwrites coordinate i with a, leaving others unchanged. J_X is the full family of these operations, and J_Y is defined analogously. For a bijection h:X->Y:

    h J_X h^{-1} = J_Y

holds iff the factor counts agree and there exist a factor permutation pi and bijections phi_i:X_i->Y_pi(i) such that

    h(x)_pi(i)=phi_i(x_i).

**Proof.** The equations R_i^a R_i^b=R_i^a and R_i^b R_i^a=R_i^b characterize membership in the same factor's reset family. Resets on distinct non-singleton factors fail this mutual-absorption condition. Conjugation preserves compositions, hence permutes these families and their values. From h R_i^a=R_pi(i)^phi_i(a) h, evaluate a state with x_i=a: its output coordinate pi(i) must be phi_i(a), independently of every other coordinate. This proves the form. Substitution proves the converse. The group is the familiar product-permutation symmetry associated with Hamming/product structures, not new general mathematics.

**Linear corollary:** for h(x)=Sx over a field, S must be monomial (exactly one nonzero in each row and column). Affine maps also allow fixed offsets. Dense linear mixing is not local-factor relabeling.

**Failure control:** if J contains only arbitrary *whole-state* constant resets, every bijection preserves it. Thus global restart access cannot establish constituent factorization. Restricted supports or missing local resets change L1's premises.

## 3. LTI pair with complete boundary equality and no redundant linear mode

Fix discrete time, one real-valued external input u and output o. The two ideal devices have their own independently stipulated local state-reset ports.

    A: x1_next=x1/2+u; x2_next=x2/4+u; o=x1+x2.
    B: z1_next=3z1/8+z2/8+2u; z2_next=z1/8+3z2/8; o=z1.

For S=[[1,1],[1,-1]], z=Sx, the matrices obey A_B=S A_A S^{-1}, B_B=S B_A and C_B=C_A S^{-1}. Induction yields equal boundary outputs for every finite input sequence and matched initial condition. A causal boundary-feedback policy also yields equal transcripts because its past observations are equal. Internal resets, energy, additional measurements, microscopic clock effects and unspecified adaptation classes are not part of this equivalence.

Both systems are controllable and observable: controllability determinants are -1/4 and 1/2; observability determinants are -1/4 and 1/8. The first Markov parameters are 2,3/4,5/16, whose two-by-two Hankel determinant is 1/16. A one-state LTI realization is impossible. Minimality is relative to that model class, not all possible microscopic hardware.

**No local organizational isomorphism:** rejecting the displayed S alone would not suffice. L1 forces every reset-preserving bijection to be factorwise up to part permutation. Such maps preserve whether a next coordinate depends on another coordinate at fixed u. A has no cross-coordinate dependence, while B has nonzero dependence in both directions. Thus no candidate preserving these local resets can conjugate their dynamics, including nonlinear factorwise candidates.

## 4. Explicit probe and exact optimal imitation gap

Common inputs -4 then 3 from zero prepare x=(1,2) and z=(3,-1), both with output 3. Set subsequent input to zero.

Source x1:=0 gives immediate and next outputs (2,1/2). Target z1:=0 gives (0,-1/8); target z2:=0 gives (3,9/8). The correctly transported source reset writes z:=(2,-2), changing both target coordinates, and reproduces the entire source output trajectory. Generally the transported reset to x1=a is

    (z1,z2) -> (a+(z1-z2)/2, a-(z1-z2)/2).

Now allow an optimally chosen **arbitrary value**, not just zero, in any one target coordinate. Writing z1:=a produces (a,(3a-1)/8). Put e=a-2 and M=max(|e|,|1+3e|/8). Then

    1 <= |1+3e|+3|e| <= 11M.

Therefore M>=1/11, attained at a=21/11. Writing only z2 leaves the immediate output3, already error1. The exact optimal two-readout minimax error over all one-part writes is consequently **1/11**, whereas the joint transported write has error zero. This comparison even permits complete state knowledge. Its constraints are a fixed write instant, common future input and no hidden compensating controller or intervening evolution.

The number 1/11 is in the declared calibrated output units, not a phenomenal metric. Under exact state/mechanism preparation, independent absolute readout errors bounded by eta<1/22 preserve distinguishability of the ideal trajectories. Unmodeled process error requires a separate bound.

## 5. General sparse-write cost and finite detection

A kick x->x+delta e_i becomes z->z+delta v_i, v_i=S e_i. For delta!=0, exact write support has size ||v_i||_0. If at most k target coordinates can immediately be written, in fixed Euclidean coordinate units the minimum squared state error is

    delta^2 * sum of the n-k smallest squared entries of v_i.

For a chosen write set, reproduce the desired changes there; all outside entries necessarily remain errors. Select the k largest squared entries to obtain the optimum. For k=1 this is delta^2(||v_i||_2^2-||v_i||_infinity^2). These are implementation costs, not experience magnitude. Metric and units must be transported under passive recoding.

If O_n=[C;CA;...;CA^(n-1)] is full rank, any nonzero post-write state mismatch changes at least one of the next n outputs, including lag0. In calibrated norms, ||O_n dz||>=sigma_min(O_n)||dz||. This needs the same future inputs and no compensating operation. Without observability a state mismatch may remain externally invisible.

For S_t=[[1,t],[-t,1]], 0<t<=1, conjugating the same diagonal source gives cross-dependence for every t>0, but normalized one-coordinate squared kick error is t^2/(1+t^2)->0. Exact nonisomorphism implies neither a large difference nor an experience-onset threshold.

## 6. Actuality, UCT and retained counterexamples

A conditional UCT application needs actual P,Q, common complete K/time, and an independently grounded reduct of these carriers, operations and dynamics such that **every** full K-isomorphism induces an isomorphism of the reduct. Only with those joint premises does the proven reduct nonisomorphism exclude full organizational isomorphism and, by inherited C1-OI, imply different complete experiential structure types.

No computational model, decoded observation or map entry supplies this actual-reduct bridge automatically. An internal implementation difference can be irrelevant to a specified actual macro-token; not every microdifference is forced into human-scale experience. A functionalism already preserving complete causal organization is not refuted by a boundary-behavior counterexample.

C1/U1/P3 remain unchanged. Persisting actual local processes do not lose experience because their reader is inaccessible, their dynamics are coupled or a mathematician diagonalizes a matrix. Their complete types need not remain constant. No familiar self, pain, color, report criterion, exclusive owner or number of subjects is derived.

Important failures retained: passive recoding must transport all operations; a failed chosen S does not itself prove nonisomorphism (scalar A=(1/2)I also has an identity isomorphism); full-state resets do not determine a factorization; non-product supports invalidate unrestricted reset arguments; hidden control can emulate a forbidden joint operation; the normal-form theorem is not a unique natural brain partition.

## 7. Verification and integration status

The expanded standard-library verifier was actually run. All checks pass: 24+40320+720 state bijections with respectively8,48,12 local-reset symmetries; four prime-field linear cases;9837 input/initial-state cases and54135 update equalities;1583 rational arbitrary-write checks alongside the analytic 1/11 proof;3696 sparse-write cases;100 small-mixing cases;48 nonzero observation tests;40320 full-reset countercontrol bijections. No human, animal or deployed-model subjective experiment was run.

The local module has26 nodes,13 conditional rules and7 non-deductive links. Relevant original A/B/C contracts and R77/TF/RT antecedents were inspected; historical v1.0.0 records were mechanically scanned. Current v1.1.0 metadata/capsule manifest was read, but the complete current1373-item graph/ledger was not restored and re-reviewed this cycle. The capsule direct-download attempt failed DNS. Therefore **PENDING_MAP / AUDIT_INCOMPLETE** remains, with no completed-map version increment. Fresh conclusion IDs do not by themselves prove whole-map semantic consistency. Existing R185/AC pending checkpoints and reviewer-controlled open items must be retained.

The next prerequisite for promotion is full current-map compatibility review and affected rederivation. This note is a substantive scoped extension, not a standalone-paper authorization or an independently confirmed consciousness breakthrough.

## Primary sources and overlap

Own sources: UCT I v1.2 DOI10.5281/zenodo.23131575 §§3.5–4; UCT III DOI10.5281/zenodo.23137088 §5; UCT II BAC; R77 and TF §5.1; RT/TH DOI10.5281/zenodo.23251651. Original source clauses were reread from the frozen user-provided archive, not only prior chat summaries.

Rubenstein et al. (2017), Causal Consistency of Structural Equation Models, https://arxiv.org/abs/1707.00819: exact causal transformations, primary abstracts read. Beckers & Halpern (2019), Abstracting Causal Models, DOI10.1609/aaai.v33i01.33012678, https://arxiv.org/html/1812.03789v4, especially Definition3.9: constructive componentwise abstraction; this note does not solve its general converse conjecture. Squires et al. (2023), https://proceedings.mlr.press/v202/squires23a.html, and Ahuja et al. (2023), https://proceedings.mlr.press/v202/ahuja23a.html: interventional representation identification, primary abstracts read. Official state-space background: https://www.mathworks.com/help/control/state-coordinate-transformation.html. The Hamming automorphism group is explicitly stated in the publisher introduction of DOI10.1016/j.dam.2021.09.017. No independent experiment or complete theorem-by-theorem external priority clearance is claimed.
