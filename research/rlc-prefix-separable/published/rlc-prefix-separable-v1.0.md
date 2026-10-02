---
title: "Exponential Run Complexity of Prefix-Separable Orders on the Boolean Cube"
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

Independent researcher, Shenzhen, China

**Report:** TA-TR-2026-22 · **Version:** 1.0 · **DOI:** 10.5281/zenodo.23103274

**Publication status:** Mathematical preprint; not externally peer reviewed.

## Abstract

Let \(Q_n=\{0,1\}^n\). An order on its vertices is prefix-separable if every proper nonempty initial segment is strictly separated from its complement by an affine hyperplane, with a different hyperplane permitted for each segment. For a rank function \(\rho\), let \(\operatorname{RLC}(\rho)\) be the minimum number of maximal consecutive monotone runs obtained by reading \(\rho\) along any generic linear-functional ordering of the vertices. We prove that prefix-separable orders can have \(\operatorname{RLC}(\rho)=\Omega(2^n/n^2)\). More precisely, if \(M_n\) is the maximum of this minimum over prefix-separable orders, then \(\liminf n^2M_n/2^n\ge 1/(8\log 3)\), where \(\log\) denotes the natural logarithm. The proof combines a fixed balanced signed-tree construction, a deterministic bound on repeated comparison labels, a small-tail estimate, and the number of linear sweep chambers. Tree representations, alternating-run statistics, and concentration tools are existing ingredients; the result concerns their quantitative combination under the cube prefix condition and a simultaneous quantifier over every linear sweep. A dimension-independent positive-density lower bound remains open here.

**Keywords:** Boolean cube; prefix separation; pseudo-sweep; alternating runs; separable permutations; linear ranking; probabilistic method.

## 1. Introduction

An order can be simple at each threshold while resisting approximation by a single additive ranking. The threshold statement is that every initial segment can be cut out by a strict affine inequality. The global comparison considered here is the number of times the rank sequence changes direction after the vertices are sorted by one linear functional. The weights in that functional may be chosen optimally and may have either sign.

The prefix condition belongs to an established geometric framework: a pseudo-sweep permutation has every initial segment equal to a strictly separated k-set [1, Section 6.1]. In the setting of Boolean term orders and qualitative probability, nonrepresentable orders whose initial segments are threshold complexes already provide a qualitative separation between individual cuts and a common additive representation [2, 3]. We do not claim this qualitative phenomenon or the prefix condition as new.

Our question is quantitative. Write \(N=2^n\). Must some prefix-separable cube order still make \(\Omega(N/\log^2N)\) monotone runs even after the best linear-functional ordering is chosen? We answer this question affirmatively. The construction uses random signs on a fixed balanced binary tree with its leaves identified with the cube in a fixed coordinate hierarchy. Its tree representation and least-common-ancestor comparison rule are standard for separable permutations [4]. The key estimate controls the chance of few runs for any fixed ordering of those leaves, without assuming that the resulting composed permutation remains separable.

A potential difficulty is that one tree sign may govern many adjacent comparisons of the chosen sweep. A direct concentration estimate based only on the number of independent signs can therefore be too weak. We use a deterministic alternative: if one sign governs too many edges, the sequence already has many runs; otherwise all bounded-difference constants can be controlled by the proposed low-run threshold. This yields a probability bound that can be summed over all linear sweeps.

The paper gives the complete proof of the general bound and an explicit finite inequality. It makes no claim of an exact extremal value, an optimal asymptotic constant, or a positive-density bound \(M_n\ge c_0 2^n\). The supplementary file contains reproducible finite checks and precise comparisons with the closest antecedents.

## 2. Definitions and main results

For a sequence \(p=(p_1,\ldots,p_m)\) of distinct real numbers with \(m\ge2\), define

\[
R(p)=1+\sum_{i=1}^{m-2}
\mathbf 1\{(p_{i+1}-p_i)(p_{i+2}-p_{i+1})<0\}.
\]

