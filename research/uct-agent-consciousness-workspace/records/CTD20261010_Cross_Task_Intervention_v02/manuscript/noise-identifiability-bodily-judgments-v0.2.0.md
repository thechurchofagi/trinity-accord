---
title: "Identifiability of Noise Sources in Bodily Judgments"
subtitle: "A computational audit of parietal stimulation and a conditional paired-readout design"
author: "Hongju Liu"
date: "10 October 2026 · CTD-PAPER-v0.2.0"
lang: en
fontsize: 11pt
geometry: margin=25mm
colorlinks: true
linkcolor: NavyBlue
urlcolor: NavyBlue
toc: false
---

**Affiliation:** Independent researcher, Shenzhen, China.

**Article type and status:** Methods and retrospective secondary analysis; author-review manuscript, not externally peer reviewed. This revision belongs to the CTD paper series and supersedes v0.1 as its main research argument. No new human participants or neural interventions were studied. No DOI has been assigned to this edition.

# Abstract

Changes in temporal response curves after brain stimulation do not by themselves locate the changing variability within a sensory or decision process. We examine this distinction in the public body-ownership and simultaneity experiment of D'Angelo et al. (2026; 30 participants, 12,600 binary judgments). Recomputing the released Bayesian causal-inference likelihoods reproduces all saved objectives within $2\times10^{-9}$. An information-criterion sign discrepancy is traced through the public code and all 30 source-data rows; correcting it preserves the aggregate preference for the noise-varying model. A parameter-free conditional test nevertheless rejects a mandatory zero-centered symmetry constraint of both released model families under their independent-binomial observation law (deviance 984.304; 19,999 conditional simulations; plus-one $p=.00005$). Adding task-specific centers improves prediction under a fixed five-fold within-cell partition; the noise-varying family with task-specific centers has lower held-out NLL than its prior-varying counterpart by 60.885 (mean participant difference −2.029; descriptive 95% interval −3.268 to −0.791). Building on established sensory/criterion-noise models, we construct a constant-sensory-variance, variable-criterion implementation that preserves every marginal probability of the released noise-varying observer, including its condition-specific threshold policy. All 1,260 fitted count-cell probabilities agree within $2.23\times10^{-16}$. We then derive a conditional repair: with calibrated marginal parameters, one shared internal sensory draw, and independent decision and lapse processes, one additional population joint-response probability identifies shared variance. Allowing bounded criterion correlation yields a sharp interval instead; near zero shared variance, centered observations have only second-order sensitivity. The contribution is a source-specific, reproducible separation of model comparison, model adequacy, and implementation identification, with an explicit additional-measurement contract. It does not identify an anatomical mediator or validate a theory of subjective experience.

**Keywords:** body ownership; simultaneity judgment; identifiability; criterion variability; Bayesian causal inference; model audit; joint responses.

# 1. The identification question

The same observable behavior can arise through different information routes. Finite source-consumer models make this problem especially clear: a successful action and an accurate prediction need not use the same source [10]. In human bodily judgments, the corresponding empirical question is harder. An intervention can change reports, a response model can explain those changes, and its fitted parameters can carry psychological names; none of these steps alone establishes where the changing variability is physically generated.

D'Angelo et al. [1] provide an unusually useful test case. Their Experiment 3 manipulated parietal transcranial alternating current stimulation (tACS) and measured ownership and visuotactile simultaneity judgments. Their computational comparison favored a model in which stimulation changes a shared sensory-uncertainty parameter over one in which stimulation changes common-cause priors. We examine the inferential step from that response-model comparison to a sensory implementation. We do not reassign authorship of the intervention, the original findings, or the underlying causal-inference framework.

The ambiguity is established science. Yarrow et al. [2,3] showed that timing-response curves depend on decision criteria as well as sensory variables, including sums of sensory and criterion variances. Cabrera, Lu, and Dosher [4] used joint-response constraints to separate encoding and decision noise in a different paradigm. Chancel, Ehrsson, and Ma [5] developed the body-ownership observer lineage, including a location-bias variant. We neither introduce Gaussian noise addition nor claim the first use of joint behavior for noise identification.

Our contribution is a concrete identification audit of the released stimulation observer. It has three linked parts. First, we reconcile the original likelihood, information-criterion calculation, and a necessary restriction of its response law against the public data. Second, we exhibit a decision-side counterpart that preserves the complete marginal predictions of its noise-varying family, rather than merely matching a fitted width or a group mean. Third, we specify an additional joint observable that would remove a particular ambiguity under explicit assumptions, derive how correlated decision noise weakens that identification, and show why a unique population inverse need not provide useful finite-sample precision.

This distinction keeps four questions separate: whether stimulation changes reports; whether one candidate response model predicts better; whether that model adequately describes the observations; and whether its parameters identify an internal physical implementation. Only the last question could subsequently contribute to a theory of the organization underlying experience. The present data do not settle that further bridge.

# 2. Public evidence and the response model

## 2.1 Data, provenance, and analysis status

We use the public Experiment 3 counts and computational-model workbook, together with the publisher's source-data file and released MATLAB code [1,6]. The source study recruited 37 participants and included 30 who met its rubber-hand-illusion screening criterion. Each included participant completed both tasks under 8-Hz, sham, and 13-Hz stimulation. The tasks used identical visuotactile stimulation but were administered in separate, counterbalanced blocks. Seven stimulus-onset asynchronies (SOAs), $s\in\{-400,-200,-100,0,100,200,400\}$ ms, each contributed ten judgments per task and condition: 42 count cells and 420 judgments per person.

The public workbook contains aggregated yes counts. It does not provide the original ordering of individual responses needed to reconstruct serial dependence or temporal drift. All count-likelihood and conditional-test interpretations below therefore state their independent-binomial or conditional-exchangeability assumptions. The reanalysis concerns this selected sample and these SOAs; it is not independent replication or population-wide generalization.

