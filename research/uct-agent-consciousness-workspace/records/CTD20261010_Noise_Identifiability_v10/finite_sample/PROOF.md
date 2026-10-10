# Finite-sample confidence sets for a calibrated paired-response model

**CTD v1.0 scientific extension, 10 October 2026.** This note turns the previous population-probability result into a finite-sample confidence procedure. Its ingredients are the classical Clopper–Pearson interval and elementary confidence-set projection. The contribution is their explicit application to this paired Gaussian interval observer, including nuisance criterion correlation, sharp endpoints, empty sets, degenerate readouts, and calibration uncertainty. No new general confidence-interval or Gaussian noise-decomposition theorem is claimed.

The result concerns a **prospective, calibrated paired-response protocol**. The source experiment supplies responses from separate tasks, not the same internal sensory draw required here. Its centered response restriction also fails the reported symmetry check. Consequently, the construction below is not an additional estimate of a participant's sensory variance from those existing counts, and it is not a validated measure of experience or a consequence of UCT C1.

## 1. Observation contract and target

For each independently repeated paired trial, suppose

\[
Z_O=E-C_O,\qquad Z_S=E-C_S,
\]

where one **same internal draw** \(E\sim N(0,a)\) reaches both consumers. The vector \((C_O,C_S)\) is jointly Gaussian, is independent of \(E\), and has covariance matrix

\[
\begin{pmatrix}v_O-a&c\\c&v_S-a\end{pmatrix}.
\tag{1}
\]

The effective marginal variances \(v_O,v_S>0\), halfwidths \(k_O,k_S\geq0\), and common zero response center are calibrated in fixed units. Halfwidths are finite. Before lapses, task \(t\) reports \(Y_t^0=1\{|Z_t|\leq k_t\}\). With known probability \(\lambda_t\in[0,1]\), its response is instead an independent fair guess. Both lapse indicators, both guesses, and the Gaussian variables are independent except for the dependence explicitly specified in (1) and the shared \(E\). This within-trial lapse condition matters even when the marginal lapse rates are known exactly.

The target is the variance \(a\) of the stipulated shared sensory draw. The admissible domain and independently justified criterion-covariance restriction are

\[
0\leq a\leq m:=\min(v_O,v_S),\qquad
|c|\leq\kappa\sqrt{(v_O-a)(v_S-a)},\quad 0\leq\kappa\leq1.
\tag{2}
\]

The covariance inequality defines the boundary cases where a criterion variance is zero; a correlation coefficient need not be defined there. A supplied \(\kappa\) is an assumption or an external calibration bound. The one joint probability below cannot independently calibrate it.

All paired trials must have the same parameters and be independent. The sample size \(n\) is fixed independently of their outcomes. On trial \(j\), define \(B_j=1\{Y_{Oj}=Y_{Sj}=1\}\) and retain

\[
K=\sum_{j=1}^n B_j\sim\operatorname{Binomial}(n,p_{11}).
\tag{3}
\]

Thus \(n\) counts paired trials, not individual reports. Within-pair dependence is permitted and is precisely what is measured. Unmodeled dependence across trials, nonidentical trial probabilities, optional stopping without a suitable sequential construction, sensory resampling between reports, or report-induced changes to the second decision are outside this contract. Implementing two reports on one physical trial does not by itself establish that they read the same internal draw.

## 2. The population map and its attainable range

Write \(h_t=k_t/\sqrt{v_t}\), \(q_t=2\Phi(h_t)-1\), and

\[
J(r)=\Pr\{|U_O|\leq h_O,|U_S|\leq h_S\},\qquad
r=\frac{|a+c|}{\sqrt{v_Ov_S}}.
\]

The centered Gaussian rectangle is even in the signed total correlation. The observed joint probability is

\[
F(r)=(1-\lambda_O)(1-\lambda_S)J(r)
 +\frac{\lambda_O(1-\lambda_S)q_S}{2}
 +\frac{\lambda_S(1-\lambda_O)q_O}{2}
 +\frac{\lambda_O\lambda_S}{4}.
\tag{4}
\]

For positive finite \(h_O,h_S\),

\[
J(0)=q_Oq_S,\qquad J(1)=\min(q_O,q_S),
\]

