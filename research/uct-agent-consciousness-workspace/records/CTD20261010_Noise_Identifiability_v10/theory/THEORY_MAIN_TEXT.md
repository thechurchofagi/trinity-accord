# Effective timing variability, an exact alternative, and a conditional additional readout

## 1. The inferential target

The source observer expresses a binary report probability as

$$
p_{tf}(s)=\lambda_t/2+(1-\lambda_t)
\left[\Phi\!\left(\frac{k_{tf}-s}{\sqrt{v_{tf}}}\right)
-\Phi\!\left(\frac{-k_{tf}-s}{\sqrt{v_{tf}}}\right)\right],
\tag{1}
$$

where $s$ is stimulus-onset asynchrony, $v$ an effective timing variance, $k$ a decision-interval halfwidth, and $\lambda<1$ a fair-guess lapse probability. The released noise-varying model shares $v_f$ across the two tasks, permits it to change across stimulation, and uses task-specific common-cause priors to determine $k_{tf}$. The parameter $\sqrt v$ belongs to this interval-response model; it is not the separately published descriptive Gaussian width or a direct measurement of neuronal noise.

Response shape can distinguish some changes in effective variance from some changes in decision thresholds. For example, with a known center and lapse, population probabilities at zero and one positive SOA uniquely identify finite positive $\sqrt v$ and $k$: the central probability determines $r=k/\sqrt v$, and the off-center probability is a strictly decreasing function of $s/\sqrt v$ at fixed $r$. Unknown lapse removes this two-point inverse. These facts concern the effective observation law. They do not establish the physical location of its variability.

## 2. A decision-side counterpart with exactly the same intervention curves

Let a sensory sample be $X=s+E$, with $E\sim N(0,a)$, and let the center of a decision interval be $C\sim N(0,b)$, independent of $E$. The report before a lapse is

$$
Y=1\{|X-C|\leq k\}.
$$

Then $E-C\sim N(0,a+b)$ and the response probability depends on the two variances only through $v=a+b$. This Gaussian sensory/criterion ambiguity is established in temporal-judgment research, including Yarrow et al. (2011, 2023). Here the lower and upper criteria move together as $C-k$ and $C+k$, an exact common-center case of that literature.

**Proposition 1.** For any positive condition variances $v_f$ in the source observer, choose a constant $a\in(0,\min_f v_f]$ and set $b_f=v_f-a$. Retain its halfwidths $k_{tf}$ and lapses. This produces sensory variance constant across stimulation and condition-dependent decision variability, while reproducing every marginal response probability at every SOA.

**Proof.** The effective variance in each cell is $a+b_f=v_f$. All arguments of both normal distribution functions in (1), and the lapse mixture, consequently remain unchanged. Thus every probability agrees, and so does the likelihood of any marginal count dataset. $\square$

A fixed rule $a=\tfrac12\min_f v_f$ creates a counterpart of the same fitted dimension; $a$ is not an extra fitted parameter. The original halfwidth trajectory generally changes with stimulation. The alternative therefore reallocates effective variance and preserves the source's condition-specific decision policy. It must not be described as varying only jitter while holding all thresholds fixed, or as the original normative observer with an unchanged sensory interpretation. Instantiating the rule at all 30 released parameter vectors reproduces all 1,260 probabilities to a maximum discrepancy of $2.22\times10^{-16}$, with identical summed negative log likelihoods of 5138.960411207295. This construction supplies an exact alternative interpretation, not evidence that participants actually used it.

A related decision ambiguity affects the source's common-cause prior. If reporting a common cause requires posterior probability above an unknown $\gamma$, its interval is determined by

$$
k^2=\left[\frac{2v(v+S^2)}{S^2}
\left\{\operatorname{logit}\pi-\operatorname{logit}\gamma
+\tfrac12\log(1+S^2/v)\right\}\right]_+.
\tag{2}
$$

Only the difference of prior and report-criterion logits occurs. Shifting both logits equally preserves all predictions. Thus a fitted prior under $\gamma=1/2$ is conditional on that report convention. Relative preference among the released parameterizations does not resolve this alias or Proposition 1's variance decomposition.

## 3. One additional joint probability under explicit premises

Consider a prospective two-consumer observation model in which one **same internal sensory draw** reaches both reports:

$$
Z_O=s+E-C_O,\qquad Z_S=s+E-C_S.
\tag{3}
$$

