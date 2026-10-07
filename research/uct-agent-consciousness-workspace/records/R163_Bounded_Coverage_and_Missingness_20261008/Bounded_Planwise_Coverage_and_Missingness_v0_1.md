# Bounded Planwise Coverage, Order Targets, Clipping, and Missingness

Version 0.1, 8 October 2026. Research checkpoint; not a published edition, an ethics approval, a recruitment plan, or evidence that the R161 apparatus has been built or run.

## 1. Question and result

R162 made planwise conditional coverage an explicit premise of any independently frozen confirmatory design. It proposed a Bonferroni Student fallback under complete i.i.d. multivariate-Gaussian participant vectors. R161 and R162, however, define the actually analysed vector as

\[
W_i\in[-1,1]^8.
\]

This round asks which finite-sample procedure can discharge the coverage premise for that bounded vector under skewness, clipping, order effects, and missingness without changing the target silently.

The result has six parts.

1. An exactly bounded random vector cannot have a non-degenerate multivariate-Gaussian law. Therefore R162's Gaussian fallback does not discharge coverage for the declared observed \(W_i\), except in the degenerate zero-variance case or after an explicit change to an unbounded latent/pre-clipping target.
2. Student–Bonferroni is not a distribution-free bounded-data fallback. An exact two-point counterexample at \(N=36\) gives only `.2531493944` simultaneous coverage across eight independent components at nominal `.95`.
3. For independent participant vectors with components in \([-1,1]\), simultaneous Bonferroni–Hoeffding intervals cover the componentwise finite-design means with probability at least \(1-\alpha\), without Gaussianity, identical participant laws, component independence, or estimated variances.
4. That guarantee is conservative: with \(m=8\), \(\alpha=.05\), simultaneous half-width `.05` requires at least `4615` independent participant vectors.
5. Random order can identify a frozen randomized-order mixture mean; it does not identify an order-invariant or canonical-order effect. Clipped observations identify clipped means, not latent means.
6. Under arbitrary outcome-dependent missingness, complete-case inference does not target the all-enrollee mean. If every enrollee's would-be bounded outcome is well-defined, a worst-case partial-identification band plus Hoeffding uncertainty is valid but can be nearly uninformative. If safety abort makes the outcome undefined, even that full-data target is unavailable.

The positive design result is therefore real but narrow: R163 supplies a valid finite-sample coverage bridge for a fixed bounded target, while refusing to convert statistical coverage into a claim about basal experience, familiar ownership, a unique subject, or a canonical order-independent body effect.

## 2. Correction to the R162 Gaussian fallback

### Proposition R163-P1: bounded/non-degenerate-Gaussian incompatibility

Let \(W\) be a multivariate Gaussian vector. If any component \(W_j\) has variance \(\sigma_j^2>0\), then its marginal law is a non-degenerate univariate Gaussian and

\[
\Pr(|W_j|>1)>0.
\]

Hence \(\Pr(W\in[-1,1]^m)=1\) implies \(\operatorname{Var}(W_j)=0\) for every component. The covariance matrix is zero and the law is a point mass. \(\square\)

R162's Student proof is mathematically correct for an unbounded complete Gaussian vector, but that model is incompatible with the observed bounded vector it was said to validate. Independence of the pilot does not repair the mismatch. The effective correction is:

- preserve `R162:PLANWISE_COVERAGE_PREMISE` and the tower-property theorem;
- withdraw the claim that exact Gaussian Student intervals discharge the premise for non-degenerate observed \(W_i\in[-1,1]^8\);
- retain Gaussian calculations only as an explicitly approximate or latent-variable scenario, never as exact finite-sample certification for the clipped vector;
- use the bounded theorem below for an exact observed-target fallback.

This is a correction of a premise discharge, not a deletion of R162's history.

## 3. Exact bounded counterexample to Student–Bonferroni

Let one component have

\[
X=\begin{cases}
1,&\text{with probability }p=.05,\\
-p/(1-p)=-1/19,&\text{with probability }.95.
\end{cases}
\]

Then \(X\in[-1,1]\) and \(\mathbb E X=0\). For a sample of size \(N\), the sample mean and variance depend only on the binomial count \(K\sim\operatorname{Binomial}(N,.05)\). Exact enumeration of all \(K=0,\ldots,N\), using the Student critical value \(t_{1-\alpha/(2m),N-1}\), gives:

