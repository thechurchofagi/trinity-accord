---
title: "Supplement: Exponential Run Complexity of Prefix-Separable Orders on the Boolean Cube"
author: "Hongju Liu"
date: "2 October 2026"
lang: en
documentclass: article
fontsize: 11pt
geometry: margin=1in
header-includes:
  - '\usepackage{amsmath,amssymb}'
  - '\usepackage{microtype}'
---

**Report:** TA-TR-2026-22 · **Version:** 1.0 · **DOI:** 10.5281/zenodo.23103274

This supplement accompanies the mathematical preprint. It records the finite verification and the closest literature comparisons. It is not an external peer-review report or an originality certificate.

## S1. Independent implementation checks

The main proof is analytic. The supplied `verify_theorem.py` constructs ranks by recursively traversing signed trees and separately predicts adjacent comparison signs by a bit-based least-common-ancestor formula. It compares these two computations for every ordering of the leaves and every tree sign assignment in dimensions 1--3. Thus the test includes arbitrary leaf orders, not just orders observed by sampling additive weights.

| Dimension | Tree sign assignments | Leaf permutations | Rank sequences checked |
| --- | ---: | ---: | ---: |
| 1 | 2 | 2 | 4 |
| 2 | 8 | 24 | 192 |
| 3 | 128 | 40,320 | 5,160,960 |

For each leaf permutation, the program checks the ancestor comparison identity, the exact mean formula \(\mathbb E R=(N+J)/2\), the deterministic inequality \(R\ge\max_u m_u\), and every one-spin change against the proposed bounded-difference constant \(2m_u\). The complete run covered 5,161,156 rank sequences and 36,127,300 one-spin comparisons, with no violation.

It also checked 120,984 finite low-run inequalities for the tested sizes. These checks use rational arithmetic: for \(a=(N-2K)^2/[8K(N-1)]<1\), the elementary inequality \(e^{-a}\ge1-a\) allows the stronger rational comparison \(\Pr(R\le K)\le1-a\). If a multiplicity exceeds \(K\), the program instead verifies that the event is empty. These finite checks do not establish the all-dimensional concentration theorem; Proposition 5.1 of the paper proves it using the standard bounded-difference inequality.

Strict prefix separators were checked for every sign assignment in dimensions 1--3 and for 64 reproducibly sampled sign assignments in each of dimensions 4--6. The total is 7,898 prefix checks. All scores in these checks are integers. The higher-dimensional checks are explicitly sampled and should not be described as exhaustive.

Finally, an independent quadratic dynamic program for the longest alternating subsequence checks \(A=R+1\) for all 5,912 permutations of sizes 2--7. This supports the exact statistical correspondence used in the literature discussion.

The deposited receipt records the tested scopes and the verification script's SHA-256. The original local run used NumPy 2.3.5. The program does not use floating-point feasibility decisions, an optimization solver, or external data.

## S2. Reproduction

With Python 3 and NumPy available, run:

```text
python3 verify_theorem.py --receipt reproduced-verification.json
```

The output state should be `FINITE_THEOREM_CHECKS_PASS`. Coverage counts and mathematical assertions should agree with the deposited receipt. Elapsed time and software versions can differ. The analytic theorem is independent of this runtime and of the finite sizes chosen for testing.

## S3. Exact relationship between the two statistics

Let \(A(p)\) be the length of the longest subsequence of distinct values whose adjacent comparison directions alternate, with either first direction permitted. If \(|p|\ge2\), then

\[
A(p)=R(p)+1.
\]

Selecting the first entry, all local turning vertices, and the last entry gives an alternating subsequence of length \(R+1\). Conversely, suppose an alternating subsequence has length \(k\). The difference between each pair of its consecutive entries is a sum of edge differences of the full sequence over a disjoint interval. At least one summand has the sign of that difference. Select one such summand in each interval. Their signs alternate, so the full edge-sign word must have at least \(k-2\) changes. Hence \(R\ge k-1\).