Assume $E\sim N(0,a)$, independent Gaussian criterion centers $C_t\sim N(0,b_t)$, and mutual independence between the centers and $E$. Then $v_t=a+b_t$ and $\operatorname{Cov}(Z_O,Z_S)=a$. Each consumer reports whether $|Z_t|\leq k_t$. Assume independently calibrated marginal variances, finite positive halfwidths, and lapse probabilities below one. The two lapse decisions and fair guesses must also be independent of one another and of the Gaussian variables. Calibration must establish a common center at $s=0$.

**Theorem 2.** Under these premises, the additional population probability $P(Y_O=1,Y_S=1)$ at the common center uniquely identifies $a\in[0,\min(v_O,v_S)]$.

**Proof.** Put $r_t=k_t/\sqrt{v_t}$ and $\rho=a/\sqrt{v_Ov_S}\geq0$. The joint nonlapse probability is the centered Gaussian rectangle

$$
J(\rho)=P(-r_O\leq U_O\leq r_O,\ -r_S\leq U_S\leq r_S),
\tag{4}
$$

for standard Gaussian variables with correlation $\rho$. Integrating the Gaussian density identity $\partial_\rho\phi_2=\partial_x\partial_y\phi_2$ gives the classical boundary derivative (Plackett, 1954)

$$
J'(\rho)=2[\phi_2(r_O,r_S;\rho)-\phi_2(r_O,-r_S;\rho)]>0
\quad(0<\rho<1).
\tag{5}
$$

The two corner densities differ strictly because $r_Or_S\rho>0$. Hence $J$ increases strictly over the admissible nonnegative interval, including its endpoints by continuity. Independent lapses give

$$
P_{11}=(1-\lambda_O)(1-\lambda_S)J
+\lambda_O(1-\lambda_S)q_S/2
+\lambda_S(1-\lambda_O)q_O/2
+\lambda_O\lambda_S/4,
\tag{6}
$$

where $q_t=2\Phi(r_t)-1$. This is an affine transformation of $J$ with positive slope and known remaining terms, so it has the same unique inverse. $\square$

For fixed marginal probabilities a binary pair has one remaining probability degree of freedom. Marginals fail to identify $a$ by Proposition 1; this one added probability suffices under Theorem 2. Minimality concerns the dimension of the observation law, not one physical trial or an optimal human protocol. Two-sided centered rectangles lose the correlation sign, since $J(\rho)=J(-\rho)$; nonnegative correlation here follows from the independent-criterion model.

The theorem does not identify $a$ from the present study. Its tasks were measured in separate blocks, and the conditional symmetry test rejects physical zero SOA as a valid center restriction of the source family under the stated binomial model. Fitting different stable task centers does not automatically yield one physical SOA centered for both. The paired result is therefore a prospective calibration protocol. It requires independent evidence that both consumers receive the same internal draw and that eliciting both reports preserves their observation laws.

## 4. A sharp sensitivity bound for correlated decision variability

Independence between the two criterion centers is the strongest exclusion in Theorem 2. Retain the calibrated-center and lapse assumptions, require that the criterion vector is jointly Gaussian and independent of $E$, and replace independence between its components by an externally supported bound

$$
|c|\leq\kappa\sqrt{(v_O-a)(v_S-a)},\qquad
c=\operatorname{Cov}(C_O,C_S),\quad0\leq\kappa\leq1.
\tag{7}
$$

The covariance formulation includes limiting zero-variance criteria. A calibrated centered joint probability identifies the magnitude $r$ of total Gaussian correlation. Set $R=r\sqrt{v_Ov_S}$.

**Theorem 3.** The sharp identified set is

$$
\mathcal A(r,\kappa)=\{a\in[0,\min(v_O,v_S)]:
(R-a)^2\leq\kappa^2(v_O-a)(v_S-a)\}.
\tag{8}
$$

For equal effective variances $v_O=v_S=v$, $x=a/v$ satisfies, when $\kappa<1$,

$$
\boxed{\max\left(0,\frac{r-\kappa}{1-\kappa}\right)
\leq x\leq\frac{r+\kappa}{1+\kappa}.}
\tag{9}
$$

At $\kappa=1$, the interval is $[0,(1+r)/2]$, including $[0,1]$ if $r=1$.