Equivalently, \(R(p)\) is the number of constant-sign blocks in the word of adjacent differences. The runs partition the edges of the sequence; adjacent runs share their turning vertex. This is the classical alternating-run or birun statistic [5], rather than the number of increasing runs alone.

A rank function is a bijection \(\rho:Q_n\to\{0,\ldots,N-1\}\). It is **prefix-separable** if, for every \(1\le k<N\), there are \(a_k\in\mathbb R^n\) and \(b_k\in\mathbb R\) such that

\[
\rho(x)<k\ \,\Longrightarrow\, a_k\cdot x<b_k,
\qquad
\rho(x)\ge k\ \,\Longrightarrow\, a_k\cdot x>b_k.
\]

The separating weights need not agree for different \(k\). This condition is denoted \(B_{\mathrm{ind}}(\rho)=1\) in the accompanying research records.

A weight \(w\in\mathbb R^n\) is **generic** if the \(N\) numbers \(w\cdot x\), \(x\in Q_n\), are distinct. Let \(\pi_w=(x_1,\ldots,x_N)\) list the vertices in increasing score order. Set

\[
\operatorname{RLC}(\rho)=
\min_{w\text{ generic}}R(\rho(x_1),\ldots,\rho(x_N)),
\qquad
M_n=\max_{\rho\text{ prefix-separable}}\operatorname{RLC}(\rho).
\]

Generic weights exist. Only finitely many distinct sweep orders occur, so the minimum is attained by an ordering chamber. The maximum is over a finite set of rank functions. For \(n\ge1\),

\[
1\le M_n\le 2^n-1.
\]

**Theorem 2.1 (exponential run complexity).** For every fixed
\(0<c<1/(8\log3)\), all sufficiently large \(n\) admit a prefix-separable rank function \(\rho\) on \(Q_n\) such that every generic weight satisfies

\[
R(\rho\circ\pi_w)>\left\lfloor\frac{c2^n}{n^2}\right\rfloor.
\]

Consequently,

\[
\liminf_{n\to\infty}\frac{n^2M_n}{2^n}
\ge\frac1{8\log3},
\qquad
\lim_{n\to\infty}\frac{\log_2 M_n}{n}=1.
\]

There is also a finite sufficient condition. Write

\[
H_n=\frac{3^n-1}{2},\qquad
S_n=2\sum_{j=0}^{n-1}\binom{H_n-1}{j},
\]

with \(\binom aj=0\) for \(j>a\).

**Theorem 2.2 (finite bound).** Let \(n\ge2\) and let \(K\) be an integer with \(1\le K<2^{n-1}\). If

\[
S_n\exp\left(-\frac{(2^n-2K)^2}{8K(2^n-1)}\right)<1,
\]

then \(M_n\ge K+1\). More generally, the random rank function constructed below has \(\operatorname{RLC}>K\) with probability at least

\[
1-S_n\exp\left(-\frac{(2^n-2K)^2}{8K(2^n-1)}\right).
\]

The latter bound is informative when its right-hand side is positive; the probability itself is always nonnegative.

## 3. A prefix-separable signed-tree family

Fix a full balanced binary tree of depth \(n\). Its root splits the cube by coordinate \(n-1\), the next level by coordinate \(n-2\), and so on down to coordinate \(0\). A node at coordinate \(j\) fixes all higher coordinates and has two children indexed by the value of \(x_j\). The canonical leaf order is the ordinary binary integer order, with coordinate \(0\) the least significant bit.

Assign each internal node \(u\) a sign \(\xi_u\in\{-1,+1\}\). Sign \(+1\) means that child 0 is traversed first; sign \(-1\) means that child 1 is traversed first. Recursively concatenate the two child orders in this chosen order. Let \(\rho_\xi(x)\) be the position of leaf \(x\), starting from 0. Each child subtree occupies a consecutive interval of ranks. There are \(N-1\) internal nodes, and we sample all their signs independently and uniformly.

