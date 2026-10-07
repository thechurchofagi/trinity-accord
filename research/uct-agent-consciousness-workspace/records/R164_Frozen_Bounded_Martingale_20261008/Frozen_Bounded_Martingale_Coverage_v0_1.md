# Frozen Bounded-Martingale Coverage for a Finite-Design Mean

Version 0.1, 8 October 2026. Research checkpoint; not a published edition, an experimental result, an ethics approval, a recruitment plan, or evidence that the R161 apparatus has been built.

## 1. Question and result

R163 supplied an exact but conservative Bonferroni–Hoeffding fallback for the frozen bounded vector (W_i\in[-1,1]^8). It left one concrete question: can a predeclared variance-adaptive method be narrower without losing finite-sample planwise validity for independent, non-identically distributed confirmatory participants?

The answer is conditional but positive.

1. The classical Maurer–Pontil empirical-Bernstein interval is an i.i.d. result. It cannot simply be relabelled as a theorem for R163's non-identically distributed finite-design mean.
2. A predictable-plug-in empirical-Bernstein confidence sequence for a common conditional mean also does not, with varying bets, automatically target the unweighted average of unequal participant means.
3. Freezing one constant positive bet per component repairs the target. The same one-step exponential inequality then yields an exact finite-sample interval for the average conditional mean. Under independent confirmatory participant vectors, this average is exactly R163's finite-design target.
4. Bonferroni union over the eight components retains the exact R161 signed-component coverage event. The already established interval-image and monotone min/max steps therefore remain valid.
5. The method can be materially narrower in low-residual-variation cases, but is not uniformly narrower than Hoeffding. With (m=8,\alpha=.05,\lambda=.9), a zero-residual half-width at (N=120) is about `.10682`, versus Hoeffding `.31006`; at (N=36), the R163 rare-spike expected half-width is about `.39708`, versus `.56609`.
6. The R163 rare-spike witness proves that zero empirical variance cannot license a zero-width interval. At (N=36,m=8), the probability that at least one coordinate shows no spike is `.7468326816`. A valid method needs an additive rare-event term or an equivalent widening device.
7. Applying the construction to lower and upper missingness endpoints can reduce sampling uncertainty, but cannot reduce the support-based identification width (2(1-\bar R_j)). Undefined post-abort outcomes remain outside that estimand.

The gain is statistical efficiency for one fixed finite physical protocol. It is not an experience criterion and does not establish bodily mineness, familiar ownership, C1, a complete organization, or an exclusive owner.

## 2. Objects, target and frozen plan

Fix a confirmatory sample size (N\), component count (m\), familywise error (\alpha\in(0,1)), and participant filtration

\[
\mathcal F_i=\sigma(W_1,\ldots,W_i).
\]

For participant (i) and component (j), let

\[
W_{ij}\in[-1,1],\qquad X_{ij}=\frac{W_{ij}+1}{2}\in[0,1].
\]

Define the conditional mean and its average by

\[
\mu_{ij}=\mathbb E[X_{ij}\mid\mathcal F_{i-1}],
\qquad
\bar\mu_{Nj}=\frac1N\sum_{i=1}^N\mu_{ij}.
\]

The corresponding (W)-scale target is

\[
\vartheta_{Nj}=2\bar\mu_{Nj}-1.
\]

For R163's independent participant vectors, 

\[
\mu_{ij}=\mathbb E X_{ij},\qquad
\vartheta_{Nj}=\frac1N\sum_i\mathbb E W_{ij}=\theta_{Nj}.
\]

Thus the theorem below has a martingale form and an exact independent finite-design specialization. Under general dependence, (\bar\mu_{Nj}) can be random; calling it a fixed superpopulation mean would be a target error.

Before confirmatory outcomes are viewed, freeze for each component:

- a constant bet (\lambda_j\in(0,1));
- a predictor rule (c_{ij}\in[0,1]) that is (\mathcal F_{i-1})-measurable;
- the sample order and all component definitions.

An independent nuisance-only pilot may select these objects from a predeclared family. Conditional on the pilot they are fixed/predictable, so R162's tower argument applies. Pilot independence does not prove the interval; the exponential inequality does.