The analysis was developed retrospectively. Dated execution plans were written before the corresponding new numerical runs, but the project was not preregistered before access to the dataset. The audit retains unsuccessful reconstructions and a numerical repair discovered during cross-review. Input hashes, original source locations, code, fit records, and the full results are supplied with this manuscript. The two OSF workbooks have SHA256 prefixes d3b2fef22f077788 and 32e58a814b7d33f5; complete hashes appear in the provenance record.

## 2.2 An effective Gaussian interval observer

Suppress participant indices. Let $t\in\{O,S\}$ identify the ownership and simultaneity tasks and $f$ the stimulation condition. The released observer predicts

$$
p_{tf}(s)=\frac{\lambda}{2}+(1-\lambda)
\left[
\Phi\!\left(\frac{k_{tf}-s}{\sigma_f}\right)
-\Phi\!\left(\frac{-k_{tf}-s}{\sigma_f}\right)
\right],
\tag{1}
$$

where $\Phi$ is the standard-normal distribution function, $\sigma_f>0$ is an effective standard deviation, $k_{tf}\geq0$ an interval halfwidth, and $\lambda$ an independent fair-guess lapse probability. We use one consistent lapse convention throughout: total lapse probability is $\lambda$, not half that value.

The Bayesian common-cause rule in the source code determines the interval through

$$
k_{tf}^{\,2}=
\left[
\frac{2v_f(v_f+S^2)}{S^2}
\left\{\operatorname{logit}\pi_{tf}
+\frac12\log(1+S^2/v_f)\right\}
\right]_+,
\qquad v_f=\sigma_f^2 ,
\tag{2}
$$

with $[z]_+=\max(z,0)$. The fixed stimulus-prior variance is $S^2=84{,}000$ ms$^2$. This is the sample variance of the six nonzero tested SOAs, as implemented in the released code. A zero interval gives the lapse baseline. Equation (2) assumes a posterior common-cause decision threshold of one half.

The source *Sigma* family has two task priors fixed across stimulation, three condition-specific standard deviations shared between tasks, and one lapse: six fitted parameters per person. The *Prior* family has six task-by-condition priors, one common standard deviation, and one lapse: eight parameters. The source scripts also count the fixed $S$ as a parameter, giving seven and nine; this does not change their two-parameter penalty difference.

For count $y_{tfj}$ out of $n_{tfj}$ judgments, we evaluate the positive negative log likelihood

$$
\mathcal L=-\sum_{t,f,j}
\{y_{tfj}\log p_{tf}(s_j)
+(n_{tfj}-y_{tfj})\log[1-p_{tf}(s_j)]\}.
\tag{3}
$$

Binomial coefficients are omitted consistently. This also permits held-out scores from separate folds to sum to binary predictive log scores.

A fitted $\sigma$ in (1) is distinct from the standard deviation of a descriptive Gaussian fitted directly to a response curve. Neither quantity is, by definition, a neural integration time or an experiential magnitude. That distinction becomes consequential in the reconstruction audit below.

# 3. What the source analysis reproduces, and what it does not

## 3.1 Exact likelihood reconstruction and a sign discrepancy

Evaluating (1)--(3) at the 60 released parameter vectors reproduces the saved negative log likelihoods to a maximum absolute error of $6.54\times10^{-13}$ for Sigma and $1.994\times10^{-9}$ for Prior. This verifies the task/condition mapping and the particular likelihood before any independent optimization.

The public master script converts positive negative log likelihoods to log likelihoods and then reverses their sign again before applying an information-criterion formula for log likelihoods. For $d_i=\mathcal L_{\Sigma,i}-\mathcal L_{P,i}$, the correct between-model differences are

$$
\Delta\mathrm{AIC}_i=-4+2d_i,\qquad
\Delta\mathrm{BIC}_i=-2\log(420)+2d_i.
\tag{4}
$$

The released calculation instead uses $-2d_i$. Its values reproduce every one of the 30 publisher source-data rows to within $4.80\times10^{-14}$. The discrepancy therefore connects the code, saved objectives, and reported comparison rather than resting on a variable name alone.

| Saved-fit quantity | Released calculation | Corrected calculation |
|:--|--:|--:|
| Sum $\Delta$AIC, Sigma minus Prior | $-112.1408$ | $-127.8592$ |
| Sum $\Delta$BIC, Sigma minus Prior | $-354.5561$ | $-370.2744$ |
| Participants favoring Sigma by AIC | 22 / 30 | 29 / 30 |
| Participants favoring Sigma by BIC | 30 / 30 | 29 / 30 |

The summed saved negative log likelihoods are 5138.9604 and 5142.8900. Correcting the arithmetic preserves the aggregate Sigma preference; it does not reverse the source paper's comparison. Raw likelihood alone favors Sigma in 14 of 30 participants. These are evaluations of saved fits, not certificates of global optima or a reproduction of every reported bootstrap or group-model-selection result. The source Methods and executable bootstrap loop differ in their resampling specifications; we do not claim to reconstruct a single verified execution history.

## 3.2 Reconstruction of descriptive Gaussian widths

The preceding CTD version analyzed the 180 released descriptive widths [11]. Auditing their estimator reveals why those widths should not be substituted for (1)'s sensory parameter. An unweighted least-squares Gaussian with a free baseline,

$$
g(s)=b+A\exp[-(s-\mu)^2/(2w^2)],
\tag{5}
$$

reconstructs 176 of 180 released widths within 0.01 ms and 178 within 0.1 ms. The median absolute discrepancy is 0.000144 ms. Two cases remain materially different: participant 1, simultaneity at 8 Hz, gives 196.651 ms instead of 169.558 ms; participant 24, ownership at 13 Hz, gives 120.484 ms instead of 127.669 ms. Additional starting points, reasonable fitting variants, and all global task/condition column permutations did not resolve both cases. The original Gaussian fitting implementation was not located in the inspected public project inventory. We do not splice a different estimator into just those cases.