This is a special fixed-shape signed-tree representation of a separable permutation. The usual direct/skew-sum description and ancestor comparison rule appear in [4, Definitions 2.8--2.9 and Observation 2.10]. We use a particular cube labeling so that the whole family satisfies the required geometric prefix condition.

**Lemma 3.1 (explicit strict separators).** Every \(\rho_\xi\) is prefix-separable.

**Proof.** Fix \(1\le k<N\), and let \(z\) be the first excluded leaf, so \(\rho_\xi(z)=k\). For each coordinate \(j\), let \(u_j(z)\) be the node on the path to \(z\) that splits coordinate \(j\). Define the integer affine form

\[
L_z(x)=\sum_{j=0}^{n-1}3^j\xi_{u_j(z)}(x_j-z_j).
\]

For \(x\ne z\), let \(j\) be its highest differing coordinate from \(z\). Both leaves pass through \(u_j(z)\), and this is their first split. The sign of their rank difference is

\[
\operatorname{sgn}(\rho_\xi(x)-\rho_\xi(z))
=\xi_{u_j(z)}\operatorname{sgn}(x_j-z_j).
\]

The \(j\)-th term of \(L_z(x)\) dominates all lower terms because

\[
3^j>\sum_{h<j}3^h=\frac{3^j-1}{2}.
\]

Thus \(L_z(x)\) has that same sign. Its integer value is at most \(-1\) on the prefix and at least \(1\) on the other excluded leaves; also \(L_z(z)=0\). The threshold \(L_z=-1/2\) strictly separates the two sets. This holds for every prefix. \(\square\)

## 4. Comparison labels and their multiplicities

Fix an arbitrary permutation \(\pi=(x_1,\ldots,x_N)\) of the leaves. It need not be an additive sweep. For \(1\le i<N\), let \(u_i\) be the least common ancestor of \(x_i,x_{i+1}\). At that node they are in opposite children. Define \(\eta_i=+1\) if they cross from child 0 to child 1, and \(\eta_i=-1\) for the reverse crossing. Both \(u_i\) and \(\eta_i\) depend only on \(\pi\) and the fixed tree.

The adjacent rank comparison sign is therefore

\[
s_i=\operatorname{sgn}(\rho_\xi(x_{i+1})-\rho_\xi(x_i))
=\eta_i\xi_{u_i}.
\]

For a node \(u\), define its comparison multiplicity by

\[
m_u(\pi)=\#\{i:u_i=u\},\qquad
\sum_u m_u(\pi)=N-1.
\]

These multiplicities are deterministic once \(\pi\) has been fixed.

**Lemma 4.1 (mean run count).** For every fixed leaf permutation \(\pi\),

\[
\mathbb E_\xi R(\rho_\xi\circ\pi)\ge N/2.
\]

