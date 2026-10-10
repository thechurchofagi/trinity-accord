# Shared perturbations and psychometric-width bridges: proportional and ordinal identification boundaries

**Prepared:** 10 October 2026.  
**Role:** English theoretical module for an empirical secondary-analysis paper.  
**Scope:** two predeclared task endpoints measured in the same participant under a finite set of interventions. The results below concern specified measurement models. They are neither a test of all consciousness theories nor a derivation of an experiential measurement law from UCT C1.

## 1. The question that the data can answer

An intervention can change two task endpoints without establishing that the two changes are proportional expressions of one shared latent process. Conversely, failure of proportionality does not necessarily establish two latent processes: one shared coordinate may be transformed nonlinearly by the two task-specific measurement relations.

This distinction is directly relevant to the dataset of D'Angelo, Lanfranco, Chancel, and Ehrsson, *Parietal alpha frequency shapes own-body perception by modulating the temporal integration of bodily signals* (Nature Communications 17, 53, 2026; DOI 10.1038/s41467-025-67657-w). The source study used ownership and simultaneity judgments and included an experimental stimulation manipulation. The proposed secondary analysis asks a more restrictive, separately declared question about the relation between the two fitted task widths. It does not attribute the exact proportional model below to the original authors. Their empirical findings and model comparisons remain their results.

Fix one participant. Let \(t\in\{O,S\}\) index the ownership and simultaneity tasks and let \(f\in\mathcal F\) index the stimulation conditions. Let \(W_{tf}>0\) be the population-level width of the predeclared psychometric function for that task and condition. A fitted estimate is written \(\widehat W_{tf}\), not silently substituted for the population quantity. All definitions below also apply to other positive endpoints when their measurement interpretation is justified.

We compare three nested or progressively relaxed propositions:

1. **Multiplicative psychometric-width bridge:** \(W_{tf}=c_t\tau_f\), with \(c_t>0\) independent of the stimulation condition.
2. **Shared scalar width bridge with increasing task maps:** \(W_{tf}=h_t(\tau_f)\), with each \(h_t\) strictly increasing and independent of the stimulation condition.
3. **Shared scalar width bridge with nondecreasing task maps:** the same representation, allowing task-specific saturation. This is the closure of the strictly increasing model on a finite condition set.

The latent coordinate \(\tau_f\) is defined through this candidate operational model. Fitting any of these models does not identify a physical oscillator, establish mediation through a particular circuit, or identify an experiential subject. A common scalar statistical representation can arise through mechanisms other than a common physical clock.

This hierarchy is not new measurement theory. The ordinal level is a state-trace hypothesis of the kind developed by Bamber (1979), Prince, Brown, and Heathcote (2012), and Kalish, Dunn, Burdakov, and Sysoev (2016). Proportionality is a more restrictive measurement assumption. The present proposed contribution is to apply and contrast these assumptions in a specific causal-intervention dataset and to report their exact minimum required departures in interpretable units.

## 2. Exact proportionality and the minimum multiplicative departure

Write \(\ell_{tf}=\log W_{tf}\) and

\[
d_f=\ell_{Of}-\ell_{Sf}.
\]

### Proposition 1: equivalent forms of the proportional model

The following conditions are equivalent:

\[
W_{tf}=c_t\tau_f,\qquad c_t,\tau_f>0;
\]

\[
\ell_{tf}=a_t+b_f;
\]

\[
d_f=d_g\quad\text{for every }f,g;
\]

\[
W_{Of}W_{Sg}=W_{Og}W_{Sf}\quad\text{for every }f,g.
\]

**Proof.** Taking logarithms gives the second representation from the first. Subtracting the task rows makes \(d_f=a_O-a_S\), independent of \(f\). Conversely, if \(d_f=d\) is constant, choose \(a_O=d\), \(a_S=0\), and \(b_f=\ell_{Sf}\). Exponentiation recovers the first representation. The last condition is exactly equality of the log differences after exponentiating. \(\square\)

For two conditions, this demands equality of the within-task width ratios, or equivalently equality of the two log changes. For three conditions it demands two independent constraints. An average log change of zero across participants is much weaker than these participant-specific restrictions.

**Scale qualification.** A within-task width ratio is invariant to a positive multiplicative rescaling \(W\mapsto cW\). It is not invariant to a general positive affine transformation \(W\mapsto a+cW\) unless \(a=0\). Equivalently, differences of log widths eliminate an additive offset in log space. This wording matters when describing the measurement assumption.

