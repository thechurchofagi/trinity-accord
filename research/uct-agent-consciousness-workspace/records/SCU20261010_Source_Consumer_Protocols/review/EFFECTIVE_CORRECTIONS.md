# Effective corrections to disabled R194, R201 and R202 records

Version: **SCU-CORRECTIONS-v0.1.0**. The original notes, code and result files remain immutable historical records. The associated JSON overlays register corrected effective statements and conditional routes; they are disabled candidates, not a new completed-map release. All actual and named phenomenal applications remain open.

## 1. Signed graphs need joint edge-and-anchor consistency

Let a finite graph have Boolean vertex labels `x_v`, edge constraints `x_u XOR x_v = epsilon_uv`, and a partial anchor assignment `eta(v)`. Choose a root in each component and propagate relative signs `p_v`. A consistent cycle guarantees path-independent relative signs. Every labelling in that component then has the form

`x_v = t_component XOR p_v`.

Each anchor forces `t_component = eta(v) XOR p_v`. If two anchors force different root values, there is no solution even though every cycle is consistent. If all anchors in the component agree on the root value, an anchored component has one solution and an unanchored component has two. Thus the count is zero when a cycle or anchor/path condition is inconsistent; otherwise it is `2^c`, with `c` unanchored components.

The smallest counterexample is one equality edge `x_0=x_1` with anchors `x_0=0, x_1=1`. It has no cycle and no unanchored component, so the unqualified cycle-only formula incorrectly returns one solution. Direct enumeration returns zero. Add five unanchored isolated vertices to embed this example in the original seven-variable domain: the unqualified count becomes 32, while the actual count remains zero.

This does not invalidate the original one-anchor numerical example or the complement symmetry of an unanchored component. It repairs an overbroad extension to multiple anchors. Relative alignment now requires a jointly consistent graph/anchor instance; a conventional compatible anchor still supplies no familiar-mineness semantics.

The independent checker compares direct Boolean assignment enumeration with component propagation on all 59,809 simple signed graphs and partial binary anchor maps with 0–4 vertices. It also checks the seven-vertex embedded counterexample. The universal finite-graph statement follows from the argument above; the enumeration has precisely the reported finite scope.

## 2. R201: preserve the sufficient theorem and replace impossible witnesses

The sufficient theorem starts with one coherent calibration and target probability contract:

`delta = rho Delta_C + b`, `0 < rho <= 1`, `|b| <= beta`,

and class-specific transport bounds `|q_Th - q_Ch| <= epsilon_h` for `h=0,1`. If

`delta > beta + epsilon_0 + epsilon_1`,

then the numerator is positive, so

`Delta_C = (delta-b)/rho >= delta-beta`.

Applying both drift bounds to this same calibration-to-target instance gives

`Delta_T >= delta-beta-epsilon_0-epsilon_1 > 0`.

This proof is valid. It is a sufficient conservative margin, not an assertion of a sharp identified set at every nuisance-budget tuple.

The original equality and reversal witnesses choose `rho=1` and `b=1/10`. But

`rho = P(H=1 | J=1) - P(H=1 | J=0) = 1`

forces the two probabilities to be 1 and 0. With both J strata supported, `H=J` almost surely. Consequently the marker contrast conditional on J equals the contrast conditional on H, so `delta=Delta_C` and `b=delta-rho Delta_C=0`. A scalar tuple with `rho=1,b=1/10` is therefore not a joint-probability witness under the note's own definitions.

For both corrected examples use `P(H,J)=(3,1,1,3)/8` in order `(0,0),(0,1),(1,0),(1,1)`, which gives `rho=1/2`.

| Quantity | Equality collapse | Below-threshold reversal |
|---|---|---|
| `P(M=1|H,J)` in that order | `(7/15,3/5,2/5,8/15)` | `(5/12,11/20,9/20,7/12)` |
| `(q_C0,q_C1)` | `(1/2,1/2)` | `(9/20,11/20)` |
| `delta` | `1/10` | `3/20` |
| `b=beta` | `1/10` | `1/10` |
| `(epsilon_0,epsilon_1)` | `(0,0)` | `(1/10,1/10)` |
| `(q_T0,q_T1)` | `(1/2,1/2)` | `(11/20,9/20)` |
| `Delta_T` | `0` | `-1/10` |