| N | exact marginal coverage | exact 8-component simultaneous coverage | no-spike probability |
|---:|---:|---:|---:|
| 24 | 0.7080096925 | 0.0631413154 | 0.2919890243 |
| 36 | 0.8422133314 | 0.2531493944 | 0.1577792148 |
| 60 | 0.9538942240 | 0.6854909926 | 0.0460697990 |
| 120 | 0.9423904243 | 0.6220809707 | 0.0021224264 |

The eight components are independent in this witness, so the simultaneous value is the eighth power of marginal coverage. At \(N=36\), a zero-spike sample has zero sample variance and produces a point interval at \(-1/19\), missing the true mean zero. Other binomial counts also determine the non-monotone finite-sample coverage.

This exact counterexample is enough to reject Student–Bonferroni as a universal bounded-data solution. A fixed-seed diagnostic with `2*Beta(.35,2)-1` at \(N=36\) gave simultaneous coverage `.8457` over 20,000 replications; it is supporting stress evidence, not a proof.

## 4. A valid bounded finite-sample alternative

### Definition R163-D1: frozen bounded finite-design target

Fix one confirmatory plan before viewing confirmatory outcomes. Let participants \(i=1,\ldots,N\) be independent. Participant laws may differ because the plan may contain fixed positions, sessions, or strata. For each component \(j=1,\ldots,m\), assume only

\[
W_{ij}\in[-1,1]\quad\text{almost surely}.
\]

The finite-design target is

\[
\theta_{Nj}=\frac1N\sum_{i=1}^N\mathbb E[W_{ij}],
\]

where the expectation includes the frozen randomization distribution, if any. Under i.i.d. sampling this reduces to the common superpopulation mean.

### Theorem R163-P2: simultaneous bounded planwise coverage

Set

\[
h_N=\sqrt{\frac{2\log(2m/\alpha)}{N}},
\qquad
I_j=[\bar W_j-h_N,\bar W_j+h_N]\cap[-1,1].
\]

Then

\[
\Pr\{\theta_{Nj}\in I_j\text{ for every }j=1,\ldots,m\}\ge 1-\alpha.
\]

**Proof.** Hoeffding's inequality for independent, not necessarily identically distributed variables with range length two yields

\[
\Pr\{ |\bar W_j-\theta_{Nj}|\ge h_N\}
\le 2\exp(-Nh_N^2/2)=\alpha/m.
\]

The union bound over \(m\) components gives total failure probability at most \(\alpha\). No independence among components within a participant is used. Intersecting with \([-1,1]\) cannot remove the true bounded mean. \(\square\)

If an independent pilot selects \(N\), a fixed randomization schedule, and a member of this declared bounded family, every selected plan has the displayed conditional guarantee. R162's tower-property theorem then transports planwise coverage to unconditional coverage. Pilot independence remains necessary for that simple transport, but the coverage proof comes from boundedness and participant independence, not from the word “independent.”

For \(m=8\), \(\alpha=.05\), and desired \(h_N\le.05\),

\[
N\ge\left\lceil\frac{2\log(320)}{.05^2}\right\rceil=4615.
\]

Thus the theorem certifies error but does not make the design practical. It can instead justify a wider interval, a different scientifically defended effect scale, or `DESIGN_NOT_FEASIBLE`. It cannot justify substituting an unvalidated narrow interval.

## 5. Candidate interval disposition

| Candidate | R163 disposition | Exact premise needed | Why it is not silently inherited |
|---|---|---|---|
| Student–Bonferroni | rejected as universal bounded fallback | exact normal marginals or a separately justified approximation | exact rare-spike counterexample; exact bounded/non-degenerate-Gaussian conflict |
| sign-flip/randomization | rejected as universal mean interval | invariance/symmetry under the null, or a sharp treatment-randomization null matching the target | bounded skew alone supplies neither; random assignment labels do not make arbitrary observed contrasts sign-symmetric |
| participant bootstrap/max-`t` | retained as a candidate only | a frozen resampling algorithm plus scenario-specific or asymptotic calibration for the actual target and missingness rule | resampling is not a finite-sample coverage theorem for every bounded law |
| Bonferroni–Hoeffding | accepted as exact observed-target fallback | independent participant vectors; fixed bounded components; frozen target/plan | distribution-free finite-sample proof, but wide |
| worst-case missingness band plus Hoeffding | accepted conditionally | well-defined bounded would-be outcomes for every enrollee; independent participants | covers a partial-identification region, not a point-identified effect |