For transparent order invariance in the saved candidate, use a pilot-frozen constant (c_{ij}=c_j). A running predictor is also mathematically allowed, but then the realized width depends on processing order and must be treated as part of the frozen procedure.

## 3. Why two familiar routes do not directly answer the question

### 3.1 Classical sample-variance empirical Bernstein

Maurer and Pontil's Theorem 4 controls an i.i.d. mean using the ordinary sample variance. Its data-dependent width is valuable, but the i.i.d. premise is stronger than R163's independent, non-identically distributed participant-vector premise. Importing the formula without that premise would repeat R162's earlier model/target mismatch.

### 3.2 Common-mean predictable betting

Waudby-Smith and Ramdas prove a predictable-plug-in empirical-Bernstein confidence sequence when

\[
\mathbb E[X_i\mid\mathcal F_{i-1}]=\mu
\quad\text{for every }i.
\]

With varying predictable bets (\lambda_i), the center is a weighted mean. If the conditional means vary, the naturally matched target is also weighted. R163 instead fixed the unweighted finite-design target. The correction is not to pretend the means are equal, but to use one constant bet over the confirmatory observations. Then the weighted target reduces exactly to the unweighted average conditional mean.

## 4. Constant-bet bounded-martingale theorem

Let

\[
g(\lambda)=-\log(1-\lambda)-\lambda,
\qquad 0<\lambda<1,
\]

and define the predictable residual sum

\[
V_{Nj}=\sum_{i=1}^N(X_{ij}-c_{ij})^2.
\]

### Theorem R164-P1: one-component average-conditional-mean interval

For any fixed component (j), frozen constant (\lambda_j\in(0,1)), and predictable (c_{ij}\in[0,1]),

\[
\Pr\left\{
\left|\bar X_j-\bar\mu_{Nj}\right|
\le
\frac{\log(2/\delta)+g(\lambda_j)V_{Nj}}{N\lambda_j}
\right\}\ge1-\delta.
\]

Equivalently on the (W) scale,

\[
I_j=
\left[
\bar W_j-h_j,\bar W_j+h_j
\right]\cap[-1,1],
\quad
h_j=
\frac{2\{\log(2/\delta)+g(\lambda_j)V_{Nj}\}}{N\lambda_j}
\]

covers (\vartheta_{Nj}) with probability at least (1-\delta).

**Proof.** The Fan/Howard one-step inequality used by Waudby-Smith and Ramdas gives

\[
\mathbb E\!\left[
\exp\{\lambda_j(X_{ij}-\mu_{ij})
-g(\lambda_j)(X_{ij}-c_{ij})^2\}
\mid\mathcal F_{i-1}
\right]\le1.
\]

Multiplying the factors produces a nonnegative supermartingale. Markov's inequality at the fixed time (N) gives a one-sided error (\delta/2) at boundary (\log(2/\delta)). Apply the same argument to (1-X_{ij}), with predictor (1-c_{ij}), and union-bound the two tails. Constancy of (\lambda_j) changes the exponent's linear term to

\[
\lambda_j N(\bar X_j-\bar\mu_{Nj}),
\]

which is precisely why the unweighted average target is preserved. The affine map (W=2X-1) doubles the half-width. Intersecting with ([-1,1]) cannot remove the bounded target. \(\square\)

This proof is a fixed-time corollary of an established bounded-supermartingale method, not a claim of new concentration mathematics.

### Corollary R164-P2: simultaneous finite-design coverage

Set (\delta=\alpha/m), so

\[
L=\log(2m/\alpha).
\]

Then

\[
\Pr\{\vartheta_{Nj}\in I_j\text{ for every }j=1,\ldots,m\}
\ge1-\alpha.
\]

No within-participant component independence is used. Under independent participant vectors, (\vartheta_{Nj}=\theta_{Nj}), the R163 finite-design mean. If an independent pilot selects (N,c_j,\lambda_j) and a plan from the declared family, the displayed guarantee holds conditional on every selected plan and hence unconditionally by R162's tower argument.