### Theorem 1: sharp distance to the proportional model

Allow a cell-specific log departure:

\[
\ell_{tf}=a_t+b_f+e_{tf},\qquad |e_{tf}|\leq\varepsilon.
\]

The smallest feasible uniform budget is

\[
\boxed{\varepsilon_{\rm prop}
=\inf_{a,b}\max_{t,f}|\ell_{tf}-a_t-b_f|
=\frac{\max_f d_f-\min_f d_f}{4}.}
\]

**Necessity.** A feasible representation has

\[
d_f=(a_O-a_S)+(e_{Of}-e_{Sf}).
\]

The residual difference is in \([-2\varepsilon,2\varepsilon]\). Hence every \(d_f\) lies within \(2\varepsilon\) of the same constant, so their range cannot exceed \(4\varepsilon\).

**Sufficiency and an attaining construction.** Put

\[
c=\frac{\max_f d_f+\min_f d_f}{2},\quad
a_O=\frac c2,\quad a_S=-\frac c2,\quad
b_f=\frac{\ell_{Of}+\ell_{Sf}}2.
\]

The resulting residuals are

\[
e_{Of}=\frac{d_f-c}{2},\qquad e_{Sf}=-\frac{d_f-c}{2},
\]

whose maximum absolute value is exactly one quarter of the range of \(d\). \(\square\)

This is an elementary Chebyshev approximation result for a two-row additive model, not a claim of new general mathematics. Its value in this application is that the numerical answer has a direct sensitivity interpretation. Any uniform per-cell correction budget that fits the table must be at least \(\varepsilon_{\rm prop}\) in log units; at least one cell attains that bound in an optimal correction. This does not require every cell to change by the full budget. A feasible corrected width \(W^*\) satisfies

\[
e^{-\varepsilon} \leq W^*_{tf}/W_{tf}\leq e^{\varepsilon}.
\]

The required departure is not itself an estimated direct neural pathway. It can include task-specific neural effects, response criteria, drift in the task-to-width relation, misspecification of the fitted psychometric shape, and sampling error. The statistic locates the size of the model discrepancy; it does not uniquely assign its cause.

### Deterministic uncertainty corollary

Suppose simultaneously defensible log-width intervals are available:

\[
\ell_{tf}\in[L_{tf},U_{tf}].
\]

Define

\[
D_f^- = L_{Of}-U_{Sf},\qquad D_f^+=U_{Of}-L_{Sf}.
\]

The smallest proportional departure compatible with the entire rectangular uncertainty set is

\[
\boxed{\varepsilon_{\rm prop,box}
=\frac{\big[\max_f D_f^- -\min_f D_f^+\big]_+}{4}.}
\]

**Proof.** Each task difference may be chosen independently from \([D_f^-,D_f^+]\). The smallest possible range of a selection from these intervals is zero when their intersection is nonempty, and otherwise is \(\max_f D_f^- -\min_f D_f^+\). In the latter case every selection must span those two limiting endpoints; choosing each difference inside the interval between them attains the bound. Apply Theorem 1. \(\square\)

This is a deterministic interval statement. Marginal 95% intervals are not automatically a simultaneous 95% uncertainty set. The empirical analysis must separately justify any confidence interpretation.

## 3. What survives unknown nonlinear task maps

### Proposition 2: exact strict monotone representability

There are values \(\tau_f\) and strictly increasing task maps \(h_O,h_S\), common across conditions, such that \(W_{tf}=h_t(\tau_f)\) if and only if

\[
\boxed{\operatorname{sign}(W_{Of}-W_{Og})
=\operatorname{sign}(W_{Sf}-W_{Sg})
\quad\text{for every }f,g.}
\]

Thus the tasks must have the same weak order, including identical patterns of ties.

**Proof.** Strict increase preserves each ordering and each equality of latent values, giving necessity. Conversely, partition the conditions into their common tied classes and assign increasing latent values to the classes. Each task's width is well defined and strictly increasing across those classes. Extend these finitely many points by any strictly increasing piecewise-linear function on the finite latent span. \(\square\)

This is the state-trace implication for two positively oriented endpoints. With only two stimulation conditions, equal signs of the two task changes are sufficient for this exact model, with ties treated explicitly. With three conditions, all three pairwise comparisons must agree. Equality of proportional effect sizes is not required.

A successful fit is compatibility with a one-dimensional representation. It does not prove that the physical system has only one cause, nor that the two phenomenological targets are identical. Rejection applies only to a common scalar acting through the specified stable, positively monotone task maps. A nonmonotone map, an intervention-dependent map, or an additional task-specific path lies outside this class.

