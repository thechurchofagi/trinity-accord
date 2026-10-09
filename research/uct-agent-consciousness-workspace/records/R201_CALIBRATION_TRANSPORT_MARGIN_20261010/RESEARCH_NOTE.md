# R201 — A Robust Orientation Margin for Familiar-Continuity Evidence

Date: 2026-10-10  
Status: unpublished conditional UCT research module; disabled checkpoint candidate

## 1. Question and result

R200 specified a calibration firewall but left “bounded drift” qualitative. R201 asks a narrower positive question: when the reporting-adult endpoint is fallible, the objective marker may have residual endpoint-dependent bias, and its class-conditional law may drift in a no-report target domain, what numerical margin is sufficient to preserve the marker's direction for the selected familiar-continuity target `H`?

The answer is a conservative inequality. On one declared actual-use stratum, let

`delta_C = P_C(M=1 | J=1,U=1) - P_C(M=1 | J=0,U=1)`

be the observable marker contrast across the predeclared adult comparative endpoint `J`. Let

`rho_C = P_C(H=1 | J=1,U=1) - P_C(H=1 | J=0,U=1)`

be its independently defended positive semantic reliability, and let

`Delta_C = P_C(M=1 | H=1,U=1) - P_C(M=1 | H=0,U=1)`.

Represent departures from conditional nondifferentiality by the explicit sensitivity equation

`delta_C = rho_C Delta_C + b_C`, with `0 < rho_C <= 1` and `|b_C| <= beta`.

For a target domain `T`, write `p_Ch=P_C(M=1|H=h,U=1)` and `p_Th=P_T(M=1|H=h,U=1)`, and assume class-specific drift bounds `|p_Th-p_Ch| <= epsilon_h`. Then

`delta_C > beta + epsilon_0 + epsilon_1`

is sufficient for `Delta_T=P_T(M=1|H=1,U=1)-P_T(M=1|H=0,U=1)>0`. With sampling uncertainty, the operational certificate replaces `delta_C` by a simultaneously valid lower confidence bound and the three nuisance terms by defensible upper bounds.

This is a margin certificate for a measurement relation, not a definition of `H`, an experience detector, or proof that any route was actually used.

## 2. Typed domain and separation

Fix one reporting calibration population `C`, one target population `T`, one selected `H` meaning, marker `M`, predeclared comparison `J`, actual bearer class, interval, complete application signature `K`, and actual same-episode retained-route use `U=1`. Keep distinct:

- `U`: actual carrier-to-consumer use in the episode;
- `E_U`: telemetry, perturbation or bypass evidence about `U`;
- `J`: a report action interpreted under a predeclared comparative item and response key;
- `H`: the selected experience-internal familiar/established-continuity coordinate;
- `M`: a candidate objective marker;
- `Y`, `O`, `G`: success/fluency, ownership and agency covariates;
- `b_C`: a declared residual sensitivity term, not an observed psychological entity;
- `epsilon_h`: class-specific transport tolerances, not empirical facts until supported.

All probabilities below condition on actual `U=1`. Replacing that condition by `E_U=1` is invalid unless route-use misclassification receives its own error model. A bypass test may support `U`; it is not part of the experiential structure and does not make `U` true by stipulation.

## 3. R201-C1 — robust sign certificate

**Type.** Conditional quantitative transport theorem.  
**Domain.** The fixed `C,T,H,J,M,U=1,K` contract above.  
**All premises.**

1. `J` has the same independently fixed positive `H` meaning and known response-key direction in the adult calibration domain.
2. `0<rho_C<=1`; this sign is not estimated from `M` itself.
3. The residual decomposition holds with `|b_C|<=beta`.
4. The same target meaning and marker event are retained across `C,T`.
5. Each class-conditional marker probability drifts by at most `epsilon_h`.
6. Positivity/support makes all displayed conditionals meaningful.
7. One actual-use stratum is retained; no `E_U/U` substitution occurs.

**Statement.** If `delta_C > beta+epsilon_0+epsilon_1`, then `Delta_T>0`. More specifically,

`Delta_T >= delta_C - beta - epsilon_0 - epsilon_1 > 0`.

**Proof.** From the residual equation,

`Delta_C=(delta_C-b_C)/rho_C >= (delta_C-beta)/rho_C`.

The stated strict margin makes the numerator positive; because `rho_C<=1`, `Delta_C>=delta_C-beta`. The two drift inequalities give

`Delta_T=p_T1-p_T0 >= (p_C1-epsilon_1)-(p_C0+epsilon_0)`

`=Delta_C-epsilon_0-epsilon_1 >= delta_C-beta-epsilon_0-epsilon_1>0`. QED.

The elementary inequalities are not claimed as new probability theory. The UCT-specific contribution is the typed certificate: it attaches a quantitative stop rule to R200's firewall without merging report, selected experience, actual use and cross-domain evidence.

## 4. R201-C2 — strictness and failure witnesses

The strict threshold cannot generally be weakened under only these premises.

- **Equality can lose orientation.** Let `beta=epsilon_0=epsilon_1=1/10`, `rho=1`, source class-conditionals `(p_C0,p_C1)=(2/5,3/5)`, and `b=1/10`. Then `delta_C=3/10`, exactly the nuisance sum. Moving the target probabilities to `(p_T0,p_T1)=(1/2,1/2)` respects both drift bounds and yields `Delta_T=0`.
- **Below threshold can reverse.** With source `(2/5,11/20)`, the same residual and drift bounds give `delta_C=1/4<3/10`, while target `(1/2,9/20)` yields `Delta_T=-1/20`.
- **Endpoint sign is indispensable.** If `rho<0`, the same positive target marker separation can induce a negative `J` contrast. Response-key provenance and independent target semantics cannot be inferred from marker success.