Of the reconstructed free-baseline curves, 96 predict outside $[0,1]$ at at least one observed SOA, and 129 do so somewhere on the real line. These nuisance parameters are our reconstruction, not released original nuisance estimates. A descriptive least-squares fit can still summarize a curve; it cannot automatically serve as a Bernoulli probability law. The remaining discrepancy and this probability-domain issue are reasons to move the main inference to the released count model. They are not evidence that the counts themselves are incorrect.

## 3.3 A parameter-free necessary-condition test

Every curve in both released BCI families satisfies

$$
p_{tf}(s)=p_{tf}(-s).
\tag{6}
$$

We test this mandatory centering restriction without fitting priors, widths, or lapses. For each participant, task, condition, and $|s|\in\{100,200,400\}$, let $y_+,y_-$ be the yes counts at the two signed SOAs and $K=y_++y_-$. Under (6) and independent binomial observations,

$$
y_+\mid K\sim\operatorname{Hypergeom}(20,K,10).
\tag{7}
$$

We sum the likelihood-ratio deviance of the separate two proportions against their pooled proportion across all 540 pairs. The observed statistic is **984.3042**. Its exact conditional null mean is 531.4224 and its standard deviation is 31.7477. None of 19,999 planned conditional Monte Carlo replicates reaches the observed statistic; the maximum is 662.3691. The plus-one Monte Carlo $p$ is **0.00005**, the resolution of this run. The exact binomial interval for the simulated exceedance probability is $[0,0.0001844]$; it describes Monte Carlo uncertainty.

The mean positive-minus-negative yes-rate differences are 6.81 percentage points for ownership and 7.52 for simultaneity. These are descriptive magnitudes, not separately selected subgroup tests. The aggregate test can detect individual asymmetry even if signed biases partly cancel in a group average.

This finding rejects the *centered independent-binomial response family*. Nonzero centers, serial dependence, or nonstationarity can each violate that family. It does not attribute asymmetry to sensory timing, decision criteria, stimulation, or body-ownership experience. Because the symmetric saturated family contains both source models, their deviance against the unrestricted count table cannot be smaller than 984.3042, irrespective of optimization. The arithmetic audit and the adequacy test thus answer different questions.

![Public-data audit. Left: released descriptive widths against a free-baseline reconstruction; the two unresolved cases are identified. Middle: the conditional centering-test reference distribution and observed deviance. Right: held-out predictive scores of the four explicitly fitted response families. All data panels use the released Experiment 3 counts; conditional simulations and refits are new analyses.](../figures/figure1_audit.pdf){width=100%}

# 4. A restricted predictive robustness analysis

## 4.1 Location extensions and held-out data

To follow the diagnosed restriction with a limited, interpretable comparison, we extend each source family with two task-specific centers $\mu_O,\mu_S$, fixed across the three stimulation conditions. Equation (1) then uses $s-\mu_t$. The resulting *Sigma + center* and *Prior + center* families have eight and ten parameters per participant. Adding location is a standard observer-model extension and has a direct BCIbias precedent in Chancel et al. [5]; it is not a new model principle.

We fit all four families to the full counts and perform a fixed five-fold within-cell split. For each cell, its ten binary responses are randomly partitioned into five held-out pairs; each fold trains on the other eight. This reconstructs exchangeable binary allocations, not original trial identities. The seed is fixed at 2026101017, and the same split is used for all families. The target is prediction of further exchangeable judgments at the existing participant/stimulus cells. There is no held-out participant, new SOA, chronological forecast, or independent experiment. The model extensions were motivated by examination of these data, so the fixed-partition scores are not selection-adjusted or externally validated estimates of their generalization advantage.

Full fits use 16 Sobol starts plus a canonical start and the released parameter start where applicable. Fold fits use eight Sobol starts plus a canonical start. Each shifted fit also receives its own unshifted solution computed on the **same training data** as a nested starting point. Neither held-out responses nor full-data fits are used to initialize fold fits.

The numerical domain is explicitly finite: prior logits in $[-16,16]$, natural logarithms of standard deviations measured in milliseconds in $[-10,10]$, lapse in $[10^{-8},1-10^{-8}]$, and centers in $[-800,800]$ ms. This is an independent bounded reanalysis, not exact replication of the original optimization domain. In particular, the independently fitted unshifted Prior total is 0.03492 NLL above the saved source total. The saved-fit arithmetic audit remains separate.

## 4.2 Results and numerical review

| Response family | Parameters / person | Full NLL | Held-out NLL | Held-out NLL / judgment |
|:--|--:|--:|--:|--:|
| Sigma | 6 | 5138.950 | 5465.166 | 0.433743 |
| Prior | 8 | 5142.925 | 5427.816 | 0.430779 |
| Sigma + center | 8 | 4894.506 | 5238.550 | 0.415758 |
| Prior + center | 10 | 4891.248 | 5299.435 | 0.420590 |

The location extension reduces held-out NLL by **226.616** for Sigma and **128.382** for Prior. Between the shifted families, Sigma + center has **60.885** lower total held-out NLL; 21 of 30 participants favor it. The mean participant difference, Sigma minus Prior, is **−2.029**, with a descriptive paired 95% interval of **[−3.268, −0.791]**. This supports the effective-noise-varying response family in this particular conditional prediction exercise. It is not a comparison against the exact decision-side counterpart derived below. Before adding centers, the held-out difference is +37.350, favoring Prior in total but with a participant interval spanning zero; the relative predictive comparison is therefore sensitive to the shared centering restriction.

Corrected AIC on full fitted data and held-out predictive scoring are distinct criteria. The Sigma families retain a lower summed AIC than the corresponding Prior families because of their smaller parameter count. That does not establish a sensory locus: Section 5 gives an exact counterpart with the same marginal likelihood and a fixed construction rule. Nor does improved held-out prediction establish full model adequacy. The shifted models still have count-table deviances of 1218.81 and 1212.29, respectively. Nominal chi-square references are imperfect with ten responses per cell, parameter boundaries, and unmodeled dependence; we therefore do not report them as definitive calibrated rejection tests.

