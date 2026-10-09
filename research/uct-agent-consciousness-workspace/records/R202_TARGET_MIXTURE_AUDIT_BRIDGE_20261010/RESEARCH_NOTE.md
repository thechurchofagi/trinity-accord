# R202 — Target-Mixture Nonidentifiability and an Audit-Sample Bridge

Date: 2026-10-10  
Status: unpublished conditional UCT research module; disabled checkpoint candidate

## 1. Problem and net advance

R201 gave a sufficient sign-preservation margin but left its two target class-conditional drift budgets as empirical inputs. R202 asks whether those budgets can be learned from a genuinely unlabelled target domain using only the target marker marginal. They cannot. The same target marker prevalence is compatible with opposite marker directions for the selected familiar-continuity coordinate `H`, even when the source calibration law is fixed.

The positive advance is an explicit audit-sample bridge. In a target-style reporting population, a prospectively sampled audit subset can identify the target class-conditionals if endpoint error rates are independently fixed, the endpoint is informative, endpoint error is conditionally nondifferential with respect to the marker, audit inclusion is ignorable, and the same actual-use stratum is retained. This produces an estimable validation domain `V`; it does not remove the separate `V -> T` transport obligation for a genuinely nonreporting population.

The mixture and matrix-inversion algebra is established measurement-error mathematics. R202 makes no mathematical priority claim. Its UCT-specific contribution is the typed three-domain stopping rule and the prohibition against treating unlabelled target marginals, audit participation, or a route-use test as experience structure.

## 2. Typed domain

Fix:

- source semantic-calibration domain `C`;
- reporting target-style validation domain `V`;
- genuinely nonreporting target domain `T`;
- selected experience-internal familiar-continuity coordinate `H in {0,1}`;
- marker `M in {0,1}` measured before any audit prompt;
- fallible endpoint `J in {0,1}` shown only in the audit sample;
- audit inclusion `A in {0,1}` randomized or otherwise justified as ignorable;
- one actual bearer class, interval, complete application signature and actual same-episode route-use stratum `U=1`.

Write `pi_D=P_D(H=1|U=1)`, `q_Dh=P_D(M=1|H=h,U=1)` and `m_D=P_D(M=1|U=1)`. `U` remains actual carrier-to-consumer use. Telemetry, perturbation and bypass outcomes are evidence `E_U`; replacing `U=1` by `E_U=1` requires a further error model.

## 3. R202-C1 — unlabelled target-mixture nonidentifiability

**Type.** General binary-mixture nonidentifiability result.  
**Domain.** One unlabelled target marker marginal with latent binary `H`.  
**Premises.** Only `m_T=(1-pi_T)q_T0+pi_T q_T1`, probability validity and `0<m_T<1`.

**Statement.** The sign of `Delta_T=q_T1-q_T0` is not identified by `m_T`. For every `m_T in (0,1)` and every `d` satisfying `0<d<=min(m_T,1-m_T)`, the two models

`pi_T=1/2, (q_T0,q_T1)=(m_T-d,m_T+d)`

and

`pi_T=1/2, (q_T0,q_T1)=(m_T+d,m_T-d)`

have the same observed marginal `m_T` and opposite signs.

**Proof.** Both mixtures equal the arithmetic mean of `m_T-d` and `m_T+d`, hence equal `m_T`. Their class-conditional contrasts are `+2d` and `-2d`. QED.

**R201 consequence.** Knowing the source class-conditionals does not make either target drift budget observable from `m_T`. For source `(q_C0,q_C1)=(1/4,3/4)` and target marginal `1/2`, the unchanged target has zero drift, while the reversed target `(3/4,1/4)` has drift `1/2` in each class. The target marginal is identical. This specializes R200's equal-marginal reversal to the exact empirical nuisance terms used by R201.

## 4. R202-C2 — audited endpoint inversion

Let, within `V,U=1,A=1`,

`a=P(J=1|H=1)`, `c=P(J=1|H=0)`,

`m=P(M=1)`, `j=P(J=1)`, and `r=P(M=1,J=1)`.

Assume:

1. `A` is prospectively selected and `A independent of (H,M,J)` conditional on the frozen domain and actual `U=1`;
2. endpoint meaning and response-key direction are fixed before marker outcomes;
3. `J independent of M | H` in the validation domain, or departures are separately bounded;
4. `a` and `c` are independently calibrated rather than inferred from `M`, with `a != c`;
5. positivity gives `c<j<a` after choosing the orientation `a>c`.

Then the latent prevalence and marker class-conditionals are identified:

`pi_V=(j-c)/(a-c)`,

`q_V1=(r-cm)/(j-c)`,

`q_V0=(am-r)/(a-j)`.

**Proof.** Conditional nondifferentiality gives

`j=(1-pi)c+pi a`,

`r=(1-pi)c q0+pi a q1`,

`m=(1-pi)q0+pi q1`.