## 4. Sharp distance to a common monotone order

For finite data, a strictly increasing model is not closed: a sequence of strict curves can converge to one containing a task-specific plateau. It is therefore useful to report distance to the closed model explicitly, rather than silently making a claim about exact strict monotonicity.

Let \(\pi\) be a permutation of the \(F\) conditions. For that common order, let

\[
\varepsilon(\pi)=\frac12
\max_{t,\,j<k}\big[\ell_{t,\pi_j}-\ell_{t,\pi_k}\big]_+.
\]

### Theorem 2: sharp common-order correction

The minimum uniform log correction needed to admit a common nondecreasing condition order is

\[
\boxed{\varepsilon_{\rm mon}
=\min_{\pi}\varepsilon(\pi).}
\]

For three conditions the minimum is over six permutations.

**Proof for one order.** If corrected values \(m_{t,\pi_j}\) are nondecreasing and \(|m_{tf}-\ell_{tf}|\leq\varepsilon\), then for \(j<k\),

\[
\ell_{t,\pi_j}-\ell_{t,\pi_k}
\leq (m_{t,\pi_j}+\varepsilon)-(m_{t,\pi_k}-\varepsilon)
\leq2\varepsilon.
\]

This proves the lower bound. Conversely, if every preceding inequality holds, set

\[
m_{t,\pi_k}=\max_{j\leq k}(\ell_{t,\pi_j}-\varepsilon).
\]

This sequence is nondecreasing. Its \(j=k\) term is at least \(\ell_{t,\pi_k}-\varepsilon\), and every term is at most \(\ell_{t,\pi_k}+\varepsilon\), by the inversion inequalities. It is consequently a valid correction. Minimize over common orders. A scalar latent sequence indexed by that order and nondecreasing task maps represents every such corrected matrix. \(\square\)

The construction is standard \(L_\infty\) isotonic-regression reasoning; Stout (2015/2017) provides a general algorithmic treatment. Searching for a shared latent order is also established in coupled monotonic regression and state-trace analysis, including Kalish et al. (2016). The formulas are retained here to make the secondary analysis transparent and reproducible.

**Why the closed model is the correct distance target.** Add an arbitrarily small increasing sequence to both corrected task rows in the chosen order. The resulting maps can be made strictly increasing while staying arbitrarily close. Conversely, any finite limit of strict common-order matrices has, along a subsequence, one fixed common order and is nondecreasing in that order. Hence this is precisely the closure of the strict model on a finite condition set.

**Tie exception.** \(\varepsilon_{\rm mon}=0\) does not imply exact strict representability. For example, log widths \((0,0,1)\) in one task and \((0,1,2)\) in the other have a common nondecreasing order but inconsistent exact ties. Their strict-model distance is zero as an infimum, yet no strictly increasing pair of task maps reproduces them exactly. Exact equality should not be inferred from numerically close fitted values.

Because every proportional model is a monotone model,

\[
0\leq\varepsilon_{\rm mon}\leq\varepsilon_{\rm prop}.
\]

The two distances locate distinct failures. A nonzero proportional distance with a negligible monotone distance is compatible with a shared temporal coordinate expressed through nonlinear task maps. A reliably nonzero monotone distance requires a larger relaxation: the signed common-order assumption, the stability of the task maps, the chosen endpoint model, or the single-coordinate model must change.

### Optional two-task closed form

For exactly two tasks, the same distance can also be written

\[
\varepsilon_{\rm mon}=\frac12
\max_{\substack{f<g:\
(\ell_{Of}-\ell_{Og})(\ell_{Sf}-\ell_{Sg})<0}}
\min\{|\ell_{Of}-\ell_{Og}|,|\ell_{Sf}-\ell_{Sg}|\},
\]

with the maximum over an empty set defined as zero.

**Proof.** An opposed pair cannot be made concordant without removing the reversal in at least one task, requiring half the smaller gap. For sufficiency, take this maximum and order conditions by \(\ell_{Of}+\ell_{Sf}\). If a task inversion along that order exceeded \(2\varepsilon\), the other task would necessarily have an opposite gap at least as large, contradicting the definition of \(\varepsilon\). The fixed-order construction of Theorem 2 then attains the bound. \(\square\)

The six-order implementation is sufficiently small and easier to audit for the three-condition application; the closed form is an independent algebraic check, not a necessary extra analysis.

## 5. Four counterexamples that determine the interpretation