An initial CV execution omitted the same-fold nested start for shifted models. Cross-review found three Sigma + center fits with training NLL worse than the contained unshifted solution, despite satisfactory optimizer status and projected-gradient checks. We repaired the rule for **all** shifted fold fits, retained the original records, and recomputed the final scores. This is a numerical nesting correction, not a choice of fits by held-out performance. The final analysis checks every full and fold nesting relation, independent finite-difference gradients, and held-out score recomputation. No optimizer certificate is interpreted as a proof of global optimality.

# 5. An exact source-model implementation ambiguity

## 5.1 Sensory variance and criterion-center variability

Consider a sensory timing sample $X=s+E$ and a decision-interval center $C$:

$$
E\sim N(0,a),\qquad C\sim N(\mu,b),\qquad E\perp C.
$$

The nonlapse response is $1\{|X-C|\leq k\}$. Because $E-(C-\mu)$ is Gaussian with variance

$$
v=a+b,
\tag{8}
$$

the response function depends on $a$ and $b$ only through their sum. The lower and upper criteria, $C-k$ and $C+k$, move together; their ordering never reverses. This exact moving-center case is an application of the sensory/criterion variability models of Yarrow et al. [2,3].

**Proposition 1 (constant-sensory counterpart).** For any participant's positive source-model variances $v_f$, choose a constant $a$ satisfying $0<a\leq\min_f v_f$ and set $b_f=v_f-a$. Retain every task-by-condition halfwidth $k_{tf}$, lapse probability, and center. The resulting implementation has sensory variance constant across stimulation yet agrees with the original observer at every SOA and hence for every possible marginal count dataset.

**Proof.** Equation (8) recovers each original $v_f$ exactly, while all other terms of (1) remain the same. Pointwise probability equality implies equality of every Bernoulli or binomial marginal likelihood. $\square$

We instantiate the fixed rule $a_i=\tfrac12\min_f v_{if}$ for all 30 released Sigma fits. Across 1,260 count cells the largest probability discrepancy is $2.22045\times10^{-16}$; the largest participant NLL discrepancy is $2.85\times10^{-14}$. Both constructions have summed NLL 5138.960411207295. Independent integration over criterion jitter verifies selected marginals. Numerical agreement illustrates the identity; the proof establishes it for all SOAs and possible count data.

The counterpart retains $k_{tf}=k(\pi_t,\sqrt{a+b_f},S)$, including its changes across stimulation. It must **not** be described as changing only criterion noise while keeping every threshold fixed. Nor is it the source observer reinterpreted as a normative Bayesian observer whose likelihood depends only on the new, constant sensory variance $a$. It is a distinct permitted implementation of the same response family, with a declared threshold policy. Setting $a$ by a fixed rule introduces no additional fitted prediction parameter.

This distinction is exactly what makes the example useful. The public comparison discriminates two restricted parameterizations of response curves. It cannot discriminate that noise-varying family from its exact decision-side counterpart using the same marginal observations. The construction does not show that humans used criterion jitter or that sensory uncertainty did not change. It shows which alternative must be excluded before the stronger sensory attribution follows.

## 5.2 Two further boundaries

An unknown posterior report criterion $\gamma$ enters (2) by replacing $\operatorname{logit}\pi$ with $\operatorname{logit}\pi-\operatorname{logit}\gamma$. Equal shifts of both logits preserve the entire response curve. Consequently a fitted prior under $\gamma=1/2$ is an effective prior under that decision convention. This standard posterior-odds identity does not make arbitrary prior changes equivalent to arbitrary noise changes; it specifies a narrower prior/criterion alias.

Known independent external Gaussian noise of variance $e$ changes (8) to $a+b+e$. Marginal noise manipulations alone cannot decompose the pre-existing $a+b$ in this additive interval family if matching threshold policies remain permitted. This scoped counterexample does not imply that external-noise experiments are generally uninformative. Identifiability results for other Bayesian observer families, including continuous-estimation paradigms with stronger restrictions, address different observables and assumptions [7].

![Exact marginal equivalence and a missing joint observable. Left: the two implementations assign condition-dependent variability to different stages while retaining total variance and the source threshold policy. Middle: their marginal curves coincide for the first participant under sham stimulation. Right: all 90 source-parameter profiles give prospective paired-yes probabilities under independent criteria and one shared sensory draw. The joint probabilities are model predictions from the original centered parameterization, whose zero-centering restriction fails the count-model check; the study did not collect them, and they do not provide an empirical power calculation.](../figures/figure2_twins.pdf){width=100%}

# 6. A conditional additional-measurement result

## 6.1 One joint probability

Marginal equivalence suggests measuring a missing relation between consumers. Suppose two binary judgments use one **same internal sensory draw** $E\sim N(0,a)$:

$$
Z_O=s+E-C_O,\qquad Z_S=s+E-C_S,
\qquad Y_t=1\{|Z_t|\leq k_t\}
\tag{9}
$$

before lapses. Assume zero-centered Gaussian criteria $C_t$ independent of one another and of $E$. Marginal variances are $v_t=a+b_t$; covariance is $a$. Positive finite $v_t,k_t$ and marginal lapses below one are independently calibrated. Lapse indicators and fair guesses are independent across reports and from the other variables.

**Theorem 2 (centered paired identification).** At a calibrated common center, one additional population probability $P(Y_O=1,Y_S=1)$ uniquely identifies $a\in[0,\min(v_O,v_S)]$ under the preceding assumptions.

Put $r_t=k_t/\sqrt{v_t}$ and $\rho=a/\sqrt{v_Ov_S}\geq0$. The nonlapse paired probability is the centered bivariate-normal rectangle

$$
J(\rho)=P(|U|\leq r_O,\ |V|\leq r_S).
$$

The classical Gaussian probability derivative [8] gives

$$
J'(\rho)=2\{\phi_2(r_O,r_S;\rho)
-\phi_2(r_O,-r_S;\rho)\}>0
\quad\text{for }0<\rho<1,
\tag{10}
$$

