# Response-level identifiability of sensory timing and decision variability

**Working theoretical module for CTD v0.2, 10 October 2026.** This module separates an observer model's effective noise parameter from its physical attribution. It provides a source-specific observational equivalence, a conditional additional readout that breaks that equivalence, and sharp sensitivity to violations of the required decision-noise independence. These statements do not identify an anatomical mediator or an experiential scale.

The Gaussian sensory/criterion-noise ambiguity is inherited, particularly from Yarrow et al. (2011, 2023). Joint-response methods for separating encoding and decision noise also have clear predecessors, including Cabrera, Lu, and Dosher (2015). The present contribution is their explicit application to the released parietal-stimulation observer, together with the exact centered paired-readout restriction, its weak-identification boundary, and its calibrated correlation sensitivity. No first general noise-decomposition or latent-correlation theorem is claimed.

## 1. The published observer and an exact prior–criterion alias

Let $s$ be physical stimulus-onset asynchrony, $\sigma>0$ an effective standard deviation, $k\geq0$ a decision-interval halfwidth, and $0\leq\lambda<1$ the probability of an independent fair-guess lapse. The released observer predicts

$$
p(s)=\frac\lambda2+(1-\lambda)G(s;\sigma,k),\qquad
G(s;\sigma,k)=\Phi\!\left(\frac{k-s}{\sigma}\right)
-\Phi\!\left(\frac{-k-s}{\sigma}\right).
\tag{1}
$$

In the released BCI code, the decision interval is determined by a common-cause prior $\pi$ and a fixed stimulus-prior standard deviation $S$:

$$
k^2=\left[\frac{2\sigma^2(\sigma^2+S^2)}{S^2}
\left\{\operatorname{logit}\pi+
\frac12\log\left(1+\frac{S^2}{\sigma^2}\right)\right\}\right]_+.
\tag{2}
$$

A nonpositive untruncated right-hand side gives a zero-width interval and the constant lapse baseline. Equation (2) assumes that the observer reports a common cause when its posterior probability exceeds $1/2$. The original code fixes $S$ at the sample standard deviation of the six nonzero tested asynchronies, approximately $289.827535$ ms [1,2]. The fitted $\sigma$ is not the separately released descriptive Gaussian width.

**Proposition 1: prior and posterior-criterion equivalence.** If the posterior report threshold is an unknown $\gamma\in(0,1)$, replace $\operatorname{logit}\pi$ in (2) by

$$
\operatorname{logit}\pi-\operatorname{logit}\gamma.
\tag{3}
$$

Consequently the complete response curve, at every SOA and noise level, depends on these two quantities only through their difference. A common shift of both logits leaves all predictions unchanged. For any finite positive $k$, given $\sigma,S,\gamma$, the corresponding prior is

$$
\pi=\operatorname{logistic}\!\left[
\frac{k^2S^2}{2\sigma^2(\sigma^2+S^2)}
-\frac12\log\left(1+\frac{S^2}{\sigma^2}\right)
+\operatorname{logit}\gamma\right].
\tag{4}
$$

**Proof.** The posterior common-cause log odds are

$$
\operatorname{logit}\pi+
\frac12\log(1+S^2/\sigma^2)
-\frac{x^2S^2}{2\sigma^2(\sigma^2+S^2)}.
$$

Comparing this expression to $\operatorname{logit}\gamma$ yields (2) with substitution (3). Solving that equality for the prior gives (4). The invariance follows immediately. $\square$

A prior estimated with $\gamma=1/2$ is therefore an effective prior under that decision convention. The binary reports cannot by themselves distinguish prior change from a compensating posterior-criterion change. This does **not** imply that an effective noise change and a fixed-interval shift are generally observationally equivalent: their curve shapes can differ.

## 2. What two calibrated response probabilities can identify

**Proposition 2: two-level recovery within the symmetric Gaussian interval family.** Suppose the curve center is known to be zero, the lapse probability is known, and the population probabilities at $0$ and a known $s_1>0$ satisfy