**Proof.** If \(u_i\ne u_{i+1}\), the two signs use independent fair spins, so the probability of a turn is \(1/2\). If \(u_i=u_{i+1}\), the three leaves cross the same split twice. Their child memberships alternate, giving \(\eta_{i+1}=-\eta_i\), so a turn is forced. There are \(N-2\) possible turns. In fact, if \(J=\#\{i:u_i=u_{i+1}\}\), then

\[
\mathbb E_\xi R(\rho_\xi\circ\pi)
=1+J+\frac{N-2-J}{2}=\frac{N+J}{2}.
\]

The asserted lower bound follows. \(\square\)

**Lemma 4.2 (multiplicity forces runs).** For every sign assignment, every fixed \(\pi\), and every internal node \(u\),

\[
m_u(\pi)\le R(\rho_\xi\circ\pi).
\]

**Proof.** The two children of \(u\) occupy disjoint rank intervals, one entirely below the other. Within a strictly increasing run, an edge labeled \(u\) must cross from the lower interval to the upper one. Once this crossing has occurred, the run cannot later return to the lower interval, so a second such edge is impossible. The decreasing case is the same with the directions reversed. This remains true if other leaves outside the subtree occur between crossings. Partition all sequence edges into their constant-sign blocks. Each block contains at most one edge labeled \(u\), proving the inequality. \(\square\)

## 5. A small-tail estimate for any fixed leaf ordering

**Proposition 5.1.** For every fixed leaf permutation \(\pi\) and integer \(1\le K<N/2\),

\[
\Pr_\xi\{R(\rho_\xi\circ\pi)\le K\}
\le
\exp\left(-\frac{(N-2K)^2}{8K(N-1)}\right).
\]

**Proof.** If \(\max_u m_u(\pi)>K\), Lemma 4.2 makes the event impossible. Suppose instead that every \(m_u(\pi)\le K\).

Flip just one tree spin \(\xi_u\). Only adjacent comparison signs with label \(u\) can change. A turn indicator depends on two neighboring comparison signs, so at most \(2m_u(\pi)\) indicators can change. Consequently the function \(R(\rho_\xi\circ\pi)\) has global bounded-difference constants

\[
c_u=2m_u(\pi),\qquad
\sum_u c_u^2\le4K\sum_u m_u(\pi)=4K(N-1).
\]

McDiarmid's inequality [6] for independent coordinates gives

\[
\Pr\{R-\mathbb E R\le-t\}
\le\exp\left(-\frac{2t^2}{\sum_u c_u^2}\right).
\]

By Lemma 4.1 we may take \(t=N/2-K>0\). Substituting the displayed bound on \(\sum c_u^2\) gives Proposition 5.1. \(\square\)

The argument does not condition the independent spins on a low-run event. Its case distinction uses fixed multiplicities, determined by the leaf order before any spins are sampled. This distinction is necessary for the stated use of the concentration inequality.

**Corollary 5.2 (finite families of tests).** If \(\mathcal P\) is any fixed family of \(L\) leaf permutations, then

\[
\Pr_\xi\{\exists\pi\in\mathcal P:
R(\rho_\xi\circ\pi)\le K\}
\le L\exp\left(-\frac{(N-2K)^2}{8K(N-1)}\right).
\]

This follows by a union bound. The test family is fixed independently of the sampled signs; no probabilistic independence between its different failure events is required.

## 6. Counting additive sweeps and completing the proof

Score ties lie on the central hyperplanes

\[
\{w:w\cdot d=0\},\qquad
d\in\{-1,0,1\}^n\setminus\{0\}.
\]

Every such \(d\) is a difference of two cube vertices. Two nonzero ternary vectors give the same hyperplane exactly when they are negatives of one another. Thus there are exactly \(H_n=(3^n-1)/2\) distinct hyperplanes. Within a chamber all pairwise score comparisons are fixed, and hence so is the sweep order.

**Lemma 6.1.** The number of generic additive sweep orders on \(Q_n\) is at most \(S_n\).

**Proof.** A central arrangement of \(H\ge1\) hyperplanes in \(\mathbb R^n\) has at most

\[
2\sum_{j=0}^{n-1}\binom{H-1}{j}
\]

regions. One can obtain this standard upper bound by induction: adding a hyperplane creates at most as many new regions as the induced central arrangement on that hyperplane; the resulting recurrence is the Pascal recurrence. The initial cases are two regions for a single hyperplane and at most two in dimension one. Coincident restrictions can only reduce the count. Applying the bound with \(H=H_n\) proves the claim. The broader use of arrangements to count linear orderings is classical; see [7]. \(\square\)

Apply Corollary 5.2 to the fixed family of all generic additive sweep orders. Lemma 3.1 ensures prefix separation for every sample. The failure probability is at most

\[
S_n\exp\left(-\frac{(N-2K)^2}{8K(N-1)}\right).
\]

Whenever this is below 1, some sign assignment has more than \(K\) runs for every sweep. This proves Theorem 2.2.

For the asymptotic claim, the crude bound \(S_n\le2nH_n^{n-1}\) gives

\[
\log S_n\le(\log3)n^2+O(n).
\]

Fix \(0<c<1/(8\log3)\) and set \(K=\lfloor cN/n^2\rfloor\). For all sufficiently large \(n\), this is an integer between 1 and \(N/2\). Moreover,

\[
\frac{(N-2K)^2}{8K(N-1)}
=\left(\frac1{8c}+o(1)\right)n^2.
\]

The logarithm of the failure bound is consequently at most

\[
\left(\log3-\frac1{8c}+o(1)\right)n^2,
\]

which tends to \(-\infty\). Thus the desired simultaneous lower bound holds with probability tending to 1. For every such \(c\), eventually \(n^2M_n/2^n\ge c\); letting \(c\) increase to \(1/(8\log3)\) proves the liminf statement. Finally, this lower bound and \(M_n\le2^n-1\) imply

\[
n-2\log_2n+O(1)\le\log_2M_n\le n,
\]

and hence the exponential-rate limit in Theorem 2.1. \(\square\)

## 7. Relation to existing results

**Prefix separation and noncoherence.** The present admissibility condition agrees with the prefix k-set condition for pseudo-sweep permutations [1]. Maclagan studies coherence and flips of Boolean term orders [2]. Edelman, Gvozdeva, and Slinko explicitly discuss an order that is not additively representable even though all its initial segments are threshold complexes [3, Example 1]. These works already establish the qualitative obstruction. Our target is a growing lower bound on the minimum run count over all linear sweeps.

**Signed trees.** The representation in Section 3 uses an established permutation construction. In particular, the ancestor sign rule used in Section 4 is [4, Observation 2.10]. We locate the quantitative argument in the multiplicity bound, the low-run tail estimate for arbitrary reordered leaves, and its combination with cube sweep counts, rather than in the tree representation itself.

**Alternating subsequences.** Pinsky [8, Theorem 1] proves that the mean longest alternating subsequence length for a uniformly random separable permutation of size \(N\) is asymptotic to \((2-\sqrt2)N\). With either initial direction permitted, that length equals \(R+1\) for every sequence of distinct values of length at least 2. Thus the statistics have a direct relationship. The relevant differences are the probability model and the simultaneous requirement: our tree shape and cube labeling are fixed, every sampled rank has strictly separable cube prefixes, and the theorem tests all additive sweeps of that same rank.

The existing mean theorem cannot simply be applied after each sweep. A combinatorially separable permutation need not have separable cube prefixes, and composing an admissible rank with a linear sweep need not produce a combinatorially separable permutation. The supplement gives two explicit \(Q_2\) examples. These examples rule out the direct substitution of that mean theorem; they do not rule out other possible reductions.

**Scope of the contribution claim.** The closest sources were checked at their pertinent definitions and theorem statements, with additional citation-chain searches. This establishes substantial antecedents and identifies the specific quantitative statement proved here. It is not a certificate of exhaustive historical priority. The manuscript presents a mathematical theorem and a bounded comparison with prior work, without claiming a new definition, a new concentration inequality, or a new theory of signed trees.

## 8. Interpretation, limitations, and further questions

The theorem measures a gap between thresholdwise linear representability and a single linear score ordering. Every initial binary classification problem for the constructed rank has an explicit strict separator. Yet a single additive score cannot order the vertices so that their ranks have few monotone pieces. This is a precise combinatorial limitation of a common linear ranking, even when the common weights are chosen optimally.

The result does not by itself give a statistical learning guarantee, a lower bound for a particular nonlinear model, or an empirical claim about biological landscapes. Its immediate value is as an extremal statement about orders and linear sweeps. Connections to ordinal modeling or preference representations would require additional model-specific arguments.

Several questions remain. First, can the \(n^2\) denominator be removed, so that \(M_n\ge c_0 2^n\) for a fixed \(c_0>0\)? Second, can a deterministic explicit family achieve the general lower bound proved here by the probabilistic method? Third, what are the sharp order of growth and constant for \(M_n\)? The finite sufficient inequality can also be sharpened by using more information about actual cube chambers or comparison-label multiplicities. None of these improvements is asserted in this version.

## 9. Verification and author disclosure

The proof in Sections 3--6 is analytic and covers all dimensions. Finite computation is supplied as an independent implementation check of its local statements, not as a replacement for that proof. The supplement specifies the verification coverage, software, and machine-readable receipts. No experimental dataset or external participant data is used.

Hongju Liu is the human author of record and responsible depositor. Substantial assistance from ChatGPT (OpenAI) under human direction was used for mathematical development, literature retrieval, proof auditing, computation, drafting, editing, and publication preparation. The checks reported here are internal mathematical and computational checks; no independent external peer review or separate final human line-by-line verification is claimed. DOI registration and archival timestamps identify a version and its bytes, rather than establishing correctness or priority.

This is adjacent first-party research hosted in the author's existing research repository. It does not amend the Trinity Accord or its Bitcoin Originals. Newly written material is released under CC BY 4.0 to the extent the depositor holds rights; cited third-party works retain their own rights.

## References

1. A. Padrol and E. Philippe. *Sweeps, polytopes, oriented matroids, and allowable graphs of permutations*. Combinatorica **44**, 63--123 (2024). DOI: [10.1007/s00493-023-00062-3](https://doi.org/10.1007/s00493-023-00062-3). [Author preprint](https://arxiv.org/html/2102.06134v3).
2. D. Maclagan. *Boolean term orders and the root system \(B_n\)*. Order **15**, 279--295 (1998). DOI: [10.1023/A:1006207716298](https://doi.org/10.1023/A:1006207716298). [Author preprint, revised 1999](https://arxiv.org/pdf/math/9809134).
3. P. H. Edelman, T. Gvozdeva, and A. Slinko. *Simplicial complexes obtained from qualitative probability orders*. SIAM J. Discrete Math. **27**(4), 1820--1843 (2013). DOI: [10.1137/110844568](https://doi.org/10.1137/110844568). [Author preprint](https://arxiv.org/pdf/1108.3700).
4. F. Bassino, M. Bouvel, V. Féray, L. Gerin, and A. Pierrot. *The Brownian limit of separable permutations*. Ann. Probab. **46**(4), 2134--2189 (2018). DOI: [10.1214/17-AOP1223](https://doi.org/10.1214/17-AOP1223). [Author preprint](https://arxiv.org/html/1602.04960v3).
5. I. M. Gessel and Y. Zhuang. *Shuffle-compatible permutation statistics*. Adv. Math. **332**, 85--141 (2018). DOI: [10.1016/j.aim.2018.05.003](https://doi.org/10.1016/j.aim.2018.05.003). [Author preprint](https://arxiv.org/pdf/1706.00750).
6. C. McDiarmid. *On the method of bounded differences*. In J. Siemons (ed.), *Surveys in Combinatorics, 1989*, London Mathematical Society Lecture Note Series **141**, Cambridge University Press, pp. 148--188 (1989). DOI: [10.1017/CBO9781107359949.008](https://doi.org/10.1017/CBO9781107359949.008).
7. R. P. Stanley. *Valid orderings of real hyperplane arrangements*. Discrete Comput. Geom. **53**, 951--964 (2015). [Author manuscript](https://math.mit.edu/~rstan/papers/vis.pdf).
8. R. G. Pinsky. *Mean and variance of the longest alternating subsequence in a random separable permutation*. arXiv:2310.08664v2 (2023), preprint. [Full text](https://arxiv.org/pdf/2310.08664).