and Plackett's Gaussian differentiation identity gives, for \(0<r<1\),

\[
J'(r)=2\{\phi_2(h_O,h_S;r)-\phi_2(h_O,-h_S;r)\}>0.
\tag{5}
\]

The inequality follows because the two density exponents differ by \(2rh_Oh_S/(1-r^2)>0\). Continuity at the endpoints and strict increase in the interior establish that \(J\), and hence \(F\) when both lapses are below one, is strictly increasing on \([0,1]\). Equation (5) and the marginal sensory/criterion-noise ambiguity are inherited results, not new mathematical claims here [2–4].

Not every \(r\in[0,1]\) is necessarily attainable under (2) when the marginal variances differ. Put \(M=\max(v_O,v_S)\). The global maximum is

\[
r_{\max}=\frac{1}{\sqrt{mM}}
\max_{0\leq a\leq m}\left[a+\kappa\sqrt{(m-a)(M-a)}\right].
\tag{6}
\]

It equals one if \(m=M\). More generally, with \(\kappa_c=2\sqrt{mM}/(m+M)\),

\[
r_{\max}=
\begin{cases}
\dfrac{m+M-(M-m)\sqrt{1-\kappa^2}}{2\sqrt{mM}},&0\leq\kappa\leq\kappa_c,\\[6pt]
\kappa,&\kappa_c\leq\kappa\leq1.
\end{cases}
\tag{7}
\]

The expressions agree at \(\kappa_c\). In particular \(r_{\max}=\sqrt{m/M}\) at \(\kappa=0\), and \(r_{\max}=1\) at \(\kappa=1\).

**Proof of (6)–(7).** At a fixed \(a\), the largest absolute total covariance is \(a+\kappa\sqrt{(m-a)(M-a)}\). The positive choice dominates the negative choice because \(a\geq0\). When \(M>m\) and \(0<\kappa<1\), substitute \(y=m-a\), differentiate, and obtain the interior stationary point

\[
y^*=\frac{M-m}{2}\left(\frac{1}{\sqrt{1-\kappa^2}}-1\right).
\]

If \(y^*\leq m\), substitution gives the first line of (7). Otherwise the maximum is at \(a=0\), giving its second line. The boundary separating these cases is \(\kappa_c\). The cases \(\kappa=0,1\) and \(M=m\) follow by direct evaluation or continuity. The admissible \((a,c)\) set is connected, and contains \((0,0)\), so every absolute correlation from zero to its maximum is attained. \(\square\)

Therefore the model's full attainable joint-probability range is

\[
\mathcal P=[F(0),F(r_{\max})].
\tag{8}
\]

## 3. Clopper–Pearson projection and finite-sample coverage

For \(0<\alpha<1\), use the closed, equal-tailed Clopper–Pearson interval \(I_\alpha(K)=[L_K,U_K]\) [1]:

\[
L_K=\begin{cases}0&K=0,\\
\operatorname{Beta}^{-1}(\alpha/2;K,n-K+1)&K>0,
\end{cases}
\]

\[
U_K=\begin{cases}1&K=n,\\
\operatorname{Beta}^{-1}(1-\alpha/2;K+1,n-K)&K<n.
\end{cases}
\tag{9}
\]

For completeness, define \(I_\alpha(0)=[0,1]\) when \(n=0\). This use of “exact” means that coverage is at least \(1-\alpha\) under the finite binomial law, without an asymptotic normal approximation; discreteness generally makes coverage exceed the nominal level.

Define the projected set

\[
\mathcal C_\alpha(K)=
\left\{a\in[0,m]:\exists c\text{ satisfying (2) such that }
F\left(\frac{|a+c|}{\sqrt{v_Ov_S}}\right)\in I_\alpha(K)\right\}.
\tag{10}
\]

**Theorem 1: finite-sample coverage under known calibration.** Under the complete contract in Section 1, for every admissible true \((a_0,c_0)\),

\[
\Pr_{a_0,c_0}\{a_0\in\mathcal C_\alpha(K)\}\geq1-\alpha.
\tag{11}
\]

In fact, with the same probability bound, \(\mathcal C_\alpha(K)\) contains the **entire population identified set** associated with the true joint probability and the stipulated calibration.

