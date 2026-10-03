---
title: "Supplement: Exponential Run Complexity of Prefix-Separable Orders on the Boolean Cube"
author: "Hongju Liu"
date: "3 October 2026"
lang: en
documentclass: article
fontsize: 11pt
geometry: margin=1in
header-includes:
  - '\usepackage{amsmath,amssymb}'
  - '\usepackage{microtype}'
---

**Report:** TA-TR-2026-22 · **Version:** 1.1 · **DOI:** 10.5281/zenodo.23118189

Mathematical preprint; internal checks, not external peer review.

## S1. Revision scope and proof dependencies

The main manuscript retains the definitions, signed-tree construction and strict separators of v1.0, DOI [10.5281/zenodo.23103274](https://doi.org/10.5281/zenodo.23103274). It replaces the bounded-difference tail with an application of the established read-k theorem of Gavinsky, Lovett, Saks and Srinivasan, *A Tail Bound for Read-k Families of Functions*, [arXiv:1205.1478](https://arxiv.org/pdf/1205.1478), Theorem 1.1. The resulting liminf coefficient increases from \(1/(8\log3)\) to \(\log2/(2\log3)\), a factor \(4\log2\). The \(n^2\) denominator remains.

All-dimensional analytic proofs establish the general bound, paired support counting, simultaneous large-support theorem, conditional bottom extension, row-lift identities and uniform-tail obstruction. Finite verification tests the formulas and implementations. It is not the proof of these all-dimensional statements.

The exact dimension-4 parent minimum used in the new conditional-doubling obstruction is a finite theorem. Completeness relies on the coherent-order region counts in Maclagan, *Boolean term orders and the root system B_n*, [author preprint](https://arxiv.org/pdf/math/9809134), Section 6. Those prior counts are not claimed as new enumeration. The dependency generator constructs 336 positive orders and all 5,376 signed orders on \(Q_4\); it checks distinctness and the known total count. The positive-order seeds come from all increasing generic 4-tuples in \(\{1,\ldots,12\}\), producing 14 distinct sorted-weight orders, followed by coordinate permutations. Dimensions 1--3 have total signed counts 2, 8, and 96.

The two existence proofs for the paired scan classes select their ranks separately. Their union is not asserted to be covered by a single rank. A low raw-support lift can encode an arbitrary upper core; relative support tending to zero is therefore not alone a proof that the scan is easy.

## S2. Reproducible verifier inventory

Extract the deposited verification ZIP and run the following from its root with Python 3. The read-k verifier additionally requires NumPy; the remaining four entrypoints use the standard library. Python 3.11 or later and NumPy 2.3.5 are the release workflow environment. NumPy arrays hold integers; no optimizer or floating-point probability comparison is used.

```text
python3 verify_readk_and_interleaving.py
python3 verify_comparison_support_entropy.py
python3 verify_bottom_extension_concentration.py
python3 verify_sparse_support_amplification.py
python3 verify_conditional_mean_obstruction.py
```

The ZIP includes scripts, integer chamber/rank helpers, JSON receipts, run logs, a source manifest and the internal mathematical audit. The release summary binds each script to its receipt. Runtime fields may change on rerun; mathematical fields and the deterministic read-k enumeration digest remain reproducible. No Python assert optimization flag should be enabled.

\newpage

| Check | Actual coverage | Limitation |
| --- | --- | --- |
| Read-k tail and rank signs | All leaf permutations and all tree orientations on \(Q_1,Q_2,Q_3\): 4, 192, and 5,160,960 rank words | All \(Q_3\) permutations, including nonadditive ones, are tests of the stronger fixed-permutation tail |
| Read-k \(Q_4\) pressure | 27 specified permutations, all 32,768 orientations; 884,736 rank words | Selected permutations, not all \(Q_4\) chambers |
| Row identities | 12,876 cases; 39 integer-score realizations through dimension 10 | All top orientations for \(d\le3\); top permutations exhaustive only for \(d\le2\), with 32 selected at \(d=3\); lower signs sampled |
| Support injection | All 40,344 permutations on \(Q_2,Q_3\), all active assignments and all thresholds; 215 actual scans through dimension 12 | Higher-dimensional scans are samples; support theorem is analytic |
| Conditional extension | All signed chambers on \(Q_2,Q_3,Q_4\), all fixed parents, all fresh assignments: 43,208 contexts, 688,912 states | Chamber completeness is inherited, not inferred from random sampling |
| Sparse amplification | 108 signed core lifts through dimension 15, direct score/support/count comparisons | Direct ranks checked at every vertex through dimension 10 and 2,048 selected vertices above it; formulas are analytic |
| Mean-doubling obstruction | All 5,376 signed \(Q_4\) chambers for parent mask 50; all 256 fresh assignments for one actual \(Q_5\) scan | One child chamber suffices to refute the proposed universal lemma |

The support audit also checks 12 nonadditive antipodal poset diagnostic cases. They are explicitly not called actual additive scans. These diagnostics are not used to refute the original \(M_n\) conjecture.

## S3. Exact finite existence certificates

Let \(a=A/B\in(0,1)\), \(\ell=N-2\), and \(t=K-1\). The read-k inequality with degree \(2K\) gives the valid rational Chernoff bound
\[
P^{2K}\le\left(\frac{1+a}{2}\right)^{N-2}a^{-(K-1)}.
\]
The minimizing parameter is \(a=t/(\ell-t)\) when \(t>0\), with the limit \(a\to0\) at \(t=0\). Any chosen rational parameter gives a weaker valid bound. Consequently the integer certificate
\[
S_n^{2K}(A+B)^{N-2}B^{K-1}
<(2B)^{N-2}A^{K-1}
\]
proves \(M_n\ge K+1\). The verifier checks:

| Dimension | Threshold \(K\) | Rational parameter | Certified consequence |
| --- | --- | --- | --- |
| 12 | 11 | \(5/2042\) | \(M_{12}\ge12\) |
| 16 | 98 | \(97/65437\) | \(M_{16}\ge99\) |

These are conservative existence certificates, not exact extrema and not explicit witness ranks. The JSON receipt records the integer sizes and SHA-256 hashes of both sides.

For the restricted support theorem, the base \(3^{144}<2^{240}\) is checked by integer arithmetic. Its entropy bound follows analytically from \(\log2>2/3\), as shown in the main proof. The bottom-extension base uses the exact rational inequality
\[
\sum_{i=0}^{4}\frac{(9/8)^i}{i!}>3,
\qquad 256>2025/8.
\]
Both verifiers check that \(2^n/n^2\) increases thereafter. These base checks accompany, rather than replace, the analytic bounds for all subsequent dimensions.

## S4. Fully specified integer conditional-mean counterexample

Phase labels are indexed by
\[
o_n(h)+u=2^{n-1}-2^{n-h-1}+u,
\qquad 0\le u<2^{n-h-2},\quad h<n-1.
\]
The top output phase is fixed at 0. For the \(Q_4\) parent mask 50, the minimum cyclic count is 6 over all signed chambers. An attaining positive witness is \((1,2,8,4)\). For a child in \(Q_5\), preserve the parent by shifting its phase mask 8 positions; its full mask is \((50\ll8)\,|\,b\), \(0\le b<256\).

Use weights \((16,1,10,8,12)\). Their actual score order is

```text
0, 2, 8, 10, 4, 6, 16, 18, 1, 3, 12, 14, 24, 26, 20, 22,
9, 11, 5, 7, 17, 19, 28, 30, 13, 15, 25, 27, 21, 23, 29, 31.
```

The corresponding sorted integer scores are

```text
0, 1, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23,
24, 25, 26, 27, 28, 29, 30, 31, 34, 35, 36, 37, 38, 39, 46, 47.
```

They are all distinct. No neighboring vertices, including the cyclic join, project to the same parent vertex. Hence every sign is fixed by the upper parent; all 256 choices have \(R=C=10\). This contradicts the proposed bound \(\mathbb E_{\rm fresh}C\ge2\min_vC(\text{parent},v)=12\).

The verifier certificate uses integer ranks and scores only. A solver used during exploratory witness simplification is unnecessary for any deposited check. The counterexample neither disproves the existential constant-density conjecture nor excludes a controlled-loss mean recurrence.

\newpage

## S5. Proven statements and remaining conjectures

| Statement | Status in v1.1 |
| --- | --- |
| Improved all-weight liminf coefficient \(\log2/(2\log3)\) | Proved analytically using known read-k concentration |
| One rank protects every large-support scan in a dimension | Proved for \(n\ge12\) and raw \(q\ge2^n/8\) |
| Any paired parent has a child protecting every scan with many bottom comparisons | Proved for \(n\ge15\), \(L\ge2^n/8\) |
| Compatible family protects qualifying actual sparse core lifts | Proved, bound \(R\ge2^n/16-1\) |
| Uniform exponentially small fixed-sweep tails in the unconditioned fair tree model | Refuted by an all-dimensional actual row-lift family |
| Exact any-parent conditional mean doubling | Refuted by the integer example in S4 |
| Unrestricted \(M_n\ge c2^n\) | Open: neither a proof nor a general disproof |
| Uniform controlled-loss paired mean inequality and sufficient paired seed | Unproved; the telescoping implication is conditional |

Additional working results, including sharp raw-support 0, 1, 2 classifications and other local score-window bounds, remain in the research continuation record. This release selects a coherent subset of the audited progress; it does not claim to publish every working lemma.

## S6. Internal audit and disclosure

The internal review checks the original strict separators, comparison signs and multiplicity dichotomy; read-degree applicability without conditioning; the entropy injection at an observed fixed top comparison; bottom-edge nonadjacency, influence and exact conditional expectations; chamber union bounds and finite starting dimensions; actual additive row realization; and the selected-rank versus all-rank quantifiers. The source audit binds exact source bytes. A separate final review binds the DOI-containing PDFs and deposited manifest.

No independent external peer review, exhaustive historical priority, or separate final human line-by-line verification is claimed. Hongju Liu is the responsible human author and depositor. Substantial ChatGPT (OpenAI) assistance under human direction is disclosed. Existing signed trees, alternating-run statistics, chamber counting, entropy and concentration methods are credited. Version registration and preservation identify exact bytes; they do not establish mathematical correctness. The manuscript is English-only and preserves the earlier v1.0 edition.