because $r_Or_S>0$. Continuity includes the endpoints. Known independent lapses apply an affine transformation with positive coefficient $(1-\lambda_O)(1-\lambda_S)$ to $J$, leaving a unique inverse. The complete expression is in Appendix B.

A binary pair with fixed marginals has exactly one remaining probability degree of freedom. Marginals alone fail by Proposition 1, while this one additional probability suffices under the stated premises. This is minimality in the dimension of an observation law. It means neither one physical trial nor an optimal finite-sample protocol.

The source experiment provides no such joint observation: its tasks were in separate blocks. Moreover, its rejection of zero-centered symmetry means that physical zero SOA cannot be treated as a calibrated common center without evidence. Asking two sequential questions also does not demonstrate that they read the same internal sample. The result is a conditional design contract, not a validated human measurement method.

## 6.2 Correlated decision noise gives a sharp interval

Retain the calibrated-center and lapse assumptions, and let $(C_O,C_S)$ be jointly Gaussian and independent of $E$, while allowing the two criteria to be correlated. Let $c=\operatorname{Cov}(C_O,C_S)$. Total covariance becomes $a+c$. The central joint probability identifies the magnitude $r$ of total correlation because $J(\rho)=J(-\rho)$, not its sign. Suppose independent calibration justifies

$$
|c|\leq\kappa\sqrt{(v_O-a)(v_S-a)},\qquad 0\leq\kappa\leq1,
$$

and write $R=r\sqrt{v_Ov_S}$.

**Theorem 3 (sharp sensitivity set).** The exact set of sensory variances compatible with these constraints is

$$
\mathcal A(r,\kappa)=
\left\{a\in[0,\min(v_O,v_S)]:
(R-a)^2\leq\kappa^2(v_O-a)(v_S-a)\right\}.
\tag{11}
$$

For equal effective variances $v_O=v_S=v$ and $\kappa<1$,

$$
\boxed{\quad
\max\!\left(0,\frac{r-\kappa}{1-\kappa}\right)
\leq\frac av\leq\frac{r+\kappa}{1+\kappa}.
\quad}
\tag{12}
$$

At $\kappa=1$, the interval is $[0,(1+r)/2]$.

**Proof.** The covariance equation is either $a+c=R$ or $a+c=-R$. For $a,R\geq0$, $|R-a|\leq R+a$, so every feasible negative-covariance case also permits the positive branch. The union is therefore exactly (11). For each feasible $a$, choose an independent Gaussian sensory variable of variance $a$ and a Gaussian criterion vector with variances $v_O-a,v_S-a$ and covariance $R-a$. Its covariance matrix is positive semidefinite, so it realizes the required law. This proves sharpness. With equal variances, $|r-a/v|\leq\kappa(1-a/v)$ gives (12). $\square$

For illustration, $r=.6$ and an externally justified $\kappa=.2$ restrict the sensory-variance fraction to $[.5,2/3]$. If $\kappa\geq r$, zero is admissible. The same joint statistic cannot estimate $\kappa$ freely and also identify $a$. Equation (11) is an explicit sensitivity analysis for this observation model, using ordinary Gaussian covariance algebra rather than a new general decomposition principle.

## 6.3 Precision, shared lapses, and calibration

The unique centered inverse is weak near independence:

$$
J(\rho)-J(0)
=2r_Or_S\phi(r_O)\phi(r_S)\rho^2+O(\rho^4).
\tag{13}
$$

There is no first-order sensitivity at zero shared variance. With known marginals, the local separation scale for variance $a$ is $n^{-1/4}$, rather than the usual $n^{-1/2}$; Appendix B derives the statement. Tail-saturated response profiles can further reduce information. A second, off-center paired observation supplies first-order local sensitivity under a common calibrated shift, but we do not claim that an arbitrary off-center probability has a globally unique inverse.

![Sensitivity of the prospective joint readout. Left: central joint-yes excess over independence rises with nonnegative shared correlation but is locally flat at zero; the dashed curve shows an off-center illustration. Right: sharp sensory-variance fractions compatible with total correlation r = 0.6 as the permitted criterion correlation increases. These are analytic model calculations, not human measurements.](../figures/figure3_identification.pdf){width=100%}

Shared lapses can also create apparent shared variance. With independent nonlapse judgments each having yes probability one half, a 20% chance of replacing both answers by the same fair coin yields a joint yes probability of .30 while retaining both marginal probabilities at .50. An independent-lapse interpretation would falsely assign positive shared variability. Similarly, two independently resampled sensory draws give product marginals regardless of their variance decomposition. The same physical stimulus is insufficient to distinguish these cases.

The proposed additional measurement must therefore calibrate task centers, marginal parameters and lapses; justify a shared internal sample and control answer-to-answer contamination; and constrain shared decision variability. A software or apparatus implementation with known routing can test that measurement contract. A human paired-report experiment would still require independent validation that its observation model is appropriate.

# 7. Interpretation, scope, and a discriminating next experiment

The principal empirical additions are the complete saved-fit arithmetic reconciliation, the conditional centering test, the estimator reconstruction with two retained discrepancies, and the restricted predictive robustness analysis. The principal constructive addition is an explicit source-family counterpart plus a conditional joint-readout result and its sharp sensitivity boundary. Together they make the gap between predictive fit and implementation attribution observable and reviewable.

These findings do not negate the source study's experimental manipulation or its reported changes in bodily judgments. An intervention on stimulation condition is evidence about that intervention and its measured outcomes. It does not, without further exclusions, make a response parameter a unique mediator. The source-specific counterpart is especially decisive about this inferential boundary: more marginal trials at the same or additional SOAs cannot discriminate two models that agree pointwise.

A future discriminating study should compare explicit implementation packages. A sensory-change package would constrain changes in the shared component $a_f$ while bounding criterion changes; a decision-change package would constrain $a_f$ to remain constant while allowing the specified criterion and threshold policy. Under a validated joint observation model, their combined marginal and joint laws can be compared. The exact marginal counterparts constructed here have different prospective joint probabilities under the independent-criterion assumptions; broader implementation packages need explicit restrictions to make their prediction sets distinct. Correlated criteria, shared lapses, or resampling create additional packages that must either be tested or excluded by independent evidence. Relative fit should then be assessed alongside necessary-condition tests and calibrated uncertainty, with model comparison specified before collecting the new joint data.