**Proof.** The total covariance is $a+c$, whose sign is unobserved, so either $a+c=R$ or $a+c=-R$. Since $|R-a|\leq R+a$ for $a,R\geq0$, feasibility of the negative branch implies feasibility of the positive branch at the same $a$. Their union is therefore precisely $|R-a|\leq\kappa\sqrt{(v_O-a)(v_S-a)}$, yielding (8).

For every $a$ in that set, take independent $E\sim N(0,a)$ and a bivariate Gaussian criterion vector with variances $v_O-a,v_S-a$ and covariance $c=R-a$. Its covariance matrix is positive semidefinite by the displayed inequality, so it realizes the observed marginal and joint laws. This proves attainability and sharpness, including degenerate limiting distributions. With equal variances, $|r-x|\leq\kappa(1-x)$ reduces to the two linear bounds in (9). $\square$

For example, $r=.6$ and a calibrated $\kappa=.2$ imply $x\in[.5,2/3]$. If $\kappa\geq r$, zero belongs to the set; the observation cannot establish a positive shared sensory component against the permitted decision correlation. With unequal variances, (8) is a quadratic inequality intersected with $[0,\min v_t]$ and may have no solution. The correlation tolerance must come from additional evidence. Estimating it freely from the same single joint probability would remove its identifying force.

This bound uses ordinary Gaussian covariance feasibility. The substantive gain is a transparent sensitivity statement for the proposed readout: how much inference survives a specified violation of criterion independence. The analysis does not claim a new general covariance theorem.

## 5. Precision and failure boundaries

The centered inverse is unique but weak near independence. Equation (5) implies

$$
J(\rho)-J(0)=2r_Or_S\phi(r_O)\phi(r_S)\rho^2+O(\rho^4).
\tag{10}
$$

Known marginal parameters give joint excess $d(a)=Ca^2+O(a^4)$ with $C>0$. The four binary probabilities change from independence by $(d,-d,-d,d)$; their Kullback–Leibler divergence is of order $a^4$. Thus $n a^4\to0$ implies asymptotically indistinguishable experiments, whereas a joint proportion separates them when $\sqrt n a^2\to\infty$. The idealized local scale is $n^{-1/4}$ for the variance $a$, not its standard deviation. Unknown calibration and nearly saturated intervals can make practical inference much weaker.

At a shared nonzero offset, define $L_t=(-k_t-s)/\sqrt{v_t}$ and $U_t=(k_t-s)/\sqrt{v_t}$. The derivative at zero correlation becomes

$$
J_s'(0)=[\phi(L_O)-\phi(U_O)][\phi(L_S)-\phi(U_S)]>0.
\tag{11}
$$

A second offset can therefore add first-order local information. This local result is not a claim of global monotonicity for arbitrary off-center intervals or a sample-size recommendation.

Three explicit failures delimit the repair. First, the decompositions $(a,b_O,b_S,c)=(.2,.8,.8,.3)$ and $(.4,.6,.6,.1)$ have the same marginal variances and total covariance, hence identical complete joint curves; unrestricted common decision noise survives pairing. Second, independently resampling the sensory variable for each report gives product marginals regardless of $a$: the same external stimulus does not mean the same internal sample. Third, correlated lapses can create joint dependence without shared sensory variance. With both marginal yes probabilities $.5$, replacing both reports by one shared fair coin on 20% of trials gives $P_{11}=.30$ while keeping both marginals unchanged. Sequential report effects create further departures if the first answer changes the second consumer's sample or criterion.

Joint-response methods for noise separation have substantial precedents, including Cabrera, Lu, and Dosher (2015); their multipass methods should not be equated with the same-internal-draw construction here. The contribution is the source-specific intervention equivalence, its conditional centered-readout repair, and explicit sensitivity and weak-identification limits. The identified quantity remains a component of a chosen response model. Neither the marginal comparison nor the prospective joint protocol alone establishes neuronal mediation, an experiential scale, or a consequence of UCT C1.

**Verification.** Independent code checks the source equivalence by direct jitter integration, reproduces all 90 prospective joint profiles, verifies derivative and inverse calculations, and checks the sharp correlation sets at 60,060 grid points across 60 parameter settings. Full proofs, counterexamples, primary references, and reproducible checks are retained in `RESPONSE_IDENTIFIABILITY_RESULTS.md` and `BCI_IDENTIFICATION_CHECKS.json`.