$$
0<q_1<q_0<1,\qquad
q_j=\frac{p(s_j)-\lambda/2}{1-\lambda}.
$$

Then those two probabilities uniquely identify the effective $\sigma$ and $k$ in (1).

**Proof.** The central probability determines

$$
r=\frac{k}{\sigma}=\Phi^{-1}\left(\frac{1+q_0}{2}\right)>0.
$$

Put $u=s_1/\sigma$. The second probability satisfies

$$
q_1=H_r(u)=\Phi(r-u)+\Phi(r+u)-1.
$$

For $u>0$,

$$
H_r'(u)=\phi(r+u)-\phi(r-u)<0,
$$

because $(r+u)^2>(r-u)^2$. Moreover $H_r(0)=q_0$ and $H_r(u)\to0$ as $u\to\infty$. A unique positive solution exists; $\sigma=s_1/u$ and $k=r\sigma$. $\square$

With one central probability alone, only $k/\sigma$ is fixed. Thus two stimulus levels are necessary and sufficient for this particular noiseless-probability problem. The theorem does not prescribe two individual trials, nor does it justify exact inversion of noisy proportions with only ten observations per cell.

Unknown lapse produces a one-parameter identification trajectory. For each feasible

$$
0\leq\lambda<\min\{1,2p(s_1),2[1-p(0)]\},
$$

the construction yields one $(\sigma(\lambda),k(\lambda))$. Further SOAs can constrain that trajectory. For example, a curve generated by $(\sigma,k,\lambda)=(120,180,.08)$ ms is matched exactly at $0$ and $100$ ms by $(129.723,181.002,0)$ and $(100.108,176.044,.2)$. Their probabilities at $400$ ms differ from the generating curve by about $-.0250$ and $+.0394$, respectively. These are synthetic examples, not estimates from the participants.

Independent lapse parameters therefore do not make every finite response table unconstrained. They do remove the two-point unique inverse. In the continuum, $p(s)\to\lambda/2$ as $|s|\to\infty$ identifies lapse, followed by the two-level argument. A finite seven-SOA experiment has no literal infinite-SOA endpoint and needs its own likelihood and uncertainty analysis.

The center premise also matters. Equation (1) predicts $p(s)=p(-s)$, whereas the separate conditional symmetry analysis rejects that centered family for the released counts under its independent-binomial assumptions. Proposition 2 is consequently a calibration result, not a direct warrant for estimating sensory noise from this dataset while ignoring its asymmetry.

## 3. An exact decision-side counterpart of the stimulation observer

Write a sensory timing sample and a decision-window center as

$$
X=s+E,\quad E\sim N(0,a),\qquad C\sim N(0,b),\quad E\perp C.
$$

The nonlapse response is $Y=1\{|X-C|\leq k\}$. Since $E-C\sim N(0,a+b)$, (1) depends only on

$$
v=\sigma^2=a+b.
\tag{5}
$$

This is the established Gaussian sensory/criterion-variability ambiguity [3,4]. The criteria $C-k$ and $C+k$ move together, so their separation remains valid on every trial; this is an exact common-center case, not an approximation permitting the lower criterion to cross the upper one.

**Proposition 3: source-specific constant-sensory counterpart.** For any participant's positive effective variances $v_f$ in the released stimulation observer, choose a constant

$$
0<a\leq\min_f v_f,\qquad b_f=v_f-a.
\tag{6}
$$

Keep the observer's task-by-condition halfwidths $k_{tf}$ and lapse probability unchanged. The resulting model has sensory variance constant across stimulation and condition-dependent criterion-center variance, yet reproduces every marginal response probability of the original observer at every SOA. It therefore has the same marginal likelihood for every possible count dataset.

**Proof.** In each task and condition, (5) makes the effective variance exactly $v_f$. The interval and lapse are unchanged, so (1) agrees pointwise. Products of the corresponding Bernoulli/binomial probabilities consequently agree for arbitrary data. $\square$

For a fixed-dimensional model counterpart, set $a=\tfrac12\min_f v_f$ as a fixed construction rule, rather than adding an independently fitted parameter. The induced decision rule can be written