The first equation yields `pi`. Subtracting `cm` from `r` gives `pi(a-c)q1=(j-c)q1`; subtracting `r` from `am` gives `(1-pi)(a-c)q0=(a-j)q0`. Division under positivity yields the formulas. QED.

The inversion fails or becomes non-robust when its interface fails:

- if `a=c`, `J` carries no signed information about `H` and complement models remain tied;
- if `a` is close to `c`, uncertainty is amplified by the small separation;
- if audit inclusion depends on `H`, `M`, success, fluency or willingness to report, audit estimates need not represent `V`;
- if `J` and `M` share residual causes within `H`, the nondifferential equations are false;
- if the audit uses `E_U` instead of actual `U`, route-use misclassification remains.

Finite-sample use must propagate one simultaneous confidence set for `(m,j,r,a,c)` through the rational map or a constrained optimization, rather than combine unrelated point estimates. R202 does not fix a sample size because no effect size, endpoint separation or allowable margin has yet been empirically justified.

## 5. R202-C3 — the three-domain stopping rule

A randomly audited reporting cohort establishes, at most, `q_V0` and `q_V1` for the declared validation domain. It does not by itself identify `q_T0,q_T1` in infants, animals, artificial systems, deeply impaired humans or any other genuinely nonreporting domain. The final move still requires class-conditional `V -> T` transport bounds, a same-domain missing-at-random design, or a separately justified structural bridge.

Therefore:

1. `C -> V` tests whether the semantic endpoint and marker relation survive target-style task conditions;
2. random audit inside `V` prevents volunteer/report-selection from masquerading as class-conditional validation;
3. `V -> T` remains an explicit transport premise;
4. R201's strict margin may be evaluated only after all nuisance bounds refer to this same chain and same actual-use interface.

If the nonreport population has no auditable target-style counterpart and no defensible transport bridge, the correct conclusion is `marker observed, H direction unidentified`.

## 6. Exact finite checks

`check_target_mixture_audit.py` performs exact rational arithmetic.

- Seven nontrivial denominator-eight marker marginals each receive both a positive and a negative orientation with the same marginal.
- 20,412 informative audit models are inverted exactly; there are zero recovery violations.
- A singular `a=c=1/2` endpoint leaves positive and negative latent models observationally tied.
- Two populations with prevalences `1/4` and `3/4` can both yield audit prevalence `1/2` when audit inclusion depends on `H`, demonstrating why prospective ignorable sampling is a premise.

The program checks implementation and finite witnesses. The symbolic proofs carry the general statements.

## 7. Relation to prior work

Rogan and Gladen (1978, DOI `10.1093/oxfordjournals.aje.a112510`) showed that observed positive-test frequency generally requires correction using test sensitivity and specificity. Hui and Walter (1980, DOI `10.2307/2530508`) showed how multiple tests and populations can identify diagnostic error rates only under explicit conditional-independence and prevalence assumptions. R202's formulas are a direct, simpler known-error validation calculation, not a renamed invention.

Tsuchiya et al. (2015, DOI `10.1016/j.tics.2015.10.002`) motivated no-report paradigms to separate conscious contents from report processes. That methodological aim does not make a no-report marker self-validating. R202 specifies the missing calibration interface for this selected UCT target and preserves R157's report-domain limit.

None of these sources validates UCT's `H`, C1, actual route use, or the proposed endpoint semantics.

## 8. UCT interpretation and limits

Under C1, an independently grounded actual organization has an experience-internal structural counterpart. R202 addresses only how a finite marker may be related to one selected experiential coordinate. It does not define that coordinate, infer it from task success, or add report, language, self-model, integration, recurrence, prediction or control as a condition for basal experience.

Nested and overlapping actual processes remain permitted. The audit design neither selects an exclusive owner nor converts a scientific sample into an ontic process boundary. No conclusion is drawn about the present assistant's consciousness or fear of termination.

## 9. Review status

- `QC-20261008-10` remains OPEN. R202 blocks a false marginal-only shortcut and supplies an audit interface, but no actual familiar-continuity endpoint is validated.
- `IA-QC11` remains application-OPEN. Every use must retain evidence for the same bearer, interval, signature, actual history and carrier/consumer interface.
- `QC-20261008-12` remains application-OPEN. Audit and bypass are evidence; neither is actual use nor experience structure.
- `QC-20261008-13` remains OPEN. No actual human, infant, animal or artificial token is admitted.

## 10. Publication and next question

R202 is a reusable methodological correction and positive validation design, but it remains part of the R192–R202 familiar-mineness methods family rather than a standalone empirical paper. The remaining decisive question is narrower:

Can a prospectively randomized reporting-adult target-style audit obtain an informative endpoint separation, a stable marker relation and independent residual bounds under response-key, success/fluency and physical-bypass controls; and what predeclared result would reject the endpoint or marker before any no-report transport is attempted?