**Proof.** The binomial upper-tail construction of \(L_K\) bounds \(\Pr_{p_0}\{L_K>p_0\}\) by \(\alpha/2\); its lower-tail counterpart bounds \(\Pr_{p_0}\{U_K<p_0\}\) by \(\alpha/2\). Their union bounds the exclusion probability by \(\alpha\), which is the classical Clopper–Pearson coverage argument. On the event \(p_0\in I_\alpha(K)\), the actual \(c_0\) witnesses that \(a_0\) satisfies (10). More strongly, every \(a\) capable of producing that same \(p_0\) with some admissible \(c\) satisfies (10). Hence the one event \(p_0\in I_\alpha(K)\) implies both coverage statements. \(\square\)

There is no additional multiplicity penalty for the statement about the entire identified set: all its elements are retained on the same single probability-coverage event. This does not authorize multiple unadjusted, separately constructed confidence claims across participants, stimulation conditions, or later-selected models.

**Empty-set rule.** If

\[
I_\alpha(K)\cap\mathcal P=\varnothing,
\tag{12}
\]

then \(\mathcal C_\alpha(K)=\varnothing\). Do not clip an incompatible observed interval to \(a=0\) or \(a=m\). Under any member of the specified family, the probability of (12) is at most \(\alpha\), because it implies that the true \(p_0\) is outside the CP interval. Thus emptiness is a level-at-most-\(\alpha\) rejection of the **combined model and calibration contract**, not a positive estimate, an attribution of which premise failed, or a rejection of a whole consciousness theory.

## 4. Sharp closed-form endpoints for equal effective variances

Assume a nondegenerate readout: both halfwidths are positive and both lapses are below one. After first checking (12), write

\[
[L'_K,U'_K]=I_\alpha(K)\cap\mathcal P,\qquad
[r_L,r_U]=[F^{-1}(L'_K),F^{-1}(U'_K)].
\tag{13}
\]

The inverse is restricted to \([0,r_{\max}]\). In equal effective variances \(v_O=v_S=v\), let \(x=a/v\). A known absolute total correlation \(r\) is compatible exactly when

\[
|r-x|\leq\kappa(1-x),\quad 0\leq x\leq1.
\tag{14}
\]

The negative-total-covariance branch has not been discarded: if it permits \(x\), then \(r+x\leq\kappa(1-x)\), which implies \(|r-x|\leq\kappa(1-x)\). Conversely every solution to (14) is realized by the positive branch \(c=v(r-x)\), with a positive semidefinite jointly Gaussian criterion vector. Thus (14) is the exact union of both signs.

**Theorem 2: sharp finite-sample projection at equal variance.** For \(0\leq\kappa<1\),

\[
\boxed{\displaystyle
\mathcal C_\alpha(K)=v\left[
\max\left\{0,\frac{r_L-\kappa}{1-\kappa}\right\},
\frac{r_U+\kappa}{1+\kappa}\right].}
\tag{15}
\]

For \(\kappa=1\),

\[
\boxed{\displaystyle
\mathcal C_\alpha(K)=v[0,(1+r_U)/2].}
\tag{16}
\]

**Proof.** At a single \(r\), solving the two linear inequalities in (14) gives

\[
\mathcal A(r,\kappa)=v\left[\max\{0,(r-\kappa)/(1-\kappa)\},
(r+\kappa)/(1+\kappa)\right]
\]

for \(\kappa<1\), and \(v[0,(1+r)/2]\) when \(\kappa=1\). The set of pairs \((x,r)\) satisfying (14) and \(r\in[r_L,r_U]\) is convex, being an intersection of linear halfspaces. Its projection onto \(x\) is therefore an interval. The lowest possible endpoint is attained at \(r_L\), and the highest at \(r_U\), because both single-\(r\) endpoint functions are nondecreasing. The Gaussian construction following (14) attains every included parameter. These are exact projected sets, not just sufficient outer bounds. \(\square\)

“Sharp” here refers to the model projection of the chosen CP interval. It does not mean that CP is the shortest possible confidence procedure, that \(K\) uses all information in the four-cell paired response table, or that the model's assumptions have been verified.