$$
k_{tf}=k\bigl(\pi_t,\sqrt{a+b_f},S\bigr).
$$

The halfwidth trajectory generally changes across stimulation. The counterpart must not be described as changing only jitter while holding every threshold fixed. It reallocates effective variability to a decision stage and carries the condition-specific halfwidth policy with it. It is not the original observer interpreted with unchanged sensory uncertainty and the same normative rule based solely on that sensory uncertainty.

The released-parameter construction gives constant sensory variance for all 30 participants. Across the 1,260 source count cells, the two predicted tables differ by at most $2.22\times10^{-16}$ and their summed negative log likelihoods both equal $5138.960411207295$. An independently coded integration over criterion jitter verifies selected marginal predictions. These calculations demonstrate an exact alternative interpretation within the stated family; they are not evidence that participants actually used criterion jitter.

Adding independently generated external Gaussian timing noise of known variance $e$ changes the observable variance to $a+b+e$. Such marginal noise manipulations alone leave decomposition (5) unresolved if the two counterparts retain matching thresholds and no new exclusion restriction is imposed. This statement is limited to this additive interval family. It does not deny identifiability results for other observer families, continuous estimation, or stronger experimental restrictions [7].

If external calibration supplies $L_j\leq b_j\leq U_j$, the sharp common-sensory-variance set for known effective variances is

$$
a\in\left[\max\{0,\max_j(v_j-U_j)\},\ \min_j(v_j-L_j)\right].
\tag{7}
$$

An empty interval rejects the constrained decomposition. Sufficiency follows by choosing $b_j=v_j-a$. Under a uniform bound $0\leq b_j\leq B$, the smallest budget allowing constant sensory variance across conditions is $B^*=\max_jv_j-\min_jv_j$. These are elementary interval consequences of the inherited ambiguity, not new generic variance bounds.

## 4. A single paired-response probability under explicit assumptions

The existing study measured the two tasks in separate blocks; it supplies no paired-response probability from one internal sample. Consider a different, prospective observation model:

$$
Z_O=s+E-C_O,\qquad Z_S=s+E-C_S,
$$

where one **same internal sensory draw** $E\sim N(0,a)$ reaches both consumers. Assume $C_O\sim N(0,b_O)$ and $C_S\sim N(0,b_S)$ are mutually independent and independent of $E$. Their marginal effective variances are $v_t=a+b_t$ and their covariance is $a$. Each task reports whether $|Z_t|\leq k_t$. The two lapse indicators and fair guesses are also independent of one another and of these variables, with known lapse probabilities below one.

**Theorem 4: centered paired identification.** Suppose $v_O,v_S>0$ and finite positive halfwidths $k_O,k_S$ have been independently identified under the observation model. At the calibrated common center $s=0$, a single additional joint probability $P(Y_O=1,Y_S=1)$ uniquely identifies

$$
a\in[0,\min(v_O,v_S)],
$$

under the independence assumptions above.

**Proof.** Put $r_t=k_t/\sqrt{v_t}$ and $\rho=a/\sqrt{v_Ov_S}\geq0$. Before lapses, the paired probability is

$$
J(\rho)=\int_{-r_O}^{r_O}\phi(z)
\left[\Phi\!\left(\frac{r_S-\rho z}{\sqrt{1-\rho^2}}\right)
-\Phi\!\left(\frac{-r_S-\rho z}{\sqrt{1-\rho^2}}\right)\right]dz.
\tag{8}
$$

The normal density identity $\partial_\rho\phi_2=\partial_x\partial_y\phi_2$, integrated over the rectangle, gives the usual Plackett boundary derivative [6]:

$$
J'(\rho)=2\{\phi_2(r_O,r_S;\rho)-\phi_2(r_O,-r_S;\rho)\}>0
\quad(0<\rho<1).
\tag{9}
$$

The inequality holds because $r_Or_S>0$ and positive correlation makes the first corner density larger. $J$ is thus strictly increasing on the nonnegative admissible interval, including by continuity its endpoints. It satisfies $J(0)=q_Oq_S$, where $q_t=2\Phi(r_t)-1$.