### Counterexample 1: a common scalar with unequal proportional effects

Let \(\tau=(1,2,4)\), \(h_O(\tau)=\tau\), and \(h_S(\tau)=\tau^2\). The tasks share one latent coordinate and have identical strict ordering. Nevertheless their within-task ratios differ. The log-width matrices are \((0,\log2,\log4)\) and \((0,2\log2,2\log4)\), yielding

\[
\varepsilon_{\rm prop}=\tfrac12\log2>0,\qquad
\varepsilon_{\rm mon}=0.
\]

Failure of equal log changes therefore does not, by itself, refute a shared scalar temporal coordinate.

### Counterexample 2: a genuine ordinal conflict in the declared model

Let the log widths be \((0,1,2)\) and \((0,2,1)\). The last two conditions reverse across tasks. Both distances equal \(1/2\). A correction smaller than one half log unit cannot remove the opposing order. At the boundary, both tasks' last two values can be moved to \(3/2\), showing sharpness. This is a conflict with the stable positive monotone model, rather than merely with proportional scaling.

### Counterexample 3: condition-dependent task maps erase the restriction

Set \(\tau_f=1\) in all conditions. For an arbitrary positive width matrix, define \(h_{tf}(z)=W_{tf}z\). Every \(h_{tf}\) is strictly increasing and the constant latent coordinate reproduces the entire table. Thus positive monotonicity alone imposes no cross-condition restriction when the map itself may change freely with the intervention. Stability or a quantified bound on its failure is indispensable. A manipulated response criterion or task-specific path cannot be excluded by the fitted width table alone.

### Counterexample 4: group agreement hides individual failure

For participant A, let the two log-width rows be \((0,1,0)\) and \((0,0,0)\). For participant B, interchange the rows. Each participant has \(\varepsilon_{\rm prop}=1/4\). Their average log widths are identical between tasks, \((0,1/2,0)\), and hence have proportional distance zero. The signed interaction has canceled across participants. Group-average agreement cannot establish participant-specific proportionality; conversely, raw positive distances in noisy individual fits cannot establish population-level violations without uncertainty analysis.

## 6. What follows for the empirical analysis and for UCT

The primary empirical estimand should be declared before comparing models: the population width parameter of a specified task-response curve, estimated by a specified fitting procedure with explicit lapse treatment. Published fitted widths are saved estimates of their own declared estimands. Response amplitudes, response bias, psychometric width, sensory uncertainty in a generative model, reported ownership, and a putative experiential coordinate are not interchangeable variables. Yarrow, Solomon, Arnold, and Roseboom (2023) provide a particularly relevant primary analysis of how observer strategy affects the window of subjective synchrony. A width change therefore does not automatically measure a change in neural timing precision. This distinction is substantive, not merely terminological.

Report, for each participant, the two distances with uncertainty and fitting diagnostics. Plot the two task widths against one another with the three stimulation conditions labelled. The proportional hypothesis constrains these points to a ray through the origin; the monotone hypothesis only constrains their shared order. Any inference about actual mechanisms additionally relies on the intervention and exclusion assumptions of the source experiment. Secondary data analysis does not establish a new downstream-port rescue or selective motor-command/proprioceptive consumer intervention.

The UCT contribution is a disciplined connection between organizational hypotheses and distinguishable endpoint consequences. C1 may motivate studying the relation between physical organization and experience, but it does not imply \(W_{tf}=c_t\tau_f\), supply a monotone task map, orient an unsigned subjective measure, or guarantee that the selected endpoint responds to every experiential difference. The proportional and monotone models are additional, explicitly defeasible bridge hypotheses. No result here determines whether an AI has experience, whether report equals experience, or whether one global consciousness theory defeats all competitors.

## 7. Verification and novelty audit

The script `shared_clock_bounds_check.py` exhaustively checks all 729 two-task, three-condition log-width matrices with entries in \(\{-1,0,1\}\). It checks Theorem 1 against an independent task-offset feasibility search and verifies its attaining construction. It checks Theorem 2 against all 6,025 distinct common-order half-grid corrected matrices, making 4,392,225 independent candidate-distance comparisons. All checks pass. The half-grid contains an optimum for the integer inputs by the proof's explicit construction. It also verifies \(\varepsilon_{\rm mon}\leq\varepsilon_{\rm prop}\), the two-task opposed-pair formula, the counterexamples, and the strict-tie exceptions. These are mathematical checks, not new human observations.