All eight joint cells are nonnegative and sum to one. The checker computes all conditionals from these actual tables rather than inserting independently chosen scalar values. The equality example shows that replacing strict `>` globally by `>=` is invalid, but its drift budget is zero. It does not prove equality sharpness for every positive drift budget. The second example is a coherent reversal below the conservative threshold.

A third, separate endpoint-sign example has `H=0,J=M=1` with mass 1/2 and `H=1,J=M=0` with mass 1/2. It has positive observed `delta=1` but `rho=-1` and `Delta_C=-1`. Without independently positive endpoint direction, an observed marker contrast cannot orient H.

These are three alternative worlds, not one world satisfying every boundary case. The original `r_strictness_witnesses` mistakenly includes the strict-margin premise while promising equality and below-margin witnesses under same-instance binding. The corrected rule uses an explicitly coherent witness-domain premise and binds each joint law and its budgets separately. The source lower bound and target sign rule are unchanged.

## 3. R202: one common residual, not exact inversion under a bound

In one fixed validation-domain binary law, let

`pi=P(H=1)`, `a=P(J=1|H=1)`, `c=P(J=1|H=0)`,

`m=P(M=1)`, `j=P(J=1)`, `r=P(M=1,J=1)`,

with independently calibrated `a>c` and positivity `c<j<a`. Define the aggregate residual

`R=(1-pi) Cov(M,J|H=0) + pi Cov(M,J|H=1)`.

The three mixture equations are

`j=c+(a-c)pi`,

`m=(1-pi)q0+pi q1`,

`r=c(1-pi)q0+a pi q1+R`.

Solving yields

`pi=(j-c)/(a-c)`,

`q1=(r-cm-R)/(j-c)`,

`q0=(am-r+R)/(a-j)`.

Conditional independence `J independent of M given H` suffices for `R=0`. An independently justified cancellation of the two weighted conditional covariances would also suffice, but observed fit cannot establish that cancellation. A bound `|R|<=kappa` alone does not yield unique q values.

The corrected bounded route retains the same R in both formulas, together with a coherent binary joint law. Marginal outer intervals may be obtained by adding/subtracting `kappa/(j-c)` or `kappa/(a-j)` to the zero-residual estimates and clipping to `[0,1]`. Their endpoints cannot be combined independently: the same residual enters with opposite signs, and joint-law feasibility may remove parts of the apparent rectangle. No arbitrary-budget sharpness claim is made.

An existing R203 dependent twin supplies a direct counterexample. Its conditional `(M,J)` cells, in order `00,01,10,11`, are `(19,1,21,9)/50` under H=0 and `(9,21,1,19)/50` under H=1, with `pi=1/2`. These give

`a=4/5`, `c=1/5`, `m=j=1/2`, `r=7/25`, `R=3/50`,

and true `(q0,q1)=(3/5,2/5)`. The invalid zero-residual inversion reports `(2/5,3/5)`, reversing the direction. Inserting the common `R=3/50` recovers the correct rates exactly. The audit also retains a separately constructed smaller-residual counterexample in `R202_RESIDUAL_COUNTEREXAMPLE.json`.

The effective exact route now uses strict conditional independence, with an explicit same-law positivity guard. A second exact route permits independently zero aggregate residual. A separate bounded route returns the common-residual feasible set. All remain conditional on calibrated endpoint meaning/rates, justified audit sampling, actual U=1 and the same target/application. Identification within reporting validation V still does not establish transport to genuinely nonreporting T.

## 4. Registration and impact

The three `*_EFFECTIVE_CORRECTION_OVERLAY.json` files contain the precise target IDs, original file and record hashes, replacement statements and premises, added conditional nodes/rules, and review-routing closures. All overrides explicitly keep the historical sources unchanged and the effective candidates disabled. Their exact proof location is this report, the rational checker and its result file.

The affected closed-map ID set is empty. R194's downstream relative/complement/anchor protocol survives after joint consistency is imposed. R201's strict sufficient theorem survives independently of its repaired counterexamples. R202's exact theorem survives on the independence/zero-residual branch; R203's covariance identity agrees with the residual-adjusted formulas. No source/consumer proof in SCU uses a faulty version as a premise.

These are corrections to mathematical and inference scope. They establish neither C1, U1, an actual installation, familiar-mineness H, nor a new empirical datum. QC10, IA-QC11, QC12 and QC13 remain open.