## 5. Relation to the exact R161 min/max decision

R162 already supplies the exact image of a signed interval under (x\mapsto|x|). On the event that all eight signed means lie in their R164 intervals, every true magnitude lies in the corresponding image interval. R161's diagonal minima and cross-effect maxima are monotone set operations on those component intervals. Therefore its confirm/exclude/unresolved rule remains conservative on the same simultaneous event.

This statement requires all premises together:

1. the R161 components, signs, order and normalization are frozen;
2. actual analysed (W_{ij}) are bounded in ([-1,1]);
3. the constant bets and predictor rules are pilot-frozen or otherwise preregistered;
4. confirmatory participants are independent for the fixed R163 target, or the claim is explicitly changed to the average conditional mean;
5. no same-confirmatory-data search selects among bet families, targets or reported intervals;
6. all six R161 physical/measurement gates pass;
7. missingness uses the separately typed construction in §8.

Nothing here validates tendon selectivity, measurement meaning, (\epsilon), apparatus fidelity, practical recruitment or experience-level interpretation.

## 6. Efficiency is conditional, not uniform

For (m=8,\alpha=.05\), (L=\log(320)\). With (\lambda=.9\), a zero-residual component has

\[
h_0=\frac{2L}{.9N}.
\]

At (N=120), (h_0=.1068208\), compared with R163 Hoeffding (h_H=.3100624\). A half-width at most `.05` requires (N\ge257) in this zero-residual case, compared with (4615) for the range-only Hoeffding guarantee.

This is not a uniform sample-size reduction. The realized penalty (g(\lambda)V_N) can make the interval wider than Hoeffding when the predictor is poor or residual variation is high. Selection of (c_j\) and (\lambda_j\) must be independent of confirmatory outcomes or performed by a theorem that explicitly permits the relevant predictable weighting while preserving the intended target.

## 7. Exact rare-spike obstruction and stress test

Reuse R163's mean-zero component:

\[
W=1\text{ with probability }.05,
\qquad
W=-1/19\text{ with probability }.95.
\]

If no spike occurs, the sample variance is zero and (\bar W=-1/19\). Any coordinatewise interval centered at (\bar W\) with half-width less than (1/19) excludes the true mean zero on that event. For (m) independent copies, any procedure with this same all-no-spike failure property has simultaneous coverage at most

\[
\{1-.95^N\}^{m}.
\]

At (N=36,m=8), the upper bound is `.2531673184`; equivalently, at least one coordinate has no spike with probability `.7468326816`. To make this event alone have probability at most `.05`, one needs

\[
N\ge
\left\lceil
\frac{\log(1-.95^{1/8})}{\log(.95)}
\right\rceil
=99.
\]

This does not say that (N=99) is sufficient for a desired interval. It proves that zero sample variance cannot remove all rare-event protection before that point. The additive (L/(N\lambda)) term in R164 is therefore a feature, not avoidable slack.

The saved exact enumeration uses (c=.5,\lambda=.9\). At (N=36), every possible binomial spike count contains zero in the R164 interval; the expected half-width is `.3970804573`, below Hoeffding `.5660938770`. At (N=120), expected half-width is `.1478320192`, below Hoeffding `.3100623861`. These distribution-specific exact checks do not replace the analytic coverage theorem.

## 8. Arbitrary missingness remains a separate target

Retain R163's well-defined would-be complete outcome (Y_{ij}\in[-1,1]), observation indicator (R_{ij}), and pointwise endpoints

\[
L_{ij}=R_{ij}Y_{ij}-(1-R_{ij}),
\qquad
U_{ij}=R_{ij}Y_{ij}+(1-R_{ij}).
\]

Apply Theorem R164-P1 separately to the (2m) endpoint variables, using independently frozen endpoint bets/predictors and per-tail union allocation (\alpha/(2m)). This changes the logarithmic factor to (\log(4m/\alpha)). If (h^L_j,h^U_j) are the resulting (W)-scale half-widths, then

\[
J_j=[\bar L_j-h^L_j,\bar U_j+h^U_j]\cap[-1,1]
\]