For \(\kappa=0\), (15) reduces to \(v[r_L,r_U]\). At positive \(\kappa\), the interval retains an identification component even with infinitely many trials. For example, \(r=0\) gives \([0,v\kappa/(1+\kappa)]\), and \(r=.6,\kappa=.2\) gives \([.5v,2v/3]\). The endpoint case \(r=1\) is sensitive to the bound: any \(\kappa<1\) forces \(a=v\), while \(\kappa=1\) admits the entire \([0,v]\). Replacing an uncalibrated bound of one by a number just below one is therefore not innocuous.

## 5. Unequal variances without a nuisance grid

This section supports the general implementation; the fixed operating-characteristic study uses \(v_O=v_S=1\).

For \(R=r\sqrt{v_Ov_S}\), the point identified set is

\[
\mathcal A(R)=\{a\in[0,m]:(R-a)^2\leq\kappa^2(v_O-a)(v_S-a)\}.
\tag{17}
\]

As before, the negative covariance branch is included because \(|R-a|\leq R+a\). Every feasible point is realized by choosing \(c=R-a\) and the corresponding Gaussian covariance matrix.

At \(\kappa<1\), (17) is a quadratic sublevel interval with coefficients

\[
A=1-\kappa^2,\quad B=\kappa^2(v_O+v_S)-2R,\quad
C=R^2-\kappa^2v_Ov_S,
\tag{18}
\]

intersected with \([0,m]\). For \(\kappa=1\), it becomes

\[
\mathcal A(R)=\left[0,\min\left\{m,
\frac{v_Ov_S-R^2}{v_O+v_S-2R}\right\}\right],
\tag{19}
\]

unless the denominator is zero, which occurs only at \(v_O=v_S=R\) and gives \([0,m]\).

Let \(R_L=r_L\sqrt{v_Ov_S}\), \(R_U=r_U\sqrt{v_Ov_S}\), and let \(\ell(R),u(R)\) be the endpoints of (17). After the attainable-range check, the exact interval union is

\[
\mathcal C_\alpha(K)=
[\ell(R_L),\ u(\operatorname{clip}(m,[R_L,R_U]))].
\tag{20}
\]

**Proof of the interval union.** Put \(h(a)=\sqrt{(v_O-a)(v_S-a)}\). It is concave on \([0,m]\), with negative second derivative \(-(v_O-v_S)^2/[4h(a)^3]\) in the unequal-variance interior. Thus the region \(|R-a|\leq\kappa h(a)\) is convex, and its intersection with the vertical strip \(R\in[R_L,R_U]\) projects to an interval. Also \(g_-(a)=a-\kappa h(a)\) is increasing. The smallest feasible \(a\) occurs at \(R_L\): a smaller \(a\) admitted at any larger \(R\) would also satisfy \(g_-(a)\leq R_L\) and \(a+\kappa h(a)\geq R_L\), contradicting the lower endpoint at \(R_L\). For the upper endpoint, if the strip includes \(R=m\), then \(a=m,c=0\) is feasible. If \(R_U<m\), the largest feasible \(a\) is controlled by \(g_-(a)\leq R_U\) and equals \(u(R_U)\). If \(R_L>m\), the lower-covariance constraint is automatic and feasibility is controlled by \(a+\kappa h(a)\geq R_L\), giving \(u(R_L)\). These are the three branches of (20). \(\square\)

This analytic projection avoids searching a finite grid over \(a\), \(c\), or nuisance correlation. A grid would generally miss compatible points and cannot establish coverage of a continuous parameter set.

## 6. Degenerate readouts and weak identification

If either \(k_t=0\), its nonlapse interval has probability zero because its effective variance is positive. If either \(\lambda_t=1\), that report is an independent fair guess. In either case, (4) is a constant \(p_*\), independent of \(a\) and \(c\). Therefore

\[
\mathcal C_\alpha(K)=
\begin{cases}
[0,m],&p_*\in I_\alpha(K),\\
\varnothing,&p_*\notin I_\alpha(K).
\end{cases}
\tag{21}
\]

For example, a unit lapse in task O gives \(p_*=(1/2)\{\lambda_S/2+(1-\lambda_S)q_S\}\). If its halfwidth and lapse are both zero, then \(p_*=0\), \(K=0\) almost surely, and the full domain is retained. A constant readout is not evidence for zero shared variance. With \(n=0\), the confidence set is the full physical domain for every valid calibration.