The single-center theorem is a mathematical starting point for this design, not an instruction to assume away calibration. If the tasks' centers cannot be aligned, their noncentered joint law needs a separate identification analysis. If they do not share an internal draw, the shared-variance interpretation fails. If criterion correlation is only bounded, the result should remain the interval in (11), including an empty interval as possible evidence against the package. The published blockwise counts cannot supply these missing observations retrospectively.

The relationship to consciousness research is limited but useful. Body-ownership reports are operational endpoints with an experiential interpretation in the source paradigm [1,5]. A Gaussian variance component does not, by itself, measure ownership experience, agency, a self, or a neural basis of consciousness. UCT's proposed structural correspondence [9] would additionally require an independently justified mapping between physical organization and a specified experiential endpoint. It yields no unique quantitative prediction for (1)--(13) without such a bridge. The results therefore cannot distinguish UCT from all competing consciousness theories, and no claim about AI consciousness follows.

The earlier CTD proportional-width analysis remains a reproducible, separate descriptive branch [11]. Its positive rank-one and ordinal restrictions do not follow from the present Bayesian observer, because a common effective noise parameter can map nonlinearly into different descriptive task widths. Moving to response-level implementation identification strengthens the scientific question without retroactively upgrading those exploratory width results.

# 8. Conclusion

The public stimulation data support a reproducible comparison of specified response families, but the stronger location of changing variability is underidentified in an explicitly larger sensory/decision family. We make that boundary concrete by reconstructing the likelihood and comparison arithmetic, testing a necessary response restriction, evaluating a limited location extension, and instantiating an exact alternative implementation. A calibrated paired response can supply a missing joint constraint, while correlated criteria and weak local sensitivity delimit what it would establish. This combination is a methods contribution to testing internal organization; an empirical identification of a sensory mechanism or experiential structure remains a further experiment.

# Reproducibility and declarations

**Data and code.** The source data and original code are available from the authors' OSF projects [6]. This manuscript's reproduction package contains the three public workbooks, independent Python implementations, execution plans, full fit and score records, theorem checks, audit reports, and source hashes. Original third-party code and articles are identified by retrieval records and citations; their complete contents need not be redistributed to run the new Python analyses. The archived CTD v0.1 remains unchanged. All joint-response figures are model calculations; conditional simulation files are not human observations.

**Ethics.** This work reanalyzes public aggregated data and recruited no participants. Approval and consent for the original experiment are reported by its authors [1]; this manuscript does not claim a new ethics approval.

**Preparation disclosure.** AI tools assisted literature examination, mathematical derivation, programming, numerical review, and drafting. The reproduction files tie the quantitative statements to executable analyses. The human author must review and approve the manuscript and complete journal-specific funding, competing-interest, and authorship declarations before submission. AI assistance is not independent external peer review.

**Acknowledgment.** We credit D'Angelo, Lanfranco, Chancel, and Ehrsson for making the study's data and modeling materials available. Their open materials enabled this audit. They have not reviewed or endorsed the present interpretation.

\newpage

# Appendix A. Audit and analysis details

## A.1 Count mapping, estimator limitations, and provenance

The first worksheet of the Experiment 3 workbook supplies rows 4--33, columns B--AQ, reshaped to participant $\times$ task $\times$ condition $\times$ SOA. The condition order is 8 Hz, sham, 13 Hz, first ownership then simultaneity; SOAs run from $-400$ to $+400$ ms. The computational-model workbook supplies Prior rows 2--31 and Sigma rows 36--65. Task-order ambiguities in headers are resolved by exact saved-likelihood reproduction, not by choosing the mapping with favorable scientific results.

For Gaussian-width reconstruction, a freely signed baseline is necessary for close agreement with most published estimates. For example, participant 1's ownership 8-Hz counts $(7,8,9,10,10,7,5)$ yield a reconstructed width of 151.2751 ms with baseline about .582 and height about .436, close to the released 151.27367 ms. A zero-baseline fit gives about 399.23 ms. This explains a large discrepancy in the earlier exploratory attempt. The two unresolved widths remain unresolved after 60 additional starts per case and the recorded estimator checks. Two further differences exceed .01 but remain below .1 ms. The claim is near-reconstruction of 178 widths at .1-ms tolerance, not exact recovery of all original estimates.

The original BCI saved-fit sums and differences are evaluated without optimization. The information-criterion penalty treats 420 binary judgments as the sample size for comparability with the released calculation. Counting the fixed stimulus-prior scale as a free parameter changes absolute AIC/BIC levels but leaves the reported Sigma-minus-Prior difference unchanged. The corrected arithmetic cannot recover an undocumented random seed, the exact bootstrap execution, or unobserved group-model-selection output.

## A.2 Conditional symmetry deviance

For one signed pair, put $\widehat p_\pm=y_\pm/10$ and $\bar p=(y_++y_-)/20$. Its deviance is

$$
T_j=2\sum_{\epsilon\in\{+,-\}}
\left[
y_\epsilon\log\frac{\widehat p_\epsilon}{\bar p}
+(10-y_\epsilon)\log\frac{1-\widehat p_\epsilon}{1-\bar p}
\right],
\tag{A1}
$$

using continuous zero-count conventions. The statistic is $T=\sum_{j=1}^{540}T_j$. Conditioning removes each nuisance common probability. We enumerate the at-most-eleven hypergeometric possibilities to obtain the exact mean and variance of each $T_j$ and sum them under independence. Monte Carlo replicates draw independently from all 540 conditional distributions, retaining each observed $K_j$. The seed and count are fixed in the execution plan.

Since a symmetric saturated model permits a distinct common probability for each signed pair, it contains the centered BCI families. Its likelihood is at least as high as theirs. Its deviance, (A1), is therefore a deterministic lower bound on their unrestricted count-table deviance. No BCI parameter estimate is used in this statement.