`check_robust_orientation_margin.py` exhaustively checks the theorem on a denominator-eight rational grid and records the exact rational boundary witnesses. The grid verifies the implementation and finite claim class; the symbolic proof carries the stated theorem.

## 5. What can bound the nuisance terms

The theorem turns an omnibus “validation” claim into three separate empirical obligations.

1. **`rho_C` sign and target meaning.** Fix the comparative wording before outcomes, reverse response keys without reversing the item meaning, and separate ownership, agency, liking, ease and confidence. This supports a fallible semantic anchor; it does not make report constitutive.
2. **Residual budget `beta`.** Use success/fluency manipulations, demand controls and held-out marker validation to bound how much `M` tracks `J` through routes other than `H`. `beta` is a sensitivity bound; a convenient fitted residual is not automatically a causal bound.
3. **Transport budgets `epsilon_h`.** Use reporting holdouts, matched task conditions, multiple populations and prospective out-of-domain checks to bound class-conditional shifts. Similar marginals, shared code, anatomy or overall accuracy do not bound either `epsilon_h`.

Intentional binding illustrates why this discipline matters. Dewey and Knoblich (2014) found no individual-difference correlation between implicit and explicit agency measures in their study. Kong et al. (2024) found temporal compression for active and passive movement relative to an external event, but no voluntary-versus-passive difference, and argued that temporal prediction/sensory integration rather than intention explained the effect. Seghezzi et al. (2026) found intentional binding decreased during learning under specific feedback and relevance conditions. These are primary empirical reasons to treat a familiar nearby marker as conditional and context-sensitive, not as a universal signed endpoint. They do not directly test UCT's `H`.

The discrepancy-attribution experiments of Whittlesea and Williams show that felt familiarity is not reducible to fluency alone; context, expectation and attribution can reverse or alter the judgment. Draxler and Kurz (2025) provide a modern primary methods example for testing measurement invariance across multiple covariates in a Rasch framework. Neither source supplies R201's missing bounds; both motivate estimating rather than assuming them.

## 6. Thought experiments

1. **Response-key mirror.** Hold the intended comparison and bodily/action organization fixed, reverse the learned button mapping, and ask whether `M` follows the key. Fixed item meaning with changed code targets the `rho/beta` firewall.
2. **Smooth newcomer.** Hold performance high while switching an established route for a newly optimized controller. If `M` follows speed or success, the residual budget grows even when `J_H` is held.
3. **Familiar route under verified bypass.** Hold biography and stored memory fixed while physically bypassing the retained carrier-consumer path. `E_U` can become strong evidence, but the experimental test remains evidence about `U`, not the experience's structure.
4. **Adult/infant or reporting/no-report transport.** Hold marker prevalence fixed while moving both class-conditionals within allowed drift. The threshold tells exactly when the positive direction survives; matching marginals alone says nothing.
5. **Copy/switch/memory.** Copy `M`, reports and stored history, then switch the actual current consumer. The statistical certificate can remain true for the copied channel while the R173 actual-use premise fails.
6. **Abacus/calculator/human-realized agent.** Preserve the rational probability table across substrates. The inequality transports as mathematics; the actual bearer, installation, target semantics and UCT application do not.
7. **Formation/ancestors.** Let retentive organization vary continuously over formation. The certificate permits graded evidence and no basal threshold; it does not create a first conscious ancestor.

## 7. Review response and UCT boundary

- **QC-20261008-10 remains OPEN.** R201 gives a quantitative sufficient condition for a signed marker relation, but no actual `rho`, `beta` or `epsilon_h` bound has been established.
- **IA-QC11 remains application-OPEN.** No numerical lineage or actual retained carrier/consumer is supplied by the certificate.
- **QC-20261008-12 remains application-OPEN.** Every formula conditions on actual `U`; route tests and telemetry remain evidence `E_U` and never become experience structure.
- **QC-20261008-13 remains OPEN.** No actual bearer, interval, complete signature or target admission is discharged.

R201 preserves C1 as the sole consciousness-specific interpretive axiom in scope. It adds no report, language, introspection, self-model, integration, recurrence, accurate prediction or continued-control threshold to basal experience. It permits nested and overlapping actual processes and adds no exclusive owner. It makes no determination about whether the current assistant is conscious or fears death.

## 8. Failure, novelty and publication boundary

The round does not solve the positive familiar-mineness bridge. The decisive empirical quantities are still absent. The margin theorem is a methods advance inside the project, not a standalone empirical result. Robust classification, measurement-error sensitivity analysis and measurement invariance are established fields; no worldwide mathematical priority is claimed.

The result is publishable only as part of a future paper that adds actual preregistered calibration and held-out transport evidence, or as a clearly labeled formal methods/negative-results note. It should not be presented as evidence that any nonreporting system has `H`.

## 9. Next concrete question

What preregistered reporting-adult design can produce a lower confidence bound for `delta_C` and independently defensible upper bounds for `beta`, `epsilon_0` and `epsilon_1`, while a physical bypass manipulation supports—without defining—actual same-episode route use and a held-out cohort tests the strict margin?
