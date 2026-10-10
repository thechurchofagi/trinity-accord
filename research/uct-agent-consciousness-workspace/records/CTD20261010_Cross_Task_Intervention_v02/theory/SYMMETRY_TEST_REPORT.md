# A conditional test of the centered response family

## Claim and scope

The released centered Gaussian-interval observer predicts equal response probabilities at positive and negative stimulus-onset asynchronies of equal magnitude. A single global conditional test rejects this necessary constraint for the released Experiment 3 counts, under independent binomial sampling within and between the specified count cells. The observed deviance is **984.304236**. None of **19,999** conditional simulations equals or exceeds it, giving the prespecified plus-one Monte Carlo value **0.00005** and an exact 95% binomial Monte Carlo interval for the simulated tail probability of **[0, 0.00018444]**.

This is a response-family adequacy result. It does not show that Bayesian causal inference generally fails, that a particular alternative noise source is correct, or that stimulation changes an anatomical mediator. Nonzero response centers, unequal flanks, criterion bias, trial drift, and dependence can violate the tested family. The data were previously inspected for other analyses; the analysis plan was recorded before this statistic was calculated, and is retrospective rather than a prospective preregistration.

## Inputs and mapping

Source: D'Angelo et al. (2026), *Parietal alpha frequency shapes own-body perception by modulating the temporal integration of bodily signals*, Nature Communications 17, 53, DOI [10.1038/s41467-025-67657-w](https://doi.org/10.1038/s41467-025-67657-w). The observation restriction follows from the released `modelprediction_log_BCI.m`, associated with the study's [OSF archive](https://osf.io/s5p4v/).

The test uses `empirical/results/aggregate_counts_tidy.csv`: 30 participants, two tasks (ownership and simultaneity), three stimulation conditions (8 Hz, sham, 13 Hz), and seven SOAs (−400, −200, −100, 0, 100, 200, 400 ms). Every count has ten nominal binary judgments. The entire 1,260-cell tidy table exactly matches the canonical array in `empirical/alignment_diagnostic.npz`, including labels and the ownership-first task order.

For the test, each nonzero SOA is paired with its negative. This gives 540 pairs and 1,080 count cells, representing 10,800 nominal judgments. The 180 zero-SOA cells carry no sign-symmetry comparison and are excluded by the declared design. No participants or nonzero SOAs are excluded.

Input SHA-256: `c289edabfb45bc62fa0498e17a36da6f3f9bd6dec469a7968d4d245013f50c00`.

## Null, statistic, and exact conditional law

Index the 540 participant/task/stimulation/magnitude pairs by $j$. Write $Y_{j+},Y_{j-}$ for their two yes counts. The tested family is

$$
Y_{j+},Y_{j-}\stackrel{\mathrm{ind}}{\sim}\operatorname{Binomial}(10,p_j),
\qquad j=1,\ldots,540,
$$

with arbitrary and unrelated $p_j$ across pairs, and independence of counts across pairs. This family is larger than either centered source BCI family. It imposes no cross-SOA, cross-task, or cross-stimulation parameter sharing beyond sign symmetry within each pair.

Let $K_j=Y_{j+}+Y_{j-}$. Conditioning on all observed $K_j$ eliminates every nuisance $p_j$. In each pair,

$$
P(Y_{j+}=y\mid K_j=k)
=\frac{\binom{10}{y}\binom{10}{k-y}}{\binom{20}{k}},
$$

over $\max(0,k-10)\leq y\leq\min(10,k)$. This is a hypergeometric law with population size 20, $k$ successes, and sample size 10. The result follows by canceling the common factors $p_j^k(1-p_j)^{20-k}$ in the conditional joint binomial probability. The conditional pair laws remain independent under the stated sampling model.

The prespecified statistic is twice the log-likelihood improvement when each sign has its own probability instead of a pair-pooled probability:

$$
T=2\sum_j\left\{\ell(Y_{j+};Y_{j+}/10)
+\ell(Y_{j-};Y_{j-}/10)
-\ell(Y_{j+};K_j/20)-\ell(Y_{j-};K_j/20)\right\},
$$

where $\ell(y;p)=y\log p+(10-y)\log(1-p)$ and $0\log0=0$. Binomial combinatorial constants cancel. No source parameter estimates or descriptive Gaussian widths enter this calculation.

For each of 19,999 independent conditional replicates, the script draws all 540 positive counts from their hypergeometric laws, sets the negative counts to $K_j-Y_{j+}$, and recomputes $T$. The upper-tail comparison includes ties. The seed is **202610100742** and the run uses vectorized chunks of 500. The plan specifies exactly one run and no adaptive extension.

## Results

| Quantity | Value |
|---|---:|
| Observed statistic | 984.304236376090 |
| Exact conditional null mean | 531.422410272679 |
| Exact conditional null standard deviation | 31.747721472275 |
| Simulated conditional mean | 531.097869223352 |
| Simulated conditional standard deviation | 31.846348628710 |
| Simulated 95th percentile | 585.026020751205 |
| Largest simulated value | 662.369092892024 |
| Exceedances including ties | 0 / 19,999 |
| Plus-one Monte Carlo value | 0.00005 |
| 95% binomial Monte Carlo interval for the tail probability | [0, 0.00018444] |

The exact conditional mean and variance are obtained by summing each pair's finite hypergeometric moments of its deviance contribution. Their agreement with the simulation is an implementation check, not a second hypothesis test. Of the pairs, 439 have a nondegenerate conditional **count** law. This is not a chi-square degrees-of-freedom count; some nondegenerate count laws still produce a constant contribution to this statistic.

The task summaries below are descriptive, as fixed in the plan. No subsidiary significance tests or multiplicity-adjusted claims are made.

| Task | Pairs | Contribution to global deviance | Mean positive-minus-negative yes-rate difference |
|---|---:|---:|---:|
| Ownership | 270 | 364.925930 | 0.068148 |
| Simultaneity | 270 | 619.378307 | 0.075185 |

The positive-minus-negative direction follows the signed SOA convention in the source file. These averages do not show that every participant or condition has the same sign, and the deviance contributions are not a between-task statistical comparison.

## A deterministic implication for the source fits

Let $\ell_{\mathrm{sat}}$ be the maximum binomial log likelihood with an arbitrary probability in all 1,260 cells. Let $\ell_{\mathrm{sym}}$ maximize a larger centered-symmetry family, pooling every sign pair and leaving every zero-SOA probability unrestricted. Then $T=2(\ell_{\mathrm{sat}}-\ell_{\mathrm{sym}})$.

Any centered source BCI parameterization is a subset of that family, hence $\ell_{\mathrm{BCI}}\leq\ell_{\mathrm{sym}}$. Its deviance against saturation must therefore satisfy

$$
2(\ell_{\mathrm{sat}}-\ell_{\mathrm{BCI}})\geq984.304236376090.
$$

This lower bound holds for every fitted parameter vector and does not depend on reaching a global optimum. It is not a new goodness-of-fit test and does not by itself calibrate a chi-square reference for the nonlinear BCI models.

## Limits and consequences for the paired-readout theorem

The conditional test assumes stable independent binomial responses. Aggregated counts do not reveal trial chronology, serial dependence, or block drift, so this analysis cannot independently validate those assumptions. The rejection concerns their conjunction with centered symmetry. Adding stable task-specific centers is a useful limited response-model sensitivity analysis, with its own held-out score and adequacy checks; it does not establish a neural explanation of the asymmetry.

The paired-readout theorem in `RESPONSE_IDENTIFIABILITY_RESULTS.md` requires a calibrated common center for two reports driven by the same internal sample, known marginal response parameters, and specified criterion and lapse relations. The source experiment collected separate task blocks and does not provide that joint law. Moreover the present result invalidates treating physical zero SOA as an empirically established common center of the released observer. The theorem is a **prospective conditional calibration protocol**, not an inference already supported by these counts. Allowing two different fitted task centers does not automatically create a single physical SOA centered for both consumers.

## Reproducibility

The full plan is `SYMMETRY_ANALYSIS_PLAN.json`, recorded at 07:42:24 UTC on 10 October 2026. The completed run is timestamped 07:43:35.748 UTC. Its plan SHA-256 is `876e8e05fb88e403ffcbd7f50ce8f63b65f253ceb5f599d5f21180538667c17f`.

The script is `test_source_symmetry.py`; machine-readable results are `SYMMETRY_TEST_RESULTS.json`. Pair contributions, descriptive task summaries, and all conditional simulated statistics are retained in the accompanying CSV and NPZ files. The run used Python 3.12.14, NumPy 2.3.5, and SciPy 1.17.0. Re-execution is unnecessary for the current results; the retained draws and inputs allow verification without obtaining a new Monte Carlo realization.