The null assumes independent, identically distributed binary observations within each stimulus cell and independence across the conditioned pairs. Aggregation prevents us from checking these assumptions against response order. The conditional result is rigorous for that observation law, not a distribution-free test immune to block effects.

## A.3 Numerical safeguards and retained failed run

All four response families use analytic derivatives checked against finite differences. An additional implementation checked 52 interior gradient cases with maximum scaled discrepancy $3.60\times10^{-6}$. We do not clip predicted probabilities and then differentiate an unclipped function. Instead, explicit lapse bounds keep likelihood evaluation inside its domain. Fit records retain start-specific objectives, parameter bounds, convergence flags, and projected-gradient diagnostics.

The first CV run violated training nesting at participant/fold pairs (16, 3), (21, 4), and (22, 2), with excess NLLs approximately 51.712, 50.513, and 99.666 for Sigma + center. The corrected rule adds the training-only unshifted fitted solution as a candidate start in every shifted fold, for both model families. The zero-center embedding is included as an optimizer initialization; all resulting fitted training objectives are checked against the unshifted nesting reference. The superseded outputs are retained and labeled; all main-text scores use the corrected run.

The finite parameter box produces boundary fits in 12, 14, 13, and 14 participants for the four full-data families, respectively, and is not a proof that the unrestricted optimum has been found. In the released Prior fit for participant 6, clipping the source start into the stated box worsens its initial objective; refitting recovers most but not all of that loss. This is why the exact saved-parameter reproduction and the new bounded fits are reported separately.

Full and held-out NLLs omit the same binomial constants. Participant-wise CV differences are summed over folds before any uncertainty summary. A descriptive paired $t$ interval uses 30 participant differences and is conditional on the fixed artificial partition and fitting rule. It neither treats 150 folds as independent participants nor provides an external replication interval.

# Appendix B. Identification proofs and failure cases

## B.1 Effective marginal parameters are a separate target

If the center and lapse are known, two exact population response probabilities at $0$ and one $s_1>0$ identify $v=\sigma^2$ and $k$ in the interval family, provided $0<q_1<q_0<1$, where $q_j=[p(s_j)-\lambda/2]/(1-\lambda)$. Specifically,

$$
r=\frac{k}{\sigma}=\Phi^{-1}\!\left(\frac{1+q_0}{2}\right),\qquad
q_1=\Phi(r-u)+\Phi(r+u)-1,\quad u=s_1/\sigma .
$$

For $u>0$, the last expression has derivative $\phi(r+u)-\phi(r-u)<0$, decreases from $q_0$ to zero, and thus has one inverse. This identifies the *effective* variance, leaving its decomposition (8) free. With an unknown lapse, a feasible interval of lapse choices generally induces a one-parameter trajectory of matching $(v,k)$ at these two points. Additional stimulus levels can constrain it. Two population probabilities are not two individual trials, and inversion of a noisy proportion is not exact calibration.

For an arbitrary posterior criterion $\gamma$, posterior log odds are

$$
\operatorname{logit}\pi+\tfrac12\log(1+S^2/v)
-\frac{x^2S^2}{2v(v+S^2)}.
$$

Comparing them with $\operatorname{logit}\gamma$ establishes the prior/criterion difference used in Section 5.2. The source threshold convention sets $\gamma=1/2$; other conventions can produce the same interval.

## B.2 Joint inversion, minimality, and weak identification

For positive finite radii,

$$
J(\rho)=\int_{-r_O}^{r_O}\phi(z)
\left[
\Phi\!\left(\frac{r_S-\rho z}{\sqrt{1-\rho^2}}\right)
-\Phi\!\left(\frac{-r_S-\rho z}{\sqrt{1-\rho^2}}\right)
\right]\,dz .
\tag{B1}
$$

Integrating $\partial_\rho\phi_2=\partial_x\partial_y\phi_2$ over the rectangle gives the four-corner boundary expression, which reduces by symmetry to (10). At zero, $J(0)=q_Oq_S$, where $q_t=2\Phi(r_t)-1$. With independent lapses,

$$
\begin{aligned}
P_{11}={}&(1-\lambda_O)(1-\lambda_S)J\\
&+\tfrac12\lambda_O(1-\lambda_S)q_S
+\tfrac12\lambda_S(1-\lambda_O)q_O
+\tfrac14\lambda_O\lambda_S .
\end{aligned}
\tag{B2}
$$

The coefficient of $J$ is positive. The admissible interval $\rho\in[0,\min(v_O,v_S)/\sqrt{v_Ov_S}]$ therefore has a unique inverse, including limiting perfectly correlated Gaussian cases by continuity. With fixed marginals a $2\times2$ table has one free entry, proving the stated minimal addition.

Equation (13) follows by expanding the two corner densities around zero and integrating. With known marginals, write the observed excess over independence as $d(a)=Ca^2+O(a^4)$, $C>0$. The four cell changes are $(d,-d,-d,d)$. Taylor expansion gives

$$
D_{\mathrm{KL}}(P_a\Vert P_0)=
\frac{C^2a^4}{2p_O(1-p_O)p_S(1-p_S)}
+O(a^6).
\tag{B3}
$$

If $na^4\to0$, product KL and Pinsker's bound imply vanishing total-variation separation from $a=0$. If $\sqrt n\,a^2\to\infty$, the joint proportion's excess dominates its sampling error. This establishes the local $n^{-1/4}$ separation scale for the *variance* parameter under known calibration. It does not give a recommended sample size for humans.

At nonzero common calibrated SOA, standardized limits are $L_t=(-k_t-s)/\sqrt{v_t}$ and $U_t=(k_t-s)/\sqrt{v_t}$. The joint derivative at zero correlation is

$$
J_s'(0)=[\phi(L_O)-\phi(U_O)]
[\phi(L_S)-\phi(U_S)]>0 \quad(s\ne0).
\tag{B4}
$$