With independent lapses, the observed paired probability is

$$
P_{11}=(1-\lambda_O)(1-\lambda_S)J
+\frac{\lambda_O(1-\lambda_S)}2q_S
+\frac{\lambda_S(1-\lambda_O)}2q_O
+\frac{\lambda_O\lambda_S}{4}.
\tag{10}
$$

The coefficient of $J$ is positive and all other quantities are known. Equations (8)–(10) therefore give a unique inverse for $a$. $\square$

With fixed marginal probabilities, a binary pair has exactly one remaining probability degree of freedom. Marginals alone fail by Proposition 3; this one joint probability suffices under the premises. This is a minimal addition in the dimension of the observation law, **not one trial**, a unique optimal experimental protocol, or an assertion that two human tasks can read the identical internal sample without changing it.

The construction is related to classical Gaussian-threshold correlation inference. Its centered two-sided intervals differ from a one-sided tetrachoric setup: $J(\rho)=J(-\rho)$ loses the correlation sign, and its derivative vanishes at zero. The sensory-variance interpretation uses $\rho\geq0$ and the specified independent-criterion model. Multipass procedures have previously used joint behavior to distinguish noise components [5]; repeating the same external stimulus does not generally preserve the same internal sensory draw assumed here.

## 5. Weak identification and an additional off-center observation

Even when the inverse is unique, it may be insensitive. Expanding (9) at zero gives

$$
J(\rho)-J(0)
=2r_Or_S\phi(r_O)\phi(r_S)\rho^2+O(\rho^4).
\tag{11}
$$

There is no first-order sensitivity to a very small shared variance. Finite thresholds far into the tails also make the coefficient very small. In the released-parameter illustration, three profiles have positive joint differences around $10^{-9}$ although a direct floating-point affinity computation rounds to one; this is weak separation, not exact equality.

For known marginal parameters, write the observed joint excess as $d(a)=C a^2+O(a^4)$ with $C>0$. The four binary cell probabilities differ from independence by $(d,-d,-d,d)$. Taylor expansion of the categorical Kullback–Leibler divergence gives

$$
D_{\rm KL}(P_a\Vert P_0)
=\frac{C^2a^4}{2p_O(1-p_O)p_S(1-p_S)}+O(a^6).
\tag{12}
$$

Thus when $n a^4\to0$, Pinsker's bound for $n$ independent observations implies vanishing total-variation separation from $a=0$. Conversely a sample joint proportion can detect the excess when $\sqrt n\,a^2\to\infty$. The centered idealization consequently has a local $n^{-1/4}$ separation scale for the **variance parameter** $a$. This is not an empirical sample-size calculation and assumes the marginal calibration is already known.

A second joint observation at nonzero calibrated SOA supplies local first-order information. Let

$$
L_t=\frac{-k_t-s}{\sqrt{v_t}},\qquad U_t=\frac{k_t-s}{\sqrt{v_t}}.
$$

Its derivative with respect to correlation at zero is

$$
\left.\frac{dJ_s}{d\rho}\right|_{0}
=[\phi(L_O)-\phi(U_O)][\phi(L_S)-\phi(U_S)]>0
\quad(s\ne0).
\tag{13}
$$

Both factors have the same nonzero sign because the physical offset is the same in the two tasks. This restores local first-order sensitivity. Equation (13) does not assert that an arbitrary off-center joint probability is globally monotone in correlation. A calibrated central observation supplies the global nonnegative inverse, while a second offset can improve local information within this prospective model.

## 6. A sharp bound when criterion jitters may be correlated

Full criterion independence is a strong premise. Retain the calibrated-center and lapse assumptions, and let $(C_O,C_S)$ be **jointly Gaussian and independent of $E$**, but potentially correlated. Gaussian marginal distributions alone are insufficient for the joint probability inversion. Let $c=\operatorname{Cov}(C_O,C_S)$ and suppose an external calibration establishes