Positive finite halfwidths and lapses below one remove these exact degeneracies, but identification can still be weak. Near \(r=0\),

\[
J(r)=q_Oq_S+2h_Oh_S\phi(h_O)\phi(h_S)r^2+O(r^4).
\tag{22}
\]

The first derivative at zero vanishes. Thus an ordinary probability uncertainty of order \(n^{-1/2}\) can translate locally into an upper-correlation uncertainty of order \(n^{-1/4}\), rather than the usual linear inverse scale. This is a local asymptotic explanation of wide sets, not a finite-sample coverage approximation or a proposed sample-size rule. The exact coverage theorem uses neither derivative nor normal approximation. At \(\kappa>0\), uncertainty about criterion correlation adds the nonvanishing identified-set width discussed after (16).

## 7. External calibration uncertainty

Let \(\theta=(v_O,v_S,k_O,k_S,\lambda_O,\lambda_S,\kappa)\) denote the full calibration in fixed physical units. Suppose external calibration yields a random set \(\mathcal K_\gamma\) satisfying

\[
\Pr\{\theta_0\in\mathcal K_\gamma\}\geq1-\gamma,
\tag{23}
\]

and suppose the covariance bound in \(\theta_0\) admits the true \((a_0,c_0)\). Define

\[
\mathcal C_{\alpha,\gamma}(K,\mathcal K_\gamma)=
\bigcup_{\theta\in\mathcal K_\gamma}\mathcal C_\alpha(K;\theta).
\tag{24}
\]

**Theorem 3: calibrated-union coverage.** If the paired-data CP coverage and (23) are individually valid, then

\[
\Pr\{a_0\in\mathcal C_{\alpha,\gamma}\}\geq1-\alpha-\gamma.
\tag{25}
\]

Independence between the two data sources is not required for this union-bound result.

**Proof.** On \(\{\theta_0\in\mathcal K_\gamma\}\cap\{p_0\in I_\alpha(K)\}\), Theorem 1 places \(a_0\) in the union's \(\theta_0\) member. The complement of this event has probability at most \(\alpha+\gamma\). The same argument covers the true-calibration population identified set. \(\square\)

Independence is not needed for the proof, but using the paired data to construct \(\mathcal K_\gamma\) still requires a valid calibration-set coverage guarantee for that procedure. Plugging fitted nuisance parameters into (15) supplies no such guarantee. To target overall 95% coverage with uncertain calibration, the error budgets must satisfy \(\alpha+\gamma\leq.05\); for example \(\alpha=\gamma=.025\). Two separate 95% statements yield the union-bound guarantee of 90%, not 95%.

**A continuous calibration case with an analytic solution.** If all other parameters are known and the only calibration uncertainty is \(\kappa\in[\kappa_L,\kappa_U]\), feasible covariance sets grow monotonically with \(\kappa\). Therefore

\[
\bigcup_{\kappa\in[\kappa_L,\kappa_U]}
\mathcal C_\alpha(K;\kappa)=\mathcal C_\alpha(K;\kappa_U).
\tag{26}
\]

An externally valid probability-at-least-\(1-\gamma\) upper bound on the absolute criterion correlation is sufficient for this case. It does not have to be estimated from the one paired-yes probability.

**Computation boundary.** The supplied code implements known-calibration projection, the analytic continuous-\(\kappa\) case, and exact unions over **explicit finite calibration sets**. It does not claim to solve arbitrary continuous confidence regions in all seven calibration coordinates. Evaluating a finite grid inside such a region produces an inner approximation to its union and can exclude the truth; it has no automatic coverage guarantee. A rigorous continuous implementation would need an analytic solution, a certified enclosing optimization, or a demonstrably conservative outer set. Arbitrarily filling gaps between the union's intervals also changes the procedure and must be labeled as a conservative outer envelope rather than the exact union.

## 8. Executable implementation and verification scope

`confidence_sets.py` provides the following functions:

| Function | Contract |
| --- | --- |
| `PairCalibration(...)` | Validates positive effective variances, finite nonnegative halfwidths, and lapse/bound parameters in [0,1]. |
| `clopper_pearson(K,n,alpha)` | Closed equal-tailed binomial interval, with explicit K=0, K=n and n=0 cases. |
| `paired_yes_probability(a,c,calibration)` | Physical paired probability; checks Gaussian covariance feasibility but permits a deliberately wrong assumed kappa for labeled negative controls. |
| `project_probability_interval(L,U,calibration)` | Full sharp projection, including both total-covariance signs and empty/full-domain cases. |
| `confidence_set(K,n,calibration,alpha)` | CP interval followed by projection. |
| `population_identified_set(p11,calibration)` | The population set; this is not a finite-sample interval. |
| `finite_calibration_union(...)` | Exact union of a specified finite calibration set, with an explicitly conditional calibration-coverage statement. |
| `kappa_calibration_interval(...)` | Continuous kappa uncertainty handled at its upper endpoint, as in (26). |

The probability-to-correlation inverse is a deterministic scalar root solve, cached independently of \(\kappa\). Centered Gaussian rectangles use Owen's T function or direct one-dimensional quadrature for small radii, with analytic values at zero and unit correlation. Special functions and roots are evaluated in floating-point arithmetic. The mathematical coverage and projection proofs concern exact probabilities; the implementation is numerically checked, not an interval-arithmetic certificate. Narrow numerical tolerances used in checks are reported separately from statistical error probabilities.

`check_confidence_sets.py` and its JSON receipt check the independent rectangle integral, the finite binomial formula, the analytic covariance projections including unequal variances, degeneracies, calibration-union behavior, and selected direct coverage implications. The separately fixed `ANALYSIS_PLAN.json` governs `run_operating_characteristics.py`: all possible counts are enumerated for 480 synthetic scenarios, including 240 within the contract. No source parameter examples, new human data, random Monte Carlo draws, or refitting of the original empirical models enter that analysis. Its operating characteristics are finite sums against the binomial probability mass, not an empirical validation of the paired protocol.

The construction resolves one previously open inferential step: a population-level readout can now be accompanied by a confidence set with an explicit finite-sample coverage guarantee under stated calibration and observation assumptions. It does not resolve whether a real procedure satisfies the same-sample, Gaussian, center, lapse, or criterion-correlation premises. Those remain independent experimental requirements.

## References and attribution

1. Clopper, C. J., & Pearson, E. S. (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika, 26*(4), 404–413. <https://doi.org/10.1093/biomet/26.4.404>. Source of the inherited exact binomial interval; publisher metadata independently checked on 10 October 2026.
2. Plackett, R. L. (1954). A reduction formula for normal multivariate integrals. *Biometrika, 41*, 351–360. <https://doi.org/10.1093/biomet/41.3-4.351>. Source of the inherited Gaussian correlation derivative.
3. Yarrow, K., Jahn, N., Durant, S., & Arnold, D. H. (2011). Shifts of criteria or neural timing? *Consciousness and Cognition, 20*, 1518–1531. <https://doi.org/10.1016/j.concog.2011.07.003>. Prior sensory/criterion noise decomposition and calibration limits.
4. Yarrow, K., Solomon, J. A., Arnold, D. H., & Roseboom, W. (2023). The best fitting of three contemporary observer models reveals how participants' strategy influences the window of subjective synchrony. *Journal of Experimental Psychology: Human Perception and Performance, 49*, 1534–1563. <https://doi.org/10.1037/xhp0001154>. Gaussian sensory and criterion variation already appear in its observer-model analysis.
5. Cabrera, C. A., Lu, Z.-L., & Dosher, B. A. (2015). Separating decision and encoding noise in signal detection tasks. *Psychological Review, 122*(3), 429–460. <https://doi.org/10.1037/a0039348>. Prior joint-response approaches to noise decomposition; their multipass design must not be equated with the same internal draw assumed here.
6. SciPy developers. `scipy.special.owens_t` and `scipy.stats.binomtest` documentation. <https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.owens_t.html>; <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html>. Primary implementation documentation, checked on 10 October 2026. Runtime versions are recorded with the executable checks.

The projection and union-bound arguments are elementary standard statistical principles proved in full above. Neither their use here nor equations (15)–(26) should be presented as a newly invented general framework for confidence inference.