Sign-flipping can be exact when the null distribution is invariant under the sign group; Canay, Romano and Shaikh explicitly locate finite-sample randomization validity in such invariance. It is not licensed merely because session order was randomized. Bootstrap methods can be valuable for efficiency, but they require a separate calibration claim and cannot be promoted to `R162:PLANWISE_COVERAGE_PREMISE` by simulation success alone.

## 6. Order effects: freeze the estimand

Suppose \(O\in\{-1,+1\}\) records order and

\[
W=.4O+\varepsilon,qquad \mathbb E[\varepsilon\mid O]=0.
\]

Under balanced randomized order, the mixture target is \(\mathbb E W=0\). Under canonical order \(O=+1\), the target is `.4`. A valid interval for the former does not entail coverage of the latter. The bounded theorem remains valid when order affects outcomes if either:

1. order is fixed and the finite-design target averages over those fixed participant positions; or
2. order is randomized according to a frozen distribution and the target explicitly averages over that randomization.

It does not establish order invariance. The protocol must report conditional order effects or declare its mixture target. “Randomized order” is a design description, not an eraser of order dependence.

## 7. Clipping: observed and latent targets differ

Let \(W=\operatorname{clip}(Z,-1,1)\). Two latent laws, \(Z=2\) almost surely and \(Z=100\) almost surely, induce the identical observed law \(W=1\) almost surely while having latent means 2 and 100. Therefore no estimator based only on clipped \(W\) identifies \(\mathbb E Z\) over this model class.

Hoeffding intervals cover \(\mathbb E W\), the clipped observed target. They do not recover latent displacement, latent salience, or an unclipped “true” bodily effect. If saturation is scientifically unacceptable, the remedy is apparatus redesign or an independently justified measurement model, not relabeling the clipped interval.

## 8. Arbitrary missingness

Let \(Y_{ij}\in[-1,1]\) be participant \(i\)'s well-defined would-be complete outcome and \(R_{ij}\in\{0,1\}\) indicate observation. No missing-at-random assumption is made. Define observed lower and upper variables

\[
L_{ij}=R_{ij}Y_{ij}-(1-R_{ij}),
\qquad
U_{ij}=R_{ij}Y_{ij}+(1-R_{ij}).
\]

Pointwise,

\[
L_{ij}\le Y_{ij}\le U_{ij}.
\]

### Theorem R163-P3: worst-case missingness confidence band

For independent participants and frozen \(m\)-component outcomes, let the same \(h_N\) as §4 be used and define

\[
J_j=[\bar L_j-h_N,\bar U_j+h_N]\cap[-1,1].
\]

Then, simultaneously for every component,

\[
\Pr\{\theta^Y_{Nj}\in J_j\text{ for all }j\}\ge1-\alpha,
\quad
\theta^Y_{Nj}=N^{-1}\sum_i\mathbb E[Y_{ij}].
\]

**Proof.** The lower failure event is \(\bar L_j-h_N>\mathbb E L_j\), and the upper failure event is \(\bar U_j+h_N<\mathbb E U_j\). Each one-sided Hoeffding probability is at most \(\exp(-Nh_N^2/2)=\alpha/(2m)\). Union-bound the \(2m\) events and use \(\mathbb E L_j\le\theta^Y_{Nj}\le\mathbb E U_j\). \(\square\)

The sample identification width before sampling uncertainty is

\[
\bar U_j-\bar L_j=2(1-\bar R_j).
\]

Thus arbitrary missingness rapidly destroys resolution. In the saved MNAR diagnostic, `R=1[Y<=-.2]` makes complete-case Student simultaneous coverage for the full-data mean exactly `0.0` over 20,000 fixed-seed replications, while the worst-case band covers in all replications but is very wide. These are diagnostics; the theorem supplies the guarantee.

If a safety stop means that \(Y_{ij}\) is not merely unobserved but physically undefined, the full-data estimand itself is invalid. The correct output is a safety/feasibility status or a different explicitly defined treatment-policy estimand, not imputation of a nonexistent token.

## 9. R161 decision and limits of the repair

The signed bounded intervals may be transformed to magnitude intervals by R162's exact interval-image map, and then passed into R161's fixed min/max aggregation. The resulting confirm/exclude/unresolved decision inherits simultaneous coverage only if all of the following hold together:

1. the eight signed components and their order are frozen;
2. each actual analysed component lies in \([-1,1]\);
3. participant vectors are independent under the chosen target/design;
4. no same-data procedure chooses among interval families or targets;
5. all six R161 physical and measurement gates pass;
6. missingness is handled by the stated target-specific rule;
7. order and clipping interpretations do not exceed the frozen estimand.

This repair does not validate tendon selectivity, readout construct validity, normalization, the dominance margin \(\epsilon\), or ethical feasibility. It does not establish a complete organization, a single \(h\), `B_min`, familiar ownership `F_O`, basal experience, report accuracy, or a unique additional owner.

## 10. Retained thought experiments

- **Ancestor/formation.** A creature can possess bounded tendon-sensitive localization before tool learning or language. The coverage theorem concerns how later investigators estimate physical effects; it does not add a threshold for the creature's experience.
- **Abacus/calculator.** Two devices can produce identical clipped outputs while their latent mechanical displacements differ without bound. Role: clipping non-identification and observed/latent target separation.
- **Human-realized agent.** Replacing independent participants with interdependent members of one coordinated human system violates the participant-independence premise even if every recorded score remains bounded. Role: actual bearer and dependence test.
- **Copy/swap/memory.** Copy the same bounded observations, change only the order assignment or delete high outcomes. The observed range is unchanged while the target or selection bias changes. Role: target-freeze and missingness counterexample; no claim of phenomenal transfer.

## 11. Relation to UCT and felt mineness

R163 is methodological support for a finite physical attribution test. Conditional on actual token organization and A:C1, the experiment may constrain whether body-related or tool-related role profiles are present. Its population-level interval does not itself belong to a particular experience, and its validity does not entail that a report, self-model, concept of self, or continuation-control policy is present.

The round therefore preserves the intended hierarchy:

- actual organization and tokenwise physical relations;
- finite measurements generated by an installed protocol;
- a frozen statistical target over such measurements;
- a cautious physical-role classification;
- only then a separately licensed experience-level interpretation.

Felt mineness remains to be explained within experience. Statistical precision neither creates nor selects an extra exclusive owner.

## 12. Failures and next question

The exact repair is conservative, depends on participant independence, and may be unusable at scientifically interesting resolution. The arbitrary-missingness band assumes well-defined complete outcomes and can be nearly vacuous. Order-mixture targets may answer the wrong scientific question. Clipping blocks latent recovery. Bootstrap, empirical-Bernstein, permutation, and covariance-adaptive alternatives remain uncertified for the exact R161 decision.

The next concrete question is: **Can a predeclared empirical-Bernstein or bounded-martingale simultaneous interval materially reduce the R163 width while retaining finite-sample planwise validity for independent, non-identically distributed participant vectors and the exact R161 min/max decision, including a separately typed missingness target?** Any answer must be compared against the R163 rare-spike law and may not infer order invariance, latent unclipped effects, or experience-level sufficiency.

## 13. Sources and attribution

- Hoeffding, W. (1963), “Probability Inequalities for Sums of Bounded Random Variables,” *Journal of the American Statistical Association* 58(301):13–30, DOI `10.1080/01621459.1963.10500830`, supplies the established bounded-sum inequality. R163's contribution is its typed application to the frozen R161/R162 target.
- Manski, C. F. (1989), “Anatomy of the Selection Problem,” *Journal of Human Resources* 24(3):343–360, supplies established support-bounds reasoning under selective observation. The displayed \(L/U\) construction and simultaneous Hoeffding layer are proved here for the R161 bounded target.
- Canay, I. A., Romano, J. P., and Shaikh, A. M. (2017), “Randomization Tests Under an Approximate Symmetry Assumption,” *Econometrica* 85(3):1013–1030, distinguishes finite-sample randomization validity under invariance from broader approximate validity.
- Owen, A. B. (2025), “Coverage errors for Student's t confidence intervals comparable to those in Hall (1988),” arXiv:`2501.07645`, supplies modern primary asymptotic context for skewness-dependent Student coverage error. R163's decisive witness is instead exact finite enumeration.
- UCT I v1.2 §§8.11–8.14, 10.1–10.3, 11, 12.1–12.4 and 14.6–14.10 supply the actual-process, bridge, no-rescue, subject/self and method boundaries.