$$
|c|\leq\kappa\sqrt{(v_O-a)(v_S-a)},\qquad0\leq\kappa\leq1.
\tag{14}
$$

The covariance inequality also defines the limiting case where a criterion variance is zero. Central joint data identify the magnitude $r$ of total correlation, not its sign. Set $R=r\sqrt{v_Ov_S}$.

**Theorem 6: calibrated correlated-criterion identification set.** The sharp set of shared sensory variances is

$$
\mathcal A(r,\kappa)=
\left\{a\in[0,\min(v_O,v_S)]:
(R-a)^2\leq\kappa^2(v_O-a)(v_S-a)\right\}.
\tag{15}
$$

For equal effective variances $v_O=v_S=v$ and $\kappa<1$, the corresponding fraction $x=a/v$ satisfies

$$
\boxed{\quad
\max\!\left(0,\frac{r-\kappa}{1-\kappa}\right)
\leq x\leq\frac{r+\kappa}{1+\kappa}.
\quad}
\tag{16}
$$

At $\kappa=1$ the interval is $[0,(1+r)/2]$, including $[0,1]$ when $r=1$.

**Proof.** Total covariance is $a+c$. Either $a+c=R$ or $a+c=-R$. Since $|R-a|\leq R+a$ for $a,R\geq0$, feasibility of the negative branch implies feasibility of the positive branch at the same $a$. The union of both branches is therefore precisely $|R-a|\leq\kappa\sqrt{(v_O-a)(v_S-a)}$, giving (15).

For every feasible $a$, choose independent $E\sim N(0,a)$ and a bivariate Gaussian criterion vector with variances $v_O-a,v_S-a$ and covariance $c=R-a$. Its covariance matrix is positive semidefinite by (14), so it realizes the required marginal and joint laws. This proves sharpness, including limiting degenerate Gaussian cases.

For equal variances, $|r-x|\leq\kappa(1-x)$. Its two linear inequalities give (16). At $\kappa=1$, only $2x\leq1+r$ restricts $x$ beyond $0\leq x\leq1$. $\square$

For instance, $r=.6$ with an externally justified $\kappa=.2$ identifies a sensory-variance fraction between $.5$ and $2/3$. If $\kappa\geq r$, the interval includes zero; that central paired observation cannot establish a positive sensory component against the permitted correlated-criterion explanation.

For unequal marginal variances and $\kappa<1$, (15) is the intersection of $[0,\min v_t]$ with the interval between the roots of

$$
(1-\kappa^2)a^2+
[\kappa^2(v_O+v_S)-2R]a+
R^2-\kappa^2v_Ov_S\leq0.
\tag{17}
$$

The set can be empty. At $\kappa=1$, its upper endpoint is the smaller of $\min v_t$ and $(v_Ov_S-R^2)/(v_O+v_S-2R)$; the zero-denominator case $v_O=v_S=R$ admits the full interval. These are ordinary covariance and quadratic-inequality calculations. Their value here is an explicit sensitivity statement for a proposed paired readout, not a new covariance principle.

The bound $\kappa$ must come from evidence outside the same joint probability. Estimating it freely from that one probability would restore the ambiguity.

## 7. Counterexamples that delimit the paired claim

**Correlated criteria.** Suppose $v_O=v_S=1$. One construction uses $(a,b_O,b_S,c)=(.2,.8,.8,.3)$; another uses $(.4,.6,.6,.1)$. Both have total covariance $.5$, valid Gaussian covariance matrices, and identical complete joint response curves at all SOAs for the same thresholds and lapses. Pairing alone does not remove a common decision-noise component.

**Independent sensory resampling.** If the two reports use $E_O$ and $E_S$ independently redrawn from the same sensory distribution, then their joint law under independent criteria is the product of marginals for every sensory variance decomposition. The phrase “same stimulus” does not establish the “same internal draw” premise.