The project records R200 and R201 already address semantic orientation, report fallibility, and binary marker transport; A3U and A3L already establish the limitations of perturbation and rescue arguments. The present core is different: a quantitative hierarchy of proportional versus ordinal *within-participant cross-task* response models applied to actual intervention data. It must not be advertised as a newly discovered general impossibility result, a new state-trace method, or a novel causal-inference framework. A publishable contribution depends on the quality and nonredundancy of the empirical reanalysis, with the transparent sensitivity measures serving that result.

The separate `APPENDIX_CALIBRATION_GAP.md` derives exact monotone-anchor bounds for a future independently calibrated contrast. That appendix explains what additional calibration could make a mechanism-to-endpoint comparison robust, but the current dataset does not automatically supply the required experiential anchors. It is an optional theoretical extension, not an additional empirical claim.

## Primary references and retrieval scope

1. D'Angelo, M., Lanfranco, R. C., Chancel, M., & Ehrsson, H. H. (2026). *Parietal alpha frequency shapes own-body perception by modulating the temporal integration of bodily signals*. Nature Communications, 17, 53. https://doi.org/10.1038/s41467-025-67657-w. Publisher search record verified; direct page fetching intermittently encounters a publisher cookie redirect. The empirical branch holds the source data and fuller study reading.
2. Bamber, D. (1979). *State-trace analysis: A method of testing simple theories of causation*. Journal of Mathematical Psychology, 19, 137–181. https://doi.org/10.1016/0022-2496(79)90016-6. Publisher abstract verified. Direct prior art for the inferential question.
3. Prince, M., Brown, S., & Heathcote, A. (2012). *The design and analysis of state-trace experiments*. Psychological Methods, 17, 78–99. https://doi.org/10.1037/a0025809. Author/institutional records and author-hosted paper verified. Relevant to design, uncertainty, and the danger of interpreting an untested plot.
4. Kalish, M. L., Dunn, J. C., Burdakov, O. P., & Sysoev, O. (2016). *A statistical test of the equality of latent orders*. Journal of Mathematical Psychology, 70, 1–11. https://doi.org/10.1016/j.jmp.2015.10.004. Publisher highlights and institutional publication record verified. Particularly close prior art: a measure, algorithm, and test of common latent order already exist.
5. Stout, Q. F. (2015; revised 2017). *L infinity isotonic regression for linear, multidimensional, and tree orders*. https://doi.org/10.48550/arXiv.1507.02226. Author preprint record verified. General computational prior art for the uniform-error isotonic component.
6. Luce, R. D., & Tukey, J. W. (1964). *Simultaneous conjoint measurement: A new type of fundamental measurement*. Journal of Mathematical Psychology, 1, 1–27. https://doi.org/10.1016/0022-2496(64)90015-X. Publisher record verified. Broad measurement-theory foundation; the present two-row log-additive model should not be equated with proving all conjoint-measurement axioms.
7. Loftus, G. R. (1978). *On interpretation of interactions*. Memory & Cognition, 6, 312–319. https://doi.org/10.3758/BF03197461. Author-hosted original full text read. Direct prior art for dependence of interaction interpretation on the theoretical-to-observed map.
8. Dunn, J. C., & Anderson, L. M. (2026; advance online publication 2024). *The monotonic linear model: Testing for removable interactions*. Psychological Methods, 31, 585–606. https://doi.org/10.1037/met0000626. PubMed and institutional records verified. Recent direct prior art showing that monotonicity-based model tests are an active established method, not a new invention of this project.
9. Yarrow, K., Solomon, J. A., Arnold, D. H., & Roseboom, W. (2023). *The best fitting of three contemporary observer models reveals how participants' strategy influences the window of subjective synchrony*. Journal of Experimental Psychology: Human Perception and Performance, 49, 1534–1563. https://doi.org/10.1037/xhp0001154. Author institutional repository and author publication records verified. An erratum corrects four displayed equations (DOI 10.1037/xhp0001226); the present module uses the qualitative measurement limitation and does not reproduce those equations.

### Search handles for the integrating agent

`turn35search0` (D'Angelo publisher record); `turn38search0` (Bamber); `turn37search9` and `turn37search10` (Prince); `turn38search3` and `turn38search4` (Kalish); `turn41view0` (Stout); `turn36search7` (Luce–Tukey); `turn15view0` (Loftus original full text); `turn38search7` and `turn38search9` (Dunn–Anderson); `turn52search8` and `turn52search12` (Yarrow). Open the desired sources in the root turn before using their source handles in chat citations.
