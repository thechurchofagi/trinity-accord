# Coherent probability corrections to R201 and R202

Version: R201-R202-CORRECTIONS-v0.1.0. Research source: `90a542d697d923aa484f2bd5a4484a438125325a`. This is an audit repair; it does not constitute a new consciousness result. The original archived notes must remain intact, with effective correction overlays and revised candidate premises.

## 1. R201-C1 remains a valid sufficient theorem

Under the note's simultaneous probability and support premises, `delta=rho*Delta_C+b`, `0<rho<=1`, `|b|<=beta`, and class-specific transport drifts at most `epsilon_0,epsilon_1`, the strict condition `delta>beta+epsilon_0+epsilon_1` still implies `Delta_T>=delta-beta-epsilon_0-epsilon_1>0`. The proof in R201 §3 is valid. Its conclusion is a conservative sufficient margin, not a sharp identified set.

## 2. R201-C2's original displayed tuples are not coherent probability witnesses

The original equality and reversal examples set `rho=1` and `b=1/10`. But `rho=P(H=1|J=1)-P(H=1|J=0)=1` forces the two conditional probabilities to be 1 and 0. With both J strata supported, `H=J` almost surely. Therefore `delta=P(M=1|J=1)-P(M=1|J=0)=Delta_C`, and `b=delta-rho*Delta_C=0`. The examples pass an unconstrained scalar calculation while violating the joint-probability interpretation. Their status as exact probability witnesses must be withdrawn.

Use `P(H,J)=(3,1,1,3)/8`, ordered `(0,0),(0,1),(1,0),(1,1)`, in both repaired examples. This yields `rho=1/2`.

| Quantity | Equality collapse | Strictly below threshold, reversed target |
|---|---|---|
| `P(M=1|H,J)` in the same order | `(7/15,3/5,2/5,8/15)` | `(5/12,11/20,9/20,7/12)` |
| `(q_C0,q_C1)` | `(1/2,1/2)` | `(9/20,11/20)` |
| `delta` | `1/10` | `3/20` |
| `b=beta` | `1/10` | `1/10` |
| `(epsilon_0,epsilon_1)` | `(0,0)` | `(1/10,1/10)` |
| `(q_T0,q_T1)` | `(1/2,1/2)` | `(11/20,9/20)` |
| `Delta_T` | `0` | `-1/10` |

The equality example shows that globally replacing `>` by `>=` is invalid. It does not show tightness for every positive choice of bias and drift budgets. In fact equality with `Delta_T=0`, `epsilon_0+epsilon_1>0`, and `rho<1` cannot attain every inequality in the displayed sufficient-bound proof. Remove any assertion of arbitrary-budget sharpness. The second example gives a feasible reversal below the conservative threshold. Full joint eight-cell distributions and exact execution checks are in `R201_COHERENT_WITNESSES.json`; the generating verifier is `check_r201_coherent_witnesses.py`.

The map auditor separately identified an invalid same-instance rule from a **strict-margin** premise to equality/below-margin counterexamples. A witness schema or its own witness-domain premise must supply those examples; the strict-margin instance cannot do so.

## 3. R202-C2 requires zero residual for its exact inversion

The R202 claim ledger correctly requires `J independent of M given H`. The note and candidate node weaken this to independence **or separately bounded departures**, then apply an exact formula. Bounded departures do not give point identification.

Let `R=(1-pi)Cov(M,J|H=0)+pi Cov(M,J|H=1)`. Then, with the same independently calibrated `a>c`, positivity `c<j<a`, and one actual validation/use contract,

`pi=(j-c)/(a-c)`,

`q1=(r-c*m-R)/(j-c)`,

`q0=(a*m-r+R)/(a-j)`.

The original inversion follows when `R=0`. Conditional independence is a sufficient condition; cancellation could also make the aggregate zero, but cannot be inferred from observed fit. For `|R|<=kappa`, replace exact values by the common-residual feasible set. Conservative marginal outer intervals are `qhat1 +/- kappa/(j-c)` and `qhat0 +/- kappa/(a-j)`, clipped to `[0,1]`. They must not be combined as independent intervals: the same R enters both with opposite signs, and coherent binary-law constraints remain in force. No sharp identified-set claim is made.

The existing feasible R203-C2 dependent twin is a sufficient counterexample; no new example is needed. Its conditional `(M,J)` cells are `(19,1,21,9)/50` under `H=0` and `(9,21,1,19)/50` under `H=1`, with `pi=1/2`. It gives `a=4/5`, `c=1/5`, `m=j=1/2`, `r=7/25`, `R=3/50`, and true `(q0,q1)=(3/5,2/5)`. The invalid zero-residual inversion returns `(2/5,3/5)`, reversing the direction. Inserting the actual common residual recovers the true values exactly. The rational checker and full joint table are in `check_r202_residual_correction.py` and `R202_RESIDUAL_CORRECTION.json`.

## 4. Downstream scope and manuscript handling

These corrections do not weaken UCT C1/U1, decide an experiential target, or invalidate R203's total-covariance identity. R202's exact result survives under its ledger's original conditional-independence premise. R201's sufficient-margin result survives. Their flawed witness/domain wording must not be promoted as an established proof.

The proposed sensorimotor source-consumer paper does not need either probability result as a premise. Preserve these corrections in its audit appendix or accompanying research record, while keeping the manuscript centered on matched outputs, prediction, actual source use, separating probes, and the limits of mechanism/phenomenal interpretation.