**Correlated lapses.** Set both marginal nonlapse probabilities to $.5$, with no common sensory variance. On 20% of trials, let both reports instead use the same fair coin. Marginal yes rates remain $.5$ and the joint yes probability becomes $.30$. Applying an independent-lapse model with the correct marginal lapse rate $.2$ would infer a spurious positive shared variance, approximately $.7602$ when both effective variances are one. Marginal lapse calibration alone does not establish lapse independence.

**Sequential report contamination.** If the second report uses the first answer, reconstructs a new timing sample, or changes its criterion after the first question, equations (8)–(10) are not its observation law. A task instruction to answer twice is not evidence that the required consumers and noise relations have been implemented. An apparatus, control manipulation, or validated response model is needed; this module does not supply one.

## 8. What the present evidence licenses

The source-specific counterpart shows that relative preference for the released noise-varying observer cannot select a sensory anatomical locus over the stated decision-side alternative from marginal counts. The symmetry gate independently shows a necessary response constraint of the centered source family is inadequate under the declared count model. Neither fact establishes that a particular decision-noise explanation is true.

A prospective paired design would test a more informative observation law, but only after validating the common internal sample, centers, lapse process, criterion relation, and task stability. The correlation-bound result states how that inference weakens when criterion independence is replaced by an externally supported tolerance. The latent quantity identified remains a variance component of a selected response model. An interpretation in terms of body ownership experience, agency, or UCT C1 requires additional measurement and physical evidence.

## Verification and prior-art record

The code verifies 27 prior/criterion equivalences, 36 two-level inverses, 37 source marginal predictions by independent jitter integration, all 90 source-derived prospective joint profiles, 48 derivative checks, 36 paired inverses, the near-zero expansion, three off-center derivatives, and explicit correlated-criterion/lapse counterexamples. The correlation-sensitivity formulas agree with 60,060 finite membership checks over 60 parameter settings. These numerical checks support implementation; the arguments above establish the stated finite-model claims.

The separate `SYMMETRY_ANALYSIS_PLAN.json` fixes the conditional source-family test before its statistic was computed. Its derivation and results are in `SYMMETRY_TEST_REPORT.md`. Neither mathematical checks nor conditional simulations are newly collected human data.

### References

1. D'Angelo, M., Lanfranco, R. C., Chancel, M., & Ehrsson, H. H. (2026). Parietal alpha frequency shapes own-body perception by modulating the temporal integration of bodily signals. *Nature Communications, 17*, 53. https://doi.org/10.1038/s41467-025-67657-w
2. Chancel, M. Released study code, `Master_BCI.m` and `modelprediction_log_BCI.m`, associated with [1]. https://osf.io/s5p4v/ . These implement the particular observation law analyzed here.
3. Yarrow, K., Jahn, N., Durant, S., & Arnold, D. H. (2011). Shifts of criteria or neural timing? The assumptions underlying timing perception studies. *Consciousness and Cognition, 20*, 1518–1531. https://doi.org/10.1016/j.concog.2011.07.003
4. Yarrow, K., Solomon, J. A., Arnold, D. H., & Roseboom, W. (2023). The best fitting of three contemporary observer models reveals how participants' strategy influences the window of subjective synchrony. *Journal of Experimental Psychology: Human Perception and Performance, 49*, 1534–1563. https://doi.org/10.1037/xhp0001154 . Appendix A explicitly treats composite sensory/criterion variances. The present lapse notation is defined in (1), not copied from that paper's corrected printed lapse equation.
5. Cabrera, C. A., Lu, Z.-L., & Dosher, B. A. (2015). Separating decision and encoding noise in signal detection tasks. *Psychological Review, 122*, 429–460. https://doi.org/10.1037/a0039348
6. Plackett, R. L. (1954). A reduction formula for normal multivariate integrals. *Biometrika, 41*, 351–360. https://doi.org/10.1093/biomet/41.3-4.351
7. Hahn, M., Wang, E., & Wei, X.-X. (2026). Identifiability of Bayesian models of perception. *Proceedings of the National Academy of Sciences*. https://doi.org/10.1073/pnas.2601013123 . Its broader identifiability results concern specified response paradigms and assumptions; the additive interval counterexample above is not a refutation of them.