The factors have the same nonzero sign, restoring first-order local sensitivity. Global monotonicity away from the center is not asserted. Unknown marginal calibration, unequal uncorrected centers, or model misspecification requires further analysis.

## B.3 Correlation bounds and explicit nonidentification

For unequal marginal variances, the sharp set (11) is the intersection of $[0,\min(v_O,v_S)]$ with

$$
(1-\kappa^2)a^2+
[\kappa^2(v_O+v_S)-2R]a+
R^2-\kappa^2v_Ov_S\leq0.
\tag{B5}
$$

For $\kappa<1$ it lies between the real roots when feasible. It may be empty. At $\kappa=1$, its upper endpoint is the smaller of $\min(v_O,v_S)$ and $(v_Ov_S-R^2)/(v_O+v_S-2R)$; the zero-denominator case $v_O=v_S=R$ admits the full interval. Degenerate zero criterion variance is defined through the covariance inequality, without dividing by a zero standard deviation.

For a direct counterexample, take $v_O=v_S=1$. The decompositions $(a,b_O,b_S,c)=(.2,.8,.8,.3)$ and $(.4,.6,.6,.1)$ both give total covariance .5 and positive-semidefinite criterion covariance matrices. They therefore give the same entire joint response family at every SOA for the same intervals and lapses. Pairing alone cannot separate an unrestricted common decision component.

Likewise, independently resampled sensory variables produce no covariance under independent criteria, however large their individual variances. A second judgment that copies the first, revisits the stimulus, or reconstructs a new sample does not satisfy (9). The theorem's interpretation depends on the actual consumer relation.

## B.4 Computational verification and illustration boundaries

The theoretical checks include 27 prior/criterion equivalences, 36 two-level marginal inverses, 37 source marginal predictions verified by integration over criterion jitter, all 90 source-derived prospective joint profiles, 48 derivative checks, 36 paired inverses, near-zero and off-center expansions, correlated-criterion and correlated-lapse counterexamples, and 60,060 membership checks for the sharp correlation set.

At the released Sigma parameters, choosing $a_i=\tfrac12\min_f v_{if}$ gives prospective paired-yes differences ranging from $3.68\times10^{-10}$ to .1348, with median .01762, relative to the all-shared-variance implementation. These are calibrated-model illustrations, not estimates of actual joint behavior. Some differences are too small to make a practical design attractive. Squared root-probability differences and log1p calculations avoid rounding their positive Hellinger distances to zero. No source-derived theoretical trial-count bound is interpreted as an empirical power analysis.

# References

1. D'Angelo, M., Lanfranco, R. C., Chancel, M., & Ehrsson, H. H. (2026). Parietal alpha frequency shapes own-body perception by modulating the temporal integration of bodily signals. *Nature Communications, 17*, 53. <https://doi.org/10.1038/s41467-025-67657-w>

2. Yarrow, K., Jahn, N., Durant, S., & Arnold, D. H. (2011). Shifts of criteria or neural timing? The assumptions underlying timing perception studies. *Consciousness and Cognition, 20*, 1518--1531. <https://doi.org/10.1016/j.concog.2011.07.003>

3. Yarrow, K., Solomon, J. A., Arnold, D. H., & Roseboom, W. (2023). The best fitting of three contemporary observer models reveals how participants' strategy influences the window of subjective synchrony. *Journal of Experimental Psychology: Human Perception and Performance, 49*, 1534--1563. <https://doi.org/10.1037/xhp0001154> Correction (2025), *51*, 1708: <https://doi.org/10.1037/xhp0001226>. The present lapse convention is independently defined; the cited variance argument does not depend on the corrected lapse factor.

4. Cabrera, C. A., Lu, Z.-L., & Dosher, B. A. (2015). Separating decision and encoding noise in signal detection tasks. *Psychological Review, 122*, 429--460. <https://doi.org/10.1037/a0039348>

5. Chancel, M., Ehrsson, H. H., & Ma, W. J. (2022). Uncertainty-based inference of a common cause for body ownership. *eLife, 11*, e77221. <https://doi.org/10.7554/eLife.77221>

6. D'Angelo and colleagues. Public study data, <https://osf.io/ytga5/>; released Bayesian computational-modeling materials, <https://osf.io/s5p4v/>. Retrieved 10 October 2026. File-specific locations and hashes are recorded in the reproduction package.

7. Hahn, M., Wang, E., & Wei, X.-X. (2026). Identifiability of Bayesian models of perception. *Proceedings of the National Academy of Sciences, 123*, e2601013123. <https://doi.org/10.1073/pnas.2601013123>

8. Plackett, R. L. (1954). A reduction formula for normal multivariate integrals. *Biometrika, 41*, 351--360. <https://doi.org/10.1093/biomet/41.3-4.351>

9. Liu, H. (2026). *Unified Consciousness Theory I: Structural--Experiential Identity and the Continuity from Physical Process to Conceptual Self* (v1.2), <https://doi.org/10.5281/zenodo.23131575>; *Unified Consciousness Theory II: Consciousness Theories as Effective Organization Theories* (v1.1), <https://doi.org/10.5281/zenodo.23030320>; *Unified Consciousness Theory III: Organization, Intelligence, and Experience---From Inorganic Processes to Artificial Agents* (v1.0), <https://doi.org/10.5281/zenodo.23137088>. Zenodo theoretical preprints; not externally peer reviewed. These commitments do not establish the measurement bridge discussed here.

10. Liu, H. (2026). *Matched Behavior and Source Use* (Version 1.0.1). Zenodo methodological preprint; not externally peer reviewed. <https://doi.org/10.5281/zenodo.23272690>. The finite source-identification setting is background; the present count-model results do not inherit a physical source-control capability from it.

11. Liu, H. (2026). *Testing a Shared Temporal Scale Across Bodily Judgments*. CTD-PAPER-v0.1.0, archived working manuscript, 10 October 2026. Preserved in the companion research repository at commit 6cbbde9e1cec7374bb104d603044900c0baad149. This unpublished preceding version is a separate descriptive analysis, not external validation of the present revision.