This elementary identity is not presented as a new result. It matters for an accurate comparison: the use of a subsequence statistic in Pinsky's paper does not, by itself, make that paper unrelated to the present run statistic. Pinsky's definition permits either initial direction, matching the identity above.

## S4. Two barriers to a direct substitution of the separable-permutation theorem

Here a vertex is encoded by its binary integer, with coordinate 0 the least significant bit. Combinatorial separability of a permutation means avoiding the patterns 2413 and 3142; geometric prefix separation is a distinct requirement.

**A separable permutation with an inseparable cube prefix.** On \(Q_2\), take the ranks by vertex integer to be \((0,2,3,1)\), giving the standard one-based permutation 1342. This permutation is combinatorially separable. However, its two lowest-ranked vertices are 0 and 3, opposite corners of the square. The other vertices are 1 and 2, and

\[
(0,0)+(1,1)=(1,0)+(0,1)=(1,1).
\]

Their two convex hulls share the square's center. No strict affine separator can cut out that prefix. Uniform sampling of all combinatorially separable permutations therefore does not ensure the cube admissibility condition.

**A linear sweep that leaves the separable-permutation class.** Take the identity rank \(\rho(x)=x\) on \(Q_2\). It is realized by weights \((1,2)\), so every prefix has a strict separator. It is also the separable permutation 1234 in the natural vertex order. The generic weight \((-2,1)\) gives scores \((0,-2,1,-1)\) and sweep vertices \((1,3,0,2)\). Reading the identity rank along that sweep gives 2413 in one-based notation, a forbidden pattern. Thus composition with a generic additive sweep need not preserve the separable-permutation class.

These examples show why Pinsky's mean theorem cannot simply be applied unchanged to every composed rank sequence. They do not establish that every possible reduction from existing permutation results is impossible.

## S5. Literature and proof audit

The following specific dependencies are acknowledged in the main paper:

- The every-prefix k-set condition for pseudo-sweeps: Padrol and Philippe, Section 6.1.
- Qualitative noncoherence with threshold initial segments: Edelman, Gvozdeva, and Slinko, Example 1, referencing Maclagan's Boolean term orders.
- Signed-tree representations and ancestor comparison signs: Bassino et al., Definitions 2.8--2.9 and Observation 2.10.
- Alternating runs as a classical permutation statistic: Gessel and Zhuang, Section 2.2.
- The independent-coordinate bounded-difference inequality: McDiarmid.
- Arrangement-based counts of linear orderings: Stanley; the paper supplies the elementary region upper bound it actually needs.
- Linear mean alternating length under uniform sampling of all separable permutations: Pinsky, Theorem 1.

The local proof audit checked the strict half-integer separator, signs at the first differing coordinate, comparison labels independent of random spins, the multiplicity inequality on edge-sign blocks, the global nature of the bounded-difference constants, both cases of the small-tail argument, and the quantifier over the whole fixed family of additive sweeps. It also checked the floor in \(K=\lfloor c2^n/n^2\rfloor\), the asymptotic constant, and the upper bound needed for the exponential-rate conclusion.

The source searches additionally considered restricted shuffle statistics, all-coherent zonotopes, gallery flip distances, and coherent monotone-path length bounds. These nearby indicators do not become the present run count without a proved reduction. The manuscript relies only on the explicit statements it cites and does not certify exhaustive historical priority.

The main conclusion remains \(\Omega(2^n/n^2)\). This version does not claim a positive-density bound, an exact extremal value, an optimal constant, or a proof about a Gray-code family.

## S6. Authorship, data, and rights

Human author of record and responsible depositor: Hongju Liu. Substantial assistance from ChatGPT (OpenAI) under human direction was used in mathematical development, literature work, proof auditing, programming, writing, and publication preparation. The verification is internal; no independent external referee or separate final human line-by-line verification is claimed.

No participant data, private dataset, or human-subject experiment is included. Newly written material is released under CC BY 4.0 to the extent rights are held; cited works retain their own rights. The paper and this supplement are adjacent research and do not amend the Trinity Accord or its Bitcoin Originals.