simultaneously covers every all-enrollee finite-design mean with probability at least (1-\alpha).

The point-identification width before sampling uncertainty remains exactly

\[
\bar U_j-\bar L_j=2(1-\bar R_j).
\]

No concentration inequality can erase it without a missingness assumption or a different estimand. If a safety stop makes (Y_{ij}) physically undefined, the displayed full-data target does not exist and this band is inapplicable.

## 9. Retained thought-experiment roles

- **Ancestor/formation.** A low-variation bodily localization process can exist before language or self-model. A narrower investigator interval does not add an experience threshold.
- **Abacus/calculator.** A stable device can have nearly deterministic bounded output and hence a narrow R164 interval, while another device has the same mean and rare large deviations. Equal means and widths do not identify mechanisms.
- **Human-realized agent.** Treating coordinated humans as independent participant vectors can invalidate the fixed finite-design specialization; bounded scores do not imply independence.
- **Copy/swap/memory.** Copy all observations but change the pilot-frozen predictor, bet, processing order or missingness pattern. The target can remain fixed while width changes, or the target can change while boundedness remains. This blocks procedure/estimand conflation and makes no claim of phenomenal transfer.

## 10. Relation to UCT and the beginner principle

UCT I requires physical witnesses, declared targets, frozen views and no post-hoc rescue. R164 improves the error model for one finite physical-view test. It does not turn a population statistic into a token experience. Conditional on actual token organization and C1, a valid protocol may constrain a selected physical role profile; a separately justified bridge remains necessary for bodily mineness or familiar ownership.

Basic experience is not made conditional on variance estimation, report, language, self-model, integration, recursion, accurate prediction or continuation control. Actual nested/overlapping processes remain allowed. No unique additional owner is sought. The conceptual “I” remains later organization within experience.

## 11. Failures, boundaries and next question

The main failures/boundaries are explicit.

- Classical i.i.d. empirical Bernstein does not answer the non-identical finite-design question without a stronger sampling model.
- Variable predictable bets generally change the target to a weighted mean when participant conditional means differ.
- The constant-bet repair can be wider than Hoeffding and depends on a defensible frozen predictor/bet.
- The rare-spike law forces a nonzero additive protection term.
- Endpoint adaptation cannot repair arbitrary-missingness identification width.
- No actual participants, apparatus, physical-role witness, (B_{min}), (F_O), or phenomenal result has been supplied.

The next exact question is: **How should an independent pilot choose a finite menu of constant bets and predictor centers under a declared maximum-width/regret criterion, while preserving the R164 target and preventing same-data method selection, and when should the result be `DESIGN_NOT_FEASIBLE` rather than a post-hoc interval switch?**

## 12. Sources and attribution

- Maurer, A. and Pontil, M. (2009), “Empirical Bernstein Bounds and Sample Variance Penalization,” COLT / arXiv:0907.3740. Established i.i.d. sample-variance empirical-Bernstein bounds; used here to mark the i.i.d. boundary.
- Howard, S. R., Ramdas, A., McAuliffe, J. and Sekhon, J. (2021), “Time-uniform, nonparametric, nonasymptotic confidence sequences,” *Annals of Statistics* 49(2), DOI `10.1214/20-AOS1991`. Established bounded empirical-Bernstein supermartingale methods and predictable variance processes.
- Waudby-Smith, I. and Ramdas, A. (2024), “Estimating means of bounded random variables by betting,” *JRSS B* 86(1):1–27; arXiv:2010.09686v7 (2022). Theorem 2 and its proof supply the predictable-plug-in exponential inequality. R164's constant-bet average-conditional-mean corollary is derived explicitly here and is not attributed to them as a protocol-specific claim.
- UCT I v1.2 fixed repository source, §§8.11–8.14, 10.1–10.3, 11, 12.1–12.4, 14.6–14.10. Supplies the physical-witness, target, bridge, no-rescue and self/subject boundaries, not the statistical theorem.
- Fixed R161–R163 repository records supply the bounded eight-component protocol, exact decision, pilot-freeze contract, finite-design target, Hoeffding fallback, rare-spike witness and missingness endpoints.
